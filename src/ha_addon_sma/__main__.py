#!/usr/bin/env python3
"""Run the energy meter."""

import asyncio
import logging
import socket
import struct
import sys
from typing import Any

from .options import OPT
from .sensors import MQTT, SMA_EM_TOPIC, ic, process_emparts
from .speedwiredecoder import decode_speedwire

MCAST_PORT = 9522

_LOGGER = logging.getLogger(__name__)
WARN: dict[str, int] = {"0": 5}


def warn(serial: str) -> bool:
    """Print a warning."""
    num = WARN.get(serial, 1)
    if num < 1:
        return False
    WARN[serial] = num - 1
    return True


class MulticastServerProtocol(asyncio.DatagramProtocol):
    """Multicast receiver."""

    def connection_made(self, transport: Any) -> None:
        """Protocol connected."""
        _LOGGER.info(
            "Listening for frames on interface %s, for multicast group %s",
            OPT.ipbind,
            OPT.mcastgrp,
        )
        _LOGGER.info(
            "Sensor discovery will be triggered by the first frame containing these serial numbers: %s",
            ", ".join(OPT.sma_device_lookup),
        )

    def datagram_received(self, data: Any, addr: Any) -> None:
        """Process frame."""
        try:
            emparts = decode_speedwire(data)
        except Exception as err:
            if warn("0"):
                _LOGGER.warning("Could not decode Speedwire %s", err)
            return

        if not emparts:
            return

        serial = str(emparts["serial"])
        if serial not in OPT.sma_device_lookup:
            if warn(serial):
                _LOGGER.warning(
                    (
                        "Unknown SMA serial number %s. If you want to use this device,"
                        "please add SERIAL_NR and HA_PREFIX to SMA_DEVICES"
                    ),
                    serial,
                )
            return
        if "unknown" in emparts and warn(f"unknown{serial}"):
            _LOGGER.info("Unknown data in frame: %s", "\n".join(emparts["unknown"]))
            return
        asyncio.get_running_loop().create_task(process_emparts(emparts))


def connect_socket() -> socket.socket:
    """Connect."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", MCAST_PORT))
    try:
        # mreq = struct.pack("4s4s", group, socket.INADDR_ANY)
        mreq = struct.pack(
            "4s4s", socket.inet_aton(OPT.mcastgrp), socket.inet_aton(OPT.ipbind)
        )
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    except BaseException:
        print("could not connect to multicast group or bind to given interface")
        sys.exit(1)
    return sock


async def main() -> None:
    """Addon entry."""
    await OPT.init_addon()
    if OPT.debug == 0:
        ic.disable()
    loop = asyncio.get_event_loop()
    loop.set_debug(OPT.debug > 1)

    aid = sorted(d.ha_prefix for d in OPT.sma_devices)[0]
    MQTT.availability_topic = f"{SMA_EM_TOPIC}/availability_{aid}"

    await MQTT.connect(OPT)

    while True:
        sock = connect_socket()
        transport, _ = await loop.create_datagram_endpoint(
            MulticastServerProtocol,
            sock=sock,
        )
        try:
            await asyncio.sleep(OPT.reconnect_interval)
        finally:
            transport.close()
            sock.close()


if __name__ == "__main__":
    asyncio.run(main())
