"""Agent-Based SIR Epidemic Simulation.

This module implements a spatial agent-based model of epidemic disease spread
using the SIR (Susceptible-Infectious-Recovered) framework. The simulation
models disease transmission in a city where agents live in homes, visit nearby
locations, and can transmit disease through contact.

Key Epidemiological Concepts:
    R₀ (Basic Reproduction Number): The average number of secondary infections
        caused by one infected individual in a completely susceptible population.
        R₀ > 1 leads to epidemic spread; R₀ < 1 leads to epidemic fadeout.

    R_effective: The effective reproduction number accounting for reduced
        susceptibility (due to immunity). As more people become immune,
        R_eff decreases below R₀, eventually falling below 1 to end the epidemic.

    Herd Immunity Threshold: The fraction of the population that must be immune
        to prevent sustained transmission. Calculated as (1 - 1/R₀). For example,
        if R₀ = 2.5, then 60% of the population must be immune to achieve herd
        immunity and prevent epidemic spread.

Model Features:
    - Spatial structure with homes and public locations
    - Agent mobility within limited radius from home
    - Stochastic transmission during shared location visits
    - Recovery after fixed infectious period
    - Vaccination capability to model intervention strategies
    - Tracking of transmission chains and R₀ estimation

The simulation demonstrates how spatial structure, mobility patterns, and
population immunity affect disease dynamics and epidemic outcomes.
"""

import numpy as np
import matplotlib.pyplot as plt
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
    """An individual agent in the epidemic simulation.

    Each agent has a home location, health state, and tracks their role in
    disease transmission for R₀ estimation.

    Attributes:
        id (int): Unique identifier for the agent.
        home (tuple): Grid coordinates (x, y) of agent's home.
        state (State): Current health state (SUSCEPTIBLE, INFECTIOUS, RECOVERED, VACCINATED).
        days_infectious (int): Number of days agent has been infectious.
        infected_by (int): ID of agent who infected this agent, or None.
        infections_caused (int): Number of other agents this agent has infected.
    """

    def __init__(self, agent_id, home_location):
        """Initialize an agent.

        Args:
            agent_id (int): Unique identifier for this agent.
            home_location (tuple): Grid coordinates (x, y) of agent's home.
        """
        self.id = agent_id
        self.home = home_location
        self.state = State.SUSCEPTIBLE
        self.days_infectious = 0
        self.infected_by = None
        self.infections_caused = 0

    def is_susceptible(self):
        """Check if agent is susceptible to infection.

        Returns:
            bool: True if agent can be infected.
        """
        return self.state == State.SUSCEPTIBLE

    def is_infectious(self):
        """Check if agent can transmit disease.

        Returns:
            bool: True if agent is currently infectious.
        """
        return self.state == State.INFECTIOUS

    def is_immune(self):
        """Check if agent is immune to infection.

        Immunity is acquired through recovery from infection or vaccination.

        Returns:
            bool: True if agent is immune (recovered or vaccinated).
        """
        return self.state in (State.RECOVERED, State.VACCINATED)


