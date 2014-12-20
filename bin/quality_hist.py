#! /usr/bin/env python
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
import random

from Bio import SeqIO

import numpy as np
import scipy as sp
import scipy.stats

import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as plt

from pbs import wc

input_file = sys.argv[1]
output_file = sys.argv[2]

num_lines = int(wc(input_file, '-l').split()[0])
assert(num_lines % 4 == 0)
num_reads = num_lines / 4

if num_reads > 10000000:
    idxs = set(sorted(random.sample(xrange(num_reads),10000000)))

qualities = []
for (i,record) in enumerate(SeqIO.parse(input_file, 'fastq')):
    if num_reads <= 10000000 or i in idxs:
        qualities.append(record.letter_annotations['phred_quality'])
    
    if i % 10000 == 0:
        sys.stdout.write("%i " % i)
        sys.stdout.flush()

qualities = np.array(qualities)

positions = range(1, qualities.shape[1]+1)

p5  = sp.stats.scoreatpercentile(qualities, 5)
p25 = sp.stats.scoreatpercentile(qualities, 25)
p50 = sp.stats.scoreatpercentile(qualities, 50)
p75 = sp.stats.scoreatpercentile(qualities, 75)
p95 = sp.stats.scoreatpercentile(qualities, 95)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(positions,p5,  s=3, c='k', linewidths=0, zorder=2)
ax.scatter(positions,p95, s=3, c='k', linewidths=0, zorder=2)
for (pos, low, high) in zip(positions, p25, p75):
    ax.plot([pos, pos], [low, high], color='#bdbdbd', lw=1, zorder=1)
ax.scatter(positions, p50, s=6, c='r', linewidths=0, zorder=3)
ax.set_xlabel('position')
ax.set_ylabel('phred score')
ax.set_xlim([positions[0]-1, positions[-1]+1])
ax.set_ylim([0, 45])
fig.savefig(output_file)
