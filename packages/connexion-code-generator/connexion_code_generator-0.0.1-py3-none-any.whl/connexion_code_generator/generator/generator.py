from __future__ import annotations

import string
from collections import defaultdict
from itertools import pairwise
from pathlib import Path
from typing import Literal

from jinja2 import Environment
from result import Err, Ok, Result

from connexion_code_generator.parser import (
    Header,
    MediaType,
    Operation,
    Parameter,
    Ref,
    RequestBody,
    Response,
    ResponseKeys,
    Schema,
    SecurityRequirement,
)
from connexion_code_generator.parser import OpenAPI30 as OpenAPI
from connexion_code_generator.pkg.exception import enriched_error

from .entities import (
    ArgumentSignature,
    BodyInfo,
    ClassSignature,
    GroupedPaths,
    HTTPMethod,
    ImportSignature,
    MethodInfo,
    MethodSignature,
    ParameterInfo,
    ReturnInfo,
    ReturnSignature,
    SecurityRequirementInfo,
    TemplateData,
    ViewInfo,
)
from .exceptions import (
    BadConfigError,
    BadPathError,
    BadSpecError,
    ExternalRefNotSupportedError,
    NoContentResponseNotSupportedError,
    NotSupportedError,
    OverlappingMethodsError,
    ParamInCookieNotSupportedError,
    RangeResponseNotSupportedError,
    ReferencedBodyNotFoundError,
    ReferencedHeaderNotFoundError,
    ReferencedParameterNotFoundError,
    ReferencedResponseNotFoundError,
    ReferencedSchemaNotFoundError,
    ReferenceNotFoundError,
    SecurityRequirementCombinationMissingInConfigError,
    UndefinedSchemaNotSupportedError,
    UnstructuredMediaSchemaNotSupportedError,
)


