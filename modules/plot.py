import matplotlib.pyplot as plt
import numpy as np

from matplotlib.ticker import NullFormatter


def plot_jointd_sct(dataframe, xband, yband, xlim=None, ylim=None):
    dataframe.reset_index(drop=True, inplace=True)
    # the random data
    x = dataframe[xband]
    y = dataframe[yband]

    # definitions for the axes
    spacing = 0.035
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left + width + 0.02

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom + height + spacing, width, 0.2]
    rect_histy = [left + width + spacing, bottom, 0.2, height]

    # start with a rectangular Figure
    plt.figure(1, figsize=(12, 12))

    axScatter = plt.axes(rect_scatter)
    axHistx = plt.axes(rect_histx)
    axHisty = plt.axes(rect_histy)

    axScatter.set_xlabel(xband, fontsize=22, color='blue')
    axScatter.set_ylabel(yband, fontsize=22, color='blue')

    axScatter.tick_params(axis='both', labelsize=18)
    axHistx.tick_params(axis='both', labelsize=18)
    axHisty.tick_params(axis='both', labelsize=18)

    # no labels
    nullfmt = NullFormatter()
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)

    # the scatter plot:
    axScatter.scatter(x, y, c='blue', s=0.5, alpha=0.03)

    binwidth = 0.05
    xymax = np.max([np.max(np.fabs(x)), np.max(np.fabs(y))])
    lim = (xymax / binwidth + 1) * binwidth

    if (xlim == None):
        xlim = (-lim, lim)

    if (ylim == None):
        ylim = (-lim, lim)

    axScatter.set_xlim(xlim)
    axScatter.set_ylim(ylim)

    xmax = np.max(x)
    xmin = np.min(x)
    ymax = np.max(y)
    ymin = np.min(y)
    sup_lim_x = (int(xmax / binwidth) + 1) * binwidth
    inf_lim_x = (int(xmin / binwidth) - 1) * binwidth
    sup_lim_y = (int(ymax / binwidth) + 1) * binwidth
    inf_lim_y = (int(ymin / binwidth) - 1) * binwidth

    # bins = np.arange(-lim, lim + binwidth, binwidth)
    bins_x = np.arange(inf_lim_x, sup_lim_x + binwidth, binwidth)
    bins_y = np.arange(inf_lim_y, sup_lim_y + binwidth, binwidth)

    # axHistx.hist(x, bins=bins, color='blue', histtype='stepfilled')
    # axHisty.hist(y, bins=bins, color='blue', histtype='stepfilled', orientation='horizontal')
    axHistx.hist(x, bins=bins_x, color='blue', histtype='stepfilled')
    axHisty.hist(y, bins=bins_y, color='blue', histtype='stepfilled', orientation='horizontal')

    axHistx.set_xlim(axScatter.get_xlim())
    axHisty.set_ylim(axScatter.get_ylim())

    plt.show()

def plot_jointd_sct_m(xdf, ydf,  xlabel, ylabel, xlim=None, ylim=None):
    xdf.reset_index(drop=True, inplace=True)
    ydf.reset_index(drop=True, inplace=True)

    # the random data
    x = xdf
    y = ydf

    # definitions for the axes
    spacing = 0.035
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left + width + 0.02

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom + height + spacing, width, 0.2]
    rect_histy = [left + width + spacing, bottom, 0.2, height]

    # start with a rectangular Figure
    plt.figure(1, figsize=(12, 12))

    axScatter = plt.axes(rect_scatter)
    axHistx = plt.axes(rect_histx)
    axHisty = plt.axes(rect_histy)

    axScatter.set_xlabel(xlabel, fontsize=22, color='blue')
    axScatter.set_ylabel(ylabel, fontsize=22, color='blue')

    axScatter.tick_params(axis='both', labelsize=18)
    axHistx.tick_params(axis='both', labelsize=18)
    axHisty.tick_params(axis='both', labelsize=18)

    # no labels
    nullfmt = NullFormatter()
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)

    # the scatter plot:
    axScatter.scatter(x, y, c='blue', s=0.5, alpha=0.03)

    binwidth = 0.05
    xymax = np.max([np.max(np.fabs(x)), np.max(np.fabs(y))])
    lim = (xymax / binwidth + 1) * binwidth

    if (xlim == None):
        xlim = (-lim, lim)

    if (ylim == None):
        ylim = (-lim, lim)

    axScatter.set_xlim(xlim)
    axScatter.set_ylim(ylim)

    xmax = np.max(x)
    xmin = np.min(x)
    ymax = np.max(y)
    ymin = np.min(y)
    sup_lim_x = (int(xmax / binwidth) + 1) * binwidth
    inf_lim_x = (int(xmin / binwidth) - 1) * binwidth
    sup_lim_y = (int(ymax / binwidth) + 1) * binwidth
    inf_lim_y = (int(ymin / binwidth) - 1) * binwidth

    # bins = np.arange(-lim, lim + binwidth, binwidth)
    bins_x = np.arange(inf_lim_x, sup_lim_x + binwidth, binwidth)
    bins_y = np.arange(inf_lim_y, sup_lim_y + binwidth, binwidth)

    # axHistx.hist(x, bins=bins, color='blue', histtype='stepfilled')
    # axHisty.hist(y, bins=bins, color='blue', histtype='stepfilled', orientation='horizontal')
    axHistx.hist(x, bins=bins_x, color='blue', histtype='stepfilled')
    axHisty.hist(y, bins=bins_y, color='blue', histtype='stepfilled', orientation='horizontal')

    axHistx.set_xlim(axScatter.get_xlim())
    axHisty.set_ylim(axScatter.get_ylim())

    plt.show()