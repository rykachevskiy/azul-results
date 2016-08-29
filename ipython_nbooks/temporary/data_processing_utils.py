import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

def density_from_sample(sample, density=True):
    limit = round(max(sample) + 1)
    return np.histogram(sample, bins=limit,
                        density=density, range=(0, limit))


def sample_from_density(pdfs,
                        sample_size=1000,
                        scaling=False,
                        noisy=False,
                        noise_scale=1.0):

    #TODO: make normal check for itterable
    #TODO: add warning on scaling
    if type(pdfs[0]) != np.ndarray and type(pdfs[0]) != list:
        pdfs = [pdfs]

    sample = np.empty(0)
    for pdf in pdfs:
        if scaling:
            pdf = pdf / sum(pdf)
        current_sample = np.random.choice(range(len(pdf)), sample_size / len(pdfs), p=pdf)
        sample = np.hstack((sample, current_sample))

    return sample


def search_boarders(density, bw, curr_position):
    left_boarder = curr_position
    right_boarder = curr_position

    if bw % 2 == 0:
        bw += 1

    right_saturation = (bw - 1) / 2
    left_saturation = (bw - 1) / 2

    while left_saturation > 0 and left_boarder > 0:
        if density[left_boarder] > 0:
            left_saturation -= 1
        left_boarder -= 1

    while right_saturation > 0 and right_boarder < len(density) - 1:
        if density[right_boarder] > 0:
            right_saturation -= 1
        right_boarder += 1

    if right_saturation == 0 and left_saturation == 0:
        return left_boarder, right_boarder
    elif right_saturation == 0 and left_saturation != 0:
        return max(0, right_boarder - curr_position), right_boarder
    elif left_saturation == 0 and right_saturation != 0:
        return left_boarder, curr_position + curr_position - left_boarder
    else:
        return 0, len(density)


def smooth_density(density, bw = 5, shall_pass = False):
    if shall_pass:
        return density
    else:
        new_density = np.zeros(len(density)*2)

        for i in range(len(density)):
            if density[i] == 0:
                pass
            else:
                left_boarder, right_boarder = search_boarders(density, bw, i)
                for j in range(left_boarder, right_boarder):
                    new_density[j] += density[i] / (right_boarder - left_boarder)

        return new_density


def bootstrap(pdfs,
              statistics_set,
              stat_sample_size=100,
              sample_size=1000,
              scaling=False,
              noisy=False):

    ##TODO: make normal check for iterable statistics set
    ##TODO ad warning on scaling

    statistics_vals = dict()
    for j in range(len(statistics_set)):
            statistics_vals[statistics_set[j]] = []

    for i in range(stat_sample_size):
        sample = sample_from_density(pdfs, sample_size, scaling=scaling)
        for j in range(len(statistics_set)):
            statistics_vals[statistics_set[j]].append(statistics_set[j].on_sample(sample))

    return statistics_vals


def __check__():
    print "works fine"


def plot_density(densities, log_flag=False, height=4, width=12, left=None, right=None, axes_limits=None,
                 colors=None, name=None):

    if type(densities[0]) != list and type(densities[0]) != np.ndarray:
        densities = [densities]
    fig = plt.figure(figsize=(width, height))
    ax = fig.add_subplot(1,1,1)

    if axes_limits:
        ax.axis(axes_limits)
        ax = plt.gca()
        ax.set_autoscale_on(False)

    if left is None:
        left = 0
    if right is None:
        right = len(densities[0])

    for i in range(len(densities)):
        density = densities[i]
        if colors is None:
            ax.plot(density[left:right])
        else:
            ax.plot(density[left:right], colors[i])

    if not name is None:
        fig.savefig(name)
    if log_flag:
        ax.set_xscale('log')
        ax.set_yscale('log')
    plt.show()


def read_single(filename, filepath=None, fulfill_flag=True, header_size=12):
    """
    :param filename:
    :param filepath:
    :param fulfill_flag:
    :return:

    Function reads density from prepared file.
    Header size is 12 lines,
    in body each lines looks like tis:
    value, counts on current value
    """

    if filepath:
        filename = filepath + filename

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


def __strings_in_string(string_list, base_string):
    checks = [check_string in base_string for check_string in string_list]
    return all(checks)


def read_multiple(path, marks=None, fulfill_flag=True, header_size=12, verbouse = False):
    pdfs = dict()

    for file_name in os.listdir(path):
        if (marks is not None and __strings_in_string(marks, file_name)) or (marks is None):
            x, curr_pdf = read_single(file_name, path, fulfill_flag=fulfill_flag, header_size=header_size)
            if fulfill_flag:
                pdfs[file_name] = (curr_pdf)
            else:
                pdfs[file_name] = ((x, curr_pdf))

            if verbouse:
                print "loading : {0}".format(file_name)
        else:
            if verbouse:
                print "skipping : {0}".format(file_name)

    return pdfs


def pdf_percentile(pdf, perc, strat='first_higher'):
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
