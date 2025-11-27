"""
GPU-Accelerated 2D Ising Model Simulation
Uses CuPy with checkerboard Metropolis algorithm for massive parallelization.

The checkerboard algorithm divides the lattice into "black" and "white" squares.
Since neighbors of a black square are all white (and vice versa), all black
squares can be updated simultaneously without conflicts.
"""

import cupy as cp
import numpy as np
from collections import deque, defaultdict


class IsingModelGPU:
    """
    GPU-accelerated 2D Ising Model using checkerboard Metropolis algorithm.

    The checkerboard approach allows updating half the spins in parallel,
    achieving significant speedup over sequential updates.
    """

    def __init__(self, size=128, temperature=2.269, seed=None):
        """
        Initialize the GPU-accelerated 2D Ising Model.

        Args:
            size: Grid size (size x size)
            temperature: Temperature relative to critical temp (Tc ≈ 2.269)
            seed: Random seed for reproducibility
        """
        self.size = size
        self.Tc = 2.269
        self.temperature = temperature
        self.beta = 1.0 / temperature  # Inverse temperature

        # Initialize RNG
        if seed is not None:
            cp.random.seed(seed)
        self.seed = seed

        # Initialize grid on GPU with random spins
        self.grid = cp.random.choice(cp.array([-1, 1], dtype=cp.int8),
                                      size=(size, size))

        self.sweeps = 0
        self.magnetization_history = []

        # Pre-compute acceptance probabilities for possible energy changes
        # dE can be -8, -4, 0, 4, 8 (2 * spin * sum_neighbors)
        self._precompute_acceptance_probs()

    def _precompute_acceptance_probs(self):
        """Pre-compute Metropolis acceptance probabilities for all possible dE values."""
        # For Ising model, dE = 2 * s * sum_neighbors
        # s = ±1, sum_neighbors = -4 to +4, so dE = -8, -4, 0, 4, 8
        self.accept_probs = {}
        for dE in [-8, -4, 0, 4, 8]:
            if dE <= 0:
                self.accept_probs[dE] = 1.0
            else:
                self.accept_probs[dE] = float(np.exp(-dE * self.beta))

        # Create lookup array for GPU
        # Index: (dE + 8) // 4 -> 0, 1, 2, 3, 4 for dE = -8, -4, 0, 4, 8
        self.accept_lookup = cp.array([
            self.accept_probs[-8],  # index 0
            self.accept_probs[-4],  # index 1
            self.accept_probs[0],   # index 2
            self.accept_probs[4],   # index 3
            self.accept_probs[8],   # index 4
        ], dtype=cp.float32)

    def set_temperature(self, T):
        """Set temperature (in units of Tc)."""
        self.temperature = T * self.Tc
        self.beta = 1.0 / self.temperature
        self._precompute_acceptance_probs()

    def _checkerboard_sweep(self, color):
        """
        Perform Metropolis updates on all cells of one color (0=black, 1=white).

        This updates half the grid in parallel - the key optimization.
        """
        size = self.size
        grid = self.grid

        # Generate random numbers for all cells
        random_vals = cp.random.random((size, size), dtype=cp.float32)

        # Calculate neighbor sums using periodic boundaries
        neighbors = (
            cp.roll(grid, 1, axis=0) +   # Up
            cp.roll(grid, -1, axis=0) +  # Down
            cp.roll(grid, 1, axis=1) +   # Left
            cp.roll(grid, -1, axis=1)    # Right
        )

        # Calculate energy change: dE = 2 * spin * neighbor_sum
        dE = 2 * grid * neighbors

        # Create checkerboard mask
        # For color=0: (i+j) % 2 == 0 (black squares)
        # For color=1: (i+j) % 2 == 1 (white squares)
        i_idx = cp.arange(size).reshape(-1, 1)
        j_idx = cp.arange(size).reshape(1, -1)
        mask = ((i_idx + j_idx) % 2) == color

        # Calculate acceptance probabilities
        # Map dE to index: (dE + 8) // 4
        dE_index = ((dE + 8) // 4).astype(cp.int32)
        dE_index = cp.clip(dE_index, 0, 4)  # Safety clamp
        accept_prob = self.accept_lookup[dE_index]

        # Accept moves where random < accept_prob, only for this color
        accept = (random_vals < accept_prob) & mask

        # Flip accepted spins
        self.grid = cp.where(accept, -grid, grid)

    def sweep(self, n_sweeps=1):
        """
        Perform n sweeps using checkerboard algorithm.

        Each sweep consists of:
        1. Update all black squares in parallel
        2. Update all white squares in parallel
        """
        for _ in range(n_sweeps):
            self._checkerboard_sweep(0)  # Black squares
            self._checkerboard_sweep(1)  # White squares
        self.sweeps += n_sweeps

    def get_magnetization(self):
        """Calculate average magnetization per spin."""
        return float(cp.mean(self.grid))

    def get_grid_cpu(self):
        """Get grid as numpy array (for visualization/analysis)."""
        return cp.asnumpy(self.grid)

    def find_domains(self):
        """
        Find all connected domains using BFS.
        Note: This runs on CPU as BFS is inherently sequential.
        Returns list of domain sizes.
        """
        grid_cpu = self.get_grid_cpu()
        size = self.size
        visited = np.zeros((size, size), dtype=bool)
        domain_sizes = []

        for i in range(size):
            for j in range(size):
                if not visited[i, j]:
                    spin = grid_cpu[i, j]
                    size_count = 0
                    queue = deque([(i, j)])
                    visited[i, j] = True

                    while queue:
                        x, y = queue.popleft()
                        size_count += 1

                        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                            nx, ny = (x + dx) % size, (y + dy) % size
                            if not visited[nx, ny] and grid_cpu[nx, ny] == spin:
                                visited[nx, ny] = True
                                queue.append((nx, ny))

                    domain_sizes.append(size_count)

        return domain_sizes

    def get_domain_distribution(self, remove_percolating=True):
        """
        Get frequency distribution of domain sizes.
        """
        domain_sizes = self.find_domains()

        if remove_percolating and len(domain_sizes) > 2:
            domain_sizes = sorted(domain_sizes)[:-2]

        counts = defaultdict(int)
        for size in domain_sizes:
            counts[size] += 1

        sizes = sorted(counts.keys())
        frequencies = [counts[s] for s in sizes]

        return sizes, frequencies


def run_quick_test():
    """Quick test to verify GPU implementation works."""
    print("Ising Model GPU - Quick Test")
    print("=" * 50)

    # Create model
    model = IsingModelGPU(size=128, temperature=2.269, seed=42)
    print(f"Grid size: {model.size}x{model.size}")
    print(f"Temperature: {model.temperature:.3f}")
    print(f"Initial magnetization: {model.get_magnetization():.4f}")

    # Run sweeps
    import time
    start = time.perf_counter()
    model.sweep(100)
    cp.cuda.Stream.null.synchronize()
    elapsed = time.perf_counter() - start

    print(f"\n100 sweeps completed in {elapsed*1000:.2f} ms")
    print(f"Final magnetization: {model.get_magnetization():.4f}")
    print(f"Sweeps/second: {100/elapsed:.0f}")


if __name__ == '__main__':
    run_quick_test()
