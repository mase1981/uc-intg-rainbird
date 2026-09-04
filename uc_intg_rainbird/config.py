"""Configuration dataclass and manager for the Rain Bird integration."""

from dataclasses import dataclass, field

from ucapi_framework import BaseConfigManager

from uc_intg_rainbird.const import DEFAULT_DURATION


@dataclass
class RainbirdConfig:
    """Configuration for a single Rain Bird LNK Wi-Fi controller."""

    identifier: str = ""
    name: str = ""
    host: str = ""
    password: str = ""
    model: str = ""
    serial: str = ""
    zones: list[int] = field(default_factory=list)
    default_duration: int = DEFAULT_DURATION


class RainbirdConfigManager(BaseConfigManager[RainbirdConfig]):
    """Config manager bound to :class:`RainbirdConfig`."""
