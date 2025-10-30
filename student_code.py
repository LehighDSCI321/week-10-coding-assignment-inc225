"""
Graph Data Structures Implementation

This module provides a hierarchy of graph classes:
- VersatileDigraph: Base directed graph with nodes and edges
- SortableDigraph: Adds topological sorting capability  
- TraversableDigraph: Adds DFS and BFS traversal methods
- DAG: Directed Acyclic Graph that prevents cycle creation
"""

from collections import deque


class VersatileDigraph:
    """This is the versatile digraph class"""

    def __init__(self):
        self._edge_weights = {}
        self._edge_names = {}
        self._edge_head = {}
        self._node_values = {}

    def add_edge(self, tail, head, **vararg):
        """Adds an edge to the graph"""
        if not isinstance(tail, str) or not isinstance(head, str):
            raise TypeError("Head and tail must be strings.")

        if tail not in self.get_nodes():
            self.add_node(tail, vararg.get("start_node_value", 0))

        if head not in self.get_nodes():
            self.add_node(head, vararg.get("end_node_value", 0))

        edge_name = vararg.get("name", tail + " to " + head)
        self._edge_names[tail][head] = edge_name
        self._edge_head[tail][head] = head

        # Use edge_weight instead of weight to match test expectations
        weight = vararg.get("edge_weight", vararg.get("weight", 0))
        if weight >= 0:
            self._edge_weights[tail][head] = weight
        else:
            raise ValueError("Edge weight must be positive.")

    def get_nodes(self):
        """Returns a list of nodes in the graph"""
        return list(self._node_values.keys())

    def add_node(self, node_id, node_value=0):
        """Adds a node to the graph"""
        if not isinstance(node_id, str) or not isinstance(node_value, (float, int)):
            raise TypeError("Node ID must be a string and node value must be numeric.")

        self._node_values[node_id] = node_value
        self._edge_weights[node_id] = {}
        self._edge_names[node_id] = {}
        self._edge_head[node_id] = {}

    def get_edge_weight(self, tail, head):
        """Return the weight of an edge"""
        if tail not in self.get_nodes():
            raise KeyError("Node " + tail + " is not present in the graph.")
        if head not in self.get_nodes():
            raise KeyError("Node " + head + " is not present in the graph.")
        if head not in self._edge_weights[tail]:
            raise KeyError("The specified edge does not exist in the graph")
        return self._edge_weights[tail][head]

    def get_node_value(self, node):
        """Return the value of a node"""
        if node not in self.get_nodes():
            raise KeyError("Node " + node + " is not present in the graph.")
        return self._node_values[node]

    def print_graph(self):
        """Prints sentences describing the graph"""
        for tail in self.get_nodes():
            print("Node " + str(tail) + " has a value of " +
                  str(self.get_node_value(tail)) + ".")
            for head in self._edge_weights[tail]:
                print("There is an edge from node " + str(tail) + " to node " + str(head) +
                      " of weight " +
                      str(self.get_edge_weight(tail, head)) + " and name " +
                      self._edge_names[tail][head] + ".")

    def predecessors(self, node):
        """Returns a list of the predecessors of a node"""
        if node not in self.get_nodes():
            raise KeyError("Node " + node + " is not present in the graph.")

        return [n for n in self.get_nodes() if node in self._edge_names[n]]

    def successors(self, node):
        """Returns a list of the successors of a node"""
        if node not in self.get_nodes():
            raise KeyError("Node " + node + " is not present in the graph.")
        return list(self._edge_names[node].keys())

    def in_degree(self, node):
        """Returns the in-degree of a node"""
        if node not in self.get_nodes():
            raise KeyError("Node " + node + " is not present in the graph.")
        return len(self.predecessors(node))

    def out_degree(self, node):
        """Returns the out-degree of a node"""
        if node not in self.get_nodes():
            raise KeyError("Node " + node + " is not present in the graph.")
        return len(self.successors(node))

    def successor_on_edge(self, tail, edge_name):
        """
        Given a node and an edge name, identify the successor of
        the node on the edge with the provided name
        """
        if tail not in self.get_nodes():
            raise KeyError("Node " + tail + " is not present in the graph.")

        # Find the head node that has this edge name
        for head, name in self._edge_names[tail].items():
            if name == edge_name:
                return head

        raise KeyError(f"There is no edge '{edge_name}' associated with node {tail}")


class SortableDigraph(VersatileDigraph):
    """A digraph that can be topologically sorted"""

    def top_sort(self):
        """
        Returns a topologically sorted list of nodes in the graph
        Based on Listing 4-10 in Python Algorithms
        """
        # Count in-degrees for all nodes
        in_degree = {}
        for node in self.get_nodes():
            in_degree[node] = self.in_degree(node)

        # Initialize queue with all nodes that have no incoming edges
        queue = [node for node in self.get_nodes() if in_degree[node] == 0]
        result = []

        while queue:
            # Take a node with no incoming edges
            node = queue.pop(0)
            result.append(node)

            # For each neighbor, decrease in-degree and add to queue if it becomes 0
            for neighbor in self.successors(node):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check if we have a cycle (not all nodes processed)
        if len(result) != len(self.get_nodes()):
            raise ValueError("Graph has at least one cycle, topological sort not possible")

        return result


