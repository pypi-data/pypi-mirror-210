WellMet is pure Python framework for spatial structural reliability analysis. Or, more specifically, for "failure probability estimation and detection of failure surfaces by adaptive sequential decomposition of the design domain".

Main dependencies are numpy+scipy, pandas, quadpy.
Qt frontend requires pyqtgraph.

To run graphical frontend with predefined reliability problems type in shell: python -m wellmet

How to use:
A. To run GUI with predefined benchmark problems:
1. Type in shell: python -m wellmet
2. Choose problem to solve, choose (optionally) filename to store samples and estimations, set up the algorithm.
3. Choose from the main menu "Batch run" and type desired number of LSF calls.

B. To test the your own problem still using WellMet's GUI use the following code:
#!/usr/bin/env python
# coding: utf-8

import numpy as np
import scipy.stats as stats

from wellmet.qt_gui import qt_box_functions as gui
from wellmet import whitebox
from wellmet.samplebox import SampleBox
from wellmet import f_models


# 1. Set up probability distribution
# Standard Gaussian variables, 2D
#f = f_models.SNorm(2)
# Just normal variables
f = f_models.Norm(mean=[-1, 0], std=[2, 1])
# Independent non-Gaussian variables
#f = f_models.UnCorD((stats.gumbel_r, stats.uniform))
# Correlated non-Gaussian marginals
#f = f_models.Nataf((stats.gumbel_r, stats.weibull_min(c=1.5)), [[1,0.8], [0.8,1]])

# 2. Define LSF function
def my_problem(input_sample):
    # get real (physical) space coordinates
    # X is a numpy array with shape (nsim, ndim)
    # the algorithm normally sends (1, ndim) sample
    X = input_sample.R
    # LSF
    g = X[:, 0] - X[:, 1] + 3
    # we should return an instance of SampleBox class
    # this instance stores coordinates along with LSF calculation result
    return SampleBox(input_sample, g, "my_problem")

# 3. Put them together
wt = whitebox.WhiteBox(f, my_problem)

# choose filename to store samples and estimations
gui.read_box(wt)
# setup algorithm
gui.setup_dicebox(wt)

# start GUI
gui.show_box(wt)








The software has been developed as part of an internal academic project no. FAST-K-21-6943 sponsored by the Czech Ministry of Education, Youth and Sports and also by project named ``Quality Internal Grants of BUT (KInG BUT)'', Reg. No. CZ.02.2.69/0.0/0.0/19\_073/0016948, which is financed from the OP RDE.