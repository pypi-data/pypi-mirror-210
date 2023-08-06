#!/usr/bin/env python
# coding: utf-8


"""
 cs: 
 

 en: 

"""

import numpy as np
from scipy import stats
import copy

class WellMetError(ValueError):
    pass

# alpha atribut beztak veřejný, ale tato funkce ještě provadí normalizaci a kontrolu
def set_alpha(f_model, input_alpha):
    alpha = np.atleast_1d(input_alpha).reshape(-1)
    if len(alpha) != f_model.nvar:
        raise WellMetError
    else:
        f_model.alpha = alpha / stats.gmean(alpha)

class Ingot:
    """
    Prazdná třida pro "nevypalené" vzorky, tj. bez přiřazeného rozdělení
    """
    def __init__(self, data, attr='R'):
        self.attr = attr
        try:
            self.data = np.atleast_2d(getattr(data, attr))
        except AttributeError:
            self.data = np.atleast_2d(data)
        
        
    def __repr__(self):
        return "%s(np.%s, '%s')"%('Ingot', repr(self.data), self.attr)
        
    def __str__(self):
        return str(self.data)
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, slice):
        self_copy = copy.copy(self)
        # robim kopiu z _data, nebo ne?
        self_copy.data = np.atleast_2d(self.data[slice,:]) #.copy()
        return self_copy
        
        
    def __getattr__(self, attr):
        if attr == 'f_model':
            return self
        # Рекурсилы пезьдэт!
        elif attr in ('attr', 'data'):
            raise AttributeError(attr)
        elif attr == 'nvar':
            nsim, nvar = self.data.shape
            return nvar
        elif attr == 'nsim':
            return len(self.data)
            
        # гулять так гулять
        elif attr == self.attr:
            return self.data
            
        raise AttributeError(attr)
      
        
        # vstupné vzorky jsou implicitně R, 
        # nikoliv z prostoru tohoto krámu
    def add_sample(self, sample, space='R'):
        # first of all, are you one of us?
        if space == self.attr:
            # does sample is another sample object? 
            # zde nechcu, aby spadlo
            try:
                self.data = np.vstack((self.data, getattr(sample, self.attr)))
            except AttributeError:
                self.data = np.vstack((self.data, sample))
            
        # no, actually
        else:
            # does sample is another sample object? 
            # self.data = np.vstack((self.data, getattr(sample, self.attr)))
            # ale zde chcu 
            # (aby spadlo)
            raise WellMetError
            
        
    # drobná pomucka
    def new_sample(f, sample=None, space='R'):  
        return Ingot(sample, space) # too easy








