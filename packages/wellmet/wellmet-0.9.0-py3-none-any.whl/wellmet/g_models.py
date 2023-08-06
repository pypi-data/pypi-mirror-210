#!/usr/bin/env python
# coding: utf-8


"""
 cs: 
 

 en: 
 data should be pandas compatible, i.e. 
 nsim, nvar = data.shape

g_model returns SampleBox object, which actually contains:
1. what-was-on-input
2. values of perfomance function
AND 3. so called gm_signature - some string to identify data
and do not let them be mixed up.
Currently WhiteBox treat as gm_signature __name__ attribute (free functions has it),
otherwise repr(). Classes supposed to define __repr__ function for correct work.

Fence off!
Some of performance functions (g_models) are able to draw
failure region boundary, in this case 
.get_2D_R_boundary(nrod, xlim, ylim) is defined.
    nrod - number of "rods" in "fencing"
    xlim, ylim describes your viewport, plotting terminal, whatever
    g_model uses these parameters only for inspiration,
    g_model is allowed to ignore them
    xlim = (xmin, xmax)
    ylim = (ymin, ymax)
    
    returns tuple (or list) of R samples
    
    
    
"""

import numpy as np
from .f_models import Ingot
from .samplebox import SampleBox


class GetQuadrantBoundary2D:
    """
    sebemenší pomocná třida pro vykreslení hranici L tvaru
    """
    def __init__(self, center_point=(0,0), quadrant='I'):
        """
        quadrants also сэрегъёс-compatible
        #### CORNERS 2D #####
        # print(сэрегъёс)
        # numbering:
        #    2  |  3
        #  -----|-----
        #    0  |  1
        """
        self.center_point = center_point
        self.quadrant = quadrant
        
    def __call__(self, nrod=100, xlim=(-5,5), ylim=(-5,5)):
        xc, yc = self.center_point
        xmin = min(*xlim, xc-1)
        xmax = max(*xlim, xc+1)
        ymin = min(*ylim, yc-1)
        ymax = max(*ylim, yc+1)
            
        nrod = int(nrod/2)
            # mně nic hezčího prostě nenapadá(
        if self.quadrant in ('I', 3):
            xbound = np.append(np.full(nrod, xc), np.linspace(xc, xmax, nrod, endpoint=True))
            ybound = np.append(np.linspace(ymax, yc, nrod, endpoint=True), np.full(nrod, yc))
        elif self.quadrant in ('II', 2):
            xbound = np.append(np.linspace(xmin, xc, nrod, endpoint=True), np.full(nrod, xc))
            ybound = np.append(np.full(nrod, yc), np.linspace(yc, ymax, nrod, endpoint=True))
        elif self.quadrant in ('III', 0):
            xbound = np.append(np.linspace(xmin, xc, nrod, endpoint=True), np.full(nrod, xc))
            ybound = np.append(np.full(nrod, yc), np.linspace(yc, ymin, nrod, endpoint=True))
        else: # self.quadrant in ('IV', 1):
            xbound = np.append(np.full(nrod, xc), np.linspace(xc, xmax, nrod, endpoint=True))
            ybound = np.append(np.linspace(ymin, yc, nrod, endpoint=True), np.full(nrod, yc))
        
    
        # sample compatible
        # малы транспонировать кароно? Озьы кулэ!
        bound_R = np.vstack((xbound, ybound)).T
        # tuple of tuple
        return (Ingot(bound_R),)
        
        

def get_R_coordinates(input_sample, envar=0):
    """
    Tohle je pomocná funkce, vrácí g_modelům numpy 2d pole s daty
    
    envar - zadavejte, pokud chcete zkontrolovat 
    počet náhodných proměnných
    envar like estimated number of variables
    """
    # is it sample object?
    try:
        if envar > 0 and input_sample.nvar != envar:
            raise ValueError('%sD data expected, but %sD sample given'% (envar, input_sample.nvar))
        else:
            return input_sample.R
        
    # it is not an sample object, 
    # but maybe numpy can handle this?
    except AttributeError:
        sample = np.atleast_2d(np.array(input_sample))
        # invar like input number of variables
        nsim, invar = sample.shape
        if envar > 0 and invar != envar:
            raise ValueError('%sD data expected, but %sD sample given'% (envar, invar))
        else:
            return sample




class Linear_nD:
    """
    Class takes for inicialization tuple of betas 
    Betas are coeffitients in sense of Regression Analysis
    
     g= a*X1 + b*X2 + c
     becames
     gm = Linear_nD(betas=(a,b,c))
     gm(samples)
     gm.get_2D_R_boundary(nrod, xlim) returns
     xbounds a ybounds zabalené do tuplu, ty zabalené do listu
    """
    
    def __init__(self, betas):
        self._betas = betas
        
        # sign
    def __repr__(self):
        return 'Linear_nD(%s)' % repr(self._betas)
        
    def __call__(self, input_sample):
        selfnvar = len(self._betas)-1
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample, selfnvar)
        # teďkom zasahujeme přímo do tohoto pole
        sim = sample.copy()
        for i in range(selfnvar):
            sim[:,i] = sim[:,i]*self._betas[i]
        g = np.sum(sim, axis=1) + self._betas[-1]
        return SampleBox(input_sample, g, repr(self))
    
    
    
    # Fence off!
    def get_2D_R_boundary(self, nrod=100, xlim=(-5,5), *args):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        
        xbound = np.linspace(xlim[0], xlim[1], nrod, endpoint=True)
    
        selfnvar = len(self._betas)-1
        # g= a*X1 + b*X2 + 0*X3 + 0*X4 + ... + c
        a = self._betas[0]
        b = self._betas[1]
        c = self._betas[-1]
        
        # 1D je spíše vtip
        if selfnvar == 1:
            return (-c/a)
        else:
            # sample compatible
            # малы транспонировать кароно? Озьы кулэ!
            bound_R = np.array((xbound, -c/b + (-a/b)*xbound)).T
            # tuple of tuple
            return (Ingot(bound_R),)
        
        
