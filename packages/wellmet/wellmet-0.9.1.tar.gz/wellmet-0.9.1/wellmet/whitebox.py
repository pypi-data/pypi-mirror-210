#!/usr/bin/env python
# coding: utf-8

"""
Zde leží whiteboxy
Zatimco BlackBox pěčlivě ukladá věškerá data,
věškeré sady vzorků, průběžné odhady a tak,
WhiteBox musí obsahovat jen pf_exact, které buď už předem zná,
nebo jej spočítá a není vůbec/nachren nutný cokoliv ukladat.

en:
f_model + g_model = pf
WhiteBox = [f_model, g_model, pf_exact]
pf_exact is most important part of WhiteBox 
Knowledge of pf is the only reason to create WhiteBox

whitebox actually IS g_model PLUS:
.f f_model
.pf_exact
.pf_exact_method
"""
import numpy as np
from scipy import stats
from scipy import special # for S_ball # for Z_prod
from scipy import integrate # for S_ball

import mpmath # for Gaussian_Z_min

mpmath.mp.dps = 325 # to cover anything that double-presigion float can handle

from .samplebox import SampleBox

from . import f_models
import copy
from . import g_models
from . import misc as wmisc



class WhiteBox:
    """
    Bazová třida pro dědictví
    
    úkolem whiteboxu je spočítat pf-ko
    .pf_exact
    .pf_exact_method
    """
    pf_exact_method = 'None'
    
    def __init__(wt,  f_model, g_model):
        wt.gm = g_model
        wt.f = f_model
        # na začatku nemáme vzorky - pouze rozdělení a podpís
        wt.sample_box = SampleBox(wt.f(), gm_signature=wt.gm_signature)
        
        try: # no to jsme líný. Možná samotný g_model tuší jak se spočte pf-ko?
            wt.pf_exact, wt.pf_exact_method = g_model.pf_expression(f_model)
        except AttributeError:
            pass
        
    def __str__(wt):
        #ёč хощется přidat nějaký popísek k testkejsům
        #č chce se odlišovat úlohy, co už získaly slavu 
        #č v časopísech od těch, co ještě nie,
        #č od těch, se kterými ještě hrajeme
        #č od těch, co jsme před chvilkou vymysleli
        if 'description' in wt.__dict__:
            return  wt.description
        else:
            return  wt.__class__.__name__ + ' of' + str(wt.gm)
        
    def __repr__(wt):
        return  'WhiteBox(%s, %s)' %(repr(wt.f), repr(wt.gm))
        
    def __len__(wt):
        return len(wt.sample_box)
        
        
    def __call__(wt, sample=None):
        if sample is None:
            sample = wt.sample_box()
        
        # zamykame se do sebe
        return wt.run_sample(sample)
    
    def run_sample(wt, sample):
        result = wt.gm(sample)
        wt.sample_box.add_sample(result)
        return result
        
    def __getitem__(self, slice):
        self_copy = copy.copy(self)
        self_copy.sample_box = self.sample_box[slice]
        return self_copy
        
    def __getattr__(wt, attr):
        if attr == 'whitebox':
            return wt
        # co patři g_modelovi?
        elif attr == 'get_2D_R_boundary':
            return wt.gm.get_2D_R_boundary
        elif attr == 'gm_signature':
            try: # byla volná funkce?
                return wt.gm.__name__
                # asi to byla trida?
            except AttributeError:
                return repr(wt.gm)
        
        
        # co mělo být definováno ve WhiteBoxu? Ale teda není?
        elif attr == 'pf_exact_method':
            raise AttributeError
            
          # пытка-непытка
        elif attr == 'pf_exact': 
            if 'beta_exact' in wt.__dict__:
                return stats.norm.cdf(-wt.beta_exact)
            else:
                # мы нищего не знаем
                raise AttributeError("Nothing known about failure probability")
                
        elif attr == 'beta_exact':
            if 'pf_exact' in wt.__dict__:
                return -stats.norm.ppf(wt.pf_exact)
            else:
                raise AttributeError("Nothing known about failure probability")
        
        
        # branime sa rekurzii
        # defend against recursion
        elif attr == 'sample_box':
            raise AttributeError
            
        # zbytek teda nievím
        else:
            return getattr(wt.sample_box, attr)
    
    # just plot, green points, red points...
    # commented out in order to not import 
    # matplotlib and pyqtgraph unnecessarly
    #plot2D = plot.plot2D
    #plot3D = plot.plot3D
    #show2D = plot.show2D
    #show3D = plot.show3D
            
        
    def get_2D_boundary(wt, nrod=100, viewport_sample=None, viewport_space='R'):
        """
        Fence off!
        nrod - number of rods in fencing
        viewport_sample - limit points of viewport
        (function will get xlim and ylim from there, 
        assuming there will be at least two points)
        """
        
        if (viewport_sample is not None): # and viewport_sample.nsim: #>0
            if viewport_space=='R':
                viewport_sample_R = viewport_sample
            else:
                viewport_sample_R = wt.f_model.new_sample(viewport_sample, viewport_space, extend=True).R
        else:
            viewport_sample_R = wt.f_model.new_sample([[-7,-7],[7,7]], 'G', extend=True).R
            
            # should I tolerate nD?
        viewport_sample_R = np.vstack((viewport_sample_R[:,:2], wt.sample_box.R[:,:2]))
        xmin = np.ma.masked_invalid(viewport_sample_R[:,0]).min()
        xmax = np.ma.masked_invalid(viewport_sample_R[:,0]).max()
        ymin = np.ma.masked_invalid(viewport_sample_R[:,1]).min()
        ymax = np.ma.masked_invalid(viewport_sample_R[:,1]).max()
        
        # získám seznam polí
        bounds_R = wt.get_2D_R_boundary(nrod, (xmin, xmax), (ymin, ymax))
        # transformuji na seznam vzorků
        return [wt.f_model.new_sample(bounds_R[i], extend=True)  for i in range(len(bounds_R))]
    
    
    def get_sensitivities(wt, nrod=200, G_radius=7, space='R'):
        #č nejdřív musíme získat relevantní ve skutečném prostoru rámec
        view_sample = wmisc.get_isodistances(wt.f_model, G_radius, nrod)
        view_sample_R = view_sample.R
        
        #č jakože tímto vyfiltrujeme nejen NaN, ale i nekonečna?
        xmin = np.ma.masked_invalid(view_sample_R[:,0]).min()
        xmax = np.ma.masked_invalid(view_sample_R[:,0]).max()
        ymin = np.ma.masked_invalid(view_sample_R[:,1]).min()
        ymax = np.ma.masked_invalid(view_sample_R[:,1]).max()
        
        #č skoro hotovo. Jsme připravení získat seznam hraničních bodů od g_modelu
        boundaries = wt.get_2D_R_boundary(nrod, (xmin, xmax), (ymin, ymax))
        
        sensitivity = np.zeros(2)
        # boundaries are instances of an obscure Ingot class.
        # Relicts from the WellMet's childhood
        for boundary in boundaries:
            #č podle ono to tam musí implicitně vzít podle R
            sample = wt.f_model.new_sample(boundary, extend=True)
            sample_space = getattr(sample, space)
            vectors = np.diff(sample_space, axis=0)
            #č k těm hustotám můžeme podstupovat několika způsoby
            #č buď zprůměrovat uzly, v nich napočítat hustoty.
            #č Nebo napočítat hustoty v tam, kde je máme, 
            #č zprůměrovat už jen hustoty. 
            #č Jdeme na tu druhou variantu
            pdf = sample.pdf(space)
            pdf[:-1] += pdf[1:]
            #pdf /= 2
            pdf = pdf[:-1]
            
            #č pokud nebudeme chtit nic křeslit, 
            #č tak samotné vektory ani nepotřebujeme
            np.square(vectors, out=vectors)
            
            #č zdá se, že ani délky nepotřebujeme
            #lengths = np.sum(vectors, axis=1)
            #vectors /= lengths
            
            vectors *= pdf.reshape(-1,1)
            mask = np.all(np.isfinite(vectors), axis=1)
            sensitivity += np.sum(vectors[mask], axis=0)[:2]
            
        sensitivity /= np.sum(sensitivity)
        y, x = sensitivity
        return x, y
        


    # Monte Carlo, n-krátá realizace
    def MC(wt, Nsim=int(1e6)):
        
        
        # tohlensto může bejt dost těžkým
        result = wt.gm(wt.f(Nsim))
        # should I stay or should I go?
        #wt.sample_box.add_sample(result)
        
        # je tu jakoby že g_model vždy vrací nějakej sample_box
        pf_exact = np.count_nonzero(result.failsi)/Nsim
        
        # šlo by to?
        if wt.pf_exact_method == 'None' or wt.pf_exact_method == 'MC' and wt.Nsim <= Nsim:
            wt.pf_exact = pf_exact
            wt.Nsim = Nsim
            wt.pf_exact_method = 'MC'
        
        print('Monte Carlo estimation of pf is %s (%s simulations)'%(pf_exact, Nsim))
        return result
        


    # IS, (n-2)-krátá realizace, n>2
    def IS(wt, Nsim=int(1e4), h_model=None, IS_mode='G'):
        """
        IS_mode - v jakých souřadnicích robím merge a jaká PDF použiváme?
        může být 'R' nebo 'G'
        jinde # čo jinde?
        """
        
        if h_model is not None:
            wt.h = h_model 
            wt.IS_mode = IS_mode
        elif 'h' not in wt.__dict__:
            wt.h = f_models.UnCorD([stats.norm(0,2.5) for i in range(wt.f.nvar)])
            wt.IS_mode = 'G'
            
            
        #
        # jdeme na to, koťě!
        #
        
        # zgenerujeme vzorky
        # nic zajimavýho
        wt.h = wt.h(Nsim)
        
        # a teď bacha!
        if wt.IS_mode == 'R':
            # jestli máme to právé vzorkovácí rozdělení - tak nemáme čo robiť
            to_sample = wt.f.new_sample(wt.h) # smerdží se to po R
            # w like weights
            wt.w = to_sample.pdf_R / wt.h.pdf_R
        elif wt.IS_mode == 'G':
            # tady musíme provést jeden trik
            to_sample = wt.f.new_sample(wt.h.R, 'G') # R-ko smerdžíme ako G-čko
            wt.w = to_sample.pdf_G / wt.h.pdf_R # snad je to správně
        else:
            # шо-то тут не то...
            # čo blbnéš, kámo?
            # What's going on with my IS_mode?
            raise ValueError("IS_mode should be either 'R' or 'G'")
        
        # vahy máme, jedeme dál
        # sample_box jíž není prázdnej
        result = wt.gm(to_sample)
        #wt.sample_box.add_sample(result)
        
        # hodilo by sa to?
        pf_exact = np.sum(wt.w[result.failsi])/Nsim
        
        if wt.pf_exact_method in ('None', 'IS_norm', 'IS'):
            wt.Nsim = Nsim
            if pf_exact < 1:
                wt.pf_exact = pf_exact
                wt.pf_exact_method = 'IS'
            else:
                # ať mně nerobí ostudu
                wt.pf_exact = np.sum(wt.w[result.failsi]) / np.sum(wt.w)
                wt.pf_exact_method = 'IS_norm'
        
        print('Importance Sampling pure estimation of pf is %s (%s simulations)'%(pf_exact, Nsim))
        return result
       


