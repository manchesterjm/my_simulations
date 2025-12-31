"""Performance Benchmarking Framework for SOC Simulations.

This module provides comprehensive CPU vs GPU performance comparison for all
self-organized criticality simulations. It measures execution time across
different grid sizes and calculates speedup factors.

Benchmarked Simulations:
    - Ising Model: 2D magnetic spins at critical temperature
    - Sandpile: Abelian sandpile avalanche simulation
    - Forest Fire: Drossel-Schwabl forest fire model

Features:
    - Multiple warmup runs to ensure stable GPU state
    - Statistical measurements (mean, std, min, max)
    - Automatic GPU detection with CPU-only fallback
    - Formatted output with speedup calculations
    - Quick and full benchmark modes

Usage:
    Run full benchmarks:
        $ python benchmark.py

    Run quick benchmarks (smaller sizes):
        $ python benchmark.py --quick

Example Output:
    Ising 256x256:
      CPU: 1.23 s ± 45.6 ms
      GPU: 31.2 ms ± 2.1 ms
      Speedup: 39.4x
"""

import time
import numpy as np
from gpu_utils import cuda_available, get_device_info, sync_gpu

# Import simulations with factory functions
from sandpile import SandpileSimulation
from ising_model import IsingModel
from forest_fire import ForestFireSimulation


def time_function(func, *args, n_runs=3, warmup=1, **kwargs):
    """Time a function with warmup runs and return statistics.

    Executes the function multiple times with warmup runs to ensure stable
    performance measurements. Automatically synchronizes GPU operations for
    accurate timing.

    Args:
        func (callable): Function to time.
        *args: Positional arguments to pass to func.
        n_runs (int): Number of timed runs (default: 3).
        warmup (int): Number of warmup runs before timing (default: 1).
        **kwargs: Keyword arguments to pass to func.

    Returns:
        dict: Timing statistics with keys:
            - mean (float): Mean execution time in seconds
            - std (float): Standard deviation in seconds
            - min (float): Minimum execution time in seconds
            - max (float): Maximum execution time in seconds
            - runs (int): Number of timed runs performed

    Example:
        >>> def my_func(n):
        ...     return np.random.random((n, n))
        >>> stats = time_function(my_func, 1000, n_runs=5)
        >>> print(f"Mean: {stats['mean']:.4f}s")
    """
    # Warmup runs to stabilize GPU state and caches
    for _ in range(warmup):
        func(*args, **kwargs)
        if cuda_available():
            sync_gpu()

    # Timed runs
    times = []
    for _ in range(n_runs):
        start = time.perf_counter()
        func(*args, **kwargs)
        # Ensure GPU operations complete before measuring elapsed time
        if cuda_available():
            sync_gpu()
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return {
        'mean': np.mean(times),
        'std': np.std(times),
        'min': np.min(times),
        'max': np.max(times),
        'runs': n_runs
    }


def format_time(seconds):
    """Format time duration in human-readable units.

    Automatically selects appropriate units (microseconds, milliseconds, or
    seconds) based on magnitude for optimal readability.

    Args:
        seconds (float): Time duration in seconds.

    Returns:
        str: Formatted time string with appropriate units.

    Example:
        >>> format_time(0.0000051)
        '5.1 µs'
        >>> format_time(0.123)
        '123.00 ms'
        >>> format_time(2.5)
        '2.50 s'
    """
    if seconds < 0.001:
        # Microseconds for very small durations
        return f"{seconds * 1e6:.1f} µs"
    elif seconds < 1:
        # Milliseconds for sub-second durations
        return f"{seconds * 1000:.2f} ms"
    else:
        # Seconds for longer durations
        return f"{seconds:.2f} s"


def print_benchmark_result(name, cpu_result, gpu_result=None):
    """Print formatted benchmark results with optional GPU speedup.

    Displays CPU timing, optional GPU timing, and calculated speedup factor.
    Uses formatted time units for readability.

    Args:
        name (str): Name of the benchmark (e.g., "Ising 256x256").
        cpu_result (dict): CPU timing statistics from time_function().
        gpu_result (dict, optional): GPU timing statistics from time_function().
            If None, only CPU results are shown.

    Example:
        >>> cpu = {'mean': 1.5, 'std': 0.1}
        >>> gpu = {'mean': 0.05, 'std': 0.002}
        >>> print_benchmark_result("Test", cpu, gpu)
        Test:
          CPU: 1.50 s ± 100.00 ms
          GPU: 50.00 ms ± 2.00 ms
          Speedup: 30.0x
    """
    print(f"\n{name}:")
    print(
        f"  CPU: {format_time(cpu_result['mean'])} "
        f"± {format_time(cpu_result['std'])}"
    )

    if gpu_result:
        # Calculate and display speedup
        speedup = cpu_result['mean'] / gpu_result['mean']
        print(
            f"  GPU: {format_time(gpu_result['mean'])} "
            f"± {format_time(gpu_result['std'])}"
        )
        print(f"  Speedup: {speedup:.1f}x")
    else:
        print("  GPU: Not available")


