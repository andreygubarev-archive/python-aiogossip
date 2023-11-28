import asyncio
import json

import networkx as nx

from aiogossip.peer import Peer

loop = asyncio.get_event_loop()

peer0 = Peer(loop=loop, node_id="p0")
peer1 = Peer(loop=loop, node_id="p1")
peer1.connect([peer0.node])
peer2 = Peer(loop=loop, node_id="p2")
peer2.connect([peer1.node])
peer3 = Peer(loop=loop, node_id="p3")
peer3.connect([peer2.node, peer1.node])


@peer3.subscribe("*")
async def recv(message):
    print("RECV", message, "\n")
    if message.get("message") == "RELAY":
        print("RELAY", message["metadata"]["route"], "\n")


async def main():
    message = {"metadata": {}, "message": "RELAY"}
    await asyncio.sleep(0.1)  # wait for connections to be established
    await peer0.publish("test", message, nodes=[peer3.node_id])


if __name__ == "__main__":
    loop.create_task(main())
    peer0.run_forever()
    loop.run_until_complete(peer0.disconnect())
    loop.run_until_complete(peer1.disconnect())
    loop.run_until_complete(peer2.disconnect())
    loop.run_until_complete(peer3.disconnect())
    loop.close()

    print(json.dumps(nx.to_dict_of_dicts(peer1.gossip.topology.graph)))
    print(json.dumps(nx.to_dict_of_dicts(peer2.gossip.topology.graph)))
    print(json.dumps(nx.to_dict_of_dicts(peer3.gossip.topology.graph)))
