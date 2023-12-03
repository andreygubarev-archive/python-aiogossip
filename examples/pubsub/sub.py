"""
Usage:
    python examples/pubsub/sub.py
"""
import aiogossip

peer = aiogossip.Peer(port=1337, peer_id="subscriber")


@peer.subscribe("*")
async def on_message(message):
    print(message)


if __name__ == "__main__":
    print("DSN:", peer.DSN)
    peer.connect()
    peer.run_forever()
