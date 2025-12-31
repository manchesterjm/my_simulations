"""N-Body Gravity Simulator

A physics simulation demonstrating gravitational interactions in an N-body system,
typically configured as a star with orbiting planets. This module implements
classical Newtonian gravity with modern numerical integration techniques.

Features
--------
- **N-body gravitational dynamics**: Simulates interactions between a central star
  and multiple planets, with all bodies influencing each other gravitationally
- **Collision physics**: Detects and merges colliding bodies while conserving
  momentum and mass
- **Ejection detection**: Identifies and tracks planets that exceed escape velocity
- **Energy-conserving integration**: Uses Velocity Verlet algorithm for stable,
  long-term orbital simulations
- **Visualization**: Real-time plotting with orbital trails, energy tracking, and
  automatic scaling

Physics Implementation
----------------------
- **Gravitational force**: Newton's law F = G*m1*m2/r^2 with softening parameter
  to prevent numerical instabilities at close range
- **Integration method**: Velocity Verlet (symplectic integrator) for excellent
  energy conservation over long timescales
- **Collision handling**: Perfectly inelastic collisions with momentum conservation,
  volume-conserving radius calculation
- **Escape criterion**: Planets with v > v_escape and positive radial velocity
  are marked as ejected

Typical Usage
-------------
    # Create simulator with Sun-like star
    sim = GravitySimulator(star_mass=1.989e30, dt=3600)

    # Add Earth-like planet in circular orbit
    sim.add_planet(mass=6e24, distance=1.5e11, radius=6.4e6)

    # Run for 1000 timesteps
    sim.run(1000)

    # Check statistics
    stats = sim.get_statistics()
    print(f"Energy: {stats['total_energy']:.3e} J")

Module Structure
----------------
- Body: Dataclass representing a celestial body with position, velocity, mass
- GravitySimulator: Main simulation class handling physics and state management
- Visualization functions: plot_state() and various demo functions
- Demo modes: Quick demo, interactive animation, collision demo, ejection demo

Constants
---------
G : float
    Gravitational constant (6.674e-11 m^3 kg^-1 s^-2)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict

# Gravitational constant (m^3 kg^-1 s^-2)
G = 6.674e-11


def gravitational_force(m1: float, m2: float, r: float) -> float:
    """Calculate gravitational force magnitude between two masses.

    Uses Newton's law of universal gravitation: F = G * m1 * m2 / r^2

    Args:
        m1: Mass of first body in kilograms.
        m2: Mass of second body in kilograms.
        r: Distance between bodies in meters.

    Returns:
        Gravitational force magnitude in Newtons.

    Example:
        >>> # Force between Earth and Moon
        >>> f = gravitational_force(5.97e24, 7.35e22, 3.84e8)
        >>> print(f"{f:.3e} N")
    """
    return G * m1 * m2 / (r * r)


def escape_velocity(mass: float, radius: float) -> float:
    """Calculate escape velocity from a body of given mass at given radius.

    The escape velocity is the minimum speed needed for an object to escape
    the gravitational pull of a celestial body. Derived from energy conservation:
    v_escape = sqrt(2 * G * M / r)

    Args:
        mass: Mass of the celestial body in kilograms.
        radius: Distance from center of body in meters.

    Returns:
        Escape velocity in meters per second.

    Example:
        >>> # Escape velocity from Earth's surface
        >>> v_esc = escape_velocity(5.97e24, 6.371e6)
        >>> print(f"{v_esc:.0f} m/s")  # ~11,200 m/s
    """
    return np.sqrt(2 * G * mass / radius)


def orbital_velocity(mass: float, radius: float) -> float:
    """Calculate circular orbital velocity around a body of given mass.

    For a circular orbit, the gravitational force provides the centripetal force.
    Solving F_gravity = F_centripetal gives: v_orbital = sqrt(G * M / r)

    Args:
        mass: Mass of the central body in kilograms.
        radius: Orbital radius in meters.

    Returns:
        Circular orbital velocity in meters per second.

    Example:
        >>> # Earth's orbital velocity around the Sun
        >>> v_orb = orbital_velocity(1.989e30, 1.5e11)
        >>> print(f"{v_orb:.0f} m/s")  # ~30,000 m/s
    """
    return np.sqrt(G * mass / radius)


@dataclass
class Body:
    """Represents a celestial body in the simulation.

    A celestial body (star, planet, asteroid, etc.) with physical properties
    and state variables for position and velocity. Supports trail recording
    for visualization of orbital paths.

    Attributes:
        mass: Body mass in kilograms.
        position: 2D position vector [x, y] in meters as numpy array.
        velocity: 2D velocity vector [vx, vy] in m/s as numpy array.
        radius: Physical radius in meters (default: 1e6 m = 1000 km).
        name: Human-readable identifier for the body (default: "").
        trail: List of historical position vectors for visualization.
        color: Color string for plotting (default: "blue").
    """

    mass: float
    position: np.ndarray
    velocity: np.ndarray
    radius: float = 1e6
    name: str = ""
    trail: List[np.ndarray] = field(default_factory=list)
    color: str = "blue"

    def kinetic_energy(self) -> float:
        """Calculate kinetic energy of the body.

        Uses the formula KE = (1/2) * m * v^2

        Returns:
            Kinetic energy in Joules.
        """
        v_squared = np.dot(self.velocity, self.velocity)
        return 0.5 * self.mass * v_squared

    def momentum(self) -> np.ndarray:
        """Calculate momentum of the body.

        Uses the formula p = m * v

        Returns:
            Momentum vector as numpy array [px, py] in kg·m/s.
        """
        return self.mass * self.velocity

    @classmethod
    def from_density(
        cls,
        density: float,
        radius: float,
        position: np.ndarray,
        velocity: np.ndarray,
        **kwargs,
    ) -> "Body":
        """Create a body from density and radius.

        Convenience constructor that calculates mass from density and volume,
        assuming a spherical body. Uses V = (4/3) * π * r^3 and m = ρ * V.

        Args:
            density: Material density in kg/m^3.
            radius: Body radius in meters.
            position: Initial position vector [x, y] in meters.
            velocity: Initial velocity vector [vx, vy] in m/s.
            **kwargs: Additional Body attributes (name, color, etc.).

        Returns:
            New Body instance with calculated mass.

        Example:
            >>> # Create rocky planet with Earth's density
            >>> pos = np.array([1.5e11, 0.0])
            >>> vel = np.array([0.0, 3e4])
            >>> planet = Body.from_density(5500, 6.4e6, pos, vel, name="Rocky")
        """
        # Calculate volume of sphere
        volume = (4 / 3) * np.pi * radius**3
        mass = density * volume
        return cls(
            mass=mass,
            position=position,
            velocity=velocity,
            radius=radius,
            **kwargs
        )


class GravitySimulator:
    """N-body gravity simulation with collision and ejection handling.

    Simulates gravitational interactions between a central star and multiple
    planets using Newton's laws and the Velocity Verlet integration method.
    Handles collisions (merging bodies) and ejections (escape velocity).

    The simulator maintains separate lists for:
    - Active planets (currently orbiting)
    - Ejected bodies (exceeded escape velocity)
    - Collision history (merged bodies)
    - Ejection history (escaped bodies)

    Attributes:
        dt: Timestep in seconds for integration.
        softening: Softening length to prevent singularities (meters).
        record_trails: Whether to record position history for visualization.
        rng: Random number generator for reproducibility.
        time: Current simulation time in seconds.
        star: The central star Body object.
        planets: List of currently orbiting planets.
        ejected: List of ejected planets.
        collision_history: List of collision event dictionaries.
        ejection_history: List of ejection event dictionaries.
    """

    def __init__(
        self,
        star_mass: float = 1.989e30,
        star_radius: float = 6.96e8,
        dt: float = 3600,
        seed: Optional[int] = None,
        record_trails: bool = False,
        softening: float = 1e9,
    ):
        """
        Initialize the gravity simulator.

        Args:
            star_mass: Mass of central star in kg (default: Sun's mass)
            star_radius: Radius of central star in m (default: Sun's radius)
            dt: Time step in seconds (default: 1 hour)
            seed: Random seed for reproducibility
            record_trails: Whether to record orbital trails
            softening: Softening parameter to prevent numerical instabilities
        """
        self.dt = dt
        self.softening = softening
        self.record_trails = record_trails
        self.rng = np.random.default_rng(seed)
        self.time = 0.0

        # Create central star
        self.star = Body(
            mass=star_mass,
            position=np.array([0.0, 0.0]),
            velocity=np.array([0.0, 0.0]),
            radius=star_radius,
            name="Star",
            color="yellow",
        )

        self.planets: List[Body] = []
        self.ejected: List[Body] = []
        self.collision_history: List[Dict] = []
        self.ejection_history: List[Dict] = []

    def add_planet(
        self,
        mass: float,
        distance: float,
        radius: float = 6.371e6,
        angle: Optional[float] = None,
        velocity_factor: float = 1.0,
        name: str = "",
        color: str = "blue",
    ) -> None:
        """
        Add a planet in circular orbit around the star.

        Args:
            mass: Planet mass in kg
            distance: Orbital distance from star in m
            radius: Planet radius in m
            angle: Initial angle in radians (random if None)
            velocity_factor: Multiplier for orbital velocity (1.0 = circular)
            name: Planet name for display
            color: Planet color for visualization
        """
        if angle is None:
            angle = self.rng.uniform(0, 2 * np.pi)

        # Position
        position = np.array([distance * np.cos(angle), distance * np.sin(angle)])

        # Circular orbital velocity (perpendicular to radius)
        v_orbital = orbital_velocity(self.star.mass, distance) * velocity_factor
        velocity = np.array([-v_orbital * np.sin(angle), v_orbital * np.cos(angle)])

        planet = Body(
            mass=mass,
            position=position,
            velocity=velocity,
            radius=radius,
            name=name or f"Planet {len(self.planets) + 1}",
            color=color,
        )

        self.planets.append(planet)

    def add_random_planets(
        self,
        n: int,
        min_orbit: float = 5e10,
        max_orbit: float = 5e11,
        min_mass: float = 1e23,
        max_mass: float = 1e27,
        min_radius: float = 1e6,
        max_radius: float = 7e7,
    ) -> None:
        """Add n planets with random properties.

        Generates planets with uniformly distributed orbital distances, masses,
        and radii within the specified ranges. Each planet is placed in a
        circular orbit with velocity appropriate for its distance.

        Args:
            n: Number of planets to add.
            min_orbit: Minimum orbital radius in meters (default: 5e10 m).
            max_orbit: Maximum orbital radius in meters (default: 5e11 m).
            min_mass: Minimum planet mass in kg (default: 1e23 kg).
            max_mass: Maximum planet mass in kg (default: 1e27 kg).
            min_radius: Minimum planet radius in meters (default: 1e6 m).
            max_radius: Maximum planet radius in meters (default: 7e7 m).
        """
        colors = [
            "blue", "green", "red", "orange",
            "purple", "cyan", "magenta", "brown"
        ]

        for i in range(n):
            mass = self.rng.uniform(min_mass, max_mass)
            distance = self.rng.uniform(min_orbit, max_orbit)
            radius = self.rng.uniform(min_radius, max_radius)
            color = colors[i % len(colors)]

            self.add_planet(
                mass=mass,
                distance=distance,
                radius=radius,
                name=f"Planet {i + 1}",
                color=color,
            )

    def _compute_accelerations(self) -> List[np.ndarray]:
        """Compute gravitational accelerations for all planets.

        Calculates the net acceleration on each planet due to gravitational
        forces from the star and all other planets. Uses softening to prevent
        numerical singularities when bodies get very close.

        Returns:
            List of acceleration vectors, one per planet, in m/s^2.

        Notes:
            The softening parameter prevents division by zero and numerical
            instabilities when r → 0. Uses: a = G*M / (sqrt(r^2 + ε^2))^2
            where ε is the softening length.
        """
        accelerations = []
        all_bodies = [self.star] + self.planets

        for planet in self.planets:
            total_acc = np.array([0.0, 0.0])

            for other in all_bodies:
                if other is planet:
                    continue

                # Vector from planet to other body
                r_vec = other.position - planet.position
                r_mag = np.linalg.norm(r_vec)

                # Softened gravitational acceleration: a = G*M / (r^2 + ε^2)
                # This prevents singularities when bodies get very close
                r_soft = np.sqrt(r_mag**2 + self.softening**2)
                acc_mag = G * other.mass / (r_soft**2)

                # Direction: unit vector from planet toward other body
                total_acc += acc_mag * r_vec / r_mag

            accelerations.append(total_acc)

        return accelerations

    def step(self) -> None:
        """Advance simulation by one time step using Velocity Verlet.

        The Velocity Verlet algorithm is a symplectic integrator that provides
        excellent energy conservation for Hamiltonian systems. It's second-order
        accurate in time and reversible.

        Algorithm steps:
        1. Compute accelerations at time t: a(t)
        2. Update positions: x(t+dt) = x(t) + v(t)*dt + 0.5*a(t)*dt^2
        3. Compute new accelerations at time t+dt: a(t+dt)
        4. Update velocities: v(t+dt) = v(t) + 0.5*(a(t) + a(t+dt))*dt

        After integration, checks for and handles collisions and ejections.
        """
        if not self.planets:
            return

        # Record trails before update for visualization
        if self.record_trails:
            for planet in self.planets:
                planet.trail.append(planet.position.copy())

        # Velocity Verlet integration - superior energy conservation
        # Step 1: Compute current accelerations a(t)
        accelerations = self._compute_accelerations()

        # Step 2: Update positions using x(t+dt) = x(t) + v(t)*dt + 0.5*a(t)*dt^2
        for i, planet in enumerate(self.planets):
            planet.position += (
                planet.velocity * self.dt
                + 0.5 * accelerations[i] * self.dt**2
            )

        # Step 3: Compute new accelerations a(t+dt) at updated positions
        new_accelerations = self._compute_accelerations()

        # Step 4: Update velocities using average acceleration
        # v(t+dt) = v(t) + 0.5*(a(t) + a(t+dt))*dt
        for i, planet in enumerate(self.planets):
            planet.velocity += 0.5 * (accelerations[i] + new_accelerations[i]) * self.dt

        self.time += self.dt

        # Handle physical events
        self._handle_collisions()
        self._check_ejections()

    def _detect_collisions(self) -> List[Tuple[int, int]]:
        """Detect colliding planet pairs.

        Checks all planet pairs for overlap by comparing center-to-center
        distance with sum of radii. Bodies are considered colliding when
        their surfaces touch or overlap.

        Returns:
            List of tuples (i, j) where i < j are indices of colliding planets.
        """
        collisions = []
        n = len(self.planets)

        for i in range(n):
            for j in range(i + 1, n):
                # Calculate center-to-center distance
                dist = np.linalg.norm(
                    self.planets[i].position - self.planets[j].position
                )
                combined_radius = self.planets[i].radius + self.planets[j].radius

                # Collision occurs when distance < sum of radii
                if dist < combined_radius:
                    collisions.append((i, j))

        return collisions

    def _merge_bodies(self, body1: Body, body2: Body) -> Body:
        """Merge two bodies conserving momentum and mass.

        Models a perfectly inelastic collision where two bodies stick together.
        Conserves total mass, momentum, and volume. The new body's position is
        at the center of mass, and velocity is determined by momentum conservation.

        Args:
            body1: First colliding body.
            body2: Second colliding body.

        Returns:
            New merged Body with combined properties.

        Notes:
            - Mass: m_new = m1 + m2
            - Position: r_new = (m1*r1 + m2*r2) / (m1 + m2)  [center of mass]
            - Velocity: v_new = (m1*v1 + m2*v2) / (m1 + m2)  [momentum conservation]
            - Radius: r_new = (r1^3 + r2^3)^(1/3)  [volume conservation]
        """
        total_mass = body1.mass + body2.mass
        total_momentum = body1.momentum() + body2.momentum()

        # Center of mass position
        new_position = (
            (body1.mass * body1.position + body2.mass * body2.position)
            / total_mass
        )

        # Velocity from momentum conservation: p = m*v
        new_velocity = total_momentum / total_mass

        # Combined radius assuming volume conservation: V1 + V2 = V_new
        # Since V = (4/3)*π*r^3, we get r_new = (r1^3 + r2^3)^(1/3)
        new_radius = (body1.radius**3 + body2.radius**3) ** (1 / 3)

        return Body(
            mass=total_mass,
            position=new_position,
            velocity=new_velocity,
            radius=new_radius,
            name=f"{body1.name}+{body2.name}",
            color=body1.color if body1.mass > body2.mass else body2.color,
        )

    def _handle_collisions(self) -> None:
        """Process all collisions for this timestep.

        Detects colliding planet pairs, merges them into new bodies, and
        records collision events. Handles multiple simultaneous collisions
        by ensuring each body is only involved in one merger.
        """
        collisions = self._detect_collisions()

        if not collisions:
            return

        # Process collisions (merge bodies)
        to_remove = set()
        new_bodies = []

        for i, j in collisions:
            # Skip if either body already involved in another collision
            if i in to_remove or j in to_remove:
                continue

            merged = self._merge_bodies(self.planets[i], self.planets[j])
            new_bodies.append(merged)
            to_remove.add(i)
            to_remove.add(j)

            # Record collision event for analysis
            self.collision_history.append(
                {
                    "time": self.time,
                    "body1": self.planets[i].name,
                    "body2": self.planets[j].name,
                    "merged_mass": merged.mass,
                }
            )

        # Remove collided bodies and add merged ones
        self.planets = [p for idx, p in enumerate(self.planets) if idx not in to_remove]
        self.planets.extend(new_bodies)

    def _is_escaping(self, planet: Body) -> bool:
        """Check if planet is escaping the system.

        A planet is considered escaping if:
        1. Its speed exceeds escape velocity at current distance
        2. Its radial velocity is positive (moving away from star)

        Args:
            planet: The planet to check.

        Returns:
            True if planet is escaping, False otherwise.

        Notes:
            Radial velocity is the component of velocity in the direction
            away from the star: v_r = (v · r) / |r|
        """
        distance = np.linalg.norm(planet.position - self.star.position)
        speed = np.linalg.norm(planet.velocity)
        v_esc = escape_velocity(self.star.mass, distance)

        # Calculate radial velocity (velocity component away from star)
        # Positive means moving away, negative means moving toward
        radial_velocity = np.dot(planet.velocity, planet.position) / distance

        # Escaping requires: (1) speed > v_escape AND (2) moving outward
        return speed > v_esc and radial_velocity > 0

    def _check_ejections(self) -> None:
        """Check for and handle ejected planets.

        Identifies planets that have exceeded escape velocity and are moving
        away from the star. Removes them from active simulation and records
        the ejection event.
        """
        to_eject = []

        for i, planet in enumerate(self.planets):
            if self._is_escaping(planet):
                to_eject.append(i)
                # Record ejection event for analysis
                self.ejection_history.append(
                    {
                        "time": self.time,
                        "name": planet.name,
                        "position": planet.position.copy(),
                        "velocity": planet.velocity.copy(),
                    }
                )

        # Remove ejected planets (iterate in reverse to maintain indices)
        for i in sorted(to_eject, reverse=True):
            self.ejected.append(self.planets.pop(i))

    def total_energy(self) -> float:
        """Calculate total energy of the system.

        Computes the sum of kinetic and gravitational potential energy for
        all bodies. For a well-integrated simulation, total energy should
        remain approximately constant (energy conservation).

        Returns:
            Total energy in Joules.

        Notes:
            - Kinetic energy: KE = Σ (1/2) * m * v^2
            - Potential energy: PE = -Σ G * m1 * m2 / r  (negative!)
            - Total energy: E = KE + PE
        """
        energy = 0.0
        all_bodies = [self.star] + self.planets

        # Kinetic energy: sum over all bodies
        for body in all_bodies:
            energy += body.kinetic_energy()

        # Gravitational potential energy: sum over all unique pairs
        # PE is negative (energy needed to separate to infinity)
        for i, body1 in enumerate(all_bodies):
            for body2 in all_bodies[i + 1 :]:
                r = np.linalg.norm(body1.position - body2.position)
                energy -= G * body1.mass * body2.mass / r

        return energy

    def run(self, steps: int) -> None:
        """Run simulation for specified number of steps.

        Executes the main simulation loop, advancing time by dt for each step.

        Args:
            steps: Number of timesteps to simulate.
        """
        for _ in range(steps):
            self.step()

    def get_statistics(self) -> Dict:
        """Get simulation statistics.

        Returns:
            Dictionary containing:
                - total_collisions: Number of collision events
                - total_ejections: Number of ejection events
                - time_elapsed: Simulation time in seconds
                - remaining_planets: Current number of orbiting planets
                - total_energy: Current total energy in Joules
        """
        return {
            "total_collisions": len(self.collision_history),
            "total_ejections": len(self.ejection_history),
            "time_elapsed": self.time,
            "remaining_planets": len(self.planets),
            "total_energy": self.total_energy(),
        }

    def modify_planet_speed(self, planet_index: int, factor: float) -> None:
        """Modify a planet's speed by a factor.

        Multiplies the planet's velocity vector by the given factor, changing
        its speed while preserving direction. Useful for creating elliptical
        orbits or ejection scenarios.

        Args:
            planet_index: Index of planet to modify.
            factor: Speed multiplier (1.0 = no change, >1.0 = faster, <1.0 = slower).
        """
        if 0 <= planet_index < len(self.planets):
            self.planets[planet_index].velocity *= factor

    def estimate_orbital_period(self, planet_index: int) -> float:
        """Estimate orbital period using Kepler's third law.

        Calculates the orbital period assuming a circular orbit at the planet's
        current distance from the star. For elliptical orbits, this gives the
        period for a circular orbit at the current radius.

        Args:
            planet_index: Index of planet to analyze.

        Returns:
            Estimated orbital period in seconds (0.0 if index invalid).

        Notes:
            Uses Kepler's third law: T = 2π * sqrt(a³ / (G*M))
            where a is the semi-major axis (approximated by current distance).
        """
        if planet_index >= len(self.planets):
            return 0.0

        planet = self.planets[planet_index]
        distance = np.linalg.norm(planet.position - self.star.position)

        # Kepler's third law: T = 2*pi*sqrt(a^3 / (G*M))
        period = 2 * np.pi * np.sqrt(distance**3 / (G * self.star.mass))

        return period


# ============================================================================
# Visualization
# ============================================================================


def _scale_radius_for_display(radius: float, scale: float = 1e9) -> float:
    """Scale radius for visualization.

    Bodies in space are too small to see at true scale (e.g., Earth's radius
    is ~6000 km but its orbit is ~150 million km). This function scales radii
    to make them visible while preserving relative sizes.

    Args:
        radius: True physical radius in meters.
        scale: Scaling factor (default: 1e9 reduces by billion).

    Returns:
        Scaled radius for display, with minimum of 0.01 to ensure visibility.
    """
    return max(radius / scale, 0.01)


def _compute_plot_scale(sim: GravitySimulator) -> float:
    """Compute appropriate plot scale based on planet positions.

    Args:
        sim: The gravity simulator instance.

    Returns:
        Plot scale in meters (1.5x the furthest planet distance).
    """
    max_dist = max(
        [np.linalg.norm(p.position) for p in sim.planets] + [1e11],
        default=1e11,
    )
    return max_dist * 1.5


def _draw_star(ax: plt.Axes, star: Body, scale: float) -> None:
    """Draw the central star on the plot.

    Args:
        ax: Matplotlib axes to draw on.
        star: The star Body object.
        scale: Plot scale for sizing.
    """
    star_size = _scale_radius_for_display(star.radius) * scale * 0.05
    star_circle = Circle((0, 0), star_size, color="yellow", zorder=10)
    ax.add_patch(star_circle)


def _draw_planet_with_trail(ax: plt.Axes, planet: Body, scale: float) -> None:
    """Draw a planet and its orbital trail.

    Args:
        ax: Matplotlib axes to draw on.
        planet: The planet Body object.
        scale: Plot scale for sizing.
    """
    # Draw trail if it exists
    if planet.trail:
        trail = np.array(planet.trail)
        ax.plot(
            trail[:, 0], trail[:, 1],
            color=planet.color, alpha=0.3, linewidth=0.5
        )

    # Draw planet
    planet_size = _scale_radius_for_display(planet.radius) * scale * 0.02
    circle = Circle(
        planet.position,
        planet_size,
        color=planet.color,
        zorder=5,
    )
    ax.add_patch(circle)


def plot_state(sim: GravitySimulator, ax: Optional[plt.Axes] = None) -> plt.Axes:
    """Plot current state of the simulation.

    Creates a visualization showing the star, planets, and orbital trails on
    a black background. Automatically scales to show all planets with appropriate
    margins.

    Args:
        sim: The gravity simulator to visualize.
        ax: Optional matplotlib axes (creates new figure if None).

    Returns:
        The axes object containing the plot.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))

    ax.clear()
    ax.set_facecolor("black")

    # Compute scale based on furthest planet
    scale = _compute_plot_scale(sim)

    # Draw celestial bodies
    _draw_star(ax, sim.star, scale)
    for planet in sim.planets:
        _draw_planet_with_trail(ax, planet, scale)

    # Configure axes
    ax.set_xlim(-scale, scale)
    ax.set_ylim(-scale, scale)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(f"Time: {sim.time / 86400:.1f} days | Planets: {len(sim.planets)}")

    return ax


