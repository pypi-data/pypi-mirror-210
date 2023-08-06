#!/usr/bin/env python
# coding: utf-8

"""
"""


import numpy as np
import collections # for defaultdict
#from scipy import optimize # it was needed for spring solution
from .candybox import CandyBox
from scipy import stats # for sample_like()
from . import f_models # for sample_like()
from .spring import get_spring_solution # for new IS function, for ISSI in future
from .welford import Welford # for PushAndPull




def get_1DS_sample(f, x_sub):
    """1DS stands for 1D sampling.
    1DS is, actually, an importance sampling method
    that, actually, does not calculate IS weights
    as f_density / h_density, but
    (arbitrary, nonuniformly) divides interval to subintervals.
    By using CDF (SF, actually) transformes subintervals 
    to 0-1 uniform probability line.
    Then gets one node as middle point of every subinterval,
    weights therefore are just interval widths itself.
    No sampling imprecisions are introduced, 
    therefore no spring, no correction are needed. 
    Usage:
    Function takes: f, x
    f: univariate (1D) distribution (scipy-compatible)
    x_sub: coordinates (n+1) of subintervals.
    Returns: x, weights
    x: n coordinates
    weights: same as IS weights
    """
    # x: 1, 2, 3
    # SF: 0.1, 0.01, 0.001
    u_sub = f.sf(x_sub)
    weights = u_sub[:-1] - u_sub[1:]
    np.abs(weights, out=weights)
    u = (u_sub[:-1] + u_sub[1:])
    #č u musí být float
    #č takže dělení dvěma nemusí robiť potíže 
    np.divide(u, 2, out=u)
    x = f.isf(u)
    return x, weights

#č chcu udělat menší IS funkci s výrovnáním odhadů
#č Síce tohle už umí ISSI, 
#č třída ale neočekává celkovou pravděpodobnost odlišnou od nuly.
#č Taky jeji funkcionalita je hodně přebytečná pro Ghull.
#č Zkratka, chcu funkci, která by na vstupu brala:
#č 1. vahy IS (tj. funkce nebude řešít souřadnice a hustoty)
#č 2. roušku (omezíme se na nejčastější případ dvou vzajemně vyloučujících jevů) a
#č 3. celkovou pravděpodobnost
#č a posleze vracela výrovnané odhady

def get_IS_estimation(weights, mask, p_overall=1):
    """Function calculates Importance Sampling estimators
    of two mutually excludive events (typical for indicator or Heaviside step function). 
    It performs correction based on a priory known overall probability.
    It takes numpy array of IS weghts (PDF / weighting function density),
    numpy boolean array and a priory known overall probability.
    Returns corrected estimators for true_event and false_event"""
    
    #č vstupní kontroly
    if np.all(mask): #č všecko je pravda - není co řešit
        return p_overall, 0
    if not np.any(mask): #č není žádná pravda - není žádné překvapení
        return 0, p_overall
    
    Nsim = len(weights)
    # there are two events:
    true_masked = weights[mask]
    false_masked = weights[~mask]
    #č podle IS vzorečků
    #č když uživatel bude hodně snažit, tak
    #č v mat. očekaváních může zajistit nuly
    #č nechcu zatím řešit
    true_mean = np.sum(true_masked)/Nsim
    false_mean = np.sum(false_masked)/Nsim
    if (true_mean + false_mean) == p_overall:
        return true_mean, false_mean
    #č podle toho, co vidím ve vzorcích - mám pocit, že se
    #č nůlový rozptyl může vyskytnout pouze v případě Nsim == 1, což
    #č zde od uživatele neočakávám. Nebo spolu s nulovým průměrem,
    #č který zatím taky nechcu řešit.
    #č (Ten ISSI je teda hrozně перемудрёный, řeší bůhvíco)
    #č Zde to nepotřebujem, udělame všecko jednoduše.
    true_var = (np.sum(true_masked**2)/Nsim - true_mean**2) / Nsim
    false_var = (np.sum(false_masked**2)/Nsim - false_mean**2) / Nsim
    
    #č pošleme to pružině. Ta je obecnější, na větší počet jevů
    #č proto bere jako vstup numpy matice
    lenghts = np.array((true_mean, false_mean))
    flexibilities = np.array((true_var, false_var))
    #č vrací taky numpy
    ls = get_spring_solution(lenghts, flexibilities, L=p_overall)
    #č rozbalíme 
    #č (na rovinu, dělám to jen aby pak kód bylo možné jednoduše přečíst)
    true_corrected_mean, false_corrected_mean = ls
    
    return true_corrected_mean, false_corrected_mean #(*ls,)




