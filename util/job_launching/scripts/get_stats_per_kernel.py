#!/usr/bin/env python

from optparse import OptionParser
import re
import os
import subprocess
import sys
import common
import math
import yaml

this_directory = os.path.dirname(os.path.realpath(__file__)) + "/"

#*********************************************************--
# main script start
#*********************************************************--
this_directory = os.path.dirname(os.path.realpath(__file__)) + "/"

help_str = "There are 3 ways to use this file" +\
           " 1) Specify a sim_name: \"-N <the-name>\"\n"+\
           "    If you do this, then the job launching logfiles"+\
           " will be searched for the most recent sim_name job launch."+\
           " Those specific output files will be parsed."+\
           " 2) Specify a logfile: \"-l <the-file>\"\n"+\
           "    If you do this, then the jobs in the specific logfile will be parsed" +\
           " If no options are specified, then it basically defaults to the -l"+\
           " option using the latest logfile."
#           " 3) Specify a configs yml: \"-y <the-yaml>\"\n"+\
#           "    The \"configs\" and \"benchmark\" lists in the yaml are parsed."+\
#           " The most recent runs of these bench+config options are searched.\n"+\


parser = OptionParser(usage=help_str)
parser = OptionParser()
parser.add_option("-l", "--logfile", dest="logfile",
                  help="The logfile the status is based on. "+\
                        "By default, we will base it on the latest simulations launched.\n" +\
                        "specify \"all\" to use all the simulation logfiles in the directory",
                  default="")
parser.add_option("-r", "--run_dir", dest="run_dir",
                  help="The directory where the benchmark/config directories exist.", default="")
parser.add_option("-N", "--sim_name", dest="sim_name",
                  help="If you are launchign run_simulations.py with the \"-N\" option" +\
                       " then you can run ./job_status.py with \"-N\" and it will" + \
                       " give you the status of the latest run with that name."+ \
                       " if you want older runs from this name, then just point it directly at the"+\
                       " logfile with \"-l\"", default="")
parser.add_option("-c", "--configs_yml", dest="configs_yml", default="",
                  help="If this option is specified, then sim_name and logfile are ignored." +\
                       "Instead, the output files that will be parsed will")
parser.add_option("-a", "--apps_yml", dest="apps_yml", default="",
                  help="If this option is specified, then sim_name and logfile are ignored." +\
                       "Instead, the output files that will be parsed will")
#parser.add_option("-b", "--simulator_build", dest="simulator_build", default="",
#                  help="If you only want data from a particular build of the simulator, specify this flag.")
parser.add_option("-s", "--stats_yml", dest="stats_yml", default="",
                  help="The yaml file that defines the stats you want to collect."+\
                       " by default it uses stats/example_stats.yml")
(options, args) = parser.parse_args()
options.logfile = options.logfile.strip()
options.run_dir = options.run_dir.strip()
options.sim_name = options.sim_name.strip()

cuda_version = common.get_cuda_version()
options.run_dir = common.dir_option_test( options.run_dir, this_directory + ("../../sim_run_%s/"%cuda_version),
                                          this_directory )
if not os.path.isdir(options.run_dir):
    exit(options.run_dir + " does not exist - specify the run directory where the benchmark/config dirs exist")

options.stats_yml = common.file_option_test( options.stats_yml, os.path.join( this_directory, "stats", "example_stats.yml" ),
                                            this_directory )
options.configs_yml = common.file_option_test( options.configs_yml, "", this_directory )
options.apps_yml = common.file_option_test( options.apps_yml, "", this_directory )

stat_map = {}
configs = set()
apps_and_args = set()
specific_jobIds = {}

stats_to_pull = {}
stats_yaml = yaml.load(open(options.stats_yml))
stats= {}
for stat in stats_yaml['collect']:
    stats_to_pull[stat] = re.compile(stats_yaml['collect'][stat])

if options.configs_yml != "" and options.apps_yml != "":
    for app in common.parse_app_yml( options.apps_yml ):
        a,b,exe_name,args_list = app
        for args in args_list:
            apps_and_args.add( os.path.join(exe_name, re.sub(r"[^a-z^A-Z^0-9]", "_", args.strip())) )
    for config, params, gpuconf_file in common.parse_config_yml( options.configs_yml ):
        configs.add( config )
