"""
Agent-Based SIR Epidemic Simulation
Based on the Susceptible-Infectious-Recovered model demonstrating disease spread dynamics.

Agents live in homes, visit nearby locations daily, and can transmit disease
when sharing the same location. The simulation tracks R₀, herd immunity,
and epidemic curves.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap
from collections import defaultdict
from enum import IntEnum


class State(IntEnum):
    """Agent health states."""
    SUSCEPTIBLE = 0
    INFECTIOUS = 1
    RECOVERED = 2
    VACCINATED = 3


# Colors for visualization
STATE_COLORS = {
    State.SUSCEPTIBLE: '#3498db',  # Blue
    State.INFECTIOUS: '#e74c3c',    # Red
    State.RECOVERED: '#95a5a6',     # Gray
    State.VACCINATED: '#2ecc71',    # Green
}


class Agent:
    """An individual in the simulation."""

    def __init__(self, agent_id, home_location):
        self.id = agent_id
        self.home = home_location
        self.state = State.SUSCEPTIBLE
        self.days_infectious = 0
        self.infected_by = None
        self.infections_caused = 0

    def is_susceptible(self):
        return self.state == State.SUSCEPTIBLE

    def is_infectious(self):
        return self.state == State.INFECTIOUS

    def is_immune(self):
        return self.state in (State.RECOVERED, State.VACCINATED)


class EpidemicSimulation:
    """
    Agent-based SIR epidemic simulation.

    Simulates disease spread in a city where agents live in homes,
    visit nearby locations daily, and can transmit disease through contact.
    """

    def __init__(self, city_size=20, home_density=0.5, agents_per_home=3,
                 infection_prob=0.01, infectious_days=2, visits_per_day=3,
                 visit_radius=3, initial_infected=10, seed=None):
        """
        Initialize the epidemic simulation.

        Args:
            city_size: Grid size (city_size x city_size locations)
            home_density: Fraction of locations that are homes
            agents_per_home: Number of agents living in each home
            infection_prob: Probability of infection per interaction
            infectious_days: Number of days an agent remains infectious
            visits_per_day: Number of non-home locations visited per day
            visit_radius: Maximum distance from home to visit
            initial_infected: Number of initially infected agents
            seed: Random seed for reproducibility
        """
        self.city_size = city_size
        self.home_density = home_density
        self.agents_per_home = agents_per_home
        self.infection_prob = infection_prob
        self.infectious_days = infectious_days
        self.visits_per_day = visits_per_day
        self.visit_radius = visit_radius
        self.initial_infected = initial_infected

        self.rng = np.random.default_rng(seed)

        # Initialize city and agents
        self._setup_city()
        self._setup_agents()
        self._infect_initial()

        # Statistics
        self.day = 0
        self.history = {
            'susceptible': [],
            'infectious': [],
            'recovered': [],
            'vaccinated': [],
            'new_infections': [],
            'R_effective': [],
        }
        self._record_state()

    def _setup_city(self):
        """Create city grid with homes and non-home locations."""
        n_locations = self.city_size * self.city_size
        n_homes = int(n_locations * self.home_density)

        # Randomly designate homes
        all_locations = [(i, j) for i in range(self.city_size)
                         for j in range(self.city_size)]
        home_indices = self.rng.choice(len(all_locations), n_homes, replace=False)

        self.homes = set(all_locations[i] for i in home_indices)
        self.non_homes = set(all_locations) - self.homes
        self.locations = set(all_locations)

    def _setup_agents(self):
        """Create agents and assign them to homes."""
        self.agents = []
        agent_id = 0

        for home in self.homes:
            for _ in range(self.agents_per_home):
                agent = Agent(agent_id, home)
                self.agents.append(agent)
                agent_id += 1

        self.n_agents = len(self.agents)

    def _infect_initial(self):
        """Infect initial agents."""
        n_infect = min(self.initial_infected, self.n_agents)
        initial_indices = self.rng.choice(self.n_agents, n_infect, replace=False)

        for idx in initial_indices:
            self.agents[idx].state = State.INFECTIOUS
            self.agents[idx].days_infectious = 0

    def _get_nearby_locations(self, home):
        """Get non-home locations within visit_radius of a home."""
        nearby = []
        hx, hy = home

        for loc in self.non_homes:
            lx, ly = loc
            distance = abs(lx - hx) + abs(ly - hy)  # Manhattan distance
            if distance <= self.visit_radius:
                nearby.append(loc)

        return nearby

    def _get_daily_visits(self, agent):
        """Determine which locations an agent visits today."""
        visits = [agent.home]  # Always at home at start/end of day

        nearby = self._get_nearby_locations(agent.home)
        if nearby:
            n_visits = min(self.visits_per_day, len(nearby))
            visit_indices = self.rng.choice(len(nearby), n_visits, replace=False)
            visits.extend(nearby[i] for i in visit_indices)

        return visits

    def _simulate_day(self):
        """Simulate one day of activity and disease spread."""
        # Track which agents are at each location
        location_agents = defaultdict(list)

        # Assign agents to locations they visit
        for agent in self.agents:
            visits = self._get_daily_visits(agent)
            for loc in visits:
                location_agents[loc].append(agent)

        # Process infections at each location
        new_infections = 0
        for loc, agents_at_loc in location_agents.items():
            new_infections += self._process_location_infections(agents_at_loc)

        # Update infectious status
        for agent in self.agents:
            if agent.is_infectious():
                agent.days_infectious += 1
                if agent.days_infectious >= self.infectious_days:
                    agent.state = State.RECOVERED

        self.day += 1
        self.history['new_infections'].append(new_infections)
        self._record_state()
        self._calculate_r_effective()

        return new_infections

    def _process_location_infections(self, agents):
        """Process potential infections at a single location."""
        infectious = [a for a in agents if a.is_infectious()]
        susceptible = [a for a in agents if a.is_susceptible()]

        if not infectious or not susceptible:
            return 0

        new_infections = 0
        for sus_agent in susceptible:
            for inf_agent in infectious:
                if self.rng.random() < self.infection_prob:
                    sus_agent.state = State.INFECTIOUS
                    sus_agent.days_infectious = 0
                    sus_agent.infected_by = inf_agent.id
                    inf_agent.infections_caused += 1
                    new_infections += 1
                    break  # Only get infected once per day

        return new_infections

    def _record_state(self):
        """Record current state counts."""
        counts = defaultdict(int)
        for agent in self.agents:
            counts[agent.state] += 1

        self.history['susceptible'].append(counts[State.SUSCEPTIBLE])
        self.history['infectious'].append(counts[State.INFECTIOUS])
        self.history['recovered'].append(counts[State.RECOVERED])
        self.history['vaccinated'].append(counts[State.VACCINATED])

    def _calculate_r_effective(self):
        """Calculate effective reproduction number from recent data."""
        if len(self.history['infectious']) < 2:
            self.history['R_effective'].append(None)
            return

        # R = new_infections / infectious_who_could_infect
        # Approximation using recent data
        infectious_prev = self.history['infectious'][-2]
        new_inf = self.history['new_infections'][-1] if self.history['new_infections'] else 0

        if infectious_prev > 0:
            # Scale by infectious period to get R per generation
            r_eff = (new_inf / infectious_prev) * self.infectious_days
        else:
            r_eff = 0

        self.history['R_effective'].append(r_eff)

    def run(self, n_days, progress_interval=None):
        """Run the simulation for n_days."""
        for day in range(n_days):
            self._simulate_day()

            if progress_interval and (day + 1) % progress_interval == 0:
                s, i, r = self.get_counts()
                print(f"Day {self.day}: S={s}, I={i}, R={r}")

    def get_counts(self):
        """Get current state counts."""
        s = self.history['susceptible'][-1]
        i = self.history['infectious'][-1]
        r = self.history['recovered'][-1] + self.history['vaccinated'][-1]
        return s, i, r

    def get_fractions(self):
        """Get current state fractions."""
        s, i, r = self.get_counts()
        total = s + i + r
        return s/total, i/total, r/total

    def calculate_r0(self):
        """
        Estimate R₀ from completed infections.

        R₀ is the average number of secondary infections caused by
        each infected agent, assuming all contacts are susceptible.
        """
        completed = [a for a in self.agents
                     if a.state == State.RECOVERED and a.infected_by is not None]

        if not completed:
            return None

        # Get infections caused by those who have recovered
        infections_caused = [a.infections_caused for a in completed]
        return np.mean(infections_caused) if infections_caused else 0

    def get_herd_immunity_threshold(self):
        """Calculate herd immunity threshold from estimated R₀."""
        r0 = self.calculate_r0()
        if r0 is None or r0 <= 1:
            return None
        return 1 - 1/r0

    def vaccinate(self, rate):
        """
        Vaccinate a fraction of susceptible agents.

        Args:
            rate: Fraction of susceptible agents to vaccinate
        """
        susceptible = [a for a in self.agents if a.is_susceptible()]
        n_vaccinate = int(len(susceptible) * rate)

        if n_vaccinate > 0:
            to_vaccinate = self.rng.choice(susceptible, n_vaccinate, replace=False)
            for agent in to_vaccinate:
                agent.state = State.VACCINATED

    def plot_epidemic_curve(self, ax=None):
        """Plot the SIR epidemic curve."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))

        days = range(len(self.history['susceptible']))

        ax.stackplot(days,
                     self.history['susceptible'],
                     self.history['infectious'],
                     self.history['recovered'],
                     self.history['vaccinated'],
                     labels=['Susceptible', 'Infectious', 'Recovered', 'Vaccinated'],
                     colors=[STATE_COLORS[State.SUSCEPTIBLE],
                            STATE_COLORS[State.INFECTIOUS],
                            STATE_COLORS[State.RECOVERED],
                            STATE_COLORS[State.VACCINATED]],
                     alpha=0.8)

        ax.set_xlabel('Day')
        ax.set_ylabel('Number of Agents')
        ax.set_title(f'Epidemic Curve (Day {self.day})')
        ax.legend(loc='upper right')
        ax.set_xlim(0, len(days)-1)
        ax.set_ylim(0, self.n_agents)

        return ax

    def plot_r_effective(self, ax=None):
        """Plot the effective reproduction number over time."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 4))

        r_values = [r for r in self.history['R_effective'] if r is not None]
        days = range(len(r_values))

        ax.plot(days, r_values, 'b-', linewidth=2)
        ax.axhline(y=1, color='r', linestyle='--', label='R=1 (threshold)')
        ax.set_xlabel('Day')
        ax.set_ylabel('R (effective)')
        ax.set_title('Effective Reproduction Number')
        ax.legend()
        ax.set_ylim(0, max(max(r_values) * 1.2, 2) if r_values else 2)

        return ax

    def plot_city(self, ax=None):
        """Plot the city grid showing agent locations and states."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))

        # Create grid showing home/non-home
        grid = np.zeros((self.city_size, self.city_size))
        for loc in self.homes:
            grid[loc] = 0.3  # Light for homes

        ax.imshow(grid, cmap='Greys', vmin=0, vmax=1, alpha=0.3)

        # Plot agents at their homes with state colors
        for agent in self.agents:
            x, y = agent.home
            color = STATE_COLORS[agent.state]
            # Jitter to show multiple agents
            jx = x + self.rng.uniform(-0.3, 0.3)
            jy = y + self.rng.uniform(-0.3, 0.3)
            ax.scatter(jy, jx, c=color, s=20, alpha=0.7)

        ax.set_title(f'City (Day {self.day})')
        ax.set_xlim(-0.5, self.city_size - 0.5)
        ax.set_ylim(-0.5, self.city_size - 0.5)

        return ax


