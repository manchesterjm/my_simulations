"""Unit tests for N-Body Gravity Simulator."""

import pytest
import numpy as np
from code_files.gravity import (
    Body,
    GravitySimulator,
    gravitational_force,
    escape_velocity,
    orbital_velocity,
    G,
)


class TestGravitationalPhysics:
    """Tests for gravitational physics calculations."""

    def test_gravitational_constant(self):
        """G should be the standard gravitational constant."""
        assert abs(G - 6.674e-11) < 1e-14

    def test_gravitational_force_inverse_square(self):
        """Force should follow inverse square law."""
        m1, m2 = 1e30, 1e24
        r1 = 1e11
        r2 = 2e11

        f1 = gravitational_force(m1, m2, r1)
        f2 = gravitational_force(m1, m2, r2)

        # Force at 2r should be 1/4 of force at r
        assert abs(f1 / f2 - 4.0) < 0.01

    def test_gravitational_force_proportional_to_masses(self):
        """Force should be proportional to both masses."""
        r = 1e11
        f1 = gravitational_force(1e30, 1e24, r)
        f2 = gravitational_force(2e30, 1e24, r)

        assert abs(f2 / f1 - 2.0) < 0.01

    def test_gravitational_force_earth_sun(self):
        """Test with real Earth-Sun values."""
        sun_mass = 1.989e30
        earth_mass = 5.972e24
        earth_sun_distance = 1.496e11

        force = gravitational_force(sun_mass, earth_mass, earth_sun_distance)
        expected = 3.54e22  # Approximately 3.54 × 10^22 N

        assert abs(force - expected) / expected < 0.01

    def test_escape_velocity(self):
        """Escape velocity should be sqrt(2GM/r)."""
        mass = 1.989e30  # Sun mass
        radius = 1.496e11  # 1 AU

        v_esc = escape_velocity(mass, radius)
        expected = np.sqrt(2 * G * mass / radius)

        assert abs(v_esc - expected) < 1

    def test_orbital_velocity_circular(self):
        """Circular orbital velocity should be sqrt(GM/r)."""
        mass = 1.989e30
        radius = 1.496e11

        v_orb = orbital_velocity(mass, radius)
        expected = np.sqrt(G * mass / radius)

        assert abs(v_orb - expected) < 1


class TestBody:
    """Tests for the Body class."""

    def test_body_creation(self):
        """Body should store mass, position, velocity, and radius."""
        body = Body(
            mass=1e24,
            position=np.array([1e11, 0.0]),
            velocity=np.array([0.0, 3e4]),
            radius=6e6,
        )

        assert body.mass == 1e24
        assert np.allclose(body.position, [1e11, 0.0])
        assert np.allclose(body.velocity, [0.0, 3e4])
        assert body.radius == 6e6

    def test_body_kinetic_energy(self):
        """Body should calculate kinetic energy correctly."""
        body = Body(
            mass=1e24,
            position=np.array([0.0, 0.0]),
            velocity=np.array([3e4, 4e4]),  # |v| = 5e4
        )

        ke = body.kinetic_energy()
        expected = 0.5 * 1e24 * (5e4) ** 2

        assert abs(ke - expected) / expected < 1e-10

    def test_body_momentum(self):
        """Body should calculate momentum correctly."""
        body = Body(
            mass=2e24,
            position=np.array([0.0, 0.0]),
            velocity=np.array([1e4, 2e4]),
        )

        momentum = body.momentum()
        expected = np.array([2e28, 4e28])

        assert np.allclose(momentum, expected)

    def test_body_from_density(self):
        """Body should be creatable from density and radius."""
        radius = 6.371e6  # Earth radius
        density = 5515  # Earth density kg/m^3

        body = Body.from_density(
            density=density,
            radius=radius,
            position=np.array([0.0, 0.0]),
            velocity=np.array([0.0, 0.0]),
        )

        expected_mass = (4 / 3) * np.pi * radius**3 * density
        assert abs(body.mass - expected_mass) / expected_mass < 1e-10


