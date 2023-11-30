"""
Usage:
    GOSSIP_SEEDS=4aed4f3c6900462baa1413fb7ef4f814@127.0.0.1:58295 python examples/members.py
"""
import os

import aiogossip

peer = aiogossip.Peer()


async def main():
    response = await peer.request("query", {"metadata": {}})
    async for resp in response:
        print(resp)


if __name__ == "__main__":
    print(peer.dsn)
    seeds = os.getenv("GOSSIP_SEEDS")
    peer.connect(seeds)
    peer.run_forever(main=main)
