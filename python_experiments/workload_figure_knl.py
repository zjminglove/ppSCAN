import os, re, decimal
from functools import partial

import matplotlib.pyplot as plt

# 1st: same
edge_tag = 'num of edges'
prune0_tag = 'prune0 definitely not reachable'
prune1_tag = 'prune1 definitely reachable'

# 2nd: different
intersect_tag = 'intersection times'
cmp0_tag = 'cmp0'
cmp1_tag = 'cmp1'
cmp_equ_tag = 'equal cmp'
runtime_tag = 'Total time without IO'

# suffix
pscan_tag = ', pscan'
pscan_plus_tag = ', pscan+'


def format_str(float_num):
    return str(decimal.Decimal.from_float(float_num).quantize(decimal.Decimal('0.000')))


def filter_lines_by_tag(tag, lines):
    return map(lambda my_str: eval(my_str.split(':')[-1].replace('ms', '')),
               filter(lambda line: tag in line, lines))


def get_workload_statistics(dataset, eps, min_pts, root_dir_path='.'):
    file_path = os.sep.join([root_dir_path, dataset, 'eps-' + str(eps), 'min_pts-' + str(min_pts),
                             '-'.join(['output', dataset, str(eps), str(min_pts)]) + '.txt'])
    with open(file_path) as ifs:
        lines = ifs.readlines()

    # runtime unit: ms
    runtime_lst = map(lambda time_str: eval(time_str.split('ms')[0]) if 'ms' in time_str else eval(time_str) / 1000,
                      map(lambda my_str: my_str.split(':')[-1], filter(lambda line: runtime_tag in line, lines)))

    # 2nd: different
    ret_dict = {runtime_tag + pscan_tag: runtime_lst[0]}
    return ret_dict


def case_study_fix_eps_min_pts(data_set_lst, eps, min_pts, root_dir_path='.'):
    for data_set in data_set_lst:
        ret_dict = get_workload_statistics(data_set, eps, min_pts, root_dir_path)
        print ret_dict


# tags for figure drawing, legends
display_pscan_runtime_tag = 'serial pscan runtime'
display_pscan_plus_runtime_tag = 'serial pscan+ runtime'

display_pscan_eval_tag = 'pscan eval number'
display_pscan_plus_eval_tag = 'pscan+ eval number'
display_prune0_tag = prune0_tag
display_prune1_tag = prune1_tag


def min_runtime(statistics_dict_lst):
    pscan_runtime_lst = map(lambda statistics_dict: statistics_dict[runtime_tag + pscan_tag], statistics_dict_lst)
    pscan_plus_runtime_lst = map(lambda statistics_dict: statistics_dict[runtime_tag + pscan_plus_tag],
                                 statistics_dict_lst)
    return min(min(pscan_plus_runtime_lst, pscan_runtime_lst))


def to_display_dict(statistics_dict, min_runtime_val):
    keys = [display_prune0_tag, display_prune1_tag, display_pscan_eval_tag, display_pscan_plus_eval_tag]
    values = map(lambda value: float(value * 2) / statistics_dict[edge_tag],
                 [statistics_dict[prune0_tag], statistics_dict[prune1_tag],
                  statistics_dict[intersect_tag + pscan_tag], statistics_dict[intersect_tag + pscan_plus_tag]])
    display_dict = dict(zip(keys, values))

    display_dict[display_pscan_runtime_tag] = float(statistics_dict[runtime_tag + pscan_tag]) / min_runtime_val
    display_dict[display_pscan_plus_runtime_tag] = float(
        statistics_dict[runtime_tag + pscan_plus_tag]) / min_runtime_val
    return display_dict


def display_workload_runtime(eps_lst, display_lst, title_append_txt='', is_display_naive=False):
    tag_list = [display_pscan_plus_eval_tag, display_pscan_eval_tag,
                display_prune0_tag, display_prune1_tag]

    # draw after get data, with partial binding technique
    shape_color_lst = ['g^-', 'rs-', 'c<-', 'y>-', 'mx-', 'k--']

    result_lst = map(lambda tag:
                     map(lambda display: display[tag], display_lst), tag_list)
    if is_display_naive:
        shape_color_lst = ['b.-', 'g^-', 'rs-', 'c<-', 'y>-', 'mx-', 'k--']
        result_lst = [map(lambda my_pair: 1 - my_pair[0] - my_pair[1],
                          zip(result_lst[-1], result_lst[-2]))] + result_lst

    prev_partial_func = plt.plot
    cur_shape_color_idx = 0
    for portion_lst in result_lst:
        # partially bind parameters
        prev_partial_func = partial(prev_partial_func, eps_lst, portion_lst,
                                    shape_color_lst[cur_shape_color_idx])
        cur_shape_color_idx += 1
    prev_partial_func()

    plt.legend(['max eval number'] + tag_list)
    font = {'family': 'serif', 'color': 'darkred', 'weight': 'normal', 'size': 12, }
    plt.title('Workload portion\n' + title_append_txt
              if title_append_txt != '' else 'Workload portion', fontdict=font)
    plt.xlabel('eps', fontdict=font)
    plt.ylabel('portion', fontdict=font)
    plt.ylim([0.0, 1.1])
    plt.savefig(local_folder + os.sep + title_append_txt.replace(' ', '') + '-' + 'workload.png',
                bbox_inches='tight', pad_inches=0, transparent=True)

    table_rows = [' | '.join(['tag'] + map(lambda eps_val: 'eps-' + str(eps_val), eps_lst)),
                  ' | '.join(['---' for _ in xrange(len(eps_lst) + 1)]),
                  ' | '.join([display_prune0_tag] + map(format_str, result_lst[-2])),
                  ' | '.join([display_prune1_tag] + map(format_str, result_lst[-1])),
                  ' | '.join(['max eval number'] + map(format_str, result_lst[0])),
                  ' | '.join([display_pscan_eval_tag] + map(format_str, result_lst[2])),
                  ' | '.join([display_pscan_plus_eval_tag] + map(format_str, result_lst[1]))]

    plt.close()
    return '\n'.join(table_rows)


