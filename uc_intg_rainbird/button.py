"""Rain Bird stop button - stops all active irrigation."""

import logging
from typing import Any

from ucapi import StatusCodes, button
from ucapi_framework import ButtonEntity

from uc_intg_rainbird.config import RainbirdConfig
from uc_intg_rainbird.device import RainbirdDevice

_LOG = logging.getLogger(__name__)


class StopButton(ButtonEntity):
    """Stops watering on every zone."""

    def __init__(self, device_config: RainbirdConfig, device: RainbirdDevice) -> None:
        self._device = device
        entity_id = f"button.{device_config.identifier}.stop"
        super().__init__(entity_id, f"{device_config.name} Stop Watering", cmd_handler=self._handle_command)

    async def _handle_command(self, entity: Any, cmd_id: str, params: dict | None = None, *_a: Any) -> StatusCodes:
        if cmd_id == button.Commands.PUSH:
            try:
                if await self._device.stop_all():
                    return StatusCodes.OK
                return StatusCodes.SERVER_ERROR
            except Exception as err:  # pylint: disable=broad-exception-caught
                _LOG.error("[%s] Stop command error: %s", entity.id, err)
                return StatusCodes.SERVER_ERROR
        return StatusCodes.NOT_IMPLEMENTED


def create_button(device_config: RainbirdConfig, device: RainbirdDevice) -> list[ButtonEntity]:
    return [StopButton(device_config, device)]
