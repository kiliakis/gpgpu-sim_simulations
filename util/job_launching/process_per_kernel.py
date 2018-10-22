#!/usr/bin/env python

from optparse import OptionParser
import re
import os
import subprocess
import sys
import common
import math
import yaml
import numpy as np
import csv

#*********************************************************--
# main script start
#*********************************************************--
this_directory = os.path.dirname(os.path.realpath(__file__)) + "/"

help_str = "Script to aggregate results formated with get_stats_per_kernel.py"

parser = OptionParser(usage=help_str)
parser = OptionParser()
parser.add_option("-c", "--csvfile", dest="csvfile",
                  help="The csv input file. It must be generated using the "+\
                        "get_stats_per_kernel.py scipt.",
                  default="")
parser.add_option("-s", "--stats_yml", dest="stats_yml", default="",
                  help="The yaml file that defines the caclulations to be done for each metric."+\
                       " By default it uses stats/example_stats_calc.yml")
parser.add_option("-o", "--outfile", dest="outfile",
                  help="The csv outfile file.", 
                  default="")

(options, args) = parser.parse_args()
options.csvfile = options.csvfile.strip()

options.stats_yml = common.file_option_test( options.stats_yml, os.path.join( this_directory, "stats", "example_stats_calc.yml" ),
                                            this_directory )
if options.outfile == "":
    exit("You need to specify the output file")
stat_map = {}
configs = set()
# available calcs
# acc, min, max, avg, wavg, first, last, unique
calcs = {
    'acc': (lambda x,y: np.sum(np.array(y, float))),
    'min': (lambda x,y: np.min(np.array(y, float))),
    'max': (lambda x,y: np.max(np.array(y))),
    'avg': (lambda x,y: np.mean(np.array(y))),
    'wavg': (lambda x,y: np.sum(np.array(y, float)*np.array(x, float))/np.sum(np.array(x, float))),
    'first': (lambda x,y: y[0]),
    'last': (lambda x,y: y[-1])
    #'unique': (lambda x,y: np.unique(y))
}

calc_types = {}
stats_yaml = yaml.load(open(options.stats_yml))
stats= {}
for stat in stats_yaml['collect']:
    calc_types[stat] = calcs[stats_yaml['collect'][stat]]

lines = open(options.csvfile).readlines()
i = 0
csv_str = ""
while i < len(lines):
    if '-'*100 in lines[i]:
        #csv_str += lines[i] + "\n"
        i+=1;
        stat = lines[i].split(',')[0]
        configs = lines[i].split(',')[1:-1]
        while i < len(lines) and lines[i] != '\n':
            #csv_str += lines[i] + "\n"
            i+=1
            splits = lines[i].split(',')[:-1]
            app_and_args = splits[0]
            kernels = len(splits[1:])//len(configs)
            #csv_str += "apps_and_args" + ","
            j = 0
            for config in configs:
                key = '{}/{}/{}'.format(app_and_args, config, stat)
                stat_map[key] = splits[1+j*kernels:1+(j+1)*kernels]
                j+=1
            i+=1
    else:
        i+=1

data = []
for key in stat_map.iterkeys():
    #print key
    app = key.split('/')[0]
    args = key.split('/')[1]
    config = key.split('/')[2]
    stat = key.split('/')[3].split(' ')[0]
    #app, args, config, stat = key.split('/')
    insn = stat_map['{}/{}/{}/gpu_sim_insn'.format(app, args, config)]
    if stat not in calc_types:
        continue
    if 'NA' in stat_map[key]:
        val = 'NA'
    else:
        val = calc_types[stat](insn, stat_map[key])
    data.append([stat, app, args, config, val])

header = ['stat', 'app', 'args', 'config', 'val']
data.sort(key=lambda a : (a[0], a[1], a[2]))
writer = csv.writer(open(options.outfile, 'w'), delimiter='\t')
writer.writerow(header)
writer.writerows(data)

