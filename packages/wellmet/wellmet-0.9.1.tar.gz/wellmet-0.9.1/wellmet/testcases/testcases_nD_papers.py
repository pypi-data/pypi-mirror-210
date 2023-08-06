#!/usr/bin/env python
# coding: utf-8

"""
We will prepare here WhiteBox instances
of different well-known different dimension problems
"""

import numpy as np
from .. import g_models as gm
from .. import f_models
from ..whitebox import WhiteBox
import scipy.stats as stats
import mpmath # for suspension_3D

__all__ = [
            'nonlinear_oscilator_6D',
            'single_spring_nonlinear_oscilator_5D',
            #'noisy_lsf_Papaioannou_6D',
            #'noisy_lsf_Liu_6D',
            'passive_vehicle_suspension_3D'
            ]



def nonlinear_oscilator_6D():
    """
    DOI:10.1016/j.strusafe.2004.11.001
    Beneﬁt of splines and neural networks in simulation based
    structural reliability analysis
    """
    f = f_models.Norm(np.array([1, 1, 0.1, 0.5, 1, 1]), 
                        np.array([0.05, 0.10, 0.01, 0.05, 0.20, 0.20]))
    wt = WhiteBox(f, gm.nonlinear_oscilator)
    wt.pf_exact = 0.0281
    wt.pf_exact_method = 'known value'
    return wt

def single_spring_nonlinear_oscilator_5D():
    c_mean = 1 + 0.1
    c_std = np.sqrt(0.10**2 + 0.01**2)
    f = f_models.Norm(np.array([1, c_mean, 0.5, 1, 1]), 
                        np.array([0.05, c_std , 0.05, 0.20, 0.20]))
    wt = WhiteBox(f, gm.single_spring_nonlinear_oscilator)
    wt.pf_exact = 0.0281
    wt.pf_exact_method = 'known value'
    return wt


__all__.append("nonlinear_oscilator_pf6_6D")
def nonlinear_oscilator_pf6_6D():
    """
    @article{ECHARD2013232,
title = {A combined Importance Sampling and Kriging reliability method for small failure probabilities with time-demanding numerical models},
journal = {Reliability Engineering & System Safety},
volume = {111},
pages = {232-240},
year = {2013},
issn = {0951-8320},
doi = {https://doi.org/10.1016/j.ress.2012.10.008},
url = {https://www.sciencedirect.com/science/article/pii/S0951832012002086},
author = {B. Echard and N. Gayton and M. Lemaire and N. Relun},
keywords = {Reliability, Kriging metamodel, Surrogate model, Small failure probability, Importance sampling},
abstract = {Applying reliability methods to a complex structure is often delicate for two main reasons. First, such a structure is fortunately designed with codified rules leading to a large safety margin which means that failure is a small probability event. Such a probability level is difficult to assess efficiently. Second, the structure mechanical behaviour is modelled numerically in an attempt to reproduce the real response and numerical model tends to be more and more time-demanding as its complexity is increased to improve accuracy and to consider particular mechanical behaviour. As a consequence, performing a large number of model computations cannot be considered in order to assess the failure probability. To overcome these issues, this paper proposes an original and easily implementable method called AK-IS for active learning and Kriging-based Importance Sampling. This new method is based on the AK-MCS algorithm previously published by Echard et al. [AK-MCS: an active learning reliability method combining Kriging and Monte Carlo simulation. Structural Safety 2011;33(2):145–54]. It associates the Kriging metamodel and its advantageous stochastic property with the Importance Sampling method to assess small failure probabilities. It enables the correction or validation of the FORM approximation with only a very few mechanical model computations. The efficiency of the method is, first, proved on two academic applications. It is then conducted for assessing the reliability of a challenging aerospace case study submitted to fatigue.}
}
    """
    
    T1_mean = 1
    T1_std = 0.2 * T1_mean
    F1_mean = 0.6
    F1_std = F1_mean / 6
    #m, c1, c2, r, F1, t1 = sample.T
    f = f_models.Norm(np.array([1, 1, 0.1, 0.5, F1_mean, T1_mean]), 
                        np.array([0.05, 0.10, 0.01, 0.05, F1_std, T1_std]))
    wt = WhiteBox(f, gm.nonlinear_oscilator)
    wt.pf_exact = 9.09e-6
    wt.pf_exact_method = 'known value'
    return wt


