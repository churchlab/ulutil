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

from ulutil import exonerate

standard_primers = {    # 5' -> 3'
    'M13R' : 'caggaaacagctatgac',
    'M13F-20' : 'gtaaaacgacggccag',
    'T3' : 'attaaccctcactaaaggga',
    'T7' : 'taatacgactcactataggg'
}

standard_vectors = {
    'pCR4-TOPO-left' : 'catgattacgccaagctcagaattaaccctcactaaagggactagtcctgcaggtttaaacgaattcgccctt',
    'pCR4-TOPO-right' : 'aagggcgaattcgcggccgctaaattcaattcgccctatagtgagtcgtattacaattca',
    'pCR4Blunt-TOPO-left' : 'catgattacgccaagctcagaattaaccctcactaaagggactagtcctgcaggtttaaacgaattcgccctt',
    'pCR4Blunt-TOPO-right' : 'aagggcgaattcgcggccgctaaattcaattcgccctatagtgagtcgtattacaattca'
}




def trimleft(left,read):
    """Align 2 seqs, forcing alignment of right-end of left.
    
                     ...RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR...
    ...LLLLLLLLLLLLLLLLLLLLLLLLLLL  <- (forced aln here)
    
    Uses exonerate.
    """
    # perform alignment
    cmd = exonerate.ExonerateCommand('findend','parsable','bestonly')
    rawaln = exonerate.run_exonerate2(cmd,left,read)
    if rawaln == '': return read
    aln = exonerate.parse_aln(rawaln)
    
    # check that the right-end of left was successfully placed
    if aln['query_len'] != aln['query_aln_end']:
        raise ValueError, "failed to align right-end of left sequence"
    
    # check that both strands are + orientation
    if aln['query_strand'] != '+':
        raise ValueError, "query strand has been reversed"
    if aln['target_strand'] != '+':
        raise ValueError, "target strand has been reversed"
    
    # return trimmed sequence
    return read[aln['target_aln_end']:]

def trimright(right,read):
    """Align 2 seqs, forcing alignment of left-end of right.
    
    ...DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD...
        (forced aln here) -> RRRRRRRRRRRRRRRRRRRRRRRRRRRRR...
    
    Uses exonerate.
    """
    # perform alignment
    cmd = exonerate.ExonerateCommand('findend','parsable','bestonly')
    rawaln = exonerate.run_exonerate2(cmd,right,read)
    if rawaln == '': return read
    aln = exonerate.parse_aln(rawaln)
    
    # check that the left-end of right was successfully placed
    if aln['query_aln_begin'] != 0:
        raise ValueError, "failed to align left-end of right sequence"
    
    # check that both strands are + orientation
    if aln['query_strand'] != '+':
        raise ValueError, "query strand has been reversed"
    if aln['target_strand'] != '+':
        raise ValueError, "target strand has been reversed"
    
    # return trimmed sequence
    return read[:aln['target_aln_begin']]

# ===============
# = UNFINISHED: =
# ===============

def bidirectional_alignment(forward,reverse):
    """Align forward and reverse sequence of bidirectional Sanger reads.
    
    forward and reverse sequences must already be in the same 'sense' (i.e.,
    reverse should be revcomped if necessary so that both strands in alignment
    are '+').
    
    Forces alignment of both ends (right end of forward, and left end of
    reverse).
    
    ...FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
                               RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR...
    
    Uses exonerate.
    """
    # perform alignment
    cmd = exonerate.ExonerateCommand('findend','parsable','bestonly')
    rawaln = exonerate.run_exonerate2(cmd,forward,reverse)
    aln = exonerate.parse_aln(rawaln)
    
    # check that both strands are + orientation
    if aln['query_strand'] != '+':
        raise ValueError, "query strand has been reversed"
    if aln['target_strand'] != '+':
        raise ValueError, "target strand has been reversed"
    
    # check that right end of forward and left end of reverse are placed
    if aln['query_len'] != aln['query_aln_end']:
        raise ValueError, "failed to align right-end of forward sequence"
    if aln['query_aln_begin'] != 0:
        raise ValueError, "failed to align left-end of right sequence"
