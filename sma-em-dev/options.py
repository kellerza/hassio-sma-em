"""Addon options."""

from __future__ import annotations

import typing as t
import logging
from json import loads
from pathlib import Path

from yaml import safe_load
import attrs
from cattrs import Converter, transform_error
from cattrs.gen import make_dict_structure_fn

_LOGGER = logging.getLogger(__name__)


@attrs.define(slots=True)
class SmaOptions:
    """Options for an SMA device."""

    serial_nr: str = ""
    ha_prefix: str = ""


@attrs.define(slots=True)
class Options:
    """HASS Addon Options."""

    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    mcastgrp: str = "239.12.255.254"
    mqtt_host: str = "core-mosquitto"
    mqtt_port: int = 1883
    mqtt_username: str = ""
    mqtt_password: str = ""
    ipbind: str = "0.0.0.0"
    sma_devices: list[SmaOptions] = attrs.field(factory=list)
    fields: list[str] = attrs.field(factory=list)
    threshold: int = 80
    reconnect_interval: int = 86400
    debug: int = 0

    sma_device_lookup: dict[str, str] = attrs.field(factory=dict)

    def load(self, value: dict) -> None:
        """Structure and copy result to self."""
        value = {k: v for k, v in value.items() if v}
        try:
            _LOGGER.debug("Loading config: %s", value)
            obj = CONVERTER.structure(value, Options)
        except Exception as exc:
            msg = "Error loading config: " + "\n".join(transform_error(exc))
            _LOGGER.error(msg)
            raise ValueError(msg)  # pylint:disable=raise-missing-from

        for key in attrs.asdict(obj):
            setattr(self, key, getattr(obj, key))

        self.sma_device_lookup = {}
        for d in self.sma_devices:
            _LOGGER.debug("dev %s %s", d, type(d))
            ha_prefix = str(d.ha_prefix).strip()
            serial_nr = str(d.serial_nr).strip()
            if not ha_prefix or not serial_nr:
                _LOGGER.warning("Invalid SMA device: %s", d)
                continue
            self.sma_device_lookup[serial_nr] = ha_prefix
        self.sma_devices.clear()


OPT = Options()


def init_options() -> None:
    """Initialize the options & logger."""
    logging.basicConfig(
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s", level=logging.DEBUG
    )

    hassosf = Path("/data/options.json")
    if hassosf.exists():
        _LOGGER.info("Loading HASS OS configuration")
        OPT.load(loads(hassosf.read_text(encoding="utf-8")))
    else:
        configf = Path(__file__).parent / "config.yaml"
        _LOGGER.info("Local mode - load defaults from %s", str(configf))
        OPT.load(safe_load(configf.read_text()).get("options", {}))
        localf = Path(__file__).parent.parent / ".local.yaml"
        if localf.exists():
            _LOGGER.info("Local mode - load overrides from %s", str(localf))
            OPT.load(safe_load(localf.read_text()))

    if OPT.debug < 2:
        logging.basicConfig(
            format="%(asctime)s %(levelname)-7s %(message)s",
            level=logging.INFO,
            force=True,
        )


CONVERTER = Converter(forbid_extra_keys=True)


def structure_ensure_lowercase_keys(cls: t.Type) -> t.Callable[[t.Any, t.Any], t.Any]:
    """Convert any uppercase keys to lowercase."""
    struct = make_dict_structure_fn(cls, CONVERTER)  # type: ignore

    def structure(d: dict[str, t.Any], cl: t.Any) -> t.Any:
        lower = [k for k in d if k.lower() != k]
        for k in lower:
            if k.lower() in d:
                _LOGGER.warning("Key %s already exists in lowercase", k.lower())
            d[k.lower()] = d.pop(k)
        return struct(d, cl)

    return structure


CONVERTER.register_structure_hook_factory(attrs.has, structure_ensure_lowercase_keys)
