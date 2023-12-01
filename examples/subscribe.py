"""
Usage:
    GOSSIP_SEEDS=4aed4f3c6900462baa1413fb7ef4f814@127.0.0.1:58295 python examples/subscribe.py
"""
import aiogossip

peer = aiogossip.Peer()


@peer.subscribe("*")
async def on_message(message):
    print(message)


if __name__ == "__main__":
    print("DSN:", peer.DSN)
    peer.connect()
    peer.run_forever()
