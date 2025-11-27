"""
GPU Utilities Module
Provides device detection, memory management, and timing utilities for CUDA acceleration.
"""

import time
from contextlib import contextmanager
from functools import wraps

# Try to import CuPy, fall back gracefully
try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    cp = None
    CUPY_AVAILABLE = False

# NumPy is always available
import numpy as np


def cuda_available():
    """Check if CUDA is available via CuPy."""
    if not CUPY_AVAILABLE:
        return False
    try:
        cp.cuda.Device()
        return True
    except cp.cuda.runtime.CUDARuntimeError:
        return False


def get_device_info():
    """Get information about the current CUDA device."""
    if not cuda_available():
        return {"available": False}

    device = cp.cuda.Device()
    mem_info = device.mem_info

    return {
        "available": True,
        "pci_bus_id": device.pci_bus_id,
        "compute_capability": device.compute_capability,
        "total_memory_gb": mem_info[1] / (1024**3),
        "free_memory_gb": mem_info[0] / (1024**3),
    }


def print_device_info():
    """Print device information in a formatted way."""
    info = get_device_info()

    if not info["available"]:
        print("CUDA: Not available")
        return

    print(f"CUDA: Available")
    print(f"  PCI Bus ID: {info['pci_bus_id']}")
    print(f"  Compute Capability: {info['compute_capability']}")
    print(f"  Total Memory: {info['total_memory_gb']:.2f} GB")
    print(f"  Free Memory: {info['free_memory_gb']:.2f} GB")


def get_array_module(backend='auto'):
    """
    Get the appropriate array module based on backend selection.

    Args:
        backend: 'auto', 'gpu', or 'cpu'

    Returns:
        Module (cupy or numpy) and the actual backend used
    """
    if backend == 'auto':
        backend = 'gpu' if cuda_available() else 'cpu'

    if backend == 'gpu':
        if not cuda_available():
            raise RuntimeError("GPU backend requested but CUDA is not available")
        return cp, 'gpu'

    return np, 'cpu'


def to_numpy(arr):
    """Convert array to NumPy (works for both CuPy and NumPy arrays)."""
    if CUPY_AVAILABLE and isinstance(arr, cp.ndarray):
        return cp.asnumpy(arr)
    return np.asarray(arr)


def to_gpu(arr):
    """Convert array to CuPy GPU array."""
    if not cuda_available():
        raise RuntimeError("CUDA is not available")
    if isinstance(arr, cp.ndarray):
        return arr
    return cp.asarray(arr)


@contextmanager
def cuda_timer():
    """
    Context manager for timing CUDA operations accurately.
    Uses CUDA events for GPU timing.
    """
    if cuda_available():
        start_event = cp.cuda.Event()
        end_event = cp.cuda.Event()

        start_event.record()
        yield
        end_event.record()
        end_event.synchronize()

        # Time in milliseconds
        elapsed = cp.cuda.get_elapsed_time(start_event, end_event)
        cuda_timer.last_elapsed = elapsed / 1000  # Convert to seconds
    else:
        start = time.perf_counter()
        yield
        cuda_timer.last_elapsed = time.perf_counter() - start


cuda_timer.last_elapsed = 0


def timed(func):
    """Decorator to time function execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)

        # Synchronize if using GPU
        if cuda_available():
            cp.cuda.Stream.null.synchronize()

        elapsed = time.perf_counter() - start
        wrapper.last_elapsed = elapsed
        return result

    wrapper.last_elapsed = 0
    return wrapper


def sync_gpu():
    """Synchronize GPU operations (wait for all kernels to complete)."""
    if cuda_available():
        cp.cuda.Stream.null.synchronize()


def clear_gpu_memory():
    """Clear GPU memory cache."""
    if cuda_available():
        cp.get_default_memory_pool().free_all_blocks()
        cp.get_default_pinned_memory_pool().free_all_blocks()


class GPUArray:
    """
    Wrapper class that provides a unified interface for CPU/GPU arrays.
    Automatically handles device placement and data transfer.
    """

    def __init__(self, data, backend='auto'):
        self.xp, self.backend = get_array_module(backend)
        if isinstance(data, (list, tuple)):
            self._data = self.xp.array(data)
        elif self.backend == 'gpu' and isinstance(data, np.ndarray):
            self._data = cp.asarray(data)
        elif self.backend == 'cpu' and CUPY_AVAILABLE and isinstance(data, cp.ndarray):
            self._data = cp.asnumpy(data)
        else:
            self._data = data

    @property
    def data(self):
        return self._data

    def to_numpy(self):
        return to_numpy(self._data)

    def to_gpu(self):
        if self.backend == 'gpu':
            return self._data
        return to_gpu(self._data)


if __name__ == '__main__':
    print("GPU Utilities Module")
    print("=" * 50)
    print_device_info()

    if cuda_available():
        print("\nQuick GPU test:")
        x = cp.random.random((1000, 1000))
        with cuda_timer():
            y = cp.dot(x, x)
            sync_gpu()
        print(f"  1000x1000 matrix multiply: {cuda_timer.last_elapsed*1000:.2f} ms")
