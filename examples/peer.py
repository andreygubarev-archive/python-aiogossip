import aiogossip

peer = aiogossip.Peer(port=12345)

if __name__ == "__main__":
    peer.run()
