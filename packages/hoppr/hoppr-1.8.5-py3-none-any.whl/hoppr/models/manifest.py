"""
Manifest file data model
"""
from __future__ import annotations

import uuid

from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, ClassVar, Literal, MutableMapping

from hoppr_cyclonedx_models.cyclonedx_1_4 import Component as ComponentSpecVersion14
from hoppr_cyclonedx_models.cyclonedx_1_4 import CyclonedxSoftwareBillOfMaterialsStandard as SbomSpecVersion14
from hoppr_cyclonedx_models.cyclonedx_1_4 import ExternalReference as ExternalReferenceSpecVersion14
from hoppr_cyclonedx_models.cyclonedx_1_4 import Property as PropertySpecVersion14
from packageurl import PackageURL
from pydantic import AnyUrl, Extra, Field, FileUrl, HttpUrl, NoneStr, create_model, validator
from pydantic.main import ModelMetaclass
from requests import HTTPError
from typer import secho

import hoppr.net
import hoppr.oci_artifacts
import hoppr.utils

from hoppr.constants import BomProps
from hoppr.exceptions import HopprLoadDataError
from hoppr.models.base import HopprBaseModel, HopprBaseSchemaModel
from hoppr.models.types import PurlType, RepositoryUrl

if TYPE_CHECKING:
    from pydantic.typing import DictStrAny


class Repository(HopprBaseModel):
    """
    Repository data model
    """

    url: RepositoryUrl
    description: NoneStr = None

    @validator("url", pre=True)
    @classmethod
    def validate_url(cls, url: str | RepositoryUrl) -> RepositoryUrl:
        """
        Validate URL string
        """
        if isinstance(url, str):
            url = RepositoryUrl(url=url)

        return url


# Dynamic Repositories model with PurlType values as attribute names
purl_type_repo_mapping = {str(purl_type): (list[Repository], Field([], unique_items=True)) for purl_type in PurlType}
RepositoriesMetaclass: ModelMetaclass = create_model(  # type: ignore[call-overload]
    "RepositoriesMetaclass", __base__=HopprBaseModel, **purl_type_repo_mapping
)


class Repositories(RepositoriesMetaclass):  # type: ignore[misc, valid-type]
    """
    Repositories data model
    """

    # pylint: disable=too-few-public-methods

    def __getitem__(self, item: str | PurlType) -> list[Repository]:
        return getattr(self, str(item), [])

    def __setitem__(self, item: str | PurlType, value: list[Repository]) -> None:
        setattr(self, str(item), value)

    def __iter__(self):
        for purl_type in PurlType:
            yield (purl_type, self[purl_type])


class LocalFile(HopprBaseModel):
    """
    LocalFile data model
    """

    local: Path


class OciFile(HopprBaseModel):
    """
    OciFile data model
    """

    oci: AnyUrl | str


class UrlFile(HopprBaseModel):
    """
    UrlFile data model
    """

    url: HttpUrl | FileUrl | AnyUrl | str


class SearchSequence(HopprBaseModel):
    """
    SearchSequence data model
    """

    version: Literal["v1"]
    repositories: list[RepositoryUrl | str] = []


IncludeRef = Annotated[LocalFile | UrlFile, Field(..., description="Reference to a local or remote manifest file")]
Includes = Annotated[list[IncludeRef], Field(..., description="List of manifest files to load")]
SbomRef = Annotated[LocalFile | OciFile | UrlFile, Field(..., description="Reference to a local or remote SBOM file")]
Sboms = Annotated[list[SbomRef], Field(..., description="List of SBOMs to process")]
SbomRefMap = Annotated[MutableMapping[SbomRef, "Sbom"], Field(...)]
ComponentPurlMap = Annotated[MutableMapping[str, "Component"], Field(...)]


class ExternalReference(HopprBaseModel, ExternalReferenceSpecVersion14):
    """
    ExternalReference data model derived from HopprBaseModel
    """

    class Config(HopprBaseModel.Config):  # pylint: disable=too-few-public-methods
        "Config for ExternalReference model"
        extra = Extra.allow


