from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator

import aiohttp
import structlog
import websockets
from signal_ai.core.config import Settings

log = structlog.get_logger()


class SignalTransport:
    def __init__(self, config: Settings):
        self._config = config
        self._session = aiohttp.ClientSession()
        self._ws_uri = (
            f"ws://{self._config.signal_service}/v1/receive/{self._config.signal_phone_number}"
        )
        self._base_url = f"http://{self._config.signal_service}"

    async def listen(self) -> AsyncGenerator[str, None]:
        """Listen for incoming messages and yield them."""
        """Listen for incoming messages and yield them."""
        backoff_delay = 1
        while True:
            try:
                log.info("Connecting to Signal WebSocket.", uri=self._ws_uri)
                async with websockets.connect(self._ws_uri) as websocket:
                    log.info("WebSocket connection established.")
                    backoff_delay = 1
                    async for raw_message in websocket:
                        if not isinstance(raw_message, str):
                            raw_message = bytes(raw_message).decode("utf-8")
                        yield raw_message
            except websockets.exceptions.ConnectionClosed:
                log.warning("WebSocket connection closed. Reconnecting...")
                await asyncio.sleep(1)
            except Exception as e:
                log.error(
                    "WebSocket connection failed.",
                    error=e,
                    delay=backoff_delay,
                )
                await asyncio.sleep(backoff_delay)
                backoff_delay = min(backoff_delay * 2, 60)

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Any:
        response.raise_for_status()
        if response.content_type == "application/json":
            return await response.json()
        return await response.read()

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self._base_url}{path}"
        async with self._session.request(method, url, **kwargs) as response:
            return await self._handle_response(response)

    async def send(self, data: dict[str, Any]) -> dict[str, Any]:
        """Send a signal message."""
        log.info("signal.send.start", recipient=data.get("recipient"))
        response = await self._request("POST", "/v2/send", json=data)
        log.info("signal.send.end", recipient=data.get("recipient"))
        return response

    async def close(self):
        await self._session.close()