#!/usr/bin/env python
# coding: utf-8

"""
Zde leží BlackBox (tuším, bude jeden)
BlackBox pěčlivě ukladá věškerá data,
věškeré sady vzorků, průběžné odhady a tak.
Nejsem už jistý, zda BlackBox je šťastný nazev, neboť
teďkom je to spíše jen krabička pro krámy
"""


import numpy as np
from scipy import spatial
from . import plot
import pickle
from . import IS_stat
from .candybox import CandyBox
from . import sball # for adaptive censoring
from . import f_models # for adaptive censoring
from scipy import stats # for adaptive censoring
from scipy import optimize # for BlackSimpleX

import inspect # for ._log() function

from .samplebox import SampleBox # for candidates packing
from . import simplex as six
from . import lukiskon as lk

from . import estimation as stm # for KechatoLukiskon
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


class BlackBox:
    """
    BlackBox pěčlivě ukladá věškerá data,
    věškeré sady vzorků (well, no yet), průběžné odhady a tak.
    Nejsem už jistý, zda BlackBox je šťastný nazev, neboť
    teďkom je to spíše jen krabička pro krámy

    .sampled_plan object
    .Z = g_values
    .failsi
    
    Souřadnice primárně z prostoru modelu, ty co jsme rovnou
    posilali do g_modelu!
    
    """
    def __init__(bx, sample_box):
        bx.sample_box = sample_box
        # not really needed
        bx.f = sample_box.sampled_plan()
        # sample density (just helpful thing)
        bx.h = bx.f
        # don't ask me
        bx.candidates = sample_box.sampled_plan()
        
        # nové uložiště odhadů zadám explicitně, aby se pak
        # odhady v stm kodu přířazovaly zprávné krabice
        bx.estimations = []
        # má bejt GuessBox součástí BlackBoxu?
        try:
            bx.guessbox = GuessBox(sample_box.filename, flush=20)
        except:
            bx.guessbox = GuessBox("", flush=20)
        bx.regen()
        
    def __repr__(bx):
        return "%s(%s)"%('BlackBox', repr(bx.sample_box))
        
    def __str__(bx):
        return str('BlackBox ' + bx.sample_box)
        
    def __len__(bx):
        return bx.sample_box.nsim
        
    def __call__(bx):
        """
        Offer next sample
        """
        # I do not see nothing illegal here
        # LHS_like_correction do right conversion
        return bx.LHS_like_correction(bx.h(1))
    
    def __getitem__(bx, slice):
        # stačí vratit sample_box
        return bx.sample_box[slice]
    
    def __getattr__(bx, attr):
        if attr == 'blackbox':
            return bx

        if attr == 'dicebox':
            return bx
            
        # branime sa rekurzii
        # defend against recursion
        # рекурсилы пезьдэт!
        if attr == 'sample_box':
            raise AttributeError
                
        # По всем вопросам обращайтесь 
        # на нашу горячую линию    
        else:
            return getattr(bx.sample_box, attr)
    
    # just plot, green points, red points...
    plot2D = plot.plot2D
    plot3D = plot.plot3D
    show2D = plot.show2D
    show3D = plot.show3D
        
    # přidávání vzorků musí bejt explicitní!
    def add_sample(bx, input_sample):
        bx._log("we have got new data:", str(input_sample))
        bx.sample_box.add_sample(input_sample)
        # tohle musí převest rozdělení vstupního vzorku na vlastní rozdělení skříňky
        inner_sample = bx.sample_box.new_sample(input_sample)
        bx.increment(inner_sample)
        
    
    def increment(bx, input_sample):
        for i in range(bx.nvar):
            for j in range(len(input_sample)):
                plan_index = np.searchsorted(bx.sorted_plan_U[i], input_sample.U[j,i])
                bx.sorted_plan_U[i] = np.insert(bx.sorted_plan_U[i], plan_index, input_sample.U[j,i])
    
    def regen(bx):
        # шайтан регенираци лэзьиз
        bx._logger(msg='regeneration started')
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
        # Здесь вижу железную конвертацию до f-ка,
        # которая пройдёт по R координатам
        # Kruci drát, tady by se nemohlo nic posrat
        to_sample_node = bx.f.new_sample(input_sample)
        
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
                 
        return bx.f.new_sample(LHS_node, 'U')
        
    def _log(bx, *msg, indent=0):
        print(bx.__class__.__name__ + ":", *msg)
            
    def _logi(bx, *msg, indent=1):
        print("\t"*indent, inspect.currentframe().f_back.f_code.co_name + ":", *msg)
        
        
        # The BlackBox Observer 
    def _logger(self, *args, msg="", indent=0, **kwargs):
        print(self.__class__.__name__ + ":" + msg, *args, kwargs) 
        
        
        # inspired by Qt
    def connect(self, slot): self._logger = slot
    def disconnect(self): del(self._logger)
    
    
    # kdyby něco
    # callback = lambda *_, **__: None
    
    
    
    
