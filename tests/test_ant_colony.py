"""Unit tests for Ant Colony Optimization Simulator."""

import pytest
import numpy as np
from code_files.ant_colony import (
    Graph,
    Ant,
    AntColonyOptimizer,
    dijkstra_shortest_path,
)


class TestGraph:
    """Tests for the Graph class."""

    def test_graph_creation_with_nodes(self):
        """Graph should be created with approximately specified number of nodes."""
        graph = Graph(n_nodes=30, seed=42)
        # Grid layout may round up to fit grid dimensions
        assert graph.n_nodes >= 30
        assert graph.n_nodes == graph.rows * graph.cols

    def test_graph_edges_have_valid_costs(self):
        """All edge costs should be between 1 and ~12 (diagonals can be 1.2x)."""
        graph = Graph(n_nodes=30, seed=42)
        for (u, v), cost in graph.edges.items():
            assert 1 <= cost <= 12  # Diagonals can be up to 10 * 1.2 = 12

    def test_graph_is_connected(self):
        """Graph should be connected (path exists between any two nodes)."""
        graph = Graph(n_nodes=30, seed=42)
        # BFS from node 0 should reach all nodes
        visited = set()
        queue = [0]
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            for neighbor in graph.get_neighbors(node):
                if neighbor not in visited:
                    queue.append(neighbor)
        assert len(visited) == graph.n_nodes

    def test_graph_neighbors(self):
        """get_neighbors should return connected nodes."""
        graph = Graph(n_nodes=10, seed=42)
        neighbors = graph.get_neighbors(0)
        assert isinstance(neighbors, list)
        assert all(isinstance(n, (int, np.integer)) for n in neighbors)
        assert all(0 <= n < 10 for n in neighbors)

    def test_graph_edge_cost(self):
        """get_edge_cost should return cost between connected nodes."""
        graph = Graph(n_nodes=10, seed=42)
        neighbors = graph.get_neighbors(0)
        if neighbors:
            cost = graph.get_edge_cost(0, neighbors[0])
            assert 1 <= cost <= 10

    def test_graph_reproducibility_with_seed(self):
        """Same seed should produce identical graphs."""
        graph1 = Graph(n_nodes=30, seed=12345)
        graph2 = Graph(n_nodes=30, seed=12345)

        assert graph1.edges == graph2.edges

    def test_graph_node_positions(self):
        """Graph should have 2D positions for visualization."""
        graph = Graph(n_nodes=30, seed=42)
        assert hasattr(graph, 'positions')
        assert len(graph.positions) == graph.n_nodes
        for pos in graph.positions.values():
            assert len(pos) == 2  # x, y coordinates


class TestPheromones:
    """Tests for pheromone initialization and updates."""

    def test_initial_pheromone_levels(self):
        """All edges should have initial pheromone levels."""
        aco = AntColonyOptimizer(n_nodes=30, seed=42)
        for edge in aco.graph.edges:
            assert edge in aco.pheromones
            assert aco.pheromones[edge] > 0

    def test_initial_pheromones_uniform(self):
        """Initial pheromone levels should be uniform."""
        aco = AntColonyOptimizer(n_nodes=30, seed=42)
        pheromone_values = list(aco.pheromones.values())
        assert all(p == pheromone_values[0] for p in pheromone_values)

    def test_pheromone_evaporation(self):
        """Evaporation should reduce all pheromone levels."""
        aco = AntColonyOptimizer(n_nodes=30, rho=0.1, seed=42)
        initial_pheromones = aco.pheromones.copy()

        aco._evaporate_pheromones()

        for edge, initial in initial_pheromones.items():
            assert aco.pheromones[edge] == pytest.approx(initial * 0.9)

    def test_pheromone_deposit(self):
        """Depositing pheromones should increase levels on path edges."""
        aco = AntColonyOptimizer(n_nodes=10, Q=1.0, seed=42)
        path = [0, 1, 2]
        path_cost = 5.0
        initial_pheromone = aco.pheromones[(0, 1)]

        aco._deposit_pheromones(path, path_cost)

        # Pheromone should increase by Q/path_cost
        expected = initial_pheromone + (1.0 / 5.0)
        assert aco.pheromones[(0, 1)] == pytest.approx(expected)

    def test_pheromones_never_negative(self):
        """Pheromone levels should never become negative."""
        aco = AntColonyOptimizer(n_nodes=30, rho=0.5, seed=42)

        # Many evaporations
        for _ in range(100):
            aco._evaporate_pheromones()

        for pheromone in aco.pheromones.values():
            assert pheromone >= 0


