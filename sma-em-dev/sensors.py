"""Run the energy meter."""
import asyncio
import logging
import statistics
import time
from typing import Union

import attr
from icecream import ic
from mqtt_entity import Device, MQTTClient, SensorEntity
from mqtt_entity.helpers import hass_device_class
from options import OPT

_LOGGER = logging.getLogger(__name__)


@attr.define
class SWSensor:
    """A speedwire sensor."""

    # pylint: disable=too-many-instance-attributes,too-few-public-methods

    name: str = attr.field()
    mod: str = attr.field()  # 0 = mean, 1 = max, -1 = min
    last_update: int = attr.field(default=0)
    interval: int = attr.field(default=5)
    value: Union[int, float] = attr.field(default=0)
    values: list[Union[int, float]] = attr.field(factory=list)
    unit: str = attr.field(default="")
    device_class: str = attr.field(default="")
    mq_entity: SensorEntity = attr.field(default=None)

    @property
    def id(self) -> str:  # pylint: disable=invalid-name
        """Return the ID."""
        if self.mod == "":
            return self.name
        if self.mod == "avg":
            return f"{self.name}_{self.interval}"
        return f"{self.name}_{self.mod}"


SENSORS: dict[str, list[SWSensor]] = {}
MQ_CLIENT = MQTTClient()


SMA_EM_TOPIC = "SMA-EM/status"


async def process_emparts(emparts: dict) -> None:
    """Process emparts from the speedwire decoder."""
    # pylint: disable=too-many-branches
    if emparts["protocol"] not in [0x6069, 0x6081]:
        _LOGGER.info("Ignore protocol %s", hex(emparts["protocol"]))
        return

    serial = emparts["serial"]
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
        mq_dev = Device(
            identifiers=[serial, f"sma_em_{serial}"],
            name="SMA Energy Meter",
            model="Energy Meter",
            manufacturer="SMA",
        )

        for sen in SENSORS[serial]:
            _LOGGER.info(" - %s every %ss", sen.id, sen.interval)
            sen.mq_entity = SensorEntity(
                name=sen.id,
                device_class=sen.device_class,
                state_topic=f"{SMA_EM_TOPIC}/{serial}/{sen.id}",
                unique_id=f"{serial}_{sen.id}",
                unit_of_measurement=sen.unit,
                device=mq_dev,
            )

        await MQ_CLIENT.publish_discovery_info(
            [s.mq_entity for sl in SENSORS.values() for s in sl]
        )
        await asyncio.sleep(5)

    push_later: list[tuple[SWSensor, Union[int, float], int]] = []
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

        await MQ_CLIENT.publish(sen.mq_entity.state_topic, sen.value)

    if not push_later:
        return

    await asyncio.sleep(0.005)
    for sen, val, delta in push_later:
        sen.value = val
        ic(sen.name, sen.value, delta)
        await MQ_CLIENT.publish(sen.mq_entity.state_topic, sen.value)


def get_sensors(*, definition: list[str], emparts: dict) -> list[SWSensor]:
    """Create a list of all SWSensors from the definitions and emparts."""
    res: list[SWSensor] = []
    for sensor_def in definition:
        name, _, mod = sensor_def.partition(":")

        if name not in emparts:
            _LOGGER.info("Unknown sensor: %s", name)
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
        sen.device_class = hass_device_class(unit=sen.unit)
        res.append(sen)

    ic(res)
    return res
