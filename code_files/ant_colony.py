"""
Ant Colony Optimization (ACO) Simulator

Implements the Ant System algorithm for finding optimal paths in a graph.
Demonstrates emergent swarm intelligence where simple agents (ants) collectively
discover near-optimal solutions through pheromone-based communication.

Algorithm:
    1. Initialize pheromone levels uniformly on all edges
    2. Each ant builds a path from source to destination:
       - At each node, select next edge probabilistically
       - Probability = (pheromone^alpha) * (1/cost)^beta / sum
    3. After all ants complete, deposit pheromones on used edges
       - Pheromone deposit = Q / path_cost
    4. Evaporate pheromones globally: pheromone *= (1 - rho)
    5. Repeat until convergence

References:
    - Dorigo, M. (1992). Optimization, Learning and Natural Algorithms. PhD thesis.
    - https://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import heapq
from typing import Dict, List, Tuple, Optional
import argparse


class Graph:
    """
    Random graph representing a road network.

    Generates a connected graph with random edge costs between 1 and 10.
    Uses a combination of nearest-neighbor connections and random edges
    to create a realistic road-network-like structure.
    """

    def __init__(self, n_nodes: int = 30, min_cost: float = 1.0,
                 max_cost: float = 10.0, seed: Optional[int] = None):
        """
        Initialize a random connected graph.

        Args:
            n_nodes: Number of nodes in the graph
            min_cost: Minimum edge cost
            max_cost: Maximum edge cost
            seed: Random seed for reproducibility
        """
        self.n_nodes = n_nodes
        self.min_cost = min_cost
        self.max_cost = max_cost
        self.rng = np.random.default_rng(seed)

        # Generate node positions for visualization
        self.positions = self._generate_positions()

        # Generate edges
        self.edges: Dict[Tuple[int, int], float] = {}
        self._generate_edges()

        # Build adjacency list for efficient neighbor lookup
        self.adjacency: Dict[int, List[int]] = defaultdict(list)
        self._build_adjacency()

    def _generate_positions(self) -> Dict[int, Tuple[float, float]]:
        """Generate 2D positions for nodes."""
        positions = {}
        for i in range(self.n_nodes):
            # Arrange in a roughly circular/grid pattern with some randomness
            angle = 2 * np.pi * i / self.n_nodes
            radius = 0.3 + 0.4 * self.rng.random()
            x = 0.5 + radius * np.cos(angle) + 0.1 * self.rng.random()
            y = 0.5 + radius * np.sin(angle) + 0.1 * self.rng.random()
            positions[i] = (x, y)
        return positions

    def _generate_edges(self):
        """Generate a connected graph with random edge costs."""
        # First, create a minimum spanning tree to ensure connectivity
        # Using nearest-neighbor heuristic
        connected = {0}
        unconnected = set(range(1, self.n_nodes))

        while unconnected:
            best_dist = float('inf')
            best_pair = None

            for c in connected:
                for u in unconnected:
                    dist = self._distance(c, u)
                    if dist < best_dist:
                        best_dist = dist
                        best_pair = (c, u)

            if best_pair:
                c, u = best_pair
                cost = self.min_cost + self.rng.random() * (self.max_cost - self.min_cost)
                self._add_edge(c, u, cost)
                connected.add(u)
                unconnected.remove(u)

        # Add additional random edges for multiple paths
        target_edges = self.n_nodes * 2  # Average degree of 4

        while len(self.edges) < target_edges:
            u = self.rng.integers(0, self.n_nodes)
            v = self.rng.integers(0, self.n_nodes)

            if u != v and (u, v) not in self.edges and (v, u) not in self.edges:
                # Prefer nearby nodes
                dist = self._distance(u, v)
                if dist < 0.5 or self.rng.random() < 0.3:
                    cost = self.min_cost + self.rng.random() * (self.max_cost - self.min_cost)
                    self._add_edge(u, v, cost)

    def _distance(self, u: int, v: int) -> float:
        """Euclidean distance between two nodes."""
        x1, y1 = self.positions[u]
        x2, y2 = self.positions[v]
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def _add_edge(self, u: int, v: int, cost: float):
        """Add undirected edge between u and v."""
        # Store with smaller index first for consistency
        edge = (min(u, v), max(u, v))
        self.edges[edge] = round(cost, 2)

    def _build_adjacency(self):
        """Build adjacency list from edges."""
        for (u, v), _ in self.edges.items():
            self.adjacency[u].append(v)
            self.adjacency[v].append(u)

    def get_neighbors(self, node: int) -> List[int]:
        """Get list of nodes adjacent to given node."""
        return self.adjacency[node]

    def get_edge_cost(self, u: int, v: int) -> float:
        """Get cost of edge between u and v."""
        edge = (min(u, v), max(u, v))
        return self.edges.get(edge, float('inf'))

    def get_edge_key(self, u: int, v: int) -> Tuple[int, int]:
        """Get canonical edge key (smaller index first)."""
        return (min(u, v), max(u, v))


class Ant:
    """
    An ant that traverses the graph probabilistically.

    The ant selects edges based on pheromone levels and edge costs,
    preferring edges with higher pheromone and lower cost.
    """

    def __init__(self, graph: Graph, pheromones: Dict[Tuple[int, int], float],
                 start: int, end: int, alpha: float = 2.0, beta: float = 2.0,
                 seed: Optional[int] = None):
        """
        Initialize an ant at the starting node.

        Args:
            graph: The graph to traverse
            pheromones: Current pheromone levels on edges
            start: Source node
            end: Destination node
            alpha: Pheromone influence exponent
            beta: Distance heuristic influence exponent
            seed: Random seed for reproducibility
        """
        self.graph = graph
        self.pheromones = pheromones
        self.start = start
        self.end = end
        self.alpha = alpha
        self.beta = beta
        self.rng = np.random.default_rng(seed)

        self.current_node = start
        self.path = [start]
        self.visited = {start}
        self.path_cost = 0.0
        self.reached_destination = False

    def _calculate_probabilities(self) -> Dict[int, float]:
        """
        Calculate selection probabilities for each neighboring node.

        Probability of selecting neighbor j:
            P(j) = (pheromone_ij^alpha * (1/cost_ij)^beta) / sum
        """
        neighbors = self.graph.get_neighbors(self.current_node)
        unvisited = [n for n in neighbors if n not in self.visited]

        if not unvisited:
            return {}

        attractiveness = {}
        total = 0.0

        for neighbor in unvisited:
            edge = self.graph.get_edge_key(self.current_node, neighbor)
            pheromone = self.pheromones.get(edge, 1.0)
            cost = self.graph.get_edge_cost(self.current_node, neighbor)

            # Attractiveness = pheromone^alpha * (1/cost)^beta
            attr = (pheromone ** self.alpha) * ((1.0 / cost) ** self.beta)
            attractiveness[neighbor] = attr
            total += attr

        # Normalize to probabilities
        probabilities = {}
        for neighbor, attr in attractiveness.items():
            probabilities[neighbor] = attr / total if total > 0 else 1.0 / len(unvisited)

        return probabilities

    def _move(self):
        """Move to next node based on probabilities."""
        probs = self._calculate_probabilities()

        if not probs:
            return False  # Stuck, no unvisited neighbors

        # Roulette wheel selection
        neighbors = list(probs.keys())
        probabilities = list(probs.values())

        next_node = self.rng.choice(neighbors, p=probabilities)

        # Update path and cost
        edge_cost = self.graph.get_edge_cost(self.current_node, next_node)
        self.path_cost += edge_cost
        self.path.append(next_node)
        self.visited.add(next_node)
        self.current_node = next_node

        return True

    def traverse(self) -> bool:
        """
        Traverse from start to end, returning True if successful.
        """
        while self.current_node != self.end:
            if not self._move():
                return False  # Got stuck

        self.reached_destination = True
        return True


class AntColonyOptimizer:
    """
    Ant Colony Optimization algorithm for finding shortest paths.

    Uses a colony of ants to explore paths through a graph,
    with pheromone trails guiding subsequent ants toward better solutions.
    """

    def __init__(self, n_nodes: int = 30, n_ants: int = 500,
                 alpha: float = 2.0, beta: float = 2.0,
                 rho: float = 0.1, Q: float = 1.0,
                 initial_pheromone: float = 1.0,
                 seed: Optional[int] = None):
        """
        Initialize the ACO optimizer.

        Args:
            n_nodes: Number of nodes in the graph
            n_ants: Number of ants per iteration
            alpha: Pheromone influence exponent
            beta: Distance heuristic influence exponent
            rho: Evaporation rate (0 to 1)
            Q: Pheromone deposit constant
            initial_pheromone: Initial pheromone level on all edges
            seed: Random seed for reproducibility
        """
        self.n_nodes = n_nodes
        self.n_ants = n_ants
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.Q = Q
        self.initial_pheromone = initial_pheromone
        self.seed = seed
        self.rng = np.random.default_rng(seed)

        # Initialize graph and pheromones
        self.graph = Graph(n_nodes=n_nodes, seed=seed)
        self.pheromones: Dict[Tuple[int, int], float] = {}
        self._initialize_pheromones()

        # Tracking
        self.best_path: Optional[List[int]] = None
        self.best_cost: float = float('inf')
        self.cost_history: List[float] = []
        self.mean_cost_history: List[float] = []
        self.path_counts: Dict[Tuple[int, ...], int] = defaultdict(int)

    def _initialize_pheromones(self):
        """Set initial pheromone levels on all edges."""
        for edge in self.graph.edges:
            self.pheromones[edge] = self.initial_pheromone

    def _evaporate_pheromones(self):
        """Apply pheromone evaporation to all edges."""
        for edge in self.pheromones:
            self.pheromones[edge] *= (1 - self.rho)
            # Ensure pheromone doesn't go below minimum
            self.pheromones[edge] = max(self.pheromones[edge], 0.001)

    def _deposit_pheromones(self, path: List[int], path_cost: float):
        """Deposit pheromones on edges in the path."""
        deposit = self.Q / path_cost

        for i in range(len(path) - 1):
            edge = self.graph.get_edge_key(path[i], path[i + 1])
            self.pheromones[edge] += deposit

    def run_iteration(self, source: int, destination: int) -> List[Dict]:
        """
        Run one iteration with all ants.

        Args:
            source: Starting node
            destination: Target node

        Returns:
            List of results for each ant (path and cost)
        """
        results = []

        for i in range(self.n_ants):
            ant_seed = None if self.seed is None else self.seed + i
            ant = Ant(
                graph=self.graph,
                pheromones=self.pheromones,
                start=source,
                end=destination,
                alpha=self.alpha,
                beta=self.beta,
                seed=ant_seed
            )

            if ant.traverse():
                results.append({
                    'path': ant.path,
                    'cost': ant.path_cost
                })

                # Track path usage
                path_key = tuple(ant.path)
                self.path_counts[path_key] += 1

        return results

    def run(self, source: int = 0, destination: int = 29,
            iterations: int = 50) -> Dict:
        """
        Run the ACO algorithm.

        Args:
            source: Starting node
            destination: Target node
            iterations: Number of iterations to run

        Returns:
            Dictionary with best path, cost, and statistics
        """
        self.cost_history = []
        self.mean_cost_history = []
        self.path_counts.clear()

        for iteration in range(iterations):
            # Run all ants
            results = self.run_iteration(source, destination)

            if results:
                # Find best in this iteration
                costs = [r['cost'] for r in results]
                best_idx = np.argmin(costs)
                iteration_best_cost = costs[best_idx]
                iteration_best_path = results[best_idx]['path']

                # Update global best
                if iteration_best_cost < self.best_cost:
                    self.best_cost = iteration_best_cost
                    self.best_path = iteration_best_path

                # Track history
                self.cost_history.append(self.best_cost)
                self.mean_cost_history.append(np.mean(costs))

                # Deposit pheromones for all successful ants
                for result in results:
                    self._deposit_pheromones(result['path'], result['cost'])

            # Evaporate pheromones
            self._evaporate_pheromones()

        return {
            'best_path': self.best_path,
            'best_cost': self.best_cost,
            'iterations': iterations,
            'total_ants': iterations * self.n_ants
        }

    def get_path_distribution(self) -> Dict[Tuple[int, ...], int]:
        """Get distribution of paths used by ants."""
        return dict(self.path_counts)

    def get_pheromone_data(self) -> Dict:
        """Get pheromone data for visualization."""
        return {
            'edges': list(self.graph.edges.keys()),
            'pheromones': dict(self.pheromones),
            'positions': self.graph.positions
        }

    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about the optimization."""
        # Find when best was found
        convergence_iter = 0
        for i, cost in enumerate(self.cost_history):
            if cost == self.best_cost:
                convergence_iter = i
                break

        return {
            'best_cost': self.best_cost,
            'best_path': self.best_path,
            'best_path_length': len(self.best_path) if self.best_path else 0,
            'iterations': len(self.cost_history),
            'total_ants': len(self.cost_history) * self.n_ants,
            'convergence_iteration': convergence_iter,
            'unique_paths': len(self.path_counts),
            'most_used_path_count': max(self.path_counts.values()) if self.path_counts else 0
        }


