#!/usr/bin/env python
# coding: utf-8

import numpy as np
from . import sball
from scipy import stats
from .candybox import CandyBox
from .IS_stat import PushAndPull # for Shell_IS
from .IS_stat import get_1DS_sample # for Shell_1DS



try: # try to outthink f****** OS's memory management
    import os
    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
except BaseException as e:
    mem_GB = 16
    mem_bytes = mem_GB * 1024**3 # hello, Windows!
    #print("ghull failed to get amount of RAM installed. %s GB is supposed."% mem_GB, repr(e))
    #print("BTW, you are using Windows, aren't you?")
    
    

        

#č pomocná třída pro integrování
#č nejsem tedy jist, jestli je to nejlepší napad - 
#č dělit Ghull na podtřídy, delegovat funkcionalitu
#č ale jinak Ghull se stavá hodně překomplikovaným.
#č nic lepšího mně nenapadá, přemyšlel jsem dlouho.
class _ShellBaseIntegration:
    def __init__(self, hull, shell, non_Gaussian_reduction=0.98):
        self.shell = shell
        self.hull = hull
        self.nvar = hull.sample.nvar
        
        self.integration_cutoff = np.inf
        self.non_Gaussian_reduction = non_Gaussian_reduction
        
        # test if r>0
        self.r = 0
        central_G = np.full(hull.sample.nvar, 0, dtype=np.int8)
        self.DP = self.hull.sample.f_model.new_sample(central_G, space='G')
        
        
    @property
    def DP_is_valid(self):
        #č dalo by se kontrolovat změny obálky 
        #č a provadět kontrolu DP pouze po změně obálky.
        #č Nejsem liný, jeden bodík prostě za to doopravdy nestoji.
        mask = self.hull.is_outside(self.DP)
        return np.any(mask)
        
    #č na rozdil od rodičovské třídy
    #č vrací odhad r na základě předchozích integrací
    #č metoda je navržena tak, aby Shell_IS jú mohl zdědit. 
    def get_r(self):
        #č bojim sa, rerukce bude aplikována vždycky
        #č Bacha, metoda bude vracet nuly pro obálky v Gaussovskem prostoru!
        return self.r * self.non_Gaussian_reduction
        
        
    #č metoda je navržena tak, aby Shell_IS jú mohl zdědit. 
    def _r_check_out(self, outside_nodes):
        sum_squares = np.sum(np.square(outside_nodes.G), axis=1)
        arg = np.nanargmin(sum_squares)
        new_r = np.sqrt(sum_squares[arg])
        if (not self.DP_is_valid) or (new_r < self.r):
            self.DP = outside_nodes[arg]
            self.r = new_r
        
    
    #č metoda je navržena tak, aby Shell_IS jú mohl zdědit. 
    def integrate(self, nis, callback_all=None, callback_outside=None):
        self.reset(nis)
        
        if self.hull.nsimplex == 0:
            bus = self.integration_cutoff
        else:
            bus = int(mem_bytes / self.hull.nsimplex / 8 / 10) + 1
        while self.nsampled < nis:
            
            seats = min(nis - self.nsampled, self.integration_cutoff, bus)
            try: 
                self._process_part(seats, nis, callback_all, callback_outside)
            except MemoryError as m:
                print(self.__class__.__name__ +":", "memory error, %s sedaček" % seats, repr(m))
                self.integration_cutoff = int(np.ceil(seats/2))
        
        assert nis == self.nsampled
        
        #č finalizovat by mohl i self._get_result(),
        #č ale nebudeme michat vodku s pivem!
        self._finalize()
        
        return self._get_result()
        
    



