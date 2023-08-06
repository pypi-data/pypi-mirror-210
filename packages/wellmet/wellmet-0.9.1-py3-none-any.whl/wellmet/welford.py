#!/usr/bin/env python
# coding: utf-8

# One does not simply calculate the sample variance.
# https://github.com/numpy/numpy/issues/6231
# Only one citation from: 
# "Online calculations happen all the time (due to resource limitations), 
# and a np.welford function would be convenient so that not everyone 
# has to implement welford on its own over and over again."

# There are actually some code can be found in internet,
# but those I've seen supposed one-by-one data addition.

"""
This is implementation of generalized (for arbitrary sample sizes) 
Welford's updating (online) algorithm, given by Chan et al. in two papers:
"Algorithms for computing the sample variance: Analysis and recommendations"
https://doi.org/10.1080%2F00031305.1983.10483115
and
 "Updating Formulae and a Pairwise Algorithm for Computing Sample Variances."
http://i.stanford.edu/pub/cstr/reports/cs/tr/79/773/CS-TR-79-773.pdf
"""


import numpy as np



class Welford:
    def __init__(self):
        self.n = 0
        
        
    def add(self, data):
        n = len(data)
        T = np.sum(data)
        #č takhle je to numericky nejstabilnější
        S = np.sum(np.square(data - T/n))
        
        if self.n == 0:
            self.n = n
            self.T = T
            self.S = S
        else:
            m = self.n #č to, co bylo
            self.S += S + m /n /(m+n) * (n/m * self.T - T)**2
            self.n += n
            self.T += T
            
    #č Pro řídká data, speciálita pro IS
    #č uděláme explicitnou funkci s povinným sample size
    def add_sparse(self, data, n):
        """Method processes sparse data, assumes 
        only non-zero values of entire sample (of size n) need to be given"""
        sample_size = len(data)
        assert n >= sample_size
        
        T = np.sum(data)
        mean = T/n
        #č takhle je to numericky nejstabilnější
        S = np.sum(np.square(data - mean)) + (n - sample_size) * mean**2
        
        if self.n == 0:
            self.n = n
            self.T = T
            self.S = S
        else:
            m = self.n #č to, co bylo
            self.S += S + m /n /(m+n) * (n/m * self.T - T)**2
            self.n += n
            self.T += T
            
    @property
    def mean(self): 
        return self.T / self.n
    
    @property
    def var(self): 
        return self.S / self.n
        
    @property
    def s2(self): 
        return self.S / (self.n - 1)

