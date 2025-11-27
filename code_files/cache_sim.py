"""
CPU Cache Simulation
Simulates cache memory behavior with various configurations.

Simulates a 64KB cache reading memory addresses and calculates access times
based on hits/misses for different configurations:
- Line sizes: 8 to 256 bytes (powers of 2)
- Replacement policies: LRU (Least Recently Used) and FIFO
- Associativity: Direct-mapped to fully associative

Calculates total access time in nanoseconds based on:
- Hit time: 2ns base + 2ns search + 0.5ns * log2(ways)
- Miss time: Hit time + 24ns RAM access + replacement overhead (1ns FIFO, 3ns LRU)

NOTE: This script requires an input file of memory addresses.
Update the filename path for your system before running.
"""


import math
from datetime import datetime

def FIFO(arr, replace) :
    arr.pop(0) # delete the first in array
    arr.append(replace) # append new value to end of array
    return arr

def LRU(arr, replace) :
    arr.remove(replace) # delete value from it's place in the list
    arr.append(replace) # add that value to the end of the array
    return arr
    
mem_list = []

name = input("enter 'non' for non_andom or leave blank for random (default random) : ")
if not (name == 'non') :
    name = ''
file_sorting = (name+"random")
filename = r'C:\Users\manch\Desktop\Assembly Code\Proj 1\\' + name + 'random_access.txt'
LRU_state = input("Enter 1 for 'LRU', 0 for 'FIFO' (default 'FIFO') : ")
if (LRU_state == '1') :
    LRU_state = int(1)
else :
    LRU_state = int(0)

with open(filename, 'r') as f : # read in addresses from file
    for line in f.readlines():
        mem_list.append(line.split(' '))

for row in range(len(mem_list)) : # convert addresses from string to integer
    for col in range (len(mem_list[0])) :
        mem_list[row][col] = int(mem_list[row][col])

two_exp = 16 # for initial cache size
cache_size = int(math.pow(2, two_exp)) # calc cache size
phys_addr_bits = int(math.log(1073741824, 2)) # how many bits are in a full address
                                              #  for the thissized cache
start_time = datetime.now()

for amt_offset in range(3, 9) :
    offset = int(math.pow(2, amt_offset)) # calc size of line
    blocks = int(cache_size / offset) # calc number of lines in the cache
    for sets in range(0, ((two_exp+1)-amt_offset)) :
        num_sets = int(math.pow(2, sets)) # calc number of sets in the cache
        set_mask = (num_sets-1)<<amt_offset # get the set mask so we can determine what bits in the address = the set number
        blocks_per_set = int(blocks / num_sets) # calc number of lines per set
        cache = [[-1 for x in range(blocks_per_set)] for x in range(num_sets)] # build the cache structure
        print("num sets : " +str(num_sets)+ ", tot num blocks : " +str(blocks)+ # configuration of the generated cache
            ", blocks per set : " +str(blocks_per_set)+", offset : "+str(offset))
        miss = 0
        hit = 0
        for addr in range(len(mem_list)) :
            mem_addr = mem_list[addr][0]
            set_num = (mem_addr&set_mask)>>amt_offset # get the set number from the address
            tag_num = mem_addr>>(sets+amt_offset) # get the tag from the address

            if cache[set_num][0] == -1 :
                if tag_num in cache[set_num] :
                    hit = hit + 1
                    if LRU_state == 1 and blocks_per_set > 1 :
                        cache[set_num] = LRU(cache[set_num], tag_num) # reorder the blocks in the set on hit
                else :
                    cache[set_num].pop(0) # make room in the set for the block
                    cache[set_num].append(tag_num) # add block to the end of the set
                    miss = miss + 1
            else :
                if tag_num in cache[set_num] :
                    hit = hit + 1
                    if LRU_state == 1 and blocks_per_set > 1 :
                        cache[set_num] = LRU(cache[set_num], tag_num) # reorder the blocks in the set on hit
                else :
                    cache[set_num] = FIFO(cache[set_num], tag_num)
                    miss = miss + 1
        if LRU_state == 1 :            
            print("LRU "+file_sorting+", total time in nano seconds ",
                  hit*(2+2+(0.5*int(math.log(blocks, 2))))
                  # hit time calc 2ns for a hit + search time of 2ns + 0.5*log2 of ways so
                  # if ways = 64, log2 of 64 is 6 so 2 + 0.5*6 = 5ns + 2ns = 7ns
                  + miss*(3+24+2+(0.5*int(math.log(blocks, 2)))))
                  # miss time calc is same as hit except the 2ns for hit is not added, but
                  # we do add 24 ns for requesting from RAM plus 3 for LRU so it would be
                  # 5ns + 3ns + 24 ns = 32 ns for a miss
        else :
            print("FIFO "+file_sorting+", total time in nano seconds ",
                  hit*(2+2+(0.5*int(math.log(blocks, 2)))) # same as above
                  + miss*(1+24+2+(0.5*int(math.log(blocks, 2)))))
                  # only difference is a + 1ns for FIFO instead of 3ns for LRU
end_time = datetime.now()
print("total computational time H:MM:SS : "+str(end_time - start_time))

            
