"""
Usage:
    GOSSIP_SEEDS=response@127.0.0.1:1337 python examples/reqresp/req.py
"""
import aiogossip

peer = aiogossip.Peer(peer_id="request")


async def main():
    message = aiogossip.Message()

    response = await peer.request("query", message)
    async for resp in response:
        print(resp)


if __name__ == "__main__":
    print("DSN:", peer.DSN)
    peer.connect()
    peer.run_forever(main=main)
