/**
 * Falling Sand Core Module
 *
 * Pure JavaScript implementation of falling sand cellular automaton.
 * This module contains the grid state and sand rules, separate from
 * any rendering concerns (WebGL, Canvas, etc).
 *
 * Based on: Nmiz falling sand video (see Falling_Sand_Idea.md)
 *
 * Three Rules:
 * 1. If pixel below is empty, fall down
 * 2. If below blocked but diagonal empty, fall diagonal (priority alternates)
 * 3. If both diagonals blocked, stay put
 */

// =============================================================================
// Constants
// =============================================================================

const EMPTY = 0;
const SAND = 1;

// =============================================================================
// Grid Class
// =============================================================================

/**
 * Represents a 2D grid of cells.
 * Coordinate system: (0,0) is bottom-left, y increases upward.
 */
class Grid {
    /**
     * Create a new grid.
     * @param {number} width - Grid width in cells
     * @param {number} height - Grid height in cells
     */
    constructor(width, height) {
        this.width = width;
        this.height = height;
        this.cells = new Uint8Array(width * height);
    }

    /**
     * Get the cell value at (x, y).
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     * @returns {number} Cell value (EMPTY or SAND)
     */
    get(x, y) {
        if (x < 0 || x >= this.width || y < 0 || y >= this.height) {
            return SAND; // Treat out-of-bounds as blocked
        }
        return this.cells[y * this.width + x];
    }

    /**
     * Set the cell value at (x, y).
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     * @param {number} value - Cell value (EMPTY or SAND)
     */
    set(x, y, value) {
        if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
            this.cells[y * this.width + x] = value;
        }
    }

    /**
     * Check if a cell is empty.
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     * @returns {boolean} True if cell is empty
     */
    isEmpty(x, y) {
        return this.get(x, y) === EMPTY;
    }

    /**
     * Check if a cell contains sand.
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     * @returns {boolean} True if cell contains sand
     */
    isSand(x, y) {
        return this.get(x, y) === SAND;
    }

    /**
     * Clear all cells to empty.
     */
    clear() {
        this.cells.fill(EMPTY);
    }

    /**
     * Count total sand particles in the grid.
     * @returns {number} Number of sand particles
     */
    countSand() {
        let count = 0;
        for (let i = 0; i < this.cells.length; i++) {
            if (this.cells[i] === SAND) {
                count++;
            }
        }
        return count;
    }

    /**
     * Create a deep copy of this grid.
     * @returns {Grid} A new grid with the same contents
     */
    clone() {
        const copy = new Grid(this.width, this.height);
        copy.cells.set(this.cells);
        return copy;
    }
}

// =============================================================================
// Sand Simulation
// =============================================================================

/**
 * Falling sand simulation.
 * Manages grid state and applies sand physics rules.
 */
class SandSimulation {
    /**
     * Create a new simulation.
     * @param {number} width - Grid width
     * @param {number} height - Grid height
     */
    constructor(width, height) {
        this.grid = new Grid(width, height);
        this.frameCount = 0;
    }

    /**
     * Get the current left/right priority based on frame count.
     * Alternates each frame to create symmetric piles.
     * @returns {boolean} True if right priority, false if left priority
     */
    isRightPriority() {
        return this.frameCount % 2 === 0;
    }

    /**
     * Place sand at a position.
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     */
    placeSand(x, y) {
        this.grid.set(x, y, SAND);
    }

    /**
     * Remove sand from a position.
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     */
    removeSand(x, y) {
        this.grid.set(x, y, EMPTY);
    }

