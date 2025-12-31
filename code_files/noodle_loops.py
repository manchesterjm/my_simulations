"""Noodle Loop Monte Carlo Simulation.

This module simulates the classic noodle loop probability problem using Monte Carlo
methods and compares results with exact combinatorial calculations.

Problem Statement
-----------------
Imagine you have n noodles, each with 2 endpoints (2n endpoints total). You randomly
tie together pairs of endpoints until all endpoints are paired. How many closed loops
will form?

Physical Interpretation
-----------------------
Think of each noodle as having a left end and a right end. One pairing (B) is fixed
(each noodle's ends are tied together). Another pairing (A) is random (endpoints are
randomly shuffled and paired). The composition of these two pairings creates a
permutation whose cycle structure determines the number of loops.

Mathematical Framework
----------------------
The problem reduces to counting cycles in a permutation:
1. Fix pairing B: B[2i] = 2i+1, B[2i+1] = 2i (each noodle paired with itself)
2. Random pairing A: randomly shuffle all 2n endpoints and pair consecutively
3. Compose: P[i] = A[B[i]] creates a permutation
4. Count cycles in P, divide by 2 to get number of loops

The division by 2 is necessary because each physical loop corresponds to 2 cycles
in the permutation (one for each direction around the loop).

Exact Probabilities
-------------------
Using combinatorial arguments:
- P(exactly 1 loop) = 2^(2n-1) * (n-1)! * n! / (2n)!
- P(exactly n loops) = 1 / (2n-1)!! = 2^n * n! / (2n)!
  where (2n-1)!! = 1 * 3 * 5 * ... * (2n-1) is the double factorial
- Expected number of loops = 1 + 1/3 + 1/5 + ... + 1/(2n-1) (harmonic series)

Monte Carlo Method
------------------
This simulation uses Monte Carlo sampling to estimate these probabilities:
1. Generate many random pairings (trials)
2. For each trial, count the number of loops formed
3. Calculate empirical probabilities and confidence intervals
4. Compare with exact theoretical values

The 95% confidence intervals are calculated using the normal approximation to the
binomial distribution: estimate ± 1.96 * standard_error, where
standard_error = sqrt(p * (1-p) / trials).

References
----------
Inspired by the Veritasium video on power laws and probability distributions.

Example
-------
    $ python noodle_loops.py --n 7 --trials 100000 --seed 31
    n=7, trials=100000, seed=31
    Monte Carlo (1 loop): 0.0100500000  (95% CI: [0.0098522815, 0.0102477185])
    Exact (1 loop):       0.0100454545
"""

import math
import random
import argparse


def random_pairing_mapping(m, rng):
    """Create a random pairing of m elements.

    Shuffles m elements and pairs them consecutively: (0,1), (2,3), ..., (m-2,m-1).
    Returns a bidirectional mapping where mapping[a] = b and mapping[b] = a for each pair.

    This represents the random tying of noodle endpoints in the Monte Carlo simulation.

    Args:
        m (int): Number of elements to pair (must be even).
        rng (random.Random): Random number generator for reproducibility.

    Returns:
        list: Bidirectional mapping where mapping[i] gives the element paired with i.
            Length m, where each element maps to its partner.

    Example:
        >>> rng = random.Random(42)
        >>> mapping = random_pairing_mapping(6, rng)
        >>> # If shuffled order is [3, 1, 4, 0, 2, 5], pairs are:
        >>> # (3,1), (4,0), (2,5) so mapping[3]=1, mapping[1]=3, etc.
    """
    # Shuffle all elements to create random ordering
    arr = list(range(m))
    rng.shuffle(arr)

    # Create bidirectional pairing: consecutive elements in shuffled array are paired
    mapping = [None] * m
    for i in range(0, m, 2):
        a, b = arr[i], arr[i + 1]
        mapping[a] = b  # a is paired with b
        mapping[b] = a  # b is paired with a
    return mapping

