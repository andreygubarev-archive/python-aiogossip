import aiogossip

peer = aiogossip.Peer(port=10001)


@peer.subscribe
async def handler(msg, addr):
    print(f"peer-1: handler received {msg} from {addr}")


if __name__ == "__main__":
    peer.main()
