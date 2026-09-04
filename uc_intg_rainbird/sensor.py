"""Rain Bird sensors - rain sensor, active zone, rain-delay days, and model."""

import logging

from ucapi import sensor
from ucapi_framework import SensorEntity

from uc_intg_rainbird.config import RainbirdConfig
from uc_intg_rainbird.const import RAIN_DRY, RAIN_WET, STATE_ON, ZONE_NONE
from uc_intg_rainbird.device import RainbirdDevice

_LOG = logging.getLogger(__name__)


class RainSensor(SensorEntity):
    """Reports whether the rain sensor is tripped."""

    def __init__(self, device_config: RainbirdConfig, device: RainbirdDevice) -> None:
        self._device = device
        super().__init__(
            f"sensor.{device_config.identifier}.rain_sensor",
            f"{device_config.name} Rain Sensor",
            [],
            {sensor.Attributes.STATE: sensor.States.UNKNOWN, sensor.Attributes.VALUE: ""},
            device_class=sensor.DeviceClasses.CUSTOM,
            options={sensor.Options.CUSTOM_UNIT: ""},
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        if self._device.state != STATE_ON:
            self.update({sensor.Attributes.STATE: sensor.States.UNAVAILABLE})
            return
        self.update(
            {
                sensor.Attributes.STATE: sensor.States.ON,
                sensor.Attributes.VALUE: RAIN_WET if self._device.rain_sensor else RAIN_DRY,
            }
        )


class ActiveZoneSensor(SensorEntity):
    """Reports which zone is currently watering."""

    def __init__(self, device_config: RainbirdConfig, device: RainbirdDevice) -> None:
        self._device = device
        super().__init__(
            f"sensor.{device_config.identifier}.active_zone",
            f"{device_config.name} Active Zone",
            [],
            {sensor.Attributes.STATE: sensor.States.UNKNOWN, sensor.Attributes.VALUE: ""},
            device_class=sensor.DeviceClasses.CUSTOM,
            options={sensor.Options.CUSTOM_UNIT: ""},
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        if self._device.state != STATE_ON:
            self.update({sensor.Attributes.STATE: sensor.States.UNAVAILABLE})
            return
        active = sorted(self._device.active_zones)
        value = ", ".join(str(z) for z in active) if active else ZONE_NONE
        self.update({sensor.Attributes.STATE: sensor.States.ON, sensor.Attributes.VALUE: value})


class RainDelaySensor(SensorEntity):
    """Reports the current rain delay in days."""

    def __init__(self, device_config: RainbirdConfig, device: RainbirdDevice) -> None:
        self._device = device
        super().__init__(
            f"sensor.{device_config.identifier}.rain_delay_days",
            f"{device_config.name} Rain Delay Days",
            [],
            {sensor.Attributes.STATE: sensor.States.UNKNOWN, sensor.Attributes.VALUE: -1},
            device_class=sensor.DeviceClasses.CUSTOM,
            options={sensor.Options.CUSTOM_UNIT: "days"},
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        if self._device.state != STATE_ON:
            self.update({sensor.Attributes.STATE: sensor.States.UNAVAILABLE})
            return
        self.update({sensor.Attributes.STATE: sensor.States.ON, sensor.Attributes.VALUE: self._device.rain_delay})


class ModelSensor(SensorEntity):
    """Reports the controller model."""

    def __init__(self, device_config: RainbirdConfig, device: RainbirdDevice) -> None:
        self._device = device
        super().__init__(
            f"sensor.{device_config.identifier}.model",
            f"{device_config.name} Model",
            [],
            {sensor.Attributes.STATE: sensor.States.UNKNOWN, sensor.Attributes.VALUE: ""},
            device_class=sensor.DeviceClasses.CUSTOM,
            options={sensor.Options.CUSTOM_UNIT: ""},
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        self.update(
            {sensor.Attributes.STATE: sensor.States.ON, sensor.Attributes.VALUE: self._device.model or "Unknown"}
        )


def create_sensors(device_config: RainbirdConfig, device: RainbirdDevice) -> list[SensorEntity]:
    return [
        RainSensor(device_config, device),
        ActiveZoneSensor(device_config, device),
        RainDelaySensor(device_config, device),
        ModelSensor(device_config, device),
    ]