def display_runtime(eps_lst, display_lst, title_append_txt=''):
    tag_list = [display_pscan_plus_runtime_tag, display_pscan_runtime_tag]

    # draw after get data, with partial binding technique
    shape_color_lst = ['mx-', 'k--']
    prev_partial_func = plt.plot
    cur_shape_color_idx = 0

    result_lst = map(lambda tag:
                     map(lambda display: display[tag], display_lst), tag_list)

    for portion_lst in result_lst:
        # partially bind parameters
        prev_partial_func = partial(prev_partial_func, eps_lst, portion_lst,
                                    shape_color_lst[cur_shape_color_idx])
        cur_shape_color_idx += 1
    prev_partial_func()

    plt.legend(tag_list)
    font = {'family': 'serif', 'color': 'darkred', 'weight': 'normal', 'size': 12, }
    plt.title('Runtime\n' + title_append_txt
              if title_append_txt != '' else 'Runtime', fontdict=font)
    plt.xlabel('eps', fontdict=font)
    plt.ylabel('time (s)', fontdict=font)

    max_val = max(max(result_lst[0]), max(result_lst[1]))
    plt.ylim([0.0, max_val * 1.1])
    plt.savefig(local_folder + os.sep + title_append_txt.replace(' ', '') + '-' + 'runtime.png',
                bbox_inches='tight', pad_inches=0, transparent=True)
    # plt.show()
    plt.close()

    table_rows = [' | '.join([display_pscan_runtime_tag] + map(format_str, result_lst[1])),
                  ' | '.join([display_pscan_plus_runtime_tag] + map(format_str, result_lst[0])), ]
    return '\n'.join(table_rows)


def case_study0():
    # case study 0
    eps = 0.3
    min_pts = 5
    root_dir_path = server_folder
    case_study_fix_eps_min_pts(data_set_lst, eps, min_pts, root_dir_path)
    print


def case_study1(min_pts=5, file_name='ReadMe.md'):
    # case study 1
    root_dir_path = server_folder

    with open(markdown_folder + os.sep + file_name, 'w') as ofs:
        parameter_eps_lst = [float(i + 1) / 10 for i in xrange(9)]
        for data_set in data_set_lst:
            statistics_lst = map(lambda eps: get_workload_statistics(data_set, eps, min_pts, root_dir_path),
                                 parameter_eps_lst)
            display_lst = map(lambda statistics_dict: to_display_dict(statistics_dict, 1000), statistics_lst)
            append_txt = ' - '.join([data_set, 'min_pts:' + str(min_pts)])
            table_lines = display_workload_runtime(parameter_eps_lst, display_lst, title_append_txt=append_txt,
                                                   is_display_naive=True)
            runtime_rows = display_runtime(parameter_eps_lst, display_lst, title_append_txt=append_txt)

            lines = ['## ' + data_set]

            def get_link():
                workload_link = local_folder.replace('.', '../..') + os.sep + append_txt.replace(' ',
                                                                                                 '') + '-' + 'workload.png'
                runtime_link = local_folder.replace('.', '../..') + os.sep + append_txt.replace(' ',
                                                                                                '') + '-' + 'runtime.png'
                return ' | '.join(['![' + data_set + '-workload](' + workload_link + ')',
                                   '![' + data_set + '-runtime](' + runtime_link + ')'])

            lines.append('\n'.join(['workload | runtime\n--- | ---', get_link()]))
            lines.append('\n'.join([table_lines, runtime_rows]))
            ofs.write('\n\n'.join(lines) + '\n\n')


if __name__ == '__main__':
    server_folder = '/mnt/mount-gpu/d2/yche/projects/python_experiments/workload-work-efficient-2'
    local_folder = './figures/' + 'workload-efficient'
    markdown_folder = 'case_studies/figures-case-study12-workload-efficient-2'
    os.system('mkdir -p ' + local_folder)
    os.system('mkdir -p ' + markdown_folder)

    data_set_lst = ['small_snap_dblp',
                    'snap_pokec', 'snap_livejournal', 'snap_orkut',
                    'webgraph_uk', 'webgraph_webbase',
                    'webgraph_twitter',
                    #  'snap_friendster',
                    '10million_avgdeg15_maxdeg50_Cdefault'
                    ]

    case_study0()

    min_pts_lst = [25, 50]
    for min_pts in min_pts_lst:
        case_study1(min_pts=min_pts, file_name='ReadMe' + '-' + str(min_pts) + '.md')