def run_epidemic_demo():
    """Demonstrate basic epidemic dynamics."""
    print("SIR Epidemic Simulation")
    print("=" * 50)

    sim = EpidemicSimulation(
        city_size=20,
        agents_per_home=3,
        infection_prob=0.02,
        infectious_days=2,
        initial_infected=10,
        seed=42
    )

    print(f"Population: {sim.n_agents} agents")
    print(f"Initial infected: {sim.initial_infected}")
    print(f"Infection probability: {sim.infection_prob}")
    print(f"Infectious period: {sim.infectious_days} days")

    print("\nRunning simulation...")
    sim.run(60, progress_interval=10)

    r0 = sim.calculate_r0()
    herd = sim.get_herd_immunity_threshold()

    print(f"\nEstimated R₀: {r0:.2f}" if r0 else "\nR₀: Not enough data")
    print(f"Herd immunity threshold: {herd:.1%}" if herd else "Herd immunity: N/A")

    s, i, r = sim.get_counts()
    print(f"\nFinal state: S={s}, I={i}, R={r}")
    print(f"Total infected: {r} ({r/sim.n_agents:.1%})")

    # Plot results
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    sim.plot_epidemic_curve(axes[0, 0])
    sim.plot_r_effective(axes[0, 1])
    sim.plot_city(axes[1, 0])

    # Plot new infections per day
    axes[1, 1].bar(range(len(sim.history['new_infections'])),
                   sim.history['new_infections'],
                   color=STATE_COLORS[State.INFECTIOUS], alpha=0.7)
    axes[1, 1].set_xlabel('Day')
    axes[1, 1].set_ylabel('New Infections')
    axes[1, 1].set_title('Daily New Infections')

    plt.tight_layout()
    plt.savefig('epidemic_results.png', dpi=150)
    plt.show()

    print("\nResults saved to epidemic_results.png")