def dijkstra_shortest_path(graph: Graph, source: int,
                           destination: int) -> Tuple[List[int], float]:
    """
    Find the shortest path using Dijkstra's algorithm.

    Args:
        graph: The graph to search
        source: Starting node
        destination: Target node

    Returns:
        Tuple of (path, cost)
    """
    # Distance to each node
    distances = {i: float('inf') for i in range(graph.n_nodes)}
    distances[source] = 0

    # Previous node in optimal path
    previous = {i: None for i in range(graph.n_nodes)}

    # Priority queue: (distance, node)
    pq = [(0, source)]
    visited = set()

    while pq:
        dist, node = heapq.heappop(pq)

        if node in visited:
            continue
        visited.add(node)

        if node == destination:
            break

        for neighbor in graph.get_neighbors(node):
            if neighbor in visited:
                continue

            edge_cost = graph.get_edge_cost(node, neighbor)
            new_dist = dist + edge_cost

            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous[neighbor] = node
                heapq.heappush(pq, (new_dist, neighbor))

    # Reconstruct path
    path = []
    node = destination
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()

    return path, distances[destination]


def plot_graph(graph: Graph, path: Optional[List[int]] = None,
               pheromones: Optional[Dict] = None, ax=None):
    """Plot the graph with optional path and pheromone visualization."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))

    # Draw edges
    max_pheromone = max(pheromones.values()) if pheromones else 1.0

    for (u, v), cost in graph.edges.items():
        x1, y1 = graph.positions[u]
        x2, y2 = graph.positions[v]

        # Edge width based on pheromone
        if pheromones:
            edge_key = graph.get_edge_key(u, v)
            pheromone = pheromones.get(edge_key, 0)
            width = 0.5 + 3 * (pheromone / max_pheromone)
            alpha = 0.3 + 0.7 * (pheromone / max_pheromone)
        else:
            width = 1
            alpha = 0.5

        ax.plot([x1, x2], [y1, y2], 'gray', linewidth=width, alpha=alpha)

    # Highlight path
    if path:
        for i in range(len(path) - 1):
            x1, y1 = graph.positions[path[i]]
            x2, y2 = graph.positions[path[i + 1]]
            ax.plot([x1, x2], [y1, y2], 'r-', linewidth=3, zorder=5)

    # Draw nodes
    for node, (x, y) in graph.positions.items():
        color = 'green' if (path and node == path[0]) else \
                'red' if (path and node == path[-1]) else 'blue'
        size = 200 if (path and (node == path[0] or node == path[-1])) else 100
        ax.scatter(x, y, c=color, s=size, zorder=10)
        ax.annotate(str(node), (x, y), ha='center', va='center',
                   fontsize=8, color='white', weight='bold')

    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    ax.set_aspect('equal')
    ax.axis('off')

    return ax


def plot_convergence(cost_history: List[float], mean_cost_history: List[float],
                     optimal_cost: Optional[float] = None, ax=None):
    """Plot convergence of best cost over iterations."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    iterations = range(1, len(cost_history) + 1)

    ax.plot(iterations, cost_history, 'b-', linewidth=2, label='Best Cost')
    ax.plot(iterations, mean_cost_history, 'g--', alpha=0.7, label='Mean Cost')

    if optimal_cost:
        ax.axhline(y=optimal_cost, color='r', linestyle=':',
                  linewidth=2, label=f'Optimal (Dijkstra): {optimal_cost:.2f}')

    ax.set_xlabel('Iteration')
    ax.set_ylabel('Path Cost')
    ax.set_title('ACO Convergence')
    ax.legend()
    ax.grid(True, alpha=0.3)

    return ax


