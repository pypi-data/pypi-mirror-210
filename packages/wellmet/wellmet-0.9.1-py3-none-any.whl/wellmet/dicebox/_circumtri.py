#!/usr/bin/env python
# coding: utf-8


import numpy as np
from scipy.spatial import distance
from scipy.spatial import KDTree

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
    entropy = -pf * np.log(pf) - (1 - pf) * np.log(1 - pf)
    if entropy > 0:
        return entropy
    else:
        return 0

max_entropy = get_entropy(0.5)

    
    
TriEstimation = namedtuple('TriEstimation', (
    *shell.ShellStats._fields,
    *shell.ShellEstimation._fields,
    'success_points',
    'failure_points',
    'success',
    *sx.FastCubatureEstimation._fields[2:],
    'max_potential'
    ))


class CircumTri(_Exploration):
    
    #č míží nám sampling_space: Ghull umí vzorkovat outside pouze v G prostoru
    #č quadpy umístí integráční bodíky v prostoru triangulace.
    def __init__(bx, sample_box, scheme, q=10, #circumcenters_only=True, 
                  store_candidates_metainformation=False, 
                  potential_mode=2, weighted_entropy=True, shell_budget=1000):
        
        bx.sample_box = sample_box
        bx.scheme = scheme
        
        bx.tri_space = 'G'
            
        
        bx.shell_budget = shell_budget
        bx.potential_mode = potential_mode
        bx.weighted_entropy = weighted_entropy
        bx.store_candidates_metainformation = store_candidates_metainformation
        #bx.circumcenters_only = circumcenters_only
        bx.q = q
        
        
        bx.direct_plan = quadpy.un.mysovskikh_1(bx.nvar).points
        bx.sball = sball.Sball(bx.nvar)
        
        
        #č přece ponechame složku pro uživatelské odhady
        #č stm kód může semka něco ukladat
        bx.estimations = []
        
        #č vítejte nové uložiště odhadů.
        #č Odhady z stm kódu už ale nemají na tohle sahat
        if hasattr(bx, 'filename'):
            bx.box_estimations = Store.create(bx.filename + "_tri", TriEstimation)
        else:
            bx.box_estimations = []
            
        bx.CC = sx.CircumCenter(sample_box.nvar)
            
        # kind of interface to CandidatesWidget
        bx.candidates_index = {}
        bx.potential_index = ValueSortedDict()
        bx.rating_index = ValueSortedDict()
        
        bx.regen()
    
        
    def init_parameters(bx):
        """
        Returns dictionary of parameters the DiceBox was initialized with
        """
        return {'sample_box':bx.sample_box, 'scheme':bx.scheme.name,
                 'potential_mode':bx.potential_mode,\
                 'shell_budget':bx.shell_budget,
                 #'circumcenters_only':bx.circumcenters_only, 
                 'q':bx.q}
    
    def __repr__(bx):
        return "%s(**%s)"%(bx.__class__.__name__,  repr(bx.init_parameters()))
        
    def __str__(bx):
        return "%s(%s)"%(bx.__class__.__name__,  str(bx.init_parameters()))
        
        
    def refine(bx):
        if len(bx.candidates_index):
            # potential mode:
            # 0 - never use, always use rating
            # 1 - always select by potential
            # n - select by potential every n-th node
            if bx.potential_mode < 1:
                # return node with the greatest rating
                key, value = bx.rating_index.peekitem()
            elif bx.nsim % bx.potential_mode: 
                # return node with the greatest rating
                key, value = bx.rating_index.peekitem()
            else:
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
        bx.rating_index.clear()
        
        bx._regen_outside()
        bx._regen_inside()
        
        if bx.nsim > 0:
            bx.get_pf_estimation() #č updates p_mixed
            bx.update_exploration_ratio()
        else:
            bx.to_explore = 1
            bx.to_refine = 0
        
        
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
        bx.to_explore += np.sqrt(bx.shell_estimation.outside)
        bx.to_refine += np.sqrt(bx.p_mixed)
    
    
    
    #č teď je to kolbek, který volá Triangulation
    def _on_mixed_added(bx, simplex, indices, vertices_model, nodes, _vol, fr, wfr, _mfpdf):
        
        circum_center = bx.CC.get_circumcenter(vertices_model)
        r = distance.euclidean(circum_center, vertices_model[0])
        circum_node = bx.f_model.new_sample(circum_center, space=bx.tri_space)
        #č můžeme nechat numpy pole z jednoho prvku. Můžeme zredukovat na float
        #circum_pdf = circum_node.pdf(bx.tri_space)
        circum_pdf = float(circum_node.pdf(bx.tri_space))
        circum_potential = r * circum_pdf**(1/bx.nvar)
        
        failsi = bx.Tri.failsi[indices]
        
        
        tree = KDTree(vertices_model, compact_nodes=False, balanced_tree=False)
        
        #č konkretně tato třída je pevně napojena na G prostor
        #č ale bacha, kbyby se to změnilo...
        dd, ii = tree.query(nodes.G, k=2)
        
        failsi_pair = failsi[ii]
        mask = np.logical_xor(failsi_pair[:,0], failsi_pair[:,1])
        #mask = np.sum(failsi[ii], axis=1) == 1
        if np.any(mask):
            nodes = nodes[mask]
            
            dr = distance.cdist(nodes.G, [circum_center]).reshape(-1)
            nodes_pdf = nodes.pdf('G')
            node_potentials = (r - dr) * nodes_pdf**(1/bx.nvar)
            
            
            max_node = np.nanargmax(node_potentials)
            max_node_potential = node_potentials[max_node]
        else:
            max_node_potential = -np.inf
        
        
        
        if max_node_potential > circum_potential:
            result_node = nodes[max_node]
            result_potential = max_node_potential
            
            d1, d2 = dd[mask][max_node]
            if bx.weighted_entropy:
                ii = ii[mask][max_node]
                pdf1, pdf2 = bx.Tri.PDF[indices][ii]
                entropy = get_entropy(pdf1 * d2 / (pdf1 * d2 + pdf2 * d1))
            else:
                entropy = get_entropy(d1 / (d1 + d2))
            result_rating = max_node_potential * entropy
        else:
            result_node = circum_node
            result_potential = circum_potential
            # circum rating
            if bx.weighted_entropy:
                entropy = get_entropy(wfr)
            else:
                entropy = get_entropy(fr)
            result_rating = circum_potential * entropy
        
        
        #č nodes příjdou zabalené do CandyNodes. Ty mají .attrs a .kwargs
        if bx.store_candidates_metainformation:
            result_node = CandyNodes(result_node)
            result_node.potential = result_potential
            result_node.rating = result_rating
            
        bx.candidates_index[simplex] = result_node
        bx.potential_index[simplex] = result_potential
        bx.rating_index[simplex] = result_rating
            
        
            

            
    # callback
    #č sx.on_delete_simplex(indices=indices)
    def _invalidate_simplex(bx, simplex):
        bx.potential_index.pop(simplex, None)
        bx.rating_index.pop(simplex, None)
        bx.candidates_index.pop(simplex, None)
    
    
    
        

                
    def _regen_outside(bx):
        bx.convex_hull = khull.QHull(bx.f_model, space='G', 
                                    incremental=True, auto_update=False)
        bx.ghull = shell.GaussianAnnulus(bx.convex_hull)
        #č konečně mám pořádnou stejtful třídu
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
            bx.Tri = sx.CubatureIntegration(bx.samplebox, bx.scheme,\
                     tri_space=bx.tri_space, incremental=True,\
                    on_mixed_added=bx._on_mixed_added,\
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
            bx.to_explore = 0
            bx.convex_hull.update()
            bx.estimate_outside()
        else:
            bx.to_refine = 0
        
        bx.box_estimations.append(bx.get_pf_estimation())
        bx.update_exploration_ratio()
    
                
                    
    
    
    
    def _rate_outside_nodes(bx, outside_nodes, d):
        #č sice získáme filtrovaný outside, 
        node_potentials = outside_nodes.pdf(bx.tri_space)**(1 / bx.nvar) * d
        
        max_node = np.nanargmax(node_potentials)
        max_node_potential = node_potentials[max_node]
        
        
        if max_node_potential > bx.potential_index[-1]:
            node_rating = 0 #max_node_potential * max_entropy
            if bx.store_candidates_metainformation:
                outside_node = CandyNodes(outside_nodes[max_node])
                outside_node.potential = max_node_potential
                outside_node.rating = node_rating
            else:
                outside_node = outside_nodes[max_node]
            
            bx.candidates_index[-1] = outside_node
            bx.potential_index.pop(-1)
            bx.potential_index[-1] = max_node_potential
            bx.rating_index.pop(-1, None)
            bx.rating_index[-1] = node_rating
        
        
    
    def estimate_outside(bx):
        #č konečně mám pořádnou stejtful třídu
        #č pokud mám aspoň jednu tečku, tak už je mi šuma
        #č zda se konvexní obálka vytvořila, či nikoliv
        
        #č Máme 2 úkoly: 
        #č 1. Získat odhady a uložit je, abychom nemuseli opakovaně integrovat,
        #č    dokud se neobjeví nějaký nový vzorek zvenku.
        #č 2. Získat kandidaty.
        #č    a. z mezíkruží (-12)
        
        #č prace s tečkami v mezikruži se změnila
        #č teď tečky dostávám přes kolbek po částech
        #č a není předem známo, kolik těch částí bude.
        bx.candidates_index.pop(-1, None)
        #č těch kastomných slovníků se bojím...
        bx.potential_index.pop(-1, None)
        #bx.rating_index.pop(-1, None)
        bx.potential_index[-1] = 0 #č pro callback
        
        bx.shell_stats = bx.ghull.get_shell_estimation()
        
        # get candidates!
        #č explicitně (pokažde) počtem teček zadavám přesnost integrace
        #č takže změny bx.shell_budget budou při dálším spuštění aplikovány
        bx.shell_estimation = bx.ghull.integrate(bx.shell_budget, \
                                callback_outside=bx._rate_outside_nodes) 
        
    
    
    def get_pf_estimation(bx):
        failsi = bx.failsi
        
        success_points = len(failsi[~failsi])
        failure_points = len(failsi[failsi])
        
        inside = bx.shell_estimation.inside
        
        __key, max_potential = bx.potential_index.peekitem()
        
        if 'tri' in dir(bx):
            tri_estimation = bx.Tri.get_pf_estimation()
            
            bx.p_mixed = tri_estimation.mix
            
            success = inside - tri_estimation.failure - tri_estimation.mix
            
            return TriEstimation(bx.nsim,  #č musíme sami lepit nové etikety, neboť
                                *bx.shell_stats[1:], #č Ghull spouštíme sporadicky
                                *bx.shell_estimation,
                                success_points,
                                failure_points,
                                success,
                                *tri_estimation[2:],
                                max_potential
                                )
            
        
        #оӵ триангуляци ӧвӧл, иськем...
        
        #č může se stát, že první dvě tečky už hned májí různé barvy,
        #č ale žádnej simplex ještě nemáme.
        #č takže celou skříňku prostě bereme jako simplex
        event, event_id, fr, wfr = sx.get_simplex_event(bx, weighting_space=bx.tri_space)
        # -1=outside, 0=success, 1=failure, 2=mix
        tri_estimation = {0:0, 1:0, 2:0}
        tri_estimation[event_id] = inside
        
        success = tri_estimation[0]
        failure = tri_estimation[1]
        bx.p_mixed = mixed = tri_estimation[2]
        
        return TriEstimation(bx.nsim,  #č musíme sami lepit nové etikety, neboť
                             *bx.shell_stats[1:], #č Ghull spouštíme sporadicky
                             *bx.shell_estimation,
                             success_points,
                             failure_points,
                             success,
                             
                             failure,
                             mixed,
                             inside * fr,
                             inside * wfr, 
                             inside * wfr,
                             0, # nsimplex
                             #sx.tn_scheme.name,
                             bx.scheme.points.shape[1],
                             0, #sx.newly_invalidated,
                             0, #sx.newly_estimated,
                             0, #len(sx.failure_simplices),
                             0, #len(sx.mixed_simplices),
                             0, #len(sx.tri.coplanar),
                             
                             max_potential
                             )
        
        
