"""
Usage:
    GOSSIP_SEEDS=4aed4f3c6900462baa1413fb7ef4f814@127.0.0.1:58295 python examples/members.py
"""
import asyncio
import os

import aiogossip

peer_id = os.getenv("GOSSIP_ID")
port = int(os.getenv("GOSSIP_PORT", 0))
peer = aiogossip.Peer(port=port, peer_id=peer_id)


async def main():
    while True:
        await asyncio.sleep(10)
        print("---")
        print("members:")
        for node in peer.nodes:
            print("-", node)
        print()


if __name__ == "__main__":
    print("DSN:", peer.DSN)
    peer.connect()
    peer.run_forever(main=main)