class Censoring(BlackBox):
    def __init__(bx, sample_object, tri_space='Rn'):
        bx.tri_space = tri_space
        super().__init__(sample_object)
        
    def __repr__(bx):
        return "%s(%s, %s)"%(bx.__class__.__name__, repr(bx.sample_box), repr(bx.tri_space))
        
    def __str__(bx):
        return str(bx.__class__.__name__)
        
    def increment(bx, input_sample):
        super().increment(input_sample)
            
        if "tri" in dir(bx):
            # tri - Deloneho triangulace
            # sample je jíž převeden na f (v .add_sample()), takže je to bezpěčný
            bx.tri.add_points(getattr(input_sample, bx.tri_space))
            # print('increment se podaril')
            if len(bx.tri.coplanar): # pokud triangulace není v pořadku
                #print('triangulace v pořádku není')
                bx._log('triangulation is coplanar')
        else:
            bx._log('Triangulace (zatím?) neexistuje')
            bx.regen()
    
    
    def regen(bx):
        super().regen()
        # chcu zachytit spadnuti QHull na začatku, kdy ještě není dostatek teček.
        #  Jinak je třeba nechat QHull spadnout
        if bx.nsim > 2*bx.nvar + 3: 
            # tady je to OK
            bx.tri = spatial.Delaunay(getattr(bx.sampled_plan, bx.tri_space), incremental=True)
            if len(bx.tri.coplanar):
                #print('triangulace v pořádku není')
                bx._logger(msg='triangulation is coplanar')
            else:
                #print('triangulace je v pořádku')
                bx._logger(msg='triangulation is OK')
            
        else: # lze přípustit chybu triangulace    
            try:
                bx.tri = spatial.Delaunay(getattr(bx.sampled_plan, bx.tri_space), incremental=True)
            except:
                bx._logger(msg='triangulation failed')
        
        
        # pokud tecek nestaci na vytvareni aspon jedneho simplexu - pokrcim rameny
        try:
            # tady je to OK
            bx.tri = spatial.Delaunay(getattr(bx.sampled_plan, bx.tri_space), incremental=True)
            if len(bx.tri.coplanar): # pokud triangulace je v pořadku
                #print('triangulace v pořádku není')
                bx._log('triangulation is coplanar')
            else:
                #print('triangulace je v pořádku')
                bx._log('triangulation is OK')
        except:
            # kdyby neco - berem kramle
            bx._log('triangulation failed')
            
    
    # tato metoda je vlastně pro MinEnergyCensoredSampling
    # ale zde se taky může hodit
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
    
            
            
    def __call__(bx):
        # je treba si uvedomit ze pravdepodobnost chytnuti muze byt min jak pf. V soucasne realizaci
        try:
            # očekávám, že projde kandidaty
            # vodkaď jsou - netuším
            to_sample, rate = bx.filter()
            # když nepovedlo s kandidaty, zkusíme sami nagenerovat
            while len(to_sample) == 0: # nekonečno
                # tak, děcka, server má spoustu času a nikam nespejchá
                # ale pokud tohle sežere věškerou paměť (ne když, ale kdy)
                # dostaneš co proto!
                # vomezíme pole na 10e6 (desitky mega teda vodhadově)
                # by bylo možně použit chytrejší vzoreček s logaritmem
                # ale snad tohle postačí
                to_sample, rate = bx.filter(bx.h(int(0.9999*rate + 100)))
            return bx.LHS_like_correction(to_sample)
        
        # chcu zachytit spadnuti QHull na začatku, kdy ještě není
        # dostatek teček. Je-li bx.tri fakticky existuje, tj.
        # triangulace jíž existovala - je třeba nechat QHull spadnout
        except AttributeError:
            # kdyby neco - berem kramle
            print("Triangulation doesn't exist. Censoring failed")
            return bx.LHS_like_correction(bx.h(1)) # it should be OK
           
    def filter(bx, candidates=[]):
        """
        supports both sample and sample.R input
        
        logika metody, nebo, přesněji, implementaci 
        je taková, že bule-li někdo-něco mimo doménu,
        tak funkce je vrátí a zbytek už neřeší
        """
        # co to bylo na vstupu?
        # když nebyl žádný,
        # projdeme vlastními kandidaty
        if len(candidates)==0:
            candidates = bx.candidates
            
        
        # tady byl problém. Funkce byla původně navržena tak, 
        # aby ji nezajimalo co je na vstupu
        # to ale nefunguje
        # další funkce jako výstup očekavají něco s validním R-kem
        candidates_to_sample_node = getattr(bx.f.new_sample(candidates), bx.tri_space)
            
            
        found_simplices = bx.tri.find_simplex(candidates_to_sample_node)
        # ouside of domain - it's easy
        outside = candidates[found_simplices < 0]
        if len(outside) > 0:
            # my hodnotili svých kandidatov?
            if bx.candidates == candidates:
                bx.candidates = outside
            return outside, len(candidates)/len(outside)
            
        # tady já chcu vrátit první vhodný vzorek a tím končít
        for candidate_id in range(len(candidates)):
            # simplex_id >= 0: # inside of domain
            simplex_id = found_simplices[candidate_id]
            simplex = bx.tri.simplices[simplex_id]

            # fp like a failure points. Number of failure points
            fp = len(np.setdiff1d(simplex, bx.failure_points))

            # pokud je simplex není jednobarevny..
            if (fp != 0) and (fp != bx.nvar+1):
                # my hodnotili svých kandidatov?
                if bx.candidates == candidates:
                    bx.candidates = candidates[candidate_id:]
                return candidates[candidate_id], candidate_id
            
        # nepovedlo. nic
        # mě nenapadá žádný lepší způsob vrátit prázdnou matici
        return candidates[0:0], len(candidates)
           
           
           
           
