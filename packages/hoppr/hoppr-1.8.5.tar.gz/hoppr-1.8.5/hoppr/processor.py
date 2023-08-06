"""
Run Hoppr processing, using multiple processors
"""
from __future__ import annotations

import logging
import multiprocessing
import os
import shutil
import socket
import sys
import tempfile
import time
import uuid

from concurrent.futures import Future, ProcessPoolExecutor
from copy import deepcopy
from datetime import datetime
from multiprocessing import cpu_count
from os import PathLike
from pathlib import Path
from threading import _RLock as RLock
from typing import Any, MutableMapping
from urllib.parse import quote_plus

import jmespath

from packageurl import PackageURL
from typer import colors, echo, secho

from hoppr import __version__
from hoppr.base_plugins.hoppr import HopprPlugin
from hoppr.core_plugins.report_generator import Report, ReportGenerator
from hoppr.exceptions import HopprPluginError
from hoppr.in_toto import HopprInTotoLinks
from hoppr.mem_logger import MemoryLogger
from hoppr.models import HopprContext
from hoppr.models.credentials import Credentials
from hoppr.models.manifest import Component, Manifest, ManifestFile, Sbom
from hoppr.models.transfer import ComponentCoverage, Plugin, StageRef, Transfer
from hoppr.models.types import BomAccess
from hoppr.result import Result
from hoppr.utils import plugin_class, plugin_instance

# Import on Unix systems only
if os.name == "posix":
    import pwd


def _run_plugin(
    plugin_name: str,
    context: HopprContext,
    config: dict[str, Any] | None,
    method_name: str,
    component: Component | None,
) -> Result:
    """
    Runs a single method for a single component (if supplied) on a single plugin
    """
    plugin = plugin_instance(plugin_name, context, config)

    match method_name:
        case HopprPlugin.pre_stage_process.__name__:
            result = plugin.pre_stage_process()
        case HopprPlugin.process_component.__name__:
            result = plugin.process_component(component)
        case HopprPlugin.post_stage_process.__name__:
            result = plugin.post_stage_process()
        case _:
            result = Result.fail(f"Invalid method: {method_name}")

    if result.return_obj is not None:
        if not plugin.bom_access.has_access_to(result.return_obj):
            result = Result.fail(
                f"Plugin {type(plugin).__name__} has BOM access level {plugin.bom_access.name}, "
                f"but returned an object of type {type(result.return_obj).__name__}"
            )

    return result


