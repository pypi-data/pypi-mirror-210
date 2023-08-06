#!/usr/bin/env python
# coding: utf-8


import numpy as np
from scipy.spatial import distance
from scipy.spatial import KDTree
from scipy import stats

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


    
    
TriEstimation = namedtuple('TriEstimation', (
    *shell.ShellStats._fields,
    *shell.ShellEstimation._fields,
    'success_points',
    'failure_points',
    *sx.CubatureEstimation._fields[2:],
    'r_safe',
    'R_safe',
    'r_mixed',
    'R_mixed',
    'r_failure',
    'R_failure',
    'p_sum',
    'max_potential'
    ))


QTriEstimation = namedtuple('QTriEstimation', (
    *khull.QHullEstimation._fields,
    'success_points',
    'failure_points',
    *sx.CubatureEstimation._fields[2:],
    'r_safe',
    'R_safe',
    'r_mixed',
    'R_mixed',
    'r_failure',
    'R_failure',
    'p_sum',
    'max_potential'
    ))


class _CircumTri(_Exploration):
    
    def __repr__(bx):
        return "%s(**%s)"%(bx.__class__.__name__,  repr(bx.init_parameters()))
        
    def __str__(bx):
        return "%s(%s)"%(bx.__class__.__name__,  str(bx.init_parameters()))
    
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
            
    
    def get_exploratory_radius(bx):
        R = bx.shell_stats.R
        # empirical rule to get desired behavior
        sphere_area = bx.convex_hull.nsphere_surface_area * (R + bx.q)**bx.nvar
        p_desired = bx.shell_estimation.outside / sphere_area
        
        # get matematically clean radius of it
        r = bx.sball.get_r(p_desired)
        return r
    
                    
    def is_mixed(bx, simplices=None):
    
        if simplices is None:
            simplices = bx.tri.simplices
        
        in_failure = np.isin(simplices, bx.failure_points)
        has_failure = in_failure.any(axis=1)
        all_failure = in_failure.all(axis=1)
        return np.logical_xor(has_failure, all_failure)
    
    
    
        
    
    def get_tri_radia(bx):
        lengths = np.sum(np.square(bx.G), axis=1)
        lengths = np.sqrt(lengths, out=lengths) #lengths of each radius-vector
        
        if 'Tri' in dir(bx):
            simplices = bx.Tri.tri.simplices
            radia = lengths[simplices]
            r = np.min(radia, axis=1)
            R = np.max(radia, axis=1)
            
            in_failure = bx.failsi[simplices]
            
            has_failure = in_failure.any(axis=1)
            all_failure = in_failure.all(axis=1)
            
            if np.any(~has_failure):
                r_safe = np.min(r[~has_failure])
                R_safe = np.max(R[~has_failure])
            else:
                r_safe, R_safe = -1, -1
            
            
            if np.any(all_failure):
                r_failure = np.min(r[all_failure])
                R_failure = np.max(R[all_failure])
            else:
                r_failure, R_failure = -1, -1
                
            mixed_mask = np.logical_xor(has_failure, all_failure)
            if np.any(mixed_mask):
                r_mixed = np.min(r[mixed_mask])
                R_mixed = np.max(R[mixed_mask]) 
            else:
                r_mixed, R_mixed = -1, -1
            
            return r_safe, R_safe, r_mixed, R_mixed, r_failure, R_failure
            
        else:
            radia = [-1] * 6
            r = np.min(lengths)
            R = np.max(lengths)
            
            if np.all(bx.failsi):
                return -1, -1, -1, -1, r, R
            elif np.any(bx.failsi):
                return -1, -1, r, R, -1, -1
            else:
                return r, R, -1, -1, -1, -1
            
            
        
    
    def perform_topological_analysis(bx):
        assert bx.tri_space == 'G'
        # tn_scheme, points, simplices, neighbors, failsi, facets, normals
        bx.ta = sx.TopologyAnalysis(bx.convex_hull.tn_scheme, bx.G, 
                                    bx.Tri.tri.simplices, bx.Tri.tri.neighbors,
                                     bx.failsi, bx.convex_hull.simplices, 
                                     bx.convex_hull.A)
        print("start integration of the convex envelope")   
        bx.ta.integrate_convex_envelope()
        print("start integration of the internal walls")
        bx.ta.integrate_walls()
        print("start topological analysis")   
        bx.ta.perform_analysis()
        
        
    
    
    
    def get_pf_estimation(bx):
        failsi = bx.failsi
        
        success_points = len(failsi[~failsi])
        failure_points = len(failsi[failsi])
        
        inside = bx.shell_estimation.inside
        
        if 'Tri' in dir(bx):
            tri_estimation = bx.Tri.get_pf_estimation()
            
            mixed = tri_estimation.mix
            failure = tri_estimation.failure
            
            if not bx.holydays:
                success = inside - mixed - failure
                p_sum = 1
            else:
                success = tri_estimation.success
                outside = bx.shell_estimation.outside
                p_sum = outside + failure + mixed + success
            
            return bx.Estimation(bx.nsim,  #č musíme sami lepit nové etikety, neboť
                                *bx.get_outside_estimation(),
                                success_points,
                                failure_points,
                                success,
                                *tri_estimation[3:],
                                
                                *bx.get_tri_radia(),
                                p_sum,
                                bx.get_max_potential()
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
        mixed = tri_estimation[2]
        
        return bx.Estimation(bx.nsim,  #č musíme sami lepit nové etikety, neboť
                             *bx.get_outside_estimation(),
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
                             
                             *bx.get_tri_radia(),
                             1,
                             bx.get_max_potential()
                             )
        







class CirQTri(_CircumTri):
    
    def __init__(bx, sample_box, scheme, convex_hull_degree=5,
                 q=1, holydays=0):
        
        bx.sample_box = sample_box
        bx.convex_hull_degree = convex_hull_degree
        bx.scheme = scheme
        
        bx.tri_space = 'G'
            
        bx.Estimation = QTriEstimation
        bx.q = q
        bx.holydays = holydays
        
        bx.sball = sball.Sball(bx.nvar)
        
        
        #č přece ponechame složku pro uživatelské odhady
        #č stm kód může semka něco ukladat
        bx.estimations = []
        
        #č vítejte nové uložiště odhadů.
        #č Odhady z stm kódu už ale nemají na tohle sahat
        if hasattr(bx, 'filename'):
            bx.box_estimations = Store.create(bx.filename + "_qtri", bx.Estimation)
        else:
            bx.box_estimations = []
            
        bx.CC = sx.CircumCenter(sample_box.nvar)
        
        bx.regen()
    
        
    def init_parameters(bx):
        """
        Returns dictionary of parameters the DiceBox was initialized with
        """
        return {'sample_box':bx.sample_box, 'scheme':bx.scheme.name,
                'convex_hull_degree':bx.convex_hull_degree,
                 'q':bx.q, 'holydays':bx.holydays}


    def _regen_outside(bx):
        facet_scheme = quadpy.tn.grundmann_moeller(bx.nvar - 1, bx.convex_hull_degree)
        bx.convex_hull = khull.QHullCubature(bx.f_model, space='G', incremental=True, 
                            auto_update=False, tn_scheme=facet_scheme)
        
        #č konečně mám pořádnou stejtful třídu
        #č pokud mám aspoň jednu tečku, tak už je mi šuma
        #č zda se konvexní obálka vytvořila, či nikoliv
        if bx.nsim > 0:
            bx.estimate_outside()
            
    
    def estimate_outside(bx):
        #č konečně mám pořádnou stejtful třídu
        #č pokud mám aspoň jednu tečku, tak už je mi šuma
        #č zda se konvexní obálka vytvořila, či nikoliv
        
        #č Máme úkol: 
        #č 1. Získat odhady a uložit je, abychom nemuseli opakovaně integrovat,
        #č    dokud se neobjeví nějaký nový vzorek zvenku.
        bx.shell_estimation = bx.convex_hull.get_convex_hull_estimation()
        bx.shell_stats = bx.shell_estimation # simple trick
    
            
    def get_outside_estimation(bx):
        return bx.shell_estimation[1:]
    
    
    def _regen_inside(bx):
        failsi = bx.failsi
        # incremental triangulation require one more point
        if (bx.nsim > bx.nvar + 1) and np.any(failsi) and not np.all(failsi):
            try:
                bx.Tri = sx.GaussCubatureIntegration(bx.samplebox, bx.scheme, 
                                            incremental=True, full=bx.holydays)
                
                #č tri - Deloneho triangulace
                bx.tri = bx.Tri.tri #č všichni tam očekávají QHull
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
        else:
            #č jíž není nutný
            bx._logger(msg="triangulation skipped")
            
    
    def get_circum_node(bx, indices):
        vertices_model = bx.Tri.tri.points[indices]
        try:
            circum_center = bx.CC.get_circumcenter(vertices_model)
        except BaseException as e:
            bx._logger(repr(e), msg='CircumCenter error')
            circum_center = np.mean(vertices_model, axis=0)
             
        if not np.all(np.isfinite(circum_center)):
            raise
             
        length2 = np.sum(np.square(circum_center))
        R = bx.get_exploratory_radius()
        if length2 > R**2:
            bx._logger(circum_center, 
                    msg='Circumcenter lies too far away from the origin. The radial distance is reduced')
            circum_center /= np.sqrt(length2)
            circum_center *= R
        
        circum_node = bx.f_model.new_sample(circum_center, space=bx.tri_space)
        return circum_node
    
    
    def refine(bx):
        if "Tri" in dir(bx):
            # get the greatest mixed simplex
            return bx.get_circum_node(bx.Tri.max_mixed_indices)
        else:
            bx._logger(msg='refine called, but triangulation does not exist yet. Fallback to a random sample')
            return bx.f_model(1)
    
    
    def holyday(bx):
        if "Tri" in dir(bx) and (bx.Tri.max_safe > 0):
            return bx.get_circum_node(bx.Tri.max_safe_indices)
        else:
            bx._logger(msg='Fallback to random sample')
            return bx.f_model(1)
    
    def regen(bx):
        """
        regen() recreates data structures of the box. 
        It shouldn't be called without reason, changed distribution, settings or so.
        """
        
        #оӵ шайтан регенираци лэзьиз
        bx._logger(msg='regeneration started')
        
        bx._regen_outside()
        bx._regen_inside()
        
        bx.to_explore = 1
        bx.to_refine = 0
        if bx.nsim > 0:
            bx.pf_estimation = bx.get_pf_estimation() 
            bx.update_exploration_ratio()
        
        bx._nsim = bx.nsim



    def get_max_potential(bx):
        if "Tri" in dir(bx):
             # get probability of the greatest mixed simplex
            return bx.Tri.max_mixed
        else:
            return -1

    def update_exploration_ratio(bx):
        bx.to_explore = stats.norm.sf(bx.pf_estimation.r)
        bx.to_refine = bx.get_max_potential()

        
    def increment(bx, input_sample):
        #č tri - Deloneho triangulace
        if "tri" in dir(bx):
            bx.Tri.update()
        else:
            bx._regen_inside()
            
        if np.any(bx.convex_hull.is_outside(input_sample)):
            bx.convex_hull.update()
            bx.estimate_outside()
        
        bx.pf_estimation = bx.get_pf_estimation()
        bx.box_estimations.append(bx.pf_estimation)
        bx.update_exploration_ratio()




class _PsiTri:
    def refine(bx):
        if len(bx.candidates_index):
            # return node with the greatest potential
            key, value = bx.potential_index.peekitem()
            return bx.candidates_index[key]
        else:
            bx._logger(msg='refine called, but triangulation does not exist yet. Fallback to random sample')
            return bx.f_model(1)
    
    
    def holyday(bx):
        if len(bx.candidates_index):
            # return node with the greatest potential
            key, value = bx.global_potential_index.peekitem()
            return bx.candidates_index[key]
        else:
            bx._logger(msg='triangulation does not exist yet. Fallback to random sample')
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
        bx.global_potential_index.clear()
        
        bx._regen_outside()
        bx._regen_inside()
        
        bx.to_explore = 1
        bx.to_refine = 0
        if bx.nsim > 0:
            bx.pf_estimation = bx.get_pf_estimation() #č updates p_mixed
            bx.update_exploration_ratio()
        
        bx._nsim = bx.nsim


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
            if bx.holydays:
                Integrator = sx.FullCubatureIntegration
            else:
                Integrator = sx.FastCubatureIntegration
            
            bx.Tri = Integrator(bx.samplebox, bx.scheme,\
                     tri_space=bx.tri_space, incremental=True,\
                    on_safe_added=bx._on_safe_added,\
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

    def get_max_potential(bx):
        if len(bx.candidates_index):
             __key, max_potential = bx.potential_index.peekitem()
        else:
            max_potential = -1
        return max_potential



    def update_exploration_ratio(bx):
        bx.to_explore += bx.pf_estimation.outside / (bx.pf_estimation.nfacets + 1)
        if bx.pf_estimation.max_potential > 0:
            bx.to_refine += bx.pf_estimation.mix / bx.pf_estimation.mixed_simplices


    #č teď je to kolbek, který volá Triangulation
    def _on_safe_added(bx, simplex, indices, vertices_model, nodes, vol):
        
        try:
            circum_center = bx.CC.get_circumcenter(vertices_model)
        except BaseException as e:
            bx._logger(repr(e), msg='CircumCenter error')
            return 
        r = distance.euclidean(circum_center, vertices_model[0])
        circum_node = bx.f_model.new_sample(circum_center, space=bx.tri_space)
        #č můžeme nechat numpy pole z jednoho prvku. Můžeme zredukovat na float
        #circum_pdf = circum_node.pdf(bx.tri_space)
        circum_pdf = float(circum_node.pdf(bx.tri_space))
        
        
        #PDF = bx.Tri.PDF[indices]
        #max_PDF = np.max(PDF)
        
        circum_potential = r**bx.nvar * circum_pdf #**bx.psi_q * max_PDF**(1-bx.psi_q)
        
        if not np.isfinite(circum_potential):
            return
        
#        max_node_potential = -np.inf
#        if not bx.circumcenters_only:
#            dr = distance.cdist(nodes.G, [circum_center]).reshape(-1)
#            nodes_pdf = nodes.pdf(bx.tri_space)
#            node_potentials = (r - dr)**bx.nvar * nodes_pdf#**bx.psi_q * PDF[i]**(1-bx.psi_q)
#            
#            max_node = np.argmax(node_potentials)
#            max_node_potential = node_potentials[max_node]
#        
#        if max_node_potential > circum_potential:
#            result_node = nodes[max_node]
#            result_potential = max_node_potential
#        else:
        result_node = circum_node
        result_potential = circum_potential
            
        if bx.store_candidates_metainformation:
            result_node = CandyNodes(result_node)
            result_node.potential = result_potential
            
        bx.candidates_index[simplex] = result_node
        bx.global_potential_index[simplex] = result_potential
    
    
    
    #č teď je to kolbek, který volá Triangulation
    def _on_mixed_added(bx, simplex, indices, vertices_model, nodes, _vol, fr, wfr, _mfpdf):
        
        try:
            circum_center = bx.CC.get_circumcenter(vertices_model)
        except BaseException as e:
            bx._logger(repr(e), msg='CircumCenter error')
            return 
        r = distance.euclidean(circum_center, vertices_model[0])
        circum_node = bx.f_model.new_sample(circum_center, space=bx.tri_space)
        #č můžeme nechat numpy pole z jednoho prvku. Můžeme zredukovat na float
        #circum_pdf = circum_node.pdf(bx.tri_space)
        circum_pdf = float(circum_node.pdf(bx.tri_space))
        
        
        failsi = bx.Tri.failsi[indices]
        PDF = bx.Tri.PDF[indices]
        max_PDF = np.max(PDF)
        
        circum_potential = r**bx.nvar * circum_pdf**bx.psi_q * max_PDF**(1-bx.psi_q)
        
        if not np.isfinite(circum_potential):
            return
        
        
        
        max_node_potential = -np.inf
        if not bx.circumcenters_only:
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
                nodes_pdf = nodes.pdf(bx.tri_space)
                #č nejdřív rouška, pak slice. V tomto pořadí numpy to zvladné bez alokací
                i = ii[mask][:,0] 
                node_potentials = (r - dr)**bx.nvar * nodes_pdf**bx.psi_q * PDF[i]**(1-bx.psi_q)
                
                max_node = np.argmax(node_potentials)
                max_node_potential = node_potentials[max_node]
        
        
        if max_node_potential > circum_potential:
            result_node = nodes[max_node]
            result_potential = max_node_potential
        else:
            result_node = circum_node
            result_potential = circum_potential
            
        if bx.store_candidates_metainformation:
            result_node = CandyNodes(result_node)
            result_node.potential = result_potential
            
        bx.candidates_index[simplex] = result_node
        bx.potential_index[simplex] = result_potential
        if bx.holydays:
            bx.global_potential_index[simplex] = result_potential
            
        
            

            
    # callback
    #č sx.on_delete_simplex(indices=indices)
    def _invalidate_simplex(bx, simplex):
        bx.potential_index.pop(simplex, None)
        bx.global_potential_index.pop(simplex, None)
        bx.candidates_index.pop(simplex, None)
        
        
    def increment(bx, input_sample):
        #č tri - Deloneho triangulace
        if "tri" in dir(bx):
            bx.Tri.update()
        else:
            bx._regen_inside()
            
        a, b, _sample = bx.convex_hull.get_exploration_vector()
        critical_r = -b
        
        coming_r = a @ input_sample.G.T  
        
        if bx._nsim > 1 and np.any(coming_r > critical_r):
            bx.to_explore = 0
            bx.convex_hull.update()
            bx.estimate_outside()
        elif np.any(bx.convex_hull.is_outside(input_sample)):
            bx.to_refine = 0
            bx.convex_hull.update()
            bx.estimate_outside()
        else:
            bx.to_refine = 0
        
        bx.pf_estimation = bx.get_pf_estimation()
        bx.box_estimations.append(bx.pf_estimation)
        bx.update_exploration_ratio()
        
        
        
        



class CircumTri(_CircumTri, _PsiTri):
    
    #č míží nám sampling_space: Ghull umí vzorkovat outside pouze v G prostoru
    #č quadpy umístí integráční bodíky v prostoru triangulace.
    def __init__(bx, sample_box, scheme, q=10, psi_q=0.5, circumcenters_only=True, 
                  holydays=10, store_candidates_metainformation=False, shell_budget=1000):
        
        bx.sample_box = sample_box
        bx.scheme = scheme
        
        bx.tri_space = 'G'
            
        bx.Estimation = TriEstimation
        bx.shell_budget = shell_budget
        #bx.potential_mode = potential_mode
        #bx.weighted_entropy = weighted_entropy
        bx.store_candidates_metainformation = store_candidates_metainformation
        bx.circumcenters_only = circumcenters_only
        bx.q = q
        bx.psi_q = psi_q
        bx.holydays = holydays
        
        bx.direct_plan = quadpy.un.mysovskikh_1(bx.nvar).points
        bx.sball = sball.Sball(bx.nvar)
        
        
        #č přece ponechame složku pro uživatelské odhady
        #č stm kód může semka něco ukladat
        bx.estimations = []
        
        #č vítejte nové uložiště odhadů.
        #č Odhady z stm kódu už ale nemají na tohle sahat
        if hasattr(bx, 'filename'):
            bx.box_estimations = Store.create(bx.filename + "_tri", bx.Estimation)
        else:
            bx.box_estimations = []
            
        bx.CC = sx.CircumCenter(sample_box.nvar)
            
        # kind of interface to CandidatesWidget
        bx.candidates_index = {}
        bx.potential_index = ValueSortedDict()
        bx.global_potential_index = ValueSortedDict()
        
        bx.regen()
    
        
    def init_parameters(bx):
        """
        Returns dictionary of parameters the DiceBox was initialized with
        """
        return {'sample_box':bx.sample_box, 'scheme':bx.scheme.name,
                 'shell_budget':bx.shell_budget,
                 'circumcenters_only':bx.circumcenters_only, 
                 'q':bx.q, 'psi_q':bx.psi_q, 'holydays':bx.holydays}


    def _regen_outside(bx):
        bx.convex_hull = khull.QHull(bx.f_model, space='G', 
                                    incremental=True, auto_update=False)
        bx.ghull = shell.GaussianAnnulus(bx.convex_hull)
        #č konečně mám pořádnou stejtful třídu
        #č pokud mám aspoň jednu tečku, tak už je mi šuma
        #č zda se konvexní obálka vytvořila, či nikoliv
        if bx.nsim > 0:
            bx.estimate_outside()
            
    
    def _rate_outside_nodes(bx, outside_nodes, d, i):
        failsi = bx.failsi
        if np.all(failsi) or not np.any(failsi):
            return
        
        try:
            mask = bx.is_mixed(bx.convex_hull.simplices[i])
            if not np.any(mask):
                return
            outside_nodes = outside_nodes[mask]
            d = d[mask]
            
        except:
            pass
            
        #č konkretně tato třída je pevně napojena na G prostor
        #č ale bacha, kbyby se to změnilo...
        _d1, i1 = bx.tree.query(outside_nodes.G, k=1)
        
        PDF = bx.pdf(bx.tri_space)
        
        nodes_pdf = outside_nodes.pdf(bx.tri_space)
        node_potentials = d**bx.nvar * nodes_pdf**bx.psi_q * PDF[i1]**(1-bx.psi_q)
        
        max_node = np.argmax(node_potentials)
        max_node_potential = node_potentials[max_node]
        
        
        if max_node_potential > bx.potential_index[-1]:
            if bx.store_candidates_metainformation:
                outside_node = CandyNodes(outside_nodes[max_node])
                outside_node.potential = max_node_potential
            else:
                outside_node = outside_nodes[max_node]
            
            bx.candidates_index[-1] = outside_node
            bx.potential_index.pop(-1)
            bx.potential_index[-1] = max_node_potential
            bx.global_potential_index.pop(-1)
            bx.global_potential_index[-1] = max_node_potential
    
    
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
        bx.global_potential_index.pop(-1, None)
        #bx.rating_index.pop(-1, None)
        bx.potential_index[-1] = 0 #č pro callback
        bx.global_potential_index[-1] = 0 #č pro callback
        
        bx.shell_stats = bx.ghull.get_shell_estimation()
        
        bx.tree = KDTree(bx.G, compact_nodes=True, balanced_tree=False)
        
        # get candidates!
        #č explicitně (pokažde) počtem teček zadavám přesnost integrace
        #č takže změny bx.shell_budget budou při dálším spuštění aplikovány
        bx.shell_estimation = bx.ghull.integrate(bx.shell_budget,
                                callback_outside=bx._rate_outside_nodes)         
    
            
    def get_outside_estimation(bx):
        #č Ghull spouštíme sporadicky
        return *bx.shell_stats[1:], *bx.shell_estimation
            
            

class QTri(_CircumTri, _PsiTri):
    
    def __init__(bx, sample_box, convex_hull_degree=5, tri_degree=5,
                 q=10, psi_q=0.5, circumcenters_only=True, 
                  holydays=10, store_candidates_metainformation=False):
        
        bx.sample_box = sample_box
        bx.convex_hull_degree = convex_hull_degree
        bx.tri_degree = tri_degree
        bx.scheme = quadpy.tn.grundmann_moeller(bx.nvar, tri_degree)
        
        bx.tri_space = 'G'
            
        bx.Estimation = QTriEstimation
        bx.store_candidates_metainformation = store_candidates_metainformation
        bx.circumcenters_only = circumcenters_only
        bx.q = q
        bx.psi_q = psi_q
        bx.holydays = holydays
        
        bx.sball = sball.Sball(bx.nvar)
        
        
        #č přece ponechame složku pro uživatelské odhady
        #č stm kód může semka něco ukladat
        bx.estimations = []
        
        #č vítejte nové uložiště odhadů.
        #č Odhady z stm kódu už ale nemají na tohle sahat
        if hasattr(bx, 'filename'):
            bx.box_estimations = Store.create(bx.filename + "_qtri", bx.Estimation)
        else:
            bx.box_estimations = []
            
        bx.CC = sx.CircumCenter(sample_box.nvar)
            
        # kind of interface to CandidatesWidget
        bx.candidates_index = {}
        bx.potential_index = ValueSortedDict()
        bx.global_potential_index = ValueSortedDict()
        
        bx.regen()
    
        
    def init_parameters(bx):
        """
        Returns dictionary of parameters the DiceBox was initialized with
        """
        return {'sample_box':bx.sample_box, 
                'convex_hull_degree':bx.convex_hull_degree,
                'tri_degree':bx.tri_degree,
                 'circumcenters_only':bx.circumcenters_only, 
                 'q':bx.q, 'psi_q':bx.psi_q, 'holydays':bx.holydays}


    def _regen_outside(bx):
        facet_scheme = quadpy.tn.grundmann_moeller(bx.nvar - 1, bx.convex_hull_degree)
        bx.convex_hull = khull.QHullCubature(bx.f_model, space='G', incremental=True, 
                            auto_update=False, tn_scheme=facet_scheme)
        
        #č konečně mám pořádnou stejtful třídu
        #č pokud mám aspoň jednu tečku, tak už je mi šuma
        #č zda se konvexní obálka vytvořila, či nikoliv
        if bx.nsim > 0:
            bx.estimate_outside()
            
    
    def estimate_outside(bx):
        #č konečně mám pořádnou stejtful třídu
        #č pokud mám aspoň jednu tečku, tak už je mi šuma
        #č zda se konvexní obálka vytvořila, či nikoliv
        
        #č Máme úkol: 
        #č 1. Získat odhady a uložit je, abychom nemuseli opakovaně integrovat,
        #č    dokud se neobjeví nějaký nový vzorek zvenku.
        bx.shell_estimation = bx.convex_hull.get_convex_hull_estimation()
        bx.shell_stats = bx.shell_estimation # simple trick
    
            
    def get_outside_estimation(bx):
        return bx.shell_estimation[1:]
        
        
