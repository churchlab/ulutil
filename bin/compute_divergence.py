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

import subprocess
import argparse

argparser = argparse.ArgumentParser(description=None)
argparser.add_argument('-q','--query',required=True)
argparser.add_argument('-t','--target',required=True)
argparser.add_argument('-o','--output',required=True)
argparser.add_argument('-u','--usearch',default='usearch')
args = argparser.parse_args()

usearch_cmd = "%s --query %s --db %s --nofastalign --nousort --minlen 1 --maxaccepts 0 --maxrejects 0 --global --id 0 --userout %s --userfields query+target+id0+id1+id2+id3+id4+gaps+intgaps+qloz+qhiz+tloz+thiz+ql+tl+cols+intcols"

p = subprocess.Popen(usearch_cmd % (args.usearch,args.query,args.target,args.output),shell=True)
p.wait()
