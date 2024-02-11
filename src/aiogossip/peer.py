import argparse
import asyncio

import typeguard

from .address import Address, to_address
from .broker import Broker
from .dispatcher import Dispatcher
from .protocol import DatagramProtocol
from .topology import Topology


class Peer:
    def __init__(self, host: str = "0.0.0.0", port: int = 0, ipc_port: int = 0, loop: asyncio.AbstractEventLoop = None):
        self._host = host
        self._port = port
        self._ipc_port = ipc_port
        self._loop = loop or asyncio.get_event_loop()

        self.topology = Topology()
        self.dispatcher = Dispatcher(self._loop)
        self.broker = Broker(self._loop, self.topology, self.dispatcher.dispatch)

    @typeguard.typechecked
    def addr(self) -> Address:
        return self.broker.addr

    @typeguard.typechecked
    def send(self, data: bytes, addr: Address):
        self.broker.send(data, addr)

    @typeguard.typechecked
    def subscribe(self, handler: callable):
        self.dispatcher.add_handler(handler)

    async def _run(self):
        command_server = await asyncio.start_server(self.process_commands, "127.0.0.1", self._ipc_port)
        self.ipc_port = command_server.sockets[0].getsockname()[1]
        print(f"IPC server listening on 127.0.0.1:{self.ipc_port}")

        self.broker.transport, protocol = await self._loop.create_datagram_endpoint(
            lambda: DatagramProtocol(self._loop, self.broker.recv),
            local_addr=(self._host, self._port),
        )
        print(f"Listening on {self.broker.addr}")

        try:
            await protocol.transport_closed
        finally:
            self.broker.close()
            command_server.close()
            await command_server.wait_closed()

    def run(self):
        try:
            self._loop.run_until_complete(self._run())
        except KeyboardInterrupt:
            self.broker.close()
        finally:
            self._loop.close()

    async def process_commands(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        # Read the commands and process them
        while True:
            data = await reader.read(100)
            if not data:
                break
            addr = writer.get_extra_info("peername")
            print(f"Received {data.decode()} from {addr}")

    def main(self):
        parser = argparse.ArgumentParser(description="Gossip Peer.")
        parser.add_argument("command", choices=["run", "send"], help="The command to run.")
        parser.add_argument("params", nargs="*", help="Parameters for the command.")
        parser.add_argument("--ipc", type=str, help="The IPC address to connect to.")
        args = parser.parse_args()

        if args.command == "run":
            self.run()
        elif args.command == "send":
            ipc_addr = to_address(args.ipc)
            print(f"Sending to {ipc_addr}")

            data = " ".join(args.params).encode("utf-8")

            async def ipc_send():
                reader, writer = await asyncio.open_connection(str(ipc_addr.ip), ipc_addr.port)
                writer.write(data)
                await writer.drain()
                writer.close()
                await writer.wait_closed()

            self._loop.run_until_complete(ipc_send())