class HyperPlane(WhiteBox): # куда ж без него...
    def __init__(self, betas=(1,2,3)):
        """
        Class takes for inicialization tuple of betas 
        Betas are coeffitients in sense of Regression Analysis (well, not really)
        g= a*X1 + b*X2 + c
        betas=(a,b,c)
        """
        self._betas = betas
        self.gm = g_models.Linear_nD(betas)
        self.f = f_models.SNorm(len(betas)-1)
        # na začatku nemáme vzorky - pouze rozdělení a podpís
        self.sample_box = SampleBox(self.f(), gm_signature=self.gm_signature)
        
        # tady už je to ta, "náše" beta )
        # beta = c/np.sqrt(a**2 + b**2)
        self.beta_exact = betas[-1]/np.sqrt(np.sum(np.array(betas[:-1])**2)) 
        self.pf_exact = stats.norm.cdf(-self.beta_exact)
        self.pf_exact_method = 'FORM (exact solution)' # Ang, Tang and Pythagoras
        self.r_exact = self.beta_exact
        
        
    def __str__(wt):
        return  'HyperPlaneBox%sD'%(len(wt._betas)-1)
        
    def __repr__(wt):
        return  'HyperPlane(%s)' % repr(wt._betas)
        
        
class Line(WhiteBox):
    def __init__(self, nvar=2, beta=5):
        """
        Class takes for inicialization tuple of betas 
        Betas are coeffitients in sense of Regression Analysis (well, not really)
        g= a*X1 + b*X2 + c
        betas=(a,b,c)
        """
        self.beta_exact = beta
        self.gm = g_models.X1(beta)
        self.f = f_models.SNorm(nvar)
        # na začatku nemáme vzorky - pouze rozdělení a podpís
        self.sample_box = SampleBox(self.f(), gm_signature=self.gm_signature)
        
        self.pf_exact = stats.norm.cdf(-beta)
        self.pf_exact_method = 'FORM (exact solution)' # Ang, Tang and Pythagoras
        self.r_exact = self.beta_exact
        
    def __str__(wt):
        return  'Line%sD' % wt.f.nvar
        
    def __repr__(wt):
        return  'Line(%s, %s)' % repr(wt.f.nvar, wt.beta_exact)
        
