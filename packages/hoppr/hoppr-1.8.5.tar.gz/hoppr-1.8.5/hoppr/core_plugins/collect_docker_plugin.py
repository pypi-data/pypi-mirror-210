"""
Collector plugin for docker images
"""

# pylint: disable=too-many-locals

from __future__ import annotations

import re
import urllib.parse

from typing import Any

import hoppr.utils

from hoppr import __version__
from hoppr.base_plugins.collector import SerialCollectorPlugin
from hoppr.base_plugins.hoppr import hoppr_rerunner
from hoppr.models import HopprContext
from hoppr.models.credentials import CredentialRequiredService
from hoppr.models.types import RepositoryUrl
from hoppr.result import Result


class CollectDockerPlugin(SerialCollectorPlugin):
    """
    Collector plugin for docker images
    """

    supported_purl_types = ["docker"]
    required_commands = ["skopeo"]
    products: list[str] = ["docker/*"]
    system_repositories: list[str] = ["https://docker.io/"]
    process_timeout = 300

    def get_version(self) -> str:  # pylint: disable=duplicate-code
        return __version__

    def __init__(self, context: HopprContext, config: dict | None = None) -> None:
        super().__init__(context=context, config=config)
        self.required_commands = (self.config or {}).get("skopeo_command", self.required_commands)

    @hoppr_rerunner
    def collect(self, comp: Any, repo_url: str, creds: CredentialRequiredService | None = None):
        """
        Copy a component to the local collection directory structure
        """
        purl = hoppr.utils.get_package_url(comp.purl)
        version_path = purl.version

        # Determine if purl version contains SHA string, determine proper formatting for skopeo command
        if re.search(r"^(sha256:)?[a-fA-F0-9]{12,64}$", purl.version) is None:
            image_name = f"{purl.name}:{purl.version}"

        elif purl.version.startswith("sha256:"):
            image_name = f"{purl.name}@{purl.version}"
        else:
            image_name = f"{purl.name}@sha256:{purl.version}"
            version_path = f"sha256:{purl.version}"

        source_image = RepositoryUrl(url=repo_url) / (purl.namespace or "") / urllib.parse.quote_plus(image_name)

        version_path = urllib.parse.quote_plus(re.sub(r'^https?://', '', version_path))
        target_dir = self.directory_for(purl.type, repo_url, subdir=purl.namespace)
        target_path = target_dir / f"{urllib.parse.unquote(purl.name)}_{purl.version}"
        destination = f"docker-archive:{target_dir / purl.name}_{version_path}"

        if source_image.scheme != "docker":
            source_image = RepositoryUrl(url=re.sub(r"^.+(?=://)", "docker", str(source_image)))

        self.get_logger().info(msg="Copying docker image:", indent_level=2)
        self.get_logger().info(msg=f"source: {source_image}", indent_level=3)
        self.get_logger().info(msg=f"destination: {destination}", indent_level=3)

        command = [self.required_commands[0], "copy"]

        password_list = []

        if creds is not None:
            password_list = [creds.password.get_secret_value()]
            command.extend(["--src-creds", f"{creds.username}:{creds.password.get_secret_value()}"])

        if re.match("^http://", repo_url):
            command = [*command, "--src-tls-verify=false"]

        command = [*command, urllib.parse.unquote(str(source_image)), destination]

        proc = self.run_command(command, password_list)

        if proc.returncode != 0:
            msg = f"Skopeo failed to copy docker image to {destination}, " + f"return_code={proc.returncode}"
            self.get_logger().debug(msg=msg, indent_level=2)

            if target_path.exists():
                self.get_logger().info(msg="Artifact collection failed, deleting file and retrying", indent_level=2)
                target_path.unlink()

            return Result.retry(message=msg)

        self.set_collection_params(comp, repo_url, target_dir)

        return Result.success(return_obj=comp)
