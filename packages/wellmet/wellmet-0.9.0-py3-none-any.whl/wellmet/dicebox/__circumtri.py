#!/usr/bin/env python
# coding: utf-8


import numpy as np
from scipy.spatial import distance

import quadpy

from .. import shell
from .. import simplex as sx
from .. import convex_hull as khull
from ..reader import Store
from ..candynodes import CandyNodes
from .. import sball

from ._exploration import _Exploration

from collections import namedtuple
from sortedcollections import ValueSortedDict





def get_entropy(pf):
    return -pf * np.log(pf) - (1 - pf) * np.log(1 - pf)


    

CircumTriEstimation = namedtuple('CircumTriEstimation', (
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
    "weighted_vertex_estimation",
    "nsimplex",
    "tn_scheme",
    "tn_scheme_points",
    "newly_invalidated",
    "newly_estimated",
    "simplex_stats",
    "candidates_sets",
    "ncoplanar"
    ))


class CircumTri(_Exploration):
    
    #č míží nám sampling_space: Ghull umí vzorkovat outside pouze v G prostoru
    #č quadpy umístí integráční bodíky v prostoru triangulace.
    def __init__(bx, sample_box, scheme, entropy_mode='weighted', 
                    circumcenters_only=True, q=10):
        
        bx.sample_box = sample_box
        bx.scheme = scheme
        bx.entropy_mode = entropy_mode
        bx.circumcenters_only = circumcenters_only
        bx.q = q
        
        
        bx.direct_plan = quadpy.un.mysovskikh_1(bx.nvar).points
        bx.sball = sball.Sball(bx.nvar)
        
        bx.tri_space = 'G'
        
        #č přece ponechame složku pro uživatelské odhady
        #č stm kód může semka něco ukladat
        bx.estimations = []
        
        #č vítejte nové uložiště odhadů.
        #č Odhady z stm kódu už ale nemají na tohle sahat
        if hasattr(bx, 'filename'):
            bx.box_estimations = Store.create(bx.filename + "_ctri", CircumTriEstimation)
        else:
            bx.box_estimations = []
            
        bx.CC = sx.CircumCenter(sample_box.nvar)
            
        # kind of interface to CandidatesWidget
        bx.candidates_index = {}
        bx.potential_index = ValueSortedDict()
        
        bx.regen()
    
        
    def init_parameters(bx):
        """
        Returns dictionary of parameters the DiceBox was initialized with
        """
        return {'sample_box':bx.sample_box, 'scheme':bx.scheme.name, 
                'entropy_mode':bx.entropy_mode, 
                'circumcenters_only':circumcenters_only, 'q':bx.q}
                 
    
    def __repr__(bx):
        return "%s(**%s)"%(bx.__class__.__name__,  repr(bx.init_parameters()))
        
    def __str__(bx):
        return "%s(%s)"%(bx.__class__.__name__,  str(bx.init_parameters()))
        
        
        
    def refine(bx):
        if len(bx.candidates_index):
            # return node with the greatest potential
            key, value = bx.potential_index.peekitem()
            return bx.candidates_index[key]
        else:
            bx._logger(msg='refine called, but triangulation does not exist yet. Fallback to random sample')
            return bx.f_model(1)
    
    
    def regen(bx):
        """
        regen() recreates data structures of the box. 
        It shouldn't be called without reason, changed distribution, settings or so.
        """
        
        #оӵ шайтан регенираци лэзьиз
        bx._logger(msg='regeneration started')
        
        bx.candidates_index.clear()
        bx.potential_index.clear()
        
        bx._regen_outside()
        bx._regen_inside()
        
        if bx.nsim > 0:
            bx.get_pf_estimation() #č updates global stats
            bx.update_exploration_ratio()
        else:
            bx.exploration_ratio = 1
        
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
    
    
    
    def update_exploration_ratio(bx):
        if "tri" in dir(bx):
            outside = np.sqrt(bx.global_stats['outside'])
            mixed = np.sqrt(bx.global_stats['mix'])
            bx.exploration_ratio = outside / (outside + mixed)
        else:
            bx.exploration_ratio = 1
        
        
    
    
    
    #č bejvalej .estimate_simplex()
    #č teď je to kolbek, který volá Triangulation
    def _on_add_simplex(bx, nodes):
        # -1=outside, 0=success, 1=failure, 2=mix
        if nodes.event_id != 2:
            return 
        
        
        indices = nodes.indices
        failsi = bx.Tri.failsi[indices]
        vertices_model = bx.Tri.tri.points[indices]
        PDF = bx.Tri.PDF[indices]
        
        circum_center = bx.CC.get_circumcenter(vertices_model)
        r = distance.euclidean(circum_center, vertices_model[0])
        circum_node = bx.f_model.new_sample(circum_center, space=bx.tri_space)
        #č můžeme nechat numpy pole z jednoho prvku. Můžeme zredukovat na float
        #circum_pdf = circum_node.pdf(bx.tri_space)
        circum_pdf = float(circum_node.pdf(bx.tri_space))
        circum_potential = r * circum_pdf**(1/bx.nvar)
        
        # circum rating
        if bx.entropy_mode == 'none':
            circum_rating = circum_potential
        elif bx.entropy_mode == 'simple':
            # fp like a failure points. Number of failure points
            fp = len(failsi[failsi]) # the fastest solution
            circum_rating = circum_potential * get_entropy(fp / len(failsi))
        elif bx.entropy_mode == 'weighted':
            # same as np.average(failsi, weights=pdf), but faster
            wfr = np.sum(PDF[failsi]) / np.sum(PDF)
            circum_rating = circum_potential * get_entropy(wfr)
        
        
        if bx.circumcenters_only:
            #č nodes příjdou zabalené do CandyNodes. Ty mají .attrs a .kwargs
            circum_node = CandyNodes(circum_node, nodes.attrs)
            circum_node.potential = circum_potential
            circum_node.rating = circum_rating
            bx.candidates_index[tuple(indices)] = circum_node
            bx.potential_index[tuple(indices)] = circum_rating
            
            return
        
        #else:
        
        nodes_model = getattr(nodes, bx.tri_space)
        dr = distance.cdist(nodes_model, [circum_center]).reshape(-1)
        nodes_pdf = nodes.pdf(bx.tri_space)
        node_potentials = (r - dr) * nodes_pdf**(1/bx.nvar)
        
        if bx.entropy_mode == 'none':
            node_ratings = node_potentials
        elif bx.entropy_mode == 'simple':
            node_ratings = node_potentials * get_entropy(nodes.pfv)
        elif bx.entropy_mode == 'weighted':
            node_ratings = node_potentials * get_entropy(nodes.pfw)
            
        
        
        max_node = np.nanargmax(node_ratings)
        max_node_rating = node_ratings[max_node]
        if circum_rating > max_node_rating:
            #č nodes příjdou zabalené do CandyNodes. Ty mají .attrs a .kwargs
            circum_node = CandyNodes(circum_node, nodes.attrs)
            circum_node.potential = circum_potential
            circum_node.rating = circum_rating
            bx.candidates_index[tuple(indices)] = circum_node
            bx.potential_index[tuple(indices)] = circum_rating
        else:
            node = nodes[max_node]
            node.potential = node_potentials[max_node]
            node.rating = max_node_rating
            bx.candidates_index[tuple(indices)] = node
            bx.potential_index[tuple(indices)] = max_node_rating
            



            
    # callback
    #č sx.on_delete_simplex(indices=indices)
    def _invalidate_simplex(bx, simplex):
        bx.candidates_index.pop(simplex, None)
        bx.potential_index.pop(simplex, None)
    
    
    
        

                
    def _regen_outside(bx):
        bx.convex_hull = khull.QHull(bx.f_model, space='G', 
                                    incremental=True, auto_update=False)
        bx.ghull = Ghull(bx.convex_hull)
        #č pokud mám aspoň jednu tečku, tak už je mi šuma
        #č zda se konvexní obálka vytvořila, či nikoliv
        if bx.nsim > 0:
            bx.estimate_outside()
        
            
    def _regen_inside(bx):
        failsi = bx.failsi
        # incremental triangulation require one more point
        if (bx.nsim > bx.nvar + 1) and np.any(failsi) and not np.all(failsi):
            #bx._logger(msg="triangulation started")
            bx.__regen_inside()
        else:
            #č jíž není nutný
            bx._logger(msg="triangulation skipped")
            
    def __regen_inside(bx):
        try:
            bx.Tri = sx.BetterCubatureIntegration(bx.samplebox, bx.scheme,\
                     tri_space='G', incremental=True,\
                    on_add_simplex=bx._on_add_simplex,\
                    on_delete_simplex=bx._invalidate_simplex)
              
            bx.Tri.integrate() # nic nevrácí, všecko je přes kolbeky
            #č tri - Deloneho triangulace
            bx.tri = bx.Tri.tri #č všichní tam očekávajou QHull
            bx._logger(msg="triangulation has been created")
            
        except BaseException as e:
            #č chcu zachytit spadnuti QHull na začatku, 
            #č kdy ještě není dostatek teček.
            #č Jinak je třeba nechat QHull spadnout
            if bx.nsim > 2*bx.nvar + 3: 
                #č no to teda ne!
                raise
            else: 
                #č lze přípustit chybu triangulace    
                bx._logger(msg='triangulation failed')
    
    
        
    def increment(bx, input_sample):
        #č tri - Deloneho triangulace
        if "tri" in dir(bx):
            bx.Tri.update()
        else:
            bx._regen_inside()
            
            
        if np.any(bx.convex_hull.is_outside(input_sample)):
            bx.convex_hull.update()
            bx.estimate_outside()
        
        bx.box_estimations.append(bx.get_pf_estimation())
        bx.update_exploration_ratio()
    
                
    
        
        
    
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
        
        #č Ghull spouštíme sporadicky, 
        #č takže musíme sami lepit nové etikety
        global_stats['nsim'] = bx.nsim
        
        failsi = bx.failsi
        
        if 'tri' in dir(bx):
            bx.global_stats.update(bx.Tri.get_pf_estimation())
            failure = bx.global_stats['failure']
            mixed = bx.global_stats['mix']
            bx.global_stats['success_points'] = len(failsi[~failsi])
            bx.global_stats['failure_points'] = len(failsi[failsi])
            bx.global_stats['success'] = pf_inside - failure - mixed
            bx.global_stats['candidates_sets'] = len(bx.candidates_index)
            
            return CircumTriEstimation(**bx.global_stats)
            
        
        #оӵ триангуляци ӧвӧл, иськем...
        
        #č může se stát, že první dvě tečky už hned májí různé barvy,
        #č ale žádnej simplex ještě nemáme.
        #č takže celou skříňku prostě bereme jako simplex
        event, event_id, fr, wfr = sx.get_simplex_event(bx, weighting_space=bx.tri_space)
        # -1=outside, 0=success, 1=failure, 2=mix
        tri_estimation = {0:0, 1:0, 2:0}
        tri_estimation[event_id] = pf_inside
        
        vertex_estimation = pf_inside * fr
        weighted_vertex_estimation = pf_inside * wfr
        
        global_stats = bx.global_stats
        # outside dodá Ghull
        global_stats['success_points'] = len(failsi[~failsi])
        global_stats['failure_points'] = len(failsi[failsi])
        global_stats['success'] = tri_estimation[0]
        global_stats['failure'] = tri_estimation[1]
        global_stats['mix'] = tri_estimation[2]
        global_stats['vertex_estimation'] = vertex_estimation
        global_stats['weighted_vertex_estimation'] = weighted_vertex_estimation
        global_stats['nsimplex'] = 0
        global_stats['tn_scheme'] = bx.scheme.name
        global_stats['tn_scheme_points'] = bx.scheme.points.shape[1]
        global_stats['newly_invalidated'] = 0
        global_stats['newly_estimated'] = 0
        global_stats['simplex_stats'] = 0
        global_stats['candidates_sets'] = len(bx.candidates_index)
        global_stats['ncoplanar'] = 0
        
        return CircumTriEstimation(**global_stats)
        
        
