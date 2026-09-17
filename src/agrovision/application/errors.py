"""Application-level errors mapped to stable HTTP responses at the boundary."""

from __future__ import annotations


class ApplicationError(Exception):
    """Base class for expected application failures."""

    code = "application_error"
    status_code = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationError(ApplicationError):
    """The request was syntactically valid but semantically rejected."""

    code = "validation_error"
    status_code = 400


class UnauthorizedError(ApplicationError):
    """Authentication failed or was missing."""

    code = "unauthorized"
    status_code = 401


class ForbiddenError(ApplicationError):
    """The authenticated user lacks permission."""

    code = "forbidden"
    status_code = 403


class NotFoundError(ApplicationError):
    """The requested resource does not exist."""

    code = "not_found"
    status_code = 404


class ConflictError(ApplicationError):
    """The request conflicts with existing state (e.g. duplicate email)."""

    code = "conflict"
    status_code = 409


class PayloadTooLargeError(ApplicationError):
    """The uploaded payload exceeds the configured limit."""

    code = "payload_too_large"
    status_code = 413


class UnsupportedMediaError(ApplicationError):
    """The uploaded media type or content is not supported."""

    code = "unsupported_media_type"
    status_code = 415


class InferenceBusyError(ApplicationError):
    """The bounded model queue could not accept more work."""

    code = "inference_busy"
    status_code = 503


class InferenceTimeoutError(ApplicationError):
    """A queued model call exceeded its configured deadline."""

    code = "inference_timeout"
    status_code = 504
