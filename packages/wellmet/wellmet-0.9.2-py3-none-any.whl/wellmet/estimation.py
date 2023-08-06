#!/usr/bin/env python
# coding: utf-8

import numpy as np
import numpy.ma as ma
import scipy.stats as stats

from scipy.spatial import cKDTree
from scipy.spatial import Delaunay
from scipy import spatial
from scipy import interpolate

import collections # for defaultdict

from . import f_models
from . import simplex as six
from . import IS_stat
from .IS_stat import IS
from .candybox import CandyBox
from . import sball 



#
# l2 Voronoi cKDTree IS localization
#
 
# Rbf_estimation so far
def L2_Voronoi_cKDTree(sample_box, nis=50000):    
    nsim, nvar = np.shape(sampled_plan_R)
    # Estimation of pf given a list of red and green points (Voronoi)
    
    sampled_plan_R_ma = np.ma.asarray(sampled_plan_R)
    
    # tady bych nedaval Rd 
    #grad = np.abs(gradient([0 for j in range(nvar)]))
    tree = cKDTree(sampled_plan_R)
    

    rbf_func = interpolate.Rbf(sampled_plan_R[:,0],sampled_plan_R[:,1],Z)

    Rbf_estimation = 0 # inicializace
    L2_Voronoi_cKDTree_test = 0
    #failure_points_indexes = np.argwhere(failsi)
    
    points_probabilities = np.empty(nsim) # probabilities of partial (failure) event
    
    # loop over points (need to integrate red regions)
    for i in range(nsim): # loop over failing points only
        
        sampled_plan_R_ma.mask = ma.nomask
        sampled_plan_R_ma[i] = ma.masked
        
        # neosvědčílo se
#==============================================================================
#         delta_Rd_matrix = sampled_plan_Rd_ma - sampled_plan_Rd[i]
#         mindist = [np.min(np.abs(np.where(delta_Rd_matrix[:,j] < 0,delta_Rd_matrix[:,j], f_i[j].std() ))) + np.min(np.abs(np.where(delta_Rd_matrix[:,j] > 0,delta_Rd_matrix[:,j], f_i[j].std() ))) for j in range(nvar)]
#                                          
#         # set the minimum distance as the standard deviation of IS densisty
#         h_i = [stats.norm(sampled_plan_Rd[i,j], mindist[j] ) for j in range(nvar)] #! dosadit  standard deviation pddle chutí
#==============================================================================
        # find distance to the nearest sampling point (from all points)
        mindist = np.min(np.sum(np.square(sampled_plan_R_ma - sampled_plan_R[i]), axis=1))**0.5
                                 
        # set the minimum distance as the standard deviation of IS densisty
        h_i = [stats.norm(sampled_plan_R[i,j], 2*mindist ) for j in range(nvar)] #! dosadit  standard deviation pddle chutí
                                 
        # use IS sampling density with center equal to the current "red" point
                                 
        # select nis = 100 points from IS density and 
        # if the point has its nearest neighbor any red point from the sampled_plan, 
                                 
        h_plan = np.zeros((nis, nvar))
        for j in range(nvar):
            h_plan[:, j] = h_i[j].ppf(np.random.random(nis)) # realizace váhové funkce náhodné veličiny
    
        # Rozptyl corrected IS
        weights_sim = np.prod([f_i[j].pdf(h_plan[:, j]) / h_i[j].pdf(h_plan[:, j]) for j in range(nvar)], axis=0) # [f1/h1, ..., fn/hn]
    
       
    
        dd, ii = tree.query(h_plan)
    
        Vor_mask = np.where(ii==i, True, False)
        
        zm = rbf_func(h_plan[:, 0][Vor_mask], h_plan[:, 1][Vor_mask])        
        
        points_probabilities[i] = np.sum(weights_sim[Vor_mask][zm<0]) / nis
        L2_Voronoi_cKDTree_test += np.sum(weights_sim[Vor_mask]) / nis
    
    
    Rbf_estimation = np.sum(points_probabilities)
    
    return Rbf_estimation, L2_Voronoi_cKDTree_test
    





# cKDTree
"""
# dd  - The distances to the nearest neighbors 
# ii - The locations of the neighbors in self.data
# k - The list of k-th nearest neighbors to return. 
# If k is an integer it is treated as a list of [1, … k] (range(1, k+1)). 
# Note that the counting starts from 1
# p - Which Minkowski p-norm to use. 
# 1 is the sum-of-absolute-values “Manhattan” distance 2 is the usual Euclidean distance 
# infinity is the maximum-coordinate-difference distance 

dd, ii = tree.query(h_plan_model, k=1, p=p_norm)
"""


