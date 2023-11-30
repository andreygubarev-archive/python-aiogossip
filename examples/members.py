"""
Usage:
    GOSSIP_SEEDS=4aed4f3c6900462baa1413fb7ef4f814@127.0.0.1:58295 python examples/members.py
"""
import asyncio
import json
import os

import aiogossip

peer = aiogossip.Peer()


@peer.subscribe("*")
async def on_message(message):
    print("---")
    print("receive: ", json.dumps(message))


async def main():
    while True:
        await asyncio.sleep(10)
        print("---")
        print("members:")
        for node in peer.nodes:
            print("-", node)
        print()


if __name__ == "__main__":
    print("dsn:", peer.dsn)
    seeds = os.getenv("GOSSIP_SEEDS")
    peer.connect(seeds)
    peer.run_forever(main=main)
