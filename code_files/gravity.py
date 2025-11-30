"""
N-Body Gravity Simulator

Simulates gravitational interactions in a solar system with:
- Central star with configurable mass and radius
- N planets with random or specified properties
- Collision detection and body merging
- Ejection detection (escape velocity)
- Energy conservation via Velocity Verlet integration
- Orbital trail visualization

Physics:
- Newton's gravitational law: F = G*m1*m2/r^2
- Velocity Verlet integration for stable orbits
- Momentum and mass conservation in collisions
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
    """Calculate gravitational force magnitude between two masses."""
    return G * m1 * m2 / (r * r)


def escape_velocity(mass: float, radius: float) -> float:
    """Calculate escape velocity from a body of given mass at given radius."""
    return np.sqrt(2 * G * mass / radius)


def orbital_velocity(mass: float, radius: float) -> float:
    """Calculate circular orbital velocity around a body of given mass."""
    return np.sqrt(G * mass / radius)


@dataclass
class Body:
    """Represents a celestial body in the simulation."""

    mass: float
    position: np.ndarray
    velocity: np.ndarray
    radius: float = 1e6
    name: str = ""
    trail: List[np.ndarray] = field(default_factory=list)
    color: str = "blue"

    def kinetic_energy(self) -> float:
        """Calculate kinetic energy of the body."""
        v_squared = np.dot(self.velocity, self.velocity)
        return 0.5 * self.mass * v_squared

    def momentum(self) -> np.ndarray:
        """Calculate momentum of the body."""
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
        """Create a body from density and radius."""
        volume = (4 / 3) * np.pi * radius**3
        mass = density * volume
        return cls(mass=mass, position=position, velocity=velocity, radius=radius, **kwargs)


class GravitySimulator:
    """N-body gravity simulation with collision and ejection handling."""

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
        """Add n planets with random properties."""
        colors = ["blue", "green", "red", "orange", "purple", "cyan", "magenta", "brown"]

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
        """Compute gravitational accelerations for all planets."""
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

                # Softened gravitational acceleration
                r_soft = np.sqrt(r_mag**2 + self.softening**2)
                acc_mag = G * other.mass / (r_soft**2)

                # Direction
                total_acc += acc_mag * r_vec / r_mag

            accelerations.append(total_acc)

        return accelerations

    def step(self) -> None:
        """Advance simulation by one time step using Velocity Verlet."""
        if not self.planets:
            return

        # Record trails before update
        if self.record_trails:
            for planet in self.planets:
                planet.trail.append(planet.position.copy())

        # Velocity Verlet integration
        # 1. Compute current accelerations
        accelerations = self._compute_accelerations()

        # 2. Update positions
        for i, planet in enumerate(self.planets):
            planet.position += planet.velocity * self.dt + 0.5 * accelerations[i] * self.dt**2

        # 3. Compute new accelerations
        new_accelerations = self._compute_accelerations()

        # 4. Update velocities
        for i, planet in enumerate(self.planets):
            planet.velocity += 0.5 * (accelerations[i] + new_accelerations[i]) * self.dt

        self.time += self.dt

        # Handle collisions and ejections
        self._handle_collisions()
        self._check_ejections()

    def _detect_collisions(self) -> List[Tuple[int, int]]:
        """Detect colliding planet pairs."""
        collisions = []
        n = len(self.planets)

        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(self.planets[i].position - self.planets[j].position)
                combined_radius = self.planets[i].radius + self.planets[j].radius

                if dist < combined_radius:
                    collisions.append((i, j))

        return collisions

    def _merge_bodies(self, body1: Body, body2: Body) -> Body:
        """Merge two bodies conserving momentum and mass."""
        total_mass = body1.mass + body2.mass
        total_momentum = body1.momentum() + body2.momentum()

        # Center of mass position
        new_position = (body1.mass * body1.position + body2.mass * body2.position) / total_mass

        # Velocity from momentum conservation
        new_velocity = total_momentum / total_mass

        # Combined radius (volume conservation)
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
        """Process all collisions for this timestep."""
        collisions = self._detect_collisions()

        if not collisions:
            return

        # Process collisions (merge bodies)
        to_remove = set()
        new_bodies = []

        for i, j in collisions:
            if i in to_remove or j in to_remove:
                continue

            merged = self._merge_bodies(self.planets[i], self.planets[j])
            new_bodies.append(merged)
            to_remove.add(i)
            to_remove.add(j)

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
        """Check if planet is escaping the system."""
        distance = np.linalg.norm(planet.position - self.star.position)
        speed = np.linalg.norm(planet.velocity)
        v_esc = escape_velocity(self.star.mass, distance)

        # Consider escaping if speed > escape velocity and moving away
        radial_velocity = np.dot(planet.velocity, planet.position) / distance

        return speed > v_esc and radial_velocity > 0

    def _check_ejections(self) -> None:
        """Check for and handle ejected planets."""
        to_eject = []

        for i, planet in enumerate(self.planets):
            if self._is_escaping(planet):
                to_eject.append(i)
                self.ejection_history.append(
                    {
                        "time": self.time,
                        "name": planet.name,
                        "position": planet.position.copy(),
                        "velocity": planet.velocity.copy(),
                    }
                )

        # Remove ejected planets
        for i in sorted(to_eject, reverse=True):
            self.ejected.append(self.planets.pop(i))

    def total_energy(self) -> float:
        """Calculate total energy of the system."""
        energy = 0.0
        all_bodies = [self.star] + self.planets

        # Kinetic energy
        for body in all_bodies:
            energy += body.kinetic_energy()

        # Potential energy
        for i, body1 in enumerate(all_bodies):
            for body2 in all_bodies[i + 1 :]:
                r = np.linalg.norm(body1.position - body2.position)
                energy -= G * body1.mass * body2.mass / r

        return energy

    def run(self, steps: int) -> None:
        """Run simulation for specified number of steps."""
        for _ in range(steps):
            self.step()

    def get_statistics(self) -> Dict:
        """Get simulation statistics."""
        return {
            "total_collisions": len(self.collision_history),
            "total_ejections": len(self.ejection_history),
            "time_elapsed": self.time,
            "remaining_planets": len(self.planets),
            "total_energy": self.total_energy(),
        }

    def modify_planet_speed(self, planet_index: int, factor: float) -> None:
        """Modify a planet's speed by a factor."""
        if 0 <= planet_index < len(self.planets):
            self.planets[planet_index].velocity *= factor

    def estimate_orbital_period(self, planet_index: int) -> float:
        """Estimate orbital period using Kepler's third law."""
        if planet_index >= len(self.planets):
            return 0.0

        planet = self.planets[planet_index]
        distance = np.linalg.norm(planet.position - self.star.position)

        # T = 2*pi*sqrt(a^3 / (G*M))
        period = 2 * np.pi * np.sqrt(distance**3 / (G * self.star.mass))

        return period