# One does not simply get IS estimations...
#č Získat IS odhady není natolik snadné...
#č Ghull totiž integruje po částech
#č a mně příšlo, že nejsprávnější volbou
#č bude i odhady zpracovavat po částech.
#č Musel jsem tedy vytvořit třídu (Welford) pro
#č průběžný výpočet průměrů a rozptylů.
#č Teď na jeji bazí postavíme IS odhadovačku
class PushAndPull: #ё Тяни-Толкай
    """Class calculates corrected Importance Sampling estimators
    of two mutually excludive events (typical for indicator or Heaviside step function). 
    It performs correction based on a priory known overall probability.
    It takes numpy array of IS weghts (PDF / weighting function density),
    numpy boolean array and a priory known overall probability."""
    def __init__(self):
        self.true_wf = Welford()
        self.false_wf = Welford()
    
    def add(self, weights, mask):
        #č add_sparse() - právě pro IS,
        #č aby se uvnitř netrapilo nulama
        n = len(mask)
        self.true_wf.add_sparse(weights[mask], n)
        self.false_wf.add_sparse(weights[~mask], n)
       
    @property 
    def mean(self):
        return self.true_wf.mean, self.false_wf.mean
        
    @property 
    def var(self):
        #č otazkou je rozptyl čeho tady máme na mysli
        #č Já bych zde spíše očekával rozptyl průměru
        #č takže rozptyl vah IS vydělíme celkovým počtem měření
        assert self.true_wf.n == self.false_wf.n
        true_var = self.true_wf.s2 / self.true_wf.n
        false_var = self.false_wf.s2 / self.false_wf.n
        return true_var, false_var
    
    def correct_means(self, p_overall=1):
        """Method calculates Importance Sampling estimators
        of two mutually excludive events. 
        It performs correction based on a priory known overall probability.
        It takes as a optional parameter a priory known overall probability.
        Returns corrected estimators for true_event and false_event"""
        
        # there are two events:
        true_mean = self.true_wf.mean
        false_mean = self.false_wf.mean
        #č vstupní kontroly
        if (true_mean + false_mean) == p_overall:
            return true_mean, false_mean
        if (true_mean == 0) and (false_mean == 0):
            half = p_overall / 2
            return half, half #č půl na půl
        if true_mean == 0: 
            return 0, p_overall
        if false_mean == 0: 
            return p_overall, 0
        
        
        #č Nulové rozptyly neřeším - neumím představit, za jakých 
        #č podmínek by mohly ve skutečné aplikaci výskytnout 
        #č (variana s jediným vzorkem mně nezajimá)
        #č striktně vzato, musíme zde vydělit počtem měření
        #č ale vysledek se dělením na stejné číslo nezmění.
        #č Dokonce můžeme se spokojit i prostě součtemi kvadratů
        true_var = self.true_wf.S
        false_var = self.false_wf.S
        
        #č pošleme to pružině. Ta je obecnější, na větší počet jevů.
        #č Proto bere jako vstup numpy matice
        lenghts = np.array((true_mean, false_mean))
        flexibilities = np.array((true_var, false_var))
        #č vrací taky numpy
        ls = get_spring_solution(lenghts, flexibilities, L=p_overall)
        #č rozbalíme 
        #č (na rovinu, dělám to jen aby pak kód bylo možné jednoduše přečíst)
        true_corrected_mean, false_corrected_mean = ls
        
        return true_corrected_mean, false_corrected_mean #(*ls,)
    
    
    
    

#č ISS a ISSI by bylo vhod předělat na spring a 
#č vyhodit ty blbosti s půlením intervalů.
#č Nechám to na potom, po zakroku by bylo potřebné 
#č všecko dobře otestovat, teď na to nemám ani kapacitu, ani zajem
#č Goal&Ghull ISSI nepotřebuje.

# bisect function is taken from somewhere in internet. 
# https://www.quora.com/How-does-one-correctly-compare-two-floats-in-Python-to-test-if-they-are-equal
# Hope it is not big issue.
def bisect(f, target, low, high):
    low, high = float(low), float(high)
    while low != high:
        mid = (low + high) / 2
        f_mid = f(mid)
        if f_mid == target:
            return mid
        elif f_mid > target:
           high = mid if mid != high else low
        else:
           low = mid if mid != low else high
    return low
    

