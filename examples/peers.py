import asyncio

from aiogossip.peer import Peer

loop = asyncio.get_event_loop()

peer1 = Peer(loop=loop)


@peer1.subscribe("test")
async def handler1(message):
    print("handler1", message)
    reply = {"message": "bar", "metadata": {}}
    await peer1.publish("test", reply)


peer2 = Peer(loop=loop)


@peer2.subscribe("test")
async def handler2(message):
    print("handler2", message)


async def main():
    peer1.run_forever()
    peer2.run_forever()
    peer2.connect([peer1.node])
    message = {"message": "foo", "metadata": {}}
    await peer2.publish("test", message)
    await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
