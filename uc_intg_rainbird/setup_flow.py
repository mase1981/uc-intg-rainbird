"""Setup flow: connect to a Rain Bird LNK module with host + password."""

import logging
import re
from typing import Any

from ucapi import RequestUserInput
from ucapi_framework import BaseSetupFlow

from uc_intg_rainbird.client import RainbirdClient
from uc_intg_rainbird.config import RainbirdConfig
from uc_intg_rainbird.const import DEFAULT_DURATION, DURATION_MAX, DURATION_MIN

_LOG = logging.getLogger(__name__)


class RainbirdSetupFlow(BaseSetupFlow[RainbirdConfig]):
    """Collect the controller IP and password, validate, and store its zones."""

    def get_manual_entry_form(self) -> RequestUserInput:
        return RequestUserInput(
            {"en": "Rain Bird Controller Setup"},
            [
                {
                    "id": "info",
                    "label": {"en": "Rain Bird Controller"},
                    "field": {"label": {"value": {"en": (
                        "Enter the IP address and device password of your Rain Bird LNK "
                        "Wi-Fi module. The password is the one you set in the Rain Bird app. "
                        "The controller must be powered on and connected to your network."
                    )}}},
                },
                {"id": "host", "label": {"en": "IP Address"}, "field": {"text": {"value": ""}}},
                {"id": "password", "label": {"en": "Device Password"}, "field": {"password": {"value": ""}}},
                {
                    "id": "duration",
                    "label": {"en": "Default watering time (minutes)"},
                    "field": {
                        "number": {
                            "value": DEFAULT_DURATION,
                            "min": DURATION_MIN,
                            "max": DURATION_MAX,
                            "steps": 1,
                        }
                    },
                },
            ],
        )

    async def query_device(self, input_values: dict[str, Any]) -> RainbirdConfig:
        host = input_values.get("host", "").strip()
        password = input_values.get("password", "").strip()
        if not host:
            raise ValueError("IP address is required")
        if not password:
            raise ValueError("Device password is required")

        try:
            duration = int(input_values.get("duration", DEFAULT_DURATION))
        except (TypeError, ValueError):
            duration = DEFAULT_DURATION
        duration = max(DURATION_MIN, min(DURATION_MAX, duration))

        client = RainbirdClient(host, password)
        try:
            await client.connect()
            model_info = await client.get_model_and_version()
            serial = await client.get_serial_number()
            zones = await client.get_available_zones()
        except Exception as err:  # pylint: disable=broad-exception-caught
            raise ValueError(
                f"Could not connect to a Rain Bird controller at {host}. Check the IP "
                f"address and password, and make sure the controller is online. ({err})"
            ) from err
        finally:
            await client.close()

        model_name = getattr(model_info, "model_name", "") or "Rain Bird Controller"
        base = serial or host
        identifier = f"rainbird_{re.sub(r'[^A-Za-z0-9]', '_', str(base))}"
        return RainbirdConfig(
            identifier=identifier,
            name=model_name,
            host=host,
            password=password,
            model=model_name,
            serial=str(serial or ""),
            zones=zones,
            default_duration=duration,
        )
