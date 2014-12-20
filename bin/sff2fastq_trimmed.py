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
import argparse

from Bio import SeqIO
    
argparser = argparse.ArgumentParser(description=None)
argparser.add_argument('input_file',nargs='?',type=argparse.FileType('rb'),default=sys.stdin)
argparser.add_argument('output_file',nargs='?',type=argparse.FileType('w'),default=sys.stdout)
args = argparser.parse_args()

for record in SeqIO.parse(args.input_file,'sff'):
    start = record.annotations['clip_qual_left']
    end   = record.annotations['clip_qual_right']
    args.output_file.write( record[start:end].format('fastq') )
