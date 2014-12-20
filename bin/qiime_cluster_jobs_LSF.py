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
import datetime
import optparse

import lsf

option_parser = optparse.OptionParser()
option_parser.add_option('-m','--make_jobs',action='store_true')
option_parser.add_option('-s','--submit_jobs',action='store_true')
option_parser.add_option('-q','--queue',default='normal_serial')
option_parser.add_option('-l','--log_dir')
(options,args) = option_parser.parse_args()

# check that we get the qiime-required arguments
if len(args) == 2:
    jobs_list_file = args[0]
    job_id = args[1]
elif len(args) == 0:
    raise ValueError, "Didn't get the right command line arguments"

# make a directory for holding LSF log files
if options.log_dir == None:
    log_dir = os.path.join(os.environ['HOME'],'qiime_parallel_logs')
else:
    log_dir = options.log_dir

if not os.path.exists(log_dir):
    os.mkdir(log_dir,0755)

# submit the jobs
jobs_handle = open(jobs_list_file,'r')
job_ids = []
logs = []
for (i,line) in enumerate(jobs_handle):
    datetimestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log = os.path.join( log_dir, 'job_%i_%s.log' % (i,datetimestamp) )
    job_id = lsf.submit_to_LSF(options.queue,log,line.strip())
    job_ids.append(job_id)
    logs.append(log)
jobs_handle.close()