def run_r0_comparison():
    """Compare epidemics with different R₀ values."""
    print("R₀ Comparison")
    print("=" * 50)

    infection_probs = [0.005, 0.01, 0.02, 0.04]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for idx, prob in enumerate(infection_probs):
        sim = EpidemicSimulation(
            city_size=20,
            infection_prob=prob,
            infectious_days=2,
            initial_infected=10,
            seed=42
        )

        sim.run(80)

        r0 = sim.calculate_r0()
        _, _, r = sim.get_counts()

        sim.plot_epidemic_curve(axes[idx])
        axes[idx].set_title(f'p={prob}, R₀≈{r0:.1f}, Total={r/sim.n_agents:.0%}' if r0 else f'p={prob}')

    plt.tight_layout()
    plt.savefig('epidemic_r0_comparison.png', dpi=150)
    plt.show()

    print("Results saved to epidemic_r0_comparison.png")


def run_vaccination_demo():
    """Demonstrate vaccination effects."""
    print("Vaccination Demo")
    print("=" * 50)

    vax_rates = [0.0, 0.3, 0.5, 0.6]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for idx, rate in enumerate(vax_rates):
        sim = EpidemicSimulation(
            city_size=20,
            infection_prob=0.02,
            infectious_days=2,
            initial_infected=10,
            seed=42
        )

        # Vaccinate before epidemic
        sim.vaccinate(rate)

        sim.run(80)

        s, i, r = sim.get_counts()
        total_infected = sim.history['recovered'][-1]  # Excluding vaccinated

        sim.plot_epidemic_curve(axes[idx])
        axes[idx].set_title(f'{rate:.0%} Vaccinated, Infected={total_infected/sim.n_agents:.0%}')

    plt.tight_layout()
    plt.savefig('epidemic_vaccination.png', dpi=150)
    plt.show()

    print("Results saved to epidemic_vaccination.png")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--compare':
        run_r0_comparison()
    elif len(sys.argv) > 1 and sys.argv[1] == '--vaccine':
        run_vaccination_demo()
    else:
        run_epidemic_demo()