class AdaptiveCensoring(Censoring):
    def __init__(bx, sample_object, tri_space='Rn', pf_lim=(1,0)):
        bx._logger(msg="instance creating")
        bx.sball = sball.Sball(sample_object.nvar)
        bx.pf_lim = pf_lim
        
        bx.base_r = bx.sball.get_r(0.5)
        
        # pro jistotu pridame
        bx.simplex_index = {'failure':[], 'success':[], 'mix':[]}
        
        
        # overall estimations
        #bx.oiss = IS_stat.ISSI(['failure', 'success', 'out', 'mix'])
        # -1 = 'out', 0=success, 1=failure, 2=mix
        bx.oiss = IS_stat.ISSI([-1,0,1,2]) 
        # current estimations
        bx.ciss = IS_stat.ISSI([-1,0,1,2]) 
        
        super().__init__(sample_object, tri_space)
        
        
    def __repr__(bx):
        return "%s(%s, %s, %s)"%(bx.__class__.__name__, repr(bx.sample_box), repr(bx.tri_space), repr(bx.pf_lim))
        
    def __str__(bx):
        return str(bx.__class__.__name__)
        
    def regen(bx):
        bx._logi(inspect.currentframe().f_back.f_code.co_name, "launched regeneration")
            
        super().regen()
        if bx.pf_lim[1] == 0:
            bx.drop_r = float("inf")
        else:
            bx.drop_r = bx.sball.get_r(bx.pf_lim[1])
        
        # dropneme (pro jistotu) odhady
        bx.oiss = bx.ciss
        # -1 = 'out', 0=success, 1=failure, 2=mix
        bx.ciss = IS_stat.ISSI([-1,0,1,2]) 
        
        # drop indexes
        bx.simplex_index = {'failure':[], 'success':[], 'mix':[]}
        
    def increment(bx, input_sample):
        super().increment(input_sample)
        
        # drop indexes
        bx.simplex_index = {'failure':[], 'success':[], 'mix':[]}
        
        # current estimations
        try: # to čo já vidím v kódu - ISSI slovníky se pokažde generujóu znovu, 
            # není nutně je explicitně kopirovať
            bx.guessbox.guess('TRI_overall_estimations', bx.nsim-1, bx.oiss.estimations)
            bx.guessbox.guess('TRI_current_estimations', bx.nsim-1, bx.ciss.estimations)
        except AttributeError:
            bx.guessbox.guess('TRI_upper_pf', bx.nsim-1, 1)
            
        # a znovu začneme počítat
        # -1 = 'out', 0=success, 1=failure, 2=mix
        bx.ciss = IS_stat.ISSI([-1,0,1,2]) 
            
            
    def __call__(bx):
        bx._logger(msg="we were asked for an recommendation")
        # je treba si uvedomit ze pravdepodobnost chytnuti muze byt min jak pf. V soucasne realizaci
        try:
            # očekávám, že projde kandidaty
            # odkaď jsou - netuším
            to_sample, rate, simplex_id = bx.filter()
            # když nepovedlo s kandidaty, zkusíme sami nagenerovat
            while len(to_sample) == 0: # nekonečno
                # pokusme se nastavit rate tak, abychom získali právě jedneho kandidata
                try: # try uvnitř traja
                    p_rate = bx.oiss.estimations[-1] + bx.oiss.estimations[2]
                except:
                    p_rate = bx.pf_lim[0] - bx.pf_lim[1]
                if p_rate < 1e-5:
                    rate = 100000
                else:
                    rate = int(1/p_rate) + 1
                to_sample, rate, simplex_id = bx.filter(bx.get_candidates(rate))
            choose = bx.LHS_like_correction(to_sample)
            bx._log("finally we choose", str(choose), "of", simplex_id, "simplex")
            return choose
        
        # chcu zachytit spadnuti QHull na začatku, kdy ještě není
        # dostatek teček. Je-li bx.tri fakticky existuje, tj.
        # triangulace jíž existovala - je třeba nechat QHull spadnout
        except AttributeError:
            choose = bx.LHS_like_correction(bx.get_candidates(1))
            if bx.nsim < bx.nvar + 1: # je to legální
                bx._log("we have no enough points to build triangulation, so", str(choose), "is our recommendation")
                return choose
                
            elif bx.nsim < 2*bx.nvar + 3: # to je ještě budiž
                bx._log("we have troubles with triangulation, so we offer random sample for now:", str(choose))
                return choose
            else: # no to teda ne!
                raise ValueError("AdaptiveCensoring: s tou triangulací je fakt něco není v pořadku")
           
           
    def filter(bx, candidates=[]):
        """
        za pvré, jako vstup očekávám kandidaty od .get_candidates() funkce,
        zabalené do полукустарного sample_boxu s zadaným .implicit_multiplicator
        (je to drobnost pro přesnějši zpracování sad IS IS_statem).
        
        Metoda musí souřádnicím přiřazovat jev 
        "success", "failure", "mix", "outside"
        
        TATO metoda jakmile narazí na "mix" nebo "outside"
        ukladá zjištěné informace do ISSI a nalezeného kandidata vrací
        """
        # co to bylo na vstupu?
        # když nebyl žádný,
        # projdeme vlastními kandidaty
        if len(candidates)==0:
            candidates = bx.candidates
            
        bx._logi("kandidaty:", candidates)
            
        # je třeba lokálně zachovat implicit_multiplicator
        # jinak se ztrací při slajsingu
        # nechceš přepsat SampleBox, Alexi?   
        try:     
            implicit_multiplicator = candidates.implicit_multiplicator
        except AttributeError: # kandidaty můžou bejt odkudkoliv
            # s nekonečným rozptylem nebudou mít váhu "absenční" jevy
            # moc to odhadům nepomůže, protože je-li kandidaty
            # nemajú .implicit_multiplicator
            # asi nebudou mať ani váhy IS v .g_values
            implicit_multiplicator = float("inf")
            bx._logi("Dobrý den, kandidaty nemajú .implicit_multiplicator")#. S pozdravem, AdaptiveCensoring")
        
        # tady byl problém. Funkce byla původně navržena tak, 
        # aby ji nezajimalo co je na vstupu
        # to ale nefunguje
        # další funkce jako výstup očekavají něco s validním R-kem
        # no tj. já zde provádím posouzení transformací z R-ka vstupních souřadnic
        candidates_to_sample_node = getattr(bx.f.new_sample(candidates), bx.tri_space)
            
            
        current_simplices = bx.tri.find_simplex(candidates_to_sample_node)
        
        
        # tak bacha
        # budeme přepísovat jevy in-place
        found_simplices = np.ma.array(current_simplices.copy()) #.copy()
        # nemaskované - obsahuji číslo simplexu
        # maskované - číslo jevu
        # -1 = 'out', 0=success, 1=failure, 2=mix
        # tj. procházíme simplexy z náhodné sady vzorků,
        # nahrazujeme čislo simplexu odpovidajicím mu jevem
        # a skryváme ho
        # pote ty "skryté", "projduté" vzorky využiváme k žískání odhadů
        
        while len(current_simplices):# > 0:
            bx._logi("current simplices", current_simplices)
            # berem hned prvního kandidata 
            # a posuzujeme co je zač
            simplex_id = current_simplices[0]
            mask = found_simplices==simplex_id
            
            if simplex_id < 0: # -1 means ouside
                # berem kramle
                break
            elif simplex_id in bx.simplex_index['success']:
                found_simplices[mask] = 0
            elif simplex_id in bx.simplex_index['failure']:
                found_simplices[mask] = 1
            elif simplex_id in bx.simplex_index['mix']:
                found_simplices[mask] = 2
                # kramle
                break
            else: # no index information
                # tady já chcu vrátit první vhodný vzorek a tím končít
                # simplex_id >= 0: # inside of domain
                # asi tady získavam množinu s čísly vrcholů
                # kteří zakladají simplex
                simplex = bx.tri.simplices[simplex_id]
                
                # for debug
                bx._logi("провал индексу", simplex_id, indent=2)
    
                # fp like a failure points. Number of failure points
                # setdiff "Return the unique values in ar1 that are not in ar2."
                fp = len(np.setdiff1d(simplex, bx.failure_points))
                
                if fp == bx.nvar+1: # 
                    bx.simplex_index['success'].append(simplex_id)
                    found_simplices[mask] = 0
                elif fp == 0:
                    bx.simplex_index['failure'].append(simplex_id)
                    found_simplices[mask] = 1
                    #print("failure simplex", simplex_id)
                else:
                    bx.simplex_index['mix'].append(simplex_id)
                    found_simplices[mask] = 2
                    bx._logi("mixed simplex", simplex_id)
                    # bacha! kramle
                    break
    
            # pridame do seznamu známého
            found_simplices[mask] = np.ma.masked
            # eště raz
            cmask = current_simplices==simplex_id
            # vyfiltrujeme
            current_simplices = current_simplices[~cmask]
    
    
            
        # zde je třeba перехватить ситуацию, куке одӥг но кандидат ӧвӧл
        # нужно ли? 
