"""Rain Bird rain-delay selector (0-14 days)."""

import logging
from typing import Any

from ucapi import StatusCodes, select
from ucapi_framework import SelectEntity

from uc_intg_rainbird.config import RainbirdConfig
from uc_intg_rainbird.const import RAIN_DELAY_MAX, RAIN_DELAY_MIN, STATE_ON
from uc_intg_rainbird.device import RainbirdDevice

_LOG = logging.getLogger(__name__)


def _label(days: int) -> str:
    if days == 0:
        return "Off"
    return f"{days} day" if days == 1 else f"{days} days"


_OPTIONS = [_label(d) for d in range(RAIN_DELAY_MIN, RAIN_DELAY_MAX + 1)]
_LABEL_TO_DAYS = {_label(d): d for d in range(RAIN_DELAY_MIN, RAIN_DELAY_MAX + 1)}


class RainDelaySelect(SelectEntity):
    """Sets and displays the current rain delay in days."""

    def __init__(self, device_config: RainbirdConfig, device: RainbirdDevice) -> None:
        self._device = device
        entity_id = f"select.{device_config.identifier}.rain_delay"
        super().__init__(
            entity_id,
            f"{device_config.name} Rain Delay",
            {
                select.Attributes.STATE: select.States.UNKNOWN,
                select.Attributes.OPTIONS: [],
                select.Attributes.CURRENT_OPTION: "",
            },
            cmd_handler=self._handle_command,
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        if self._device.state != STATE_ON:
            self.update({select.Attributes.STATE: select.States.UNAVAILABLE})
            return
        self.update(
            {
                select.Attributes.STATE: select.States.ON,
                select.Attributes.OPTIONS: _OPTIONS,
                select.Attributes.CURRENT_OPTION: _label(self._device.rain_delay),
            }
        )

    async def _handle_command(self, entity: Any, cmd_id: str, params: dict | None = None, *_a: Any) -> StatusCodes:
        if cmd_id == select.Commands.SELECT_OPTION:
            option = params.get("option", "") if params else ""
            days = _LABEL_TO_DAYS.get(option)
            if days is None:
                return StatusCodes.BAD_REQUEST
            try:
                if await self._device.set_rain_delay(days):
                    return StatusCodes.OK
                return StatusCodes.SERVER_ERROR
            except Exception as err:  # pylint: disable=broad-exception-caught
                _LOG.error("[%s] Rain-delay command error: %s", entity.id, err)
                return StatusCodes.SERVER_ERROR
        return StatusCodes.NOT_IMPLEMENTED


def create_select(device_config: RainbirdConfig, device: RainbirdDevice) -> list[SelectEntity]:
    return [RainDelaySelect(device_config, device)]