class SNorm:
    __slots__ = ('G', '_U', '_pdf_G', 'alpha')
    """
    Standard Gauss distribution
    """
    @classmethod
    def _fromdata(cls, G, U=None, pdf_G=None, alpha=1):
        f = super().__new__(cls)
        f.G = G
        f._U = U
        f._pdf_G = pdf_G
        f.alpha = alpha
        return f
    
    @classmethod
    def from_G(cls, G, alpha=1):
        f = super().__new__(cls)
        f.G = G
        f._U = None
        f._pdf_G = None
        f.alpha = alpha
        return f
        
    @classmethod
    def from_U(cls, U, alpha=1):
        f = super().__new__(cls)
        f._U = U
        f.G = stats.norm.ppf(U)
        f._pdf_G = None
        f.alpha = alpha
        return f
    
    def __init__(self, nvar, alpha=1):
        self.G = np.empty((0, nvar), dtype=float)
        self._U = None
        self._pdf_G = None
        self.alpha = alpha
        
     # nemusím duplikovat a dědit 
    set_alpha = set_alpha
    
    def __repr__(self):
        return "%s(%s, %s)"%('SNorm', self.nvar, repr(self.alpha))
        
    def __str__(f):
        return "SNorm sample: " + str(f.R)
        
    def __call__(self, ns=0):
        if ns:
            return SNorm.from_G(np.random.randn(ns, self.nvar), self.alpha)
        #else:
        return SNorm(self.nvar, self.alpha)
        
    def __len__(self):
        return len(self.G)
    
    def __getitem__(self, slice):
        G = np.atleast_2d(self.G[slice]) 
        
        if self._U is not None:
            U = np.atleast_2d(self._get_U()[slice]) 
        else:
            U = None
                
        if self._pdf_G is not None:
            pdf_G = np.atleast_1d(self._get_pdf()[slice]) 
        else:
            pdf_G = None
                
        return SNorm._fromdata(G, U, pdf_G, self.alpha)
        
        
    def __getattr__(f, attr):
        if attr == 'f_model':
            return f
        elif attr in ('R', 'Rn', 'GK'):
            return f.G
        elif attr in ('aR', 'aRn', 'aGK', 'aG'):
            return f.G * f.alpha
        elif attr in ('P', 'U'):
            return f._get_U()
        elif attr in ('aP', 'aU'):
            return f.U * f.alpha
        elif attr == 'nvar':
            return f.G.shape[1]
        elif attr == 'nsim':
            return len(f.G)
        elif attr == 'marginals':
            return [stats.norm for __ in range(f.nvar)]
        elif attr == 'cor':
            return np.diag([1 for __ in range(f.nvar)])
            
        # hustoty
        # I'm considering to deprecate attribute access
        elif attr[:4] == 'pdf_':
            return f.pdf(attr[4:])
            
        raise AttributeError(attr)
        
    
    def _get_U(self):
        _U = self._U
        G = self.G
        if _U is None:
            U = stats.norm.cdf(G)
            self._U = U
            return U
            
        len_U = len(_U)
        if len_U == len(G):
            return _U
        else:
            U = np.empty_like(G)
            U[:len_U] = _U
            U[len_U:] = stats.norm.cdf(G[len_U:])
            self._U = U
            return U
            
            
    def _get_pdf(self):
        _pdf_G = self._pdf_G
        G = self.G
        if _pdf_G is None:
            pdf_G = self._calculate_pdf(G)
            self._pdf_G = pdf_G
            return pdf_G
            
        len_pdf = len(_pdf_G)
        nsim = len(G)
        if len_pdf == nsim:
            return _pdf_G
        else:
            pdf_G = np.empty(nsim, dtype=float)
            pdf_G[:len_pdf] = _pdf_G
            pdf_G[len_pdf:] = self._calculate_pdf(G[len_pdf:])
            self._pdf_G = pdf_G
            return pdf_G
            
            
    @staticmethod           
    def _calculate_pdf(G):
        return np.prod(stats.norm.pdf(G), axis=1)
            
            
    def _add_U(self, U_to_add):
        "č method přeppokladá, že self.G ještě není dotčen"
        n = len(U_to_add)
        nsim = self.nsim
        U = np.empty((nsim + n, self.nvar), dtype=float)
        U[nsim:] = U_to_add
        
        _U = self._U
        G = self.G
        if _U is None:
            U[:nsim] = stats.norm.cdf(G)
        else:
            len_U = len(_U)
            if len_U == len(G):
                U[:nsim] = _U
            else:
                U[:len_U] = _U
                U[len_U:nsim] = stats.norm.cdf(G[len_U:])
            
        self._U = U
            
        
    def add_sample(f, input_sample, space='R'):
        """
        Adds coordinates from input sample
        """
        try: # is sample another f_model object? 
            sample = getattr(input_sample, space)
        except AttributeError:
            # no, it is just coordinates array
            sample = input_sample
        
        sample = np.atleast_2d(sample)
        isim, ivar = np.shape(sample) # input sim, var
        if ivar != f.nvar:
            raise WellMetError('%sD data expected, but %sD sample given'% (f.nvar, ivar))
        
        if isim == 0:
            return None
        
        nsim = f.nsim
        G = np.empty((nsim + isim, f.nvar), dtype=float)
        G[:nsim] = f.G
        
        # new piece of code "alpha"-related
        if space in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            sample = sample / f.alpha
            space = space[1:]
        
        if space in ('R', 'Rn', 'GK', 'G'):
            G[nsim:] = sample
            f.G = G
        elif space in ('P', 'U'):
            #č _add_U() přeppokladá, že self.G ještě není dotčen
            f._add_U(sample)
            G[nsim:] = stats.norm.ppf(sample)
            f.G = G
        else:
            raise WellMetError('SNorm: unknown space %s' % space)
            
        
    #č tohle už není "drobná pomucka"
    #č to je jedná z funkcí, která běží 30% času
    def new_sample(f, input_sample=None, space='R', extend=False):
        """
        Returns new f_model object with the same distribution and with coordinates from 'sample' taken
        """
        if input_sample is None:
            return SNorm(f.nvar, f.alpha)
        
        try: # does sample is another f_model object? 
            sample = getattr(input_sample, space)
        except AttributeError:
            # no, it is just coordinates array
            sample = input_sample
        
        sample = np.atleast_2d(sample)
        isim, ivar = np.shape(sample) # input sim, var
        if extend:
            to_extend = sample
            sample = np.zeros((isim, f.nvar))
            sample[:,:ivar] = to_extend
        elif ivar != f.nvar:
            raise WellMetError('%sD data expected, but %sD sample given'% (f.nvar, ivar))
            
        
        # new piece of code "alpha"-related
        if space in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            sample = sample / f.alpha
            space = space[1:]
        
        
        if space in ('R', 'Rn', 'GK', 'G'):
            return SNorm.from_G(sample, f.alpha)
        elif space in ('P', 'U'):
            return SNorm.from_U(sample, f.alpha)
        else:
            raise WellMetError('SNorm: unknown space %s' % space)
            
    
    
    
    
    def pdf(f, space='R'):
        """
        Returns own probability densities in the given space
        """
        if space in ('R', 'Rn', 'GK', 'G'):
            return f._get_pdf()
        elif space in ('P', 'U'):
            ones = np.ones(f.nsim)
            mask = np.all((f.U >= 0) & (f.U <= 1), axis=1)
            if not np.all(mask):
                ones[~mask] = 0
            return ones
        elif space in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            return f.pdf(space[1:]) / np.prod(f.alpha)
            
        else:   
            raise WellMetError('Unknown space %s' % space)
            
        
        
    def sample_pdf(f, input_sample, space='R'):
        """
        Calculates probability density for the given external sample in the given space.
        Function intended for the case no transformation needed. 
        Otherwise new f_sample should be instanciated.
        """
        
        # does sample is another f_model object? 
        # кинлы со zase кулэ?
        try:
            sample = getattr(input_sample, space)
        except AttributeError:
            # no
            sample = np.atleast_2d(input_sample)
            
        
        if space in ('R', 'Rn', 'GK', 'G'):
            pdfs_R = stats.norm.pdf(sample)
            return np.prod(pdfs_R, axis=pdfs_R.ndim-1)
            
        elif space in ('P', 'U'):
            ones = np.ones(len(sample))
            mask = np.all((sample >= 0) & (sample <= 1), axis=1)
            if not np.all(mask):
                ones[~mask] = 0
            return ones
            
        # new piece of code "alpha"-related
        elif space in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            return f.sample_pdf(sample / f.alpha, space=space[1:]) / np.prod(f.alpha)
            
        else:   
            raise WellMetError('Unknown space %s' % space)



