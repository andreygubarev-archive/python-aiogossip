import aiogossip

peer = aiogossip.Peer(port=10002)


@peer.subscribe
async def handler(msg, addr):
    print(f"peer-2: handler received {msg} from {addr}")


if __name__ == "__main__":
    peer.run()
