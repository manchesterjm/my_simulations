"""
Unit tests for Forest Fire Simulation
Based on BDD scenarios in features/forest_fire.feature
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings

import sys
sys.path.insert(0, 'code_files')
from forest_fire import ForestFireSimulation, EMPTY, TREE, BURNING


class TestForestFireCellStates:
    """Tests for cell state transitions."""

    def test_cell_states_constants(self):
        """Test that cell state constants are defined correctly."""
        assert EMPTY == 0
        assert TREE == 1
        assert BURNING == 2

    def test_empty_cell_can_grow_tree(self):
        """Scenario: Empty cell can grow a tree."""
        # Given an empty cell
        sim = ForestFireSimulation(size=10, tree_growth_prob=1.0, lightning_prob=0, seed=42)

        assert sim.grid[5, 5] == EMPTY

        # When a growth event occurs (prob=1.0 guarantees growth)
        sim.step()

        # Then the cell should become a tree
        assert sim.grid[5, 5] == TREE

    def test_tree_can_catch_fire(self):
        """Scenario: Tree can catch fire from lightning."""
        sim = ForestFireSimulation(size=10, tree_growth_prob=0, lightning_prob=1.0, seed=42)

        # Given a tree at position (5, 5)
        sim.grid[5, 5] = TREE

        # When lightning strikes (prob=1.0)
        fire_size = sim.spread_fire(5, 5)

        # Then the cell should become burning
        assert sim.grid[5, 5] == BURNING
        assert fire_size == 1

    def test_burning_cell_becomes_empty(self):
        """Scenario: Burning cell becomes empty."""
        sim = ForestFireSimulation(size=10, tree_growth_prob=0, lightning_prob=0, seed=42)

        # Given a burning cell
        sim.grid[5, 5] = BURNING

        # When one simulation step completes
        sim.step()

        # Then the cell should become empty
        assert sim.grid[5, 5] == EMPTY


class TestForestFireSpreading:
    """Tests for fire spreading mechanics."""

    def test_fire_spreads_to_adjacent_trees(self):
        """Scenario: Fire spreads to adjacent trees."""
        sim = ForestFireSimulation(size=10, tree_growth_prob=0, lightning_prob=0, seed=42)

        # Given a tree at center and trees at all 8 neighbors
        sim.grid[5, 5] = TREE
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di != 0 or dj != 0:
                    sim.grid[5 + di, 5 + dj] = TREE

        # When fire starts at center
        fire_size = sim.spread_fire(5, 5)

        # Then all 9 trees should burn (center + 8 neighbors)
        assert fire_size == 9

        # All should now be burning
        assert sim.grid[5, 5] == BURNING
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                assert sim.grid[5 + di, 5 + dj] == BURNING

    def test_fire_does_not_spread_to_empty_cells(self):
        """Scenario: Fire does not spread to empty cells."""
        sim = ForestFireSimulation(size=10, tree_growth_prob=0, lightning_prob=0, seed=42)

        # Given a tree surrounded by empty cells
        sim.grid[5, 5] = TREE

        # When fire starts
        fire_size = sim.spread_fire(5, 5)

        # Then only the one tree burns
        assert fire_size == 1
        assert sim.grid[5, 5] == BURNING

        # Neighbors should still be empty
        assert sim.grid[4, 5] == EMPTY
        assert sim.grid[6, 5] == EMPTY

    def test_fire_does_not_wrap_around_boundaries(self):
        """Scenario: Fire does not wrap around boundaries."""
        sim = ForestFireSimulation(size=10, tree_growth_prob=0, lightning_prob=0, seed=42)

        # Given a tree at corner and another at opposite corner
        sim.grid[0, 0] = TREE
        sim.grid[9, 9] = TREE

        # When fire starts at (0, 0)
        fire_size = sim.spread_fire(0, 0)

        # Then only the corner tree burns (fire doesn't wrap)
        assert fire_size == 1
        assert sim.grid[0, 0] == BURNING
        assert sim.grid[9, 9] == TREE  # Should NOT have caught fire

    def test_spread_fire_on_empty_cell(self):
        """Test that spreading fire on empty cell does nothing."""
        sim = ForestFireSimulation(size=10, seed=42)

        fire_size = sim.spread_fire(5, 5)

        assert fire_size == 0


class TestForestFireSizeTracking:
    """Tests for fire size tracking."""

    def test_single_tree_fire_size(self):
        """Scenario: Single tree fire."""
        sim = ForestFireSimulation(size=10, tree_growth_prob=0, lightning_prob=0, seed=42)

        # Given only one isolated tree
        sim.grid[5, 5] = TREE

        # When lightning strikes
        fire_size = sim.spread_fire(5, 5)
        sim.fire_sizes.append(fire_size)

        # Then a fire of size 1 should be recorded
        assert fire_size == 1
        assert sim.fire_sizes == [1]

    def test_connected_forest_fire_size(self):
        """Scenario: Connected forest fire."""
        sim = ForestFireSimulation(size=10, tree_growth_prob=0, lightning_prob=0, seed=42)

        # Given a cluster of 10 connected trees (3x3 + 1)
        for i in range(3):
            for j in range(3):
                sim.grid[4 + i, 4 + j] = TREE
        sim.grid[7, 5] = TREE  # One more to make 10

        # When lightning strikes one tree in the cluster
        fire_size = sim.spread_fire(5, 5)

        # Then all connected trees should burn
        assert fire_size == 10


class TestForestFireDensity:
    """Tests for tree density calculations."""

    def test_tree_density_empty(self):
        """Test tree density with empty grid."""
        sim = ForestFireSimulation(size=10, seed=42)

        assert sim.tree_density() == 0.0

    def test_tree_density_full(self):
        """Test tree density with full grid."""
        sim = ForestFireSimulation(size=10, seed=42)
        sim.grid[:, :] = TREE

        assert sim.tree_density() == 1.0

    def test_tree_density_partial(self):
        """Scenario: Tree density calculation - 10%."""
        sim = ForestFireSimulation(size=10, seed=42)

        # Set 10 trees in a 100-cell grid
        for i in range(10):
            sim.grid[i, 0] = TREE

        density = sim.tree_density()
        assert density == pytest.approx(0.10)

    def test_count_trees(self):
        """Test tree counting."""
        sim = ForestFireSimulation(size=10, seed=42)

        # Set 25 trees
        for i in range(5):
            for j in range(5):
                sim.grid[i, j] = TREE

        assert sim.count_trees() == 25


class TestForestFireStatistics:
    """Tests for statistical properties."""

    def test_fire_distribution_empty(self):
        """Test distribution with no fires."""
        sim = ForestFireSimulation(size=10, seed=42)

        sizes, frequencies = sim.get_fire_distribution()

        assert sizes == []
        assert frequencies == []

    def test_fire_distribution_after_fires(self):
        """Test distribution after fires occur."""
        sim = ForestFireSimulation(size=50, tree_growth_prob=0.05, lightning_prob=0.01, seed=42)
        sim.run(1000, progress_interval=None)

        sizes, frequencies = sim.get_fire_distribution()

        if sim.fire_sizes:
            assert len(sizes) > 0
            assert len(frequencies) > 0
            assert all(f > 0 for f in frequencies)

    def test_tree_count_tracking(self):
        """Scenario: Tree count tracking."""
        sim = ForestFireSimulation(size=20, tree_growth_prob=0.1, lightning_prob=0.001, seed=42)

        # When I run the simulation for 100 steps
        sim.run(100, progress_interval=None)

        # Then tree count should be tracked at each step
        assert len(sim.tree_counts) == 100


class TestForestFireReproducibility:
    """Tests for reproducibility."""

    def test_reproducibility_with_seed(self):
        """Scenario: Reproducibility with seed."""
        # Given a random seed of 42
        sim1 = ForestFireSimulation(size=50, tree_growth_prob=0.01, lightning_prob=0.001, seed=42)
        sim2 = ForestFireSimulation(size=50, tree_growth_prob=0.01, lightning_prob=0.001, seed=42)

        # When I run the simulation for 500 steps
        sim1.run(500, progress_interval=None)
        sim2.run(500, progress_interval=None)

        # Then both runs should produce identical results
        assert np.array_equal(sim1.grid, sim2.grid)
        assert sim1.fire_sizes == sim2.fire_sizes
        assert sim1.tree_counts == sim2.tree_counts


class TestForestFireInitialization:
    """Tests for initialization."""

    def test_default_initialization(self):
        """Test default values."""
        sim = ForestFireSimulation()

        assert sim.size == 256
        assert sim.p == 0.01
        assert sim.f == 0.001  # p/10
        assert sim.timestep == 0
        assert len(sim.fire_sizes) == 0
        assert len(sim.tree_counts) == 0
        assert sim.grid.shape == (256, 256)
        assert np.all(sim.grid == EMPTY)

    def test_custom_initialization(self):
        """Test custom values."""
        sim = ForestFireSimulation(size=100, tree_growth_prob=0.05, lightning_prob=0.01, seed=123)

        assert sim.size == 100
        assert sim.p == 0.05
        assert sim.f == 0.01
        assert sim.grid.shape == (100, 100)

    def test_default_lightning_prob(self):
        """Test default lightning probability is p/10."""
        sim = ForestFireSimulation(size=50, tree_growth_prob=0.02)

        assert sim.f == 0.002  # 0.02 / 10


class TestForestFireStep:
    """Tests for step mechanics."""

    def test_timestep_increments(self):
        """Test that timestep increments correctly."""
        sim = ForestFireSimulation(size=10, seed=42)

        assert sim.timestep == 0

        sim.step()
        assert sim.timestep == 1

        sim.step()
        assert sim.timestep == 2

    def test_run_multiple_steps(self):
        """Test running multiple steps."""
        sim = ForestFireSimulation(size=10, seed=42)

        sim.run(100, progress_interval=None)

        assert sim.timestep == 100


# Hypothesis fuzz tests
class TestForestFireFuzz:
    """Fuzz tests using Hypothesis."""

    @given(st.integers(min_value=5, max_value=50))
    @settings(max_examples=10)
    def test_fuzz_grid_size(self, size):
        """Fuzz test: various grid sizes should work."""
        sim = ForestFireSimulation(size=size, seed=42)
        sim.run(50, progress_interval=None)

        # Grid should have valid cell states
        assert np.all((sim.grid == EMPTY) | (sim.grid == TREE) | (sim.grid == BURNING))
        assert sim.grid.shape == (size, size)

    @given(st.floats(min_value=0.001, max_value=0.5))
    @settings(max_examples=10)
    def test_fuzz_growth_probability(self, prob):
        """Fuzz test: various growth probabilities should work."""
        sim = ForestFireSimulation(size=20, tree_growth_prob=prob, seed=42)
        sim.run(50, progress_interval=None)

        # Density should be in valid range
        density = sim.tree_density()
        assert 0.0 <= density <= 1.0

    @given(st.integers(min_value=1, max_value=200))
    @settings(max_examples=10)
    def test_fuzz_num_steps(self, num_steps):
        """Fuzz test: various step counts should work."""
        sim = ForestFireSimulation(size=20, seed=42)
        sim.run(num_steps, progress_interval=None)

        assert sim.timestep == num_steps
        assert len(sim.tree_counts) == num_steps

    @given(st.integers(min_value=0, max_value=2**31-1))
    @settings(max_examples=10)
    def test_fuzz_random_seed(self, seed):
        """Fuzz test: various seeds should produce reproducible results."""
        sim1 = ForestFireSimulation(size=20, seed=seed)
        sim2 = ForestFireSimulation(size=20, seed=seed)

        sim1.run(50, progress_interval=None)
        sim2.run(50, progress_interval=None)

        assert np.array_equal(sim1.grid, sim2.grid)
        assert sim1.fire_sizes == sim2.fire_sizes
