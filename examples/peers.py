import asyncio

from aiogossip.peer import Peer

loop = asyncio.get_event_loop()

peer1 = Peer(loop=loop, identity="p1")


@peer1.subscribe("test")
async def handler1(message):
    print("handler1", message, "\n")
    reply = {"message": "bar", "metadata": {}}
    await peer1.publish("test", reply)


peer2 = Peer(loop=loop, identity="p2")
peer2.connect([peer1.node])


@peer2.subscribe("test")
async def handler2(message):
    print("handler2", message, "\n")


peer3 = Peer(loop=loop, identity="p3")
peer3.connect([peer1.node])


@peer3.subscribe("*")
async def handler3(message):
    print("handler3", message, "\n")


async def main():
    message = {"message": "foo", "metadata": {}}
    await asyncio.sleep(0.1)  # wait for connections to be established
    await peer2.publish("test", message)


if __name__ == "__main__":
    loop.create_task(main())
    peer1.run_forever()
    loop.run_until_complete(peer1.disconnect())
    loop.run_until_complete(peer2.disconnect())
    loop.run_until_complete(peer3.disconnect())
    loop.close()
