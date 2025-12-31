Feature: Birthday Paradox Monte Carlo Simulation
  As a probability enthusiast
  I want to simulate the birthday paradox
  So that I can empirically verify the theoretical result

  Background:
    Given a year has 365 days (ignoring leap years)

  Scenario: Simulate birthday collisions for a given group size
    Given a room with 23 people
    When I run 10000 Monte Carlo trials
    Then the probability of a shared birthday should be approximately 50.7%
    And the result should be within 2% of the theoretical value

  Scenario: Find minimum group size for 50% probability
    When I search for the minimum group size where probability exceeds 50%
    Then the answer should be 23 people
    And running simulations with 22 people should show probability below 50%
    And running simulations with 23 people should show probability above 50%

  Scenario: Verify probability increases with group size
    Given group sizes from 1 to 50
    When I calculate collision probability for each size
    Then the probability should monotonically increase
    And probability for 1 person should be 0%
    And probability for 366 people should be 100%

  Scenario: Theoretical vs empirical comparison
    Given group sizes of 10, 20, 23, 30, 40, 50
    When I compare Monte Carlo results to theoretical probabilities
    Then all results should be within 3% of theoretical values
