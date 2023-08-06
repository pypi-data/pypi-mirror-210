"""
Base model for Hoppr config files
"""
from __future__ import annotations

from typing import Literal

from pydantic import Extra, Field, validator
from pydantic_yaml import YamlModel


class Metadata(YamlModel):
    """
    Metadata data model
    """

    name: str
    version: str | int
    description: str


class HopprBaseModel(YamlModel):
    """
    Base Hoppr data model
    """

    class Config:  # pylint: disable=too-few-public-methods
        """Config for HopprBaseModel"""

        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        extra = Extra.forbid
        use_enum_values = True

    def __hash__(self) -> int:
        """
        Define to test equality or uniqueness between objects
        """
        return hash(repr(self))


class HopprBaseSchemaModel(HopprBaseModel):
    """
    Base Hoppr config file schema model
    """

    kind: Literal["Credentials", "Manifest", "Transfer"] = Field(..., description="Data model/schema kind")
    metadata: Metadata | None = Field(None, description="Metadata for the file")
    schema_version: str = Field(..., alias="schemaVersion", title="Schema Version")

    @validator("kind", allow_reuse=True, pre=True)
    @classmethod
    def validate_kind(cls, kind: str) -> str:
        """
        Return supplied `kind` value with only first letter capitalized
        """
        return kind.capitalize()