#ё нам позарез нужен ещё один, свой собственный словник 
#č ten, na rozdil od defaultdict'a, neuklada chybejicí složky do slovníku
class DefaultDict(dict):
    def __init__(self, default_value=None):
        self.default_value = default_value
        
    def __missing__(self, key):
        return self.default_value
    
    
#
#č deme na to, koťě!
#
    
    #č IS, (n-2)-krátá realizace, n>>2, n→∞
def IS(f, h_model, space_from_h='R', space_to_f='G',  Nsim=int(1e4)):
    """
    space_from_h
    space_to_f
    matching - v jakých souřadnicích robím merge a jaká PDF použiváme?
    """
    
    
    # zgenerujeme vzorky
    # nic zajimavýho
    h = h_model(Nsim)
    
    
    # tady musíme provést jeden trik
    # totež jako v IS_like - ve výsledku dycky dostaneme f_model
    to_sample = f.new_sample(getattr(h, space_from_h), space_to_f) # R-ko smerdžíme ako G-čko
    w = to_sample.pdf(space_to_f) / h.pdf(space_from_h) # snad je to správně
    
    # vahy máme
    # zabalme do boxu
    # zbytek už nejsou naši starosti
    return CandyBox(to_sample, w=w)
        


def get_norm_plan(nis, nvar, mean=0, std=1, design=None):
    """
    mean: [0.05, 2, 100500]
    std: [0.05, 2, 100500]
    
    design(nis, nvar) should return sampling plan in hypercube (U space)!
    """
    
    if design is None:
        sampling_plan_G = np.random.randn(nis, nvar)
    else: #оӵ я, ярам, гиперкуб. Кинлэсь меда Гаусс вӧлмэтын дизайн куром на?
        #č transformací z U prostoru dochází ke ztratě přesnosti 
        #č a omezenému na 8.2 poloměru v Gaussovském prostoru.
        #č Jenže jsem si uvědomil, že těžko na to narazím,
        #č projevilo by se to při počtu vzorků řadově 10**15,
        #č to bych musel tejden generovat vzorky
        sampling_plan_G = stats.norm.ppf(design(nis, nvar))
    
    
    #č pdf spočteme na původním Gaussovském designu
    # sample_pdf(sample / alpha) / np.prod(alpha)
    
    ## desired: pdf = np.prod(stats.norm.pdf(sampling_plan_G) / std, axis=1)
    pdf = stats.norm.pdf(sampling_plan_G)
    pdf = np.divide(pdf, std, out=pdf)
    pdf = np.prod(pdf, axis=1)
    
    
    #č a teď pustíme se do výpočtu souřadnic
    ## desired: sampling_plan_N = (sampling_plan_G * std) + mean
    sampling_plan_N = sampling_plan_G; del(sampling_plan_G)
    sampling_plan_N = np.multiply(sampling_plan_N, std, out=sampling_plan_N)
    sampling_plan_N = np.add(sampling_plan_N, mean, out=sampling_plan_N)
    
    return sampling_plan_N, pdf


def IS_norm(f, mean=0, std=1, sampling_space='G', nis=1000, design=None):
    """
    mean: [0.05, 2, 100500]
    std: [0.05, 2, 100500]
    
    design(nis, nvar) should return sampling plan in hypercube (U space)!
    """
    
    sampling_plan_N, pdf = get_norm_plan(nis, f.nvar, mean, std, design)
    
    #č tady musíme provést jeden trik
    #č totež jako v IS_like - ve výsledku dycky dostaneme f_model
    to_sample = f.new_sample(sampling_plan_N, sampling_space) #č naše N-ko smerdžíme ako G-čko
    w = to_sample.pdf(sampling_space) / pdf #č snad je to správně
    
    #č vahy máme
    #č zabalme do boxu
    #č zbytek už nejsou naši starosti
    return CandyBox(to_sample, w=w)



    # for simplex: d = nvar+2 
    # for cell: d = base_r**2
