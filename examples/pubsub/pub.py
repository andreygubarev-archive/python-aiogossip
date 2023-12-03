"""
Usage:
    GOSSIP_SEEDS=subscriber@127.0.0.1:1337 python examples/pubsub/pub.py
"""
import aiogossip

peer = aiogossip.Peer(peer_id="publisher")


async def main():
    message = aiogossip.Message(payload=b"payload")
    await peer.publish("topic", message)


if __name__ == "__main__":
    print("DSN:", peer.DSN)
    peer.connect()
    peer.run_forever(main=main)
