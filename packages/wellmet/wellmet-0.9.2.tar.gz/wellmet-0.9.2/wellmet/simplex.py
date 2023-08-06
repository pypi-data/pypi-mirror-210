#!/usr/bin/env python
# coding: utf-8

import gc
import numpy as np
from . import IS_stat
from . import sball
from . import f_models
from .candynodes import CandyNodes
from scipy import spatial
from scipy import stats
from scipy import optimize

import quadpy

from typing import NamedTuple
from collections import namedtuple, defaultdict
from sortedcollections import ValueSortedDict




#č napadlo mě zababáchnuť třidu, která by se sama starala o všem co se tyče 
#č vnější domény. Nešlo mě totíž to udělat jednou funkcí, bylo by velmi
#č špatné z hlediska zodpovednosti kódu. Tak to všecko zabalíme to třidy  
#č a odebereme z už beztak přetíženého blackboxu část komplexity
# keywords: ISSI, estimation, outside, ConvexHull, Sball, IS kolem středních hodnot
class Shull: # issi_estimate_outside
    def __init__(sx, f, model_space, sampling_space='G', \
                 powerset_correction=True, incremental=True, design=None):
        #č tím powerset_corretion je myšlena úplná soustava jevů,
        #č tj. vyrovnaní s použitím míry vnější i vnitřní
        #č powerset_correction=True přídá -2 (inside) jev do ISSI
        
        #č zde f-ko musí taky obsahovat vzorky!
        sx.f = f
        sx.model_space = model_space
        
        #č kašlu na to, pokud uživatel zadal nesmysl, tak
        #č sam převedu do nečěho smyslúplnějšího
        _dict = {'R':'Rn', 'aR':'aRn', 'P':'GK', 'aP':'aGK', 'U':'G', 'aU':'aG'}
        if sampling_space in _dict:
            sx.sampling_space = _dict[sampling_space]
        else:
            sx.sampling_space = sampling_space
            
        sx.design = design
            
        sampled_plan_model = getattr(f, model_space)
        #č žádná kontrola chyb - nechť to spadné, když má spadnout!
        sx.convex_hull = spatial.ConvexHull(sampled_plan_model, incremental=incremental)
        
        # current outside probability estimation
        sx.p_out = 0.5 # implicit value
        sx.sball = sball.Sball(f.nvar)
        sx.base_r = sx.sball.get_r(0.5) # we want in average 50/50 ratio
        
            
        # -1 = 'outside'
        # -2 = 'inside'
        #č založme ISSI
        sx.powerset_correction = powerset_correction
        #č potřebuji pro korektnost mít před integrací zadané jevy 
        if powerset_correction:
            sx.oiss = IS_stat.ISSI([-1, -2]) 
        else:
            sx.oiss = IS_stat.ISSI([-1]) 
        
        
    
    def increment(sx, input_sample):
        #č sample by měl byt jíž převeden na f (v .add_sample()),
        #č zodpovidá za to volajicí kód!
        sx.convex_hull.add_points(getattr(input_sample, sx.model_space))
        
        
        
        # require
    def integrate(sx, nis):
        # getting rid of the old estimations
        sx.oiss.delete_event_data(-1)
        sx.oiss.events.append(-1) #č už tak trošku sahám do vnitřku cizí třidy
        if sx.powerset_correction:
            sx.oiss.delete_event_data(-2)
            sx.oiss.events.append(-2) #č a záse
    
        #č posunutí středu trošiňku porušuje předpoklady, za kterých 
        #č Sball volí rozdělení, ale přečo se mi stavá,
        #č že ve více dimenzích Shull na začatku prostě nemůže 
        #č trefit ten blbej... v podstatě simplex
        #č Těžiště, přesnějí, prostě nějaký střed můžeme najít dvěma způsoby: 
        #č 1. mean(vertices.model_space).sampling_space
        #č 2. mean(vertices.sampling_space)
        #č myslím si, že ten první (a bez váh) je stabilnější 
        #č (víme, jak střed vrcholů v nějakém prostoru může ani netrefit do 
        #č simplexu v původním prostoru)
#        vertices_model = sx.convex_hull.points[sx.convex_hull.vertices]
#        barycenter_model = np.mean(vertices_model, axis=0)
#        if sx.model_space == sx.sampling_space:
#            sx.barycenter_sampling = barycenter_model
#        else:
#            barycenter = sx.f.new_sample(barycenter_model, sx.model_space)
#            sx.barycenter_sampling = np.squeeze(getattr(barycenter, sx.sampling_space))

        #č rozhodl jsem, že shull musí odhadovat outside, ne motat se centrem Brna.
        #č předpokladám, že uživatel zadal buď G, nebo aspoň Rn prostor
        #sx.barycenter_sampling = np.full(sx.f.nvar, 0, dtype=np.int8)
        
        # first step
        nodes = sx._sample_sball(nis)
        mask = nodes.is_outside
        
        
        cut_off_out = int(nis/3)
        cut_off_in = int(nis/3)
        #č robím cyklus dokud nesberu dostatečně teček.
        #č To je fakt nejrobustnější řešení, co mě napadá
        # while (number_of_out_nodes or number_of_nodes_inside is too_small)
        while (len(mask[mask]) < cut_off_out): # or (len(mask[~mask]) < cut_off_in):
            print(sx.__class__.__name__ + ":", "cut off! Outsides: %s, insides: %s, p_out=%s"\
                                                 % (len(mask[mask]), len(mask[~mask]), sx.p_out))
            #č je třeba jenom sehnat dostatečně bodíků a utikat
            nodes.add_sample(sx._sample_sball(nis))
            mask = nodes.is_outside
            
        #č když neprovadíme výrovnání, tak ten vnitršek nachren nepotřebujem
        if (len(mask[~mask]) < cut_off_in) and sx.powerset_correction:
            print(sx.__class__.__name__ + ":", \
            "cut off inside (%s of %s needed)! Do simplex-based integration of convex hull"\
                                                     % (len(mask[~mask]), cut_off_in))
            
            nodes.add_sample(sx._sample_simplex(nis))
        
            
        return nodes
        
        
        
    def _sample_simplex(sx, nis):
        
        #č f-ko sice musí odkazovat na aktuální f_model
        #č ale na druhou stranu normálně ._integrate_simplex()
        #č potřebujeme pouze jednou - hned při vytvaření
        vertices = sx.f[sx.convex_hull.vertices]
        nvar = vertices.nvar
        
        # IS_like uses .new_sample method, so vertices can not be a SampleBox object
        #
        #č IS_like těžiště počítá v sampling_space, ale asi mu to až tak nevadí
        #
        # already divided by nsim in variance formule
        # divide by /(nvar+1)/(nvar+2) from simplex inertia tensor solution
        # multiply by simplex_volume, but it looks like it shouldn't be here
        # for simplex: d = nvar+2 
        #č sice to má nazev h_plan, ale nese rozdělení a hustoty v f-ku
        nodes = IS_stat.IS_like(vertices, sampling_space=sx.sampling_space, \
                nis=nis, d=nvar+2, design=sx.design)
        
        #č indikatorová funkce
        sx.is_outside(nodes)
        
        # for IS_stats
        #č zkoušel jsem zadavat celou serii - zhoršuje to odhady
        #č nemůžeme důvěrovat tomu, jak ten slepej simplex vidí svět
        weights = nodes.w[~nodes.is_outside]
        sx.oiss.add_single_event_data(weights, event=-2, nis=nis)
        # add_single_event_data() do not calculate estimations itself
        sx.oiss.get_estimations()
        return nodes
    
    
    
    def _sample_sball(sx, nis):
        nvar = sx.f.nvar
        sampling_r, sx.p_out = sx.sball.get_r_iteration(sx.p_out)
        #sampling_r = sx.sball.get_r(sx.p_out)
        
        #č asi tam bylo sampling_r/base_r, že?
        std_ball = sampling_r/sx.base_r
        #č chcu std=1, když p_out -> 1
        #č a std=sball_solušn, když p_out -> 0
        #č surovější nevymyslíš! 
        std = std_ball + sx.p_out
        #č u stats.norm zadáváme směrodatnou odchylku, je to asi správné
        #h = f_models.UnCorD([stats.norm(sx.barycenter_sampling[i], std) for i in range(nvar)])
        #nodes = IS_stat.IS(sx.f, h, space_from_h='R', space_to_f=sx.sampling_space,  Nsim=nis)
        
        #norm_params = [(sx.barycenter_sampling[i], std) for i in range(nvar)]
        nodes = IS_stat.IS_norm(sx.f, std=std, \
                sampling_space=sx.sampling_space, nis=nis, design=sx.design)
        
        outside_measure = sx._apply_nodes(nodes, nis)
        
        #č pro přiště
        sx.p_out = (sx.p_out + outside_measure) / 2
        
        return nodes
    
    
    def _apply_nodes(sx, nodes, nis):
        #č indikatorová funkce
        sx.is_outside(nodes)
        
        # for IS_stats
        if sx.powerset_correction:
            #č získáme výrovnaný odhad - je to skoro zdarma
            #svar = (sampling_r/sx.base_r)**2 # svar like sampling_variance
            #č kdysi snažil jsem něco odvést, moc se mi to nepovedlo
            #č je to jen tak, jeden z pokusu, hrubej nastřel
            #im = svar**nvar * np.exp(nvar/svar - nvar)
            
            #č radší ne. IM špatně zachycuje nizkou důvěru k tomu, co nemá vlastní tečky
            sx.oiss.add_IS_serie(nodes.w, nodes.event_id, implicit_multiplicator=np.inf)
            outside_measure = sx.oiss.estimations[-1]
        else:
            weights = nodes.w[nodes.is_outside]
            #č IM všecko pokazí, jakmile začnu přídávát další jevy
            sx.oiss.add_single_event_data(weights, event=-1, nis=nis)
            # add_single_event_data() do not calculate estimations itself
            weighted_mean, __, events = sx.oiss.get_means()
            # outside probability
            #č nevyrovnané!
            outside_measure = weighted_mean[events==-1][0]
            
        return outside_measure
    
    
    
    def is_outside(sx, nodes):
        node_coordinates = getattr(nodes, sx.model_space)
        mask = is_outside(sx.convex_hull, node_coordinates)
        
        # -1 = 'outside'
        # -2 = 'inside'
        nodes.event_id = mask - 2
        nodes.is_outside = mask



# https://math.stackexchange.com/questions/4056099/circumcenter-of-the-n-simplex/4064749
#оӵ таза (но визьмо) лу, Nico Schlömer!
#č pozdravuji zde Nico Schlömer :)
# My greetings to Nico Schlömer :)
class CircumCenter:
    def __init__(self, ndim):
        self.A = np.ones((ndim+2, ndim+2))
        self.b = np.ones(ndim+2)
        self.A[-1, -1] = 0
    
    def get_circumcenter(self, vertices):
        VV = vertices @ vertices.T
        self.A[:-1, :-1] = 2 * VV
        self.b[:-1] = np.diag(VV)
        x = np.linalg.solve(self.A, self.b)
        return vertices.T @ x[:-1]





#č vlastní slovník se dycky hodí
#č ten, na rozdil od defaultdict'a, neuklada chybejicí složky do slovníku
class DefaultDict(dict):
    def __init__(self, nvar):
        self.nvar = nvar
        
    def __missing__(self, key):
        return np.zeros(self.nvar, dtype=float)



class _NaiveSense:

    def _init(self):
        # I'll try to use dual name convention here
        # self for this class, sensibility-related things
        # sx for general Triangulation class related attributes
        sx = self
        
        nsim, nvar = sx.tri.points.shape

        self._local_scope = dict()
        self._to_parse = set()
        self._parsed = set()
        
        self.points = sx.tri.points
        self.failsi = sx.sample_box.failsi
        self.non_failsi = ~self.failsi
        self._point_mask = np.empty_like(self.failsi) 
        #self._scalars = np.empty(len(self.failsi))
        self._boolmask = np.empty_like(self.failsi)



        self.c_zeros = np.zeros(nvar + 1) # prices in terms of LP
        self.b_ub = -np.ones(nsim)
        
        self.A_ub = np.empty((nsim, nvar + 1))
        self.A_ub[:, :-1] = sx.tri.points
        self.A_ub[:, -1] = self.b_ub
        self.A_ub *= (self.failsi * 2 - 1).reshape(-1, 1)
        
        simplices = sx.tri.simplices
        self.mixed_mask = mixed_mask = sx.is_mixed(simplices)
        
        event_ids = np.empty(sx.tri.nsimplex + 1, dtype=np.int8)
        event_ids[:-1] = sx.get_events()
        event_ids[-1] = -1
        
        neighbors = sx.tri.neighbors
        neighbors_mask = event_ids[neighbors] == 2
        
        #č v těch otačkách budeme potřebovat pořad dokola
        self.neighbors_masked = neighbors_masked = dict() #defaultdict(list)
        zip_iter = zip(range(len(mixed_mask)), mixed_mask, neighbors, neighbors_mask)
        for id, is_mixed, neis, neis_mask in zip_iter:
            if not is_mixed:
                continue
            
            neighbors_masked[id] = neis[neis_mask]
        



    #č přes liblinear to taky jde
    #from liblinear import liblinearutil
    #pr = liblinearutil.problem(box.failsi, box.G)
    #param = liblinearutil.parameter('-s 2 -c 10000 -B 1')
    #m = liblinearutil.train(pr, param)
    #m.get_decfun()
    def get_separation_axis(self, mask):
        A_ub = self.A_ub[mask]
        b_ub = self.b_ub[:len(A_ub)]
        return optimize.linprog(self.c_zeros, A_ub=A_ub, b_ub=b_ub, 
                        options={'presolve':False}, method='highs-ds', 
                        bounds=(None, None))
        
        
    def perform_sensitivity_analysis(self):
        # I'll try to use dual name convention here
        # self for this class, sensitivity-related things
        # sx for general Triangulation class related attributes
        sx = self
        
        self._init()
        
        simplices = sx.tri.simplices
        mixed_mask = self.mixed_mask
        #nmixed = np.count_nonzero(mixed_mask)
        
        
        mixed_probability = 0
        global_gradient = np.zeros(sx.sample_box.nvar)
        sensitivities = np.zeros(sx.sample_box.nvar)
        
        depths = defaultdict(int)
        vectors = dict()
        probabilities = dict()
        
        for simplex_id, is_mixed in zip(range(len(mixed_mask)), mixed_mask):
            if not is_mixed:
                continue
            
            indices = simplices[simplex_id]
            
            #č poslední složka vektoru je buď nvar+1 dimenze 
            #č v případě get_simplex_normal()
            #č nebo offset aka bias 
            #
            # the last item of vector is either nvar+1 coordinate
            # in case of get_simplex_normal()
            # or offset aka bias
            # in case of separation axis
            # i.e. we should ignore it anyway
            depth = depths[simplex_id]
            if simplex_id in vectors:
                vector, scalars = vectors[simplex_id]
            else:
                vector = sx.get_simplex_normal(indices)[:-1]
                scalars = None
            
            scope, normal, scalars = self.process_simplex(simplex_id, depth, vector, scalars)
            
            # scale to unit length
            length = np.sqrt(np.inner(normal, normal))
            np.divide(normal, length, out=normal) 
            
            p_mixed = sx.get_simplex_probability(indices)
            mixed_probability += p_mixed
            probabilities[simplex_id] = p_mixed
            global_gradient += normal * p_mixed
            sensitivities += np.square(normal) * p_mixed
                
            #č tak. Teď do projděných simplexu píšeme jen vektor,
            #č do těch, co ještě musíme projít - vektor a skalární součin
            vectors[simplex_id] = normal
            new_depth = scope[simplex_id]
            depths[simplex_id] = new_depth
                
            if new_depth > depth:
                for id, new_depth in scope.items():
                    if (id > simplex_id) and (new_depth >= depths[id]):
                        vectors[id] = normal, scalars
                        depths[id] = new_depth
                
                
        #length = np.sqrt(np.inner(global_gradient, global_gradient))
        #global_gradient = global_gradient / length
        
        sensitivities /= mixed_probability
        
        return global_gradient, sensitivities, \
                probabilities, depths, vectors
        
                
        
    
        
        
        
        
        
    def is_separable(self, scalars, point_mask):
        #č postup se míří na 5-6D,
        #č kde je mou snahou zbytečně nealokovat
        #č na každém kolečku
        #scalars = self._scalars
        #č vector je již bez poslední složky
        #np.matmul(self.points, vector, out=scalars)
        mask = self._boolmask
        
        np.logical_and(point_mask, self.failsi, out=mask)
        #č boolean indexing se dycky alokuje 
        reds = scalars[mask] 
        #min_red = np.min(reds)
        max_red = np.max(reds)
        
        np.logical_and(point_mask, self.non_failsi, out=mask)
        #č boolean indexing se dycky alokuje 
        greens = scalars[mask] 
        min_green = np.min(greens)
        #max_green = np.max(greens)
        
        # ...........       ,,,,,,,,,,,,,
        # min_i   max_i    min_j       max_j
        #(max_green < min_red) != (max_red < min_green)
        
        # let's use vector's convention red < green
        return max_red < min_green
        
        
    def process_simplex(self, simplex_id, depth, vector, scalars):
        # self for this class, sensitivity-related things
        # sx for general Triangulation class related attributes
        sx = self
        
        points = self.points
        
        local_scope = self._local_scope
        local_scope.clear()
        local_scope[simplex_id] = 0
        
        to_parse = self._to_parse
        to_parse.clear()
        
        parsed = self._parsed
        parsed.clear()
        
        simplices = sx.tri.simplices
        neighbors_masked = self.neighbors_masked
        
        point_mask = self._point_mask
        point_mask[:] = False
        
        to_parse.update(neighbors_masked[simplex_id])
        point_mask[simplices[simplex_id]] = True
        
        for __i in range(depth):
            for key in local_scope.keys():
                local_scope[key] += 1
                
            to_parse -= local_scope.keys()
            to_parse, parsed = parsed, to_parse
            to_parse.clear()
            for id in parsed: # meant to be parsed in the cycle's end
                to_parse.update(neighbors_masked[id])
                point_mask[simplices[id]] = True
                local_scope[id] = 0
            
        
        assert local_scope[simplex_id] == depth
        
        npoints_now = np.count_nonzero(point_mask)
        #assert self.is_separable(vector, point_mask)
        
        #č běh smyčky je podmíněn tím, že má co dělat
        to_parse -= local_scope.keys()
        while len(to_parse): #č máme co dělat?
            
            #č projedeme várku simplexu, přídáme je do slovníku,
            #č "zapneme" přípojené k ním vzorky
            to_parse, parsed = parsed, to_parse
            to_parse.clear()
            for id in parsed: # meant to be parsed in the cycle's end
                to_parse.update(neighbors_masked[id])
                point_mask[simplices[id]] = True
                local_scope[id] = -1
            
            #č zkontrolujeme separabilitu.
            #č Nebude-li zajištěna, tak končíme s nedotknutými
            #č hloubkou a vektorem
            npoints_before, npoints_now = npoints_now, np.count_nonzero(point_mask)
            #if npoints_now == npoints_before: print("Sense: no new points to separate")
            if npoints_now > npoints_before:
                if scalars is None:
                    scalars = np.matmul(points, vector)
                if not self.is_separable(scalars, point_mask):
                    result = self.get_separation_axis(point_mask)
                    if not result.success: #č konec, zde končíme
                        if result.status != 2: # Problem appears to be infeasible.
                            print("Sense: linprog ended with status %s" % result.status)
                        return local_scope, vector, scalars
                    
                    #č hned odřízneme poslední složku - 
                    #č bude tam posunutí b aka offcet aka bias
                    vector = result.x[:-1]
                    scalars = None
            
            #č pokud jsme tu, tak vzorky byly separabilní,
            #č je na čase "navysit" hloubku
            for key in local_scope.keys():
                local_scope[key] += 1
        
            #č běh smyčky je podmíněn tím, že má co dělat
            to_parse -= local_scope.keys()
            
            
        return local_scope, vector, scalars
    
    
    
    
