#!/usr/bin/env python
# coding: utf-8

"""

Zde leží DiceBox (tuším, bude jeden)
DiceBox pěčlivě ukladá věškerá data,
věškeré sady vzorků, průběžné odhady a tak.
Nejsem už jistý, zda DiceBox je šťastný nazev, neboť
teďkom je to spíše jen krabička pro krámy
"""


import numpy as np
from scipy import spatial
from scipy import stats
import pickle
from .. import IS_stat
from ..candybox import CandyBox
from scipy import optimize # for BlackSimpleX


from ..samplebox import SampleBox # for candidates packing
from ..ghull import Ghull
from .. import simplex as sx
from .. import convex_hull as khull
from .. import lukiskon as lk
from .. import reader # for Goal
from .. import estimation as stm # for KechatoLukiskon
import collections #E for Counter in MinEnergyCensoredSampling





# considering to rewrite it with pandas
class GuessBox:
    """
    Je tu vynalezaní kola, ale aspoň tak
    Odhady můžou tvořít strašnej bordel a proto jsou
    ukladany do slovníku.
    Tak ale jej nemůžu furt ukladat,
    proto to robim s určitým krokem
    Na konci je třeba zabalit tuhle krabičku ručně!
    """
    def __init__(gb, filename='', flush=100):
        """
        .counter - kdy bylo poslední ukladaní
        """
        gb.estimations = dict()
        gb.filename = filename
        gb.counter = 0
        gb.flush = flush
        gb.pick()
            
    def __repr__(self):
        return "%s(%r, %s)"%(self.__class__.__name__, self.filename, self.flush)
        
    def __str__(gb):
        return str(gb.estimations)
        
    def __len__(gb):
        return len(gb.estimations)
    
    def __getitem__(gb, slice):
        return gb.estimations[slice]
                
    def guess(gb, index, nsim, estimation):
        if index in gb.estimations:
            gb.estimations[index][0].append(nsim)
            gb.estimations[index][1].append(estimation)
        else:
            gb.estimations[index] = [[nsim], [estimation]]
        
        gb.counter+= 1
        if gb.filename and gb.counter > gb.flush:
            gb.put()
        
    def pick(gb):
        if gb.filename:
            try:
                with open(gb.filename + '.pickle', 'rb') as f:
                    gb.estimations = pickle.load(f)
            except:
                # škoda, no
                print("GuessBox: Já tu vaši odhady %s.pickle nevidím" % gb.filename)
        else:
            print('GuessBox is in air mode')
                
    def put(gb):
        if gb.filename:
            try:
                with open(gb.filename + '.pickle', 'wb') as f:
                    pickle.dump(gb.estimations, f)
                gb.counter = 0
            except:
                # nefrčí...
                print("GuessBox: Can not write %s.pickle" % gb.filename)
        else:
            print('GuessBox is in air mode')



#ё нам позарез нужен ещё один, свой собственный словник 
#č jako sůl potřebujeme ještě jeden svůj vlastní slovník
class CacheDict(dict):
    def __init__(self, potential):
        super().__init__()
        self.potential = potential
        self.cache = dict()
        
        
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        
        bids = getattr(value, self.potential)
        if len(bids):
            bid = np.nanmax(bids)
        else:
            bid = 0
        #print("Cache", key, bid)
        self.cache[key] = bid
        
    def __delitem__(self, key):
        super().__delitem__(key)
        
        #print("throw away", key)
        self.cache.__delitem__(key)
    
    def pop(self, *args):
        
        #print("throw away", args[0])
        self.cache.pop(*args)
        
        return super().pop(*args)
        
        


#оӵ дӥсё 
class DiceBox:
    #č kruci, totálně v tohlenstom ztracím
    """
    DiceBox
    Public methods:
        __init__():
            regen():
                _LHS_regen()
            
        add_sample(): 
            increment():
                _LHS_increment()
        
        __call__(): 
            LHS_like_correction()
    
    Public attributes:
        estimations
        guessbox
    """
    def __init__(bx, sample_box):
        bx.sample_box = sample_box
        
        # user candidates 
        #ё шоб было
        bx.candidates = CandyBox(bx.f_model())
        
        # nové uložiště odhadů zadám explicitně, aby se pak
        # odhady v stm kodu přířazovaly správné krabičce
        bx.estimations = []
        # má bejt GuessBox součástí DiceBoxu?
        try:
            bx.guessbox = GuessBox(sample_box.filename, flush=20)
        except:
            bx.guessbox = GuessBox("", flush=20)
        bx.regen()
        
    def __repr__(bx):
        return "%s(%s)"%('DiceBox', repr(bx.sample_box))
        
    def __str__(bx):
        return str('DiceBox ' + bx.sample_box)
        
    def __len__(bx):
        return bx.sample_box.nsim
        
    def __call__(bx):
        """
        Offer next sample
        """
        # I do not see nothing illegal here
        # LHS_like_correction do right conversion
        return bx.LHS_like_correction(bx.f_model(1))
    
    def __getitem__(bx, slice):
        # stačí vratit sample_box
        return bx.sample_box[slice]
    
    def __getattr__(dx, attr):
        if attr == 'dicebox':
            return dx
            
        # branime sa rekurzii
        # defend against recursion
        # рекурсилы пезьдэт!
        if attr == 'sample_box':
            raise AttributeError
                
        # По всем вопросам обращайтесь 
        # на нашу горячую линию    
        else:
            return getattr(dx.sample_box, attr)
    
        
    # přidávání vzorků musí bejt explicitní!
    def add_sample(bx, input_sample):
        bx._logger(msg="we have got new data:", data=input_sample)
        bx.sample_box.add_sample(input_sample)
        bx.increment(bx.sample_box[bx._nsim:])
        bx._nsim = bx.nsim
    
    def increment(bx, input_sample):
        bx._LHS_increment(input_sample)
    
    def regen(bx):
        #ё шайтан регенираци лэзьиз
        bx._logger(msg='regeneration started')
        bx._LHS_regen()
        bx._nsim = bx.nsim
        
    def _LHS_regen(bx):
        # pro LHS_like_correction
        bx.sorted_plan_U = [i for i in range(bx.nvar)] # just create list
        for i in range(bx.nvar):
            bx.sorted_plan_U[i] = np.concatenate(([0], np.sort(bx.sampled_plan.U[:, i]), [1]))
            
    # LHS_style correction  
    def LHS_like_correction(bx, input_sample):
        """
        returns sample object (f_model)
        """
        # what is input?
        # as we need transformation anyway,
        # I'll ask for conversion to f sample
        #ё Здесь вижу железную конвертацию до f-ка,
        #ё которая пройдёт по R координатам
        #č Kruci drát, tady by se nemohlo nic posrat
        to_sample_node = bx.f_model.new_sample(input_sample)
        
        LHS_node = np.empty(bx.nvar, dtype=float)
        for i in range(bx.nvar):
            if to_sample_node.U.reshape(-1)[i] <= bx.sorted_plan_U[i][0]:
                LHS_node[i] = (bx.sorted_plan_U[i][0] + bx.sorted_plan_U[i][1]) / 2
            elif to_sample_node.U.reshape(-1)[i] >= bx.sorted_plan_U[i][-1]:
                LHS_node[i] = (bx.sorted_plan_U[i][-2] + bx.sorted_plan_U[i][-1]) / 2
            else:
                plan_index = np.searchsorted(bx.sorted_plan_U[i], to_sample_node.U.reshape(-1)[i])
                # vzdy
                LHS_node[i] = (bx.sorted_plan_U[i][plan_index] + bx.sorted_plan_U[i][plan_index - 1]) / 2
                 
        return bx.f_model.new_sample(LHS_node, 'U')
        
        
    def _LHS_increment(bx, input_sample):
        for i in range(bx.nvar):
            for j in range(len(input_sample)):
                plan_index = np.searchsorted(bx.sorted_plan_U[i], input_sample.U[j,i])
                bx.sorted_plan_U[i] = np.insert(bx.sorted_plan_U[i], plan_index, input_sample.U[j,i])
    
        
        # The DiceBox Observer 
    def _logger(self, *args, msg="", indent=0, **kwargs):
        if not kwargs:
            kwargs = "" #č ať se nám prázdné závorky nezobrazujou
        print(self.__class__.__name__ + ":", msg, *args, kwargs) 
        
        
        # inspired by Qt
    def connect(self, slot): self._logger = slot
    def disconnect(self): del(self._logger)
    
    
    # kdyby něco
    # callback = lambda *_, **__: None
    
    
    
    
    
            
            

