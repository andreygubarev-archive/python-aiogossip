"""
aiogossip.cli - Command line interface for aiogossip
"""

import argparse
import os

from aiogossip.peer import Peer


def main():
    parser = argparse.ArgumentParser(description="aiogossip")
    parser.add_argument("--name", default=None, help="name of the peer")
    parser.add_argument("--host", default="0.0.0.0", help="host to bind to")
    parser.add_argument("--port", default=0, type=int, help="port to bind to")
    parser.add_argument("--seeds", default=None, help="comma separated list of seeds")
    args = parser.parse_args()

    print("aiogossip: starting peer '{}': {}".format(args.name, os.getpid()))
    peer = Peer(host=args.host, port=args.port, peer_id=args.name)
    if args.seeds:
        print("aiogossip: connecting to seeds {}".format(args.seeds))
        peer.connect(args.seeds)
    print("aiogossip: peer started as {}".format(peer.DSN))
    peer.run_forever()


if __name__ == "__main__":
    main()
