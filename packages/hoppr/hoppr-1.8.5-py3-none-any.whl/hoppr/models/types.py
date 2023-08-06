"""
Enumeration to indicate how a plugin may change a BOM
"""
from __future__ import annotations

import re

from typing import TYPE_CHECKING, Any

from hoppr_cyclonedx_models.cyclonedx_1_4 import Component
from hoppr_cyclonedx_models.cyclonedx_1_4 import CyclonedxSoftwareBillOfMaterialsStandard as Bom
from pydantic import Field, SecretStr, root_validator
from pydantic_yaml import YamlIntEnum, YamlStrEnum

from hoppr.models.base import HopprBaseModel

if TYPE_CHECKING:
    from pydantic.typing import DictStrAny


class BomAccess(YamlIntEnum):
    """
    Enumeration to indicate how a plugin may change a BOM
    """

    # pylint: disable=duplicate-code
    NO_ACCESS = 0
    COMPONENT_ACCESS = 1
    FULL_ACCESS = 2

    def has_access_to(self, obj: Any) -> bool:
        """
        Determine whether the specified value allows updates to an object
        """
        match self:
            case BomAccess.NO_ACCESS:
                return obj is None
            case BomAccess.COMPONENT_ACCESS:
                return isinstance(obj, Component)
            case BomAccess.FULL_ACCESS:
                return isinstance(obj, Bom)


class PurlType(YamlStrEnum):
    """
    Enumeration of supported purl types
    """

    # pylint: disable=duplicate-code
    DEB = "deb"
    DOCKER = "docker"
    GENERIC = "generic"
    GIT = "git"
    GITHUB = "github"
    GITLAB = "gitlab"
    GOLANG = "golang"
    HELM = "helm"
    MAVEN = "maven"
    NPM = "npm"
    PYPI = "pypi"
    RAW = "raw"
    REPO = "repo"
    RPM = "rpm"


class RepositoryUrl(HopprBaseModel):
    """
    RepositoryUrl data model
    """

    class Config(HopprBaseModel.Config):  # pylint: disable=too-few-public-methods
        "RepositoryUrl model config"
        allow_mutation = False
        validate_assignment = True

    url: str = Field(...)
    scheme: str | None = Field(default=None)
    username: str | None = Field(default=None)
    password: SecretStr | str | None = Field(default=None)
    hostname: str | None = Field(default=None)
    port: int | None = Field(default=None)
    path: str | None = Field(default=None)
    query: str | None = Field(default=None)
    fragment: str | None = Field(default=None)
    netloc: str | None = Field(default=None, exclude=True)

    @root_validator(pre=True)
    @classmethod
    def validate_model(cls, values: DictStrAny):
        """
        Validate RepositoryUrl model
        """
        if not (url := values.get("url")):
            raise ValueError("Input parameter `url` must be a non-empty string")

        if url.endswith(":"):
            url = f"{url}//"

        if not (
            match := re.search(
                pattern=(
                    r"^((?P<scheme>[^:/?#]+):(?=//))?(//)?((("
                    r"?P<username>[^:]+)(?::("
                    r"?P<password>[^@]+)?)?@)?("
                    r"?P<hostname>[^@/?#:]*)(?::("
                    r"?P<port>\d+)?)?)?("
                    r"?P<path>[^?#]*)(\?("
                    r"?P<query>[^#]*))?(#("
                    r"?P<fragment>.*))?"
                ),
                string=url,
            )
        ):
            raise ValueError(f"Not a valid URL: {url}")

        values.update({name: value for name, value in match.groupdict().items() if value is not None})

        if values.get("port"):
            values["port"] = int(values["port"])

        if isinstance(password := values.get("password"), str):
            password = SecretStr(password)

        auth = ":".join(filter(None, [values.get("username"), values.get("password")]))
        host_port = ":".join(filter(None, [values.get("hostname"), str(values.get("port") or "")]))
        values["netloc"] = "@".join(filter(None, [auth, host_port]))

        values["url"] = f"{values['scheme']}://" if values.get("scheme") else ""
        values["url"] = f"{values['url']}{values['netloc']}"
        values["url"] = "/".join(filter(None, [values["url"], values["path"].strip("/") if values.get("path") else ""]))
        values["url"] = "?".join(filter(None, [values["url"], values.get("query")]))
        values["url"] = "#".join(filter(None, [values["url"], values.get("fragment")]))

        return values

    def __repr__(self) -> str:
        props = ", ".join(f'{name}={repr(value)}' for name, value in dict(self).items())
        return f"RepositoryUrl({props})"

    def __str__(self) -> str:
        return self.url

    def __truediv__(self, other: str) -> RepositoryUrl:
        return self.join(other)

    def __itruediv__(self, other: str) -> RepositoryUrl:
        # Convert all instances of two or more slashes to single slash
        other = "/".join(filter(None, other.split("/")))
        return self.join(other)

    def join(self, other: str) -> RepositoryUrl:  # pylint: disable=missing-docstring
        # Convert two or more slashes to single slash (ignores `://`)
        joined = "/".join([re.sub(pattern="(?<!:)//+", repl="/", string=self.url), other.strip("/")])
        return type(self)(url=joined)
