#!/usr/bin/env python3
"""Run the energy meter."""
import asyncio
import logging
import socket
import struct

import sensors
from speedwiredecoder import decode_speedwire

BROADCAST_ADDR = "239.12.255.254"
BROADCAST_PORT = 9522

_LOGGER = logging.getLogger(__name__)

class MulticastServerProtocol(asyncio.DatagramProtocol):
    def connection_made(self, _transport):
        pass

    def datagram_received(self, data, _addr):
        try:
            emparts = decode_speedwire(data)
        except Exception as err:
            _LOGGER.warning("Could not decode Speedwire %s", err)
        else:
            asyncio.get_running_loop().create_task(sensors.process_emparts(emparts))

def connect_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", BROADCAST_PORT))
    group = socket.inet_aton(BROADCAST_ADDR)
    mreq = struct.pack("4sL", group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT,)
    return sock

async def main():
    sensors.startup()
    logging.basicConfig(
        level=logging.DEBUG if sensors.OPTIONS["DEBUG"] != 0 else logging.INFO
    )

    LOOP = asyncio.get_event_loop()
    LOOP.set_debug(True)

    RECONNECT_INTERVAL = sensors.OPTIONS["RECONNECT_INTERVAL"]

    while True:
        _sock = connect_socket()
        _transport, _protocol = await LOOP.create_datagram_endpoint(
            MulticastServerProtocol,
            sock=_sock,
        )

        try:
            await asyncio.sleep(RECONNECT_INTERVAL)
        finally:
            _transport.close()
            _sock.close()

if __name__ == "__main__":
    # if os.name == "nt":
    #     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
