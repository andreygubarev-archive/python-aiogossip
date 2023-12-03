import asyncio
import ipaddress
import logging
import os
import socket
import sys

from . import codec
from .address import Address

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
if os.environ.get("DEBUG"):
    logger.setLevel(logging.DEBUG)  # pragma: no cover


class Transport:
    """
    Represents a transport layer for sending and receiving messages over UDP.
    """

    PACKET_SIZE = 4096

    def __init__(self, bind, loop: asyncio.AbstractEventLoop):
        self._loop = loop

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(bind)
        self.sock.setblocking(False)

        self.rx_bytes = 0
        self.rx_packets = 0
        self.tx_bytes = 0
        self.tx_packets = 0

    @property
    def addr(self):
        """
        Returns the local address of the transport.
        """
        ip, port = self.sock.getsockname()
        ip = ipaddress.ip_address(ip)
        return Address(ip, port)

    async def send(self, message, addr: Address):
        """
        Sends a message to the specified address.

        Args:
            message: The message to send.
            addr: The address to send the message to.

        Raises:
            TypeError: If the address is not of type Address.
            ValueError: If the message size exceeds the packet size.

        Returns:
            None
        """
        if not isinstance(addr, Address):
            raise TypeError(f"Address must be a tuple, got: {type(addr)}")
        if not isinstance(addr.ip, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            raise TypeError(f"IP address must be IPv4, got: {type(addr.ip)}")
        if not isinstance(addr.port, int):
            raise TypeError(f"Port must be an integer, got: {type(addr.port)}")

        msg = codec.encode(message)
        if len(msg) > self.PACKET_SIZE:
            raise ValueError(f"Message size exceeds packet size of {self.PACKET_SIZE} bytes: {len(msg)}")

        await self._loop.sock_sendto(self.sock, msg, (addr.ip.exploded, addr.port))
        self.tx_packets += 1
        self.tx_bytes += len(msg)

        logger.debug(f"DEBUG: {self.addr[1]} > {addr[1]} send: {message}\n")

    async def recv(self):
        """
        Receives a message from the transport.

        Returns:
            A tuple containing the received message and the address it was received from.
        """
        msg, addr = await self._loop.sock_recvfrom(self.sock, self.PACKET_SIZE)
        self.rx_packets += 1
        self.rx_bytes += len(msg)

        addr = Address(ipaddress.ip_address(addr[0]), int(addr[1]))
        message = codec.decode(msg)
        logger.debug(f"DEBUG: {self.addr.port} < {addr.port} recv: {message}\n")

        return message, addr

    def close(self):
        """
        Closes the transport.
        """
        self.sock.close()