# MinEnergyCensoredSampling
#č Pokud nepletu, hlavní pointa třídy byla v použití konvexní obálky
#č místo triangulaci pro zjíštění inside-outside. 
#č Tohle brutálně všechno zrychlilo, proto se třída dostala název Chrt.
class Chrt(DiceBox):
    """
    Chrt
    methods:
        *__init__():
            DiceBox.__init__():
                *regen():
                    >_LHS_regen()
                    _regen_outside():
                        estimate_outside():
                            assess_candidates:
                                _nominate
                    _regen_inside():
                        get_events
                        estimate_simplex(simplex)
                            _former_candidates_recovering
                            assess_candidates
            
        >add_sample(): 
            *increment():
                _LHS_increment()
                export_estimation()            
                _handle_changed_triangulation(input_sample):
                    get_events()
                    estimate_simplex(simplex):
                        _former_candidates_recovering
                        assess_candidates
                    _invalidate_simplex(simplex)
                    
                _handle_changed_outside(input_sample)
                    estimate_outside():
                        assess_candidates:
                            _nominate
                    
                _handle_candidates()
                    _judge_unjudged
                        assess_candidates:
                            _nominate
                    assess_candidates:
                        _nominate
                    
                *regen()
        
        *__call__(): 
            >LHS_like_correction()
    
        get_pf_estimation()
        
        export_estimation():
            get_pf_estimation()
    """
    #č už mě to dědění nebaví
    #ё без поллитры было не разобраться, что этот слоёный пирог делал
    def __init__(bx, sample_object, tri_space='Rn', tree_space=None,\
                 sampling_space=None, kechato_space='U', potential='psee',\
                  p_norm=2, budget=1000, simplex_budget=100, q=0.5,\
                  LHS_correction=False, design=None):
        
        
        bx.tri_space = tri_space
        if tree_space is None:
            bx.tree_space = tri_space
        else:
            bx.tree_space = tree_space
            
        if sampling_space is None:
            bx.sampling_space = tri_space
        else:
            bx.sampling_space = sampling_space
            
        
        bx.kechato_space = kechato_space
        bx.budget = budget
        bx.simplex_budget = simplex_budget
        bx.p_norm = p_norm
        bx.q = q
        bx.potential = potential
        bx.LHS_correction = LHS_correction
        bx.design = design
        
        # for current candidates
        # kandidaty musí být 'judged' a 'assessed'
        # viz. regen()
        #bx.candidates_index = dict()
        # krám, přece třidíme odpad!
        bx.former_candidates = []
        bx.unjudged_candidates = []
        
        super().__init__(sample_object)
        
        
    def init_parameters(bx):
        """
        Returns dictionary of parameters the DiceBox was initialized with
        """
        return {'sample_object':bx.sample_box, \
                 'tri_space':bx.tri_space, 'tree_space':bx.tree_space,\
                 'sampling_space':bx.sampling_space, 'kechato_space':bx.kechato_space,\
                 'potential':bx.potential, 'p_norm':bx.p_norm, 'budget':bx.budget,\
                 'simplex_budget':bx.simplex_budget, \
                 'LHS_correction':bx.LHS_correction, 'design':str(bx.design)}
        
        
    def __repr__(bx):
        return "%s(**%s)"%(bx.__class__.__name__,  repr(bx.init_parameters()))
        
    def __str__(bx):
        return "%s(%s)"%(bx.__class__.__name__,  str(bx.init_parameters()))
        
    
    def get_events(bx, simplices=None):
        """
        Metoda musí simplexům přiřazovat jev 
        0=success, 1=failure, 2=mix
        """
        if simplices is None:
            simplices = bx.tri.simplices
        
        in_failure = np.isin(simplices, bx.failure_points)
        has_failure = in_failure.any(axis=1)
        all_failure = in_failure.all(axis=1)
        return np.int8(np.where(has_failure, np.where(all_failure, 1, 2), 0))
        
        
        
    def regen(bx):
        """
        regen() recreates data structures of the box. 
        It shouldn't be called without reason, changed distribution, settings or so.
        """
        
        #оӵ шайтан регенираци лэзьиз
        bx._logger(msg='regeneration started')
        bx._LHS_regen()
        
        # kind of interface to CandidatesWidget
        bx.candidates_index = CacheDict(bx.potential)
        
        if bx.nsim > 0:
            # needed for potential calculation
            sampled_plan_tree = getattr(bx.sample_box, bx.tree_space)
            bx.tree = spatial.cKDTree(sampled_plan_tree)
            bx.highest_bid = 0 
        
        bx._regen_outside()
        bx._regen_inside()
        bx._nsim = bx.nsim
                
                
    def _regen_outside(bx):
        if bx.nsim >= bx.nvar + 1:
            try:
                bx.shull = sx.Shull(bx.f_model, bx.tri_space, bx.sampling_space,\
                             powerset_correction=True, design=bx.design)
                bx.siss = bx.shull.oiss
                bx.convex_hull = bx.shull.convex_hull # for gl_plot
                bx.estimate_outside()
                #č a máme hotovo
                return # Ok, go away
            except BaseException as e:
                # I suppose ConvexHull to be much more stable 
                # (if compare with Delaunay triangulation).
                # Hope no issues "we have triangulation, but not the hull" will occur here
                msg = "error of creating ConvexHull "
                error_msg = bx.__class__.__name__ + ": " + msg + repr(e)
                bx._logger(msg=error_msg)
            
        # nothing happened? We are still here? 
        # we need to generate at least something
        if bx.nsim > 0: #č požaduji, aby nějaké těčíčky byly vždy pritomné
            if bx.design is None:
                nodes = bx.f_model(bx.budget)
            else: 
                nodes = bx.f_model.new_sample(bx.design(bx.budget, bx.nvar), 'U')
            #č současný CandyBox odmítne vytvořit neprazdný object bez atributů
            candidates = CandyBox(nodes, event_id=np.full(bx.budget, -1, dtype=np.int8))
            bx.assess_candidates(candidates)
            #č uložíme
            bx.candidates_index[-1] = candidates  
        
            
    def _regen_inside(bx):
        #оӵ кылсузъет кылдытом
        bx.simplex_stats = dict()
        # create .tri triangulation
        if bx.nsim > bx.nvar + 1: # incremental triangulation require one more point
            try:
                
                #č tri - Deloneho triangulace
                tri_plan = getattr(bx.sampled_plan, bx.tri_space)
                bx.tri = spatial.Delaunay(tri_plan, incremental=True)
                if len(bx.tri.coplanar):
                    #print('triangulace v pořádku není')
                    bx._logger(msg='triangulation is coplanar')
                else:
                    #print('triangulace je v pořádku')
                    bx._logger(msg='triangulation is OK')
                    
                #č vyhodil jsem simplex_id'y
                bx.simplex_events = bx.get_events()
                #č ty množiny jsou tak trošku overkill, ale budiž
                bx.simplices_set = set()
                for simplex in bx.tri.simplices:
                    # zde jen počítame
                    bx.estimate_simplex(simplex)       
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
    
    
    
        
        #č beží 99% času
    def increment(bx, input_sample):
        #ё ну нахрен это ваше наследование-расследование
        
        #č nechť bude, asi nikomu nevadí
        bx._LHS_increment(input_sample)
        
        #č strom posuneme sem    
        # cKDTree is used for potential calculation
        # we need everytime regenerate it
        sampled_plan_tree = getattr(bx.sample_box, bx.tree_space)
        bx.tree = spatial.cKDTree(sampled_plan_tree)
        bx.highest_bid = 0 
        
        #č fór je v tom, že tu triangulaci nemůžeme výtvořit hned na začátku
        #č a ConvexHull taky ne
        #č tri - Deloneho triangulace
        if ("tri" in dir(bx)) and ("shull" in dir(bx)):
            bx.export_estimation()            
            bx._handle_changed_triangulation(input_sample)            
            bx._handle_changed_outside(input_sample)
            bx._handle_candidates()
        else:
            bx._logger('Triangulace (zatím?) neexistuje')
            bx.regen()
            
        
        
        #č tato funkce běží 91% času
        # bottleneck function
    def _handle_changed_triangulation(bx, input_sample):
        """
        Triangulace zajistěně existuje
        """
        
        former_simplices = bx.tri.simplices
        
        #č sample je jíž převeden na f (v .add_sample()), takže je to bezpěčný
        bx.tri.add_points(getattr(input_sample, bx.tri_space))
        bx.simplex_events = bx.get_events()
        # print('increment se podaril')
        if len(bx.tri.coplanar): # pokud triangulace není v pořadku
            #print('triangulace v pořádku není')
            bx._logger(msg='triangulation has coplanar points', coplanar=bx.tri.coplanar)
            
        
        # zkontrolujeme co se změnilo
        # předpokladám, že se počet simplexů přidaním bodů nezměnší 
        equal_mask = former_simplices == bx.tri.simplices[:len(former_simplices)]
        
        
        #č zde spolehám na to, že pořadí indexů se nikdy nezmění
        #č (dá se něco takovýho očekavát podle toho co jsem čet v dokumentaci)
        
        #č u těch přečíslovaných zkolntrolujeme, zda fakt v té triangulaci nejsou 
        for simplex in former_simplices[~equal_mask.all(axis=1)]:
            #č když tam je
            #č každopadně tohle je rychlejší než přepočet spousty simplexů
            #isin = np.any(np.all(np.isin(bx.tri.simplices, simplex),axis=1))
            # few times faster
            isin = (bx.tri.simplices == simplex).all(axis=1).any()
            if not isin:
                bx._invalidate_simplex(simplex)
                
        
            
        # změněné simplexy přepočítáme
        for simplex in bx.tri.simplices[:len(former_simplices)][~equal_mask.all(axis=1)]:
            #č ty množiny jsou tak trošku overkill, ale budiž
            if tuple(simplex) not in bx.simplices_set:
                bx.estimate_simplex(simplex)    
            
            
        # teď nové simplexy
        # simplexy свежего разлива
        for simplex in bx.tri.simplices[len(former_simplices):]:
            #č ty množiny jsou tak trošku overkill, ale budiž
            if tuple(simplex) not in bx.simplices_set:
                bx.estimate_simplex(simplex) 
            
                
                
                
    def _handle_changed_outside(bx, input_sample):
        """
        Triangulace a ConvexHull zajistěně existujou
        """
        # sample je jíž převeden na f (v .add_sample()), takže je to bezpěčný
        bx.shull.increment(input_sample)
        # handle changed outside
        #č přepočíst -1 v zavislosti na simplexu vstupního bodu
        try:
            #č kontrola korrektní i v případě NaN
            test = input_sample.event_id > -1
            #оӵ эскером
            if not test.all():
                bx.former_candidates.append(bx.candidates_index.pop(-1))
                bx.estimate_outside()
        except BaseException as e:
            msg = "input sample didn't provide correct 'event_id' attribute "
            error_msg = bx.__class__.__name__ + ": " + msg + repr(e)
            bx._logger(msg=error_msg)
            bx.former_candidates.append(bx.candidates_index.pop(-1))
            bx.estimate_outside()
    
    
    
    
    def _handle_candidates(bx):
        #č prohrabeme odpad
        bx._judge_unjudged(bx.unjudged_candidates)
        bx._judge_unjudged(bx.former_candidates)
        
        #č A ještě... AUKCE, AUCTION    
        # Election - selection
        for candidates in bx.candidates_index.values():
            bids = getattr(candidates, bx.potential)
            if len(bids):
                bid = np.nanmax(bids)
                # side effect
                if bid > bx.highest_bid:
                    #č pokud neprovadíme optimalizaci v simplexech
                    #č tak nám stačí jednoduše assessovat
                    bx.assess_candidates(candidates) 
                
        # probably, we shouldn't purge user candidates (if they are)
        # just every time evaluate them
        if len(bx.candidates) > 0:
            bx.judge_candidates(bx.candidates)
            bx.assess_candidates(bx.candidates)
                    
                    
    def _nominate(bx, candidates):
        """
        function should be only runned by .assess_candidates()
        """
        bids = getattr(candidates, bx.potential)
        # -1 = 'out', 0=success, 1=failure, 2=mix
        #č -1 a 2 jsou samozrejmě disjunktní
        bids *= (candidates.event_id == -1) + (candidates.event_id == 2)
        if len(bids):
            bid = np.nanmax(bids)
            # side effect
            if bid > bx.highest_bid:
                # já prečo spoléhám na ksee a psee potenciály
                # v tom, že nepřířadí vysoký potenciál 
                # vzorkům s nulovou hustotou
                bx.bidder = candidates[np.nanargmax(bids)]
                bx.highest_bid = bid
                
        
    def is_mixed(bx, simplices=None):
        """
        Metoda musí simplexům přiřazovat jev 
        0=success, 1=failure, 2=mix
        """
        if simplices is None:
            simplices = bx.tri.simplices
        
        in_failure = np.isin(simplices, bx.failure_points)
        has_failure = in_failure.any(axis=1)
        all_failure = in_failure.all(axis=1)
        return np.logical_xor(has_failure, all_failure)
            
            
    def __call__(bx):
        bx._logger(msg="we were asked for an recommendation")
        
        if bx.nsim < 1: # je to legální
            bx._logger(msg="median first!")
            node = bx.LHS_like_correction(bx.f_model(1))
            return CandyBox(node, event_id=np.full(1, -1, dtype=np.int8))
        else:
            selected = bx.bidder
            if bx.LHS_correction:
                #č hrubě ošidíme s takovejhlema usilima námi pěčlivě vybraný vzorečiček
                selected.sampling_plan = bx.LHS_like_correction(selected)
            return selected
           
    
    
    
    def estimate_outside(bx):
        # předpokládám, že convex_hull jíž existuje
        
        # get candidates!
        #č explicitně (pokažde) počtem teček zadavám přesnost integrace
        #č takže změny bx.budget budou při dálším spuštění aplikovány
        candidates = bx.shull.integrate(bx.budget) 
        candidates = candidates[candidates.is_outside]
        
        #č vyhodnotíme
        bx.assess_candidates(candidates)
        #č vzorky je třeba přidát ke kandidatům
        #č jako, nic nepokazí, ale čo tam připadně bylo - přepíše
        # -1 = 'outside', 0=success, 1=failure, 2=mix
        bx.candidates_index[-1] = candidates
            
    
    
    
    
        # potřebuju nová slovesa
    #ё пранк вышел из под контроля
    #č jako, byl to takovej vtipeček označit potenciál dvojitým e
    #č stala se z toho ale konvence, ne že by všal byla ničím nepodložena
    #č algorithmus se sestavá ze dvou částí: 
    #č tri - triangulace, 
    #č tree - stromovej cKDTree scipy algorithmus, který hledá nejblížší body
    #č (nechám bokem otázku, že ten asi hned na začátku nepřepiná do banalního brute force)
    #č Každopadně, davá smysl, že psee, chee atd. potenciály spadají do tree části.
    def assess_candidates(bx, candidates):
        #č nikdo to nepouživá, ale se mi nějaký takový parameter libí.
        candidates.nsim_stamp = np.full(len(candidates), bx.nsim)
    
        candidates_tree = getattr(candidates, bx.tree_space)
        dd, ii = bx.tree.query(candidates_tree, k=1, p=bx.p_norm)
        
        # from scipy documentation:
        # [dd] Missing neighbors are indicated with infinite distances.
        # [ii] Missing neighbors are indicated with self.n
        
        #č mǐ radši budeme předpokladat nulovou vzdálenost a třeba nulového souseda
        #č ne, radší posledného souseda
        #č pokud ten chytrej strom si myslí, že nějaký kandidat nemá spolubydlu
        mask = ii == bx.nsim
        if np.any(mask): #č ať mě to neznervozňuje
            ii[mask] = bx.nsim - 1
            dd[mask] = 0
            bx._logger(msg="cKDTree zlobí", orphan_candidates=candidates[mask], P=candidates[mask].P)
            
        # the most agressive potential ever
        candidates.dd = dd
        
        if bx.potential in ('psee', 'fee', 'fee2'):
            #оӵ кучапи
            #č pejskovej potenciál
            #č psí-kučapí není invariántní vůči lineárním transformácím
            
            PDFs = bx.sample_box.pdf(bx.tree_space)
            # teď máme hustoty kandidatů a prislušejicích jím vzorků
            PDF = PDFs[ii]
            pdf = candidates.pdf(bx.tree_space)
            
            tree_Pdf_mean = (pdf+PDF)/2
            tree_Pdf_gmean = np.sqrt(pdf*PDF)
            volume = np.power(dd, bx.nvar)
            candidates.psee = tree_Pdf_gmean * volume
            candidates.fee =  tree_Pdf_mean * volume * np.power(pdf/PDF, 1/(bx.nvar+1))
            candidates.fee2 = tree_Pdf_mean * volume * np.power(pdf/PDF, 1/(bx.nvar*2))
        
        elif bx.potential == 'ksee': # ksee 
            #оӵ кечато
            #č koťatko-káčátkovej potenciál
            #č ksí-kěčató není invariántní vůčí rotacím
            ksee = np.empty(len(candidates))
            for i in np.unique(ii):
                # doufám, že je to legální
                ksee[i==ii] = lk.kechato_potential(bx.f_model[i], candidates[i==ii], kechato_space=bx.kechato_space)
            candidates.ksee = ksee
            
        elif bx.potential == 'q_psee': #č kup si
            #оӵ кучапи
            #č pejskovej potenciál
            #č psí-kučapí není invariántní vůči lineárním transformácím
            
            PDFs = bx.sample_box.pdf(bx.tree_space)
            # teď máme hustoty kandidatů a prislušejicích jím vzorků
            PDF = PDFs[ii]
            pdf = candidates.pdf(bx.tree_space)
            
            volume = np.power(dd, bx.nvar)
            candidates.psee = np.sqrt(pdf*PDF) * volume
            candidates.q_psee = pdf**bx.q * PDF**(1-bx.q) * volume
        
        
        elif bx.potential in ('chee', 'chee2'):
            PDFs = bx.sample_box.pdf(bx.tree_space)
            # teď máme hustoty kandidatů a prislušejicích jím vzorků
            PDF = PDFs[ii]
            candidates.PDF = PDF 
            pdf = candidates.pdf(bx.tree_space)
            candidates.Pdf = pdf #č pdf() je funkce f_modelu
            
            
            tree_Pdf_gmean = np.sqrt(pdf*PDF)
            volume = np.power(dd, bx.nvar)
            candidates.psee = tree_Pdf_gmean * volume
            
            sum_squares = np.sqrt(np.sum(np.square(candidates.G), axis=1))
            chi2 = stats.chi2.pdf(sum_squares, bx.nvar)
            candidates.chi2 = chi2
            candidates.chee2 = np.sqrt(chi2*PDF) * volume
        
            r = np.sqrt(sum_squares)
            candidates.r = r
            chi = stats.chi.pdf(r, bx.nvar)
            candidates.chi = chi
            candidates.chee = np.sqrt(chi*PDF) * volume
            
            
        
        # prepare to elections
        bx._nominate(candidates)
        
        
    def _judge_unjudged(bx, list):
        for i in range(len(list)):
            candidates = list.pop()
            bx.shull.is_outside(candidates)
            
            mask = candidates.is_outside
            if np.any(mask): #č pokud aspoň jeden bydlí mimo Brno
                candidates = candidates[mask]
                #č shull event_id přiřadí
                #candidates.event_id = np.full(len(candidates), -1, dtype=np.int8)
                #č vyhodnotíme
                bx.assess_candidates(candidates)
                #č půlku prýč
                bids = getattr(candidates, bx.potential)
                mask = np.isfinite(bids)
                if np.any(mask): #č hmm... 
                    candidates = candidates[mask]
                    bids = bids[mask]
                    median = np.median(bids, overwrite_input=False)#č bojím sa
                    candidates = candidates[bids > median]
                    #č vzorky je třeba přidát ke kandidatům
                    bx.candidates_index[-1].add_sample(candidates)    
    
    
    # ještě by asi hodily funkce pro pridaní uživatelských kandidatů
    # funkce, která přídává dálší kandidaty? outside sampling
    
    
    def get_pf_estimation(bx):
        # TRI-compatible estimation
        # -1=outside, 0=success, 1=failure, 2=mix
        #č dostaneme vyrovnané odhady Brna-města (-2) a Brna-venkova (-1)
        tri_estimation = dict()
        tri_estimation[-1] = bx.siss.estimations[-1]
        
        # set initial values
        tri_estimation[0] = 0
        tri_estimation[1] = 0
        tri_estimation[2] = 0
        
        #č něco konkretnějšího
        vertex_estimation = 0
        weighted_vertex_estimation = 0
        
        pf_inside = bx.siss.estimations[-2]
        if "tri" in dir(bx):
            # let's iterate over all simplices we have
            # (calling code is responsible for the .simplex_stats validity)
            for event_id, simplex_measure, fm, wfm in bx.simplex_stats.values():
                tri_estimation[event_id] += simplex_measure
                vertex_estimation += fm
                weighted_vertex_estimation += wfm
            
            #č success klidně může být i záporným
            tri_estimation[0] = pf_inside - tri_estimation[1] - tri_estimation[2]
            
        elif np.all(bx.failsi[:len(bx.convex_hull.points)]):
            #č veškerej vnitršek je v poruše
            tri_estimation[1] = pf_inside
            vertex_estimation = pf_inside
            weighted_vertex_estimation = pf_inside
        else:
            #č vnitršek je asi v pořadku
            tri_estimation[0] = pf_inside
        
        return {'TRI_overall_estimations': tri_estimation, \
            'vertex_estimation' : vertex_estimation, \
            'weighted_vertex_estimation' : weighted_vertex_estimation}
            
            
            
    def export_estimation(bx):
        for key, value in bx.get_pf_estimation().items():
            bx.guessbox.guess(key, len(bx.convex_hull.points), value) #č nebo bx.tri.npoints
        
    
    
    
    #č vyhodil jsem simplex_id'y
    def estimate_simplex(bx, indices):
        
        #č zkusím funkci návrhnout tak, že 
        #ё вызывающая функция запускает estimate_simplex
        #ё на всём подряд без разбору.
        #č Našim úkolem je zjistit co je simplex zač
        #č a ty zelené ignorovat
        
        #č ty množiny jsou tak trošku overkill, ale budiž
        bx.simplices_set.add(tuple(indices))
        
        
        # I'll use tree_space as a weigthing space
        # It could be separeted, but I am a little bit tired
        # from so much different spaces over there
        event, event_id, fr, wfr = sx.get_indices_event(bx, indices, bx.tree_space)
        
        # -1 = 'outside', 0=success, 1=failure, 2=mix
        if event_id != 0:
            #оӵ чылкыт f_model
            #č do sample_simplexu musíme poslat čístý f_model
            # we should send pure f_model to sample_simplex()
            vertices = bx.f_model[indices]
            print("estimate", indices)
            h_plan, convex_hull, simplex_measure = sx.sample_simplex(vertices,\
                        model_space=bx.tri_space, design=bx.design,\
                        sampling_space=bx.sampling_space, nis=bx.simplex_budget)
            
            
            fm = simplex_measure * fr
            wfm = simplex_measure * wfr
            
            #č ISSI tu nemáme, místo toho prostě ukladáme co máme do slovníku
            bx.simplex_stats[tuple(indices)] = (event_id, simplex_measure, fm, wfm)
            
            mask = ~h_plan.is_outside
            if event == 'mix':
                
                candidates = h_plan[mask]
                #bx._former_candidates_recovering(candidates, convex_hull, bx.unjudged_candidates)
                bx._former_candidates_recovering(candidates, convex_hull, \
                                                    bx.former_candidates)
                
                candidates.event_id = np.full(len(candidates), event_id, dtype=np.int8)
                #candidates.simplex = np.full((len(candidates), bx.nvar+1), indices)
                
                #č vyhodnotíme je
                bx.assess_candidates(candidates)
                
                #č vzorky je třeba přidát ke kandidatům
                #č jako, nic nepokazí, ale čo tam připadně bylo - přepíše
                bx.candidates_index[tuple(indices)] = candidates
        
        
            #č vzorky je třeba přidát ke kandidatům
            #č zás nakladaní s odpadem...
            #bx.unjudged_candidates.append(h_plan[~mask])
            #č roušky jsou dráhé
            bx.unjudged_candidates.append(h_plan)


    #č vyhodil jsem simplex_id'y
    def _invalidate_simplex(bx, indices):
        simplex = tuple(indices)
        
        #č ten simplex tam musí být, 
        #č pokud teda bo boxu nikdo nesahá...
        bx.simplices_set.remove(simplex)
        
        if simplex in bx.simplex_stats:
            bx.simplex_stats.pop(simplex)
        
        if simplex in bx.candidates_index:
            bx.former_candidates.append(bx.candidates_index.pop(simplex))
        
        


    def _former_candidates_recovering(bx, actual, convex_hull, former_list):
        #č prohrabeme odpad
        for former in former_list:
            former_tri = getattr(former, bx.tri_space)
            mask = ~sx.is_outside(convex_hull, former_tri)
            
            if np.any(mask): #č pokud aspoň jeden se nám hodí
                #č vzorky je třeba přidát ke kandidatům
                actual.add_sample(former[mask])


    def judge_candidates(bx, candidates):
        """
        Only for user candidates should be used
        """
    
        candidates_tri = getattr(candidates, bx.tri_space)
            
        found_simplices = bx.tri.find_simplex(candidates_tri)
        
        candidates.simplex = found_simplices
        events = found_simplices.copy()
        # black magic
        # zhruba - get_events() vrací pole s odpovidajícími čísly jevů pro každý simplex, počineje od nuly
        # tím slajsingem my jakoby vybirame ke každemu nalezenemu simplexovi ten správnej mu odpovídajicí jev
        events[found_simplices >= 0] = bx.simplex_events[found_simplices[found_simplices >= 0]]
        candidates.event_id = events







