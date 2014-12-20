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

import os
import sys
import argparse

import numpy as np
import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as plt

import seqtools

argparser = argparse.ArgumentParser(description=None)
argparser.add_argument('positional',nargs='*')
argparser.add_argument('--log',action='store_true')
args = argparser.parse_args()

if len(args.positional) == 2:
    inhandle = open(args.positional[0],'r')
    outfile = args.positional[1]
elif len(args.positional) == 1:
    inhandle = open(args.positional[0],'r')
    outfile = 'lenhist.png'
elif len(args.positional) == 0:
    inhandle = sys.stdin
    outfile = 'lenhist.png'

read_lengths = []
for (name,read) in seqtools.FastaIterator(inhandle):
    read_lengths.append(len(read))

print "Number of reads: %i" % len(read_lengths)
print "Shortest read length: %i bp" % min(read_lengths)
print "Longest read length: %i bp" % max(read_lengths)
print "Median read length: %i bp" % np.median(read_lengths)
print "Mean read length: %i bp" % np.mean(read_lengths)

if not args.log:
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(read_lengths,bins=range(max(read_lengths)+1),linewidth=0,log=False)
    ax.set_xlabel('Read length')
    fig.savefig(outfile)
else:
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(read_lengths,bins=range(max(read_lengths)+1),linewidth=0,log=True)
    ax.set_xlabel('Read length')
    fig.savefig(outfile)
