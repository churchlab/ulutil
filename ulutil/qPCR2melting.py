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

import matplotlib as mpl
import matplotlib.pyplot as plt

def qPCR2melting(inputfile,output_formats):
    outputbasename = os.path.splitext(os.path.basename(inputfile))[0]
    
    # Learn some things about the data:
    #   How many curves are there?
    ip = open(inputfile,'r')
    for line in ip:
        if line.startswith('Step'):
            # Verify the fields in the line:
            fields = line.split(',')
            if fields[0] != 'Step' or fields[1] != 'Cycle' or fields[2] != 'Dye' or fields[3] != 'Temp.':
                raise ValueError, 'Expected line like: "Step,Cycle,Dye,Temp.,..."'
            curve_labels = fields[4:-1]   # (skip the above four fields and last extra comma)
            break
    #   What step is the melting at?
    for line in ip: # advance to data set characterization
        if line.strip() == 'Analysis Options':
            break
    for line in ip:
        if line.startswith("Step") and "Melting Curve" in line:
            line_id = line.split()[1].strip(':')
            break
    ip.close()
    
    # Create data structures
    temps = []
    curves = [[] for curve in curve_labels]
    
    # Load the data
    ip = open(inputfile,'r')
    for line in ip: # advance to data
        if line.startswith('Step'):
            break
    for line in ip:
        if line.strip() == '':
            break
        if line.split(',')[0] == line_id:
            temps.append(float(line.split(',')[3]))
            data = map(float,line.split(',')[4:-1])
            for (i,value) in enumerate(data):
                curves[i].append(value)
    
    # Make the plots
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for (label,curve) in zip(curve_labels,curves):
        ax.plot(temps,curve,label=label)
    ax.legend(loc=2)
    ax.set_xlabel('Temperature')
    ax.set_ylabel('Fluorescence (a.u.)')
    for format in output_formats:
        fig.savefig(outputbasename+'.melting.'+format)

if __name__ == '__main__':
    import sys
    import optparse
    
    output_formats = set()
    def append_format(option,opt_str,value,parser):
        output_formats.add(opt_str.strip('-'))
    
    option_parser = optparse.OptionParser()
    option_parser.add_option('--png',action='callback',callback=append_format)
    option_parser.add_option('--pdf',action='callback',callback=append_format)
    option_parser.add_option('--eps',action='callback',callback=append_format)
    (options,args) = option_parser.parse_args()
    
    if len(args) != 1:
        raise ValueError, "Must give a single file as input."
    
    output_formats = list(output_formats)
    if output_formats == []:
        output_formats.append('pdf')
        output_formats.append('png')
    inputfile = args[0]
    
    qPCR2melting(inputfile,output_formats)
    