class TestGravitySimulator:
    """Tests for the GravitySimulator class."""

    def test_simulator_creation(self):
        """Simulator should initialize with a star."""
        sim = GravitySimulator(star_mass=1.989e30, star_radius=6.96e8, seed=42)

        assert sim.star.mass == 1.989e30
        assert sim.star.radius == 6.96e8
        assert np.allclose(sim.star.position, [0.0, 0.0])

    def test_add_planet(self):
        """Should be able to add planets to the simulation."""
        sim = GravitySimulator(star_mass=1.989e30, seed=42)
        sim.add_planet(
            mass=5.972e24,
            distance=1.496e11,
            radius=6.371e6,
        )

        assert len(sim.planets) == 1
        assert sim.planets[0].mass == 5.972e24

    def test_add_random_planets(self):
        """Should add n random planets within orbital range."""
        sim = GravitySimulator(star_mass=1.989e30, seed=42)
        sim.add_random_planets(
            n=5,
            min_orbit=5e10,
            max_orbit=5e11,
            min_mass=1e23,
            max_mass=1e27,
        )

        assert len(sim.planets) == 5

        for planet in sim.planets:
            distance = np.linalg.norm(planet.position)
            assert 5e10 <= distance <= 5e11
            assert 1e23 <= planet.mass <= 1e27

    def test_step_updates_positions(self):
        """Simulation step should update planet positions."""
        sim = GravitySimulator(star_mass=1.989e30, seed=42)
        sim.add_planet(mass=5.972e24, distance=1.496e11, radius=6.371e6)

        initial_pos = sim.planets[0].position.copy()
        sim.step()

        assert not np.allclose(sim.planets[0].position, initial_pos)

    def test_circular_orbit_stability(self):
        """Planet in circular orbit should stay approximately circular."""
        sim = GravitySimulator(star_mass=1.989e30, dt=3600, seed=42)
        sim.add_planet(mass=5.972e24, distance=1.496e11, radius=6.371e6)

        initial_distance = np.linalg.norm(sim.planets[0].position)

        # Run for ~1/100 of Earth's orbital period
        for _ in range(876):  # ~36.5 days
            sim.step()

        final_distance = np.linalg.norm(sim.planets[0].position)

        # Distance should remain within 1% for stable orbit
        assert abs(final_distance - initial_distance) / initial_distance < 0.01

    def test_collision_detection(self):
        """Should detect when two bodies collide."""
        sim = GravitySimulator(star_mass=1.989e30, seed=42)

        # Add two planets on collision course
        sim.planets.append(
            Body(
                mass=1e24,
                position=np.array([1e10, 0.0]),
                velocity=np.array([0.0, 0.0]),
                radius=1e7,
            )
        )
        sim.planets.append(
            Body(
                mass=1e24,
                position=np.array([1e10 + 1.5e7, 0.0]),  # Within combined radii
                velocity=np.array([0.0, 0.0]),
                radius=1e7,
            )
        )

        collisions = sim._detect_collisions()
        assert len(collisions) > 0

    def test_collision_merger_conserves_momentum(self):
        """Merged body should conserve total momentum."""
        sim = GravitySimulator(star_mass=1.989e30, seed=42)

        body1 = Body(
            mass=1e24,
            position=np.array([1e10, 0.0]),
            velocity=np.array([1e3, 0.0]),
            radius=1e7,
        )
        body2 = Body(
            mass=2e24,
            position=np.array([1e10, 1e7]),
            velocity=np.array([0.0, 2e3]),
            radius=1e7,
        )

        initial_momentum = body1.momentum() + body2.momentum()

        merged = sim._merge_bodies(body1, body2)

        assert np.allclose(merged.momentum(), initial_momentum, rtol=1e-10)

    def test_collision_merger_conserves_mass(self):
        """Merged body should conserve total mass."""
        sim = GravitySimulator(star_mass=1.989e30, seed=42)

        body1 = Body(mass=1e24, position=np.array([0.0, 0.0]), velocity=np.array([0.0, 0.0]), radius=1e7)
        body2 = Body(mass=2e24, position=np.array([1e7, 0.0]), velocity=np.array([0.0, 0.0]), radius=1e7)

        merged = sim._merge_bodies(body1, body2)

        assert merged.mass == 3e24

    def test_ejection_detection(self):
        """Should detect when planet exceeds escape velocity."""
        sim = GravitySimulator(star_mass=1.989e30, seed=42)

        # Add planet with escape velocity
        v_esc = escape_velocity(1.989e30, 1e11)
        sim.planets.append(
            Body(
                mass=1e24,
                position=np.array([1e11, 0.0]),
                velocity=np.array([v_esc * 1.5, 0.0]),  # Well above escape velocity
                radius=1e7,
            )
        )

        assert sim._is_escaping(sim.planets[0])

    def test_ejected_planets_removed(self):
        """Ejected planets should be removed from simulation."""
        sim = GravitySimulator(star_mass=1.989e30, seed=42)

        v_esc = escape_velocity(1.989e30, 1e11)
        sim.planets.append(
            Body(
                mass=1e24,
                position=np.array([1e11, 0.0]),
                velocity=np.array([v_esc * 2, 0.0]),
                radius=1e7,
            )
        )

        sim.step()
        sim._check_ejections()

        assert len(sim.ejected) == 1
        assert len(sim.planets) == 0

    def test_energy_conservation(self):
        """Total energy should be approximately conserved."""
        sim = GravitySimulator(star_mass=1.989e30, dt=3600, seed=42)
        sim.add_planet(mass=5.972e24, distance=1.496e11, radius=6.371e6)

        initial_energy = sim.total_energy()

        for _ in range(1000):
            sim.step()

        final_energy = sim.total_energy()

        # Energy should be conserved within 0.1%
        assert abs(final_energy - initial_energy) / abs(initial_energy) < 0.001

    def test_reproducibility_with_seed(self):
        """Same seed should produce identical simulations."""
        sim1 = GravitySimulator(star_mass=1.989e30, seed=12345)
        sim1.add_random_planets(n=3, min_orbit=1e11, max_orbit=3e11)

        sim2 = GravitySimulator(star_mass=1.989e30, seed=12345)
        sim2.add_random_planets(n=3, min_orbit=1e11, max_orbit=3e11)

        for p1, p2 in zip(sim1.planets, sim2.planets):
            assert p1.mass == p2.mass
            assert np.allclose(p1.position, p2.position)
            assert np.allclose(p1.velocity, p2.velocity)

    def test_run_simulation(self):
        """run() method should execute multiple steps."""
        sim = GravitySimulator(star_mass=1.989e30, seed=42)
        sim.add_random_planets(n=3, min_orbit=1e11, max_orbit=3e11)

        initial_positions = [p.position.copy() for p in sim.planets]

        sim.run(steps=100)

        for i, planet in enumerate(sim.planets):
            assert not np.allclose(planet.position, initial_positions[i])

    def test_get_statistics(self):
        """Should track simulation statistics."""
        sim = GravitySimulator(star_mass=1.989e30, seed=42)
        sim.add_random_planets(n=5, min_orbit=1e11, max_orbit=3e11)

        sim.run(steps=100)

        stats = sim.get_statistics()
        assert "total_collisions" in stats
        assert "total_ejections" in stats
        assert "time_elapsed" in stats


