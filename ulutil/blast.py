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

import sys
from Bio.Blast import NCBIWWW, NCBIXML

def number_genome_qblast_hits(seqreclist):
    fastastring = ''.join([rec.format('fasta') for rec in seqreclist])
    results_handle = NCBIWWW.qblast('blastn','nr',fastastring,expect=1.,word_size=7,nucl_reward=1,nucl_penalty=-3,hitlist_size=1000)
    blast_records = NCBIXML.parse(results_handle)
    
    hits = [len(record.alignments) for record in blast_records]
    
    return hits

def number_genome_qblast_protein_hits(sequence):
    results_handle = NCBIWWW.qblast('blastp','nr',sequence,expect=100,word_size=3,hitlist_size=1000)
    blast_records = NCBIXML.parse(results_handle)
    num_hits = sum([len(record.alignments) for record in blast_records])
    return num_hits
    


# def number_genome_qblast_hits(seqlist):
#     fastastring = ''
#     for (i,seq) in enumerate(seqlist): fastastring += '>seq%i\n%s\n' % (i,seq)
#     
#     results_handle = NCBIWWW.qblast('blastn','nr',fastastring,expect=0.1,word_size=7,nucl_reward=1,nucl_penalty=-3,hitlist_size=500)
#     blast_records = NCBIXML.parse(results_handle)
#     
#     total_hits = 0
#     for record in blast_records: total_hits += len(record.alignments)
#     
#     # print total_hits
#     # sys.stdout.flush()
#     
#     return total_hits
