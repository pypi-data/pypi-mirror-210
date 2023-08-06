from typing import Optional
from fastapi import HTTPException


class ApiError(HTTPException):

    error_key: str = "api_error"
    status_code: int = 500

    def __init__(self, message: Optional[str] = None):
        super(ApiError, self).__init__(status_code=self.status_code, detail=message)


class AuthenticationError(ApiError):
    status_code = 401
    error_key = "auth_error"

    def __init__(self, message: str = "you must be authenticated first") -> None:
        super().__init__(message)


class ConfigurationError(SystemExit):
    error_key = "configuration_error"


class Forbidden(ApiError):
    error_key = "forbidden"
    status_code = 403


class BadRequest(ApiError):
    error_key = "bad_request"
    status_code = 400


class Conflict(ApiError):
    error_key = "conflict"
    status_code = 409


class IntegrityError(ApiError):
    error_key = "integrity_error"
    status_code = 409


class NotFound(ApiError):
    error_key = "not_found"
    status_code = 404


class InternalServerError(ApiError):
    error_key = "intrnl_error"
    status_code = 500


class InvalidShardId(InternalServerError):
    error_key = "intrnl_error"


class ShardIsReadOnly(IntegrityError):
    error_key = "shard_readonly"


class ModelDestroyed(IntegrityError):
    error_key = "model_destroyed"


class InputDataError(ApiError):
    error_key = "bad_input"
    pass


class InvalidFieldType(ApiError):
    error_key = "bad_input_type"


class OAuthError(ApiError):
    error_key = "oauth_error"
    status_code = 401


class ORMException(Exception):
    pass


class AbortTransaction(ORMException):
    def __init__(self) -> None:
        super().__init__("transaction aborted")


class ValidationError(ORMException, ApiError):
    error_key = "validation_error"
    status_code = 422


class DoNotSave(ORMException):
    pass


class ObjectSaveRequired(ORMException):
    pass


class ObjectHasReferences(ORMException, ApiError):
    status_code = 409
    error_key = "object_has_references"


class MissingSubmodel(ORMException):
    pass


class WrongSubmodel(ORMException):
    pass


class UnknownSubmodel(ORMException):
    pass