class EpidemicSimulation:
    """Agent-based SIR epidemic simulation with spatial structure.

    Simulates disease spread in a city where agents live in homes,
    visit nearby locations daily, and can transmit disease through contact.
    The model tracks disease dynamics, estimates R₀, and can simulate
    intervention strategies like vaccination.

    Attributes:
        city_size (int): Grid dimension (creates city_size x city_size locations).
        home_density (float): Fraction of locations designated as homes.
        agents_per_home (int): Number of agents residing in each home.
        infection_prob (float): Probability of transmission per susceptible-infectious contact.
        infectious_days (int): Duration of infectious period before recovery.
        visits_per_day (int): Number of non-home locations each agent visits daily.
        visit_radius (int): Maximum Manhattan distance from home for visits.
        initial_infected (int): Number of agents infected at simulation start.
        homes (set): Set of (x, y) coordinates designated as homes.
        non_homes (set): Set of (x, y) coordinates for public locations.
        agents (list): List of all Agent objects in the simulation.
        n_agents (int): Total number of agents.
        day (int): Current simulation day.
        history (dict): Time series of epidemic statistics.
    """

    def __init__(self, city_size=20, home_density=0.5, agents_per_home=3,
                 infection_prob=0.01, infectious_days=2, visits_per_day=3,
                 visit_radius=3, initial_infected=10, seed=None):
        """Initialize the epidemic simulation.

        Args:
            city_size (int, optional): Grid size (city_size x city_size locations). Defaults to 20.
            home_density (float, optional): Fraction of locations that are homes. Defaults to 0.5.
            agents_per_home (int, optional): Number of agents living in each home. Defaults to 3.
            infection_prob (float, optional): Probability of infection per contact between
                susceptible and infectious agents. Higher values increase R₀. Defaults to 0.01.
            infectious_days (int, optional): Number of days an agent remains infectious before
                recovering. Longer periods increase R₀. Defaults to 2.
            visits_per_day (int, optional): Number of non-home locations visited per day.
                More visits increase contact opportunities and R₀. Defaults to 3.
            visit_radius (int, optional): Maximum Manhattan distance from home to visit.
                Defaults to 3.
            initial_infected (int, optional): Number of initially infected agents to seed
                the epidemic. Defaults to 10.
            seed (int, optional): Random seed for reproducibility. Defaults to None.
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
        """Create city grid with homes and non-home locations.

        Randomly designates a fraction of grid locations as homes based on
        home_density, with remaining locations serving as public spaces where
        disease transmission can occur.
        """
        n_locations = self.city_size * self.city_size
        n_homes = int(n_locations * self.home_density)

        # Randomly designate homes across the city grid
        all_locations = [(i, j) for i in range(self.city_size)
                         for j in range(self.city_size)]
        home_indices = self.rng.choice(len(all_locations), n_homes, replace=False)

        self.homes = set(all_locations[i] for i in home_indices)
        self.non_homes = set(all_locations) - self.homes
        self.locations = set(all_locations)

    def _setup_agents(self):
        """Create agents and assign them to homes.

        Creates agents_per_home agents for each home location, establishing
        the total population size based on city structure.
        """
        self.agents = []
        agent_id = 0

        for home in self.homes:
            for _ in range(self.agents_per_home):
                agent = Agent(agent_id, home)
                self.agents.append(agent)
                agent_id += 1

        self.n_agents = len(self.agents)

    def _infect_initial(self):
        """Infect initial agents to seed the epidemic.

        Randomly selects agents to become initially infected, starting the
        epidemic. These index cases begin the transmission chains used to
        estimate R₀.
        """
        n_infect = min(self.initial_infected, self.n_agents)
        initial_indices = self.rng.choice(self.n_agents, n_infect, replace=False)

        for idx in initial_indices:
            self.agents[idx].state = State.INFECTIOUS
            self.agents[idx].days_infectious = 0

    def _get_nearby_locations(self, home):
        """Get non-home locations within visit_radius of a home.

        Uses Manhattan distance (sum of absolute coordinate differences) to
        determine which public locations are accessible from a given home.

        Args:
            home (tuple): Coordinates (x, y) of the home location.

        Returns:
            list: List of (x, y) tuples for nearby non-home locations.
        """
        nearby = []
        hx, hy = home

        for loc in self.non_homes:
            lx, ly = loc
            distance = abs(lx - hx) + abs(ly - hy)  # Manhattan distance
            if distance <= self.visit_radius:
                nearby.append(loc)

        return nearby

    def _get_daily_visits(self, agent):
        """Determine which locations an agent visits today.

        Agents always spend time at home and randomly visit nearby public
        locations. More visits increase contact opportunities and disease
        transmission potential.

        Args:
            agent (Agent): The agent whose daily visits to determine.

        Returns:
            list: List of (x, y) location tuples the agent visits today.
        """
        visits = [agent.home]  # Always at home at start/end of day

        nearby = self._get_nearby_locations(agent.home)
        if nearby:
            n_visits = min(self.visits_per_day, len(nearby))
            visit_indices = self.rng.choice(len(nearby), n_visits, replace=False)
            visits.extend(nearby[i] for i in visit_indices)

        return visits

    def _simulate_day(self):
        """Simulate one day of activity and disease spread.

        Each day consists of three phases:
        1. Agents visit locations (home + nearby public spaces)
        2. Disease transmission occurs where susceptible and infectious agents meet
        3. Infectious agents progress toward recovery

        Returns:
            int: Number of new infections that occurred today.
        """
        # Track which agents are at each location during the day
        location_agents = defaultdict(list)

        # Assign agents to all locations they visit today
        for agent in self.agents:
            visits = self._get_daily_visits(agent)
            for loc in visits:
                location_agents[loc].append(agent)

        # Process potential infections at each location
        new_infections = 0
        for loc, agents_at_loc in location_agents.items():
            new_infections += self._process_location_infections(agents_at_loc)

        # Update disease progression: infectious agents move toward recovery
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
        """Process potential infections at a single location.

        For each susceptible agent, checks all infectious agents at the location.
        Each susceptible-infectious pair has infection_prob chance of transmission.
        Tracks transmission chains for R₀ estimation.

        Args:
            agents (list): All agents present at this location.

        Returns:
            int: Number of new infections at this location.
        """
        infectious = [a for a in agents if a.is_infectious()]
        susceptible = [a for a in agents if a.is_susceptible()]

        if not infectious or not susceptible:
            return 0

        new_infections = 0
        for sus_agent in susceptible:
            # Each susceptible agent can be infected by any infectious agent
            for inf_agent in infectious:
                if self.rng.random() < self.infection_prob:
                    # Infection occurs - update agent state and track transmission
                    sus_agent.state = State.INFECTIOUS
                    sus_agent.days_infectious = 0
                    sus_agent.infected_by = inf_agent.id
                    inf_agent.infections_caused += 1  # Used to calculate R₀
                    new_infections += 1
                    break  # Agent can only get infected once per day

        return new_infections

    def _record_state(self):
        """Record current state counts to history.

        Tracks the number of agents in each state over time to create
        epidemic curves showing disease progression through the population.
        """
        counts = defaultdict(int)
        for agent in self.agents:
            counts[agent.state] += 1

        self.history['susceptible'].append(counts[State.SUSCEPTIBLE])
        self.history['infectious'].append(counts[State.INFECTIOUS])
        self.history['recovered'].append(counts[State.RECOVERED])
        self.history['vaccinated'].append(counts[State.VACCINATED])

    def _calculate_r_effective(self):
        """Calculate effective reproduction number from recent data.

        R_effective is the average number of secondary infections per infectious
        individual, accounting for reduced susceptibility in the population.
        It decreases as immunity builds up. When R_eff < 1, the epidemic declines.

        This calculation estimates R_eff from the ratio of new infections to
        the number of infectious individuals who could have caused them, scaled
        by the infectious period.
        """
        if len(self.history['infectious']) < 2:
            self.history['R_effective'].append(None)
            return

        # R_effective = (new infections) / (infectious who could infect)
        # Scaled by infectious period to get per-generation estimate
        infectious_prev = self.history['infectious'][-2]
        new_inf = (
            self.history['new_infections'][-1]
            if self.history['new_infections'] else 0
        )

        if infectious_prev > 0:
            # Scale by infectious period to get R per generation
            r_eff = (new_inf / infectious_prev) * self.infectious_days
        else:
            r_eff = 0

        self.history['R_effective'].append(r_eff)

    def run(self, n_days, progress_interval=None):
        """Run the simulation for a specified number of days.

        Args:
            n_days (int): Number of days to simulate.
            progress_interval (int, optional): If provided, print status every
                this many days. Defaults to None (no progress output).
        """
        for day in range(n_days):
            self._simulate_day()

            if progress_interval and (day + 1) % progress_interval == 0:
                s, i, r = self.get_counts()
                print(f"Day {self.day}: S={s}, I={i}, R={r}")

    def get_counts(self):
        """Get current state counts.

        Returns:
            tuple: (susceptible, infectious, recovered) counts where recovered
                includes both naturally recovered and vaccinated agents.
        """
        s = self.history['susceptible'][-1]
        i = self.history['infectious'][-1]
        r = self.history['recovered'][-1] + self.history['vaccinated'][-1]
        return s, i, r

    def get_fractions(self):
        """Get current state fractions.

        Returns:
            tuple: (susceptible, infectious, recovered) as fractions of total
                population, summing to 1.0.
        """
        s, i, r = self.get_counts()
        total = s + i + r
        return s/total, i/total, r/total

    def calculate_r0(self):
        """Estimate R₀ (basic reproduction number) from completed infections.

        R₀ represents the average number of secondary infections caused by one
        infected individual in a completely susceptible population. It is a key
        parameter determining epidemic potential:
        - R₀ > 1: Epidemic will grow
        - R₀ = 1: Endemic equilibrium
        - R₀ < 1: Epidemic will die out

        This method estimates R₀ by averaging the number of infections caused
        by agents who have recovered, using only those infected after the
        initial seeding (infected_by is not None).

        Returns:
            float or None: Estimated R₀ value, or None if insufficient data.
        """
        # Only use secondary cases (not initial seed infections) for R₀ estimation
        completed = [a for a in self.agents
                     if a.state == State.RECOVERED and a.infected_by is not None]

        if not completed:
            return None

        # Average the number of infections caused by recovered agents
        infections_caused = [a.infections_caused for a in completed]
        return np.mean(infections_caused) if infections_caused else 0

    def get_herd_immunity_threshold(self):
        """Calculate herd immunity threshold from estimated R₀.

        The herd immunity threshold is the fraction of the population that
        must be immune (through infection or vaccination) to prevent sustained
        transmission. It is calculated as:

            HIT = 1 - 1/R₀

        For example, if R₀ = 3, then HIT = 1 - 1/3 = 67%, meaning 67% of the
        population must be immune to achieve herd immunity.

        Returns:
            float or None: Herd immunity threshold as a fraction (0-1), or None
                if R₀ cannot be estimated or is ≤ 1.
        """
        r0 = self.calculate_r0()
        if r0 is None or r0 <= 1:
            return None
        return 1 - 1/r0

    def vaccinate(self, rate):
        """Vaccinate a fraction of susceptible agents.

        Vaccination provides immunity without requiring infection. This models
        pre-epidemic vaccination campaigns. Vaccinating above the herd immunity
        threshold can prevent epidemic spread entirely.

        Args:
            rate (float): Fraction of susceptible agents to vaccinate (0.0 to 1.0).
                For example, 0.6 means 60% of susceptible agents will be vaccinated.
        """
        susceptible = [a for a in self.agents if a.is_susceptible()]
        n_vaccinate = int(len(susceptible) * rate)

        if n_vaccinate > 0:
            to_vaccinate = self.rng.choice(susceptible, n_vaccinate, replace=False)
            for agent in to_vaccinate:
                agent.state = State.VACCINATED

    def plot_epidemic_curve(self, ax=None):
        """Plot the SIR epidemic curve over time.

        Creates a stacked area plot showing the number of agents in each state
        (Susceptible, Infectious, Recovered, Vaccinated) over time. The classic
        SIR curve shows susceptible declining, infectious rising then falling,
        and recovered rising to a plateau.

        Args:
            ax (matplotlib.axes.Axes, optional): Axes to plot on. If None, creates
                new figure. Defaults to None.

        Returns:
            matplotlib.axes.Axes: The axes containing the plot.
        """
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
        """Plot the effective reproduction number over time.

        Shows how R_effective changes during the epidemic. R_eff typically
        starts near R₀ and decreases as immunity builds up. The epidemic
        peaks when R_eff crosses below 1, and declines thereafter.

        Args:
            ax (matplotlib.axes.Axes, optional): Axes to plot on. If None, creates
                new figure. Defaults to None.

        Returns:
            matplotlib.axes.Axes: The axes containing the plot.
        """
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
        """Plot the city grid showing agent locations and states.

        Visualizes the spatial distribution of the epidemic by showing each
        agent at their home location, colored by health state. Homes are
        shown with a light gray background.

        Args:
            ax (matplotlib.axes.Axes, optional): Axes to plot on. If None, creates
                new figure. Defaults to None.

        Returns:
            matplotlib.axes.Axes: The axes containing the plot.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))

        # Create grid showing home/non-home locations
        grid = np.zeros((self.city_size, self.city_size))
        for loc in self.homes:
            grid[loc] = 0.3  # Light gray for homes

        ax.imshow(grid, cmap='Greys', vmin=0, vmax=1, alpha=0.3)

        # Plot agents at their homes with state-based colors
        for agent in self.agents:
            x, y = agent.home
            color = STATE_COLORS[agent.state]
            # Add jitter to show multiple agents at same home
            jx = x + self.rng.uniform(-0.3, 0.3)
            jy = y + self.rng.uniform(-0.3, 0.3)
            ax.scatter(jy, jx, c=color, s=20, alpha=0.7)

        ax.set_title(f'City (Day {self.day})')
        ax.set_xlim(-0.5, self.city_size - 0.5)
        ax.set_ylim(-0.5, self.city_size - 0.5)

        return ax


