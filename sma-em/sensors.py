"""Run the energy meter."""
import asyncio
import logging
import statistics
import sys
import time
from json import dumps, loads
from pathlib import Path
from typing import Any, Dict, Sequence

import attr
from icecream import ic
from mqtt import MQTTClient

_LOGGER = logging.getLogger(__name__)


@attr.define
class SWSensor:
    """A speedwire sensor."""

    name = attr.field()
    mod = attr.field()  # 0 = mean, 1 = max, -1 = min
    last_update: int = attr.field(default=0)
    interval = attr.field(default=5)
    value = attr.field(default=0)
    values = attr.field(factory=list)
    unit = attr.field(default=None)
    device_class = attr.field(default=None)

    @property
    def id(self):
        if self.mod == "":
            return self.name
        if self.mod == "avg":
            return f"{self.name}_{self.interval}"
        return f"{self.name}_{self.mod}"


SENSORS: Dict[str, Sequence[SWSensor]] = {}
OPTIONS: Dict[str, Any] = {}
_MQTT = MQTTClient()


MQTT_HOST = "MQTT_HOST"
MQTT_PORT = "MQTT_PORT"
MQTT_USERNAME = "MQTT_USERNAME"
MQTT_PASSWORD = "MQTT_PASSWORD"
IPBIND = "IPBIND"
SERIALS = "SMA_SERIALS"
FIELDS = "FIELDS"
THRESHOLD = "THRESHOLD"
DEBUG = "DEBUG"
RECONNECT_INTERVAL = "RECONNECT_INTERVAL"
AUTODISCOVER_CONFIG = "AUTODISCOVER_CONFIG"

SMA_EM_TOPIC = "SMA-EM/status"


async def mqtt_publish(topic: str, payload: Any, retain: bool = False):
    await _MQTT.connect(
        username=OPTIONS[MQTT_USERNAME],
        password=OPTIONS[MQTT_PASSWORD],
        host=OPTIONS[MQTT_HOST],
        port=OPTIONS[MQTT_PORT],
    )
    if not topic:
        return
    ic(topic, payload)
    await _MQTT.publish(topic=topic, payload=payload, retain=retain)


async def process_emparts(emparts: dict):
    serial = emparts["serial"]
    if not SENSORS.get(serial):
        SENSORS[serial] = get_sensors(definition=OPTIONS[FIELDS], emparts=emparts)
        _LOGGER.info(
            "Discover %s/%s sensors on SMA %s",
            len(SENSORS[serial]),
            len(OPTIONS[FIELDS]),
            serial,
        )
        for sen in SENSORS[serial]:
            _LOGGER.info(" - %s every %ss", sen.id, sen.interval)
            await hass_discover_sensor(sma_id=serial, sensor=sen)
        await asyncio.sleep(5)

    push_later = []
    now = int(time.time())
    for sen in SENSORS[serial]:
        val = emparts.get(sen.name)

        publish = now >= sen.last_update + sen.interval

        # check threshold crossing
        smart_s = sen.mod == "" and sen.values
        if smart_s and val > sen.value + OPTIONS[THRESHOLD]:
            publish = True
            push_later.append((sen, val, OPTIONS[THRESHOLD]))
        elif smart_s and val < sen.value - 2 * OPTIONS[THRESHOLD]:
            publish = True
            push_later.append((sen, val, -2 * OPTIONS[THRESHOLD]))
        else:
            sen.values.append(val)

        if not publish:
            continue
        ic(now, val, sen.value, len(sen.values))

        sen.last_update = now
        if sen.mod == "min":
            sen.value = round(min(sen.values), 1)
        if sen.mod == "max":
            sen.value = round(max(sen.values), 1)
        else:
            sen.value = round(statistics.mean(sen.values), 1)
        sen.values = []

        await mqtt_publish(f"{SMA_EM_TOPIC}/{emparts['serial']}/{sen.id}", sen.value)

    if not push_later:
        return

    await asyncio.sleep(0.005)
    for sen, val, delta in push_later:
        sen.value = round(val, 1)
        ic(sen.name, sen.value, delta)
        await mqtt_publish(f"{SMA_EM_TOPIC}/{emparts['serial']}/{sen.id}", sen.value)


# device_calss:current/energy/power
# unit_of_measurement
def hass_device_class(*, unit: str):
    return {
        "W": "power",
        "kW": "power",
        "kVA": "power",
        "V": "voltage",
        "Hz": None,
    }.get(
        unit, "energy"
    )  # kwh, kVa,


async def hass_discover_sensor(*, sma_id: str, sensor: SWSensor):
    topic = f"homeassistant/sensor/{sma_id}/{sensor.id}/config"
    payload = {
        "name": sensor.id,
        "dev_cla": sensor.device_class,
        "stat_t": f"{SMA_EM_TOPIC}/{sma_id}/{sensor.id}",
        "unit_of_meas": sensor.unit,
        "uniq_id": f"{sma_id}_{sensor.id}",
        # "state_class": "measurement",
        # "last_reset": "2021-07-30T00:00:00+00:00",
        "dev": {
            "ids": [f"sma_em_{sma_id}"],
            "name": "SMA Energy Meter",
            "mdl": "Energy Meter",
            "mf": "SMA",
        },
    }
    if sensor.device_class == "energy":
        payload["state_class"] = "total_increasing"
    if isinstance(OPTIONS.get(AUTODISCOVER_CONFIG), list):
        for item in OPTIONS[AUTODISCOVER_CONFIG]:
            payload[item["key"]] = item["value"]

    await mqtt_publish(topic, dumps(payload), retain=True)


def get_sensors(*, definition: str, emparts: dict):
    res = []
    for sensor_def in definition:
        name, _, mod = sensor_def.partition(":")

        if name not in emparts:
            _LOGGER.info("Unknown sensor: %s", name)
            continue

        sen = SWSensor(name=name, mod=mod, unit=emparts.get(f"{name}unit"))
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


def startup():
    """Read the hassos configuration."""
    ofile = Path("/data/options.json")
    options = (
        loads(ofile.read_text())
        if ofile.exists()
        else {
            MQTT_HOST: "192.168.88.128",
            MQTT_PASSWORD: sys.argv[1],
            MQTT_PORT: 1883,
            MQTT_USERNAME: "hass",
            IP_BIND: "",
            SERIALS: [],
            FIELDS: [
                "pconsume",
                "pconsumecounter:max",
                "pconsume:5",
                "u1:min",
            ],
            THRESHOLD: 80,
            RECONNECT_INTERVAL: 86400,
            DEBUG: 0,
        }
    )
    for key, val in options.items():
        OPTIONS[key] = val

    if OPTIONS[DEBUG] == 0:

        def blank(*args):
            pass

        global ic
        ic = blank
