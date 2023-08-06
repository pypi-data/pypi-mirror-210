#!/usr/bin/env python
# coding: utf-8

#оӵ Тӧдьы кабъёс (ящикьёс) эскером

from .. import whitebox
from .. import samplebox #č pro proxy_prod
from .. import g_models as gm
from .. import f_models
import scipy.stats as stats

import numpy as np

f = f_models.SNorm(2)
h = f_models.UnCorD((stats.norm(-12,5), stats.norm(12,5)))
#l = f_models.UnCorD([stats.lognorm(s=1), stats.lognorm(s=1)])
#č pro různorodost
gew = f_models.Nataf((stats.gumbel_r, stats.weibull_min(c=1.5)), [[1,0.8], [0.8,1]])
gewm = f_models.Nataf((stats.gumbel_r, stats.weibull_min(c=1.5)), [[1,-0.8], [-0.8,1]])
gb = f_models.Nataf((stats.gumbel_r(scale=0.3), stats.beta(0.6, 0.8)), [[1,-0.75], [-0.75,1]])
#gew = f_models.Nataf((stats.norm, stats.norm), [[1,0.8], [0.8,1]])
#gew = f_models.Nataf((stats.gumbel_r, stats.gumbel_l), [[1,0.8], [0.8,1]])
#č uniforma je na [0, 1], takže v cajku
u = f_models.UnCorD((stats.uniform, stats.uniform))

__all__ = []

#č zde ten __all__ těžko dohlídáme
#č budeme přidávat do seznamu postupně
def add(str):
    __all__.append(str)


# HyperRovina, куда ж без неё?
#############
# g= a*X1 + b*X2 + c
# becames
# gm = Linear_nD(betas=(a,b,c))
add('natafm_plane_2D')
def natafm_plane_2D():
    wt = whitebox.WhiteBox(gewm, gm.Linear_nD((-1, -2, 7)))
    wt.pf_exact = 0.00114
    wt.Nsim = int(10e8)
    wt.pf_exact_method = 'MC'
    return wt



# nobody knows whats going on there
""" parametry pravdepodobnostniho rozdeleni pro Z_min s Weib. velicinami
wb_scales=(1,1) - tuple of Weibull scale parameters, len(wb_scales)==nvar
shape = 5 
je třeba zadat buď pf_exact, nebo konštantu u funkce minima Z_min """
# g= min(X1, X2, X3, X4) + c
add('weibull_min_2D')
def weibull_min_2D():
    return whitebox.Weibull_Z_min(wb_scales=(1.5,0.9), shape=4, const=-2.5)
    #whitebox.Weibull_Z_min(wb_scales=(1.5,0.9), shape=4, pf_exact=1.0e-6)



# neither Gauß knows whats going on there
#whitebox.Gaussian_Z_sumexp(nvar=2, pf_exact=1.0e-6)




# je třeba zadat buď pf_exact, nebo konštantu u funkce Z_sumsq
# g = np.sum(sample**2, axis=1) - self._const
add('sumsq_2D')
def sumsq_2D():
    return whitebox.SNorm_Z_sumsq(nvar=2, const=9.2)
    #whitebox.SNorm_Z_sumsq(nvar=2, pf_exact=1.0e-6)



# libustka
add('ball_2D')
def ball_2D():
    return whitebox.SNorm_S_ball(nvar=2, r=5)




"""suma velicin plus beta*sqrt(Nvar. )
Pro IID Gaussian ma tohle ind. spol. beta = beta
The same as Linear_nD, but defined via 
beta in sense of reliability index"""
# Z_sum s divokým rozdělením
# pro obyčejný norm dist viz. HyperPlane
add('nataf_sum_2D')
def nataf_sum_2D():
    wt = whitebox.WhiteBox(gew, gm.Z_sum(nvar=2, beta_exact=np.sqrt(2)))
    wt.pf_exact = 0.000495
    wt.Nsim = int(10e6)
    wt.pf_exact_method = 'MC'
    return wt