class Generator:
    def __init__(
        self,
        spec: OpenAPI,
        security_requirement_mapping: dict[tuple[str, ...], SecurityRequirementInfo],
        dto_module_path: str,
        internal_server_error_response_type: str | None = None,
        class_mode: Literal["protocol", "abstract"] = "abstract",
        sync_mode: Literal["sync", "async"] = "async",
    ) -> None:
        super().__init__()
        self._spec = spec
        self._dto_module_path = dto_module_path
        self._internal_server_error_response_type = internal_server_error_response_type
        self._class_mode: Literal["protocol", "abstract"] = class_mode
        self._sync_mode: Literal["sync", "async"] = sync_mode
        self._security_requirement_mapping = {
            tuple(
                sorted(key)): value for key,
            value in security_requirement_mapping.items()}

        jinja_environment = Environment()  # noqa: S701
        file_dir = Path(__file__).parent

        classes_template_path = file_dir / "class_template.py.jinja"

        with classes_template_path.open() as f:
            self._classes_template = jinja_environment.from_string(f.read())

        if self._spec.security is not None:
            self._default_security_requirements = _extract_security_requirements(self._spec.security)
        else:
            self._default_security_requirements: tuple[str, ...] = ()

    def generate(self) -> Result[str, NotSupportedError | ReferenceNotFoundError | BadSpecError | BadConfigError]:
        match self._check_if_two_path_params_come_back_to_back():
            case Err(e):
                return enriched_error(e)
            case Ok():
                pass

        match self._group_paths():
            case Err(e):
                return enriched_error(e)
            case Ok(grouped_paths):
                pass

        view_info_results = [self._extract_view_info(grouped_path) for grouped_path in grouped_paths]

        for item in view_info_results:
            if isinstance(item, Err):
                return enriched_error(item.err())

        view_infos = [item.unwrap() for item in view_info_results]

        template_data = self._get_template_data(view_infos)

        res = self._classes_template.render(data=template_data)

        return Ok(res)

    def _get_template_data(self, view_infos: list[ViewInfo]) -> TemplateData:
        imports = self._extract_imports(view_infos)
        class_signatures = [
            ClassSignature(
                class_name=view.view_name,
                methods=[
                    MethodSignature(
                        method_name=method.method_type if method.method_type != "list" else "search",
                        arguments=_get_arguments_signature(method),
                        returns=_get_returns_signature(method),
                    ) for method in view.methods
                ],
            ) for view in view_infos
        ]

        return TemplateData(
            class_signatures,
            imports,
            self._sync_mode,
            self._class_mode,
        )

    def _check_if_two_path_params_come_back_to_back(self) -> Result[None, BadPathError]:
        for path in self._spec.paths:
            path_semantic_parts = ["param" if _is_parameter(part) else "not_param" for part in path[1:].split("/")]

            for (p1, p2) in pairwise(path_semantic_parts):
                if p1 == "param" and p2 == "param":
                    return Err(BadPathError(f"Two consequent parameters in path is not supported. {path}"))

        return Ok(None)

    def _group_paths(self) -> Result[list[GroupedPaths], ExternalRefNotSupportedError | OverlappingMethodsError]:
        views: dict[str, GroupedPaths] = {}

        for path, path_spec in sorted(self._spec.paths.items(), key=lambda k: len(k[0].split("/"))):
            path_ends_with_parameter = _does_path_ends_with_parameter(path)
            view_name = _get_full_view_name(path)

            if isinstance(path_spec, Ref):
                return Err(ExternalRefNotSupportedError(f"Path `{path}` is using an external reference."))

            path_methods_with_none: set[HTTPMethod | None] = {
                "get" if path_spec.get is not None and path_ends_with_parameter else None,
                "list" if path_spec.get is not None and not path_ends_with_parameter else None,
                "put" if path_spec.put is not None else None,
                "post" if path_spec.post is not None else None,
                "delete" if path_spec.delete is not None else None,
                "options" if path_spec.options is not None else None,
                "head" if path_spec.head is not None else None,
                "patch" if path_spec.patch is not None else None,
                "trace" if path_spec.trace is not None else None,
            }

            path_methods: set[HTTPMethod] = {method for method in path_methods_with_none if method is not None}

            if (existing_view := views.get(view_name)) is None:
                views[view_name] = GroupedPaths(view_name, (path, ), path_methods)
                continue

            if (shared_methods := existing_view.methods.intersection(path_methods)) != set():
                return Err(
                    OverlappingMethodsError(
                        f"Immediate sub paths cannot share method. paths `{path}` & `{existing_view.paths[0]}` share {shared_methods}",   # noqa: E501
                    ),
                )

            views[view_name] = GroupedPaths(view_name, (existing_view.paths[0], path),
                                            existing_view.methods.union(path_methods))

        return Ok(list(views.values()))

    def _extract_view_info(self, grouped_path: GroupedPaths) -> Result[ViewInfo, NotSupportedError | ReferenceNotFoundError | BadConfigError]:  # noqa: E501
        methods: list[MethodInfo] = []
        for path in grouped_path.paths:
            path_ends_with_parameter = _does_path_ends_with_parameter(path)
            path_spec = self._spec.paths[path]

            if isinstance(path_spec, Ref):
                return Err(ExternalRefNotSupportedError(f"Path `{path}` is using an external reference."))

            match self._convert_parameters_specs(path_spec.parameters):
                case Err(e):
                    return enriched_error(e, f"path: {path}")
                case Ok(path_parameters):
                    pass

            path_methods: dict[HTTPMethod, Operation | None] = {
                "get": path_spec.get if path_spec.get is not None and path_ends_with_parameter else None,
                "list": path_spec.get if path_spec.get is not None and not path_ends_with_parameter else None,
                "put": path_spec.put if path_spec.put is not None else None,
                "post": path_spec.post if path_spec.post is not None else None,
                "delete": path_spec.delete if path_spec.delete is not None else None,
                "options": path_spec.options if path_spec.options is not None else None,
                "head": path_spec.head if path_spec.head is not None else None,
                "patch": path_spec.patch if path_spec.patch is not None else None,
                "trace": path_spec.trace if path_spec.trace is not None else None,
            }

            for method, method_spec in path_methods.items():
                if method_spec is None:
                    continue

                if method_spec.security is not None:
                    security_requirements = _extract_security_requirements(method_spec.security)
                else:
                    security_requirements = self._default_security_requirements

                match self._convert_security_requirements(security_requirements):
                    case Err(e):
                        return enriched_error(e, "Bad config")
                    case Ok(security_requirement_info):
                        pass

                match self._convert_body_spec(method_spec.request_body):
                    case Err(e):
                        return enriched_error(e, f"path: {path}")
                    case Ok(body):
                        pass

                match self._convert_parameters_specs(method_spec.parameters):
                    case Err(e):
                        return enriched_error(e, f"path: {path}")
                    case Ok(method_parameters):
                        pass

                combined_parameters = _combine_path_and_method_parameters(path_parameters, method_parameters)

                match self._convert_return_spec(method_spec.responses):
                    case Err(e):
                        return enriched_error(e, f"path: {path}")
                    case Ok(responses_info):
                        pass

                methods.append(MethodInfo(method, security_requirement_info, body, combined_parameters, responses_info))

        return Ok(ViewInfo(grouped_path.view_name, grouped_path.paths, methods))

    def _convert_security_requirements(self, security_requirements_names: tuple[str, ...]) -> Result[SecurityRequirementInfo | None, SecurityRequirementCombinationMissingInConfigError]:  # noqa: E501
        if security_requirements_names == ():
            return Ok(None)

        sorted_security_requirements_names = tuple(sorted(security_requirements_names))
        res = self._security_requirement_mapping.get(sorted_security_requirements_names)
        if res is None:
            return enriched_error(SecurityRequirementCombinationMissingInConfigError(
                f"Missing combination for {sorted_security_requirements_names}"))

        return Ok(res)

    def _convert_parameters_specs(self, parameters: list[Parameter | Ref] | None) -> Result[list[ParameterInfo], NotSupportedError | ReferenceNotFoundError]:  # noqa: E501
        if parameters is None:
            return Ok([])

        parameters_spec_results = (self._dereference_parameter(param) for param in parameters)
        parameters_results = [
            self._convert_parameter_spec(param_or_error.unwrap()) if isinstance(param_or_error, Ok) else param_or_error
            for param_or_error in parameters_spec_results
        ]

        for ok_or_error in parameters_results:
            if isinstance(ok_or_error, Err):
                return Err(ok_or_error.err())

        return Ok([ok_or_error.unwrap() for ok_or_error in parameters_results])

    def _convert_parameter_spec(self, param_spec: Parameter) -> Result[ParameterInfo, NotSupportedError | ReferenceNotFoundError]:  # noqa: E501
        if param_spec.in_ == "cookie":
            return Err(ParamInCookieNotSupportedError(f"Param {param_spec.name} is located in cookie."))

        if param_spec.schema_ is None:
            return Err(UndefinedSchemaNotSupportedError("Parameter is missing schema"))

        match self._dereference_schema(param_spec.schema_):
            case Err(e):
                return enriched_error(e)
            case Ok(param_schema):
                pass

        return Ok(
            ParameterInfo(
                param_spec.in_,
                param_spec.name,
                _convert_data_type_name(param_schema),
                param_spec.required))

    def _convert_body_spec(self, body_spec: RequestBody | Ref | None) -> Result[BodyInfo | None, ReferenceNotFoundError | NotSupportedError]:  # noqa: E501
        if body_spec is None:
            return Ok(None)

        match self._dereference_body(body_spec):
            case Err(e):
                return enriched_error(e)
            case Ok(body_spec):
                pass

        match self._extract_data_type_name_from_media_type(body_spec.content["application/json"], dest="body"):
            case Err(e):
                return enriched_error(e)
            case Ok(data_type_name):
                pass

        return Ok(BodyInfo(data_type_name, body_spec.required))

    def _convert_return_spec(self, responses_specs: dict[ResponseKeys, Response | Ref]) -> Result[list[ReturnInfo], NotSupportedError | ReferenceNotFoundError]:  # noqa: E501
        return_infos: list[ReturnInfo] = []
        include_500_response = False
        for code, response_spec in responses_specs.items():
            if code in {"default", "1XX", "2XX", "3XX", "4XX", "5XX"}:
                return Err(RangeResponseNotSupportedError(f"Range response is not supported: {code}"))

            if code == "500":
                include_500_response = True

            match self._dereference_response(response_spec):
                case Err(e):
                    return enriched_error(e, f"Code: {code}")
                case Ok(response_spec):
                    pass

            if response_spec.content is None:
                return Err(NoContentResponseNotSupportedError("No content response not supported"))

            match self._extract_data_type_name_from_media_type(response_spec.content["application/json"], dest="response"):  # noqa: E501
                case Err(e):
                    return enriched_error(e, f"Code: {code}")
                case Ok(data_type_name):
                    pass

            if response_spec.headers is None:
                return_infos.append(ReturnInfo(int(code), data_type_name, None))
                continue

            header_infos: dict[str, str] = {}
            for header_key, header_spec in response_spec.headers.items():
                match self._dereference_header(header_spec):
                    case Err(e):
                        return enriched_error(e, f"Code: {code}")
                    case Ok(header_spec):
                        pass

                if header_spec.schema_ is None:
                    return Err(UndefinedSchemaNotSupportedError(f"Header schema is not defined. {header_key}"))

                match self._dereference_schema(header_spec.schema_):
                    case Err(e):
                        return enriched_error(e, f"Code: {code}")
                    case Ok(header_schema):
                        pass

                header_infos[header_key] = _convert_data_type_name(header_schema)

            return_infos.append(ReturnInfo(int(code), data_type_name, header_infos))

        if include_500_response is False and self._internal_server_error_response_type is not None:
            return_infos.append(ReturnInfo(500, self._internal_server_error_response_type, None))

        return Ok(return_infos)

    def _extract_data_type_name_from_media_type(self, media_type: MediaType, dest: Literal["body", "response"]) -> Result[str, ReferenceNotFoundError | NotSupportedError]:  # noqa: E501
        if dest == "body":
            return Ok("object")

        match media_type.schema_:
            case None:
                return Err(UndefinedSchemaNotSupportedError("MediaType is missing schema"))

            case Ref():
                match self._dereference_schema(media_type.schema_):
                    case Err(e):
                        return enriched_error(e)
                    case Ok(no_ref_body_schema):
                        pass

            case Schema() as no_ref_body_schema:
                pass

        match no_ref_body_schema.type_:
            case "object":
                data_type_name = "dict[str, object]"
            case "array":
                data_type_name = "list[object]"
            case _ as t:
                return Err(UnstructuredMediaSchemaNotSupportedError(
                    f"Unstructured media schema not supported. type: {t}"))

        if isinstance(media_type.schema_, Ref):
            data_type_name = _snake_case_to_pascal_case(media_type.schema_.ref.rsplit("/", 1)[-1])

        return Ok(data_type_name)

    def _dereference_header(self, header_or_ref: Header | Ref) -> Result[Header, ReferencedHeaderNotFoundError]:
        if not isinstance(header_or_ref, Ref):
            return Ok(header_or_ref)

        ref_name = header_or_ref.ref.rsplit("/", 1)[-1]
        if self._spec.components is None or self._spec.components.headers is None:
            return Err(ReferencedHeaderNotFoundError(
                f"Failed to find the reference to header for: {header_or_ref.ref}"))

        resolved_header = self._spec.components.headers.get(ref_name)

        if resolved_header is None:
            return Err(ReferencedHeaderNotFoundError(
                f"Failed to find the reference to header for: {header_or_ref.ref}"))

        if isinstance(resolved_header, Ref):
            return self._dereference_header(resolved_header)

        return Ok(resolved_header)

    def _dereference_response(self, response_or_ref: Response |
                              Ref) -> Result[Response, ReferencedResponseNotFoundError]:
        if not isinstance(response_or_ref, Ref):
            return Ok(response_or_ref)

        ref_name = response_or_ref.ref.rsplit("/", 1)[-1]
        if self._spec.components is None or self._spec.components.responses is None:
            return Err(ReferencedResponseNotFoundError(
                f"Failed to find the reference to response for: {response_or_ref.ref}"))

        resolved_response = self._spec.components.responses.get(ref_name)

        if resolved_response is None:
            return Err(ReferencedResponseNotFoundError(
                f"Failed to find the reference to response for: {response_or_ref.ref}"))

        if isinstance(resolved_response, Ref):
            return self._dereference_response(resolved_response)

        return Ok(resolved_response)

    def _dereference_parameter(self, parameter_or_ref: Parameter |
                               Ref) -> Result[Parameter, ReferencedParameterNotFoundError]:
        if not isinstance(parameter_or_ref, Ref):
            return Ok(parameter_or_ref)

        ref_name = parameter_or_ref.ref.rsplit("/", 1)[-1]
        if self._spec.components is None or self._spec.components.parameters is None:
            return Err(ReferencedParameterNotFoundError(
                f"Failed to find the reference to parameter for: {parameter_or_ref.ref}"))

        resolved_parameter = self._spec.components.parameters.get(ref_name)

        if resolved_parameter is None:
            return Err(ReferencedParameterNotFoundError(
                f"Failed to find the reference to parameter for: {parameter_or_ref.ref}"))

        if isinstance(resolved_parameter, Ref):
            return self._dereference_parameter(resolved_parameter)

        return Ok(resolved_parameter)

    def _dereference_body(self, body_or_ref: RequestBody | Ref) -> Result[RequestBody, ReferencedBodyNotFoundError]:
        if not isinstance(body_or_ref, Ref):
            return Ok(body_or_ref)

        ref_name = body_or_ref.ref.rsplit("/", 1)[-1]
        if self._spec.components is None or self._spec.components.request_bodies is None:
            return Err(ReferencedBodyNotFoundError(f"Failed to find the reference to body for: {body_or_ref.ref}"))

        resolved_body = self._spec.components.request_bodies.get(ref_name)

        if resolved_body is None:
            return Err(ReferencedBodyNotFoundError(f"Failed to find the reference to body for: {body_or_ref.ref}"))

        if isinstance(resolved_body, Ref):
            return self._dereference_body(resolved_body)

        return Ok(resolved_body)

    def _dereference_schema(self, schema_or_ref: Schema | Ref) -> Result[Schema, ReferencedSchemaNotFoundError]:
        if not isinstance(schema_or_ref, Ref):
            return Ok(schema_or_ref)

        ref_name = schema_or_ref.ref.rsplit("/", 1)[-1]
        if self._spec.components is None or self._spec.components.schemas is None:
            return Err(ReferencedSchemaNotFoundError(
                f"Failed to find the reference to schema for: {schema_or_ref.ref}"))

        resolved_schema = self._spec.components.schemas.get(ref_name)

        if resolved_schema is None:
            return Err(ReferencedSchemaNotFoundError(
                f"Failed to find the reference to schema for: {schema_or_ref.ref}"))

        if isinstance(resolved_schema, Ref):
            return self._dereference_schema(resolved_schema)

        return Ok(resolved_schema)

    def _extract_imports(self, view_infos: list[ViewInfo]) -> list[ImportSignature]:
        imports: set[ImportSignature | None] = set()

        for view_info in view_infos:
            for method in view_info.methods:
                if method.security_requirement is not None:
                    imports.add(self._extract_import(method.security_requirement.parameter_data_type))

                if method.body is not None:
                    imports.add(self._extract_import(method.body.data_type_name))

                for param in method.parameters:
                    imports.add(self._extract_import(param.data_type_name))

                for res in method.returns:
                    imports.add(self._extract_import(res.data_type_name))

        return [imp for imp in imports if imp is not None]

    def _extract_import(self, type_name: str) -> ImportSignature | None:
        match type_name:
            case "date":
                return ImportSignature("datetime", "date")
            case "datetime":
                return ImportSignature("datetime", "datetime")
            case "UUID":
                return ImportSignature("uuid", "UUID")
            case "None":
                return None

            case _:
                pass

        if type_name[0] not in string.ascii_uppercase:
            return None

        return ImportSignature(self._dto_module_path, type_name)


