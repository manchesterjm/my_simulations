"""
Birthday Match Monte Carlo Simulation

Different from the birthday paradox! This asks:
How many people do you need in a room for the probability that
at least one person shares YOUR SPECIFIC birthday to exceed 50%?

The theoretical answer is 253 people (probability ≈ 50.05%).

This is much higher than 23 because we're matching against ONE specific
date rather than any matching pair.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple


DAYS_IN_YEAR = 365


def date_to_day_number(month: int, day: int) -> int:
    """Convert a date to day-of-year (0-indexed)."""
    days_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return sum(days_in_months[:month-1]) + day - 1


def day_number_to_date(day_num: int) -> str:
    """Convert day-of-year (0-indexed) to date string."""
    days_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    remaining = day_num
    for i, days in enumerate(days_in_months):
        if remaining < days:
            return f"{month_names[i]} {remaining + 1}"
        remaining -= days
    return f"Dec 31"


def simulate_match_probability(
    n_people: int,
    target_day: int,
    n_trials: int = 10000,
    seed: Optional[int] = None
) -> float:
    """
    Run Monte Carlo simulation to estimate probability that at least
    one person in the room shares a specific birthday.

    Args:
        n_people: Number of OTHER people in the room (not including you)
        target_day: Your birthday (0-364)
        n_trials: Number of simulation trials
        seed: Random seed for reproducibility

    Returns:
        Estimated probability of at least one match
    """
    if n_people <= 0:
        return 0.0

    rng = np.random.default_rng(seed)
    matches = 0

    for _ in range(n_trials):
        birthdays = rng.integers(0, DAYS_IN_YEAR, size=n_people)
        if target_day in birthdays:
            matches += 1

    return matches / n_trials


def theoretical_match_probability(n_people: int) -> float:
    """
    Calculate the exact theoretical probability that at least one
    person shares your specific birthday.

    P(at least one match) = 1 - P(no matches)
    P(no matches) = (364/365)^n
    """
    if n_people <= 0:
        return 0.0

    p_no_match = ((DAYS_IN_YEAR - 1) / DAYS_IN_YEAR) ** n_people
    return 1.0 - p_no_match


def find_threshold_group_size(
    target_probability: float = 0.5,
    target_day: int = 0,
    n_trials: int = 10000,
    seed: Optional[int] = None
) -> int:
    """
    Find the minimum group size where match probability exceeds target.

    Returns:
        Minimum number of OTHER people needed for probability > target
    """
    rng = np.random.default_rng(seed)

    for n in range(1, 1000):
        sub_seed = rng.integers(0, 2**31) if seed is not None else None
        prob = simulate_match_probability(n, target_day, n_trials, sub_seed)
        if prob > target_probability:
            return n

    return -1


def find_theoretical_threshold(target_probability: float = 0.5) -> int:
    """Find minimum n where theoretical probability exceeds target."""
    for n in range(1, 1000):
        if theoretical_match_probability(n) > target_probability:
            return n
    return -1


def run_probability_curve(
    target_day: int,
    max_people: int = 300,
    n_trials: int = 10000,
    seed: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate both simulated and theoretical probabilities for range of group sizes.
    """
    rng = np.random.default_rng(seed)
    group_sizes = np.arange(1, max_people + 1)
    simulated = []
    theoretical = []

    for n in group_sizes:
        sub_seed = rng.integers(0, 2**31) if seed is not None else None
        simulated.append(simulate_match_probability(n, target_day, n_trials, sub_seed))
        theoretical.append(theoretical_match_probability(n))

    return group_sizes, np.array(simulated), np.array(theoretical)


