# Copyright 2014 Uri Laserson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ulutil import oligoTm, unafold, seqtools

def generate_candidates(seq,minlen=18,maxlen=30):
    candidates = []
    for start in xrange(len(seq)):
        length = minlen
        while length <= maxlen and start+length <= len(seq):
            candidates.append( seq[start:start+length] )
            length += 1
    return candidates

def choose_PCR_primer(seq,target_Tm=62.):
    candidates = generate_candidates(seq)
    
    # filter for Tm
    candidates = filter(lambda s: abs(oligoTm.oligoTm(s) - target_Tm) <= 2, candidates)
    if len(candidates) == 0:
        raise ValueError, "No primer candidates meet Tm cutoffs"
    
    # filter for 0.4-0.6 GC content
    candidates = filter(lambda s: abs(seqtools.gc_content(s) - 0.5) <= 0.1,candidates)
    if len(candidates) == 0:
        raise ValueError, "No primer candidates meet GC content cutoffs"
    
    # rank on secondary structure minimization
    candidates.sort(key=unafold.hybrid_ss_min)
    
    return candidates[0]