class TwoLine(WhiteBox):
    def __init__(self, nvar=2, beta=5):
        """
        Class takes for inicialization tuple of betas 
        Betas are coeffitients in sense of Regression Analysis (well, not really)
        g= a*X1 + b*X2 + c
        betas=(a,b,c)
        """
        self.beta = beta
        self.gm = g_models.AbsX1(beta)
        self.f = f_models.SNorm(nvar)
        # na začatku nemáme vzorky - pouze rozdělení a podpís
        self.sample_box = SampleBox(self.f(), gm_signature=self.gm_signature)
        
        self.pf_exact = stats.norm.cdf(-beta) * 2
        self.pf_exact_method = '2FORM (exact solution)' # Ang, Tang and Pythagoras
        self.r_exact = self.beta
        
        
    def __str__(wt):
        return  'TwoLine%sD' % wt.f.nvar
        
    def __repr__(wt):
        return  'TwoLine(%s, %s)' % repr(wt.f.nvar, wt.beta)


class Gaussian_Z_sum(WhiteBox): #ё куда ж без этого...
    def __init__(self, nvar=2, beta_exact=5):
        """
        
        """
        self.gm = g_models.Z_sum(nvar, beta_exact)
        self.f = f_models.SNorm(nvar)
        #č na začatku nemáme vzorky - pouze rozdělení a podpís
        self.sample_box = SampleBox(self.f(), gm_signature=self.gm_signature)
        
        self.beta_exact = beta_exact
        self.pf_exact = stats.norm.cdf(-self.beta_exact)
        self.pf_exact_method = 'FORM (exact solution)' # Ang, Tang and Pythagoras
        self.r_exact = self.beta_exact
        
        
    def __str__(wt):
        return  'Gaussian_Z_sum%sD'%(wt.f.nvar)
        
    def __repr__(wt):
        return  'Gaussian_Z_sum(nvar=%s, beta_exact=%s)' % (wt.f.nvar, wt.beta_exact)