def _get_arguments_signature(method: MethodInfo) -> list[ArgumentSignature]:
    result: list[ArgumentSignature] = []

    if method.security_requirement is not None:
        result.append(
            ArgumentSignature(
                argument_name=method.security_requirement.parameter_name,
                argument_type=method.security_requirement.parameter_data_type,
            ),
        )

    for parameter in method.parameters:
        if parameter.in_ == "header":
            # TODO: We don't support header parameter auto injection yet
            continue

        if parameter.required is True:
            result.append(
                ArgumentSignature(
                    argument_name=parameter.name if not parameter.name.endswith("[]") else parameter.name[:-2],
                    argument_type=parameter.data_type_name,
                ),
            )

    if method.body is not None and method.body.required is True:
        result.append(
            ArgumentSignature(
                argument_name="body",
                argument_type=method.body.data_type_name,
            ),
        )

    for parameter in method.parameters:
        if parameter.in_ == "header":
            # TODO: We don't support header parameter auto injection yet
            continue

        if parameter.required is False:
            result.append(
                ArgumentSignature(
                    argument_name=parameter.name if not parameter.name.endswith("[]") else parameter.name[:-2],
                    argument_type=f"{parameter.data_type_name} | None",
                    argument_default="None",
                ),
            )

    if method.body is not None and method.body.required is False:
        result.append(
            ArgumentSignature(
                argument_name="body",
                argument_type=f"{method.body.data_type_name} | None",
                argument_default="None",
            ),
        )

    return result


