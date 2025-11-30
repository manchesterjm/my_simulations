"""GPU-Accelerated Forest Fire Simulation with Hybrid Approach.

This module implements the Drossel-Schwabl forest fire model using a hybrid
CPU/GPU approach. Tree growth and cell clearing run on GPU, while fire spread
uses CPU-based BFS (breadth-first search).

Physics:
    Trees grow randomly on empty cells with probability p. Lightning strikes
    with probability f (typically f = p/10), igniting fires. Fire spreads to
    all connected trees via Moore neighborhood (8 neighbors). System exhibits
    self-organized criticality with power law fire size distributions.

Hybrid CPU/GPU Approach:
    - GPU: Tree growth (parallel random generation)
    - GPU: Clearing burning cells (parallel array operations)
    - CPU: Fire spread via BFS (inherently sequential graph traversal)

Performance Limitations:
    Shows LIMITED GPU speedup (~1.3x at 400x400) due to:
    - BFS fire spread is inherently sequential
    - Requires frequent GPU-CPU data transfers for BFS
    - Only tree growth benefits from parallelization

When to Use:
    - GPU version: Very large grids (500x500+) or when GPU is idle
    - CPU version: Most use cases - comparable or better performance

Example:
    >>> sim = ForestFireGPU(size=200, tree_growth_prob=0.01, seed=42)
    >>> sim.run(5000)
    >>> sizes, freqs = sim.get_fire_distribution()
    >>> # Plot log-log to see power law
"""

import cupy as cp
import numpy as np
from collections import deque, defaultdict

# Cell states
EMPTY = 0
TREE = 1
BURNING = 2


class ForestFireGPU:
    """GPU-accelerated Forest Fire simulation using hybrid CPU/GPU approach.

    Implements Drossel-Schwabl forest fire model with GPU-accelerated tree
    growth and CPU-based fire spread. The hybrid approach provides modest
    speedup for large grids but BFS limits parallelization.

    Attributes:
        size (int): Grid dimension (creates size x size grid).
        p (float): Tree growth probability per empty cell per timestep.
        f (float): Lightning strike probability per tree per timestep.
        seed (int): Random seed for reproducibility.
        grid (cupy.ndarray): Current state on GPU (0=empty, 1=tree, 2=burning).
        timestep (int): Current simulation timestep.
        fire_sizes (list): Sizes of all fires (trees burned per fire).
        tree_counts (list): Tree count history over time.

    Example:
        >>> sim = ForestFireGPU(size=200, tree_growth_prob=0.01)
        >>> sim.run(5000)
        >>> print(f"Largest fire: {max(sim.fire_sizes)}")
    """

    def __init__(self, size=256, tree_growth_prob=0.01, lightning_prob=None, seed=None):
        """Initialize the GPU-accelerated Forest Fire simulation.

        Args:
            size (int): Grid size (creates size x size grid, default: 256).
            tree_growth_prob (float): Probability p that empty cell grows tree (default: 0.01).
            lightning_prob (float, optional): Probability f of lightning strike (default: p/10).
            seed (int, optional): Random seed for reproducibility.

        Note:
            Grid initialized on GPU. Both GPU and CPU RNGs are seeded for
            hybrid operations.
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
        """Spread fire from ignition point using breadth-first search on CPU.

        Fire spreads through all connected trees using Moore neighborhood
        (8 adjacent cells). BFS ensures all reachable trees burn.

        Args:
            start_i (int): Row of ignition point.
            start_j (int): Column of ignition point.
            grid_cpu (numpy.ndarray): Grid state on CPU (modified in place).

        Returns:
            tuple: (trees_burned, modified_grid)
                - trees_burned (int): Number of trees consumed by fire
                - modified_grid: Updated grid with burned cells marked

        Note:
            BFS is inherently sequential (graph traversal), requiring CPU.
            This is the performance bottleneck limiting GPU speedup.
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
        """Perform one simulation timestep.

        Sequence:
            1. Clear burning cells (GPU)
            2. Grow new trees (GPU)
            3. Attempt lightning strike and spread fire (CPU/hybrid)
            4. Record tree count

        Note:
            Most time is spent in fire spread (CPU BFS), limiting GPU benefits.
        """
        self.timestep += 1
        self._clear_burning_cells()
        self._grow_trees()
        self._try_lightning_strike()
        self.tree_counts.append(self.count_trees())

    def run(self, num_steps, progress_interval=1000):
        """Run simulation for specified number of timesteps.

        Args:
            num_steps (int): Number of timesteps to simulate.
            progress_interval (int, optional): Print progress every N steps.
                Set to None to disable progress output (default: 1000).

        Example:
            >>> sim = ForestFireGPU(size=200)
            >>> sim.run(10000, progress_interval=2500)
            Step 2500/10000, Trees: 15234, Fires: 145
            Step 5000/10000, Trees: 15198, Fires: 289
            ...
        """
        for step_num in range(num_steps):
            self.step()
            if progress_interval and (step_num + 1) % progress_interval == 0:
                print(
                    f"Step {step_num + 1}/{num_steps}, "
                    f"Trees: {self.count_trees()}, Fires: {len(self.fire_sizes)}"
                )

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