#
# Voronoi estimation
#    (gradient tu nechcu)
def Voronoi_tesselation(sample_box, model_space='Rn', sampling_space=None, p_norm=1, budget=20000, callback=None):
    """
    Voronoi estimations 
    budget=20000
    """
    global_stats = {'Voronoi_failure_rate':0}

    
    
    nsim = sample_box.nsim
    
        
    # jsou to informace nejen pro callback 
    # nis upresníme dále
    estimation={'method': "Voronoi_tesselation",  'p_norm':p_norm, 'nis':0, 'nsim':nsim}
    estimation['model_space'] = model_space
    estimation['sampling_space'] = sampling_space
    
    if len(sample_box.failure_points) > 0:
        nis = max(round(budget/len(sample_box.failure_points)), 100)
        estimation['nis'] = nis
    
        # vytahneme ze sample_boxu rozdělení
        f = sample_box.sampled_plan
        
        # já vím, že sample box pokážde failure_points přepočítavá
        failure_points = sample_box.failure_points 
        
        # zde provadím rozdělení na prostor, ve kterém vzorkujem
        # a prostor "modelu", vô ktôrom, v podstatě, měříme vzdaleností
        sampled_plan_model = getattr(sample_box, model_space)
        tree = cKDTree(sampled_plan_model)
        
        
        if sampling_space is None:
            sampling_space = model_space
            # sing like sampling
            sampled_plan_sing = sampled_plan_model
            tree_sampling = tree
        else:
            sampled_plan_sing = getattr(sample_box, sampling_space)
            # narychlo, moc to nepomůže, neboť asi po 16 vzorcích počítá brut forsem 
            tree_sampling = cKDTree(sampled_plan_sing,  compact_nodes=False, balanced_tree=False)
            
        # find distance to the nearest sampling point (from all points)
        dd2, ii2 = tree_sampling.query(sampled_plan_sing[failure_points], k=[2], p=p_norm)
        mindist_sing = dd2.reshape(-1)
        #ii2 = ii2.reshape(-1)
        
        
        
        # loop over points (need to integrate red regions)
        for i, i2 in zip(sample_box.failure_points, range(len(mindist_sing))): # loop over failing points only
            # use IS sampling density with center equal to the current "red" point
            # set the minimum distance as the standard deviation of IS densisty
            h_i = [stats.norm(sampled_plan_sing[i,j], 1.5*mindist_sing[i2]) for j in range(sample_box.nvar)] #! dosadit  standard deviation podle chutí
            h = f_models.UnCorD(h_i)
            
                                     
            # select nis = 100 points from IS density 
            # sice to má nazev h_plan, ale nese rozdělení a hustoty v f-ku
            h_plan = IS(f, h, space_from_h='R', space_to_f=sampling_space, Nsim=nis) 
            
            # součet váh nemá cenu kontrolovat, jedná tam nebude, nevyjde
            
            
            h_plan_model = getattr(h_plan, model_space)
            dd, ii = tree.query(h_plan_model, k=1, p=p_norm)
            
            cell_probability = np.sum(h_plan.w[ii==i]) / nis
            global_stats['Voronoi_failure_rate'] += cell_probability
            
            # kolbek ↓
            if callback is not None:
                cell_stats = {'Voronoi_failure_rate': cell_probability}
                cell_stats['cell_probability'] = cell_probability
                cell_stats['event'] = 'failure'
                callback(estimation=estimation, nodes=h_plan[ii==i], cell_stats=cell_stats, out_nodes=h_plan[ii!=i])

        
    result = {**estimation, **global_stats}
    # try to put it to the BlackBox
    try:
        sample_box.estimations.append(result)
    except: # asi ani nebudu neuspěch hlasit
        pass
        
    return result
    

    
    
    
#
# Voronoi 2_point estimation
# 
def Voronoi_2_point_estimation(sample_box, model_space='Rn', sampling_space=None, p_norm=1, gradient=None, budget=20000, callback=None):
    """
    Voronoi_2_point estimations 
    budget=20000
    """
    
    # tak, na rovinu
    # нет ножек - нет мультиков
#    if gradient is None:
#        return Voronoi_2_point_cKDTree(sample_box, model_space=model_space,sampling_space=sampling_space,\
#                                                            p_norm=p_norm, budget=budget, callback=callback)