class FinalizedAxis(NamedTuple):
    normal: np.ndarray
    separated_simplices: set

class SensitivityResult(NamedTuple):
    global_gradient: np.ndarray
    sensitivities: np.ndarray
    shares: dict
    depths: dict
    vectors:dict
    coverings:dict
    unique_id_vectors: dict
    unique_set_vectors: dict
    
    
class _Sense:

    def _init(self):
        # I'll try to use dual name convention here
        # self for this class, sensibility-related things
        # sx for general Triangulation class related attributes
        sx = self
        
        nsim, nvar = sx.tri.points.shape

        
        
        #self.points = sx.tri.points
        #self.failsi = sx.sample_box.failsi
        #self.non_failsi = ~self.failsi
        #self._point_mask = np.empty_like(self.failsi) 
        #self._scalars = np.empty(len(self.failsi))
        #self._boolmask = np.empty_like(self.failsi)


        points = sx.tri.points
        failsi = sx.sample_box.failsi
        simplices = sx.tri.simplices
        
        self._local_scope = dict()
        #ё сепаратошная
        self.separability_solver = SeparationAxis(sx, self._local_scope)
        
        self._to_parse = set()
        self._parsed = set()
        
        
        
        self.mixed_mask = mixed_mask = sx.is_mixed(simplices)
        
        event_ids = np.empty(sx.tri.nsimplex + 1, dtype=np.int8)
        event_ids[:-1] = sx.get_events()
        event_ids[-1] = -1
        
        neighbors = sx.tri.neighbors
        neighbors_mask = event_ids[neighbors] == 2
        
        #č v těch otačkách budeme potřebovat pořad dokola
        self.neighbors_masked = neighbors_masked = dict() #defaultdict(list)
        zip_iter = zip(range(len(mixed_mask)), mixed_mask, neighbors, neighbors_mask)
        for id, is_mixed, neis, neis_mask in zip_iter:
            if not is_mixed:
                continue
            
            neighbors_masked[id] = neis[neis_mask]
        
        
    def get_finalized_supports(sx, finalized_nornal):
        ED = sx.tri.points
        failsi = sx.sample_box.failsi
        simplices = sx.tri.simplices
        
        point_scope = set()
        for key in finalized_nornal.separated_simplices:
            point_scope.update(simplices[key])
            
        
        # set supports
        max_red = -np.inf
        min_green = np.inf
        for point in point_scope:
            failure = failsi[point]
            value = np.inner(finalized_nornal.normal, ED[point])
            if failure and (value > max_red):
                max_red = value
                #red_supp = point
            elif not failure and (value < min_green):
                min_green = value
                #green_supp = point
        
        assert max_red < min_green
        
        return max_red, min_green
        
        
    def perform_sensitivity_analysis(self):
        # I'll try to use dual name convention here
        # self for this class, sensitivity-related things
        # sx for general Triangulation class related attributes
        sx = self
        
        self._init()
        
        
        mixed_mask = self.mixed_mask
        
        depths = defaultdict(int) #č hloubka jádra
        coverings = defaultdict(int) #č počet separovaných vektorem simplexů
        vectors = dict()
        
        last_scope = self._local_scope
        
        for simplex_id, is_mixed in zip(range(len(mixed_mask)), mixed_mask):
            if not is_mixed:
                continue
            
            depth = depths[simplex_id]
            normal = vectors.get(simplex_id, None)    
            id_before = id(normal)
            # we will remain normal for finalized normal
            # and vector for just nunpy vector
            normal = self.process_simplex(simplex_id, depth, normal)
            id_after = id(normal)
            
            new_depth = last_scope[simplex_id]
            covering = len(normal.separated_simplices)
            
            vectors[simplex_id] = normal
            depths[simplex_id] = new_depth
            coverings[simplex_id] = covering
            
            #č na vystupu z process_simplex() musí být finální vektor
            #č pokud není stejný, tak má cenu ho přířadit všem simplexům, které pokryvá
            #č pokud byť i stejný vektor získal větší hloubku,
            #č má cenu projít simplexy, ať přiště nebudou přepsany
            #č a ušetří to na neprojděných simplexech kus práce
            #
            #č zavadíme tady covering. Ale je to jedno.
            #č s nim musí to bejt o maliňko líp, bez nej - o maliňko hůř.
            #č Procházíme veškeré simplexy i zpětně.
            #č Ale je to jedno. Můžeme procházet, můžeme neprocházet.
            #č Takto musí to bejt o maliňko líp, bez toho - o maliňko hůř.
            if (id_before != id_after) or (new_depth > depth):
                for key, key_depth in last_scope.items():
                    #č teď povolíme i přepsaní jíž projděných simplexů
                    if (key_depth >= depths[key]) and (covering >= coverings[key]):
                        vectors[key] = normal
                        depths[key] = key_depth
                        coverings[key] = covering
            
                
                
                
        probabilities = dict()
        mixed_probability = 0
        nvar = sx.sample_box.nvar
        global_gradient = np.zeros(nvar)
        sensitivities = np.zeros(nvar)
        simplices = sx.tri.simplices
        
        vector = np.empty(nvar)
        #sensitivity = np.empty(nvar)
        
        for simplex_id, normal in vectors.items():
            indices = simplices[simplex_id]
            p_mixed = sx.get_simplex_share(indices)
            mixed_probability += p_mixed
            probabilities[simplex_id] = p_mixed
            
            np.multiply(normal.normal, p_mixed, out=vector)
            global_gradient += vector
            
            np.square(normal.normal, out=vector)
            vector *= p_mixed
            sensitivities += vector
        
        
        sensitivities /= mixed_probability
        
        # piece of postprocesing
        
        unique_id_vectors = {}
        for normal in vectors.values():
            unique_id_vectors[id(normal)] = normal
        
        unique_set_vectors = {}
        #č id neposkytují záruku unikatnosti
        #č ještě musíme přímo kontrolovat množiny separovaných simplexů
        for normal in unique_id_vectors.values():
            unique_set_vectors[normal.separated_simplices] = normal.normal
        
        return SensitivityResult(global_gradient, sensitivities, 
                probabilities, depths, vectors , coverings, 
                unique_id_vectors, unique_set_vectors)
        
        
        
    
        
    def process_simplex(self, simplex_id, depth, finalized_normal):
        # self for this class, sensitivity-related things
        # sx for general Triangulation class related attributes
        sx = self
        
        solver = self.separability_solver
        solver.reset(simplex_id, finalized_normal)
        
        local_scope = self._local_scope
        local_scope.clear()
        local_scope[simplex_id] = 0
        
        to_parse = self._to_parse
        to_parse.clear()
        
        parsed = self._parsed
        parsed.clear()
        
        simplices = sx.tri.simplices
        neighbors_masked = self.neighbors_masked
        
        to_parse.update(neighbors_masked[simplex_id])
        
        #č nenulový depth může příjít jen spolu s 
        #č s nějakou finalized_normal.
        #č Ta zaručeně bude pokryvat simplexy 
        #č do hloubky depth. 
        #č Netřeba nic kontrolovat, ani do solveru nic ukladat
        for __i in range(depth):
            for key in local_scope.keys():
                local_scope[key] += 1
                
            to_parse -= local_scope.keys()
            to_parse, parsed = parsed, to_parse
            to_parse.clear()
            for id in parsed: # meant to be parsed in the cycle's end
                to_parse.update(neighbors_masked[id])
                local_scope[id] = 0
            
        
        assert local_scope[simplex_id] == depth
        
        #č teď:
        #č když byl před tím finalized_normal,
        #č tak volaním .add_simplex() solver bude jenom kontrolovat uložený 
        #č do nej seznam simplexu. Nebude nikde nic ukladat.
        #č Až narazí na separabilitu, tak teprve tehdy potřebuje ten local_scope
        #č ale i na něj má uloženou referenci.
        #
        #č Pokud žádný finalized_normal není,
        #č tak předchozí smyčka se neuskuteční,
        #č local_scope a point skoupy řešiče se rovnoměrně naplňují od nuly.
        #č Solver tedy tím is_separable() skutečně mění svůj stav 
        #č a navíc se předpokládá, že do add_simplex() se budou sypat
        #č jen skutečně sousedící simplexy.
        #
        #č Závěr: použité abstrakce jsou děravé.
        #č Tahlensta smyčka je hodně provazana s tím řešičem
        #č a teprve dohromady tvoří společný algoritmus.
        #č Ale i tak mám velkou radost, že se mi podařilo 
        #č aspoň nejak ty části odseparovat.
        
        
        #č běh smyčky je podmíněn tím, že má co dělat
        to_parse -= local_scope.keys()
        while len(to_parse): #č máme co dělat?
            
            #č projedeme várku simplexu, přídáme je do slovníku,
            #č "zapneme" přípojené k ním vzorky
            to_parse, parsed = parsed, to_parse
            to_parse.clear()
            for id in parsed: # meant to be parsed in the cycle's end
                if solver.add_neighbor_simplex(id):
                    #č přídáme do to_parse pouze pokud
                    #č simplex se uspěšně přídal
                    local_scope[id] = -1
                    to_parse.update(neighbors_masked[id])
                
                #č tady je jediné místo, kde řešič použil local_scope
                #č narazili jsme na neseparabilitu tzv. jádra
                #č teď nám jde o to, abychom vrátili jakékoliv finální vektor
                #č Pokud ho zrovna máme v ruce, tak ho jenom vrátíme.
                elif solver.finalized_nornal is None:
                    #č některé simplexy zůstaly s hloubkou -1
                    #č poďme je vrátíme do normálu
                    #č umožní to přepsaní implicitní nulové hodnoty
                    #č přířadí se jim náš skvělý finální vektor
                    #č ušetří se tím kousiček práce
                    for key in parsed:
                        if key in local_scope:
                            #č prostě paušalně navysíme o jednu
                            #č byly tam -1
                            local_scope[key] += 1
                    return self._continue_search(id, to_parse, parsed)
                else:
                    return solver.finalized_nornal
                
            
            #č pokud jsme tu, tak vzorky byly separabilní,
            #č je na čase "navysit" hloubku
            for key in local_scope.keys():
                local_scope[key] += 1
        
            #č běh smyčky je podmíněn tím, že má co dělat
            to_parse -= local_scope.keys()
            
        
        #č šťastné finále, region je plně separabilní
        if solver.finalized_nornal is None:
            return self.get_finalized(solver.normal, frozenset(local_scope.keys()))
        else:
            return solver.finalized_nornal
    
    
    @staticmethod
    def get_finalized(normal, separated_simplices):
        length = np.sqrt(np.inner(normal, normal))
        # scale to unit length
        np.divide(normal, length, out=normal) 
        
        #sensitivities = np.square(normal)
        
        return FinalizedAxis(normal, separated_simplices)
    
    
    # should be only called by process_simplex()!
    def _continue_search(self, non_separable_simplex_id, to_parse, parsed):
        # self for this class, sensitivity-related things
        # sx for general Triangulation class related attributes
        sx = self
        
        solver = self.separability_solver
        assert solver.finalized_nornal is None
        
        
        simplices = sx.tri.simplices
        neighbors_masked = self.neighbors_masked
        
        non_separable_simplices = {non_separable_simplex_id}
        
        #č důležité: běh process_simplex() byl
        #č přerušen neseparabilitou.
        #č My budeme pokračovat
        #č a my víme, že v techto množinách zůstalo
        #č to, co máme projít. A pozastavilo se to na parsed
        local_scope = self._local_scope
        
        for key in parsed:
            if key in local_scope:
                #č ten klíč jíž byl zpracován, jedeme dál
                continue
            
            if solver.add_neighbor_simplex(key):
                #č přídáme do to_parse pouze pokud
                #č simplex se uspěšně přídal
                #č v této fázi všemu dáváme nulu,
                #č hloubku nadale jíž nenavyšujeme
                local_scope[key] = 0 
                to_parse.update(neighbors_masked[key])
            else:
                non_separable_simplices.add(key)
            
            
        
        #č naposled množinové operace
        to_parse -= local_scope.keys()
        to_parse -= non_separable_simplices
        while len(to_parse):
            key = to_parse.pop()
            if (key in local_scope) or (key in non_separable_simplices):
                #č ten klíč jíž byl zpracován, jedeme dál
                continue
            
            if solver.add_neighbor_simplex(key):
                #č přídáme do to_parse pouze pokud
                #č simplex se uspěšně přídal
                #č v této fázi všemu dáváme nulu,
                #č hloubku nadale jíž nenavyšujeme
                local_scope[key] = 0 
                to_parse.update(neighbors_masked[key])
            else:
                non_separable_simplices.add(key)
            
            
        return self.get_finalized(solver.normal, frozenset(local_scope.keys()))
    

    
    
    
    
    
    
    
    
    
    
    
    
