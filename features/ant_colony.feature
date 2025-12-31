Feature: Ant Colony Optimization Simulator
  As a computer science student
  I want to simulate ant colony optimization on a graph
  So that I can observe emergent swarm intelligence finding optimal paths

  Background:
    Given default ACO parameters alpha=2, beta=2, rho=0.1, Q=1

  Scenario: Create a random graph with nodes and edges
    Given a graph with 30 nodes
    And edges connecting nodes like a road network
    And each edge has a random cost between 1 and 10
    When I initialize the simulation
    Then the graph should have 30 nodes
    And all edges should have costs in the valid range

  Scenario: Initialize pheromone levels on edges
    Given a graph with edges
    When I initialize the simulation
    Then all edges should have initial pheromone levels
    And pheromone levels should be uniform at start

  Scenario: Ant path selection based on probability
    Given an ant at a node with multiple outgoing edges
    And edges have different pheromone levels and costs
    When the ant selects the next edge
    Then selection probability should follow (pheromone^alpha) * (1/cost)^beta
    And edges with higher pheromone and lower cost should be more likely

  Scenario: Ant completes a path from source to destination
    Given a graph with source node 0 and destination node 29
    And an ant starting at the source
    When the ant traverses the graph
    Then it should reach the destination
    And the path should be recorded with its total cost

  Scenario: Pheromone deposit after path completion
    Given an ant that completed a path with cost 15
    When pheromones are deposited
    Then edges in the path should receive pheromone Q/path_cost
    And edges not in the path should remain unchanged

  Scenario: Pheromone evaporation
    Given edges with pheromone levels
    When evaporation occurs with rate rho=0.1
    Then all pheromone levels should be multiplied by (1-rho)
    And no pheromone level should become negative

  Scenario: Colony finds shorter paths over iterations
    Given a graph with 30 nodes
    And 500 ants in the colony
    And source node 0 and destination node 29
    When I run 50 iterations
    Then the best path cost should decrease over iterations
    And ants should converge toward the optimal path

  Scenario: Visualization of pheromone trails
    Given a completed simulation
    When I request visualization
    Then I should see all nodes positioned in space
    And edge thickness should represent pheromone intensity
    And the best path should be highlighted

  Scenario: Path distribution analysis
    Given a completed simulation with 500 ants
    When I analyze path usage
    Then I should see which paths were most frequently used
    And the distribution should show convergence to optimal

  Scenario: Reproducible simulation with seed
    Given a simulation with seed 12345
    When I run two identical simulations with the same seed
    Then the graph structure should be identical
    And the final best path should be identical

  Scenario: Compare with Dijkstra's shortest path
    Given a graph with known structure
    When I run ACO and Dijkstra's algorithm
    Then ACO should find a path close to Dijkstra's optimal
    And the comparison should show ACO effectiveness