class X1:
    """
    suma velicin plus beta*sqrt(Nvar. )
    Pro IID Gaussian ma tohle ind. spol. beta = beta
    The same as Linear_nD, but defined via 
    beta in sense of reliability index
    """
    def __init__(self, beta_exact):
        self._beta_exact = beta_exact
        
    # sign
    def __repr__(self):
        return 'X1(%s)' % repr(self._beta_exact)
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample)
        g = -sample[:, 0] + self._beta_exact
        return SampleBox(input_sample, g, repr(self))

    # Fence off!
    def get_2D_R_boundary(self, nrod=100, xlim=(-5,5), ylim=(-5,5), *args):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        
        bound_R = np.empty((nrod, 2))
        bound_R[:, 0] = self._beta_exact
        bound_R[:, 1] = np.linspace(ylim[0], ylim[1], nrod, endpoint=True)
        # tuple of tuple
        return (Ingot(bound_R),)
        
        
class AbsX1:
    """
    suma velicin plus beta*sqrt(Nvar. )
    Pro IID Gaussian ma tohle ind. spol. beta = beta
    The same as Linear_nD, but defined via 
    beta in sense of reliability index
    """
    def __init__(self, beta_exact):
        self._beta_exact = beta_exact
        
    # sign
    def __repr__(self):
        return 'X1(%s)' % repr(self._beta_exact)
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample)
        g = -np.abs(sample[:, 0]) + self._beta_exact
        return SampleBox(input_sample, g, repr(self))

    # Fence off!
    def get_2D_R_boundary(self, nrod=100, xlim=(-5,5), ylim=(-5,5), *args):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        
        bound_R = np.empty((nrod, 2))
        bound_R[:, 0] = self._beta_exact
        bound_R[:, 1] = np.linspace(ylim[0], ylim[1], nrod, endpoint=True)
        # tuple of tuple
        return (Ingot(bound_R), Ingot(-bound_R))
        
        
class Z_sum:
    """
    suma velicin plus beta*sqrt(Nvar. )
    Pro IID Gaussian ma tohle ind. spol. beta = beta
    The same as Linear_nD, but defined via 
    beta in sense of reliability index
    """
    def __init__(self, nvar, beta_exact):
        self._nvar = nvar
        self._beta_exact = beta_exact
        
    # sign
    def __repr__(self):
        return 'Z_sum(%s, %s)' % (repr(self._nvar), repr(self._beta_exact))
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample, self._nvar)
        g = np.sum(sample, axis=1) + self._beta_exact * np.sqrt(self._nvar) 
        return SampleBox(input_sample, g, repr(self))

    # Fence off!
    def get_2D_R_boundary(self, nrod=100, xlim=(-5,5), *args):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        
        xbound = np.linspace(xlim[0], xlim[1], nrod, endpoint=True)
    
        # g= a*X1 + b*X2 + 0*X3 + 0*X4 + ... + c
        a = 1
        b = 1
        c = self._beta_exact * np.sqrt(self._nvar) 
        
        # sample compatible
        # малы транспонировать кароно? Озьы кулэ!
        bound_R = np.array((xbound, -c/b + (-a/b)*xbound)).T
        # tuple of tuple
        return (Ingot(bound_R),)

      
        
class Z_prod:
    """
    soucin velicin plus nějaká konstanta 
    # g= s * (X1 * X2 * X3 * X4 + c )
    """
    # tenhle model ani nvar si neukladá, tohle vůbec neřeší
    def __init__(self, const=0, sign=1):
        self._const = const
        self._sign = sign
        
    # sign
    def __repr__(self):
        return 'Z_prod(%s, %s)' % (self._const, self._sign)
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample)
        g = self._sign * (np.prod(sample, axis=1) + self._const)
        return SampleBox(input_sample, g, repr(self))

    # Fence off!
    def get_2D_R_boundary(self, nrod=100, *args):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        # g= X1 * X2 + c
        #
        # a^2 = 2*X^2 
        # a=b= X * sqrt(2)
        # a^2 = 2*c
        # r = a*b / np.sqrt(b**2 * np.cos(phi)**2 - a**2 * np.sin(phi)**2)
        
        c = self._const
        _c = np.sign(c)
        #č náš oblibený trik - hranici nakreslime pomoci polárních souřádnic
        phi = np.linspace(0.25*np.pi, (0.25+_c/2)*np.pi, nrod , endpoint=False)[1:]
        r = np.sqrt(2*c / (np.sin(phi)**2 - np.cos(phi)**2))
        bound_x_left = r * np.cos(phi+np.pi/4)
        bound_y_left = r * np.sin(phi+np.pi/4)
        
        phi = np.linspace(-0.75*np.pi, (_c/2-0.75)*np.pi, nrod , endpoint=False)[1:]
        r = np.sqrt(2*c / (np.sin(phi)**2 - np.cos(phi)**2))
        bound_x_right = r * np.cos(phi+np.pi/4)
        bound_y_right = r * np.sin(phi+np.pi/4)
        
        # sample compatible
        # малы транспонировать кароно? Озьы кулэ!
        bound_R_left = np.array((bound_x_left, bound_y_left)).T
        bound_R_right = np.array((bound_x_right, bound_y_right)).T
        # tuple of samples
        return (Ingot(bound_R_left), Ingot(bound_R_right))
             
        