#č tohle vůbec není žádná samostatná třída
#č simplex_scope je extrémně vázano na _Sense.process_simplex()
#č uživatel třídy vola .reset(), pak .add_neighbor_simplex()
#č uživatel třídy má kontrolovat finalized_nornal
#č atributy třídy platí pouze pokud finalized_nornal je None
# class attributs are valid only if finalized_nornal is None
class SeparationAxis:
    
    def __init__(self, sx, simplex_scope_reference):
        #č simplex_scope potřebujeme pouze v jednom místě
        self.simplex_scope = simplex_scope_reference
        self.point_scope = set()
        self.non_separable_point_set = set()
        self.sx = sx # for sx.get_simplex_normal()
        
        self.ED = points = sx.tri.points
        self.failsi = failsi = sx.sample_box.failsi
        self.simplices = sx.tri.simplices
        
        nsim, nvar = points.shape
        
        self.c_zeros = np.zeros(nvar + 1) # prices in terms of LP
        self.b_ub = -np.ones(nsim)
        
        self.A_ub = np.empty((nsim, nvar + 1))
        self.A_ub[:, :-1] = points
        self.A_ub[:, -1] = self.b_ub
        self.A_ub *= (failsi * 2 - 1).reshape(-1, 1)
        
        
        
    # method to start new task 
    def reset(self, simplex_id, finalized_nornal):
        self.finalized_nornal = finalized_nornal
        
        #č je vhodně zde vynulovat point scopes
        self.point_scope.clear()
        self.non_separable_point_set.clear()
        
        #č I když se mi nechce semka tahnout get_simplex_normal(),
        #č stejně potřebuji indices pro point_scope
        if finalized_nornal is None:
            indices = self.simplices[simplex_id]
            self.point_scope.update(indices)
            #č hloubka je nulová, žádné přípravné otačky konat nebudou.
            #č tahle normála půjde rovnou na dějiště
            #č poslední složka vektoru je buď nvar+1 dimenze 
            #č v případě get_simplex_normal()
            #č nebo offset aka bias 
            #
            # the last item of vector is either nvar+1 coordinate
            # in case of get_simplex_normal()
            # or offset aka bias
            # in case of separation axis
            # i.e. we should ignore it anyway
            self._set_normal(self.sx.get_simplex_normal(indices)[:-1])
            
            
            
            
        
    def _set_normal(self, normal):
        #č podtržitko v názvu je k tomu, abych zdůraznil,
        #č že point_scope musí být před volaním metody
        #č jíž nastaven, musí být platný, musí být v pořádku
        self.finalized_nornal = None
        self.normal = normal
        
        
        ED = self.ED
        failsi = self.failsi
        
        # set supports
        max_red = -np.inf
        min_green = np.inf
        for point in self.point_scope:
            failure = failsi[point]
            value = np.inner(normal, ED[point])
            if failure and (value > max_red):
                max_red = value
                self.red_supp = point
            elif not failure and (value < min_green):
                min_green = value
                self.green_supp = point
        
        assert max_red < min_green
        
        self.max_red = max_red
        self.min_green = min_green
        
        
    # it's actually something between "is_separable" and "add_simplex"
    def add_neighbor_simplex(self, simplex_id):
        if self.finalized_nornal is None:
            return self._is_non_finalized_separable(simplex_id)
        
        if simplex_id in self.finalized_nornal.separated_simplices:
            return True
        
        #č předpokladáme, že finální vektor je omezen nadbytečnými simplexy
        #č a tedy i nadbytečným vzálenými vzorky.
        #č Že když pustíme LP my, tak kvůli menší bázi 
        #č zvládneme odseparovat i další simplexy.
        #č To je poznámka k tomu, 
        #č že ze žádného porovnání množin simplexů a vzorků
        #č nejsme shopní udělat žádný závěr.
        #č Vyjímečný případ, že by množiny byly si rovny neuvažujeme.
        #if self.finalized_nornal.separated_simplices == self.scope.keys():
        #   return False
        
        
        # non-separable, then
        #оӵ LP лэзьыны кулэ
        #č poprvé s tomto runu potřebujeme tečky
        #č odsuď jsou jenom dvě cesty:
        #č ono se buď objeví být separabilní, 
        #č tehdy budeme pokračovat s nefinalizovaným vektorem.
        #č nebo separabilní nebude, tehdy končíme, jdeme na další run.
        simplices = self.simplices
        
        point_scope = self.point_scope
        #č musí jíž být vyprazdněný v reset()
        #č ale hypoteticky, kdyby nás opakovaně volal někdo jinej
        point_scope.clear()
        #č jediné místo, kde simplex_scope potřebujeme!
        for key in self.simplex_scope.keys():
            point_scope.update(simplices[key])
        
        #č máme finitně-finální vektor.
        #č pokud teď čerstvě přídaný simplex separovat nepůjde,
        #č tak volající kód timhle skončí, ten finitní vektor vrátí.
        #č Když půjde, tak budeme pokračovat s nově nalezenou normálou.
        #č To je k tomu, že nemá cenu brat v uvahu první scenář.
        #č Tam to hned skončí a je to jedno, co tu budeme mít za skoupy.
        #č A nejen to. Kdyby někdo neohledúplně volal is_separable(),
        #č tak v případě False my nesaháme na finalizovaný vektor
        #č a tak v příštím volaní point_scope se očístí a naplní se znovu.
        #č Mimochodem, díky takovému odvažnému apdejtu je nám jedno,
        #č jak přesně volající kód zachází s simplex_scope,
        #č zda přídává simplex před, po, zárověň...
        point_scope.update(simplices[simplex_id])
        indices = np.fromiter(point_scope, int, len(point_scope))
        result = self.get_separation_axis(indices)
        if not result.success: #č konec, zde končíme
            if result.status != 2: # Problem appears to be infeasible.
                print("linprog status %s: %s" % (result.status, result.message))
                print("linprog result %s" % result.x)
            #č non_separable_point_set zde taky nemusím řešit
            return False #č na finalized_nornal nesáháme
        
        # sucсess!               
        #č musíme se přípravit k dalšímu životu
        #č _set_normal() tu totalní normalu vynulue
        #self.finalized_nornal = None
        
        #č point_scope jíž má platný obsah
        #č zbyvá vynulovat doplňek - buď zde, nebo v reset()
        #self.non_separable_point_set.clear()
        
        #č hned odřízneme poslední složku - 
        #č bude tam posunutí b aka offcet aka bias
        #č point_scope jíž máme v pořádku.
        self._set_normal(result.x[:-1])
        
        return True
            
            
            
    #č Pokud zkoušíme separabilitu sousedícího simplexu,
    #č tak narazíme na maximálně jeden nový vzorek.
    #č Zbytek nového simplexu tvoří společná stěna-hyperrovina.
    def _is_non_finalized_separable(self, simplex_id):
        
        #č z logiky volajícího kódu nema cenu kontrolovat simplex_scope
        #č ono se ptá na separabilitu pouze toho, co jíž není ve skoupu
        #if simplex_id in self.simplex_scope:
        #    return True
            
        for point in self.simplices[simplex_id]:
            if point not in self.point_scope:
                #č jediné místo, kde non_separable_point_set použijeme
                if point in self.non_separable_point_set:
                    #č prostě vrácíme False, nic dalšího řešit netřeba
                    return False 
                value = np.inner(self.normal, self.ED[point])
                if self.failsi[point]:
                    if value > self.min_green:
                        #č současná normála to neseparuje.
                        #č ale možná bude nějaká jiná?
                        return self._is_one_more_point_ever_separable(point)
                    elif value > self.max_red:
                        self.max_red = value
                        self.red_supp = point
                else:
                    if value < self.max_red:
                        #č současná normála to neseparuje.
                        #č ale možná bude nějaká jiná?
                        return self._is_one_more_point_ever_separable(point)
                    elif value < self.min_green:
                        self.min_green = value
                        self.green_supp = point
                
                #č v této fázi, 
                #č když jsme doposud neskončíli,
                #č už víme, že vrchol je separabilní
                self.point_scope.add(point)
                
                #č takovej vzorek, který není ve skoupu
                #č u sousedicího simplexu může být maximálně jeden
                return True
        return True



    
    def _is_one_more_point_ever_separable(self, non_separable_point):
        
        #č tady je to opakový opak
        #č Pokud vzorek nejde separovat, tak se nesmí dostat do point_scope
        #č V každém případě se bude pokračovat až do posledního simplexu
        
        #č Pokud zkoušíme separabilitu sousedícího simplexu,
        #č tak narazíme na maximálně jeden nový vzorek.
        #č Zbytek nového simplexu tvoří společná stěna-hyperrovina.
            
        
        #č point_scope už máme
        point_list = list(self.point_scope)
        point_list.append(non_separable_point)
        
        result = self.get_separation_axis(point_list)
        if not result.success: #č konec, zde končíme
            if result.status != 2: # Problem appears to be infeasible.
                print("linprog status %s: %s" % (result.status, result.message))
                print("linprog result %s" % result.x)
            #č jediné místo, kde něco do non_separable_point_set přídávame
            self.non_separable_point_set.add(non_separable_point)
            return False
        
        # sucсess!               
        #č dodáme ten diskutovaný pochybný, jíž ospravedlněný vzorek
        self.point_scope.add(non_separable_point)
        
        #č hned odřízneme poslední složku - 
        #č bude tam posunutí b aka offcet aka bias
        self._set_normal(result.x[:-1])
        
        return True


        

    #č přes liblinear to taky jde
    #from liblinear import liblinearutil
    #pr = liblinearutil.problem(box.failsi, box.G)
    #param = liblinearutil.parameter('-s 2 -c 10000 -B 1')
    #m = liblinearutil.train(pr, param)
    #m.get_decfun()
    def get_separation_axis(self, indices):
        A_ub = self.A_ub[indices]
        b_ub = self.b_ub[:len(A_ub)]
        return optimize.linprog(self.c_zeros, A_ub=A_ub, b_ub=b_ub, 
                        options={'presolve':False}, method='highs-ds', 
                        bounds=(None, None))
    
    
    
   

    

    
    
    




# np.count_nonzero
class TopologyAnalysis:
    
    
    
    def __init__(self, tn_scheme, points, simplices, neighbors, failsi, facets, normals):
        self.simplices = simplices
        self.neighbors = neighbors
        self.failsi = failsi
        self.facets = facets
        self.normals = normals
        self.points = points
        self.tn_scheme = tn_scheme
        
        self.to_parse = set()
        
        self.internal_walls = set()
        #self.external_facets = dict()
        
        nsim, nvar = points.shape
        self.nvar = nvar
        self.nsim = nsim
        self.simplex_values = DefaultDict(nvar)
        
        
        
        
        
    def integrate_convex_envelope(self):
        facets = np.sort(self.facets[:, ::-1], kind='mergesort', axis=1)
        vertices_model = self.points[facets].transpose((1, 0, 2))
        result = self.tn_scheme.integrate(self._norm_inside_callback, vertices_model)
        
        mask = result > 0
        
        if not np.all(mask):
            print("Negative measure has occured during integration")
        
        #č nejdřív rouška - prointegrovalo se to vůbec kladně?
        #č pak normala - ona je pro tyhle ortogonálky konstantní
        result *= mask
        result *= self.normals.T
        
        
        self.p_inside = np.sum(result, axis=1)
        
        self.external_facets = dict(zip((tuple(facet) for facet in facets), result.T))
        
        
        
        
    # quadpy
    @staticmethod
    def _norm_inside_callback(x):
        # x.shape == (simplex_dim + 1, nsimplex, scheme_npoints) #(3, 26, 56)
        nvar, nsimplex, scheme_npoints = x.shape
        
        cdfs = stats.norm.cdf(x)
        pdfs = stats.norm.pdf(x)
        
        for i in range(nvar):
            cdfs[i] *= np.prod(pdfs[:i], axis=0)
            cdfs[i] *= np.prod(pdfs[i+1:], axis=0)
            #cdfs[i] *= normals[:, i]
        
        
        # n_values x nsimplex x scheme_points
        return cdfs
        
        
    @staticmethod
    def get_events(simplices, failsi):
        """
        Metoda musí simplexům přiřazovat jev 
        0=success, 1=failure, 2=mix
        """
        
        in_failure = failsi[simplices]
        has_failure = in_failure.any(axis=1)
        all_failure = in_failure.all(axis=1)
        return np.where(has_failure, np.where(all_failure, 1, 2), 0)
    
        
        
    def integrate_walls(self):
        simplices = self.simplices
        neighbors = self.neighbors
        failsi = self.failsi
        points = self.points
        
        nsimplex, nvertices = simplices.shape
        nvar = nvertices - 1
        
        self.event_ids = event_ids = np.empty(len(simplices)+1, dtype=np.int8)
        event_ids[:-1] = self.get_events(simplices, failsi)
        event_ids[-1] = -1
        
        
        neighbors_event_ids = event_ids[neighbors]
        self.mask_unequal = neighbors_event_ids != np.atleast_2d(event_ids[:-1]).T 
        
        mask_inside = neighbors_event_ids != -1
        np.logical_and(self.mask_unequal,  mask_inside, out=mask_inside)
        
        mask = np.any(mask_inside, axis=1)
        
        wall_indices = np.empty(nvar, dtype=int)
        vertex_arange = np.arange(nvar + 1)
        
        
        
        for simplex_id in np.arange(nsimplex)[mask]:
            indices = simplices[simplex_id]
            vertex_mask = mask_inside[simplex_id]
            
            counter_indices = neighbors[simplex_id]
            
            for vertex_number in vertex_arange[vertex_mask]:
                
                counter_simplex_id = counter_indices[vertex_number]
                max_id = max(simplex_id, counter_simplex_id)
                min_id = min(simplex_id, counter_simplex_id)
                record = (max_id, min_id)
                
                if record not in self.internal_walls:
                    wall_indices[:vertex_number] = indices[:vertex_number]
                    wall_indices[vertex_number:] = indices[vertex_number+1:]
                    
                    vertices_model = points[wall_indices]
                    inner_node = points[indices[vertex_number]]
                    value = self._integrate_wall(vertices_model, inner_node)
                    
                    
                    #č teď je to nejzajimavější. 
                    #č přídame do množiny záznam, 
                    #č že už jsme tento pár simplexu prointegrovali.
                    #č No a k jednotlivým simplexum příčteme 
                    #č výsledek integrace s opačnými znaménky
                    
                    self.simplex_values[simplex_id] += value
                    self.simplex_values[counter_simplex_id] -= value
                    self.internal_walls.add(record)
                
        
    def _integrate_wall(self, vertices_model, inner_node):
        
        vectors = vertices_model[1:] - vertices_model[0]
        basis, __ = np.linalg.qr(vectors.T, mode='complete')
        
        normal = basis[:, -1]
        
        wall_offset = np.inner(normal, vertices_model[0])
        node_ofset = np.inner(normal, inner_node)
        #č pro nasměrovanou navenek normálu by měl byt
        #č offset stěny větší jak offset zbívajícího bodíku
        normal_sign = np.sign(wall_offset - node_ofset)
        
        
        # x.shape == (simplex_dim + 1, scheme_npoints) #(3, 56)
        x = quadpy.tn.transform(self.tn_scheme.points, vertices_model.T)
        vol = quadpy.tn.get_vol(vertices_model)
        
        if not np.isfinite(vol):
            print("Incorrect surface area has occured during integration")
            vol = 0
        
        
        
        # n_values x scheme_points
        cdfs = stats.norm.cdf(x)
        pdfs = stats.norm.pdf(x)
        
        for i in range(len(x)): # len(x) == nvar
            cdfs[i] *= np.prod(pdfs[:i], axis=0)
            cdfs[i] *= np.prod(pdfs[i+1:], axis=0)
            
        
        # shape: n_values
        values = np.dot(cdfs, self.tn_scheme.weights)
        mask = values > 0
        
        if not np.all(mask):
            print("Negative measure has occured during integration")
        
        #č nejdřív rouška - prointegrovalo se to vůbec kladně?
        #č pak normala - ona je pro tyhle ortogonálky konstantní
        
        
        values *= mask
        values *= normal
        values *= vol * normal_sign
        
        return values
        
    
        
    def perform_analysis(self):
        self.region_lookup = region_lookup = dict()
        self.reds = []
        self.greens = []
        self.yellows = []
        
        
        simplices = self.simplices
        neighbors = self.neighbors
        failsi = self.failsi
        points = self.points
        
        event_ids = self.event_ids
        neighbors_event_ids = event_ids[neighbors]
        mask_unequal = self.mask_unequal
        
        
        
        
        
        for simplex_id in range(len(self.simplices)):
            if simplex_id in region_lookup:
                continue
            
            self.process_new_region(simplex_id)
        
        
    def postprocess(self):
        for region in self.greens:
            self.postprocess_region(region)
            print(region)
        for region in self.yellows:
            self.postprocess_region(region)
            print(region)
        for region in self.reds:
            self.postprocess_region(region)
            print(region)
        
        
    def postprocess_region(self, region):
        
        self.region_lookup[-1] = -1
        for neighbor_simplex in region.neighbor_simplices:
            region.neighbor_regions.add(self.region_lookup[neighbor_simplex])
            
        region.simplices = []   
        for simplex_id in region.simplex_index:
            simplex = self.simplices[simplex_id]
            region.simplices.append(simplex)
            for point_id in simplex:
                region.point_ids.add(point_id)
        
        region.points = []  
        for point_id in region.point_ids:
            region.points.append(self.points[point_id])
        
        
    def process_new_region(self, start_id):
        to_parse = self.to_parse
        to_parse.clear()
        to_parse.add(start_id)
        
        parsed = self.region_lookup
        
        mask_unequal = self.mask_unequal
        neighbors = self.neighbors
        simplices = self.simplices
        
        external_facets = self.external_facets
        
        
        
        
        event_id = self.event_ids[start_id]
        
        nvar = self.nvar
            
        region = Region(nvar, start_id)
        region.event_id = event_id
        
        # 0=success, 1=failure, 2=mix
        if event_id == 2:
            self.yellows.append(region)
        elif event_id == 1:
            self.reds.append(region)
        else:
            self.greens.append(region)
        
        
        
        wall_indices = np.empty(nvar, dtype=int)
        vertex_arange = np.arange(nvar + 1)
        
        while len(to_parse):
            simplex_id = to_parse.pop()
            simplex_neighbors = neighbors[simplex_id]
            vertex_mask = mask_unequal[simplex_id]
            
            #č zde je prostor pro integraci
            # ....
            if np.any(vertex_mask):
                region.probability += self.simplex_values[simplex_id]
                
                indices = simplices[simplex_id]
                
                for vertex_number in vertex_arange[vertex_mask]:
                    counter_simplex_id = simplex_neighbors[vertex_number]
                    region.neighbor_simplices.add(counter_simplex_id)
                    if counter_simplex_id == -1:
                        wall_indices[:vertex_number] = indices[:vertex_number]
                        wall_indices[vertex_number:] = indices[vertex_number+1:]
                        
                        region.probability += external_facets[tuple(np.sort(wall_indices))]
                        
            
            
            for neighbor_id in simplex_neighbors[~vertex_mask]:
                if neighbor_id not in parsed:
                    to_parse.add(neighbor_id)
            
            parsed[simplex_id] = region
            region.simplex_index.add(simplex_id)
            
            
        
            
            

