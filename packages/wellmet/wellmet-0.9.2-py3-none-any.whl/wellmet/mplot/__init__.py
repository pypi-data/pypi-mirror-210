#!/usr/bin/env python
# coding: utf-8


# nazvy proměnných jsou v angličtině
# Ale komenty teda ne)


import matplotlib

# direct use of matplotlib.fugure requires
# FigureManagerBase and managing of event loop
#import matplotlib.figure as mfigure

#č takže budeme i nadale pokorně použivat pyplot
import matplotlib.pyplot as plt

matplotlib.rcParams['mathtext.fontset'] = 'cm' # Computer Modern (TeX)
matplotlib.rcParams['font.family'] = 'STIXGeneral'
matplotlib.rcParams['savefig.dpi'] = 300
matplotlib.rcParams['savefig.bbox'] = 'tight'
matplotlib.rcParams['savefig.pad_inches'] = 0.015
matplotlib.rcParams['axes.linewidth'] = 0.4
matplotlib.rcParams['font.size'] = 7

# Show-functions
# Specially for qt_plot. 

def show_ax(ax_function, sample_box, space='R'):
    fig = plt.figure(figsize=(9/2.54, 9/2.54), tight_layout=True)
    ax = fig.add_subplot(111)
    ax.space = space
    ax.sample_box = sample_box
    ax_function(ax)
    fig.show()
    
def show_ax3d(ax3d_function, sample_box, space='R'):
    fig = plt.figure(figsize=(9/2.54, 9/2.54), tight_layout=True)
    ax = fig.add_subplot(111, projection='3d', azim=-90.0001, elev=89)
    ax.space = space
    ax.sample_box = sample_box
    ax3d_function(ax)
    fig.show()

def show_fig(fig_function, *args, **kwargs):
    fig = plt.figure(figsize=(9/2.54, 9/2.54), tight_layout=True)
    fig_function(fig, *args, **kwargs)
    fig.show()

