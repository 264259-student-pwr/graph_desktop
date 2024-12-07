import heapq
import networkx as nx

def dijkstra(graph, start, end):
    """
    Implementacja algorytmu Dijkstry.

    :param graph: Obiekt grafu (NetworkX)
    :param start: Węzeł początkowy
    :param end: Węzeł końcowy
    :return: Najkrótsza ścieżka jako lista węzłów, całkowity koszt, kroki algorytmu
    """
    distances = {node: float('inf') for node in graph.nodes}
    distances[start] = 0
    previous_nodes = {node: None for node in graph.nodes}
    priority_queue = [(0, start)]
    steps = []

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node == end:
            break

        if current_distance > distances[current_node]:
            continue

        for neighbor in graph.neighbors(current_node):
            weight = graph[current_node][neighbor]['weight']
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))
                steps.append((current_node, neighbor, weight))

    path = []
    current_node = end
    while current_node is not None:
        path.append(current_node)
        current_node = previous_nodes[current_node]
    path.reverse()

    return path, distances[end], steps