def benchmark_ising(sizes=[64, 128, 256, 512], sweeps=100):
    """Benchmark Ising model across various grid sizes.

    Tests the 2D Ising model at critical temperature using checkerboard
    Metropolis algorithm. GPU version shows significant speedup due to
    parallel spin updates.

    Args:
        sizes (list): List of grid sizes to test (default: [64, 128, 256, 512]).
        sweeps (int): Number of Monte Carlo sweeps per test (default: 100).

    Example:
        >>> benchmark_ising(sizes=[128, 256], sweeps=50)
        ISING MODEL BENCHMARK
        ...
        Ising 128x128:
          CPU: 245.67 ms ± 12.34 ms
          GPU: 6.12 ms ± 0.45 ms
          Speedup: 40.1x
    """
    print("\n" + "=" * 60)
    print("ISING MODEL BENCHMARK")
    print("=" * 60)

    has_gpu = cuda_available()

    for size in sizes:
        print(f"\nGrid size: {size}x{size}, Sweeps: {sweeps}")

        # CPU benchmark using sequential Metropolis algorithm
        def run_cpu():
            model = IsingModel(size=size, temperature=2.269, seed=42)
            model.sweep(sweeps)

        cpu_result = time_function(run_cpu, n_runs=3)

        # GPU benchmark using checkerboard parallel algorithm
        gpu_result = None
        if has_gpu:
            from ising_gpu import IsingModelGPU

            def run_gpu():
                model = IsingModelGPU(size=size, temperature=2.269, seed=42)
                model.sweep(sweeps)

            gpu_result = time_function(run_gpu, n_runs=3)

        print_benchmark_result(f"Ising {size}x{size}", cpu_result, gpu_result)


def benchmark_sandpile(sizes=[100, 200, 500], drops=50000):
    """Benchmark sandpile simulation across various grid sizes.

    Tests the Abelian sandpile model using batch processing. GPU version
    processes avalanches in parallel, achieving significant speedup for
    avalanche propagation.

    Args:
        sizes (list): List of grid sizes to test (default: [100, 200, 500]).
        drops (int): Number of sand grain drops per test (default: 50000).

    Note:
        GPU version uses batch mode (batch_size=1000) to maximize parallel
        grain drops and reduce Python loop overhead.

    Example:
        >>> benchmark_sandpile(sizes=[100, 200], drops=20000)
        SANDPILE BENCHMARK
        ...
        Sandpile 200x200:
          CPU: 3.45 s ± 0.12 s
          GPU: 89.23 ms ± 5.67 ms
          Speedup: 38.7x
    """
    print("\n" + "=" * 60)
    print("SANDPILE BENCHMARK")
    print("=" * 60)

    has_gpu = cuda_available()

    for size in sizes:
        print(f"\nGrid size: {size}x{size}, Drops: {drops}")

        # CPU benchmark using sequential avalanche processing
        def run_cpu():
            sim = SandpileSimulation(size=size, seed=42)
            sim.run(drops)

        cpu_result = time_function(run_cpu, n_runs=3)

        # GPU benchmark using batched parallel avalanche processing
        gpu_result = None
        if has_gpu:
            from sandpile_gpu import SandpileSimulationGPU

            def run_gpu():
                sim = SandpileSimulationGPU(size=size, seed=42)
                sim.run_batch(drops, batch_size=1000)

            gpu_result = time_function(run_gpu, n_runs=3)

        print_benchmark_result(f"Sandpile {size}x{size}", cpu_result, gpu_result)