#        if len(current_simplices) == 0:
#            # nepovedlo. nic
#            bx.candidates = candidates[0:0]
#            # mě nenapadá žádný lepší způsob vrátit prázdnou matici
#            return candidates[0:0], len(candidates), -2 # simple_id
                
        # nemaskované, včetně současného kandidata (nevím proč) - ke kandidatům
        # землю - крестьянам, фабрики - рабочим
        # předpokladam, že kandidaty jsou se všim všudy
        # s vahami (.g_value) a se svým .implicit_multiplicator'em
        ## zde True hodnoty roušky - to co jíž bylo skryto
        bx.candidates = candidates[~np.ma.getmaskarray(found_simplices)][1:] # toho prvního prečo nechcem
        try: # na zacatku je tam prazdný f_model, kterému atribut pripsat nemůžeme
            bx.candidates.implicit_multiplicator = implicit_multiplicator
        except:
            pass
        
        # vrátíme kandidaty, všechny-ne všechny?
        # малы одӥг гинэ? уг тодӥськы чик...
        selected_candidate = candidates[~np.ma.getmaskarray(found_simplices)][:1] # chcem toho prvního
        
        
        # odešleme ISSI
        try:
            # pridame do seznamu známého
            # rouška musí zůstat z cyklu
            # proboha, Alexi, co to je za roušku, co se tu děje?
            # jakmile v tom hlavním cyklu nalezli jsme mix nebo outside
            # my hned z cyklu vylezli a je neskryli - abychom je vzali jako kandidaty
            # teď je však skryváme s tou "rouškou", co musela být před opuštěním cyklu nastavena
            # tak ISSI bude mít možnost odhadovat i pravděpodobnosti mix a outside
            found_simplices[mask] = np.ma.masked
            # zde získáme True hodnoty roušek
            # ukazatel
            imask = found_simplices.mask
            found_simplices.mask = ~imask # invertujem, dotkne to i samotnou imask
            events = found_simplices.compressed()
            print(candidates)
            print(candidates.g_values)
            print("imask", imask)
            print(candidates.g_values[~imask])
            print(events)
            bx.oiss.add_IS_serie(candidates.g_values[~imask], events, implicit_multiplicator)
            print("global estimation", bx.oiss.estimations)
            bx.ciss.add_IS_serie(candidates.g_values[~imask], events, implicit_multiplicator)
            print("current estimation", bx.ciss.estimations)
        except AttributeError:
            bx._logi("Это вы мне прислали неваженых кандидатов?")
        except UnboundLocalError: # čo tu chybu způsobuje?
            # asi nebyly žádné kandidaty (třeba hned na začátku)
            assert len(candidates)==0 and len(bx.candidates)==0, "AdaptiveCensoring: Что за бурда с этими кандидатама?"
            return candidates, 0, -2
            
        
        # rate = kolík bylo - kolik zůstalo
        return selected_candidate, len(candidates) - len(bx.candidates), simplex_id
            
       
    
    
    def get_candidates(bx, Nsim=int(1e4)):
        # -1 = 'out', 0=success, 1=failure, 2=mix
        
        # не мудрствуя лукаво
        user_pf = np.mean(bx.pf_lim)
        try:
            low_pf = bx.oiss.estimations[1] # failure
            upper_pf = 1 - bx.ciss.estimations[0] # sucess
            self_pf = (low_pf + upper_pf)/2
        except AttributeError:
            self_pf = 0.5
            
            # bereme *mean* od svého a uživatelského odhadu
            # minimum nejede
        sampling_r, __ = bx.sball.get_r_iteration(np.mean((self_pf, user_pf)))
        # asi tam bylo sampling_r/bx.base_r, že?
        # u stats.norm zadáváme směrodatnou odchylku, je to asi správné
        h = f_models.UnCorD([stats.norm(0, sampling_r/bx.base_r) for i in range(bx.nvar)])
        
        # for IS_stats
        svar = (sampling_r/bx.base_r)**2 # svar like sampling_variance
        # něco takovýho bych nahrubo placnul
        implicit_multiplicator = svar**bx.nvar * np.exp(bx.nvar/svar - bx.nvar)
            
        #
        # jdeme na to, koťě!
        #
        
        # zgenerujeme vzorky
        # nic zajimavýho
        h = h(Nsim)
        # dropneme priliš vzdálené kandidaty
        distance_from_zero = np.sum(h.R**2, axis=1)
        mask = distance_from_zero < bx.drop_r
        
        # a teď bacha!
        # tady musíme provést jeden trik
        to_sample = bx.f.new_sample(h.R[mask], 'G') # R-ko smerdžíme ako G-čko
        w = to_sample.pdf_G / h.pdf_R # snad je to správně
        # zabalme do boxu
        candidates = SampleBox(to_sample, w, 'BlackBox internal samples and weights')
        candidates.implicit_multiplicator = implicit_multiplicator
        # vahy máme, zbytek už nejsou naši starosti
        return candidates
       






