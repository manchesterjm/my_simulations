/**
 * Unit Tests for Falling Sand Core Module
 *
 * Tests based on BDD scenarios from features/falling_sand.feature
 * Uses Node.js assert module for simplicity.
 *
 * Run: node tests/sand_core.test.js
 */

const assert = require('assert');
const { Grid, SandSimulation, EMPTY, SAND } = require('../src/sand_core.js');

// =============================================================================
// Test Utilities
// =============================================================================

let passCount = 0;
let failCount = 0;
const failures = [];

function test(name, fn) {
    try {
        fn();
        passCount++;
        console.log(`  ✓ ${name}`);
    } catch (err) {
        failCount++;
        failures.push({ name, error: err.message });
        console.log(`  ✗ ${name}`);
        console.log(`    ${err.message}`);
    }
}

function describe(name, fn) {
    console.log(`\n${name}`);
    fn();
}

// =============================================================================
// Grid Tests
// =============================================================================

describe('Grid', () => {
    test('creates empty grid of specified size', () => {
        const grid = new Grid(10, 10);
        assert.strictEqual(grid.width, 10);
        assert.strictEqual(grid.height, 10);
        assert.strictEqual(grid.countSand(), 0);
    });

    test('get returns EMPTY for empty cells', () => {
        const grid = new Grid(10, 10);
        assert.strictEqual(grid.get(5, 5), EMPTY);
    });

    test('set and get work correctly', () => {
        const grid = new Grid(10, 10);
        grid.set(5, 5, SAND);
        assert.strictEqual(grid.get(5, 5), SAND);
    });

    test('get returns SAND for out of bounds (treated as blocked)', () => {
        const grid = new Grid(10, 10);
        assert.strictEqual(grid.get(-1, 5), SAND);
        assert.strictEqual(grid.get(10, 5), SAND);
        assert.strictEqual(grid.get(5, -1), SAND);
        assert.strictEqual(grid.get(5, 10), SAND);
    });

    test('isEmpty returns true for empty cells', () => {
        const grid = new Grid(10, 10);
        assert.strictEqual(grid.isEmpty(5, 5), true);
    });

    test('isEmpty returns false for sand cells', () => {
        const grid = new Grid(10, 10);
        grid.set(5, 5, SAND);
        assert.strictEqual(grid.isEmpty(5, 5), false);
    });

    test('isSand returns true for sand cells', () => {
        const grid = new Grid(10, 10);
        grid.set(5, 5, SAND);
        assert.strictEqual(grid.isSand(5, 5), true);
    });

    test('countSand returns correct count', () => {
        const grid = new Grid(10, 10);
        grid.set(1, 1, SAND);
        grid.set(2, 2, SAND);
        grid.set(3, 3, SAND);
        assert.strictEqual(grid.countSand(), 3);
    });

    test('clear removes all sand', () => {
        const grid = new Grid(10, 10);
        grid.set(1, 1, SAND);
        grid.set(2, 2, SAND);
        grid.clear();
        assert.strictEqual(grid.countSand(), 0);
    });

    test('clone creates independent copy', () => {
        const grid = new Grid(10, 10);
        grid.set(5, 5, SAND);
        const copy = grid.clone();
        grid.set(5, 5, EMPTY);
        assert.strictEqual(copy.get(5, 5), SAND);
    });
});

// =============================================================================
// Rule 1: Fall Down
// =============================================================================

