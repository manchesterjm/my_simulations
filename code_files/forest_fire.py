"""Forest Fire Simulation - Drossel-Schwabl Model.

This module implements the Drossel-Schwabl forest fire model, a cellular automaton
that demonstrates self-organized criticality (SOC). The system naturally evolves
to a critical state without external tuning, exhibiting power-law behavior in
fire size distributions.

Model Overview:
    The Drossel-Schwabl model (1992) is one of the simplest examples of SOC.
    Each cell in a 2D grid can be in one of three states:
    - EMPTY (0): No tree present
    - TREE (1): Living tree
    - BURNING (2): Tree on fire (temporary state)

Rules (applied each timestep):
    1. Burning cells become EMPTY (fire consumes tree)
    2. Empty cells grow a TREE with probability p
    3. Trees are struck by lightning with probability f (typically f << p)
    4. Fire spreads instantly to all neighboring trees (Moore neighborhood)

Self-Organized Criticality:
    The system self-tunes to a critical state where:
    - Tree growth (p) slowly builds up fuel
    - Lightning strikes (f) trigger avalanches (fires)
    - Fire sizes follow a power-law distribution P(s) ~ s^(-τ)
    - The system exhibits "pink noise" in tree density fluctuations

    At criticality, the forest maintains an optimal density where small fires
    are common but large catastrophic fires occasionally occur. This is analogous
    to earthquake distributions (Gutenberg-Richter law) and solar flares.

Fire Suppression Paradox:
    Reducing lightning probability (f) causes higher tree density, making
    catastrophic mega-fires MORE likely when they do occur. This demonstrates
    the danger of disrupting self-organized critical systems.

GPU Acceleration:
    The simulation supports GPU acceleration via CuPy, though speedup is limited
    (~1.2-1.4x) due to the inherently sequential nature of BFS fire propagation.

References:
    Drossel, B., & Schwabl, F. (1992). Self-organized critical forest-fire model.
    Physical Review Letters, 69(11), 1629.

Example:
    >>> sim = ForestFireSimulation(size=200, tree_growth_prob=0.01, seed=42)
    >>> sim.run(10000)
    >>> sizes, frequencies = sim.get_fire_distribution()
    >>> # Plot log-log to see power law distribution
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

# Check GPU availability
try:
    from gpu_utils import cuda_available
    GPU_AVAILABLE = cuda_available()
except ImportError:
    GPU_AVAILABLE = False


def create_forest_fire(size=256, tree_growth_prob=0.01, lightning_prob=None,
                       seed=None, backend='auto'):
    """
    Factory function to create a Forest Fire simulation with the specified backend.

    Args:
        size: Grid size (size x size)
        tree_growth_prob: Probability p that an empty cell grows a tree
        lightning_prob: Probability f of lightning strike (default: p/10)
        seed: Random seed for reproducibility
        backend: 'auto', 'gpu', or 'cpu'
            - 'auto': Use GPU if available, else CPU
            - 'gpu': Force GPU (raises error if unavailable)
            - 'cpu': Force CPU

    Note: GPU provides limited speedup (~1.2-1.4x) for this simulation due to
    the inherently sequential BFS fire spread algorithm.

    Returns:
        ForestFireSimulation (CPU) or ForestFireGPU instance
    """
    use_gpu = False
    if backend == 'auto':
        use_gpu = GPU_AVAILABLE
    elif backend == 'gpu':
        if not GPU_AVAILABLE:
            raise RuntimeError("GPU backend requested but CUDA is not available")
        use_gpu = True
    elif backend == 'cpu':
        use_gpu = False
    else:
        raise ValueError(f"Unknown backend: {backend}. Use 'auto', 'gpu', or 'cpu'")

    if use_gpu:
        from forest_fire_gpu import ForestFireGPU
        return ForestFireGPU(size=size, tree_growth_prob=tree_growth_prob,
                             lightning_prob=lightning_prob, seed=seed)
    else:
        return ForestFireSimulation(size=size, tree_growth_prob=tree_growth_prob,
                                     lightning_prob=lightning_prob, seed=seed)


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
        """Count the total number of living trees in the forest.

        Returns:
            int: Number of cells in TREE state.
        """
        return np.sum(self.grid == TREE)

    def tree_density(self):
        """Calculate the fraction of cells occupied by trees.

        At the critical state, tree density fluctuates around an equilibrium
        value determined by the ratio of growth probability (p) to lightning
        probability (f).

        Returns:
            float: Tree density as a fraction (0.0 to 1.0).
        """
        return self.count_trees() / (self.size * self.size)

    def _get_moore_neighbors(self, i, j):
        """Get valid Moore neighborhood positions (8 adjacent cells).

        Fire spreads through the Moore neighborhood, which includes all 8 cells
        surrounding a burning tree (horizontal, vertical, and diagonal neighbors).
        Boundary cells have fewer neighbors as the grid does not wrap around.

        Args:
            i (int): Row index of the center cell.
            j (int): Column index of the center cell.

        Returns:
            list of tuple: List of (row, col) positions of valid neighbors.
        """
        neighbors = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:  # Skip the center cell itself
                    continue
                ni, nj = i + di, j + dj
                # Only include neighbors within grid boundaries
                if 0 <= ni < self.size and 0 <= nj < self.size:
                    neighbors.append((ni, nj))
        return neighbors

    def spread_fire(self, start_i, start_j):
        """Spread fire from ignition point to all connected trees using BFS.

        Fire propagates through the Moore neighborhood (8 adjacent cells) in a
        breadth-first manner, forming an "avalanche" that continues until all
        connected trees are consumed. This creates the power-law distribution
        characteristic of self-organized criticality.

        The fire spread is instantaneous in the model (all connected trees burn
        in a single timestep), representing the timescale separation between
        slow growth and fast fire propagation.

        Args:
            start_i (int): Row index of ignition point.
            start_j (int): Column index of ignition point.

        Returns:
            int: Total number of trees burned (fire size/avalanche size).
                 Returns 0 if starting cell is not a tree.
        """
        if self.grid[start_i, start_j] != TREE:
            return 0

        burned = 0
        queue = deque([(start_i, start_j)])
        self.grid[start_i, start_j] = BURNING

        # BFS to spread fire to all connected trees
        while queue:
            i, j = queue.popleft()
            burned += 1

            # Check all 8 neighbors for trees to ignite
            for ni, nj in self._get_moore_neighbors(i, j):
                if self.grid[ni, nj] == TREE:
                    self.grid[ni, nj] = BURNING
                    queue.append((ni, nj))

        return burned

    def _clear_burning_cells(self):
        """Convert all burning cells to empty cells.

        After fire spreads (instantaneous in the model), all burned trees
        become empty cells in the next timestep, ready for regrowth.
        """
        self.grid[self.grid == BURNING] = EMPTY

    def _grow_trees(self):
        """Grow new trees on empty cells with probability p.

        Tree growth is the slow driving force in the system, gradually building
        up fuel (tree clusters) until lightning triggers an avalanche. This
        timescale separation (slow growth vs fast fire) is essential for SOC.
        """
        empty_mask = self.grid == EMPTY
        # Each empty cell independently becomes a tree with probability p
        grow_mask = self.rng.random((self.size, self.size)) < self.p
        self.grid[empty_mask & grow_mask] = TREE

    def _try_lightning_strike(self):
        """Attempt to ignite a tree via lightning strike with probability f.

        Lightning is the perturbation that triggers avalanches (fires) in the
        system. The probability f is typically much smaller than growth
        probability p (often f = p/10), allowing the system to reach critical
        tree density before ignition.

        At most one fire starts per timestep. Once ignited, fire spreads
        instantaneously to all connected trees.
        """
        tree_positions = np.argwhere(self.grid == TREE)
        if len(tree_positions) == 0:
            return

        # Check each tree for lightning strike (at most one fire per step)
        for i, j in tree_positions:
            if self.rng.random() < self.f:
                fire_size = self.spread_fire(i, j)
                if fire_size > 0:
                    self.fire_sizes.append(fire_size)  # Record avalanche size
                break  # Only one fire per timestep

    def step(self):
        """Execute one timestep of the Drossel-Schwabl model.

        Each timestep applies the three model rules in sequence:
        1. Clear burning cells (fire consumption)
        2. Grow new trees (slow driving force)
        3. Attempt lightning strike (perturbation/trigger)

        Tree count is recorded after each step for time series analysis.
        """
        self.timestep += 1
        self._clear_burning_cells()  # Rule 1: Burning → Empty
        self._grow_trees()            # Rule 2: Empty → Tree (prob p)
        self._try_lightning_strike()  # Rule 3: Tree → Burning (prob f)
        self.tree_counts.append(self.count_trees())

    def run(self, num_steps, progress_interval=1000):
        """Run the simulation for multiple timesteps.

        The system typically requires thousands of steps to reach the critical
        state where power-law behavior emerges. Early transients should be
        discarded when analyzing distributions.

        Args:
            num_steps (int): Number of timesteps to simulate.
            progress_interval (int or None): Print progress every N steps.
                Set to None to disable progress printing.
        """
        for step in range(num_steps):
            self.step()
            if progress_interval and (step + 1) % progress_interval == 0:
                print(
                    f"Step {step + 1}/{num_steps}, Trees: {self.count_trees()}, "
                    f"Fires: {len(self.fire_sizes)}"
                )

    def get_fire_distribution(self):
        """Get frequency distribution of fire sizes for power-law analysis.

        At the critical state, the distribution follows a power law:
        P(s) ~ s^(-τ), which appears as a straight line on a log-log plot.
        This is the signature of self-organized criticality.

        Returns:
            tuple: (sizes, frequencies) where:
                - sizes (list of int): Unique fire sizes (trees burned).
                - frequencies (list of int): Number of fires of each size.
                Returns ([], []) if no fires have occurred.
        """
        if not self.fire_sizes:
            return [], []

        # Count occurrences of each fire size
        counts = defaultdict(int)
        for size in self.fire_sizes:
            counts[size] += 1

        sizes = sorted(counts.keys())
        frequencies = [counts[s] for s in sizes]

        return sizes, frequencies

    def plot_state(self, ax=None):
        """Plot the current forest state as a colored grid.

        Visualizes the spatial structure of the forest showing tree clusters,
        empty patches, and active fires. At criticality, the forest exhibits
        fractal-like patterns with clusters at all scales.

        Args:
            ax (matplotlib.axes.Axes, optional): Axes to plot on.
                If None, creates a new figure.

        Returns:
            matplotlib.image.AxesImage: Image object for animation updates.
        """
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
        """Plot fire size distribution on log-log scale to reveal power law.

        A power-law distribution P(s) ~ s^(-τ) appears as a straight line on
        a log-log plot. This is the hallmark of self-organized criticality,
        indicating scale-invariant behavior (no characteristic fire size).

        Args:
            ax (matplotlib.axes.Axes, optional): Axes to plot on.
                If None, creates a new figure.

        Returns:
            matplotlib.axes.Axes: Axes object with the plot.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))

        sizes, frequencies = self.get_fire_distribution()

        if sizes:
            ax.loglog(
                sizes, frequencies, 'o', markersize=4, alpha=0.7,
                color='orangered'
            )
            ax.set_xlabel('Fire Size (trees burned)')
            ax.set_ylabel('Frequency')
            ax.set_title('Fire Size Distribution (Log-Log)')
            ax.grid(True, alpha=0.3)

        return ax