def IS_like(f_plan, sampling_space='G', weights=None, nis=1000, d=1, design=None):
    """
    takes sample and returns sampling plan with the same cov (in case d=1)
    covariance matrix we'll divide by d
    """
    
    plan = getattr(f_plan, sampling_space)
    
                
    S_bc = np.cov(plan, rowvar=False, bias=True, aweights=weights)
    barycenter = np.average(plan, axis=0, weights=weights)
    
    
    #č matika
    w, v = np.linalg.eig(S_bc)
    
    # use IS sampling density with center equal to the simplex's barycenter
    # set the minimum distance as the standard deviation of IS densisty
    #č u stats.norm zadáváme směrodatnou odchylku, to je asi správné
    sigmas = np.sqrt(w/d) 
    mean = 0
    h_plan_N, pdf_N = get_norm_plan(nis, f_plan.nvar, mean, sigmas, design)
    
    #ёӵ здесь уже так легко не отделаемся. Трансформовать кароно.
    h_plan_bc = (v @ h_plan_N.T).T
    h_plan_sing = h_plan_bc + barycenter
    
    
    
    #č sice to má nazev h_plan, ale nese rozdělení a hustoty v f-ku
    #
    #č jelikož výtvaříme nový vzorek z "čístých" souřadnic
    #č máme zaručeno, že h_plan vždy bude f_modelem (podle současného kódu CandyBox)
    h_plan = f_plan.new_sample(h_plan_sing, sampling_space) 
    ## desired: w = h_plan.pdf(sampling_space) / pdf_N # snad je to správně
    w = np.divide(h_plan.pdf(sampling_space), pdf_N, out=pdf_N); del(pdf_N)
    
    #č vahy máme
    #č zabalme do boxu
    #č zbytek už nejsou naši starosti
    return CandyBox(h_plan, w=w)






    # for simplex: d = nvar+2 
    # for cell: it's not so easy
def sample_alike(plan, weights=None, nis=1000, d=1, design=None):
    """
    takes sample and returns sampling plan with the same cov (in case d=1)
    covariance matrix we'll divide by d
    
    Returns: sampling_plan, h_pdfs
    """
    nsim, ndim = plan.shape
    
    #ё зрада отменяется!
    #č Tahle funkce se pokusí aspoň něco nejak navzorkovat,
    #č ale musí být aspoň-alespoň dva vzorky.
    #č nechvám zodpovědnost za to na volajícím kódě!
    assert nsim > 1
    
    S_bc = np.cov(plan, rowvar=False, bias=True, aweights=weights)
    barycenter = np.average(plan, axis=0, weights=weights)
    
    
    
    if nsim < ndim + 1:
        S2 = np.diag(S_bc)
        if not np.all(S2 > 0):
            std = np.sqrt(np.sum(S2) / ndim / d) 
        else:
            std = np.sqrt(S2 / d)
        return get_norm_plan(nis, ndim, mean=barycenter, \
                    std=std, design=design)
                
    
    #č matika
    w, v = np.linalg.eig(S_bc)
    
    if not np.all(w > 0):
        S2 = np.diag(S_bc)
        if not np.all(S2 > 0):
            std = np.sqrt(np.sum(w) / ndim / d) 
        else:
            std = np.sqrt(S2 / d)
        return get_norm_plan(nis, ndim, mean=barycenter, \
                    std=std, design=design)
    
    # use IS sampling density with center equal to the simplex's barycenter
    # set the minimum distance as the standard deviation of IS densisty
    #č u stats.norm zadáváme směrodatnou odchylku, to je asi správné
    sigmas = np.sqrt(w/d) 
    mean = 0
    h_plan_N, pdf_N = get_norm_plan(nis, ndim, mean, sigmas, design)
    
    #ёӵ здесь уже так легко не отделаемся. Трансформовать кароно.
    h_plan_bc = (v @ h_plan_N.T).T
    h_plan_sing = h_plan_bc + barycenter
    
    return h_plan_sing, pdf_N


            
#č tím "TrueIS" bylo myšleno abosolutně matematicky korektní 
#č započítávání sad vzorků, vybraných z libovolných (navzajem odlišných)
#č rozdělení IS. 
#č To je v literatuře známo jako "multiple importance sampling"
#č Tahle třída (na rozdil od ISSI) musí udržovat v paměti souřadnice všech 
#č předchozích sad vzorku a jejich rozdělení.
#č Tím se to líší od ISSI, která počíta ze sad pouze statistiky 
#č a ukladá pouze průměry a rozptyly.
#č S touhle třídou se hralo v době prvních hraček s rejection samplingem
#č a bylo to spíše takový proof-of-concept, u kterého jsem uviděl, že funguje,
#č ale žádné extensivní testování nikdy nebylo provedeno a třída nikdy nebyla
#č skutečně použita v kódu WellMet.
#č Tehdy problemem bylo to, že pro učely rejection samplingu by bylo třeba
#č ukladat nejen souřadnice a rozdělení, ale ještě navic i stavy 
#č přislušných triangulací, což bylo už i pro mně moc. 

