Feature: N-Body Gravity Simulator
  As a physics enthusiast
  I want to simulate gravitational interactions in a solar system
  So that I can observe orbital dynamics, collisions, and ejections

  Background:
    Given a gravitational constant G = 6.674e-11

  Scenario: Create a solar system with a central star
    Given a star with mass 1.989e30 kg and radius 6.96e8 m
    When I initialize the simulation
    Then the star should be at the center of the system
    And the star should have the correct gravitational influence

  Scenario: Add planets with random properties
    Given a star with mass 1.989e30 kg
    And 5 planets with random masses between 1e23 and 1e27 kg
    When I initialize the simulation
    Then all planets should have initial orbital velocities
    And all planets should be within the specified orbital range

  Scenario: Gravitational force calculation
    Given two bodies with masses 1e30 kg and 1e24 kg
    And they are separated by 1.5e11 meters
    When I calculate the gravitational force
    Then the force should follow Newton's law F = G*m1*m2/r^2

  Scenario: Stable circular orbit
    Given a star with mass 1.989e30 kg at the origin
    And a planet at distance 1.5e11 m with circular orbital velocity
    When I run the simulation for one orbital period
    Then the planet should return approximately to its starting position
    And the orbital path should be nearly circular

  Scenario: Planet collision and merger
    Given two planets on collision course
    When they come within their combined radii
    Then they should merge into a single body
    And the merged body should conserve total momentum
    And the merged body should conserve total mass

  Scenario: Planet ejection from system
    Given a planet with velocity exceeding escape velocity
    When I run the simulation
    Then the planet should be marked as ejected
    And it should be removed from gravitational calculations
    And the ejection event should be recorded

  Scenario: Multiple planet interactions
    Given a star with mass 1.989e30 kg
    And 10 planets in various orbits
    When I run the simulation for 1000 steps
    Then planets should perturb each other's orbits
    And the system should track orbital statistics

  Scenario: Energy conservation
    Given a closed gravitational system
    When I run the simulation
    Then total energy should be approximately conserved
    And energy drift should be minimal with Verlet integration

  Scenario: Visualization of orbits
    Given a running simulation with planets
    When I request visualization
    Then I should see the star at center
    And I should see all planets with their current positions
    And I should see orbit trails for each planet

  Scenario: Speed modification
    Given a planet in stable orbit
    When I increase its velocity by 50%
    Then its orbit should become more elliptical
    And if velocity exceeds escape velocity it may be ejected

  Scenario: Reproducible simulation with seed
    Given a simulation with seed 12345
    When I run two identical simulations with the same seed
    Then the planet configurations should be identical
    And the simulation results should be reproducible