class Region:
    __slots__ = ('id', 'simplex_index', 'simplices', 'neighbor_simplices', 'neighbor_regions',
                'probability', 'event_id', 
                'point_ids', 'points')
    
    def __init__(self, nvar, id):
        self.id = id
        self.simplex_index = set()
        self.neighbor_simplices = set()
        self.neighbor_regions = set()
        self.simplices = None
        self.points = None
        self.point_ids = set()
        self.probability = np.zeros(nvar)
    
    def __repr__(self):
        return "Region(%s, %s)" % (len(self.probability), self.id)
        
    def __str__(self):
        return "Region %s id %s of %s simplices and %s points p=%s"%( self.event_id, self.id, 
                len(self.simplex_index), len(self.point_ids), np.mean(self.probability))

        



#č šablona třidy
class _Triangulation:
    def tri_setup(sx, sample_box, tri_space='Rn', incremental=True):
        
        sx.sample_box = sample_box
        sx.tri_space = tri_space
        
        sx.simplices_set = set()
        
        sx.newly_estimated = 0
        sx.newly_invalidated = 0
        
        # create .tri triangulation
        #č tri - Deloneho triangulace
        #č žádné chyby nechytám
        #čs když se tringulace nepovede tak nemáme čo robiť
        # incremental triangulation requires one more point
        tri_plan = getattr(sample_box, tri_space)
        sx.tri = spatial.Delaunay(tri_plan, incremental=incremental)
        if len(sx.tri.coplanar):
            #print('triangulace v pořádku není')
            print('Triangulation is coplanar:', sx.tri.coplanar)
        else:
            #print('triangulace je v pořádku')
            print('Triangulation is OK')
            
        
        
    
    def get_events(sx, simplices=None):
        """
        Metoda musí simplexům přiřazovat jev 
        0=success, 1=failure, 2=mix
        """
        if simplices is None:
            simplices = sx.tri.simplices
        
        in_failure = sx.sample_box.failsi[simplices]
        has_failure = in_failure.any(axis=1)
        all_failure = in_failure.all(axis=1)
        return np.int8(np.where(has_failure, np.where(all_failure, 1, 2), 0))
        
        
    def get_nfailures(sx, simplices=None):
        if simplices is None:
            simplices = sx.tri.simplices
        
        in_failure = sx.sample_box.failsi[simplices]
        return np.sum(in_failure, axis=1)
        
        
        
        #č tato funkce běží 91% času
        # bottleneck function
    def update(sx):
        simplices_set_to_estimate = sx._update()
        gc.collect()
        
        sx.estimate_simplices(simplices_set_to_estimate)
        
        
    def _update(sx):
        """
        Triangulace zajistěně existuje
        """
        #č tato funkce je koncipována jinač
        #č narozdíl od Shull, zde nám taky záleží
        #č na poruchách i neporuchách
        #č f_model proto nám stačit nebude
        #č a bylo by blbě tečky brat zevnějšku,
        #č a failsi - zevnitřku.
        #č Takže - všechno bereme ze sample_box
        #č reference, jenom dejte vědet, 
        #č že máme triangulaci aktualizovat
        
        sx._tri_update() #č jako vždy, chyby nechytáme
        
        
        #č vyhodit ty pomalé pytloviny, co tu byly
        #č (tady bylo něco jako tringulace - 1,45 s, drbání kolem - 1366 s),
        #č nahradit je pěknejma, krasnejma, jednoduchejma
        #č množináma. Přihodily se nám.
        
        #č podstata problému byla a je v tom, 
        #č že numpy neumí pracovat s věktory, případně s submaticemi
        #č jako s celky. Má routiny pouze pro 1D množiny.
        #č Navíc, numpy vektory nejsou hashable, nejde je přímo hodit 
        #č ani do setů, ani do slovníků
        #č Nezbyvá nám nic jineho, než prévest ndarray na množinu n-tic.
        new_simplices_set = set(tuple(simplex) for simplex in sx.tri.simplices)
        
        # possible naive implementation
        #to_invalidate = sx.simplices_set - new_simplices_set
        #to_estimate = new_simplices_set - sx.simplices_set
        
        #č vymejšlím, jak by se mohlo ušetřit,
        #č aby se neprobíhala smyčka přes obrovský set na dvakrat
        # Update the set, keeping only elements found in either set, but not in both
        new_simplices_set.symmetric_difference_update(sx.simplices_set)
        to_estimate = new_simplices_set - sx.simplices_set
        to_invalidate = new_simplices_set - to_estimate
        
        sx.newly_estimated = len(to_estimate)
        sx.newly_invalidated = len(to_invalidate)
        
        #č invalidace
        # difference_update
        sx.simplices_set -= to_invalidate
        
        # update
        sx.simplices_set |= to_estimate
        
        #č necháme zbytek jednotlivým podtřídám
        #č co jsem viděl, voláme tyhle funkce jenom my
        sx._invalidate_simplices(to_invalidate)
        
        
        #č zde spolehám na to, že pořadí indexů se nikdy nezmění
        #č tj. [12, 13, 26] najednou nestane [26, 12, 13]
        #č (dá se něco takovýho očekavát podle toho co jsem čet v dokumentaci)
        #
        # here "simplices_set_to_estimate" is a set of tuples
        #simplices_to_estimate = np.array(list(simplices_set_to_estimate))
        return to_estimate
        
        
    def _tri_update(sx):
        tri_plan = getattr(sx.sample_box, sx.tri_space)
        #č separujeme, abychom vědeli, kolik času žere samotný QHull
        sx.tri.add_points(tri_plan[sx.tri.npoints:])
        
        if len(sx.tri.coplanar): # pokud triangulace není v pořadku
            #print('triangulace v pořádku není')
            print('Triangulation has coplanar points:', sx.tri.coplanar)
                
        
    def is_mixed(bx, simplices=None):
    
        if simplices is None:
            simplices = bx.tri.simplices
        
        in_failure = bx.sample_box.failsi[simplices]
        has_failure = in_failure.any(axis=1)
        all_failure = in_failure.all(axis=1)
        return np.logical_xor(has_failure, all_failure)
            
            
    def get_simplex_normal(sx, indices):
        nvar = sx.sample_box.nvar
        failsi = sx.sample_box.failsi
        
        points = sx.tri.points
        
        vectors = np.empty((nvar, nvar + 1))
        vectors[:, :-1] = points[indices[1:]] - points[indices[:1]]
        vectors[:, -1] = failsi[indices[1:]] #č numpy nedá boleans 
        vectors[:, -1] -= failsi[indices[0]] #č jen tak odečíst
        basis, __ = np.linalg.qr(vectors.T, mode='complete')
        
        normal = basis[:, -1]
        
        #č ujistit se, že normály směrovany nahoru, 
        #č tj. směrem k bezpečným vzorkám
        normal = normal * (1 - 2 * (normal[-1] < 0)) 
        
        return normal
        
        
    def get_averaged_mixed_normals(sx, depth=2):
        simplices = sx.tri.simplices
        
        nvar = sx.sample_box.nvar
        failsi = sx.sample_box.failsi
        mask = np.empty(sx.tri.nsimplex + 1, dtype=bool)
        mask[-1] = False
        
        in_failure = failsi[simplices]
        has_failure = in_failure.any(axis=1)
        all_failure = in_failure.all(axis=1)
        np.logical_xor(has_failure, all_failure, out=mask[:-1])
        
        
        mixed_simplices = simplices[mask[:-1]]
        
        
        X = np.empty((sx.sample_box.nsim, nvar + 1))
        X[:, :-1] = getattr(sx.sample_box, sx.tri_space)
        X[:, -1] = failsi
        
        vectors = X[mixed_simplices[:, 1:]] - X[mixed_simplices[:, :1]]
        basises, __ = np.linalg.qr(vectors.transpose(0, 2, 1), mode='complete')
        
        #č o jeden simplex víc aby index -1 odkazoval na nulovou normálu
        normals = np.zeros((sx.tri.nsimplex + 1, nvar + 1))
        normals[mask] = basises[:, :, -1]
        
        #č ujistit se, že normály směrovany nahoru, 
        #č tj. směrem k bezpečným vzorkám
        normals *= (1 - 2 * (normals[:,-1:] < 0)) 
        
        
        for __ in range(depth):
            # n_mixed_simplices x nvar+1 (neighbors) x nvar+1 (coordinates)
            normals[:-1] += np.sum(normals[sx.tri.neighbors], axis=1)
        
#        neighbors = sx.tri.neighbors[mask[:-1]]
#        mixed_normals = normals[mask]
#        mixed_normals += np.sum(normals[neighbors], axis=1)
        
        return normals[mask], mixed_simplices
            
            
    def get_pure_mixed_normals(sx):
        simplices = sx.tri.simplices
        
        mask = sx.is_mixed(simplices)
        simplices = simplices[mask]
        
        nvar = sx.sample_box.nvar
        failsi = sx.sample_box.failsi
        
        X = np.empty((sx.sample_box.nsim, nvar + 1))
        X[:, :-1] = getattr(sx.sample_box, sx.tri_space)
        X[:, -1] = failsi
        
#        X = np.empty((nvar + 1, sx.sample_box.nsim))
#        X[:-1] = getattr(sx.sample_box, sx.tri_space).T
#        X[-1] = failsi
        
        
        vectors = X[simplices[:, 1:]] - X[simplices[:, :1]]
        basises, __ = np.linalg.qr(vectors.transpose(0, 2, 1), mode='complete')
        
        normals = basises[:, :, -1]
        
        #č ujistit se, že normály směrovany nahoru, 
        #č tj. směrem k bezpečným vzorkám
        normals = normals * (1 - 2 * (normals[:,-1:] < 0)) 
        
        return normals, simplices
        
        
    def get_gradients(sx, depth=2):
        normals, simplices = sx.get_averaged_mixed_normals(depth=depth)
        
        gradients = normals[:, :-1]
        
        lengths = np.sum(np.square(gradients), axis=1)
        lengths = np.sqrt(lengths, out=lengths) #lengths of each radius-vector
        
        # scale all radii-vectors to unit length
        # use [:,None] to get an transposed 2D array
        np.divide(gradients, lengths[:,None], out=gradients) 
        
        return gradients, simplices
            
            
    def get_failure_moments(sx):
        simplices = sx.tri.simplices
        
        nvar = sx.sample_box.nvar
        
        failsi = sx.sample_box.failsi
        
        in_failure = failsi[simplices]
        has_failure = in_failure.any(axis=1)
        
        in_failure = in_failure[has_failure]
        simplices = simplices[has_failure]
        
        X = getattr(sx.sample_box, sx.tri_space)
        
        #č stačí tak, když jedeme jen přes červené simplexy
        PDF = sx.sample_box.pdf(sx.tri_space)
        #failure_PDF = sx.sample_box.pdf(sx.tri_space) * failsi
        
        
        nbodies = np.sum(in_failure)
        
        
        centroids = np.empty((nbodies, nvar + 1))
        V = np.empty(nbodies)
        
        i = 0
        room = np.zeros((nvar + 1, nvar + 1))
        base = np.zeros(nvar + 1)
        for simplex, failures in zip(simplices, in_failure):
            vertices_model = X[simplex]
            base[:-1] = vertices_model[0]
            
            np.subtract(vertices_model, base[:-1], out=room[:, :-1])
            
            for vertex, pdf in zip(room[failures], PDF[simplex[failures]]):
                room[0] = vertex
                room[0,-1] = pdf
                
                V[i] = np.linalg.det(room) #/ np.math.factorial(nvar + 1)
                np.mean(room, axis=0, out=centroids[i])
                centroids[i] += base
                
                i += 1
                
                
                
        assert i == nbodies 
        
        
        
        pf = np.sum(V) / np.math.factorial(nvar + 1)
        mean = np.average(centroids, axis=0, weights=V)
        
        cov_matrix = np.cov(centroids, rowvar=False, ddof=0, aweights=V)
    
        return pf, mean, cov_matrix
    
    
    
    
    
    
