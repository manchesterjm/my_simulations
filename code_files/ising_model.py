"""2D Ising Model Simulation - Statistical Physics and Phase Transitions.

This module implements the 2D Ising model, a fundamental model in statistical physics
that demonstrates magnetic phase transitions, critical phenomena, and self-organized
criticality. The Ising model was originally proposed to study ferromagnetism but has
applications across physics, from magnetism to lattice gases to neural networks.

Physical Model:
    The system consists of a 2D lattice of magnetic spins, each with value +1 (spin up)
    or -1 (spin down). Neighboring spins interact via exchange coupling energy J.

    Hamiltonian: H = -J * Σ(s_i * s_j) where the sum is over nearest neighbors.

    The system energy favors aligned neighbors (ferromagnetic coupling J > 0).

Phase Transitions:
    The model exhibits a second-order phase transition at the critical temperature
    Tc ≈ 2.269 J/k_B (exact solution by Onsager, 1944):

    - T < Tc (Ordered phase): Spins spontaneously align into large domains of mostly
      +1 or mostly -1 spins. The system exhibits spontaneous magnetization and
      long-range order. Domain boundaries are sharp.

    - T = Tc (Critical point): The system exhibits scale-free behavior with power-law
      distributions of domain sizes. Domains exist at all scales from single spins
      to system-spanning clusters. This is an example of self-organized criticality.
      The correlation length diverges: ξ ~ |T - Tc|^(-ν) with ν ≈ 1.

    - T > Tc (Disordered phase): Thermal fluctuations dominate. Spins are randomly
      oriented with no long-range order. Magnetization approaches zero. Only small
      transient domains form.

Metropolis Algorithm:
    The simulation uses the Metropolis-Hastings Monte Carlo algorithm to sample
    equilibrium configurations at temperature T:

    1. Randomly select a spin at position (i, j)
    2. Calculate energy change ΔE if the spin were flipped
    3. Accept the flip with probability:
       - P = 1 if ΔE ≤ 0 (energy decreases)
       - P = exp(-ΔE/kT) if ΔE > 0 (Boltzmann factor)

    This satisfies detailed balance and samples the Boltzmann distribution.
    After sufficient sweeps, the system reaches thermal equilibrium.

Critical Phenomena:
    At T = Tc, the system exhibits universal critical behavior:
    - Power-law domain size distribution: P(s) ~ s^(-τ) with τ ≈ 2.05
    - Diverging correlation length and susceptibility
    - Scale invariance and fractal domain boundaries
    - Critical slowing down (long equilibration times)

Observables:
    - Magnetization: M = <s_i> (order parameter, zero above Tc)
    - Domain sizes: Connected regions of same-spin sites
    - Energy and specific heat

GPU Acceleration:
    Supports GPU acceleration via CuPy using checkerboard decomposition for
    parallel Metropolis updates (spins on opposite sublattices don't interact).
    Speedup ~40x for large lattices.

References:
    - Onsager, L. (1944). "Crystal statistics. I. A two-dimensional model with an
      order-disorder transition." Physical Review, 65(3-4), 117.
    - Newman, M. E. J., & Barkema, G. T. (1999). Monte Carlo Methods in Statistical
      Physics. Oxford University Press.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap
from collections import deque, defaultdict

# Check GPU availability
try:
    from gpu_utils import cuda_available
    GPU_AVAILABLE = cuda_available()
except ImportError:
    GPU_AVAILABLE = False


def create_ising_model(size=128, temperature=2.269, seed=None, backend='auto'):
    """
    Factory function to create an Ising Model with the specified backend.

    Args:
        size: Grid size (size x size)
        temperature: Temperature relative to critical temp (Tc ≈ 2.269)
        seed: Random seed for reproducibility
        backend: 'auto', 'gpu', or 'cpu'
            - 'auto': Use GPU if available, else CPU
            - 'gpu': Force GPU (raises error if unavailable)
            - 'cpu': Force CPU

    Returns:
        IsingModel (CPU) or IsingModelGPU instance
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
        from ising_gpu import IsingModelGPU
        return IsingModelGPU(size=size, temperature=temperature, seed=seed)
    else:
        return IsingModel(size=size, temperature=temperature, seed=seed)


