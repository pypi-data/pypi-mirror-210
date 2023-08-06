"""
Collector plugin for git repositories
"""
from __future__ import annotations

import os
import re

from pathlib import Path

from packageurl import PackageURL  # type: ignore[import]

from hoppr import __version__
from hoppr.base_plugins.collector import SerialCollectorPlugin
from hoppr.base_plugins.hoppr import hoppr_rerunner
from hoppr.models import HopprContext
from hoppr.models.credentials import CredentialRequiredService
from hoppr.models.manifest import Component
from hoppr.result import Result


class CollectGitPlugin(SerialCollectorPlugin):
    """
    Class to copy git repositories

    configuration options:
    config:
      depth: all, 1, or any int > 1

    """

    supported_purl_types = ["git", "gitlab", "github"]
    required_commands = ["git"]
    products: list[str] = ["git/*", "gitlab/*", "github/*"]

    def get_version(self) -> str:  # pylint: disable=duplicate-code
        return __version__

    def __init__(self, context: HopprContext, config: dict | None = None) -> None:
        super().__init__(context=context, config=config)
        if self.config is not None and "git_command" in self.config:
            self.required_commands = [self.config["git_command"]]

    @hoppr_rerunner
    def collect(self, comp: Component, repo_url: str, creds: CredentialRequiredService | None = None) -> Result:
        """
        Collect git repository
        """
        purl: PackageURL = PackageURL.from_string(comp.purl)  # pyright: ignore[reportGeneralTypeIssues]

        source_url = os.path.join(repo_url, purl.namespace, purl.name)

        self.get_logger().info(msg=f"Cloning {source_url}", indent_level=2)

        # Only reference the namespace.  The actual clone creates the named directory
        target_dir = self.directory_for(purl.type, repo_url, subdir=purl.namespace)

        git_result = self.git_clone(tmp_dir=target_dir, source_url=source_url, source_creds=creds, comp=comp)
        if not git_result.is_success():
            return git_result

        git_result = self.git_update(target_dir, purl.name)
        if not git_result.is_success():
            return git_result

        self.set_collection_params(comp, repo_url, target_dir)

        return Result.success(return_obj=comp)

    def git_clone(
        self,
        tmp_dir: Path,
        source_url: str,
        source_creds: CredentialRequiredService | None,
        comp: Component,
    ) -> Result:
        """
        Git clone
        """
        git_src = source_url
        password_list: list[str] = []
        if re.match("^https?://", git_src) and source_creds is not None:
            git_src = git_src.replace("://", f"://{source_creds.username}@", 1)
            if source_creds.password:
                git_src = git_src.replace("@", f":{source_creds.password.get_secret_value()}@")
                password_list = [source_creds.password.get_secret_value()]

        if git_src.startswith("ssh://") and source_creds is not None:
            git_src = git_src.replace("ssh://", f"ssh://{source_creds.username}@")

        if not git_src.endswith(".git"):
            git_src += ".git"

        opts: list[str] = []
        if str(comp.version).strip():
            opts.extend(("--branch", str(comp.version)))

        # Default depth
        depth = "1"
        if self.config is not None:
            # Allow for further depth default to 1
            depth = self.config.get("depth", depth)

        # Recognize the 'all' keyword as requesting all history
        if depth.lower() != "all":
            opts.extend(("--depth", depth))

        # Command
        command = [self.required_commands[0], "clone", *opts, git_src]

        # Only clone with a depth of one and reference the version specified.
        result = self.run_command(
            command,
            password_list,
            cwd=tmp_dir,
        )
        if result.returncode != 0:
            msg = f"Failed to clone {source_url}"
            self.get_logger().debug(msg=msg, indent_level=2)
            return Result.retry(message=msg)

        return Result.success()

    def git_update(self, tmp_dir: Path, name_git: str) -> Result:
        """
        Git update-server-info
        """
        repo_dir = tmp_dir / name_git

        # Make the clone usable as a remote
        result = self.run_command(
            [self.required_commands[0], "update-server-info"],
            cwd=repo_dir,
        )

        if result.returncode != 0:
            msg = "Failed to make the clone usable as a remote"
            self.get_logger().debug(msg=msg, indent_level=2)
            return Result.retry(message=msg)

        return Result.success()