class StageProcessor:  # pylint: disable=too-few-public-methods
    """
    Class to handle all processing within a single Hoppr stage
    """

    component_based_methods = [HopprPlugin.process_component.__name__]

    def __init__(self, stage_ref: StageRef, context: HopprContext):
        self.stage_id = stage_ref.name
        self.context = context
        self.plugin_ref_list = stage_ref.plugins
        self.config_component_coverage = None
        if stage_ref.component_coverage is not None:
            self.config_component_coverage = ComponentCoverage[str(stage_ref.component_coverage)]
        self.required_coverage = ComponentCoverage.OPTIONAL
        self.results: dict[str, list[tuple[str, str | None, Result]]] = {}

    def run(self) -> Result:
        """
        Run all processes for this stage
        """
        try:
            self.plugin_ref_list = self._get_stage_plugins()
            self.required_coverage = self._get_required_coverage()
        except (ModuleNotFoundError, HopprPluginError) as err:
            return Result.fail(str(err))

        result = self._check_bom_access()
        if not result.is_success():
            return result

        # Run each sub-stage (pre_stage_process, process_component, post_stage_process)
        # for all plugins (and, for process_component, for all components).
        # Each sub-stage must complete before the next can begin
        result.merge(self._run_all(HopprPlugin.pre_stage_process.__name__))
        result.merge(self._run_all(HopprPlugin.process_component.__name__))
        result.merge(self._run_all(HopprPlugin.post_stage_process.__name__))

        return result

    def _run_all(self, method_name: str):
        """
        Run the named method for all plugins.  If appropriate to the method, run it for
        all components for all plug-ins.
        """

        # Map to allow access to the arguments that went into a future call
        future_argument_map: dict[Future[Result], tuple[Plugin, Component | None]] = {}

        with ProcessPoolExecutor(max_workers=self.context.max_processes) as executor:
            for plugin in self.plugin_ref_list:

                plugin_cls = plugin_class(plugin.name)

                if getattr(plugin_cls, method_name) == getattr(HopprPlugin, method_name):
                    continue

                if method_name in self.component_based_methods:
                    # Create one concurrent future object to run this method for each component
                    for component in self.context.delivered_sbom.components or []:
                        future_proc = executor.submit(
                            _run_plugin,
                            plugin_name=plugin.name,
                            context=self.context,
                            config=plugin.config,
                            method_name=method_name,
                            component=component,
                        )
                        future_argument_map[future_proc] = (plugin, component)
                else:
                    # Create a concurrent future object to run this method
                    future_proc = executor.submit(
                        _run_plugin,
                        plugin_name=plugin.name,
                        context=self.context,
                        config=plugin.config,
                        method_name=method_name,
                        component=None,
                    )
                    future_argument_map[future_proc] = (plugin, None)

            # Save all the results, count failures and retries
            # Note: future.results() blocks until the process is complete
            need_method_label = True
            failures = 0
            retries = 0

            for future_proc, (plugin, comp) in future_argument_map.items():
                future_result: Result = future_proc.result()
                if not future_result.is_skip():
                    if need_method_label:
                        echo(f"   Beginning method {method_name}")
                        need_method_label = False

                    plugin_cls = plugin_class(plugin.name)

                    if not future_result.is_excluded():
                        self._save_result(method_name, plugin_cls.__name__, future_result, comp)
                        self._update_bom(future_result.return_obj, comp)
                    self._report_result(plugin_cls.__name__, comp, future_result)

                    ReportGenerator.report_gen_list.append(
                        Report(
                            uuid.uuid4(),
                            plugin_cls.__name__,
                            self.stage_id,
                            future_result.status,
                            future_result.message,
                            method_name,
                            comp,
                        )
                    )

                    if future_result.is_fail():
                        failures += 1
                    if future_result.is_retry():
                        retries += 1

        if method_name in self.component_based_methods:
            failures += self._check_component_coverage(method_name)

        return self._get_stage_result(method_name, failures, retries)

    def _get_stage_result(self, method_name: str, failures: int, retries: int) -> Result:
        if failures + retries == 0:
            return Result.success()
        if failures == 0 and retries > 0:
            return Result.fail(f"{retries} '{method_name}' processes returned 'retry'")
        if failures > 0 and retries == 0:
            return Result.fail(f"{failures} '{method_name}' processes failed")
        return Result.fail(f"{failures} '{method_name}' processes failed, and {retries} returned 'retry'")

    def _get_required_coverage(self) -> ComponentCoverage:
        if self.config_component_coverage is not None:
            return self.config_component_coverage

        if len(self.plugin_ref_list) == 0:
            return ComponentCoverage.OPTIONAL

        plugin = plugin_class(self.plugin_ref_list[0].name)
        coverage = plugin.default_component_coverage

        for plugin_ref in self.plugin_ref_list:
            plugin = plugin_class(plugin_ref.name)
            if plugin.default_component_coverage != coverage:
                raise HopprPluginError(
                    f"Plugins for stage {self.stage_id} do not have consistent default "
                    "component coverage values. The value may be overridden in transfer file."
                )

        return coverage

    def _check_component_coverage(self, method_name: str) -> int:
        result_count: dict[str | None, int] = {}
        for (_, purl, _) in self.results.get(method_name, []):
            result_count[purl] = result_count.get(purl, 0) + 1

        additional_failures = 0
        for component in self.context.delivered_sbom.components or []:
            count = result_count.get(component.purl, 0)
            if not self.required_coverage.accepts_count(count) and str(component.scope) not in {
                'excluded',
                'Scope.excluded',
            }:
                bad_comp_result = Result.fail(
                    f"Component processed {count} times, {self.required_coverage.name} coverage required"
                )
                self._save_result(method_name, f"Stage {self.stage_id}", bad_comp_result, component)
                self._report_result(f"Stage {self.stage_id}", component, bad_comp_result)
                additional_failures += 1

        return additional_failures

    def _check_bom_access(self) -> Result:
        access_counts: dict[BomAccess, list[str]] = {}
        for access in BomAccess:
            access_counts[access] = []

        for plugin_ref in self.plugin_ref_list:
            plugin_cls = plugin_class(plugin_ref.name)
            access_counts[plugin_cls.bom_access].append(plugin_cls.__name__)

        if len(access_counts[BomAccess.FULL_ACCESS]) > 0 and len(self.plugin_ref_list) > 1:
            msg = (
                f"Stage {self.stage_id} has one or more plugins with {BomAccess.FULL_ACCESS.name}: "
                f"{', '.join(access_counts[BomAccess.FULL_ACCESS])}"
                ", and multiple plugins defined for the stage."
                "\n    Any plugin with FULL BOM access must be the only plugin in the stage"
            )
            secho(msg, fg=colors.RED)
            return Result.fail(msg)

        if len(access_counts[BomAccess.COMPONENT_ACCESS]) > 0 and self.required_coverage.max_value > 1:
            msg = (
                f"Stage {self.stage_id} has one or more plugins with {BomAccess.COMPONENT_ACCESS.name}: "
                f"{', '.join(access_counts[BomAccess.COMPONENT_ACCESS])}"
                f", and required component coverage for the stage of {self.required_coverage.name}."
                "\n    If any plugins have COMPONENT access, the stage required coverage must be "
                "EXACTLY_ONCE or NO_MORE_THAN_ONCE."
            )
            secho(msg, fg=colors.RED)
            return Result.fail(msg)

        return Result.success()

    def _update_bom(self, return_obj: Any, comp: Component | None):
        if self.context.delivered_sbom.components is not None and isinstance(return_obj, Component):
            for index, delivered_comp in enumerate(self.context.delivered_sbom.components):
                if delivered_comp == comp:
                    self.context.delivered_sbom.components[index] = return_obj
                    break

        elif isinstance(return_obj, Sbom):
            self.context.delivered_sbom = return_obj

    @staticmethod
    def _report_result(plugin: str, comp: Component | None, result: Result):
        desc = f"      {plugin} {result.status.name}"
        if comp is not None:
            desc = desc + f" for {comp.purl}"

        if result.is_success():
            color = colors.GREEN
        elif result.is_excluded():
            color = colors.YELLOW
        else:
            color = colors.RED
        if result.message:
            desc = desc + f": {result.message}"
        secho(desc, fg=color)

    def _save_result(self, method_name: str, plugin: str, result: Result, comp: Component | None):
        """
        Store the results for later use
        """
        comp_string = None
        if comp is not None and PackageURL.from_string(comp.purl) is not None:
            comp_string = comp.purl

        # If needed, create a new list for this method
        # Might need to expand this definition in the future to separate by plug-in

        if not method_name in self.results:
            self.results[method_name] = []

        self.results[method_name].append((plugin, comp_string, result))

    def _get_stage_plugins(self) -> list[Plugin]:
        """
        Determine list of plugin references used in this stage
        """
        used_purl_types: set[str] = set()

        # Get list of all component PURLs that are not None
        results = jmespath.search(
            expression="components[*].purl | not_null(@)",
            data=self.context.delivered_sbom.dict(by_alias=True),
        )

        used_purl_types.update(PackageURL.from_string(purl).type for purl in results)

        plugin_list: list[Plugin] = []

        # Loop over copy of transfer plugin references
        for plugin_ref in set(self.plugin_ref_list):
            plugin_cls = plugin_class(plugin_ref.name)

            # Determine if plugin's `supported_purl_types` are in the set of PURL types defined in SBOM components
            plugin_needed: bool = len(used_purl_types.intersection(plugin_cls.supported_purl_types)) > 0

            if len(plugin_cls.supported_purl_types) == 0 or plugin_needed:
                plugin_list.append(plugin_ref)

        return plugin_list


