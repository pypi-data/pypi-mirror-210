"""
Framework for manipulating bundles for airgapped transfers.
"""
from __future__ import annotations

import ctypes
import os
import sys

from pathlib import Path
from platform import python_version
from runpy import run_module
from typing import Optional

from typer import Argument, Option, Typer, echo, secho, style

from hoppr import __version__, main

# Windows flags and types
NT_ENABLE_ECHO_INPUT = 0x0004
NT_ENABLE_LINE_INPUT = 0x0002
NT_ENABLE_PROCESSED_INPUT = 0x0001
NT_CONSOLE_FLAGS = NT_ENABLE_ECHO_INPUT | NT_ENABLE_LINE_INPUT | NT_ENABLE_PROCESSED_INPUT
NT_STD_OUTPUT_HANDLE = ctypes.c_uint(-11)

# Enable ANSI processing on Windows systems
if sys.platform == "win32":  # pragma: no cover
    nt_kernel = ctypes.WinDLL(name="kernel32.dll")

    nt_kernel.SetConsoleMode(nt_kernel.GetStdHandle(NT_STD_OUTPUT_HANDLE), NT_CONSOLE_FLAGS)


ATTESTATION_OPTION: bool = Option(
    False,
    "-a",
    "--attest",
    help="Generate in-toto attestations",
    envvar="HOPPR_ATTESTATION",
)


CREDENTIALS_FILE_OPTION: Path = Option(
    None,
    "-c",
    "--credentials",
    help="Specify credentials config for services",
    envvar="HOPPR_CREDS_CONFIG",
)


FUNCTIONARY_KEY_BUNDLE_OPTION: Optional[Path] = Option(
    None,
    "-fk",
    "--functionary-key",
    help="Path to key used to sign in-toto layout",
    envvar="HOPPR_FUNCTIONARY_KEY",
)


FUNCTIONARY_KEY_GENERATE_LAYOUT_OPTION: Path = Option(
    ...,
    "-fk",
    "--functionary-key",
    help="Path to key used to sign in-toto layout",
    envvar="HOPPR_FUNCTIONARY_KEY",
)


FUNCTIONARY_KEY_PASSWORD_OPTION: str = Option(
    None,
    "-fk-pass",
    "--project-owner-key-password",
    help="Password for project owner key",
    envvar="HOPPR_PROJECT_OWNER_KEY_PASSWORD",
)


FUNCTIONARY_KEY_PROMPT_OPTION: bool = Option(
    False,
    "-p",
    "--prompt",
    help="Prompt user for project owner key's password",
    envvar="HOPPR_PROJECT_OWNER_KEY_PROMPT",
)


LOG_FILE_OPTION: Path = Option(
    None,
    "-l",
    "--log",
    help="File to which log will be written",
    envvar="HOPPR_LOG_FILE",
)


MANIFEST_FILE_ARGUMENT: Path = Argument(
    "manifest.yml",
    help="Path to manifest file",
    expose_value=True,
)


OUTPUT_DIR_OPTION: Path = Option(
    Path(),
    "-o",
    "--output-dir",
    file_okay=False,
    resolve_path=True,
    exists=True,
    show_default=False,
    help="[default: current directory]",
)


PREVIOUS_DELIVERY_OPTION: Path = Option(
    None,
    "-pd",
    "--previous-delivery",
    help="Path to manifest or tar bundle representing a previous delivery",
    envvar="HOPPR_PREVIOUS_DELIVERY",
)


PROJECT_OWNER_KEY_OPTION: Path = Option(
    ...,
    "-pk",
    "--project-owner-key",
    help="Path to key used to sign in-toto layout",
    envvar="HOPPR_PROJECT_OWNER_KEY",
)


PROJECT_OWNER_KEY_PASSWORD_OPTION: str = Option(
    None,
    "-pk-pass",
    "--project-owner-key-password",
    help="Password for project owner key",
    envvar="HOPPR_PROJECT_OWNER_KEY_PASSWORD",
)


