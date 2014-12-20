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

if __name__ == '__main__':
    import sys
    import argparse
    
    argparser = argparse.ArgumentParser(description=None)
    argparser.add_argument('positional',type=int,nargs='*')
    argparser.add_argument('input_file',nargs='?',type=argparse.FileType('r'),default=sys.stdin)
    argparser.add_argument('output_dir',nargs='?',default=os.getcwd())
    argparser.add_argument('--option',dest='xxx',action='store_const',default=5)
    args = argparser.parse_args()
    
    if len(args.positional) == 2:
        inhandle = open(args.positional[0],'r')
        outhandle = open(args.positional[1],'w')
    elif len(args.positional) == 1:
        inhandle = open(args.positional[0],'r')
        outhandle = sys.stdout
    elif len(args.positional) == 0:
        inhandle = sys.stdin
        outhandle = sys.stdout



# OR

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) == 3:
        inhandle = open(sys.argv[1],'r')
        outhandle = open(sys.argv[2],'w')
    elif len(sys.argv) == 2:
        inhandle = open(sys.argv[1],'r')
        outhandle = sys.stdout
    elif len(sys.argv) == 1:
        inhandle = sys.stdin
        outhandle = sys.stdout