class IsingModel:
    """2D Ising Model with Metropolis Monte Carlo dynamics.

    This class implements the CPU-based 2D Ising model on a square lattice with
    periodic boundary conditions (toroidal topology). Spins evolve via single-spin
    Metropolis updates toward thermal equilibrium at temperature T.

    The model demonstrates:
        - Spontaneous magnetization below Tc (ferromagnetic phase)
        - Critical behavior at Tc ≈ 2.269 with power-law distributions
        - Paramagnetic disorder above Tc

    Attributes:
        size (int): Linear dimension of square lattice (total spins = size²).
        Tc (float): Critical temperature Tc = 2/ln(1+√2) ≈ 2.269 in units J/k_B.
        temperature (float): Current simulation temperature.
        rng (np.random.Generator): Random number generator for reproducibility.
        grid (np.ndarray): 2D array of spins with values +1 or -1.
        sweeps (int): Number of complete lattice sweeps performed.
        magnetization_history (list): Historical magnetization values.
    """

    def __init__(self, size=128, temperature=2.269, seed=None):
        """Initialize the 2D Ising Model with random spin configuration.

        Creates a square lattice with randomly initialized spins (+1 or -1 with
        equal probability). The initial state is typically a high-energy, disordered
        configuration that equilibrates during simulation.

        Args:
            size (int): Grid size (size x size). Larger sizes show clearer critical
                behavior but require more sweeps to equilibrate. Default 128.
            temperature (float): Absolute temperature in units where J/k_B = 1.
                Tc ≈ 2.269. Use temperature < Tc for ordered phase, = Tc for
                critical point, > Tc for disordered phase. Default 2.269.
            seed (int, optional): Random seed for reproducibility. If None, uses
                non-deterministic randomness. Default None.

        Example:
            >>> model = IsingModel(size=64, temperature=2.269, seed=42)
            >>> model.sweep(100)  # Equilibrate
            >>> sizes, freqs = model.get_domain_distribution()
        """
        self.size = size
        # Exact critical temperature from Onsager's solution: Tc = 2/ln(1+√2)
        self.Tc = 2.269
        self.temperature = temperature
        self.rng = np.random.default_rng(seed)

        # Initialize with random spins (infinite temperature initial condition)
        self.grid = self.rng.choice([-1, 1], size=(size, size))
        self.sweeps = 0
        self.magnetization_history = []

    def set_temperature(self, T):
        """Set simulation temperature as multiple of critical temperature.

        Convenience method for setting temperature relative to Tc. For example,
        set_temperature(0.5) sets T = 0.5 * Tc (ordered phase).

        Args:
            T (float): Temperature as ratio T/Tc. Use T < 1 for ordered phase,
                T = 1 for critical point, T > 1 for disordered phase.
        """
        self.temperature = T * self.Tc

    def _get_neighbor_sum(self, i, j):
        """Calculate sum of four nearest-neighbor spins with periodic boundaries.

        Uses modulo arithmetic to implement periodic (toroidal) boundary conditions,
        eliminating edge effects. Each spin has exactly 4 neighbors.

        Args:
            i (int): Row index of central spin.
            j (int): Column index of central spin.

        Returns:
            int: Sum of neighboring spins, ranging from -4 to +4.
                +4: all neighbors aligned up
                -4: all neighbors aligned down
                 0: balanced or mixed neighbors
        """
        return (
            self.grid[(i + 1) % self.size, j] +      # Right neighbor
            self.grid[(i - 1) % self.size, j] +      # Left neighbor
            self.grid[i, (j + 1) % self.size] +      # Below neighbor
            self.grid[i, (j - 1) % self.size]        # Above neighbor
        )

    def _should_flip(self, dE):
        """Determine if spin flip should be accepted via Metropolis criterion.

        Implements the Metropolis acceptance rule for Monte Carlo sampling:
        - Always accept energy-lowering moves (ΔE ≤ 0)
        - Accept energy-raising moves with probability exp(-ΔE/kT) (Boltzmann factor)

        This ensures detailed balance and samples the canonical ensemble at
        temperature T. The Boltzmann factor allows thermal fluctuations to
        occasionally flip aligned spins, preventing the system from getting
        stuck in local energy minima.

        Args:
            dE (float): Energy change ΔE = E_new - E_old for proposed spin flip.

        Returns:
            bool: True if flip should be accepted, False otherwise.
        """
        # Energy-lowering moves always accepted (downhill in energy landscape)
        if dE <= 0:
            return True
        # Energy-raising moves accepted with Boltzmann probability (uphill allowed)
        return self.rng.random() < np.exp(-dE / self.temperature)

    def get_energy_change(self, i, j):
        """Calculate energy change if spin at (i,j) were flipped.

        For the Ising Hamiltonian H = -J Σ s_i s_j, flipping spin s_i changes
        the interaction energy with its four neighbors. Since we flip s_i → -s_i,
        the energy change is:

            ΔE = -(-s_i → s_i) * Σ s_neighbors = 2 * s_i * Σ s_neighbors

        This is computed without actually flipping the spin, allowing us to
        evaluate the Metropolis criterion before modifying the state.

        Args:
            i (int): Row index of spin to potentially flip.
            j (int): Column index of spin to potentially flip.

        Returns:
            float: Energy change ΔE if this spin were flipped. Positive ΔE means
                energy increases (unfavorable), negative means energy decreases
                (favorable for alignment).
        """
        return 2 * self.grid[i, j] * self._get_neighbor_sum(i, j)

    def metropolis_step(self):
        """Perform one Metropolis Monte Carlo step (single spin flip attempt).

        The Metropolis algorithm is the core dynamics engine:
        1. Randomly select one spin from the lattice
        2. Calculate energy change ΔE if this spin were flipped
        3. Accept/reject flip based on Metropolis criterion:
           - Accept if ΔE ≤ 0 (energy decreases)
           - Accept with probability exp(-ΔE/kT) if ΔE > 0 (Boltzmann factor)
        4. If accepted, flip the spin: s → -s

        Multiple steps are needed to equilibrate the system. One "sweep" is
        size² steps, attempting to flip each spin once on average.

        Note: This is a serial algorithm. For GPU acceleration, use IsingModelGPU
        which implements parallel checkerboard updates.
        """
        # Randomly select a spin position
        i = self.rng.integers(0, self.size)
        j = self.rng.integers(0, self.size)

        # Calculate energy change from flipping this spin
        dE = self.get_energy_change(i, j)

        # Apply Metropolis acceptance criterion
        if self._should_flip(dE):
            self.grid[i, j] *= -1  # Flip: +1 → -1 or -1 → +1

    def sweep(self, n_sweeps=1):
        """Perform n Monte Carlo sweeps to evolve the system.

        One sweep consists of size² Metropolis steps, meaning each spin is
        selected for a flip attempt once on average. Multiple sweeps are needed
        to reach thermal equilibrium and decorrelate measurements.

        Equilibration time depends on temperature:
        - Near Tc: ~100-200 sweeps (critical slowing down)
        - Far from Tc: ~50-100 sweeps usually sufficient

        Args:
            n_sweeps (int): Number of complete lattice sweeps to perform.
                Default 1.

        Note: After calling this method, check observables like magnetization
        to verify equilibration (should plateau after initial transient).
        """
        n_steps = n_sweeps * self.size * self.size
        for _ in range(n_steps):
            self.metropolis_step()
        self.sweeps += n_sweeps

    def get_magnetization(self):
        """Calculate average magnetization per spin (order parameter).

        Magnetization M = (1/N) Σ s_i is the order parameter for the
        ferromagnetic phase transition:
        - T < Tc: |M| ≈ 1 (spontaneous magnetization, ordered phase)
        - T = Tc: M fluctuates widely, <M²> ~ 1 but <M> ≈ 0
        - T > Tc: M ≈ 0 (paramagnetic phase, no long-range order)

        Returns:
            float: Average magnetization in range [-1, 1].
                +1: all spins up
                -1: all spins down
                 0: equal mix or random spins
        """
        return np.mean(self.grid)

    def _bfs_domain_size(self, start_i, start_j, visited):
        """Find size of spin domain using breadth-first search.

        A domain is a maximal connected region of identically-oriented spins.
        Uses BFS to traverse all spins connected to the starting spin through
        nearest-neighbor bonds. Periodic boundaries are respected.

        Args:
            start_i (int): Starting row index.
            start_j (int): Starting column index.
            visited (np.ndarray): Boolean array tracking visited spins (modified in-place).

        Returns:
            int: Number of spins in this connected domain.
        """
        spin = self.grid[start_i, start_j]
        size = 0
        queue = deque([(start_i, start_j)])
        visited[start_i, start_j] = True

        while queue:
            x, y = queue.popleft()
            size += 1

            # Check all four nearest neighbors
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = (x + dx) % self.size, (y + dy) % self.size
                # Add neighbor if unvisited and same spin orientation
                if not visited[nx, ny] and self.grid[nx, ny] == spin:
                    visited[nx, ny] = True
                    queue.append((nx, ny))

        return size

    def find_domains(self):
        """Find all connected spin domains in the lattice.

        Identifies all maximal connected regions where spins have the same
        orientation (+1 or -1). This is analogous to percolation cluster
        finding or connected components in a graph.

        Domain statistics reveal critical behavior:
        - T < Tc: Few large domains (spontaneous symmetry breaking)
        - T = Tc: Power-law distribution P(s) ~ s^(-τ) with τ ≈ 2.05
        - T > Tc: Many small domains (thermal disorder)

        Returns:
            list of int: Sizes of all domains found. Length equals number of
                distinct domains. Sum equals size².
        """
        visited = np.zeros((self.size, self.size), dtype=bool)
        domain_sizes = []

        # Scan entire lattice to find all domains
        for i in range(self.size):
            for j in range(self.size):
                if not visited[i, j]:
                    size = self._bfs_domain_size(i, j, visited)
                    domain_sizes.append(size)

        return domain_sizes

    def get_domain_distribution(self, remove_percolating=True):
        """Get frequency distribution of domain sizes for power-law analysis.

        At the critical temperature, the domain size distribution follows a
        power law P(s) ~ s^(-τ) characteristic of scale-free systems. This
        method computes the empirical distribution for log-log plotting.

        Args:
            remove_percolating (bool): If True, remove the two largest domains.
                At criticality, the largest domains often span the entire system
                (finite-size percolation) and don't follow the power law. Removing
                them gives cleaner power-law fits. Default True.

        Returns:
            tuple: (sizes, frequencies) where:
                sizes (list of int): Sorted unique domain sizes.
                frequencies (list of int): Number of domains of each size.
                Both lists have the same length.

        Example:
            >>> model = IsingModel(size=128, temperature=2.269, seed=42)
            >>> model.sweep(200)
            >>> sizes, freqs = model.get_domain_distribution()
            >>> # Plot on log-log scale to see power law
        """
        domain_sizes = self.find_domains()

        if remove_percolating and len(domain_sizes) > 2:
            # Remove two largest domains (percolating clusters at finite size)
            # These represent the +1 and -1 spanning clusters
            domain_sizes = sorted(domain_sizes)[:-2]

        # Count frequency of each domain size
        counts = defaultdict(int)
        for size in domain_sizes:
            counts[size] += 1

        sizes = sorted(counts.keys())
        frequencies = [counts[s] for s in sizes]

        return sizes, frequencies

    def plot_state(self, ax=None):
        """Visualize the current spin configuration as a 2D image.

        Creates a color-coded visualization where blue represents spin-down (-1)
        and red represents spin-up (+1). Domain structure and phase transitions
        are visually apparent:
        - T < Tc: Large uniform regions (red or blue domains)
        - T = Tc: Fractal-like domain boundaries at all scales
        - T > Tc: Random speckled pattern (no structure)

        Args:
            ax (matplotlib.axes.Axes, optional): Axes to plot on. If None,
                creates new figure. Default None.

        Returns:
            matplotlib.image.AxesImage: The image object for animation updates.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))

        # Blue for spin-down, red for spin-up (ferromagnetic visualization)
        cmap = ListedColormap(['#3498db', '#e74c3c'])
        im = ax.imshow(self.grid, cmap=cmap, vmin=-1, vmax=1)

        T_ratio = self.temperature / self.Tc
        mag = self.get_magnetization()
        ax.set_title(f'Ising Model (T/Tc = {T_ratio:.3f}, M = {mag:.3f})')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')

        return im

    def plot_domain_distribution(self, ax=None, remove_percolating=True):
        """Plot domain size distribution on log-log scale to reveal power laws.

        At the critical temperature, the distribution follows P(s) ~ s^(-τ)
        which appears as a straight line on log-log axes. The slope gives the
        critical exponent τ ≈ 2.05 for the 2D Ising model.

        Args:
            ax (matplotlib.axes.Axes, optional): Axes to plot on. If None,
                creates new figure. Default None.
            remove_percolating (bool): Whether to remove largest domains that
                span the system. Default True.

        Returns:
            matplotlib.axes.Axes: The axes object containing the plot.
        """
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


def _simulate_at_temperature(T, axes_row, col_idx):
    """Simulate and plot Ising model at a single temperature.

    Helper function for temperature comparison visualization. Runs equilibration
    sweeps and plots both spin configuration and domain distribution.

    Args:
        T (float): Absolute temperature to simulate.
        axes_row (array): 2D array of matplotlib axes [spin_axes, dist_axes].
        col_idx (int): Column index for this temperature in the subplot grid.
    """
    print(f"Simulating T = {T:.3f} (T/Tc = {T/2.269:.3f})...")

    model = IsingModel(size=128, temperature=T, seed=42)
    model.sweep(100)  # Equilibrate system

    # Plot spin configuration in top row
    model.plot_state(axes_row[0][col_idx])

    # Plot domain distribution in bottom row
    # Only remove percolating domains near critical temperature
    model.plot_domain_distribution(
        axes_row[1][col_idx], remove_percolating=(abs(T - 2.269) < 0.1)
    )


def run_temperature_comparison():
    """Compare Ising model behavior across the phase transition.

    Creates a 2x4 grid showing spin configurations (top) and domain distributions
    (bottom) at four temperatures spanning the phase transition. This demonstrates:
    - Ordered phase (T < Tc): Large domains, magnetization
    - Critical point (T = Tc): Scale-free domains, power-law distribution
    - Disordered phase (T > Tc): Small random domains, no magnetization

    Saves output to 'ising_temperature_comparison.png'.
    """
    print("2D Ising Model - Temperature Comparison")
    print("=" * 50)

    # Sample temperatures: ordered, intermediate, critical, disordered
    temperatures = [0.5, 1.0, 2.269, 4.0]
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))

    for i, T in enumerate(temperatures):
        _simulate_at_temperature(T, axes, i)

    plt.tight_layout()
    plt.savefig('ising_temperature_comparison.png', dpi=150)
    plt.show()
    print("\nResults saved to ising_temperature_comparison.png")


def _setup_ising_animation(model, ax1, ax2):
    """Initialize animation axes for spin configuration and domain distribution.

    Sets up two side-by-side plots: spin lattice visualization (left) and
    domain size distribution on log-log scale (right).

    Args:
        model (IsingModel): The model to animate.
        ax1 (matplotlib.axes.Axes): Axes for spin configuration.
        ax2 (matplotlib.axes.Axes): Axes for domain distribution.

    Returns:
        tuple: (im, line) where:
            im: Image object for spin configuration updates.
            line: Line2D object for distribution updates.
    """
    # Set up spin configuration visualization
    cmap = ListedColormap(['#3498db', '#e74c3c'])
    im = ax1.imshow(model.grid, cmap=cmap, vmin=-1, vmax=1)
    ax1.set_title('Spin Configuration')

    # Set up domain distribution plot
    line, = ax2.loglog([], [], 'o', markersize=4, alpha=0.7, color='purple')
    ax2.set_xlabel('Domain Size')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Domain Size Distribution')
    ax2.set_xlim(1, 10000)
    ax2.set_ylim(1, 1000)
    ax2.grid(True, alpha=0.3)

    return im, line


def _create_ising_update(model, im, ax1, ax2, line):
    """Create update function for animation of Ising model dynamics.

    The returned function advances the simulation and updates both plots
    each frame. This allows visualization of equilibration and critical
    fluctuations at T = Tc.

    Args:
        model (IsingModel): Model instance to evolve.
        im (AxesImage): Image object for spin lattice.
        ax1 (Axes): Axes containing spin configuration.
        ax2 (Axes): Axes containing domain distribution.
        line (Line2D): Line object for distribution plot.

    Returns:
        function: Update function for FuncAnimation with signature update(frame).
    """
    def update(frame):
        # Advance simulation by 5 sweeps per frame
        model.sweep(5)

        # Update spin configuration display
        im.set_array(model.grid)
        ax1.set_title(f'T/Tc = 1.0, Sweep {model.sweeps}')

        # Update domain distribution plot
        sizes, frequencies = model.get_domain_distribution(remove_percolating=True)
        if sizes:
            line.set_data(sizes, frequencies)
            # Dynamically adjust axes to data range
            ax2.set_xlim(0.8, max(sizes) * 2)
            ax2.set_ylim(0.8, max(max(frequencies), 10) * 2)

        return im, line
    return update


def run_critical_animation():
    """Animate Ising model evolution at the critical temperature.

    Shows real-time dynamics of spin domains at T = Tc where the system
    exhibits scale-free fluctuations. Both the spin configuration and
    domain size distribution are updated each frame.

    At Tc, you'll observe:
    - Constantly shifting domain boundaries at all scales
    - Domain sizes spanning from single spins to large clusters
    - Power-law distribution emerging after equilibration
    - Critical opalescence (large correlated regions)

    Press 'q' or close window to stop animation.
    """
    print("Running Ising Model at Critical Temperature...")

    model = IsingModel(size=128, temperature=2.269, seed=42)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    im, line = _setup_ising_animation(model, ax1, ax2)
    update = _create_ising_update(model, im, ax1, ax2, line)

    _anim = FuncAnimation(fig, update, frames=200, interval=100, blit=False)
    plt.tight_layout()
    plt.show()


def _print_ising_stats(model):
    """Print statistical summary of current Ising model state.

    Displays key observables including magnetization (order parameter) and
    domain statistics that characterize the phase.

    Args:
        model (IsingModel): The model to summarize.
    """
    print(f"Sweeps completed: {model.sweeps}")
    print(f"Magnetization: {model.get_magnetization():.4f}")

    domain_sizes = model.find_domains()
    print(f"Number of domains: {len(domain_sizes)}")
    print(f"Largest domain: {max(domain_sizes)} spins")


def run_quick_demo():
    """Quick demonstration of Ising model at critical temperature.

    Runs a single simulation at T = Tc, equilibrates the system, and generates
    a visualization showing both the spin configuration and domain size
    distribution. This demonstrates self-organized criticality and power-law
    behavior.

    The critical temperature Tc ≈ 2.269 is where the correlation length
    diverges and the system exhibits scale-free behavior. The domain size
    distribution should follow P(s) ~ s^(-τ) with τ ≈ 2.05.

    Output saved to 'ising_critical.png'.
    """
    print("2D Ising Model at Critical Temperature")
    print("=" * 50)

    # Initialize at critical temperature with fixed seed for reproducibility
    model = IsingModel(size=128, temperature=2.269, seed=42)
    print("Equilibrating...")
    model.sweep(200)  # Allow system to reach equilibrium

    _print_ising_stats(model)

    # Generate side-by-side plots
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
