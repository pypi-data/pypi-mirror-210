#!/usr/bin/env python
# coding: utf-8

import numpy as np
from . import sball
from scipy import stats
from .candynodes import CandyNodes
from .IS_stat import get_1DS_sample # for Shell_1DS

from collections import namedtuple

try: # try to outthink OS's memory management
    import os
    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
except BaseException as e:
    mem_GB = 16
    mem_bytes = mem_GB * 1024**3 # hello, Windows!
    #print("ghull failed to get amount of RAM installed. %s GB is supposed."% mem_GB, repr(e))
    #print("BTW, you are using Windows, aren't you?")
    
    
    
ShellStats = namedtuple('ShellStats', (
                                        'nsim',
                                        'nvar',
                                        'nfacets',
                                        'r', 'R',
                                        'inner',
                                        'shell',
                                        'outer',
                                        'FORM_outside',
                                        'TwoFORM_outside',
                                        'orth_outside'
                                        ))

ShellEstimation = namedtuple('ShellEstimation', 
                            ('shell_budget', 'shell_inside', 
                            'shell_outside', 'inside', 'outside'))


#č pomocná třída pro integrování
#č nejsem tedy jist, jestli je to nejlepší napad - 
#č dělit Ghull na podtřídy, delegovat funkcionalitu
#č ale jinak Ghull se stavá hodně překomplikovaným.
#č nic lepšího mně nenapadá, přemyšlel jsem dlouho.
class Shell_1DS:
    """1DS stands for 1D sampling.
    1DS is, actually, an importance sampling method
    that, actually, does not calculate IS weights
    as f_density / h_density, but
    (arbitrary, nonuniformly) divides interval to subintervals.
    By using CDF transformes subintervals to 0-1 measure line.
    Then gets one node as middle point of every subinterval,
    weights therefore are just interval widths itself.
    No sampling imprecisions are introduced, 
    therefore no spring, no correction are needed. 
    """
    def __init__(self, hull, shell):
        self.shell = shell
        self.hull = hull
        self.nvar = hull.sample.nvar
        
        #č objevilo se, že scipy.stats.chi je neunosně nepřesné
        #č vzdává se jíž na poloměru 8
        self.sball = sball.Sball(self.nvar)
        
        self.integration_cutoff = np.inf
        
    
    def integrate(self, nis, callback_all=None, callback_outside=None):
        self.reset(nis)
        
        if self.hull.nsimplex == 0:
            bus = self.integration_cutoff
        else:
            bus = int(mem_bytes / self.hull.nsimplex / 8 / 10) + 1
        while self.nsampled < nis:
            
            seats = min(nis - self.nsampled, self.integration_cutoff, bus)
            try: 
                self._process_part(seats, nis, callback_all, callback_outside)
            except MemoryError as m:
                print(self.__class__.__name__ +":", "memory error, %s sedaček" % seats, repr(m))
                self.integration_cutoff = int(np.ceil(seats/2))
        
        assert nis == self.nsampled
        
        return self._get_result()
        
    
    def reset(self, nis): # clear
        
        self.nsampled = 0
        
        #č poloměry bereme ze skořapky
        #č za správné nastavení (stejně jako u MC)
        #č zodpovidá uživatel třídy
        #č třída vlastní odhad r nijak nevyuživá!
        r = self.shell.r
        R = self.shell.R
        # let's predefine 1D sequence at very beginning
        if r > np.sqrt(self.nvar - 1):
            x_sub = np.geomspace(r, R, nis+1, endpoint=True)
        else:
            x_sub = np.linspace(r, R, nis+1, endpoint=True)
        
        
        x, weights = get_1DS_sample(self.sball, x_sub)
        self.x = x
        self.weights = weights
        self.mask = np.empty(nis, dtype=bool)
        
    
    
    # bus analogy
    def _process_part(self, seats, nis, callback_all=None, callback_outside=None):
        # boarding
        left = self.nsampled
        right = self.nsampled + seats
        rs = self.x[left:right]
        
        # rand_dir: prepare ns random directions on a unit d-sphere
        rand_dir = sball.get_random_directions(seats, self.nvar) #random directions
        nodes_G = rand_dir*rs[:,None]
        nodes = self.hull.sample.f_model.new_sample(nodes_G, space='G')
        
        # who is back?
        d, i = self.hull.query(nodes)
        mask = d > 0
        assert len(mask) == seats
        
        # the most important part
        self.nsampled += len(mask) 
        self.mask[left:right] = mask
        
        if callback_all is not None:
            # -2 = 'inside' -1 = 'outside'
            candy_nodes = CandyNodes(nodes, event_id=mask-2, is_outside=mask, d=d, i=i)
            callback_all(candy_nodes)
            
        if (callback_outside is not None) and np.any(mask):
            callback_outside(nodes[mask], d[mask], i[mask])
        
        
        
    def _get_result(self):
        #č mask related to hull.is_outside()
        shell_pf = np.sum(self.weights[self.mask])
        shell_ps = np.sum(self.weights[~self.mask])
        
        return self.nsampled, shell_ps, shell_pf
        
        
        
        
class GaussianAnnulus:
    def __init__(self, hull):
        assert hull.space == 'G'
        
        self.hull = hull
        self.shell = sball.Shell(hull.sample.nvar)
        self.outside_dist = sball.Shell(hull.sample.nvar)
        self.sample = hull.sample
        
        self.gint = Shell_1DS(self.hull, self.shell)
        
            
    def boom(self, ns, use_MC=False):
        if use_MC:
            self.outside_dist.set_bounds(self.get_R())
            nodes_G = self.outside_dist.rvs(ns)
        else:
            # rand_dir: prepare ns random directions on a unit d-sphere
            rand_dir = sball.get_random_directions(ns, self.sample.nvar) #random directions
            
            #č deme od vnější .get_R() kružnici směrem ven
            r = self.get_R()
            
            # maximum radius, where norm.pdf() wasn't zero
            # -38.575500173381374935388521407730877399444580
            # don't ask me what the magic python use to distinguish
            # digits after double precision
            max_R_ever = 37
            if r < max_R_ever:
                R = max_R_ever
            else:
                R = r + 10
            r = np.linspace(self.get_R(), max_R_ever, ns, endpoint=True) 
            nodes_G = rand_dir*r[:,None]
        
        nodes = self.sample.f_model.new_sample(nodes_G, space='G')
        return nodes
        
            
    def get_R(self):
        sum_squared = np.sum(np.square(self.sample.G), axis=1)
        #index = np.argmax(sum_squared)
        return np.sqrt(np.nanmax(sum_squared))
        
    def setup_shell(self):
        shell = self.shell
        r = self.hull.get_r()
        R = self.get_R()
        
        if r<0:
            shell.set_bounds(0, R)
        else:
            shell.set_bounds(r, R)
        
        return r, R
    
    def get_shell_estimation(self):
        r, R = self.setup_shell()
        
        return ShellStats(
                            self.sample.nsim,
                            self.sample.nvar,
                            self.hull.nsimplex,
                            r, R,
                            self.shell.ps,
                            self.shell.p_shell,
                            self.shell.pf,
                            stats.norm.sf(r),
                            self.hull.get_2FORM_outside(),
                            self.hull.get_orth_outside()
                        )
        
    def integrate(self, nis, callback_all=None, callback_outside=None):
        self.setup_shell()
        
        nsampled, shell_ps, shell_pf = self.gint.integrate(nis, callback_all, callback_outside)
        
        inside = shell_ps + self.shell.ps
        outside = shell_pf + self.shell.pf
        
        return ShellEstimation(nsampled, shell_ps, shell_pf, inside, outside)
        
        
