"""
Forest Fire Simulation
Based on the Drossel-Schwabl model demonstrating self-organized criticality.

Trees grow with probability p, and lightning strikes with probability f.
When a tree is struck by lightning, fire spreads to all connected trees.
The system naturally tunes itself to a critical state.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap
from collections import deque, defaultdict

# Cell states
EMPTY = 0
TREE = 1
BURNING = 2

class ForestFireSimulation:
    def __init__(self, size=256, tree_growth_prob=0.01, lightning_prob=None, seed=None):
        """
        Initialize the Forest Fire simulation.

        Args:
            size: Grid size (size x size)
            tree_growth_prob: Probability p that an empty cell grows a tree
            lightning_prob: Probability f of lightning strike (default: p/10)
            seed: Random seed for reproducibility
        """
        self.size = size
        self.p = tree_growth_prob
        self.f = lightning_prob if lightning_prob is not None else tree_growth_prob / 10
        self.rng = np.random.default_rng(seed)

        self.grid = np.zeros((size, size), dtype=np.int32)
        self.timestep = 0
        self.fire_sizes = []
        self.tree_counts = []

    def count_trees(self):
        """Count the number of trees."""
        return np.sum(self.grid == TREE)

    def tree_density(self):
        """Calculate tree density."""
        return self.count_trees() / (self.size * self.size)

    def _get_moore_neighbors(self, i, j):
        """Get valid Moore neighborhood positions (8 neighbors)."""
        neighbors = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < self.size and 0 <= nj < self.size:
                    neighbors.append((ni, nj))
        return neighbors

    def spread_fire(self, start_i, start_j):
        """Spread fire from a starting point using BFS. Returns trees burned."""
        if self.grid[start_i, start_j] != TREE:
            return 0

        burned = 0
        queue = deque([(start_i, start_j)])
        self.grid[start_i, start_j] = BURNING

        while queue:
            i, j = queue.popleft()
            burned += 1

            for ni, nj in self._get_moore_neighbors(i, j):
                if self.grid[ni, nj] == TREE:
                    self.grid[ni, nj] = BURNING
                    queue.append((ni, nj))

        return burned

    def _clear_burning_cells(self):
        """Convert burning cells to empty."""
        self.grid[self.grid == BURNING] = EMPTY

    def _grow_trees(self):
        """Grow new trees on empty cells."""
        empty_mask = self.grid == EMPTY
        grow_mask = self.rng.random((self.size, self.size)) < self.p
        self.grid[empty_mask & grow_mask] = TREE

    def _try_lightning_strike(self):
        """Attempt a lightning strike on a random tree."""
        tree_positions = np.argwhere(self.grid == TREE)
        if len(tree_positions) == 0:
            return

        for i, j in tree_positions:
            if self.rng.random() < self.f:
                fire_size = self.spread_fire(i, j)
                if fire_size > 0:
                    self.fire_sizes.append(fire_size)
                break

    def step(self):
        """Perform one simulation step."""
        self.timestep += 1
        self._clear_burning_cells()
        self._grow_trees()
        self._try_lightning_strike()
        self.tree_counts.append(self.count_trees())

    def run(self, num_steps, progress_interval=1000):
        """Run the simulation for a number of steps."""
        for step in range(num_steps):
            self.step()
            if progress_interval and (step + 1) % progress_interval == 0:
                print(f"Step {step + 1}/{num_steps}, Trees: {self.count_trees()}, Fires: {len(self.fire_sizes)}")

    def get_fire_distribution(self):
        """Get frequency distribution of fire sizes."""
        if not self.fire_sizes:
            return [], []

        counts = defaultdict(int)
        for size in self.fire_sizes:
            counts[size] += 1

        sizes = sorted(counts.keys())
        frequencies = [counts[s] for s in sizes]

        return sizes, frequencies

    def plot_state(self, ax=None):
        """Plot the current forest state."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))

        # Colors: black (empty), green (tree), red/orange (burning)
        colors = ['#1a1a2e', '#2d5a27', '#ff4500']
        cmap = ListedColormap(colors)

        im = ax.imshow(self.grid, cmap=cmap, vmin=0, vmax=2)
        density = self.tree_density()
        ax.set_title(f'Forest (Step {self.timestep}, Density: {density:.2%})')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')

        return im

    def plot_fire_distribution(self, ax=None):
        """Plot fire size distribution on log-log scale."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))

        sizes, frequencies = self.get_fire_distribution()

        if sizes:
            ax.loglog(sizes, frequencies, 'o', markersize=4, alpha=0.7, color='orangered')
            ax.set_xlabel('Fire Size (trees burned)')
            ax.set_ylabel('Frequency')
            ax.set_title('Fire Size Distribution (Log-Log)')
            ax.grid(True, alpha=0.3)

        return ax


def _setup_forest_animation(sim, ax1, ax2):
    """Set up axes for forest fire animation."""
    colors = ['#1a1a2e', '#2d5a27', '#ff4500']
    cmap = ListedColormap(colors)
    im = ax1.imshow(sim.grid, cmap=cmap, vmin=0, vmax=2)
    ax1.set_title('Forest')

    line, = ax2.loglog([], [], 'o', markersize=4, alpha=0.7, color='orangered')
    ax2.set_xlabel('Fire Size')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Fire Size Distribution')
    ax2.set_xlim(1, 10000)
    ax2.set_ylim(1, 1000)
    ax2.grid(True, alpha=0.3)

    return im, line


def _create_forest_update(sim, im, ax1, ax2, line):
    """Create animation update function for forest fire."""
    def update(frame):
        for _ in range(10):
            sim.step()

        im.set_array(sim.grid)
        density = sim.tree_density()
        ax1.set_title(f'Forest (Step {sim.timestep}, Density: {density:.1%}, Fires: {len(sim.fire_sizes)})')

        sizes, frequencies = sim.get_fire_distribution()
        if sizes:
            line.set_data(sizes, frequencies)
            ax2.set_xlim(0.8, max(sizes) * 2)
            ax2.set_ylim(0.8, max(max(frequencies), 10) * 2)

        return im, line
    return update


def run_interactive_simulation():
    """Run an animated simulation."""
    print("Forest Fire Simulation - Interactive")
    print("=" * 50)

    sim = ForestFireSimulation(size=200, tree_growth_prob=0.02, seed=42)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    im, line = _setup_forest_animation(sim, ax1, ax2)
    update = _create_forest_update(sim, im, ax1, ax2, line)

    FuncAnimation(fig, update, frames=500, interval=50, blit=False)
    plt.tight_layout()
    plt.show()


def _run_and_plot_scenario(sim, ax_state, ax_dist, label):
    """Run a simulation scenario and plot results."""
    sim.run(5000, progress_interval=1000)
    sim.plot_state(ax_state)
    ax_state.set_title(f'{label}: {len(sim.fire_sizes)} fires')
    sim.plot_fire_distribution(ax_dist)


def run_fire_suppression_demo():
    """Demonstrate the effect of fire suppression (low lightning probability)."""
    print("Forest Fire - Fire Suppression Demo")
    print("=" * 50)
    print("Comparing normal vs suppressed fire conditions...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    print("\nNormal conditions (p=0.01, f=0.001)...")
    sim_normal = ForestFireSimulation(size=200, tree_growth_prob=0.01, lightning_prob=0.001, seed=42)
    _run_and_plot_scenario(sim_normal, axes[0, 0], axes[0, 1], 'Normal')

    print("\nFire suppression (p=0.01, f=0.0001)...")
    sim_suppressed = ForestFireSimulation(size=200, tree_growth_prob=0.01, lightning_prob=0.0001, seed=42)
    _run_and_plot_scenario(sim_suppressed, axes[1, 0], axes[1, 1], 'Suppressed')

    plt.tight_layout()
    plt.savefig('forest_fire_suppression.png', dpi=150)
    plt.show()

    print("\nResults saved to forest_fire_suppression.png")
    print("\nNotice: With fire suppression, the forest becomes denser,")
    print("making catastrophic mega-fires more likely when they do occur!")


def _print_forest_stats(sim):
    """Print forest fire simulation statistics."""
    print(f"\nTimesteps: {sim.timestep}")
    print(f"Tree density: {sim.tree_density():.2%}")
    print(f"Total fires: {len(sim.fire_sizes)}")
    if sim.fire_sizes:
        print(f"Largest fire: {max(sim.fire_sizes)} trees")
        print(f"Average fire: {np.mean(sim.fire_sizes):.1f} trees")


def run_quick_demo():
    """Quick demonstration of the forest fire model."""
    print("Forest Fire Simulation")
    print("=" * 50)

    sim = ForestFireSimulation(size=200, tree_growth_prob=0.01, seed=42)
    print("Running simulation...")
    sim.run(10000, progress_interval=2000)

    _print_forest_stats(sim)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    sim.plot_state(ax1)
    sim.plot_fire_distribution(ax2)

    plt.tight_layout()
    plt.savefig('forest_fire_results.png', dpi=150)
    plt.show()
    print("\nResults saved to forest_fire_results.png")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--animate':
        run_interactive_simulation()
    elif len(sys.argv) > 1 and sys.argv[1] == '--suppression':
        run_fire_suppression_demo()
    else:
        run_quick_demo()