class _FullTriangulation(_Triangulation):

    def integrate(sx):
        #č Metoda musí simplexům přiřazovat jev 
        # 0=success, 1=failure, 2=mix
        #č vyhodil jsem simplex_id'y
        event_ids = sx.get_events()
        
        for simplex, event_id in zip(sx.tri.simplices, event_ids):
        
            #č ty množiny je super věc
            sx.simplices_set.add(tuple(simplex))
            
            # -1 = 'outside', 0=success, 1=failure, 2=mix
            event, fr, wfr = get_failure_ratio(sx.sample_box, event_id,\
                                             simplex, sx.weighting_space)
            sx.integrate_simplex(simplex, event, event_id, fr, wfr)    
        
        
    #č vyhodil jsem simplex_id'y
    def _invalidate_simplices(sx, simplices_set_to_delete):
        
        # here "simplices_set_to_delete" is a set of tuples
        
        #č ty simplexy tam MUSÍ být, 
        #č pokud teda bo boxu nikdo nesahá...
        for simplex in simplices_set_to_delete:
            sx.simplex_stats.pop(simplex)
            sx.issi.delete_event_data(simplex)
            
            if sx.on_delete_simplex is not None:
                #č zpatky do ndarray...
                sx.on_delete_simplex(indices=np.array(simplex))
    
    
    def estimate_simplices(sx, simplices_set_to_estimate):
        for simplex in simplices_set_to_estimate:
            sx.estimate_simplex(np.array(simplex))
    
    
    #č vyhodil jsem simplex_id'y
    def estimate_simplex(sx, indices):
        # -1 = 'outside', 0=success, 1=failure, 2=mix
        event, event_id, fr, wfr = get_indices_event(sx.sample_box,\
                                         indices, sx.weighting_space)
        
        sx.integrate_simplex(indices, event, event_id, fr, wfr)  
    

        

class _FastTriangulation(_Triangulation):
        
    def integrate(sx):
        #č Metoda musí simplexům přiřazovat jev 
        # 0=success, 1=failure, 2=mix
        #č vyhodil jsem simplex_id'y
        event_ids = sx.get_events()
        
        #č zde chceme ušetřít, a nechat stranou zelené simplexy
        simplices = sx.tri.simplices[event_ids != 0]
        event_ids = event_ids[event_ids != 0]
        
        
        #č zde postupně v cyklu prochazíme simplexy
        #č tynhlenstím zajišťujeme disjunktnost 
        #čs a môžeme všechny nasbírané pravděpodobnosti jednoduše sčítat
        for simplex, event_id in zip(simplices, event_ids):
            
            #č ty množiny jsou super
            sx.simplices_set.add(tuple(simplex))
            
            # -1 = 'outside', 0=success, 1=failure, 2=mix
            event, fr, wfr = get_failure_ratio(sx.sample_box,\
                             event_id, simplex, sx.weighting_space)
            
            sx.integrate_simplex(simplex, event, event_id, fr, wfr)  
            
    
    def get_pf_estimation(sx):
        # TRI-compatible estimation
        # -1=outside, 0=success, 1=failure, 2=mix
        tri_estimation = {-1:0, 0:0, 1:0, 2:0}
        
        # Shull should be inicialized with powerset_correction=True
        #č dostaneme vyrovnané odhady Brna-města (-2) a Brna-venkova (-1)
        #č současný kód Shull zajišťuje, 
        #č že v ISSI estimátory budou spočítány
        #sx.issi.get_estimations()
        tri_estimation[-1] = sx.issi.estimations[-1]
        
        #č něco konkretnějšího
        vertex_estimation = 0
        weighted_vertex_estimation = 0
        
        pf_inside = sx.issi.estimations[-2]
        #č nechce se mi počitat přes numpy: np.array(tuple(c.values()))
        # let's iterate over all simplices we have
        # (calling code is responsible for the .simplex_stats validity)
        for event_id, simplex_measure, fm, wfm in sx.simplex_stats.values():
            tri_estimation[event_id] += simplex_measure
            vertex_estimation += fm
            weighted_vertex_estimation += wfm
        
        #č success klidně může být i záporným
        tri_estimation[0] = pf_inside - tri_estimation[1] - tri_estimation[2]
        
        
        #ё так, для красоты
        global_stats = dict()
        global_stats['outside'] = 0
        global_stats['success'] = 0 
        global_stats['failure'] = tri_estimation[1]
        global_stats['mix'] = tri_estimation[2]
        
        return {'TRI_estimation': tri_estimation, 'global_stats': global_stats, \
            'vertex_estimation' : vertex_estimation, \
            'weighted_vertex_estimation' : weighted_vertex_estimation, 
            'coplanar':sx.tri.coplanar}
            
             
    
    #č vyhodil jsem simplex_id'y
    def _invalidate_simplices(sx, simplices_set_to_delete):
        
        # here "simplices_set_to_delete" is a set of tuples
        
        #č ty simplexy NEmusí tam být, 
        for simplex in simplices_set_to_delete:
            if simplex in sx.simplex_stats:
                sx.simplex_stats.pop(simplex)
        
            if sx.on_delete_simplex is not None:
                #č zpatky do ndarray...
                sx.on_delete_simplex(indices=np.array(simplex))


    def estimate_simplices(sx, simplices_set_to_estimate):
        for simplex in simplices_set_to_estimate:
            sx.estimate_simplex(np.array(simplex))


    #č vyhodil jsem simplex_id'y
    def estimate_simplex(sx, indices):
        
        #č zkusím funkci návrhnout tak, že 
        #ё вызывающая функция запускает estimate_simplex
        #ё на всём подряд без разбору.
        #č Našim úkolem je zjistit co je simplex zač
        #č a ty zelené ignorovat
        
        # -1 = 'outside', 0=success, 1=failure, 2=mix
        event, event_id, fr, wfr = get_indices_event(sx.sample_box,\
                                         indices, sx.weighting_space)
        
        if event_id != 0:
            sx.integrate_simplex(indices, event, event_id, fr, wfr)  




class _SamplingTriangulation:
    def __init__(sx, sample_box, tri_space='Rn', issi=None, weighting_space=None, \
            incremental=True, on_add_simplex=None, on_delete_simplex=None, \
            sampling_space=None, simplex_budget=100, design=None):
            
        if sampling_space is None:
            sx.sampling_space = tri_space
        else:
            sx.sampling_space = sampling_space
            
        sx.simplex_budget = simplex_budget
        sx.design = design
        
        sx.tri_setup(sample_box, tri_space=tri_space, incremental=incremental)
        
        sx.setup(issi=issi, weighting_space=weighting_space,
                  on_add_simplex=on_add_simplex,
                   on_delete_simplex=on_delete_simplex)        



    def setup(sx, issi=None, weighting_space=None,
                 on_add_simplex=None, on_delete_simplex=None):
        
        sx.issi = issi #č ISSI potřebujem pro tri_estimation
            
        if weighting_space is None:
            sx.weighting_space = sx.tri_space
        else:
            sx.weighting_space = weighting_space
        
        #č kolbeky
        sx.on_add_simplex = on_add_simplex
        sx.on_delete_simplex = on_delete_simplex
            
        #оӵ кылсузъет кылдытом
        sx.simplex_stats = dict()
        


class _CubatureTriangulation:
    def __init__(sx, sample_box, tn_scheme=None, tri_space='Rn', issi=None, weighting_space=None, \
            incremental=True, on_add_simplex=None, on_delete_simplex=None):
        
        sx.tri_setup(sample_box, tri_space=tri_space, incremental=incremental)
        _SamplingTriangulation.setup(sx, issi=issi,
                 weighting_space=weighting_space,
                  on_add_simplex=on_add_simplex,
                   on_delete_simplex=on_delete_simplex)
        
        #č Hodil by se nám levný odhad ve chvili, 
        #č kdy už si nemôžeme dovoliť víc jak jednoho kandidata v simplexu
        #č schema bere vrcholy simplexu, které májí stejné vahy. 
        #č  Tohle by se přece nemohlo selhat!
        # tn_fallback_scheme
        sx.stroud_tn_1_2 = quadpy.tn.stroud_tn_1_2(sample_box.nvar)
            
        sx.set_tn_scheme(tn_scheme)
        
        #оӵ чылкыт f_model
        #č ptat se na něco u skříňky je extrémně dráho
        sx.f = sample_box.f_model




    #č spojení integraci s candidaty nejdřív se zdálo 
    #č efektivnou opmizací, ale teď začíná obracet protí nám
    #č mohli bychom chtit přesně integrovat, 
    #č ale ukladat jen mírnější počty kandidatů
    #č Uděláme to takhle. 
    def set_tn_scheme(sx, tn_scheme):
        sx.tn_scheme = tn_scheme
        
        if tn_scheme is None:
            sx.tn_scheme = sx.stroud_tn_1_2 #č do odhadů se píše tn_scheme.name
            sx.integrate_simplex = sx._cheap_integrate_simplex
        elif sx.on_add_simplex is not None:
            sx.integrate_simplex = sx._callback_integrate_simplex
        else:
            sx.integrate_simplex = sx._no_callback_integrate_simplex
            
            
    def _fallback_simplex_integration(sx, vertices):
        vertices_model = getattr(vertices, sx.tri_space)
        fx = vertices.pdf(sx.tri_space)
        
        # very special for stroud_tn_1_2
        def _get_pdf(x): return fx
        
        simplex_measure = sx.stroud_tn_1_2.integrate(_get_pdf, vertices_model)
        
        if (not np.isfinite(simplex_measure)) or (simplex_measure < 0):
            print("Kurňa, rozbíla se nám integrace totálně", simplex_measure)
            print("min_pdf", np.min(fx), "max_pdf", np.max(fx))
            simplex_measure = 0
        
        return simplex_measure
            
    # cheap means we will use (existent) simplex vertices 
    # to integrate by stroud_tn_1_2 cubature scheme
    #č skoro není důvod zde použivat quadpy. 
    #č stroud_tn_1_2 je pouhym průměrem vrcholů
    #č ale nechce se mi tahat sem výpočet objemu simplexu s těm determinantem
    #č nechame to proto kuadpajovi
    def _cheap_integrate_simplex(sx, indices, event, event_id, fr, wfr):
            
        vertices = sx.f[indices]
        simplex_measure = sx._fallback_simplex_integration(vertices)
        
        assert fr >= 0
        assert wfr >= 0
        
        fm = simplex_measure * fr
        wfm = simplex_measure * wfr
        
        #č ISSI tu nemáme, místo toho prostě ukladáme co máme do slovníku
        sx.simplex_stats[tuple(indices)] = (event_id, simplex_measure, fm, wfm)
        
        if sx.on_add_simplex is not None:
            cell_stats = dict()
            
            cell_stats['cell_probability'] = simplex_measure
            cell_stats['vertex_estimation'] = fm
            cell_stats['weighted_vertex_estimation'] = wfm
            cell_stats['event'] = event
            
            
            #č kolbek ↓
            sx.on_add_simplex(sx, indices=indices, simplex=vertices, \
                                nodes=vertices, cell_stats=cell_stats)
        
        
    def _callback_integrate_simplex(sx, indices, event, event_id, fr, wfr):
        
        f = sx.f
        
        # quadpy
        points = [] # container #č vždyť Python nemá pointery
        def _get_pdf(x):
            nodes = f.new_sample(x.T, sx.tri_space)
            fx = nodes.pdf(sx.tri_space)
            #print("estimate", indices)
            #print('x', x.T)
            #print('fx', fx)
            points.append((nodes, fx)) # side effect
            return fx
            
        vertices = f[indices]
        vertices_model = getattr(vertices, sx.tri_space)
        simplex_measure = sx.tn_scheme.integrate(_get_pdf, vertices_model)
        
        if (not np.isfinite(simplex_measure)) or (simplex_measure < 0):
            print("_CubatureTriangulation:")
            if simplex_measure < 0:
                print("Integráční schema je na houby.", simplex_measure)
            else:
                print("Kurňa, rozbíla se nám integrace", simplex_measure)
            print("min_pdf", np.min(points[0][1]), "max_pdf", np.max(points[0][1]))
            simplex_measure = sx._fallback_simplex_integration(vertices)
            print("fallback integration result:", simplex_measure)
        
        assert fr >= 0
        assert wfr >= 0
        
        fm = simplex_measure * fr
        wfm = simplex_measure * wfr
        
        #č ISSI tu nemáme, místo toho prostě ukladáme co máme do slovníku
        sx.simplex_stats[tuple(indices)] = (event_id, simplex_measure, fm, wfm)
        
        #č kolbek ↓
        cell_stats = dict()
        
        cell_stats['cell_probability'] = simplex_measure
        cell_stats['vertex_estimation'] = fm
        cell_stats['weighted_vertex_estimation'] = wfm
        cell_stats['event'] = event
        
        nodes, pdf = points[0]
        sx.on_add_simplex(sx, indices=indices, simplex=vertices, nodes=nodes, cell_stats=cell_stats)
        
        
        
    #č spojení integraci s candidaty nejdřív se zdálo 
    #č efiktivnou opmizací, ale teď začíná obracet protí nám
    def _no_callback_integrate_simplex(sx, indices, event, event_id, fr, wfr):
        #оӵ чылкыт f_model
        f = sx.sample_box.f_model
        
        # quadpy
        def _get_pdf(x):
            fx = f.sample_pdf(x.T, sx.tri_space)
            return fx
            
        vertices = f[indices]
        vertices_model = getattr(vertices, sx.tri_space)
        simplex_measure = sx.tn_scheme.integrate(_get_pdf, vertices_model)
        
        
        if (not np.isfinite(simplex_measure)) or (simplex_measure < 0):
            print("_CubatureTriangulation:")
            if simplex_measure < 0:
                print("Integráční schema je na houby.", simplex_measure)
            else:
                print("Kurňa, rozbíla se nám integrace", simplex_measure)
            simplex_measure = sx._fallback_simplex_integration(vertices)
            print("fallback integration result:", simplex_measure)
        
        
        assert fr >= 0
        assert wfr >= 0
        
        fm = simplex_measure * fr
        wfm = simplex_measure * wfr
        
        #č ISSI tu nemáme, místo toho prostě ukladáme co máme do slovníku
        sx.simplex_stats[tuple(indices)] = (event_id, simplex_measure, fm, wfm)
        
    
    


# Shull should be inicialized with powerset_correction=False
class FullSamplingTriangulation(_FullTriangulation, _SamplingTriangulation):
    
    def get_pf_estimation(sx):
        # TRI-compatible estimation
        # -1=outside, 0=success, 1=failure, 2=mix
        tri_estimation = {-1:0, 0:0, 1:0, 2:0}
        sx.issi.get_estimations()
        tri_estimation[-1] = sx.issi.estimations[-1]
        
        
        #č něco konkretnějšího
        vertex_estimation = 0
        weighted_vertex_estimation = 0
        
        #č otside asi necháme nulovým
        global_stats = {0:0, 1:0, 2:0}
        
        # let's iterate over all simplices we have
        # (calling code is responsible for the .simplex_stats validity)
        for key, simplex_measure in sx.issi.estimations.items():
            if key == -1:
                continue
            event_id, _simplex_measure, fr, wfr = sx.simplex_stats[key]
            tri_estimation[event_id] += simplex_measure
            global_stats[event_id] += _simplex_measure
            vertex_estimation += fr * simplex_measure
            weighted_vertex_estimation += wfr * simplex_measure
        
        #ё так, для красоты
        global_stats['outside'] = 0
        global_stats['success'] = global_stats.pop(0)
        global_stats['failure'] = global_stats.pop(1)
        global_stats['mix'] = global_stats.pop(2) 
        
        return {'TRI_estimation': tri_estimation, 'global_stats': global_stats, \
            'vertex_estimation' : vertex_estimation, \
            'weighted_vertex_estimation' : weighted_vertex_estimation,
            'coplanar':sx.tri.coplanar}
            
        
    #č vyhodil jsem simplex_id'y
    def integrate_simplex(sx, indices, event, event_id, fr, wfr):
        #оӵ чылкыт f_model
        #č do sample_simplexu musíme poslat čístý f_model
        # we should send pure f_model to sample_simplex()
        vertices = sx.sample_box.f_model[indices]
        print("estimate", indices)
        h_plan, convex_hull, simplex_measure = sample_simplex(vertices,\
                model_space=sx.tri_space, sampling_space=sx.sampling_space,\
                 nis=sx.simplex_budget, design=sx.design)
        
        
        #čs necháme ISSI trapit sa pravděpodobnostma
        mask = ~h_plan.is_outside
        sx.issi.add_single_event_data(h_plan.w[mask], event=tuple(indices), nis=sx.simplex_budget)
        
        #č ještě navíc ukložime co máme do slovníku
        #č zde slovník obsahuje odlišné hodnoty! fr a wfr místo fm a wfm!
        sx.simplex_stats[tuple(indices)] = (event_id, simplex_measure, fr, wfr)
            
        
        
        if sx.on_add_simplex is not None:
            cell_stats = dict()
            
            cell_stats['cell_probability'] = simplex_measure
            cell_stats['vertex_estimation'] = fr * simplex_measure
            cell_stats['weighted_vertex_estimation'] = wfr * simplex_measure
            cell_stats['event'] = event
            
            
            # kolbek ↓
            nodes = h_plan[mask]
            nodes.event_id = np.full(len(nodes), event_id, dtype=np.int8)
            out_nodes = h_plan[~mask]
            sx.on_add_simplex(sx, indices=indices, simplex=vertices,\
                 nodes=nodes, cell_stats=cell_stats, out_nodes=out_nodes)
            
    