def gauss_prod_CDF(z):
    """product Z= X_1 * X_2  has probability density f(z) = K_0(|z|)/pi, 
    where K_0() is the modified Bessel function of the second kind (zero order) and
    $X_1, X_2$ are independent standard normal variables.
    The distribution function F(z) = \int_{-\infty}^z f(t) dt  can be solved in closed form as follows
    F_Z(z)= 1/2 + z/2/pi * (K_0(|z|) * (2 + pi * L_1(z)) + K_1(|z|) * pi * L_0(|z|)),
    where L_0() L_1() are the modified Struve functions of orders zero and one respectively. 
    """
    StruveL0 = special.modstruve(0, np.abs(z))
    StruveL1 = special.modstruve(1, z)
    BesselK0 = special.kn(0, np.abs(z))
    BesselK1 = special.kn(1, np.abs(z))
    return 0.5 + z/2/np.pi * (BesselK0 * (2 + np.pi * StruveL1) + BesselK1 * np.pi * StruveL0)

class Gaussian_Z_prod_2D(WhiteBox): 
    def __init__(self, **kwargs):
        """
        Breitung RESS 182 (2019) p. 99
        """
        #č měníme logiku. 
        #č u této třídy známenko constanty bude ovlivňovat 
        #č poruchové kvadranty.
        if 'sign' in kwargs:
            self.sign = kwargs['sign']
        else:
            self.sign = 1
        if 'const' in kwargs:
            self.const = kwargs['const']
        elif 'beta' in kwargs:
            self.beta = kwargs['beta']
            self.const = self.beta**2/2
        else:
            raise ValueError
        
        
        #č g-modelu je to samozřejmě šuma, ale bílá skříňka nechť raději
        #č pečlivěji zpracovává vstup
        self.gm = g_models.Z_prod(const=self.const, sign=np.sign(self.sign))
        self.f = f_models.SNorm(2)
        #č na začatku nemáme vzorky - pouze rozdělení a podpís
        self.sample_box = SampleBox(self.f(), gm_signature=self.gm_signature)
        #č Rozdělení transformovaného náhodného čísla je zadano jako 
        # special.kn(0, np.abs(x)) / np.pi # Breitung RESS 182 (2019) p. 99
        # kn(n, x) Modified Bessel function of the second kind of integer order n
        # modstruve(v, x) Modified Struve function of order v at x
        #č Odvození pf_exact z Maple
        #self.pf_exact = 0.5 - const/2 * (StruveL1 * BesselK0 + StruveL0 * BesselK1 + 2/np.pi * BesselK0)
        if self.sign > 0:
            self.pf_exact = gauss_prod_CDF(-self.const)
        else:
            self.pf_exact = 1 - gauss_prod_CDF(-self.const)
        self.pf_exact_method = 'exact (Bessel) solution' 
        self.r_exact = np.sqrt(np.abs(self.const) * 2)
        
    def __str__(wt):
        return  'Gaussian_Z_prod_2D'
        
    def __repr__(wt):
        return  'Gaussian_Z_prod_2D(const=%s)' % wt.const