#оӵ ӧрӟи
#č RJ
#č Třída nevytvaří triangulaci, dokud nejsou tečky oboje druhů.
#č Jakoby letí nad zemi jako orel (ӧрӟи), nebo jako vlaky RJ jede bez zastavek.
class Erjee(Chrt):
    def _regen_inside(bx):
        failsi = bx.failsi
        if np.any(failsi) and not np.all(failsi):
            #bx._logger(msg="triangulation started")
            super()._regen_inside()
        else:
            #č jíž není nutný
            #bx.simplex_stats = dict() # for .get_pf_estimation()
            bx._logger(msg="triangulation skipped")
    
    def increment(bx, input_sample):
        #ё ну нахрен это ваше наследование-расследование
        
        #č nechť bude, asi nikomu nevadí
        bx._LHS_increment(input_sample)
        
        #č strom posuneme sem    
        # cKDTree is used for potential calculation
        # we need everytime regenerate it
        sampled_plan_tree = getattr(bx.sample_box, bx.tree_space)
        bx.tree = spatial.cKDTree(sampled_plan_tree)
        bx.highest_bid = 0 
        
        
        #č fór je v tom, že tu triangulaci nemůžeme výtvořit hned na začátku
        #č a ConvexHull taky ne
        #č tri - Deloneho triangulace
        if ("tri" in dir(bx)) and ("shull" in dir(bx)):
            bx.export_estimation()            
            bx._handle_changed_triangulation(input_sample)            
            bx._handle_changed_outside(input_sample)
            bx._handle_candidates()
        elif "shull" in dir(bx):
            bx.export_estimation() 
            bx._regen_inside()
            bx._handle_changed_outside(input_sample)
            bx._handle_candidates()
        else:
            #bx._logger('Triangulace (zatím?) neexistuje')
            #bx._logger('Konvexnej tvař (zatím?) neexistuje')
            bx._logger("Neither triangulation, neither convex hull does not exist yet")
            bx._regen_outside()
            bx._regen_inside()










