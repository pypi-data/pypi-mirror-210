from MPSPlots.tools.directories import style_directory
import matplotlib.pyplot as plt


def use_mpsplots_style():
    plt.style.use(style_directory.joinpath('mps_plot.mplstyle'))


def use_new_age_style():
    plt.style.use(style_directory.joinpath('new_age.mplstyle'))
    plt.rcParams["mathtext.fontset"] = "dejavuserif"
    plt.rcParams["font.family"] = "serif"
    plt.rcParams['axes.edgecolor'] = 'black'
    plt.rcParams['axes.grid.which'] = 'both'


def use_ggplot_style():
    plt.style.use('ggplot')
    plt.rcParams["mathtext.fontset"] = "dejavuserif"
    plt.rcParams["font.family"] = "serif"
    plt.rcParams['axes.edgecolor'] = 'black'
    plt.rcParams['axes.grid.which'] = 'both'


def use_default_style():
    plt.style.use('default')
    plt.rcParams["mathtext.fontset"] = "dejavuserif"
    plt.rcParams["font.family"] = "serif"
    plt.rcParams['axes.edgecolor'] = 'black'
    plt.rcParams['axes.grid.which'] = 'both'


use_mpsplots_style()  # default
# -
