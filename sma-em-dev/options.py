"""Addon options."""
from __future__ import annotations

import logging
from json import loads
from pathlib import Path

import attr
import yaml

_LOGGER = logging.getLogger(__name__)


@attr.define(slots=True)
class Options:
    """HASS Addon Options."""

    # pylint: disable=too-few-public-methods
    mcastgrp: str = "239.12.255.254"
    mqtt_host: str = ""
    mqtt_port: int = 0
    mqtt_username: str = ""
    mqtt_password: str = ""
    sma_serials: list[str] = []
    fields: list[str] = []
    threshold: int = 80
    reconnect_interval: int = 86400
    debug: int = 1

    def update(self, json: dict) -> None:
        """Update options."""
        for key, val in json.items():
            setattr(self, key.lower(), val)


OPT = Options()


def init_options() -> None:
    """Initialize the options & logger."""
    logging.basicConfig(
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s", level=logging.DEBUG
    )

    hassosf = Path("/data/options.json")
    if hassosf.exists():
        _LOGGER.info("Loading HASS OS configuration")
        OPT.update(loads(hassosf.read_text(encoding="utf-8")))
    else:
        configf = Path(__file__).parent / "config.yaml"
        _LOGGER.info("Local mode - load defaults from %s", str(configf))
        OPT.update(yaml.safe_load(configf.read_text()).get("options", {}))
        localf = Path(__file__).parent.parent / ".local.yaml"
        if localf.exists():
            _LOGGER.info("Local mode - load overrides from %s", str(localf))
            OPT.update(yaml.safe_load(localf.read_text()))

    if OPT.debug < 2:
        logging.basicConfig(
            format="%(asctime)s %(levelname)-7s %(message)s",
            level=logging.INFO,
            force=True,
        )