# soucin velicin plus nějaká konstanta 
# g= X1 * X2 * X3 * X4 + c
add('prod_2D_1')
add('prod_2D_5')
def prod_2D_1():
    return whitebox.WhiteBox(f, gm.Z_prod(const=1))
def prod_2D_5():
    return whitebox.WhiteBox(f, gm.Z_prod(const=5))

gm_z_prod = gm.Z_prod(const=5)

def proxy_prod(input_sample):
    # očekávam, že get_R_coordinates mně vrátí 2D pole
    sample = gm.get_R_coordinates(input_sample, 2)
    x, y = sample.T
    
    # osudná podmínka
    mask = np.atleast_1d(np.sign(x)==np.sign(y)).astype(bool)
    #č mrdáme na kontrolu. současný startup candybox vytvoří vždycky
    input_sample.candybox.proxy = mask
    sweet_sample = input_sample
    #sweet_sample = CandyBox(input_sample, proxy=mask)
            
    # zatím, pro jednoduchost, předpokladáme,
    # že dostaváme vzorky po jednom
    if np.all(mask):
        # nevíme vůbec, co to je za funkci
        # ale veříme, že víme co tam bude
        g = np.full(len(sweet_sample), 1)
        # s praznejm podpísem odmítá
        return samplebox.SampleBox(sweet_sample, g, 'proxy_prod')
        
    else: # deme počítat, bez b
        true_sample = gm_z_prod(sweet_sample)
        # padelame pospís
        true_sample.gm_signature = 'proxy_prod'
        return true_sample

# wrap
proxy_prod.get_2D_R_boundary = gm_z_prod.get_2D_R_boundary

add('proxy_prod_2D_5')
def proxy_prod_2D_5():
    return whitebox.WhiteBox(f, proxy_prod)


# min velicin plus nějaká konstanta 
# g= min(X1, X2, X3, X4) + c
add('min_2D')
def min_2D():
    return whitebox.Gaussian_Z_min(ndim=2, const=5)



# g = np.sum(np.exp(-(sample**2)), axis=1) + self._const
add('nataf_supexp_2D')
def nataf_supexp_2D():
    return whitebox.WhiteBox(gew, gm.Z_sumexp(const=-0.003))
add('nataf_sumexp_2D')
def nataf_sumexp_2D():
    wt = whitebox.WhiteBox(gewm, gm.Z_sumexp(const=-0.003))
    wt.pf_exact = 1.2e-05
    wt.Nsim = int(10e6)
    wt.pf_exact_method = 'MC'
    return wt


"""
c = 0.5 # wave amplitude in Gaussian space
d = 3.0 # average of sine fiunction in Gaussian space
k = 6   # number of sine waves (design points)
"""
add('sinball_2D')
def sinball_2D():
    return whitebox.WhiteBox(f, gm.S_ballSin2D(c=0.5, d=3.0, k=6))





# g = np.sum(sample**2, axis=1) - self._const
add('nataf_sumsq_2D')
def nataf_sumsq_2D():
    return whitebox.WhiteBox(gew, gm.Z_sumsq(const=9.2))




# obecný S_ball bez výpočtu pf
add('nataf_ball_2D')
def nataf_ball_2D():
    wt = whitebox.WhiteBox(gew, gm.S_ball(r=5))
    wt.pf_exact = 0.012403
    wt.Nsim = int(10e6)
    wt.pf_exact_method = 'MC'
    return wt

add('natafm_ball_2D')
def natafm_ball_2D():
    wt = whitebox.WhiteBox(gewm, gm.S_ball(r=5))
    wt.pf_exact = 0.006812
    wt.Nsim = int(10e6)
    wt.pf_exact_method = 'MC'
    return wt
    
add('beta_circle_2D')
def beta_circle_2D():
    wt = whitebox.WhiteBox(gb, gm.ConicSection(l=1.5, e=0, c=(0.5,0), sign=-1))
    wt.pf_exact = 0.001622
    wt.Nsim = int(10e6)
    wt.pf_exact_method = 'MC'
    return wt