class Z_hyperbola:
    """
    soucin velicin plus nějaká konstanta 
    # g= s * (X1 * X2 * X3 * X4 + c )
    """
    # tenhle model ani nvar si neukladá, tohle vůbec neřeší
    def __init__(self, const=0):
        self._const = const
        
    # sign
    def __repr__(self):
        return 'Z_hyperbola(%s)' % self._const
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample)
        g = self._const - np.all(sample > 0, axis=1) * np.prod(sample, axis=1)
        return SampleBox(input_sample, g, repr(self))

    # Fence off!
    def get_2D_R_boundary(self, nrod=100, *args):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        # g= X1 * X2 + c
        #
        # a^2 = 2*X^2 
        # a=b= X * sqrt(2)
        # a^2 = 2*c
        # r = a*b / np.sqrt(b**2 * np.cos(phi)**2 - a**2 * np.sin(phi)**2)
        
        c = -self._const
        _c = -1
        #č náš oblibený trik - hranici nakreslime pomoci polárních souřádnic
        phi = np.linspace(0.25*np.pi, (0.25+_c/2)*np.pi, nrod , endpoint=False)[1:]
        r = np.sqrt(2*c / (np.sin(phi)**2 - np.cos(phi)**2))
        bound_x_left = r * np.cos(phi+np.pi/4)
        bound_y_left = r * np.sin(phi+np.pi/4)
        
#        phi = np.linspace(-0.75*np.pi, (_c/2-0.75)*np.pi, nrod , endpoint=False)[1:]
#        r = np.sqrt(2*c / (np.sin(phi)**2 - np.cos(phi)**2))
#        bound_x_right = r * np.cos(phi+np.pi/4)
#        bound_y_right = r * np.sin(phi+np.pi/4)
        
        # sample compatible
        # малы транспонировать кароно? Озьы кулэ!
        bound_R_left = np.array((bound_x_left, bound_y_left)).T
        #bound_R_right = np.array((bound_x_right, bound_y_right)).T
        # tuple of samples
        return (Ingot(bound_R_left), ) #Ingot(bound_R_right))


class Z_min:
    """
    min velicin plus nějaká konstanta 
    # g= min(X1, X2, X3, X4) + c
    """
    def __init__(self, const):
        self._const = const
        self.get_2D_R_boundary = GetQuadrantBoundary2D(center_point=(-const,-const), quadrant='I')
        
    # sign
    def __repr__(self):
        return 'Z_min(%s)' % repr(self._const)
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample)
        g = np.min(sample, axis=1) + self._const
        return SampleBox(input_sample, g, repr(self))
    
    # samotná "volaná" se určí v __init__
    # trik aby se nezabindila
    @staticmethod
    def get_2D_R_boundary(): return None
        

class Z_max:
    """
    max velicin plus nějaká konstanta 
    # g= max(X1, X2, X3, X4) + c
    """
    def __init__(self, const):
        self._const = const
        self.get_2D_R_boundary = GetQuadrantBoundary2D(center_point=(-const,-const), quadrant='III')
        
    # sign
    def __repr__(self):
        return 'Z_max(%s)' % repr(self._const)
        
    def __call__(self, input_sample):
        #č očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample)
        g = np.max(sample, axis=1) + self._const
        return SampleBox(input_sample, g, repr(self))
    
    #č samotná "volaná" se určí v __init__
    #č trik aby se nezabindila
    @staticmethod
    def get_2D_R_boundary(): return None


class Z_sumexp:
    """
    """
    def __init__(self, const):
        self._const = const
        
    # sign
    def __repr__(self):
        return 'Z_sumexp(%s)' % repr(self._const)
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample)
        g = np.sum(np.exp(-(sample**2)), axis=1) + self._const
        return SampleBox(input_sample, g, repr(self))

    # Fence off!
    def get_2D_R_boundary(self, nrod=100, xlim=(-5,5), ylim=(-5,5)):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        
        
        def e_bound(xbound): return np.sqrt(-np.log(-self._const - np.exp(-xbound**2)))
        
        # let's mirror about (s,s) point
        # 0 = 2*e^(-s^2)+c
        # log(-c/2) = -s^2
        # s = sqrt(-log(-c/2))
        s = np.sqrt(-np.log(-self._const/2))
        xmin = min(*xlim, -s-1)
        xmax = max(*xlim, s+1)
        ymin = min(*ylim, -s-1)
        ymax = max(*ylim, s+1)
        
        xb_1eft = np.linspace(xmin, -s, nrod, endpoint=False)
        xb_right = np.linspace(xmax, s, nrod, endpoint=False)
        yb_up = np.linspace(s, ymax, nrod)
        yb_down = np.linspace(-s, ymin, nrod)
        
        
        # numerace je náhodná
        bound_R_1 = np.array((np.append(xb_1eft, -e_bound(yb_up)), np.append(e_bound(xb_1eft), yb_up))).T
        bound_R_2 = np.array((np.append(xb_1eft, -e_bound(yb_down)), np.append(-e_bound(xb_1eft), yb_down))).T
        bound_R_3 = np.array((np.append(xb_right, e_bound(yb_up)), np.append(e_bound(xb_right), yb_up))).T
        bound_R_4 = np.array((np.append(xb_right, e_bound(yb_down)), np.append(-e_bound(xb_right), yb_down))).T
        
        # sample compatible
        # tuple of samples
        return (Ingot(bound_R_1), Ingot(bound_R_2), Ingot(bound_R_3), Ingot(bound_R_4))
              
        


