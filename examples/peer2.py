import asyncio

import aiogossip

peer = aiogossip.Peer()


async def send():
    await asyncio.sleep(1)
    addr = aiogossip.to_address(("127.0.0.1", 12345))
    peer.send(b"Hello, world!", addr)


if __name__ == "__main__":
    peer._loop.create_task(send())
    peer.run()
