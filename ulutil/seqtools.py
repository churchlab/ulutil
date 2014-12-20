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

import copy
import json
import string
import random
import itertools

from Bio import Alphabet, pairwise2
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation

import numpy as np
import scipy as sp
import scipy.stats

from jellyfish import hamming_distance

from ulutil import unafold
from ulutil.pyutils import as_handle

random.seed()

# ==============================
# = General sequence utilities =
# ==============================

def substitute(seq,pos,sub):
    return seq[:pos] + sub + seq[pos+1:]


complement_table = string.maketrans('ACGTRYSWKMBDHVN','TGCAYRSWMKVHDBN')

def reverse(seq):
    return seq[::-1]


def complement(seq):
    return seq.upper().translate(complement_table)


def reverse_complement(seq):
    """Compute reverse complement of sequence.
    
    Mindful of IUPAC ambiguities.
    Return all uppercase.
    """
    return reverse(complement(seq))
    # return seq.upper().translate(complement_table)[::-1]

def translate(seq):
    return Seq(seq.replace('-','N'),Alphabet.DNAAlphabet()).translate().tostring()


def gc_content(seq):
    gc = seq.lower().count('g') + seq.lower().count('c')
    return float(gc) / len(seq)


def random_dna_seq(n):
    choice = random.choice
    return reduce(lambda cumul,garbage:cumul+choice('ACGT'),xrange(n),'')

global_align = lambda seq1,seq2: pairwise2.align.globalms(seq1,seq2,0.5,-0.75,-2.,-1.5,one_alignment_only=True)[0]

def percent_id(seq1,seq2):
    alignment = global_align(seq1,seq2)
    return (1. - hamming_distance(alignment[0],alignment[1]) / float(len(alignment[0]))) * 100.


# barcode mapping fns
def barcode_hamming(observed,barcodes):
    """Compute entropy of probabilistic barcode assignment.
    
    observed -- SeqRecord of the barcode
    barcodes -- list of barcode possibilities (python strings)
    """
    obs_seq = observed.seq.tostring()
    distances = [(barcode,hamming_distance(obs_seq,barcode)) for barcode in barcodes]
    closest = min(distances,key=lambda p: p[1])
    return closest  # tuple of (barcode, distance)

def barcode_probabilities(observed,barcodes):
    """Compute entropy of probabilistic barcode assignment.
    
    observed -- 'fastq' SeqRecord of the barcode
    barcodes -- list of barcode possibilities (python strings)
    """
    obs_seq = np.array(list(observed.seq.tostring()))
    obs_qual = np.array(observed.letter_annotations['phred_quality'])
    barcodes = np.array([list(bc) for bc in barcodes])
    
    choice = np.zeros(barcodes.shape, dtype=np.int)
    choice[barcodes == obs_seq] = 1
    choice[barcodes != obs_seq] = 2
    choice[:, obs_seq == 'N'] = 0
    
    N = np.zeros((1,barcodes.shape[1]))
    E = np.log1p(-np.power(10, -obs_qual / 10.))
    D = -np.log(3) - (obs_qual / 10.) * np.log(3)
    
    B = np.exp(np.sum(np.choose(choice, [N,E,D]), axis=1))
    return B / np.sum(B)

def barcode_entropy(observed, barcodes):
    """Compute entropy of probabilistic barcode assignment.
    
    observed -- 'fastq' SeqRecord of the barcode
    barcodes -- list of barcode possibilities (python strings)
    """
    P = barcode_probabilities(observed, barcodes)
    return sp.stats.entropy(P)


# for generating 'safe' filenames from identifiers
cleanup_table = string.maketrans('/*|><+ ','_____p_')
def cleanup_id(identifier):
    return identifier.translate(cleanup_table)


def seqhist(seqlist):
    seqdict = dict()
    for seq in seqlist:
        seqdict[seq] = seqdict.get(seq,0) + 1
    return seqdict

def seqmode(seqs):
    if isinstance(seqs,list):
        seqs = seqhist(seqs)
    return max(seqs.iterkeys(),key=lambda k: seqs[k])

def dimer_dG(seq1,seq2):
    """Compute a primer-dimer score using UNAFOLD hybrid_min"""
    scores = []
    subseqs1 = []
    subseqs2 = []
    for i in xrange( min(len(seq1),len(seq2)) ):
        subseqs1.append( seq1[-i-1:] )
        subseqs2.append( seq2[-i-1:] )
    scores = unafold.hybrid_min_list(subseqs1,subseqs2,NA='DNA')
    return -min(scores)

def dimer_overlap(seq1,seq2,weight_3=10):
    """Compute a primer-dimer score by counting overlaps
    
    weight_3 is the num of 3' bases to add extra weight to either primer
    """
    # import pdb
    # pdb.set_trace()
    overlap_score = lambda s1,s2: sum(1 if c1.lower() == c2.lower() else -1 for c1, c2 in itertools.izip(s1,s2))
    seq2rc = reverse_complement(seq1)
    scores = []
    for i in xrange( min(len(seq1),len(seq2)) ):
        subseq1 = seq1[-i-1:]
        subseq2 = seq2rc[:i+1]
        score = 0
        if (i+1) <= 2*weight_3:
            score += overlap_score(subseq1,subseq2) * 2
        else:
            score += overlap_score(subseq1[:weight_3],subseq2[:weight_3]) * 2
            score += overlap_score(subseq1[weight_3:-weight_3],subseq2[weight_3:-weight_3])
            score += overlap_score(subseq1[-weight_3:],subseq2[-weight_3:]) * 2
        scores.append(score)
    return max(scores)

