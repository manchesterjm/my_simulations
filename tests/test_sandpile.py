"""
Unit tests for Sandpile Simulation
Based on BDD scenarios in features/sandpile.feature
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings

import sys
sys.path.insert(0, 'code_files')
from sandpile import SandpileSimulation


class TestSandpileCoreMechanics:
    """Tests for core sandpile mechanics."""

    def test_drop_grain_on_empty_cell(self):
        """Scenario: Dropping a grain on an empty cell."""
        # Given a sandpile simulation with grid size 50x50
        sim = SandpileSimulation(size=50, threshold=4, drop_mode='center')

        # And an empty cell at position (25, 25) - center
        assert sim.grid[25, 25] == 0

        # When I drop a grain at position (25, 25)
        avalanche_size = sim.drop_grain()

        # Then the cell at (25, 25) should have 1 grain
        assert sim.grid[25, 25] == 1

        # And the total grain count should be 1
        assert sim.total_grains == 1

        # And no avalanche should occur
        assert avalanche_size == 0

    def test_cell_topples_at_threshold(self):
        """Scenario: Cell topples when reaching threshold."""
        # Given a sandpile simulation
        sim = SandpileSimulation(size=50, threshold=4, drop_mode='center')

        # And a cell at position (25, 25) with 3 grains
        sim.grid[25, 25] = 3

        # When I drop a grain at position (25, 25)
        sim.total_grains = 3  # Account for existing grains
        avalanche_size = sim.drop_grain()

        # Then the cell at (25, 25) should have 0 grains
        assert sim.grid[25, 25] == 0

        # And each orthogonal neighbor should receive 1 grain
        assert sim.grid[24, 25] == 1  # Up
        assert sim.grid[26, 25] == 1  # Down
        assert sim.grid[25, 24] == 1  # Left
        assert sim.grid[25, 26] == 1  # Right

        # And an avalanche of size 1 should be recorded
        assert avalanche_size == 1
        assert len(sim.avalanche_sizes) == 1

    def test_cascading_avalanche(self):
        """Scenario: Cascading avalanche."""
        # Given a sandpile simulation
        sim = SandpileSimulation(size=50, threshold=4, drop_mode='center')

        # And a cell at position (25, 25) with 3 grains
        sim.grid[25, 25] = 3

        # And a cell at position (25, 26) with 3 grains
        sim.grid[25, 26] = 3

        # When I drop a grain at position (25, 25)
        avalanche_size = sim.drop_grain()

        # Then an avalanche larger than 1 should occur
        assert avalanche_size > 1

        # And all cells should have fewer than 4 grains when stable
        assert np.all(sim.grid < sim.threshold)

    def test_grains_fall_off_edge(self):
        """Scenario: Grains fall off the edge."""
        # Given a sandpile simulation
        sim = SandpileSimulation(size=50, threshold=4, drop_mode='center')

        # And a cell at position (0, 0) with 3 grains
        sim.grid[0, 0] = 3

        # When I drop a grain at position (0, 0)
        sim.drop_mode = 'center'  # Temporarily override
        sim.grid[0, 0] = 4  # Force topple at corner
        avalanche_size = sim.process_avalanche()

        # Then the cell at (0, 0) should have 0 grains
        assert sim.grid[0, 0] == 0

        # And only 2 neighbors should receive grains (corner has only 2 neighbors)
        assert sim.grid[0, 1] == 1  # Right
        assert sim.grid[1, 0] == 1  # Down

        # And 2 grains should be lost to the boundary (implicitly tested)


class TestSandpileDropModes:
    """Tests for different drop modes."""

    def test_random_drop_mode(self):
        """Scenario: Random drop mode."""
        # Given drop mode is set to "random"
        sim = SandpileSimulation(size=50, drop_mode='random', seed=42)

        # When I drop 100 grains
        sim.run(100)

        # Then grains should be distributed across multiple cells
        non_zero_cells = np.sum(sim.grid > 0)
        assert non_zero_cells > 1

    def test_center_drop_mode(self):
        """Scenario: Center drop mode."""
        # Given drop mode is set to "center"
        sim = SandpileSimulation(size=50, drop_mode='center')

        # When I drop 3 grains (before toppling)
        for _ in range(3):
            sim.drop_grain()

        # Then all grains should land at the center cell
        center = sim.size // 2
        assert sim.grid[center, center] == 3


class TestSandpileStatistics:
    """Tests for statistical properties."""

    def test_power_law_distribution_emerges(self):
        """Scenario: Power law distribution emerges."""
        # Given the simulation has run for 50000 grain drops
        sim = SandpileSimulation(size=100, drop_mode='random', seed=42)
        sim.run(50000)

        # When I analyze the avalanche size distribution
        sizes, frequencies = sim.get_avalanche_distribution()

        # Then the distribution should have multiple sizes
        assert len(sizes) > 10

        # And avalanche sizes should span multiple orders of magnitude
        if sizes:
            size_range = max(sizes) / min(sizes)
            assert size_range > 10  # At least one order of magnitude

    def test_reproducibility_with_seed(self):
        """Scenario: Reproducibility with seed."""
        # Given a random seed of 42
        sim1 = SandpileSimulation(size=50, drop_mode='random', seed=42)
        sim2 = SandpileSimulation(size=50, drop_mode='random', seed=42)

        # When I run the simulation for 1000 drops
        sim1.run(1000)

        # And I reset and run again with the same seed
        sim2.run(1000)

        # Then both runs should produce identical results
        assert np.array_equal(sim1.grid, sim2.grid)
        assert sim1.avalanche_sizes == sim2.avalanche_sizes


class TestSandpileStability:
    """Tests for grid stability."""

    def test_grid_stable_after_avalanche(self):
        """Scenario: Grid reaches stable state after avalanche."""
        sim = SandpileSimulation(size=50, drop_mode='random', seed=42)

        # When I drop grains until an avalanche occurs
        for _ in range(1000):
            avalanche_size = sim.drop_grain()

            # Then all cells should have fewer than threshold grains
            assert np.all(sim.grid < sim.threshold)

            # And no cells should be in an unstable state
            assert not np.any(sim.grid >= sim.threshold)


class TestSandpileInitialization:
    """Tests for initialization."""

    def test_default_initialization(self):
        """Test default values."""
        sim = SandpileSimulation()

        assert sim.size == 50
        assert sim.threshold == 4
        assert sim.drop_mode == 'random'
        assert sim.total_grains == 0
        assert len(sim.avalanche_sizes) == 0
        assert sim.grid.shape == (50, 50)
        assert np.all(sim.grid == 0)

    def test_custom_initialization(self):
        """Test custom values."""
        sim = SandpileSimulation(size=100, threshold=6, drop_mode='center', seed=123)

        assert sim.size == 100
        assert sim.threshold == 6
        assert sim.drop_mode == 'center'
        assert sim.grid.shape == (100, 100)


class TestSandpileDistribution:
    """Tests for avalanche distribution."""

    def test_empty_distribution(self):
        """Test distribution with no avalanches."""
        sim = SandpileSimulation(size=50)
        sizes, frequencies = sim.get_avalanche_distribution()

        assert sizes == {}
        assert frequencies == {}

    def test_distribution_after_avalanches(self):
        """Test distribution after avalanches occur."""
        sim = SandpileSimulation(size=50, drop_mode='random', seed=42)
        sim.run(5000)

        sizes, frequencies = sim.get_avalanche_distribution()

        # Should have some data
        assert len(sizes) > 0
        assert len(frequencies) > 0
        assert len(sizes) == len(frequencies)

        # Frequencies should be positive
        assert all(f > 0 for f in frequencies)


# Hypothesis fuzz tests
class TestSandpileFuzz:
    """Fuzz tests using Hypothesis."""

    @given(st.integers(min_value=5, max_value=50))
    @settings(max_examples=20)
    def test_fuzz_grid_size(self, size):
        """Fuzz test: various grid sizes should work."""
        sim = SandpileSimulation(size=size, seed=42)
        sim.run(100)

        # Grid should remain stable
        assert np.all(sim.grid < sim.threshold)
        assert sim.grid.shape == (size, size)

    @given(st.integers(min_value=3, max_value=8))
    @settings(max_examples=10)
    def test_fuzz_threshold(self, threshold):
        """Fuzz test: various thresholds should work."""
        sim = SandpileSimulation(size=20, threshold=threshold, seed=42)
        sim.run(100)

        # Grid should remain stable
        assert np.all(sim.grid < threshold)

    @given(st.integers(min_value=1, max_value=1000))
    @settings(max_examples=20)
    def test_fuzz_num_drops(self, num_drops):
        """Fuzz test: various drop counts should work."""
        sim = SandpileSimulation(size=20, seed=42)
        sim.run(num_drops)

        # Total grains should match drops
        assert sim.total_grains == num_drops

        # Grid should be stable
        assert np.all(sim.grid < sim.threshold)

    @given(st.integers(min_value=0, max_value=2**31-1))
    @settings(max_examples=10)
    def test_fuzz_random_seed(self, seed):
        """Fuzz test: various seeds should produce reproducible results."""
        sim1 = SandpileSimulation(size=20, seed=seed)
        sim2 = SandpileSimulation(size=20, seed=seed)

        sim1.run(100)
        sim2.run(100)

        assert np.array_equal(sim1.grid, sim2.grid)