class Norm:
    __slots__ = ('G', '_U', '_pdf_G', 'mean', 'std', 'alpha')
    """
    Normal distribution
    """
    @classmethod
    def _fromdata(cls, G, U, pdf_G, mean, std, alpha=1):
        f = super().__new__(cls)
        f.G = G
        f._U = U
        f._pdf_G = pdf_G
        f.mean = mean
        f.std = std
        f.alpha = alpha
        return f
    
    @classmethod
    def from_G(cls, G, mean, std, alpha=1):
        f = super().__new__(cls)
        f.G = G
        f.mean = mean
        f.std = std
        f._U = None
        f._pdf_G = None
        f.alpha = alpha
        return f
        
    @classmethod
    def from_U(cls, U, mean, std, alpha=1):
        f = super().__new__(cls)
        f._U = U
        f.G = stats.norm.ppf(U)
        f.mean = mean
        f.std = std
        f._pdf_G = None
        f.alpha = alpha
        return f
    
    def __init__(self, mean, std, alpha=1):
        assert len(mean) == len(std)
        self.mean = mean
        self.std = std
        
        self.G = np.empty((0, len(mean)), dtype=float)
        self._U = None
        self._pdf_G = None
        self.alpha = alpha
        
     # nemusím duplikovat a dědit 
    set_alpha = set_alpha
    
    def __repr__(self):
        return "%s(%s, %s, %s)"%('Norm', self.mean, self.std, repr(self.alpha))
        
    def __str__(f):
        return "Norm sample: " + str(f.R)
        
    def __call__(self, ns=0):
        if ns:
            return Norm.from_G(np.random.randn(ns, self.nvar), self.mean, self.std, self.alpha)
        #else:
        return Norm(self.mean, self.std, self.alpha)
        
    def __len__(self):
        return len(self.G)
    
    def __getitem__(self, slice):
        G = np.atleast_2d(self.G[slice]) 
        
        if self._U is not None:
            U = np.atleast_2d(self._get_U()[slice]) 
        else:
            U = None
                
        if self._pdf_G is not None:
            pdf_G = np.atleast_1d(self._get_pdf()[slice]) 
        else:
            pdf_G = None
                
        return Norm._fromdata(G, U, pdf_G, self.mean, self.std, self.alpha)
        
        
    def __getattr__(f, attr):
        if attr == 'f_model':
            return f
        elif attr == 'R':
            sample = f.G * f.std
            sample += f.mean
            return sample
        elif attr in ('Rn', 'GK'):
            return f.G
        elif attr in ('aR', 'aRn', 'aGK', 'aG'):
            return f.G * f.alpha
        elif attr in ('P', 'U'):
            return f._get_U()
        elif attr in ('aP', 'aU'):
            return f.U * f.alpha
        elif attr == 'nvar':
            return len(f.mean)
        elif attr == 'nsim':
            return len(f.G)
        elif attr == 'marginals':
            return [stats.norm(m, s) for m, s in zip(self.mean, self.std)]
        elif attr == 'cor':
            return np.diag([1 for __ in range(f.nvar)])
            
        # hustoty
        # I'm considering to deprecate attribute access
        elif attr[:4] == 'pdf_':
            return f.pdf(attr[4:])
            
        raise AttributeError(attr)
        
    
    def _get_U(self):
        _U = self._U
        G = self.G
        if _U is None:
            U = stats.norm.cdf(G)
            self._U = U
            return U
            
        len_U = len(_U)
        if len_U == len(G):
            return _U
        else:
            U = np.empty_like(G)
            U[:len_U] = _U
            U[len_U:] = stats.norm.cdf(G[len_U:])
            self._U = U
            return U
            
            
    def _get_pdf(self):
        _pdf_G = self._pdf_G
        G = self.G
        if _pdf_G is None:
            pdf_G = self._calculate_pdf(G)
            self._pdf_G = pdf_G
            return pdf_G
            
        len_pdf = len(_pdf_G)
        nsim = len(G)
        if len_pdf == nsim:
            return _pdf_G
        else:
            pdf_G = np.empty(nsim, dtype=float)
            pdf_G[:len_pdf] = _pdf_G
            pdf_G[len_pdf:] = self._calculate_pdf(G[len_pdf:])
            self._pdf_G = pdf_G
            return pdf_G
            
            
    @staticmethod           
    def _calculate_pdf(G):
        return np.prod(stats.norm.pdf(G), axis=1)
            
            
    def _add_U(self, U_to_add):
        "č method přeppokladá, že self.G ještě není dotčen"
        n = len(U_to_add)
        nsim = self.nsim
        U = np.empty((nsim + n, self.nvar), dtype=float)
        U[nsim:] = U_to_add
        
        _U = self._U
        G = self.G
        if _U is None:
            U[:nsim] = stats.norm.cdf(G)
        else:
            len_U = len(_U)
            if len_U == len(G):
                U[:nsim] = _U
            else:
                U[:len_U] = _U
                U[len_U:nsim] = stats.norm.cdf(G[len_U:])
            
        self._U = U
            
        
    def add_sample(f, input_sample, space='R'):
        """
        Adds coordinates from input sample
        """
        try: # is sample another f_model object? 
            sample = getattr(input_sample, space)
        except AttributeError:
            # no, it is just coordinates array
            sample = input_sample
        
        sample = np.atleast_2d(sample)
        isim, ivar = np.shape(sample) # input sim, var
        if ivar != f.nvar:
            raise WellMetError('%sD data expected, but %sD sample given'% (f.nvar, ivar))
        
        if isim == 0:
            return None
        
        nsim = f.nsim
        G = np.empty((nsim + isim, f.nvar), dtype=float)
        G[:nsim] = f.G
        
        # new piece of code "alpha"-related
        if space in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            sample = sample / f.alpha
            space = space[1:]
        
        if space in ('Rn', 'GK', 'G'):
            G[nsim:] = sample
            f.G = G
        elif space == 'R':
            G[nsim:] = sample
            G[nsim:] -= f.mean
            G[nsim:] /= f.std
            f.G = G
        elif space in ('P', 'U'):
            #č _add_U() přeppokladá, že self.G ještě není dotčen
            f._add_U(sample)
            G[nsim:] = stats.norm.ppf(sample)
            f.G = G
        else:
            raise WellMetError('SNorm: unknown space %s' % space)
            
        
    #č tohle už není "drobná pomucka"
    #č to je jedná z funkcí, která běží 30% času
    def new_sample(f, input_sample=None, space='R', extend=False):
        """
        Returns new f_model object with the same distribution and with coordinates from 'sample' taken
        """
        if input_sample is None:
            return Norm(f.mean, f.std, f.alpha)
        
        try: # does sample is another f_model object? 
            sample = getattr(input_sample, space)
        except AttributeError:
            # no, it is just coordinates array
            sample = input_sample
        
        sample = np.atleast_2d(sample)
        isim, ivar = np.shape(sample) # input sim, var
        if extend:
            to_extend = sample
            sample = np.zeros((isim, f.nvar))
            sample[:,:ivar] = to_extend
        elif ivar != f.nvar:
            raise WellMetError('%sD data expected, but %sD sample given'% (f.nvar, ivar))
            
        
        # new piece of code "alpha"-related
        if space in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            sample = sample / f.alpha
            space = space[1:]
        
        
        if space in ('Rn', 'GK', 'G'):
            return Norm.from_G(sample, f.mean, f.std, f.alpha)
        elif space == 'R':
            sample = sample - f.mean
            sample /= f.std
            return Norm.from_G(sample, f.mean, f.std, f.alpha)
        elif space in ('P', 'U'):
            return Norm.from_U(sample, f.mean, f.std, f.alpha)
        else:
            raise WellMetError('SNorm: unknown space %s' % space)
            
    
    
    
    
    def pdf(f, space='R'):
        """
        Returns own probability densities in the given space
        """
        if space in ('Rn', 'GK', 'G'):
            return f._get_pdf()
        elif space == 'R':
            return f._get_pdf() / np.prod(f.std)
        elif space in ('P', 'U'):
            ones = np.ones(f.nsim)
            mask = np.all((f.U >= 0) & (f.U <= 1), axis=1)
            if not np.all(mask):
                ones[~mask] = 0
            return ones
        elif space in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            return f.pdf(space[1:]) / np.prod(f.alpha)
            
        else:   
            raise WellMetError('Unknown space %s' % space)
            
        
        
    def sample_pdf(f, input_sample, space='R'):
        """
        Calculates probability density for the given external sample in the given space.
        Function intended for the case no transformation needed. 
        Otherwise new f_sample should be instanciated.
        """
        
        # does sample is another f_model object? 
        # кинлы со zase кулэ?
        try:
            sample = getattr(input_sample, space)
        except AttributeError:
            # no
            sample = np.atleast_2d(input_sample)
            
        
        if space in ('Rn', 'GK', 'G'):
            pdfs_R = stats.norm.pdf(sample)
            return np.prod(pdfs_R, axis=pdfs_R.ndim-1)
            
        elif space == 'R':
            sample = sample - f.mean
            sample /= f.std
            pdfs_R = stats.norm.pdf(sample)
            return np.prod(pdfs_R, axis=pdfs_R.ndim-1) / np.prod(f.std)
            
        elif space in ('P', 'U'):
            ones = np.ones(len(sample))
            mask = np.all((sample >= 0) & (sample <= 1), axis=1)
            if not np.all(mask):
                ones[~mask] = 0
            return ones
            
        # new piece of code "alpha"-related
        elif space in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            return f.sample_pdf(sample / f.alpha, space=space[1:]) / np.prod(f.alpha)
            
        else:   
            raise WellMetError('Unknown space %s' % space)