class Shell_MC(_ShellBaseIntegration):
        
    def reset(self, nis): # clear
        self.r_needed = (self.hull.space!='G')
        
        self.nsampled = 0
        self.nfailed = 0
        
        
    # stateless
    def rvs(self, nsampled, seats, ns): 
        "Generování vzorků (kandidátů a integračních bodů)"
        # rand_dir: prepare ns random directions on a unit d-sphere
        rand_dir = sball.get_random_directions(seats, self.nvar) #random directions
        
        # generate sampling probabilites
        left = (ns-nsampled) / ns
        right = (ns-nsampled-seats) / ns
        #č přidáme trochu zmatku.
        #č globálně jdeme r->R, localně ale R_i+ -> R_i-
        #č menší poloměry musejí jít dřív - na to zavazano nonGaussian _r
        #č převracení lokalně umožní vždycky mít alespoň jeden bodík outside,
        #č což je taky velmi vhodné vzhledem k tomu, že se _r bere z outside bodíků
        p = np.linspace(right, left, seats, endpoint=False) # probabilities for the radius
        
        # convert probabilitites into random radii
        # (distances from origin that are greater than r and less than R)
        r = self.shell.isf(p) # actually, it is the same as CDF inverse
        
        #finally a random sample from the optimal IS density:
        sample_G = rand_dir*r[:,None]
        
        return sample_G
    
    # bus analogy
    def _process_part(self, seats, nis, callback_all=None, callback_outside=None):
        # boarding
        nodes_G = self.rvs(self.nsampled, seats, nis)
        nodes = self.hull.sample.f_model.new_sample(nodes_G, space='G')
        # who is back?
        mask = self.hull.is_outside(nodes)
        if self.r_needed and np.any(mask):
            #č rvs má vzorkovat od měnšího poloměru k většímu.
            #č to znamená, že první outside bude mít nejměnší r vůbec
            self._r_check_out(nodes[mask])
            self.r_needed = False
        
        if callback_all is not None:
            # -2 = 'inside' -1 = 'outside'
            candy_nodes = CandyBox(nodes, event_id=mask-2, is_outside=mask)
            callback_all(candy_nodes)
            
        if (callback_outside is not None) and np.any(mask):
            callback_outside(nodes[mask])
        
        assert len(mask) == seats
        #č nevím proč, ale kdysi mě to vyšlo rychlejc jak obyčejný součet
        self.nfailed += len(mask[mask]) 
        self.nsampled += len(mask) 
        
        
    #č finalizovat by mohl i self._get_result(),
    #č ale nebudeme michat vodku s pivem!
    def _finalize(self):
        #č nebyl žádný outside?
        #č to přece není v pořádku!
        #č (jen to nikomu neříkejte,
        #č ale v současné implementaci třídy 
        #č podmínka dole by neměla nikdy nastat)
        if self.r_needed:
            self.r = self.shell.R * self.non_Gaussian_reduction
        
    def _get_result(self):
        
        nis = self.nsampled
        nf = self.nfailed
        ns = nis - nf
        p_shell = self.shell.p_shell
        shell_pf = nf/nis * p_shell
        shell_ps = ns/nis * p_shell
        
        stats = dict()
        stats["shell_budget"] = nis
        stats["shell_inside"] = shell_ps
        stats["shell_outside"] = shell_pf
        
        return shell_ps, shell_pf, stats




