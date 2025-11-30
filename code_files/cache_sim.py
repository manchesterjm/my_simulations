"""
CPU Cache Simulation with Configurable Replacement Policies

This module simulates CPU cache memory behavior to analyze the performance impact
of different cache configurations. It models a 64KB cache processing memory access
patterns and calculates total access times based on cache hits and misses.

Cache Fundamentals:
-------------------
A CPU cache is a small, fast memory located between the CPU and main RAM. It stores
recently accessed memory addresses to reduce the time needed to access data.

Cache Structure:
    - **Cache Line/Block**: Fixed-size chunk of memory (8-256 bytes)
    - **Set**: Group of cache lines that can store data from the same memory region
    - **Tag**: Upper bits of address identifying which memory block is cached
    - **Index/Set Number**: Middle bits determining which set stores the data
    - **Offset**: Lower bits specifying byte position within a cache line

Associativity:
    - **Direct-mapped** (1-way): Each memory address maps to exactly one cache line
    - **N-way set associative**: Each address can map to N different lines within a set
    - **Fully associative**: Any address can be stored in any cache line (most flexible)

Replacement Policies:
    - **FIFO** (First-In-First-Out): Replace the oldest cache line in the set
    - **LRU** (Least Recently Used): Replace the line that hasn't been accessed longest

Simulation Parameters:
---------------------
- Cache size: 64KB (65,536 bytes)
- Line sizes tested: 8, 16, 32, 64, 128, 256 bytes (powers of 2)
- Associativity: From direct-mapped to fully associative
- Replacement policies: LRU and FIFO

Access Time Model (in nanoseconds):
----------------------------------
- Hit time: 2ns (base access) + 2ns (search) + 0.5ns * log₂(associativity)
- Miss time: Hit time + 24ns (RAM access) + replacement overhead
    - FIFO replacement overhead: 1ns
    - LRU replacement overhead: 3ns (more complex bookkeeping)

Example:
    For a 64-way set associative cache with LRU:
    - Hit time: 2 + 2 + 0.5*log₂(64) = 2 + 2 + 3 = 7ns
    - Miss time: 7 + 24 + 3 = 34ns

Usage:
------
    $ python cache_sim.py

    The script will prompt for:
    1. Access pattern type: 'non' for non-random, blank for random
    2. Replacement policy: '1' for LRU, '0' for FIFO

    It expects memory address files in the current directory:
    - random_access.txt or nonrandom_access.txt

Note:
-----
    This simulation processes real memory access traces to evaluate cache performance
    under different configurations, helping understand the trade-offs between cache
    line size, associativity, and replacement policy.
"""


import math
import os
from datetime import datetime


def fifo_replace(cache_set, new_tag):
    """Replace the oldest cache line using FIFO (First-In-First-Out) policy.

    FIFO maintains insertion order and always evicts the first element that was
    added to the set. This is simple to implement but may evict frequently used
    lines.

    Args:
        cache_set (list): List of cache line tags in the set, ordered by insertion time.
            First element is oldest, last element is newest.
        new_tag (int): Tag value of the new cache line to insert.

    Returns:
        list: Updated cache set with oldest line removed and new line appended.
    """
    cache_set.pop(0)  # Remove the oldest (first) element
    cache_set.append(new_tag)  # Add new element at the end
    return cache_set


def lru_reorder(cache_set, accessed_tag):
    """Update cache set order using LRU (Least Recently Used) policy.

    LRU tracks access recency by moving accessed lines to the end of the list.
    The first element is always the least recently used and will be evicted on
    the next miss. This policy exploits temporal locality but requires more
    bookkeeping than FIFO.

    Args:
        cache_set (list): List of cache line tags in the set, ordered by access time.
            First element is least recently used, last is most recently used.
        accessed_tag (int): Tag value that was just accessed (hit or miss).

    Returns:
        list: Updated cache set with accessed tag moved to the end (most recent).
    """
    cache_set.remove(accessed_tag)  # Remove tag from its current position
    cache_set.append(accessed_tag)  # Add it to the end (most recently used)
    return cache_set


