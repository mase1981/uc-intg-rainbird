"""Integration driver for Rain Bird irrigation controllers."""

from ucapi_framework import BaseIntegrationDriver

from uc_intg_rainbird.button import create_button
from uc_intg_rainbird.config import RainbirdConfig
from uc_intg_rainbird.device import RainbirdDevice
from uc_intg_rainbird.select import create_select
from uc_intg_rainbird.sensor import create_sensors
from uc_intg_rainbird.switch import create_switches


class RainbirdDriver(BaseIntegrationDriver[RainbirdDevice, RainbirdConfig]):
    """Builds the entity set for each Rain Bird controller."""

    def __init__(self) -> None:
        super().__init__(
            device_class=RainbirdDevice,
            entity_classes=[
                create_switches,
                create_button,
                create_select,
                create_sensors,
            ],
            driver_id="uc_intg_rainbird",
        )
