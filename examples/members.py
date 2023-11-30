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
