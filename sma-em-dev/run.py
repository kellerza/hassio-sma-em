#!/usr/bin/env python3
"""Run the energy meter."""
import asyncio
import logging
import socket
import struct
import sys

import sensors
from options import OPT, init_options
from speedwiredecoder import decode_speedwire

MCAST_PORT = 9522
IPBIND = "0.0.0.0"

_LOGGER = logging.getLogger(__name__)


class MulticastServerProtocol(asyncio.DatagramProtocol):
    """Multicast receiver."""

    def connection_made(self, _transport):
        """Protocol connected."""
        _LOGGER.info(
            "Listening for multicast frames. "
            "Sensor discovery will be triggered by the first frame."
        )

    def datagram_received(self, data, _addr):
        """Process frame."""
        try:
            emparts = decode_speedwire(data)
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.warning("Could not decode Speedwire %s", err)
        else:
            asyncio.get_running_loop().create_task(sensors.process_emparts(emparts))


def connect_socket():
    """Connect."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", MCAST_PORT))
    try:
        # mreq = struct.pack("4s4s", group, socket.INADDR_ANY)
        mreq = struct.pack(
            "4s4s", socket.inet_aton(OPT.mcastgrp), socket.inet_aton(IPBIND)
        )
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    except BaseException:  # pylint: disable=broad-except
        print("could not connect to mulicast group or bind to given interface")
        sys.exit(1)
    return sock


async def main():
    """Addon entry."""
    init_options()

    sensors.MQ_CLIENT.availability_topic = (
        f"{sensors.SMA_EM_TOPIC}/{''.join(OPT.sma_serials)}/available"
    )

    await sensors.MQ_CLIENT.connect(options=OPT)

    if OPT.debug == 0:
        sensors.ic.disable()

    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    while True:
        _sock = connect_socket()
        _transport, _protocol = await loop.create_datagram_endpoint(
            MulticastServerProtocol,
            sock=_sock,
        )

        try:
            await asyncio.sleep(OPT.reconnect_interval)
        finally:
            _transport.close()
            _sock.close()


if __name__ == "__main__":
    # if os.name == "nt":
    #     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
