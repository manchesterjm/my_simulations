"""
2D Ising Model Simulation
Demonstrates magnetic phase transitions and criticality at the Curie temperature.

Each cell represents a magnetic spin (+1 or -1). At low temperatures, spins align
into large domains. At high temperatures, spins are random. At the critical
temperature (Tc ≈ 2.269), the system shows power-law domain size distributions.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap
from collections import deque, defaultdict

class IsingModel:
    def __init__(self, size=128, temperature=2.269, seed=None):
        """
        Initialize the 2D Ising Model.

        Args:
            size: Grid size (size x size)
            temperature: Temperature relative to critical temp (T/Tc where Tc ≈ 2.269)
            seed: Random seed for reproducibility
        """
        self.size = size
        self.Tc = 2.269  # Critical temperature for 2D Ising model
        self.temperature = temperature
        self.rng = np.random.default_rng(seed)

        # Initialize random spins (+1 or -1)
        self.grid = self.rng.choice([-1, 1], size=(size, size))

        # Statistics
        self.sweeps = 0
        self.magnetization_history = []

    def set_temperature(self, T):
        """Set temperature (in units of Tc)."""
        self.temperature = T * self.Tc

    def get_energy_change(self, i, j):
        """Calculate energy change if spin at (i,j) were flipped."""
        spin = self.grid[i, j]
        # Sum of neighbors (periodic boundary conditions)
        neighbors = (
            self.grid[(i + 1) % self.size, j] +
            self.grid[(i - 1) % self.size, j] +
            self.grid[i, (j + 1) % self.size] +
            self.grid[i, (j - 1) % self.size]
        )
        # Energy change = 2 * spin * sum_of_neighbors
        return 2 * spin * neighbors

    def metropolis_step(self):
        """Perform one Metropolis Monte Carlo step (single spin flip attempt)."""
        i = self.rng.integers(0, self.size)
        j = self.rng.integers(0, self.size)

        dE = self.get_energy_change(i, j)

        # Accept or reject the flip
        if dE <= 0:
            self.grid[i, j] *= -1
        elif self.rng.random() < np.exp(-dE / self.temperature):
            self.grid[i, j] *= -1

    def sweep(self, n_sweeps=1):
        """Perform n sweeps (each sweep = size^2 flip attempts)."""
        n_steps = n_sweeps * self.size * self.size
        for _ in range(n_steps):
            self.metropolis_step()
        self.sweeps += n_sweeps

    def get_magnetization(self):
        """Calculate average magnetization per spin."""
        return np.mean(self.grid)

    def find_domains(self):
        """
        Find all connected domains using BFS.
        Returns list of domain sizes.
        """
        visited = np.zeros((self.size, self.size), dtype=bool)
        domain_sizes = []

        for i in range(self.size):
            for j in range(self.size):
                if not visited[i, j]:
                    # BFS to find connected domain
                    spin = self.grid[i, j]
                    size = 0
                    queue = deque([(i, j)])
                    visited[i, j] = True

                    while queue:
                        x, y = queue.popleft()
                        size += 1

                        # Check neighbors
                        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                            nx, ny = (x + dx) % self.size, (y + dy) % self.size
                            if not visited[nx, ny] and self.grid[nx, ny] == spin:
                                visited[nx, ny] = True
                                queue.append((nx, ny))

                    domain_sizes.append(size)

        return domain_sizes

    def get_domain_distribution(self, remove_percolating=True):
        """
        Get frequency distribution of domain sizes.
        At critical temperature, optionally remove the two largest (percolating) domains.
        """
        domain_sizes = self.find_domains()

        if remove_percolating and len(domain_sizes) > 2:
            # Remove two largest domains (they percolate through the system)
            domain_sizes = sorted(domain_sizes)[:-2]

        counts = defaultdict(int)
        for size in domain_sizes:
            counts[size] += 1

        sizes = sorted(counts.keys())
        frequencies = [counts[s] for s in sizes]

        return sizes, frequencies

    def plot_state(self, ax=None):
        """Plot the current spin configuration."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))

        cmap = ListedColormap(['#3498db', '#e74c3c'])  # Blue for -1, Red for +1
        im = ax.imshow(self.grid, cmap=cmap, vmin=-1, vmax=1)

        T_ratio = self.temperature / self.Tc
        mag = self.get_magnetization()
        ax.set_title(f'Ising Model (T/Tc = {T_ratio:.3f}, M = {mag:.3f})')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')

        return im

    def plot_domain_distribution(self, ax=None, remove_percolating=True):
        """Plot domain size distribution on log-log scale."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))

        sizes, frequencies = self.get_domain_distribution(remove_percolating)

        if sizes:
            ax.loglog(sizes, frequencies, 'o', markersize=4, alpha=0.7, color='purple')
            ax.set_xlabel('Domain Size (number of spins)')
            ax.set_ylabel('Frequency')
            ax.set_title('Domain Size Distribution (Log-Log)')
            ax.grid(True, alpha=0.3)

        return ax


def run_temperature_comparison():
    """Show the system at different temperatures."""
    print("2D Ising Model - Temperature Comparison")
    print("=" * 50)

    temperatures = [0.5, 1.0, 2.269, 4.0]  # T values (not T/Tc)
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))

    for i, T in enumerate(temperatures):
        print(f"Simulating T = {T:.3f} (T/Tc = {T/2.269:.3f})...")

        model = IsingModel(size=128, temperature=T, seed=42)
        # Equilibrate
        model.sweep(100)

        # Top row: spin configuration
        model.plot_state(axes[0, i])

        # Bottom row: domain distribution
        model.plot_domain_distribution(axes[1, i], remove_percolating=(abs(T - 2.269) < 0.1))

    plt.tight_layout()
    plt.savefig('ising_temperature_comparison.png', dpi=150)
    plt.show()

    print("\nResults saved to ising_temperature_comparison.png")


def run_critical_animation():
    """Animate the system at the critical temperature."""
    print("Running Ising Model at Critical Temperature...")

    model = IsingModel(size=128, temperature=2.269, seed=42)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Initial spin plot
    cmap = ListedColormap(['#3498db', '#e74c3c'])
    im = ax1.imshow(model.grid, cmap=cmap, vmin=-1, vmax=1)
    ax1.set_title('Spin Configuration')

    # Domain distribution plot
    line, = ax2.loglog([], [], 'o', markersize=4, alpha=0.7, color='purple')
    ax2.set_xlabel('Domain Size')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Domain Size Distribution')
    ax2.set_xlim(1, 10000)
    ax2.set_ylim(1, 1000)
    ax2.grid(True, alpha=0.3)

    def update(frame):
        model.sweep(5)

        im.set_array(model.grid)
        ax1.set_title(f'T/Tc = 1.0, Sweep {model.sweeps}')

        sizes, frequencies = model.get_domain_distribution(remove_percolating=True)
        if sizes:
            line.set_data(sizes, frequencies)
            ax2.set_xlim(0.8, max(sizes) * 2)
            ax2.set_ylim(0.8, max(max(frequencies), 10) * 2)

        return im, line

    ani = FuncAnimation(fig, update, frames=200, interval=100, blit=False)
    plt.tight_layout()
    plt.show()


def run_quick_demo():
    """Quick demonstration at critical temperature."""
    print("2D Ising Model at Critical Temperature")
    print("=" * 50)

    model = IsingModel(size=128, temperature=2.269, seed=42)

    print("Equilibrating...")
    model.sweep(200)

    print(f"Sweeps completed: {model.sweeps}")
    print(f"Magnetization: {model.get_magnetization():.4f}")

    domain_sizes = model.find_domains()
    print(f"Number of domains: {len(domain_sizes)}")
    print(f"Largest domain: {max(domain_sizes)} spins")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    model.plot_state(ax1)
    model.plot_domain_distribution(ax2)

    plt.tight_layout()
    plt.savefig('ising_critical.png', dpi=150)
    plt.show()

    print("\nResults saved to ising_critical.png")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--animate':
        run_critical_animation()
    elif len(sys.argv) > 1 and sys.argv[1] == '--compare':
        run_temperature_comparison()
    else:
        run_quick_demo()