def _get_returns_signature(method: MethodInfo) -> list[ReturnSignature]:
    # TODO: group similar data_type, return headers into a single one
    codes_grouped_by_return_type_headers: dict[str, list[int]] = defaultdict(list)
    for r in method.returns:
        codes_grouped_by_return_type_headers[f"{r.data_type_name}-{r.returned_headers}"].append(r.code)

    grouped_codes = {
        tuple(codes): [r for r in method.returns if r.code in codes][0]
        for codes in codes_grouped_by_return_type_headers.values()
    }

    return [
        ReturnSignature(
            data_type_name=r.data_type_name,
            codes=codes,
            returned_headers=r.returned_headers,
        )
        for codes, r in grouped_codes.items()
    ]


def _convert_data_type_name(schema: Schema) -> str:
    match schema.type_:
        case "string":
            if schema.format_ == "date":
                return "date"

            if schema.format_ == "datetime":
                return "datetime"

            if schema.format_ == "UUID":
                return "UUID"

            return "str"

        case "number":
            if schema.format_ == "datetime":
                return "datetime"

            return "float"

        case "integer":
            if schema.format_ == "datetime":
                return "datetime"

            return "int"

        case "boolean":
            return "bool"

        case "null":
            return "None"

        case "array":
            return "list[object]"

        case "object":
            return "dict[str, object]"

        case None:
            return "None"