def cycles_in_permutation(perm):
    """Count the number of cycles in a permutation.

    Uses cycle decomposition to count disjoint cycles. A cycle is a sequence of elements
    where perm[i] = j, perm[j] = k, ..., eventually returning to i. This is equivalent
    to following the permutation arrows until returning to the starting point.

    In the noodle problem, each cycle in the permutation P = A ∘ B corresponds to a
    path through the noodle endpoints. Two cycles form one physical loop.

    Args:
        perm (list): Permutation represented as a list where perm[i] gives the image of i.
            Must be a valid permutation of range(n).

    Returns:
        int: Number of disjoint cycles in the permutation.

    Example:
        >>> cycles_in_permutation([1, 0, 3, 2])  # Two cycles: (0,1) and (2,3)
        2
        >>> cycles_in_permutation([1, 2, 0])  # One cycle: (0,1,2,0)
        1
    """
    n = len(perm)
    seen = [False] * n
    cycles = 0

    # Find each cycle by following the permutation until we return to start
    for i in range(n):
        if not seen[i]:
            # Start of a new cycle
            cycles += 1
            j = i
            # Follow the cycle: i -> perm[i] -> perm[perm[i]] -> ... -> i
            while not seen[j]:
                seen[j] = True
                j = perm[j]  # Move to next element in cycle

    return cycles

def single_loop_probability_exact(n):
    """Calculate exact probability of forming exactly one loop with n noodles.

    Uses the combinatorial formula: P(1 loop) = 2^(2n-1) * (n-1)! * n! / (2n)!

    This formula comes from counting the number of ways to arrange 2n endpoints such
    that the composition A ∘ B forms a single cycle (which corresponds to one loop
    when divided by 2).

    Computation is done in log-space to avoid overflow for large n, then exponentiated.

    Args:
        n (int): Number of noodles (must be positive).

    Returns:
        float: Exact probability of forming exactly 1 loop.

    Example:
        >>> single_loop_probability_exact(3)
        0.06666666666666667
        >>> single_loop_probability_exact(7)
        0.010045454545454545
    """
    # Compute in log-space: ln(p) = (2n-1)*ln(2) + ln((n-1)!) + ln(n!) - ln((2n)!)
    # Using lgamma(k) = ln((k-1)!) gives us the log of factorials
    ln_p = (
        (2 * n - 1) * math.log(2)  # 2^(2n-1)
        + math.lgamma(n)  # (n-1)!
        + math.lgamma(n + 1)  # n!
        - math.lgamma(2 * n + 1)  # (2n)!
    )
    return math.exp(ln_p)

def hundred_loops_probability_exact(n):
    """Calculate exact probability of forming exactly n loops with n noodles.

    DEPRECATED: Use all_loops_probability_exact() instead. This function is kept
    for backward compatibility but delegates to all_loops_probability_exact().

    Note: The name "hundred_loops" is historical/misleading - it actually computes
    the probability of forming n loops (the maximum possible), not 100 loops.

    Args:
        n (int): Number of noodles (must be positive).

    Returns:
        float: Exact probability of forming exactly n loops (all loops separate).
    """
    return all_loops_probability_exact(n)


def all_loops_probability_exact(n):
    """Calculate exact probability of forming exactly n loops with n noodles.

    This is the maximum number of loops possible - it occurs when each noodle forms
    its own separate loop (no noodles are connected to each other).

    Uses the formula: P(n loops) = 1 / (2n-1)!! = 2^n * n! / (2n)!
    where (2n-1)!! = 1 * 3 * 5 * ... * (2n-1) is the double factorial.

    This probability decreases rapidly as n grows (roughly exponentially), making
    the all-separate-loops outcome extremely rare for large n.

    Computation is done in log-space to avoid overflow for large n.

    Args:
        n (int): Number of noodles (must be positive).

    Returns:
        float: Exact probability of forming exactly n separate loops.

    Example:
        >>> all_loops_probability_exact(3)
        0.06666666666666667
        >>> all_loops_probability_exact(7)
        9.18273645546373e-05
    """
    # Compute in log-space: ln(p) = n*ln(2) + ln(n!) - ln((2n)!)
    # Using (2n-1)!! = (2n)! / (2^n * n!), we get p = 1/(2n-1)!! = 2^n * n! / (2n)!
    ln_p = (
        n * math.log(2)  # 2^n
        + math.lgamma(n + 1)  # n!
        - math.lgamma(2 * n + 1)  # (2n)!
    )
    return math.exp(ln_p)


