"""Domain-specific errors and user-facing error translation."""

from __future__ import annotations


class OpenMeteoError(Exception):
    """Base error for server-specific failures."""


class InputValidationError(OpenMeteoError):
    """Raised when tool input is invalid."""


class UpstreamRequestError(OpenMeteoError):
    """Raised when the upstream API request fails."""


class UpstreamTimeoutError(UpstreamRequestError):
    """Raised when the upstream API times out."""


class UpstreamRateLimitError(UpstreamRequestError):
    """Raised when the upstream API rate-limits requests."""


class UpstreamResponseFormatError(UpstreamRequestError):
    """Raised when the upstream response shape is invalid."""


class ResourceNotFoundError(OpenMeteoError):
    """Raised when the upstream API returns no matching resource."""


def format_user_error(exc: OpenMeteoError) -> str:
    """Map internal exceptions to concise, actionable user-facing messages."""
    if isinstance(exc, InputValidationError):
        return f"Input error: {exc}"
    if isinstance(exc, ResourceNotFoundError):
        return str(exc)
    if isinstance(exc, UpstreamRateLimitError):
        return (
            "The weather service is temporarily rate-limiting requests. "
            "Please wait a moment and try again."
        )
    if isinstance(exc, UpstreamTimeoutError):
        return "The weather service timed out. Please try again."
    if isinstance(exc, UpstreamResponseFormatError):
        return (
            "The weather service returned an unexpected response format. " "Please try again later."
        )
    if isinstance(exc, UpstreamRequestError):
        return "The weather service request failed. Please try again later."
    return "The server encountered an unexpected error. Please try again later."
