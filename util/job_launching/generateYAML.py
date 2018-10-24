import yaml
import numpy as np
import sys
import argparse
import collections

parser = argparse.ArgumentParser(description='Generate the YAML configuration file.',
                                 usage='python ' + sys.argv[0] + ' -o [outfile]')

parser.add_argument('-o', '--outfile', type=str, default='config.yml',
                    help='The output file name.'
                    ' Default: config.yml')


def cartesianProduct(inlist):
    data = []
    for entry in inlist:
        for param, values in entry.iteritems():
            if len(data) == 0:
                data = [('{} {}'.format(param, x),
                         '{}{}'.format(shortName[param], x))
                        for x in values]
            else:
                data = [('{} {} {}'.format(t1[0], param, t2),
                        '{}_{}{}'.format(t1[1], shortName[param], t2))
                        for t1 in data for t2 in values]
    return data


shortName = {
    '-gpgpu_n_clusters': 'cl',
    '-gpgpu_n_cores_per_cluster': 'cpcl',
}

configs = {
    'base_file': '$GPGPUSIM_ROOT/configs/GTX480/gpgpusim.config',
    'extra_params': [{
        '-gpgpu_n_clusters': [5, 10, 15],
        '-gpgpu_n_cores_per_cluster': [1, 2, 4],
        # '-gpgpu_n_cores': [1, 2, 4]
    }],
    'extra_params_exclude': [{
        '-gpgpu_n_clusters': [15],
        '-gpgpu_n_cores_per_cluster': [2, 4]
    }],
    # 'extra_params_include': [],
}

if __name__ == '__main__':
    args = parser.parse_args()
    yamlfile = args.outfile

    # generate all combinations
    data = cartesianProduct(configs['extra_params'])
    
    # remove the exclude configurations
    to_exclude = cartesianProduct(configs['extra_params_exclude'])
    data = list(set(data) - set(to_exclude))


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
    with open(yamlfile, 'w') as f:
        yaml.dump(dic, f, default_flow_style=False)

