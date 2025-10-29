
from collections import deque

class VersatileDigraph:
    def __init__(self):
        self._edge_weights = {}
        self._edge_names = {}
        self._edge_head = {}
        self._node_values = {}

    def add_edge(self, tail, head, **vararg):
        if not isinstance(tail, str) or not isinstance(head, str):
            raise TypeError("Head and tail must be strings.")
        if tail not in self.get_nodes():
            self.add_node(tail, vararg.get("start_node_value", 0))
        if head not in self.get_nodes():
            self.add_node(head, vararg.get("end_node_value", 0))
        edge_name = vararg.get("name", tail + " to " + head)
        self._edge_names[tail][head] = edge_name
        self._edge_head[tail][head] = head
        if vararg.get("weight", 0) >= 0:
            self._edge_weights[tail][head] = vararg.get("weight", 0)
        else:
            raise ValueError("Edge weight must be positive.")

    def get_nodes(self):
        return list(self._node_values.keys())

    def add_node(self, node_id, node_value=0):
        if not isinstance(node_id, str) or not isinstance(node_value, (float, int)):
            raise TypeError("Node ID must be a string and node value must be numeric.")
        self._node_values[node_id] = node_value
        self._edge_weights[node_id] = {}
        self._edge_names[node_id] = {}
        self._edge_head[node_id] = {}

    def get_node_value(self, node):
        if node not in self.get_nodes():
            raise KeyError("Node " + node + " is not present in the graph.")
        return self._node_values[node]

    def print_graph(self):
        for tail in self.get_nodes():
            print("Node " + str(tail) + " has a value of " +
                  str(self.get_node_value(tail)) + ".")
            for head in self._edge_weights[tail]:
                print("There is an edge from node " + str(tail) + " to node " + str(head) +
                      " of weight " +
                      str(self.get_edge_weight(tail, head)) + " and name " +
                      self._edge_names[tail][head] + ".")

    def predecessors(self, node):
        if node not in self.get_nodes():
            raise KeyError("Node " + node + " is not present in the graph.")
        return [n for n in self.get_nodes() if node in self._edge_names[n]]

    def successors(self, node):
        if node not in self.get_nodes():
            raise KeyError("Node " + node + " is not present in the graph.")
        return list(self._edge_names[node].keys())

    def in_degree(self, node):
        if node not in self.get_nodes():
            raise KeyError("Node " + node + " is not present in the graph.")
        return len(self.predecessors(node))

    def out_degree(self, node):
        if node not in self.get_nodes():
            raise KeyError("Node " + node + " is not present in the graph.")
        return len(self.successors(node))

    def get_edge_weight(self, tail, head):
        if tail not in self.get_nodes():
            raise KeyError("Node " + tail + " is not present in the graph.")
        if head not in self.get_nodes():
            raise KeyError("Node " + head + " is not present in the graph.")
        if head not in self._edge_weights[tail]:
            raise KeyError("The specified edge does not exist in the graph")
        return self._edge_weights[tail][head]

    def successor_on_edge(self, tail, edge_name):
        if tail not in self.get_nodes():
            raise KeyError("Node " + tail + " is not present in the graph.")
        for head, name in self._edge_names[tail].items():
            if name == edge_name:
                return head
        raise KeyError(f"There is no edge '{edge_name}' associated with node {tail}")


class SortableDigraph(VersatileDigraph):
    def top_sort(self):
        in_degree = {}
        for node in self.get_nodes():
            in_degree[node] = self.in_degree(node)
        queue = [node for node in self.get_nodes() if in_degree[node] == 0]
        result = []
        while queue:
            node = queue.pop(0)
            result.append(node)
            for neighbor in self.successors(node):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        if len(result) != len(self.get_nodes()):
            raise ValueError("Graph has at least one cycle, topological sort not possible")
        return result


class TraversableDigraph(SortableDigraph):
    def dfs(self, start=None):
        """
        Depth-first search traversal based on Listing 5-5 from Python Algorithms
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
        """
        if start is None:
            nodes = self.get_nodes()
            if not nodes:
                return
            start = nodes[0]
        
        # Initialize visited set and queue
        visited = set([start])
        queue = deque([start])
        
        while queue:
            node = queue.popleft()
            yield node
            # Explore neighbors
            for neighbor in self.successors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)


class DAG(TraversableDigraph):
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


# Test the implementation
if __name__ == "__main__":
    print("=== Testing TraversableDigraph ===")
    
    # Create a test graph
    graph = TraversableDigraph()
    nodes = ['A', 'B', 'C', 'D', 'E', 'F']
    
    for node in nodes:
        graph.add_node(node)
    
    # Add edges to create a tree-like structure
    graph.add_edge('A', 'B')
    graph.add_edge('A', 'C')
    graph.add_edge('B', 'D')
    graph.add_edge('B', 'E')
    graph.add_edge('C', 'F')
    
    print("Nodes:", graph.get_nodes())
    print("DFS traversal from A:", graph.dfs('A'))
    print("BFS traversal from A:", list(graph.bfs('A')))
    
    print("\nBFS with yield demonstration:")
    for i, node in enumerate(graph.bfs('A')):
        print(f"Step {i+1}: Visiting node {node}")
    
    print("\n=== Testing DAG ===")
    
    # Test valid DAG (no cycles)
    dag = DAG()
    for node in ['X', 'Y', 'Z', 'W']:
        dag.add_node(node)
    
    dag.add_edge('X', 'Y')
    dag.add_edge('X', 'Z')
    dag.add_edge('Y', 'W')
    dag.add_edge('Z', 'W')
    
    print("Valid DAG topological sort:", dag.top_sort())
    
    # Test invalid DAG (attempt to create cycle)
    cyclic_dag = DAG()
    for node in ['P', 'Q', 'R']:
        cyclic_dag.add_node(node)
    
    cyclic_dag.add_edge('P', 'Q')
    cyclic_dag.add_edge('Q', 'R')
    
    try:
        cyclic_dag.add_edge('R', 'P')  # This should raise an exception
        print("ERROR: Cycle was not detected!")
    except ValueError as e:
        print("Cycle correctly detected:", e)
    
    # Test self-loop
    try:
        cyclic_dag.add_edge('S', 'S')  # Self-loop should be detected
        print("ERROR: Self-loop was not detected!")
    except ValueError as e:
        print("Self-loop correctly detected:", e)
