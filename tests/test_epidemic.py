"""
Tests for the Epidemic Simulation module.
"""

import pytest
import numpy as np
import sys
sys.path.insert(0, 'code_files')

from epidemic import EpidemicSimulation, Agent, State


class TestAgentStates:
    """Tests for agent state transitions."""

    def test_agent_initial_state(self):
        """New agents should be susceptible."""
        agent = Agent(0, (0, 0))
        assert agent.state == State.SUSCEPTIBLE
        assert agent.is_susceptible()
        assert not agent.is_infectious()
        assert not agent.is_immune()

    def test_agent_infectious_state(self):
        """Infectious agents should be identified correctly."""
        agent = Agent(0, (0, 0))
        agent.state = State.INFECTIOUS
        assert agent.is_infectious()
        assert not agent.is_susceptible()
        assert not agent.is_immune()

    def test_agent_recovered_state(self):
        """Recovered agents should be immune."""
        agent = Agent(0, (0, 0))
        agent.state = State.RECOVERED
        assert agent.is_immune()
        assert not agent.is_susceptible()
        assert not agent.is_infectious()

    def test_agent_vaccinated_state(self):
        """Vaccinated agents should be immune."""
        agent = Agent(0, (0, 0))
        agent.state = State.VACCINATED
        assert agent.is_immune()
        assert not agent.is_susceptible()


class TestCitySetup:
    """Tests for city initialization."""

    def test_city_size(self):
        """City should have correct number of locations."""
        sim = EpidemicSimulation(city_size=10, seed=42)
        total_locations = len(sim.homes) + len(sim.non_homes)
        assert total_locations == 10 * 10

    def test_home_density(self):
        """Home density should be approximately correct."""
        sim = EpidemicSimulation(city_size=20, home_density=0.5, seed=42)
        actual_density = len(sim.homes) / (20 * 20)
        assert 0.45 <= actual_density <= 0.55

    def test_agents_per_home(self):
        """Each home should have correct number of agents."""
        sim = EpidemicSimulation(city_size=10, agents_per_home=3, seed=42)
        expected_agents = len(sim.homes) * 3
        assert len(sim.agents) == expected_agents


class TestInfectionMechanics:
    """Tests for disease transmission."""

    def test_initial_infections(self):
        """Simulation should start with correct number infected."""
        sim = EpidemicSimulation(initial_infected=5, seed=42)
        infectious_count = sum(1 for a in sim.agents if a.is_infectious())
        assert infectious_count == 5

    def test_infection_spreads(self):
        """Disease should spread with high infection probability."""
        sim = EpidemicSimulation(
            city_size=10,
            infection_prob=0.5,  # High probability
            infectious_days=5,
            initial_infected=5,
            seed=42
        )
        initial_susceptible = sim.history['susceptible'][0]

        sim.run(20)

        final_susceptible = sim.history['susceptible'][-1]
        # Disease should have spread
        assert final_susceptible < initial_susceptible

    def test_no_spread_with_zero_probability(self):
        """Disease should not spread with zero infection probability."""
        sim = EpidemicSimulation(
            city_size=10,
            infection_prob=0.0,
            infectious_days=2,
            initial_infected=5,
            seed=42
        )

        sim.run(10)

        # Only initial infections should have occurred
        total_infected = sim.history['recovered'][-1] + sim.history['infectious'][-1]
        assert total_infected <= 5

    def test_recovery_after_infectious_period(self):
        """Agents should recover after infectious period."""
        sim = EpidemicSimulation(
            city_size=10,
            infection_prob=0.0,  # No new infections
            infectious_days=2,
            initial_infected=5,
            seed=42
        )

        sim.run(5)

        # All initially infected should have recovered
        infectious_count = sim.history['infectious'][-1]
        assert infectious_count == 0