class SNormClassic:
    """
    Standard Gauss distribution
    """
    sample_pdf = SNorm.sample_pdf
    
    def __init__(self, nvar, alpha=None):
        self.__nvar = nvar
        # nvar_R + nvar_U + pdf_R
        rowsize = nvar*2 + 1
        # data? takový neslaný nazev...
        # data suppose to be cKDTree compatible, i.e. 
        # nsim, nvar = data.shape
        self._data = np.empty((0, rowsize), dtype=float)
        if alpha is None:
            self.alpha = np.ones(nvar)
        else:
            self.set_alpha(alpha)
        
     # nemusím duplikovat a dědit 
    set_alpha = set_alpha
    
    def __repr__(self):
        return "%s(%s, %s)"%('SNorm', self.__nvar, repr(self.alpha))
        
    def __str__(f):
        return "SNorm sample: " + str(f.R)
        
    def __call__(f, ns=0):
        f_copy = copy.copy(f)
        if ns:
            sample_P = np.random.random((ns, f_copy.nvar))
            sample_R = stats.norm.ppf(sample_P)
                
            pdfs_R = stats.norm.pdf(sample_R)
            pdf_R = np.prod(pdfs_R, axis=1).reshape(-1, 1)
            f_copy._data = np.hstack((sample_R, sample_P, pdf_R))
        else:
            f_copy._data = np.empty((0, f_copy._data.shape[1]), dtype=float)
        return f_copy
        
    def __len__(f):
        return len(f._data)
    
    def __getitem__(f, slice):
        f_copy = copy.copy(f)
        # robim kopiu z _data, nebo ne?
        f_copy._data = np.atleast_2d(f._data[slice,:]) #.copy()
        return f_copy
        
        
    def __getattr__(f, attr):
        if attr == 'f_model':
            return f
        elif attr in ('R', 'Rn', 'GK', 'G'):
            return f._data[:,:f.__nvar]
        elif attr in ('aR', 'aRn', 'aGK', 'aG'):
            return f._data[:,:f.__nvar] * f.alpha
        elif attr in ('P', 'U'):
            return f._data[:,f.__nvar:2*f.__nvar]
        elif attr in ('aP', 'aU'):
            return f._data[:,f.__nvar:2*f.__nvar] * f.alpha
        elif attr == 'nvar':
            return f.__nvar
        elif attr == 'nsim':
            return len(f._data)
        elif attr == 'marginals':
            return [stats.norm for __ in range(f.__nvar)]
        elif attr == 'cor':
            return np.diag([1 for __ in range(f.__nvar)])
            
        # hustoty
        # I'm considering to deprecate attribute access
        elif attr[:4] == 'pdf_':
            return f.pdf(attr[4:])
            
        raise AttributeError(attr)
        
        
       # pro určitou konzistenci. Ne že bych chtěl zamykat dveře v Pythonu
    def __setattr__(f, attr, value):
        if attr in ('_SNorm__nvar','_data', 'alpha'):
            f.__dict__[attr] = value
        else:
            #raise AttributeError('Čo tu robíš?')
            #raise AttributeError('Враг не пройдёт!')
            #raise AttributeError('Иди отсюда!')
            #raise AttributeError('Аслыкъёсы воштыны уг луи!')
            raise AttributeError('Atribute %s of %s object is not writable' % (attr, f.__class__.__name__))
        
        
        
    def add_sample(f, sample, space='R'):
        """
        Adds coordinates from input sample
        """
        newdata = f._parse_sample(sample, space)
        f._data = np.vstack((f._data, newdata))
            
        
    #č tohle už není "drobná pomucka"
    #č to je jedná z funkcí, která běží 30% času
    def new_sample(f, sample=None, space='R', extend=False):
        """
        Returns new f_model object with the same distribution and with coordinates from 'sample' taken
        """
        f_copy = copy.copy(f)
        if sample is None:
            f_copy._data = np.empty((0, f_copy._data.shape[1]), dtype=float)
        else:
            f_copy._data = np.atleast_2d(f._parse_sample(sample, space, extend))
        return f_copy
    
    
    def _parse_sample(f, input_sample, space='R', extend=False):
        # does sample is exactly me?
        if f.__repr__() == input_sample.__repr__():
            newdata = input_sample._data
            
        else:
            try: # does sample is another f_model object? 
                sample = getattr(input_sample, space)
            except AttributeError:
                # no, it is just coordinates array
                sample = input_sample
            
            sample = np.atleast_2d(sample)
            isim, ivar = np.shape(sample) # input sim, var
            if extend:
                to_extend = sample
                sample = np.zeros((isim, f.nvar))
                sample[:,:ivar] = to_extend
            elif ivar != f.nvar:
                raise ValueError('%sD data expected, but %sD sample given'% (f.nvar, ivar))
                
            
            # new piece of code "alpha"-related
            if space in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
                sample = sample / f.alpha
                space = space[1:]
            
            if space in ('R', 'Rn', 'GK', 'G'):
                sample_R = sample
                sample_P = stats.norm.cdf(sample_R)
                
                pdfs_R = stats.norm.pdf(sample_R)
                pdf_R = np.prod(pdfs_R, axis=pdfs_R.ndim-1)
                if pdfs_R.ndim == 2:
                    newdata = np.hstack((sample_R, sample_P, pdf_R.reshape(len(pdf_R), 1)))
                else:
                    newdata = np.hstack((sample_R, sample_P, pdf_R))
                
            elif space in ('P', 'U'):
                sample_P = sample
                sample_R = stats.norm.ppf(sample_P)
                    
                pdfs_R = stats.norm.pdf(sample_R)
                pdf_R = np.prod(pdfs_R, axis=pdfs_R.ndim-1)
                if pdfs_R.ndim == 2:
                    newdata = np.hstack((sample_R, sample_P, pdf_R.reshape(len(pdf_R), 1)))
                else:
                    newdata = np.hstack((sample_R, sample_P, pdf_R))
                    
            else:
                raise ValueError('SNorm: unknown space %s' % space)
            
        return newdata
    
    
    
    
    def pdf(f, space='R'):
        """
        Returns own probability densities in the given space
        """
        if space in ('R', 'Rn', 'GK', 'G'):
            return f._data[:,-1]
        elif space in ('P', 'U'):
            return f.sample_pdf(f, space)
            
        elif space in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            return f.pdf(space[1:]) / np.prod(f.alpha)
            
        else:   
            raise ValueError('Unknown space %s' % space)
            
        
    
        
            
    


