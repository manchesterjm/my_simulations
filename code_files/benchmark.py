"""
Benchmark Framework
Compare CPU vs GPU performance for all simulations.
"""

import time
import numpy as np
from gpu_utils import cuda_available, get_device_info, sync_gpu

# Import simulations with factory functions
from sandpile import SandpileSimulation, create_sandpile
from ising_model import IsingModel, create_ising_model
from forest_fire import ForestFireSimulation, create_forest_fire


def time_function(func, *args, n_runs=3, warmup=1, **kwargs):
    """
    Time a function with warmup runs.

    Returns:
        dict with mean, std, min, max times in seconds
    """
    # Warmup runs
    for _ in range(warmup):
        func(*args, **kwargs)
        if cuda_available():
            sync_gpu()

    # Timed runs
    times = []
    for _ in range(n_runs):
        start = time.perf_counter()
        func(*args, **kwargs)
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
    """Format time nicely."""
    if seconds < 0.001:
        return f"{seconds * 1e6:.1f} µs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.2f} s"


def print_benchmark_result(name, cpu_result, gpu_result=None):
    """Print benchmark results with optional speedup calculation."""
    print(f"\n{name}:")
    print(f"  CPU: {format_time(cpu_result['mean'])} ± {format_time(cpu_result['std'])}")

    if gpu_result:
        speedup = cpu_result['mean'] / gpu_result['mean']
        print(f"  GPU: {format_time(gpu_result['mean'])} ± {format_time(gpu_result['std'])}")
        print(f"  Speedup: {speedup:.1f}x")
    else:
        print("  GPU: Not available")


def benchmark_ising(sizes=[64, 128, 256, 512], sweeps=100):
    """Benchmark Ising model at various sizes."""
    print("\n" + "=" * 60)
    print("ISING MODEL BENCHMARK")
    print("=" * 60)

    has_gpu = cuda_available()

    for size in sizes:
        print(f"\nGrid size: {size}x{size}, Sweeps: {sweeps}")

        # CPU benchmark
        def run_cpu():
            model = IsingModel(size=size, temperature=2.269, seed=42)
            model.sweep(sweeps)

        cpu_result = time_function(run_cpu, n_runs=3)

        # GPU benchmark
        gpu_result = None
        if has_gpu:
            from ising_gpu import IsingModelGPU

            def run_gpu():
                model = IsingModelGPU(size=size, temperature=2.269, seed=42)
                model.sweep(sweeps)

            gpu_result = time_function(run_gpu, n_runs=3)

        print_benchmark_result(f"Ising {size}x{size}", cpu_result, gpu_result)


def benchmark_sandpile(sizes=[100, 200, 500], drops=50000):
    """Benchmark sandpile simulation at various sizes (batch mode for GPU)."""
    print("\n" + "=" * 60)
    print("SANDPILE BENCHMARK")
    print("=" * 60)

    has_gpu = cuda_available()

    for size in sizes:
        print(f"\nGrid size: {size}x{size}, Drops: {drops}")

        # CPU benchmark
        def run_cpu():
            sim = SandpileSimulation(size=size, seed=42)
            sim.run(drops)

        cpu_result = time_function(run_cpu, n_runs=3)

        # GPU benchmark (batch mode)
        gpu_result = None
        if has_gpu:
            from sandpile_gpu import SandpileSimulationGPU

            def run_gpu():
                sim = SandpileSimulationGPU(size=size, seed=42)
                sim.run_batch(drops, batch_size=1000)

            gpu_result = time_function(run_gpu, n_runs=3)

        print_benchmark_result(f"Sandpile {size}x{size}", cpu_result, gpu_result)


def benchmark_forest_fire(sizes=[200, 400, 800], steps=2000):
    """Benchmark forest fire simulation at various sizes."""
    print("\n" + "=" * 60)
    print("FOREST FIRE BENCHMARK")
    print("=" * 60)
    print("(Note: Limited GPU speedup due to sequential BFS fire spread)")

    has_gpu = cuda_available()

    for size in sizes:
        print(f"\nGrid size: {size}x{size}, Steps: {steps}")

        # CPU benchmark
        def run_cpu():
            sim = ForestFireSimulation(size=size, seed=42)
            sim.run(steps, progress_interval=None)

        cpu_result = time_function(run_cpu, n_runs=3)

        # GPU benchmark
        gpu_result = None
        if has_gpu:
            from forest_fire_gpu import ForestFireGPU

            def run_gpu():
                sim = ForestFireGPU(size=size, seed=42)
                sim.run(steps, progress_interval=None)

            gpu_result = time_function(run_gpu, n_runs=3)

        print_benchmark_result(f"Forest Fire {size}x{size}", cpu_result, gpu_result)


def run_all_benchmarks():
    """Run all benchmarks."""
    print("\n" + "=" * 60)
    print("SIMULATION BENCHMARK SUITE - CPU vs GPU")
    print("=" * 60)

    # Print device info
    info = get_device_info()
    if info['available']:
        print(f"\nGPU: Available (Compute {info['compute_capability']})")
        print(f"     Memory: {info['free_memory_gb']:.1f} GB free / {info['total_memory_gb']:.1f} GB total")
    else:
        print("\nGPU: Not available (CPU-only benchmarks)")

    # Run benchmarks
    benchmark_ising()
    benchmark_sandpile()
    benchmark_forest_fire()

    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)


def run_quick_benchmark():
    """Quick benchmark with smaller sizes."""
    print("\n" + "=" * 60)
    print("QUICK BENCHMARK - CPU vs GPU")
    print("=" * 60)

    info = get_device_info()
    if info['available']:
        print(f"\nGPU: Available (Compute {info['compute_capability']})")
    else:
        print("\nGPU: Not available")

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
