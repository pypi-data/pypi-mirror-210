# -*- coding: utf-8 -*-
#♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥
"""
♥Люкиськон яке люкаськон понна функциос?

Clustering and decomposition are nearly the same, right?


U Voroného diagramu ani není jásně co vlastně děláme - 
dělíme prostor na úseky, nebo přířazujeme části prostoru jednotlivým vzorkům, sjednocujeme tečíčky?
Stejně tak nerozlišitelně se to popísuje v udmurtštině - slovy ľukiš'kón a ľukaš'kón.
"""

"""
kechato actually means checked, checkered, here denotes something like "orthogonal net"    

kěčató znamená kostkovaný
"""
#♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥

import numpy as np
#import numpy.ma as ma
#import scipy.stats as stats
#import pandas as pd


    # vtipné ǐ-čko
def kechato_potential(samples, candidates, weights=None, kechato_space='U'):
    
    
    samples_model = getattr(samples, kechato_space)
    nsim, nvar = np.shape(samples_model) 
    
    candidates_model = getattr(candidates, kechato_space)
    nis = len(candidates_model)
    
    PDF = samples.pdf(kechato_space)
    pdf = candidates.pdf(kechato_space)
    
    if weights is None:
        weights = (1 for __ in range(nsim))
    
    # kechato potential
    ksee = np.ones(nis)
    
    for i, pivot_point, weight in zip(range(nsim), samples_model, weights): # for all points in sample
        
        deltas = np.abs(candidates_model - pivot_point)
        bases = np.prod(deltas, axis=1)
        # kruci, je to na dobrou diskusi
        # ale prečo chcu aby potenciál byl nulový 
        # u kandidatů s nulovou hustotou
        #heights = (PDF[i] + pdf) / 2
        # uarianta 1
        #heights = pdf
        # uarianta 2
        heights = np.sqrt(PDF[i] * pdf)
        volumes = bases * heights
            
        # side effect
        ksee *= volumes * weight
                
    
    return ksee            












# ToDo normování prostoru. Jak?
def IS_localized_candidates(wx, nis_budget): # wx like whitebox
    nsim, nvar = np.shape(wx.sampled_plan_P)
        
    
    sampled_plan_Rn_ma = np.ma.asarray(wx.sampled_plan_Rn)
    
    # minimálně jeden kandidat u vzorku
    nis = round(nis_budget/nsim) + 1
    
    # loop over points 
    hplans = []
    for i in range(nsim): 
        
        sampled_plan_Rn_ma.mask = ma.nomask
        sampled_plan_Rn_ma[i] = ma.masked
        
        # find distance to the nearest sampling point (from all points)
        mindist = np.min(np.sum(np.square(sampled_plan_Rn_ma - wx.sampled_plan_Rn[i]), axis=1))**0.5
                                 
        # set the minimum distance as the standard deviation of IS densisty
        h_i = [stats.norm(wx.sampled_plan_Rn[i,j], 2*mindist ) for j in range(nvar)] #! dosadit  standard deviation pddle chutí
                                 
        # use IS sampling density with center equal to the current point
                                 
        # select nis points from IS density 
                                 
        h_plan_Rn = np.zeros((nis, nvar))
        for j in range(nvar):
            h_plan_Rn[:, j] = h_i[j].ppf(np.random.random(nis)) # realizace váhové funkce náhodné veličiny
    
        # Rozptyl corrected IS
        #weights_sim = np.prod([f_i[j].pdf(h_plan_Rn[:, j]) / h_i[j].pdf(h_plan_Rn[:, j]) for j in range(nvar)], axis=0) # [f1/h1, ..., fn/hn]
    
        # není ani nutný
        #weights_sim = wx.pdf(wx.Rn2R(h_plan_Rn)) * np.prod([1 / h_i[j].pdf(h_plan_Rn[:, j]) for j in range(nvar)], axis=0) 
       
        hplans.append(h_plan_Rn)       
       
    # ToDo
    # ale zatím to neřeším
    candidates_Rn = np.vstack(hplans)
    candidates_R = wx.Rn2R(candidates_Rn)
    candidates_Rd = wx.R2Rd(candidates_R) # candidates_R * wx.alpha
    
    candidates_P = wx.R2P(candidates_R)
    
    
    candidates_to_sample, candidates_mask, ivortodon, min_P_distances, overall_probabilities = entropy_estimation(wx.sampled_plan_P, wx.sampled_plan_Rd, candidates_P, candidates_Rd, wx.corners, wx.corner_values, wx.failsi, wx.PDF)
    
    
    return candidates_P, candidates_Rd, candidates_to_sample, min_P_distances, ivortodon, candidates_mask





