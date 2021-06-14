"""Run the energy meter."""
import asyncio
import statistics
import sys
import time
from json import dumps, loads
from pathlib import Path
from typing import Any, Dict, Sequence

import attr
from asyncio_mqtt import Client
from icecream import ic


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


SENSORS: Dict[str, Sequence[SWSensor]] = {}
OPTIONS: Dict[str, Any] = {}
MQTT: Client = None


MQTT_HOST = "MQTT_HOST"
MQTT_PORT = "MQTT_PORT"
MQTT_USERNAME = "MQTT_USERNAME"
MQTT_PASSWORD = "MQTT_PASSWORD"
SERIALS = "SMA_SERIALS"
FIELDS = "FIELDS"
THRESHOLD = "THRESHOLD"

SMA_EM_TOPIC = "SMA-EM/status"


async def process_emparts(emparts: dict):
    serial = emparts["serial"]
    if not SENSORS.get(serial):
        SENSORS[serial] = get_sensors(definition=OPTIONS[FIELDS], emparts=emparts)
        for sen in SENSORS[serial]:
            await hass_discover_sensor(sma_id=serial, field=sen.name)

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

        ic(sen.name, sen.value)
        await MQTT.publish(
            f"{SMA_EM_TOPIC}/{emparts['serial']}/{sen.name}{sen.mod}", sen.value
        )

    if not push_later:
        return

    await asyncio.sleep(0.005)
    for sen, val, delta in push_later:
        sen.value = round(val, 1)
        ic(sen.name, sen.value, delta)
        await MQTT.publish(
            f"{SMA_EM_TOPIC}/{emparts['serial']}/{sen.name}{sen.mod}", sen.value
        )


# device_calss:current/energy/power
# unit_of_measurement
def hass_device_class(name: str):
    if name.endswith("counter"):
        return "energy"
    if name.startswith("u"):
        return "voltage"
    if name.endswith("frequency"):
        return None
    return "power"


async def hass_discover_sensor(*, sma_id: str, field: str):
    smap = ("", "", "")  # SENSOR_MAP.get(field, ("energy", ""))
    topic = f"homeassistant/sensor/{sma_id}/{field}/config"
    payload = dumps(
        {
            "name": field,
            "dev_cla": smap[0],
            "stat_t": f"{SMA_EM_TOPIC}/{sma_id}/{field}",
            "unit_of_meas": smap[1],
            "uniq_id": f"{sma_id}_{field}",
            "dev": {
                "ids": [f"sma_em_{sma_id}"],
                "name": "SMA Energy Meter",
                "mdl": "Energy Meter",
                "mf": "SMA",
            },
        }
    )

    ic(topic, payload)
    print("")
    await MQTT.connect()
    await MQTT.publish(topic, payload, retain=True)


def get_sensors(*, definition: str, emparts: dict):
    res = []
    for sensor_def in definition:
        name, _, mod = sensor_def.partition(":")

        if name not in emparts:
            print("Unknown sensor", name)
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
        sen.device_class = hass_device_class(name)
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
            SERIALS: [],
            FIELDS: ["pconsume"],
            THRESHOLD: 80,
            "DEBUG": 0,
        }
    )
    for key, val in options.items():
        OPTIONS[key] = val

    global MQTT
    MQTT = Client(
        hostname=OPTIONS[MQTT_HOST],
        port=OPTIONS[MQTT_PORT],
        username=OPTIONS[MQTT_USERNAME],
        password=OPTIONS[MQTT_PASSWORD],
    )