class Shell_IS(Shell_MC):
    def reset(self, nis): # clear
        self.r_needed = (self.hull.space!='G')
        
        self.nsampled = 0
        self.pp = PushAndPull()
        
        
    # stateless
    def rvs(self, nsampled, seats, ns): 
        "Generování vzorků (kandidátů a integračních bodů)"
        # rand_dir: prepare ns random directions on a unit d-sphere
        rand_dir = sball.get_random_directions(seats, self.nvar) #random directions
        
        #č poloměry bereme ze skořapky
        #č za správné nastavení (stejně jako u MC)
        #č zodpovidá uživatel třídy
        #č třída vlastní odhad r nijak nevyuživá!
        r = self.shell.r
        R = self.shell.R
        delta_r = R - r
        left = nsampled / ns * delta_r + r
        right = (nsampled + seats) / ns * delta_r + r
        #č přidáme trochu zmatku.
        #č globálně jdeme r->R, localně ale R_i+ -> R_i-
        #č menší poloměry musejí jít dřív - na to zavazano nonGaussian _r
        #č převracení lokalně umožní vždycky mít alespoň jeden bodík outside,
        #č což je taky velmi vhodné vzhledem k tomu, že se _r bere z outside bodíků
        rs = np.linspace(right, left, seats, endpoint=False)
        
        #finally a random sample from the optimal IS density:
        sample_G = rand_dir*rs[:,None]
        
        #č a jsme doma. Platba za špatný design.
        #č Potřebujeme hustotu 1D rozdělení, implementovanou v Radial
        #č Shell se síce dědí od Radial, ale implementuje .pdf() jako sdruženou 
        #č hustotu v nD Gaussovskem prostoru
        #
        #č vahy jsou definovány jako podil původního rozdělení k vzorkovácímu
        #č původní - Chi rozdělení. nemá zde být žádný p_shell
        f_pdf = stats.chi.pdf(rs, self.nvar)
        #č vzorkovácí. 
        #h_pdf = 1/delta_r
        weights = f_pdf * delta_r
        
        return sample_G, weights
    
    # bus analogy
    def _process_part(self, seats, nis, callback_all=None, callback_outside=None):
        # boarding
        nodes_G, weights = self.rvs(self.nsampled, seats, nis)
        nodes = self.hull.sample.f_model.new_sample(nodes_G, space='G')
        # who is back?
        mask = self.hull.is_outside(nodes)
        if self.r_needed and np.any(mask):
            #č rvs má vzorkovat od měnšího poloměru k většímu.
            #č to znamená, že první outside bude mít nejměnší r vůbec
            self._r_check_out(nodes[mask])
            self.r_needed = False
        
        assert len(mask) == seats
        self.pp.add(weights, mask)
        self.nsampled += len(mask) 
        
        if callback_all is not None:
            # -2 = 'inside' -1 = 'outside'
            candy_nodes = CandyBox(nodes, event_id=mask-2, is_outside=mask, weights=weights)
            callback_all(candy_nodes)
            
        if (callback_outside is not None) and np.any(mask):
            callback_outside(nodes[mask])
        
        
    def _get_result(self):
        
        nis = self.nsampled
        #č nejdřív true, pak false. Posilali jsme is_outside
        mean_pf, mean_ps = self.pp.mean
        var_pf, var_ps = self.pp.var
        shell_pf, shell_ps = self.pp.correct_means(p_overall=self.shell.p_shell)
        
        stats = dict()
        stats["shell_budget"] = nis
        stats["shell_inside_measured"] = mean_ps
        stats["shell_outside_measured"] = mean_pf
        stats["shell_inside_var"] = var_ps
        stats["shell_outside_var"] = var_pf
        stats["shell_inside"] = shell_ps
        stats["shell_outside"] = shell_pf
        
        return shell_ps, shell_pf, stats



#č slovní zásoba došla mně už před pár rokama
class Shell_1DS(_ShellBaseIntegration):
    """1DS stands for 1D sampling.
    1DS is, actually, an importance sampling method
    that, actually, does not calculate IS weights
    as f_density / h_density, but
    (arbitrary, nonuniformly) divides interval to subintervals.
    By using CDF transformes subintervals to 0-1 measure line.
    Then gets one node as middle point of every subinterval,
    weights therefore are just interval widths itself.
    No sampling imprecisions are introduced, 
    therefore no spring, no correction are needed. 
    """
    def reset(self, nis): # clear
        self.r_needed = (self.hull.space!='G')
        
        self.nsampled = 0
        
        #č poloměry bereme ze skořapky
        #č za správné nastavení (stejně jako u MC)
        #č zodpovidá uživatel třídy
        #č třída vlastní odhad r nijak nevyuživá!
        r = self.shell.r
        R = self.shell.R
        # let's predefine 1D sequence at very beginning
        if r > np.sqrt(self.nvar - 1):
            x_sub = np.geomspace(r, R, nis+1, endpoint=True)
        else:
            x_sub = np.linspace(r, R, nis+1, endpoint=True)
        
        #č objevilo se, že scipy.stats.chi je neunosně nepřesné
        #č vzdává se jíž na poloměru 8
        s_ball = sball.Sball(self.nvar)
        x, weights = get_1DS_sample(s_ball, x_sub)
        self.x = x
        self.weights = weights
        self.mask = np.empty(nis, dtype=bool)
        
    
    
    # bus analogy
    def _process_part(self, seats, nis, callback_all=None, callback_outside=None):
        # boarding
        left = self.nsampled
        right = self.nsampled + seats
        rs = self.x[left:right]
        
        # rand_dir: prepare ns random directions on a unit d-sphere
        rand_dir = sball.get_random_directions(seats, self.nvar) #random directions
        nodes_G = rand_dir*rs[:,None]
        nodes = self.hull.sample.f_model.new_sample(nodes_G, space='G')
        
        # who is back?
        mask = self.hull.is_outside(nodes)
        assert len(mask) == seats
        
        if self.r_needed and np.any(mask):
            #č má se vzorkovat od měnšího poloměru k většímu.
            #č to znamená, že první outside bude mít nejměnší r vůbec
            self._r_check_out(nodes[mask])
            self.r_needed = False
        
        # the most important part
        self.nsampled += len(mask) 
        self.mask[left:right] = mask
        
        if callback_all is not None:
            # -2 = 'inside' -1 = 'outside'
            candy_nodes = CandyBox(nodes, event_id=mask-2, is_outside=mask)
            callback_all(candy_nodes)
            
        if (callback_outside is not None) and np.any(mask):
            callback_outside(nodes[mask])
        
        
    def _finalize(self):
        #č nebyl žádný outside?
        #č to přece není v pořádku!
        if self.r_needed:
            self.r = self.shell.R * self.non_Gaussian_reduction
        
        
    def _get_result(self):
        #č mask related to hull.is_outside()
        shell_pf = np.sum(self.weights[self.mask])
        shell_ps = np.sum(self.weights[~self.mask])
        
        stats = dict()
        stats["shell_budget"] = self.nsampled
        stats["shell_inside"] = shell_ps
        stats["shell_outside"] = shell_pf
        
        return shell_ps, shell_pf, stats
        
        
        
        
