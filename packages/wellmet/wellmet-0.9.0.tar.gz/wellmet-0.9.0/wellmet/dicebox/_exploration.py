#!/usr/bin/env python
# coding: utf-8


import numpy as np
import quadpy

from ..ghull import Ghull
from .. import convex_hull as khull
from .. import simplex as sx
from ..reader import Store
from .. import sball

from scipy import stats
from scipy import spatial

from collections import namedtuple
from sortedcollections import ValueSortedDict



    
    



class _Exploration:
    
    outer_budget = 100
    psi_q = 0.5
        
    def __call__(bx):
        if bx.nsim < 1: # je to legální
            return bx.f_model.new_sample([], space='G', extend=True)
        elif bx.holydays and not bx.nsim % bx.holydays:
            bx._logger(msg='holyday!')
            return bx.holyday()
        elif bx.to_refine > bx.to_explore:
            bx._logger(msg='refine!')
            return bx.refine()
        else:
            return bx.explore()
            
            
            
    def explore(bx):
        r = bx.get_exploratory_radius()
        
        #č konkretně tato třída je pevně napojena na G prostor
        #č ale bacha, kbyby se to změnilo...
        assert bx.convex_hull.space == 'G'
        
        a, b, _sample = bx.convex_hull.get_exploration_vector()
        R = -b
            
        if r < R:
            bx._logger(msg='refine (fallbacked)!')
            return bx.refine()
        
        orth_nodes_T = np.random.randn(len(a), bx.outer_budget) # len(a) == ndim
        orth_basis = khull.get_orth_basis(a)
        sample_from = stats.norm.sf(r)
        t = np.linspace(sample_from, 0, bx.outer_budget, endpoint=False)
        orth_nodes_T[0] = stats.norm.isf(t)
            
        outside_nodes_G = (orth_basis.T @ orth_nodes_T).T
        outside_nodes = bx.f_model.new_sample(outside_nodes_G, space='G')
        
        tree = spatial.KDTree(bx.G, compact_nodes=True, balanced_tree=False)
        d1, i1 = tree.query(outside_nodes_G, k=1)
        
        PDF = bx.pdf('G')
        
        nodes_pdf = outside_nodes.pdf('G')
        node_potentials = d1**bx.nvar * nodes_pdf**bx.psi_q * PDF[i1]**(1-bx.psi_q)
        
        max_node = np.argmax(node_potentials)
        
        bx._logger(msg='explore!')
        return outside_nodes[max_node]
    
    def get_exploratory_radius(bx):
        # empirical rule to get desired behavior
        p_desired = np.exp(-np.sqrt(bx.q * bx.nsim))
        
        # get matematically clean radius of it
        r = bx.sball.get_r(p_desired)
        return r
        
        
ExplorationLog = namedtuple('ExplorationLog', (
    "nsim",
    "nvar",
    "nfacets",
    "r","R",
    "inner",
    "shell",
    "outer",
    "FORM_outside",
    "TwoFORM_outside",
    "orth_outside",
    "inside",
    "outside",
    "success_points",
    "failure_points",
    "success",
    "failure",
    "mix",
    "vertex_estimation",
    "weighted_vertex_estimation"
    ))        
        
        