class Gaussian_Hyperbola_2D(WhiteBox): 
    def __init__(self, **kwargs):
        """
        Breitung RESS 182 (2019) p. 99
        """
        if 'const' in kwargs:
            self.const = kwargs['const']
        elif 'beta' in kwargs:
            self.beta = kwargs['beta']
            self.const = self.beta**2/2
        else:
            raise ValueError
        
        
        #č g-modelu je to samozřejmě šuma, ale bílá skříňka nechť raději
        #č pečlivěji zpracovává vstup
        self.gm = g_models.Z_hyperbola(self.const)
        self.f = f_models.SNorm(2)
        #č na začatku nemáme vzorky - pouze rozdělení a podpís
        self.sample_box = SampleBox(self.f(), gm_signature=self.gm_signature)
        #č Rozdělení transformovaného náhodného čísla je zadano jako 
        # special.kn(0, np.abs(x)) / np.pi # Breitung RESS 182 (2019) p. 99
        # kn(n, x) Modified Bessel function of the second kind of integer order n
        # modstruve(v, x) Modified Struve function of order v at x
        #č Odvození pf_exact z Maple
        #self.pf_exact = 0.5 - const/2 * (StruveL1 * BesselK0 + StruveL0 * BesselK1 + 2/np.pi * BesselK0)
        self.pf_exact = gauss_prod_CDF(-self.const) / 2
        self.pf_exact_method = 'exact (Bessel) solution' 
        self.r_exact = np.sqrt(np.abs(self.const) * 2)
        
    def __str__(wt):
        return  'Gaussian_Hyperbola_2D'
        
    def __repr__(wt):
        return  'Gaussian_Hyperbola_2D(const=%s)' % wt.const


#č já jsem si najednou uvědomil, že v tomto modulu
#č mám náprosto hrozný mix Camel- a snailcas'u.
#č Výmluvím z toho tak, podtržitko odděluje rozdělení a nazev g-modelu
class Gaussian_ProdFourBetas_2D(WhiteBox): 
    def __init__(self, beta=2):
        """
        Breitung RESS 182 (2019) p. 99
        """
        assert beta > 0
        self.beta = beta
        self.const = self.beta**2/2
        
        self.gm = g_models.Prod_FourBetas(self.beta)
        self.f = f_models.SNorm(2)
        #č na začatku nemáme vzorky - pouze rozdělení a podpís
        self.sample_box = SampleBox(self.f(), gm_signature=self.gm_signature)
        #č Rozdělení transformovaného náhodného čísla je zadano jako 
        # special.kn(0, np.abs(x)) / np.pi # Breitung RESS 182 (2019) p. 99
        # kn(n, x) Modified Bessel function of the second kind of integer order n
        # modstruve(v, x) Modified Struve function of order v at x
        #č Odvození pf_exact z Maple
        const = np.abs(self.const)
        StruveL0 = special.modstruve(0, const)
        StruveL1 = special.modstruve(1, const)
        BesselK0 = special.kn(0, const)
        BesselK1 = special.kn(1, const)
        self.pf_exact = 1 - const * (StruveL1 * BesselK0 + StruveL0 * BesselK1 + 2/np.pi * BesselK0)
        self.pf_exact_method = 'exact (Bessel) solution' 
        self.r_exact = self.beta
        
    def __str__(wt):
        return  'Gaussian_ProdFourBetas_2D'
        
    def __repr__(wt):
        return  'Gaussian_ProdFourBetas_2D(beta=%s)' % wt.beta


