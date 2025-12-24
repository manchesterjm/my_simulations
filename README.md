# Physics, Probability & AI Simulations

Simulations demonstrating **self-organized criticality**, **power law distributions**, **Monte Carlo methods**, and **reinforcement learning**.

## Overview

This project contains simulations exploring emergent behavior in complex systems - from avalanches to epidemics to AI agents learning to play games.

### Physics & Probability Simulations

| Simulation | Model | Key Phenomenon |
|------------|-------|----------------|
| **Sandpile** | Per Bak's Abelian Sandpile | Avalanche cascades, power laws |
| **Ising Model** | 2D magnetic spins | Phase transitions at Curie temperature |
| **Forest Fire** | Drossel-Schwabl model | Fire spread and self-organized criticality |
| **Epidemic** | Agent-based SIR model | Disease spread, R0, herd immunity |
| **Noodle Loops** | Monte Carlo simulation | Probability puzzle with exact solutions |
| **Gravity** | N-body simulation | Orbital dynamics, collisions, ejections |
| **Cache Sim** | CPU cache simulator | LRU/FIFO replacement policies |

### AI/ML Simulations

| Project | Model | Key Achievement |
|---------|-------|-----------------|
| **Minesweeper ML** | Hybrid (AC-3 + Neural Network) | 88% win rate on beginner |

See [AI_ML/minesweeper_ml_project/](AI_ML/minesweeper_ml_project/) for details.

### GPU Acceleration

The physics simulations support **GPU acceleration** via CuPy:
- Ising Model: ~40x speedup with checkerboard Metropolis
- Sandpile: ~40x speedup with batch avalanche processing
- Forest Fire: ~1.3x speedup (limited by sequential BFS)

## Inspiration

This project was inspired by [Derek Muller's](https://www.veritasium.com/) (Veritasium) video on power laws and self-organized criticality. The simulations demonstrate how completely different physical systems can exhibit identical mathematical behavior at critical points.

## Installation

\`\`\`bash
git clone https://github.com/manchesterjm/my_simulations.git
cd my_simulations
pip install -r support_files/requirements.txt

# Optional: GPU support
pip install cupy-cuda12x
\`\`\`

## Usage

\`\`\`bash
# Self-Organized Criticality Simulations
python code_files/sandpile.py              # Quick demo
python code_files/sandpile.py --animate    # Animated visualization

python code_files/ising_model.py           # Critical temperature demo
python code_files/ising_model.py --animate # Animated at Tc
python code_files/ising_model.py --compare # Temperature comparison

python code_files/forest_fire.py           # Quick demo
python code_files/forest_fire.py --animate # Animated visualization
python code_files/forest_fire.py --suppression  # Fire suppression demo

# Run all SOC simulations together
python code_files/run_all.py               # Side-by-side comparison
python code_files/run_all.py --combined    # Overlay distributions

# Epidemic Simulation
python code_files/epidemic.py              # Basic SIR simulation
python code_files/epidemic.py --compare    # Compare different infection rates
python code_files/epidemic.py --vaccine    # Vaccination intervention demo

# N-Body Gravity Simulation
python code_files/gravity.py               # Quick demo (solar system)
python code_files/gravity.py --animate     # Animated with random planets
python code_files/gravity.py --collision   # Collision demo
python code_files/gravity.py --ejection    # Ejection demo

# Monte Carlo
python code_files/noodle_loops.py          # Noodle loop probability simulation
python code_files/noodle_loops.py --n 10 --trials 100000

# Benchmarks (GPU vs CPU)
python code_files/benchmark.py             # Compare performance
\`\`\`

## Testing

\`\`\`bash
# Run all tests (105 total)
pytest tests/ -v

# Run with hypothesis statistics
pytest tests/ --hypothesis-show-statistics
\`\`\`

## Project Structure

\`\`\`
/
├── README.md
├── LICENSE
├── CLAUDE.md              # Development guidelines
├── code_files/            # Physics simulation source code
│   ├── sandpile.py        # Abelian sandpile (CPU + GPU)
│   ├── ising_model.py     # Ising model (CPU + GPU)
│   ├── forest_fire.py     # Forest fire (CPU + GPU)
│   ├── epidemic.py        # SIR epidemic model
│   ├── gravity.py         # N-body gravity simulator
│   ├── noodle_loops.py    # Monte Carlo simulation
│   ├── cache_sim.py       # CPU cache simulator
│   ├── run_all.py         # Combined demo
│   ├── benchmark.py       # CPU vs GPU benchmarks
│   ├── gpu_utils.py       # GPU detection utilities
│   └── *_gpu.py           # GPU implementations
├── AI_ML/                 # AI/ML projects
│   └── minesweeper_ml_project/  # Minesweeper AI (PyTorch)
├── features/              # BDD specifications (Gherkin)
├── tests/                 # Unit tests (105 tests)
├── sessions/              # Development session logs
└── support_files/         # Config and reference materials
\`\`\`

## Development Principles

This project follows strict development practices:

- **BDD First**: All features start with Gherkin specifications
- **TDD**: Tests written before code; tests are never modified to pass
- **SOFA**: Short, One thing, Few arguments, Abstraction consistency
- **Comprehensive Testing**: Unit tests, fuzz tests (Hypothesis)

See [CLAUDE.md](CLAUDE.md) for detailed development guidelines.

## Key Concepts

### Self-Organized Criticality
Systems that naturally tune themselves to a critical state where:
- Events span many orders of magnitude
- Power law distributions emerge
- Small causes can have large effects

### Power Laws
Mathematical relationships where frequency decreases as size increases, appearing as straight lines on log-log plots. Found in:
- Earthquakes
- Forest fires
- Stock market crashes
- City populations
- And many more natural phenomena

### SIR Epidemic Model
Agent-based disease modeling with:
- **S**usceptible: Can be infected
- **I**nfectious: Can spread disease
- **R**ecovered: Immune (temporary or permanent)

Key metrics: R0 (basic reproduction number), herd immunity threshold

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Derek Muller** ([Veritasium](https://www.youtube.com/veritasium)) for the inspiring video on power laws
- **Per Bak** for pioneering work on self-organized criticality
- **Ernst Ising** for the Ising model of ferromagnetism
- **Drossel & Schwabl** for the forest fire model