class TestVaccination:
    """Tests for vaccination mechanics."""

    def test_vaccination_changes_state(self):
        """Vaccination should change agents to vaccinated state."""
        sim = EpidemicSimulation(city_size=10, initial_infected=0, seed=42)
        initial_susceptible = sum(1 for a in sim.agents if a.is_susceptible())

        sim.vaccinate(0.5)

        final_susceptible = sum(1 for a in sim.agents if a.is_susceptible())
        vaccinated = sum(1 for a in sim.agents if a.state == State.VACCINATED)

        assert vaccinated > 0
        assert final_susceptible < initial_susceptible

    def test_vaccination_prevents_infection(self):
        """Vaccinated agents should not get infected."""
        sim = EpidemicSimulation(
            city_size=10,
            infection_prob=0.5,
            initial_infected=0,
            seed=42
        )

        # Vaccinate everyone
        sim.vaccinate(1.0)

        # Manually infect some agents (should not spread)
        sim.agents[0].state = State.INFECTIOUS

        sim.run(10)

        # Only the manually infected one should have been infected
        total_infected = sim.history['recovered'][-1] + sim.history['infectious'][-1]
        assert total_infected <= 1


class TestStatistics:
    """Tests for statistical calculations."""

    def test_get_counts(self):
        """State counts should sum to total population."""
        sim = EpidemicSimulation(city_size=10, seed=42)
        sim.run(5)

        s, i, r = sim.get_counts()
        assert s + i + r == sim.n_agents

    def test_get_fractions(self):
        """State fractions should sum to 1."""
        sim = EpidemicSimulation(city_size=10, seed=42)
        sim.run(5)

        s, i, r = sim.get_fractions()
        assert abs(s + i + r - 1.0) < 0.001

    def test_history_tracking(self):
        """History should track all days."""
        sim = EpidemicSimulation(city_size=10, seed=42)
        n_days = 15
        sim.run(n_days)

        assert len(sim.history['susceptible']) == n_days + 1  # +1 for initial state
        assert len(sim.history['infectious']) == n_days + 1
        assert len(sim.history['recovered']) == n_days + 1

    def test_new_infections_tracked(self):
        """New infections should be tracked daily."""
        sim = EpidemicSimulation(
            city_size=15,
            infection_prob=0.1,
            initial_infected=10,
            seed=42
        )
        sim.run(20)

        # Should have recorded new infections
        assert len(sim.history['new_infections']) == 20
        # At least some infections should have occurred
        assert sum(sim.history['new_infections']) > 0


class TestReproducibility:
    """Tests for reproducible results with seeds."""

    def test_reproducibility_with_seed(self):
        """Same seed should produce same results."""
        sim1 = EpidemicSimulation(city_size=15, infection_prob=0.05, seed=123)
        sim1.run(30)

        sim2 = EpidemicSimulation(city_size=15, infection_prob=0.05, seed=123)
        sim2.run(30)

        assert sim1.history['susceptible'] == sim2.history['susceptible']
        assert sim1.history['infectious'] == sim2.history['infectious']
        assert sim1.history['recovered'] == sim2.history['recovered']


class TestHerdImmunity:
    """Tests for herd immunity calculations."""

    def test_herd_immunity_formula(self):
        """Herd immunity threshold should follow 1 - 1/R0 formula."""
        # For R0 = 2.5, herd immunity should be 60%
        sim = EpidemicSimulation(city_size=10, seed=42)
        # Manually set R0 by creating agents with known infection counts
        for i, agent in enumerate(sim.agents[:10]):
            agent.state = State.RECOVERED
            agent.infected_by = 0
            agent.infections_caused = 2  # Each infected 2 others

        # R0 should be around 2, herd immunity around 50%
        r0 = sim.calculate_r0()
        herd = sim.get_herd_immunity_threshold()

        if r0 and r0 > 1:
            expected_herd = 1 - 1/r0
            assert abs(herd - expected_herd) < 0.01


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_zero_initial_infected(self):
        """Simulation should handle zero initial infections."""
        sim = EpidemicSimulation(initial_infected=0, seed=42)
        sim.run(10)

        # Should remain all susceptible
        assert sim.history['susceptible'][-1] == sim.n_agents
        assert sim.history['infectious'][-1] == 0

    def test_all_infected_initially(self):
        """Simulation should handle all agents infected initially."""
        sim = EpidemicSimulation(city_size=5, seed=42)
        n_agents = sim.n_agents

        # Infect all
        for agent in sim.agents:
            agent.state = State.INFECTIOUS
            agent.days_infectious = 0

        sim.run(5)

        # All should recover
        assert sim.history['recovered'][-1] == n_agents

    def test_small_city(self):
        """Simulation should work with minimal city size."""
        sim = EpidemicSimulation(city_size=3, initial_infected=1, seed=42)
        sim.run(10)

        s, i, r = sim.get_counts()
        assert s + i + r == sim.n_agents