def _setup_forest_animation(sim, ax1, ax2):
    """Set up visualization axes for animated forest fire simulation.

    Args:
        sim (ForestFireSimulation): Simulation instance.
        ax1 (matplotlib.axes.Axes): Axes for forest state visualization.
        ax2 (matplotlib.axes.Axes): Axes for fire size distribution plot.

    Returns:
        tuple: (im, line) matplotlib objects for updating animation.
    """
    # Set up forest state visualization
    colors = ['#1a1a2e', '#2d5a27', '#ff4500']  # Empty, Tree, Burning
    cmap = ListedColormap(colors)
    im = ax1.imshow(sim.grid, cmap=cmap, vmin=0, vmax=2)
    ax1.set_title('Forest')

    # Set up distribution plot
    line, = ax2.loglog([], [], 'o', markersize=4, alpha=0.7, color='orangered')
    ax2.set_xlabel('Fire Size')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Fire Size Distribution')
    ax2.set_xlim(1, 10000)
    ax2.set_ylim(1, 1000)
    ax2.grid(True, alpha=0.3)

    return im, line


def _create_forest_update(sim, im, ax1, ax2, line):
    """Create animation update function with gradual fire spread visualization.

    The standard model spreads fire instantaneously, but for visualization
    purposes, this creates an update function that spreads fire one layer
    per frame, making the BFS propagation visible.

    Args:
        sim (ForestFireSimulation): Simulation instance.
        im (matplotlib.image.AxesImage): Image object for forest grid.
        ax1 (matplotlib.axes.Axes): Axes for forest visualization.
        ax2 (matplotlib.axes.Axes): Axes for distribution plot.
        line (matplotlib.lines.Line2D): Line object for distribution.

    Returns:
        function: Update function for FuncAnimation that takes frame number.
    """
    # Track active fire state across frames
    state = {'burning_count': 0, 'fire_size': 0}

    def _spread_fire_layer():
        """Spread fire one layer outward from currently burning cells."""
        burning_cells = np.argwhere(sim.grid == BURNING)
        new_burning = []

        # Find all trees adjacent to burning cells
        for i, j in burning_cells:
            for ni, nj in sim._get_moore_neighbors(i, j):
                if sim.grid[ni, nj] == TREE:
                    new_burning.append((ni, nj))

        # Current burning cells become empty (consumed by fire)
        sim.grid[sim.grid == BURNING] = EMPTY

        # Ignite newly reached trees
        for ni, nj in new_burning:
            sim.grid[ni, nj] = BURNING
            state['fire_size'] += 1

        # Record fire size when spread is complete
        if len(new_burning) == 0 and state['fire_size'] > 0:
            sim.fire_sizes.append(state['fire_size'])
            state['fire_size'] = 0

    def _execute_normal_step():
        """Execute normal simulation step: grow trees and maybe start fire."""
        sim.timestep += 1
        sim._grow_trees()

        # Try lightning - ignite one cell without immediate spread
        tree_positions = np.argwhere(sim.grid == TREE)
        if len(tree_positions) > 0:
            for i, j in tree_positions:
                if sim.rng.random() < sim.f:
                    sim.grid[i, j] = BURNING
                    state['fire_size'] = 1  # Start tracking new fire
                    break

        sim.tree_counts.append(sim.count_trees())

    def _update_visualization():
        """Update both forest grid and distribution plot."""
        im.set_array(sim.grid)
        density = sim.tree_density()
        ax1.set_title(
            f'Forest (Step {sim.timestep}, Density: {density:.1%}, '
            f'Fires: {len(sim.fire_sizes)})'
        )

        # Update distribution plot with current data
        sizes, frequencies = sim.get_fire_distribution()
        if sizes:
            line.set_data(sizes, frequencies)
            ax2.set_xlim(0.8, max(sizes) * 2)
            ax2.set_ylim(0.8, max(max(frequencies), 10) * 2)

    def update(frame):
        """Animation update function called each frame.

        Args:
            frame (int): Frame number (unused, required by FuncAnimation).

        Returns:
            tuple: (im, line) updated matplotlib objects.
        """
        burning_cells = np.argwhere(sim.grid == BURNING)

        if len(burning_cells) > 0:
            # Fire is active - spread one layer per frame for visualization
            _spread_fire_layer()
        else:
            # No active fire - do normal step
            _execute_normal_step()

        _update_visualization()
        return im, line

    return update


