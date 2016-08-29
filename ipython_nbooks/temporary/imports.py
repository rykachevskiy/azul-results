import pandas as pd
import numpy as np
import distribution_generator as dg
from scipy import stats
import matplotlib.pyplot as plt
from random import lognormvariate, normalvariate

from sklearn.neighbors import KernelDensity



def Density(sample, scale = 1):
    #works only with positive vals
    scaled_sample = [i * scale for i in sample]
    density = [0 for i in range(int(max(scaled_sample)) + 2)]
    for t in scaled_sample:
        density[int(t)] += 1
    return density

def Distribution(sample):
    density = Density(sample)
    distribution = []
    summ = 0
    for i in range(len(density)):
        summ += density[i]
        distribution.append(summ)
        
    return np.array(distribution, 'float64')

def sampleFromDensity(density, sample_size = None):
    if sample_size == None:
         sample_size = sum(density)
    resized_density = (density * sample_size / sum(density)).astype('int')

    sample = [0 for i in range(sum(resized_density))]
    current = 0
    value = 0
    for value in range(len(resized_density)):
        for i in range(resized_density[value]):
            sample[current] = value
            current += 1
    return np.array(sample)

def plotDensity(densities, log_flag = False, height = 8, width = 12, left = None, right = None, axes_limits = None):
    if type(densities[0]) != list and type(densities[0]) != np.ndarray:
        densities = [densities]
    fig = plt.figure(figsize=(height, width))
    ax = fig.add_subplot(2,1,1)

    #fig.set_size_inches(6, 4)
    if axes_limits:
        plt.axis(axes_limits)
        ax = plt.gca()
        ax.set_autoscale_on(False)

    if left is None:
        left = 0
    if right is None:
        right = len(densities[0])
    for density in densities:
        ax.plot(density[left : right])
    if log_flag:
        ax.set_xscale('log')
        ax.set_yscale('log')
    plt.show()


def readRD(filename, filepath = None, fullfill_flag = True, scale = True):
    if filepath: 
        filename = filepath + filename
    
    f = open(filename, "r")
    lines = f.readlines()
    f.close()
    
    total_count = int(list(lines[0].split('='))[1]) 
    x = []
    pdf = []
    cdf = []
    count = 0
    header_size = 12
    for line in lines[12:]:
        l = line.split(',')
        val = int(l[0])
        count = int(l[1])
        total_count = 0
        x.append(val)
        pdf.append(count)
        cdf.append(total_count)
    
    if fullfill_flag:
        fullfilled_cdf = [0 for i in range(max(x))]
        fullfilled_pdf = [0 for i in range(max(x))]
        curr = 0
        current_cdf_val = 0
        for i in range(max(x)):
            if i == x[curr]:
                current_cdf_val = cdf[curr]
                fullfilled_pdf[i] = pdf[curr]
                curr += 1
            fullfilled_cdf[i] = current_cdf_val
        x = x
        pdf = fullfilled_pdf
        cdf = fullfilled_cdf

    if not scale:
        return np.array(x), np.array(pdf), np.array(cdf)
    else:
	print 'asasas'
        return np.array(x), np.array(pdf).astype('float')/sum(pdf), np.array(cdf).astype('float')/max(cdf)

def standartize(density):
    mean = np.mean(density)
    stdvar = np.std(density)
    return (density - mean)/stdvar

def buildTrustedInterval(cdf, alpha):
    n = cdf.shape[0]
    print(np.sqrt(np.log(2 / alpha) / (2 * n)))
    lower_bound = cdf - np.sqrt(np.log(2 / alpha) / (2 * n))
    upper_bound = cdf + np.sqrt(np.log(2 / alpha) / (2 * n))
    return lower_bound, upper_bound

def chunk(pdf, chunk_size):
    new_pdf = np.zeros(int(pdf.shape[0] / chunk_size) + 1)
    for i in range(pdf.shape[0]):
        new_pdf[int(i / chunk_size)] += pdf[i]
    return new_pdf

class DensityInstance():
    def __init__(self, density_y, density_x = None):
        self.density_y = np.array(density_y)
        if density_x:
            self.density_x = np.array(density_x)
        else:
            self.density_x = np.linspace(0, len(density_y), 1)
    def shift(self, shift_val, fulfill = False, cut = False):
        if not fulfill:
            self.density_x += shift
        else:
            new_y = np.array([0.0 for i in range(len(self.density_y) + shift_val)])
            for i in range(len(self.density_y)):
                new_y[i + shift_val] = self.density_y[i]
            self.density_y = new_y
    def scale(self, coef):
        new_y = np.array([0. for i in range((int(len(self.density_y) * (coef + 1))))])
        for i in range(len(self.density_y)):
            new_y[int(i * coef)] = self.density_y[i]

        self.density_y = new_y
    def vertScale(self, coef):
        self.density_y *= coef
    def add(self, y):
        new_y = np.array([0.0 for i in range(max(len(y) , len(self.density_y)))])
        for i in range(min(len(y), len(self.density_y))):
            new_y[i] = y[i] + self.density_y[i]
        if len(self.density_y) > len(y):
            for i in range(len(y), len(self.density_y)):
                new_y[i] = self.density_y[i]
        else:
            for i in range(len(self.density_y),len(y)):
                new_y[i] = y[i]
        self.density_y = new_y

def preparePDF(filename, filepath = None, bandwidth = 10, kernel = 'gaussian', grid = 10):
    x, unscaled_pdf, unscaled_cdf = readRD(filename, filepath)
    sample = sampleFromDensity(unscaled_pdf)
    kde = KernelDensity(kernel=kernel, bandwidth=3).fit(sample[::grid].reshape(-1, 1))
    log_dens = kde.score_samples(np.linspace(0, sample.shape[0] / grid, sample.shape[0] / grid).reshape(-1,1))
    smoothed_pdf = np.exp(log_dens)
    
    return unscaled_pdf.astype('float64')/sum(unscaled_pdf), smoothed_pdf