#č Má nějakou alfu, která "not used", netuším, k čemu sloužila.
#č Má metody pro výpočet vah a pro výpočet odhadů s (bacha!) úpravenými vzorečky. 
class TrueIS:
    def __init__(self, f, IS_mode='G'):
        self.f_sample = f()
        self.series_data = []
        self.IS_mode = IS_mode
        self.events = []
        
    def add_IS_serie(self, sample, events, alpha=1):
        """
        alpha is for rejection sampling, not used
        """
        self.series_data.append((sample, events, alpha))
        self.events += events
        if self.IS_mode == 'R':
            # jestli máme to právé vzorkovácí rozdělení - tak nemáme čo robiť
            self.f_sample.add_sample(sample) # smerdží se to po R
            # w like weights
            #wt.w = to_sample.pdf_R / wt.h.pdf_R
        else: #IS_mode == 'G':
            # tady musíme provést jeden trik
            self.f_sample.add_sample(sample.R, 'G') # R-ko smerdžíme ako G-čko
            #wt.w = to_sample.pdf_G / wt.h.pdf_R # snad je to správně
        
        
    def get_weights(self):
        accu_denom_w = np.zeros(self.f_sample.nsim, dtype=float)
        if self.IS_mode == 'R':
            for serie in self.series_data:
                h_sample, events, alpha = serie
                h = h_sample.new_sample(self.f_sample)
                accu_denom_w += h.pdf_R * h_sample.nsim
            return self.f_sample.pdf_R / accu_denom_w, self.events
                
        else: # IS_mode == 'G'
            for serie in self.series_data:
                h_sample, events, alpha = serie
                h = h_sample.new_sample(self.f_sample.G, 'R')
                accu_denom_w += h.pdf_R * h_sample.nsim
            return self.f_sample.pdf_G / accu_denom_w, self.events
                
        
    def get_means(self):
        w, events = self.get_weights()
        keys = np.unique(events)
        Nsim = len(w)
        
        means = np.empty(len(keys), dtype=float)
        vars = np.empty(len(keys), dtype=float)
        
        
        # tak bacha
        ev = np.array(events)
        for key, i in zip(keys, range(len(keys))):
                
            mask = ev==key
            ev_w = w[mask]
            # podle IS vzorečků (skoro)
            key_mean = np.sum(ev_w)
            key_var = (np.sum(ev_w**2)*Nsim - key_mean**2) / Nsim
                
            # uložime
            means[i] = key_mean
            vars[i] = key_var
            
            # vyfiltrujeme zbytek
            w = w[~mask]
            ev = ev[~mask]
        
        # kontrola  
        assert len(w)==0 and len(ev)==0, "Что за хренотень?!"
        
        return means, vars
        