__all__.append("single_spring_nonlinear_oscilator_pf6_5D")
def single_spring_nonlinear_oscilator_pf6_5D():
    c_mean = 1 + 0.1
    c_std = np.sqrt(0.10**2 + 0.01**2)
    T1_mean = 1
    T1_std = 0.2 * T1_mean
    F1_mean = 0.6
    F1_std = F1_mean / 6
    f = f_models.Norm(np.array([1, c_mean, 0.5, F1_mean, T1_mean]), 
                        np.array([0.05, c_std , 0.05, F1_std, T1_std]))
    wt = WhiteBox(f, gm.single_spring_nonlinear_oscilator)
    wt.pf_exact = 9.09e-6
    wt.pf_exact_method = 'known value'
    return wt






__all__.append("nonlinear_oscilator_pf8_6D")
def nonlinear_oscilator_pf8_6D():
    """
    @article{ECHARD2013232,
title = {A combined Importance Sampling and Kriging reliability method for small failure probabilities with time-demanding numerical models},
journal = {Reliability Engineering & System Safety},
volume = {111},
pages = {232-240},
year = {2013},
issn = {0951-8320},
doi = {https://doi.org/10.1016/j.ress.2012.10.008},
url = {https://www.sciencedirect.com/science/article/pii/S0951832012002086},
author = {B. Echard and N. Gayton and M. Lemaire and N. Relun},
keywords = {Reliability, Kriging metamodel, Surrogate model, Small failure probability, Importance sampling},
abstract = {Applying reliability methods to a complex structure is often delicate for two main reasons. First, such a structure is fortunately designed with codified rules leading to a large safety margin which means that failure is a small probability event. Such a probability level is difficult to assess efficiently. Second, the structure mechanical behaviour is modelled numerically in an attempt to reproduce the real response and numerical model tends to be more and more time-demanding as its complexity is increased to improve accuracy and to consider particular mechanical behaviour. As a consequence, performing a large number of model computations cannot be considered in order to assess the failure probability. To overcome these issues, this paper proposes an original and easily implementable method called AK-IS for active learning and Kriging-based Importance Sampling. This new method is based on the AK-MCS algorithm previously published by Echard et al. [AK-MCS: an active learning reliability method combining Kriging and Monte Carlo simulation. Structural Safety 2011;33(2):145–54]. It associates the Kriging metamodel and its advantageous stochastic property with the Importance Sampling method to assess small failure probabilities. It enables the correction or validation of the FORM approximation with only a very few mechanical model computations. The efficiency of the method is, first, proved on two academic applications. It is then conducted for assessing the reliability of a challenging aerospace case study submitted to fatigue.}
}
    """
    
    T1_mean = 1
    T1_std = 0.2 * T1_mean
    F1_mean = 0.45
    F1_std = F1_mean / 6
    #m, c1, c2, r, F1, t1 = sample.T
    f = f_models.Norm(np.array([1, 1, 0.1, 0.5, F1_mean, T1_mean]), 
                        np.array([0.05, 0.10, 0.01, 0.05, F1_std, T1_std]))
    wt = WhiteBox(f, gm.nonlinear_oscilator)
    wt.pf_exact = 1.55e-8
    wt.pf_exact_method = 'known value'
    return wt


__all__.append("single_spring_nonlinear_oscilator_pf8_5D")
def single_spring_nonlinear_oscilator_pf8_5D():
    c_mean = 1 + 0.1
    c_std = np.sqrt(0.10**2 + 0.01**2)
    T1_mean = 1
    T1_std = 0.2 * T1_mean
    F1_mean = 0.45
    F1_std = F1_mean / 6
    f = f_models.Norm(np.array([1, c_mean, 0.5, F1_mean, T1_mean]), 
                        np.array([0.05, c_std , 0.05, F1_std, T1_std]))
    wt = WhiteBox(f, gm.single_spring_nonlinear_oscilator)
    wt.pf_exact = 1.55e-8
    wt.pf_exact_method = 'known value'
    return wt




def noisy_lsf_Papaioannou_6D():
    """
    Papaioannou. Sequental importance sampling
    for structural reliability analysis
    """
    f = f_models.UnCorD([ #č já jsem nepřišel na to, jak to mysleli s tím rozdělením
                        stats.lognorm(s=8, loc=120), 
                        stats.lognorm(s=8, loc=120), 
                        stats.lognorm(s=8, loc=120), 
                        stats.lognorm(s=8, loc=120), 
                        stats.lognorm(s=10, loc=50), 
                        stats.lognorm(s=8, loc=40), 
                        ])
    wt = WhiteBox(f, gm.noisy_lsf)
    wt.pf_exact = 5.29e-4
    wt.pf_exact_method = 'known value'
    return wt




