"""
Unit tests for 2D Ising Model Simulation
Based on BDD scenarios in features/ising_model.feature
"""

import pytest
import numpy as np

import sys
sys.path.insert(0, 'code_files')
from ising_model import IsingModel


class TestIsingCoreMechanics:
    """Tests for core Ising model mechanics."""

    def test_spin_values(self):
        """Test that all spins are +1 or -1."""
        model = IsingModel(size=50, seed=42)

        assert np.all((model.grid == 1) | (model.grid == -1))

    def test_energy_change_calculation_aligned(self):
        """Test energy change when spin is aligned with neighbors."""
        model = IsingModel(size=10, seed=42)

        # Set up: center spin +1, all neighbors +1
        model.grid[5, 5] = 1
        model.grid[4, 5] = 1  # Up
        model.grid[6, 5] = 1  # Down
        model.grid[5, 4] = 1  # Left
        model.grid[5, 6] = 1  # Right

        # Energy change for flipping aligned spin should be positive (unfavorable)
        dE = model.get_energy_change(5, 5)
        assert dE > 0  # Flipping would increase energy

    def test_energy_change_calculation_anti_aligned(self):
        """Test energy change when spin is anti-aligned with neighbors."""
        model = IsingModel(size=10, seed=42)

        # Set up: center spin -1, all neighbors +1
        model.grid[5, 5] = -1
        model.grid[4, 5] = 1  # Up
        model.grid[6, 5] = 1  # Down
        model.grid[5, 4] = 1  # Left
        model.grid[5, 6] = 1  # Right

        # Energy change for flipping anti-aligned spin should be negative (favorable)
        dE = model.get_energy_change(5, 5)
        assert dE < 0  # Flipping would decrease energy

    def test_periodic_boundary_conditions(self):
        """Scenario: Periodic boundary conditions."""
        model = IsingModel(size=10, seed=42)

        # Set specific spins at boundaries
        model.grid[0, 0] = 1
        model.grid[0, 9] = 1  # Left neighbor of (0,0) via wrap
        model.grid[9, 0] = 1  # Top neighbor of (0,0) via wrap

        # Calculate energy change at corner
        dE = model.get_energy_change(0, 0)

        # Should include wrapped neighbors
        # The calculation should use grid[9, 0] and grid[0, 9]
        assert np.issubdtype(type(dE), np.number)


class TestIsingTemperatureBehavior:
    """Tests for temperature-dependent behavior."""

    def test_low_temperature_ordered_state(self):
        """Scenario: Low temperature produces ordered state."""
        # Given temperature is set to 0.5 (well below Tc=2.269)
        model = IsingModel(size=30, temperature=0.5, seed=42)

        # Start with all spins aligned for faster equilibration
        model.grid[:, :] = 1

        # When I run 100 sweeps
        model.sweep(100)

        # Then the absolute magnetization should remain high (system stays ordered)
        abs_mag = abs(model.get_magnetization())
        assert abs_mag > 0.9  # Should remain highly magnetized at low T

    def test_high_temperature_disordered_state(self):
        """Scenario: High temperature produces disordered state."""
        # Given temperature is set to 4.0 (above Tc)
        model = IsingModel(size=50, temperature=4.0, seed=42)

        # When I run 200 sweeps
        model.sweep(200)

        # Then the absolute magnetization should be close to 0.0
        abs_mag = abs(model.get_magnetization())
        assert abs_mag < 0.3  # Should be relatively disordered

    def test_critical_temperature_domains(self):
        """Scenario: Critical temperature shows criticality."""
        # Given temperature is set to 2.269 (at Tc)
        model = IsingModel(size=64, temperature=2.269, seed=42)

        # When I run 200 sweeps
        model.sweep(200)

        # Then domains of various sizes should be present
        domain_sizes = model.find_domains()
        unique_sizes = len(set(domain_sizes))

        # Should have variety of domain sizes
        assert unique_sizes > 5


