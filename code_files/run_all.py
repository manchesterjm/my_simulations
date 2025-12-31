"""Power Laws and Self-Organized Criticality Demonstration.

This module orchestrates all three SOC simulations from the Veritasium power laws
video, demonstrating that completely different physical systems exhibit the same
universal behavior when at criticality: power law distributions with no
characteristic scale.

Simulations Demonstrated:
    1. Sandpile: Per Bak's Abelian Sandpile Model
       - Avalanche sizes follow power law distribution
       - Self-organizes to critical state through grain accumulation

    2. Ising Model: 2D magnetic spins at Curie temperature
       - Domain sizes follow power law distribution at Tc ≈ 2.269
       - Critical point between ordered and disordered phases

    3. Forest Fire: Drossel-Schwabl Model
       - Fire sizes follow power law distribution
       - Balance between tree growth and lightning strikes

Universal Behavior:
    All three systems, despite completely different mechanisms, exhibit:
    - Power law distributions (straight lines on log-log plots)
    - No characteristic scale (events span many orders of magnitude)
    - Self-organization to criticality (no parameter tuning needed)

Usage:
    Run all simulations with 2x3 visualization grid:
        $ python run_all.py

    Plot all distributions on single graph:
        $ python run_all.py --combined

Outputs:
    - power_law_comparison.png: Side-by-side simulations and distributions
    - universal_power_law.png: Combined normalized distributions (--combined mode)

Key Insight:
    The same mathematical pattern emerges from radically different physics,
    suggesting universal principles govern complex systems at criticality.
"""

import numpy as np
import matplotlib.pyplot as plt
from sandpile import SandpileSimulation
from ising_model import IsingModel
from forest_fire import ForestFireSimulation