class UnCorD: # nic moc nazev, ale je přece lepší nez CommonJointDistribution
    """
    Takes tuple of scipy stats distribution objects
    """
    def __init__(self, marginals, alpha=None):
        self.__marginals = marginals
        # nvar_Rn + nvar_R + nvar_P + nvar_G + pdf_R + pdf_G
        rowsize = len(marginals)*4 + 2
        # data? takový neslaný nazev...
        # data suppose to be cKDTree compatible, i.e. 
        # nsim, nvar** = data.shape
        self._data = np.empty((0, rowsize), dtype=float)
        if alpha is None:
            self.alpha = np.ones(self.nvar)
        else:
            self.set_alpha(alpha)
        
     # nemusím duplikovat a dědit 
    set_alpha = set_alpha
        
    def __repr__(self):
        return "%s(%s, %s)"%('UnCorD', repr(self.__marginals), repr(self.alpha))
        
    def __str__(f):
        return "UnCorD: " + str(f.R)
    
    def __call__(f, ns=0):  
        f_copy = copy.copy(f) # nebo deep?
        f_copy._data = np.empty((0, f_copy._data.shape[1]), dtype=float)
        
        if ns:
            sample_dict = {'P':np.random.random((ns, f_copy.nvar))}
            f._chain(sample_dict)
            pdf_G = np.prod(stats.norm.pdf(sample_dict['G']), axis=1).reshape(-1, 1)
            pdfs_R = [f.marginals[i].pdf(sample_dict['R'][:, i]) for i in range(f.nvar)]
            # je tu fakt axis=0. Dochazí totíž v iterátoru k převracení
            pdf_R = np.prod(pdfs_R, axis=0).reshape(-1, 1)
            # nvar_Rn + nvar_R + nvar_P + nvar_G + pdf_R + pdf_G
            f_copy._data = np.hstack((sample_dict['Rn'], sample_dict['R'], sample_dict['P'], sample_dict['G'], pdf_R, pdf_G))
        return f_copy
    
    def __len__(f):
        return len(f._data)
    
    def __getitem__(f, slice):
        f_copy = copy.copy(f) # nebo deep?
        f_copy._data = np.atleast_2d(f._data[slice,:]) #.copy()
        return f_copy
        
        # dúfám, že tyhle slajsy sa vyplatí
    def __getattr__(f, attr):
        if attr == 'f_model':
            return f
        elif attr == 'Rn':
            return f.__frame(0)
        elif attr == 'R':
            return f.__frame(1)
        elif attr in ('P', 'U'):
            return f.__frame(2)
        elif attr in ('GK', 'G'):
            return f.__frame(3)
            
        elif attr == 'nvar':
            return len(f.__marginals)
        elif attr == 'nsim':
            return len(f._data)
        elif attr == 'marginals':
            return f.__marginals
        elif attr == 'cor':
            return np.diag([1 for __ in range(f.nvar)])
            
        elif attr in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            return getattr(f, attr[1:]) * f.alpha
            
        # hustoty
        # I'm considering to deprecate attribute access
        elif attr[:4] == 'pdf_':
            return f.pdf(attr[4:])
            
        raise AttributeError(attr)
        
    # pro určitou konzistenci. Ne že bych chtěl zamykat dveře v Pythonu
    def __setattr__(f, attr, value):
        if attr in ('_UnCorD__marginals','_data', 'alpha'):
            f.__dict__[attr] = value
        else:
            #raise AttributeError('Аслыкъёсы воштыны уг луи!')
            raise AttributeError('Atribute %s of %s object is not writable' % (attr, f.__class__.__name__))
        
    def __frame(f, i):
        nvar = f.nvar
        sl = slice(i*nvar, (i+1)*nvar)
        return f._data[:,sl]
        
        
    def add_sample(f, sample, space='R'):
        """
        Adds coordinates from input sample
        """
        newdata = f._parse_sample(sample, space)
        f._data = np.vstack((f._data, newdata))
            
        
    #č tohle už není "drobná pomucka"
    #č to je jedná z funkcí, která běží 30% času
    def new_sample(f, sample=None, space='R', extend=False):
        """
        Returns new f_model object with the same distribution and with coordinates from 'sample' taken
        """
        f_copy = copy.copy(f)
        if sample is None:
            f_copy._data = np.empty((0, f_copy._data.shape[1]), dtype=float)
        else:
            f_copy._data = np.atleast_2d(f._parse_sample(sample, space, extend))
        return f_copy
    
    
    def _parse_sample(f, input_sample, space='R', extend=False):
        # isinstance, ne?
        if f.__class__.__name__ == input_sample.__class__.__name__:
            if f.marginals == input_sample.marginals:
                if (space in ('R', 'Rn', 'P', 'GK', 'G', 'U')) or np.all(f.alpha == input_sample.alpha):
                    return input_sample._data
        
        
        # does sample is another f_model object? 
        try:
            sample_ = getattr(input_sample, space)
        except AttributeError:
            # no
            sample_ = input_sample
            
        sample_ = np.atleast_2d(sample_)
        isim, ivar = np.shape(sample_) # input sim, var
        if extend:
            to_extend = sample_
            sample_ = np.zeros((isim, f.nvar))
            sample_[:,:ivar] = to_extend
        elif ivar != f.nvar:
            raise ValueError('%sD data expected, but %sD sample given'% (f.nvar, ivar))
            
        # new piece of code "alpha"-related
        if space in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            sample_ = sample_ / f.alpha
            space = space[1:]        
                
        elif space not in ('R', 'Rn', 'P', 'GK', 'G', 'U'):
            # co jako, mám gettext sem tahnout?!
            raise ValueError('SNorm: zadaný prostor %s mi není znám' % space)
            raise ValueError('SNorm: unknown space %s' % space)
            
            
        if space=='GK':
            space='G'
        elif space=='U':
            space='P'
            
        sample_dict = {space:np.array(sample_, dtype=float).reshape(-1, f.nvar)}
        f._chain(sample_dict)
        pdf_G = np.prod(stats.norm.pdf(sample_dict['G']), axis=1).reshape(-1, 1)
        pdfs_R = [f.marginals[i].pdf(sample_dict['R'][:, i]) for i in range(f.nvar)]
        # je tu fakt axis=0. Dochazí totíž v iterátoru k převracení
        pdf_R = np.prod(pdfs_R, axis=0).reshape(-1, 1)
        # nvar_Rn + nvar_R + nvar_P + nvar_G + pdf_R + pdf_G
        newdata = np.hstack((sample_dict['Rn'], sample_dict['R'], sample_dict['P'], sample_dict['G'], pdf_R, pdf_G))
                    
        return newdata
    
    
     
    def _chain(f, sample_dict):
        # chain tam
        # чаль татысь
        if 'R' not in sample_dict and 'Rn' in sample_dict:
            sample_dict['R'] = np.empty_like(sample_dict['Rn'])
            for i in range(f.nvar):
                sample_dict['R'][:, i] = sample_dict['Rn'][:, i]*f.marginals[i].std() + f.marginals[i].mean()
                
        if 'P' not in sample_dict and 'R' in sample_dict:
            sample_dict['P'] = np.empty_like(sample_dict['R'])
            for i in range(f.nvar):
                sample_dict['P'][:, i] = f.marginals[i].cdf(sample_dict['R'][:, i])
                
        if 'G' not in sample_dict and 'P' in sample_dict:
            sample_dict['G'] = stats.norm.ppf(sample_dict['P'])
        
        # chain sem
        # чаль татчи
        elif 'P' not in sample_dict and 'G' in sample_dict:
            sample_dict['P'] = stats.norm.cdf(sample_dict['G'])
            
        if 'R' not in sample_dict and 'P' in sample_dict:
            sample_dict['R'] = np.empty_like(sample_dict['P'])
            for i in range(f.nvar):
                sample_dict['R'][:, i] = f.marginals[i].ppf(sample_dict['P'][:, i])
                
        if 'Rn' not in sample_dict and 'R' in sample_dict:
            sample_dict['Rn'] = np.empty_like(sample_dict['R'])
            for i in range(f.nvar):
                sample_dict['Rn'][:, i] = (sample_dict['R'][:, i] - f.marginals[i].mean())/f.marginals[i].std()
     
     
    def pdf(f, space='R'):
        """
        Returns own probability densities in the given space
        """
        if space == 'R':
            return f._data[:,-2]
        elif space == 'Rn':
            return f._data[:,-2] * np.prod(list(f.marginals[i].std() for i in range(f.nvar)))
        elif space in ('GK', 'G'):
            return f._data[:,-1]
        elif space in ('P', 'U'):
            return f.sample_pdf(f, space)
            
        elif space in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            return f.pdf(space[1:]) / np.prod(f.alpha)
        
        else:   
            raise ValueError('Unknown space %s' % space)
            
        
        
    def sample_pdf(f, input_sample, space='R'):
        """
        Calculates probability density for the given external sample in the given space.
        Function intended for the case no transformation needed. 
        Otherwise new f_sample should be instanciated.
        """
        
        # does sample is another f_model object? 
        # кинлы со zase кулэ?
        try:
            sample = getattr(input_sample, space)
        except AttributeError:
            # no
            sample = np.atleast_2d(input_sample)
            
        
        if space == 'R':
            pdfs_R = [f.marginals[i].pdf(sample[:, i]) for i in range(f.nvar)]
            # je tu fakt axis=0. Dochazí totíž v iterátoru k převracení
            return np.prod(pdfs_R, axis=0)
                
        elif space == 'Rn':
            sample_Rn = sample
            sample_R = np.empty_like(sample_Rn)
            for i in range(f.nvar):
                sample_R[:, i] = sample_Rn[:, i]*f.marginals[i].std() + f.marginals[i].mean()
            pdf_R = f.sample_pdf(sample_R, space='R')
            return pdf_R * np.prod(list(f.marginals[i].std() for i in range(f.nvar)))
        
        elif space in ('GK', 'G'):
            pdfs_R = stats.norm.pdf(sample)
            return np.prod(pdfs_R, axis=pdfs_R.ndim-1)
            
        elif space in ('P', 'U'):
            return np.where(np.all((sample >= 0) & (sample <= 1), axis=1), 1, 0)
            
        # new piece of code "alpha"-related
        elif space in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            return f.sample_pdf(sample / f.alpha, space=space[1:]) / np.prod(f.alpha)
            
        else:   
            raise ValueError('Unknown space %s' % space)
            