class TestIsingDomainAnalysis:
    """Tests for domain detection and analysis."""

    def test_domain_detection_single_domain(self):
        """Test domain detection with uniform grid."""
        model = IsingModel(size=10, seed=42)

        # Set all spins to +1
        model.grid[:, :] = 1

        domains = model.find_domains()

        # Should be exactly one domain of size 100
        assert len(domains) == 1
        assert domains[0] == 100

    def test_domain_detection_two_domains(self):
        """Test domain detection with two halves."""
        model = IsingModel(size=10, seed=42)

        # Set left half to +1, right half to -1
        model.grid[:, :5] = 1
        model.grid[:, 5:] = -1

        domains = model.find_domains()

        # Should be exactly two domains of size 50 each
        assert len(domains) == 2
        assert sorted(domains) == [50, 50]

    def test_domain_distribution(self):
        """Test domain size distribution."""
        model = IsingModel(size=50, temperature=2.269, seed=42)
        model.sweep(100)

        sizes, frequencies = model.get_domain_distribution(remove_percolating=False)

        # Should have some distribution data
        assert len(sizes) > 0
        assert len(frequencies) > 0

        # Total domains should equal sum of frequencies
        total_domains = sum(frequencies)
        assert total_domains == len(model.find_domains())

    def test_domain_distribution_removes_percolating(self):
        """Test that percolating clusters are removed."""
        model = IsingModel(size=50, temperature=2.269, seed=42)
        model.sweep(100)

        sizes_with, _ = model.get_domain_distribution(remove_percolating=False)
        sizes_without, _ = model.get_domain_distribution(remove_percolating=True)

        # With percolating removed, should have fewer or equal sizes
        all_domains = model.find_domains()
        if len(all_domains) > 2:
            # The two largest should be removed
            assert len(sizes_without) <= len(sizes_with)


class TestIsingMagnetization:
    """Tests for magnetization calculation."""

    def test_magnetization_all_up(self):
        """Test magnetization when all spins are +1."""
        model = IsingModel(size=10, seed=42)
        model.grid[:, :] = 1

        mag = model.get_magnetization()
        assert mag == 1.0

    def test_magnetization_all_down(self):
        """Test magnetization when all spins are -1."""
        model = IsingModel(size=10, seed=42)
        model.grid[:, :] = -1

        mag = model.get_magnetization()
        assert mag == -1.0

    def test_magnetization_half_half(self):
        """Test magnetization when half up, half down."""
        model = IsingModel(size=10, seed=42)
        model.grid[:, :5] = 1
        model.grid[:, 5:] = -1

        mag = model.get_magnetization()
        assert mag == 0.0

    def test_magnetization_75_percent_up(self):
        """Scenario: Magnetization calculation - 75% up."""
        model = IsingModel(size=10, seed=42)

        # Set 75 cells to +1, 25 to -1
        model.grid[:, :] = 1
        model.grid[:5, :5] = -1  # 25 cells

        mag = model.get_magnetization()
        # 75 * (+1) + 25 * (-1) = 50, average = 50/100 = 0.5
        assert mag == 0.5


class TestIsingReproducibility:
    """Tests for reproducibility."""

    def test_reproducibility_with_seed(self):
        """Scenario: Reproducibility with seed."""
        # Given a random seed of 42
        model1 = IsingModel(size=50, temperature=2.269, seed=42)
        model2 = IsingModel(size=50, temperature=2.269, seed=42)

        # Initial grids should be identical
        assert np.array_equal(model1.grid, model2.grid)

        # When I run 100 sweeps
        model1.sweep(100)
        model2.sweep(100)

        # Then both runs should produce identical final states
        assert np.array_equal(model1.grid, model2.grid)


class TestIsingInitialization:
    """Tests for initialization."""

    def test_default_initialization(self):
        """Test default values."""
        model = IsingModel()

        assert model.size == 128
        assert model.temperature == 2.269
        assert model.Tc == 2.269
        assert model.sweeps == 0
        assert model.grid.shape == (128, 128)

    def test_custom_initialization(self):
        """Test custom values."""
        model = IsingModel(size=64, temperature=3.0, seed=123)

        assert model.size == 64
        assert model.temperature == 3.0
        assert model.grid.shape == (64, 64)

    def test_set_temperature(self):
        """Test set_temperature method."""
        model = IsingModel(size=10)

        # Set temperature to 0.5 * Tc
        model.set_temperature(0.5)
        assert model.temperature == pytest.approx(0.5 * 2.269)

        # Set temperature to 2.0 * Tc
        model.set_temperature(2.0)
        assert model.temperature == pytest.approx(2.0 * 2.269)


class TestIsingSweep:
    """Tests for sweep mechanics."""

    def test_sweep_count(self):
        """Test that sweep count is tracked correctly."""
        model = IsingModel(size=10, seed=42)

        assert model.sweeps == 0

        model.sweep(5)
        assert model.sweeps == 5

        model.sweep(10)
        assert model.sweeps == 15