PROJECT_OWNER_KEY_PROMPT_OPTION: bool = Option(
    False,
    "-p",
    "--prompt",
    help="Prompt user for project owner key's password",
    envvar="HOPPR_PROJECT_OWNER_KEY_PROMPT",
)


STRICT_OPTION: bool = Option(
    True,
    "--strict/--no-strict",
    help="Utilize only manifest repositories for package collection",
    envvar="HOPPR_STRICT_REPOS",
)


TRANSFER_FILE_OPTION: Path = Option(
    "transfer.yml",
    "-t",
    "--transfer",
    help="Specify transfer config",
    envvar="HOPPR_TRANSFER_CONFIG",
)


VERBOSE_OPTION: bool = Option(
    False,
    "-v",
    "--debug",
    "--verbose",
    help="Enable debug output",
)


app = Typer(
    context_settings=dict(help_option_names=["-h", "--help"]),
    help="Collect, process, & bundle your software supply chain",
    no_args_is_help=True,
)


@app.command()
def bundle(
    # pylint: disable=unused-argument
    # pylint: disable=too-many-arguments
    manifest_file: Path = MANIFEST_FILE_ARGUMENT,
    credentials_file: Path = CREDENTIALS_FILE_OPTION,
    transfer_file: Path = TRANSFER_FILE_OPTION,
    log_file: Path = LOG_FILE_OPTION,
    verbose: bool = VERBOSE_OPTION,
    strict_repos: bool = STRICT_OPTION,
    create_attestations: bool = ATTESTATION_OPTION,
    functionary_key_path: Optional[Path] = FUNCTIONARY_KEY_BUNDLE_OPTION,
    functionary_key_prompt: bool = FUNCTIONARY_KEY_PROMPT_OPTION,
    functionary_key_password: str = FUNCTIONARY_KEY_PASSWORD_OPTION,
    previous_delivery: Path = PREVIOUS_DELIVERY_OPTION,
):  # pragma: no cover
    """
    Run the stages specified in the transfer config
    file on the content specified in the manifest
    """
    main.bundle(**locals())


@app.command()
def validate(
    # pylint: disable=unused-argument
    input_files: list[Path],
    credentials_file: Path = CREDENTIALS_FILE_OPTION,
    transfer_file: Path = TRANSFER_FILE_OPTION,
):  # pragma: no cover
    """
    Validate multiple manifest files for schema errors
    """
    main.validate(**locals())


@app.command()
def generate_layout(
    # pylint: disable=unused-argument
    transfer_file: Path = TRANSFER_FILE_OPTION,
    project_owner_key_path: Path = PROJECT_OWNER_KEY_OPTION,
    functionary_key_path: Path = FUNCTIONARY_KEY_GENERATE_LAYOUT_OPTION,
    project_owner_key_prompt: bool = PROJECT_OWNER_KEY_PROMPT_OPTION,
    project_owner_key_password: str = PROJECT_OWNER_KEY_PASSWORD_OPTION,
):  # pragma: no cover
    """
    Create in-toto layout based on transfer file
    """
    main.generate_layout(**locals())


@app.command()
def generate_schemas(output_dir: Path = OUTPUT_DIR_OPTION):  # pragma: no cover
    """
    Generate schema files from input file models
    """
    os.chdir(output_dir)
    run_module(mod_name="hoppr.models")


@app.command()
def version():
    """
    Print version information for `hoppr`
    """
    # Only print ANSI art on TTY terminals
    if sys.stdout.isatty():
        hippo = Path(__file__).parent / ".." / "resources" / "hoppr-hippo.ansi"
        with hippo.open(mode="rb") as ansi:
            echo(ansi.read())

    secho(f"{style(text='Hoppr Framework Version', fg='green')} : {__version__}")
    secho(f"{style(text='Python Version         ', fg='green')} : {python_version()}")
