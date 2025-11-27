"""
GPU-Accelerated Forest Fire Simulation
Uses CuPy for GPU array operations with hybrid CPU/GPU approach.

GPU handles: tree growth, clearing burning cells, random generation
CPU handles: BFS fire spread (inherently sequential)

NOTE: The Forest Fire model shows LIMITED GPU speedup (~1.1x at 400x400)
because BFS fire spread is inherently sequential and requires GPU-CPU
data transfers. For most use cases, the CPU version may be comparable.
GPU becomes beneficial only at very large grid sizes (500x500+).
"""

import cupy as cp
import numpy as np
from collections import deque, defaultdict

# Cell states
EMPTY = 0
TREE = 1
BURNING = 2


class ForestFireGPU:
    """
    GPU-accelerated Forest Fire simulation using hybrid approach.

    Tree growth and cell clearing run on GPU, while fire spread
    uses CPU-based BFS (graph traversal is inherently sequential).
    """

    def __init__(self, size=256, tree_growth_prob=0.01, lightning_prob=None, seed=None):
        """
        Initialize the GPU-accelerated Forest Fire simulation.

        Args:
            size: Grid size (size x size)
            tree_growth_prob: Probability p that an empty cell grows a tree
            lightning_prob: Probability f of lightning strike (default: p/10)
            seed: Random seed for reproducibility
        """
        self.size = size
        self.p = tree_growth_prob
        self.f = lightning_prob if lightning_prob is not None else tree_growth_prob / 10

        # Initialize RNG
        if seed is not None:
            cp.random.seed(seed)
            np.random.seed(seed)  # For CPU-side BFS random selection
        self.seed = seed

        # Initialize grid on GPU
        self.grid = cp.zeros((size, size), dtype=cp.int32)

        self.timestep = 0
        self.fire_sizes = []
        self.tree_counts = []

        # Pre-allocate random arrays for efficiency
        self._random_buffer = None
        self._lightning_buffer = None

    def count_trees(self):
        """Count the number of trees (GPU-accelerated)."""
        return int(cp.sum(self.grid == TREE))

    def tree_density(self):
        """Calculate tree density."""
        return self.count_trees() / (self.size * self.size)

    def _clear_burning_cells(self):
        """Convert burning cells to empty (GPU)."""
        self.grid = cp.where(self.grid == BURNING, EMPTY, self.grid)

    def _grow_trees(self):
        """Grow new trees on empty cells (GPU-accelerated)."""
        # Generate random values on GPU
        random_vals = cp.random.random((self.size, self.size), dtype=cp.float32)

        # Find empty cells and apply growth probability
        empty_mask = self.grid == EMPTY
        grow_mask = random_vals < self.p

        # Grow trees where both conditions are met
        self.grid = cp.where(empty_mask & grow_mask, TREE, self.grid)

    def _get_tree_positions_gpu(self):
        """Get tree positions efficiently using GPU."""
        return cp.argwhere(self.grid == TREE)

    def _spread_fire_cpu(self, start_i, start_j, grid_cpu):
        """
        Spread fire from a starting point using BFS (CPU).

        This must run on CPU as BFS is inherently sequential.
        Returns trees burned.
        """
        if grid_cpu[start_i, start_j] != TREE:
            return 0, grid_cpu

        burned = 0
        queue = deque([(start_i, start_j)])
        grid_cpu[start_i, start_j] = BURNING

        size = self.size
        while queue:
            i, j = queue.popleft()
            burned += 1

            # Moore neighborhood (8 neighbors)
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < size and 0 <= nj < size:
                        if grid_cpu[ni, nj] == TREE:
                            grid_cpu[ni, nj] = BURNING
                            queue.append((ni, nj))

        return burned, grid_cpu

    def _try_lightning_strike(self):
        """Attempt a lightning strike on trees."""
        # Get tree positions on GPU
        tree_positions = self._get_tree_positions_gpu()

        if len(tree_positions) == 0:
            return

        # Transfer to CPU for BFS fire spread
        tree_positions_cpu = cp.asnumpy(tree_positions)
        grid_cpu = cp.asnumpy(self.grid)

        # Try lightning on each tree with probability f
        for pos in tree_positions_cpu:
            i, j = pos[0], pos[1]
            if np.random.random() < self.f:
                fire_size, grid_cpu = self._spread_fire_cpu(i, j, grid_cpu)
                if fire_size > 0:
                    self.fire_sizes.append(fire_size)
                break

        # Transfer back to GPU
        self.grid = cp.asarray(grid_cpu)

    def step(self):
        """Perform one simulation step."""
        self.timestep += 1
        self._clear_burning_cells()
        self._grow_trees()
        self._try_lightning_strike()
        self.tree_counts.append(self.count_trees())

    def run(self, num_steps, progress_interval=1000):
        """Run the simulation for a number of steps."""
        for step_num in range(num_steps):
            self.step()
            if progress_interval and (step_num + 1) % progress_interval == 0:
                print(f"Step {step_num + 1}/{num_steps}, Trees: {self.count_trees()}, Fires: {len(self.fire_sizes)}")

    def run_batch(self, num_steps, batch_size=100):
        """
        Run simulation with batched steps.

        Batches multiple tree growth steps before checking lightning,
        which reduces GPU-CPU synchronization overhead.
        """
        remaining = num_steps
        while remaining > 0:
            batch = min(batch_size, remaining)

            # Batch tree growth on GPU
            for _ in range(batch):
                self.timestep += 1
                self._clear_burning_cells()
                self._grow_trees()

            # Single lightning check per batch
            self._try_lightning_strike()
            self.tree_counts.append(self.count_trees())

            remaining -= batch

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

    def get_grid_cpu(self):
        """Get grid as numpy array (for visualization/analysis)."""
        return cp.asnumpy(self.grid)


def run_quick_test():
    """Quick test to verify GPU implementation works."""
    print("Forest Fire GPU - Quick Test")
    print("=" * 50)

    import time

    # Create simulation
    sim = ForestFireGPU(size=200, tree_growth_prob=0.01, seed=42)
    print(f"Grid size: {sim.size}x{sim.size}")
    print(f"Growth prob: {sim.p}, Lightning prob: {sim.f}")

    # Run simulation
    n_steps = 5000
    start = time.perf_counter()
    sim.run(n_steps, progress_interval=1000)
    cp.cuda.Stream.null.synchronize()
    elapsed = time.perf_counter() - start

    print(f"\n{n_steps} steps completed in {elapsed:.2f} s")
    print(f"Steps/second: {n_steps/elapsed:.0f}")
    print(f"Tree density: {sim.tree_density():.1%}")
    print(f"Total fires: {len(sim.fire_sizes)}")
    if sim.fire_sizes:
        print(f"Largest fire: {max(sim.fire_sizes)}")


if __name__ == '__main__':
    run_quick_test()
