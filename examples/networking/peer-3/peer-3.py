import asyncio

import aiogossip

peer = aiogossip.Peer(port=10003)


async def send():
    await asyncio.sleep(1)
    addr = aiogossip.to_address(("127.0.0.1", 10001))
    peer.send(b"peer-3: hello, world!", addr)


if __name__ == "__main__":
    peer._loop.create_task(send())
    peer.run()
