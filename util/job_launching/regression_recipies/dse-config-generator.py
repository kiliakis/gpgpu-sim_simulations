import yaml
import numpy as np
import sys
import argparse
import collections
from cycler import cycle

parser = argparse.ArgumentParser(description='Generate the YAML configuration file.',
                                 usage='python ' + sys.argv[0] + ' -o [outfile]')

parser.add_argument('-o', '--outfile', type=str, default='dse-config-output.yml',
                    help='The output file name.')


parser.add_argument('-i', '--infile', type=str, default='dse-config-input.yml',
                    help='The output file name.')

def nocommas(x):
    return str(x).replace(',','')

def cartesianProduct(inlist):
    data = []
    if not inlist:
        return data

    for entry in inlist:
        tempdata = []
        for param, values in entry.items():
            if len(tempdata) == 0:
                tempdata = [('{} {}'.format(param, x),
                             '{}{}'.format(shortNames[param], nocommas(x)))
                            for x in values]
            else:
                tempdata = [('{} {} {}'.format(t1[0], param, t2),
                             '{}_{}{}'.format(t1[1], shortNames[param], nocommas(t2)))
                            for t1 in tempdata for t2 in values]
        data += tempdata
    return data


def dotProduct(inlist):
    data = []
    if not inlist:
        return data

    for entry in inlist:
        tempdata = []
        for param, values in entry.items():
            if len(tempdata) == 0:
                tempdata = [('{} {}'.format(param, x),
                             '{}{}'.format(shortNames[param], nocommas(x)))
                            for x in values]
            else:
                tempdata = [('{} {} {}'.format(t1[0], param, t2),
                             '{}_{}{}'.format(t1[1], shortNames[param], nocommas(t2)))
                            for t1, t2 in zip(tempdata, cycle(values))]
        data += tempdata
    return data


def add_params(data, base_params):
    for i, d in enumerate(data):
        for k, v in base_params.items():
            data[i] = ('{} {} {}'.format(d[0], k, v),
                       d[1])
            # '{}_{}{}'.format(d[1], shortNames[k], v))


if __name__ == '__main__':
    args = parser.parse_args()

    with open(args.infile, 'r') as f:
        inconfig = yaml.load(f)

    shortNames = inconfig['shortNames']
    configs = inconfig['configs']

    data = set(dotProduct(configs['unique_params']))

    # generate all combinations
    data |= set(cartesianProduct(configs['loop_params']))

    # remove the exclude configurations
    data -= set(cartesianProduct(configs['exclude_loop_params']))

    data = list(data)
    add_params(data, configs['base_params'])

    # generate the dictionary
    dic = {}
    dic['run'] = []

    for conf in data:
        dic['run'].append(conf[1])
        dic[conf[1]] = {
            'base_file': configs['base_file'],
            'extra_params': conf[0]
        }

    # generate yaml
    with open(args.outfile, 'w') as f:
        yaml.dump(dic, f, default_flow_style=False)
