# Self-Organized Criticality Simulations

Physics simulations demonstrating **self-organized criticality** and **power law distributions**.

## Overview

This project contains three classic physics simulations that all exhibit the same universal behavior at criticality - power law distributions where small events are common and large events are rare, but not as rare as you'd expect from a normal distribution.

### Simulations

| Simulation | Model | Key Phenomenon |
|------------|-------|----------------|
| **Sandpile** | Per Bak's Abelian Sandpile | Avalanche cascades |
| **Ising Model** | 2D magnetic spins | Phase transitions at Curie temperature |
| **Forest Fire** | Drossel-Schwabl model | Fire spread and suppression |

## Inspiration

This project was inspired by [Derek Muller's](https://www.veritasium.com/) (Veritasium) video on power laws and self-organized criticality. The simulations demonstrate how completely different physical systems can exhibit identical mathematical behavior at critical points.

## Installation

```bash
git clone https://github.com/manchesterjm/my_simulations.git
cd my_simulations
pip install -r support_files/requirements.txt
```

## Usage

```bash
# Individual simulations
python code_files/sandpile.py              # Quick demo
python code_files/sandpile.py --animate    # Animated visualization

python code_files/ising_model.py           # Critical temperature demo
python code_files/ising_model.py --animate # Animated at Tc
python code_files/ising_model.py --compare # Temperature comparison

python code_files/forest_fire.py           # Quick demo
python code_files/forest_fire.py --animate # Animated visualization
python code_files/forest_fire.py --suppression  # Fire suppression demo

# Run all simulations together
python code_files/run_all.py               # Side-by-side comparison
python code_files/run_all.py --combined    # Overlay distributions
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with hypothesis statistics
pytest tests/ --hypothesis-show-statistics

# Mutation testing
mutmut run --paths-to-mutate=code_files/
mutmut results
```

## Project Structure

```
/
├── README.md
├── LICENSE
├── CLAUDE.md              # Development guidelines
├── code_files/            # Simulation source code
├── features/              # BDD specifications (Gherkin)
├── tests/                 # Unit and fuzz tests
├── sessions/              # Development session logs
└── support_files/         # Config and reference materials
```

## Development Principles

This project follows strict development practices:

- **BDD First**: All features start with Gherkin specifications
- **TDD**: Tests written before code; tests are never modified to pass
- **SOFA**: Short, One thing, Few arguments, Abstraction consistency
- **Comprehensive Testing**: Unit tests, fuzz tests (Hypothesis), mutation tests (mutmut)

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Derek Muller** ([Veritasium](https://www.youtube.com/veritasium)) for the inspiring video on power laws
- **Per Bak** for pioneering work on self-organized criticality
- **Ernst Ising** for the Ising model of ferromagnetism
- **Drossel & Schwabl** for the forest fire model
