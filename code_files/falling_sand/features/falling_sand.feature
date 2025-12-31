# features/falling_sand.feature
#
# BDD specification for falling sand cellular automaton
# Based on Nmiz video: https://www.youtube.com/watch?v=...
# See Falling_Sand_Idea.md for algorithm description

Feature: Falling Sand Simulation
  As a user
  I want to simulate falling sand particles
  So that I can watch sand form realistic piles

  Background:
    Given an empty grid

  # ==========================================================================
  # Rule 1: Fall Down
  # "If the pixel below the current sand cell is empty, move there."
  # ==========================================================================

  Scenario: Sand falls down when cell below is empty
    Given sand at position (5, 5)
    And the cell at (5, 4) is empty
    When the simulation steps once
    Then there should be sand at (5, 4)
    And the cell at (5, 5) should be empty

  Scenario: Sand moves diagonal when cell below is blocked (not straight down)
    Given sand at position (5, 5)
    And sand at position (5, 4)
    When the simulation steps once
    Then the cell at (5, 5) should be empty
    And sand should have moved to a diagonal position

  Scenario: Sand at bottom of grid does not fall
    Given a grid of height 10
    And sand at position (5, 0)
    When the simulation steps once
    Then there should be sand at (5, 0)

  # ==========================================================================
  # Rule 2: Fall Diagonal (when below is blocked)
  # "If that pixel is blocked, but the pixel below and to the right is empty,
  #  move there. And finally, if both the pixels to the right and underneath
  #  the current cell are blocked, but there's room to the left, move there."
  # ==========================================================================

  Scenario: Sand falls diagonally when below is blocked
    Given sand at position (5, 5)
    And sand at position (5, 4)
    And the cell at (6, 4) is empty
    When the simulation steps once with right priority
    Then there should be sand at (6, 4)
    And the cell at (5, 5) should be empty

  Scenario: Sand falls left diagonal when right is blocked
    Given sand at position (5, 5)
    And sand at position (5, 4)
    And sand at position (6, 4)
    And the cell at (4, 4) is empty
    When the simulation steps once with right priority
    Then there should be sand at (4, 4)
    And the cell at (5, 5) should be empty

  Scenario: Sand does not move when all three positions blocked
    Given sand at position (5, 5)
    And sand at position (5, 4)
    And sand at position (6, 4)
    And sand at position (4, 4)
    When the simulation steps once
    Then there should be sand at (5, 5)

  # ==========================================================================
  # Rule 3: Alternating Priority (for symmetric piles)
  # "This is pretty easily solved by just alternating checking the left first
  #  or the right first each frame."
  # ==========================================================================

  Scenario: Left priority causes sand to fall left first
    Given sand at position (5, 5)
    And sand at position (5, 4)
    And the cell at (4, 4) is empty
    And the cell at (6, 4) is empty
    When the simulation steps once with left priority
    Then there should be sand at (4, 4)
    And the cell at (5, 5) should be empty

  Scenario: Right priority causes sand to fall right first
    Given sand at position (5, 5)
    And sand at position (5, 4)
    And the cell at (4, 4) is empty
    And the cell at (6, 4) is empty
    When the simulation steps once with right priority
    Then there should be sand at (6, 4)
    And the cell at (5, 5) should be empty

  # ==========================================================================
  # Conservation of Matter
  # "We're no longer erasing matter from existence"
  # ==========================================================================

  Scenario: Sand count remains constant after simulation steps
    Given 100 sand particles placed randomly
    When the simulation steps 50 times
    Then there should be exactly 100 sand particles

  Scenario: No sand appears spontaneously
    Given an empty grid
    When the simulation steps 10 times
    Then the grid should remain empty

  # ==========================================================================
  # Edge Cases
  # ==========================================================================

  Scenario: Sand at left edge falls right diagonal only
    Given sand at position (0, 5)
    And sand at position (0, 4)
    And the cell at (1, 4) is empty
    When the simulation steps once
    Then there should be sand at (1, 4)
    And the cell at (0, 5) should be empty

  Scenario: Sand at right edge falls left diagonal only
    Given a grid of width 10
    And sand at position (9, 5)
    And sand at position (9, 4)
    And the cell at (8, 4) is empty
    When the simulation steps once
    Then there should be sand at (8, 4)
    And the cell at (9, 5) should be empty

  Scenario: Sand at left edge with blocked diagonal stays put
    Given sand at position (0, 5)
    And sand at position (0, 4)
    And sand at position (1, 4)
    When the simulation steps once
    Then there should be sand at (0, 5)

  Scenario: Sand at right edge with blocked diagonal stays put
    Given a grid of width 10
    And sand at position (9, 5)
    And sand at position (9, 4)
    And sand at position (8, 4)
    When the simulation steps once
    Then there should be sand at (9, 5)

  # ==========================================================================
  # Pile Formation
  # "With these deceptively simple rules, we get some really nice behavior,
  #  and the sand forms these pleasing triangular piles."
  # ==========================================================================

  Scenario: Sand forms stable pile
    Given sand stacked vertically at column 5 from y=0 to y=4
    When the simulation runs until stable
    Then no sand particle should be floating
    And each sand particle should be either on ground or on top of another
