"""Run the energy meter."""

import asyncio
import logging
import statistics
import time

import attr
from icecream import ic
from mqtt_entity import MQTTClient, MQTTDevice, MQTTSensorEntity
from mqtt_entity.helpers import hass_device_class

from .helpers import pretty_print_dict
from .options import OPT

_LOG = logging.getLogger(__name__)

HA_MEASUREMENT = ("W", "V", "A", "Hz", "°C", "°F", "%", "Ah", "VA")
HA_COUNTER = ("Wh", "kWhvarh", "kvarh")

MQTT = MQTTClient(origin_name="SMA Energy Meter")


@attr.define
class SWSensor:
    """A speedwire sensor."""

    name: str
    mod: str
    """Min,max, or a number to indicate seconds."""
    last_update: int = 0
    interval: int = 60
    value: int | float | str = 0
    values: list[int | float] = attr.field(factory=list)
    unit: str = ""
    mq_entity: MQTTSensorEntity = attr.field(default=None)

    def __post_attrs_init__(self) -> None:
        """Post init."""
        if self.name in ("speedwire-version",):
            self.mod = ""
            self.value = ""
            return

        if self.name.endswith("counter"):
            if self.mod not in ("max", ""):
                _LOG.warning("Counter sensor %s will only return the max", self.name)
            self.mod = "max"
            self.interval = 60
            return

        if self.mod in ["min", "max"]:
            self.interval = 60
        else:
            try:
                self.interval = int(self.mod)
                self.mod = "avg"
            except ValueError:
                self.mod = ""
                self.interval = 60

    @property
    def id(self) -> str:
        """Return the ID."""
        if self.mod == "" or self.name.endswith("counter"):
            return self.name
        if self.mod == "avg":
            return f"{self.name}_{self.interval}"
        return f"{self.name}_{self.mod}"


SENSORS: dict[str, list[SWSensor]] = {}


SMA_EM_TOPIC = "SMA-EM/status"


async def process_emparts(emparts: dict) -> None:  # noqa: PLR0912
    """Process emparts from the speedwire decoder."""
    if emparts["protocol"] not in [0x6069, 0x6081]:
        _LOG.info("Ignore protocol %s", hex(emparts["protocol"]))
        return

    serial = str(emparts["serial"])
    if serial not in SENSORS:
        _LOG.info("Multicast frame received for SMA %s", serial)
        discover_sensors(definition=OPT.fields, emparts=emparts, serial=serial)
        await MQTT.publish_discovery_info()
        MQTT.monitor_homeassistant_status()
        await asyncio.sleep(5)

    push_later: list[tuple[SWSensor, int | float, int]] = []
    now = int(time.time())
    for sen in SENSORS[serial]:
        val = emparts.get(sen.name)
        if val is None:
            continue

        # treat string values differently
        if isinstance(sen.value, str) or isinstance(val, str):
            if val != sen.value:
                sen.value = str(val)
                await sen.mq_entity.send_state(MQTT, sen.value)
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


def discover_sensors(*, definition: list[str], emparts: dict, serial: str) -> None:
    """Create a list of all SWSensors from the definitions and emparts."""
    ha_prefix = OPT.sma_device_lookup.get(serial, "sma")
    mq_dev = MQTTDevice(
        identifiers=[serial, f"sma_em_{serial}"],
        # https://github.com/kellerza/sunsynk/issues/165
        # name=f"{OPT.manufacturer} AInverter {serial_nr}",
        name=ha_prefix,  # name="SMA Energy Meter",
        model="Energy Meter",
        manufacturer="SMA",
        components={},
    )
    MQTT.devs.append(mq_dev)
    result: dict[str, SWSensor] = {}

    for sensor_def in definition:
        name, _, mod = sensor_def.partition(":")
        if name not in emparts:
            _LOG.info("Unknown sensor: %s", name)
            pretty_print_dict(emparts, indent=5)
            continue

        sen = SWSensor(name=name, mod=mod, unit=emparts.get(f"{name}unit", ""))

        if sen.id in result:
            _LOG.warning("Sensor %s already exists for SMA %s", sen.id, serial)
            continue
        result[sen.id] = sen

        _LOG.info(" - %s (%s) every %ss ", sen.id, sen.unit, sen.interval)
        sen.mq_entity = MQTTSensorEntity(
            name=sen.id,
            device_class=hass_device_class(unit=sen.unit),
            state_topic=f"{SMA_EM_TOPIC}/{serial}/{sen.id}",
            unique_id=f"{serial}_{sen.id}",
            unit_of_measurement=sen.unit,
            state_class="measurement" if sen.unit in HA_MEASUREMENT else "",
            object_id=f"{ha_prefix} {sen.name}".lower(),
            suggested_display_precision=1
            if sen.unit in HA_MEASUREMENT or sen.unit in HA_COUNTER
            else 0,
        )

    mq_dev.components = {k: s.mq_entity for k, s in result.items()}
    SENSORS[serial] = sss = list(result.values())
    _LOG.debug("Added %s/%s sensors for SMA %s", len(sss), len(OPT.fields), serial)
