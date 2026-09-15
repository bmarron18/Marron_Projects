#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  6 17:15:03 2025

@author: bmarron18
"""
    
# %%

'''
Counts
    Outcome Space 
'''

from pathlib import Path
import os

import math
import numpy as np
import pandas as pd
from scipy.stats import hypergeom, binom, beta
from itertools import combinations

# %%

    ≠   ctlt+shift+U+2260


# %%

----    Vocab/Glossary    --------------------------------------------
arrangement
group
set
collection
type
characteristics
category
mutually exclusive and exhaustive (MEE)
sequence
combination
pull
draw
selection
atomic outcome
collective outcome
outcome
event
member
element



permutation ==  * A time-based sequence of uniquely labeled entities with various characteristics
                 * Although there may be characteristics shared among entities,
                   the unique labels are most important; the unique labels could be time stamps
                 * The entities ARE NOT exchangeable in the sequence bc there would be a 
                   change in info content
                 * For example, a1a2b1 ≠ a2a1b1 or cat ≠ act

combination ==  * a jumbled or unordered group of uniquely labeled entities with various 
                  characteristics
                * Although there are unique labels, the characteristics shared among 
                  the entities are the most important
                * The entities ARE exchangeable in the combination bc there is no  
                  change in info content within a bin collection  
                * For example, a1a2b1 = = a1b1a2 = a2a1b1 = etc all belong to the 
                  bin collection 2 type a, 1 type b
                  

bin collection == * a specific combination based on the cts of entites with
                    specific characteristics within the combination
                  * For example, if the output from a generator is a closed set of 
                    type a and type b entities (ie, {a,b}), then 
                    the MEE set of possible bin collections includes:
                        5 type a, 0 type b
                        4 type a, 1 type b
                        3 type a, 2 type b
                        2 type a, 3 type b
                        1 type a, 4 type b
                        0 type a, 5 type b

mutually exclusive and exhaustive (MEE) == 

# %%
'''
Example 1
    based on Jaynes, pp 52

'''
    There are 11 balls in an urn; 7 are white (type a) and 4 are red (type b). The balls have 
    unique labels and are identical except for color and label. The Principle of Indifference
    applies. Five (5) balls are pulled at random from the urn.
    
    entitity            == a ball
    label               == [1, 11]
    characteristic      == white (type a) and red (type b)


---- W/O REPLACEMENT --------------------------------------  
    (1) 
    Observation Level I: 
        - Can discern the unique label AND the characteristic color of each ball.
    Atomic Outcome: 
        - The random pull/draw/selection of one (1) single ball from the urn; W/O REPLACEMENT
        - Each ball is a unique entity (per label) with additional characteristics:
          white (type a) or red (type b)
    Collective Outcome: 
        - A single, time-based sequence of five (5) atomic outcomes; a permutation.
        - The members of the complete set of permutations (sequences) are 
          MEE (per the observation level)

          
    Collective Outcome Space Cts:
        Ct Entities Available/Draw          Time stamp/Draw
        -------------------                 ----------
        11 options for the first draw       (t1)
        10 options for the second draw      (t2)
        09 options for the third draw       (t3)
        08 options for the fourth draw      (t4)
        07 options for the fifth draw       (t5)
  
        
        Ct of all members in the complete set of MEE permutations:
        n!/(n-r)!
        11!/(11-5)! = 11!/6! = 11*10*9*8*7 = 55440 
        
        
        # Verification: breaking it down by bin collections (ie, ct type a and ct type b)
        
        Bin Collection          Ct Combinations/Bin Collection
        ------------------      ------------------------------
        5 type a ; 0 type b ==> 7C5 * 4C0 * 5! = 21*120    = 2520
        4 type a ; 1 type b ==> 7C4 * 4C1 * 5! = 35*4*120  = 16800
        3 type a : 2 type b ==> 7C3 * 4C2 * 5! = 35*6*120  = 25200
        2 type a : 3 type b ==> 7C2 * 4C3 * 5! = 21*4*120  = 10080
        1 type a : 4 type b ==> 7C1 * 4C4 * 5! = 7*1*120   = 840
        
                                                SUM         = 55440
        
        There are 5! = 120 arrangements for each bin collection
        Thus, 
        (120)(21+140+210+84+7) = 55440


     (2) 
 Observational Level II: 
     - Can discern ONLY the color of each ball OR labels are not important
 Atomic Outcome:
     - The  random pull/draw/selection of one (1) single ball from the urn; W/O REPLACEMENT
     - Each ball remains a unique entity (per label) with additional characteristics
       (type a or type b) but only characteristics are important or observeable; labels are 
       of secondary importance
 Collective Outcome: 
     - A time-based unordered group of five (5) atomic outcomes as a combination 
       of type a and type b cts; a bin collection
     - The members of the complete set of combinations are MEE (per the observation level)


     Ct of all members in the complete set of MEE bin collections:
     nCr
     11C5 = 11!/5!6! = 462 ct of combinations in the complete set of bin collections
     
  Collective Outcome Space Cts:
      Bin Collection            Ct Combinations/Bin Collection
      -------------------        ------------------------------
     5 type a ; 0 type b ==> 7C5 * 4C0 = 21*1 = 21
     4 type a ; 1 type b ==> 7C4 * 4C1 = 35*4 = 140
     3 type a : 2 type b ==> 7C3 * 4C2 = 35*6 = 210
     2 type a : 3 type b ==> 7C2 * 4C3 = 21*4 = 84
     1 type a : 4 type b ==> 7C1 * 4C4 = 7 * 1 = 7
                                         SUM == 462
                                         
     21+140+210+84+7 = 462


---- W/ REPLACEMENT -------------------------------------------

    (3)
    Observation Level I: 
        Can discern time-stamp label AND color on each ball.
    Atomic Outcome: 
        The pull of one (1) single ball from the urn; W/ REPLACEMENT
        Each ball is a unique entity (per time-stamp label) with additional characteristics
        (here, type a or type b)
     Collective Outcome: 
        A single, time-based sequence of five (5) atomic outcomes as a unique permutation
        of labeled entities. The members of the complete set of permutations/sequences are 
        mutually exclusive and exhaustive(MEE) per the observation level
    Collective Outcome Space Cts:
        11 options for the first draw
        11 options for the second draw
        11 options for the third draw
        11 options for the fourth draw
        11 options for the fifth draw
        
        11^5 = 11**5 = 161051 unique sequences of time-stamped labeled entities
        
        (n+r-1)!/(n-1)!(r)!
        (11+5-1)!/(10)!(5)! = 15!/10!5! = 3003 types of bin collections 
       
        
        This creates a time-based set of replicates of the original set.
        There are five (5) replicate sets of the original set  bc there are five (5) 
        draws/ slots  per sequence:
            
            t1      a1.1 a2.1 a3.1 a4.1 a5.1 a6.1 a7.1  b8.1 b9.1 b10.1 b11.1
            t2      a1.2 a2.2 a3.2 a4.2 a5.2 a6.2 a7.2  b8.2 b9.2 b10.2 b11.2
            t3      a1.3 a2.3 a3.3 a4.3 a5.3 a6.3 a7.3  b8.3 b9.3 b10.3 b11.3
            t4      a1.4 a2.4 a3.4 a4.4 a5.4 a6.4 a7.4  b8.4 b9.4 b10.4 b11.4
            t5      a1.5 a2.5 a3.5 a4.5 a5.5 a6.5 a7.5  b8.5 b9.5 b10.5 b11.5
    
        At each time step there is the options to fill the current slot in the sequence with
        any member of this time-based set.
        
        
        
        # python Factorial
        >>>
       z= math.factorial(5)
        >>>
        
        # python xCy combinations
        >>>
        data = list(range(1, 36))
        ct = len(list(combinations(data, 5)))
        print (ct)
        <<<
        
        
    (4)
    Observation Level II: 
        Can discern ONLY color on each ball OR labels are unimportant.
    Atomic Outcome: 
        The pull of one (1) single ball from the urn; W/ REPLACEMENT
        Each ball is an entity with characteristics (here, type a or type b)
     Collective Outcome: 
        A single, group of five (5) atomic outcomes as a combination / bin collection
        of labeled entities. The members of the complete set of combinations are 
        mutually exclusive and exhaustive(MEE) per the observation level
    Collective Outcome Space Cts:
        2 options for the first draw (t1)
        2 options for the second draw (t2)
        2 options for the third draw (t3)
        2 options for the fourth draw (t4)
        2 options for the fifth draw (t5)
        
        NB. Although there are 7 type a and 4 type b cts in the urn, the lack of entity 
        uniqueness (ie, labels) coupled with the abibility to generate replacemnts contracts the
        set of entities to simply {a, b}, or one, type a ct and one, type b ct
        
        n^r
        2^5 = 2**5 = 32 unique sequences (IFF labels were observable)
        
        (n+r-1)!/(n-1)!(r)!
        (2+5-1)!/(1)!(5)! = 6!/5! = 6 types of bin collections 
        
        # Verification: breaking it down by bin collections of characteristics (type a and type b)
        # Possible collections of characteristics are:        
        5 type a ; 0 type b ==> 5! / 5! * 0!    =  1
        4 type a ; 1 type b ==> 5! / 4! * 1!    =  5
        3 type a : 2 type b ==> 5! / 3! * 2!    = 10
        2 type a : 3 type b ==> 5! / 2! * 3!    = 10
        1 type a : 4 type b ==> 5! / 1! * 4!    =  5
        0 type a ; 5 type b ==> 5! / 5! * 0!    =  1
        
                                        SUM     = 32
        
        
       # python xCy combinations
        >>>
        data = list(range(1, 36))
        ct = len(list(combinations(data, 5)))  # 11C5
        print (ct)
            462
        <<<
    
    
    
    
    
    What are all of the observable outcomes that are possible given that 
    there are no unique labels on the balls? That is, how many observable 
    are possible regardless of whether the balls carry unique labels or not. The observable
    outcomes are mutually exclusive and exhaustive (MEE) 
    
     
       

    (2) Q: Iff the balls carried unique labels AND a single outcome is defined as drawing 
    five balls from the urn, one after the other,  and placing them sequentially in order 
    in a set of 5 slots, how many unique sequences could be genrated? The sequences are
    NOT exchangeable because the resolution of observability is at the level of the
    labels, regardless of other characteristics of the balls.
    A: There would be 11 options for drawing the first ball, 10 options for drawing the 
    second ball, 9 options for drawing the third ball,..., and 7 options for drawing the 
    fifth ball. 
    
    
    ct of possible unique sequences = 11! / (11-5)!
                                    = 11*10*9*8*7
                                    = 55440
    
    
    
     * M = 11 (ct of all entities in a set; two types)
     * N = 4 Type I entities
     * M-N = 7 Type II entities
     * n = 5 (ct of draws/trials/slots)
     * k =2 (ct of Type I in n draws/trials/slots)
     
 

hypergeom.pmf(2, 11, 5, 4, loc=0)
	


# %%
'''
Example 2
    from Hoff pp
'''

# --- Outcome Space from Actual Sampling -----------------------------------------  
    # If take a sample of 20 people and the output for each person is either
    # type a or type b (entities with two possible characteristics) 
    
Observation Level 1 
    # Imagine that each of the slots/positions of the sequences are also identifiable
    # or that the entities themselves are labeled: Sequences are NOT EXCHANGEABLE
    # Thus there are 1048576 possible unique sequences (permutations) for the data
    
    # The output space of unique sequences is now closed (with 1048576 ct of 
    # unique sequences)
    
 2^20 = 1048576 unique sequences in the outcome space
 
     # python
 >>> 
 2**20
 >>>
    
Observational Level 2 (Jaynes pp 62)
    # The labels on individual entities is unimportant or not observable, only the 
    # chracteristics are important or observable. Then the set of sequences is an EXCHANGEABLE.
    # DISTRIBUTION of sequences. That is, only the TOTAL CTS of type a and type b  
    # in any sequence are important or observable; the actual location/position  of 
    # characteristics in the sequence is not important.
    
    # Take any one of the 1048576 unique sequences. This unique sequence will have either 
    # a type a characteristic or a type b characteristic in/at each of the 20 slots/positions
    # in the sequence. For example, the unique sequence
    #      a1a2a3a4b5a6a7a8a9a10a11a12a13b14a15a16a17a18a19a20

>>>
"""
If the output from your iteration is very large, or you only need to process one item at a
time without storing the entire result in memory, you can use a generator function. This 
allows for "lazy" evaluation, yielding results as needed.

