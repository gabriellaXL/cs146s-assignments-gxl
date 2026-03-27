"""Input validation helpers."""

from __future__ import annotations

from week3.server.errors import InputValidationError


def validate_place_name(name: str) -> str:
    cleaned = (name or "").strip()
    if not cleaned:
        raise InputValidationError("place name must not be empty")
    if len(cleaned) > 200:
        raise InputValidationError("place name must be at most 200 characters")
    return cleaned


def validate_max_results(max_results: int, max_allowed: int = 10) -> int:
    try:
        parsed = int(max_results)
    except (TypeError, ValueError) as exc:
        raise InputValidationError(
            f"max_results must be an integer between 1 and {max_allowed}"
        ) from exc

    if not 1 <= parsed <= max_allowed:
        raise InputValidationError(f"max_results must be between 1 and {max_allowed}")
    return parsed


def validate_latitude(latitude: float) -> float:
    try:
        parsed = float(latitude)
    except (TypeError, ValueError) as exc:
        raise InputValidationError("latitude must be a number between -90 and 90") from exc

    if not -90.0 <= parsed <= 90.0:
        raise InputValidationError("latitude must be between -90 and 90")
    return parsed


def validate_longitude(longitude: float) -> float:
    try:
        parsed = float(longitude)
    except (TypeError, ValueError) as exc:
        raise InputValidationError("longitude must be a number between -180 and 180") from exc

    if not -180.0 <= parsed <= 180.0:
        raise InputValidationError("longitude must be between -180 and 180")
    return parsed