class Property(HopprBaseModel, PropertySpecVersion14):
    """
    Property data model derived from HopprBaseModel
    """


class Component(HopprBaseModel, ComponentSpecVersion14):
    """
    Component data model derived from HopprBaseModel
    """

    class Config(HopprBaseModel.Config):  # pylint: disable=too-few-public-methods
        "Config for Component model"
        extra = Extra.allow

    components: list[Component] | None = Field(None)  # type: ignore[assignment]
    externalReferences: list[ExternalReference] | None = Field(None)  # type: ignore[assignment]
    properties: list[Property] | None = Field(None)  # type: ignore[assignment]

    # Attributes not included in schema
    component_lookup: ClassVar[ComponentPurlMap] = {}

    @classmethod
    def find(cls, purl_string: str) -> Component | None:
        """
        Look up Component object by package URL string

        Args:
            purl_string (str): Package URL string to look up

        Returns:
            Component | None: Component object if found, otherwise None
        """
        return cls.component_lookup.get(purl_string)


class Sbom(HopprBaseModel, SbomSpecVersion14):
    """
    Sbom data model derived from HopprBaseModel
    """

    class Config(HopprBaseModel.Config):  # pylint: disable=too-few-public-methods
        "Config for generic Sbom model"

        extra = Extra.allow

    components: list[Component] = Field(...)  # type: ignore[assignment]
    externalReferences: list[ExternalReference] | None = Field(None)  # type: ignore[assignment]

    # Attributes not included in schema
    loaded_sboms: ClassVar[SbomRefMap] = {}
    consolidated_sbom: ClassVar[Sbom]

    @classmethod
    def find(cls, ref_type: Literal["local", "oci", "url"], location: str | Path) -> Sbom | None:
        """
        Look up SBOM object by reference

        Args:
            ref_type (Literal["local", "oci", "url"]): Type of SBOM reference
            location (str | Path): Location of SBOM reference

        Returns:
            Sbom | None: SBOM object if found, otherwise None
        """
        match ref_type:
            case "local":
                return cls.loaded_sboms.get(LocalFile(local=Path(location)), None)
            case "oci":
                return cls.loaded_sboms.get(OciFile(oci=str(location)), None)
            case "url":
                return cls.loaded_sboms.get(UrlFile(url=str(location)), None)
            case _:
                return None


class ManifestFile(HopprBaseSchemaModel):
    """
    Data model to describe a single manifest file
    """

    kind: Literal["Manifest"]
    repositories: Repositories = Field(..., description="Maps supported PURL types to package repositories/registries")
    includes: Includes = []
    sboms: Sboms = []

    @classmethod
    def parse_file(cls, path: str | Path, *args, **kwargs) -> ManifestFile:  # pylint: disable=unused-argument
        """
        Override to resolve local file paths relative to manifest file
        """
        path = Path(path).resolve()

        data = hoppr.utils.load_file(path)
        if not isinstance(data, dict):
            raise TypeError("Local file content was not loaded as dictionary")

        # Resolve local file path references relative to manifest file path
        for sbom in data.get("sboms", []):
            if "local" in sbom:
                sbom["local"] = str((path.parent / sbom["local"]).resolve())

        for include in data.get("includes", []):
            if "local" in include:
                include["local"] = str((path.parent / include["local"]).resolve())

        return cls(**data)

    @classmethod
    def parse_obj(cls, obj: DictStrAny) -> ManifestFile:
        """
        Override to remove local file paths that can't be resolved
        """
        for include in list(obj.get("includes", [])):
            if "local" in include and not Path(include["local"]).is_absolute():
                secho(f"Skipping local include: relative path '{include['local']}' cannot be resolved", fg="yellow")
                obj["includes"].remove(include)

        for sbom in list(obj.get("sboms", [])):
            if "local" in sbom and not Path(sbom["local"]).is_absolute():
                secho(f"Skipping local SBOM: relative path '{sbom['local']}' cannot be resolved", fg="yellow")
                obj["sboms"].remove(sbom)

        return cls(**obj)