# kruznicka
add('circle_2D')
def circle_2D():
    return whitebox.WhiteBox(f, gm.ConicSection(l=2, e=0, teta=-np.pi/4, c=(-3,1), sign=1))


# Fajvka
# člověk se tu bez půllitry nevýzná
# viz. conic_section_boundaries_test.py pro inspiraciju
add('five_2D')
def five_2D():
    return whitebox.WhiteBox(h, gm.ConicSection(l=.1, e=1.1, teta=-np.pi/4, c=(-3,1), sign=1))


# Exp_P
# g = y - 1./np.exp(x)**5
# g = y - self._k/np.exp(x)**self._pow
# k tomuhlenstomu by bylo možně výtvořiť bílou skřiňku (pro výpočet pf)
add('exp_P_2D')
def exp_P_2D():
    return whitebox.WhiteBox(u, gm.Exp_P(k=1., pow=5))

add('nataf_exp_2D')
def nataf_exp_2D():
    return whitebox.WhiteBox(gew, gm.Exp_P(k=1., pow=-0.5))


# Sin2D
# g = self._kx * x + self._ky * y + np.sin(self._kxsin*x) + self._const
add('sin_2D')
def sin_2D():
    return whitebox.WhiteBox(f, gm.Sin2D(kx=-1/4., ky=-1, kxsin=5, const=5))





# Prod_FourBetas
# g = beta^2/2 - |x1 * x2|
#whitebox.WhiteBox(f, gm.Prod_FourBetas(beta=2.0))



""" BlackSwan2D
a = 2.0 # boundary for x1
b = 5.0 # boundary for x2
y = np.where(sim[:,0] <= a, sim[:,0], sim[:,1])
# pro x1 <= a   y = x1
# pro x1 >  a   y = x2
g = b - y # failure for b<y"""
#whitebox.WhiteBox(f, gm.BlackSwan2D(a=2.0, b=5.0))



""" Metaballs2D
# sebemenší parametrizace
y1 = 4/9*(x1 + 2  )**2 + 1/25 * (x2    )**2 
y2 = 1/4*(x1 - 2.5)**2 + 1/25 * (x2-0.5)**2 
g = 30.0/( y1**2 + 1.0 ) + 20.0/( y2**2 + 1.0 ) - self._const"""
#whitebox.WhiteBox(f, gm.Metaballs2D(const=5))




""" Logistic2D
# sebemenší parametrizace
y1 = self._c1 - x1
y2 = self._c2 + x2
y3 = 1.0/(1+np.exp(-2.0*y2)) - 0.5

if self.easy_version:
    g = np.minimum(y1,y2)  # easy version for SuS
else:
    g = np.minimum(y1,y3)  # difficult version for SuS"""
#whitebox.WhiteBox(f, gm.Logistic2D(c1=5, c2=4, easy_version=True))




""" CosExp2D
# sebemenší parametrizace
s = self._s
# g = cos((np.exp(-xm-s  ))*xm)   * np.exp(-(x +s  )/3)
g = np.cos( ( np.exp(-sample[:,0] - s ) )*sample[:,0])   * np.exp( -(sample[:,0] + s  )/3 )  """
#whitebox.WhiteBox(f, gm.CosExp2D(s=5))



""" FourBranch2D
g1 = k1 + 0.1*(x1 - x2)**2 - (x1 + x2)/np.sqrt(2)
g2 = k1 + 0.1*(x1 - x2)**2 + (x1 + x2)/np.sqrt(2)
g3 = (x1 - x2) + k2/np.sqrt(2)
g4 = (x2 - x1) + k2/np.sqrt(2) #č byl tu překlep v jednom članku
g = np.min((g1, g2, g3, g4), axis=0)"""
#whitebox.WhiteBox(f, gm.FourBranch2D(k1=3, k2=7))