def load_memory_addresses(filename):
    """Load memory addresses from a file.

    Args:
        filename (str): Path to file containing memory addresses. Each line should
            contain space-separated integer addresses.

    Returns:
        list: 2D list where each row contains memory addresses from one line of the file.
            All values are converted to integers.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    mem_list = []

    with open(filename, 'r') as f:
        for line in f.readlines():
            mem_list.append(line.split(' '))

    # Convert all addresses from string to integer
    for row in range(len(mem_list)):
        for col in range(len(mem_list[0])):
            mem_list[row][col] = int(mem_list[row][col])

    return mem_list


def get_user_configuration():
    """Prompt user for simulation configuration.

    Returns:
        tuple: (access_pattern, use_lru, filename) where:
            - access_pattern (str): 'random' or 'nonrandom'
            - use_lru (bool): True for LRU policy, False for FIFO
            - filename (str): Path to the memory access trace file
    """
    # Get access pattern type
    pattern_input = input("enter 'non' for non_random or leave blank for random (default random) : ")
    if pattern_input == 'non':
        access_pattern = 'nonrandom'
        prefix = 'non'
    else:
        access_pattern = 'random'
        prefix = ''

    # Construct filename - check current directory first
    filename = prefix + 'random_access.txt'
    if not os.path.exists(filename):
        # Fallback to original Windows path style (won't work on Linux but maintains compatibility)
        filename = r'C:\Users\manch\Desktop\Assembly Code\Proj 1\\' + prefix + 'random_access.txt'

    # Get replacement policy
    lru_input = input("Enter 1 for 'LRU', 0 for 'FIFO' (default 'FIFO') : ")
    use_lru = (lru_input == '1')

    return access_pattern, use_lru, filename


def initialize_cache(num_sets, blocks_per_set):
    """Create an empty cache structure.

    Args:
        num_sets (int): Number of sets in the cache.
        blocks_per_set (int): Number of cache lines (ways) per set.

    Returns:
        list: 2D list representing the cache. Each row is a set, each column is
            a way. All entries initialized to -1 (empty).
    """
    return [[-1 for _ in range(blocks_per_set)] for _ in range(num_sets)]


def extract_cache_fields(address, offset_bits, set_bits):
    """Extract set number and tag from a memory address.

    A memory address is divided into three parts (from low to high bits):
        [Offset | Set Index | Tag]

    - Offset: Identifies byte within a cache line (not used for lookup)
    - Set Index: Determines which set can store this address
    - Tag: Identifies which specific memory block is cached

    Args:
        address (int): Physical memory address.
        offset_bits (int): Number of bits for the offset field (log₂ of line size).
        set_bits (int): Number of bits for the set index field (log₂ of num_sets).

    Returns:
        tuple: (set_number, tag) where:
            - set_number (int): Which set this address maps to
            - tag (int): Tag value identifying the memory block
    """
    # Create mask to extract set bits: (2^set_bits - 1) shifted left by offset_bits
    set_mask = ((1 << set_bits) - 1) << offset_bits

    # Extract set number by masking and shifting right
    set_number = (address & set_mask) >> offset_bits

    # Extract tag by shifting away set and offset bits
    tag = address >> (set_bits + offset_bits)

    return set_number, tag


def is_cache_hit(cache_set, tag):
    """Check if a tag is present in the cache set.

    Args:
        cache_set (list): List of tags currently in the set.
        tag (int): Tag to search for.

    Returns:
        bool: True if tag is found (cache hit), False otherwise (cache miss).
    """
    return tag in cache_set


def is_cache_empty(cache_set):
    """Check if a cache set has empty slots.

    Args:
        cache_set (list): List of tags in the set (-1 indicates empty slot).

    Returns:
        bool: True if the set has at least one empty slot, False if full.
    """
    return cache_set[0] == -1


def handle_cache_hit(cache_set, tag, use_lru, blocks_per_set):
    """Update cache state after a cache hit.

    Args:
        cache_set (list): Current cache set contents.
        tag (int): Tag that was hit.
        use_lru (bool): Whether to use LRU reordering.
        blocks_per_set (int): Number of ways in the set.

    Returns:
        list: Updated cache set (reordered if using LRU).
    """
    # LRU: Move accessed tag to end (most recently used position)
    # FIFO: No reordering needed on hits
    # Only reorder for multi-way caches (direct-mapped doesn't need it)
    if use_lru and blocks_per_set > 1:
        return lru_reorder(cache_set, tag)
    return cache_set


def handle_cache_miss_empty(cache_set, tag):
    """Handle cache miss when the set has empty slots.

    Args:
        cache_set (list): Current cache set contents with empty slots.
        tag (int): Tag to insert.

    Returns:
        list: Updated cache set with tag appended.
    """
    cache_set.pop(0)  # Remove one empty slot (-1)
    cache_set.append(tag)  # Add new tag at the end
    return cache_set


def handle_cache_miss_full(cache_set, tag, use_lru):
    """Handle cache miss when the set is full (replacement needed).

    Args:
        cache_set (list): Current cache set contents (full).
        tag (int): Tag to insert.
        use_lru (bool): If True, use LRU; if False, use FIFO.

    Returns:
        list: Updated cache set with one line replaced.
    """
    if use_lru:
        # LRU: Tag wasn't in cache, so insert it and treat as recently used
        return lru_reorder(cache_set, tag)
    else:
        # FIFO: Replace oldest line
        return fifo_replace(cache_set, tag)


def simulate_cache_access(cache, mem_list, offset_bits, set_bits, use_lru):
    """Simulate cache accesses for all memory addresses.

    Args:
        cache (list): 2D cache structure (sets x ways).
        mem_list (list): List of memory addresses to access.
        offset_bits (int): Number of offset bits in address.
        set_bits (int): Number of set index bits in address.
        use_lru (bool): True for LRU policy, False for FIFO.

    Returns:
        tuple: (hits, misses) - count of cache hits and misses.
    """
    hits = 0
    misses = 0
    blocks_per_set = len(cache[0])

    for addr_list in mem_list:
        mem_addr = addr_list[0]

        # Extract cache fields from address
        set_num, tag = extract_cache_fields(mem_addr, offset_bits, set_bits)

        # Check for hit or miss
        if is_cache_hit(cache[set_num], tag):
            hits += 1
            cache[set_num] = handle_cache_hit(cache[set_num], tag, use_lru, blocks_per_set)
        else:
            misses += 1
            if is_cache_empty(cache[set_num]):
                cache[set_num] = handle_cache_miss_empty(cache[set_num], tag)
            else:
                cache[set_num] = handle_cache_miss_full(cache[set_num], tag, use_lru)

    return hits, misses


def calculate_access_time(hits, misses, associativity, use_lru):
    """Calculate total memory access time based on hits, misses, and cache configuration.

    Access time model:
        - Base hit time: 2ns (cache access) + 2ns (search)
        - Associativity penalty: 0.5ns * log₂(associativity)
        - Miss penalty: 24ns (RAM access) + replacement overhead
        - FIFO overhead: 1ns
        - LRU overhead: 3ns (more complex bookkeeping)

    Args:
        hits (int): Number of cache hits.
        misses (int): Number of cache misses.
        associativity (int): Number of ways (blocks per set).
        use_lru (bool): True if using LRU (3ns overhead), False for FIFO (1ns overhead).

    Returns:
        float: Total access time in nanoseconds.
    """
    # Associativity penalty: log₂(ways) * 0.5ns
    assoc_penalty = 0.5 * int(math.log(associativity, 2))

    # Hit time: 2ns base + 2ns search + associativity penalty
    hit_time = 2 + 2 + assoc_penalty

    # Miss components
    ram_access = 24  # RAM access time
    replacement_overhead = 3 if use_lru else 1  # LRU is more expensive

    # Miss time: search time (no base hit) + RAM + replacement overhead
    miss_time = 2 + assoc_penalty + ram_access + replacement_overhead

    # Total time
    total_time = hits * hit_time + misses * miss_time

    return total_time


def print_configuration(num_sets, total_blocks, blocks_per_set, line_size):
    """Print cache configuration details.

    Args:
        num_sets (int): Number of sets.
        total_blocks (int): Total number of cache lines.
        blocks_per_set (int): Associativity (ways per set).
        line_size (int): Size of each cache line in bytes.
    """
    print(f"num sets : {num_sets}, tot num blocks : {total_blocks}, "
          f"blocks per set : {blocks_per_set}, offset : {line_size}")


def print_timing_result(use_lru, access_pattern, total_time):
    """Print simulation timing result.

    Args:
        use_lru (bool): True if LRU was used, False if FIFO.
        access_pattern (str): Description of access pattern (e.g., 'random').
        total_time (float): Total access time in nanoseconds.
    """
    policy = "LRU" if use_lru else "FIFO"
    print(f"{policy} {access_pattern}, total time in nano seconds {total_time}")


def run_single_configuration(cache_size_bits, line_size_bits, set_bits,
                             mem_list, use_lru, access_pattern):
    """Run cache simulation for a single configuration.

    Args:
        cache_size_bits (int): log₂ of total cache size (16 for 64KB).
        line_size_bits (int): log₂ of cache line size.
        set_bits (int): log₂ of number of sets.
        mem_list (list): Memory addresses to simulate.
        use_lru (bool): True for LRU, False for FIFO.
        access_pattern (str): Description of access pattern.
    """
    # Calculate cache parameters
    line_size = 1 << line_size_bits  # 2^line_size_bits
    cache_size = 1 << cache_size_bits  # 2^cache_size_bits
    total_blocks = cache_size // line_size
    num_sets = 1 << set_bits  # 2^set_bits
    blocks_per_set = total_blocks // num_sets

    # Initialize cache structure
    cache = initialize_cache(num_sets, blocks_per_set)

    # Print configuration
    print_configuration(num_sets, total_blocks, blocks_per_set, line_size)

    # Run simulation
    hits, misses = simulate_cache_access(cache, mem_list, line_size_bits,
                                         set_bits, use_lru)

    # Calculate and print timing
    total_time = calculate_access_time(hits, misses, total_blocks, use_lru)
    print_timing_result(use_lru, access_pattern, total_time)


def run_all_configurations(mem_list, use_lru, access_pattern):
    """Run cache simulation across all line sizes and associativity levels.

    Tests configurations:
        - Line sizes: 8, 16, 32, 64, 128, 256 bytes (2^3 to 2^8)
        - For each line size, test all valid associativity levels from
          direct-mapped (1-way) to fully associative

    Args:
        mem_list (list): Memory addresses to simulate.
        use_lru (bool): True for LRU replacement, False for FIFO.
        access_pattern (str): Description of access pattern for output.
    """
    cache_size_bits = 16  # 64KB = 2^16 bytes

    # Test line sizes from 8 to 256 bytes (2^3 to 2^8)
    for line_size_bits in range(3, 9):
        # For each line size, test different set configurations
        # Maximum sets = cache_size / line_size (direct-mapped)
        # Minimum sets = 1 (fully associative)
        max_set_bits = cache_size_bits - line_size_bits

        for set_bits in range(0, max_set_bits + 1):
            run_single_configuration(cache_size_bits, line_size_bits, set_bits,
                                   mem_list, use_lru, access_pattern)


def main():
    """Main entry point for cache simulation.

    Orchestrates the complete simulation workflow:
    1. Get user configuration (access pattern and replacement policy)
    2. Load memory access trace from file
    3. Run simulations for all cache configurations
    4. Report total computation time
    """
    start_time = datetime.now()

    # Get configuration from user
    access_pattern, use_lru, filename = get_user_configuration()

    # Load memory addresses
    mem_list = load_memory_addresses(filename)

    # Run simulations for all configurations
    run_all_configurations(mem_list, use_lru, access_pattern)

    # Report computation time
    end_time = datetime.now()
    print(f"total computational time H:MM:SS : {end_time - start_time}")


if __name__ == "__main__":
    main()