#    if gradient is None:
#        gradient = lambda *_, **__: np.ones(sample_box.nvar)

    if callback is None:
        callback = lambda *_, **__: None
    
    nsim = sample_box.nsim
    # ощень, ощень скромненько
    p_base = 0.3 # chcu, aby behem první iterace p_base tečiček jistě dopadlo do buňky
    nis_base = int((sample_box.nvar+1)/p_base)
    nis = int(max(budget/nsim, nis_base / stats.binom.sf(int(sample_box.nvar+1), nis_base, p_base)))
        
    # jsou to informace pro callback 
    estimation={'method': "Voronoi_2_point_estimation",  'p_norm':p_norm, 'nis':nis, 'nsim':nsim}
    estimation['model_space'] = model_space
    estimation['sampling_space'] = sampling_space
    
    
    # vytahneme ze sample_boxu rozdělení
    f = sample_box.sampled_plan
    
    # já vím, že sample box pokážde failsi přepočítavá
    failsi = sample_box.failsi 
    
    PDF = sample_box.pdf(model_space)
    
    # zde provadím rozdělení na prostor, ve kterém vzorkujem
    # a prostor "modelu", vô ktôrom, v podstatě, měříme vzdaleností
    sampled_plan_model = getattr(sample_box, model_space)
    tree = cKDTree(sampled_plan_model)
    
    
    if sampling_space is None:
        sampling_space = model_space
        # sing like sampling
        sampled_plan_sing = sampled_plan_model
        tree_sampling = tree
    else:
        sampled_plan_sing = getattr(sample_box, sampling_space)
        # narychlo, moc to nepomůže, neboť asi po 16 vzorcích počítá brut forsem 
        tree_sampling = cKDTree(sampled_plan_sing,  compact_nodes=False, balanced_tree=False)
        
    # find distance to the nearest sampling point (from all points)
    dd2, ii2 = tree_sampling.query(sampled_plan_sing, k=[2], p=p_norm)
    mindist_sing = dd2.reshape(-1)
    
    # chcu, aby behem první iterace pulka (p_base) tečiček jistě dopadla do buňky
    base_r = sball.Sball(sample_box.nvar).get_r(1 - p_base)
    # np.sum(abs(stats.norm(0, 10).rvs(1000))<sb.get_r(.5)*10)
    
    

    global_stats = collections.defaultdict(int)
    
    
    
    # zde postupně v cyklu prochazíme všemi body (tj. vzorky)
    # a omezujeme se pouse nejbližšími bodíkama
    # tynhlenstím zajišťujeme disjunktnost 
    # a môžeme všechny nasbírané pravděpodobnosti jednoduše sčítat
    for i in range(nsim): # loop over all points, not failing points only
    
        # use IS sampling density with center equal to the current point
        # set the minimum distance as the standard deviation of IS densisty
        # mindist dělíme dvěma - hranice buňky je na půlcesty
        # a dělíme base_r'kem k získání sigmy. Přemejmenším empiricky mně to vychází
        # (u Norm'u vždy zadaváme směrodatnou odchylku)
        h_i = [stats.norm(sampled_plan_sing[i,j], mindist_sing[i]/2/base_r) for j in range(sample_box.nvar)] 
        h = f_models.UnCorD(h_i)
        
                                 
        # select nis points from IS density 
        # sice to má nazev h_plan, ale nese rozdělení a hustoty v f-ku
        h_plan = IS(f, h, space_from_h='R', space_to_f=sampling_space, Nsim=nis) 
        
        # součet váh nemá cenu kontrolovat, jedná tam nebude, nevyjde
        
        h_plan_model = getattr(h_plan, model_space)
        dd, ii = tree.query(h_plan_model, k=1, p=p_norm)
        
        # nechám s velkým písmenkem
        Vor_mask = ii==i
        h_plan_model_ma = h_plan_model[Vor_mask]
        weights_sim = h_plan.w[Vor_mask]
        # dd1 jsou vzdalenosti tečiček do centra Voroneho buňky
        dd1 = dd[Vor_mask]
        
        trace = 0
        nis_ma = len(weights_sim)
        
        h_plan_sing_ma = getattr(h_plan, sampling_space)[Vor_mask]
        S_bc = np.cov(h_plan_sing_ma, rowvar=False, bias=True, aweights=weights_sim)
        barycenter = np.average(h_plan_sing_ma, axis=0, weights=weights_sim)
        # effective nis
        nis_eff = nis
        #print("start", i)
        
        while trace < np.trace(S_bc):
            # number of nodes inside the cell matters too
            trace = np.trace(S_bc)# * nis_ma
            #print(S_bc)
            #print(nis_ma)
        
            
            
            
            # matika
            w, v = np.linalg.eig(S_bc)
            
            # use IS sampling density with center equal to the cell's barycenter
            # set the minimum distance as the standard deviation of the IS densisty
            # u stats.norm zadáváme směrodatnou odchylku, to je asi správné
            sigmas = np.sqrt(w) / base_r #(sample_box.nvar+2) #! dosadit  standard deviation podle chutí
            h_i = [stats.norm(0, sigmas[j]) for j in range(sample_box.nvar)]
            # rozdělení ve vlastním prostoru
            # select nis = 100 points from IS density 
            h_L = f_models.UnCorD(h_i)(nis)
            
            # здесь уже так легко не отделаемся. Трансформовать кароно.
            h_plan_bc = (v @ h_L.R.T).T
            h_plan_sing = h_plan_bc + barycenter
            
            # sice to má nazev h_plan, ale nese rozdělení a hustoty v f-ku
            h_plan_part = f.new_sample(h_plan_sing, sampling_space)
            
            
            # jdeme na ty hustoty
            # mně příjde, že je to legalní
            # sice samply podporujou maskovaní, to je ale drahé
            weights_sim_part = h_plan_part.pdf(sampling_space) / h_L.pdf('R') # snad je to správně
            h_plan.add_sample(CandyBox(h_plan_part, w=weights_sim_part))
            
            # vyfiltrujeme vzorky
            h_plan_model_part = getattr(h_plan_part, model_space)
            dd, ii = tree.query(h_plan_model_part, k=1, p=p_norm)
            
            # parta
            Vor_mask_part = ii==i
            weights_sim_part = weights_sim_part[Vor_mask_part]
            
            nis_ma = len(weights_sim_part)
            
            # zajišťovat Vor_mask je docela zbytečně, je to jen pro out_nodes,
            # které se zatím nikdě nepouživá
            Vor_mask = np.append(Vor_mask, Vor_mask_part)
            
            
            
            
            h_plan_model_ma = np.vstack((h_plan_model_ma, h_plan_model_part[Vor_mask_part]))
            weights_sim = np.append(weights_sim, weights_sim_part)
            # dd1 jsou vzdalenosti tečiček do centra Voroneho buňky
            dd1 = np.append(dd1, dd[Vor_mask_part])
            
            # zkusím těžiště počitat jen pro partu - možná tak algoritmus bude agresivnější?
            #barycenter = np.average(h_plan_sing[Vor_mask_part], axis=0, weights=weights_sim_part)
            h_plan_sing_ma = np.vstack((h_plan_sing_ma, h_plan_sing[Vor_mask_part])) 
            #S_bc = np.cov(h_plan_sing[Vor_mask_part], rowvar=False, bias=True, aweights=weights_sim_part)
            S_bc = np.cov(h_plan_sing_ma, rowvar=False, bias=True, aweights=weights_sim)
            barycenter = np.average(h_plan_sing_ma, axis=0, weights=weights_sim)
            nis_eff += nis
            
        
        
        #print(S_bc)
        #print(nis_ma)
        
        
        
        
        cell_stats = dict()
        # musí sa (na konci) rovnat jedne
        # opravdu dělíme nis'em, jako v normálním IS
        # nikoliv počtem příjatých bodíků, 
        # protože průměrná vaha je o hodně mene významná metrika
        cell_stats['cell_probability'] = np.sum(weights_sim) / nis_eff
        
        
        # tu bacha!
        # takhle se počíta, pokud se netrapíme gradijentem
        # a je to trošiňku optimizovaný, takže čert se nevyzná
        if gradient is None:
            # indexy ii nás moc nezajimajou
            # vzdalenosti snad byjsme zvladli použit?
            
            
            dd2, ii2 = tree.query(h_plan_model_ma, k=[2], p=p_norm)
            dd2 = dd2.reshape(-1)
            ii2 = ii2.reshape(-1)
            
            # tahle hračka s indexy je pro numpy poměrně drahá
            failsii_2 = failsi[ii2]
            # jeden vzorek (včetně hustoty PDF[i])  je nám vždy znám
            # porucha
            if failsi[i]:
                points_1 = PDF[i] * dd2
                node_pf_estimations = points_1 / (points_1 + PDF[ii2] * dd1)
                node_pf_estimations = np.where(failsii_2,1, node_pf_estimations)
                node_pf_pure_estimations = dd2 / (dd1 + dd2)
                node_pf_pure_estimations = np.where(failsii_2,1, node_pf_pure_estimations)
            
                cell_stats['Voronoi_2_point_upper_bound'] = cell_stats['cell_probability'] 
                cell_stats['Voronoi_2_point_failure_rate'] = np.sum(weights_sim * node_pf_estimations) / nis_eff
                cell_stats['Voronoi_2_point_pure_failure_rate'] = np.sum(weights_sim * node_pf_pure_estimations) / nis_eff
                cell_stats['Voronoi_2_point_lower_bound'] = np.sum(weights_sim[failsii_2]) / nis_eff
                cell_stats['Voronoi_failure_rate'] = cell_stats['cell_probability'] 
                nodes=CandyBox(h_plan.sampling_plan[Vor_mask], w=weights_sim, node_pf_estimations=node_pf_estimations,\
                                    node_pf_pure_estimations=node_pf_pure_estimations, dd1=dd1, dd2=dd2, ii2=ii2)
            
            # neporucha    
            else:
                dd1 = dd1[failsii_2]
                dd2 = dd2[failsii_2]
                points_1 = PDF[i] * dd2
                points_2 = PDF[ii2[failsii_2]] * dd1
                
                node_pf_estimations = points_2 / (points_1 + points_2)
                node_pf_pure_estimations = dd1 / (dd1 + dd2)
            
                cell_stats['Voronoi_2_point_upper_bound'] = np.sum(weights_sim[failsii_2]) / nis_eff
                cell_stats['Voronoi_2_point_failure_rate'] = np.sum(weights_sim[failsii_2]*node_pf_estimations) / nis_eff
                cell_stats['Voronoi_2_point_pure_failure_rate'] = np.sum(weights_sim[failsii_2] * node_pf_pure_estimations) / nis_eff
                cell_stats['Voronoi_2_point_lower_bound'] = 0
                cell_stats['Voronoi_failure_rate'] = 0
                nodes=CandyBox(h_plan.sampling_plan[Vor_mask][failsii_2], w=weights_sim[failsii_2], node_pf_estimations=node_pf_estimations,\
                                            node_pf_pure_estimations=node_pf_pure_estimations, dd1=dd1, dd2=dd2, ii2=ii2[failsii_2])
                
                # take something with corresponding length
                zeros = np.zeros(len(weights_sim) - len(dd2))
                # add remaining nodes
                nodes.add_sample(CandyBox(h_plan.sampling_plan[Vor_mask][~failsii_2], w=weights_sim[~failsii_2], node_pf_estimations=zeros,\
                                            node_pf_pure_estimations=zeros, ii2=ii2[~failsii_2]))
        
        
        # takhle - pokud chceme gradient použit
        # je třeba eště zoptimalizovať
        else:
            # kolik bodíků jsou nejbližší k mému vzorečkovi
            # np.empty() implicitně má dtype=float
            # tyhle blbosti ponechám jen kvůli callbackovi
            node_pf_estimations = np.empty(len(h_plan_model_ma))
            node_pf_pure_estimations = np.empty(len(h_plan_model_ma))# pure distance estimation
            node_failsi = np.empty(len(h_plan_model_ma), dtype=bool) # for L1 Voronoi # co to je za L1 Voronoi?
            
            # projdeme přes každej bodíček
            for node_idx in range(len(h_plan_model_ma)):
                # KDTree byl použit jen k rozdělení na disjunktní úseky, veškerej děj se odehravá tu
                # a to je všechno kvůli gradientu
                node = h_plan_model_ma[node_idx]
                # axis=1 - sčítá všechy směry dohromady, vysledkem je 1D pole rozměru nsim 
                inode2points_model_matrix = np.sum(np.abs(((sampled_plan_model - node) * gradient(node))**p_norm), axis=1)
                #print(inode2points_Rd_matrix)
                
                """
                partition - 
                Creates a copy of the array with its elements rearranged in such a way that
                 the value of the element in k-th position is in the position it would be in a sorted array. 
                 All elements smaller than the k-th element are moved before this element 
                 and all equal or greater are moved behind it. The ordering of the elements in the two partitions is undefined.
                """
                idx = np.argpartition(inode2points_model_matrix, 1) # musí tu bejt 1, počítá sa od nuly
                # je to správný, neboť numpy zaručuje, že druhej prvek (s indexem 1) bude na druhem místě
                node_failsi[node_idx] = failsi[idx[0]] 
                
                                          
                points_weight = PDF[idx[0]] / inode2points_model_matrix[idx[0]] + PDF[idx[1]] / inode2points_model_matrix[idx[1]]
                points_distances = 1 / inode2points_model_matrix[idx[0]] + 1 / inode2points_model_matrix[idx[1]]
                
                failure_weight  = int(failsi[idx[0]]) * PDF[idx[0]] / inode2points_model_matrix[idx[0]]
                failure_weight += int(failsi[idx[1]]) * PDF[idx[1]] / inode2points_model_matrix[idx[1]]
                
                failure_distance = int(failsi[idx[0]]) / inode2points_model_matrix[idx[0]] + int(failsi[idx[1]]) / inode2points_model_matrix[idx[1]]
                
                
                node_pf_estimations[node_idx] = failure_weight/points_weight
                node_pf_pure_estimations[node_idx] = failure_distance/points_distances
            
            
            cell_stats['Voronoi_2_point_upper_bound'] = np.sum(h_plan.w[Vor_mask]*np.ceil(node_pf_estimations)) / nis_eff
            cell_stats['Voronoi_2_point_failure_rate'] = np.sum(h_plan.w[Vor_mask]*node_pf_estimations) / nis_eff
            cell_stats['Voronoi_2_point_pure_failure_rate'] = np.sum(h_plan.w[Vor_mask]*node_pf_pure_estimations) / nis_eff
            cell_stats['Voronoi_2_point_lower_bound'] = np.sum(h_plan.w[Vor_mask]*np.floor(node_pf_estimations)) / nis_eff
            cell_stats['Voronoi_failure_rate'] = np.sum(h_plan.w[Vor_mask]*node_failsi) / nis_eff
            
            nodes=CandyBox(h_plan.sampling_plan[Vor_mask], w=h_plan.w[Vor_mask], node_pf_estimations=node_pf_estimations,\
                                            node_pf_pure_estimations=node_pf_pure_estimations, node_failsi=node_failsi)
            
            
        
        for key, value in cell_stats.items():
            global_stats[key] += value
        
        # kolbek ↓
        if failsi[i]:
            cell_stats['event'] = 'failure'
        else:
            cell_stats['event'] = 'success'
        callback(estimation=estimation, nodes=nodes, cell_stats=cell_stats, out_nodes=h_plan[~Vor_mask])

        
    
    result = {**estimation, **global_stats}
    # try to put it to the BlackBox
    try:
        sample_box.estimations.append(result)
    except: # asi ani nebudu neuspěch hlasit
        pass
        
    return result
    
    # dedictvi
