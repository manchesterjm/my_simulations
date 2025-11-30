"""GPU Utilities Module for CUDA Acceleration.

This module provides a unified interface for GPU/CPU array operations using CuPy
and NumPy. It handles device detection, automatic backend selection, memory
management, and accurate timing for CUDA operations.

Key Features:
    - Automatic GPU detection with graceful CPU fallback
    - Unified array interface (GPUArray) for seamless CPU/GPU code
    - Context managers and decorators for accurate GPU timing
    - Memory management utilities for clearing GPU cache
    - Device information querying and reporting

Backend Selection:
    Use 'auto' (default) for automatic GPU detection, or force with 'gpu'/'cpu'.
    All functions handle the case where CUDA is unavailable gracefully.

Example:
    >>> if cuda_available():
    ...     xp, backend = get_array_module('auto')  # Returns cupy if available
    ...     arr = xp.random.random((1000, 1000))
    ...     with cuda_timer():
    ...         result = xp.dot(arr, arr)
    ...     print(f"Time: {cuda_timer.last_elapsed:.4f}s")

Dependencies:
    - NumPy: Always required
    - CuPy: Optional, for GPU acceleration
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
    """Check if CUDA GPU is available and functional.

    This function first checks if CuPy is installed, then attempts to access
    a CUDA device. Returns False if either check fails.

    Returns:
        bool: True if CUDA is available and functional, False otherwise.

    Example:
        >>> if cuda_available():
        ...     print("GPU acceleration available")
        ... else:
        ...     print("Falling back to CPU")
    """
    if not CUPY_AVAILABLE:
        return False
    try:
        # Attempt to access CUDA device
        cp.cuda.Device()
        return True
    except cp.cuda.runtime.CUDARuntimeError:
        return False


def get_device_info():
    """Get detailed information about the current CUDA device.

    Queries the GPU for device properties including memory and compute capability.
    Returns a minimal dictionary if CUDA is unavailable.

    Returns:
        dict: Device information with keys:
            - available (bool): Whether CUDA is available
            - pci_bus_id (str): PCI bus identifier (if available)
            - compute_capability (str): CUDA compute capability version (if available)
            - total_memory_gb (float): Total GPU memory in GB (if available)
            - free_memory_gb (float): Free GPU memory in GB (if available)

    Example:
        >>> info = get_device_info()
        >>> if info['available']:
        ...     print(f"GPU has {info['total_memory_gb']:.1f} GB total memory")
    """
    if not cuda_available():
        return {"available": False}

    device = cp.cuda.Device()
    # mem_info returns (free, total) in bytes
    mem_info = device.mem_info

    return {
        "available": True,
        "pci_bus_id": device.pci_bus_id,
        "compute_capability": device.compute_capability,
        "total_memory_gb": mem_info[1] / (1024**3),  # Convert bytes to GB
        "free_memory_gb": mem_info[0] / (1024**3),
    }


def print_device_info():
    """Print CUDA device information in a human-readable format.

    Displays GPU availability, compute capability, and memory information.
    If CUDA is unavailable, prints a simple message and returns.

    Example:
        >>> print_device_info()
        CUDA: Available
          PCI Bus ID: 0000:01:00.0
          Compute Capability: 8.6
          Total Memory: 24.00 GB
          Free Memory: 20.15 GB
    """
    info = get_device_info()

    if not info["available"]:
        print("CUDA: Not available")
        return

    print("CUDA: Available")
    print(f"  PCI Bus ID: {info['pci_bus_id']}")
    print(f"  Compute Capability: {info['compute_capability']}")
    print(f"  Total Memory: {info['total_memory_gb']:.2f} GB")
    print(f"  Free Memory: {info['free_memory_gb']:.2f} GB")


def get_array_module(backend='auto'):
    """Get the appropriate array module (CuPy or NumPy) based on backend selection.

    This function provides a unified way to select between GPU and CPU array
    operations. Use 'auto' for automatic selection based on GPU availability.

    Args:
        backend (str): Backend selection - 'auto', 'gpu', or 'cpu'.
            - 'auto': Automatically select GPU if available, otherwise CPU
            - 'gpu': Force GPU usage (raises error if unavailable)
            - 'cpu': Force CPU usage

    Returns:
        tuple: (module, backend_name) where:
            - module: Either cupy (cp) or numpy (np)
            - backend_name: Either 'gpu' or 'cpu'

    Raises:
        RuntimeError: If 'gpu' backend is requested but CUDA is unavailable.

    Example:
        >>> xp, backend = get_array_module('auto')
        >>> arr = xp.random.random((100, 100))  # Uses GPU if available
        >>> print(f"Using {backend} backend")
    """
    # Auto-detect based on CUDA availability
    if backend == 'auto':
        backend = 'gpu' if cuda_available() else 'cpu'

    if backend == 'gpu':
        if not cuda_available():
            raise RuntimeError("GPU backend requested but CUDA is not available")
        return cp, 'gpu'

    return np, 'cpu'


def to_numpy(arr):
    """Convert array to NumPy format, handling both CPU and GPU arrays.

    This function provides a unified interface for transferring arrays to CPU
    memory. Works seamlessly with both CuPy (GPU) and NumPy (CPU) arrays.

    Args:
        arr: Input array (can be CuPy ndarray, NumPy ndarray, or array-like).

    Returns:
        numpy.ndarray: Array in NumPy format on CPU.

    Example:
        >>> gpu_arr = cp.array([1, 2, 3])  # GPU array
        >>> cpu_arr = to_numpy(gpu_arr)     # Transfer to CPU
        >>> isinstance(cpu_arr, np.ndarray)
        True
    """
    # Transfer from GPU to CPU if it's a CuPy array
    if CUPY_AVAILABLE and isinstance(arr, cp.ndarray):
        return cp.asnumpy(arr)
    # Otherwise, ensure it's a NumPy array
    return np.asarray(arr)


def to_gpu(arr):
    """Convert array to CuPy format on GPU.

    Transfers array to GPU memory. If the array is already on the GPU,
    returns it unchanged.

    Args:
        arr: Input array (can be NumPy ndarray, CuPy ndarray, or array-like).

    Returns:
        cupy.ndarray: Array in CuPy format on GPU.

    Raises:
        RuntimeError: If CUDA is not available.

    Example:
        >>> cpu_arr = np.array([1, 2, 3])
        >>> gpu_arr = to_gpu(cpu_arr)
        >>> isinstance(gpu_arr, cp.ndarray)
        True
    """
    if not cuda_available():
        raise RuntimeError("CUDA is not available")
    # Already on GPU, return as-is
    if isinstance(arr, cp.ndarray):
        return arr
    # Transfer CPU array to GPU
    return cp.asarray(arr)


@contextmanager
def cuda_timer():
    """Context manager for accurate timing of CUDA operations.

    Uses CUDA events for GPU timing (more accurate than CPU timing due to
    asynchronous kernel execution). Falls back to perf_counter for CPU operations.
    The elapsed time is stored in `cuda_timer.last_elapsed` attribute.

    Yields:
        None: Control to the with-block body.

    Example:
        >>> with cuda_timer():
        ...     arr = cp.random.random((1000, 1000))
        ...     result = cp.dot(arr, arr)
        >>> print(f"Time: {cuda_timer.last_elapsed:.4f}s")

    Note:
        CUDA events automatically synchronize, ensuring accurate measurement
        of asynchronous GPU operations. For CPU, uses high-resolution timer.
    """
    if cuda_available():
        # Use CUDA events for accurate GPU timing
        start_event = cp.cuda.Event()
        end_event = cp.cuda.Event()

        start_event.record()
        yield
        end_event.record()
        end_event.synchronize()  # Wait for GPU to finish

        # Get elapsed time in milliseconds, convert to seconds
        elapsed = cp.cuda.get_elapsed_time(start_event, end_event)
        cuda_timer.last_elapsed = elapsed / 1000
    else:
        # Fall back to CPU timing
        start = time.perf_counter()
        yield
        cuda_timer.last_elapsed = time.perf_counter() - start


cuda_timer.last_elapsed = 0


def timed(func):
    """Decorator for timing function execution with automatic GPU synchronization.

    Measures wall-clock time of function execution. Automatically synchronizes
    GPU operations before measuring elapsed time to ensure accuracy.
    Elapsed time is stored in the wrapper's `last_elapsed` attribute.

    Args:
        func (callable): Function to be timed.

    Returns:
        callable: Wrapped function that measures its own execution time.

    Example:
        >>> @timed
        ... def my_gpu_function():
        ...     return cp.random.random((1000, 1000))
        >>> result = my_gpu_function()
        >>> print(f"Took {my_gpu_function.last_elapsed:.4f}s")

    Note:
        GPU synchronization ensures that asynchronous kernels complete before
        measuring elapsed time, providing accurate timing results.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)

        # Synchronize GPU to ensure all operations complete
        if cuda_available():
            cp.cuda.Stream.null.synchronize()

        elapsed = time.perf_counter() - start
        wrapper.last_elapsed = elapsed
        return result

    wrapper.last_elapsed = 0
    return wrapper