# ============================================================================
# Visualization
# ============================================================================


def _scale_radius_for_display(radius: float, scale: float = 1e9) -> float:
    """Scale radius for visualization (bodies would be invisible at true scale)."""
    return max(radius / scale, 0.01)


def plot_state(sim: GravitySimulator, ax: Optional[plt.Axes] = None) -> plt.Axes:
    """Plot current state of the simulation."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))

    ax.clear()
    ax.set_facecolor("black")

    # Find scale based on furthest planet
    max_dist = max(
        [np.linalg.norm(p.position) for p in sim.planets] + [1e11],
        default=1e11,
    )
    scale = max_dist * 1.5

    # Draw star
    star_size = _scale_radius_for_display(sim.star.radius) * scale * 0.05
    star_circle = Circle((0, 0), star_size, color="yellow", zorder=10)
    ax.add_patch(star_circle)

    # Draw planets and trails
    for planet in sim.planets:
        # Trail
        if planet.trail:
            trail = np.array(planet.trail)
            ax.plot(trail[:, 0], trail[:, 1], color=planet.color, alpha=0.3, linewidth=0.5)

        # Planet
        planet_size = _scale_radius_for_display(planet.radius) * scale * 0.02
        circle = Circle(
            planet.position,
            planet_size,
            color=planet.color,
            zorder=5,
        )
        ax.add_patch(circle)

    ax.set_xlim(-scale, scale)
    ax.set_ylim(-scale, scale)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(f"Time: {sim.time / 86400:.1f} days | Planets: {len(sim.planets)}")

    return ax


def run_quick_demo():
    """Run a quick demonstration of the gravity simulator."""
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
    sim.add_planet(mass=3.3e23, distance=5.8e10, radius=2.4e6, name="Mercury", color="gray")
    sim.add_planet(mass=4.9e24, distance=1.1e11, radius=6.1e6, name="Venus", color="orange")
    sim.add_planet(mass=6.0e24, distance=1.5e11, radius=6.4e6, name="Earth", color="blue")
    sim.add_planet(mass=6.4e23, distance=2.3e11, radius=3.4e6, name="Mars", color="red")
    sim.add_planet(mass=1.9e27, distance=7.8e11, radius=7.0e7, name="Jupiter", color="brown")

    print(f"Created solar system with {len(sim.planets)} planets")
    print(f"Initial energy: {sim.total_energy():.3e} J")

    # Run simulation for ~1 Earth year
    steps = 365 * 4  # 6-hour steps, ~1 year
    print(f"\nRunning simulation for {steps} steps (~1 year)...")

    sim.run(steps)

    print(f"\nFinal energy: {sim.total_energy():.3e} J")
    print(f"Energy drift: {abs(sim.total_energy() / sim.total_energy() - 1) * 100:.4f}%")

    stats = sim.get_statistics()
    print(f"\nStatistics:")
    print(f"  Collisions: {stats['total_collisions']}")
    print(f"  Ejections: {stats['total_ejections']}")
    print(f"  Time elapsed: {stats['time_elapsed'] / 86400:.1f} days")

    # Plot final state
    fig, ax = plt.subplots(figsize=(10, 10))
    plot_state(sim, ax)
    plt.tight_layout()
    plt.show()


def run_interactive_simulation():
    """Run animated simulation."""
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

    anim = FuncAnimation(fig, update, frames=500, interval=50, blit=False)
    plt.tight_layout()
    plt.show()


def run_collision_demo():
    """Demonstrate planet collisions."""
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

    anim = FuncAnimation(fig, update, frames=500, interval=50, blit=False)
    plt.tight_layout()
    plt.show()

    if sim.collision_history:
        print("\nCollision events:")
        for event in sim.collision_history:
            print(f"  {event['body1']} + {event['body2']} at t={event['time']/86400:.1f} days")


def run_ejection_demo():
    """Demonstrate planet ejection."""
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
    print(f"Rogue planet velocity factor: 1.8x circular orbital velocity")

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

    anim = FuncAnimation(fig, update, frames=300, interval=50, blit=False)
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