class ISSI:
    """
    IS statistics = weights series + events
    ISSI calculates probabilities of repeated IS series
    with implicit (non-zero) variances
    
    zda se mi, že tím nelze nic zhoršit
    """
    #č mám pocit, že je tu někde bug pythonu
    #č ten prazdnej list [] přežije cokoliv
    def __init__(self, events=None):
        """
        """ 
        self.series_data = []
        if events is None:
            self.events = []
        else:
            self.events = events
        
    def add_IS_serie(self, weights, events, implicit_multiplicator=1):
        keys = np.unique(events)
        Nsim = len(weights)
        
        # vytvoříme slovník pro sadu vzorků, který implicitně
        # bude předpokládát průměr=0 a rozptyl 1/Nsim^2 
        # pro všecko, co se v sadě neobjevilo
        if Nsim == 1:
            # jedno meření je taky měření)
            implicit_var = implicit_multiplicator
        else:
            implicit_var = implicit_multiplicator*(1-1/Nsim)/Nsim**2
        serie = DefaultDict((0, implicit_var))
        
        # tak bacha
        w = np.array(weights)
        ev = np.array(events)
        for key in keys:
            if key not in self.events:
                self.events.append(key)
                
            mask = ev==key
            ev_w = w[mask]
            # podle IS vzorečků
            key_mean = np.sum(ev_w)/Nsim
            key_var = (np.sum(ev_w**2)/Nsim - key_mean**2) / Nsim
            if key_var == 0: # to nechcem
                key_var = implicit_var
                
            # uložime
            serie[key] = (key_mean, key_var)
            
            # vyfiltrujeme zbytek
            w = w[~mask]
            ev = ev[~mask]
        
        # kontrola  
        assert len(w)==0 and len(ev)==0, "Что за хренотень?!"
        
        self.series_data.append(serie)
        
        # ачиз значение утёз
        self.get_estimations()
        
        
        
    def add_single_event_data(self, weights, event, nis=None, implicit_multiplicator=np.inf):
        
        if nis is None:
            Nsim = len(weights)
        else:
            Nsim = nis
            
        # kontrola předpokladů
        assert len(weights) <= Nsim, "jseš jistej, že máš spravnej počet měření?"
        
        # vytvoříme slovník pro sadu vzorků, který implicitně
        # bude předpokládát průměr=0 a rozptyl 1/Nsim^2 
        # pro všecko, co se v sadě neobjevilo
        if Nsim == 1:
            # jedno meření je taky měření)
            implicit_var = implicit_multiplicator
        else:
            implicit_var = implicit_multiplicator*(1-1/Nsim)/Nsim**2
        serie = DefaultDict((0, implicit_var))
        
        
        w = np.array(weights)
        if event not in self.events:
            self.events.append(event)
            
        # podle IS vzorečků
        key_mean = np.sum(w)/Nsim
        key_var = (np.sum(w**2)/Nsim - key_mean**2) / Nsim
        if key_var == 0: # to nechcem
            key_var = implicit_var
            
        # uložime
        serie[event] = (key_mean, key_var)
        
        self.series_data.append(serie)
        
        #č nebudeme hned počítat odhady, nechť to dělá volající kód sam
        # ачиз значение утёз
        #self.get_estimations()
        #self.estimations = {self.events[i] : self.values[i] for i in range(len(self.events))}
    
        
    def get_means(self):
        # počet jevů
        # number of events
        n_ev = len(self.events)
        self.weighted_means = np.empty(n_ev, dtype=float)
        self.weighted_vars = np.empty(n_ev, dtype=float)
        
        # spočteme važené průměry a rozptyly
        for event, key in zip(self.events, range(n_ev)):
            key_accusum = 0
            key_accuweight = 0
            for serie in self.series_data:
                key_mean, key_var = serie[event]
                key_accusum += key_mean / key_var
                key_accuweight += 1/key_var
            
            if key_accuweight == 0:
                #č já vidím, že .get_estimations nuly skryje
                self.weighted_means[key] = 0
                self.weighted_vars[key] = np.inf
            else:
                self.weighted_means[key] = key_accusum / key_accuweight
                self.weighted_vars[key] = 1/key_accuweight
            
        
        return self.weighted_means, self.weighted_vars, np.array(self.events)
            
    def get_estimations(self):
    
        # p-čka. We are still talking about probabilities, right?    
        p, vars, __ = self.get_means() 
        
        sum_p = np.sum(p)
        if sum_p == 1: # а вдруг?
            self.values = p
            #♥оӵ ачиз значение утёз
            self.estimations = {self.events[i] : self.values[i] for i in range(len(self.events))}
            return p, np.array(self.events)
            
            # spring (non-linear) analogue
        # silu, kterou zatížíme system jen tak neseženeme
        elif sum_p > 1: # stlačit
            low_atF = -np.pi/2
            high_atF = 0
        else: # roztahnout
            low_atF = 0
            high_atF = np.pi/2
        
        # nuly nám udělaj problém    
        mask = p==0
        p = np.ma.array(p)
        vars = np.ma.array(p)
        p.mask = mask
        vars.mask = mask
        
        F = np.tan(bisect(lambda atF: np.sum(np.exp(np.tan(atF)*vars/p)*p), 1, low_atF, high_atF))
        corrected_means = p * np.exp(F * vars/p)
        
        corrected_means.mask = False
        self.values = corrected_means
        #♥ ачиз значение утёз
        self.estimations = {self.events[i] : self.values[i] for i in range(len(self.events))}
        return corrected_means, np.array(self.events)
        
        
    def delete_event_data(self, event):
        """
        pomocná funkce třeba pro případ změny (zpřesnění) nějakých jevů na straně modelu
        function doesn't recalculate estimations after that!
        """
        # prozatím nebudu kontrolovat, zda ten jev tam vůbec je
        self.events.remove(event)
        for serie in self.series_data:
            # vymažem jev
            if event in serie:
                serie.pop(event)
        
        #č krucinál, tady narazím už ne natolik triviálné chyby
        for i in range(len(self.series_data)-1, -1, -1): # reverse
            serie = self.series_data[i]
            #č zkontrolujem, zda v serii se ještě něco zůstalo
            if len(serie) == 0:
                #č jako doufám, že tam tato serie bude jedina 
                self.series_data.remove(serie)
                
        
        
        
        
        