# ==========================
# = Manual FASTA iteration =
# ==========================

# taken from biopython

identity = string.maketrans('','')
nonalpha = identity.translate(identity,string.ascii_letters)

def FastaIterator(handleish,title2ids=lambda s: s):
    with as_handle(handleish,'r') as handle:
        while True:
            line = handle.readline()
            if line == '' : return
            if line[0] == '>':
                break
    
        while True:
            if line[0] != '>':
                raise ValueError("Records in Fasta files should start with '>' character")
            descr = title2ids(line[1:].rstrip())
            fullline = ''
            line = handle.readline()
            while True:
                if not line : break
                if line[0] == '>': break
                fullline += line.translate(identity,nonalpha)
                line = handle.readline()
        
            yield (descr,fullline)
        
            if not line : return #StopIteration
        assert False, "Should not reach this line"


# ============================
# = biopython-specific tools =
# ============================

def make_SeqRecord(name,seq):
    return SeqRecord(Seq(seq),id=name,name=name,description=name)


def get_string(seqobj):
    if isinstance(seqobj,SeqRecord):
        seq = seqobj.seq.tostring().upper()
    elif isinstance(seqobj,Seq):
        seq = seqobj.tostring().upper()
    elif isinstance(seqobj,str):
        seq = seqobj.upper()
    return seq


def get_features(feature_list,feature_type):
    target_features = []
    for feature in feature_list:
        if feature.type == feature_type:
            target_features.append(feature)
    return target_features


def advance_to_features(feature_iter,feature_types):
    # note, here feature_types is a list of possible stopping points
    for feature in feature_iter:
        if feature.type in feature_types:
            return feature
    raise ValueError, "didn't find %s in record" % feature_types


def advance_to_feature(feature_iter,feature_type):
    return advance_to_features(feature_iter,[feature_type])

def map_feature( feature, coord_mapping, offset=0, erase=[] ):
    new_feature = copy.deepcopy(feature)
    new_start = coord_mapping[feature.location.start.position][-1] + offset
    new_end   = coord_mapping[feature.location.end.position][0] + offset
    new_location = FeatureLocation(new_start,new_end)
    new_feature.location = new_location
    for qual in erase:
        new_feature.qualifiers.pop(qual,None)
    return new_feature

def copy_features( record_from, record_to, coord_mapping, offset=0, erase=[], replace=False ):
    if replace:
        # index record_to features:
        feature_index = {}
        for (i,feature) in enumerate(record_to.features):
            feature_index.setdefault(feature.type,[]).append(i)
    
    feat_idx_to_delete = []
    for feature in record_from.features:
        if replace:
            feat_idx_to_delete += feature_index.get(feature.type,[])
        new_feature = map_feature( feature, coord_mapping, offset, erase )
        record_to.features.append(new_feature)
    
    if replace:
        for idx in sorted(feat_idx_to_delete,reverse=True):
            record_to.features.pop(idx)

def translate_features( record ):
    for feature in record.features:
        offset = int(feature.qualifiers.get('codon_start',[1])[0]) - 1
        feature.qualifiers['translation'] = feature.extract(record.seq)[offset:].translate()

# SeqRecord <-> JSON-serializable

def simplifySeq(seq):
    obj = {}
    obj['__Seq__'] = True
    obj['seq'] = seq.tostring()
    obj['alphabet'] = seq.alphabet.__repr__().rstrip(')').rstrip('(')
    return obj

def complicateSeq(obj):
    if '__Seq__' not in obj:
        raise ValueError, "object must be converable to Bio.Seq"
    
    # Figure out which alphabet to use
    try:
        alphabet = Alphabet.__getattribute__(obj['alphabet'])()
    except AttributeError:
        pass
    try:
        alphabet = Alphabet.IUPAC.__getattribute__(obj['alphabet'])()
    except AttributeError:
        raise
    
    seq = Seq(obj['seq'],alphabet=alphabet)
    return seq

def simplifySeqFeature(feature):
    obj = {}
    obj['__SeqFeature__'] = True
    obj['location'] = (feature.location.nofuzzy_start,feature.location.nofuzzy_end)
    obj['type'] = feature.type
    obj['strand'] = feature.strand
    obj['id'] = feature.id
    obj['qualifiers'] = feature.qualifiers
    return obj

def complicateSeqFeature(obj):
    if '__SeqFeature__' not in obj:
        raise ValueError, "object must be converable to Bio.SeqFeature"
    location = FeatureLocation(*obj['location'])
    feature = SeqFeature(location=location,type=obj['type'],strand=obj['strand'],id=obj['id'],qualifiers=obj['qualifiers'])
    return feature

def simplifySeqRecord(record):
    obj = {}
    obj['__SeqRecord__'] = True
    obj['seq'] = simplifySeq(record.seq)
    obj['id'] = record.id
    obj['name'] = record.name
    obj['description'] = record.description
    obj['dbxrefs'] = record.dbxrefs
    obj['annotations'] = record.annotations
    obj['letter_annotations'] = record.letter_annotations   # should work because it is actually a _RestrictedDict obj which subclasses dict
    obj['features'] = map(simplifySeqFeature,record.features)
    return obj

def complicateSeqRecord(obj):
    if '__SeqRecord__' not in obj:
        raise ValueError, "object must be converable to Bio.SeqRecord"
    features = map(complicateSeqFeature,obj['features'])
    record = SeqRecord(seq=complicateSeq(obj['seq']),id=obj['id'],name=obj['name'],description=obj['description'],dbxrefs=obj['dbxrefs'],features=features,annotations=obj['annotations'],letter_annotations=obj['letter_annotations'])
    return record