# Shull should be inicialized with powerset_correction=True
class FastSamplingTriangulation(_FastTriangulation, _SamplingTriangulation):
        
    #č vyhodil jsem simplex_id'y
    def integrate_simplex(sx, indices, event, event_id, fr, wfr):
        #оӵ чылкыт f_model
        #č do sample_simplexu musíme poslat čístý f_model
        # we should send pure f_model to sample_simplex()
        vertices = sx.sample_box.f_model[indices]
        print("estimate", indices)
        h_plan, convex_hull, simplex_measure = sample_simplex(vertices,\
                model_space=sx.tri_space, sampling_space=sx.sampling_space,\
                 nis=sx.simplex_budget, design=sx.design)
        
        
        #čs necháme ISSI trapit sa pravděpodobnostma
        mask = ~h_plan.is_outside
        sx.issi.add_single_event_data(h_plan.w[mask], event=tuple(indices), nis=sx.simplex_budget)
        
        fm = simplex_measure * fr
        wfm = simplex_measure * wfr
        
        #č ISSI tu nemáme, místo toho prostě ukladáme co máme do slovníku
        sx.simplex_stats[tuple(indices)] = (event_id, simplex_measure, fm, wfm)
            
        
        
        if sx.on_add_simplex is not None:
            cell_stats = dict()
            
            cell_stats['cell_probability'] = simplex_measure
            cell_stats['vertex_estimation'] = fm
            cell_stats['weighted_vertex_estimation'] = wfm
            cell_stats['event'] = event
            
            
            # kolbek ↓
            mask = ~h_plan.is_outside
            nodes = h_plan[mask]
            nodes.event_id = np.full(len(nodes), event_id, dtype=np.int8)
            out_nodes = h_plan[~mask]
            sx.on_add_simplex(sx, indices=indices, simplex=vertices,\
                 nodes=nodes, cell_stats=cell_stats, out_nodes=out_nodes)
    


# Shull should be inicialized with powerset_correction=True
class FastCubatureTriangulation(_FastTriangulation, _CubatureTriangulation):
    pass #č máme všecko, čo potrebujem


# should we use Shull after all?
class FullCubatureTriangulation(_FullTriangulation, _CubatureTriangulation):
        
    def get_pf_estimation(sx):
        # TRI-compatible estimation
        # -1=outside, 0=success, 1=failure, 2=mix
        tri_estimation = {-1:0, 0:0, 1:0, 2:0}
        
        #č něco konkretnějšího
        vertex_estimation = 0
        weighted_vertex_estimation = 0
        
        #č nechce se mi počitat přes numpy: np.array(tuple(c.values()))
        # let's iterate over all simplices we have
        # (calling code is responsible for the .simplex_stats validity)
        for event_id, simplex_measure, fm, wfm in sx.simplex_stats.values():
            tri_estimation[event_id] += simplex_measure
            vertex_estimation += fm
            weighted_vertex_estimation += wfm
        
        #č outside klidně může být i záporným
        tri_estimation[-1] = 1 - tri_estimation[0] - tri_estimation[1] - tri_estimation[2]
        
        #č do global_stats exportujeme faktické odhady
        # -1=outside, 0=success, 1=failure, 2=mix
        global_stats = dict()
        global_stats['outside'] = 0
        global_stats['success'] = tri_estimation[0]
        global_stats['failure'] = tri_estimation[1]
        global_stats['mix'] = tri_estimation[2]
        
        return {'TRI_estimation': tri_estimation, 'global_stats': global_stats, \
            'vertex_estimation' : vertex_estimation, \
            'weighted_vertex_estimation' : weighted_vertex_estimation,
            'coplanar':sx.tri.coplanar}

    
        
#č Triangulation třída byla navržena s těsnou vazbou na Shull in mind.
#č Snahou bylo vyrovnání odhadů, získaných při hojném využití IS
#č Teď ale, chceme-li použit Ghull + quadpy, potřebujem třídu bez vázby na Shull
#č Dávám to do zvláštní třídy jen kvůli logickému rozdělení kódu
#č Jinak by se třída nijak nelišila od FastCubatureTriangulation
class JustCubatureTriangulation(_FastTriangulation, _CubatureTriangulation):
#č Tahle třída stala se komplikovanou jako šroub.
#č zdědené metody, náhled z hlediska vazby na ISSI:
# implicitly inherited from _Triangulation by _FastTriangulation:
# setup - OK (implicitně zadává se issi=None)
# get_events - OK
# update - OK (co vidím, není vazán na Shull, řeší pouze triangulaci)
# is_mixed - OK

# inherited from _FastTriangulation(_Triangulation) itself:
# integrate - OK
# !get_pf_estimation - neOK
# _invalidate_simplex - OK
# estimate_simplex - OK
    
# inherited from _CubatureTriangulation:
# __init__ - OK (implicitně zadává se issi=None)
# integrate_simplex - OK

    #č to je právý pf_estimation
    #č jiné třídy ve skutku vracej tri_estimation
    def get_pf_estimation(sx):
        # TRI-compatible estimation
        # -1=outside, 0=success, 1=failure, 2=mix
        #č ISSI nepouživáme, outside (-1), ani success (0) nebudou korektní
        tri_estimation = {-1:0, 0:0, 1:0, 2:0}
        
        #č něco konkretnějšího
        vertex_estimation = 0
        weighted_vertex_estimation = 0
        
        #č nechce se mi počitat přes numpy: np.array(tuple(c.values()))
        # let's iterate over all simplices we have
        # (calling code is responsible for the .simplex_stats validity)
        for event_id, simplex_measure, fm, wfm in sx.simplex_stats.values():
            tri_estimation[event_id] += simplex_measure
            vertex_estimation += fm
            weighted_vertex_estimation += wfm
        
        
        #ё так, для красоты
        global_stats = dict()
        # outside dodá Ghull
        global_stats['success_points'] = None #č další kód musí to přepsat
        global_stats['failure_points'] = None #č další kód musí to přepsat
        global_stats['success'] = None #č další kód musí to přepsat
        global_stats['failure'] = tri_estimation[1]
        global_stats['mix'] = tri_estimation[2]
        global_stats['vertex_estimation'] = vertex_estimation
        global_stats['weighted_vertex_estimation'] = weighted_vertex_estimation
        global_stats['nsimplex'] = sx.tri.nsimplex
        global_stats['tn_scheme'] = sx.tn_scheme.name
        global_stats['tn_scheme_points'] = sx.tn_scheme.points.shape[1]
        global_stats['newly_invalidated'] = sx.newly_invalidated
        global_stats['newly_estimated'] = sx.newly_estimated
        global_stats['simplex_stats'] = len(sx.simplex_stats)
        global_stats['candidates_sets'] = None #č další kód musí to přepsat
        global_stats['ncoplanar'] = len(sx.tri.coplanar)
        
        return {'TRI_estimation': tri_estimation, 'global_stats': global_stats, \
            'vertex_estimation' : vertex_estimation, \
            'weighted_vertex_estimation' : weighted_vertex_estimation, 
            'coplanar':sx.tri.coplanar}






CubatureEstimation = namedtuple('CubatureEstimation', (
                        'nvar',
                        'nsim',
                        'success',
                        'failure',
                        'mix',
                        'vertex_ratio_estimation',
                        'vertex_estimation',
                        'weighted_ratio_estimation',
                        'nsimplex',
                        #'tn_scheme',
                        'tn_scheme_points',
                        'newly_invalidated',
                        'newly_estimated',
                        'failure_simplices',
                        'mixed_simplices',
                        'ncoplanar'
                        ))



class FullCubatureIntegration(_Triangulation):
    def __init__(sx, sample_box, tn_scheme, tri_space='Rn', incremental=True, 
              on_failure_added=lambda *__: None, on_mixed_added=lambda *__: None,
              on_safe_added=lambda *__: None, on_delete_simplex=lambda __: None):
        
        sx.tri_setup(sample_box, tri_space=tri_space, incremental=incremental)
        
        sx.tn_scheme = tn_scheme
        
        #оӵ чылкыт f_model
        #č ptat se na něco u skříňky je extrémně dráho
        sx.f = sample_box.f_model
    
        sx.PDF = sample_box.pdf(tri_space)
        sx.failsi = sample_box.failsi
        
        #č kolbeky
        sx.on_safe_added = on_safe_added
        sx.on_failure_added = on_failure_added
        sx.on_mixed_added = on_mixed_added
        sx.on_delete_simplex = on_delete_simplex
        
        #оӵ кылсузъет кылдытом
        sx.safe_simplices = dict()
        sx.failure_simplices = dict()
        sx.mixed_simplices = dict()
        
        sx.centroids = dict()
        
    
    def integrate(sx):
        simplices = sx.tri.simplices
        in_failure = sx.failsi[simplices]
        
        has_failure = in_failure.any(axis=1)
        all_failure = in_failure.all(axis=1)
        
        for indices in simplices[all_failure]:
            simplex = tuple(indices)
            #č ty množiny jsou super
            sx.simplices_set.add(simplex)
            sx._integrate_red_simplex(simplex, indices)
            
        for indices in simplices[~has_failure]:
            simplex = tuple(indices)
            #č ty množiny jsou super
            sx.simplices_set.add(simplex)
            sx._integrate_safe_simplex(simplex, indices)
            
        mixed_mask = np.logical_and(has_failure, ~all_failure)
        simplices = simplices[mixed_mask]
        in_failure = in_failure[mixed_mask]
        
        frs = np.sum(in_failure, axis=1) / (sx.sample_box.nvar + 1)
        pdfs = sx.PDF[simplices] 
        fpdfs = np.sum(pdfs * in_failure, axis=1)
        wfrs = fpdfs / np.sum(pdfs, axis=1)
        mfpdfs = fpdfs / (sx.sample_box.nvar + 1)
        
        for indices, fr, wfr, mfpdf in zip(simplices, frs, wfrs, mfpdfs):
            #č ty množiny jsou super
            simplex = tuple(indices)
            #č ty množiny jsou super
            sx.simplices_set.add(simplex)
            sx._integrate_mixed_simplex(simplex, indices, fr, wfr, mfpdf)
            
        
             
    
    #č vyhodil jsem simplex_id'y
    def _invalidate_simplices(sx, simplices_set_to_delete):
        
        # here "simplices_set_to_delete" is a set of tuples
        
        #č ty simplexy NEmusí tam být, 
        for simplex in simplices_set_to_delete:
            sx.failure_simplices.pop(simplex, None)
            sx.mixed_simplices.pop(simplex, None)
            sx.safe_simplices.pop(simplex, None)
            
            sx.centroids.pop(simplex, None)
        
            #č Bacha, teď posíláme tuple. 
            #č Kód na té straně úplně stejně bude vyhazovat 
            #č záznamy ze slovníků
            sx.on_delete_simplex(simplex)


    def estimate_simplices(sx, simplices_set_to_estimate):
        #č aktualizace krajské urovně
        sx.PDF = PDF = sx.sample_box.pdf(sx.tri_space)
        sx.failsi = failsi = sx.sample_box.failsi
        
        #ё вызывающая функция запускает estimate_simplex
        #ё на всём подряд без разбору.
        #č Našim úkolem je zjistit co je simplex zač
        #č a ty zelené ignorovat
        
        # fp is like failure points. Number of failure points
        max_fp = sx.sample_box.nvar + 1
        
        for simplex in simplices_set_to_estimate:
            indices = np.array(simplex)
            
            #č žádný intersect, žádný setdiff
            #č tohle je nejrychlejší!
            indices_failsi = failsi[indices]
            
            # fp is like failure points. Number of failure points
            fp = len(indices_failsi[indices_failsi]) # the fastest solution
            
            if fp == max_fp:
                sx._integrate_red_simplex(simplex, indices)
            elif fp > 0:
                fr = fp / max_fp
                pdf = PDF[indices]
                fpdf = np.sum(pdf[indices_failsi]) 
                # same as np.average(failsi, weights=pdf), but faster
                wfr = fpdf / np.sum(pdf)
                mfpdf = fpdf / max_fp
                sx._integrate_mixed_simplex(simplex, indices, fr, wfr, mfpdf)
            else:
                sx._integrate_safe_simplex(simplex, indices)
    
            
            
