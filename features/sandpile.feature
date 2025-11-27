Feature: Sandpile Avalanche Simulation
  As a physicist studying self-organized criticality
  I want to simulate the Abelian sandpile model
  So that I can observe power-law distributions in avalanche sizes

  Background:
    Given a sandpile simulation with grid size 50x50
    And a toppling threshold of 4 grains

  # Core Mechanics
  Scenario: Dropping a grain on an empty cell
    Given an empty cell at position (25, 25)
    When I drop a grain at position (25, 25)
    Then the cell at (25, 25) should have 1 grain
    And the total grain count should be 1
    And no avalanche should occur

  Scenario: Cell topples when reaching threshold
    Given a cell at position (25, 25) with 3 grains
    When I drop a grain at position (25, 25)
    Then the cell at (25, 25) should have 0 grains
    And each orthogonal neighbor should receive 1 grain
    And an avalanche of size 1 should be recorded

  Scenario: Cascading avalanche
    Given a cell at position (25, 25) with 3 grains
    And a cell at position (25, 26) with 3 grains
    When I drop a grain at position (25, 25)
    Then an avalanche larger than 1 should occur
    And all cells should have fewer than 4 grains when stable

  Scenario: Grains fall off the edge
    Given a cell at position (0, 0) with 3 grains
    When I drop a grain at position (0, 0)
    Then the cell at (0, 0) should have 0 grains
    And only 2 neighbors should receive grains
    And 2 grains should be lost to the boundary

  # Drop Modes
  Scenario: Random drop mode
    Given drop mode is set to "random"
    When I drop 100 grains
    Then grains should be distributed across multiple cells

  Scenario: Center drop mode
    Given drop mode is set to "center"
    When I drop 10 grains
    Then all grains should initially land at the center cell

  # Statistical Properties
  Scenario: Power law distribution emerges
    Given the simulation has run for 50000 grain drops
    When I analyze the avalanche size distribution
    Then the distribution should approximate a power law on log-log scale
    And avalanche sizes should span multiple orders of magnitude

  Scenario: Reproducibility with seed
    Given a random seed of 42
    When I run the simulation for 1000 drops
    And I reset and run again with the same seed
    Then both runs should produce identical results

  # Stability
  Scenario: Grid reaches stable state after avalanche
    When I drop grains until an avalanche occurs
    Then all cells should have fewer than threshold grains
    And no cells should be in an unstable state