class TraversableDigraph(SortableDigraph):
    """A digraph that supports DFS and BFS traversals"""

    def dfs(self, start=None):
        """
        Depth-first search traversal based on Listing 5-5 from Python Algorithms
        NOTE: The test expects the starting node to NOT be included in the result
        """
        if start is None:
            nodes = self.get_nodes()
            if not nodes:
                return []
            start = nodes[0]

        visited = set()
        result = []

        def recursive_dfs(node):
            if node not in visited:
                visited.add(node)
                # Only add node if it's not the starting node
                if node != start:
                    result.append(node)
                for neighbor in self.successors(node):
                    recursive_dfs(neighbor)

        recursive_dfs(start)
        return result

    def bfs(self, start=None):
        """
        Breadth-first search traversal that yields nodes
        Based on Listing 5-6 (General Graph Traversal) from Python Algorithms
        Uses deque for efficiency
        
        NOTE: The test expects the starting node to NOT be included in the result
        """
        if start is None:
            nodes = self.get_nodes()
            if not nodes:
                return
            start = nodes[0]

        # Initialize visited set and queue
        visited = set()
        queue = deque()

        # Start by adding all successors of the starting node (excluding start node itself)
        for neighbor in self.successors(start):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                yield neighbor

        # Continue with standard BFS
        while queue:
            node = queue.popleft()
            # Explore neighbors
            for neighbor in self.successors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    yield neighbor


class DAG(TraversableDigraph):
    """Directed Acyclic Graph that prevents cycle creation"""

    def add_edge(self, tail, head, **vararg):
        """
        Override add_edge to ensure no cycles are created
        Checks if there's already a path from head to tail before adding the edge
        """
        # Check if adding this edge would create a cycle
        if self._has_path(head, tail):
            raise ValueError(f"Adding edge from {tail} to {head} would create a cycle")

        # If no cycle would be created, call parent's add_edge
        super().add_edge(tail, head, **vararg)

    def _has_path(self, start, target):
        """
        Check if there's a path from start node to target node
        Uses BFS to search for the target
        """
        if start == target:
            return True

        visited = set()
        queue = deque([start])
        visited.add(start)

        while queue:
            current = queue.popleft()
            for neighbor in self.successors(current):
                if neighbor == target:
                    return True
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return False


# Test with the clothing dependencies example
def test_clothing_dependencies():
    """Test the complete implementation with clothing dependencies"""
    clothing = DAG()

    # Add all clothing items
    items = ["shirt", "tie", "pants", "jacket", "vest", "belt", "shoes", "socks"]
    for item in items:
        clothing.add_node(item)

    # Add dependencies based on the description
    # Shirt goes to tie, pants, jacket and vest
    clothing.add_edge("shirt", "tie")
    clothing.add_edge("shirt", "pants")
    clothing.add_edge("shirt", "jacket")
    clothing.add_edge("shirt", "vest")

    # Tie goes to jacket
    clothing.add_edge("tie", "jacket")

    # Pants goes to belt and shoes
    clothing.add_edge("pants", "belt")
    clothing.add_edge("pants", "shoes")

    # Socks goes to shoes
    clothing.add_edge("socks", "shoes")

    # Belt goes to jacket
    clothing.add_edge("belt", "jacket")

    # Vest goes to jacket
    clothing.add_edge("vest", "jacket")

    print("=== Clothing Dependencies Graph ===")
    clothing.print_graph()

    print("\n=== Valid Dressing Order (Topological Sort) ===")
    try:
        dressing_order = clothing.top_sort()
        for i, item in enumerate(dressing_order, 1):
            print(f"{i}. {item}")
    except ValueError as e:
        print(f"Error: {e}")

    print("\n=== DFS Traversal Starting from 'shirt' (Excluding Start) ===")
    dfs_order = clothing.dfs("shirt")
    for i, item in enumerate(dfs_order, 1):
        print(f"{i}. {item}")

    print("\n=== BFS Traversal Starting from 'shirt' (Excluding Start) ===")
    bfs_order = list(clothing.bfs("shirt"))
    for i, item in enumerate(bfs_order, 1):
        print(f"{i}. {item}")

    # Test cycle detection
    print("\n=== Testing Cycle Detection ===")
    try:
        clothing.add_edge("jacket", "shirt")  # This should create a cycle
        print("ERROR: Cycle was not detected!")
    except ValueError as e:
        print(f"✓ Correctly detected cycle: {e}")


# Test edge_weight functionality
def test_edge_weight():
    """Test that edge_weight parameter works correctly"""
    print("\n=== Testing Edge Weight Functionality ===")
    graph = DAG()
    graph.add_node("A", 10)
    graph.add_node("B", 20)
    graph.add_edge("A", "B", edge_weight=5)
    
    weight = graph.get_edge_weight("A", "B")
    print(f"Edge weight from A to B: {weight}")
    print(f"Test passed: {weight == 5}")


# Test DFS excluding start node
def test_dfs_excludes_start():
    """Test that DFS excludes the starting node"""
    print("\n=== Testing DFS Excludes Start Node ===")
    graph = TraversableDigraph()
    
    # Adding nodes
    graph.add_node("A")
    graph.add_node("B")
    graph.add_node("C")
    graph.add_node("D")
    graph.add_node("E")
    graph.add_node("F")
    
    # Adding edges
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("B", "D")
    graph.add_edge("C", "D")
    graph.add_edge("D", "E")
    graph.add_edge("E", "F")
    graph.add_edge("B", "F")
    
    # Perform DFS from node "A"
    dfs_result = graph.dfs("A")
    print(f"DFS result from A (should exclude A): {dfs_result}")
    print(f"A is not in result: {'A' not in dfs_result}")


if __name__ == "__main__":
    test_clothing_dependencies()
    test_edge_weight()
    test_dfs_excludes_start()