#    def _integrate_mixed_simplex(sx, simplex, indices):
#        
#        vertices_model = sx.tri.points[indices]
#        PDF = sx.PDF[indices]
#        failsi = sx.failsi[indices]
#        
#        # quadpy
#        def _get_pdf(x):
#            dmv = 1 / spatial.distance.cdist(x.T, vertices_model) 
#            dmw = dmv * PDF
#            
#            # same as np.sum(dmv[:, failsi], axis=1) / np.sum(dmv, axis=1)
#            pfv = np.sum(dmv.T[failsi], axis=0) / np.sum(dmv, axis=1)
#            pfw = np.sum(dmw.T[failsi], axis=0) / np.sum(dmw, axis=1)
#            
#            # side effect
#            if sx.on_add_simplex is not None: 
#                nodes = sx.f.new_sample(x.T, sx.tri_space)
#                fx = nodes.pdf(sx.tri_space)
#                # -1=outside, 0=success, 1=failure, 2=mix
#                args = {'event_id':2, 'indices':indices}
#                sx.on_add_simplex(CandyNodes(nodes, args, pfv=pfv, pfw=pfw))
#            else:
#                fx = sx.f.sample_pdf(x.T, sx.tri_space)
#            
#            return fx, fx*pfv, fx*pfw
#            
#        
#        simplex_measures = sx.tn_scheme.integrate(_get_pdf, vertices_model)
#        #č místo fallback integrací
#        mask = simplex_measures < 0
#        if np.any(mask):
#            print("Negative measures have occured in simplex %s" % indices)
#            print("Rozbíla se nám integrace, integráční schema je na houby.")
#            simplex_measures[mask] = 0
#        
#        p_mixed, pfv_simplex, pfw_simplex = simplex_measures
#        
#        
#        assert p_mixed >= 0
#        assert pfv_simplex >= 0
#        assert pfw_simplex >= 0
#        
#        #č přídavám jednou, sčítám pořad dokola
#        simplex_estimation = np.array((p_mixed, 0, pfv_simplex, pfw_simplex))
#        sx.simplex_stats[simplex] = simplex_estimation
        
            
    def _integrate_mixed_simplex(sx, simplex, indices, fr, wfr, mfpdf):
        
        vertices_model = sx.tri.points[indices]
        

        x = quadpy.tn.transform(sx.tn_scheme.points, vertices_model.T)
        vol = quadpy.tn.get_vol(vertices_model)
        
        if not np.isfinite(vol):
            print("Incorrect volume has occured in simplex %s" % indices)
            vol = 0
        
        nodes = sx.f.new_sample(x.T, sx.tri_space)
        fx = nodes.pdf(sx.tri_space)

        p_mixed = vol * np.dot(fx, sx.tn_scheme.weights)
            
        
        if not (p_mixed > 0):
            print("Incorrect measure %s has occured in simplex %s" % (p_mixed, indices))
            #print("Rozbíla se nám integrace, integráční schema je na houby.")
            p_mixed = 0
        
        
        pfv = p_mixed * fr
        pfw = p_mixed * wfr
        pf = vol * mfpdf
        
        assert p_mixed >= 0
        assert pfv >= 0
        assert pfw >= 0
        assert pf >= 0
        
        #č přídavám jednou, sčítám pořad dokola
        simplex_estimation = np.array((p_mixed, pfv, pfw, pf))
        sx.mixed_simplices[simplex] = simplex_estimation 
        #č odhady jsou ve slovníku, posíláme jen to, co tam není
        sx.on_mixed_added(simplex, indices, vertices_model, nodes, vol, fr, wfr, mfpdf)
        
            
    def _integrate_red_simplex(sx, simplex, indices):
        
        vertices_model = sx.tri.points[indices]
        
        x = quadpy.tn.transform(sx.tn_scheme.points, vertices_model.T)
        vol = quadpy.tn.get_vol(vertices_model)
        
        if not np.isfinite(vol):
            print("Incorrect volume has occured in simplex %s" % indices)
            vol = 0
        
        nodes = sx.f.new_sample(x.T, sx.tri_space)
        fx = nodes.pdf(sx.tri_space)
        
        weights = fx * sx.tn_scheme.weights

        p_failure = vol * np.sum(weights)
            
        
        if p_failure < 0:
            print("Negative measure has occured in simplex %s" % indices)
            #print("Rozbíla se nám integrace, integráční schema je na houby.")
            p_failure = 0
        
        assert p_failure >= 0
        
        sx.centroids[simplex] = np.average(x, axis=1, weights=weights)
        sx.failure_simplices[simplex] = p_failure    
        #č odhady jsou ve slovníku, posíláme jen to, co tam není
        sx.on_failure_added(simplex, indices, vertices_model, nodes, vol)
            
            
    def get_sensitivities(sx, depth=2):
        gradients, simplices = sx.get_gradients(depth=depth)
        
        p_mix = 0
        global_gradient = np.zeros(sx.sample_box.nvar)
        sensitivities = np.zeros(sx.sample_box.nvar)
        
        for gradient, simplex in zip(gradients, simplices):
            # p_mixed, pfv, pfw, pf
            p_mixed, pfv, pfw, pf = sx.mixed_simplices[tuple(simplex)]
            p_mix += p_mixed
            global_gradient += gradient * p_mixed
            sensitivities += gradient**2 * p_mixed
            
        #length = np.sqrt(np.inner(global_gradient, global_gradient))
        #global_gradient = global_gradient / length
        
        global_gradient /= p_mix
        sensitivities /= p_mix
        
        return p_mix, global_gradient, sensitivities
            
            
    def get_failure_moments(sx):
        simplices = sx.tri.simplices[sx.is_mixed()]
        
        nvar = sx.sample_box.nvar
        
        failsi = sx.sample_box.failsi
        
        in_failure = failsi[simplices]
        
        
        X = getattr(sx.sample_box, sx.tri_space)
        
        #č stačí tak, když jedeme jen přes červené simplexy
        PDF = sx.sample_box.pdf(sx.tri_space)
        #failure_PDF = sx.sample_box.pdf(sx.tri_space) * failsi
        
        
        nbodies = np.sum(in_failure) + len(sx.centroids)
        
        
        centroids = np.empty((nbodies, nvar + 1))
        V = np.empty(nbodies)
        
        i = 0
        room = np.zeros((nvar + 1, nvar + 1))
        base = np.zeros(nvar + 1)
        for simplex, failures in zip(simplices, in_failure):
            vertices_model = X[simplex]
            base[:-1] = vertices_model[0]
            
            np.subtract(vertices_model, base[:-1], out=room[:, :-1])
            
            for vertex, pdf in zip(room[failures], PDF[simplex[failures]]):
                room[0] = vertex
                room[0,-1] = pdf
                
                V[i] = np.linalg.det(room) / np.math.factorial(nvar + 1)
                np.mean(room, axis=0, out=centroids[i])
                centroids[i] += base
                
                i += 1
                
                
                
        assert i == np.sum(in_failure) 
        
        for centroid, failure_simplex in zip(sx.centroids.values(), sx.failure_simplices.values()):
            centroids[i, :-1] = centroid
            V[i] = failure_simplex
            i += 1
            
        mask = V > 0
        pf = np.sum(V[mask])
        mean = np.average(centroids[mask], axis=0, weights=V[mask])
        
        cov_matrix = np.cov(centroids[mask], rowvar=False, ddof=0, aweights=V[mask])
    
        return pf, mean[:-1], cov_matrix[:-1, :-1]
    
    def _integrate_safe_simplex(sx, simplex, indices):
        
        vertices_model = sx.tri.points[indices]
        
        x = quadpy.tn.transform(sx.tn_scheme.points, vertices_model.T)
        vol = quadpy.tn.get_vol(vertices_model)
        
        if not np.isfinite(vol):
            print("Incorrect volume has occured in simplex %s" % indices)
            vol = 0
        
        nodes = sx.f.new_sample(x.T, sx.tri_space)
        fx = nodes.pdf(sx.tri_space)

        p_safe = vol * np.dot(fx, sx.tn_scheme.weights)
            
        
        if p_safe < 0:
            print("Negative measure has occured in simplex %s" % indices)
            p_safe = 0
        
        assert p_safe >= 0
        
        sx.safe_simplices[simplex] = p_safe
        #č odhady jsou ve slovníku, posíláme jen to, co tam není
        sx.on_safe_added(simplex, indices, vertices_model, nodes, vol)
            

    def get_pf_estimation(sx):
        # p_mixed, pfv, pfw, pf
        simplex_estimations = np.zeros(4, dtype=float)
        
        #č nechce se mi počitat přes numpy: np.array(tuple(c.values()))
        # let's iterate over all simplices we have
        # (calling code is responsible for the .simplex_stats validity)
        for simplex_estimation in sx.mixed_simplices.values():
            simplex_estimations += simplex_estimation
        
        p_failure = 0
        for failure_simplex in sx.failure_simplices.values():
            p_failure += failure_simplex
        
        p_success = 0
        for safe_simplex in sx.safe_simplices.values():
            p_success += safe_simplex
        
        p_mixed, pfv, pfw, pf = simplex_estimations
        nsim, nvar = sx.tri.points.shape
        return CubatureEstimation(
                                  nvar,
                                  nsim,
                                  p_success,
                                  p_failure,
                                  p_mixed,
                                  pfv + p_failure,
                                  pf + p_failure,
                                  pfw + p_failure,
                                  sx.tri.nsimplex,
                                  #sx.tn_scheme.name,
                                  sx.tn_scheme.points.shape[1],
                                  sx.newly_invalidated,
                                  sx.newly_estimated,
                                  len(sx.failure_simplices),
                                  len(sx.mixed_simplices),
                                  len(sx.tri.coplanar)
                                  )





#č zadavame v každem integračním bodě očekavaní pravděpodobnosti poruchy 
# p_f + p_s = 1
#č jednou z cest integrace je rovnou vynasobit p_f hustoty pravděpodobnosti f(x)
# f_f(x) = f(x) * p_f(x)
#č f_f(x) integrujeme kubaturou. Tím jakoby integrujeme červenou část simplexu.
# Pf_simplex = sum(f_f * w) = sum(f * p_f * w), kde
# sum(w) = 1 #č vahy kubatur
#č Nebo můžem kubaturou prointegrovat přímo p_f(x), 
#č čímž dostaneme míru "poruchovosti" simplexu.
#č Houby, výsledek je jiný. 
#č A je stejně nekorektní jak odhad vzalenosti přes průměrnou rychlost
# pf_simplex = sum(p_f * w)
# P_simplex = sum(f * w)
# Pf_simplex = pf_simplex * P_simplex = sum(p_f * w) * sum(f * w) 
# (p_f1 * w1 + p_f2*w2 + p_f3*w3) * (f1 * w1 + f2*w2 + f3*w3)
class FastCubatureIntegration(FullCubatureIntegration):
    
    def integrate(sx):
        simplices = sx.tri.simplices
        in_failure = sx.failsi[simplices]
        
        has_failure = in_failure.any(axis=1)
        simplices = simplices[has_failure]
        in_failure = in_failure[has_failure]
        
        all_failure = in_failure.all(axis=1)
        for indices in simplices[all_failure]:
            simplex = tuple(indices)
            #č ty množiny jsou super
            sx.simplices_set.add(simplex)
            sx._integrate_red_simplex(simplex, indices)
            
        simplices = simplices[~all_failure]
        in_failure = in_failure[~all_failure]
        
        frs = np.sum(in_failure, axis=1) / (sx.sample_box.nvar + 1)
        pdfs = sx.PDF[simplices] 
        fpdfs = np.sum(pdfs * in_failure, axis=1)
        wfrs = fpdfs / np.sum(pdfs, axis=1)
        mfpdfs = fpdfs / (sx.sample_box.nvar + 1)
        
        for indices, fr, wfr, mfpdf in zip(simplices, frs, wfrs, mfpdfs):
            #č ty množiny jsou super
            simplex = tuple(indices)
            #č ty množiny jsou super
            sx.simplices_set.add(simplex)
            sx._integrate_mixed_simplex(simplex, indices, fr, wfr, mfpdf)
            
        
    def _integrate_safe_simplex(sx, simplex, indices):
        pass

    



class GaussCubatureIntegration(_Triangulation, _Sense):
    def __init__(sx, sample_box, tn_scheme, incremental=True, full=False):
        
        sx.tri_setup(sample_box, tri_space='G', incremental=incremental)
        
        sx.tn_scheme = tn_scheme
        sx.full = full
    
        #оӵ кылсузъет кылдытом
        sx.safe_simplices = dict()
        sx.failure_simplices = dict()
        sx.mixed_simplices = dict()
        
        sx._norm_pdf_C = (2*np.pi)**(sample_box.nvar / 2)
        
        
    def update(sx):
        sx._tri_update() #č chyby nechytáme
        

    def integrate_simplex(sx, indices):
        sx.newly_estimated += 1
        return sx._preintegrate_simplex(indices)
        
    def _preintegrate_simplex(sx, indices):
        vertices_model = sx.tri.points[indices]
        
        vol = quadpy.tn.get_vol(vertices_model)
        
        if not np.isfinite(vol) or (vol < 0):
            print("Incorrect volume %s has occured in simplex %s" % (vol, indices))
            return 0, 0
        
        
        x = sx._x
        fx = sx._fx
        
        # nvar x n_integration_nodes
        # Transform the points `xi` from the reference simplex onto `simplex`.
        # same as quadpy.tn.transform(sx.tn_scheme.points, vertices_model.T)
        #np.dot(simplex, points)
        np.matmul(vertices_model.T, sx.tn_scheme.points, out=x) # G nodes
        
        np.square(x, out=x)
        np.divide(x, -2, out=x)
        np.exp(x, out=x) # == norm.pdf() * np.sqrt(2*np.pi)
        
        np.prod(x, axis=0, out=fx)

        mean = np.inner(fx, sx.tn_scheme.weights)
        
        if mean > 0:
            return vol, mean
        else:
            print("Negative measure %s has occured in simplex %s" % (mean, indices))
            return vol, 0
        
    def get_simplex_probability(sx, indices):
        key = indices.tobytes()
        p_mixed, pfv, pfw, pf = sx.mixed_simplices[key]
        return p_mixed / sx._norm_pdf_C
            
    # share = p_simplex * V**((ndim-1)/ndim)
    # component of sensitivity intagral f(x)dS
    def get_simplex_share(sx, indices):
        vol, fx = sx._preintegrate_simplex(indices)
        #č matematicky korektně musíme hustoty ještě vydělit
        #sx._norm_pdf_C
        #č ale u těch citlovostí jde nám jen o podíly
        #č a nemusíme provadět jednu operaci navíc
        ndim = len(indices) - 1
        return fx * vol**((ndim-1)/ndim)
            

    def get_pf_estimation(sx):
        if len(sx.tri.points) < sx.sample_box.nsim:
            sx._tri_update() #č chyby nechytáme
        
        nsim, nvar = sx.tri.points.shape
        full = sx.full
        
    
        #č kdyby se změnila kubatura
        ncubature = len(sx.tn_scheme.weights)
        sx._x = np.empty((nvar, ncubature))
        sx._fx = np.empty(ncubature)
        
        sx.newly_estimated = 0
        
        safe_simplices = sx.safe_simplices
        failure_simplices = sx.failure_simplices
        mixed_simplices = sx.mixed_simplices
        
        #оӵ выль кылсузъет кылдытом
        new_safe_simplices = dict()
        new_failure_simplices = dict()
        new_mixed_simplices = dict()
        
        
        PDF = sx.sample_box.pdf(sx.tri_space)
        failsi = sx.sample_box.failsi
        
        # fp is like failure points. Number of failure points
        max_fp = nvar + 1
        
        max_safe = -1
        max_mixed = -1
        
        p_failure = 0
        p_success = 0
        #p_mixed, pfv, pfw, pf = 0
        # p_mixed, pfv, pfw, pf
        mixed_estimation = np.zeros(4)
        
        for indices in sx.tri.simplices:
            indices_failsi = failsi[indices]
            
            # fp is like failure points. Number of failure points
            fp = np.count_nonzero(indices_failsi)
            
            if fp == max_fp:
                key = indices.tobytes()
                simplex_estimation = failure_simplices.pop(key, None)
                if simplex_estimation is None:
                    area, height = sx.integrate_simplex(indices)
                    simplex_estimation = area * height
                new_failure_simplices[key] = simplex_estimation
                p_failure += simplex_estimation
                
            elif fp > 0:
                key = indices.tobytes()
                simplex_estimation = mixed_simplices.pop(key, None)
                if simplex_estimation is None:
                    area, height = sx.integrate_simplex(indices)
                    p_mixed = area * height # / sx._norm_pdf_C
                    fr = fp / max_fp
                    pdf = PDF[indices]
                    fpdf = np.sum(pdf[indices_failsi]) 
                    # same as np.average(failsi, weights=pdf), but faster
                    wfr = fpdf / np.sum(pdf)
                    mfpdf = fpdf / max_fp
                    pfv = p_mixed * fr
                    pfw = p_mixed * wfr
                    #č použivá pouze plochu, tu konstantu nepotřebuje 
                    pf = area * mfpdf 
                    
                    #č přídavám jednou, sčítám pořad dokola
                    simplex_estimation = np.array((p_mixed, pfv, pfw, pf))
        
                new_mixed_simplices[key] = simplex_estimation
                mixed_estimation += simplex_estimation
                
                if simplex_estimation[0] > max_mixed:
                    max_mixed = simplex_estimation[0]
                    sx.max_mixed_indices = indices
                
                
            elif full:
                key = indices.tobytes()
                simplex_estimation = safe_simplices.pop(key, None)
                if simplex_estimation is None:
                    area, height = sx.integrate_simplex(indices)
                    simplex_estimation = area * height
                new_safe_simplices[key] = simplex_estimation
                p_success += simplex_estimation
    
                if simplex_estimation > max_safe:
                    max_safe = simplex_estimation
                    sx.max_safe_indices = indices
            
            
        
            
        sx.newly_invalidated =  len(safe_simplices) + \
                                len(mixed_simplices) + \
                                len(failure_simplices)
        
        
        sx.safe_simplices = new_safe_simplices
        sx.failure_simplices = new_failure_simplices
        sx.mixed_simplices = new_mixed_simplices
        
        sx.max_safe = max_safe / sx._norm_pdf_C
        sx.max_mixed = max_mixed / sx._norm_pdf_C
        
        p_success /= sx._norm_pdf_C
        p_failure /= sx._norm_pdf_C
        
        p_mixed, pfv, pfw, pf = mixed_estimation
        p_mixed /= sx._norm_pdf_C
        pfv /= sx._norm_pdf_C
        pfw /= sx._norm_pdf_C
        #č pf tu konstantu nepotřebuje 
        
        return CubatureEstimation(
                                  nvar,
                                  nsim,
                                  p_success,
                                  p_failure,
                                  p_mixed,
                                  pfv + p_failure,
                                  pf + p_failure,
                                  pfw + p_failure,
                                  sx.tri.nsimplex,
                                  #sx.tn_scheme.name,
                                  sx.tn_scheme.points.shape[1],
                                  sx.newly_invalidated,
                                  sx.newly_estimated,
                                  len(sx.failure_simplices),
                                  len(sx.mixed_simplices),
                                  len(sx.tri.coplanar)
                                  )


