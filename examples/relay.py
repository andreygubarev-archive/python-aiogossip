import asyncio
import json

import networkx as nx

from aiogossip.peer import Peer

loop = asyncio.get_event_loop()

peer1 = Peer(loop=loop, identity="p1")
peer2 = Peer(loop=loop, identity="p2")
peer2.connect([peer1.node])
peer3 = Peer(loop=loop, identity="p3")
peer3.connect([peer2.node])


@peer3.subscribe("*")
async def recv(message):
    print("recv", message, "\n")


async def main():
    message = {"metadata": {}}
    await asyncio.sleep(0.1)  # wait for connections to be established
    await peer1.publish("test", message, nodes=[peer3.identity])


if __name__ == "__main__":
    loop.create_task(main())
    peer1.run_forever()
    loop.run_until_complete(peer1.disconnect())
    loop.run_until_complete(peer2.disconnect())
    loop.run_until_complete(peer3.disconnect())
    loop.close()

    print(json.dumps(nx.to_dict_of_dicts(peer1.gossip.topology.graph)))
    print(json.dumps(nx.to_dict_of_dicts(peer2.gossip.topology.graph)))
    print(json.dumps(nx.to_dict_of_dicts(peer3.gossip.topology.graph)))