class Lognormal_Z_prod(WhiteBox): #č ověřím to moje odvození...
    def __init__(self, nvar=2, beta_exact=5, sign=1):
        """
        
        """
        self._sign = sign
        const = -np.exp(-np.sign(sign) * beta_exact * np.sqrt(nvar))
        self.gm = g_models.Z_prod(const, sign)
        self.f = f_models.UnCorD([stats.lognorm(s=1) for __ in range(nvar)])
        #č na začatku nemáme vzorky - pouze rozdělení a podpís
        self.sample_box = SampleBox(self.f(), gm_signature=self.gm_signature)
        
        self.beta_exact = beta_exact
        self.pf_exact = stats.norm.cdf(-self.beta_exact)
        self.pf_exact_method = 'FORM (exact solution)' # Ang, Tang and Pythagoras
        self.r_exact = self.beta_exact
        
    def __str__(wt):
        return  'Lognormal_Z_prod%sD'%(wt.f.nvar)
        
    def __repr__(wt):
        return  'Lognormal_Z_prod(nvar=%s, %s, %s)' % (wt.f.nvar, wt.beta_exact, wt.sign)


class Gaussian_Z_min(WhiteBox):
    def __init__(self, ndim=2, **kwargs):
        "je třeba zadat buď pf_exact, nebo konštantu u funkce minima Z_min"
        
        self.f = f_models.SNorm(ndim)
        self.ndim = ndim
    
        
        self.pf_exact_method = 'exact solution'
        if 'pf_exact' in kwargs:
            self.pf_exact = kwargs['pf_exact']
            sf = 1 - mpmath.root(1 - mpmath.mpf(self.pf_exact), ndim)
            self.const = stats.norm.isf(float(sf))
        elif 'const' in kwargs:
            self.const = kwargs['const']
            self.pf_exact = float(1 - mpmath.ncdf(self.const)**ndim)
        else:
            raise ValueError
        self.r_exact = self.const
        self.gm = g_models.Z_min(self.const) # min(X1, X2, XN) + const
        # na začatku nemáme vzorky - pouze rozdělení a podpís
        self.sample_box = SampleBox(self.f(), gm_signature=self.gm_signature)

    def __str__(self):
        return  'Gaussian_Z_min%sD'%(self.ndim)
        
    def __repr__(self):
        return  'Gaussian_Z_min(%s, pf_exact=%s)' % (repr(self.ndim), repr(self.pf_exact))


class Weibull_Z_min(WhiteBox):
    def __init__(self, wb_scales=(1.,1.), shape=5, **kwargs):
        """
        parametry pravdepodobnostniho rozdeleni pro Z_min s Weib. velicinami
        wb_scales=(1,1) - tuple of Weibull scale parameters, len(wb_scales)==nvar
        shape = 5 
        je třeba zadat buď pf_exact, nebo konštantu u funkce minima Z_min
        """
        self.wb_scales = wb_scales
        self.shape = 5
        self.f = f_models.UnCorD([stats.weibull_min(shape, scale=sc_i) for sc_i in wb_scales])
        
        # scale parametr minima z nvar Weibullovskych
        # tohle by platilo pro stejná rozdělení
        #sn = scale * nvar ** (-1.0 / shape)
        # pro nás musí to být něco takovýho
        sn = np.sum(np.power(wb_scales, -shape)) ** (-1.0 / shape)
        self.rvweibmin = stats.weibull_min(shape, scale=sn)
        
        # je třeba zadat buď pf_exact, nebo konštantu u funkce minima Z_min
        self.pf_exact_method = 'exact solution'
        if 'pf_exact' in kwargs:
            self.pf_exact = kwargs['pf_exact']
            self.const = -self.rvweibmin.ppf(self.pf_exact)
        elif 'beta_exact' in kwargs:
            self.beta_exact = kwargs['beta_exact']
            self.const = -self.rvweibmin.ppf(self.pf_exact)
        elif 'const' in kwargs:
            self.const = kwargs['const']
            self.pf_exact = self.rvweibmin.cdf(-self.const) # asi
        else:
            # no to teda uživatele пошли
            self.pf_exact = 1e-4
            self.const = -self.rvweibmin.ppf(self.pf_exact)
        
        sf = 1 - mpmath.root(1 - mpmath.mpf(self.pf_exact), len(wb_scales))
        self.r_exact = stats.norm.isf(float(sf))
        self.gm = g_models.Z_min(self.const)
        # na začatku nemáme vzorky - pouze rozdělení a podpís
        self.sample_box = SampleBox(self.f(), gm_signature=self.gm_signature)

    def __str__(self):
        return  'Weibull_Z_min%sD'%(len(self.wb_scales))
        
    def __repr__(self):
        return  'Weibull_Z_min(%s, %s, pf_exact=%s)' % (repr(self.wb_scales), repr(self.shape), repr(self.pf_exact))


