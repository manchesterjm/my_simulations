"""
Noodle Loop Monte Carlo Simulation
Classic probability puzzle: randomly tie n noodle endpoints and count loops.

Each noodle has 2 endpoints (2n total). When you randomly pair all endpoints,
how many closed loops form? This simulation compares Monte Carlo estimates
with exact combinatorial formulas.

Key results:
- P(1 loop) = 2^(2n-1) * (n-1)! * n! / (2n)!
- P(n loops) = 1 / (2n-1)!! = 2^n * n! / (2n)!
- Expected loops follows harmonic series pattern
"""

import math
import random
import argparse

def random_pairing_mapping(m, rng):
    arr = list(range(m))
    rng.shuffle(arr)
    mapping = [None]*m
    for i in range(0, m, 2):
        a, b = arr[i], arr[i+1]
        mapping[a] = b
        mapping[b] = a
    return mapping

def cycles_in_permutation(perm):
    n = len(perm)
    seen = [False]*n
    cycles = 0
    for i in range(n):
        if not seen[i]:
            cycles += 1
            j = i
            while not seen[j]:
                seen[j] = True
                j = perm[j]
    return cycles

def single_loop_probability_exact(n):
    # Exactly 1 loop: p1 = 2^{2n-1} (n-1)! n! / (2n)!
    ln_p = (2*n-1) * math.log(2) + math.lgamma(n) + math.lgamma(n+1) - math.lgamma(2*n+1)
    return math.exp(ln_p)

def hundred_loops_probability_exact(n):
    # Exactly n loops occurs iff A == B → probability = 1 / (2n-1)!!
    # Using (2n-1)!! = (2n)! / (2^n n!):
    # p = (2^n n!) / (2n)!
    ln_p = n*math.log(2) + math.lgamma(n+1) - math.lgamma(2*n+1)
    return math.exp(ln_p)

def all_loops_probability_exact(n):
    # P(all n loops) = 1 / (2n-1)!! = (2^n n!) / (2n)!
    ln_p = n * math.log(2) + math.lgamma(n + 1) - math.lgamma(2 * n + 1)
    return math.exp(ln_p)


def simulate(n, trials, seed):
    rng = random.Random(seed)
    m = 2 * n

    # fixed noodle pairing
    B = [0] * m
    for i in range(n):
        a, b = 2 * i, 2 * i + 1
        B[a] = b
        B[b] = a

    single = 0
    nloops = 0
    total_loops = 0

    for _ in range(trials):
        A = random_pairing_mapping(m, rng)
        P = [A[B[i]] for i in range(m)]
        c = cycles_in_permutation(P)
        loops = c // 2

        total_loops += loops
        if loops == 1:
            single += 1
        if loops == n:
            nloops += 1

    est1 = single / trials
    se1 = (est1 * (1 - est1) / trials) ** 0.5
    ci1 = (est1 - 1.96 * se1, est1 + 1.96 * se1)

    estn = nloops / trials
    sen = (estn * (1 - estn) / trials) ** 0.5
    cin = (estn - 1.96 * sen, estn + 1.96 * sen)

    avg_loops = total_loops / trials
    return single, est1, ci1, avg_loops, nloops, estn, cin


def main():
    ap = argparse.ArgumentParser(description="Monte Carlo for random noodle pairings.")
    ap.add_argument("--n", type=int, default=7, help="number of noodles")
    ap.add_argument("--trials", type=int, default=100_000, help="number of Monte Carlo trials")
    ap.add_argument("--seed", type=int, default=31, help="RNG seed")
    args = ap.parse_args()

    single, est1, ci1, avg_loops, nloops, estn, cin = simulate(args.n, args.trials, args.seed)
    exact1 = single_loop_probability_exact(args.n)
    exactn = all_loops_probability_exact(args.n)

    print(f"n={args.n}, trials={args.trials}, seed={args.seed}")
    print(f"single-loop count: {single}")
    print(f"Monte Carlo (1 loop): {est1:.10f}  (95% CI: [{ci1[0]:.10f}, {ci1[1]:.10f}])")
    print(f"Exact (1 loop):       {exact1:.10f}")
    print(f"Average loops/trial:  {avg_loops:.10f}")
    print(f"{args.n}-loop count:  {nloops}")
    print(f"Monte Carlo ({args.n}): {estn:.10f}  (95% CI: [{cin[0]:.10f}, {cin[1]:.10f}])")
    print(f"Exact ({args.n} loops): {exactn:.10e}")


if __name__ == "__main__":
    main()