#for k in range(len(ii)):
#    points_weigths[ii[k]] = points_weigths[ii[k]] + weights_sim[k] / nis
#    near_neighbors[ii[k]] = near_neighbors[ii[k]] + 1
#    Vor_mask[k] = failsi[ii[k]]    
    
    

    
    



def _issi_estimate_outside(f, model_space, sampling_space='G', \
                 powerset_correction=True, design=None, callback=None, outside_budget=1000):
    #č zde f-ko musí taky obsahovat vzorky!
    
    shull = six.Shull(f, model_space, sampling_space, \
                      powerset_correction, incremental=False, design=design)
    
    nodes = shull.integrate(outside_budget)
    
    # -1 = 'out'
    # -2 = 'inside'
    #č převezmeme ISSI
    oiss = shull.oiss
    
    
    # events přepíšeme
    weighted_mean, __, events = oiss.get_means()
    # outside probability
    #č nevyrovnané!
    outside_probability = weighted_mean[events==-1][0]
    
    if callback is not None:
        cell_stats = dict()
        #č tohle je opravdu jen pro formu
        cell_stats['cell_probability'] = outside_probability
        cell_stats['vertex_estimation'] = 0
        cell_stats['weighted_vertex_estimation'] = 0
        cell_stats['event'] = 'outside' #č "outside" se mi libí víc než prostě "out"
        
        
        #:) kolbek ↓
        mask = nodes.is_outside
        #nodes = nodes[mask]
        # out_nodes here meant "not needed"
        out_nodes = nodes[~mask] #č možná je čas se zbavit toho, co se stejně nepouživá?
        callback(shull=shull, nodes=nodes[mask], cell_stats=cell_stats, out_nodes=out_nodes) 
        
    return oiss, outside_probability

    