def kechato_candidates(sampled_plan_P, sampled_plan_Rd, sorted_plan_P, f_i, corner_values, failsi, PDF, alpha, сэрегъёс, odhady):
    nsim, nvar = np.shape(sampled_plan_P)    
    
    # kechato here means "orthogonal net"    
    # kěčato znamená kostkovaný
    

    # шоръёсты шертем лыдъетлэсь кечато лыдъетлы пуктыськом
    # 1D arrays of midpoints between existing points in U-space
    kechato_list = []
    for i in range(nvar):
        sertem_vertices = []
        for j in range(len(sorted_plan_P[i]) - 1):
            sertem_vertices.append((sorted_plan_P[i][j+1] + sorted_plan_P[i][j]) / 2)
        kechato_list.append(sertem_vertices)
    
    # build an Nv-dimensional grid from the lists: the candidates
    kechato_grid_P = np.array( discrepancy_grid(kechato_list) )

    
    
    # pomocnej seznam pro výpočet objemů. Sestavá se z délek podel každé osy
    bydzjala_list = [] #list of lengths
    for i in range(nvar):
        sertem_list = [] #1D list
        for j in range(len(sorted_plan_P[i]) - 1):
            sertem_list.append(sorted_plan_P[i][j+1] - sorted_plan_P[i][j])
        bydzjala_list.append(sertem_list) #nv-dimensional list of 1D lists
    
    # Vobjemy. Sorry, chtěl jsem říct objemy.
    kechatlen_bydzjalaosty = np.prod(discrepancy_grid(bydzjala_list), axis=1)
    kechatlen_bydzjalaosty = np.array(kechatlen_bydzjalaosty)
    
    # počet grid bodů   (Ns+1)^Nv
    ketchatlen_lyd = len(kechatlen_bydzjalaosty)
    
    # grid points in the sampling space
    kechato_grid_R = np.empty([ketchatlen_lyd, nvar])
    for i in range(nvar):
        kechato_grid_R[:, i] = f_i[i].ppf(kechato_grid_P[:, i])
        
        
    # ToDo
    # ale zatím to neřeším
    kechato_grid_Rd = kechato_grid_R * alpha
    
    
    
    candidates_to_sample, candidates_mask, ivortodon, min_P_distances, overall_probabilities = entropy_estimation(sampled_plan_P, sampled_plan_Rd, kechato_grid_P, kechato_grid_Rd, сэрегъёс, corner_values, failsi, PDF)
    
    
    kechato_upper_bound = np.matmul(np.ceil(overall_probabilities), kechatlen_bydzjalaosty) 
    kechato_failure_rate = np.matmul(overall_probabilities, kechatlen_bydzjalaosty) 
    kechato_lower_bound = np.matmul(np.floor(overall_probabilities), kechatlen_bydzjalaosty) 
    print("kechato_failure_rate: ", kechato_failure_rate)

    
    odhady['kechato_upper_bound'][0].append(nsim)
    odhady['kechato_upper_bound'][1].append(kechato_upper_bound)
    odhady['kechato_failure_rate'][0].append(nsim)
    odhady['kechato_failure_rate'][1].append(kechato_failure_rate)
    odhady['kechato_lower_bound'][0].append(nsim)
    odhady['kechato_lower_bound'][1].append(kechato_lower_bound)    
    
    return kechato_grid_P, kechato_grid_Rd, candidates_to_sample, min_P_distances, ivortodon, candidates_mask






