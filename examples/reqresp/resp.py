"""
Usage:
    python examples/reqresp/resp.py
"""
import aiogossip

peer = aiogossip.Peer(port=1337, peer_id="response")


@peer.response("query")
async def query(message):
    return aiogossip.Message(payload=b"response")


if __name__ == "__main__":
    print("DSN:", peer.DSN)
    peer.connect()
    peer.run_forever()