class TestOrbitalMechanics:
    """Tests for orbital mechanics features."""

    def test_orbit_trail_recording(self):
        """Should record orbital trails for visualization."""
        sim = GravitySimulator(star_mass=1.989e30, seed=42, record_trails=True)
        sim.add_planet(mass=5.972e24, distance=1.496e11, radius=6.371e6)

        sim.run(steps=100)

        assert len(sim.planets[0].trail) == 100

    def test_planet_speed_modification(self):
        """Should be able to modify planet velocity."""
        sim = GravitySimulator(star_mass=1.989e30, seed=42)
        sim.add_planet(mass=5.972e24, distance=1.496e11, radius=6.371e6)

        initial_speed = np.linalg.norm(sim.planets[0].velocity)

        sim.modify_planet_speed(0, factor=1.5)

        new_speed = np.linalg.norm(sim.planets[0].velocity)
        assert abs(new_speed / initial_speed - 1.5) < 0.01

    def test_orbital_period_estimation(self):
        """Should estimate orbital period from current state."""
        sim = GravitySimulator(star_mass=1.989e30, seed=42)
        sim.add_planet(mass=5.972e24, distance=1.496e11, radius=6.371e6)

        period = sim.estimate_orbital_period(0)

        # Earth's orbital period is ~3.156e7 seconds (1 year)
        expected = 3.156e7
        assert abs(period - expected) / expected < 0.01
