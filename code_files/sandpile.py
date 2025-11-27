"""
Sandpile Avalanche Simulation
Based on Per Bak's Abelian Sandpile Model demonstrating self-organized criticality.

When a cell reaches the threshold (4 grains), it topples and distributes
one grain to each of its 4 neighbors. This can trigger cascading avalanches.
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


def create_sandpile(size=50, threshold=4, drop_mode='random', seed=None, backend='auto'):
    """
    Factory function to create a Sandpile simulation with the specified backend.

    Args:
        size: Grid size (size x size)
        threshold: Number of grains that triggers toppling (default 4)
        drop_mode: 'center' or 'random' drop location
        seed: Random seed for reproducibility
        backend: 'auto', 'gpu', or 'cpu'
            - 'auto': Use GPU if available, else CPU
            - 'gpu': Force GPU (raises error if unavailable)
            - 'cpu': Force CPU

    Returns:
        SandpileSimulation (CPU) or SandpileSimulationGPU instance
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
    def __init__(self, size=50, threshold=4, drop_mode='random', seed=None):
        """
        Initialize the sandpile simulation.

        Args:
            size: Grid size (size x size)
            threshold: Number of grains that triggers toppling (default 4)
            drop_mode: 'center' or 'random' drop location
            seed: Random seed for reproducibility
        """
        self.size = size
        self.threshold = threshold
        self.drop_mode = drop_mode
        self.grid = np.zeros((size, size), dtype=np.int32)
        self.rng = np.random.default_rng(seed)

        # Statistics
        self.total_grains = 0
        self.avalanche_sizes = []

    def _get_drop_position(self):
        """Get the position where the next grain will be dropped."""
        if self.drop_mode == 'center':
            return self.size // 2, self.size // 2
        return self.rng.integers(0, self.size), self.rng.integers(0, self.size)

    def _distribute_to_neighbors(self, topple_mask):
        """Distribute grains from toppled cells to their neighbors."""
        self.grid[1:, :] += topple_mask[:-1, :]   # Up
        self.grid[:-1, :] += topple_mask[1:, :]   # Down
        self.grid[:, 1:] += topple_mask[:, :-1]   # Left
        self.grid[:, :-1] += topple_mask[:, 1:]   # Right

    def _record_avalanche(self, size):
        """Record an avalanche if it occurred."""
        if size > 0:
            self.avalanche_sizes.append(size)

    def drop_grain(self):
        """Drop a single grain of sand and process any resulting avalanche."""
        x, y = self._get_drop_position()
        self.grid[x, y] += 1
        self.total_grains += 1

        avalanche_size = self.process_avalanche()
        self._record_avalanche(avalanche_size)

        return avalanche_size

    def process_avalanche(self):
        """Process all toppling until the grid is stable."""
        total_topples = 0

        while True:
            unstable = self.grid >= self.threshold
            if not np.any(unstable):
                break

            topple_count = np.sum(unstable)
            total_topples += topple_count

            topple_mask = unstable.astype(np.int32)
            self.grid -= self.threshold * topple_mask
            self._distribute_to_neighbors(topple_mask)

        return total_topples

    def run(self, num_drops):
        """Run the simulation for a number of grain drops."""
        for _ in range(num_drops):
            self.drop_grain()

    def get_avalanche_distribution(self):
        """Get the frequency distribution of avalanche sizes."""
        if not self.avalanche_sizes:
            return {}, {}

        counts = defaultdict(int)
        for size in self.avalanche_sizes:
            counts[size] += 1

        sizes = sorted(counts.keys())
        frequencies = [counts[s] for s in sizes]

        return sizes, frequencies

    def plot_state(self, ax=None):
        """Plot the current state of the sandpile."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))

        # Custom colormap: darker = more grains
        colors = ['#2d2d2d', '#8b7355', '#c4a35a', '#daa520', '#ff4444']
        cmap = ListedColormap(colors)

        im = ax.imshow(self.grid, cmap=cmap, vmin=0, vmax=self.threshold)
        ax.set_title(f'Sandpile (Grains: {self.total_grains}, Avalanches: {len(self.avalanche_sizes)})')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')

        return im

    def plot_power_law(self, ax=None):
        """Plot the avalanche size distribution on log-log scale."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))

        sizes, frequencies = self.get_avalanche_distribution()

        if sizes:
            ax.loglog(sizes, frequencies, 'o', markersize=4, alpha=0.7)
            ax.set_xlabel('Avalanche Size (number of topples)')
            ax.set_ylabel('Frequency')
            ax.set_title('Avalanche Size Distribution (Log-Log)')
            ax.grid(True, alpha=0.3)

        return ax


def _setup_animation_axes(ax1, ax2, sim):
    """Set up axes for animation display."""
    im = ax1.imshow(sim.grid, cmap='YlOrBr', vmin=0, vmax=sim.threshold)
    plt.colorbar(im, ax=ax1, label='Grains')
    ax1.set_title('Sandpile')

    line, = ax2.loglog([], [], 'o', markersize=4, alpha=0.7)
    ax2.set_xlabel('Avalanche Size')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Power Law Distribution')
    ax2.set_xlim(1, 10000)
    ax2.set_ylim(1, 10000)
    ax2.grid(True, alpha=0.3)

    return im, line


def _create_update_function(sim, im, ax1, ax2, line):
    """Create the animation update function."""
    def update(frame):
        for _ in range(100):
            sim.drop_grain()

        im.set_array(sim.grid)
        ax1.set_title(f'Sandpile (Grains: {sim.total_grains})')

        sizes, frequencies = sim.get_avalanche_distribution()
        if sizes:
            line.set_data(sizes, frequencies)
            ax2.set_xlim(0.8, max(sizes) * 2)
            ax2.set_ylim(0.8, max(frequencies) * 2)

        return im, line
    return update


def run_interactive_simulation():
    """Run an animated simulation."""
    sim = SandpileSimulation(size=100, drop_mode='random', seed=42)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    im, line = _setup_animation_axes(ax1, ax2, sim)
    update = _create_update_function(sim, im, ax1, ax2, line)

    FuncAnimation(fig, update, frames=500, interval=50, blit=False)
    plt.tight_layout()
    plt.show()


def _print_simulation_stats(sim):
    """Print simulation statistics."""
    print(f"Total grains dropped: {sim.total_grains}")
    print(f"Total avalanches: {len(sim.avalanche_sizes)}")
    if sim.avalanche_sizes:
        print(f"Largest avalanche: {max(sim.avalanche_sizes)} topples")
        print(f"Average avalanche: {np.mean(sim.avalanche_sizes):.1f} topples")


def _plot_demo_results(sim):
    """Plot and save demonstration results."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    im = ax1.imshow(sim.grid, cmap='YlOrBr', vmin=0, vmax=sim.threshold)
    plt.colorbar(im, ax=ax1, label='Grains')
    ax1.set_title(f'Sandpile State ({sim.size}x{sim.size})')

    sim.plot_power_law(ax2)

    plt.tight_layout()
    plt.savefig('sandpile_results.png', dpi=150)
    plt.show()


def run_quick_demo():
    """Run a quick demonstration and show results."""
    print("Running Sandpile Simulation...")
    print("=" * 50)

    sim = SandpileSimulation(size=100, drop_mode='random', seed=42)
    sim.run(50000)

    _print_simulation_stats(sim)
    _plot_demo_results(sim)

    print("\nResults saved to sandpile_results.png")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--animate':
        run_interactive_simulation()
    else:
        run_quick_demo()
