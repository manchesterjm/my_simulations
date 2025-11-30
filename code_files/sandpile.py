"""Abelian Sandpile Model - Self-Organized Criticality Simulation

This module implements Per Bak's Abelian Sandpile Model, a cellular automaton that
demonstrates self-organized criticality (SOC). The model shows how complex systems
naturally evolve toward a critical state where events of all sizes can occur,
following power law distributions.

The Sandpile Model:
-------------------
The sandpile operates on a 2D grid where each cell contains a number of sand grains.
When grains are added one-by-one, the pile builds up until it reaches a critical
state. At this point, adding just one more grain can trigger avalanches of any size.

Physics & Mechanics:
-------------------
1. **Addition**: Grains are dropped one at a time onto the grid (random or center).
2. **Toppling**: When a cell reaches the threshold (typically 4 grains), it becomes
   unstable and "topples" - redistributing 4 grains to its 4 orthogonal neighbors.
3. **Cascading**: Toppling can cause neighboring cells to exceed the threshold,
   triggering cascading avalanches that propagate through the grid.
4. **Dissipation**: Grains that topple off the edge of the grid are lost, creating
   a natural dissipation mechanism that prevents infinite growth.
5. **Criticality**: After many drops, the system reaches a critical state where
   the distribution of avalanche sizes follows a power law: P(s) ∝ s^(-τ), where
   τ ≈ 1.0 for 2D sandpiles.

Self-Organized Criticality:
--------------------------
SOC systems have three key properties, all exhibited by this model:
1. **Self-organization**: The system evolves to criticality without external tuning
2. **Scale invariance**: Avalanches occur at all scales (power law distribution)
3. **Universality**: The critical exponent τ is independent of details like grid size

Backend Support:
---------------
The simulation supports both CPU and GPU backends:
- CPU: Pure NumPy implementation (works everywhere)
- GPU: CuPy implementation with ~40x speedup for large grids (requires CUDA)
- Auto: Automatically selects GPU if available, falls back to CPU

Example Usage:
-------------
    # Quick demonstration
    from sandpile import SandpileSimulation

    sim = SandpileSimulation(size=100, drop_mode='random', seed=42)
    sim.run(50000)  # Drop 50,000 grains

    # Analyze results
    sizes, frequencies = sim.get_avalanche_distribution()
    sim.plot_power_law()

    # GPU-accelerated simulation
    from sandpile import create_sandpile

    sim = create_sandpile(size=200, backend='auto')  # Uses GPU if available
    sim.run(100000)

References:
----------
- Bak, P., Tang, C., & Wiesenfeld, K. (1987). "Self-organized criticality: An
  explanation of the 1/f noise." Physical Review Letters, 59(4), 381.
- Veritasium video on power laws and self-organized criticality
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.animation import FuncAnimation
from collections import defaultdict

# Check GPU availability
try:
    from gpu_utils import cuda_available
    GPU_AVAILABLE = cuda_available()
except ImportError:
    GPU_AVAILABLE = False


def create_sandpile(
    size=50, threshold=4, drop_mode='random', seed=None, backend='auto'
):
    """Factory function to create a Sandpile simulation with backend selection.

    This function provides automatic backend selection between CPU and GPU
    implementations. The GPU backend (when available) provides ~40x speedup
    for large grids through parallelized avalanche processing.

    Args:
        size (int): Grid size (size x size). Default 50. Larger grids show
            clearer power law behavior but require more computation time.
        threshold (int): Number of grains that triggers toppling. Default 4.
            Standard value for 2D sandpile with 4 orthogonal neighbors.
        drop_mode (str): Where to drop grains. Options:
            - 'random': Drop at random locations (faster criticality)
            - 'center': Drop at grid center (creates symmetric patterns)
        seed (int, optional): Random seed for reproducible results.
            Same seed produces identical avalanche sequences.
        backend (str): Computation backend. Options:
            - 'auto': Use GPU if available, else CPU (recommended)
            - 'gpu': Force GPU (raises RuntimeError if unavailable)
            - 'cpu': Force CPU (always works)

    Returns:
        SandpileSimulation or SandpileSimulationGPU: Instance of the appropriate
            simulation class based on backend selection.

    Raises:
        RuntimeError: If backend='gpu' is specified but CUDA is not available.
        ValueError: If backend is not 'auto', 'gpu', or 'cpu'.

    Example:
        >>> sim = create_sandpile(size=100, backend='auto')
        >>> sim.run(50000)
        >>> sizes, freqs = sim.get_avalanche_distribution()
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
        from sandpile_gpu import SandpileSimulationGPU
        return SandpileSimulationGPU(size=size, threshold=threshold,
                                      drop_mode=drop_mode, seed=seed)
    else:
        return SandpileSimulation(size=size, threshold=threshold,
                                   drop_mode=drop_mode, seed=seed)


