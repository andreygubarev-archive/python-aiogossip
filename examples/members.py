import asyncio
import os

import aiogossip

peer = aiogossip.Peer()


async def main():
    while True:
        asyncio.sleep(5)
        print("Members:")
        for node in peer.nodes:
            print(node)


if __name__ == "__main__":
    print("Peer: ", peer.node)

    seeds = os.getenv("GOSSIP_SEEDS")
    peer.connect(seeds)
    peer.run_forever(main=main)