else:
    # This code gets the logfiles to pull the stats from if you are using the "-l" or "-N" option
    parsed_logfiles = []
    logfiles_directory = this_directory + "../job_launching/logfiles/"
    if options.logfile == "":
        if not os.path.exists(logfiles_directory):
            exit("No logfile specified and the default logfile directory cannot be found")
        all_logfiles = [os.path.join(logfiles_directory, f) \
                           for f in os.listdir(logfiles_directory) if(re.match(r'sim_log.*',f))]
        if len(all_logfiles) == 0:
            exit("ERROR - No Logfiles in " + logfiles_directory)
        if options.sim_name != "":
            named_sim = []
            for logf in all_logfiles:
                match_str = r".*\/sim_log\.{0}\..*".format( options.sim_name )
                if re.match( match_str, logf ):
                    named_sim.append( logf )
            if len( named_sim ) == 0:
                exit( "Could not find logfiles for job with the name \"{0}\"".format( options.sim_name ) )
            all_logfiles = named_sim
        parsed_logfiles.append(max(all_logfiles, key=os.path.getmtime))
    elif options.logfile == "all":
        parsed_logfiles = [os.path.join(logfiles_directory, f) \
                        for f in os.listdir(logfiles_directory) if(re.match(r'sim_log.*\.latest',f))]
    else:
        parsed_logfiles.append(common.file_option_test( options.logfile, "", this_directory ))

    print "Using logfiles " + str(parsed_logfiles)

    for logfile in parsed_logfiles:
        if not os.path.isfile(logfile):
            exit("Cannot open Logfile " + logfile)

        with open( logfile ) as f:
            for line in f:
                time, jobId, app ,args, config, jobname = line.split()
                configs.add(config)
                app_and_args = os.path.join( app, args )
                apps_and_args.add( app_and_args )
                specific_jobIds[ config + app_and_args ] = jobId

for app_and_args in apps_and_args:
    for config in configs:
        # now get the right output file
        output_dir = os.path.join(options.run_dir, app_and_args, config)
        if not os.path.isdir( output_dir ):
            print("WARNING the outputdir " + output_dir + " does not exist")
            continue
        
        if config + app_and_args in specific_jobIds:
            jobId = specific_jobIds[ config + app_and_args ]
            outfile = os.path.join(output_dir, app_and_args.replace("/", "-") + "." + "o" + jobId)
        else:
            all_outfiles = [os.path.join(output_dir, f) \
                           for f in os.listdir(output_dir) if(re.match(r'.*\.o[0-9]+',f))]
            outfile = max(all_outfiles, key=os.path.getmtime)

        stat_found = set()

        if not os.path.isfile( outfile ):
            print "WARNING - " + outfile + " does not exist"
            continue

        # Do a quick 100-line pass to get the GPGPU-Sim Version number
        MAX_LINES = 100
        count = 0
        for line in open(outfile).readlines():
            count += 1
            if count >= MAX_LINES:
                break
            build_match = re.match(".*\[build\s+(.*)\].*", line)
            if build_match:
                stat_map[app_and_args + config + "GPGPU-Sim-build"] = [build_match.group(1)]
                break


        # Only go up for 10000 lines looking for stuff
        MAX_LINES = 100000
        count = 0
        '''
        for stat_name, token in stats_to_pull.iteritems():
            if stat_name in stat_found:
                continue
            for line in open(outfile).readlines():
                existance_test = token.search(line.rstrip())
                if existance_test != None:
                    stat_found.add(stat_name)

            #existance_test = token.findall(open(outfile).readlines())
            #if len(existance_test) > 0:
            #    stat_found.add(stat_name)
            if len(stat_found) == len(stats_to_pull):
                break
        '''

        for line in open(outfile).readlines():
            #count += 1
            #if count >= MAX_LINES:
            #    break

            # pull out some stats
            for stat_name, token in stats_to_pull.iteritems():
                #if stat_name in stat_found:
                #    continue
                existance_test = token.search( line.rstrip() )
                #existance_test = token.findall( line.rstrip() )
                if existance_test != None:
                    stat_found.add(stat_name)
                    number = existance_test.group(1).strip()
                    if app_and_args + config + stat_name not in stat_map:
                        stat_map[app_and_args + config + stat_name] = []
                    stat_map[app_and_args + config + stat_name].append(number)
                    # stat_map[app_and_args + config + stat_name] = number
            #if len(stat_found) == len(stats_to_pull):
            #    break
        
# After collection, spew out the tables
DIVISION = "-" * 100
csv_str = ""

# Just adding this in here since it is a special case and is not parsed like 
# everything else, because you need to read from the beginning not the end
stats_to_pull["GPGPU-Sim-build"] = ""
for stat_name in stats_to_pull:
    csv_str += DIVISION + "\n"
    csv_str += stat_name + ","
    for config in configs:
        csv_str += config + ","
    csv_str += "\n"
    for appargs in apps_and_args:
        csv_str += appargs + ","
        times = max([len(stat_map[appargs + config + stat_name]) for config in configs if appargs + config + stat_name in stat_map]+[1])
        for config in configs:
            if appargs + config + stat_name in stat_map:
                csv_str += ",".join(stat_map[appargs + config + stat_name]) + ","
            else:
                csv_str += "NA,"*times
        csv_str += "\n"
    csv_str += "\n"

print csv_str