def noisy_lsf_Liu_6D():
    """
    @article{LIU1991161,
    title = {Optimization algorithms for structural reliability},
    journal = {Structural Safety},
    volume = {9},
    number = {3},
    pages = {161-177},
    year = {1991},
    issn = {0167-4730},
    doi = {https://doi.org/10.1016/0167-4730(91)90041-7},
    url = {https://www.sciencedirect.com/science/article/pii/0167473091900417},
    author = {Pei-Ling Liu and Armen {Der Kiureghian}},
    keywords = {algorithms, finite element, optimization, probability theory, reliability analysis, robustness, safety, structures},
    abstract = {Several optimization algorithms are evaluated for application in structural reliability, where the minimum distance from the origin to the limit-state surface in the standard normal space is required. The objective is to determine the suitability of the algorithms for application to linear and nonlinear finite element reliability problems. After a brief review, five methods are compared through four numerical examples. Comparison criteria are the generality, robustness, efficiency, and capacity of each method.}
    }
    """
    f = f_models.UnCorD([ #č já jsem nepřišel na to, jak to mysleli s tím rozdělením
                        stats.lognorm(s=1, loc=120, scale=12), 
                        stats.lognorm(s=1, loc=120, scale=12), 
                        stats.lognorm(s=1, loc=120, scale=12), 
                        stats.lognorm(s=1, loc=120, scale=12), 
                        stats.lognorm(s=1, loc=50, scale=15), 
                        stats.lognorm(s=1, loc=40, scale=12), 
                        ])
    wt = WhiteBox(f, gm.noisy_lsf)
    wt.pf_exact = stats.norm.sf(2.3482)
    wt.DP = [117.3, 115.3, 115.3, 117.3, 83.62, 55.54]
    wt.pf_exact_method = 'known value'
    return wt






def passive_vehicle_suspension_3D():
    mu1, mu2, mu3 = (431.7221, 1475.5503, 55.0406)
    s = 10
    f3 = f_models.Norm(np.array((mu1, mu2, mu3)),
                        np.array((s, s, s))
                        )
    wt = WhiteBox(f3, gm.PassiveVehicleSuspension())
    # first (bottom) design point 
    max_failure_1 = 1442.64218624
    min_success_1 = 1442.64243976
    DP1 = 1442.642281
    # pf(beta 1) je mezi array([0.00049949, 0.00049954])

    # second (left) design point 
    max_failure_2 = 391.20793653
    min_success_2 = 391.21532796
    DP2 = 391.2123922
    # pf(beta 2) je mezí [2.54542636e-05, 2.55348088e-05]

    # ještě 3 poruchových bodů on very low K values, however, they do not form simple failure plane, there are success points even lower.
    #array([[4.08598926e+02, 1.47388406e+03, 1.00615452e-01],
    #   [4.77325547e+02, 1.46414564e+03, 5.55312946e-02],
    #   [4.24694913e+02, 1.45236644e+03, 9.50311636e-01]])
    
    wt.pf_upper = 1 - (1 - mpmath.ncdf(min_success_2, mu=mu1, sigma=s)) \
                * (1 - mpmath.ncdf(min_success_1, mu=mu2, sigma=s)) \
                * (1 - mpmath.ncdf("9.50311636e-01", mu=mu3, sigma=s))
                
    wt.pf_lower = 1 - (1 - mpmath.ncdf(max_failure_2, mu=mu1, sigma=s)) \
                * (1 - mpmath.ncdf(max_failure_1, mu=mu2, sigma=s))
    wt.pf_exact = float(1 - (1 - mpmath.ncdf(DP2, mu=mu1, sigma=s)) \
                * (1 - mpmath.ncdf(DP1, mu=mu2, sigma=s)))
    #č 0.000525 je hodně dobrý odhad
    wt.pf_exact_method = 'FORM-based precise geometry analysis'
    
    wt.r_exact = (mu2 - DP1) / s
    
    #wt.pf_exact = 0.00052
    #wt.pf_exact_method = 'IS'
    #wt.Nsim = 1000000
    #wt.description = ""
    return wt