class TestAnt:
    """Tests for the Ant class."""

    def test_ant_creation(self):
        """Ant should be created at starting node."""
        graph = Graph(n_nodes=10, seed=42)
        pheromones = {edge: 1.0 for edge in graph.edges}
        ant = Ant(graph, pheromones, start=0, end=9, alpha=2, beta=2)

        assert ant.current_node == 0
        assert ant.path == [0]

    def test_ant_path_selection_probability(self):
        """Path selection should follow probability formula."""
        graph = Graph(n_nodes=10, seed=42)
        pheromones = {edge: 1.0 for edge in graph.edges}
        ant = Ant(graph, pheromones, start=0, end=9, alpha=2, beta=2, seed=42)

        # Get probabilities for next step
        probs = ant._calculate_probabilities()

        assert sum(probs.values()) == pytest.approx(1.0)
        assert all(p >= 0 for p in probs.values())

    def test_ant_reaches_destination(self):
        """Ant should reach destination node."""
        graph = Graph(n_nodes=10, seed=42)
        pheromones = {edge: 1.0 for edge in graph.edges}
        ant = Ant(graph, pheromones, start=0, end=9, alpha=2, beta=2, seed=42)

        ant.traverse()

        assert ant.path[-1] == 9
        assert ant.reached_destination

    def test_ant_path_cost_calculation(self):
        """Ant should calculate total path cost correctly."""
        graph = Graph(n_nodes=10, seed=42)
        pheromones = {edge: 1.0 for edge in graph.edges}
        ant = Ant(graph, pheromones, start=0, end=9, alpha=2, beta=2, seed=42)

        ant.traverse()

        # Manually calculate expected cost
        expected_cost = 0
        for i in range(len(ant.path) - 1):
            expected_cost += graph.get_edge_cost(ant.path[i], ant.path[i + 1])

        assert ant.path_cost == pytest.approx(expected_cost)

    def test_ant_no_revisit(self):
        """Ant should not revisit nodes (no cycles in path)."""
        graph = Graph(n_nodes=10, seed=42)
        pheromones = {edge: 1.0 for edge in graph.edges}
        ant = Ant(graph, pheromones, start=0, end=9, alpha=2, beta=2, seed=42)

        ant.traverse()

        # All nodes in path should be unique
        assert len(ant.path) == len(set(ant.path))

    def test_ant_prefers_high_pheromone(self):
        """Ant should prefer edges with higher pheromone."""
        graph = Graph(n_nodes=5, seed=42)
        pheromones = {edge: 0.1 for edge in graph.edges}

        # Set one edge to have very high pheromone
        neighbors = graph.get_neighbors(0)
        if len(neighbors) >= 2:
            high_pheromone_edge = (0, neighbors[0])
            if high_pheromone_edge not in pheromones:
                high_pheromone_edge = (neighbors[0], 0)
            pheromones[high_pheromone_edge] = 100.0

            # Run multiple ants and count which edge they take
            high_pheromone_count = 0
            for i in range(100):
                ant = Ant(graph, pheromones, start=0, end=4, alpha=2, beta=2, seed=i)
                ant._move()
                if ant.current_node == neighbors[0]:
                    high_pheromone_count += 1

            # Should strongly prefer high pheromone edge
            assert high_pheromone_count > 70


class TestAntColonyOptimizer:
    """Tests for the AntColonyOptimizer class."""

    def test_optimizer_creation(self):
        """Optimizer should initialize with correct parameters."""
        aco = AntColonyOptimizer(
            n_nodes=30,
            n_ants=500,
            alpha=2,
            beta=2,
            rho=0.1,
            Q=1,
            seed=42
        )

        assert aco.n_ants == 500
        assert aco.alpha == 2
        assert aco.beta == 2
        assert aco.rho == 0.1
        assert aco.Q == 1

    def test_optimizer_run_iteration(self):
        """Single iteration should deploy all ants."""
        aco = AntColonyOptimizer(n_nodes=30, n_ants=100, seed=42)

        results = aco.run_iteration(source=0, destination=29)

        # Not all ants may successfully reach destination (some may get stuck)
        assert len(results) > 0
        assert len(results) <= 100
        assert all('path' in r and 'cost' in r for r in results)

    def test_optimizer_tracks_best_path(self):
        """Optimizer should track the best path found."""
        aco = AntColonyOptimizer(n_nodes=30, n_ants=100, seed=42)

        aco.run(source=0, destination=29, iterations=10)

        assert aco.best_path is not None
        assert aco.best_path[0] == 0
        assert aco.best_path[-1] == 29
        assert aco.best_cost > 0

    def test_optimizer_convergence(self):
        """Best path cost should improve or stabilize over iterations."""
        aco = AntColonyOptimizer(n_nodes=30, n_ants=100, seed=42)

        aco.run(source=0, destination=29, iterations=50)

        # Cost history should exist
        assert len(aco.cost_history) == 50

        # Later iterations should have equal or better costs
        early_best = min(aco.cost_history[:10])
        late_best = min(aco.cost_history[-10:])
        assert late_best <= early_best

    def test_optimizer_500_ants(self):
        """Should handle 500 ants as specified in requirements."""
        aco = AntColonyOptimizer(n_nodes=30, n_ants=500, seed=42)

        aco.run(source=0, destination=29, iterations=10)

        assert aco.best_path is not None

    def test_optimizer_path_usage_distribution(self):
        """Should track how often each path is used."""
        aco = AntColonyOptimizer(n_nodes=30, n_ants=500, seed=42)

        aco.run(source=0, destination=29, iterations=20)

        distribution = aco.get_path_distribution()
        assert isinstance(distribution, dict)
        assert sum(distribution.values()) > 0

    def test_optimizer_reproducibility_with_seed(self):
        """Same seed should produce identical results."""
        aco1 = AntColonyOptimizer(n_nodes=30, n_ants=100, seed=12345)
        aco1.run(source=0, destination=29, iterations=10)

        aco2 = AntColonyOptimizer(n_nodes=30, n_ants=100, seed=12345)
        aco2.run(source=0, destination=29, iterations=10)

        assert aco1.best_path == aco2.best_path
        assert aco1.best_cost == aco2.best_cost

    def test_optimizer_different_source_destination(self):
        """Should work with various source/destination pairs."""
        aco = AntColonyOptimizer(n_nodes=30, seed=42)

        aco.run(source=5, destination=25, iterations=10)

        assert aco.best_path[0] == 5
        assert aco.best_path[-1] == 25