class S_ballSin2D:
    """
    c = 0.5 # wave amplitude in Gaussian space
    d = 3.0 # average of sine fiunction in Gaussian space
    k = 6   # number of sine waves (design points)
    """
    def __init__(self, c, d, k):
        self._c = c
        self._d = d
        self._k = k
        
    # sign
    def __repr__(self):
        return 'S_ballSin2D(%s,%s,%s)' % (self._c, self._d, self._k)
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample, 2)
        
        R2 = np.sum(np.square(sample), axis=1)
        R = np.sqrt(R2)
        phi = np.arctan2(sample[:,1] , sample[:,0])  #arctan2(y,x)
        rmax = self._c * np.sin(self._k * phi) + self._d
        g = rmax - R 
        return SampleBox(input_sample, g, repr(self))

    # Fence off!
    def get_2D_R_boundary(self, nrod=100, *args):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        
        phi = np.linspace(0, 6.283185307, nrod , endpoint=True)
        r = self._c * np.sin(self._k * phi) + self._d
        bound_x = r * np.cos(phi)
        bound_y = r * np.sin(phi)
        
        # sample compatible
        # малы транспонировать кароно? Озьы кулэ!
        bound_R = np.array((bound_x, bound_y)).T
        # tuple of samples
        return (Ingot(bound_R),)


class Z_sumsq:
    """
    """
    def __init__(self, const):
        self._const = const
        
    # sign
    def __repr__(self):
        return 'Z_sumsq(%s)' % repr(self._const)
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample)
        g = np.sum(sample**2, axis=1) - self._const
        return SampleBox(input_sample, g, repr(self))

    # Fence off!
    def get_2D_R_boundary(self, nrod=100, *args):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        
        phi = np.linspace(0, 2*np.pi, nrod , endpoint=True)
        r = np.sqrt(self._const)
        bound_x = r * np.cos(phi)
        bound_y = r * np.sin(phi)
        
        # sample compatible
        # малы транспонировать кароно? Озьы кулэ!
        bound_R = np.array((bound_x, bound_y)).T
        # tuple of samples
        return (Ingot(bound_R),)



class S_ball:
    """
    Find 10 differences with Z_sumsq
    """
    def __init__(self, r):
        self._r = r
        
    # sign
    def __repr__(self):
        return 'S_ball(%s)' % repr(self._r)
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample)
        R2 = np.sum(np.square(sample), axis=1)
        g = self._r**2 - R2
        return SampleBox(input_sample, g, repr(self))

    # Fence off!
    def get_2D_R_boundary(self, nrod=100, *args):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        phi = np.linspace(0, 6.283185307, nrod, endpoint=True)
        r = self._r
        bound_x = r * np.cos(phi)
        bound_y = r * np.sin(phi)
        
        # sample compatible
        # малы транспонировать кароно? Озьы кулэ!
        bound_R = np.array((bound_x, bound_y)).T
        # tuple of samples
        return (Ingot(bound_R),)


class ConicSection:
    """
    """
    def __init__(self, l, e, teta=0, c=(0,0), sign=1):
        self._l = l
        self._e = e
        self._teta = teta
        self._c = c
        self._sign = sign
        
    # sign
    def __repr__(self):
        return 'ConicSection(%s, %s, %s, %s, %s)' % (repr(self._l), repr(self._e), repr(self._teta), repr(self._c), repr(self._sign))
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample)
        x_i, y_i, *__ = (*sample.T,)
        x = x_i - self._c[0]
        y = y_i - self._c[1]
        phi = np.arctan2(y, x)# zde musí bejt to obracené pořádí
        
        r = np.sqrt(np.square(x) + np.square(y))
        r_bound = abs(self._l / (1 - self._e * np.cos(phi-self._teta)))
        g = self._sign * (r - r_bound)
        return SampleBox(input_sample, g, repr(self))

    # Fence off!
    def get_2D_R_boundary(self, nrod=100, *args):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        if self._e == 1:
            phi = np.linspace(self._teta, 6.283185307+self._teta, nrod, endpoint=False)[1:]
        else:
            phi = np.linspace(0, 6.283185307, nrod, endpoint=True)
            
        r_bound = abs(self._l / (1 - self._e * np.cos(phi-self._teta)))
        
        bound_x = (r_bound * np.cos(phi)) + self._c[0]
        bound_y = (r_bound * np.sin(phi)) + self._c[1]
        
        # sample compatible
        # малы транспонировать кароно? Озьы кулэ!
        bound_R = np.array((bound_x, bound_y)).T
        # tuple of samples
        return (Ingot(bound_R),)


