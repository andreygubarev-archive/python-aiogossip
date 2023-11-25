import asyncio

from aiogossip.peer import Peer

peer1 = Peer()


@peer1.subscribe("*")
async def handler1(message):
    print(message)
    reply = {"message": "bar", "metadata": {}}
    await peer1.publish("test", reply)


peer2 = Peer()


@peer2.subscribe("*")
async def handler2(message):
    print(message)


def main():
    peer1.run_forever()
    peer2.run_forever()
    peer2.connect([peer1.node])
    message = {"message": "foo", "metadata": {}}
    peer1.publish("test", message)


if __name__ == "__main__":
    asyncio.run(main())
