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
        # for dic in entry:        
        tempdata = []
        for param, values in entry.iteritems():
            if len(tempdata) == 0:
                tempdata = [('{} {}'.format(param, x),
                         '{}{}'.format(shortName[param], x))
                        for x in values]
            else:
                tempdata = [('{} {} {}'.format(t1[0], param, t2),
                         '{}_{}{}'.format(t1[1], shortName[param], t2))
                        for t1 in tempdata for t2 in values]
        data += tempdata
    return data


shortName = {
    '-gpgpu_max_insn_issue_per_warp': 'mxiipw',
    '-gpgpu_num_sched_per_core': 'nspc',
    '-gpgpu_shader_core_pipeline': 'scp',
    '-gpgpu_shader_registers': 'sr',
    '-gpgpu_shader_cta': 'sc',
    '-gpgpu_num_reg_banks': 'nrb',
    '-gpgpu_shmem_num_banks': 'snb', 
    '-gpgpu_shmem_size': 'ss',
    '-gpgpu_n_clusters': 'nc',
    '-gpgpu_n_cores_per_cluster': 'ncpc',
    '-gpgpu_operand_collector_num_units_sp': 'ocnusp',
    '-gpgpu_operand_collector_num_units_sfu': 'ocnusfu',
    '-gpgpu_operand_collector_num_units_mem': 'ocnum',
    '-gpgpu_operand_collector_num_in_ports_sp': 'ocnipsp',
    '-gpgpu_operand_collector_num_in_ports_sfu': 'ocnipsfu',
    '-gpgpu_operand_collector_num_in_ports_mem': 'ocnipm',
    '-gpgpu_operand_collector_num_out_ports_sp': 'ocnopsp',
    '-gpgpu_operand_collector_num_out_ports_sfu': 'ocnopsfu',
    '-gpgpu_operand_collector_num_out_ports_mem': 'ocnopm',
    '-gpgpu_num_sp_units': 'nspu',
    '-gpgpu_num_sfu_units': 'nsfu',
    '-gpgpu_num_mem_units': 'nmu',
    '-gpgpu_cache:dl1': 'cdl1',
    '-gpgpu_cache:dl2': 'cdl2',
}

configs = {
    'base_file': '$GPGPUSIM_ROOT/configs/GTX480/gpgpusim.config',
    'extra_params': [
        {'-gpgpu_max_insn_issue_per_warp': [1, 2, 3, 4, 5]},
        {'-gpgpu_num_sched_per_core': [1, 2, 3, 4, 5]},
        {'-gpgpu_shader_core_pipeline': ['256:32', '512:32', '768:32', '1024:32', '1280:32', '1536:32', '1792:32', '2048:32']},
        {'-gpgpu_shader_registers': [16384, 24576, 32768, 49152, 65536, 98304, 131072]},
        {'-gpgpu_shader_cta': [4, 6, 8, 10, 12, 14]},
        #{'-gpgpu_num_reg_banks': [8, 16, 24, 32, 48, 64]},
        {'-gpgpu_shmem_num_banks': [16, 24, 32, 48, 64]},
        {'-gpgpu_shmem_size': [16384, 24576, 32768, 49152, 65536, 81920]},
        #{'-gpgpu_n_clusters': [10, 12, 14, 16, 18, 20]},
        # {'-gpgpu_n_cores_per_cluster': [1, 2, 4, 6, 8]},
        # {'-gpgpu_operand_collector_num_units_sp': [6]},
        # {'-gpgpu_operand_collector_num_units_sfu': [8]},
        # {'-gpgpu_operand_collector_num_units_mem': [2]},
        # {'-gpgpu_operand_collector_num_in_ports_sp': [2]},
        # {'-gpgpu_operand_collector_num_in_ports_sfu': [2]},
        # {'-gpgpu_operand_collector_num_in_ports_mem': [1]},
        # {'-gpgpu_operand_collector_num_out_ports_sp': [2]},
        # {'-gpgpu_operand_collector_num_out_ports_sfu': [1]},
        # {'-gpgpu_operand_collector_num_out_ports_mem': [1]},
        {'-gpgpu_num_sp_units': [1, 2, 3, 4, 5, 6]},
        {'-gpgpu_num_sfu_units': [1, 2, 3, 4, 5, 6]},
        {'-gpgpu_num_mem_units': [1, 2, 3, 4, 5, 6]},
        # {'-gpgpu_pipeline_widths': ['2,0,1,1,2,0,1,1,2']},
        # {'-gpgpu_cache:dl1': [32:128:4,L:L:m:N:H,A:32:8,8]},
        # {'-gpgpu_cache:dl2': [64:128:8,L:B:m:W:L,A:32:4,4:0,32]},
    ],
    'extra_params_exclude': [{}],
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
