"""
Usage:
    GOSSIP_SEEDS=4aed4f3c6900462baa1413fb7ef4f814@127.0.0.1:58295 python examples/members.py
"""
import aiogossip

peer = aiogossip.Peer()


async def main():
    message = aiogossip.Message(payload=b"payload")
    await peer.publish("topic", message)


if __name__ == "__main__":
    print("DSN:", peer.DSN)
    peer.connect()
    peer.run_forever(main=main)
