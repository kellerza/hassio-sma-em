#!/usr/bin/env python3
"""Run the energy meter."""
import importlib
from json import dumps, loads
import os
from pathlib import Path

import paho.mqtt.client as mqtt
from icecream import ic

MQTT_HOST = "MQTT_HOST"
MQTT_PORT = "MQTT_PORT"
MQTT_USERNAME = "MQTT_USERNAME"
MQTT_PASSWORD = "MQTT_PASSWORD"
SERIALS = "SMA_SERIALS"
FIELDS = "FIELDS"


# device_calss:current/energy/power
# unit_of_measurement
SENSOR_MAP = {
    "pconsumecounter": ("energy", "kWh"),
    "psupplycounter": ("energy", "kWh"),
    "frequency": (None, "Hz"),
    "pconsume": ("power", "W"),
    "psupply": ("power", "W"),
    "u1": ("voltage", "V"),
    "u2": ("voltage", "V"),
    "u3": ("voltage", "V"),
}


def sensor(client, sma_id, field):
    unique_id = f"{sma_id}_{field}"
    state_t = f"SMA-EM/status/{sma_id}/{field}"

    smap = SENSOR_MAP.get(field, ("energy", ""))

    topic = f"homeassistant/sensor/{unique_id}/config"
    payload = dumps(
        {
            "name": field,
            "device_class": smap[0],
            "state_topic": state_t,
            "unit_of_measurement": smap[1],
            "uniq_id": unique_id,
        }
    )

    ic(topic, payload)
    print("")
    client.publish(topic, payload)


def discover_all(opt):
    print("Homeassistant Auto-discovery:")

    client = mqtt.Client(client_id="sma-em-hassos")
    client.username_pw_set(username=opt[MQTT_USERNAME], password=opt[MQTT_PASSWORD])
    client.connect(opt[MQTT_HOST], opt[MQTT_PORT])
    client.loop_start()  # threaded

    for sma_id in opt[SERIALS].split(" "):
        for field in opt[FIELDS].split(","):
            sensor(client, sma_id, field)

    client.loop_stop()
    client.disconnect()


def main():
    # Read the hassos configuration
    options = loads(Path("/data/options.json").read_text())
    
    if not options.get(SERIALS):
        ic("No SMA_SERIALS configured, capturing a SINGLE debug packet")
        os.system("./sma-em-capture-package.py | grep serial")
        while True:
           pass

    # options[FIELDS] = "pconsume,pconsumecounter"
    # Read the template
    config = Path("config.ini").read_text()
    for key, val in options.items():
        config = config.replace(f"${key}", str(val))

    discover_all(options)

    Path("config").write_text(config)

    smad = importlib.import_module("sma-daemon")
    daemon = smad.MyDaemon(smad.pidfile)
    daemon.run()


if __name__ == "__main__":
    main()
