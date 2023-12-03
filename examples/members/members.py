"""
Usage:
    GOSSIP_ID=p1 GOSSIP_PORT=1337 python examples/members/members.py
    GOSSIP_ID=p2 GOSSIP_SEEDS=p1@127.0.0.1:1337 python examples/members/members.py
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
            reachable = peer.gossip.topology[node]["reachable"]
            print("-", node, "reachable" if reachable else "unreachable")
        print()


if __name__ == "__main__":
    print("DSN:", peer.DSN)
    peer.connect()
    peer.run_forever(main=main)
