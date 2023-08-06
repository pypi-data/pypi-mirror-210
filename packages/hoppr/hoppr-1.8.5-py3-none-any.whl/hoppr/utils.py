"""
Hoppr utility functions
"""
from __future__ import annotations

import importlib
import inspect

from abc import ABCMeta
from functools import cache
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Type

from packageurl import PackageURL
from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError as YAMLParserError
from ruamel.yaml.scanner import ScannerError as YAMLScannerError

from hoppr.exceptions import HopprLoadDataError, HopprPluginError

if TYPE_CHECKING:
    from hoppr.base_plugins.hoppr import HopprPlugin
    from hoppr.models import HopprContext


def _class_in_module(cls_type: ABCMeta, plugin_module: ModuleType):
    """
    Determines if the specified object is a class
    defined in the module
    """
    return inspect.isclass(cls_type) and cls_type.__module__ == plugin_module.__name__


def plugin_class(plugin_name: str) -> Type[HopprPlugin]:
    """
    return a concrete class of an object defined by a plugin name

    Assumes the specified plugin will define exactly one concrete class, which
    will be instaniated using a default constructor (i.e., one with no parameters).
    """
    try:
        plugin_module = importlib.import_module(name=plugin_name)
    except ModuleNotFoundError as mnfe:
        raise ModuleNotFoundError(f"Unable to locate plug-in {plugin_name}: {mnfe}") from mnfe

    plugin_cls = None

    for cls_name, cls_type in inspect.getmembers(plugin_module, inspect.isclass):
        if _class_in_module(cls_type, plugin_module):
            if plugin_cls is not None:
                raise HopprPluginError(
                    f"Multiple candidate classes defined in {plugin_name}: {plugin_cls.__name__}, {cls_name}"
                )

            plugin_cls = cls_type

    if plugin_cls is None:
        raise HopprPluginError(f"No class definition found in in {plugin_name}.")

    return plugin_cls


def plugin_instance(plugin_name: str, context: HopprContext, config: Any = None):
    """
    Create an instance of an object defined by a plugin name

    Assumes the specified plugin will define exactly one concrete class, which
    will be instaniated using a default constructor (i.e., one with no parameters).
    """
    plugin_cls = plugin_class(plugin_name)

    return plugin_cls(context=context, config=config)


def load_string(contents: str) -> dict | list | None:
    """
    Return a YAML or JSON formatted string as a dict
    """
    if not contents.strip():
        raise HopprLoadDataError("Empty string cannot be parsed.")

    # Replace tab characters with spaces to prevent parsing errors
    contents = contents.replace("\t", "  ")
    loaded_contents: dict | list | None = None

    try:
        # Applicable to both YAML and JSON formats since valid JSON data is also valid YAML
        yaml = YAML(typ="safe", pure=True)
        contents = contents.replace("\t", "  ")
        loaded_contents = yaml.load(contents)

        # yaml.safe_load will sometimes return a single string rather than the required structure
        if isinstance(loaded_contents, str):
            raise HopprLoadDataError("Expected dictionary or list, but contents were loaded and returned as string")
    except (YAMLParserError, YAMLScannerError) as ex:
        raise HopprLoadDataError("Unable to recognize data as either json or yaml") from ex
    except HopprLoadDataError as ex:
        raise HopprLoadDataError from ex

    return loaded_contents


def load_file(input_file_path: Path) -> dict | list | None:
    """
    Load file content (either JSON or YAML) into a dict
    """

    if not input_file_path.is_file():
        raise HopprLoadDataError(f"{input_file_path} is not a file, cannot be opened.")

    with input_file_path.open(mode="r", encoding="utf-8") as input_file:
        content: str = input_file.read()
        if not content.strip():
            raise HopprLoadDataError(f"File {input_file_path} is empty.")

    return load_string(content)


def dedup_list(list_in: list[Any]) -> list[Any]:
    """
    De-duplicate a list
    """
    return list(dict.fromkeys(list_in)) if list_in is not None else []


def obscure_passwords(command_list: list[str], sensitive_args: list[str] | None = None) -> str:
    """
    Returns an input string with any specified passwords hidden
    """

    password_list: list[str] = sensitive_args if sensitive_args is not None else []
    obscured_command_list: list[str] = []

    for arg in command_list:
        # Quote arguments that contain spaces
        if " " in arg:
            arg = f'"{arg}"'

        # Replace password string(s) in argument
        for password in password_list:
            if password is not None and len(password) > 0:
                arg = arg.replace(password, "[masked]")

        obscured_command_list.append(arg)

    return " ".join(obscured_command_list)


def remove_empty(directory: Path) -> set[Path]:
    """
    Removes empty folders given the directory including parent folders
    """
    deleted: set[Path] = set()

    if not directory.exists():
        raise FileNotFoundError()

    for subdir in directory.iterdir():
        if subdir.is_dir():
            deleted.update(remove_empty(subdir))

    if directory.is_dir() and not any(directory.iterdir()):
        directory.rmdir()
        deleted.add(directory)

    return deleted


@cache
def get_package_url(purl_string: str) -> PackageURL:
    """
    Get the PackageURL for a given purl_string and store it in a cache for improved performance.

    Args:
        purl_string (str): The string representation of a Package URL

    Returns:
        PackageURL: The object representation of a PackageURL

    """
    return PackageURL.from_string(purl_string)  # pyright: ignore[reportGeneralTypeIssues]
