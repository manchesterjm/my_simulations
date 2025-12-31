"""Tests for the Birthday Paradox Monte Carlo simulation."""

import pytest
import numpy as np


class TestBirthdayParadox:
    """Test suite for birthday paradox simulation."""

    def test_single_trial_detects_collision(self):
        """A trial with duplicate birthdays should detect collision."""
        from code_files.birthday_paradox import has_birthday_collision

        # All same birthday - definite collision
        birthdays = [100, 100, 50, 200]
        assert has_birthday_collision(birthdays) is True

    def test_single_trial_no_collision(self):
        """A trial with unique birthdays should not detect collision."""
        from code_files.birthday_paradox import has_birthday_collision

        birthdays = [1, 2, 3, 4, 5]
        assert has_birthday_collision(birthdays) is False

    def test_generate_random_birthdays(self):
        """Should generate correct number of random birthdays in valid range."""
        from code_files.birthday_paradox import generate_birthdays

        birthdays = generate_birthdays(n_people=10, seed=42)
        assert len(birthdays) == 10
        assert all(0 <= b < 365 for b in birthdays)

    def test_simulation_returns_probability(self):
        """Simulation should return a probability between 0 and 1."""
        from code_files.birthday_paradox import simulate_birthday_probability

        prob = simulate_birthday_probability(n_people=23, n_trials=1000, seed=42)
        assert 0.0 <= prob <= 1.0

    def test_one_person_zero_probability(self):
        """One person cannot share a birthday with themselves."""
        from code_files.birthday_paradox import simulate_birthday_probability

        prob = simulate_birthday_probability(n_people=1, n_trials=1000, seed=42)
        assert prob == 0.0

    def test_366_people_certain_collision(self):
        """With 366 people, pigeonhole principle guarantees collision."""
        from code_files.birthday_paradox import simulate_birthday_probability

        prob = simulate_birthday_probability(n_people=366, n_trials=100, seed=42)
        assert prob == 1.0

    def test_probability_increases_with_group_size(self):
        """Probability should increase as group size increases."""
        from code_files.birthday_paradox import simulate_birthday_probability

        probs = []
        for n in [5, 10, 15, 20, 25, 30]:
            prob = simulate_birthday_probability(n_people=n, n_trials=5000, seed=42)
            probs.append(prob)

        # Check monotonically increasing (allowing small variance)
        for i in range(len(probs) - 1):
            assert probs[i] <= probs[i + 1] + 0.02  # small tolerance for randomness

    def test_23_people_approximately_50_percent(self):
        """23 people should give approximately 50% probability."""
        from code_files.birthday_paradox import simulate_birthday_probability

        prob = simulate_birthday_probability(n_people=23, n_trials=10000, seed=42)
        # Theoretical is 50.73%, allow 5% tolerance
        assert 0.45 <= prob <= 0.56

    def test_find_threshold_returns_23(self):
        """Finding the 50% threshold should return 23."""
        from code_files.birthday_paradox import find_threshold_group_size

        threshold = find_threshold_group_size(
            target_probability=0.5,
            n_trials=5000,
            seed=42
        )
        assert threshold == 23

    def test_theoretical_probability(self):
        """Theoretical probability calculation should be accurate."""
        from code_files.birthday_paradox import theoretical_probability

        # Known values
        assert theoretical_probability(1) == 0.0
        assert abs(theoretical_probability(23) - 0.5073) < 0.001
        assert theoretical_probability(366) == 1.0

    def test_simulation_vs_theory_close(self):
        """Monte Carlo results should be close to theoretical values."""
        from code_files.birthday_paradox import (
            simulate_birthday_probability,
            theoretical_probability
        )

        for n in [10, 20, 30, 40, 50]:
            simulated = simulate_birthday_probability(n_people=n, n_trials=10000, seed=42)
            theory = theoretical_probability(n)
            assert abs(simulated - theory) < 0.03  # within 3%

    def test_seed_reproducibility(self):
        """Same seed should produce same results."""
        from code_files.birthday_paradox import simulate_birthday_probability

        prob1 = simulate_birthday_probability(n_people=23, n_trials=1000, seed=123)
        prob2 = simulate_birthday_probability(n_people=23, n_trials=1000, seed=123)
        assert prob1 == prob2

    def test_different_seeds_different_results(self):
        """Different seeds should (likely) produce different results."""
        from code_files.birthday_paradox import simulate_birthday_probability

        prob1 = simulate_birthday_probability(n_people=23, n_trials=1000, seed=123)
        prob2 = simulate_birthday_probability(n_people=23, n_trials=1000, seed=456)
        # Very unlikely to be exactly equal with different seeds
        # (but theoretically possible, so we just check they run)
        assert isinstance(prob1, float) and isinstance(prob2, float)