class HopprProcessor:  # pylint: disable=too-many-instance-attributes
    """
    Run the Hoppr process
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        transfer_file: Path,
        manifest_file: Path,
        credentials_file: Path | None,
        create_attestations: bool = False,
        functionary_key_path: Path | None = None,
        functionary_key_password: str | None = None,
        log_level: int = logging.INFO,
        log_file: str | Path | None = None,
        strict_repos: bool = True,
        previous_delivery: Path | None = None,
    ) -> None:
        self.context: HopprContext
        self.logger: MemoryLogger
        self.log_file: Path = Path(log_file or f"hoppr_{time.strftime('%Y%m%d-%H%M%S')}.log")
        self.log_level = log_level
        self.logfile_lock = multiprocessing.RLock()
        self.metadata_files: list[Path] = []
        self.strict_repos: bool = strict_repos

        self.manifest_file = ManifestFile.parse_file(manifest_file)

        self.credentials = Credentials.load(credentials_file)
        self.manifest = Manifest.load(manifest_file)
        self.transfer = Transfer.load(transfer_file)

        self.stage_processor_map: MutableMapping[StageRef, StageProcessor] = {}

        self.previous_delivery: Path | None = previous_delivery

        self.in_toto_links = HopprInTotoLinks(
            create_attestations,
            self.transfer,
            functionary_key_path,
            functionary_key_password,
        )

        self.report_gen: ReportGenerator

    def _collect_file(
        self, file_name: str | PathLike[str], target_dir: str | PathLike[str]
    ) -> None:  # pragma: no cover
        self.get_logger().info(f"Collecting metadata file {file_name}")
        abs_path = Path(file_name).absolute()

        target = Path(target_dir, quote_plus(f"{abs_path}"))
        shutil.copyfile(file_name, f"{target}")

    def _collect_manifest_metadata(self, manifest: ManifestFile, target_dir: str | PathLike[str]) -> None:
        for include_ref in manifest.includes:
            include = Manifest.loaded_manifests[include_ref]
            include_dict = include_ref.dict()

            if "local" in include_dict:
                url = str(include_dict["local"])
            else:
                url = str(include_dict["url"])

            target_file = Path(target_dir) / quote_plus(url)

            with target_file.open(mode="w+", encoding="utf-8") as output_file:
                output_file.write(include.yaml(by_alias=True, exclude_unset=True, indent=True))

        for sbom_ref in manifest.sboms:
            sbom = Sbom.loaded_sboms[sbom_ref]
            sbom_dict = sbom_ref.dict()

            if "local" in sbom_dict:
                url = str(sbom_dict["local"])
            elif "oci" in sbom_dict:
                url = str(sbom_dict["oci"])
            else:
                url = str(sbom_dict["url"])

            target_file = Path(target_dir) / quote_plus(url)

            with target_file.open(mode="w+", encoding="utf-8") as output_file:
                output_file.write(sbom.json(by_alias=True, exclude_unset=True, indent=2))

    def _collect_metadata(self):
        echo("Collecting Hoppr Metadata")
        target_dir = Path(self.context.collect_root_dir) / "generic" / "_metadata_"
        target_dir.mkdir(exist_ok=True, parents=True)

        if os.name == "posix":
            user = pwd.getpwuid(os.getuid()).pw_name
        else:
            user = os.getlogin()  # pragma: no cover

        with (target_dir / "_run_data_").open(mode="w", encoding="utf-8") as rundata:
            rundata.write(
                f"Hoppr Version:     {__version__}\n"
                f"Collection Start:  {str(datetime.now())}\n"
                f"User:              {user}\n"
                f"Host FQDN:         {socket.getfqdn()}\n"
                f"Working directory: {os.getcwd()}\n"
                f"Argument List:     {sys.argv[1:]}\n"
            )

        for file_name in self.metadata_files:
            self._collect_file(file_name, target_dir)

        self._collect_manifest_metadata(self.manifest_file, target_dir)

    def _collect_consolidated_bom(self) -> None:
        target_dir = Path(self.context.collect_root_dir) / "generic" / "_metadata_"
        target_dir.mkdir(parents=True, exist_ok=True)

        with (target_dir / "_consolidated_bom.json").open(mode="w", encoding="utf-8") as bom_data:
            bom_data.write(self.context.consolidated_sbom.json(exclude_none=True, by_alias=True, indent=2))

    def _collect_delivered_bom(self, stage_name: str | None = None) -> None:
        target_dir = Path(self.context.collect_root_dir) / "generic" / "_metadata_"
        target_dir.mkdir(parents=True, exist_ok=True)

        preface = f"intermediate_{stage_name}_" if stage_name else ""

        with (target_dir / f"_{preface}delivered_bom.json").open(mode="w", encoding="utf-8") as bom_data:
            bom_data.write(self.context.delivered_sbom.json(exclude_none=True, by_alias=True, indent=2))

    def _summarize_results(self) -> int:
        """
        Summarize the results of a HopprProcess run
        """
        echo(f"\n{' Results Summary '.center(40, '=')}")

        total_success_count = 0
        total_failure_count = 0
        for stage_ref, stage in self.stage_processor_map.items():
            echo(f"\nStage: {stage_ref.name}")

            for method_name, result_list in stage.results.items():
                echo(f"   {method_name}")
                result_count = len(result_list)
                failure_count = 0
                failure_list = "\n      Failure Summary:\n"

                for plugin_name, comp_str, result in result_list:
                    # All retries should be handled internally by the plugins,
                    # So if a RETRY result is returned, that's a failure
                    if result.is_fail() or result.is_retry():
                        failure_count += 1
                        failure_list += f"         {plugin_name}: "

                        if comp_str is not None:
                            failure_list += f"Component: {comp_str}: "

                        failure_list += result.message + "\n"

                total_failure_count += failure_count
                total_success_count += result_count - failure_count
                echo(f"      {result_count - failure_count} jobs succeeded, {failure_count} failed")

                if failure_count > 0:
                    echo(failure_list)

        echo(f"\nGRAND TOTAL: {total_success_count} jobs succeeded, {total_failure_count} failed\n")
        self.report_gen = ReportGenerator(self.context)
        self.report_gen.generate_report()

        return total_failure_count

    def get_logger(
        self,
        lock: RLock | None = None,
        log_name: str | None = None,
        log_file: str | Path = "hoppr.log",
        log_level: int = logging.INFO,
    ) -> MemoryLogger:
        """
        Returns the logger for this class

        Args:
            lock (RLock | None, optional): Reentrant lock for shared log file. Defaults to None.
            log_name (str | None, optional): Name of logger. Defaults to None.
            log_file (str | Path | None, optional): Path to log file. Defaults to "hoppr.log".
            log_level (int, optional): Logging level. Defaults to logging.INFO.

        Returns:
            MemoryLogger: A new MemoryLogger instance.
        """
        if not hasattr(self, "logger"):
            self.logger = MemoryLogger(
                file_name=str(log_file),
                lock=lock,
                log_name=log_name or f"HopprProcessor--{os.getpid()}",
                log_level=log_level,
                flush_immed=True,
            )

        return self.logger

    def run(self) -> Result:
        """
        Run the Hoppr process executing each stage in turn

        Args:
            log_file (Path | None, optional): Path to log file. Defaults to None.
            strict_repos (bool, optional): Enables strict repository searches for components. Defaults to True.

        Returns:
            Result: The composite result of all executed stages
        """
        result = Result.success()

        with tempfile.TemporaryDirectory() as collection_root, multiprocessing.Manager() as manager:
            logfile_lock = manager.RLock()

            self.context = HopprContext(
                collect_root_dir=Path(collection_root).resolve(),
                consolidated_sbom=deepcopy(Sbom.consolidated_sbom),
                credential_required_services=getattr(self.credentials, "credential_required_services", None),
                delivered_sbom=deepcopy(Sbom.consolidated_sbom),
                log_level=self.log_level,
                logfile_location=self.log_file,
                logfile_lock=logfile_lock,
                max_processes=self.transfer.max_processes or cpu_count(),
                repositories=self.manifest.repositories,
                sboms=list(Sbom.loaded_sboms.values()),
                stages=self.transfer.stages,
                strict_repos=self.strict_repos,
            )

            self.logger = self.get_logger(
                lock=logfile_lock,
                log_name=f"HopprProcessor--{os.getpid()}",
                log_file=self.log_file,
                log_level=self.log_level,
            )

            if self.context.consolidated_sbom is not None and len(self.context.consolidated_sbom.components or []) == 0:
                msg = "No SBOMs defined in manifests, or SBOMs contain no components. Nothing to process."
                secho(msg, fg=colors.RED)
                return Result.fail(msg)

            self.in_toto_links.set_collection_root(collection_root)
            self.in_toto_links.record_stage_start("_collect_metadata")
            self._collect_metadata()
            self._collect_consolidated_bom()
            self.in_toto_links.record_stage_stop("_collect_metadata")

            # Reset some class variables (we should refactor to use instance variables, see issue
            # https://gitlab.com/hoppr/hoppr/-/issues/230) so that:
            #   1: The consolidated bom cannot be modified
            #   2: Plug-ins may choose to load other manifests.
            del Sbom.consolidated_sbom
            Component.component_lookup = {}
            Component.components = []
            Component.properties = []
            Manifest.loaded_manifests = {}

            msg = f"Beginning Hoppr Process execution, max_processes={self.context.max_processes}"
            self.logger.info(msg=msg)
            echo(message=msg)

            for stage_ref in self.transfer.stages:
                msg = f" Beginning Stage {stage_ref.name} ".center(100, "=")
                self.logger.info(msg)
                echo(msg)

                stage = StageProcessor(stage_ref, self.context)
                self.in_toto_links.record_stage_start(stage_ref.name)
                self.stage_processor_map[stage_ref] = stage

                result = stage.run()

                if result.is_fail() or result.is_retry():
                    msg = f"Stage {stage_ref.name} failed, processing terminated: {result.message}"
                    self.logger.error(msg=msg)
                    secho(message=f"  {msg}", fg=colors.RED)

                    break

                self._collect_delivered_bom(stage_ref.name)
                self._collect_delivered_bom()
                self.in_toto_links.record_stage_stop(stage_ref.name)

            self.in_toto_links.record_stage_start("_finalize")
            self._collect_delivered_bom()
            self.in_toto_links.record_stage_stop("_finalize")

        failed_jobs = self._summarize_results()
        if failed_jobs > 0:
            result.merge(Result.fail(f"{failed_jobs} failed during this execution"))

        return result
