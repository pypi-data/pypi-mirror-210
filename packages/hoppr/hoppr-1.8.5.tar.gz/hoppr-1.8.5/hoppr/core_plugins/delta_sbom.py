"""
Plugin to remove SBOM components that are specified by a "previous" SBOM
"""
import io
import tarfile

from copy import deepcopy
from pathlib import Path

from packageurl import PackageURL

from hoppr import __version__
from hoppr.base_plugins.hoppr import HopprPlugin, hoppr_process
from hoppr.exceptions import HopprError
from hoppr.models.manifest import Component, Manifest, Sbom
from hoppr.models.types import BomAccess
from hoppr.result import Result
from hoppr.utils import dedup_list, get_package_url, load_string


class DeltaSbom(HopprPlugin):
    """
    Plugin to remove SBOM components that are specified by a "previous" SBOM
    """

    bom_access = BomAccess.FULL_ACCESS
    products: list[str] = ["generic/_metadata_/_previous_bom.json"]

    def get_version(self) -> str:
        return __version__

    @hoppr_process
    def pre_stage_process(self):
        """
        Tar-up the context.collect_root_dir directory
        """

        if self.context.previous_delivery is not None:
            previous_source = str(self.context.previous_delivery)
        elif self.config is None or self.config.get("previous") is None:
            return Result.success(
                "No previously delivered bundle specified for delta bundle. All components will be delivered"
            )
        else:
            previous_source = self.config.get("previous")

        if not Path(previous_source).exists():  # pyright: ignore[reportGeneralTypeIssues]
            return Result.fail(f"Previous source file \"{previous_source}\" not found.")

        self.get_logger().info(f"Creating delta/update SBOM, previous SBOM being retrieved from {previous_source}")

        previous_sbom = self._get_previous_bom(previous_source)  # pyright: ignore[reportGeneralTypeIssues]

        target_dir = self.context.collect_root_dir / "generic" / "_metadata_"
        target_dir.mkdir(parents=True, exist_ok=True)

        with (target_dir / "_previous_bom.json").open(mode="w", encoding="utf-8") as bom_data:
            bom_data.write(previous_sbom.json(exclude_none=True, by_alias=True, indent=2))

        delta_sbom = deepcopy(self.context.delivered_sbom)
        delta_sbom.components = []

        for new_comp in self.context.delivered_sbom.components or []:
            include_component = True
            for prev_comp in previous_sbom.components or []:
                if DeltaSbom._component_match(new_comp, prev_comp):
                    include_component = False
                    break

            if include_component:
                self.get_logger().debug(f"Including purl {new_comp.purl}", indent_level=1)
                delta_sbom.components.append(new_comp)

        self.get_logger().info(f"Input sbom has {len(self.context.delivered_sbom.components)} components")
        self.get_logger().info(f"Prev  sbom has {len(previous_sbom.components)} components")
        self.get_logger().info(f"Delta sbom has {len(delta_sbom.components)} components")

        if len(delta_sbom.components) == 0:
            return Result.fail(f"No components updated since \"{previous_source}\".")

        return Result.success(
            f"Delivering updates for {len(delta_sbom.components)} of "
            f"{len(self.context.delivered_sbom.components)} components.",
            return_obj=delta_sbom,
        )

    @staticmethod
    def _get_previous_bom(source: str) -> Sbom:
        try:
            Manifest.load(Path(source))
            return Sbom.consolidated_sbom
        except (TypeError, UnicodeDecodeError):
            pass

        with tarfile.open(source) as tar:
            buffer = tar.extractfile("./generic/_metadata_/_consolidated_bom.json")

            if buffer is None:
                raise HopprError("Unable to extract BOM file from tar")

            with io.TextIOWrapper(buffer) as bom_file:
                content: str = bom_file.read()
                bom_dict = load_string(content)
                if not isinstance(bom_dict, dict):
                    raise HopprError("Invalid BOM file retrieved from tar")
                return Sbom(**bom_dict)

    @staticmethod
    def _purl_match(new_purl: PackageURL, prev_purl: PackageURL) -> bool:

        if (
            new_purl.name != prev_purl.name
            or new_purl.type != prev_purl.type
            or (new_purl.namespace or "") != (prev_purl.namespace or "")
            or (new_purl.version or "") != (prev_purl.version or "")
            or (new_purl.subpath or "") != (prev_purl.subpath or "")
        ):
            return False

        qual_keys = list(new_purl.qualifiers.keys()) or []
        qual_keys.extend(list(prev_purl.qualifiers.keys()) or [])

        for key in dedup_list(qual_keys):
            if new_purl.qualifiers.get(key) != prev_purl.qualifiers.get(key):
                return False

        return True

    @staticmethod
    def _component_match(new_comp: Component, prev_comp: Component) -> bool:

        new_purl: PackageURL = get_package_url(new_comp.purl)
        prev_purl: PackageURL = get_package_url(prev_comp.purl)

        if not DeltaSbom._purl_match(new_purl, prev_purl):
            return False

        hash_matches = 0

        for new_hash in new_comp.hashes or []:
            for prev_hash in prev_comp.hashes or []:
                if new_hash.alg.value != prev_hash.alg.value:
                    continue
                if new_hash.content != prev_hash.content:
                    return False
                hash_matches += 1

        if hash_matches > 0:
            return True

        if new_purl.version is None or new_purl.version == "latest":
            return False

        return True
