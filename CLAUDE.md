# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Physics simulations demonstrating **self-organized criticality**, **power law distributions**, and **Monte Carlo methods**. Inspired by the Veritasium video on power laws. All simulations show that different physical systems exhibit universal behavior at criticality.

## File Structure

```
/
├── CLAUDE.md              # This file
├── .gitignore
├── code_files/            # Simulation source code
│   ├── sandpile.py        # Abelian sandpile (CPU + GPU backend)
│   ├── sandpile_gpu.py    # GPU implementation
│   ├── ising_model.py     # Ising model (CPU + GPU backend)
│   ├── ising_gpu.py       # GPU implementation
│   ├── forest_fire.py     # Forest fire (CPU + GPU backend)
│   ├── forest_fire_gpu.py # GPU implementation
│   ├── epidemic.py        # Agent-based SIR epidemic model
│   ├── gravity.py         # N-body gravity simulator
│   ├── ant_colony.py      # Ant Colony Optimization
│   ├── noodle_loops.py    # Monte Carlo probability simulation
│   ├── cache_sim.py       # CPU cache simulator
│   ├── run_all.py         # Combined SOC demo
│   ├── benchmark.py       # CPU vs GPU performance comparison
│   └── gpu_utils.py       # GPU detection utilities
├── features/              # BDD specifications (Gherkin)
│   ├── sandpile.feature
│   ├── ising_model.feature
│   ├── forest_fire.feature
│   ├── gravity.feature
│   └── ant_colony.feature
├── tests/                 # Test files (138 tests total)
│   ├── test_sandpile.py
│   ├── test_ising_model.py
│   ├── test_forest_fire.py
│   ├── test_epidemic.py
│   ├── test_gravity.py
│   └── test_ant_colony.py
├── sessions/              # Session logs (SESSION_YYYYMMDD_HHMMSS.md)
└── support_files/         # Configuration and reference
    ├── requirements.txt
    ├── pytest.ini
    └── transcript.md      # Veritasium video transcript
```

## Running Simulations

Install dependencies:
```bash
pip install -r support_files/requirements.txt

# Optional: GPU support
pip install cupy-cuda12x
```

```bash
# Self-Organized Criticality (with GPU support)
python code_files/sandpile.py              # Quick demo
python code_files/sandpile.py --animate    # Animated visualization

python code_files/ising_model.py           # Critical temperature demo
python code_files/ising_model.py --animate # Animated at Tc
python code_files/ising_model.py --compare # Temperature comparison

python code_files/forest_fire.py           # Quick demo
python code_files/forest_fire.py --animate # Animated visualization
python code_files/forest_fire.py --suppression  # Fire suppression comparison

# Combined SOC comparison
python code_files/run_all.py               # Side-by-side all three simulations
python code_files/run_all.py --combined    # Overlay distributions on single plot

# Epidemic Simulation
python code_files/epidemic.py              # Basic SIR simulation
python code_files/epidemic.py --compare    # Compare infection rates
python code_files/epidemic.py --vaccine    # Vaccination demo

# N-Body Gravity Simulation
python code_files/gravity.py              # Quick demo (solar system)
python code_files/gravity.py --animate    # Animated with random planets
python code_files/gravity.py --collision  # Collision demo
python code_files/gravity.py --ejection   # Ejection demo

# Ant Colony Optimization
python code_files/ant_colony.py           # Quick demo with 30 nodes
python code_files/ant_colony.py --animate # Animated visualization
python code_files/ant_colony.py --compare # Compare parameter settings
# Or open ant_colony.html in browser for interactive web version

# Monte Carlo
python code_files/noodle_loops.py --n 7 --trials 100000

# Benchmarks
python code_files/benchmark.py             # CPU vs GPU comparison
```

## Architecture

Each simulation follows the same pattern:
- **Simulation class**: Grid-based model with `run()` method and statistics tracking
- **Distribution methods**: `get_*_distribution()` returns (sizes, frequencies) for power law plotting
- **Visualization**: `plot_state()` for grid view, `plot_*_distribution()` for log-log plots
- **Entry points**: `run_quick_demo()` for static results, `run_interactive_simulation()` for animation
- **Backend selection**: `backend='auto'/'gpu'/'cpu'` for GPU acceleration (SOC simulations)

`run_all.py` imports and orchestrates all three SOC simulations to demonstrate universality.

## Key Parameters

| Simulation | Critical Parameters |
|------------|-------------------|
| Sandpile | `threshold=4`, `drop_mode='random'` or `'center'` |
| Ising | `temperature=2.269` (Curie temperature Tc) |
| Forest Fire | `tree_growth_prob=0.01`, `lightning_prob=p/10` |
| Epidemic | `infection_prob=0.01`, `infectious_days=2`, `visits_per_day=3` |
| Gravity | `star_mass`, `n_planets`, `dt=3600` (timestep) |
| Ant Colony | `alpha=2`, `beta=2`, `rho=0.1`, `n_ants=500` |

All simulations accept a `seed` parameter for reproducibility.

## GPU Acceleration

Three simulations support GPU via CuPy with automatic fallback:
- **Ising Model**: Checkerboard Metropolis (~40x speedup)
- **Sandpile**: Batch avalanche processing (~40x speedup)
- **Forest Fire**: Hybrid CPU/GPU (~1.3x speedup, BFS limited)

Use `backend='auto'` (default) for automatic GPU detection, or force with `backend='gpu'`/`backend='cpu'`.

## Development Principles

### Session Logging
Before starting any task, create a session file `sessions/SESSION_YYYYMMDD_HHMMSS.md` documenting:
- **Before work begins**: What we are about to do (protects against crashes)
- **After task completion**: What was done and what remains to do

This creates an audit trail and recovery point for every coding session.

### Commit Immediately
Commit all changes to GitHub immediately upon task completion. Do not batch multiple tasks into a single commit.

### BDD First
All new features must start with Behavior-Driven Development. Write Gherkin-style specifications (Given/When/Then) before any implementation to define expected behavior from the user's perspective.

### TDD Workflow
1. Write failing tests first
2. Write minimal code to pass tests
3. Refactor while keeping tests green

**Tests are the source of truth.** Never modify tests to make code pass—always modify code to make tests pass.

### SOFA Principles
Design all functions following SOFA:
- **Short**: Functions should be concise and readable
- **One thing**: Each function does exactly one thing
- **Few arguments**: Minimize parameter count (ideally ≤3)
- **Abstraction level consistency**: All code within a function operates at the same level of abstraction

### Fix Failures Immediately
When a test fails, fix it immediately. Do not report a failure and move on—diagnose the issue and implement a fix before proceeding.

### Testing Requirements

```bash
# Unit tests (105 tests)
pytest tests/ -v
```

All code must pass unit tests (standard pytest assertions).
