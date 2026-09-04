"""Rain Bird zone switches - one per irrigation zone."""

import logging
from typing import Any

from ucapi import StatusCodes, switch
from ucapi_framework import SwitchEntity

from uc_intg_rainbird.config import RainbirdConfig
from uc_intg_rainbird.const import STATE_ON
from uc_intg_rainbird.device import RainbirdDevice

_LOG = logging.getLogger(__name__)


class ZoneSwitch(SwitchEntity):
    """A single irrigation zone. On starts the zone for the default duration; off stops all watering."""

    def __init__(self, device_config: RainbirdConfig, device: RainbirdDevice, zone: int) -> None:
        self._device = device
        self._zone = zone
        entity_id = f"switch.{device_config.identifier}.zone_{zone}"
        super().__init__(
            entity_id,
            f"{device_config.name} Zone {zone}",
            [switch.Features.ON_OFF, switch.Features.TOGGLE],
            {switch.Attributes.STATE: switch.States.UNKNOWN},
            cmd_handler=self._handle_command,
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        if self._device.state != STATE_ON:
            self.update({switch.Attributes.STATE: switch.States.UNAVAILABLE})
            return
        running = self._zone in self._device.active_zones
        self.update({switch.Attributes.STATE: switch.States.ON if running else switch.States.OFF})

    async def _handle_command(self, entity: Any, cmd_id: str, params: dict | None = None, *_a: Any) -> StatusCodes:
        try:
            if cmd_id == switch.Commands.ON:
                ok = await self._device.start_zone(self._zone)
            elif cmd_id == switch.Commands.OFF:
                ok = await self._device.stop_all()
            elif cmd_id == switch.Commands.TOGGLE:
                if self._zone in self._device.active_zones:
                    ok = await self._device.stop_all()
                else:
                    ok = await self._device.start_zone(self._zone)
            else:
                return StatusCodes.NOT_IMPLEMENTED
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.error("[%s] Switch command error (%s): %s", entity.id, cmd_id, err)
            return StatusCodes.SERVER_ERROR


def create_switches(device_config: RainbirdConfig, device: RainbirdDevice) -> list[SwitchEntity]:
    return [ZoneSwitch(device_config, device, zone) for zone in device.zones]