class DumbExploration(_Exploration):
    holydays = 0
    
    #č hull musí být v G prostoru s auto_update=True
    def __init__(bx, sample_box, q=10):
        bx.sample_box = sample_box
        
        bx.direct_plan = quadpy.un.mysovskikh_1(bx.nvar).points
        
        bx.convex_hull = khull.Grick(bx.f_model, bx.direct_plan, nrandom=50)
        bx.q = q
        
        bx.ghull = Ghull(bx.convex_hull)
        bx.sball = sball.Sball(bx.nvar)
        
        bx.to_explore = 2
        bx.to_refine = 0 # never refine
        
        #č přece ponechame složku pro uživatelské odhady
        #č stm kód může semka něco ukladat
        bx.estimations = []
        
        #č vítejte nové uložiště odhadů.
        #č Odhady z stm kódu už ale nemají na tohle sahat
        if hasattr(bx, 'filename'):
            bx.box_estimations = Store.create(bx.filename + "_exp", ExplorationLog)
        else:
            bx.box_estimations = []
        
        bx.regen()
    
        
    def init_parameters(bx):
        """
        Returns dictionary of parameters the DiceBox was initialized with
        """
        return {'sample_box':bx.sample_box, 'hull':bx.hull, 'q':bx.q}
                 
    
    def __repr__(bx):
        return "%s(**%s)"%(bx.__class__.__name__,  repr(bx.init_parameters()))
        
    def __str__(bx):
        return "%s(%s)"%(bx.__class__.__name__,  str(bx.init_parameters()))
        
        
    
    
    def regen(bx):
        if bx.nsim > 0:
            bx.estimate_outside()
        bx._nsim = bx.nsim
                 
    
    
    
    
    def __len__(bx):
        return bx.sample_box.nsim
    
    def __getitem__(bx, slice):
        #č stačí vratit sample_box
        return bx.sample_box[slice]
    
    def __getattr__(dx, attr):
        if attr == 'dicebox':
            return dx
            
        #č branime sa rekurzii
        # defend against recursion
        #оӵ рекурсилы пезьдэт!
        if attr == 'sample_box':
            raise AttributeError
                
        #ё По всем вопросам обращайтесь 
        #ё на нашу горячую линию    
        else:
            return getattr(dx.sample_box, attr)
    
    
    # The DiceBox Observer 
    def _logger(self, *args, msg="", indent=0, **kwargs):
        if not kwargs:
            kwargs = "" #č ať se nám prázdné závorky nezobrazujou
        print(self.__class__.__name__ + ":", msg, *args, kwargs) 
        
        
        # inspired by Qt
    def connect(self, slot): self._logger = slot
    def disconnect(self): del(self._logger)
    
        
    # přidávání vzorků musí bejt explicitní!
    def add_sample(bx, input_sample):
        bx.sample_box.add_sample(input_sample)
        bx.increment(bx.sample_box[bx._nsim:])
        bx._nsim = bx.nsim
    
    
        
        
    def increment(bx, input_sample):
        bx.estimate_outside()
        
        bx.box_estimations.append(bx.get_pf_estimation())
    
                
                    
    
    
    
        
        
    
    def estimate_outside(bx):
        #č konečně mám pořádnou stejtful třídu
        #č pokud mám aspoň jednu tečku, tak už je mi šuma
        #č zda se konvexní obálka vytvořila, či nikoliv
        
        
        shell_estimation, global_stats = bx.ghull.get_shell_estimation()
        
        # shell_estimation  -22: inner, -3: shell, -11: outer
        bx.shell_estimation = shell_estimation
        
        #č kvůli názvu neleze do namedtuple
        global_stats['TwoFORM_outside'] = global_stats.pop('2FORM_outside')
        #č ndim se nelibí pandas
        global_stats['nvar'] = global_stats.pop('ndim')
        
        bx.global_stats = global_stats
        
        
        
        
        
    def get_pf_estimation(bx):
        global_stats = bx.global_stats
        orth_outside = global_stats['outside'] = global_stats['orth_outside']
        pf_inside = global_stats['inside'] = 1 - orth_outside
        
        #č takže celou skříňku prostě bereme jako simplex
        event, event_id, fr, wfr = sx.get_simplex_event(bx, weighting_space='G')
        # -1=outside, 0=success, 1=failure, 2=mix
        tri_estimation = {0:0, 1:0, 2:0}
        tri_estimation[event_id] = pf_inside
        
        vertex_estimation = pf_inside * fr
        weighted_vertex_estimation = pf_inside * wfr
        
        
        failsi = bx.failsi
        global_stats['success_points'] = len(failsi[~failsi])
        global_stats['failure_points'] = len(failsi[failsi])
        global_stats['success'] = tri_estimation[0]
        global_stats['failure'] = tri_estimation[1]
        global_stats['mix'] = tri_estimation[2]
        global_stats['vertex_estimation'] = vertex_estimation
        global_stats['weighted_vertex_estimation'] = weighted_vertex_estimation
        
        return ExplorationLog(**global_stats)
        