# use cubature formulas for simplex integration
class Razitko(Erjee):
    #č už mě to dědění nebaví
    #ё без поллитры было не разобраться, что этот слоёный пирог делал
    def __init__(bx, sample_object, scheme, tri_space='Rn', tree_space=None,\
                 sampling_space=None, kechato_space='U', potential='psee',\
                  p_norm=2, q=0.5, budget=1000, \
                  LHS_correction=False, design=None):
        
        bx.scheme = scheme
        bx.tri_space = tri_space
        if tree_space is None:
            bx.tree_space = tri_space
        else:
            bx.tree_space = tree_space
            
        if sampling_space is None:
            bx.sampling_space = tri_space
        else:
            bx.sampling_space = sampling_space
            
        
        bx.kechato_space = kechato_space
        bx.budget = budget
        bx.p_norm = p_norm
        bx.q = q
        bx.potential = potential
        bx.LHS_correction = LHS_correction
        bx.design = design
        
        # for current candidates
        # kandidaty musí být 'judged' a 'assessed'
        # viz. regen()
        #bx.candidates_index = dict()
        # krám, přece třidíme odpad!
        bx.former_candidates = []
        bx.unjudged_candidates = []
        
        DiceBox.__init__(bx, sample_object)
    
    # přidávání vzorků musí bejt explicitní!
#    def add_sample(bx, input_sample):
#        bx._logger(msg="we have got new data:", data=input_sample)
#        bx.sample_box.add_sample(input_sample)
#        # tohle musí převest rozdělení vstupního vzorku na vlastní rozdělení skříňky
#        #inner_sample = bx.sample_box.new_sample(input_sample)
#        #bx.increment(inner_sample)
        
    def init_parameters(bx):
        """
        Returns dictionary of parameters the DiceBox was initialized with
        """
        return {'sample_object':bx.sample_box, 'scheme':bx.scheme.name,\
                 'tri_space':bx.tri_space, 'tree_space':bx.tree_space,\
                 'sampling_space':bx.sampling_space, 'kechato_space':bx.kechato_space,\
                 'potential':bx.potential, 'p_norm':bx.p_norm, 'budget':bx.budget,\
                 'LHS_correction':bx.LHS_correction, 'design':str(bx.design)}
        
    def _regen_inside(bx):
        failsi = bx.failsi
        if np.any(failsi) and not np.all(failsi):
            #bx._logger(msg="triangulation started")
            bx.__regen_inside()
        else:
            #č jíž není nutný
            #bx.simplex_stats = dict() # for .get_pf_estimation()
            bx._logger(msg="triangulation skipped")
            
    def __regen_inside(bx):
        # create .tri triangulation
        if bx.nsim > bx.nvar + 1: # incremental triangulation require one more point
            try:
                # I'll use tri_space as a weigthing space
                # It could be separeted, but I am a little bit tired
                # from so much different spaces over there
                bx.Tri = sx.FastCubatureTriangulation(bx.samplebox, bx.scheme,\
                         tri_space=bx.tri_space, issi=bx.siss, \
                        weighting_space=bx.tri_space, incremental=True,\
                        on_add_simplex=bx._on_add_simplex,\
                        on_delete_simplex=bx._invalidate_simplex)
                  
                bx.Tri.integrate()
                #č tri - Deloneho triangulace
                bx.tri = bx.Tri.tri #č všichní tam očekávajou QHull
                
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
    
    
        #č tato funkce běží 91% času
        # bottleneck function
    def _handle_changed_triangulation(bx, input_sample):
        """
        Triangulace zajistěně existuje
        """
        bx.Tri.update()
                
    
    def get_pf_estimation(bx):
        #č dle toho, čo vidím v kódu (spouští nás .increment())
        #č přinejmenším konvexní obálka
        #č zajištěně existuje
        if 'tri' in dir(bx):
            estimations = bx.Tri.get_pf_estimation()
            tri_estimation = estimations.pop('TRI_estimation')
            estimations['TRI_overall_estimations'] = tri_estimation
            return estimations
            
        
        #оӵ триангуляци ӧвӧл, иськем...
        #č dostaneme vyrovnané odhady Brna-města (-2) a Brna-venkova (-1)
        pf_inside = bx.siss.estimations[-2]
        pf_outside = bx.siss.estimations[-1]
        
        if np.all(bx.failsi[:len(bx.convex_hull.points)]):
            #č veškerej vnitršek je v poruše
            # -1=outside, 0=success, 1=failure, 2=mix
            return {'TRI_overall_estimations': {-1:pf_outside, 0:0, 1:pf_inside, 2:0}, \
                    'vertex_estimation' : pf_inside, \
                    'weighted_vertex_estimation' : pf_inside}
            
        else:
            #č vnitršek je asi v pořadku
            # -1=outside, 0=success, 1=failure, 2=mix
            return {'TRI_overall_estimations': {-1:pf_outside, 0:pf_inside, 1:0, 2:0}, \
                    'vertex_estimation' : 0, \
                    'weighted_vertex_estimation' : 0}
            
    
    #č bejvalej .estimate_simplex()
    #č teď je to kolbek, který volá Triangulation
    def _on_add_simplex(bx, box=None, indices=None, simplex=None, nodes=None, cell_stats=None):
        if cell_stats['event'] == 'mix':
            candidates = CandyBox(nodes, event_id=np.full(len(nodes), 2, dtype=np.int8))
            
            #č vyhodnotíme je
            bx.assess_candidates(candidates)
            
            #č vzorky je třeba přidát ke kandidatům
            #č jako, nic nepokazí, ale čo tam připadně bylo - přepíše
            bx.candidates_index[tuple(indices)] = candidates
    
    # callback
    #č sx.on_delete_simplex(indices=indices)
    def _invalidate_simplex(bx, indices):
        simplex = tuple(indices)
        
        if simplex in bx.candidates_index:
            bx.candidates_index.pop(simplex)
        
        
    def export_estimation(bx):
        for key, value in bx.get_pf_estimation().items():
            bx.guessbox.guess(key, len(bx.convex_hull.points), value) #č nebo bx.tri.npoints




#č Teď je třeba vytvoriť novou skříňku, která by místo Shull použivala Ghull.
#č Samozřejmě, že už ani já, ani čert nemůžeme se v tom vyznat
#č Takže radší zdědíme pouze bázový DiceBox