class Gaussian_Z_max(WhiteBox):
    def __init__(self, ndim=2, **kwargs):
        "je třeba zadat buď pf_exact, nebo konštantu u funkce maxima Z_max"
        
        self.f = f_models.SNorm(ndim)
        self.ndim = ndim
    
        
        self.pf_exact_method = 'exact solution'
        if 'pf_exact' in kwargs:
            self.pf_exact = kwargs['pf_exact']
            cdf = mpmath.root(self.pf_exact, ndim)
            self.const = -stats.norm.ppf(float(cdf))
        elif 'const' in kwargs:
            self.const = kwargs['const']
            self.pf_exact = float(mpmath.ncdf(-self.const)**ndim)
        else:
            raise ValueError
        self.r_exact = np.sqrt(self.const**2 * ndim)
        self.gm = g_models.Z_max(self.const) # min(X1, X2, XN) + const
        # na začatku nemáme vzorky - pouze rozdělení a podpís
        self.sample_box = SampleBox(self.f(), gm_signature=self.gm_signature)

    def __str__(self):
        return  'Gaussian_Z_max%sD'%(self.ndim)
        
    def __repr__(self):
        return  'Gaussian_Z_max(%s, pf_exact=%s)' % (repr(self.ndim), repr(self.pf_exact))


#č masturbace
class Gaussian_Z_sumexp_2D(WhiteBox):
    def __init__(self, const):
        self.const = const
        self.f = f_models.SNorm(2)
        self.beta = np.sqrt(-np.log(-self.const/2)*2) 
        self.pf_exact_method = 'rude (product) asymptotic approximation'
        self.pf_exact = stats.norm.cdf(-self.beta) * 2 * np.sqrt(2)
        
        self.gm = g_models.Z_sumexp(self.const)
        # na začatku nemáme vzorky - pouze rozdělení a podpís
        self.sample_box = SampleBox(self.f(), gm_signature=self.gm_signature)
     
    def __str__(self):
        return  'Gaussian_Z_sumexp_2D'
        
    def __repr__(self):
        return  'Gaussian_Z_sumexp_2D(%s)' % repr(self.const)

#č masturbace pro příště
#č tady jsou nekorektní hračky s momenty rozdělení
#č není známo, jestli se někdy do tohoto kódu dorazí
#č korektní výpočet pf
#class Gaussian_Z_sumexp(WhiteBox):
#    def __init__(self, nvar=2, **kwargs):
#        """
#        je třeba zadat buď pf_exact, nebo konštantu u funkce Z_sumexp
#        """
#        
#        # je tam předpoklad SNormu?
#        self.f = f_models.SNorm(nvar)
#        
#        self.C1 = np.sqrt(np.sqrt(5) / 3. - 1. / 3.)
#        self.C2 = np.sqrt(3.) / 3.
#        # je třeba zadat buď pf_exact, nebo konštantu u funkce Z_sumexp
#        self.pf_exact_method = 'tešt solution'
#        if 'pf_exact' in kwargs:
#            self.pf_exact = kwargs['pf_exact']
#            self.C = self.beta_exact * self.C1 * np.sqrt(nvar) - self.C2 * nvar
#        elif 'beta_exact' in kwargs:
#            self.beta_exact = kwargs['beta_exact']
#            self.C = self.beta_exact * self.C1 * np.sqrt(nvar) - self.C2 * nvar
#        elif 'const' in kwargs:
#            self.const = kwargs['const']
#            self.C = self.const
#            self.beta_exact = (self.C + self.C2 * nvar) / self.C1 / np.sqrt(nvar)
#        elif 'C' in kwargs:
#            self.C = kwargs['C']
#            self.beta_exact = (self.C + self.C2 * nvar) / self.C1 / np.sqrt(nvar)
#        else:
#            # no to teda uživatele пошли
#            self.pf_exact = 1e-4
#            self.C = self.beta_exact * self.C1 * np.sqrt(nvar) - self.C2 * nvar
#        
#        
#        self.const = self.C
#        self.gm = g_models.Z_sumexp(self.const)
#        # na začatku nemáme vzorky - pouze rozdělení a podpís
#        self.sample_box = SampleBox(self.f(), gm_signature=self.gm_signature)
#     
#    def __str__(self):
#        return  'Gaussian_Z_sumexp%sD'%(self.nvar)
#        
#    def __repr__(self):
#        return  'Gaussian_Z_sumexp(%s, pf_exact=%s)' % (repr(self.nvar), repr(self.pf_exact))   



