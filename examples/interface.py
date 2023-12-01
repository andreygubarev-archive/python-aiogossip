# Sender ######################################################################
from aiogossip import Peer, Message  # noqa

sender = Peer()


async def main():
    message = Message()
    response = await sender.request("query", message, peers=[sender.peers[0]])
    async for resp in response:
        print(resp)


if __name__ == "__main__":
    sender.run_forever(main=main)

# Receiver ####################################################################
from aiogossip import Peer  # noqa

receiver = Peer()
receiver.connect([sender])


@receiver.response("query")
async def resp(message):
    print(message)
    return Message(payload=b"response")


if __name__ == "__main__":
    receiver.run_forever()

# Pub #########################################################################
from aiogossip import Peer  # noqa

publisher = Peer()


async def main():
    message = Message()
    await publisher.publish("event", message)


if __name__ == "__main__":
    publisher.run_forever(main=main)

# Sub #########################################################################

from aiogossip import Peer  # noqa

subscriber = Peer()
subscriber.connect([publisher])


@subscriber.subscribe("event")
async def event(message):
    print(message)


if __name__ == "__main__":
    subscriber.run_forever()
