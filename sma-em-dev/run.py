#!/usr/bin/env python3
"""Run the energy meter."""
import socket
import struct
import time
import traceback
from contextlib import contextmanager
from json import dumps, loads
from pathlib import Path

import attr
import paho.mqtt.client as mqtt
from icecream import ic
from speedwiredecoder import decode_speedwire

MCAST_GROUP = "239.12.255.254"
MCAST_PORT = 9522
BIND_IP = "0.0.0.0"

MQTT_HOST = "MQTT_HOST"
MQTT_PORT = "MQTT_PORT"
MQTT_USERNAME = "MQTT_USERNAME"
MQTT_PASSWORD = "MQTT_PASSWORD"
SERIALS = "SMA_SERIALS"
FIELDS = "FIELDS"

SMA_EM_TOPIC = "SMA-EM/status"


@contextmanager
def mqtt_client(opt):
    """Connect to the MQTT broker provide the client."""
    client = mqtt.Client(client_id="sma-em-hassos")
    client.username_pw_set(username=opt[MQTT_USERNAME], password=opt[MQTT_PASSWORD])
    sleep = 5
    while True:
        try:
            client.connect(opt[MQTT_HOST], opt[MQTT_PORT])
            client.loop_start()  # threaded
            break
        except Exception as e:
            print("Could not connect to the MQTT client:", str(e))
            time.sleep(sleep)
            if sleep < 60:
                sleep += 10

    try:
        yield client
    finally:
        client.loop_stop()
        client.disconnect()


def yield_sma_emparts():
    """Receive multicast Speedwire datagrams."""
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", MCAST_PORT))
        try:
            mreq = struct.pack(
                "4s4s", socket.inet_aton(MCAST_GROUP), socket.inet_aton(BIND_IP)
            )
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            print("Multicast group connected")
        except BaseException:
            print("Could not connect to the mulicast group... will retry in 5s")
            time.sleep(5)
        else:
            try:
                while True:
                    yield decode_speedwire(sock.recv(608))
            finally:
                print("closing socket")
                sock.close()


# device_calss:current/energy/power
# unit_of_measurement
def hass_device_class(name):
    if name.endswith("counter"):
        return "energy"
    if name.startswith("u"):
        return "voltage"
    if name.endswith("frequency"):
        return None
    return "power"


def hass_discover_sensor(*, client, sma_id, field):
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
    client.publish(topic, payload, retain=True)


@attr.define
class SWSensor:
    """A speedwire sensor."""

    name = attr.field()
    mod = attr.field()  # 0 = mean, 1 = max, -1 = min
    last = attr.field(default=0)
    interval = attr.field(default=5)
    values = attr.field(factory=list)
    unit = attr.field(default=None)
    device_class = attr.field(default=None)


THRESHOLD_ABS = 70  # W
THRESHOLD_REL = 100  # %


def get_sensors(definition, emparts):
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
                sen.mod = "smart"
                sen.interval = 50
        sen.device_class = hass_device_class(name)
        res.append(sen)

    ic(res)
    return res


def process_sensors(sensors, emparts):
    pass


def main():
    # Read the hassos configuration
    options = loads(Path("/data/options.json").read_text())

    sensors = {}
    while True:
        with mqtt_client(options) as client:
            try:
                for emparts in yield_sma_emparts():
                    serial = emparts["serial"]
                    if not sensors.get(serial):
                        sensors[serial] = get_sensors(options[FIELDS], emparts)
                        for sen in sensors[serial]:
                            hass_discover_sensor(
                                client=client, sma_id=serial, field=sen.name
                            )
                    process_sensors(client, emparts, sensors[serial])
            except Exception as err:
                print("Daemon: Exception occurred", err)
                print(traceback.format_exc())
                return  # will attempt to rebind the socket


if __name__ == "__main__":
    main()
