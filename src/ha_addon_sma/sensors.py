"""Run the energy meter."""

import asyncio
import logging
import statistics
import time

import attr
from icecream import ic  # type:ignore[import]
from mqtt_entity import MQTTClient, MQTTDevice, MQTTSensorEntity
from mqtt_entity.helpers import hass_device_class

from .helpers import pretty_print_dict
from .options import OPT

_LOGGER = logging.getLogger(__name__)
MQTT = MQTTClient(origin_name="SMA Energy Meter")


@attr.define
class SWSensor:
    """A speedwire sensor."""

    name: str
    mod: str
    """0 = mean, 1 = max, -1 = min"""
    last_update: int = 0
    interval: int = 5
    value: int | float = 0
    values: list[int | float] = attr.field(factory=list)
    unit: str = ""
    mq_entity: MQTTSensorEntity = attr.field(default=None)

    @property
    def id(self) -> str:
        """Return the ID."""
        if self.mod == "":
            return self.name
        if self.mod == "avg":
            return f"{self.name}_{self.interval}"
        return f"{self.name}_{self.mod}"


SENSORS: dict[str, list[SWSensor]] = {}


SMA_EM_TOPIC = "SMA-EM/status"


async def process_emparts(emparts: dict) -> None:  # noqa: PLR0912
    """Process emparts from the speedwire decoder."""
    if emparts["protocol"] not in [0x6069, 0x6081]:
        _LOGGER.info("Ignore protocol %s", hex(emparts["protocol"]))
        return

    serial = str(emparts["serial"])
    if not SENSORS.get(serial):
        # Discover the sensors
        _LOGGER.info(
            "Multicast frame received for SMA serial %s, discovered sensors:", serial
        )
        SENSORS[serial] = get_sensors(definition=OPT.fields, emparts=emparts)
        _LOGGER.debug(
            "Discover %s/%s sensors on SMA %s",
            len(SENSORS[serial]),
            len(OPT.fields),
            serial,
        )
        ha_prefix = OPT.sma_device_lookup.get(serial, "sma")
        mq_dev = MQTTDevice(
            identifiers=[serial, f"sma_em_{serial}"],
            # https://github.com/kellerza/sunsynk/issues/165
            # name=f"{OPT.manufacturer} AInverter {serial_nr}",
            name=ha_prefix,
            # name="SMA Energy Meter",
            model="Energy Meter",
            manufacturer="SMA",
            components={},
        )
        MQTT.devs.append(mq_dev)

        for sen in SENSORS[serial]:
            _LOGGER.info(" - %s every %ss", sen.id, sen.interval)
            sen.mq_entity = MQTTSensorEntity(
                name=sen.id,
                device_class=hass_device_class(unit=sen.unit),
                state_topic=f"{SMA_EM_TOPIC}/{serial}/{sen.id}",
                unique_id=f"{serial}_{sen.id}",
                unit_of_measurement=sen.unit,
                state_class="measurement" if is_measurement(sen.unit) else "",
                object_id=f"{ha_prefix} {sen.name}".lower(),
                suggested_display_precision=1,
            )

        mq_dev.components = {s.id: s.mq_entity for sl in SENSORS.values() for s in sl}
        await MQTT.publish_discovery_info()
        MQTT.monitor_homeassistant_status()
        await asyncio.sleep(5)

    push_later: list[tuple[SWSensor, int | float, int]] = []
    now = int(time.time())
    for sen in SENSORS[serial]:
        val = emparts.get(sen.name)
        if val is None:
            continue

        publish = now >= sen.last_update + sen.interval

        # check threshold crossing
        smart_s = sen.mod == "" and sen.values
        if smart_s and val > sen.value + OPT.threshold:
            publish = True
            push_later.append((sen, val, OPT.threshold))
        elif smart_s and val < sen.value - 2 * OPT.threshold:
            publish = True
            push_later.append((sen, val, -2 * OPT.threshold))
        else:
            sen.values.append(val)

        if not publish:
            continue
        ic(now, val, sen.value, len(sen.values))

        sen.last_update = now
        if sen.mod == "min":
            sen.value = min(sen.values)
        if sen.mod == "max":
            sen.value = max(sen.values)
        else:
            sen.value = statistics.mean(sen.values)
        sen.values = []

        await sen.mq_entity.send_state(MQTT, sen.value)

    if not push_later:
        return

    await asyncio.sleep(0.005)
    for sen, val, delta in push_later:
        sen.value = val
        ic(sen.name, sen.value, delta)
        await sen.mq_entity.send_state(MQTT, sen.value)


def is_measurement(units: str) -> bool:
    """Return True if the units are a measurement."""
    return units in {"W", "V", "A", "Hz", "°C", "°F", "%", "Ah", "VA"}


def get_sensors(*, definition: list[str], emparts: dict) -> list[SWSensor]:
    """Create a list of all SWSensors from the definitions and emparts."""
    res: list[SWSensor] = []
    for sensor_def in definition:
        name, _, mod = sensor_def.partition(":")

        if name not in emparts:
            _LOGGER.info("Unknown sensor: %s", name)
            pretty_print_dict(emparts, indent=5)
            continue

        sen = SWSensor(name=name, mod=mod, unit=emparts.get(f"{name}unit", ""))
        if sen.mod in ["min", "max"]:
            sen.interval = 60
        else:
            try:
                sen.interval = int(mod)
                sen.mod = "avg"
            except ValueError:
                sen.mod = ""
                sen.interval = 60
        res.append(sen)

    ic(res)
    return res
