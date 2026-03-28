from __future__ import annotations

import asyncio

import httpx
import pytest

from week3.server.config import DEFAULT_CONFIG
from week3.server.errors import (
    ResourceNotFoundError,
    UpstreamRateLimitError,
    UpstreamResponseFormatError,
    UpstreamTimeoutError,
)
from week3.server.logging_utils import configure_logging
from week3.server.openmeteo_client import OpenMeteoClient


def _make_client(handler):
    transport = httpx.MockTransport(handler)
    http_client = httpx.AsyncClient(transport=transport)
    return (
        OpenMeteoClient(
            config=DEFAULT_CONFIG,
            logger=configure_logging(),
            client=http_client,
        ),
        http_client,
    )


async def _run_search_places_success() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "name": "Beijing",
                        "country": "China",
                        "admin1": "Beijing",
                        "latitude": 39.9042,
                        "longitude": 116.4074,
                    }
                ]
            },
        )

    client, http_client = _make_client(handler)
    try:
        result = await client.search_places("Beijing", 1)
    finally:
        await http_client.aclose()

    assert result[0].name == "Beijing"
    assert result[0].longitude == pytest.approx(116.4074)


async def _run_search_places_empty_results_raise_not_found() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"results": []})

    client, http_client = _make_client(handler)
    try:
        with pytest.raises(ResourceNotFoundError):
            await client.search_places("Nowhere", 3)
    finally:
        await http_client.aclose()


async def _run_get_current_weather_invalid_shape_raises_format_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"current": []})

    client, http_client = _make_client(handler)
    try:
        with pytest.raises(UpstreamResponseFormatError):
            await client.get_current_weather(39.9, 116.4)
    finally:
        await http_client.aclose()


async def _run_rate_limit_error_is_raised_with_injected_client() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "rate limit"})

    client, http_client = _make_client(handler)
    try:
        with pytest.raises(UpstreamRateLimitError):
            await client.search_places("Beijing", 1)
    finally:
        await http_client.aclose()


async def _run_timeout_is_translated() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    client, http_client = _make_client(handler)
    try:
        with pytest.raises(UpstreamTimeoutError):
            await client.search_places("Beijing", 1)
    finally:
        await http_client.aclose()


def test_search_places_success_sync() -> None:
    asyncio.run(_run_search_places_success())


def test_search_places_empty_results_raise_not_found_sync() -> None:
    asyncio.run(_run_search_places_empty_results_raise_not_found())


def test_get_current_weather_invalid_shape_raises_format_error_sync() -> None:
    asyncio.run(_run_get_current_weather_invalid_shape_raises_format_error())


def test_rate_limit_error_is_raised_with_injected_client_sync() -> None:
    asyncio.run(_run_rate_limit_error_is_raised_with_injected_client())


def test_timeout_is_translated_sync() -> None:
    asyncio.run(_run_timeout_is_translated())
