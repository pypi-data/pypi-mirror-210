#!/usr/bin/env python
# coding: utf-8

import numpy as np
from scipy import interpolate

from . import sball # for Isocurves
from . import IS_stat

def pf_entropy(pf):
    return -pf*np.log(pf) - (1-pf)*np.log(1-pf)


class RBF_surrogate:
    def __init__(self, sample_box, space='R'):
        self.sample_box = sample_box
        self.space = space
        self._nsim = -100500
        self.update()
    
    def __call__(self, *args):
        self.update()
        self.rbf(*args)
    
    def update(self):
        if self.sample_box.nsim > self._nsim:
            sample_space = getattr(self.sample_box, self.space)
            self.rbf = interpolate.Rbf(*sample_space.T, self.sample_box.g_values, function='gaussian')
            self._nsim = self.sample_box.nsim

    def get_pf_estimation(self, nis=100000):
        self.update()
        nodes = IS_stat.IS_norm(self.sample_box.f_model, mean=0, std=2.5, sampling_space='G', nis=nis, design=None)
        gi = self.rbf(*getattr(nodes, self.space).T)
        return np.sum(nodes.w[gi<0])/nis



def get_isodistances(f_model, r, nrod=200):
    phi = np.linspace(0, 6.283185307, nrod, endpoint=True)
    cos_phi = np.cos(phi)
    sin_phi = np.sin(phi)
    
    sample_G = np.array((cos_phi, sin_phi)).T * r
    return f_model.new_sample(sample_G, space='G', extend=True)


def isolevels_2d(pdf, weighting_pdf_const, r_levels, from_top=None):
    """
    weighting_pdf_const = 1 / (xmax - xmin) / (ymax - ymin)
    """
    s_ball = sball.Sball(2) # nvar=2
    p_levels = []
    for r in r_levels:
        p_levels.append(1 - s_ball.get_pf(r))
    
    return isolevels(pdf, weighting_pdf_const, p_levels, from_top)




def isolevels(pdf, weighting_pdf_const, p_levels, from_top=None):
    """
    weighting_pdf_const = 1 / (xmax - xmin) / (ymax - ymin)
    """
    #č třeba P prostor doopravdy zlobí, takže zkusím nějak tak
    if from_top is None:
        weights = pdf / weighting_pdf_const
        p_all = np.sum(weights) / len(pdf)
        #č prečo víme, že celková pravděpodobnost může bejt nekoněčně velká
        if p_all <= 1:
            from_top = True
        else:
            from_top = False
            
    max_pdf = np.max(pdf)
    pdf_levels = []
    if from_top:
        # descending
        sorted_pdf = np.flip(np.sort(pdf))
        p_cumsum = np.cumsum(sorted_pdf) / weighting_pdf_const / len(pdf)
        for p in p_levels:
            # little bit tricky, didn't find numpy method for this
            mask = p_cumsum <= p
            level_down_bound = np.max(sorted_pdf[~mask], initial=0)
            level_up_bound = np.min(sorted_pdf[mask], initial=max_pdf)
            pdf_levels.append((level_down_bound + level_up_bound) / 2)
            
    else: # from bottom
        sorted_pdf = np.sort(pdf)
        p_cumsum = np.cumsum(sorted_pdf) / weighting_pdf_const / len(pdf)
        for p in p_levels:
            # little bit tricky, didn't find numpy method for this
            mask = p_cumsum <= 1-p
            level_down_bound = np.max(sorted_pdf[mask], initial=0)
            level_up_bound = np.min(sorted_pdf[~mask], initial=max_pdf)
            pdf_levels.append((level_down_bound + level_up_bound) / 2)

    return pdf_levels
