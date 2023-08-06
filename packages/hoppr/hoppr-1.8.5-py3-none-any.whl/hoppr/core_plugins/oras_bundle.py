"""
Plugin to create oras oci bundle
"""
import re

from datetime import datetime
from pathlib import Path
from typing import Any, List, Tuple

import oras.client
import oras.defaults
import oras.oci
import oras.provider
import oras.utils

from oras.container import Container

from hoppr import __version__
from hoppr.base_plugins.hoppr import HopprPlugin, hoppr_process
from hoppr.core_plugins.oras_registry import Registry
from hoppr.exceptions import HopprCredentialsError, HopprPluginError
from hoppr.models import HopprContext as Context
from hoppr.models.credentials import Credentials
from hoppr.result import Result


class OrasBundlePlugin(HopprPlugin):
    """
    Plugin to create an Oras file upload

    This plug-in supports the following config values:
        - oras_artifact_name: Name of oras artifact.
        - oras_artifact_version: Version of artifact.
        - oras_registry: Registry to push Oras Artifact.
    """

    def get_version(self) -> str:
        return __version__

    def __init__(self, context: Context, config: Any = None) -> None:
        super().__init__(context=context, config=config)
        self._results: List[Tuple[Path, Result]] = []
        self.failures = 0
        self.retries = 0
        self.finalize_failures = 0

    @hoppr_process
    def post_stage_process(self):
        """
        Bundle up the context.collect_root_dir directory and push to registry
        """

        root_dir = self.context.collect_root_dir

        if self.config is not None:
            oras_artifact_name = self.config.get("oras_artifact_name")
            if oras_artifact_name is None:
                raise HopprPluginError("Failed to collect oras artifact name from config.")
            oras_artifact_version = self.config.get("oras_artifact_version")
            if oras_artifact_version is None:
                raise HopprPluginError("Failed to collect oras artifact version from config.")
            oras_registry = self.config.get("oras_registry")
            if oras_registry is None:
                raise HopprPluginError("Failed to collect oras registry from config.")
            if oras_registry.startswith('http'):
                raise HopprPluginError("Oras Registry name should just be a hostname and not contain a protocol scheme")
        else:
            self.get_logger().info("Oras config not correct")
            return Result.fail()

        self.get_logger().info(
            "Bundling collected artifacts into oras artifact " f"{oras_artifact_name}:{oras_artifact_version}"
        )
        self.get_logger().flush()

        if ':' in oras_registry:
            cred = Credentials.find(oras_registry.split(':', maxsplit=1)[0])
        else:
            cred = Credentials.find(oras_registry)
        if cred is None:
            raise HopprCredentialsError("Credentials must not be empty for Oras Bundle Plugin")

        # Setup Oras Client
        client = self.get_oras_client(username=cred.username, password=cred.password.get_secret_value())

        # Gather list of files to upload
        file_list = [str(file) for file in root_dir.rglob("*") if file.is_file()]
        archives = self.get_files_from_root_dir(file_list=file_list, root_dir=root_dir)
        archives = self.verify_contents(self.context.delivered_sbom.components, archives)

        # Push should be relative to cache context
        with oras.utils.workdir(root_dir):
            uri = f'{oras_artifact_name}:{oras_artifact_version}'
            container = Container(name=uri, registry=oras_registry)
            client.push(container, archives, logger=self.get_logger())
        self.get_logger().info(f"Uploaded: {uri}")
        return Result.success()

    def get_oras_client(self, username: str, password: str):
        """
        Consistent method to get an oras client

        Args:
            username (str): username for registry
            password (str): password for registry

        Returns:
            hoppr.core_plugins.oras_registry.Registry: Override of oras registry object
        """
        reg = Registry()
        if username and password:
            self.get_logger().info("Found username and password for basic auth")
            reg.set_basic_auth(username, password)
        else:
            raise HopprPluginError("Username and Password not set in the credentials.yml.")
        return reg

    def get_files_from_root_dir(self, file_list: list, root_dir: Path) -> list:
        """
        Helper function to get file array list and build archives

        Args:
            root_dir (Path): _description_

        Returns:
            list: A list of dictionaries
        """
        # Create lookup of archives - relative path and mediatype
        archives = []
        now = datetime.now()

        for filename in file_list:
            media_type = "application/vnd.oci.image.layer.v1.tar"
            size = Path(filename).stat().st_size  # bytes
            annotations = {"creationTime": str(now), "size": str(size)}
            if str(root_dir / "generic" / "_metadata_" / "_delivered_bom.json") == filename:
                media_type = "application/vnd.cyclonedx"
            elif str(root_dir / "generic" / "_metadata_" / "_consolidated_bom.json") == filename:
                media_type = "application/vnd.cyclonedx"
                media_type = 'application/vnd.cyclonedx'
            archives.append(
                {
                    "path": filename,
                    "title": filename.replace(f"{root_dir}/", "", -1),
                    "media_type": media_type,
                    "annotations": annotations,
                }
            )
        return archives

    def verify_contents(self, components: list, archives: list) -> list:
        """
        Verify that components are upgraded

        Args:
            components (list): Cyclonedx Components
            archives (list): List of dictionaries

        Raises:
            HopprPluginError: Hoppr plugin error
        """
        total_components = len(components)
        self.get_logger().info(f"Total components: {total_components}")
        self.get_logger().info(f"Total archives: {len(archives)}")
        self.get_logger().flush()
        for component in components:
            pattern = f"{component.name}[-|_]{component.version}"
            scope = str(component.scope)
            for archive in archives:
                result = re.match(pattern, archive['path'])
                if result:
                    if 'excluded' in scope:
                        self.get_logger().info(f"Found scope {component.scope}, removing component from archive.")
                        self.get_logger().flush()
                        archives.remove(archive)
        self.get_logger().info("Components validated in bundle for upload.")
        self.get_logger().flush()
        return archives
