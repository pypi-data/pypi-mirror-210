from __future__ import annotations


class GeneratorBaseError(Exception):
    pass


class BadConfigError(GeneratorBaseError):
    pass


class SecurityRequirementCombinationMissingInConfigError(BadConfigError):
    pass


class BadSpecError(GeneratorBaseError):
    pass


class BadPathError(BadSpecError):
    pass


class OverlappingMethodsError(BadSpecError):
    pass


class NotSupportedError(GeneratorBaseError):
    pass


class ExternalRefNotSupportedError(NotSupportedError):
    pass


class ParamInCookieNotSupportedError(NotSupportedError):
    pass


class UndefinedSchemaNotSupportedError(NotSupportedError):
    pass


class UnstructuredMediaSchemaNotSupportedError(NotSupportedError):
    pass


class RangeResponseNotSupportedError(NotSupportedError):
    pass


class NoContentResponseNotSupportedError(NotSupportedError):
    pass


class ReferenceNotFoundError(GeneratorBaseError):
    pass


class ReferencedHeaderNotFoundError(ReferenceNotFoundError):
    pass


class ReferencedParameterNotFoundError(ReferenceNotFoundError):
    pass


class ReferencedBodyNotFoundError(ReferenceNotFoundError):
    pass


class ReferencedSchemaNotFoundError(ReferenceNotFoundError):
    pass


class ReferencedResponseNotFoundError(ReferenceNotFoundError):
    pass
