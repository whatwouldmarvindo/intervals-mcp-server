"""
Unit tests for the make_intervals_request function in intervals_mcp_server.server.

These tests focus on error handling, particularly the scenario where the API returns invalid JSON.
Mock classes are used to simulate httpx responses and client behavior.
"""

import asyncio
import logging
from json import JSONDecodeError

import intervals_mcp_server.server as server


class MockBadJSONResponse:
    """
    Simulates an httpx response object that returns invalid JSON content.
    Used to test error handling for JSONDecodeError in make_intervals_request.
    """
    def __init__(self):
        self.content = b"bad"
        self.status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        raise JSONDecodeError("Expecting value", "bad", 0)


class MockAsyncClient:
    """
    Simulates an httpx.AsyncClient for use in monkeypatching.
    Always returns a MockBadJSONResponse from get().
    """
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def get(self, *args, **kwargs):
        return MockBadJSONResponse()


def test_make_intervals_request_bad_json(monkeypatch, caplog):
    """
    Test that make_intervals_request returns an error dict when the response contains invalid JSON.
    Ensures proper logging and error message content.
    """
    monkeypatch.setattr(server, "httpx_client", MockAsyncClient())

    with caplog.at_level(logging.ERROR):
        result = asyncio.run(server.make_intervals_request("/bad"))

    assert result["error"] is True
    assert "Invalid JSON in response" in result["message"]