def run_epidemic_demo():
    """Demonstrate basic SIR epidemic dynamics.

    Runs a complete epidemic simulation and produces comprehensive visualizations
    including epidemic curves, R_effective tracking, spatial distribution, and
    daily infection counts. Also estimates and reports R₀ and herd immunity
    threshold.
    """
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
    """Compare epidemics with different R₀ values.

    Demonstrates how infection probability affects epidemic outcomes by running
    four simulations with different infection probabilities. Shows that higher
    R₀ leads to faster spread and higher total infection rates.
    """
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
        axes[idx].set_title(
            f'p={prob}, R₀≈{r0:.1f}, Total={r/sim.n_agents:.0%}'
            if r0 else f'p={prob}'
        )

    plt.tight_layout()
    plt.savefig('epidemic_r0_comparison.png', dpi=150)
    plt.show()

    print("Results saved to epidemic_r0_comparison.png")


def run_vaccination_demo():
    """Demonstrate vaccination effects on epidemic dynamics.

    Compares epidemic outcomes with different vaccination rates (0%, 30%, 50%, 60%).
    Shows how vaccination above the herd immunity threshold can prevent or
    significantly reduce epidemic spread, demonstrating the population-level
    benefits of vaccination.
    """
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
        axes[idx].set_title(
            f'{rate:.0%} Vaccinated, Infected={total_infected/sim.n_agents:.0%}'
        )

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
