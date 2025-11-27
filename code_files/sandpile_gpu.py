"""
GPU-Accelerated Sandpile Avalanche Simulation
Uses CuPy for GPU array operations.

The avalanche processing loop still exists (we can't know when to stop),
but each iteration runs entirely on the GPU.
"""

import cupy as cp
import numpy as np
from collections import defaultdict


class SandpileSimulationGPU:
    """
    GPU-accelerated sandpile simulation using CuPy.

    The avalanche processing uses GPU-accelerated array operations,
    achieving significant speedup especially for larger grids.
    """

    def __init__(self, size=50, threshold=4, drop_mode='random', seed=None):
        """
        Initialize the GPU-accelerated sandpile simulation.

        Args:
            size: Grid size (size x size)
            threshold: Number of grains that triggers toppling (default 4)
            drop_mode: 'center' or 'random' drop location
            seed: Random seed for reproducibility
        """
        self.size = size
        self.threshold = threshold
        self.drop_mode = drop_mode

        # Initialize grid on GPU
        self.grid = cp.zeros((size, size), dtype=cp.int32)

        # Random number generator
        if seed is not None:
            cp.random.seed(seed)
        self.seed = seed

        # Statistics
        self.total_grains = 0
        self.avalanche_sizes = []

    def _get_drop_position(self):
        """Get the position where the next grain will be dropped."""
        if self.drop_mode == 'center':
            return self.size // 2, self.size // 2
        # Random position
        return (int(cp.random.randint(0, self.size)),
                int(cp.random.randint(0, self.size)))

    def _distribute_to_neighbors(self, topple_mask):
        """Distribute grains from toppled cells to their neighbors (GPU)."""
        self.grid[1:, :] += topple_mask[:-1, :]   # Up
        self.grid[:-1, :] += topple_mask[1:, :]   # Down
        self.grid[:, 1:] += topple_mask[:, :-1]   # Left
        self.grid[:, :-1] += topple_mask[:, 1:]   # Right

    def drop_grain(self):
        """Drop a single grain of sand and process any resulting avalanche."""
        x, y = self._get_drop_position()
        self.grid[x, y] += 1
        self.total_grains += 1

        avalanche_size = self.process_avalanche()
        if avalanche_size > 0:
            self.avalanche_sizes.append(avalanche_size)

        return avalanche_size

    def process_avalanche(self):
        """Process all toppling until the grid is stable (GPU-accelerated)."""
        total_topples = 0

        while True:
            unstable = self.grid >= self.threshold
            if not cp.any(unstable):
                break

            topple_count = int(cp.sum(unstable))
            total_topples += topple_count

            topple_mask = unstable.astype(cp.int32)
            self.grid -= self.threshold * topple_mask
            self._distribute_to_neighbors(topple_mask)

        return total_topples

    def drop_grains_batch(self, n_grains):
        """
        Drop multiple grains and process avalanches.

        For random mode, this generates all positions at once on GPU.
        This is more efficient than dropping one at a time.
        """
        if self.drop_mode == 'center':
            # All grains go to center
            center = self.size // 2
            self.grid[center, center] += n_grains
            self.total_grains += n_grains
            avalanche_size = self.process_avalanche()
            if avalanche_size > 0:
                self.avalanche_sizes.append(avalanche_size)
            return avalanche_size

        # Random mode: generate all positions at once
        positions = cp.random.randint(0, self.size, size=(n_grains, 2))

        # Use bincount to count grains at each position efficiently
        flat_indices = positions[:, 0] * self.size + positions[:, 1]
        counts = cp.bincount(flat_indices, minlength=self.size * self.size)
        self.grid += counts.reshape(self.size, self.size).astype(cp.int32)
        self.total_grains += n_grains

        avalanche_size = self.process_avalanche()
        if avalanche_size > 0:
            self.avalanche_sizes.append(avalanche_size)

        return avalanche_size

    def run(self, num_drops):
        """Run the simulation for a number of grain drops."""
        for _ in range(num_drops):
            self.drop_grain()

    def run_batch(self, num_drops, batch_size=1000):
        """
        Run simulation with batched grain drops.

        More efficient for large numbers of drops as it reduces
        Python loop overhead and maximizes GPU utilization.
        """
        remaining = num_drops
        while remaining > 0:
            batch = min(batch_size, remaining)
            self.drop_grains_batch(batch)
            remaining -= batch

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

    def get_grid_cpu(self):
        """Get grid as numpy array (for visualization/analysis)."""
        return cp.asnumpy(self.grid)


def run_quick_test():
    """Quick test to verify GPU implementation works."""
    print("Sandpile GPU - Quick Test")
    print("=" * 50)

    import time

    # Create simulation
    sim = SandpileSimulationGPU(size=100, drop_mode='random', seed=42)
    print(f"Grid size: {sim.size}x{sim.size}")

    # Run simulation
    n_drops = 50000
    start = time.perf_counter()
    sim.run(n_drops)
    cp.cuda.Stream.null.synchronize()
    elapsed = time.perf_counter() - start

    print(f"\n{n_drops} drops completed in {elapsed*1000:.2f} ms")
    print(f"Drops/second: {n_drops/elapsed:.0f}")
    print(f"Total avalanches: {len(sim.avalanche_sizes)}")
    if sim.avalanche_sizes:
        print(f"Largest avalanche: {max(sim.avalanche_sizes)}")


if __name__ == '__main__':
    run_quick_test()