def run_all_simulations():
    """Run all three SOC simulations and visualize their power law distributions.

    This orchestrates the complete demonstration of self-organized criticality
    by running sandpile, Ising model, and forest fire simulations. Results are
    displayed in a 2x3 grid showing both system states and their power law
    distributions.

    The function demonstrates universality: despite completely different physical
    mechanisms, all three systems exhibit power law behavior (straight lines on
    log-log plots) characteristic of critical systems.

    Outputs:
        Saves visualization to 'power_law_comparison.png' and displays statistics
        for each simulation including largest events and system metrics.

    Example:
        >>> run_all_simulations()
        ==================================================
        POWER LAWS AND SELF-ORGANIZED CRITICALITY
        ...
        [1/3] Running Sandpile Simulation...
              Largest avalanche: 1523
        [2/3] Running Ising Model at Critical Temperature...
              Number of domains: 47
        [3/3] Running Forest Fire Simulation...
              Largest fire: 2891
        ...
        Results saved to: power_law_comparison.png
    """

    print("=" * 60)
    print("POWER LAWS AND SELF-ORGANIZED CRITICALITY")
    print("Demonstrating Universal Behavior Across Different Systems")
    print("=" * 60)

    # Create figure with 2 rows: visualizations on top, distributions on bottom
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # =========== SANDPILE ===========
    print("\n[1/3] Running Sandpile Simulation...")
    # Initialize and run sandpile with random grain drops
    sandpile = SandpileSimulation(size=100, drop_mode='random', seed=42)
    sandpile.run(50000)

    # Display statistics
    print(f"      Grains dropped: {sandpile.total_grains}")
    print(f"      Total avalanches: {len(sandpile.avalanche_sizes)}")
    if sandpile.avalanche_sizes:
        print(f"      Largest avalanche: {max(sandpile.avalanche_sizes)}")

    # Plot current sandpile state (grain heights)
    im1 = axes[0, 0].imshow(sandpile.grid, cmap='YlOrBr', vmin=0, vmax=4)
    axes[0, 0].set_title('Sandpile', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('X')
    axes[0, 0].set_ylabel('Y')
    plt.colorbar(im1, ax=axes[0, 0], label='Grains')

    # Plot avalanche size distribution (power law on log-log plot)
    sizes, freqs = sandpile.get_avalanche_distribution()
    if sizes:
        axes[1, 0].loglog(sizes, freqs, 'o', markersize=3, alpha=0.6, color='#d35400')
        axes[1, 0].set_xlabel('Avalanche Size')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Avalanche Distribution', fontsize=10)
        axes[1, 0].grid(True, alpha=0.3)

    # =========== ISING MODEL ===========
    print("\n[2/3] Running Ising Model at Critical Temperature...")
    # Initialize at critical temperature (Tc ≈ 2.269 for 2D Ising)
    ising = IsingModel(size=128, temperature=2.269, seed=42)
    ising.sweep(200)  # Run Monte Carlo sweeps

    # Display statistics
    print(f"      Sweeps completed: {ising.sweeps}")
    print(f"      Magnetization: {ising.get_magnetization():.4f}")
    domain_sizes = ising.find_domains()  # Find connected spin clusters
    print(f"      Number of domains: {len(domain_sizes)}")

    # Plot Ising state (up/down spins as blue/red)
    from matplotlib.colors import ListedColormap
    cmap_ising = ListedColormap(['#3498db', '#e74c3c'])
    _im2 = axes[0, 1].imshow(ising.grid, cmap=cmap_ising, vmin=-1, vmax=1)
    axes[0, 1].set_title('Ising Model (T = Tc)', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('X')
    axes[0, 1].set_ylabel('Y')

    # Plot domain size distribution (power law at criticality)
    sizes, freqs = ising.get_domain_distribution(remove_percolating=True)
    if sizes:
        axes[1, 1].loglog(sizes, freqs, 'o', markersize=3, alpha=0.6, color='#8e44ad')
        axes[1, 1].set_xlabel('Domain Size')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Domain Size Distribution', fontsize=10)
        axes[1, 1].grid(True, alpha=0.3)

    # =========== FOREST FIRE ===========
    print("\n[3/3] Running Forest Fire Simulation...")
    # Initialize with tree growth probability (lightning = p/10)
    forest = ForestFireSimulation(size=200, tree_growth_prob=0.01, seed=42)
    forest.run(10000, progress_interval=2500)

    # Display statistics
    print(f"      Timesteps: {forest.timestep}")
    print(f"      Tree density: {forest.tree_density():.1%}")
    print(f"      Total fires: {len(forest.fire_sizes)}")
    if forest.fire_sizes:
        print(f"      Largest fire: {max(forest.fire_sizes)}")

    # Plot forest state (empty/tree/burning as dark/green/orange)
    cmap_forest = ListedColormap(['#1a1a2e', '#2d5a27', '#ff4500'])
    _im3 = axes[0, 2].imshow(forest.grid, cmap=cmap_forest, vmin=0, vmax=2)
    axes[0, 2].set_title('Forest Fire', fontsize=12, fontweight='bold')
    axes[0, 2].set_xlabel('X')
    axes[0, 2].set_ylabel('Y')

    # Plot fire size distribution (power law emerges naturally)
    sizes, freqs = forest.get_fire_distribution()
    if sizes:
        axes[1, 2].loglog(sizes, freqs, 'o', markersize=3, alpha=0.6, color='#c0392b')
        axes[1, 2].set_xlabel('Fire Size')
        axes[1, 2].set_ylabel('Frequency')
        axes[1, 2].set_title('Fire Size Distribution', fontsize=10)
        axes[1, 2].grid(True, alpha=0.3)

    # Add main title
    fig.suptitle('Self-Organized Criticality: Three Systems, One Universal Pattern',
                 fontsize=14, fontweight='bold', y=1.02)

    plt.tight_layout()
    plt.savefig('power_law_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print("""
All three simulations show POWER LAW distributions (straight lines
on log-log plots). This is the signature of self-organized criticality.

Key insights from the video:
- Small events are common, large events are rare (but not as rare as
  normal distributions would predict)
- There is no characteristic scale - events span many orders of magnitude
- The same grain of sand / lightning strike / spin flip can cause
  either a tiny event or a massive cascade
- The system naturally tunes itself to this critical state

This universality means you can understand complex systems (earthquakes,
forest fires, stock markets) using simple models like these!
""")
    print("Results saved to: power_law_comparison.png")


def plot_combined_distributions():
    """Plot all three distributions on a single graph to demonstrate universality.

    Runs all three simulations and overlays their normalized power law
    distributions on a single log-log plot. This visualization clearly shows
    that despite completely different physics, all three systems exhibit the
    same universal power law behavior.

    The distributions are normalized (divided by total events) to enable
    direct comparison. A reference power law line (x^-1.5) is included
    for comparison.

    Outputs:
        Saves combined visualization to 'universal_power_law.png' showing
        all three distributions with different markers overlaid on one plot.

    Example:
        >>> plot_combined_distributions()
        Running simulations for combined plot...
        Combined plot saved to: universal_power_law.png

    Note:
        All distributions should approximately follow the same slope on the
        log-log plot, demonstrating universality class behavior.
    """

    print("Running simulations for combined plot...")

    # Run all three simulations with same parameters as main demo
    sandpile = SandpileSimulation(size=100, drop_mode='random', seed=42)
    sandpile.run(50000)

    ising = IsingModel(size=128, temperature=2.269, seed=42)
    ising.sweep(200)

    forest = ForestFireSimulation(size=200, tree_growth_prob=0.01, seed=42)
    forest.run(10000, progress_interval=None)

    # Create single plot for overlaid distributions
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot sandpile avalanche distribution (normalized)
    sizes, freqs = sandpile.get_avalanche_distribution()
    if sizes:
        # Normalize by total number of events for comparison
        total = sum(freqs)
        freqs_norm = [f / total for f in freqs]
        ax.loglog(sizes, freqs_norm, 'o', markersize=4, alpha=0.7,
                  color='#d35400', label='Sandpile Avalanches')

    # Plot Ising domain distribution (normalized, percolating domains removed)
    sizes, freqs = ising.get_domain_distribution(remove_percolating=True)
    if sizes:
        total = sum(freqs)
        freqs_norm = [f / total for f in freqs]
        ax.loglog(sizes, freqs_norm, 's', markersize=4, alpha=0.7,
                  color='#8e44ad', label='Ising Domains')

    # Plot forest fire distribution (normalized)
    sizes, freqs = forest.get_fire_distribution()
    if sizes:
        total = sum(freqs)
        freqs_norm = [f / total for f in freqs]
        ax.loglog(sizes, freqs_norm, '^', markersize=4, alpha=0.7,
                  color='#c0392b', label='Forest Fires')

    # Add reference power law line for comparison
    x = np.logspace(0, 4, 100)
    ax.loglog(x, 0.5 * x ** -1.5, '--', color='gray', alpha=0.5,
              label=r'Reference: $x^{-1.5}$')

    ax.set_xlabel('Event Size', fontsize=12)
    ax.set_ylabel('Normalized Frequency', fontsize=12)
    ax.set_title('Universal Power Law Behavior\nThree Different Systems, Same Pattern',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('universal_power_law.png', dpi=150)
    plt.show()

    print("Combined plot saved to: universal_power_law.png")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--combined':
        plot_combined_distributions()
    else:
        run_all_simulations()
