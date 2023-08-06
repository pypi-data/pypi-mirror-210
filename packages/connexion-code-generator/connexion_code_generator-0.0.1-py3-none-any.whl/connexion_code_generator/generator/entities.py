from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

HTTPMethod = Literal[
    "get",
    "list",
    "put",
    "post",
    "delete",
    "options",
    "head",
    "patch",
    "trace",
]


@dataclass
class SecurityRequirementInfo:
    parameter_name: str
    parameter_data_type: str


@dataclass(eq=True, frozen=True)
class GroupedPaths:
    view_name: str
    paths: tuple[str] | tuple[str, str]
    methods: set[HTTPMethod]


@dataclass
class ParameterInfo:
    in_: Literal["query", "header", "path"]
    name: str
    data_type_name: str
    required: bool


@dataclass
class BodyInfo:
    data_type_name: str
    required: bool


@dataclass
class ReturnInfo:
    code: int
    data_type_name: str
    returned_headers: dict[str, str] | None


@dataclass
class MethodInfo:
    method_type: HTTPMethod
    security_requirement: SecurityRequirementInfo | None
    body: BodyInfo | None
    parameters: list[ParameterInfo]
    returns: list[ReturnInfo]


@dataclass
class ViewInfo:
    view_name: str
    paths: tuple[str] | tuple[str, str]
    methods: list[MethodInfo]


@dataclass
class ArgumentSignature:
    argument_name: str
    argument_type: str
    argument_default: str | None = None


@dataclass
class ReturnSignature:
    data_type_name: str
    codes: tuple[int, ...]
    returned_headers: dict[str, str] | None


@dataclass
class MethodSignature:
    method_name: str
    arguments: list[ArgumentSignature]
    returns: list[ReturnSignature]


@dataclass
class ClassSignature:
    class_name: str
    methods: list[MethodSignature]


@dataclass(eq=True, frozen=True)
class ImportSignature:
    from_: str
    import_: str


@dataclass
class TemplateData:
    classes: list[ClassSignature]
    imports: list[ImportSignature]
    sync_mode: Literal["sync", "async"]
    class_mode: Literal["protocol", "abstract"]
