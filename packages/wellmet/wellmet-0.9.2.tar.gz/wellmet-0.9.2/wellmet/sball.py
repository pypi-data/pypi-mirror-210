#!/usr/bin/env python
# coding: utf-8

import numpy as np
import scipy.special as sc
from scipy import stats

#######################################################
# s-balls  -- tools to calc probabilities and radii ###
#######################################################


def get_ps_ball(d,R):
    "returns probability of falling inside d-ball with radius R"
    #return np.sum(np.exp(-(rho**2)/2)*rho**(d-1) )* R/n
    return sc.gammainc(d/2, R**2/2)

def get_pf_ball(d,R):
    "returns probability of falling outside d-ball with radius R"
    return sc.gammaincc(d/2, R**2/2)

def get_Radius_pf(d,pf_ball):
    "returns radius of an d-ball with probability pf outside"
    rsqdiv2 = sc.gammainccinv(d/2, pf_ball)
    return np.sqrt(2*rsqdiv2) #radius

def get_Radius_ps(d,ps_ball):
    "returns radius of an d-ball with probability ps inside"
    rsqdiv2 = sc.gammaincinv(d/2, ps_ball)
    return np.sqrt(2*rsqdiv2) #radius





# implement class compatible to the old ones

# dispatcher
def Sball(nvar):
    if nvar == 2:
        return Sball_2D(nvar)
    else:
        return Sball_nD(nvar)

class Sball_nD:
    def __init__(self, nvar):
        self.nvar = nvar
        self.a = nvar/2
        
    def get_pf(self, r):
        "returns pf, i.e. complementary part of multidimensional Gaussian distribution"
        return sc.gammaincc(self.a, r**2/2)
        
    def get_ps(self, r):
        "returns probability of falling inside d-ball with radius R"
        return sc.gammainc(self.a, r**2/2)
    
    def get_r(self, desired_pf):
        "sball inversion. Returns radius of the s-ball with probability pf outside"
        rsqdiv2 = sc.gammainccinv(self.a, desired_pf)
        return np.sqrt(2*rsqdiv2) #radius
    
    
    def get_r_iteration(self, desired_pf):
        "Same as .get_r(), just keeps compatibility with previous versions"
        return self.get_r(desired_pf), desired_pf
    
    # make it, finally, scipy.stats -compatible
    sf = get_pf
    isf = get_r
    cdf = get_ps
    def ppf(self, q):
        return get_Radius_ps(self.nvar, q)

    
class Sball_2D(Sball_nD):
    def get_pf(self, r):
        "returns pf, i.e. complementary part of multidimensional Gaussian distribution"
        return np.exp(-r**2/2)
    
    def get_r(self, desired_pf):
        "sball inversion. Returns radius of the s-ball with probability pf outside"
        return np.sqrt(-2*np.log(desired_pf))
    
    
# calculation is as fast as Sball_nD
# but I'm not sure about precision
class Sball_4D(Sball_nD):
    def get_pf(self, r):
        "returns pf, i.e. complementary part of multidimensional Gaussian distribution"
        return (r**2/2+1)*np.exp(-r**2/2)








#1/ univariate funkce pro bounded Gauss
# left-right-bounded univariate Gaussian
class Radial:
    def __init__(self, nvar, r=0, R=np.inf):
        self.sball = Sball(nvar)
        self.set_bounds(r, R)
        
    def set_bounds(self, r=0, R=np.inf):
        #č kbyby se někomu nechtělo naťukat "np.inf"
        self.r = r # left bound
        self.R = R # rigth bound
        
        self.ps = self.sball.get_ps(r)
        self.pf = self.sball.get_pf(R)
        #č obsah pravděpodobnosti v mezikruži
        # well, probability falling to the shell
        self.p_shell = self.sball.get_pf(r) - self.pf
    
    #č jen pro formu. Kdo by to potřeboval?
    def _pdf(self, x): return stats.chi.pdf(x, self.sball.nvar) / self.p_shell
    def _cdf(self, x): return (self.sball.get_ps(x) - self.ps) / self.p_shell
    def _sf(self, x): return (self.sball.get_pf(x) - self.pf) / self.p_shell
    
    def pdf(self, x):
        return np.piecewise(x, [x<=self.r, x>=self.R], [0, 0, self._pdf])
        
    def cdf(self, x):
        return np.piecewise(x, [x<=self.r, x>=self.R], [0, 1, self._cdf])
        
    def sf(self, x): # 1 - cdf
        return np.piecewise(x, [x<=self.r, x>=self.R], [1, 0, self._sf])

    def ppf(self, q):
        return get_Radius_ps(self.sball.nvar, q*self.p_shell + self.ps)
        
    def isf(self, q): # inverse of .sf()
        return self.sball.get_r(q*self.p_shell + self.pf)
        
        

def get_random_directions(ns, ndim):
    # rand_dir: prepare ns random directions on a unit d-sphere
    rand_dir = np.random.randn(ns, ndim) #random directions
    
    
    lengths = np.sum(np.square(rand_dir), axis=1)
    lengths = np.sqrt(lengths, out=lengths) #lengths of each radius-vector
    
    # scale all radii-vectors to unit length
    # use [:,None] to get an transposed 2D array
    rand_dir = np.divide(rand_dir, lengths[:,None], out=rand_dir) 
    
    return rand_dir



#č nebyl to úplně ideální napad dědit od Radial
#č cdf, ppf, sf a isf metody nejsou pro Shell aplikovatelné!
#č Ještě jednou, bacha, davejte pozor, co vztahuje k 1D radiálnímu rozdělení,
#č co - k optimálnímu IS rozdělení proporcionálnímu nD Gaussu.
# We apologize for inconvenience
class Shell(Radial):
    """
    Optimal sampling density for Nv-ball (gaussian samples outside Nv-ball)
    with density proportional to Gaussian density
    """
    def rvs(self, size=1): # keyword size is scipy.stats-compatible
        "Generování­ vzorků (kandidátů a integračních bodů)"
        ns = size
        # rand_dir: prepare ns random directions on a unit d-sphere
        rand_dir = get_random_directions(ns, self.sball.nvar) #random directions
        
        # generate sampling probabilites
        p = np.linspace(1, 0, ns, endpoint=False) # probabilities for the radius
        
        # convert probabilitites into random radii
        # (distances from origin that are greater than r and less than R)
        r = self.isf(p) # actually, it is the same as CDF inverse
        
        #finally a random sample from the optimal IS density:
        sample_G = rand_dir*r[:,None]
        
        return sample_G

    #оӵ кулэ ӧвӧл #č multi nebudem použivat
    def _pdf_multi(self, x): return np.prod(stats.norm.pdf(x), axis=1)/self.p_shell
    
    def _pdf_norm(self, rx): 
        # stats.norm.pdf(0) == 0.3989422804014327
        c = 0.3989422804014327**(self.sball.nvar-1)
        return stats.norm.pdf(rx)*c/self.p_shell
    
    #č Vypocet hustot optimalni vzorkovaci veliciny (left-right-bounded)
    def pdf(self, x):
        """density of optimal IS variable h, 
        i.e. Gaussian variable with zero density inside d-ball"""
        rx = np.sum(x**2, axis=1)
        rx = np.sqrt(rx, out=rx) 
        return np.piecewise(rx, [rx<=self.r, rx>=self.R], [0, 0, self._pdf_norm])

