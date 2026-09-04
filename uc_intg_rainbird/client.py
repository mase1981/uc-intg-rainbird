"""Async client for the Rain Bird LNK Wi-Fi module.

Thin wrapper around :mod:`pyrainbird` that owns the aiohttp session. The LNK
module accepts only one request at a time, so the connector is limited to a
single connection and every call is serialised through a lock by the caller.
"""

import logging
from typing import Any

import aiohttp
from pyrainbird.async_client import AsyncRainbirdController, CreateController

_LOG = logging.getLogger(__name__)


class RainbirdClient:
    """Local control client for one Rain Bird controller."""

    def __init__(self, host: str, password: str) -> None:
        self._host = host
        self._password = password
        self._session: aiohttp.ClientSession | None = None
        self._controller: AsyncRainbirdController | None = None

    @property
    def is_connected(self) -> bool:
        return self._controller is not None and self._session is not None and not self._session.closed

    async def connect(self) -> bool:
        """Open the session and build the controller, then probe reachability."""
        if self.is_connected:
            return True
        self._session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=1))
        self._controller = CreateController(self._session, self._host, self._password)
        try:
            await self._controller.get_model_and_version()
        except Exception:
            await self.close()
            raise
        return True

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
        self._session = None
        self._controller = None

    def _require(self) -> AsyncRainbirdController:
        if self._controller is None:
            raise ConnectionError("Rain Bird controller is not connected")
        return self._controller

    async def get_model_and_version(self) -> Any:
        return await self._require().get_model_and_version()

    async def get_serial_number(self) -> str:
        return await self._require().get_serial_number()

    async def get_available_zones(self) -> list[int]:
        stations = await self._require().get_available_stations()
        return sorted(stations.active_set)

    async def get_active_zones(self) -> set[int]:
        states = await self._require().get_zone_states()
        return set(states.active_set)

    async def get_rain_sensor_state(self) -> bool:
        return bool(await self._require().get_rain_sensor_state())

    async def get_rain_delay(self) -> int:
        return int(await self._require().get_rain_delay())

    async def set_rain_delay(self, days: int) -> None:
        await self._require().set_rain_delay(days)

    async def irrigate_zone(self, zone: int, minutes: int) -> None:
        await self._require().irrigate_zone(zone, minutes)

    async def stop_irrigation(self) -> None:
        await self._require().stop_irrigation()