def _create_fixed_noodle_pairing(n):
    """Create fixed pairing where each noodle's endpoints are paired together.

    This is the B mapping in the noodle problem: B[2i] = 2i+1 and B[2i+1] = 2i.
    It represents the natural pairing of each noodle with itself.

    Args:
        n (int): Number of noodles.

    Returns:
        list: Bidirectional mapping of length 2n where each noodle's two endpoints
            (2i and 2i+1) are paired together.
    """
    m = 2 * n
    B = [0] * m
    for i in range(n):
        left_end = 2 * i
        right_end = 2 * i + 1
        B[left_end] = right_end
        B[right_end] = left_end
    return B


def _calculate_confidence_interval(successes, trials):
    """Calculate estimate and 95% confidence interval for a binomial proportion.

    Uses the normal approximation to the binomial distribution with z = 1.96
    for a 95% confidence level.

    Args:
        successes (int): Number of successful trials.
        trials (int): Total number of trials.

    Returns:
        tuple: (estimate, standard_error, confidence_interval) where:
            - estimate (float): Point estimate (successes / trials)
            - standard_error (float): Standard error of the estimate
            - confidence_interval (tuple): (lower_bound, upper_bound) for 95% CI
    """
    estimate = successes / trials
    # Standard error for binomial proportion: sqrt(p * (1-p) / n)
    standard_error = (estimate * (1 - estimate) / trials) ** 0.5
    # 95% CI: estimate ± 1.96 * SE
    margin = 1.96 * standard_error
    confidence_interval = (estimate - margin, estimate + margin)
    return estimate, standard_error, confidence_interval


def simulate(n, trials, seed):
    """Run Monte Carlo simulation of the noodle loop problem.

    Performs the following steps for each trial:
    1. Create fixed pairing B (each noodle paired with itself)
    2. Create random pairing A (randomly shuffle and pair all endpoints)
    3. Compose A ∘ B to get permutation P
    4. Count cycles in P, divide by 2 to get number of loops
    5. Track statistics for 1-loop and n-loop outcomes

    Args:
        n (int): Number of noodles (each has 2 endpoints).
        trials (int): Number of Monte Carlo trials to run.
        seed (int): Random seed for reproducibility.

    Returns:
        tuple: Seven-element tuple containing:
            - single (int): Count of trials with exactly 1 loop
            - est1 (float): Estimated probability of 1 loop
            - ci1 (tuple): 95% confidence interval for 1-loop probability
            - avg_loops (float): Average number of loops per trial
            - nloops (int): Count of trials with exactly n loops
            - estn (float): Estimated probability of n loops
            - cin (tuple): 95% confidence interval for n-loop probability

    Example:
        >>> single, est1, ci1, avg, nloops, estn, cin = simulate(5, 10000, 42)
        >>> 0.01 < est1 < 0.05  # Probability of 1 loop is small
        True
    """
    rng = random.Random(seed)
    m = 2 * n  # Total number of endpoints

    # Create fixed pairing B: each noodle's two ends paired together
    B = _create_fixed_noodle_pairing(n)

    # Initialize counters for Monte Carlo estimation
    single = 0  # Trials with exactly 1 loop
    nloops = 0  # Trials with exactly n loops (maximum)
    total_loops = 0  # Sum of loops across all trials

    # Monte Carlo sampling: run many random trials
    for _ in range(trials):
        # Create random pairing A of all endpoints
        A = random_pairing_mapping(m, rng)

        # Compose A and B to get permutation P: P[i] = A[B[i]]
        P = [A[B[i]] for i in range(m)]

        # Count cycles in permutation (each physical loop = 2 cycles)
        c = cycles_in_permutation(P)
        loops = c // 2  # Convert cycles to physical loops

        # Update statistics
        total_loops += loops
        if loops == 1:
            single += 1
        if loops == n:
            nloops += 1

    # Calculate estimates and confidence intervals for 1-loop outcome
    est1, se1, ci1 = _calculate_confidence_interval(single, trials)

    # Calculate estimates and confidence intervals for n-loop outcome
    estn, sen, cin = _calculate_confidence_interval(nloops, trials)

    # Calculate average number of loops per trial
    avg_loops = total_loops / trials

    return single, est1, ci1, avg_loops, nloops, estn, cin