def sync_gpu():
    """Synchronize GPU operations by waiting for all kernels to complete.

    This function blocks until all previously queued CUDA kernels have finished
    executing. Use this before timing measurements or when CPU code needs to
    wait for GPU results. Does nothing if CUDA is unavailable.

    Example:
        >>> arr = cp.random.random((1000, 1000))
        >>> result = cp.dot(arr, arr)  # Asynchronous GPU operation
        >>> sync_gpu()                  # Wait for completion
        >>> # Now safe to time or access result
    """
    if cuda_available():
        cp.cuda.Stream.null.synchronize()


def clear_gpu_memory():
    """Clear GPU memory cache by freeing all unused memory blocks.

    Releases all unused memory in both the default GPU memory pool and the
    pinned memory pool back to CUDA. Useful for freeing memory between
    simulations or when memory is fragmented. Does nothing if CUDA is unavailable.

    Example:
        >>> # After running a large simulation
        >>> del large_array
        >>> clear_gpu_memory()  # Free memory back to CUDA
    """
    if cuda_available():
        # Free regular GPU memory pool
        cp.get_default_memory_pool().free_all_blocks()
        # Free pinned (page-locked) host memory pool
        cp.get_default_pinned_memory_pool().free_all_blocks()


class GPUArray:
    """Unified interface for CPU/GPU arrays with automatic device placement.

    This wrapper class provides seamless handling of arrays on either CPU or GPU,
    automatically managing data transfer and device placement based on the
    selected backend.

    Attributes:
        xp: The array module (cupy or numpy) for this instance.
        backend (str): The actual backend being used ('gpu' or 'cpu').
        data: The underlying array data.

    Example:
        >>> arr = GPUArray([1, 2, 3, 4], backend='auto')
        >>> print(arr.backend)  # 'gpu' if CUDA available, else 'cpu'
        >>> cpu_data = arr.to_numpy()  # Transfer to CPU
    """

    def __init__(self, data, backend='auto'):
        """Initialize GPUArray with automatic device placement.

        Args:
            data: Input data (list, tuple, NumPy array, or CuPy array).
            backend (str): Backend selection - 'auto', 'gpu', or 'cpu'.
                'auto' automatically selects based on GPU availability.
        """
        self.xp, self.backend = get_array_module(backend)

        # Convert input data to appropriate array type
        if isinstance(data, (list, tuple)):
            # Create array using the selected backend module
            self._data = self.xp.array(data)
        elif self.backend == 'gpu' and isinstance(data, np.ndarray):
            # Transfer NumPy array to GPU
            self._data = cp.asarray(data)
        elif self.backend == 'cpu' and CUPY_AVAILABLE and isinstance(data, cp.ndarray):
            # Transfer CuPy array to CPU
            self._data = cp.asnumpy(data)
        else:
            # Already correct type
            self._data = data

    @property
    def data(self):
        """Get the underlying array data.

        Returns:
            Array in the format of the selected backend (CuPy or NumPy).
        """
        return self._data

    def to_numpy(self):
        """Transfer array to CPU as NumPy array.

        Returns:
            numpy.ndarray: Array data on CPU.
        """
        return to_numpy(self._data)

    def to_gpu(self):
        """Transfer array to GPU as CuPy array.

        Returns:
            cupy.ndarray: Array data on GPU.

        Raises:
            RuntimeError: If CUDA is not available.
        """
        if self.backend == 'gpu':
            # Already on GPU
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
