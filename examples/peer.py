import aiogossip

peer = aiogossip.Peer(port=12345)


@peer.subscribe
async def handler(data, addr):
    print(f"Handler received {data} from {addr}")


if __name__ == "__main__":
    peer.run()