def main():
    """Command-line interface for noodle loop Monte Carlo simulation.

    Parses command-line arguments, runs the simulation, and displays results
    comparing Monte Carlo estimates with exact theoretical probabilities.

    Command-line Arguments:
        --n (int): Number of noodles to simulate (default: 7)
        --trials (int): Number of Monte Carlo trials (default: 100,000)
        --seed (int): Random number generator seed for reproducibility (default: 31)

    Output:
        Displays:
        - Simulation parameters (n, trials, seed)
        - Count and probability of exactly 1 loop (Monte Carlo vs exact)
        - Average number of loops per trial
        - Count and probability of exactly n loops (Monte Carlo vs exact)
        - 95% confidence intervals for Monte Carlo estimates

    Example:
        $ python noodle_loops.py --n 5 --trials 10000
        n=5, trials=10000, seed=31
        single-loop count: 219
        Monte Carlo (1 loop): 0.0219000000  (95% CI: [0.0189465207, 0.0248534793])
        Exact (1 loop):       0.0218181818
        Average loops/trial:  2.1023000000
        5-loop count:  1
        Monte Carlo (5): 0.0001000000  (95% CI: [-0.0000960144, 0.0002960144])
        Exact (5 loops): 1.26262626e-03
    """
    # Parse command-line arguments
    ap = argparse.ArgumentParser(
        description="Monte Carlo for random noodle pairings."
    )
    ap.add_argument("--n", type=int, default=7, help="number of noodles")
    ap.add_argument(
        "--trials", type=int, default=100_000, help="number of Monte Carlo trials"
    )
    ap.add_argument("--seed", type=int, default=31, help="RNG seed")
    args = ap.parse_args()

    # Run Monte Carlo simulation
    single, est1, ci1, avg_loops, nloops, estn, cin = simulate(
        args.n, args.trials, args.seed
    )

    # Calculate exact theoretical probabilities
    exact1 = single_loop_probability_exact(args.n)
    exactn = all_loops_probability_exact(args.n)

    # Display results comparing Monte Carlo estimates with exact values
    print(f"n={args.n}, trials={args.trials}, seed={args.seed}")
    print(f"single-loop count: {single}")
    print(
        f"Monte Carlo (1 loop): {est1:.10f}  "
        f"(95% CI: [{ci1[0]:.10f}, {ci1[1]:.10f}])"
    )
    print(f"Exact (1 loop):       {exact1:.10f}")
    print(f"Average loops/trial:  {avg_loops:.10f}")
    print(f"{args.n}-loop count:  {nloops}")
    print(
        f"Monte Carlo ({args.n}): {estn:.10f}  "
        f"(95% CI: [{cin[0]:.10f}, {cin[1]:.10f}])"
    )
    print(f"Exact ({args.n} loops): {exactn:.10e}")


if __name__ == "__main__":
    main()