def entropy_estimation(sampled_plan_P, sampled_plan_Rd, kechato_grid_P, kechato_grid_Rd, сэрегъёс, corner_values, failsi, PDF):
    nsim, nvar = np.shape(sampled_plan_P)    
    nis = len(kechato_grid_P) # here means number of candidates
    
    min_P_distances = [] #potentials at grid points (candidates)
    
    dosah_lydjet = [] #list of visibility of simulation points from the viewpoint of each grid point
    
    quadrant_wise_reach = [] # kechato_grid size.... visibility in separate qudrants

    
    
    
    
    for i in range(nis): #in all grid points
        
        
        inode2points_P_matrix = sampled_plan_P - kechato_grid_P[i]
        
        node_quadrants = [] # size of 2**nvar
        
        
        
        for j in range(2**nvar):
            quadrant_points = []
            vyl_node_kusypjos = сэрегъёс[j] - kechato_grid_P[i]
            #quadrant_filter = (np.sign(inode2points_P_matrix) == np.sign(vyl_node_kusypjos)).all(axis=1)
            # je lepší z hlediska simulací na stejných souřadnicích
            quadrant_filter = np.logical_not((np.sign(inode2points_P_matrix) != np.sign(vyl_node_kusypjos)).any(axis=1))
            
            quadrant_selection = np.copy(inode2points_P_matrix[quadrant_filter])
            indexes = np.array(range(nsim))[quadrant_filter] # pomocnej seznam
            
            #np.argmin(np.sum(np.abs(quadrant_selection), axis=1))
            
            for _k in range(len(quadrant_selection)):
                k = np.argmin(np.sum(np.abs(quadrant_selection), axis=1))
                quadrant_points.append(indexes[k])
                #vuz_node_kusypjos = vyl_node_kusypjos
                #vyl_node_kusypjos = quadrant_selection[k] - kechato_grid_P[i]
                quadrant_filter = np.min(np.subtract(quadrant_selection, quadrant_selection[k]) * np.sign(vyl_node_kusypjos), axis=1) < 0
                quadrant_selection = np.copy(quadrant_selection[quadrant_filter])
                indexes = np.copy(indexes[quadrant_filter]) # pomocnej seznam
                if len(quadrant_selection) == 0:
                    break
                
            #simulation points that are visible from current grid point in each quadrant
            node_quadrants.append(quadrant_points)
        
        
        #simulation points that are vidible from each grid point in each quadrant
        quadrant_wise_reach.append(node_quadrants)
        
        dosah_lydjet.append([item for sublist in node_quadrants for item in sublist])


        
    
    
    # není nutný, přenejmenším zatím
    #==============================================================================
    # 
    #PDF_gridu = np.empty(ketchatlen_lyd)
    #for i in range(ketchatlen_lyd):
    #    PDF_gridu[i] = np.prod([f_i[j].pdf(kechato_grid_R[i][j]) for j in range(nvar)])
    # 
    # 
    # 
    #==============================================================================
    
    
    
    
    
    # vyhodnocení
    
    # entropy (calculated from estimated probability that failure will occur at a candidate point)
    ivortodon = [] 

    
    # pravděpodobnostní pole
    overall_probabilities = np.empty(nis)
    
    быгатонлыкъёс = np.empty([nis, 2]) # 2_point_Voronoi probabilities
    #heat_probabilities = np.empty([ketchatlen_lyd, 2])
    quadrant_probabilities = np.empty([nis, 2])
    
    
    
    candidates_to_sample = []
    candidates_mask = np.empty(nis, bool)
    
    # vyhodnocení v každém bodě
    for i in range(nis):    
        # will only consider candidate points that see both: failure and success
#==============================================================================
#         I_ve_got_joy = False
#         I_ve_got_sorrow = False
#==============================================================================
        #pdf_sum = 0 # nazev není úplně korektní. Spíše suma váh
        success_weight = 0
        failure_weight = 0
        
        # hledáme nejbližší body
        success_Rd_distance = np.inf
        failure_Rd_distance = np.inf
        
        
        # Netscape Navigator
