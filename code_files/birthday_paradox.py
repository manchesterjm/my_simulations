"""
Birthday Paradox Monte Carlo Simulation

Simulates the famous birthday problem: What is the minimum number of people
needed in a room for the probability of at least two sharing a birthday
to exceed 50%?

The theoretical answer is 23 people (probability ≈ 50.73%).

This uses Monte Carlo simulation to empirically verify this result.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Optional, Tuple


DAYS_IN_YEAR = 365


def has_birthday_collision(birthdays: List[int]) -> bool:
    """Check if any two people share a birthday."""
    return len(birthdays) != len(set(birthdays))


def generate_birthdays(n_people: int, seed: Optional[int] = None) -> List[int]:
    """Generate random birthdays for n people (0-364)."""
    rng = np.random.default_rng(seed)
    return list(rng.integers(0, DAYS_IN_YEAR, size=n_people))


def simulate_birthday_probability(
    n_people: int,
    n_trials: int = 10000,
    seed: Optional[int] = None
) -> float:
    """
    Run Monte Carlo simulation to estimate probability of shared birthday.

    Args:
        n_people: Number of people in the room
        n_trials: Number of simulation trials
        seed: Random seed for reproducibility

    Returns:
        Estimated probability of at least two people sharing a birthday
    """
    if n_people <= 1:
        return 0.0
    if n_people >= DAYS_IN_YEAR + 1:
        return 1.0

    rng = np.random.default_rng(seed)
    collisions = 0

    for _ in range(n_trials):
        birthdays = rng.integers(0, DAYS_IN_YEAR, size=n_people)
        if len(birthdays) != len(set(birthdays)):
            collisions += 1

    return collisions / n_trials


def theoretical_probability(n_people: int) -> float:
    """
    Calculate the exact theoretical probability of a birthday collision.

    P(collision) = 1 - P(no collision)
    P(no collision) = (365/365) × (364/365) × (363/365) × ... × ((365-n+1)/365)
    """
    if n_people <= 1:
        return 0.0
    if n_people >= DAYS_IN_YEAR + 1:
        return 1.0

    # Calculate probability of NO collision
    p_no_collision = 1.0
    for i in range(n_people):
        p_no_collision *= (DAYS_IN_YEAR - i) / DAYS_IN_YEAR

    return 1.0 - p_no_collision


def find_threshold_group_size(
    target_probability: float = 0.5,
    n_trials: int = 10000,
    seed: Optional[int] = None
) -> int:
    """
    Find the minimum group size where collision probability exceeds target.

    Args:
        target_probability: Target probability threshold (default 0.5)
        n_trials: Number of trials per group size
        seed: Random seed

    Returns:
        Minimum number of people for probability > target
    """
    rng = np.random.default_rng(seed)

    for n in range(2, DAYS_IN_YEAR + 2):
        # Use a fresh seed derived from main seed for each n
        sub_seed = rng.integers(0, 2**31) if seed is not None else None
        prob = simulate_birthday_probability(n, n_trials, sub_seed)
        if prob > target_probability:
            return n

    return DAYS_IN_YEAR + 1


def run_probability_curve(
    max_people: int = 60,
    n_trials: int = 10000,
    seed: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate both simulated and theoretical probabilities for range of group sizes.

    Returns:
        Tuple of (group_sizes, simulated_probs, theoretical_probs)
    """
    rng = np.random.default_rng(seed)
    group_sizes = np.arange(1, max_people + 1)
    simulated = []
    theoretical = []

    for n in group_sizes:
        sub_seed = rng.integers(0, 2**31) if seed is not None else None
        simulated.append(simulate_birthday_probability(n, n_trials, sub_seed))
        theoretical.append(theoretical_probability(n))

    return group_sizes, np.array(simulated), np.array(theoretical)


def plot_birthday_paradox(
    max_people: int = 60,
    n_trials: int = 10000,
    seed: Optional[int] = None
):
    """Create visualization of the birthday paradox."""
    sizes, simulated, theoretical = run_probability_curve(max_people, n_trials, seed)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left plot: Probability curve
    ax1.plot(sizes, theoretical, 'b-', linewidth=2, label='Theoretical')
    ax1.scatter(sizes, simulated, c='red', s=20, alpha=0.6, label=f'Monte Carlo ({n_trials:,} trials)')
    ax1.axhline(y=0.5, color='green', linestyle='--', alpha=0.7, label='50% threshold')
    ax1.axvline(x=23, color='orange', linestyle='--', alpha=0.7, label='n=23')

    ax1.set_xlabel('Number of People', fontsize=12)
    ax1.set_ylabel('Probability of Shared Birthday', fontsize=12)
    ax1.set_title('Birthday Paradox: Probability vs Group Size', fontsize=14)
    ax1.legend(loc='lower right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(1, max_people)
    ax1.set_ylim(0, 1)

    # Highlight the critical region
    ax1.fill_between(sizes, 0, theoretical, where=(sizes >= 23), alpha=0.2, color='orange')

    # Right plot: Error between simulation and theory
    error = np.abs(simulated - theoretical) * 100
    ax2.bar(sizes, error, color='purple', alpha=0.6)
    ax2.set_xlabel('Number of People', fontsize=12)
    ax2.set_ylabel('Absolute Error (%)', fontsize=12)
    ax2.set_title('Monte Carlo vs Theoretical Error', fontsize=14)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def run_demo(n_trials: int = 10000, seed: Optional[int] = None):
    """Run a demonstration of the birthday paradox."""
    print("=" * 60)
    print("        BIRTHDAY PARADOX - Monte Carlo Simulation")
    print("=" * 60)
    print()
    print("Question: What's the minimum number of people needed for")
    print("          the probability of a shared birthday to exceed 50%?")
    print()

    # Show some key probabilities
    print(f"Running {n_trials:,} trials per group size...")
    print()
    print("Group Size | Simulated | Theoretical | Difference")
    print("-" * 55)

    rng = np.random.default_rng(seed)
    key_sizes = [5, 10, 15, 20, 22, 23, 24, 25, 30, 40, 50]

    for n in key_sizes:
        sub_seed = rng.integers(0, 2**31) if seed is not None else None
        sim_prob = simulate_birthday_probability(n, n_trials, sub_seed)
        theory_prob = theoretical_probability(n)
        diff = abs(sim_prob - theory_prob) * 100

        marker = " <-- 50% threshold!" if n == 23 else ""
        print(f"    {n:3d}    |   {sim_prob:.1%}   |    {theory_prob:.1%}    |   {diff:.2f}%{marker}")

    print()
    print("=" * 60)
    print("ANSWER: 23 people gives a 50.73% probability of a match!")
    print("=" * 60)
    print()
    print("This is counterintuitive because we compare against ALL other")
    print("birthdays, not just one specific date. With 23 people, there")
    print(f"are {23 * 22 // 2} = C(23,2) possible pairs to compare!")

    # Show the visualization
    plot_birthday_paradox(max_people=60, n_trials=n_trials, seed=seed)
    plt.show()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Birthday Paradox Monte Carlo Simulation")
    parser.add_argument("--trials", type=int, default=10000,
                        help="Number of Monte Carlo trials per group size")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    parser.add_argument("--find-threshold", action="store_true",
                        help="Find the exact threshold via simulation")

    args = parser.parse_args()

    if args.find_threshold:
        print(f"Searching for 50%% threshold with {args.trials:,} trials...")
        threshold = find_threshold_group_size(0.5, args.trials, args.seed)
        print(f"Found: {threshold} people")
    else:
        run_demo(n_trials=args.trials, seed=args.seed)