#č Je třeba dávát bacha na odlišnosti v (staré) Triangulation třídě a nové Ghull třídě.
#č Zatímco Triangulation drží starý stáv, dokud .update() není spustěn,
#č Ghull, ale hlavně, odpovídající modely konvexních obálek jíž žádný .update() nemájí,
#č nové tečky uvidí sami dřív než se naše skříňka probere.
#č Takže teď odhady nově budeme ukladať hned pri incrementu.
#č Triangulation používá i jínej kód, samotné třídy beztak zbytečně komplikováné,
#č nechci teď to toho lezt.
class Goal(DiceBox):
    """
    Goal
    methods:
        *__init__():
            DiceBox.__init__():
                Chrt.regen():
                    DiceBox._LHS_regen()
                    _regen_outside():
                        estimate_outside():
                            Chrt.assess_candidates:
                                Chrt._nominate
                    _regen_inside():
                        __regen_inside:
                            **Triangulation magic**:
                                Razitko._on_add_simplex:
                                    Chrt.assess_candidates:
                                        Chrt._nominate
            
        >add_sample(): 
            *increment():
                >_LHS_increment()
                export_estimation()            
                _handle_changed_triangulation(input_sample):
                    get_events()
                    estimate_simplex(simplex):
                        assess_candidates
                    _invalidate_simplex(simplex)
                    
                _handle_changed_outside(input_sample)
                    estimate_outside():
                        assess_candidates:
                            _nominate
                    
                _handle_candidates()
                    assess_candidates:
                        _nominate
                    
                *regen()
        
        Chrt.__call__(): 
            >LHS_like_correction()
    
        get_pf_estimation()
        
        export_estimation():
            get_pf_estimation()
    """
    
    #č praca s kandidatama moc sa nezměnila
    #č funkce assess_candidates přířadí potenciál bodíkům
    #č a zaroveň je nominuje na soutež.
    #č na vstupu assess_candidates musí být CandyBox 
    #č s jíž nastaveným event_id
    assess_candidates = Chrt.assess_candidates
    _nominate = Chrt._nominate
    
    #č explicitně převezmu některé funkce
    #č ať v budoucnu nelamame hlavu, co jestě potřebujeme, co už nikoliv
    __repr__ = Chrt.__repr__
    __str__ = Chrt.__str__
    __call__ = Chrt.__call__
    regen = Chrt.regen
    
    _on_add_simplex = Razitko._on_add_simplex
    _invalidate_simplex = Razitko._invalidate_simplex
    
    
    #č míží nám sampling_space: Ghull umí vzorkovat outside pouze v G prostoru
    #č quadpy umístí integráční bodíky v prostoru triangulace.
    def __init__(bx, sample_object, scheme, tri_space='G', tree_space=None,\
                  kechato_space='U', potential='q_psee', q=0.5,\
                  p_norm=2, shell_budget=1000, outer_budget=100,\
                  LHS_correction=False, stm_filename=None):
        
        bx.scheme = scheme
        bx.tri_space = tri_space
        if tree_space is None:
            bx.tree_space = tri_space
        else:
            bx.tree_space = tree_space
            
        
        bx.kechato_space = kechato_space
        bx.shell_budget = shell_budget
        bx.outer_budget = outer_budget
        bx.p_norm = p_norm
        bx.potential = potential
        bx.q = q # used for q_psee potential only
        bx.LHS_correction = LHS_correction
        
        bx.stm_filename = stm_filename
        
        DiceBox.__init__(bx, sample_object)
    
        
    def init_parameters(bx):
        """
        Returns dictionary of parameters the DiceBox was initialized with
        """
        return {'sample_object':bx.sample_box, 'scheme':bx.scheme.name,\
                 'tri_space':bx.tri_space, 'tree_space':bx.tree_space,\
                 'kechato_space':bx.kechato_space, 'potential':bx.potential,\
                 'p_norm':bx.p_norm, 'shell_budget':bx.shell_budget,\
                 'outer_budget':bx.outer_budget, 'LHS_correction':bx.LHS_correction}
        

                
    def _regen_outside(bx):
        bx.convex_hull = khull.QHull(bx.f_model, space=bx.tri_space) # for gl_plot
        bx.ghull = Ghull(bx.convex_hull)
        bx._R = -1 # update outer under R>_R condition
        bx._afacet = None
        bx._bfacet = np.inf
        #č konečně mám pořádnou stejtful třídu
        #č pokud mám aspoň jednu tečku, tak už je mi šuma
        #č zda se konvexní obálka vytvořila, či nikoliv
        if bx.nsim > 0:
            bx.estimate_outside()
        
            
    def _regen_inside(bx):
        failsi = bx.failsi
        if np.any(failsi) and not np.all(failsi):
            #bx._logger(msg="triangulation started")
            bx.__regen_inside()
        else:
            #č jíž není nutný
            bx._logger(msg="triangulation skipped")
            
    def __regen_inside(bx):
        # create .tri triangulation
        if bx.nsim > bx.nvar + 1: # incremental triangulation require one more point
            try:
                # I'll use tri_space as a weigthing space
                # It could be separeted, but I am a little bit tired
                # from so much different spaces over there
                bx.Tri = sx.JustCubatureTriangulation(bx.samplebox, bx.scheme,\
                         tri_space=bx.tri_space, issi=None, \
                        weighting_space=bx.tri_space, incremental=True,\
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
    
    
        
        #č beží 99% času
    def increment(bx, input_sample):
        #ё ну нахрен это ваше наследование-расследование
        
        #č nechť bude, asi nikomu nevadí
        bx._LHS_increment(input_sample)
        
        #č strom posuneme sem    
        # cKDTree is used for potential calculation
        # we need everytime regenerate it
        sampled_plan_tree = getattr(bx.sample_box, bx.tree_space)
        bx.tree = spatial.cKDTree(sampled_plan_tree)
        bx.highest_bid = 0 
        
        
        #č logika se mění. Konvexní obálku máme vždycky.
        #č jistě, že po incrementu máme alespoň jeden vzorek
        #č takže hned od začátku můžeme trhat odhady
        
        #č tri - Deloneho triangulace
        if "tri" in dir(bx):
            bx._handle_changed_triangulation(input_sample)
        else:
            bx._regen_inside()
            
            
        bx._handle_changed_outside(input_sample)
        bx._handle_candidates()
        
        #č exportovať odhady jistě môžeme
        #č teďkom to děláme hned po přídání vzorků
        bx.export_estimation()
        
        
        #č tato funkce běží 91% času
        # bottleneck function
    def _handle_changed_triangulation(bx, input_sample):
        """
        Triangulace zajistěně existuje
        """
        bx.Tri.update()
            
                
                
                
    def _handle_changed_outside(bx, input_sample):
        try:
            #č kontrola korrektní i v případě NaN
            test = input_sample.event_id > -1
            #оӵ эскером
            if not test.all():
                bx.estimate_outside()
        except BaseException as e:
            msg = "input sample didn't provide correct 'event_id' attribute "
            error_msg = bx.__class__.__name__ + ": " + msg + repr(e)
            bx._logger(msg=error_msg)
            bx.estimate_outside()
    
    
    
    
    def _handle_candidates(bx):
        #č A ještě... AUKCE, AUCTION    
        # Election - selection
        for key, cached_bid in reversed(bx.candidates_index.cache.items()):
            # side effect
            if cached_bid > bx.highest_bid:
                #č pokud neprovadíme optimalizaci v simplexech
                #č tak nám stačí jednoduše assessovat
                bx.assess_candidates(bx.candidates_index[key])
                #č tím se mi aktualizuje cache
                bx.candidates_index[key] = bx.candidates_index[key]
                
        # probably, we shouldn't purge user candidates (if they are)
        # just every time evaluate them
        #č kdyby někdo chtěl mít užovatelské kandidaty...
#        if len(bx.candidates) > 0:
#            bx.judge_candidates(bx.candidates)
#            bx.assess_candidates(bx.candidates)
                    
    
    
    
    def _ghull_outside_callback(bx, outside_nodes):
        #č sice získáme filtrovaný outside, 
        #č musíme sami zabalit bodíky do CandyBoxu
        # -2 = 'inside' -1 = 'outside'
        event_ids = np.full(len(outside_nodes), -1, dtype=np.int8)
        candidates = CandyBox(outside_nodes, event_id=event_ids)
        bx.assess_candidates(candidates)
        
        bids = getattr(candidates, bx.potential)
        #č nie třeba kontrolovat jevy, tam je pouze outside
        #bids *= (candidates.event_id == -1) + (candidates.event_id == 2)
        bid = np.nanmax(bids)
        if bid > bx._highest_outside:
            #č uložíme varku bodíku pouze když 
            #č majú větší potenciál, 
            bx._highest_outside = bid
            #č čo tam připadně bylo - přepíšeme
            #č uložíme s indexem dle ghull_estimation:
            # -22: inner, -21: shell inside, -12: shell outside, -11: outer
            bx.candidates_index[-12] = candidates
        
    
    def estimate_outside(bx):
        #č konečně mám pořádnou stejtful třídu
        #č pokud mám aspoň jednu tečku, tak už je mi šuma
        #č zda se konvexní obálka vytvořila, či nikoliv
        
        #č Máme 2 úkoly: 
        #č 1. Získat odhady a uložit je, abychom nemuseli opakovaně integrovat,
        #č    dokud se neobjeví nějaký nový vzorek zvenku.
        #č 2. Získat kandidaty.
        #č    a. z mezíkruží (-12)
        #č    b. fire, to co navrhne QHull (-1)
        #č    c. boom, doporuření QHull můžou i zklamat (-11)
        #č    cc. ze vdálenejších galaxí (-111)
        
        #č prace s tečkami v mezikruži se změnila
        #č teď tečky dostávám přes kolbek po částech
        #č a není předem známo, kolik těch částí bude.
        #č Na začátku radší, pro jistotu, 
        #č vyhodíme stare bodíky z mezikruži (-12)
        bx.candidates_index.pop(-12, "Nejsou? Nevadí...") # "Ӧвӧл-а мар-а?"
        bx._highest_outside = 0
        
        # get candidates!
        #č explicitně (pokažde) počtem teček zadavám přesnost integrace
        #č takže změny bx.shell_budget budou při dálším spuštění aplikovány
        data = bx.ghull.integrate(bx.shell_budget, \
                                callback_outside=bx._ghull_outside_callback) 
        ghull_estimation, convex_hull_estimation, global_stats = data
        #č uložíme. Не жалко.
        #č první úkol máme splněný
        bx.ghull_estimation = ghull_estimation
        bx.convex_hull_estimation = convex_hull_estimation
        bx.global_stats = global_stats
        bx._logger(msg="outside estimation:", ghull_stats=global_stats)
        
        
        
        #č zde už nám jde pouze o kandidaty
        
        # fire
        bx._fire()
        # boom
        
        if global_stats['R'] > bx._R:
            #č Projedeme Moravou
            nodes = bx.ghull.boom(bx.outer_budget, use_MC=True)
            #č tyhle funkce už vracej pouhý f_model
            event_id = np.full(bx.outer_budget, -1, dtype=np.int8)
            candidates = CandyBox(nodes, event_id=event_id)
            bx.assess_candidates(candidates) # nic nevrácí, to je procedura
            bx.candidates_index[-11] = candidates
            
            #č Už máte Mléčnou dráhu projdutou?
            nodes = bx.ghull.boom(bx.outer_budget, use_MC=False)
            #č tyhle funkce už vracej pouhý f_model
            event_id = np.full(bx.outer_budget, -1, dtype=np.int8)
            candidates = CandyBox(nodes, event_id=event_id)
            bx.assess_candidates(candidates) # nic nevrácí, to je procedura
            bx.candidates_index[-111] = candidates
            
            bx._R = global_stats['R']
            bx._logger(msg='boom!', _R=bx._R)
        #č to je vše. Nic nevrácíme
    
    def _fire(bx):
        qhull = bx.ghull.hull
        if bx._afacet is None:
            bx.__fire()
        
        #č podle mě sem nemusí dojít, 
        #č dokud se konvexní obálka ve skutku nevytvoří
        #č b-čko u QHull pro nás má jakoby záporné vzdálenosti
        elif np.all(bx._bfacet > qhull.b):
            #č jasně, že musíme zapalit
            bx.__fire()
        elif np.any(bx._afacet != qhull.A[np.nanargmax(qhull.b)]):
            #č "beta" se nezměnila, ale jen kvůli jinejm návrhovým bodům
            bx.__fire()
    
    def __fire(bx):
        qhull = bx.ghull.hull
        nodes = qhull.fire(bx.outer_budget, use_MC=True)
        if nodes is not None:
            #č tyhle funkce už vracej pouhý f_model
            event_id = np.full(bx.outer_budget, -1, dtype=np.int8)
            candidates = CandyBox(nodes, event_id=event_id)
            bx.assess_candidates(candidates) # nic nevrácí, to je procedura
            bx.candidates_index[-1] = candidates
            
            arg = np.nanargmax(qhull.b)
            bx._bfacet = b = qhull.b[arg]
            bx._afacet = a = qhull.A[arg]
            bx._logger(msg='fire!', a=a, b=b)
    
    
    def get_pf_estimation(bx):
        #č dle toho, čo vidím v kódu (spouští nás .increment())
        #č přinejmenším konvexní obálka musí 
        #č zajištěně existovat
        # convex_hull_estimation  -2: inside, -1: outside
        pf_inside = bx.convex_hull_estimation[-2]
        pf_outside = bx.convex_hull_estimation[-1]
        
        #č Ghull spouštíme sporadicky, 
        #č takže musíme sami lepit nové etikety
        bx.global_stats['nsim'] = bx.nsim
        
        failsi = bx.failsi
        
        if 'tri' in dir(bx):
            #č Tri.get_pf_estimation() vrací:
            # 'TRI_estimation': tri_estimation, 'global_stats': {mix, failure}, \
            #'vertex_estimation' : vertex_estimation, \
            #'weighted_vertex_estimation' : weighted_vertex_estimation, 
            #'coplanar':sx.tri.coplanar}
            estimations = bx.Tri.get_pf_estimation()
            # TRI-compatible estimation
            # -1=outside, 0=success, 1=failure, 2=mix
            #č to je JustTriangulation, 
            #č outside (-1), ani success (1) nebudou korektní
            tri_estimation = estimations.pop('TRI_estimation')
            tri_estimation[-1] = pf_outside
            tri_estimation[0] = pf_inside - tri_estimation[1] - tri_estimation[2]
            estimations['TRI_overall_estimations'] = tri_estimation
            estimations['ghull_estimation'] = bx.ghull_estimation
            
            #č hrozně důležitý. Těšíme se na csv-čko.
            bx.global_stats.update(estimations['global_stats'])
            bx.global_stats['success_points'] = len(failsi[~failsi])
            bx.global_stats['failure_points'] = len(failsi[failsi])
            bx.global_stats['success'] = tri_estimation[0]
            bx.global_stats['candidates_sets'] = len(bx.candidates_index)
            estimations['global_stats'].update(bx.global_stats)
            return estimations
            
        
        #оӵ триангуляци ӧвӧл, иськем...
        
        #č může se stát, že první dvě tečky už hned májí různé barvy,
        #č ale žádnej simplex ještě nemáme.
        #č takže celou skříňku prostě bereme jako simplex
        event, event_id, fr, wfr = sx.get_simplex_event(bx, weighting_space=bx.tri_space)
        # -1=outside, 0=success, 1=failure, 2=mix
        tri_estimation = {-1:pf_outside, 0:0, 1:0, 2:0}
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
        
        return {'TRI_overall_estimations': tri_estimation, \
                'vertex_estimation' : vertex_estimation, \
                'weighted_vertex_estimation' : weighted_vertex_estimation, \
                'ghull_estimation' : bx.ghull_estimation}
        
        
    def export_estimation(bx):
        #č teď raději estimátory ukladáme hned
        for key, value in bx.get_pf_estimation().items():
            bx.guessbox.guess(key, bx.nsim, value)
        
        # prepare export to csv
        # All I Can Give You (Ashley Wallbridge Remix)
        # but not sure about proxy
        #č Ghull nabízí slušný stats
        
        #č Teď je to hrozně křehký, musí být zajištěno
        #č stejný počet a stejné pořádí estimátorů.
        #č Musí být způštěn bx.get_pf_estimation()
        #č který dopočíta zbývající estimátory z triangulaci.
        #č bx.get_pf_estimation() spolehá na určíté pořádí 
        #č global_stats z Triangulation třídy, čímž jsme
        #č porušujeme zásady SOLID
        #č Ale zatím budíž. Až se to rozbíje, tak možná
        #č necham třídu samostatně inicializovyvat svůj
        #č vlastní slovník s pevným počtem a pevným pořadím složek.
        if bx.stm_filename is not None:
            reader.export_estimation(bx.stm_filename, bx.global_stats)







#č alternativní název je 
#:) UltimateFastOptimizationOptimizedMinDistanceEnergyAdaptiveCensoringSampling
class DiceSimpleX:
    
    #č rozdil je v chybejicích odhadéch
    def _handle_changed_triangulation(bx, input_sample):
        """
        Triangulace zajistěně existuje
        """
            
        former_simplices = bx.tri.simplices
        mixed = bx.is_mixed()
        
        # sample je jíž převeden na f (v .add_sample()), takže je to bezpěčný
        bx.tri.add_points(getattr(input_sample, bx.tri_space))
        bx.simplex_events = bx.get_events()
        # print('increment se podaril')
        if len(bx.tri.coplanar): # pokud triangulace není v pořadku
            #print('triangulace v pořádku není')
            bx._logger(msg='triangulation has coplanar points')
            
        
        
        
        # zkontrolujeme co se změnilo
        # předpokladám, že se počet simplexů přidaním bodů nezměnší 
        equal_mask = former_simplices == bx.tri.simplices[:len(former_simplices)]
        changed_simplices_ids = np.argwhere(~equal_mask.all(axis=1)).reshape(-1)
        
            
            #č popajem pouze mixy, ty musel jsem spočítat před aktualizací
        for simplex_id in changed_simplices_ids[mixed[changed_simplices_ids]]:
            bx.candidates_index.pop(simplex_id)
            
        
        # pokud není splněná podmínka, 
        # tak nemáme jistotu, že se potenciály nezměni
        # ani u kandidatů, které se nacházejí v pojíštěných státem buňkách
        if (bx.tree_space != bx.tri_space) or (bx.p_norm != 2):
            for candidates in bx.candidates_index.values():
                bx.assess_candidates(candidates)    
            
        # změněné simplexy přepočítáme
        for simplex_id in changed_simplices_ids:
            bx.estimate_simplex(simplex_id)    
            
            
            
        # teď nové simplexy
        # simplexy свежего разлива
        for simplex_id in range(len(former_simplices), bx.tri.nsimplex):
            # zde jen počítame
            bx.estimate_simplex(simplex_id)
            
            
                
                
    def _handle_candidates(bx):
        #č prohrabeme odpad
        bx._judge_unjudged(bx.unjudged_candidates)
        bx._judge_unjudged(bx.former_candidates)
            
        
        
        #č A ještě...
        # 
        highest_bid = 0 
        for i, candidates in bx.candidates_index.items():
            bids = getattr(candidates, bx.potential)
            bid = np.max(bids)
            # side effect
            if bid > highest_bid:
                if np.any(candidates.nsim != bx.nsim):
                    if i == -1:
                        bx.assess_candidates(candidates)  
                    else:
                        bx.estimate_simplex(i)
                        candidates = bx.candidates_index[i]
                        
                    #š a eště ráz
                    bids = getattr(candidates, bx.potential)
                    bid = np.max(bids)
                    if bid > highest_bid:
                        highest_bid = bid
                
                else:
                    highest_bid = bid
                
            
        
    #č pro kompatibilitu s bx.regen() rodičovské třidy
    #č nechávám stejné názvy, ale žádný estimate tu nedělám
    def estimate_simplex(bx, simplex_id):
        
        simplex = bx.tri.simplices[simplex_id]
        
        # fp like a failure points. Number of failure points
        # intersect 2 times faster than setdiff (in my tests)
        fp = len(np.intersect1d(simplex, bx.samplebox.failure_points, assume_unique=True))
        #č hned na začátku odmítneme simplex, 
        #č pokud nevypadá jako stará Běloruská vlajka
        if (fp > 0) and (fp < bx.nvar + 1):
            
            # чылкыт f_model
            vertices = bx.f_model[simplex]
            
            
            vertices_model = getattr(vertices, bx.tri_space)
            
            #č budeme pokažde sestavovat ConvexHull z jedného simplexu
            #č a rešit jen zda naši bodíky "inside or outside"
            #č (s narustajícím nsim tohle brzy se stavá rychlejším než bežný dotaz)
            convex_hull = spatial.ConvexHull(vertices_model)
            
            
            #č nepodařilo se mi ve FORTRANovém kódě Kobyly význat #ё(древние руны, блин)
            #č a tak nevím jak přesně Kobyla sestavuje simplex.
            #č Každopádně, jsme asi schopní nabídnout lepší "roběh",
            #č než s tou implicitnou jedničkou.
            x0 = np.mean(vertices_model, axis=0)
            rhobeg = np.mean(np.abs(vertices_model - x0))
            #print("roběh", rhobeg)
            # catol - Tolerance (absolute) for constraint violations
            # default value for catol is 0.0002
            options = {'rhobeg': rhobeg, 'maxiter': bx.simplex_budget, 'disp': False, 'catol': 0}
            
            
            constraints = six.get_COBYLA_constraints(convex_hull)
            # as I can see, scipy treats 'tol' as 'rhoend'
            # with default value tol=1e-4
            #č jediný mechnizmus ukončení - vyčerpaní maximálního počtu iterací
            res = optimize.minimize(bx.assess_candidate, x0, args=(), method='COBYLA', \
                        tol=0, constraints=constraints, options=options)
                        
            bx._logger("simplex %s optimization: %s" %(simplex_id, res))
            #bx._logger(msg="estimate simplex"+str(simplex_id))
        
            
            x_sample = bx.f_model.new_sample(res.x, bx.tri_space)
            candidate = CandyBox(x_sample, event=[2])
            #č a, kruci, je třeba zas je vyhodnotit
            bx.assess_candidates(candidate)
            # vzorky je třeba přidát ke kandidatům
            # jako, nic nepokazí, ale čo tam připadně bylo - přepíše
            bx.candidates_index[simplex_id] = candidate
            

    
    
    def assess_candidate(bx, x):
        """
        Objective function for optimalization
        """
        
        if (bx.tri_space == bx.tree_space) and (bx.potential == 'psee'):
            x_tree = x
            pdf = float(bx.f_model.sample_pdf(x, bx.tree_space))
        else:#č máme smulu
            x_sample = bx.f_model.new_sample(x, bx.tri_space)
            x_tree = getattr(x_sample, bx.tree_space)
            pdf = float(x_sample.pdf(bx.tree_space))
        
        #č dd a ii budou prostě skalární hodnoty
        dd, ii = bx.tree.query(x_tree, k=1, p=bx.p_norm)
        
        PDFs = bx.sample_box.pdf(bx.tree_space)
        # teď máme hustoty kandidatů a prislušejicích jím vzorků
        PDF = PDFs[ii]
        
        if bx.potential == 'psee':
            #оӵ кучапи
            #č pejskovej potenciál
            #č psí-kučapí není invariántní vůči lineárním transformácím
            
            psee = -np.sqrt(pdf*PDF) * np.power(dd , bx.nvar)
            #print(psee)
            return psee
        else: # ksee 
            #оӵ кечато
            #č koťatko-káčátkovej potenciál
            #č ksí-kěčató není invariántní vůčí rotacím
            
            ksee = -float(lk.kechato_potential(bx.f_model[ii], x_sample, kechato_space=bx.kechato_space)) 
            #print(ksee)
            return ksee









        
    

class KickPointVoronoi(DiceBox):
    """
    Goal
    methods:
        *__init__():
            DiceBox.__init__():
                Chrt.regen():
                    DiceBox._LHS_regen()
                    _regen_outside():
                        estimate_outside():
                            Chrt.assess_candidates:
                                Chrt._nominate
                    _regen_inside():
                        __regen_inside:
                            **Triangulation magic**:
                                Razitko._on_add_simplex:
                                    Chrt.assess_candidates:
                                        Chrt._nominate
            
        >add_sample(): 
            *increment():
                >_LHS_increment()
                export_estimation()            
                _handle_changed_triangulation(input_sample):
                    get_events()
                    estimate_simplex(simplex):
                        assess_candidates
                    _invalidate_simplex(simplex)
                    
                _handle_changed_outside(input_sample)
                    estimate_outside():
                        assess_candidates:
                            _nominate
                    
                _handle_candidates()
                    assess_candidates:
                        _nominate
                    
                *regen()
        
        Chrt.__call__(): 
            >LHS_like_correction()
    
        get_pf_estimation()
        
        export_estimation():
            get_pf_estimation()
    """
    
    #č praca s kandidatama moc sa nezměnila
    #č funkce assess_candidates přířadí potenciál bodíkům
    #č a zaroveň je nominuje na soutež.
    #č na vstupu assess_candidates musí být CandyBox 
    #č s jíž nastaveným event_id
    assess_candidates = Chrt.assess_candidates
    _nominate = Chrt._nominate
    
    #č explicitně převezmu některé funkce
    #č ať v budoucnu nelamame hlavu, co jestě potřebujeme, co už nikoliv
    __repr__ = Chrt.__repr__
    __str__ = Chrt.__str__
    __call__ = Chrt.__call__
    regen = Chrt.regen
    
    _on_add_simplex = Razitko._on_add_simplex
    _invalidate_simplex = Razitko._invalidate_simplex
    
    
    #č míží nám sampling_space: Ghull umí vzorkovat outside pouze v G prostoru
    #č quadpy umístí integráční bodíky v prostoru triangulace.
    def __init__(bx, sample_object, scheme, tri_space='G', tree_space=None,\
                  kechato_space='U', potential='q_psee', q=0.5,\
                  p_norm=2, shell_budget=1000, outer_budget=100,\
                  LHS_correction=False, stm_filename=None):
        
        bx.scheme = scheme
        bx.tri_space = tri_space
        if tree_space is None:
            bx.tree_space = tri_space
        else:
            bx.tree_space = tree_space
            
        
        bx.kechato_space = kechato_space
        bx.shell_budget = shell_budget
        bx.outer_budget = outer_budget
        bx.p_norm = p_norm
        bx.potential = potential
        bx.q = q # used for q_psee potential only
        bx.LHS_correction = LHS_correction
        
        bx.stm_filename = stm_filename
        
        DiceBox.__init__(bx, sample_object)
    
        
    def init_parameters(bx):
        """
        Returns dictionary of parameters the DiceBox was initialized with
        """
        return {'sample_object':bx.sample_box, 'scheme':bx.scheme.name,\
                 'tri_space':bx.tri_space, 'tree_space':bx.tree_space,\
                 'kechato_space':bx.kechato_space, 'potential':bx.potential,\
                 'p_norm':bx.p_norm, 'shell_budget':bx.shell_budget,\
                 'outer_budget':bx.outer_budget, 'LHS_correction':bx.LHS_correction}
        

                
    def _regen_outside(bx):
        bx.convex_hull = khull.QHull(bx.f_model, space=bx.tri_space) # for gl_plot
        bx.ghull = Ghull(bx.convex_hull)
        bx._R = -1 # update outer under R>_R condition
        bx._afacet = None
        bx._bfacet = np.inf
        #č konečně mám pořádnou stejtful třídu
        #č pokud mám aspoň jednu tečku, tak už je mi šuma
        #č zda se konvexní obálka vytvořila, či nikoliv
        if bx.nsim > 0:
            bx.estimate_outside()
        
            
    def _regen_inside(bx):
        failsi = bx.failsi
        if np.any(failsi) and not np.all(failsi):
            #bx._logger(msg="triangulation started")
            bx.__regen_inside()
        else:
            #č jíž není nutný
            bx._logger(msg="triangulation skipped")
            
    def __regen_inside(bx):
        # create .tri triangulation
        if bx.nsim > bx.nvar + 1: # incremental triangulation require one more point
            try:
                # I'll use tri_space as a weigthing space
                # It could be separeted, but I am a little bit tired
                # from so much different spaces over there
                bx.Tri = sx.JustCubatureTriangulation(bx.samplebox, bx.scheme,\
                         tri_space=bx.tri_space, issi=None, \
                        weighting_space=bx.tri_space, incremental=True,\
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
    
    
        
        #č beží 99% času
    def increment(bx, input_sample):
        #ё ну нахрен это ваше наследование-расследование
        
        #č nechť bude, asi nikomu nevadí
        bx._LHS_increment(input_sample)
        
        #č strom posuneme sem    
        # cKDTree is used for potential calculation
        # we need everytime regenerate it
        sampled_plan_tree = getattr(bx.sample_box, bx.tree_space)
        bx.tree = spatial.cKDTree(sampled_plan_tree)
        bx.highest_bid = 0 
        
        
        #č logika se mění. Konvexní obálku máme vždycky.
        #č jistě, že po incrementu máme alespoň jeden vzorek
        #č takže hned od začátku můžeme trhat odhady
        
        #č tri - Deloneho triangulace
        if "tri" in dir(bx):
            bx._handle_changed_triangulation(input_sample)
        else:
            bx._regen_inside()
            
            
        bx._handle_changed_outside(input_sample)
        bx._handle_candidates()
        
        #č exportovať odhady jistě môžeme
        #č teďkom to děláme hned po přídání vzorků
        bx.export_estimation()
        
        
        #č tato funkce běží 91% času
        # bottleneck function
    def _handle_changed_triangulation(bx, input_sample):
        """
        Triangulace zajistěně existuje
        """
        bx.Tri.update()
            
                
                
                
    def _handle_changed_outside(bx, input_sample):
        try:
            #č kontrola korrektní i v případě NaN
            test = input_sample.event_id > -1
            #оӵ эскером
            if not test.all():
                bx.estimate_outside()
        except BaseException as e:
            msg = "input sample didn't provide correct 'event_id' attribute "
            error_msg = bx.__class__.__name__ + ": " + msg + repr(e)
            bx._logger(msg=error_msg)
            bx.estimate_outside()
    
    
    
    
    def _handle_candidates(bx):
        #č A ještě... AUKCE, AUCTION    
        # Election - selection
        for key, cached_bid in reversed(bx.candidates_index.cache.items()):
            # side effect
            if cached_bid > bx.highest_bid:
                #č pokud neprovadíme optimalizaci v simplexech
                #č tak nám stačí jednoduše assessovat
                bx.assess_candidates(bx.candidates_index[key])
                #č tím se mi aktualizuje cache
                bx.candidates_index[key] = bx.candidates_index[key]
                
        # probably, we shouldn't purge user candidates (if they are)
        # just every time evaluate them
        #č kdyby někdo chtěl mít užovatelské kandidaty...
#        if len(bx.candidates) > 0:
#            bx.judge_candidates(bx.candidates)
#            bx.assess_candidates(bx.candidates)
                    
    
    
    
    def _ghull_outside_callback(bx, outside_nodes):
        #č sice získáme filtrovaný outside, 
        #č musíme sami zabalit bodíky do CandyBoxu
        # -2 = 'inside' -1 = 'outside'
        event_ids = np.full(len(outside_nodes), -1, dtype=np.int8)
        candidates = CandyBox(outside_nodes, event_id=event_ids)
        bx.assess_candidates(candidates)
        
        bids = getattr(candidates, bx.potential)
        #č nie třeba kontrolovat jevy, tam je pouze outside
        #bids *= (candidates.event_id == -1) + (candidates.event_id == 2)
        bid = np.nanmax(bids)
        if bid > bx._highest_outside:
            #č uložíme varku bodíku pouze když 
            #č majú větší potenciál, 
            bx._highest_outside = bid
            #č čo tam připadně bylo - přepíšeme
            #č uložíme s indexem dle ghull_estimation:
            # -22: inner, -21: shell inside, -12: shell outside, -11: outer
            bx.candidates_index[-12] = candidates
        
    
    def estimate_outside(bx):
        #č konečně mám pořádnou stejtful třídu
        #č pokud mám aspoň jednu tečku, tak už je mi šuma
        #č zda se konvexní obálka vytvořila, či nikoliv
        
        #č Máme 2 úkoly: 
        #č 1. Získat odhady a uložit je, abychom nemuseli opakovaně integrovat,
        #č    dokud se neobjeví nějaký nový vzorek zvenku.
        #č 2. Získat kandidaty.
        #č    a. z mezíkruží (-12)
        #č    b. fire, to co navrhne QHull (-1)
        #č    c. boom, doporuření QHull můžou i zklamat (-11)
        #č    cc. ze vdálenejších galaxí (-111)
        
        #č prace s tečkami v mezikruži se změnila
        #č teď tečky dostávám přes kolbek po částech
        #č a není předem známo, kolik těch částí bude.
        #č Na začátku radší, pro jistotu, 
        #č vyhodíme stare bodíky z mezikruži (-12)
        bx.candidates_index.pop(-12, "Nejsou? Nevadí...") # "Ӧвӧл-а мар-а?"
        bx._highest_outside = 0
        
        # get candidates!
        #č explicitně (pokažde) počtem teček zadavám přesnost integrace
        #č takže změny bx.shell_budget budou při dálším spuštění aplikovány
        data = bx.ghull.integrate(bx.shell_budget, \
                                callback_outside=bx._ghull_outside_callback) 
        ghull_estimation, convex_hull_estimation, global_stats = data
        #č uložíme. Не жалко.
        #č první úkol máme splněný
        bx.ghull_estimation = ghull_estimation
        bx.convex_hull_estimation = convex_hull_estimation
        bx.global_stats = global_stats
        bx._logger(msg="outside estimation:", ghull_stats=global_stats)
        
        
        
        #č zde už nám jde pouze o kandidaty
        
        # fire
        bx._fire()
        # boom
        
        if global_stats['R'] > bx._R:
            #č Projedeme Moravou
            nodes = bx.ghull.boom(bx.outer_budget, use_MC=True)
            #č tyhle funkce už vracej pouhý f_model
            event_id = np.full(bx.outer_budget, -1, dtype=np.int8)
            candidates = CandyBox(nodes, event_id=event_id)
            bx.assess_candidates(candidates) # nic nevrácí, to je procedura
            bx.candidates_index[-11] = candidates
            
            #č Už máte Mléčnou dráhu projdutou?
            nodes = bx.ghull.boom(bx.outer_budget, use_MC=False)
            #č tyhle funkce už vracej pouhý f_model
            event_id = np.full(bx.outer_budget, -1, dtype=np.int8)
            candidates = CandyBox(nodes, event_id=event_id)
            bx.assess_candidates(candidates) # nic nevrácí, to je procedura
            bx.candidates_index[-111] = candidates
            
            bx._R = global_stats['R']
            bx._logger(msg='boom!', _R=bx._R)
        #č to je vše. Nic nevrácíme
    
    def _fire(bx):
        qhull = bx.ghull.hull
        if bx._afacet is None:
            bx.__fire()
        
        #č podle mě sem nemusí dojít, 
        #č dokud se konvexní obálka ve skutku nevytvoří
        #č b-čko u QHull pro nás má jakoby záporné vzdálenosti
        elif np.all(bx._bfacet > qhull.b):
            #č jasně, že musíme zapalit
            bx.__fire()
        elif np.any(bx._afacet != qhull.A[np.nanargmax(qhull.b)]):
            #č "beta" se nezměnila, ale jen kvůli jinejm návrhovým bodům
            bx.__fire()
    
    def __fire(bx):
        qhull = bx.ghull.hull
        nodes = qhull.fire(bx.outer_budget, use_MC=True)
        if nodes is not None:
            #č tyhle funkce už vracej pouhý f_model
            event_id = np.full(bx.outer_budget, -1, dtype=np.int8)
            candidates = CandyBox(nodes, event_id=event_id)
            bx.assess_candidates(candidates) # nic nevrácí, to je procedura
            bx.candidates_index[-1] = candidates
            
            arg = np.nanargmax(qhull.b)
            bx._bfacet = b = qhull.b[arg]
            bx._afacet = a = qhull.A[arg]
            bx._logger(msg='fire!', a=a, b=b)
    
    
    def get_pf_estimation(bx):
        #č dle toho, čo vidím v kódu (spouští nás .increment())
        #č přinejmenším konvexní obálka musí 
        #č zajištěně existovat
        # convex_hull_estimation  -2: inside, -1: outside
        pf_inside = bx.convex_hull_estimation[-2]
        pf_outside = bx.convex_hull_estimation[-1]
        
        #č Ghull spouštíme sporadicky, 
        #č takže musíme sami lepit nové etikety
        bx.global_stats['nsim'] = bx.nsim
        
        failsi = bx.failsi
        
        if 'tri' in dir(bx):
            #č Tri.get_pf_estimation() vrací:
            # 'TRI_estimation': tri_estimation, 'global_stats': {mix, failure}, \
            #'vertex_estimation' : vertex_estimation, \
            #'weighted_vertex_estimation' : weighted_vertex_estimation, 
            #'coplanar':sx.tri.coplanar}
            estimations = bx.Tri.get_pf_estimation()
            # TRI-compatible estimation
            # -1=outside, 0=success, 1=failure, 2=mix
            #č to je JustTriangulation, 
            #č outside (-1), ani success (1) nebudou korektní
            tri_estimation = estimations.pop('TRI_estimation')
            tri_estimation[-1] = pf_outside
            tri_estimation[0] = pf_inside - tri_estimation[1] - tri_estimation[2]
            estimations['TRI_overall_estimations'] = tri_estimation
            estimations['ghull_estimation'] = bx.ghull_estimation
            
            #č hrozně důležitý. Těšíme se na csv-čko.
            bx.global_stats.update(estimations['global_stats'])
            bx.global_stats['success_points'] = len(failsi[~failsi])
            bx.global_stats['failure_points'] = len(failsi[failsi])
            bx.global_stats['success'] = tri_estimation[0]
            bx.global_stats['candidates_sets'] = len(bx.candidates_index)
            estimations['global_stats'].update(bx.global_stats)
            return estimations
            
        
        #оӵ триангуляци ӧвӧл, иськем...
        
        #č může se stát, že první dvě tečky už hned májí různé barvy,
        #č ale žádnej simplex ještě nemáme.
        #č takže celou skříňku prostě bereme jako simplex
        event, event_id, fr, wfr = sx.get_simplex_event(bx, weighting_space=bx.tri_space)
        # -1=outside, 0=success, 1=failure, 2=mix
        tri_estimation = {-1:pf_outside, 0:0, 1:0, 2:0}
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
        
        return {'TRI_overall_estimations': tri_estimation, \
                'vertex_estimation' : vertex_estimation, \
                'weighted_vertex_estimation' : weighted_vertex_estimation, \
                'ghull_estimation' : bx.ghull_estimation}
        
        
    def export_estimation(bx):
        #č teď raději estimátory ukladáme hned
        for key, value in bx.get_pf_estimation().items():
            bx.guessbox.guess(key, bx.nsim, value)
        
        # prepare export to csv
        # All I Can Give You (Ashley Wallbridge Remix)
        # but not sure about proxy
        #č Ghull nabízí slušný stats
        
        #č Teď je to hrozně křehký, musí být zajištěno
        #č stejný počet a stejné pořádí estimátorů.
        #č Musí být způštěn bx.get_pf_estimation()
        #č který dopočíta zbývající estimátory z triangulaci.
        #č bx.get_pf_estimation() spolehá na určíté pořádí 
        #č global_stats z Triangulation třídy, čímž jsme
        #č porušujeme zásady SOLID
        #č Ale zatím budíž. Až se to rozbíje, tak možná
        #č necham třídu samostatně inicializovyvat svůj
        #č vlastní slovník s pevným počtem a pevným pořadím složek.
        if bx.stm_filename is not None:
            reader.export_estimation(bx.stm_filename, bx.global_stats)


	#č boom-body klidně můžou spadat dovnitř orth obálky.
    #č Ale to nevadí, kandidati za vnější kryžnicí nejsou špatní, že?
    def boom(self, ns):
        # rand_dir: prepare ns random directions on a unit d-sphere
        rand_dir = sball.get_random_directions(ns, self.sample.nvar) #random directions
        
        #č deme od vnější .get_R() kružnici směrem ven
        r = self.get_R()
        
        if r < max_R_ever:
            R = max_R_ever
        else:
            R = r + 10
        r = np.linspace(self.get_R(), max_R_ever, ns, endpoint=True) 
        nodes_G = rand_dir*r[:,None]
        
        nodes = self.sample.f_model.new_sample(nodes_G, space='G')
        return nodes
        
            
    
            
    def get_R(self):
    	return self._R
        #sum_squared = np.sum(np.square(self.sample.G), axis=1)
        #index = np.argmax(sum_squared)
        #return np.sqrt(np.nanmax(sum_squared))


##č nie treba počítat odhady v každem kroku
##č ale zas, taky že chceme do článků davat nějaké diagramy
#
##č 
##č po 2. kroku ghull.fire() nastaví vnější poloměr R a dovnitř už ani nesahne. 
##č Je to v porádku, pokud rozhodování je v G prostoru, 
##č protože v druhem kroku algoritmus nějak zvolil ten nejoptimálnější poloměr 
##č a není v dalším kroku skutečně důvod pod ten poloměr jít.
##č Pokud rozhodujeme v R prostoru s nějakým divokým rozdělením - už je to trošku problem.
#
##č Jak poznam, že není dostatek teček, nebo je nějaký problem? Jakou chybu hodí Ghull?


#♥♥♥♥♥♥
# DiceBoxiCheck
class KechatoLukiskon(DiceBox):
    def __init__(kl, sample_object, model_space='Rn', sampling_space=None, kechato_space='Rn', p_norm=1, gradient=None, budget=20000):
        kl.model_space = model_space
        kl.sampling_space = sampling_space
        kl.kechato_space = kechato_space
        kl.p_norm = p_norm
        kl.gradient = gradient
        kl.budget = budget
        
        super().__init__(sample_object)
        
        
    def __call__(kl):
        kl._logger(msg="умой! Умойлэсь но умой сэмпл шедьтоно")
        
        if (len(kl.failure_points) < 1) or (len(kl.success_points) < 1):
            kl._logger(msg="Умоез сэмпл шедьтыны уг быгаты :( ")
            return kl.LHS_like_correction(kl.h(1))
            
        else:
            
            kl.ivortodon = 0
            kl.to_sample = None
            
            # ty brdo, stm nedává číslo tečky. Nemusí, no...
            kl.i = 0
            stm.Voronoi_2_point_estimation(kl, model_space=kl.model_space, sampling_space=kl.sampling_space,\
                                        p_norm=kl.p_norm, gradient=kl.gradient, budget=kl.budget, callback=kl.callback)
                
            if kl.to_sample is not None:
                # hrubě ošidíme s takovejhlema usilima námi pěčlivě vybraný vzorečiček
                return kl.LHS_like_correction(kl.to_sample) 
            else:
                kl._logger(msg="Умоез сэмпл шедьтыны ӧй быгаты :( ")
                return kl.LHS_like_correction(kl.h(1))
        
        
    def callback(kl, *args, **kwargs):
        # spoléhám na to, že stm vrácí tečky v f-ku
        nodes = kwargs['nodes']
        node_pf = nodes.node_pf_estimations
        
        mask = (node_pf > 0) * (node_pf < 1)
        nodes = nodes[mask]
        if len(nodes) > 0:
            node_pf = node_pf[mask]
            
            #  !!!! ENTROPY !!!
            nodes.entropy = -node_pf*np.log(node_pf) - (1-node_pf)*np.log(1-node_pf)
            
            nodes.ksee = lk.kechato_potential(kl.f_model[kl.i], nodes, kechato_space=kl.kechato_space)
            
            nodes.ivortodon = nodes.entropy * nodes.ksee
            
            if np.max(nodes.ivortodon) > kl.ivortodon:
                # side effects
                kl.ivortodon = np.max(nodes.ivortodon)
                kl.to_sample = nodes[np.argmax(nodes.ivortodon)]
        
        # side effect
        kl.i += 1
                                    
    
#♥♥♥♥♥♥♥♥♥♥♥♥
class KechatoTwoPointLukiskon(DiceBox):
    def __init__(kl, sample_object, model_space='Rn', sampling_space=None, kechato_space='Rn', p_norm=1, gradient=None, budget=20000):
        kl.model_space = model_space
        kl.sampling_space = sampling_space
        kl.kechato_space = kechato_space
        kl.p_norm = p_norm
        kl.gradient = gradient
        kl.budget = budget
        
        super().__init__(sample_object)
        
        
    def __call__(kl):
        kl._logger(msg="умой! Умойлэсь но умой сэмпл шедьтоно")
        
        kl.candidates_index = {}
        
        if (len(kl.failure_points) < 1) or (len(kl.success_points) < 1):
            kl._logger(msg="Умоез сэмпл шедьтыны уг быгаты :( ")
            return kl.LHS_like_correction(kl.h(1))
            
        else:
            
            kl.ivortodon = 0
            kl.to_sample = None
            
            # ty brdo, stm nedává číslo tečky. Nemusí, no...
            kl.i = 0
            stm.Voronoi_2_point_estimation(kl, model_space=kl.model_space, sampling_space=kl.sampling_space,\
                                        p_norm=kl.p_norm, gradient=kl.gradient, budget=kl.budget, callback=kl.callback)
                
            if kl.to_sample is not None:
                # hrubě ošidíme s takovejhlema usilima námi pěčlivě vybraný vzorečiček
                return kl.LHS_like_correction(kl.to_sample) 
            else:
                kl._logger(msg="Умоез сэмпл шедьтыны ӧй быгаты :( ")
                return kl.LHS_like_correction(kl.h(1))
        
        
    def callback(kl, *args, **kwargs):
        # spoléhám na to, že stm vrácí tečky v f-ku
        nodes = kwargs['nodes']
        node_pf = nodes.node_pf_estimations
        
        mask = (node_pf > 0) * (node_pf < 1)
        nodes = nodes[mask]
        if len(nodes) > 0:
            node_pf = node_pf[mask]
            
            #  !!!! ENTROPY !!!
            nodes.entropy = -node_pf*np.log(node_pf) - (1-node_pf)*np.log(1-node_pf)
            
            
            #nodes.ksee = lk.kechato_potential(kl.f_model[kl.i], nodes, kechato_space=kl.kechato_space)
            #♥ кечато
            #č ksí-kěčató není invariántní vůčí rotacím
            ksee = np.empty(len(nodes))
            ii2 = nodes.ii2
            for ii in np.unique(nodes.ii2):
                #č doufám, že je to legální
                ksee[ii==ii2] = lk.kechato_potential(kl.f_model[[kl.i, ii]], nodes[ii==ii2], kechato_space=kl.kechato_space)
            nodes.ksee = ksee
            
            
            nodes.ivortodon = nodes.entropy * nodes.ksee
            
            kl.candidates_index[kl.i] = nodes
            
            if np.max(nodes.ivortodon) > kl.ivortodon:
                #E side effects
                kl.ivortodon = np.max(nodes.ivortodon)
                kl.to_sample = nodes[np.argmax(nodes.ivortodon)]
        
        #E side effect
        kl.i += 1    