class SandpileSimulation:
    """Abelian Sandpile Model simulation (CPU implementation).

    This class implements the core mechanics of the Abelian Sandpile Model,
    a cellular automaton that demonstrates self-organized criticality. The
    simulation evolves a 2D grid of sand grains through repeated dropping
    and toppling events.

    The system naturally evolves to a critical state where avalanche sizes
    follow a power law distribution P(s) ∝ s^(-τ), with τ ≈ 1.0 for 2D grids.
    This emergent behavior occurs without any parameter tuning - the system
    "self-organizes" to criticality.

    Attributes:
        size (int): Grid dimensions (size x size).
        threshold (int): Number of grains that triggers toppling.
        drop_mode (str): Grain dropping strategy ('random' or 'center').
        grid (np.ndarray): 2D array of grain counts, shape (size, size).
        rng (np.random.Generator): Random number generator for reproducibility.
        total_grains (int): Total number of grains dropped into the system.
        avalanche_sizes (list): Recorded sizes (topple counts) of all avalanches.

    Example:
        >>> sim = SandpileSimulation(size=100, drop_mode='random', seed=42)
        >>> sim.run(50000)  # Reach critical state
        >>> sizes, freqs = sim.get_avalanche_distribution()
        >>> sim.plot_power_law()  # Show power law distribution
    """

    def __init__(self, size=50, threshold=4, drop_mode='random', seed=None):
        """Initialize the sandpile simulation.

        Creates an empty grid and sets up the random number generator. The grid
        starts with zero grains in all cells. As grains are dropped, the system
        gradually builds up to a critical state.

        Args:
            size (int): Grid size (size x size). Default 50. Larger grids show
                clearer power law statistics but require more drops to reach
                the critical state.
            threshold (int): Number of grains that triggers toppling. Default 4,
                corresponding to 4 orthogonal neighbors in a 2D grid.
            drop_mode (str): Where to drop grains. Options:
                - 'random': Drop at uniformly random positions (default)
                - 'center': Drop all grains at the grid center
            seed (int, optional): Random seed for reproducibility. If None,
                results will vary between runs.
        """
        self.size = size
        self.threshold = threshold
        self.drop_mode = drop_mode
        # Initialize grid with zeros (empty sandpile)
        self.grid = np.zeros((size, size), dtype=np.int32)
        # Create RNG for reproducible random drops
        self.rng = np.random.default_rng(seed)

        # Statistics tracking for power law analysis
        self.total_grains = 0  # Total grains added to system
        self.avalanche_sizes = []  # Size (topple count) of each avalanche

    def _get_drop_position(self):
        """Get the position where the next grain will be dropped.

        The drop position depends on the configured drop_mode:
        - 'center': Always returns the center of the grid
        - 'random': Returns a uniformly random position

        Returns:
            tuple: (row, col) coordinates where the grain will be dropped.
        """
        if self.drop_mode == 'center':
            return self.size // 2, self.size // 2
        return self.rng.integers(0, self.size), self.rng.integers(0, self.size)

    def _distribute_to_neighbors(self, topple_mask):
        """Distribute grains from toppled cells to their orthogonal neighbors.

        Each toppling cell distributes exactly one grain to each of its four
        orthogonal neighbors (up, down, left, right). Grains that would go
        off the edge of the grid are lost (dissipation mechanism).

        This uses efficient NumPy array slicing to update all neighbors in
        parallel, which is much faster than iterating over individual cells.

        Args:
            topple_mask (np.ndarray): Binary mask where 1 indicates a cell
                that is toppling this iteration, shape (size, size).
        """
        # Distribute one grain to each orthogonal neighbor using array slicing
        # Note: Grains at boundaries don't wrap - they fall off the edge
        self.grid[1:, :] += topple_mask[:-1, :]   # Up (row - 1)
        self.grid[:-1, :] += topple_mask[1:, :]   # Down (row + 1)
        self.grid[:, 1:] += topple_mask[:, :-1]   # Left (col - 1)
        self.grid[:, :-1] += topple_mask[:, 1:]   # Right (col + 1)

    def _record_avalanche(self, size):
        """Record an avalanche if it occurred.

        Avalanche size is measured by the total number of toppling events
        (not the number of grains moved). A size of 0 means no toppling occurred.

        Args:
            size (int): Number of toppling events in the avalanche. Only
                recorded if size > 0.
        """
        if size > 0:
            self.avalanche_sizes.append(size)

    def drop_grain(self):
        """Drop a single grain of sand and process any resulting avalanche.

        This is the primary interface for advancing the simulation. Each grain
        drop may or may not trigger an avalanche, depending on the current state
        of the grid. In the critical state, avalanches of all sizes can occur.

        The process:
        1. Determine drop position (random or center)
        2. Add grain to that cell
        3. Process any resulting avalanche until grid is stable
        4. Record avalanche size for statistical analysis

        Returns:
            int: Total number of toppling events in the avalanche. Returns 0
                if no avalanche occurred (grain landed on cell with < threshold-1
                grains).
        """
        # Determine where this grain will land
        x, y = self._get_drop_position()
        # Add one grain to that cell
        self.grid[x, y] += 1
        self.total_grains += 1

        # Process any cascading avalanche triggered by this grain
        avalanche_size = self.process_avalanche()
        self._record_avalanche(avalanche_size)

        return avalanche_size

    def process_avalanche(self):
        """Process all toppling until the grid reaches a stable state.

        An avalanche proceeds in discrete time steps. At each step, all cells
        that are unstable (grain count >= threshold) topple simultaneously.
        Each toppling cell:
        1. Loses 'threshold' grains (typically 4)
        2. Distributes one grain to each of its 4 neighbors

        This process repeats until no cells are unstable. The avalanche then
        stops, and the grid is in a stable state (all cells < threshold).

        Key property: The final state is independent of the order in which cells
        topple - hence "Abelian" sandpile (commutative property).

        Returns:
            int: Total number of toppling events across all iterations of the
                avalanche. This is the avalanche "size" used for power law analysis.
        """
        total_topples = 0

        # Continue until grid is stable (no unstable cells)
        while True:
            # Find all unstable cells (>= threshold grains)
            unstable = self.grid >= self.threshold
            if not np.any(unstable):
                # Grid is stable - avalanche is over
                break

            # Count toppling events this iteration
            topple_count = np.sum(unstable)
            total_topples += topple_count

            # All unstable cells topple simultaneously
            topple_mask = unstable.astype(np.int32)
            # Remove 'threshold' grains from each toppling cell
            self.grid -= self.threshold * topple_mask
            # Distribute one grain to each neighbor of toppling cells
            self._distribute_to_neighbors(topple_mask)

        return total_topples

    def run(self, num_drops):
        """Run the simulation for a specified number of grain drops.

        This is the main simulation loop. Each iteration drops one grain and
        processes any resulting avalanche. After many drops (typically 10,000+),
        the system reaches a critical state where the avalanche size distribution
        follows a power law.

        Args:
            num_drops (int): Number of grains to drop. For clear power law
                statistics, use at least 10,000 drops. Larger grids require
                more drops to reach criticality.
        """
        for _ in range(num_drops):
            self.drop_grain()

    def get_avalanche_distribution(self):
        """Get the frequency distribution of avalanche sizes for power law analysis.

        Computes a histogram of avalanche sizes, counting how many times each
        size occurred. This distribution can be plotted on log-log axes to
        visualize the power law relationship: P(s) ∝ s^(-τ).

        Returns:
            tuple: (sizes, frequencies) where:
                - sizes (list): Sorted unique avalanche sizes
                - frequencies (list): Count of how many times each size occurred
                Returns ({}, {}) if no avalanches have been recorded yet.

        Example:
            >>> sim = SandpileSimulation(size=100, seed=42)
            >>> sim.run(50000)
            >>> sizes, freqs = sim.get_avalanche_distribution()
            >>> # Plot on log-log axes to see power law
        """
        if not self.avalanche_sizes:
            return {}, {}

        # Count frequency of each avalanche size
        counts = defaultdict(int)
        for size in self.avalanche_sizes:
            counts[size] += 1

        # Sort by size for cleaner plotting
        sizes = sorted(counts.keys())
        frequencies = [counts[s] for s in sizes]

        return sizes, frequencies

    def plot_state(self, ax=None):
        """Plot the current state of the sandpile grid.

        Visualizes the spatial distribution of grains using a color map where
        darker colors indicate more grains. Red cells (if any) are unstable
        and should only appear transiently during avalanche processing.

        Args:
            ax (matplotlib.axes.Axes, optional): Axes to plot on. If None,
                creates a new figure with size (8, 8).

        Returns:
            matplotlib.image.AxesImage: The image object created by imshow,
                useful for animations.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))

        # Custom colormap: darker = more grains, red = unstable (>= threshold)
        colors = ['#2d2d2d', '#8b7355', '#c4a35a', '#daa520', '#ff4444']
        cmap = ListedColormap(colors)

        im = ax.imshow(self.grid, cmap=cmap, vmin=0, vmax=self.threshold)
        ax.set_title(
            f'Sandpile (Grains: {self.total_grains}, '
            f'Avalanches: {len(self.avalanche_sizes)})'
        )
        ax.set_xlabel('X')
        ax.set_ylabel('Y')

        return im

    def plot_power_law(self, ax=None):
        """Plot the avalanche size distribution on log-log scale.

        Visualizes the power law distribution of avalanche sizes. In the critical
        state, this plot shows a straight line on log-log axes, indicating
        P(s) ∝ s^(-τ). The slope of the line is -τ, which is approximately -1.0
        for 2D sandpiles.

        Args:
            ax (matplotlib.axes.Axes, optional): Axes to plot on. If None,
                creates a new figure with size (8, 6).

        Returns:
            matplotlib.axes.Axes: The axes object containing the plot.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))

        sizes, frequencies = self.get_avalanche_distribution()

        if sizes:
            # Log-log plot reveals power law as straight line
            ax.loglog(sizes, frequencies, 'o', markersize=4, alpha=0.7)
            ax.set_xlabel('Avalanche Size (number of topples)')
            ax.set_ylabel('Frequency')
            ax.set_title('Avalanche Size Distribution (Log-Log)')
            ax.grid(True, alpha=0.3)

        return ax