#==============================================================================
#         boundary_navigator = False
#         for var in range(nvar):
#             if kechato_grid_P[i][var] < np.min(sampled_plan_P[:, var]):
#                 boundary_navigator = True
#                 break
#             elif kechato_grid_P[i][var] > np.max(sampled_plan_P[:, var]):
#                 boundary_navigator = True
#                 break
#==============================================================================
        
        
        
        min_P_prod_distance = 1
        
        min_Rd_distance_1 = np.inf
        min_Rd_distance_2 = np.inf
        

        # сэрегъёс - rohy
        # zpracování rohů лэсьтыны кулэ
        # zatím se předpokladá, že jsou v někonečnu s nulovou hustotou

        ## kvadrantové omezení
        # 
        visible_corner = False # kandidat vidí alespoň jeden někaký rozík
        
        quadrant_approved = False # chcete tu vzorek?
        failuring_quadrants = 0
        countable_quadrants = 2**nvar
        for j in range(2**(nvar-1)):
            quadrant_mixed = False 
            inert_corner = False 
            crossing_corner = False # zda je jeden z těchto dvou kvadrantů je prazdnej
            
            # první kvadrant
            if quadrant_wise_reach[i][j]:
                quadrant_1 = failsi[quadrant_wise_reach[i][j][0]]
                failure_quadrant = float(quadrant_1)
                for point in quadrant_wise_reach[i][j][1:]:
                    if failsi[point] != quadrant_1:
                        # davaj do svidanija!
                        quadrant_mixed = True
                        failure_quadrant = 0.5
                
            elif corner_values[j] == -1:
                inert_corner = True
                failure_quadrant = 0.0
                countable_quadrants -= 1
                visible_corner = True # nutný?
            else:
                crossing_corner = True
                visible_corner = True
                quadrant_1 = corner_values[j] != 1
#==============================================================================
#                 if quadrant_1:                    
#                     I_ve_got_sorrow = True
#                 else:
#                     I_ve_got_joy = True
#==============================================================================
                failure_quadrant = float(quadrant_1)
                # krychličku počítáme aj do rohů
#==============================================================================
#                 vyl_node_kusypjos = сэрегъёс[j] - kechato_grid_P[i]
#                 prod_distance_P = np.prod(np.abs(vyl_node_kusypjos))
#                 if prod_distance_P < min_P_prod_distance:
#                      min_P_prod_distance = prod_distance_P
#==============================================================================
            failuring_quadrants += failure_quadrant
            
            # protílehlý kvadrant
            if quadrant_wise_reach[i][-j-1]:
                quadrant_2 = failsi[quadrant_wise_reach[i][-j-1][0]]
                failure_quadrant = float(quadrant_2)
                for point in quadrant_wise_reach[i][-j-1][1:]:
                    if failsi[point] != quadrant_2:
                        # davaj do svidanija!
                        quadrant_mixed = True
                        failure_quadrant = 0.5
            elif corner_values[-j-1] == -1:
                inert_corner = True
                failure_quadrant = 0.0
                countable_quadrants -= 1
                visible_corner = True # nutný?
            else:
                crossing_corner = True
                visible_corner = True
                quadrant_2 = corner_values[-j-1] != 1
#==============================================================================
#                 if quadrant_2:                    
#                     I_ve_got_sorrow = True
#                 else:
#                     I_ve_got_joy = True
#==============================================================================
                
                failure_quadrant = float(quadrant_2)
                # krychličku počítáme aj do rohů
#==============================================================================
#                 vyl_node_kusypjos = сэрегъёс[-j-1] - kechato_grid_P[i]
#                 prod_distance_P = np.prod(np.abs(vyl_node_kusypjos))
#                 if prod_distance_P < min_P_prod_distance:
#                      min_P_prod_distance = prod_distance_P
#==============================================================================
            failuring_quadrants += failure_quadrant
                
            # teď kontroly
            # zda v kvadrantu naprotí roru se mění znamenko
            if not (inert_corner or quadrant_mixed or quadrant_1 == quadrant_2) and crossing_corner:
                quadrant_approved = True
                
        
        
        
        # procházíme simulacemi v dohlednu
        for j in dosah_lydjet[i]:
            
            
            
            # tento kus kódu spíš pro vzorkovaní
            #point_P_distance = np.sum(np.abs(sampled_plan_P[j] - kechato_grid_P[i]))
            prod_distance_P = np.prod(np.abs(sampled_plan_P[j] - kechato_grid_P[i]))
            if prod_distance_P < min_P_prod_distance:
                min_P_prod_distance = prod_distance_P
                
            
            # tento kus kódu spíš pro vyhodnocení
            point_Rd_distance = np.sum(np.abs(sampled_plan_Rd[j] - kechato_grid_Rd[i]))
            
            
            # two nearest points
            if point_Rd_distance < min_Rd_distance_1:
                min_Rd_distance_2 = min_Rd_distance_1
                min_Rd_distance_1 = point_Rd_distance
            elif point_Rd_distance < min_Rd_distance_2:
                min_Rd_distance_2 = point_Rd_distance
            
            
            point_weight = PDF[j] / point_Rd_distance
            #pdf_sum += point_weight
            if failsi[j] and point_Rd_distance < failure_Rd_distance:
                failure_weight = point_weight
                failure_Rd_distance = point_Rd_distance
                
            elif not failsi[j] and point_Rd_distance < success_Rd_distance:
                success_weight = point_weight
                success_Rd_distance = point_Rd_distance
                
                