def run_quick_demo(seed: int = 42):
    """Run a quick demonstration of ACO."""
    print("=" * 60)
    print("ANT COLONY OPTIMIZATION - Quick Demo")
    print("=" * 60)

    # Initialize
    aco = AntColonyOptimizer(
        n_nodes=30,
        n_ants=100,
        alpha=2.0,
        beta=2.0,
        rho=0.1,
        Q=1.0,
        seed=seed
    )

    source, destination = 0, 29

    # Get optimal path for comparison
    optimal_path, optimal_cost = dijkstra_shortest_path(aco.graph, source, destination)
    print(f"\nDijkstra's Optimal Path: {optimal_path}")
    print(f"Dijkstra's Optimal Cost: {optimal_cost:.2f}")

    # Run ACO
    print(f"\nRunning ACO with {aco.n_ants} ants for 50 iterations...")
    result = aco.run(source=source, destination=destination, iterations=50)

    print(f"\nACO Best Path: {result['best_path']}")
    print(f"ACO Best Cost: {result['best_cost']:.2f}")
    print(f"Optimality Gap: {((result['best_cost'] - optimal_cost) / optimal_cost * 100):.1f}%")

    stats = aco.get_statistics()
    print(f"\nStatistics:")
    print(f"  Convergence at iteration: {stats['convergence_iteration']}")
    print(f"  Unique paths explored: {stats['unique_paths']}")
    print(f"  Most used path count: {stats['most_used_path_count']}")

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Graph with best path
    plot_graph(aco.graph, path=result['best_path'],
              pheromones=aco.pheromones, ax=axes[0])
    axes[0].set_title(f'Best Path Found (Cost: {result["best_cost"]:.2f})')

    # Convergence plot
    plot_convergence(aco.cost_history, aco.mean_cost_history,
                    optimal_cost=optimal_cost, ax=axes[1])

    plt.tight_layout()
    plt.show()