def full_simplex_estimation(sample_box, model_space='Rn', sampling_space=None, weighting_space=None,\
                           outside_budget=1000, simplex_budget=100, design=None, callback=None):
    """
    Delaunay triangulation
    """
    
    #č zde provadím rozdělení na prostor, ve kterém vzorkujem
    #čs a prostor "modelu", vô ktôrom, v podstatě, měříme vzdaleností
    if sampling_space is None:
        sampling_space = model_space
    
    if weighting_space is None:
        weighting_space = model_space
        
    
    #č jsou to informace (nejen) pro callback 
    estimation={'method': "full_simplex_estimation", 'nsim':sample_box.nsim}
    estimation['model_space'] = model_space
    estimation['sampling_space'] = sampling_space
    estimation['weighting_space'] = weighting_space
    estimation['outside_budget'] = outside_budget
    estimation['simplex_budget'] = simplex_budget
    estimation['design'] = str(design)
    
    
    #č vytahneme ze sample_boxu rozdělení
    f = sample_box.f_model
    
    # powerset_correction=False
    #č totíž my zodpovidáme za to, že Triangulaci pošleme správné ISSI 
    issi, outside = _issi_estimate_outside(f, model_space,\
                     sampling_space=sampling_space, powerset_correction=False,\
                design=design, callback=callback, outside_budget=outside_budget)
                
    tri = six.FullSamplingTriangulation(sample_box, tri_space=model_space, issi=issi, \
             weighting_space=weighting_space, incremental=False,\
              on_add_simplex=callback, sampling_space=sampling_space, \
              simplex_budget=simplex_budget, design=design)
              
    tri.integrate()
                
    # TRI-compatible estimation
    # -1 = 'outside', 0=success, 1=failure, 2=mix
    estimations = tri.get_pf_estimation()
    #č doplním
    estimations['global_stats']['outside'] = outside
    
    result = {**estimation, **estimations}
    # try to put it to the BlackBox
    try:
        sample_box.estimations.append(result)
    except: #č asi ani nebudu neuspěch hlasit
        pass
        
    return result
        