class MinEnergyCensoredSampling(Censoring):
    # už mě to dědění nebaví
    # без поллитры не разберёшься, что этот слоёный пирог делает
    def __init__(bx, sample_object, tri_space='Rn', tree_space=None, sampling_space=None, kechato_space='U', \
                                        potencial='ksee', p_norm=2, budget=1000, simplex_budget=100):
        
        bx.sball = sball.Sball(sample_object.nvar)
        bx.base_r = bx.sball.get_r(0.5)
        
        if tree_space is None:
            bx.tree_space = tri_space
        else:
            bx.tree_space = tree_space
            
        if sampling_space is None:
            bx.sampling_space = tri_space
        else:
            bx.sampling_space = sampling_space
        
        bx.kechato_space = kechato_space
        # pro simplexy. Chcu ukladat jejich míry
        # viz. .regen()
        #bx.siss = IS_stat.ISSI()
        bx.budget = budget
        bx.simplex_budget = simplex_budget
        bx.p_norm = p_norm
        bx.potencial = potencial
        
        # for current candidates
        # kandidaty musí být 'judged' a 'assessed'
        # viz. regen()
        #bx.candidates_index = dict()
        # krám, přece třidíme odpad!
        bx.former_candidates = []
        bx.unjudged_candidates = []
        # user .candidates should be initializated in the base class
        # but we need to set additional attributes to them
        super().__init__(sample_object, tri_space)
        bx.candidates = CandyBox(bx.f())
        
        
        
        
    def regen(bx):
        """
        regen() recreates data structures of the box. 
        It shouldn't be called without reason, changed distribution, settings or so.
        """
        super().regen()
        # zás mám vyhodit odhady?
        bx.siss = IS_stat.ISSI() 
        bx.candidates_index = dict()
        
        sampled_plan_tree = getattr(bx.sample_box, bx.tree_space)
        bx.tree = spatial.cKDTree(sampled_plan_tree)
        
        if "tri" in dir(bx):
            # tri - Deloneho triangulace
            bx.simplex_events = bx.get_events()
            bx.estimate_outside()
            for simplex_id in range(bx.tri.nsimplex):
                # zde jen počítame
                bx.estimate_simplex(simplex_id)
                
                
        elif bx.nsim > 0: # požaduji, aby nějaké těčíčky byly vždy pritomné
            
            candidates = IS_stat.IS(bx.f, bx.h, space_from_h='R', space_to_f=bx.sampling_space,  Nsim=bx.budget)
            # nevím co tam bylo za h-ko, ale nechť IM zůstane 1
            implicit_multiplicator = 1
            
            # teoreticky lze
            #bx.siss.add_IS_serie(candidates.w, candidates.simplex, implicit_multiplicator)
        
            bx.assess_candidates(candidates)
            # uložíme
            bx.candidates_index[-1] = candidates
            
            
            
        
    
    
    def export_estimation(bx):
        bx.siss.get_estimations()
        simplices = np.array(tuple(bx.siss.estimations.keys()))
        probabilities = np.array(tuple(bx.siss.estimations.values()))
        
        estimation = dict()
        estimation[-1] = np.sum(probabilities[simplices == -1])
        
        # jevy aj klidně in-place (nerobím kopiju)
        events = simplices[simplices != -1]
        probabilities = probabilities[simplices != -1]
        
        # zhruba - get_events() vrací pole s odpovidajícími čísly jevů pro každý simplex, počineje od nuly
        # tím slajsingem my jakoby vybirame ke každemu nalezenemu simplexovi ten správnej mu odpovídajicí jev
        events = bx.simplex_events[events]
        
        for i in range(3): # kvůli 0,1,2 robiť cyklus?
            estimation[i] = np.sum(probabilities[events == i])
        
        bx.guessbox.guess('TRI_overall_estimations', bx.tri.npoints, estimation)
        
        
    def increment(bx, input_sample):
        # ну нахрен это ваше наследование-расследование
        
        # nechť bude, asi nikomu nevadí
        for i in range(bx.nvar):
            for j in range(len(input_sample)):
                plan_index = np.searchsorted(bx.sorted_plan_U[i], input_sample.U[j,i])
                bx.sorted_plan_U[i] = np.insert(bx.sorted_plan_U[i], plan_index, input_sample.U[j,i])
        
        #č strom posuneme sem    
        sampled_plan_tree = getattr(bx.sample_box, bx.tree_space)
        bx.tree = spatial.cKDTree(sampled_plan_tree)
        
        
        # fór je v tom, že tu triangulaci nemůžeme výtvořit hned na začátku
        if "tri" in dir(bx):
            # tri - Deloneho triangulace
            
            bx.export_estimation()
            
            # чыры-пыры
            # invalidujeme staré vzorky
            if -2 in bx.candidates_index:
                bx.former_candidates.append(bx.candidates_index.pop(-2))
            
            
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
            
            # invalidirujeme jejich odhady
            for simplex_id in changed_simplices_ids:
                bx.siss.delete_event_data(simplex_id)
                
                # popajem pouze mixy, ty musel jsem spočítat před aktualizací
            for simplex_id in changed_simplices_ids[mixed[changed_simplices_ids]]:
                bx.former_candidates.append(bx.candidates_index.pop(simplex_id))
                
            
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
            
            
            
            # přepočíst -1 v zavislosti na simplexu vstupního bodu
            try:
                # kontrola korrektní i v případě NaN
                test = input_sample.simplex > -1
                # эскером
                if not test.all():
                    bx.former_candidates.append(bx.candidates_index.pop(-1))
                    bx.siss.delete_event_data(-1)
                    bx.estimate_outside()
            except BaseException as e:
                msg = "input sample didn't provide correct 'simplex' attribute "
                error_msg = bx.__class__.__name__ + ": " + msg + repr(e)
                bx._logger(msg=error_msg)
                bx.former_candidates.append(bx.candidates_index.pop(-1))
                bx.siss.delete_event_data(-1)
                bx.estimate_outside()
                
                
            
            
            # pokud -2 jíž existuje, tak pro dnešek stačí
            if (-2 not in bx.candidates_index) and (len(bx.former_candidates) > 0):
                # nikdo nám neslibil, že u starých kandidatu 
                # třeba se nebude zvýšovat potanciál
                # (je to prostě, opravdu ríct, jednodušší)
                
                # prohrabeme odpad
                candidates = bx.former_candidates.pop()
                for i in range(len(bx.former_candidates)):
                    candidates.add_sample(bx.former_candidates.pop())
                for i in range(len(bx.unjudged_candidates)):
                    candidates.add_sample(bx.unjudged_candidates.pop())
                
                # hodil by se ještě nám?
                bx.judge_candidates(candidates)
                # profiltrujeme
                # -1 = 'out', 0=success, 1=failure, 2=mix
                candidates = candidates[candidates.event != 0] 
                candidates = candidates[candidates.event != 1] 
                # uvalíme pokutu
                bx.assess_candidates(candidates)
                #č někoho z tyto hromady dostaneme 
                for __ in range((bx.nvar+1)*2):
                    if len(candidates) > 0:
                        mc_id = collections.Counter(candidates.simplex).most_common()[0][0]
                        #č uložíme
                        bx.candidates_index[mc_id].add_sample(candidates[candidates.simplex == mc_id])
                        #č a teď bacha - ty co jsem uložil do simplexu nechcu v -2 videt
                        candidates = candidates[candidates.simplex != mc_id]
                    else:
                        break
                if len(candidates) > 0:
                    #č -2 je určen pro zbytky, кылем-мылем
                    bx.candidates_index[-2] = candidates
                
                
        else:
            bx._logger('Triangulace (zatím?) neexistuje')
            bx.regen()
        
        
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
            return bx.LHS_like_correction(bx.h(1))
        else:
            selected = bx.select_candidate()
            # hrubě ošidíme s takovejhlema usilima námi pěčlivě vybraný vzorečiček
            #selected.sampling_plan = bx.LHS_like_correction(selected)
            return selected
           
    
    
    def select_candidate(bx):
    
        # 
        # AUKCE, AUCTION    
        # 
        # for current candidates
        # kandidaty musí být 'judged' a 'assessed'
        highest_bid = 0 
        for candidates in bx.candidates_index.values():
            bids = getattr(candidates, bx.potencial)
            bid = np.max(bids)
            # side effect
            if bid > highest_bid:
                bidder = candidates[np.argmax(bids)]
                highest_bid = bid
        
        
        
        # probably, we shouldn't purge user candidates (if they are)
        # just every time evaluate them
        if len(bx.candidates) > 0:
            bx.judge_candidates(bx.candidates)
            bx.assess_candidates(bx.candidates)
            bids = getattr(bx.candidates, bx.potencial)
            # -1 = 'out', 0=success, 1=failure, 2=mix
            bids *= (bx.candidates.event == -1) + (bx.candidates.event == 2)
            bid = max(bids)
            # side effect
            if bid > highest_bid:
                bidder = bx.candidates[np.argmax(bids)]
                # ... кулэ ӧвӧл
        
        
        # já prečo spoléhám na ksee a psee potenciály
        # v tom, že nepřířadí vysoký potenciál 
        # vzorkům s nulovou hustotou
        return bidder
          
            
       
    
    
    def estimate_outside(bx):
        # předpokládám, že triangulece jíž existuje
         
        # -1 = 'out', 0=success, 1=failure, 2=mix
        #current outside probability estimation
        try:
            p_out = bx.siss.estimations[-1]
        except:
            p_out = 1/(bx.nsim + 1)
            bx._logger(msg="suppose p_out=1/(bx.nsim + 1)="+str(p_out))
        
        if p_out == 0:
            p_out = 1/(bx.nsim + 1)
            bx._logger(msg="suppose p_out=1/(bx.nsim + 1)="+str(p_out))
            
        if p_out > 0.5:
            # zužovat nechceme
            # trapit sa generacema taky ne
            candidates = IS_stat.IS(bx.f, bx.h, space_from_h='R', space_to_f=bx.sampling_space,  Nsim=bx.budget)
            
            # nevím co tam bylo za h-ko, ale nechť IM zůstane 1
            implicit_multiplicator = 1
            
        else: # tak deme... trapit sa generacema
            
            sampling_r, __ = bx.sball.get_r_iteration(p_out)
            # asi tam bylo sampling_r/bx.base_r, že?
            # u stats.norm zadáváme směrodatnou odchylku, je to asi správné
            h = f_models.UnCorD([stats.norm(0, sampling_r/bx.base_r) for i in range(bx.nvar)])
            
            # for IS_stats
            #svar = (sampling_r/bx.base_r)**2 # svar like sampling_variance
            # něco takovýho bych nahrubo placnul
            #implicit_multiplicator = svar**bx.nvar * np.exp(bx.nvar/svar - bx.nvar)
            implicit_multiplicator = np.inf
            candidates = IS_stat.IS(bx.f, h, space_from_h='R', space_to_f=bx.sampling_space,  Nsim=bx.budget)
                
                
        bx.judge_candidates(candidates)
        # odhady zlobily, zkusím jako multiplikator posílat nekonečno
        bx.siss.add_IS_serie(candidates.w, candidates.simplex, implicit_multiplicator=implicit_multiplicator)
        
        # odebereme kus práce u selectu
        # -1 = 'out', 0=success, 1=failure, 2=mix
        candidates = candidates[candidates.event != 0] 
        candidates = candidates[candidates.event != 1] 
        # uvalíme pokutu
        bx.assess_candidates(candidates)
        # uložíme
        bx.candidates_index[-1] = candidates[candidates.event == -1] 
        if len(candidates[candidates.event == 2]) > 0:
            # -2 je určen pro zbytky, кылем-мылем
            bx.candidates_index[-2] = candidates[candidates.event == 2] 
        
    
    
    def estimate_simplex(bx, simplex_id):
        """
        Delaunay triangulation
        """
        #bx._logger(msg="estimate simplex"+str(simplex_id))
        
        simplex = bx.tri.simplices[simplex_id]
        # чылкыт f_model
        vertices = bx.f_model[simplex]
        
        
        # already divided by nsim in variance formule
        # divide by /(nvar+1)/(nvar+2) from simplex inertia tensor solution
        # multiply by simplex_volume, but it looks like it shouldn't be here
        # for simplex: d = nvar+2 
        # sice to má nazev h_plan, ale nese rozdělení a hustoty v f-ku
        h_plan = IS_stat.IS_like(vertices, sampling_space=bx.sampling_space, nis=bx.simplex_budget, d=bx.nvar+2)
        
        # nejdřív vyfiltrujeme vzorky, pak budeme řešit hustoty
        #
        h_plan_model = getattr(h_plan, bx.tri_space)
        vertices_model = getattr(vertices, bx.tri_space)
        
        # budeme pokažde sestavovat triangulaci z jedného simplexu
        # a rešit jen zda naši bodíky "inside or outside"
        # (s narustajícím nsim tohle brzy se stavá rychlejším než bežný dotaz)
        found_simplices = spatial.Delaunay(vertices_model).find_simplex(h_plan_model)
        
        # ten simplex nic neznamená, asi nebudu jej použivat
        h_plan.simplex = found_simplices
            
        # uvnitř simplexu - mel by tam bejt pouze jeden, "nulový" simplex
        mask = found_simplices == 0
        
        
        # necháme ISSI trapit sa pravděpodobnostma
        bx.siss.add_single_event_data(h_plan.w[mask], event=simplex_id, nis=bx.simplex_budget)
        
        
        # je nejvyšší čas zjistit čo to byl za utvar
        
        # fp like a failure points. Number of failure points
        # intersect 2 times faster than setdiff (in my tests)
        fp = len(np.intersect1d(simplex, bx.sample_box.failure_points, assume_unique=True))
        # -1 = 'out', 0=success, 1=failure, 2=mix
        if fp == bx.nvar + 1:
            pass
            #event = 'failure'
            #event_id = 0
        elif fp == 0:
            pass
            #event = 'success'
            #event_id = 1
        else:
            #event = 'mix'
            event_id = 2
            
            candidates = h_plan[mask]
            candidates.event = np.full(len(candidates), event_id, dtype=np.int8)
            # a vyhodnotíme je
            bx.assess_candidates(candidates)
            # vzorky je třeba přidát ke kandidatům
            # jako, nic nepokazí, ale čo tam připadně bylo - přepíše
            bx.candidates_index[simplex_id] = candidates
            
            
        
        # vzorky je třeba přidát ke kandidatům
        # zás nakladaní s odpadem...
        bx.unjudged_candidates.append(h_plan[~mask])
            
            
            
        
        
        
    
        # potřebuju nová slovesa
    def assess_candidates(bx, candidates):
        candidates.nsim_stamp = np.full(len(candidates), bx.nsim)
    
        candidates_tree = getattr(candidates, bx.tree_space)
        dd, ii = bx.tree.query(candidates_tree, k=1, p=bx.p_norm)
        candidates.dd = dd
        candidates.ii = ii
        
        PDFs = bx.sample_box.pdf(bx.tree_space)
        # teď máme hustoty kandidatů a prislušejicích jím vzorků
        PDF = PDFs[ii]
        pdf = candidates.pdf(bx.tree_space)
        
        # кучапи
        # psí-kučapí není invariántní vůči lineárním transformácím
        candidates.psee = np.sqrt(pdf*PDF) * np.power(dd , bx.nvar)
        
        # кечато
        # ksí-kěčató není invariántní vůčí rotacím
        ksee = np.empty(len(candidates))
        for i in np.unique(ii):
            # doufám, že je to legální
            ksee[i==ii] = lk.kechato_potential(bx.f_model[i], candidates[i==ii], kechato_space=bx.kechato_space)
        candidates.ksee = ksee
        
        
        
    
    
    # ještě by asi hodily funkce pro pridaní uživatelských kandidatů
    # funkce, která přídává dálší kandidaty? outside sampling
    
    
    def judge_candidates(bx, candidates):
    
        candidates_tri = getattr(candidates, bx.tri_space)
            
        found_simplices = bx.tri.find_simplex(candidates_tri)
        
        candidates.simplex = found_simplices
        events = found_simplices.copy()
        # black magic
        # zhruba - get_events() vrací pole s odpovidajícími čísly jevů pro každý simplex, počineje od nuly
        # tím slajsingem my jakoby vybirame ke každemu nalezenemu simplexovi ten správnej mu odpovídajicí jev
        events[found_simplices >= 0] = bx.simplex_events[found_simplices[found_simplices >= 0]]
        candidates.event = events
        
        
    