describe('Rule 1: Fall Down', () => {
    test('sand falls down when cell below is empty', () => {
        const sim = new SandSimulation(10, 10);
        sim.placeSand(5, 5);
        sim.step();
        assert.strictEqual(sim.grid.isSand(5, 4), true, 'Sand should be at (5, 4)');
        assert.strictEqual(sim.grid.isEmpty(5, 5), true, 'Cell (5, 5) should be empty');
    });

    test('sand moves diagonal when cell below is blocked (not straight down)', () => {
        const sim = new SandSimulation(10, 10);
        sim.placeSand(5, 5);
        sim.placeSand(5, 4);
        sim.step();
        // Sand at (5,5) can't fall straight down (blocked), so it moves diagonal
        // Sand should NOT be at (5,5) - it moved
        assert.strictEqual(sim.grid.isEmpty(5, 5), true, 'Cell (5, 5) should be empty (sand moved diagonal)');
        // Sand moved to either (4,4) or (6,4) depending on priority
        const movedLeft = sim.grid.isSand(4, 4);
        const movedRight = sim.grid.isSand(6, 4);
        assert.strictEqual(movedLeft || movedRight, true, 'Sand should have moved to a diagonal position');
    });

    test('sand at bottom of grid does not fall', () => {
        const sim = new SandSimulation(10, 10);
        sim.placeSand(5, 0);
        sim.step();
        assert.strictEqual(sim.grid.isSand(5, 0), true, 'Sand should remain at (5, 0)');
    });
});

// =============================================================================
// Rule 2: Fall Diagonal
// =============================================================================

describe('Rule 2: Fall Diagonal', () => {
    test('sand falls right-diagonal when below is blocked (right priority)', () => {
        const sim = new SandSimulation(10, 10);
        sim.placeSand(5, 5);
        sim.placeSand(5, 4);
        sim.step(true); // right priority
        assert.strictEqual(sim.grid.isSand(6, 4), true, 'Sand should be at (6, 4)');
        assert.strictEqual(sim.grid.isEmpty(5, 5), true, 'Cell (5, 5) should be empty');
    });

    test('sand falls left-diagonal when right is blocked (right priority)', () => {
        const sim = new SandSimulation(10, 10);
        sim.placeSand(5, 5);
        sim.placeSand(5, 4);
        sim.placeSand(6, 4);
        sim.step(true); // right priority
        assert.strictEqual(sim.grid.isSand(4, 4), true, 'Sand should be at (4, 4)');
        assert.strictEqual(sim.grid.isEmpty(5, 5), true, 'Cell (5, 5) should be empty');
    });

    test('sand does not move when all three positions blocked', () => {
        const sim = new SandSimulation(10, 10);
        sim.placeSand(5, 5);
        sim.placeSand(5, 4);
        sim.placeSand(6, 4);
        sim.placeSand(4, 4);
        sim.step();
        assert.strictEqual(sim.grid.isSand(5, 5), true, 'Sand should remain at (5, 5)');
    });
});

// =============================================================================
// Rule 3: Alternating Priority
// =============================================================================

describe('Rule 3: Alternating Priority', () => {
    test('left priority causes sand to fall left first', () => {
        const sim = new SandSimulation(10, 10);
        sim.placeSand(5, 5);
        sim.placeSand(5, 4);
        sim.step(false); // left priority
        assert.strictEqual(sim.grid.isSand(4, 4), true, 'Sand should be at (4, 4)');
        assert.strictEqual(sim.grid.isEmpty(5, 5), true, 'Cell (5, 5) should be empty');
    });

    test('right priority causes sand to fall right first', () => {
        const sim = new SandSimulation(10, 10);
        sim.placeSand(5, 5);
        sim.placeSand(5, 4);
        sim.step(true); // right priority
        assert.strictEqual(sim.grid.isSand(6, 4), true, 'Sand should be at (6, 4)');
        assert.strictEqual(sim.grid.isEmpty(5, 5), true, 'Cell (5, 5) should be empty');
    });

    test('priority alternates each frame automatically', () => {
        const sim = new SandSimulation(10, 10);
        const priority1 = sim.isRightPriority();
        sim.step();
        const priority2 = sim.isRightPriority();
        assert.notStrictEqual(priority1, priority2, 'Priority should alternate');
    });
});

// =============================================================================
// Conservation of Matter
// =============================================================================

