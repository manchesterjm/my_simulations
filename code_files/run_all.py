"""
Power Laws and Self-Organized Criticality
==========================================

This script runs all three simulations from the Veritasium video and
demonstrates that they all produce power law distributions - a signature
of systems at criticality.

Simulations:
1. Sandpile (Per Bak's Abelian Sandpile Model)
2. Ising Model (2D magnetic spins at Curie temperature)
3. Forest Fire (Drossel-Schwabl Model)

All three systems, despite their completely different physical mechanisms,
exhibit the same universal behavior: power law distributions with no
characteristic scale.
"""

import numpy as np
import matplotlib.pyplot as plt
from sandpile import SandpileSimulation
from ising_model import IsingModel
from forest_fire import ForestFireSimulation


def run_all_simulations():
    """Run all three simulations and compare their power law distributions."""

    print("=" * 60)
    print("POWER LAWS AND SELF-ORGANIZED CRITICALITY")
    print("Demonstrating Universal Behavior Across Different Systems")
    print("=" * 60)

    # Create figure with 2 rows: visualizations on top, distributions on bottom
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # =========== SANDPILE ===========
    print("\n[1/3] Running Sandpile Simulation...")
    sandpile = SandpileSimulation(size=100, drop_mode='random', seed=42)
    sandpile.run(50000)

    print(f"      Grains dropped: {sandpile.total_grains}")
    print(f"      Total avalanches: {len(sandpile.avalanche_sizes)}")
    if sandpile.avalanche_sizes:
        print(f"      Largest avalanche: {max(sandpile.avalanche_sizes)}")

    # Plot sandpile state
    im1 = axes[0, 0].imshow(sandpile.grid, cmap='YlOrBr', vmin=0, vmax=4)
    axes[0, 0].set_title('Sandpile', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('X')
    axes[0, 0].set_ylabel('Y')
    plt.colorbar(im1, ax=axes[0, 0], label='Grains')

    # Plot sandpile distribution
    sizes, freqs = sandpile.get_avalanche_distribution()
    if sizes:
        axes[1, 0].loglog(sizes, freqs, 'o', markersize=3, alpha=0.6, color='#d35400')
        axes[1, 0].set_xlabel('Avalanche Size')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Avalanche Distribution', fontsize=10)
        axes[1, 0].grid(True, alpha=0.3)

    # =========== ISING MODEL ===========
    print("\n[2/3] Running Ising Model at Critical Temperature...")
    ising = IsingModel(size=128, temperature=2.269, seed=42)
    ising.sweep(200)

    print(f"      Sweeps completed: {ising.sweeps}")
    print(f"      Magnetization: {ising.get_magnetization():.4f}")
    domain_sizes = ising.find_domains()
    print(f"      Number of domains: {len(domain_sizes)}")

    # Plot Ising state
    from matplotlib.colors import ListedColormap
    cmap_ising = ListedColormap(['#3498db', '#e74c3c'])
    im2 = axes[0, 1].imshow(ising.grid, cmap=cmap_ising, vmin=-1, vmax=1)
    axes[0, 1].set_title('Ising Model (T = Tc)', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('X')
    axes[0, 1].set_ylabel('Y')

    # Plot Ising distribution
    sizes, freqs = ising.get_domain_distribution(remove_percolating=True)
    if sizes:
        axes[1, 1].loglog(sizes, freqs, 'o', markersize=3, alpha=0.6, color='#8e44ad')
        axes[1, 1].set_xlabel('Domain Size')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Domain Size Distribution', fontsize=10)
        axes[1, 1].grid(True, alpha=0.3)

    # =========== FOREST FIRE ===========
    print("\n[3/3] Running Forest Fire Simulation...")
    forest = ForestFireSimulation(size=200, tree_growth_prob=0.01, seed=42)
    forest.run(10000, progress_interval=2500)

    print(f"      Timesteps: {forest.timestep}")
    print(f"      Tree density: {forest.tree_density():.1%}")
    print(f"      Total fires: {len(forest.fire_sizes)}")
    if forest.fire_sizes:
        print(f"      Largest fire: {max(forest.fire_sizes)}")

    # Plot forest state
    cmap_forest = ListedColormap(['#1a1a2e', '#2d5a27', '#ff4500'])
    im3 = axes[0, 2].imshow(forest.grid, cmap=cmap_forest, vmin=0, vmax=2)
    axes[0, 2].set_title('Forest Fire', fontsize=12, fontweight='bold')
    axes[0, 2].set_xlabel('X')
    axes[0, 2].set_ylabel('Y')

    # Plot forest distribution
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
    """Plot all three distributions on one graph to show universality."""

    print("Running simulations for combined plot...")

    # Run simulations
    sandpile = SandpileSimulation(size=100, drop_mode='random', seed=42)
    sandpile.run(50000)

    ising = IsingModel(size=128, temperature=2.269, seed=42)
    ising.sweep(200)

    forest = ForestFireSimulation(size=200, tree_growth_prob=0.01, seed=42)
    forest.run(10000, progress_interval=None)

    # Normalize distributions for comparison
    fig, ax = plt.subplots(figsize=(10, 8))

    # Sandpile
    sizes, freqs = sandpile.get_avalanche_distribution()
    if sizes:
        # Normalize
        total = sum(freqs)
        freqs_norm = [f / total for f in freqs]
        ax.loglog(sizes, freqs_norm, 'o', markersize=4, alpha=0.7,
                  color='#d35400', label='Sandpile Avalanches')

    # Ising
    sizes, freqs = ising.get_domain_distribution(remove_percolating=True)
    if sizes:
        total = sum(freqs)
        freqs_norm = [f / total for f in freqs]
        ax.loglog(sizes, freqs_norm, 's', markersize=4, alpha=0.7,
                  color='#8e44ad', label='Ising Domains')

    # Forest
    sizes, freqs = forest.get_fire_distribution()
    if sizes:
        total = sum(freqs)
        freqs_norm = [f / total for f in freqs]
        ax.loglog(sizes, freqs_norm, '^', markersize=4, alpha=0.7,
                  color='#c0392b', label='Forest Fires')

    # Reference power law line
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