def fast_simplex_estimation(sample_box, model_space='Rn', sampling_space=None, weighting_space=None,\
                                            outside_budget=1000, simplex_budget=100, design=None, callback=None):
    
    
    #č vytahneme ze sample_boxu rozdělení
    f = sample_box.f_model
    
    
    #č zde provadím rozdělení na prostor, ve kterém vzorkujem
    #čs a prostor "modelu", vô ktôrom, v podstatě, měříme vzdaleností
    sampled_plan_model = getattr(sample_box, model_space)
    if sampling_space is None:
        sampling_space = model_space
    
    if weighting_space is None:
        weighting_space = model_space
        
    
    #č jsou to informace pro callback 
    estimation={'method': "fast_simplex_estimation", 'nsim':sample_box.nsim}
    estimation['model_space'] = model_space
    estimation['sampling_space'] = sampling_space
    estimation['weighting_space'] = weighting_space
    estimation['outside_budget'] = outside_budget
    estimation['simplex_budget'] = simplex_budget
    estimation['design'] = str(design)
        
    # powerset_correction=True
    #č totíž my zodpovidáme za to, že Triangulaci pošleme správné ISSI 
    issi, outside = _issi_estimate_outside(f, model_space,\
                     sampling_space=sampling_space, powerset_correction=True,\
                design=design, callback=callback, outside_budget=outside_budget)
    
    #č na fastě môžem si dovoliť zkratit cestu 
    failsi = sample_box.failsi
    if np.any(failsi) and not np.all(failsi):
        tri = six.FastSamplingTriangulation(sample_box, tri_space=model_space, issi=issi, \
                 weighting_space=weighting_space, incremental=False,\
                  on_add_simplex=callback, sampling_space=sampling_space, \
                  simplex_budget=simplex_budget, design=design)
                  
        tri.integrate()
                    
        # TRI-compatible estimation
        # -1 = 'outside', 0=success, 1=failure, 2=mix
        estimations = tri.get_pf_estimation()
        #č doplním
        estimations['global_stats']['outside'] = outside
        
        result = {**estimation, **estimations}
        
    elif np.all(failsi):
        # TRI-compatible estimation
        # -1=outside, 0=success, 1=failure, 2=mix
        #č dostaneme vyrovnané odhady Brna-města (-2) a Brna-venkova (-1)
        #č veškerej vnitršek je v poruše
        pf_inside = issi.estimations[-2]
        pf_outside = issi.estimations[-1]
        
        global_stats = dict()
        global_stats['outside'] = outside
        global_stats['success'] = 0
        global_stats['failure'] = 0 # nechce se mi z ISSI vytahovat
        global_stats['mix'] = 0 
        
        # -1=outside, 0=success, 1=failure, 2=mix
        result = {**estimation, \
                'TRI_estimation': {-1:pf_outside, 0:0, 1:pf_inside, 2:0}, \
                'global_stats': global_stats,'vertex_estimation' : pf_inside, \
                'weighted_vertex_estimation' : pf_inside}
        
    else:
        # TRI-compatible estimation
        # -1=outside, 0=success, 1=failure, 2=mix
        #č dostaneme vyrovnané odhady Brna-města (-2) a Brna-venkova (-1)
        #č vnitršek je asi v pořadku
        pf_inside = issi.estimations[-2]
        pf_outside = issi.estimations[-1]
        
        global_stats = dict()
        global_stats['outside'] = outside
        global_stats['success'] = 0 # nechce se mi z ISSI vytahovat
        global_stats['failure'] = 0
        global_stats['mix'] = 0 
        
        # -1=outside, 0=success, 1=failure, 2=mix
        result = {**estimation, \
                'TRI_estimation': {-1:pf_outside, 0:pf_inside, 1:0, 2:0}, \
                'global_stats': global_stats,'vertex_estimation' : 0, \
                'weighted_vertex_estimation' : 0}
            
    # try to put it to the BlackBox
    try:
        sample_box.estimations.append(result)
    except: #č asi ani nebudu neuspěch hlasit
        pass
        
    return result




