"""Addon options."""

import logging
from functools import cached_property

import attrs
from mqtt_entity.options import MQTTOptions

_LOGGER = logging.getLogger(__name__)


@attrs.define()
class SmaOptions:
    """Options for an SMA device."""

    serial_nr: str = ""
    ha_prefix: str = ""

    def __attrs_post_init__(self) -> None:
        """Post init."""
        self.ha_prefix = self.ha_prefix.lower()


@attrs.define(slots=True)
class Options(MQTTOptions):
    """HASS Addon Options."""

    mcastgrp: str = ""
    ipbind: str = ""
    sma_devices: list[SmaOptions] = attrs.field(factory=list)
    fields: list[str] = attrs.field(factory=list)
    threshold: int = 80
    reconnect_interval: int = 86400
    debug: int = 0

    def __attrs_post_init__(self) -> None:
        """Post init."""
        self.mcastgrp = self.mcastgrp or "239.12.255.254"
        self.ipbind = self.ipbind or "0.0.0.0"
        self.reconnect_interval = self.reconnect_interval or 86400

    @cached_property
    def sma_device_lookup(self) -> dict[str, str]:
        """Build lookup."""
        res = {}
        for d in self.sma_devices:
            _LOGGER.debug("dev %s %s", d, type(d))
            ha_prefix = str(d.ha_prefix).strip()
            serial_nr = str(d.serial_nr).strip()
            if not ha_prefix or not serial_nr:
                _LOGGER.warning("Invalid SMA device: %s", d)
                continue
            res[serial_nr] = ha_prefix
        return res


OPT = Options()
