#!/usr/bin/env python
# coding: utf-8

import matplotlib


__all__ = ['margins3d_patch', 'grid3d_patch', 'enable_tex']

def margins3d_patch(*args, **kwargs):
    from . import _axis3d_margins_patch
    
def grid3d_patch(*args, **kwargs):
    from . import _axis3d_margins_patch, _axes3d


def enable_tex(*args, **kwargs):
    matplotlib.rcParams['text.usetex'] = True
    
    # Times, Palatino, New Century Schoolbook, Bookman, Computer Modern Roman
    matplotlib.rc('font',**{'family':'serif','serif':['Computer Modern Roman']}) 
    #matplotlib.use('pgf')
    #matplotlib.rcParams["pgf.texsystem"] = "xelatex"
    #matplotlib.rcParams["pgf.rcfonts"] = False
    
    preamble = r'''\usepackage[utf8]{inputenc} %unicode support
    \usepackage[T1]{fontenc}
    \DeclareMathAlphabet{\pazocal}{OMS}{zplm}{m}{n}
    \usepackage{calrsfs}
    \usepackage{amsmath}
    \usepackage{bm}
    \usepackage[bitstream-charter]{mathdesign}
    '''
    
    
    #with open("preamble.tex", "r") as file:
    #    preamble = file.read()
    
    matplotlib.rc('text.latex', preamble=preamble)
    #matplotlib.rcParams["pgf.preamble"] = preamble