def _setup_animation_axes(ax1, ax2, sim):
    """Set up axes for animation display.

    Creates the initial plot elements for both the grid visualization and
    the power law distribution plot. These will be updated each frame.

    Args:
        ax1 (matplotlib.axes.Axes): Axes for grid visualization.
        ax2 (matplotlib.axes.Axes): Axes for power law distribution.
        sim (SandpileSimulation): Simulation instance to visualize.

    Returns:
        tuple: (im, line) where:
            - im: AxesImage for the grid heatmap
            - line: Line2D for the distribution scatter plot
    """
    # Set up grid visualization
    im = ax1.imshow(sim.grid, cmap='YlOrBr', vmin=0, vmax=sim.threshold)
    plt.colorbar(im, ax=ax1, label='Grains')
    ax1.set_title('Sandpile')

    # Set up power law distribution plot
    line, = ax2.loglog([], [], 'o', markersize=4, alpha=0.7)
    ax2.set_xlabel('Avalanche Size')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Power Law Distribution')
    ax2.set_xlim(1, 10000)
    ax2.set_ylim(1, 10000)
    ax2.grid(True, alpha=0.3)

    return im, line


def _create_update_function(sim, im, ax1, ax2, line):
    """Create the animation update function.

    Returns a closure that updates the visualization each frame. The update
    function drops 100 grains per frame and refreshes both plots.

    Args:
        sim (SandpileSimulation): Simulation instance.
        im (matplotlib.image.AxesImage): Grid visualization image.
        ax1 (matplotlib.axes.Axes): Axes for grid.
        ax2 (matplotlib.axes.Axes): Axes for distribution.
        line (matplotlib.lines.Line2D): Distribution plot line.

    Returns:
        function: Update function for FuncAnimation.
    """
    def update(frame):
        # Drop 100 grains per frame for smooth animation
        for _ in range(100):
            sim.drop_grain()

        # Update grid visualization
        im.set_array(sim.grid)
        ax1.set_title(f'Sandpile (Grains: {sim.total_grains})')

        # Update power law distribution
        sizes, frequencies = sim.get_avalanche_distribution()
        if sizes:
            line.set_data(sizes, frequencies)
            # Adjust axes dynamically as distribution evolves
            ax2.set_xlim(0.8, max(sizes) * 2)
            ax2.set_ylim(0.8, max(frequencies) * 2)

        return im, line
    return update