#č je чёртова прорва těch různejch pythonovejch balíků,
#č co ten Natafův model implementujou
#č takže skoro není důvod znovu to psat
#č ale udělám takovou rychlovku
#č kdyby někdo nechtěl tahnout externí závislosti
#č taky zde mám větší kontrolu nad kodem 

class Nataf: # quick'n dirty
    """
    Takes tuple of scipy stats distribution objects
    Note, there is correlation distortion in Nataf model, 
    correlation matrix meant to be in Gaussian space (just easier to implement) 
    """
    def __init__(self, marginals, gauss_cor=None, alpha=None):
        #č zatím nechcu nic kontrolovat. Python to je nebo co?
        self._marginals = marginals
        if gauss_cor is None:
            self._gauss_cor = np.diag([1 for __ in range(self.nvar)])
        else:
            self._gauss_cor = gauss_cor
        # data suppose to be cKDTree compatible, i.e. 
        # nsim, nvar = data.shape
        self.G = np.empty((0, len(marginals)), dtype=float)
        if alpha is None:
            self.alpha = np.ones(self.nvar)
        else:
            self.set_alpha(alpha)
        
     # nemusím duplikovat a dědit 
    set_alpha = set_alpha
    #č jsou ještě alfy, ty mě ale nezajimají
    #č G-čko taky ne
    _pdf_attrs = ('pdf_Rn', 'pdf_R', 'pdf_P', 'pdf_GK', 'pdf_G', 'pdf_U')
    _length_attrs = ('Rn', 'R', 'P', 'GK', 'U',\
             'pdf_Rn', 'pdf_R', 'pdf_P', 'pdf_GK', 'pdf_G', 'pdf_U')
             
    _attrs = ('_pdf_left_part', '_inv_cor', '_L', '_inv_L', '_pdf_Rn_coef')
        
    def __repr__(self):
        return "%s(%s, %s, %s)"%('Nataf', self._marginals, self._gauss_cor, self.alpha)
        
    def __str__(f):
        return "Nataf: " + str(f.R)
    
    def __call__(self, ns=0):  
        f_copy = self.__class__(self._marginals, self._gauss_cor, self.alpha)
        
        if ns:
            f_copy.G = np.random.randn(ns, len(self._marginals))
        return f_copy
    
    def __len__(f):
        return len(f.G)
    
    def __getitem__(f, slice):
        f_copy = f.__class__(f._marginals, f._gauss_cor, f.alpha)
        f_copy.G = np.atleast_2d(f.G[slice])
        for _attr in ('_Rn', '_R', '_P', '_GK', '_U'):
            try:
                setattr(f_copy, _attr, np.atleast_2d(getattr(f, _attr)[slice]))
            except:
                pass
        for attr in f._pdf_attrs:
            _attr = '_' + attr
            try:
                setattr(f_copy, _attr, np.atleast_1d(getattr(f, _attr)[slice]))
            except:
                pass
        return f_copy
        
        # dúfám, že tyhle slajsy sa vyplatí
    def __getattr__(f, attr):
        if attr == 'f_model':
            return f
        elif attr in f._length_attrs:
            return f._get_lengthy_attr('_' + attr)
        elif attr in f._attrs:
            return f._get_attr(attr)
            
        elif attr == 'nvar':
            return len(f._marginals)
        elif attr == 'nsim':
            return len(f.G)
        elif attr == 'marginals':
            return f._marginals
        elif attr == 'cor':
            return self._gauss_cor
            
        elif attr in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            return getattr(f, attr[1:]) * f.alpha
            
        #č hustoty
        #č alfy. podle mě nemusí být částé
        elif attr[:4] == 'pdf_':
            return f.pdf(attr[4:])
            
        raise AttributeError(attr)
        
            
        
    #č tohle už není "drobná pomucka"
    #č to je jedná z funkcí, která běží 30% času
    def new_sample(self, sample=None, space='R', extend=False):
        """
        Returns new f_model object with the same distribution 
        and coordinates taken from the 'sample' 
        """
        f_copy = self.__class__(self._marginals, self._gauss_cor, self.alpha)
        if sample is not None:
            f_copy.add_sample(sample, space, extend)
        return f_copy
    
    
    def add_sample(f, input_sample, space='R', extend=False):
        "Adds coordinates from the input sample"
        
        # does sample is another f_model object? 
        try:
            sample_ = getattr(input_sample, space)
        except AttributeError:
            # no
            sample_ = input_sample
            
        sample_ = np.atleast_2d(sample_)
        isim, ivar = np.shape(sample_) # input sim, var
        if extend:
            to_extend = sample_
            sample_ = np.zeros((isim, f.nvar))
            sample_[:,:ivar] = to_extend
        elif ivar != f.nvar:
            raise ValueError('%sD data expected, but %sD sample given'% (f.nvar, ivar))
            
        # new piece of code "alpha"-related
        if space in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            sample_ = sample_ / f.alpha
            space = space[1:]        
                
                
            
        if space=='Rn':
            f._put_attr(space, sample_)
            sample_ = f.Rn_to_R(sample_)
            space = 'R'
            
        if space=='R':
            f._put_attr(space, sample_)
            sample_ = f.R_to_P(sample_)
            space = 'P'
        
        if space=='P':
            f._put_attr(space, sample_)
            sample_ = f.P_to_GK(sample_)
            space = 'GK'
        
        if space=='GK':
            f._put_attr(space, sample_)
            sample_ = f.GK_to_G(sample_)
            space = 'G'
        
        
        if space=='U':
            f._put_attr(space, sample_)
            sample_ = f.U_to_G(sample_)
            space = 'G'
            
        
        if space=='G':
            f.G = np.vstack((f.G, sample_))
        else:
            # fail. Nothing happend...  
            #č co jako, mám gettext sem tahnout?!
            raise ValueError('Nataf: zadaný prostor %s mi není znám' % space)
            raise ValueError('Nataf: unknown space %s' % space)
    
    
    
    
    #č doufám, že se nic tu nepokazí
    def _put_attr(f, attr, value):
        "attr supposed to Rn, R, P, GK or U"
        if len(f.G):
            current = getattr(f, attr)
            setattr(f, '_' + attr, np.vstack((current, value)))
        else:
            setattr(f, '_' + attr, value)
    
    def Rn_to_R(f, Rn):
        R = np.empty_like(Rn)
        for i in range(f.nvar):
            R[:, i] = Rn[:, i]*f.marginals[i].std() + f.marginals[i].mean()
        return R
    
    def R_to_P(f, R):
        P = np.empty_like(R)
        for i in range(f.nvar):
            P[:, i] = f.marginals[i].cdf(R[:, i])
        return P
        
    def P_to_GK(f, P):
        return stats.norm.ppf(P)
        
    def GK_to_G(f, GK):
        return (f._inv_L @ GK.T).T
        
    def U_to_G(f, U):
        return stats.norm.ppf(U)
    
    #č náhrada čejnu
    def _get_lengthy_attr(f, _attr):
        """č zatím přdpokládám, že jako vstup bere něco jako _R, _Rn, _GK atd."""
        chain_function = getattr(f, '_get' + _attr)
        if _attr in f.__dict__:
            current = getattr(f, _attr)
            length = len(current)
            if length < len(f.G):
                append = chain_function(slice(length,len(f.G)))
                if length:
                    if _attr[:5] == '_pdf_':
                        current = np.hstack((current, append))
                    else:
                        current = np.vstack((current, append))
                else:
                    current = append
                setattr(f, _attr, current)
                return current
            else: #č nechce se mi dělat-robiť kontroly
                #č když je currebt z jakéhokoliv důvodu větší jak f.G
                #č tak vratím jej uživateli, ať s tím drbá won! 
                return current
        
        #č nejsem jist, jestli ta matika (tady, v čejnu) se nezlobí
        #č když ji strkám na výpočet prazdné matice
        elif len(f.G)==0:
            if _attr[:5] == '_pdf_':
                return np.empty(0) 
            else:
                return np.empty_like(f.G)
        else:
            current = chain_function(slice(0,len(f.G)))
            setattr(f, _attr, current)
            return current
    
    def _get_attr(f, current_attr):
        """č zatím přdpokládám, že jako vstup bere něco jako _L, _inv_L atd."""
        chain_function = getattr(f, '_get' + current_attr)
        #č předpokladám, že tyhle blbosti stačí spočítat jenom jednou
        current = chain_function()
        setattr(f, current_attr, current)
        return current
    
    def _get_pdf_left_part(f):
        denominator = np.power(2*np.pi, f.nvar/2) * np.sqrt(np.linalg.det(f._gauss_cor))
        return 1/denominator
            
    def _get_inv_cor(self):
        return np.linalg.inv(self._gauss_cor)
        
    def _get_L(self):
        return np.linalg.cholesky(self._gauss_cor)
        
    def _get_inv_L(self):
        return np.linalg.inv(self._L)
        
    def _get_pdf_Rn_coef(f):
        return np.prod(list(f.marginals[i].std() for i in range(f.nvar)))
            
    
    #č np.empty_like není úplně bezpěčný
    #č ať se ti nestane to, že se objeví nějaká celočiselná matice!
    #č Zatim všecho řetezí od f.G, který je explicitně s plovoucí tečkou
    #č takže zatim asi v cajku
    
    #č vidím, že numpy žere aj None jako slice. Tím lepe!
    #č žere, ale přidává dimenzi
    