class Exp_P:
    """
        g = y - 1./np.exp(x)**5
    """
    def __init__(self, k=1., pow=5):
        self._k = k
        self._pow = pow
        
    # sign
    def __repr__(self):
        return 'Exp_P(%s, %s)' % (self._k, self._pow)
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample, 2)
        
        x = sample[:,0]
        y = sample[:,1]
        g = y - self._k/np.exp(x)**self._pow
        return SampleBox(input_sample, g, repr(self))

    # Fence off!
    def get_2D_R_boundary(self, nrod=100, xlim=(-5,5), *args):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        
        xbound = np.linspace(xlim[0], xlim[1], nrod, endpoint=True)
        
        bound_y = self._k/np.exp(xbound)**self._pow
        
        # sample compatible
        # малы транспонировать кароно? Озьы кулэ!
        bound_R = np.array((xbound, bound_y)).T
        # tuple of samples
        return (Ingot(bound_R),)
            
            
class Sin2D:
    """
    """
    def __init__(self, kx=-1/4., ky=-1, kxsin=5, const=5):
        self._kx = kx
        self._ky = ky
        self._kxsin = kxsin
        self._const = const
        
    # sign
    def __repr__(self):
        return 'Sin2D(%s, %s, %s, %s)' % (self._kx, self._ky, self._kxsin, self._const)
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample, 2)
        
        x = sample[:,0]
        y = sample[:,1]
        g = self._kx * x + self._ky * y + np.sin(self._kxsin*x) + self._const
        return SampleBox(input_sample, g, repr(self))

    # Fence off!
    def get_2D_R_boundary(self, nrod=100, xlim=(-5,5), *args):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        xbound = np.linspace(xlim[0], xlim[1], nrod, endpoint=True)
        
        bound_y = -(self._kx * xbound  + np.sin(self._kxsin * xbound) + self._const) / self._ky
        
        # sample compatible
        # малы транспонировать кароно? Озьы кулэ!
        bound_R = np.array((xbound, bound_y)).T
        # tuple of samples
        return (Ingot(bound_R),) 



class Prod_FourBetas:
    """
    g = beta^2/2 - |x1 * x2|
    """
    def __init__(self, beta=2.0):
        self._beta = beta
        
    # sign
    def __repr__(self):
        return 'Prod_FourBetas(beta=%s)' % repr(self._beta)
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample)
        
        g = self._beta**2/2.0 - np.prod(np.abs(sample), axis=1)
        return SampleBox(input_sample, g, repr(self))

    # Fence off!
    def get_2D_R_boundary(self, nrod=100, xlim=(-5,5), ylim=(-5,5)):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        # zde vynechal abs(), ale úpravil znaménka dolů
        # don't ask me why. Ачим но уг тодӥськы.
        def e_bound(xbound): return self._beta**2/2 / xbound
        
        # let's mirror about (s,s) point
        # 0 = beta^2/2 - s^2
        # beta^2/2 = s^2
        # s = beta/sqrt(2)
        s = self._beta / np.sqrt(2)
        xmin = min(*xlim, -s-1)
        xmax = max(*xlim, s+1)
        ymin = min(*ylim, -s-1)
        ymax = max(*ylim, s+1)
        
        xb_1eft = np.linspace(xmin, -s, nrod, endpoint=False)
        xb_right = np.linspace(xmax, s, nrod, endpoint=False)
        yb_up = np.linspace(s, ymax, nrod)
        yb_down = np.linspace(-s, ymin, nrod)
        
        
        # numerace je náhodná. Je tu hračka se znaménky.
        bound_R_1 = np.array((np.append(xb_1eft, -e_bound(yb_up)), np.append(-e_bound(xb_1eft), yb_up))).T
        bound_R_2 = np.array((np.append(xb_1eft, e_bound(yb_down)), np.append(e_bound(xb_1eft), yb_down))).T
        bound_R_3 = np.array((np.append(xb_right, e_bound(yb_up)), np.append(e_bound(xb_right), yb_up))).T
        bound_R_4 = np.array((np.append(xb_right, -e_bound(yb_down)), np.append(-e_bound(xb_right), yb_down))).T
        
        # sample compatible
        # tuple of samples
        return (Ingot(bound_R_1), Ingot(bound_R_2), Ingot(bound_R_3), Ingot(bound_R_4))
        
        
        
class BlackSwan2D:
    """
        a = 2.0 # boundary for x1
        b = 5.0 # boundary for x2
        y = np.where(sim[:,0] <= a, sim[:,0], sim[:,1])
        # pro x1 <= a   y = x1
        # pro x1 >  a   y = x2
        g = b - y # failure for b<y
    """
    def __init__(self, a=2.0, b=5.0):
        self._a = a
        self._b = b
        if a<b:
            self.get_2D_R_boundary = GetQuadrantBoundary2D(center_point=(a, b), quadrant='I')
        
    # sign
    def __repr__(self):
        return 'BlackSwan2D(%s, %s)' % (self._a, self._b)
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample, 2)
        
        y = np.where(sample[:,0] <= self._a, sample[:,0], sample[:,1])
        g = self._b - y # failure for b<y
        return SampleBox(input_sample, g, repr(self))


    # samotná "volaná" se určí v __init__
    # trik aby se nezabindila
    @staticmethod
    def get_2D_R_boundary(*args, **kwargs): 
        # jako kdyby .get_2D_R_boundary nebyla vůbec definována.
        raise AttributeError
        