class TestDijkstraComparison:
    """Tests for comparing ACO with Dijkstra's algorithm."""

    def test_dijkstra_finds_shortest_path(self):
        """Dijkstra should find the optimal shortest path."""
        graph = Graph(n_nodes=10, seed=42)

        path, cost = dijkstra_shortest_path(graph, source=0, destination=9)

        assert path[0] == 0
        assert path[-1] == 9
        assert cost > 0

    def test_aco_approximates_dijkstra(self):
        """ACO should find a path close to Dijkstra's optimal."""
        graph = Graph(n_nodes=30, seed=42)

        # Get optimal path
        optimal_path, optimal_cost = dijkstra_shortest_path(graph, 0, 29)

        # Run ACO
        aco = AntColonyOptimizer(n_nodes=30, n_ants=500, seed=42)
        aco.graph = graph  # Use same graph
        aco._initialize_pheromones()
        aco.run(source=0, destination=29, iterations=100)

        # ACO should be within 20% of optimal (generous for stochastic algorithm)
        assert aco.best_cost <= optimal_cost * 1.2

    def test_aco_finds_optimal_on_simple_graph(self):
        """ACO should find optimal path on simple graph with enough iterations."""
        # Create a small deterministic graph
        graph = Graph(n_nodes=5, seed=42)

        optimal_path, optimal_cost = dijkstra_shortest_path(graph, 0, 4)

        aco = AntColonyOptimizer(n_nodes=5, n_ants=100, seed=42)
        aco.graph = graph
        aco._initialize_pheromones()
        aco.run(source=0, destination=4, iterations=50)

        # With small graph and many iterations, should find optimal
        assert aco.best_cost <= optimal_cost * 1.05


class TestVisualization:
    """Tests for visualization capabilities."""

    def test_get_pheromone_matrix(self):
        """Should return pheromone levels for visualization."""
        aco = AntColonyOptimizer(n_nodes=30, seed=42)
        aco.run(source=0, destination=29, iterations=10)

        pheromone_data = aco.get_pheromone_data()

        assert 'edges' in pheromone_data
        assert 'pheromones' in pheromone_data
        assert 'positions' in pheromone_data

    def test_get_convergence_data(self):
        """Should return data for plotting convergence."""
        aco = AntColonyOptimizer(n_nodes=30, n_ants=100, seed=42)
        aco.run(source=0, destination=29, iterations=20)

        assert len(aco.cost_history) == 20
        assert len(aco.mean_cost_history) == 20


class TestStatistics:
    """Tests for simulation statistics."""

    def test_get_statistics(self):
        """Should return comprehensive statistics."""
        aco = AntColonyOptimizer(n_nodes=30, n_ants=500, seed=42)
        aco.run(source=0, destination=29, iterations=50)

        stats = aco.get_statistics()

        assert 'best_cost' in stats
        assert 'best_path' in stats
        assert 'iterations' in stats
        assert 'total_ants' in stats
        assert 'convergence_iteration' in stats

    def test_iteration_statistics(self):
        """Should track per-iteration statistics."""
        aco = AntColonyOptimizer(n_nodes=30, n_ants=100, seed=42)
        aco.run(source=0, destination=29, iterations=20)

        assert len(aco.cost_history) == 20
        assert len(aco.mean_cost_history) == 20