class OptimizedCensoredSampling(MinEnergyCensoredSampling):


    def regen(bx):
        """
        regen() recreates data structures of the box. 
        It shouldn't be called without reason, changed distribution, settings or so.
        """
        if bx.nsim > bx.nvar + 1:
            try:
                bx.convex_hull = spatial.ConvexHull(getattr(bx.sampled_plan, bx.tri_space), incremental=True)
            except BaseException as e:
                    msg = "error of creating ConvexHull "
                    error_msg = bx.__class__.__name__ + ": " + msg + repr(e)
                    bx._logger(msg=error_msg)
        
        super().regen()
            
            
            
    
        
        
    def increment(bx, input_sample):
        #☺ ну нахрен это ваше наследование-расследование
        
        #č nechť bude, asi až tak nevadí
        for i in range(bx.nvar):
            for j in range(len(input_sample)):
                plan_index = np.searchsorted(bx.sorted_plan_U[i], input_sample.U[j,i])
                bx.sorted_plan_U[i] = np.insert(bx.sorted_plan_U[i], plan_index, input_sample.U[j,i])
            
        #č strom posuneme sem    
        sampled_plan_tree = getattr(bx.sample_box, bx.tree_space)
        bx.tree = spatial.cKDTree(sampled_plan_tree)
        
        #č fór je v tom, že tu triangulaci nemůžeme výtvořit hned na začátku
        if "tri" in dir(bx):
            # tri - Deloneho triangulace
            
            bx.export_estimation()
            
            
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
            
            # invalidirujeme jejich odhady
            for simplex_id in changed_simplices_ids:
                bx.siss.delete_event_data(simplex_id)
                
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
            
            bx.convex_hull.add_points(getattr(input_sample, bx.tri_space))
            #č přepočíst -1 v zavislosti na simplexu vstupního bodu
            try:
                #č kontrola korrektní i v případě NaN
                test = input_sample.simplex > -1
                #♥ эскером
                if not test.all():
                    bx.former_candidates.append(bx.candidates_index.pop(-1))
                    bx.siss.delete_event_data(-1)
                    bx.estimate_outside()
            except BaseException as e:
                msg = "input sample didn't provide correct 'simplex' attribute "
                error_msg = bx.__class__.__name__ + ": " + msg + repr(e)
                bx._logger(msg=error_msg)
                bx.former_candidates.append(bx.candidates_index.pop(-1))
                bx.siss.delete_event_data(-1)
                bx.estimate_outside()
                
                
            
            #č prohrabeme odpad
            bx._judge_unjudged(bx.unjudged_candidates)
            bx._judge_unjudged(bx.former_candidates)
                
                
                
                
        else:
            bx._logger('Triangulace (zatím?) neexistuje')
            bx.regen()
            
    
    
    def _judge_unjudged(bx, list):
        for i in range(len(list)):
            candidates = list.pop()
            bx.is_outside(candidates)
            
            mask = candidates.is_outside
            if np.any(mask): #č pokud aspoň jeden bydlí mimo Brno
                candidates = candidates[mask]
                candidates.simplex = candidates.event = np.full(len(candidates), -1, dtype=np.int8)
                #č vyhodnotíme
                bx.assess_candidates(candidates)
                #č vzorky je třeba přidát ke kandidatům
                # jako, nic nepokazí, ale čo tam připadně bylo - přepíše
                bx.candidates_index[-1].add_sample(candidates)
    
    
    
    def estimate_outside(bx):
        # předpokládám, že triangulece jíž existuje
        
        # -1 = 'out', 0=success, 1=failure, 2=mix
        #current outside probability estimation
        try:
            p_out = bx.siss.estimations[-1]
        except:
            p_out = 1/(bx.nsim + 1)
            bx._logger(msg="suppose p_out=1/(bx.nsim + 1)="+str(p_out))
        
        if p_out == 0:
            p_out = 1/(bx.nsim + 1)
            bx._logger(msg="suppose p_out=1/(bx.nsim + 1)="+str(p_out))
        
        #
        # get candidates!
        # 
        if p_out > 0.5:
            # zužovat nechceme
            # trapit sa generacema taky ne
            candidates = IS_stat.IS(bx.f, bx.h, space_from_h='R', space_to_f=bx.sampling_space,  Nsim=bx.budget)
            
            # nevím co tam bylo za h-ko, ale nechť IM zůstane 1
            #implicit_multiplicator = 1
            
        else: # tak jdeme... trapit sa generacema
            
            sampling_r, __ = bx.sball.get_r_iteration(p_out)
            # asi tam bylo sampling_r/bx.base_r, že?
            # u stats.norm zadáváme směrodatnou odchylku, je to asi správné
            h = f_models.UnCorD([stats.norm(0, sampling_r/bx.base_r) for i in range(bx.nvar)])
            candidates = IS_stat.IS(bx.f, h, space_from_h='R', space_to_f=bx.sampling_space,  Nsim=bx.budget)
                
        bx.is_outside(candidates)
        candidates = candidates[candidates.is_outside]
        
        
        #č řeším problém, že při načítaní ze souboru
        #č blackbox nemá adekvatní odhad Brno-venkova
        while len(candidates) < 2:
            p_out = p_out/2
            bx._logger(msg="suppose p_out="+str(p_out))
            
            sampling_r, __ = bx.sball.get_r_iteration(p_out)
            # asi tam bylo sampling_r/bx.base_r, že?
            # u stats.norm zadáváme směrodatnou odchylku, je to asi správné
            h = f_models.UnCorD([stats.norm(0, sampling_r/bx.base_r) for i in range(bx.nvar)])
            candidates = IS_stat.IS(bx.f, h, space_from_h='R', space_to_f=bx.sampling_space,  Nsim=bx.budget)
                    
            bx.is_outside(candidates)
            candidates = candidates[candidates.is_outside]
        
        
        
        #č necháme ISSI trapit sa pravděpodobnostma
        bx.siss.add_single_event_data(candidates.w, event=-1, nis=bx.budget)
        
        candidates.simplex = candidates.event = np.full(len(candidates), -1, dtype=np.int8)
            
            
        #č vyhodnotíme
        bx.assess_candidates(candidates)
        # vzorky je třeba přidát ke kandidatům
        # jako, nic nepokazí, ale čo tam připadně bylo - přepíše
        bx.candidates_index[-1] = candidates
            
    
          

    def is_outside(bx, candidates):
    
        x = getattr(candidates, bx.tri_space)
        
        #E [normal, offset] forming the hyperplane equation of the facet (see Qhull documentation for more)
        A = bx.convex_hull.equations[:,:-1]
        b = bx.convex_hull.equations[:,-1]
        
        # N=nsim
        NxN = A @ x.T + np.atleast_2d(b).T
        mask = np.any(NxN > 0, axis=0)
        candidates.is_outside = mask






