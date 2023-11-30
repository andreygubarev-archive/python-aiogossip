"""
Usage:
    GOSSIP_SEEDS=4aed4f3c6900462baa1413fb7ef4f814@127.0.0.1:58295 python examples/members.py
"""
import asyncio
import os

import aiogossip

peer = aiogossip.Peer()


async def main():
    while True:
        await asyncio.sleep(5)
        print("---")
        print("members:")
        for node in peer.nodes:
            print("-", node)
        print()


if __name__ == "__main__":
    print("---")
    print("peer: ")
    print("  id:", peer.node["node_id"])

    addr = list(peer.node["node_addr"])
    if addr[0] == "0.0.0.0":
        addr[0] = "127.0.0.1"
    addr = ":".join(str(a) for a in addr)

    print("  addr:", addr)
    print()

    seeds = os.getenv("GOSSIP_SEEDS")
    peer.connect(seeds)
    peer.run_forever(main=main)