class Metaballs2D:
    """
    """
    def __init__(self, const=5):
        # sebemenší parametrizace
        self._const = const
        
    # sign
    def __repr__(self):
        return 'Metaballs2D(%s)' % repr(self._const)
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample, 2)
        
        x1 = sample[:,0]  
        x2 = sample[:,1]
        
        # auxiliary variables
        y1 = 4/9*(x1 + 2  )**2 + 1/25 * (x2    )**2 
        y2 = 1/4*(x1 - 2.5)**2 + 1/25 * (x2-0.5)**2 
        g = 30.0/( y1**2 + 1.0 ) + 20.0/( y2**2 + 1.0 ) - self._const
        return SampleBox(input_sample, g, repr(self))
    
    
    # Fence off!
    def get_2D_R_boundary(self, nrod=100, *args):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        #č myšlenkou je vygenerovat rovnoměrně spoustu teček v každém směru,
        #č pro každé phi zvolit nejblížší k nule r-ko
        phi = np.linspace(0, 6.283185307, nrod , endpoint=True)
        #č obecná hranice poruchy ӧвӧл :(
        #č tyhle meze vícemené platí jen pro const=5
        r = np.linspace(4, 8, nrod//2 , endpoint=True)
        X = np.atleast_2d(r).T @ np.cos(np.atleast_2d(phi))
        Y = np.atleast_2d(r).T @ np.sin(np.atleast_2d(phi))
        # auxiliary variables
        y1 = 4/9*(X + 2  )**2 + 1/25 * (Y    )**2 
        y2 = 1/4*(X - 2.5)**2 + 1/25 * (Y-0.5)**2 
        g = 30.0/( y1**2 + 1.0 ) + 20.0/( y2**2 + 1.0 ) - self._const
        
        #č nechapu úplně přoč tam není axis=1, ale O, ale to funguje
        arg_r = np.argmin(np.abs(g), axis=0)
        bound_r = r[arg_r]
        
        bound_x = bound_r * np.cos(phi)
        bound_y = bound_r * np.sin(phi)
        
        # sample compatible
        # малы транспонировать кароно? Озьы кулэ!
        bound_R = np.array((bound_x, bound_y)).T
        # tuple of samples
        return (Ingot(bound_R),)
        
        
class Logistic2D:
    """
    """
    def __init__(self, c1=5, c2=4, easy_version=True):
        # sebemenší parametrizace
        self._c1 = c1
        self._c2 = c2
        self.easy_version = easy_version
        
        # For both versions
        
        self.get_2D_R_boundary = GetQuadrantBoundary2D(center_point=(c1,-c2), quadrant='II')
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample, 2)
        
        x1 = sample[:,0]  
        x2 = sample[:,1]
        
        # auxiliary variables
        y1 = self._c1 - x1
        y2 = self._c2 + x2
        y3 = 1.0/(1+np.exp(-2.0*y2)) - 0.5
        
        if self.easy_version:
            g = np.minimum(y1,y2)  # easy version for SuS
        else:
            g = np.minimum(y1,y3)  # difficult version for SuS
        return SampleBox(input_sample, g, repr(self))
    
    def __repr__(self):
        return 'Logistic2D(%s, %s, easy_version=%s)'%(self._c1, self._c2, self.easy_version)
    
    def pf_expression(self, f_model):
        """
        We trying to say how to calculate pf
        to someone, who will know actual distribution 
        """
        a = f_model.marginals[0].sf(self._c1)
        b = f_model.marginals[1].cdf(-self._c2)
        # subtract the twice calculated intersection
        return a + b - a*b, 'exact solution'
    
    @staticmethod
    def get_2D_R_boundary(): return None
    
        
        
class CosExp2D:
    """
    """
    def __init__(self, s=5):
        # sebemenší parametrizace
        self._s = s
        
    # sign
    def __repr__(self):
        return 'CosExp2D(s=%s)' % repr(self._s)
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample)

        # auxiliary variables
        s = self._s
        # g = cos((np.exp(-xm-s  ))*xm)   * np.exp(-(x +s  )/3)
        g = np.cos( ( np.exp(-sample[:,0] - s ) )*sample[:,0])   * np.exp( -(sample[:,0] + s  )/3 )        
        return SampleBox(input_sample, g, repr(self))
        
    def pf_expression(self, f):
        xs, rad_max = self._get_x()
        sign = np.sign(np.cos(rad_max))
        #sign = (k_max + 1) // 2 - 1
        xs.reverse()
        print(xs)
        cdfs = f.marginals[0].cdf(xs)
        print(cdfs)
        if sign > 0:
            pf = 0
        else:
            pf = 1
        for cdf in cdfs:
            pf += cdf * sign
            sign *= -1
        
        #print(pf)
        return pf, "series calculation"
        
    def _get_x(self, n=10, steps=10):
        ## log(np.pi/4) == -x - s + log(x)
        ## log(rad) + s == -x + log(x)
        ## x-log(x) = -log(rad) - s
        
        #rad = exp(-x-s)*x
        #log(rad/x) = -x -s
        #x = -log(rad/x) - s
        
        # d_rad/dx = -exp(-x-s)*x + exp(-x-s)
        # d_rad/dx = exp(-x-s) * (1-x)
        
        ## d2/dx2 = exp(-x-s) * (x-1) - exp(-x-s)
        ## d2/dx2 = exp(-x-s) * (x-2)
        
        rad_max = np.exp(-self._s - 1)
        #print(rad_max)
        k_max = np.floor(rad_max / np.pi - 1/2)
        k = k_max
        #x = f.marginals[0].ppf(1e-200)
        rad = (k - n - 1 + 1/2) * np.pi
        #x = rad / np.exp(-self._s)
        x = -np.log(abs(rad)) - self._s
        xs = []
        
        for i in range(-n, 2):
            #print(rad)
            for __ in range(steps): # 10 out to be enough for everybody
                x = x + (rad  / np.exp(-x-self._s) - x) / (1-x)
                #print(x)
            xs.append(x)
            rad = (k+i + 1/2) * np.pi
        return xs, rad_max
        
    # Fence off!
    def get_2D_R_boundary(self, nrod=100, xlim=(-5,5), ylim=(-5,5)):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        
        # it is not mine
        #xa = -4.05229846333861
        #xb = -4.95067172463682
        #xc = -5.37859367619679
        #xd = -5.66345816541508
        #xe = -5.87765022259327
        #xf = -6.04950202015156
        #xg = -6.19309680892552
        
        # ikska
        #xes = (xa, xb, xc, xd, xe, xf, xg)
        xes, __rad_max = self._get_x()
        
        boundaries = []
        ymin, ymax = ylim
        
        for x in xes:
            xbound = np.full(nrod, x)
            ybound = np.linspace(ymin, ymax, nrod, endpoint=True)
            # sample compatible
            # малы транспонировать кароно? Озьы кулэ!
            bound_R = np.vstack((xbound, ybound)).T
            boundaries.append(Ingot(bound_R))
            
        
        return boundaries    
            
        



