# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Physics simulations demonstrating **self-organized criticality** and **power law distributions**, inspired by the Veritasium video on power laws. All simulations show that different physical systems exhibit universal behavior at criticality.

## File Structure

```
/
├── CLAUDE.md              # This file
├── .gitignore
├── code_files/            # Simulation source code
│   ├── sandpile.py
│   ├── ising_model.py
│   ├── forest_fire.py
│   └── run_all.py
├── features/              # BDD specifications (Gherkin)
│   ├── sandpile.feature
│   ├── ising_model.feature
│   └── forest_fire.feature
├── tests/                 # Test files
│   └── test_*.py
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
```

```bash
# Individual simulations (run from code_files/)
python code_files/sandpile.py              # Quick demo
python code_files/sandpile.py --animate    # Animated visualization

python code_files/ising_model.py           # Critical temperature demo
python code_files/ising_model.py --animate # Animated at Tc
python code_files/ising_model.py --compare # Temperature comparison

python code_files/forest_fire.py           # Quick demo
python code_files/forest_fire.py --animate # Animated visualization
python code_files/forest_fire.py --suppression  # Fire suppression comparison

# Combined comparison
python code_files/run_all.py               # Side-by-side all three simulations
python code_files/run_all.py --combined    # Overlay distributions on single plot
```

## Architecture

Each simulation follows the same pattern:
- **Simulation class**: Grid-based model with `run()` method and statistics tracking
- **Distribution methods**: `get_*_distribution()` returns (sizes, frequencies) for power law plotting
- **Visualization**: `plot_state()` for grid view, `plot_*_distribution()` for log-log plots
- **Entry points**: `run_quick_demo()` for static results, `run_interactive_simulation()` for animation

`run_all.py` imports and orchestrates all three simulations to demonstrate universality.

## Key Parameters

| Simulation | Critical Parameters |
|------------|-------------------|
| Sandpile | `threshold=4`, `drop_mode='random'` or `'center'` |
| Ising | `temperature=2.269` (Curie temperature Tc) |
| Forest Fire | `tree_growth_prob=0.01`, `lightning_prob=p/10` |

All simulations accept a `seed` parameter for reproducibility.

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
# Unit tests
pytest -c support_files/pytest.ini

# Fuzz testing with Hypothesis
pytest -c support_files/pytest.ini --hypothesis-show-statistics

# Mutation testing with mutmut
mutmut run --paths-to-mutate=code_files/
mutmut results
```

All code must pass:
- **Unit tests**: Standard pytest assertions
- **Fuzz tests**: Property-based testing via `hypothesis` to find edge cases
- **Mutation tests**: `mutmut` to verify test quality (tests should catch mutations)
