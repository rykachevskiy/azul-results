# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 01:37:54 2016

@author: Anton Rykachevskiy
anton.rykachevskiy@yandex.ru
"""

import argparse

import os
import sys

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


PERCENTILES_SET = [50, 90, 99, 99.9, 99.99]
VERBOUSE = 0
OUTLIERS_TREASHOLD = 0.9
PLOT = False
HEADER_SIZE = 12


def parse_args(input_string=None):
    parser = argparse.ArgumentParser(description='Superscript.')

    parser.add_argument('-if',
                        nargs=2,
                        dest='input_folders',
                        default=None,
                        help='Two folders where data is strored, use space to separate them from each other.')

    parser.add_argument('-rq',
                        dest='required_name_part',
                        default='',
                        type=str,
                        help='Required string in the name of the file.')

    parser.add_argument('-bn',
                        dest='builds_names',
                        type=str,
                        nargs=2,
                        default=[None, None],
                        help='Name of builds, use space to separate one from another.')

    parser.add_argument('-v',
                        dest='verbouse',
                        type=int,
                        default=1,
                        help='Verbousity level, should be 0, 1, 2, 3,'
                             ' where 0 is for no information and 3 is all posible information.')

    parser.add_argument('-ot',
                        dest='outliers_treashold',
                        type=float,
                        default=1.0,
                        help='Set outliers treashold. 1.0 - no outliers, 0.0 - every point is an outlier')

    parser.add_argument('-p',
                        dest='plot',
                        action='store_true',
                        help='Plot percentile values.')

    parser.add_argument('-chp',
                        dest='percentiles_set',
                        type=float,
                        default=None,
                        nargs='*',
                        help='Change default percentile set.')

    parser.add_argument('-of',
                        dest='output_file',
                        type=str,
                        default=None,
                        help='Output file name with path.')

    parser.add_argument('-oi',
                        dest='output_image',
                        type=str,
                        default=None,
                        help='Output image name with path.')

    if input_string is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(input_string.split())

    return args


def check_folders(folders):
    return all([os.path.isdir(folder) for folder in folders])


def read_single(filename, filepath=None, fulfill_flag=True, header_size=HEADER_SIZE):
    """
    Function reads density from prepared file.
    Header size is 12 lines,
    in body each lines looks like tis:
    value, counts on current value
    """

    if filepath:
        if filepath[-1] == '/':
            filename = filepath + filename
        else:
            filename = filepath + '/' + filename

    f = open(filename, "r")
    lines = f.readlines()
    f.close()

    x = []
    pdf = []

    for line in lines[header_size:]:
        l = line.split(',')
        x_val = int(l[0])
        count = int(l[1])
        x.append(x_val)
        pdf.append(count)

    x_carret = 0
    if fulfill_flag:
        fulfilled_pdf = np.zeros(max(x))
        for i in range(max(x)):
            if i == x[x_carret]:
                fulfilled_pdf[i] = pdf[x_carret]
                x_carret += 1
        x = np.array(x)
        pdf = fulfilled_pdf

    return x, pdf.astype(float) / sum(pdf)


def strings_in_string(string_list, base_string):
    checks = [check_string in base_string for check_string in string_list]
    return all(checks)


def read_multiple(path, requirment=None, fulfill_flag=True, header_size=HEADER_SIZE, verbouse=False):
    pdfs = dict()

    for file_name in os.listdir(path):
        if (requirment is not None and strings_in_string(requirment, file_name)) or (requirment is None):
            x, curr_pdf = read_single(file_name, path, fulfill_flag=fulfill_flag, header_size=header_size)
            if fulfill_flag:
                pdfs[file_name] = curr_pdf
            else:
                pdfs[file_name] = x, curr_pdf

            if verbouse:
                print "loading : {0}".format(file_name)
        else:
            if verbouse:
                print "skipping : {0}".format(file_name)

    return pdfs


def percentiles_from_pdf(pdf, perc, strat='first_higher'):
    perc_normed = float(perc) / 100
    curr_perc = 0.0

    i = 0
    last_grow = 0
    while curr_perc < perc_normed and i < len(pdf):
        curr_perc += pdf[i]
        if pdf[i] > 0 and curr_perc < perc_normed:
            last_grow = i
        i += 1

    if curr_perc >= perc_normed:
        if strat == 'first_higher':
            return i
        else:
            return last_grow
    else:
        return -1


def calculate_perc(pdfs):
    percentiles_dict = dict()

    for perc in PERCENTILES_SET:
        percentiles_dict[perc] = dict()
        for run_name in pdfs:
            percentiles_dict[perc][run_name] = percentiles_from_pdf(pdfs[run_name], perc)

    return percentiles_dict


def drop_single_outliers(target_percentile_dict, treashold=1):
    cleared_percentiles_dict = dict()
    dropped_percentiles_dict = dict()

    mean = np.mean(target_percentile_dict.values())
    std =np.std(target_percentile_dict.values())
    for run_name in target_percentile_dict:
        interval = stats.norm.interval(treashold, mean, std)

        if target_percentile_dict[run_name] >= interval[0] and target_percentile_dict[run_name] <= interval[1]:
            cleared_percentiles_dict[run_name] = target_percentile_dict[run_name]
        else:
            dropped_percentiles_dict[run_name] = target_percentile_dict[run_name]

    if cleared_percentiles_dict == {}:
        raise ValueError('Treashold is too strong, so non of the percentile values fulfil it. Try to increase -ot')
    return cleared_percentiles_dict, dropped_percentiles_dict


def drop_all_outliers(percentiles_dict):
    cleared_percentiles_dict = dict()
    dropped_percentiles_dict = dict()

    for perc in PERCENTILES_SET:
        cleared_percentiles_dict[perc], dropped_percentiles_dict[perc] = drop_single_outliers(percentiles_dict[perc],
                                                                                              OUTLIERS_TREASHOLD)

    return cleared_percentiles_dict, dropped_percentiles_dict


def make_distributions(percentiles_dict):
    distributions_dict = dict()
    ks_tests_results_dict = dict()
    for perc in PERCENTILES_SET:
        mean = np.mean(percentiles_dict[perc].values())
        std = np.std(percentiles_dict[perc].values())

        normed_perc_values = [(perc_value - mean) / std for perc_value in
                              percentiles_dict[perc].values()]

        distributions_dict[perc] = stats.norm(mean, std)

        ks_tests_results_dict[perc] = stats.kstest(normed_perc_values, "norm")

    return distributions_dict, ks_tests_results_dict


def ks_tests(first_percentiles_dict, second_percentiles_dict):
    ks_tests_dict = dict()

    for perc in first_percentiles_dict:
        ks_tests_dict[perc] = stats.ks_2samp(first_percentiles_dict[perc].values(),
                                             second_percentiles_dict[perc].values())

    return ks_tests_dict


def print_percentiles_dict(percentiles_dict):
    for perc in PERCENTILES_SET:
        print "percentile value: {0}".format(perc)
        print percentiles_dict[perc].values()
        print "___"


def name_checker(first_all_data, second_all_data):
    if first_all_data['build_name'] is None:
        first_all_data['build_name'] = 'first folder'
    if second_all_data['build_name'] is None:
        second_all_data['build_name'] = 'second folder'


def print_results(first_all_data,
                  second_all_data,
                  ks_tests_dict,
                  output_file=None):
    name_checker(first_all_data, second_all_data)

    if not output_file is None:
        of = open(output_file, 'w')
        stdout_backup = sys.stdout
        sys.stdout = of

    for perc in PERCENTILES_SET:
        print "percentile value: {0}".format(perc)
        print "{0} mean and std: {1}, {2}".format(first_all_data['build_name'],
                                                  first_all_data['distributions_dict'][0][perc].mean(),
                                                  first_all_data['distributions_dict'][0][perc].std())
        print "{0} mean and std: {1}, {2}".format(second_all_data['build_name'],
                                                  second_all_data['distributions_dict'][0][perc].mean(),
                                                  second_all_data['distributions_dict'][0][perc].std())
        print "Probability of being drown from different distr.: {0}".format(1 - ks_tests_dict[perc][1])
        if VERBOUSE >= 2:
            print ""
            print "number of data points to compare: {0}, {1}".format(
                len(first_all_data['cleared_percentiles_dict'][perc].values()),
                len(second_all_data['cleared_percentiles_dict'][perc].values()))
            print "dropped runs names: {0}".format(first_all_data['dropped_percentiles_dict'][perc].keys())
            print "dropped runs names: {0}".format(second_all_data['dropped_percentiles_dict'][perc].keys())
            print "KS_values : {0}, {1}".format(first_all_data['distributions_dict'][1][perc][1],
                                                second_all_data['distributions_dict'][1][perc][1])
        print "---------------------------------------------------------------"

    if VERBOUSE >= 3:
        print "\n"
        print "{0} percentile values : ".format(first_all_data['build_name'])
        print_percentiles_dict(first_all_data['percentiles_dict'])
        print "\n"
        print "{0} percentile values : ".format(second_all_data['build_name'])
        print_percentiles_dict(second_all_data['percentiles_dict'])

    if not output_file is None:
        of.close()
        sys.stdout = stdout_backup


def plot_percentile_distr(ax, distributions_dict, percentiles_dict, perc, color=None):
    mean = distributions_dict[perc].mean()
    std = distributions_dict[perc].std()

    x_vals = np.linspace(mean - 3 * std, mean + 3 * std, 6 * std)
    y_vals = distributions_dict[perc].pdf(x_vals)

    line = ax.plot(x_vals, y_vals, color=color)
    ax.plot(percentiles_dict[perc].values(), [-max(y_vals) / 10 for _ in range(len(percentiles_dict[perc].values()))],
            'o', color=color)

    return line


def plot_all(first_all_data, second_all_data, output_file=None):
    name_checker(first_all_data, second_all_data)

    fig, axes = plt.subplots(nrows=len(PERCENTILES_SET), ncols=1)

    fig.tight_layout()

    first_lines = []
    second_lines = []
    for curr in range(len(PERCENTILES_SET)):
        line = plot_percentile_distr(axes[curr], first_all_data['distributions_dict'][0],
                                     first_all_data['cleared_percentiles_dict'], PERCENTILES_SET[curr],
                                     color='r')
        first_lines.append(line)
        line = plot_percentile_distr(axes[curr], second_all_data['distributions_dict'][0],
                                     second_all_data['cleared_percentiles_dict'], PERCENTILES_SET[curr],
                                     color='g')
        second_lines.append(line)
        axes[curr].set_xlabel('Perc : {0}'.format(PERCENTILES_SET[curr]))

    red_patch = mpatches.Patch(color='red', label=first_all_data['build_name'])
    green_patch = mpatches.Patch(color='green', label=second_all_data['build_name'])
    axes[0].legend(handles=[red_patch, green_patch], prop={'size': 10})

    if not output_file is None:
        fig.savefig(output_file)
    else:
        plt.show()


def prepare_all_data(args, folder_name, build_name):
    pdfs = read_multiple(folder_name, [args.required_name_part, '.rd'])

    percentiles_dict = calculate_perc(pdfs)
    cleared_percentiles_dict, dropped_percentiles_dict = drop_all_outliers(percentiles_dict)

    distributions_dict = make_distributions(cleared_percentiles_dict)

    return {'pdfs': pdfs,
            'percentiles_dict': percentiles_dict,
            'cleared_percentiles_dict': cleared_percentiles_dict,
            'dropped_percentiles_dict': dropped_percentiles_dict,
            'distributions_dict': distributions_dict,
            'build_name': build_name}


def whole_cycle(args):
    global PLOT
    global VERBOUSE
    global OUTLIERS_TREASHOLD
    global PERCENTILES_SET

    PLOT = args.plot
    VERBOUSE = args.verbouse
    OUTLIERS_TREASHOLD = args.outliers_treashold

    if not args.percentiles_set is None:
        PERCENTILES_SET = args.percentiles_set

    if not args.input_folders is None:
        if check_folders(args.input_folders):
            first_all_data = prepare_all_data(args, args.input_folders[0], args.builds_names[0])
            second_all_data = prepare_all_data(args, args.input_folders[1], args.builds_names[1])

            ks_test_resuts = ks_tests(first_all_data['cleared_percentiles_dict'],
                                      second_all_data['cleared_percentiles_dict'])

            if VERBOUSE >= 1:
                print_results(first_all_data, second_all_data, ks_test_resuts, None)

                if not args.output_file is None:
                    print_results(first_all_data, second_all_data, ks_test_resuts, args.output_file)
            else:
                if not args.output_file is None:
                    print_results(first_all_data, second_all_data, ks_test_resuts, args.output_file)


            if PLOT:
                plot_all(first_all_data, second_all_data, None)

            if args.output_image:
                plot_all(first_all_data, second_all_data, args.output_image)


if __name__ == "__main__":

    args = parse_args()
    whole_cycle(args)