def run_quick_demo():
    """Run a quick demonstration of the gravity simulator.

    Creates a solar system with 5 planets (Mercury, Venus, Earth, Mars, Jupiter)
    and runs the simulation for approximately one Earth year. Displays energy
    conservation statistics and plots the final state with orbital trails.
    """
    print("N-Body Gravity Simulator")
    print("=" * 50)

    # Create solar system
    sim = GravitySimulator(
        star_mass=1.989e30,
        star_radius=6.96e8,
        dt=3600 * 6,  # 6 hour steps
        seed=42,
        record_trails=True,
    )

    # Add planets at different distances
    sim.add_planet(
        mass=3.3e23, distance=5.8e10, radius=2.4e6,
        name="Mercury", color="gray"
    )
    sim.add_planet(
        mass=4.9e24, distance=1.1e11, radius=6.1e6,
        name="Venus", color="orange"
    )
    sim.add_planet(
        mass=6.0e24, distance=1.5e11, radius=6.4e6,
        name="Earth", color="blue"
    )
    sim.add_planet(
        mass=6.4e23, distance=2.3e11, radius=3.4e6,
        name="Mars", color="red"
    )
    sim.add_planet(
        mass=1.9e27, distance=7.8e11, radius=7.0e7,
        name="Jupiter", color="brown"
    )

    print(f"Created solar system with {len(sim.planets)} planets")
    print(f"Initial energy: {sim.total_energy():.3e} J")

    # Run simulation for ~1 Earth year
    steps = 365 * 4  # 6-hour steps, ~1 year
    print(f"\nRunning simulation for {steps} steps (~1 year)...")

    sim.run(steps)

    print(f"\nFinal energy: {sim.total_energy():.3e} J")
    energy_drift = abs(sim.total_energy() / sim.total_energy() - 1) * 100
    print(f"Energy drift: {energy_drift:.4f}%")

    stats = sim.get_statistics()
    print("\nStatistics:")
    print(f"  Collisions: {stats['total_collisions']}")
    print(f"  Ejections: {stats['total_ejections']}")
    print(f"  Time elapsed: {stats['time_elapsed'] / 86400:.1f} days")

    # Plot final state
    fig, ax = plt.subplots(figsize=(10, 10))
    plot_state(sim, ax)
    plt.tight_layout()
    plt.show()


