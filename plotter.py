# -*- coding: utf-8 -*-
"""
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
from matplotlib.colors import BoundaryNorm
from comparer import read_single, read_multiple, name_checker, check_folders, strings_in_string, percentiles_from_pdf

MAX_PERCENTILE = 99
COEFFICIENT = 1.2


def parse_args(input_string=None):
    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('-if',
                        nargs='*',
                        dest='input_folders',
                        help='Folders where data is stored, use space to separate them from each other.')

    parser.add_argument('-rq',
                        dest='required_name_part',
                        type=str,
                        default = '',
                        help='Required string in the names of the all files.')

    parser.add_argument('-bn',
                        dest='builds_names',
                        type=str,
                        nargs='*',
                        default= [],
                        help='Name of builds, use space to separate one from another. Should be the same amount as input folders')

    parser.add_argument('-oi',
                        dest='output_image',
                        type=str,
                        default=None,
                        help='Output image name with path.')

    parser.add_argument('-al',
                        dest='axes_limits',
                        type=float,
                        nargs=4,
                        default=None,
                        help='Axes limits.')

    parser.add_argument('-aa',
                        dest='auto_axes_limits',
                        default = False,
                        action='store_true',
                        help='Set axes limits automaticly. X is 0 to 99tile, Y is 0 to 1.2*max'
                        )

    parser.add_argument('-p',
                        dest='plot',
                        action='store_true',
                        help='Plot in external window.')

    if input_string is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(input_string.split())

    return args


def plot_single(ax, pdfs, color):
    for pdf in pdfs.values():
        ax.plot(pdf, color = color)


def plot_all(all_data, axes_limits=None, output_image=None):
    fig = plt.figure()
    ax = fig.add_subplot('111')

    if axes_limits == 'auto':
        x_max = COEFFICIENT * min(map(lambda x : percentiles_from_pdf(x, MAX_PERCENTILE) , np.hstack(pdfs.values() for pdfs in all_data.values())))
        y_max = COEFFICIENT * (max(np.hstack(np.hstack(pdfs.values() for pdfs in all_data.values()))))
        axes_limits = [0, x_max, 0, y_max]
    elif not axes_limits is None:
        axes_limits = axes_limits

    if not axes_limits is None:
        ax.axis(axes_limits)
        ax = plt.gca()
        ax.set_autoscale_on(False)

    cmap = plt.get_cmap('cool')
    colors = cmap(np.linspace(0, 1, len(all_data.keys())))
    clr = {all_data.keys()[i]: colors[i] for i in range(len(all_data.keys()))}

    patches = []
    for build_name in all_data:
        plot_single(ax, all_data[build_name], clr[build_name])
        patches.append(mpatches.Patch(color=clr[build_name], label=build_name))

    ax.legend(handles=patches, prop={'size': 10})

    ax.set_xlabel('Latency, microseconds')
    ax.set_ylabel('Percentage')
    if output_image is None:
        plt.show(fig)
    else:
        fig.savefig(output_image)


def whole_cycle(args):

    all_data = dict()

    for i in range(abs(len(args.builds_names) - len(args.input_folders))):
        args.builds_names.append('build {0}'.format(i))

    for folder_name, build_name in zip(args.input_folders, args.builds_names):
        pdfs = read_multiple(folder_name, [args.required_name_part, '.rd'])
        all_data[build_name] = pdfs

    if args.auto_axes_limits:
        axes_limits = 'auto'
    else:
        axes_limits = args.axes_limits

    if args.plot:
        plot_all(all_data, axes_limits=axes_limits)
    if args.output_image:
        plot_all(all_data, axes_limits=axes_limits, output_image=args.output_image)



if __name__ == '__main__':
    args = parse_args()
    whole_cycle(args)
