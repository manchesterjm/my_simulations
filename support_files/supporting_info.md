# Supporting Information and References

## Original Video Sources

### 1. Veritasium - Power Laws and Self-Organized Criticality
The inspiration for this project's simulations.

- **Video**: "The Surprising satisfying satisfying math that's everywhere" (Power Laws)
- **Channel**: Veritasium (Derek Muller)
- **URL**: https://www.youtube.com/watch?v=tDXPT4N4D4c
- **Topics**: Power law distributions, self-organized criticality, Pareto distribution
- **Transcript**: `support_files/transcript.md`

### 2. Computerphile - Memoization
Reference material on caching/memoization techniques.

- **Video**: "Memoization"
- **Channel**: Computerphile
- **URL**: https://www.youtube.com/watch?v=P8Xa2BitN3I
- **Topics**: Caching, recursion optimization, stair-climbing problem
- **Transcript**: `support_files/memoization.transcript.md`
- **Analysis**: Not applicable to this project (simulations are stochastic, not recursive combinatorial problems)

### 3. Numberphile - Frog Hopping Problem
Referenced in the Computerphile memoization video.

- **Channel**: Numberphile
- **URL**: https://www.youtube.com/watch?v=8ei-vEf4cCQ
- **Topics**: Fibonacci sequence, combinatorial counting

## Web Articles

### Memoization Techniques Guide
- **URL**: https://www.numberanalytics.com/blog/the-ultimate-guide-to-memoization-techniques
- **Topics**: When to use memoization, caching strategies, implementation patterns
- **Key Points**:
  - Best for recursive algorithms with repeated subproblems
  - Requires pure/deterministic functions
  - Not suitable for functions with side effects or randomness

## Analysis Notes

### Why Memoization Doesn't Apply Here

These simulations are **Monte Carlo / stochastic processes**, not recursive combinatorial problems:

| Memoization Requirement | Our Simulations |
|------------------------|-----------------|
| Deterministic functions | Use random number generators |
| Same inputs = same outputs | Grid state changes every step |
| Repeated subproblems | Each timestep is unique |
| Pure functions | Functions modify grid state |

The simulations evolve forward in time with randomness, rather than computing deterministic results from overlapping sub-problems.