class FourBranch2D:
    """
    Four branch system
    """
    def __init__(self, k1=3, k2=7):
        self.k1 = k1
        self.k2 = k2
        
    # sign
    def __repr__(self):
        return 'FourBranch2D(k1=%s, k2=%s)' % (self.k1, self.k2)
        
    def __call__(self, input_sample):
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample)

        k1, k2 = self.k1, self.k2
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample, 2)
        x1, x2 = sample[:,0], sample[:,1]
        g1 = k1 + 0.1*(x1 - x2)**2 - (x1 + x2)/np.sqrt(2)
        g2 = k1 + 0.1*(x1 - x2)**2 + (x1 + x2)/np.sqrt(2)
        g3 = (x1 - x2) + k2/np.sqrt(2)
        g4 = (x2 - x1) + k2/np.sqrt(2) #č byl tu překlep v jednom članku
        g = np.min((g1, g2, g3, g4), axis=0)
        return SampleBox(input_sample, g, repr(self))
        
    # Fence off!
    def get_2D_R_boundary(self, nrod=100, *args, **kwargs):
        """
        Fence off!
        nrod - number of rods in fencing
        """
        
        k1, k2 = self.k1, self.k2
        sqrt2 = np.sqrt(2)
        
        m = k1/sqrt2 + k2**2/20/sqrt2
        x1_1 = -m - k2/2/sqrt2
        x1_2 = m - k2/2/sqrt2
        
        
        #č nrod je na každou větev
        xbound_1 = np.linspace(x1_1, x1_2, nrod, endpoint=False)
        ybound_1 = xbound_1 + k2/sqrt2
        
        
        #č naša milovaná parabolka v pootočených souřadnicích
        xbound_2_ = np.linspace(-k2/2, k2/2, nrod, endpoint=False)
        ybound_2_ = xbound_2_**2/5 + k1
        
        xbound_2 = (xbound_2_ + ybound_2_) / sqrt2
        ybound_2 = (-xbound_2_ + ybound_2_) / sqrt2
        
        xbound = np.hstack((xbound_1, xbound_2, -xbound_1, -xbound_2))
        ybound = np.hstack((ybound_1, ybound_2, -ybound_1, -ybound_2))
        
        
        # sample compatible
        # малы транспонировать кароно? Озьы кулэ!
        bound_R = np.array((xbound, ybound)).T
        # tuple of samples
        return (Ingot(bound_R),) 



class PassiveVehicleSuspension:
    """
    """
    def __init__(self, V=10, A=0.15915, b_0=0.27, m=0.8158, M=3.2633, g=981):
        #self.constants = [V, A/2/np.pi, b_0, m, M, g]
        self.constants = [V, A, b_0, m, M, g]
        
    # sign
    def __repr__(self):
        return 'PassiveVehicleSuspension(%s, %s, %s, %s, %s, %s)' % (*self.constants,)
        
    def __call__(self, input_sample):
        V, A, b_0, m, M, g = self.constants
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample, 3)
        c, c_k, k = sample[:,0], sample[:,1], sample[:,2]
        K1 = (np.pi * m * V * A) / (b_0 * k * g**2)
        C1 = c_k / (m + M)
        C2 = c / M
        C3 = c**2 / (m * M)
        C4 = c_k * k**2 /(m * M**2)
        G1 = 1 - K1 * ((C1-C2)**2 + C3 + C4)
        #G2 = 1 - 7.6394 / (4000 * (M*g)**(-1.5) * c - 1)
        G2 = 4000 * (M*g)**(-1.5) * c - 8.6394 
        #G3 = 1 - 0.5 / np.sqrt(M * g)  / np.sqrt(k**2 * c_k / c / (M + m) + c)
        G3 = 2* np.sqrt(M * g)  * np.sqrt(k**2 * c_k / c / (M + m) + c) - 1
        G4 = c_k  - (g * (M + m))**0.877 
        print(G1, G2, G3, G4)
        return SampleBox(input_sample, np.min((G1, G2, G3, G4), axis=0), repr(self))



#
# Free functions
#


