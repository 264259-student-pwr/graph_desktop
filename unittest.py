import unittest
import networkx as nx
from app.algorithms.dijkstra import dijkstra

class TestDijkstraAlgorithm(unittest.TestCase):
    def setUp(self):
        # Tworzenie przykładowego grafu
        self.graph = nx.Graph()
        self.graph.add_edge('A', 'B', weight=1)
        self.graph.add_edge('B', 'C', weight=2)
        self.graph.add_edge('A', 'C', weight=4)
        self.graph.add_edge('C', 'D', weight=1)

    def test_simple_graph(self):
        """Test najkrótszej ścieżki w prostym grafie."""
        path, cost, steps = dijkstra(self.graph, 'A', 'D')
        self.assertEqual(path, ['A', 'B', 'C', 'D'])
        self.assertEqual(cost, 4)

    def test_isolated_node(self):
        """Test dla grafu z izolowanym węzłem."""
        self.graph.add_node('E')  # Izolowany węzeł
        path, cost, steps = dijkstra(self.graph, 'A', 'E')
        self.assertEqual(path, [])
        self.assertEqual(cost, float('inf'))

    def test_directed_graph(self):
        """Test dla grafu skierowanego."""
        directed_graph = nx.DiGraph()
        directed_graph.add_edge('A', 'B', weight=1)
        directed_graph.add_edge('B', 'C', weight=2)
        directed_graph.add_edge('C', 'A', weight=3)  # Skierowana krawędź
        path, cost, steps = dijkstra(directed_graph, 'A', 'C')
        self.assertEqual(path, ['A', 'B', 'C'])
        self.assertEqual(cost, 3)

    def test_graph_with_cycle(self):
        """Test dla grafu z cyklem."""
        self.graph.add_edge('D', 'A', weight=10)  # Tworzenie cyklu
        path, cost, steps = dijkstra(self.graph, 'A', 'D')
        self.assertEqual(path, ['A', 'B', 'C', 'D'])
        self.assertEqual(cost, 4)

    def test_graph_with_equal_weights(self):
        """Test dla grafu z równymi wagami."""
        self.graph = nx.Graph()
        self.graph.add_edge('A', 'B', weight=1)
        self.graph.add_edge('B', 'C', weight=1)
        self.graph.add_edge('A', 'C', weight=1)
        path, cost, steps = dijkstra(self.graph, 'A', 'C')
        self.assertEqual(path, ['A', 'B', 'C'])  # Kolejność węzłów może zależeć od implementacji
        self.assertEqual(cost, 2)

    def test_large_weights(self):
        """Test dla grafu z dużymi wagami."""
        self.graph = nx.Graph()
        self.graph.add_edge('A', 'B', weight=10**9)
        self.graph.add_edge('B', 'C', weight=10**9)
        path, cost, steps = dijkstra(self.graph, 'A', 'C')
        self.assertEqual(path, ['A', 'B', 'C'])
        self.assertEqual(cost, 2 * 10**9)

    def test_no_path(self):
        """Test dla węzłów bez ścieżki."""
        self.graph.add_node('E')  # Izolowany węzeł
        path, cost, steps = dijkstra(self.graph, 'A', 'E')
        self.assertEqual(path, [])
        self.assertEqual(cost, float('inf'))

    def test_single_node(self):
        """Test dla grafu z jednym węzłem."""
        self.graph = nx.Graph()
        self.graph.add_node('A')
        path, cost, steps = dijkstra(self.graph, 'A', 'A')
        self.assertEqual(path, ['A'])
        self.assertEqual(cost, 0)

if __name__ == '__main__':
    unittest.main()