#==============================================================================
#             if failsi[j]:
#                 I_ve_got_sorrow = True
#             else:
#                 I_ve_got_joy = True
#==============================================================================

                
                
        
        
        
        # počítame pravděpodobnosti v bodech gridu a entropii
        #        
        # podle Rd vzdáleností a pdf
        #if pdf_sum > 0:
        
        min_P_distances.append(min_P_prod_distance)
        
        fs_weight = failure_weight + success_weight
        быгатонлыкъёс[i] = [failure_weight/fs_weight, success_weight/fs_weight]        
        
        # countable_quadrants -> disregard mixed ones
        quadrant_probabilities[i] = [failuring_quadrants/countable_quadrants, 1 - failuring_quadrants/countable_quadrants]
        
        # kvadrantový a heat estimatory dohromady
#==============================================================================
#         if nsim == 1:
#             node_pf = quadrant_probabilities[i][0]
#         elif visible_corner:
#             node_pf = (X_mesh[i] + quadrant_probabilities[i][0]) / 2
#         else:
#             node_pf = X_mesh[i]
#==============================================================================
            
        # kvadrantový a 2_point_Voronoi estimatory dohromady
        if visible_corner: # if visible, then average of 2p voronoi and quadrant 
            node_pf = (быгатонлыкъёс[i][0] + quadrant_probabilities[i][0]) / 2
            overall_probabilities[i] = node_pf
        else: # inside will only use 2p Voronoi
            node_pf = быгатонлыкъёс[i][0]
            overall_probabilities[i] = node_pf
        
        #node_pf = Least_square_probabilities[i][0]

        #  !!!! ENTROPY !!!
        if node_pf > 0 and node_pf < 1:
            кечатлэн_ивортодон = -node_pf*np.log(node_pf) - (1-node_pf)*np.log(1-node_pf)
        else:
            кечатлэн_ивортодон = 0
            
        ivortodon.append(кечатлэн_ивортодон)
        
        fs_Rd_distance = success_Rd_distance + failure_Rd_distance 
        

        if min_Rd_distance_2 != np.inf:    
            point_distance_approved = np.divide(min_Rd_distance_1 + min_Rd_distance_2, fs_Rd_distance) > 0.99
        else:
            point_distance_approved = False
        #if I_ve_got_joy and I_ve_got_sorrow and ((min_Rd_distance_1 + min_Rd_distance_2) / fs_Rd_distance > 0.99 or corner_explorer):
        if visible_corner and quadrant_approved  or  point_distance_approved: # and not visible_corner:
        #if I_ve_got_joy and I_ve_got_sorrow:
            candidates_to_sample.append(i)
            candidates_mask[i] = True
        else:
            candidates_mask[i] = False
            
    return candidates_to_sample, candidates_mask, ivortodon, min_P_distances, overall_probabilities
            
















w_sim = int(5e5) # zhruba zadava jemnost gridu
def w_grid(w_sim, nvar):
    
    n_grid = round(w_sim ** (1/nvar))
    #print("jemnost gridu  n_grid = " + str(n_grid))
    w_sim = n_grid**nvar
    #print("počet váhových bodů  w_sim = " + str(w_sim))

    #generuje rovnomerny vahovy grid ve 0-1 prostoru
    weight_plan = np.empty([w_sim, nvar])
    for i in range(w_sim):
        for j in range(nvar):
            if j==0: 
                quotient, modulo = divmod(i, n_grid)
                weight_plan[i, j] =  (modulo + 0.5) / n_grid
            else: 
                quotient, modulo = divmod(i, n_grid ** (j+1))
                quotient, modulo = divmod(modulo, n_grid ** j)
            
                weight_plan[i, j] = (quotient + 0.5) / n_grid 
    return weight_plan