def quadratic(input_sample):
    selfnvar = 2
    # očekávam, že get_R_coordinates mně vrátí 2D pole
    sample = get_R_coordinates(input_sample, selfnvar)
    x1, x2 = sample[:,0], sample[:,1]
    g = 3 - x1**4/33 - x2
    return SampleBox(input_sample, g, 'quadratic')

def quadratic_R_boundary(nrod=210, xlim=(-5,5), *args):
        boundaries = []
        x_min, x_max = xlim
        x1 = np.linspace(x_min, x_max, nrod, endpoint=True)
        x2 = 3 - x1**4/33
        
        bound_R_1 = np.vstack(( x1, x2)).T
        boundaries.append(Ingot(bound_R_1))
        return boundaries    

quadratic.get_2D_R_boundary = quadratic_R_boundary



# AK-MCS An active learning reliability method combining kriging
def modified_rastrigin(input_sample):
    selfnvar = 2
    # očekávam, že get_R_coordinates mně vrátí 2D pole
    sample = get_R_coordinates(input_sample, selfnvar)
    
    g = 10 - np.sum(sample**2 - 5 * np.cos(2 * np.pi * sample), axis=1)
    return SampleBox(input_sample, g, 'modified_rastrigin')


# Papaioannou. Sequental importance sampling
# for structural reliability analysis
def noisy_lsf(input_sample):
    selfnvar = 6
    # očekávam, že get_R_coordinates mně vrátí 2D pole
    sample = get_R_coordinates(input_sample, selfnvar)
    
    g = np.sum(sample * [1, 2, 2, 1, -5, -5] + 0.001 * np.sin(100 * sample), axis=1)
    return SampleBox(input_sample, g, 'noisy_lsf')

def single_spring_nonlinear_oscilator(input_sample):
    selfnvar = 5
    # očekávam, že get_R_coordinates mně vrátí 2D pole
    sample = get_R_coordinates(input_sample, selfnvar)
    m, c, r, F1, t1 = sample.T
    # I don't care about physical meaningfullness
    # and I don't care if frequency is less than zero
    w0 = np.sqrt(c / m)
    g = 3 * r - np.abs(2 * F1 / m / w0**2 * np.sin(w0 * t1 / 2))
    return SampleBox(input_sample, g, 'single_spring_nonlinear_oscilator')
        
# DOI:10.1016/j.strusafe.2004.11.001
# Beneﬁt of splines and neural networks in simulation based
# structural reliability analysis
def nonlinear_oscilator(input_sample):
    selfnvar = 6
    # očekávam, že get_R_coordinates mně vrátí 2D pole
    sample = get_R_coordinates(input_sample, selfnvar)
    m, c1, c2, r, F1, t1 = sample.T
    # I don't care about physical meaningfullness
    # and I don't care if frequency is less than zero
    w0 = np.sqrt((c1 + c2) / m)
    g = 3 * r - np.abs(2 * F1 / m / w0**2 * np.sin(w0 * t1 / 2))
    return SampleBox(input_sample, g, 'nonlinear_oscilator')    
        
        
def piecewise_2D_linear(input_sample):
        selfnvar = 2
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample, selfnvar)
        x1, x2 = sample[:,0], sample[:,1]
        g1 = np.where(x1 > 3.5, 4-x1, 0.85-0.1*x1)
        g2 = np.where(x2 > 2, 0.5-0.1*x2, 2.3-x2)
        g = np.min((g1,g2), axis=0)
        return SampleBox(input_sample, g, 'piecewise_2D_linear')

# boundary
piecewise_2D_linear.get_2D_R_boundary = GetQuadrantBoundary2D(center_point=(4,5), quadrant='III')
piecewise_2D_linear.pf_expression = lambda fm, a=4, b=5: (fm.marginals[0].sf(a) + fm.marginals[1].sf(b) - fm.marginals[0].sf(a)*fm.marginals[1].sf(b), 'exact solution')


       
        
def non_chi_squares(input_sample):
        selfnvar = 2
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample, selfnvar)
        x1, x2 = sample[:,0], sample[:,1]
        g = 0.1 * (52 - 1.5 * x1**2 - x2**2)
        return SampleBox(input_sample, g, 'non_chi_squares')


# boundary for non_chi_squares (Breitung with pareto tail)
def non_chi_squares_R_boundary(nrod=210, *args):
     
        boundaries = []
        y = np.linspace(-np.sqrt(52), np.sqrt(52), nrod, endpoint=True)
        x = + np.sqrt(2*(52-y**2)/3)
        bound_R_1 = np.vstack(( x, y)).T
        bound_R_2 = np.vstack((-x, y)).T
        boundaries.append(Ingot(bound_R_1))
        boundaries.append(Ingot(bound_R_2))
        return boundaries    

non_chi_squares.get_2D_R_boundary = non_chi_squares_R_boundary







def branin_2D(input_sample):
        """
        Rescaled Branin function
        """
        selfnvar = 2
        # očekávam, že get_R_coordinates mně vrátí 2D pole
        sample = get_R_coordinates(input_sample, selfnvar)
        x1, x2 = sample[:,0], sample[:,1]
        g = 80 - ((15*x2 - 5/(4*np.pi**2)*(15*x1-5)**2 + 5/np.pi*(15*x1-5)-6)**2 + 10*(1-1/8/np.pi)*np.cos(15*x1-5) + 10)
        return SampleBox(input_sample, g, 'branin_2D')



def neverfall(input_sample):
    g = np.full(len(input_sample), 1, dtype=np.int8)
    return SampleBox(input_sample, g, 'neverfall')