def run_interactive_simulation():
    """Run animated forest fire simulation with gradual fire spread.

    Displays side-by-side visualization of forest state and fire size
    distribution. Fire spreads one layer per frame to show BFS propagation.
    Watch as the system self-organizes to a critical state where small
    fires are common but large catastrophic fires occasionally occur.
    """
    print("Forest Fire Simulation - Interactive")
    print("=" * 50)

    sim = ForestFireSimulation(size=200, tree_growth_prob=0.02, seed=42)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    im, line = _setup_forest_animation(sim, ax1, ax2)
    update = _create_forest_update(sim, im, ax1, ax2, line)

    _anim = FuncAnimation(fig, update, frames=500, interval=1000, blit=False)
    plt.tight_layout()
    plt.show()


def _run_and_plot_scenario(sim, ax_state, ax_dist, label):
    """Run a single simulation scenario and plot its results.

    Args:
        sim (ForestFireSimulation): Configured simulation instance.
        ax_state (matplotlib.axes.Axes): Axes for final forest state.
        ax_dist (matplotlib.axes.Axes): Axes for fire distribution.
        label (str): Label for the scenario (e.g., "Normal", "Suppressed").
    """
    sim.run(5000, progress_interval=1000)
    sim.plot_state(ax_state)
    ax_state.set_title(f'{label}: {len(sim.fire_sizes)} fires')
    sim.plot_fire_distribution(ax_dist)