IncludeRefMap = Annotated[MutableMapping[IncludeRef, ManifestFile], Field(...)]


class Manifest(ManifestFile):
    """
    Manifest data model that generates lookups for `includes` and `sboms` references
    """

    # Attributes not included in schema
    loaded_manifests: ClassVar[IncludeRefMap] = {}

    @validator("includes", allow_reuse=True, always=True)
    @classmethod
    def populate_loaded_manifests(cls, includes: Includes, values: DictStrAny) -> Includes:
        """
        Validator that automatically loads manifest from local file or URL into lookup dictionary
        """
        for include_ref in includes:
            if include_ref not in cls.loaded_manifests:
                match include_ref:
                    case LocalFile():
                        cls.loaded_manifests[include_ref] = ManifestFile.parse_file(include_ref.local)
                        loaded = cls.load(include_ref.local)
                    case UrlFile():
                        data = hoppr.net.load_url(include_ref.url)
                        if not isinstance(data, dict):
                            raise TypeError("URL manifest include was not loaded as dictionary")

                        cls.loaded_manifests[include_ref] = ManifestFile.parse_obj(data)
                        loaded = cls.load(include_ref.url)
                    case _:
                        continue

                # Add all repositories of current manifest to included manifest
                for purl_type in PurlType:
                    # List of repos for purl type in current manifest
                    combined_repos = deepcopy(values["repositories"][str(purl_type)])

                    # List of repos for purl type in included manifest
                    include_repos: list[Repository] = getattr(loaded.repositories, str(purl_type), [])

                    # Append each included manifest repo to list of current manifest repos
                    for repo in include_repos:
                        if repo not in combined_repos:
                            combined_repos.append(repo)

                    # Set included manifest repos to the combined list of repos for purl type
                    setattr(loaded.repositories, str(purl_type), combined_repos)

                cls.loaded_manifests[include_ref] = loaded

        return includes

    @validator("sboms", allow_reuse=True, always=True)
    @classmethod
    def populate_loaded_sboms(cls, sboms: Sboms, values: DictStrAny) -> Sboms:
        """
        Validator that automatically loads SBOM from local file or URL into lookup dictionary
        """
        if not hasattr(Sbom, "consolidated_sbom"):
            Sbom.consolidated_sbom = Sbom(
                specVersion="1.4",
                version=1,
                bomFormat="CycloneDX",  # type: ignore[arg-type]
                serialNumber=uuid.uuid4().urn,
                components=[],
                externalReferences=[],
            )

        for sbom_ref in sboms:
            if sbom_ref not in Sbom.loaded_sboms:
                loaded = cls._load_sbom(sbom_ref)
                ref_url = cls._get_ref_url(sbom_ref)

                if loaded is None or ref_url is None:
                    continue

                loaded_sn = getattr(loaded, "serialNumber")

                # Merge current SBOM metadata into consolidated SBOM
                Sbom.consolidated_sbom.externalReferences.append(  # type: ignore[union-attr]
                    ExternalReference(
                        url=ref_url,
                        type="bom",  # type: ignore[arg-type]
                        comment=loaded_sn,
                        hashes=None,
                    )
                )

                for component in loaded.components or []:
                    purl_str = getattr(component, "purl", None)
                    if purl_str is None:
                        continue

                    purl_type = hoppr.utils.get_package_url(purl_str).type

                    if component.properties is None:
                        component.properties = []

                    # Generate the repository search sequence
                    search_sequence = SearchSequence(
                        version="v1", repositories=[str(repo.url) for repo in values["repositories"][purl_type]]
                    )

                    # Add repository search sequence as component property
                    component.properties.append(
                        Property(name=BomProps.COMPONENT_SEARCH_SEQUENCE, value=search_sequence.json())
                    )

                    # Add external reference to SBOM file that includes this component
                    if component.externalReferences is None:
                        component.externalReferences = []

                    component.externalReferences.append(
                        ExternalReference(
                            url=ref_url, comment=loaded_sn, type="bom", hashes=None  # type: ignore[arg-type]
                        )
                    )

                    # Merge component into consolidated SBOM
                    cls._add_component(component)

                Sbom.loaded_sboms[sbom_ref] = loaded

        return sboms

    @classmethod
    def _add_component(cls, component: Component) -> None:
        # Remove purl qualifiers for later comparison
        purl: PackageURL = hoppr.utils.get_package_url(component.purl)
        purl.qualifiers.clear()
        purl_str = purl.to_string()

        loaded = Component.find(purl_str)
        # Merge component into previously loaded component
        if loaded is not None:
            loaded.externalReferences = hoppr.utils.dedup_list(
                [*(loaded.externalReferences or []), *(component.externalReferences or [])]
            )

            if loaded.properties is None:
                loaded.properties = []  # pragma: no cover

            for prop in component.properties or []:
                if prop.name not in [loaded_prop.name for loaded_prop in loaded.properties]:
                    loaded.properties.append(prop)
        else:
            Sbom.consolidated_sbom.components.append(component)
            Component.component_lookup[purl_str] = component

    @classmethod
    def _get_ref_url(cls, sbom_ref: SbomRef) -> str | None:
        match sbom_ref:
            case LocalFile():
                return sbom_ref.local.as_uri()
            case OciFile():
                return sbom_ref.oci
            case UrlFile():
                return sbom_ref.url
            case _:
                return None

    @classmethod
    def _load_sbom(cls, sbom_ref: SbomRef) -> Sbom | None:
        match sbom_ref:
            case LocalFile():
                return Sbom.parse_file(sbom_ref.local)
            case OciFile():
                data = hoppr.oci_artifacts.pull_artifact(sbom_ref.oci)
                if not isinstance(data, dict):
                    raise TypeError("OCI URL SBOM file was not loaded as dictionary")

                return Sbom.parse_obj(data)
            case UrlFile():
                data = hoppr.net.load_url(sbom_ref.url)
                if not isinstance(data, dict):
                    raise TypeError("URL SBOM file was not loaded as dictionary")

                return Sbom.parse_obj(data)
            case _:
                return None

    @classmethod
    def find(cls, ref_type: Literal["local", "url"], location: str | Path) -> ManifestFile | None:
        """
        Lookup manifest object by include reference

        Args:
            ref_type (Literal["local", "url"]): Type of include
            location (str | Path): Path to included manifest

        Returns:
            ManifestFile | None: Manifest object if found, otherwise None
        """
        match ref_type:
            case "local":
                return cls.loaded_manifests.get(LocalFile(local=Path(location)))
            case "url":
                return cls.loaded_manifests.get(UrlFile(url=str(location)))
            case _:
                return None

    @classmethod
    def load(cls, source: str | Path | DictStrAny) -> Manifest:
        """
        Load manifest from local file, URL, or dict
        """
        match source:
            case dict():
                data = source
            case Path():
                path = Path(source).resolve()
                manifest_file = cls.parse_file(path)
                local_ref = LocalFile(local=path)
                cls.loaded_manifests[local_ref] = manifest_file
                data = manifest_file.dict(by_alias=True)
            case str():
                try:
                    include_dict = hoppr.net.load_url(source)
                    if not isinstance(include_dict, dict):
                        raise TypeError("URL manifest include was not loaded as dictionary")

                    manifest_file = cls.parse_obj(include_dict)
                    url_ref = UrlFile(url=source)
                    cls.loaded_manifests[url_ref] = manifest_file
                except (HopprLoadDataError, HTTPError) as ex:
                    raise HopprLoadDataError from ex

                data = manifest_file.dict(by_alias=True)

        return cls(**data)
