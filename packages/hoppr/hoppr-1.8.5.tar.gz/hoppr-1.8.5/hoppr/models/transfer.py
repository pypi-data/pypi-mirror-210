"""
Transfer file data model
"""
from __future__ import annotations

import math
import re

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, Literal, Pattern

from pydantic import ConstrainedStr, Field, validator

from hoppr.models.base import HopprBaseModel, HopprBaseSchemaModel

if TYPE_CHECKING:
    from pydantic.typing import DictStrAny
else:
    DictStrAny = dict[str, Any]


class StageName(ConstrainedStr):
    """
    Constrained string type for stage key name
    """

    regex: Pattern[str] = re.compile(pattern=r"^[A-Za-z_][\w\s]*$")
    min_length: int = 1


class Plugin(HopprBaseModel):
    """
    Plugin data model
    """

    name: str = Field(..., description="Name of plugin")
    config: DictStrAny | None = Field(None, description="Mapping of additional plugin configuration settings to values")


Plugin.update_forward_refs()


class ComponentCoverage(Enum):
    """
    Enumeration to indicate how often each component should be processed
    """

    OPTIONAL = (0, math.inf)
    EXACTLY_ONCE = (1, 1)
    AT_LEAST_ONCE = (1, math.inf)
    NO_MORE_THAN_ONCE = (0, 1)

    def __init__(self, min_allowed: int, max_allowed: int):
        self.min_value = min_allowed
        self.max_value = max_allowed

    def __str__(self) -> str:
        return str(self.name)

    def accepts_count(self, count: int) -> bool:
        """
        Identifies whether a specified count is acceptable for this coverage value
        """
        return self.min_value <= count <= self.max_value


class Stage(HopprBaseModel):
    """
    Stage data model
    """

    component_coverage: Literal["AT_LEAST_ONCE", "EXACTLY_ONCE", "NO_MORE_THAN_ONCE", "OPTIONAL"] | None = Field(
        default=None, exclude=True, description="Defines how often components should be processed"
    )
    plugins: list[Plugin] = Field(..., description="List of Hoppr plugins to load")


class StageRef(Stage):
    """
    StageRef data model
    """

    name: StageName


Stages = Annotated[dict[StageName, Stage], ...]


class TransferFile(HopprBaseSchemaModel):
    """
    Transfer file data model
    """

    kind: Literal["Transfer"]
    max_processes: int | None = Field(3, description="Max processes to create when running Hoppr application")
    stages: Stages = Field(..., description="Mapping of stage names to property definitions")


class Transfer(TransferFile):
    """
    Transfer data model
    """

    stages: list[StageRef]  # type: ignore[assignment]

    @validator("stages", allow_reuse=True, pre=True)
    @classmethod
    def validate_stages(cls, stages: DictStrAny) -> list[StageRef]:
        """
        Transform Stages into list of StageRef objects
        """
        stage_refs: list[StageRef] = []

        add_delta = True

        for stage_name, stage in stages.items():
            stage["name"] = stage_name
            stage_refs.append(StageRef.parse_obj(stage))

            for plugin in stage["plugins"]:
                if plugin["name"] == "hoppr.core_plugins.delta_sbom":
                    add_delta = False

        if add_delta:
            stage_refs.insert(
                0,
                StageRef(
                    name=StageName("_delta_sbom_"),
                    plugins=[
                        Plugin(
                            name="hoppr.core_plugins.delta_sbom",
                            config=None,
                        )
                    ],
                ),
            )

        return stage_refs

    @classmethod
    def load(cls, source: str | Path | DictStrAny) -> Transfer:
        """
        Load transfer file from local path or dict
        """
        match source:
            case dict():
                return cls.parse_obj(source)
            case str() | Path():
                return cls.parse_file(source)
            case _:
                raise TypeError("'source' argument must be one of: 'str', 'Path', 'dict[str, Any]'")