def run_interactive_simulation():
    """Run an animated sandpile simulation.

    Creates a real-time visualization showing both the grid state and the
    evolving power law distribution. The animation runs for 500 frames,
    dropping 100 grains per frame (50,000 total grains).

    Watch as the system self-organizes to criticality - the distribution
    plot will gradually form a straight line on the log-log axes.
    """
    # Create simulation with fixed seed for reproducibility
    sim = SandpileSimulation(size=100, drop_mode='random', seed=42)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Set up visualization elements
    im, line = _setup_animation_axes(ax1, ax2, sim)
    update = _create_update_function(sim, im, ax1, ax2, line)

    # Run animation (500 frames × 100 grains = 50,000 total grains)
    _anim = FuncAnimation(fig, update, frames=500, interval=50, blit=False)
    plt.tight_layout()
    plt.show()


def _print_simulation_stats(sim):
    """Print simulation statistics to console.

    Displays key metrics about the simulation run, including total grains
    dropped, number of avalanches, and avalanche size statistics.

    Args:
        sim (SandpileSimulation): Simulation instance to report on.
    """
    print(f"Total grains dropped: {sim.total_grains}")
    print(f"Total avalanches: {len(sim.avalanche_sizes)}")
    if sim.avalanche_sizes:
        print(f"Largest avalanche: {max(sim.avalanche_sizes)} topples")
        print(f"Average avalanche: {np.mean(sim.avalanche_sizes):.1f} topples")


