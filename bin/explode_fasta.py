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

from Bio import SeqIO

from pyutils import cleanup_id

argparser = argparse.ArgumentParser(description=None)
argparser.add_argument('input_file',nargs='?',type=argparse.FileType('r'),default=sys.stdin)
argparser.add_argument('output_dir',nargs='?',default=os.getcwd())
args = argparser.parse_args()

for record in SeqIO.parse(args.input_file,'fasta'):
    output_file = os.path.join(args.output_dir,'%s.fasta' % cleanup_id(record.id))
    with open(output_file,'w') as op:
        print >>op, record.format('fasta')
