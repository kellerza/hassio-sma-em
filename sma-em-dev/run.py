import asyncio
import logging
import socket
import struct

import sensors
from speedwiredecoder import decode_speedwire

BROADCAST_ADDR = "239.12.255.254"
BROADCAST_PORT = 9522


class MulticastServerProtocol:
    def connection_made(self, _transport):
        pass

    def datagram_received(self, data, _addr):
        try:
            emparts = decode_speedwire(data)
        except Exception as err:
            logging.getLogger(__name__).warning("Could not decode Speedwire %s", err)
        else:
            asyncio.get_event_loop().create_task(sensors.process_emparts(emparts))


def main():
    LOOP = asyncio.get_event_loop()
    LOOP.set_debug(True)
    logging.basicConfig(level=logging.DEBUG)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", BROADCAST_PORT))
    group = socket.inet_aton(BROADCAST_ADDR)
    mreq = struct.pack("4sL", group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    sensors.startup()

    listen = LOOP.create_datagram_endpoint(
        MulticastServerProtocol,
        sock=sock,
    )
    print("done")

    _transport, _protocol = LOOP.run_until_complete(listen)

    LOOP.run_forever()
    LOOP.close()


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    main()