def _plot_demo_results(sim):
    """Plot and save demonstration results.

    Creates a two-panel figure showing:
    1. Final grid state with grain distribution
    2. Power law distribution on log-log axes

    The figure is saved to 'sandpile_results.png' and displayed.

    Args:
        sim (SandpileSimulation): Simulation instance to visualize.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot final grid state
    im = ax1.imshow(sim.grid, cmap='YlOrBr', vmin=0, vmax=sim.threshold)
    plt.colorbar(im, ax=ax1, label='Grains')
    ax1.set_title(f'Sandpile State ({sim.size}x{sim.size})')

    # Plot power law distribution
    sim.plot_power_law(ax2)

    plt.tight_layout()
    plt.savefig('sandpile_results.png', dpi=150)
    plt.show()


def run_quick_demo():
    """Run a quick demonstration of the sandpile model.

    This function demonstrates the complete sandpile simulation workflow:
    1. Initialize a 100×100 grid
    2. Drop 50,000 grains at random locations
    3. Print statistics about avalanche distribution
    4. Plot and save results showing the power law

    The simulation uses a fixed seed for reproducibility. Results are
    saved to 'sandpile_results.png' in the current directory.
    """
    print("Running Sandpile Simulation...")
    print("=" * 50)

    # Create and run simulation (50,000 drops is enough to reach criticality)
    sim = SandpileSimulation(size=100, drop_mode='random', seed=42)
    sim.run(50000)

    # Display statistics and visualizations
    _print_simulation_stats(sim)
    _plot_demo_results(sim)

    print("\nResults saved to sandpile_results.png")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--animate':
        run_interactive_simulation()
    else:
        run_quick_demo()