def plot_birthday_match(
    target_day: int,
    max_people: int = 300,
    n_trials: int = 10000,
    seed: Optional[int] = None
):
    """Create visualization of the birthday match problem."""
    sizes, simulated, theoretical = run_probability_curve(
        target_day, max_people, n_trials, seed
    )

    threshold = find_theoretical_threshold(0.5)
    date_str = day_number_to_date(target_day)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left plot: Probability curve
    ax1.plot(sizes, theoretical, 'b-', linewidth=2, label='Theoretical')
    ax1.scatter(sizes[::5], simulated[::5], c='red', s=20, alpha=0.6,
                label=f'Monte Carlo ({n_trials:,} trials)')
    ax1.axhline(y=0.5, color='green', linestyle='--', alpha=0.7, label='50% threshold')
    ax1.axvline(x=threshold, color='orange', linestyle='--', alpha=0.7,
                label=f'n={threshold}')

    ax1.set_xlabel('Number of Other People in Room', fontsize=12)
    ax1.set_ylabel(f'Probability Someone Shares {date_str}', fontsize=12)
    ax1.set_title(f'Birthday Match: P(someone shares {date_str})', fontsize=14)
    ax1.legend(loc='lower right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(1, max_people)
    ax1.set_ylim(0, 1)

    # Highlight the critical region
    ax1.fill_between(sizes, 0, theoretical, where=(sizes >= threshold),
                     alpha=0.2, color='orange')

    # Right plot: Comparison with birthday paradox
    from birthday_paradox import theoretical_probability as paradox_prob
    paradox_theory = [paradox_prob(n) for n in sizes]

    ax2.plot(sizes, theoretical, 'b-', linewidth=2, label=f'Match YOUR birthday ({date_str})')
    ax2.plot(sizes, paradox_theory, 'r-', linewidth=2, label='Any two share ANY birthday')
    ax2.axhline(y=0.5, color='green', linestyle='--', alpha=0.7)
    ax2.axvline(x=23, color='red', linestyle=':', alpha=0.7, label='n=23 (paradox)')
    ax2.axvline(x=threshold, color='blue', linestyle=':', alpha=0.7, label=f'n={threshold} (match)')

    ax2.set_xlabel('Number of People', fontsize=12)
    ax2.set_ylabel('Probability', fontsize=12)
    ax2.set_title('Birthday Paradox vs Birthday Match', fontsize=14)
    ax2.legend(loc='right')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(1, max_people)
    ax2.set_ylim(0, 1)

    plt.tight_layout()
    return fig


def run_demo(
    target_month: int = 7,
    target_day: int = 11,
    n_trials: int = 10000,
    seed: Optional[int] = None
):
    """Run a demonstration of the birthday match problem."""
    target = date_to_day_number(target_month, target_day)
    date_str = day_number_to_date(target)
    threshold = find_theoretical_threshold(0.5)

    print("=" * 65)
    print("        BIRTHDAY MATCH - Monte Carlo Simulation")
    print("=" * 65)
    print()
    print(f"Question: How many people need to be in a room for the")
    print(f"          probability that someone shares YOUR birthday ({date_str})")
    print(f"          to exceed 50%?")
    print()
    print("This is DIFFERENT from the birthday paradox!")
    print("  - Paradox: Any two people share ANY birthday (answer: 23)")
    print(f"  - Match:   Someone shares YOUR specific birthday (answer: {threshold})")
    print()

    # Show some key probabilities
    print(f"Running {n_trials:,} trials per group size...")
    print()
    print("People in Room | Simulated | Theoretical | Difference")
    print("-" * 60)

    rng = np.random.default_rng(seed)
    key_sizes = [23, 50, 100, 150, 200, 250, 252, 253, 254, 255, 300, 365]

    for n in key_sizes:
        sub_seed = rng.integers(0, 2**31) if seed is not None else None
        sim_prob = simulate_match_probability(n, target, n_trials, sub_seed)
        theory_prob = theoretical_match_probability(n)
        diff = abs(sim_prob - theory_prob) * 100

        marker = " <-- 50% threshold!" if n == threshold else ""
        if n == 23:
            marker = " (birthday paradox answer)"
        print(f"      {n:3d}      |   {sim_prob:.1%}   |    {theory_prob:.1%}    |   {diff:.2f}%{marker}")

    print()
    print("=" * 65)
    print(f"ANSWER: {threshold} people gives a {theoretical_match_probability(threshold):.2%} probability")
    print(f"        that someone shares your birthday ({date_str})!")
    print("=" * 65)
    print()
    print("Why so many more than 23?")
    print("  - Birthday paradox: Compare ALL pairs = n*(n-1)/2 comparisons")
    print(f"    With 23 people: 253 pairs to check")
    print("  - Birthday match: Only compare against YOUR one date")
    print(f"    Need ~253 people to get 253 independent chances!")
    print()
    print(f"The math: P(no match) = (364/365)^n")
    print(f"          Solve for P(match) > 0.5:")
    print(f"          n > ln(0.5) / ln(364/365) = {-np.log(0.5) / np.log(364/365):.1f}")

    # Show the visualization
    plot_birthday_match(target, max_people=300, n_trials=n_trials, seed=seed)
    plt.show()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Birthday Match Monte Carlo Simulation")
    parser.add_argument("--trials", type=int, default=10000,
                        help="Number of Monte Carlo trials per group size")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    parser.add_argument("--month", type=int, default=7,
                        help="Your birth month (1-12)")
    parser.add_argument("--day", type=int, default=11,
                        help="Your birth day (1-31)")

    args = parser.parse_args()
    run_demo(
        target_month=args.month,
        target_day=args.day,
        n_trials=args.trials,
        seed=args.seed
    )