#
## global sample_box function
##č tím globálným sample_box'em my šetříme čas na poměrně drahých slajséch
#def get_failure_ratios(sample_box, event_id, simplices, weighting_space=None):
#    """
#    Function takes global sample_box, event_id, indices of vertex points
#    and (optionally) weighting_space to calculate weighted failure ratio
#    
#    Returns event and both failure and weighted failure ratio
#    
#    Values of event_id and event are as follows:
#    -1 = 'outside', 0=success, 1=failure, 2=mix
#    Please note, simplex cannot be "outside".
#    """
#    
#    # -1 = 'outside', 0=success, 1=failure, 2=mix
#    #č simplex -1 mít nemůže
#    if event_id == 0:
#        #event = 'success'
#        #fr = 0 # failure ratio
#        #wfr = 0 # weighted failure ratio
#        return 'success', 0, 0
#    elif event_id == 1:
#        #event = 'failure'
#        #fr = 1 # failure ratio
#        #wfr = 1 # weighted failure ratio
#        return 'failure', 1, 1
#    else: #č simplex -1 mít nemůže
#        #event = 'mix'
#        #č žádný intersect, žádný setdiff
#        #č tohle je nejrychlejší!
#        indices_failsi = sample_box.failsi[indices]
#        
#        # fp like a failure points. Number of failure points
#        fp = len(indices_failsi[indices_failsi]) # the fastest solution
#        fr = fp / len(indices) # failure ratio
#        # weighted failure ratio
#        if weighting_space is None:
#            wfr = fr
#        else:
#            indices_pdf = sample_box.pdf(weighting_space)[indices]
#            # same as np.average(failsi, weights=pdf), but faster
#            wfr = np.sum(indices_pdf[indices_failsi]) / np.sum(indices_pdf)
#            
#        return 'mix', fr, wfr
#
#
#



#č tato metoda je vlastně pro MinEnergyCensoredSampling
#č ale zde se taky může hodit
def get_events(sb, simplices): #simplices = bx.tri.simplices
    """
    Metoda musí simplexům přiřazovat jev 
    0=success, 1=failure, 2=mix
    """
    
    
    in_failure = sb.failsi[simplices]
    has_failure = in_failure.any(axis=1)
    all_failure = in_failure.all(axis=1)
    return np.int8(np.where(has_failure, np.where(all_failure, 1, 2), 0))


# local sample_box function
#č toto lokální řešení teoreticky mohlo být lepší protože ve chvili, 
#č kdy potřebujeme provzorkovat simplex - stejně potrebujem i slajs, 
#č testy ale ukazují, že běží to jen nepatrně rychleji
def get_simplex_event(simplex_sb, weighting_space=None):
    """
    Function requires sample_box object, that contains vertex points
    and (optionally) weighting_space to calculate weighted failure ratio
    
    Returns event, event_id and both failure and weighted failure ratio
    
    Values of event_id and event are as follows:
    -1 = 'outside', 0=success, 1=failure, 2=mix
    Please note, simplex cannot be "outside", therefore function will never return -1
    """
    
    #č žádný intersect, žádný setdiff
    #č tohle je nejrychlejší!
    failsi = simplex_sb.failsi
    # fp like a failure points. Number of failure points
    fp = len(failsi[failsi]) # the fastest solution
    
    # -1 = 'outside', 0=success, 1=failure, 2=mix
    #č simplex -1 mít nemůže
    if fp == 0:
        event = 'success'
        event_id = 0
        fr = 0 # failure ratio
        wfr = 0 # weighted failure ratio
    elif fp == len(simplex_sb):
        event = 'failure'
        event_id = 1
        fr = 1 # failure ratio
        wfr = 1 # weighted failure ratio
    else: #č simplex -1 mít nemůže
        event = 'mix'
        event_id = 2
        fr = fp / len(simplex_sb) # failure ratio
        # weighted failure ratio
        if weighting_space is None:
            wfr = fr
        else:
            pdf = simplex_sb.pdf(weighting_space)
            # same as np.average(failsi, weights=pdf), but faster
            wfr = np.sum(pdf[failsi]) / np.sum(pdf)
            
    return event, event_id, fr, wfr
    
    
    

# global sample_box function
#č tím globálným sample_box'em my šetříme čas na poměrně drahých slajséch
def get_indices_event(sample_box, indices, weighting_space=None):
    """
    Function takes global sample_box, indices of vertex points
    and (optionally) weighting_space to calculate weighted failure ratio
    
    Returns event, event_id and, as a bonus, both failure and weighted failure ratio
    
    Values of event_id and event are as follows:
    -1 = 'outside', 0=success, 1=failure, 2=mix
    Please note, simplex cannot be "outside", therefore function will never return -1
    """
    
    #č žádný intersect, žádný setdiff
    #č tohle je nejrychlejší!
    indices_failsi = sample_box.failsi[indices]
    
    # fp like a failure points. Number of failure points
    fp = len(indices_failsi[indices_failsi]) # the fastest solution
    
    # -1 = 'outside', 0=success, 1=failure, 2=mix
    #č simplex -1 mít nemůže
    if fp == 0:
        event = 'success'
        event_id = 0
        fr = 0 # failure ratio
        wfr = 0 # weighted failure ratio
    elif fp == len(indices):
        event = 'failure'
        event_id = 1
        fr = 1 # failure ratio
        wfr = 1 # weighted failure ratio
    else: #č simplex -1 mít nemůže
        event = 'mix'
        event_id = 2
        fr = fp / len(indices) # failure ratio
        # weighted failure ratio
        if weighting_space is None:
            wfr = fr
        else:
            indices_pdf = sample_box.pdf(weighting_space)[indices]
            # same as np.average(failsi, weights=pdf), but faster
            wfr = np.sum(indices_pdf[indices_failsi]) / np.sum(indices_pdf)
            
    return event, event_id, fr, wfr



# global sample_box function
#č tím globálným sample_box'em my šetříme čas na poměrně drahých slajséch
def get_failure_ratio(sample_box, event_id, indices, weighting_space=None):
    """
    Function takes global sample_box, event_id, indices of vertex points
    and (optionally) weighting_space to calculate weighted failure ratio
    
    Returns event and both failure and weighted failure ratio
    
    Values of event_id and event are as follows:
    -1 = 'outside', 0=success, 1=failure, 2=mix
    Please note, simplex cannot be "outside".
    """
    
    # -1 = 'outside', 0=success, 1=failure, 2=mix
    #č simplex -1 mít nemůže
    if event_id == 0:
        #event = 'success'
        #fr = 0 # failure ratio
        #wfr = 0 # weighted failure ratio
        return 'success', 0, 0
    elif event_id == 1:
        #event = 'failure'
        #fr = 1 # failure ratio
        #wfr = 1 # weighted failure ratio
        return 'failure', 1, 1
    else: #č simplex -1 mít nemůže
        #event = 'mix'
        #č žádný intersect, žádný setdiff
        #č tohle je nejrychlejší!
        indices_failsi = sample_box.failsi[indices]
        
        # fp like a failure points. Number of failure points
        fp = len(indices_failsi[indices_failsi]) # the fastest solution
        fr = fp / len(indices) # failure ratio
        # weighted failure ratio
        if weighting_space is None:
            wfr = fr
        else:
            indices_pdf = sample_box.pdf(weighting_space)[indices]
            # same as np.average(failsi, weights=pdf), but faster
            wfr = np.sum(indices_pdf[indices_failsi]) / np.sum(indices_pdf)
            
        return 'mix', fr, wfr




def get_TRI_estimation(siss, simplex_events):
    siss.get_estimations()
    simplices = np.array(tuple(siss.estimations.keys()))
    probabilities = np.array(tuple(siss.estimations.values()))
    
    estimation = dict()
    estimation[-1] = np.sum(probabilities[simplices == -1])
    
    #čs jevy aj klidně in-place (nerobím kopiju)
    events = simplices[simplices != -1]
    probabilities = probabilities[simplices != -1]
    
    #č zhruba - get_events() vrací pole s odpovidajícími čísly jevů pro každý simplex, počineje od nuly
    #č tím slajsingem my jakoby vybirame ke každemu nalezenemu simplexovi ten správnej mu odpovídajicí jev
    events = simplex_events[events]
    
    for i in range(3): #čs kvůli 0,1,2 robiť cyklus?
        estimation[i] = np.sum(probabilities[events == i])
    
    return estimation




def sample_simplex(vertices, model_space, sampling_space, nis, design=None):
    nvar = vertices.nvar
    
    # IS_like uses .new_sample method, so vertices can not be a SampleBox object
    #
    # already divided by nsim in variance formule
    # divide by /(nvar+1)/(nvar+2) from simplex inertia tensor solution
    # multiply by simplex_volume, but it looks like it shouldn't be here
    # for simplex: d = nvar+2 
    #č sice to má nazev h_plan, ale nese rozdělení a hustoty v f-ku
    h_plan = IS_stat.IS_like(vertices, sampling_space=sampling_space, \
                            nis=nis, d=nvar+2, design=design)
    
    
    h_plan_model = getattr(h_plan, model_space)
    vertices_model = getattr(vertices, model_space)
    
    #č budeme pokažde sestavovat ConvexHull z jedného simplexu
    #č a rešit jen zda naši bodíky "inside or outside"
    #č (s narustajícím nsim tohle brzy se stavá rychlejším než bežný dotaz)
    convex_hull = spatial.ConvexHull(vertices_model)
    h_plan.is_outside = is_outside(convex_hull, h_plan_model)
    mask = ~h_plan.is_outside
    
    
    #č součet tady nemusí sa (na konci) rovnat jedne
    #č opravdu dělíme nis'em, jako v normálním IS
    #č nikoliv počtem příjatých bodíků, 
    #č protože průměrná vaha je o hodně mene významná metrika
    simplex_measure = np.sum(h_plan.w[mask]) / nis
    
    #č v kódu scipy vidím, že objem máme zadarmo,
    #č přesneji říct, máme v ceně
    #č ConvexHull třida dycky nechá QHull přepočíst 
    #č objem a plochu při káždé změně
    #simplex_volume = convex_hull.volume
        
    #return h_plan, simplex_measure, simplex_volume
    return h_plan, convex_hull, simplex_measure
    




def is_outside(convex_hull, node_coordinates):

    x = node_coordinates
    
    #E [normal, offset] forming the hyperplane equation of the facet (see Qhull documentation for more)
    A = convex_hull.equations[:,:-1]
    b = convex_hull.equations[:,-1]
    
    # N=nsim
    NxN = A @ x.T + np.atleast_2d(b).T
    mask = np.any(NxN > 0, axis=0)
    return mask



def get_sub_simplex(convex_hull):
    """
    returns coordinates of sub-simplex, 
    
    truly yours, C.O.
    """
    #č zatím bez váh 
    #simplices -- ndarray of ints, shape (nfacet, ndim)
    return np.mean(convex_hull.points[[convex_hull.simplices]], axis=1)


def get_COBYLA_constraints(convex_hull):
    
        constraints = []
        
        #E [normal, offset] forming the hyperplane equation of the facet (see Qhull documentation for more)
        A = convex_hull.equations[:,:-1]
        b = convex_hull.equations[:,-1]
        
        def fungen(A_i, b_i):
            def fun(x):
                constrain = -(A_i @ x + b_i)
                #print(x, A_i, b_i, constrain)
                return constrain
            return fun
        
        for i in range(len(b)):
            # taken from COBYLA sources:
            # "the constraint functions should become
            # nonnegative eventually, at least to the precision of RHOEND"
            
            constraints.append({'type':'ineq', 'fun':fungen(A[i], b[i])})
        return constraints




def filter(Tri, candidates):
    """
    Metoda musí souřádnicím přiřazovat jev 
    "success", "failure", "mix", "outside"
    """
    
    # tady byl problém. Funkce byla původně navržena tak, 
    # aby ji nezajimalo co je na vstupu
    # to ale nefunguje
    # další funkce jako výstup očekavají něco s validním R-kem
    # no tj. já zde provádím posouzení transformací z R-ka vstupních souřadnic
    candidates_tri_space = getattr(candidates, Tri.tri_space)
        
        
    found_simplices = Tri.tri.find_simplex(candidates_tri_space)
    current_simplices = Tri.tri.simplices[found_simplices[found_simplices!=-1]]
    
    # -1 = 'out', 0=success, 1=failure, 2=mix
    found_simplices[found_simplices!=-1] = Tri.get_events(current_simplices)
    
    return found_simplices




#
# DEPRECATED
#

# unbelivable: I was unable to find a package to calculate the second moments of an simplex
def points_inertia_tensor(vertices, masses=1):
    """
    coordinates of vertices
    """
    nsim, nvar = np.shape(vertices)
    
    inertia_tensor = np.empty((nvar, nvar))
    for i in range(nvar):
        for j in range(i + 1):
            if i==j:
                inertia_tensor[i,j] = np.sum( masses * (np.sum(np.square(vertices), axis=1) - np.square(vertices[:, i])))
            else:
                inertia_tensor[i,j] = inertia_tensor[j,i] = - np.sum(masses * vertices[:, i]*vertices[:, j])
    return inertia_tensor




def simplex_volume(vertices):
    """
    coordinates of vertices
    """
    nsim, nvar = np.shape(vertices)
    
    return abs(np.linalg.det(vertices[1:] - vertices[0])) / np.math.factorial(nvar)



def simplex_barycenter_inertia_tensor(vertices, masses=1):
    """
    Returns the inertia matrix relative to the center of mass
    coordinates of vertices
    """
    nsim, nvar = np.shape(vertices)
    return points_inertia_tensor(vertices, masses) /(nvar+1)/(nvar+2) * simplex_volume(vertices)
    
    
    
def simplex_inertia_tensor(vertices, masses=1):
    """
    coordinates of vertices
    """
    nsim, nvar = np.shape(vertices)
    masses = masses * np.append(np.full(nsim, 1/(nvar+1)/(nvar+2)), (nvar+1)/(nvar+2)) 
    
    barycenter = np.mean(vertices, axis=0)
    # barycenter beztak sepri4te ke každemu řádku tensoru
    #_tensor = points_inertia_tensor(vertices, masses)/(nvar+1) + np.diag(np.square(barycenter))#*(nvar+1))
    _tensor = points_inertia_tensor(np.vstack((vertices, barycenter)), masses=masses)
    #return _tensor / (nvar+2) * simplex_volume(vertices)
    return _tensor * simplex_volume(vertices)
    
    
# don't ask me what is it
def simplex_covariance_matrix(vertices, weights=1):
    """
    coordinates of vertices
    """
    nsim, nvar = np.shape(vertices)
    
    # normalizace
    weights = weights / np.mean(weights)
    
    barycenter = np.mean((vertices.T*weights).T, axis=0)
    vertices = vertices - barycenter
    
    covariance_matrix = np.empty((nvar, nvar))
    for i in range(nvar):
        for j in range(i + 1):
            if i==j:
                covariance_matrix[i,j] = np.sum(weights * np.square(vertices[:, i]))
            else:
                covariance_matrix[i,j] = covariance_matrix[j,i] = np.sum(weights * vertices[:, i]*vertices[:, j])
                
    # divide by nsim from variance formule, do we need it?
    # divide by /(nvar+1)/(nvar+2) from simplex inertia tensor solution
    # same as simplex_volume, but it looks like it shouldn't be here
    return covariance_matrix /(nvar+1)/(nvar+2) #* simplex_volume(vertices) 
    