def n_size_grid(n_grid, nvar):
    
    w_sim = n_grid**nvar
    #print("počet váhových bodů  w_sim = " + str(w_sim))

    #generuje rovnomerny vahovy grid ve 0-1 prostoru
    weight_plan = np.empty([w_sim, nvar])
    for i in range(w_sim):
        for j in range(nvar):
            if j==0: 
                quotient, modulo = divmod(i, n_grid)
                weight_plan[i, j] =  (modulo + 0.5) / n_grid
            else: 
                quotient, modulo = divmod(i, n_grid ** (j+1))
                quotient, modulo = divmod(modulo, n_grid ** j)
            
                weight_plan[i, j] = (quotient + 0.5) / n_grid 
    return weight_plan
    
    
    
def discrepancy_grid(sorted_plan):
    # data frame 1
    d0 = {'ID':1,
      -1:pd.Series(sorted_plan[0])}
    dfr = pd.DataFrame(d0)
    
    for i in range(len(sorted_plan)-1):
        
        # next data frame 
        d = {'ID':1, i:pd.Series(sorted_plan[i+1])}
        df = pd.DataFrame(d)
        
        
        # outer join in python pandas
        dfr = pd.merge(dfr, df, how='outer')
        
    dfr.drop('ID', axis=1, inplace=True)
    return dfr



# kechato_discrepancy(np.random.random((10, 2)))
def kechato_discrepancy(sampled_plan_P):
    # kechato here means "orthogonal net"    
    # kechato znamená ortogonální síť
    
    nsim, nvar = sampled_plan_P.shape
    
    sorted_plan_P = [i for i in range(nvar)] # just create list
    for i in range(nvar):
        sorted_plan_P[i] = np.concatenate(([0], np.sort(sampled_plan_P[:, i]), [1]))
        
    


        
    kechato_list = []
    for i in range(nvar):
        sertem_vertices = [] # i.e. sorted
        for j in range(len(sorted_plan_P[i]) - 1):
            sertem_vertices.append((sorted_plan_P[i][j+1] + sorted_plan_P[i][j]) / 2) # i.e. sorted
        kechato_list.append(sertem_vertices)
    
    
    kechato_grid_P = np.array( discrepancy_grid(kechato_list) )
    
    
    
    
    bydzjala_list = []
    for i in range(nvar):
        sertem_list = []
        for j in range(len(sorted_plan_P[i]) - 1):
            sertem_list.append(sorted_plan_P[i][j+1] - sorted_plan_P[i][j])
        bydzjala_list.append(sertem_list)
    
    kechatlen_bydzjalaosty = np.prod( discrepancy_grid(bydzjala_list), axis=1 )
    
    
    
    ketchatlen_lyd = len(kechatlen_bydzjalaosty)
    
    
    # nepotřebuji pro "diskrepanciju"
#==============================================================================
#     kechato_grid_R = np.empty([ketchatlen_lyd, nvar])
#     for i in range(nvar):
#         kechato_grid_R[:, i] = f_i[i].ppf(kechato_grid_P[:, i])
#         
#     # ToDo
#     # ale zatím to neřeším
#     kechato_grid_Rd = kechato_grid_R 
#==============================================================================
    
        
    
    dosah_lydjet = []
    
    for i in range(ketchatlen_lyd):
        dosah_nodu = []
        for j in range(len(sampled_plan_P)):
            node_vatsano = True
            for k in dosah_nodu:
                vuz_node_kusypjos = sampled_plan_P[k] - kechato_grid_P[i]
                vyl_node_kusypjos = sampled_plan_P[j] - kechato_grid_P[i]
    
                if not (np.sign(vuz_node_kusypjos) == np.sign(vyl_node_kusypjos)).any():
                    next
                
                if np.max(np.subtract(vuz_node_kusypjos, vyl_node_kusypjos) * np.sign(vuz_node_kusypjos)) < 0:
                    node_vatsano = False
                    break
            if node_vatsano:
                dosah_nodu.append(j)
                
        dosah_nodu_2 = []
        for j in dosah_nodu:
            node_vatsano = True
            for k in dosah_nodu:
                if j==k:
                    next
                
                vuz_node_kusypjos = sampled_plan_P[k] - kechato_grid_P[i]
                vyl_node_kusypjos = sampled_plan_P[j] - kechato_grid_P[i]
    
                if not (np.sign(vuz_node_kusypjos) == np.sign(vyl_node_kusypjos)).any():
                    next
                
                if np.max(np.subtract(vuz_node_kusypjos, vyl_node_kusypjos) * np.sign(vuz_node_kusypjos)) < 0:
                    node_vatsano = False
                    break
            if node_vatsano:
                dosah_nodu_2.append(j)
            
        
        dosah_lydjet.append(dosah_nodu_2)
    
    
    
    # nepotřebuji pro "diskrepanciju"