#č alternativní název je 
#:) UltimateFastOptimizationOptimizedMinDistanceEnergyAdaptiveCensoringSampling
class BlackSimpleX(OptimizedCensoredSampling):
    
    def increment(bx, input_sample):
        #☺ ну нахрен это ваше наследование-расследование
        
        #č nechť bude, asi až tak nevadí
        for i in range(bx.nvar):
            for j in range(len(input_sample)):
                plan_index = np.searchsorted(bx.sorted_plan_U[i], input_sample.U[j,i])
                bx.sorted_plan_U[i] = np.insert(bx.sorted_plan_U[i], plan_index, input_sample.U[j,i])
            
            
        #č strom posuneme sem    
        sampled_plan_tree = getattr(bx.sample_box, bx.tree_space)
        bx.tree = spatial.cKDTree(sampled_plan_tree)
        
        
        #č fór je v tom, že tu triangulaci nemůžeme výtvořit hned na začátku
        if "tri" in dir(bx):
            # tri - Deloneho triangulace
            
            
            
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
            
            
            bx.convex_hull.add_points(getattr(input_sample, bx.tri_space))
            #č přepočíst -1 v zavislosti na simplexu vstupního bodu
            try:
                #č kontrola korrektní i v případě NaN
                test = input_sample.simplex > -1
                #♥ эскером
                if not test.all():
                    bx.former_candidates.append(bx.candidates_index.pop(-1))
                    bx.siss.delete_event_data(-1)
                    bx.estimate_outside()
            except BaseException as e:
                msg = "input sample didn't provide correct 'simplex' attribute "
                error_msg = bx.__class__.__name__ + ": " + msg + repr(e)
                bx._logger(msg=error_msg)
                bx.former_candidates.append(bx.candidates_index.pop(-1))
                bx.siss.delete_event_data(-1)
                bx.estimate_outside()
                
                
            
            #č prohrabeme odpad
            bx._judge_unjudged(bx.unjudged_candidates)
            bx._judge_unjudged(bx.former_candidates)
                
            
            
            #č A ještě...
            # 
            highest_bid = 0 
            for i, candidates in bx.candidates_index.items():
                bids = getattr(candidates, bx.potencial)
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
                        bids = getattr(candidates, bx.potencial)
                        bid = np.max(bids)
                        if bid > highest_bid:
                            highest_bid = bid
                    
                    else:
                        highest_bid = bid
                
                
        else:
            bx._logger('Triangulace (zatím?) neexistuje')
            bx.regen()
            
            
            
        
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
        
        if (bx.tri_space == bx.tree_space) and (bx.potencial == 'psee'):
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
        
        if bx.potencial == 'psee':
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



#♥♥♥♥♥♥
# BlackBoxiCheck
class KechatoLukiskon(BlackBox):
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
class KechatoTwoPointLukiskon(BlackBox):
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