def run_interactive_simulation(seed: int = 42):
    """Run an animated simulation showing ants finding the path."""
    import matplotlib.animation as animation

    print("=" * 60)
    print("ANT COLONY OPTIMIZATION - Interactive Animation")
    print("=" * 60)

    aco = AntColonyOptimizer(
        n_nodes=30,
        n_ants=50,
        alpha=2.0,
        beta=2.0,
        rho=0.1,
        Q=1.0,
        seed=seed
    )

    source, destination = 0, 29
    optimal_path, optimal_cost = dijkstra_shortest_path(aco.graph, source, destination)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    iteration = [0]
    max_iterations = 100

    def update(frame):
        if iteration[0] >= max_iterations:
            return

        # Run one iteration
        results = aco.run_iteration(source, destination)

        if results:
            costs = [r['cost'] for r in results]
            best_idx = np.argmin(costs)

            if costs[best_idx] < aco.best_cost:
                aco.best_cost = costs[best_idx]
                aco.best_path = results[best_idx]['path']

            aco.cost_history.append(aco.best_cost)
            aco.mean_cost_history.append(np.mean(costs))

            for result in results:
                aco._deposit_pheromones(result['path'], result['cost'])

        aco._evaporate_pheromones()
        iteration[0] += 1

        # Update plots
        axes[0].clear()
        axes[1].clear()

        plot_graph(aco.graph, path=aco.best_path,
                  pheromones=aco.pheromones, ax=axes[0])
        axes[0].set_title(f'Iteration {iteration[0]} - Best Cost: {aco.best_cost:.2f}')

        if aco.cost_history:
            plot_convergence(aco.cost_history, aco.mean_cost_history,
                           optimal_cost=optimal_cost, ax=axes[1])

        fig.suptitle('Ant Colony Optimization', fontsize=14)

    ani = animation.FuncAnimation(fig, update, frames=max_iterations,
                                  interval=200, repeat=False)
    plt.tight_layout()
    plt.show()