#    def _get_sliced(f, attr, slice):
#       if slice is None:
#           return getattr(f, attr)
#       else:
#           return getattr(f, attr)[slice]
    
    def _get_Rn(f, slice=None):
        R = f.R[slice]
        Rn = np.empty_like(R)
        for i in range(f.nvar):
            Rn[:, i] = (R[:, i] - f.marginals[i].mean())/f.marginals[i].std()
        return Rn
            
    def _get_R(f, slice=None):
        P = f.P[slice]
        R = np.empty_like(P)
        for i in range(f.nvar):
            R[:, i] = f.marginals[i].ppf(P[:, i])
        return R
            
    def _get_P(f, slice=None):
        GK = f.GK[slice]
        P = stats.norm.cdf(GK)
        return P
    
    def _get_GK(f, slice=None):
        G = f.G[slice]
        GK = (f._L @ G.T).T
        return GK
        
    def _get_U(f, slice=None):
        G = f.G[slice]
        U = stats.norm.cdf(G)
        return U
            
            
    def _get_pdf_U(f, slice=None):
        U = f.U[slice]
        pdf_U = np.where(np.all((U >= 0) & (U <= 1), axis=1), 1, 0)
        return np.nan_to_num(pdf_U, copy=False)
        
    
    def _get_pdf_G(f, slice=None):
        G = f.G[slice]
        pdf_G = np.prod(stats.norm.pdf(G), axis=1)
        return np.nan_to_num(pdf_G, copy=False)   
        
    def _get_pdf_GK(f, slice=None):
        GK = f.GK[slice]
        right_part = np.exp(-0.5 * np.sum((GK @ f._inv_cor)*GK, axis=1))
        pdf_GK = f._pdf_left_part * right_part
        return np.nan_to_num(pdf_GK, copy=False)  
        
    def _get_pdf_P(f, slice=None):
        P = f.P[slice]
        GK = f.GK[slice]
        pdf_GK = f.pdf_GK[slice]
        pdf_GK_indep = np.prod(stats.norm.pdf(GK), axis=1)
        pdf_P = pdf_GK/pdf_GK_indep
        pdf_P = np.where(np.all((P >= 0) & (P <= 1), axis=1), pdf_P, 0)
        return np.nan_to_num(pdf_P, copy=False)  
        
    def _get_pdf_R(f, slice=None):
        pdf_P = f.pdf_P[slice]
        R = f.R[slice]
        pdfs_R = [f.marginals[i].pdf(R[:, i]) for i in range(f.nvar)]
        # je tu fakt axis=0. Dochazí totíž v iterátoru k převracení
        pdf_R = np.prod(pdfs_R, axis=0) * pdf_P
        return np.nan_to_num(pdf_R, copy=False)
        
    def _get_pdf_Rn(f, slice=None):
        pdf_R = f.pdf_R[slice]
        pdf_Rn = pdf_R * f._pdf_Rn_coef
        return np.nan_to_num(pdf_Rn, copy=False)
        
    
    def pdf(f, space='R'):
        """
        Returns own probability densities in the given space
        """
        if space in ('Rn', 'R', 'P', 'GK', 'G', 'U'):
            return f._get_lengthy_attr('_pdf_' + space)
            
        elif space in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            return f.pdf(space[1:]) / np.prod(f.alpha)
        
        else:   
            raise ValueError('Unknown space %s' % space)
            
        
        
    def sample_pdf(f, input_sample, space='R'):
        """
        Calculates probability density for the given external sample in the given space.
        Function intended for the case no transformation needed. 
        Otherwise new f_sample should be instanciated.
        """
        
        # does sample is another f_model object? 
        # кинлы со zase кулэ?
        try:
            sample = getattr(input_sample, space)
        except AttributeError:
            # no
            sample = np.atleast_2d(input_sample)
            
        
        if space == 'G':
            pdfs_R = stats.norm.pdf(sample)
            return np.prod(pdfs_R, axis=pdfs_R.ndim-1)
                
        elif space == 'U':
            return np.where(np.all((sample >= 0) & (sample <= 1), axis=1), 1, 0)
        
        elif space in ('Rn', 'R', 'P', 'GK'):
            #č tohle už není až tak triviální
            _f = f()
            _f.add_sample(sample, space=space)
            return _f.pdf(space)
            
        # new piece of code "alpha"-related
        elif space in ('aR', 'aRn', 'aGK', 'aG', 'aP', 'aU'):
            return f.sample_pdf(sample / f.alpha, space=space[1:]) / np.prod(f.alpha)
            
        else:   
            raise ValueError('Unknown space %s' % space)
            