def benchmark_forest_fire(sizes=[200, 400, 800], steps=2000):
    """Benchmark forest fire simulation across various grid sizes.

    Tests the Drossel-Schwabl forest fire model. GPU version shows LIMITED
    speedup (~1.3x) because fire spread uses sequential BFS which requires
    GPU-CPU data transfers.

    Args:
        sizes (list): List of grid sizes to test (default: [200, 400, 800]).
        steps (int): Number of simulation steps per test (default: 2000).

    Note:
        Limited GPU acceleration due to:
        - BFS fire spread is inherently sequential (graph traversal)
        - Requires frequent GPU-CPU data transfers for BFS
        - Only tree growth and cell clearing run on GPU

    Example:
        >>> benchmark_forest_fire(sizes=[200, 400], steps=1000)
        FOREST FIRE BENCHMARK
        (Note: Limited GPU speedup due to sequential BFS fire spread)
        ...
        Forest Fire 400x400:
          CPU: 12.34 s ± 0.45 s
          GPU: 9.52 s ± 0.32 s
          Speedup: 1.3x
    """
    print("\n" + "=" * 60)
    print("FOREST FIRE BENCHMARK")
    print("=" * 60)
    print("(Note: Limited GPU speedup due to sequential BFS fire spread)")

    has_gpu = cuda_available()

    for size in sizes:
        print(f"\nGrid size: {size}x{size}, Steps: {steps}")

        # CPU benchmark using pure CPU implementation
        def run_cpu():
            sim = ForestFireSimulation(size=size, seed=42)
            sim.run(steps, progress_interval=None)

        cpu_result = time_function(run_cpu, n_runs=3)

        # GPU benchmark using hybrid GPU/CPU approach
        gpu_result = None
        if has_gpu:
            from forest_fire_gpu import ForestFireGPU

            def run_gpu():
                sim = ForestFireGPU(size=size, seed=42)
                sim.run(steps, progress_interval=None)

            gpu_result = time_function(run_gpu, n_runs=3)

        print_benchmark_result(f"Forest Fire {size}x{size}", cpu_result, gpu_result)


def run_all_benchmarks():
    """Run comprehensive benchmarks for all simulations.

    Executes full benchmark suite with default parameters:
    - Ising: [64, 128, 256, 512] grid sizes, 100 sweeps
    - Sandpile: [100, 200, 500] grid sizes, 50000 drops
    - Forest Fire: [200, 400, 800] grid sizes, 2000 steps

    Displays GPU information and results for all simulations with speedup
    calculations where applicable.

    Example:
        >>> run_all_benchmarks()
        SIMULATION BENCHMARK SUITE - CPU vs GPU
        ...
        GPU: Available (Compute 8.6)
             Memory: 20.1 GB free / 24.0 GB total
        ...
        BENCHMARK COMPLETE
    """
    print("\n" + "=" * 60)
    print("SIMULATION BENCHMARK SUITE - CPU vs GPU")
    print("=" * 60)

    # Print device info
    info = get_device_info()
    if info['available']:
        print(f"\nGPU: Available (Compute {info['compute_capability']})")
        print(
            f"     Memory: {info['free_memory_gb']:.1f} GB free / "
            f"{info['total_memory_gb']:.1f} GB total"
        )
    else:
        print("\nGPU: Not available (CPU-only benchmarks)")

    # Run all benchmark suites
    benchmark_ising()
    benchmark_sandpile()
    benchmark_forest_fire()

    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)


def run_quick_benchmark():
    """Run quick benchmarks with reduced problem sizes.

    Executes abbreviated benchmark suite for faster testing:
    - Ising: [128, 256] grid sizes, 50 sweeps
    - Sandpile: [100, 200] grid sizes, 20000 drops
    - Forest Fire: [200, 400] grid sizes, 1000 steps

    Useful for rapid performance validation or when time is limited.

    Example:
        >>> run_quick_benchmark()
        QUICK BENCHMARK - CPU vs GPU
        ...
        GPU: Available (Compute 8.6)
        ...
        QUICK BENCHMARK COMPLETE
    """
    print("\n" + "=" * 60)
    print("QUICK BENCHMARK - CPU vs GPU")
    print("=" * 60)

    info = get_device_info()
    if info['available']:
        print(f"\nGPU: Available (Compute {info['compute_capability']})")
    else:
        print("\nGPU: Not available")

    # Run abbreviated benchmark suite
    benchmark_ising(sizes=[128, 256], sweeps=50)
    benchmark_sandpile(sizes=[100, 200], drops=20000)
    benchmark_forest_fire(sizes=[200, 400], steps=1000)

    print("\n" + "=" * 60)
    print("QUICK BENCHMARK COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        run_quick_benchmark()
    else:
        run_all_benchmarks()
