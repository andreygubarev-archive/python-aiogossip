import asyncio
import json


class IPC:
    """IPC class for communicating with the Gossip server"""

    def __init__(self, peer, host: str = "127.0.0.1", port: int = 0):
        self.host = host
        self.port = port

        self.server = None

    async def recv(self):
        self.server = await asyncio.start_server(self.handler, self.host, self.port)
        self.port = self.server.sockets[0].getsockname()[1]

        print(f"ipc server listening on 127.0.0.1:{self.port}")

    async def send(self, command, params):
        data = json.dumps(
            {
                "command": command,
                "params": params,
            }
        ).encode()

        reader, writer = await asyncio.open_connection(self.host, self.port)
        writer.write(data)
        await writer.drain()

        writer.close()
        await writer.wait_closed()

    async def handler(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        while True:
            data = await reader.read(100)
            if not data:
                break

            data = json.loads(data.decode())
            command = data["command"]
            params = data["params"]
            print(f"Received {command} with {params}")

    async def close(self):
        self.server.close()
        await self.server.wait_closed()
        self.server = None
