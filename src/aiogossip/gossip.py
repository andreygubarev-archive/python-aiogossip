from .topology import Topology


class Gossip:
    def __init__(self, node, transport, fanout=5):
        """
        Initialize a Gossip instance.

        Args:
            node (Node): The local node.
            transport (Transport): The transport layer for communication.
            fanout (int, optional): The number of nodes to gossip with. Defaults to 5.
        """
        self.node = node
        self.transport = transport
        self.fanout = fanout

        self.topology = Topology()
        self.topology.add_node(node)

    async def close(self):
        """
        Close the Gossip instance by closing the transport layer.
        """
        self.transport.close()