#č weighting space nechám pro bodové odhady pf
#č ale podle mně nemá význam
def fast_simplex_cubature(sample_box, tn_scheme, model_space='Rn', sampling_space=None, weighting_space=None,\
                                            outside_budget=1000, callback=None, design=None):
    """
    Delaunay triangulation
    """
    
    #č vytahneme ze sample_boxu rozdělení
    f = sample_box.f_model
    
    
    #č zde provadím rozdělení na prostor, ve kterém vzorkujem
    #čs a prostor "modelu", vô ktôrom, v podstatě, měříme vzdaleností
    sampled_plan_model = getattr(sample_box, model_space)
    if sampling_space is None:
        sampling_space = model_space
    
    if weighting_space is None:
        weighting_space = model_space
        
    
    #č jsou to informace pro callback 
    estimation={'method': "fast_simplex_cubature", 'nsim':sample_box.nsim}
    estimation['tn_scheme'] = tn_scheme.name
    estimation['model_space'] = model_space
    estimation['sampling_space'] = sampling_space
    estimation['weighting_space'] = weighting_space
    estimation['outside_budget'] = outside_budget
    estimation['design'] = str(design)
        
    
    # powerset_correction=True
    #č totíž my zodpovidáme za to, že Triangulaci pošleme správné ISSI 
    issi, outside = _issi_estimate_outside(f, model_space,\
                     sampling_space=sampling_space, powerset_correction=True,\
                design=design, callback=callback, outside_budget=outside_budget)
    
    #č na fastě môžem si dovoliť zkratit cestu 
    failsi = sample_box.failsi
    if np.any(failsi) and not np.all(failsi):
        tri = six.FastCubatureTriangulation(sample_box, tn_scheme, tri_space=model_space, issi=issi, \
                 weighting_space=weighting_space, incremental=False,\
                  on_add_simplex=callback)
                  
        tri.integrate()
                    
        # TRI-compatible estimation
        # -1 = 'outside', 0=success, 1=failure, 2=mix
        estimations = tri.get_pf_estimation()
        #č doplním
        estimations['global_stats']['outside'] = outside
        
        result = {**estimation, **estimations}
        
    elif np.all(failsi):
        # TRI-compatible estimation
        # -1=outside, 0=success, 1=failure, 2=mix
        #č dostaneme vyrovnané odhady Brna-města (-2) a Brna-venkova (-1)
        #č veškerej vnitršek je v poruše
        pf_inside = issi.estimations[-2]
        pf_outside = issi.estimations[-1]
        
        global_stats = dict()
        global_stats['outside'] = outside
        global_stats['success'] = 0
        global_stats['failure'] = 0 # nechce se mi z ISSI vytahovat
        global_stats['mix'] = 0 
        
        # -1=outside, 0=success, 1=failure, 2=mix
        result = {**estimation, \
                'TRI_estimation': {-1:pf_outside, 0:0, 1:pf_inside, 2:0}, \
                'global_stats': global_stats,'vertex_estimation' : pf_inside, \
                'weighted_vertex_estimation' : pf_inside}
        
    else:
        # TRI-compatible estimation
        # -1=outside, 0=success, 1=failure, 2=mix
        #č dostaneme vyrovnané odhady Brna-města (-2) a Brna-venkova (-1)
        #č vnitršek je asi v pořadku
        pf_inside = issi.estimations[-2]
        pf_outside = issi.estimations[-1]
        
        global_stats = dict()
        global_stats['outside'] = outside
        global_stats['success'] = 0 # nechce se mi z ISSI vytahovat
        global_stats['failure'] = 0
        global_stats['mix'] = 0 
        
        # -1=outside, 0=success, 1=failure, 2=mix
        result = {**estimation, \
                'TRI_estimation': {-1:pf_outside, 0:pf_inside, 1:0, 2:0}, \
                'global_stats': global_stats,'vertex_estimation' : 0, \
                'weighted_vertex_estimation' : 0}
            
    # try to put it to the BlackBox
    try:
        sample_box.estimations.append(result)
    except: #č asi ani nebudu neuspěch hlasit
        pass
        
    return result
    


#č weighting space nechám pro bodové odhady pf
#č ale podle mně nemá význam
def full_simplex_cubature(sample_box, tn_scheme, model_space='Rn',\
                         weighting_space=None, callback=None):
    """
    Delaunay triangulation
    """
    if weighting_space is None:
        weighting_space = model_space
        
    
    #č jsou to informace pro callback 
    estimation={'method': "full_simplex_cubature", 'nsim':sample_box.nsim}
    estimation['tn_scheme'] = tn_scheme.name
    estimation['model_space'] = model_space
    estimation['weighting_space'] = weighting_space
        
    tri = six.FullCubatureTriangulation(sample_box, tn_scheme, tri_space=model_space, \
             weighting_space=weighting_space, incremental=False,\
              on_add_simplex=callback)
              
    tri.integrate()
                
    # TRI-compatible estimation
    # -1 = 'outside', 0=success, 1=failure, 2=mix
    estimations = tri.get_pf_estimation()
    
    result = {**estimation, **estimations}
        
            
    # try to put it to the BlackBox
    try:
        sample_box.estimations.append(result)
    except: #č asi ani nebudu neuspěch hlasit
        pass
        
    return result