Fxn: generate_large_permutations(items) 
Generates permutations of a list of items using itertools.permutations.
Args:
  items: The list or iterable for which to generate permutations.
Yields:
  Each permutation as a tuple.
"""

def generate_large_permutations(items):
  yield from itertools.permutations(items)

# a large list
sequence = ['a1', 'a2', 'a3', 'a4','b5', 'a6', 'a7', 'a8', 'a9', 'a10', 'a11', 'a12', 'a13', 'b14', 'a15', 'a16', 'a17', 'a18', 'a19', 'a20']

# Create the generator
permutation_generator = generate_large_permutations(sequence)

# Iterate through the permutations without storing them all in memory
print("First 3 permutations:")
for i, perm in enumerate(permutation_generator):
  if i == 20081700:
      print(perm)

>>>




>>> python
    # create paths to files
    # Retrieve files as PosixPaths
    
doc_dir = "/home/bmarron18/Desktop"
OUTPUT_FILE = "PandaTests.txt"
output_filepath = os.path.join(doc_dir, OUTPUT_FILE)
output_f = Path(output_filepath)

output_data = []
sequence = ['a1', 'a2', 'a3', 'a4','b5', 'a6']
all_permutations = permutations(sequence)

  # Output
for i in all_permutations:
    result = i
    output_data.append(result) 
    
with open(output_f, "w", encoding="utf-8") as f:
     f.write(output_data)
>>>
   
    # There are 20!=2432902008176640000 arrangements for this possible unique sequence. Realizing
    
>>>
math.factorial(20)

>>>
    # these arrangements would generate a subset from the complete set of 1048576
    # sequences that all share EQUAL CTS of type a and type b characteristics. 
    # The subset contains degenrate sequences, those sequences that contain equal cts of
    # type a and type b characteristics. Degenerate sequences are combinations.
    
    # 
    # all of the sets of combinations generated by 20! are symmetric about the cts 
    # of type a and type b characteristic. For example, there are 20 sequences in the
    # set where there is 1 type a and 19 type b. And symmetrically, there are 20
    # sequences in the set where there are 19 type a and 1 type b.
    
    # To find the ct of degenrate sequences in a set:
    #   1 sequence with 0 infected / 20 non-infected 
    #       == 20!/0!20! == math.comb(20,0) in python
    #   20 sequences with 1 infected / 19 non-infected
    #       == 20!/1!19! == math.comb(20,1)
    #   190 sequences with 2 infected / 18 non-infected
    #       == 20!/2!18! == math.comb(20,2)
    #   1140 sequences with 3 infected / 17 uninfected 
    #       == 20!/3!17! == math.comb(20,3)
    #   ...
    #   1140 sequences with 17 infected / 3 uninfected 
    #       == 20!/3!17! == math.comb(20,17)
    #   190 sequences with 18 infected / 2 non-infected
    #       == 20!/2!18! == math.comb(20,18)
    #   20 sequences with 19 infected / 1 non-infected
    #       == 20!/1!19! == math.comb(20,19)
    #   1 sequence with 20 infected / 0 uninfected
    #       == 20!/20!0! == math.comb(20,20)