class ISS:
    """
    IS statistics = weights series + events
    ISS calculates probabilities of repeated IS series
    """
    def __init__(self):
        """
        defaultdict zajistí, že na každý jev nás čeka seznam, do kterého 
        může přidávat průměr a rozptyl ze sady
        """ 
        self.data = collections.defaultdict(list)
        
    def add_IS_serie(self, weights, events):
        keys = np.unique(events)
        Nsim = len(weights)
        
        # tak bacha
        w = np.array(weights)
        ev = np.array(events)
        for key in keys:
            mask = ev==key
            ev_w = w[mask]
            # podle IS vzorečků
            key_mean = np.sum(ev_w)/Nsim
            key_var = (np.sum(ev_w**2)/Nsim - key_mean**2) / Nsim
            # uložime
            self.data[key].append((key_mean, key_var))
            
            # vyfiltrujeme zbytek
            w = w[~mask]
            ev = ev[~mask]
        
        # kontrola  
        assert len(w)==0 and len(ev)==0, "Что за хренотень?!"
        
        
        
    def get_means(self):
        # počet jevů
        # number of events
        weighted_means = []
        weighted_vars = []
        
        # spočteme važené průměry a rozptyly
        for key_data in self.data.values():
            key_accusum = 0
            key_accuweight = 0
            for key_mean, key_var in key_data:
                key_accusum += key_mean / key_var
                key_accuweight += 1/key_var
            
            weighted_means.append(key_accusum / key_accuweight)
            weighted_vars.append(1/key_accuweight)
            
            
        return weighted_means, weighted_vars, np.array(list(self.data.keys()))
            
    def get_estimations(self):
        weighted_means, weighted_vars, __ = self.get_means() 
        
        # p-čka. We are still talking about probabilities, right?    
        p = np.array(weighted_means)
        vars = np.array(weighted_vars)
        
        sum_p = np.sum(p)
        if sum_p == 1: # а вдруг?
            return p, np.array(list(self.data.keys()))
            
            # spring (non-linear) analogue
        # silu, kterou zatížíme system jen tak neseženeme
        elif sum_p > 1: # stlačit
            low_atF = -np.pi/2
            high_atF = 0
        else: # roztahnout
            low_atF = 0
            high_atF = np.pi/2
            
        F = np.tan(bisect(lambda atF: np.sum(np.exp(np.tan(atF)*vars/p)*p), 1, low_atF, high_atF))
        corrected_means = p * np.exp(F * vars/p)
        
        return corrected_means, np.array(list(self.data.keys()))
        
        
        
            
           # scipy проверяет брэкеты, чем вызывает overflow warning, раздражает
#        sol = optimize.root_scalar(lambda atF: np.sum(np.exp(np.tan(atF)*vars/p)*p)-1, bracket=(-np.pi/2, np.pi/2) )
#        F = np.tan(sol.root)
        
        
        
        
        
                # triangle analogue        
#        if len(weighted_means) == 2:
#           # tak je to jednoduchý
#           # it's piece of cake
#           # triangle analogue
#           a, b = *weighted_means
#           # derivations of Heron's formula
#           da = 8*a*b**2 + 6*a - 2*b - 2
#           db = 8*b*a**2 + 6*b - 2*a - 2
#           # matice koeficientů přetvořené podmínkové rovnice
#           B = np.array([[1,1], [da, db]])

#           u = 1 - np.sum(p)
#           # vzoreček z teorii chyb měření a vyrovnávacího počtu nefunguje
#           # dává aj záporné pravděpodobnosti
#           #k = (1 - np.sum(weighted_means))/np.sum(weighted_vars)
#           #corrected_means = weighted_means + weighted_vars*k