class SNorm_Z_sumsq(WhiteBox):
    def __init__(self, nvar=2, **kwargs):
        """
        je třeba zadat buď pf_exact, nebo konštantu u funkce Z_sumsq
        """
        
        # je tu předpoklad SNormu, to vím
        self.f = f_models.SNorm(nvar)
        
        self.rvchisq = stats.chi2(nvar)
        
        # je třeba zadat buď pf_exact, nebo konštantu u funkce Z_sumsq
        self.pf_exact_method = 'exact solution'
        if 'pf_exact' in kwargs:
            self.pf_exact = kwargs['pf_exact']
            self.C = self.rvchisq.ppf(self.pf_exact)
        elif 'beta_exact' in kwargs:
            self.beta_exact = kwargs['beta_exact']
            self.C = self.rvchisq.ppf(self.pf_exact)
        elif 'const' in kwargs:
            self.const = kwargs['const']
            self.C = self.const
            self.pf_exact = self.rvchisq.cdf(self.C)
        elif 'C' in kwargs:
            self.C = kwargs['C']
            self.pf_exact = self.rvchisq.cdf(self.C)
        else:
            # no to teda uživatele пошли
            self.pf_exact = 1e-4
            self.C = self.rvchisq.ppf(self.pf_exact)
        
        
        self.const = self.C
        self.R_exact = np.sqrt(self.const)
        self.gm = g_models.Z_sumsq(self.C)
        # na začatku nemáme vzorky - pouze rozdělení a podpís
        self.sample_box = SampleBox(self.f(), gm_signature=self.gm_signature)
     
    def __str__(self):
        return  'SNorm_Z_sumsq%sD'%(self.nvar)
        
    def __repr__(self):
        return  'SNorm_Z_sumsq(%s, pf_exact=%s)' % (repr(self.nvar), repr(self.pf_exact))   






class SNorm_S_ball(WhiteBox):
    #r = 5.256521 # pf 1.00000404635e-06
    def __init__(self, nvar=2, r=5.256521):
        
        
        # SNorm
        self.f = f_models.SNorm(nvar)
        
        
        #
        #   pf, jen tak, hračka
        #
        self.pf_exact_method = 'precise solution'
        if nvar == 1:
            #self.pf_exact = 1 - 2**(1-nvar/2) / special.gamma(nvar/2)    *    (np.sqrt(np.pi)*special.erf(r/np.sqrt(2)))/np.sqrt(2)
            self.pf_exact = 1 - special.erf(r/1.4142135623730951)
        elif nvar == 2:
            self.pf_exact = np.exp(-r**2/2)
        elif nvar == 3:
            #self.pf_exact = 1 - 2**(1-nvar/2) / special.gamma(nvar/2)    *    (np.exp(-r**2/2)*(np.sqrt(np.pi)*np.exp(r**2/2)*special.erf(r/np.sqrt(2))-np.sqrt(2)*r))/np.sqrt(2)
            self.pf_exact = 1 - 0.5641895835477564 * (np.exp(-r**2/2)*(np.sqrt(np.pi)*np.exp(r**2/2)*special.erf(r/np.sqrt(2))-np.sqrt(2)*r))
        elif nvar == 4:
            self.pf_exact = (r**2/2+1)*np.exp(-r**2/2)
        elif nvar == 6:
            self.pf_exact = (r**4+4*r**2+8)*np.exp(-r**2/2)/8
            
            # nvar=8:  (48-(r^6+6*r^4+24*r^2+48)*e^(-r^2/2)  / 2**(nvar/2))/48
            
            # hračička ve hračce
            # nemám žádnou jistotu, že tohle počítá přesněji
        elif nvar % 2 == 0: # sudé
            poly = [1]
            for i in range(nvar-2, 0, -2):
                poly.append(0)
                poly.append(i*poly[-2])
            self.pf_exact = np.polyval(np.array(poly) / poly[-1], r) * np.exp(-r**2/2) 
            
        else:
            self.pf_exact = 1 - 2**(1-nvar/2) / special.gamma(nvar/2)    *    integrate.quad(lambda x: np.exp(-(x**2)/2)*x**(nvar-1), 0, r)[0] 
        
        
        self.r = r
        self.r_exact = self.r
        self.gm = g_models.S_ball(r)
        # na začatku nemáme vzorky - pouze rozdělení a podpís
        self.sample_box = SampleBox(self.f(), gm_signature=self.gm_signature)
     
    def __str__(self):
        return  'SNorm_S_ball%sD'%(self.nvar)
        
    def __repr__(self):
        return  'SNorm_S_ball(nvar=%s, r=%s)' % (repr(self.nvar), repr(self.r))   


