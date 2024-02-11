class Topology:
    """Topology class for managing the network topology."""

    def __init__(self):
        self.nodes = set()

    def add_node(self, node):
        """Add a node to the topology."""
        self.nodes.add(node)
        print(f"Added node {node}")