    /**
     * Compute the next position for a sand particle based on a grid state.
     * Returns null if the particle should not move.
     *
     * Rules (from Nmiz video):
     * 1. If below is empty, move down
     * 2. If below blocked, try diagonal (priority alternates)
     * 3. If both diagonals blocked, stay put
     *
     * @param {Grid} grid - The grid to check against (usually snapshot)
     * @param {number} x - Current X coordinate
     * @param {number} y - Current Y coordinate
     * @param {boolean} rightPriority - True to check right diagonal first
     * @returns {{x: number, y: number} | null} New position or null
     */
    computeNextPositionFrom(grid, x, y, rightPriority) {
        // Rule 1: Fall down if below is empty
        if (grid.isEmpty(x, y - 1)) {
            return { x: x, y: y - 1 };
        }

        // Rule 2: Fall diagonal if below is blocked
        const d1 = rightPriority ? 1 : -1;  // First diagonal to check
        const d2 = rightPriority ? -1 : 1;  // Second diagonal to check

        // Check first diagonal
        if (grid.isEmpty(x + d1, y - 1)) {
            return { x: x + d1, y: y - 1 };
        }

        // Check second diagonal
        if (grid.isEmpty(x + d2, y - 1)) {
            return { x: x + d2, y: y - 1 };
        }

        // Rule 3: Can't move
        return null;
    }

    /**
     * Compute the next position using current grid state.
     * Convenience wrapper for computeNextPositionFrom.
     */
    computeNextPosition(x, y, rightPriority) {
        return this.computeNextPositionFrom(this.grid, x, y, rightPriority);
    }

    /**
     * Step the simulation once.
     * Uses double-buffering: reads from snapshot, writes to current grid.
     * This ensures all particles make decisions based on the same initial state.
     * @param {boolean} [rightPriority] - Override priority (optional)
     */
    step(rightPriority = null) {
        const priority = rightPriority !== null ? rightPriority : this.isRightPriority();

        // Clone the grid to read from (snapshot of initial state)
        // This prevents cascading within a single step
        const oldGrid = this.grid.clone();

        // Track which cells have been claimed as destinations this step
        // This handles race conditions where multiple particles want the same spot
        const claimed = new Set();

        // Process from bottom to top
        for (let y = 0; y < this.grid.height; y++) {
            // Process columns in alternating order based on priority
            const startX = priority ? 0 : this.grid.width - 1;
            const endX = priority ? this.grid.width : -1;
            const stepX = priority ? 1 : -1;

            for (let x = startX; x !== endX; x += stepX) {
                // Check OLD grid for sand presence
                if (!oldGrid.isSand(x, y)) {
                    continue;
                }

                // Compute next position based on OLD grid state
                const next = this.computeNextPositionFrom(oldGrid, x, y, priority);

                if (next !== null) {
                    const targetKey = `${next.x},${next.y}`;
                    // Check if target cell is available (not claimed by another particle)
                    if (!claimed.has(targetKey)) {
                        // Move the sand
                        this.grid.set(x, y, EMPTY);
                        this.grid.set(next.x, next.y, SAND);
                        claimed.add(targetKey);
                    }
                    // If target is claimed, sand stays in place (no change needed)
                }
                // If next is null, sand stays in place (no change needed)
            }
        }

        this.frameCount++;
    }

    /**
     * Run simulation until stable (no movement).
     * @param {number} [maxSteps=1000] - Maximum steps to prevent infinite loop
     * @returns {number} Number of steps taken
     */
    runUntilStable(maxSteps = 1000) {
        for (let i = 0; i < maxSteps; i++) {
            const before = this.grid.clone();
            this.step();

            // Check if anything moved
            let changed = false;
            for (let j = 0; j < this.grid.cells.length; j++) {
                if (this.grid.cells[j] !== before.cells[j]) {
                    changed = true;
                    break;
                }
            }

            if (!changed) {
                return i + 1;
            }
        }
        return maxSteps;
    }

    /**
     * Check if all sand is stable (not floating).
     * @returns {boolean} True if all sand is on ground or supported
     */
    isStable() {
        for (let y = 1; y < this.grid.height; y++) {
            for (let x = 0; x < this.grid.width; x++) {
                if (this.grid.isSand(x, y)) {
                    // Check if supported (something below)
                    if (this.grid.isEmpty(x, y - 1) &&
                        this.grid.isEmpty(x - 1, y - 1) &&
                        this.grid.isEmpty(x + 1, y - 1)) {
                        return false; // Floating sand
                    }
                }
            }
        }
        return true;
    }
}

// =============================================================================
// Exports (CommonJS for Node.js testing, also works in browser)
// =============================================================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Grid, SandSimulation, EMPTY, SAND };
}