#==============================================================================
#     PDF = np.empty(len(sampled_plan_P))
#     for i in range(len(PDF)):
#         PDF[i] = np.prod([f_i[j].pdf(f_i[j].ppf(sampled_plan_P[i][j])) for j in range(nvar)])
#     
#     
#     PDF_gridu = np.empty(ketchatlen_lyd)
#     for i in range(ketchatlen_lyd):
#         PDF_gridu[i] = np.prod([f_i[j].pdf(kechato_grid_R[i][j]) for j in range(nvar)])
#==============================================================================
    
    # nepotřebuji pro "diskrepanciju"
#==============================================================================
#     ivortodon = [] # informace
#     быгатонлыкъёс = [] # pravděpodobnosti
#     
#     for i in range(ketchatlen_lyd):    
#         weight_sum = 0
#         success_weight = 0
#         failure_weight = 0
#         for j in dosah_lydjet[i]:
#             point_weight = PDF[j] / np.sum(np.abs(sampled_plan_P[j] - kechato_grid_P[i]))
#             weight_sum += point_weight
#             if failsi[j]:
#                 failure_weight += point_weight
#             else:
#                 success_weight += point_weight
#                 
#                 
#         # zpracování rohů лэсьтыны кулэ
#                 
#         быгатонлыкъёс.append([failure_weight/weight_sum, success_weight/weight_sum])
#         кечатлэн_ивортодон = быгатонлыкъёс[i][0]*np.log(быгатонлыкъёс[i][0]) + быгатонлыкъёс[i][1]*np.log(быгатонлыкъёс[i][1])
#         if np.isnan(кечатлэн_ивортодон):
#             ivortodon.append(0)
#         else:
#             ivortodon.append(кечатлэн_ивортодон)
#==============================================================================
    
    
    
    # nepotřebuji pro "diskrepanciju"
#==============================================================================
#     PDF_сэрегъёслэн = np.empty(len(corner_values))
#     for i in range(len(PDF_сэрегъёслэн)):
#         PDF_сэрегъёслэн[i] = np.prod([f_i[j].pdf(f_i[j].ppf(сэрегъёс[i][j])) for j in range(nvar)])
#==============================================================================
    
    
    
    
    matice_zasahu = np.zeros([ketchatlen_lyd, ketchatlen_lyd], np.int8)
    np.fill_diagonal(matice_zasahu, 1)
    for i in range(ketchatlen_lyd):
        for j in range(i+1, ketchatlen_lyd):
            matice_zasahu[i,j] = 1
            for k in dosah_lydjet[i]:
                vuz_node_kusypjos = sampled_plan_P[k] - kechato_grid_P[i]
                vyl_node_kusypjos = kechato_grid_P[j] - kechato_grid_P[i]
    
                if not (np.sign(vuz_node_kusypjos) == np.sign(vyl_node_kusypjos)).any():
                    next
                
                if np.max(np.subtract(vuz_node_kusypjos, vyl_node_kusypjos) * np.sign(vuz_node_kusypjos)) < 0:
                    matice_zasahu[i,j] = 0
                    break
    
    matice_zasahu = symmetrize(matice_zasahu)
    
    kechatlen_adjzonezy = np.matmul(matice_zasahu, kechatlen_bydzjalaosty) # viditelnosti
    
    return np.sum(kechatlen_bydzjalaosty * kechatlen_adjzonezy)
    


def symmetrize(a):
    return a + a.T - np.diag(a.diagonal())
