#!/usr/bin/python
import matplotlib.pyplot as plt
import numpy as np
# import matplotlib.lines as mlines
import matplotlib.ticker
from matplotlib.ticker import FormatStrFormatter
import argparse
import matplotlib.gridspec as gridspec
from plot.plotting_utilities import *
from matplotlib import colors
from cycler import cycler
import sys
import yaml
import re
import os

this_directory = os.path.dirname(os.path.realpath(__file__)) + "/"


parser = argparse.ArgumentParser(
    description='Plot the collected stats into a grid of subplots with one line ' +
    'per app.',
    usage='{} infile -o outfile'.format(sys.argv[0]))

parser.add_argument('-i', '--infile', action='store', type=str,
                    help='The input file that contains the data to plot.')

parser.add_argument('-o', '--outdir', action='store', type=str,
                    default='./', help='The directory to store the plots.')

parser.add_argument('-y', '--yamlfile', type=str,
                    default=this_directory+'plot_config.yml',
                    help='The yaml config file.')

parser.add_argument('-s', '--show', action='store_true',
                    help='Show the plots or save only.')

if __name__ == '__main__':
    # read cmd line options
    args = parser.parse_args()

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    # read yaml config file
    yc = yaml.load(open(args.yamlfile, 'r'))
    locyc = yc[sys.argv[0].split('/')[-1]]
    globyc = yc['global']

    # read input file to datadir
    datadir = {}
    data = np.genfromtxt(args.infile, delimiter='\t', dtype=str)
    header, data = data[0], data[1:]
    datadir = data_to_dir(header, data, ['metric', 'app_and_args', 'config'],
                          keep_only=['num_kernels', 'valuelist'])

    # generate the figdir, groups input data, ready to be plotted
    figdir = {}
    for metric in datadir.keys():
        if metric not in locyc['stats_to_plot']:
            continue
        if metric not in figdir:
            figdir[metric] = {}
        for app in datadir[metric].keys():
            for conf in datadir[metric][app].keys():
                matches = re.compile('([a-z]+)([0-9]*:?[0-9]*)').findall(conf)
                if not matches:
                    continue
                knob = ','.join([m[0] for m in matches])
                if knob not in locyc['knobs_to_plot']:
                    continue
                if knob not in figdir[metric]:
                    figdir[metric][knob] = {}
                if app not in figdir[metric][knob]:
                    figdir[metric][knob][app] = {'x': [], 'y': []}
                # x = ','.join(m[1].split(':')[0] for m in matches)
                x = float(matches[0][1].split(':')[0])
                y = float(datadir[metric][app][conf][1])
                figdir[metric][knob][app]['x'].append(x)
                figdir[metric][knob][app]['y'].append(y)

    # iterate over the figdir and plot
    for metric in figdir.keys():
        for knob in figdir[metric].keys():
            outdir = args.outdir + '/' + globyc['knobs'][knob]
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            fig = plt.figure(
                figsize=(locyc['figsize']['w'], locyc['figsize']['h']))
            fig.suptitle('Knob:{}, Stat:{}'.format(globyc['knobs'][knob],
                                                   globyc['stat_shorts'][metric]))
            outfile = '{}/{}-{}.jpeg'.format(outdir,
                                             globyc['stat_shorts'][metric],
                                             globyc['knobs'][knob])
            rows = locyc['grid']['rows']
            cols = locyc['grid']['columns']
            gs = gridspec.GridSpec(rows, cols)
            idx = 0
            for app in figdir[metric][knob].keys():
                x = np.array(figdir[metric][knob][app]['x'])
                y = np.array(figdir[metric][knob][app]['y'])
                app = app.split('/')[0]
                indices = [i[0]
                           for i in sorted(enumerate(x), key=lambda a:a[1])]
                x, y = x[indices], y[indices]
                # ax.set_title(app)
                ax = plt.subplot(gs[idx//cols, idx % cols])
                # if idx%cols == 0:
                #     ax.set_ylabel(metric)
                # if idx//cols == rows-1:
                #     ax.set_xlabel(knob)
                y = y / y[0]
                ax.plot(x, y, label=globyc['bench_shorts']
                        [app], marker=locyc['marker'])
                ax.legend(**locyc['legend'])
                ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(
                    nbins=locyc['nticks']['y'], integer=True))
                ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(
                    nbins=locyc['nticks']['x'], integer=True))
                ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
                # ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
                # ax2.yaxis.set_major_locator(matplotlib.ticker.LinearLocator(nticks))
                idx += 1
            plt.tight_layout()
            plt.subplots_adjust(wspace=0.3, hspace=0.15, top=0.95)
            save_and_crop(fig, outfile, dpi=600, bbox_inches='tight')
            if args.show:
                plt.show()
            plt.close()

    # plt.legend(loc='best', fancybox=True, fontsize='11')
    # plt.axvline(700.0, color='k', linestyle='--', linewidth=1.5)
    # plt.axvline(1350.0, color='k', linestyle='--', linewidth=1.5)
    # plt.annotate('Light\nCombine\nWorkload', xy=(
    #     200, 6.3), textcoords='data', size='16')
    # plt.annotate('Moderate\nCombine\nWorkload', xy=(
    #     800, 6.3), textcoords='data', size='16')
    # plt.annotate('Heavy\nCombine\nWorkload', xy=(
    #     1400, 8.2), textcoords='data', size='16')
