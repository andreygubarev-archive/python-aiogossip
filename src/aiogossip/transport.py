import asyncio
import socket

import typeguard

from .address import Address, to_address


class UDPTransport:
    PACKET_SIZE = 8192

    @typeguard.typechecked
    def __init__(self, addr: Address, loop: asyncio.AbstractEventLoop):
        self.loop = loop

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((addr.ip.exploded, addr.port))
        self.sock.setblocking(False)

        self.addr = to_address(self.sock.getsockname())

        self.rx_bytes = 0
        self.rx_packets = 0
        self.tx_bytes = 0
        self.tx_packets = 0

    @typeguard.typechecked
    async def send(self, data: bytes, addr: Address):
        """
        Sends a message to the specified address.

        Args:
            data: The message to send.
            addr: The address to send the message to.

        Raises:
            TypeError: If the address is not of type Address.
            ValueError: If the message size exceeds the packet size.

        Returns:
            None
        """
        if len(data) > self.PACKET_SIZE:
            raise ValueError(f"Message size exceeds packet size of {self.PACKET_SIZE} bytes: {len(data)}")

        await self.loop.sock_sendto(self.sock, data, (addr.ip.exploded, addr.port))
        self.tx_packets += 1
        self.tx_bytes += len(data)

    @typeguard.typechecked
    async def recv(self) -> tuple[bytes, Address]:
        """
        Receives a data from the transport.

        Returns:
            A tuple containing the received data and the address it was received from.
        """
        data, addr = await self.loop.sock_recvfrom(self.sock, self.PACKET_SIZE)
        self.rx_packets += 1
        self.rx_bytes += len(data)

        addr = to_address(addr)
        return data, addr

    def close(self):
        """
        Closes the transport.
        """
        self.sock.close()
