import asyncio

from aiogossip.peer import Peer

loop = asyncio.get_event_loop()

peer1 = Peer(loop=loop)
peer1.run_forever()


@peer1.subscribe("test")
async def handler1(message):
    print("handler1", message)
    reply = {"message": "bar", "metadata": {}}
    await peer1.publish("test", reply)


peer2 = Peer(loop=loop)
peer2.connect([peer1.node])
peer2.run_forever()


@peer2.subscribe("test")
async def handler2(message):
    print("handler2", message)


peer3 = Peer(loop=loop)
peer3.connect([peer1.node])
peer3.run_forever()


@peer3.subscribe("*")
async def handler3(message):
    print("handler3", message)


async def main():
    message = {"message": "foo", "metadata": {}}
    await asyncio.sleep(0.1)  # wait for connections to be established
    await peer2.publish("test", message)
    await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
