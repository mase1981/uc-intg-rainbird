"""Rain Bird controller device - polls one LNK Wi-Fi module over the local API."""

import asyncio
import logging
from typing import Any

from ucapi_framework import DeviceEvents, PollingDevice

from uc_intg_rainbird.client import RainbirdClient
from uc_intg_rainbird.config import RainbirdConfig
from uc_intg_rainbird.const import (
    POLL_INTERVAL,
    RAIN_DELAY_MAX,
    RAIN_DELAY_MIN,
    STATE_ON,
    STATE_UNAVAILABLE,
)

_LOG = logging.getLogger(__name__)


class RainbirdDevice(PollingDevice):
    """One Rain Bird irrigation controller."""

    def __init__(self, device_config: RainbirdConfig, **kwargs: Any) -> None:
        super().__init__(device_config, poll_interval=POLL_INTERVAL, **kwargs)
        self._device_config = device_config
        self._client: RainbirdClient | None = None
        self._connect_lock: asyncio.Lock = asyncio.Lock()
        self._state: str = STATE_UNAVAILABLE

        self.model: str = device_config.model or ""
        self.serial: str = device_config.serial or ""
        self.zones: list[int] = list(device_config.zones)
        self.active_zones: set[int] = set()
        self.rain_sensor: bool = False
        self.rain_delay: int = 0

    @property
    def identifier(self) -> str:
        return self._device_config.identifier

    @property
    def name(self) -> str:
        return self._device_config.name

    @property
    def address(self) -> str:
        return self._device_config.host

    @property
    def log_id(self) -> str:
        return f"{self.name} ({self.address})"

    @property
    def state(self) -> str:
        return self._state

    @property
    def default_duration(self) -> int:
        return self._device_config.default_duration

    async def establish_connection(self) -> RainbirdClient:
        # Never raise when the controller is unreachable: the framework does not
        # retry a failed connect, which would leave entities unavailable until
        # the Remote reconnects. Polling keeps running and reconnects instead.
        async with self._connect_lock:
            if self._client is None:
                self._client = RainbirdClient(self._device_config.host, self._device_config.password)
            if not await self._connect_locked():
                _LOG.warning("[%s] Controller unreachable, will keep retrying", self.log_id)
                self._state = STATE_UNAVAILABLE
                return self._client

            try:
                await self._read_state()
            except ConnectionError:
                _LOG.warning("[%s] Initial state query failed, using defaults", self.log_id)

            self._state = STATE_ON
            return self._client

    async def _connect_locked(self) -> bool:
        """Connect the client and refresh zones. Caller MUST hold ``self._connect_lock``."""
        assert self._client is not None
        if not self._client.is_connected:
            try:
                await self._client.connect()
            except Exception as err:  # pylint: disable=broad-exception-caught
                _LOG.debug("[%s] Connect failed: %s", self.log_id, err)
                return False

        try:
            zones = await self._client.get_available_zones()
        except Exception as err:  # pylint: disable=broad-exception-caught
            # Zones are stored in the config; keep using them.
            _LOG.debug("[%s] Zone query failed: %s", self.log_id, err)
            return True
        if zones:
            self.zones = zones
            if zones != self._device_config.zones:
                self.update_config(zones=zones)
        return True

    async def poll_device(self) -> None:
        if self._client is None:
            return
        try:
            async with self._connect_lock:
                if not self._client.is_connected and not await self._connect_locked():
                    raise ConnectionError("Controller unreachable")
                await self._read_state()
            # A successful poll always restores availability after an error.
            self._state = STATE_ON
            self.push_update()
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.debug("[%s] Poll error: %s", self.log_id, err)
            if self._state != STATE_UNAVAILABLE:
                self._state = STATE_UNAVAILABLE
                self.events.emit(DeviceEvents.DISCONNECTED, self.identifier)

    async def _read_state(self) -> None:
        """Read runtime state. Caller MUST hold ``self._connect_lock``."""
        assert self._client is not None
        try:
            self.active_zones = await self._client.get_active_zones()
            self.rain_sensor = await self._client.get_rain_sensor_state()
            self.rain_delay = await self._client.get_rain_delay()
        except Exception as err:  # pylint: disable=broad-exception-caught
            raise ConnectionError(f"Failed to read controller state: {err}") from err

    async def disconnect(self) -> None:
        async with self._connect_lock:
            if self._client is not None:
                await self._client.close()
                self._client = None
        self._state = STATE_UNAVAILABLE
        await super().disconnect()

    async def start_zone(self, zone: int, minutes: int | None = None) -> bool:
        duration = minutes if minutes and minutes > 0 else self.default_duration
        async with self._connect_lock:
            if self._client is None:
                return False
            await self._client.irrigate_zone(zone, duration)
        self.active_zones = {zone}
        self.push_update()
        return True

    async def stop_all(self) -> bool:
        async with self._connect_lock:
            if self._client is None:
                return False
            await self._client.stop_irrigation()
        self.active_zones = set()
        self.push_update()
        return True

    async def set_rain_delay(self, days: int) -> bool:
        days = max(RAIN_DELAY_MIN, min(RAIN_DELAY_MAX, int(days)))
        async with self._connect_lock:
            if self._client is None:
                return False
            await self._client.set_rain_delay(days)
        self.rain_delay = days
        self.push_update()
        return True