def run_comparison(seed: int = 42):
    """Compare ACO performance with different parameters."""
    print("=" * 60)
    print("ANT COLONY OPTIMIZATION - Parameter Comparison")
    print("=" * 60)

    # Base graph
    graph = Graph(n_nodes=30, seed=seed)
    optimal_path, optimal_cost = dijkstra_shortest_path(graph, 0, 29)
    print(f"\nOptimal cost (Dijkstra): {optimal_cost:.2f}")

    # Different configurations
    configs = [
        {'n_ants': 100, 'alpha': 1, 'beta': 2, 'name': 'Low Pheromone Influence'},
        {'n_ants': 100, 'alpha': 2, 'beta': 2, 'name': 'Balanced'},
        {'n_ants': 100, 'alpha': 3, 'beta': 1, 'name': 'High Pheromone Influence'},
        {'n_ants': 500, 'alpha': 2, 'beta': 2, 'name': 'Large Colony'},
    ]

    results = []

    for config in configs:
        aco = AntColonyOptimizer(
            n_nodes=30,
            n_ants=config['n_ants'],
            alpha=config['alpha'],
            beta=config['beta'],
            rho=0.1,
            Q=1.0,
            seed=seed
        )
        aco.graph = graph  # Use same graph
        aco._initialize_pheromones()

        result = aco.run(source=0, destination=29, iterations=50)

        gap = (result['best_cost'] - optimal_cost) / optimal_cost * 100
        results.append({
            'name': config['name'],
            'cost': result['best_cost'],
            'gap': gap,
            'history': aco.cost_history
        })

        print(f"\n{config['name']}:")
        print(f"  Best cost: {result['best_cost']:.2f}")
        print(f"  Optimality gap: {gap:.1f}%")

    # Plot comparison
    fig, ax = plt.subplots(figsize=(12, 6))

    for result in results:
        ax.plot(result['history'], label=f"{result['name']} ({result['gap']:.1f}%)")

    ax.axhline(y=optimal_cost, color='black', linestyle=':',
              linewidth=2, label='Optimal')

    ax.set_xlabel('Iteration')
    ax.set_ylabel('Best Path Cost')
    ax.set_title('ACO Parameter Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ant Colony Optimization Simulator')
    parser.add_argument('--animate', action='store_true',
                       help='Run animated visualization')
    parser.add_argument('--compare', action='store_true',
                       help='Compare different parameter settings')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility')
    parser.add_argument('--nodes', type=int, default=30,
                       help='Number of nodes in graph')
    parser.add_argument('--ants', type=int, default=500,
                       help='Number of ants per iteration')
    parser.add_argument('--iterations', type=int, default=50,
                       help='Number of iterations')

    args = parser.parse_args()

    if args.animate:
        run_interactive_simulation(seed=args.seed)
    elif args.compare:
        run_comparison(seed=args.seed)
    else:
        run_quick_demo(seed=args.seed)