describe('Conservation of Matter', () => {
    test('sand count remains constant after simulation steps', () => {
        const sim = new SandSimulation(20, 20);
        // Place 100 sand particles randomly
        for (let i = 0; i < 100; i++) {
            const x = Math.floor(Math.random() * 20);
            const y = Math.floor(Math.random() * 20);
            sim.placeSand(x, y);
        }
        const initialCount = sim.grid.countSand();

        // Run simulation
        for (let i = 0; i < 50; i++) {
            sim.step();
        }

        const finalCount = sim.grid.countSand();
        assert.strictEqual(finalCount, initialCount, `Sand count should be ${initialCount}, got ${finalCount}`);
    });

    test('no sand appears spontaneously', () => {
        const sim = new SandSimulation(20, 20);
        // Run simulation on empty grid
        for (let i = 0; i < 10; i++) {
            sim.step();
        }
        assert.strictEqual(sim.grid.countSand(), 0, 'Grid should remain empty');
    });
});

// =============================================================================
// Edge Cases
// =============================================================================

describe('Edge Cases', () => {
    test('sand at left edge falls right diagonal only', () => {
        const sim = new SandSimulation(10, 10);
        sim.placeSand(0, 5);
        sim.placeSand(0, 4);
        sim.step();
        assert.strictEqual(sim.grid.isSand(1, 4), true, 'Sand should be at (1, 4)');
        assert.strictEqual(sim.grid.isEmpty(0, 5), true, 'Cell (0, 5) should be empty');
    });

    test('sand at right edge falls left diagonal only', () => {
        const sim = new SandSimulation(10, 10);
        sim.placeSand(9, 5);
        sim.placeSand(9, 4);
        sim.step();
        assert.strictEqual(sim.grid.isSand(8, 4), true, 'Sand should be at (8, 4)');
        assert.strictEqual(sim.grid.isEmpty(9, 5), true, 'Cell (9, 5) should be empty');
    });

    test('sand at left edge with blocked diagonal stays put', () => {
        const sim = new SandSimulation(10, 10);
        sim.placeSand(0, 5);
        sim.placeSand(0, 4);
        sim.placeSand(1, 4);
        sim.step();
        assert.strictEqual(sim.grid.isSand(0, 5), true, 'Sand should remain at (0, 5)');
    });

    test('sand at right edge with blocked diagonal stays put', () => {
        const sim = new SandSimulation(10, 10);
        sim.placeSand(9, 5);
        sim.placeSand(9, 4);
        sim.placeSand(8, 4);
        sim.step();
        assert.strictEqual(sim.grid.isSand(9, 5), true, 'Sand should remain at (9, 5)');
    });
});

// =============================================================================
// Pile Formation
// =============================================================================

describe('Pile Formation', () => {
    test('sand forms stable pile', () => {
        const sim = new SandSimulation(20, 20);
        // Stack sand vertically at column 10
        for (let y = 0; y < 5; y++) {
            sim.placeSand(10, y);
        }

        // Run until stable
        sim.runUntilStable();

        // Check all sand is supported
        assert.strictEqual(sim.isStable(), true, 'All sand should be stable');
    });

    test('tall stack spreads into pile', () => {
        const sim = new SandSimulation(20, 20);
        // Stack sand vertically at column 10, high up
        for (let y = 10; y < 15; y++) {
            sim.placeSand(10, y);
        }
        const initialCount = sim.grid.countSand();

        // Run until stable
        sim.runUntilStable();

        // Sand should spread but count stays same
        assert.strictEqual(sim.grid.countSand(), initialCount, 'Sand count should be preserved');
        assert.strictEqual(sim.isStable(), true, 'All sand should be stable after settling');
    });
});

// =============================================================================
// Test Runner
// =============================================================================

console.log('\n========================================');
console.log('Falling Sand Core - Test Results');
console.log('========================================');

if (failCount === 0) {
    console.log(`\n✓ All ${passCount} tests passed!\n`);
    process.exit(0);
} else {
    console.log(`\n✗ ${failCount} of ${passCount + failCount} tests failed.\n`);
    console.log('Failures:');
    failures.forEach(f => {
        console.log(`  - ${f.name}: ${f.error}`);
    });
    console.log('');
    process.exit(1);
}
