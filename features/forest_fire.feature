Feature: Forest Fire Simulation
  As a physicist studying self-organized criticality
  I want to simulate the Drossel-Schwabl forest fire model
  So that I can observe power-law distributions in fire sizes

  Background:
    Given a forest fire simulation with grid size 256x256
    And tree growth probability of 0.01
    And lightning probability of 0.001

  # Cell States
  Scenario: Empty cell can grow a tree
    Given an empty cell at position (100, 100)
    When a growth event occurs at that cell
    Then the cell should become a tree

  Scenario: Tree can catch fire from lightning
    Given a tree at position (100, 100)
    When lightning strikes at position (100, 100)
    Then the cell should become burning

  Scenario: Burning cell becomes empty
    Given a burning cell at position (100, 100)
    When one simulation step completes
    Then the cell should become empty

  # Fire Spreading
  Scenario: Fire spreads to adjacent trees
    Given a burning cell at position (100, 100)
    And trees at all 8 neighboring positions
    When fire spreading is processed
    Then all 8 neighbors should become burning

  Scenario: Fire does not spread to empty cells
    Given a burning cell at position (100, 100)
    And empty cells at all neighboring positions
    When fire spreading is processed
    Then all neighbors should remain empty

  Scenario: Fire does not wrap around boundaries
    Given a burning cell at position (0, 0)
    And a tree at position (255, 255)
    When fire spreading is processed
    Then the tree at (255, 255) should not catch fire

  # Fire Size Tracking
  Scenario: Single tree fire
    Given only one isolated tree in the forest
    When lightning strikes that tree
    Then a fire of size 1 should be recorded

  Scenario: Connected forest fire
    Given a cluster of 10 connected trees
    When lightning strikes one tree in the cluster
    Then a fire of size 10 should be recorded
    And all trees in the cluster should burn

  # Self-Organized Criticality
  Scenario: System reaches critical state
    Given the simulation has run for 10000 steps
    When I observe the forest state
    Then there should be a mix of tree clusters and empty areas
    And no single cluster should dominate the entire grid

  Scenario: Power law distribution of fire sizes
    Given the simulation has run for 10000 steps
    When I analyze the fire size distribution
    Then the distribution should approximate a power law on log-log scale
    And fire sizes should span multiple orders of magnitude

  # Fire Suppression Demonstration
  Scenario: Low lightning leads to dense forest
    Given lightning probability of 0.0001
    When the simulation runs for 5000 steps
    Then tree density should be higher than normal conditions
    And risk of catastrophic fire should increase

  Scenario: Normal lightning maintains balance
    Given lightning probability of 0.001
    When the simulation runs for 5000 steps
    Then tree density should stabilize around a critical value
    And fire sizes should follow power law distribution

  # Tree Density
  Scenario: Tree density calculation
    Given 1000 trees in a 100x100 grid
    When I calculate tree density
    Then the density should be 0.10 (10%)

  Scenario: Tree count tracking
    When I run the simulation for 100 steps
    Then tree count should be tracked at each step
    And I should be able to plot tree count over time

  # Reproducibility
  Scenario: Reproducibility with seed
    Given a random seed of 42
    When I run the simulation for 1000 steps
    And I reset and run again with the same seed
    Then both runs should produce identical fire histories