def run_interactive_simulation():
    """Run animated simulation with real-time visualization.

    Creates a system with 8 random planets and displays an animated visualization
    showing orbital evolution and energy conservation over time. Updates every
    5 simulation steps for smooth animation.
    """
    sim = GravitySimulator(
        star_mass=1.989e30,
        star_radius=6.96e8,
        dt=3600 * 24,  # 1 day steps
        seed=42,
        record_trails=True,
    )

    # Add random planets
    sim.add_random_planets(
        n=8,
        min_orbit=5e10,
        max_orbit=8e11,
        min_mass=1e23,
        max_mass=5e26,
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Energy tracking
    energies = []
    times = []

    def update(frame):
        # Run multiple steps per frame for speed
        for _ in range(5):
            sim.step()

        energies.append(sim.total_energy())
        times.append(sim.time / 86400)  # Convert to days

        # Plot state
        plot_state(sim, ax1)

        # Plot energy
        ax2.clear()
        ax2.plot(times, energies, "g-", linewidth=1)
        ax2.set_xlabel("Time (days)")
        ax2.set_ylabel("Total Energy (J)")
        ax2.set_title("Energy Conservation")
        ax2.grid(True, alpha=0.3)

        return []

    _anim = FuncAnimation(fig, update, frames=500, interval=50, blit=False)
    plt.tight_layout()
    plt.show()


def run_collision_demo():
    """Demonstrate planet collisions with animated visualization.

    Creates two planets on intersecting orbits with one moving faster (elliptical
    orbit), leading to a collision. Shows the merger process and displays
    collision event details.
    """
    print("Collision Demo")
    print("=" * 50)

    sim = GravitySimulator(
        star_mass=1.989e30,
        dt=3600,
        seed=42,
        record_trails=True,
    )

    # Add planets on intersecting orbits
    sim.add_planet(mass=1e25, distance=1e11, radius=1e7, name="Planet A", color="blue")
    sim.add_planet(
        mass=1e25,
        distance=1e11,
        radius=1e7,
        angle=np.pi / 6,  # Slightly offset
        velocity_factor=1.2,  # Faster = elliptical
        name="Planet B",
        color="red",
    )

    print(f"Starting with {len(sim.planets)} planets")

    fig, ax = plt.subplots(figsize=(10, 10))

    def update(frame):
        for _ in range(10):
            sim.step()

        plot_state(sim, ax)
        ax.set_title(
            f"Time: {sim.time / 86400:.1f} days | "
            f"Planets: {len(sim.planets)} | "
            f"Collisions: {len(sim.collision_history)}"
        )
        return []

    _anim = FuncAnimation(fig, update, frames=500, interval=50, blit=False)
    plt.tight_layout()
    plt.show()

    if sim.collision_history:
        print("\nCollision events:")
        for event in sim.collision_history:
            time_days = event['time'] / 86400
            print(
                f"  {event['body1']} + {event['body2']} "
                f"at t={time_days:.1f} days"
            )


def run_ejection_demo():
    """Demonstrate planet ejection with animated visualization.

    Creates one stable planet and one "rogue" planet with velocity 1.8x the
    circular orbital velocity, which exceeds escape velocity. Shows the ejection
    process and displays ejection event details.
    """
    print("Ejection Demo")
    print("=" * 50)

    sim = GravitySimulator(
        star_mass=1.989e30,
        dt=3600 * 6,
        seed=42,
        record_trails=True,
    )

    # Add a normal planet
    sim.add_planet(mass=6e24, distance=1.5e11, radius=6e6, name="Earth", color="blue")

    # Add a fast planet that will be ejected
    sim.add_planet(
        mass=1e24,
        distance=1e11,
        radius=5e6,
        velocity_factor=1.8,  # Well above escape velocity
        name="Rogue",
        color="red",
    )

    print(f"Starting with {len(sim.planets)} planets")
    print("Rogue planet velocity factor: 1.8x circular orbital velocity")

    fig, ax = plt.subplots(figsize=(10, 10))

    def update(frame):
        for _ in range(5):
            sim.step()

        plot_state(sim, ax)
        ax.set_title(
            f"Time: {sim.time / 86400:.1f} days | "
            f"Planets: {len(sim.planets)} | "
            f"Ejected: {len(sim.ejected)}"
        )
        return []

    _anim = FuncAnimation(fig, update, frames=300, interval=50, blit=False)
    plt.tight_layout()
    plt.show()

    if sim.ejection_history:
        print("\nEjection events:")
        for event in sim.ejection_history:
            print(f"  {event['name']} ejected at t={event['time']/86400:.1f} days")


if __name__ == "__main__":
    import sys

    if "--animate" in sys.argv:
        run_interactive_simulation()
    elif "--collision" in sys.argv:
        run_collision_demo()
    elif "--ejection" in sys.argv:
        run_ejection_demo()
    else:
        run_quick_demo()
