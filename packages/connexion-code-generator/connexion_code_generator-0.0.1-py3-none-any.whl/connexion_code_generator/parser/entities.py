from __future__ import annotations

from typing import Any, Literal

import pydantic
from pydantic import BaseModel, EmailStr, Field, HttpUrl

from .enums import ResponseKeys

SecurityRequirement = dict[str, list[str]]


class SecuritySchemeBase(BaseModel):
    type_: Literal["apiKey", "http", "oauth2", "openIdConnect"] = Field(alias="type")
    description: str | None = None


class APIKeySecurityScheme(SecuritySchemeBase):
    type_: Literal["apiKey"] = Field(alias="type")
    name: str
    in_: Literal["query", "header", "cookie"] = Field(alias="in")


class HTTPSecurityScheme(SecuritySchemeBase):
    type_: Literal["http"] = Field(alias="type")
    scheme_: Literal["basic", "bearer"] = Field(alias="scheme")
    bearer_format: str | None = Field(default=None, alias="bearerFormat")


class OAuth2SecurityScheme(SecuritySchemeBase):
    type_: Literal["oauth2"] = Field(alias="type")
    # TODO: Add flows: OAuthFlows


class OpenIdConnectSecurityScheme(SecuritySchemeBase):
    type_: Literal["openIdConnect"] = Field(alias="type")
    open_id_connect_url: HttpUrl = Field(alias="openIdConnectUrl")


SecurityScheme = APIKeySecurityScheme | HTTPSecurityScheme | OAuth2SecurityScheme | OAuth2SecurityScheme


class Ref(BaseModel, frozen=True):
    ref: str = Field(alias="$ref")


class Schema(BaseModel):
    type_: Literal["string", "number", "integer", "object", "array",
                   "boolean", "null"] | None = Field(default=None, alias="type")
    format_: str | None = Field(default=None, alias="format")
    enum: list[str] | None = None
    # TODO: Here we don't care about the rest of Schema, and it's really big, so for now we'll ignore it


class MediaType(BaseModel):
    schema_: Ref | Schema | None = Field(default=None, alias="schema")
    # TODO: Add example, examples, and encoding


class Header(BaseModel):
    description: str | None = None
    required: bool = False
    deprecated: bool = False
    allow_empty_value: bool | None = Field(default=None, alias="allowEmptyValue")
    style: Literal["form", "simple"] = "simple"
    explode: bool | None = None
    allow_reserved: bool = Field(default=False, alias="allowReserved")
    schema_: Ref | Schema | None = Field(default=None, alias="schema")
    # TODO: more correct default values based on `in`, `style` and `schema`
    # TODO: Add example and examples


class Response(BaseModel):
    description: str
    headers: dict[str, Header | Ref] | None = None
    # TODO: In our application all requests are JSON, so we'll ignore rest
    content: dict[Literal["application/json"], MediaType] | None = None
    # TODO: Add links: dict[str, Link | Ref] | None = None


class RequestBody(BaseModel):
    description: str | None = None
    required: bool = False
    # TODO: In our application all requests are JSON, so we'll ignore rest
    content: dict[Literal["application/json"], MediaType]


class Parameter(BaseModel):
    name: str
    in_: Literal["query", "header", "path", "cookie"] = Field(alias="in")
    description: str | None = None
    required: bool
    deprecated: bool = False
    allow_empty_value: bool | None = Field(default=None, alias="allowEmptyValue")
    style: Literal["form", "simple"] = Field("")
    explode: bool | None = None
    allow_reserved: bool = Field(default=False, alias="allowReserved")
    schema_: Ref | Schema | None = Field(default=None, alias="schema")

    @pydantic.root_validator
    def get_style(cls, values: dict[str, Any]) -> dict[str, Any]:  # noqa: N805
        if values.get("style") is not None:
            return values

        if values.get("in_") is None:
            return values

        if values["in_"] in ["query", "cookie"]:
            values["style"] = "form"
        else:
            values["style"] = "simple"

        return values

    # TODO: more correct default values based on `in`, `style` and `schema`
    # TODO: Add example and examples


class ServerVariable(BaseModel, frozen=True):
    enum: tuple[str, ...] | None = None
    default: str
    description: str | None = None


class Server(BaseModel, frozen=True):
    url: HttpUrl
    description: str | None = None
    variables: dict[str, ServerVariable] | None = None


class Operation(BaseModel):
    tags: tuple[str, ...] | None = None
    summary: str | None = None
    description: str | None = None
    # TODO: Add external_docs: ExternalDocumentation | None = Field(default=None, alias="externalDocs")
    operation_id: str | None = Field(default=None, alias="operationId")
    parameters: list[Parameter | Ref] | None = None
    request_body: RequestBody | Ref | None = Field(default=None, alias="requestBody")
    responses: dict[ResponseKeys, Response | Ref]
    # TODO: Add callbacks: dict[str, Callback | Ref] | None = Field(default=None)
    deprecated: bool = False
    security: list[SecurityRequirement] | None = None
    servers: list[Server] | None = None


class License(BaseModel, frozen=True):
    name: str
    url: HttpUrl | None = None


class Contact(BaseModel, frozen=True):
    name: str | None = None
    url: HttpUrl | None = None
    email: EmailStr | None = None


class Tag(BaseModel, frozen=True):
    name: str
    description: str | None = None
    # TODO: Add external_docs: ExternalDocumentation | None = Field(default=None, alias="externalDocs")


class Components(BaseModel):
    schemas: dict[str, Ref | Schema] | None = None
    responses: dict[str, Response | Ref] | None = None
    parameters: dict[str, Parameter | Ref] | None = None
    # TODO: Add examples: dict[str, Example| Ref] | None = None
    request_bodies: dict[str, RequestBody | Ref] | None = Field(default=None, alias="requestBodies")
    headers: dict[str, Header | Ref] | None = None
    security_schemes: dict[str, SecurityScheme | Ref] | None = Field(default=None, alias="securitySchemes")
    # TODO: Add links: dict[str, Link | Ref] | None = None
    # TODO: Add callbacks: dict[str, Callback | Ref] | None = None


class PathItem(BaseModel):
    summary: str | None = None
    description: str | None = None
    get: Operation | None = None
    put: Operation | None = None
    post: Operation | None = None
    delete: Operation | None = None
    options: Operation | None = None
    head: Operation | None = None
    patch: Operation | None = None
    trace: Operation | None = None
    servers: tuple[Server, ...] | None = None
    parameters: list[Parameter | Ref] | None = None


class Info(BaseModel, frozen=True):
    title: str
    description: str | None = None
    terms_of_service: HttpUrl | None = Field(default=None, alias="termsOfService")
    contact: Contact | None = None
    license_: License | None = Field(default=None, alias="license")
    version: str


class OpenAPI30(BaseModel):
    openapi: Literal["3.0.0", "3.0.1", "3.0.2", "3.0.3"]
    info: Info
    servers: tuple[Server, ...] | None = None
    paths: dict[str, PathItem | Ref]
    components: Components | None = None
    security: list[SecurityRequirement] | None = None
    tags: list[Tag]
    # TODO: Add external_docs: ExternalDocumentation | None = Field(default=None, alias="externalDocs")
