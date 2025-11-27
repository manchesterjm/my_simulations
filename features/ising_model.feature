Feature: 2D Ising Model Simulation
  As a physicist studying phase transitions
  I want to simulate the 2D Ising model
  So that I can observe critical behavior at the Curie temperature

  Background:
    Given an Ising model simulation with grid size 128x128
    And spins initialized randomly to +1 or -1

  # Core Mechanics
  Scenario: Spin flip acceptance when energy decreases
    Given a spin at position (64, 64) with value +1
    And all four neighbors have value +1
    When I attempt to flip the spin at (64, 64)
    Then the flip should be rejected
    Because flipping would increase energy

  Scenario: Spin flip acceptance when energy increases
    Given a spin at position (64, 64) with value -1
    And all four neighbors have value +1
    When I attempt to flip the spin at (64, 64)
    Then the flip should be accepted
    Because flipping would decrease energy

  Scenario: Metropolis algorithm probability
    Given a temperature above zero
    And a proposed flip that increases energy by delta_E
    When the flip is evaluated
    Then acceptance probability should be exp(-delta_E / temperature)

  Scenario: Periodic boundary conditions
    Given a spin at position (0, 0)
    When I calculate its neighbors
    Then the left neighbor should be at position (0, 127)
    And the top neighbor should be at position (127, 0)

  # Temperature Behavior
  Scenario: Low temperature produces ordered state
    Given temperature is set to 1.0 (below Tc)
    When I run 200 sweeps
    Then the absolute magnetization should be close to 1.0
    And large aligned domains should be visible

  Scenario: High temperature produces disordered state
    Given temperature is set to 4.0 (above Tc)
    When I run 200 sweeps
    Then the absolute magnetization should be close to 0.0
    And spins should appear random with small domains

  Scenario: Critical temperature shows criticality
    Given temperature is set to 2.269 (at Tc)
    When I run 200 sweeps
    Then domains of all sizes should be present
    And the system should show fractal-like patterns

  # Domain Analysis
  Scenario: Domain detection using BFS
    Given a grid with connected regions of same spin
    When I run domain detection
    Then each connected component should be identified
    And domain sizes should be counted correctly

  Scenario: Power law at critical temperature
    Given temperature is set to 2.269 (at Tc)
    And the simulation has run for 200 sweeps
    When I analyze the domain size distribution
    Then the distribution should approximate a power law
    And removing percolating clusters should improve the fit

  # Reproducibility
  Scenario: Reproducibility with seed
    Given a random seed of 42
    And temperature is set to 2.269
    When I run 100 sweeps
    And I reset and run again with the same seed
    Then both runs should produce identical final states

  # Magnetization
  Scenario: Magnetization calculation
    Given a grid where 75% of spins are +1
    When I calculate magnetization
    Then the magnetization should be 0.5
