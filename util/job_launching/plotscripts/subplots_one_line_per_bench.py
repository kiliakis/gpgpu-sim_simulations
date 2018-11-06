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

    args.outdir = '{}/{}/'.format(args.outdir,
                                  args.infile.split('stats-')[1].split('.csv')[0])
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
    bench_suite = ''
    for metric in datadir.keys():
        if metric not in locyc['stats_to_plot']:
            continue
        if metric not in figdir:
            figdir[metric] = {}
        for app in datadir[metric].keys():
            if 'sdk-4.1.15' in app:
                bench_suite = 'sdk'
            elif 'ispass2009-1.0' in app:
                bench_suite = 'ispass'
            elif 'rodinia-2.0-ft' in app:
                bench_suite = 'rodinia'
            elif 'parboil-0.2' in app:
                bench_suite = 'parboil'
            else:
                print('Benchmark suite {} not recognized.')
                exit(-1)
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

                # Only using the first knob
                x = float(matches[0][1].split(':')[0])
                y = float(datadir[metric][app][conf][1])
                if not np.isnan(y):
                    figdir[metric][knob][app]['x'].append(x)
                    figdir[metric][knob][app]['y'].append(y)

    # iterate over the figdir and plot
    for metric in figdir.keys():
        for knob in figdir[metric].keys():
            # Only using the first knob
            knob1 = knob.split(',')[0]
            outdir = args.outdir + '/' + globyc['knobs'][knob1]
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            rows = locyc[bench_suite]['grid']['rows']
            cols = locyc[bench_suite]['grid']['columns']
            figsize = (2. * cols, 2.*rows)
            fig = plt.figure(figsize=figsize)
            fig.suptitle('Knob:{}, Stat:{}'.format(globyc['knobs'][knob1],
                                                   globyc['stat_shorts'][metric]))
            outfile = '{}/{}-{}.jpeg'.format(outdir,
                                             globyc['stat_shorts'][metric],
                                             globyc['knobs'][knob1])
            gs = gridspec.GridSpec(rows, cols)
            idx = 0
            yavg_l = []
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
                if len(y) == 0:
                    print('Empty values for {}:{}:{}'.format(metric, knob, app))
                    continue
                y = y / y[0]
                yavg_l.append((x, y))
                ax.plot(x, y, label=globyc['bench_shorts']
                        [app], marker=locyc['marker'])
                ax.legend(**locyc['legend'])
                ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(
                    nbins=locyc['nticks']['y'], integer=True))
                ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(
                    nbins=locyc['nticks']['x'], integer=True))
                ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
                plt.xticks(**locyc['ticks']['x'])
                plt.yticks(**locyc['ticks']['y'])
                # ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
                # ax2.yaxis.set_major_locator(matplotlib.ticker.LinearLocator(nticks))
                idx += 1
            # Plot the average
            x = set()
            for d in yavg_l:
                x |= set(d[0])
            x = list(x)
            y = np.zeros(len(x))
            ynum = np.zeros(len(x))
            for d in yavg_l:
                for i in range(len(d[0])):
                    y[x.index(d[0][i])] += d[1][i]
                    ynum[x.index(d[0][i])] += 1
            y /= ynum
            ax = plt.subplot(gs[idx//cols, idx % cols])
            ax.plot(x, y, label=globyc['bench_shorts']
                    ['average'], marker=locyc['marker'])
            ax.legend(**locyc['legend'])
            ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(
                nbins=locyc['nticks']['y'], integer=True))
            ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(
                nbins=locyc['nticks']['x'], integer=True))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
            plt.xticks(**locyc['ticks']['x'])
            plt.yticks(**locyc['ticks']['y'])
            # end plot the average

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