def _combine_path_and_method_parameters(path_parameters: list[ParameterInfo], method_parameters: list[ParameterInfo]) -> list[ParameterInfo]:  # noqa: E501
    path_parameters_indicators = {(p.name, p.in_) for p in path_parameters}
    method_parameters_indicators = {(p.name, p.in_) for p in method_parameters}
    common_parameters_indicators = path_parameters_indicators.intersection(method_parameters_indicators)

    non_overridden_path_parameters = [p for p in path_parameters if (p.name, p.in_) not in common_parameters_indicators]

    return method_parameters + non_overridden_path_parameters


def _extract_security_requirements(security_requirement: list[SecurityRequirement]) -> tuple[str, ...]:
    return tuple(list(sec_req.keys())[0] for sec_req in security_requirement)


def _get_full_view_name(path: str) -> str:
    non_parameter_path_parts = [_to_camel_case(part) for part in path.split("/") if not _is_parameter(part)]
    return f"{''.join(non_parameter_path_parts)}View"


def _to_camel_case(inp: str) -> str:
    return "".join(_capitalize(x) for x in inp.split("_"))


def _capitalize(inp: str) -> str:
    if len(inp) == 0:
        return ""

    return f"{inp[0].upper()}{inp[1:]}"


def _is_parameter(path_part: str) -> bool:
    if len(path_part) == 0:
        return False

    return bool(path_part[0] == "{" and path_part[-1] == "}")


def _does_path_ends_with_parameter(path: str) -> bool:
    last_part = path.rsplit("/", 1)[-1]
    return _is_parameter(last_part)


def _snake_case_to_pascal_case(inp: str) -> str:
    return "".join(_capitalize(p) for p in inp.split("_"))
