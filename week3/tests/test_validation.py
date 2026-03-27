from __future__ import annotations

import pytest

from week3.server.errors import InputValidationError
from week3.server.validation import (
    validate_latitude,
    validate_longitude,
    validate_max_results,
    validate_place_name,
)


def test_validate_place_name_rejects_blank() -> None:
    with pytest.raises(InputValidationError):
        validate_place_name("   ")


def test_validate_max_results_rejects_out_of_range() -> None:
    with pytest.raises(InputValidationError):
        validate_max_results(11)


def test_validate_latitude_rejects_invalid_value() -> None:
    with pytest.raises(InputValidationError):
        validate_latitude(100)


def test_validate_longitude_accepts_boundary() -> None:
    assert validate_longitude(-180) == -180.0