def run_fire_suppression_demo():
    """Demonstrate the fire suppression paradox.

    Compares two scenarios:
    1. Normal: Natural lightning frequency (f = p/10)
    2. Suppressed: Reduced lightning (fire suppression policy)

    The suppression scenario shows higher tree density but larger catastrophic
    fires when they do occur, demonstrating the danger of disrupting
    self-organized critical systems. This mirrors real-world forest management
    where fire suppression leads to fuel accumulation and mega-fires.
    """
    print("Forest Fire - Fire Suppression Demo")
    print("=" * 50)
    print("Comparing normal vs suppressed fire conditions...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    print("\nNormal conditions (p=0.01, f=0.001)...")
    sim_normal = ForestFireSimulation(
        size=200, tree_growth_prob=0.01, lightning_prob=0.001, seed=42
    )
    _run_and_plot_scenario(sim_normal, axes[0, 0], axes[0, 1], 'Normal')

    print("\nFire suppression (p=0.01, f=0.0001)...")
    sim_suppressed = ForestFireSimulation(
        size=200, tree_growth_prob=0.01, lightning_prob=0.0001, seed=42
    )
    _run_and_plot_scenario(sim_suppressed, axes[1, 0], axes[1, 1], 'Suppressed')

    plt.tight_layout()
    plt.savefig('forest_fire_suppression.png', dpi=150)
    plt.show()

    print("\nResults saved to forest_fire_suppression.png")
    print("\nNotice: With fire suppression, the forest becomes denser,")
    print("making catastrophic mega-fires more likely when they do occur!")


def _print_forest_stats(sim):
    """Print summary statistics from forest fire simulation.

    Args:
        sim (ForestFireSimulation): Completed simulation instance.
    """
    print(f"\nTimesteps: {sim.timestep}")
    print(f"Tree density: {sim.tree_density():.2%}")
    print(f"Total fires: {len(sim.fire_sizes)}")
    if sim.fire_sizes:
        print(f"Largest fire: {max(sim.fire_sizes)} trees")
        print(f"Average fire: {np.mean(sim.fire_sizes):.1f} trees")


def run_quick_demo():
    """Run quick demonstration showing self-organized criticality.

    Executes 10,000 timesteps with default parameters and displays:
    1. Final forest state showing spatial structure
    2. Fire size distribution on log-log scale (should show power law)

    The simulation demonstrates how the Drossel-Schwabl model self-organizes
    to a critical state exhibiting scale-invariant avalanche dynamics.
    """
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