#č mým úkolem při návrhu této třidy je pořádně všecko zkomplikovat.
#č Dostávám za to peníze. 
#č Takže. Udělám 3 druhů estimátorů
# convex_hull_estimation  -2: inside, -1: outside
# shell_estimation  -22: inner, -3: shell, -11: outer
# ghull_estimation  -22: inner, -21: shell inside, -12: shell outside, -11: outer 
class Ghull:
    def __init__(self, hull, calculate_orth=True, calculate_2FORM=True, \
                        Integrator=Shell_1DS, non_Gaussian_reduction=0.9):
        self.hull = hull
        self.shell = sball.Shell(hull.sample.nvar)
        self.outside_dist = sball.Shell(hull.sample.nvar)
        self.sample = hull.sample
        
        #č vlastně nevím, ale nemusejí byť úplně zadarmo...
        self.calculate_orth = calculate_orth
        self.calculate_2FORM = calculate_2FORM
        
        self.set_integrator(Integrator, non_Gaussian_reduction)
        
    def set_integrator(self, Integrator, non_Gaussian_reduction=0.9):
        self.gint = Integrator(self.hull, self.shell, non_Gaussian_reduction)
        
            
    def boom(self, ns, use_MC=False):
        if use_MC:
            self.outside_dist.set_bounds(self.get_R())
            nodes_G = self.outside_dist.rvs(ns)
        else:
            # rand_dir: prepare ns random directions on a unit d-sphere
            rand_dir = sball.get_random_directions(ns, self.sample.nvar) #random directions
            
            #č deme od vnější .get_R() kružnici směrem ven
            r = self.get_R()
            
            # maximum radius, where norm.pdf() wasn't zero
            # -38.575500173381374935388521407730877399444580
            # don't ask me what the magic python use to distinguish
            # digits after double precision
            max_R_ever = 37
            if r < max_R_ever:
                R = max_R_ever
            else:
                R = r + 10
            r = np.linspace(self.get_R(), max_R_ever, ns, endpoint=True) 
            nodes_G = rand_dir*r[:,None]
        
        nodes = self.sample.f_model.new_sample(nodes_G, space='G')
        return nodes
        
    def get_orth_outside(self):
        if self.hull.space == 'G':
            return self.hull.get_orth_outside()
        else: 
            ###č bude to horší jak s-ball, ale budiž.
            ##x = np.full(self.sample.nvar, self.get_R())
            ##return calculate_brick_complement_probability(-x, x)
            #č zůstal calculate_brick_complement_probability
            #č v convex_hull modulu,
            #č ale. na orth odhady celkem spolehám,
            #č nechť se vrací aspon d-ball odhad
            #
            #č shell normálně musí se aktualizovat
            #č nechcu to tady řešit
            return self.shell.pf 
            
    def get_2FORM_outside(self):
        if self.hull.space == 'G':
            return self.hull.get_2FORM_outside()
        else: 
            #č nebudem do toho michat nic dalšího. 
            #č Když 2FORM, tak 2FORM!
            return 2 * stats.norm.sf(self.get_R())
            
    def get_FORM_outside(self):
        if self.hull.space == 'G':
            return stats.norm.sf(self.get_r())
        else:
            return stats.norm.sf(self.get_R())
            
    def get_R(self):
        sum_squared = np.sum(np.square(self.sample.G), axis=1)
        #index = np.argmax(sum_squared)
        return np.sqrt(np.nanmax(sum_squared))
        
    def get_r(self):
        "calculates minimal signed distance to planes. Can therefore be negative"
        #return -np.nanmax(self.hull.b)
        if self.hull.space == 'G':
            return self.hull.get_r()
        else:
            #č get_design_points() nemusí být.
            #č QHull může nemít dostatek teček
            try:
                hull_points = self.hull.get_design_points()
                sum_squared = np.sum(np.square(hull_points.G), axis=1)
                hull_r = np.sqrt(np.nanmin(sum_squared))
            except BaseException as e:
                msg = "cannot get hull points from the convex hull"
                print(self.__class__.__name__ +":", msg, repr(e))
                hull_r = np.inf
                
            
            # ask our experimentation team
            gint_r = self.gint.get_r()
            
            #č podle mně, nemůže se stat, že by metoda vratila:
            #č 1. nenůlový poloměr a že by dokonce i centralní bod byl venku.
            #č 2. poloměr větší jak R
            #č Odpovědnost za to kladu na gint.
            return np.nanmin((hull_r, gint_r))
     
    def get_shell_estimation(self):
        shell = self.shell
        r = self.get_r()
        R = self.get_R()
        
        if r<0:
            shell.set_bounds(0, R)
        else:
            shell.set_bounds(r, R)
        
        # shell_estimation  -22: inner, -3: shell, -11: outer
        shell_estimation = {-22:shell.ps, -3: shell.p_shell, -11: shell.pf}
        global_stats = {"nsim":self.sample.nsim, "ndim":self.sample.nvar, \
                        "nfacets": self.hull.nsimplex, "r":r, "R":R, \
                    "inner":shell.ps, "shell":shell.p_shell, "outer":shell.pf}
        global_stats['FORM_outside'] = self.get_FORM_outside()
        if self.calculate_2FORM:
            global_stats['2FORM_outside'] = self.get_2FORM_outside()
        if self.calculate_orth:
            global_stats['orth_outside'] = self.get_orth_outside()
        return shell_estimation, global_stats
        
    #č nie    
    ##č pro mně je důležité, aby bylo možné rychle přepinat mezi metodama,
    ##č aby bylo možné výsledky jednoduše porovnavat.
    ##č Proto explicitně posílám priznak, jakou metodu použit.
    def integrate(self, nis, callback_all=None, callback_outside=None):
        #č no to teda disajn třidy je doopravdy hroznej
        # .get_shell_estimation() will calculate radiuses and will update shell
        shell_estimation, global_stats = self.get_shell_estimation()
        # shell_estimation  -22: inner, -3: shell, -11: outer
        shell_estimation.pop(-3)
        # ghull_estimation  -22: inner, -21: shell inside, -12: shell outside, -11: outer 
        ghull_estimation = shell_estimation; del(shell_estimation)
        
        
        shell_ps, shell_pf, stats = self.gint.integrate(nis, callback_all, callback_outside)
        ghull_estimation[-21] = shell_ps
        ghull_estimation[-12] = shell_pf
        global_stats.update(stats)
        
        # convex_hull_estimation  -2: inside, -1: outside
        inside = shell_ps + self.shell.ps
        outside = shell_pf + self.shell.pf
        convex_hull_estimation = {-2: inside, -1: outside}
        global_stats["inside"] = inside
        global_stats["outside"] = outside
        
        return ghull_estimation, convex_hull_estimation, global_stats
        
        
