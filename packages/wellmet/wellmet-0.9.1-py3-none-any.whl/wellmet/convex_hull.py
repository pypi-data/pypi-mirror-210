#!/usr/bin/env python
# coding: utf-8

import numpy as np
import mpmath
from scipy import stats
from scipy import spatial # for QHull
from scipy import special # for QHull outside integration

from . import sball

import quadpy

from collections import namedtuple

mpmath.mp.dps = 325 # to cover anything that double-presigion float can handle

# maximum radius, where norm.pdf() wasn't zero
# -38.575500173381374935388521407730877399444580.....
# don't ask me what the magic python use to distinguish
# digits after double precision
max_R_ever = 37

#č jako sůl potřebujem statefull třidu,
#č která by schovávala vnitřní implementaciju,
#č která by nabízela jednotné rozhraní pro ostatní kód WellMet
#č a byla by přiměřeně kompatibilní s ConvexHull ze scipy.spatial
#č Ze scipy bych viděl podporu atributů .points, .npoints, .equations
#č Určitě bych chtěl funkce .update() a .is_outside(sample)
#č Atribute .space by ukazoval, v jakém prostoru konvexní obál je vytvořen
# GBall, BrickHull, DirectHull, CompleteHull and QHull has been implemented


def calculate_brick_complement_probability(mins, maxs):
    "For Gaussian space"
    #č na začátku nastavíme obyčejnou 1
    #č v cyklu bude nasobit delkami 
    #č podle jednotlivých souřadnic
    #č a typ se změní na mpf (hodně přesná aritmetika)
    volume = 1
    
    # ncdf() do not support matrix input
    for xmin, xmax in zip(mins, maxs):
        volume *= mpmath.ncdf(xmax) - mpmath.ncdf(xmin)
    
    # print test
#    if len(mins) == 2:
#        min_x, min_y = mins
#        max_x, max_y = maxs
#        test_volume = 0
#        test_volume += np.sum(stats.norm.cdf(mins)) 
#        test_volume += np.sum(stats.norm.sf(maxs))
#        test_volume -= stats.norm.cdf(min_x) * stats.norm.cdf(min_y)
#        test_volume -= stats.norm.cdf(min_x) * stats.norm.sf(max_y)
#        test_volume -= stats.norm.sf(max_x) * stats.norm.cdf(min_y)
#        test_volume -= stats.norm.sf(max_x) * stats.norm.sf(max_y)
#        print("test_volume:", test_volume)  
        
    return float(1-volume)
    
# inspired by 
# https://math.stackexchange.com/questions/192610/how-to-build-a-orthogonal-basis-from-a-vector/979013
# most interesting from there:
# """Pick a vector. WLOG, you chose $(x_1,x_2,x_3,x_4)$. 
# Now write it as a quaternion: $$x_1+ix_2+jx_3+kx_4$$ 
# Then, since multiplication by $i,j,k$ 
# rotates this vector $90^0$ across the various axes of our 4D space,
# the following three vectors make your initial choice of vector into an orthonormal basis: 
# $$i(x_1+ix_2+jx_3+kx_4)=ix_1-x_2+kx_3-jx_4\mapsto (-x_2,x_1,-x_4,x_3)$$ 
# $$j(x_1+ix_2+jx_3+kx_4)=jx_1-kx_2-x_3+ix_4\mapsto (-x_3,x_4,x_1,-x_2)$$
# $$k(x_1+ix_2+jx_3+kx_4)=kx_1+jx_2-ix_3-x_4\mapsto (-x_4,-x_3,x_2,x_1)$$"""
def get_orth_basis(vector):
    dim = len(vector)
    if dim == 2:
        x, y = vector
        return np.array([[x, y],[-y, x]])
    elif dim == 4:
        x_1, x_2, x_3, x_4 = vector
        return np.array([
            [x_1, x_2, x_3, x_4],
            [-x_2, x_1, -x_4, x_3],
            [-x_3, x_4, x_1, -x_2],
            [-x_4, -x_3, x_2, x_1]])
    else:
        random_basis = np.random.random((dim, dim))
        #č QR rozklad jede po sloupcich
        random_basis[:,0] = vector
        #č co jsem viděl, numpy matici Q normalizuje
        #č a první sloupec zůstavá (skoro) tím samým, co byl před tím
        Q, __R = np.linalg.qr(random_basis)
        # yep. Numpy sometimes inverts sign of the first Q matrix vector
        Q[:,0] = vector
        return Q.T
    
        
        
#ё рельса
#č nepodařílo se mi nějak rozumně zobecnit pro libovolný prostor
#č takže Gauss
#č (každá třida implementuje zvlášť)

def shot(hull, ns, use_MC=False):
    if hull.space == 'G':
        to_fire = np.nanargmax(hull.b)
        r = -hull.b[to_fire]
        a = hull.A[to_fire]
        
        if use_MC:
            fire_from = stats.norm.sf(r)
            t = np.linspace(fire_from, 0, ns, endpoint=False)
            t = stats.norm.isf(t)
        else:
            if r < max_R_ever:
                R = max_R_ever
            else:
                R = r + 10
            t = np.linspace(r, R, ns, endpoint=True)
            
        fire_G = t.reshape(-1,1) @ a.reshape(1,-1)
        return hull.sample.f_model.new_sample(fire_G, space='G')


def fire(hull, ns, use_MC=False):
    if hull.space == 'G':
        to_fire = np.nanargmax(hull.b)
        r = -hull.b[to_fire]
        a = hull.A[to_fire]
        
        orth_nodes_T = np.random.randn(len(a), ns) # len(a) == ndim
        orth_basis = get_orth_basis(a)
        
        if use_MC:
            fire_from = stats.norm.sf(r)
            t = np.linspace(fire_from, 0, ns, endpoint=False)
            orth_nodes_T[0] = stats.norm.isf(t)
        else:
            if r < max_R_ever:
                R = max_R_ever
            else:
                R = r + 10
            orth_nodes_T[0] = np.linspace(r, R, ns, endpoint=True)
            
        fire_G = (orth_basis.T @ orth_nodes_T).T
        return hull.sample.f_model.new_sample(fire_G, space='G')

#
# Common orth functions for DirectHull, CompleteHull and QHull
#

# (even private function can be shared :D )
def _orth_helper(hull):
    # supposed hull.space == 'G'
    hull._update()
    
    
    ndim = hull.sample.nvar
    #č je to špatné z hlediska testování,
    #č ale nevím jak z toho.
    #č pro 2D musím udělat vyjimku z "předposlední"
    if ndim > 2:
        orth_basis = _get_nD_orth_basis(hull)
    else:
        to_fire = np.nanargmax(hull.b)
        a = hull.A[to_fire]
        orth_basis = get_orth_basis(a)
    
    #č musí tam bejt G coordinates
    A = orth_basis @ hull.points.T
    bp = np.nanmax(A, axis=1)
    bm = np.nanmin(A, axis=1)
    
    return orth_basis, bp, bm
    
    

def _get_nD_orth_basis(hull):
    # supposed hull.space == 'G'
    # supposed hull._update()
    
    #č bůhví, jestli obálka negeneruje A a b-čko dynamicky
    b = hull.b
    A = hull.A 
    
    return _get_nD_orth_basis_from_normals(A, b)
    
    
def _get_nD_orth_basis_from_normals(A, b):
    _nplates, ndim = A.shape
    
    #č pro 2D "nastav první a pak po veškerem zbytku 
    #č ještě ten předposlední vektor" špatně funguje
    assert ndim > 2
    
    to_fire = np.nanargmax(b)
    a = A[to_fire]
    
    
    #č QR rozklad jede po sloupcich
    basis_T = np.empty((ndim, ndim)) 
    basis_T[:,0] = a
    
    #č skalarní součín
    cos = A @ a
    bcos = b * (1 + np.abs(cos))
    
    for i in range(1, ndim-2):
        
        to_fire = np.nanargmax(bcos)
        next_vector = A[to_fire]
        
        #č QR rozklad komplikuje život transponovanim matic
        basis_T[:,i] = next_vector
        basis_T[:, :i+1], __R = np.linalg.qr(basis_T[:, :i+1])
        
        next_orth_vector = basis_T[:,i]
        
        #č skalarní součín
        cos = A @ next_orth_vector
        bcos *= (1 + np.abs(cos))
        
    
    to_fire = np.nanargmax(bcos)
    #č předposlední vektor
    next_vector = A[to_fire]
    basis_T[:,ndim-2] = next_vector
    #č a už ready. Poslední vektor je určen předchozími
    basis_T, __R = np.linalg.qr(basis_T)
    
    #č QR rozklad jede po sloupcich
    #č co jsem viděl, numpy matici Q normalizuje
    #č a první sloupec zůstavá (skoro) tím samým, co byl před tím
    #Q, __R = np.linalg.qr(basis.T)
    # yep. Numpy sometimes inverts sign of the first Q matrix vector
    #č ale na znáky kašleme. To je důležité pro kandidaty,
    #č zde nám ale jde o basis
    orth_basis = basis_T.T
    
    return orth_basis
    
    
def get_orth_outside(hull):
    if hull.space == 'G' :
        # hull._update() will perform _orth_helper()
        A, bp, bm = hull._orth_helper()
        return calculate_brick_complement_probability(bm, bp)
    else:
        #č když prostor není G, můžeme sice něco odvodit od s-ball 
        #č ale nechť se s tím pará GHull, vrátíme nulu.
        return 0

def get_orth_equations(hull):
    # hull._update() will perform _orth_helper()
    direct_plan, bp, bm = hull._orth_helper()

    A = np.vstack((-direct_plan, direct_plan))
    b = np.concatenate((bm, -bp))
    return np.hstack((A,b[:,None]))     


#
# Common 2FORM functions for DirectHull, CompleteHull and QHull
#

# (even private function can be shared :D )
def _2FORM_helper(hull):
    # supposed hull.space == 'G'
    hull._update()
    to_fire = np.nanargmax(hull.b)
    a = hull.A[to_fire]
    
    #č musí tam bejt G coordinates
    # we'll get 1D npoints-sized negative b array
    x = a @ hull.points.T
    # here x == _b array has another meaning than hull.b
    # where in hull.b we search for least distanced hyperplane
    # here, in x, we search for a valid b_backward hyperplane offset
    # It can be seen as transformation of the ED to 1D a-projection.
    # There evidently exist min(x) and max(x)
    # such that every single x value lies inside (between)
    # max(x) (forward) value should be corresponding to r, to -hull.b
    # So, we need to find min(x) (backward) value
    # x_forward == max(x) == -b == r == max(a @ points.T) == -max(hull.b) == min(-hull.b)
    # x_backward == min(x) == max(-a @ points.T)
    x_forward = np.max(x)
    x_backward = np.min(x)
    #print(-np.max(hull.b), x_forward) 
    return x_backward, x_forward, a


def get_2FORM_outside(hull):
    if hull.space == 'G':
        # hull._update() will perform _FORM_helper()
        x_backward, x_forward, __a = hull._2FORM_helper()
        return stats.norm.cdf(x_backward) + stats.norm.sf(x_forward)
    else:
        #č když prostor není G, můžeme sice něco odvodit od s-ball 
        #č ale nechť se s tím pará GHull, vrátíme nulu.
        return 0
            
def get_2FORM_equations(hull):
    # hull._update() will perform _2FORM_helper()
    x_backward, x_forward, a = hull._2FORM_helper()
    A = np.vstack((-a, a))
    b = np.array([[x_backward],[-x_forward]])
    return np.hstack((A,b))  
    
def get_bp_bm(A, points):
    B = A @ points.T
    bp = np.nanmax(B, axis=1)
    bm = np.nanmin(B, axis=1)
    return bp, bm
    

#č jistě musíme mít nějaký zbytečný kus kódu
#č třida jen pro formu, jen tak na hračku
#č když tečíčky jsou dále jak nejvzdálenější vzorek (bod),
#č tak řekneme, že jsou totálně mimo!
class GBall:
    def __init__(hull, sample):
        hull.sample = sample
        hull.space = 'G' #оӵ малы? Кинлы со кулэ?
    
    @property
    def points(hull):
        return hull.sample.G
        
    @property
    def npoints(hull):
        return len(hull.sample)
        
    @property
    def nsimplex(hull):
        return 1
        
    #def update(hull): pass
    
    def is_inside(hull, nodes):
        R2_hull = np.nanmax(np.sum(np.square(hull.sample.G), axis=1))
        
        R2_nodes = np.sum(np.square(nodes.G), axis=1)
        return R2_nodes < R2_hull 

    def is_outside(hull, nodes): 
        return ~hull.is_inside(nodes)
        
    def get_R(hull):
        return np.sqrt(np.nanmax(np.sum(np.square(hull.sample.G), axis=1)))
        
    def get_r(hull): 
        # zero at best, 
        # on the safe side, between -R and 0
        #r2_hull = np.nanmin(np.sum(np.square(hull.sample.G), axis=1))
        #return -np.sqrt(r2_hull)
        
        #č když na get_r nahlížím z hlediska toho,
        #č že r vymezuje mezikruží, kde nejsme jistí
        #č inside-outside,
        #č tak zde get_r vždy musí vracet prostě R
        return hull.get_R()
        
    def get_orth_outside(hull):
        x = np.full(hull.sample.nvar, hull.get_r())
        return calculate_brick_complement_probability(-x, x)
        
     
    def get_2FORM_outside(hull):
        return 2*stats.norm.sf(hull.get_r())
        
     
    def fire(hull, *args, **kwargs):
        pass
    
    def shot(hull, *args, **kwargs):
        pass
        


#č vyhejbám slovu Box, ať nevnáším ještě víc zmatku v označení
class BrickHull: #č nebo BoundingBrick
    def __init__(hull, sample, space='G'):
        hull.sample = sample
        hull.space = space
        
        
        hull._npoints = 0
        #č miny a maxy obsahují minima a maxima 
        #č podel jednotlivých souřadnic (proměnných)
        #č sincerely yours, Captain Obvious.
        hull.mins = np.full(hull.sample.nvar, np.inf)
        hull.maxs = np.full(hull.sample.nvar, -np.inf)
    
    def _update(hull):
        if hull._npoints < hull.npoints:
            hull.mins = np.nanmin(hull.points, axis=0)
            hull.maxs = np.nanmax(hull.points, axis=0)
            hull._npoints = hull.npoints
        
        
    def is_inside(hull, nodes):
        hull._update()
        x = getattr(nodes, hull.space)
        more = np.all(x < hull.maxs, axis=1)
        less = np.all(x > hull.mins, axis=1)
        
        return np.all((more, less), axis=0) #np.all(np.array((more, less)), axis=0)
        
    def is_outside(hull, nodes): 
        return ~hull.is_inside(nodes)
        
    def get_hyperplane_distances(hull, nodes):
        hull._update()
        x = getattr(nodes, hull.space)
        maxs = np.nanmax(x - hull.maxs, axis=1)
        mins = np.nanmax(hull.mins - x, axis=1)
        
        return np.max((maxs, mins), axis=0) #np.all(np.array((more, less)), axis=0)
        
    def get_design_points(hull):
        hull._update()
        #sample_model = -hull.A * hull.b.reshape(-1,1)
        sample_model = np.vstack((np.diag(hull.maxs), np.diag(hull.mins)))
        return hull.sample.f_model.new_sample(sample_model, space=hull.space)
        
    def get_exploration_vector(hull):
        hull._update()
        to_fire = np.nanargmax(hull.b)
        return hull.A[to_fire], hull.b[to_fire], hull.sample
        
    # shortcut for Ghull
    # valid only if space==G
    def get_r(hull):
        if hull.space=='G':
            hull._update()
            return np.min((-hull.mins, hull.maxs))
        else:
            return 0
        
    @property
    def points(hull):
        return getattr(hull.sample, hull.space)
        
    @property
    def npoints(hull):
        return len(hull.sample)
        
    @property
    def nsimplex(hull):
        return hull.sample.nvar*2
        
    @property
    def A(hull):
        hull._update()
        #č žádná optimizace, ale kdo tu funkci bude spouštět?
        diag = np.diag(np.ones(hull.sample.nvar))
        return np.vstack((diag, -diag))
        
    @property
    def b(hull):
        hull._update()
        return np.concatenate((hull.maxs, -hull.mins))
        
    @property
    def equations(hull):
        hull._update()
        #č žádná optimizace, ale kdo tu funkci bude spouštět?
        diag = np.diag(np.ones(hull.sample.nvar))
        
        A = np.vstack((diag, -diag))
        b = np.concatenate((-hull.maxs, hull.mins))
        return np.hstack((A,b[:,None]))
        
        
    def get_orth_outside(hull):
        if hull.space == 'G':
            hull._update()
            return calculate_brick_complement_probability(hull.mins, hull.maxs)
        else:
            #č když prostor není G, můžeme sice něco odvodit od s-ball 
            #č ale nechť se s tím pará GHull, vrátíme nulu.
            return 0
            
    def get_orth_equations(hull):
        return hull.equations
        
        
    def _2FORM_helper(hull):
        hull._update()
        #č je to úplně zbýtečně trapit se nejakejma argama
        #č poďme na to globálně!
        #č (doufám, že nvar*2 výpočtů cdf() nikomu neublíží... )
        #min_arg = np.nanargmin(hull.mins)
        #max_arg = np.nanargmax(hull.maxs)
        cdfs = stats.norm.cdf(hull.mins)
        sfs = stats.norm.sf(hull.maxs)
        #č _update() počítá nanmin a nanmax
        #č takže nemusíme se bat nějakého hnusu v číslech
        pfs = cdfs + sfs
        i = np.argmax(pfs) # number of variable
        # we'll return 2FORM estimation 
        # and corresponding number of variable
        return pfs[i], i
        
        
    def get_2FORM_outside(hull):
        if hull.space == 'G':
            # hull._update() will perform _FORM_helper()
            p_out, __i = hull._2FORM_helper()
            return p_out
        else:
            #č když prostor není G, můžeme sice něco odvodit od s-ball 
            #č ale nechť se s tím pará GHull, vrátíme nulu.
            return 0
            
        
    def get_2FORM_equations(hull):
        __p_out, i = hull._2FORM_helper()
        equations = np.zeros((2,hull.sample.nvar+1))
        equations[0, i] = 1
        equations[0, -1] = -hull.maxs[i]
        equations[1, i] = -1
        equations[1, -1] = hull.mins[i]
        return equations
        
    def shot(hull, *args, **kwargs):
        pass
        
        # add use_MC to the function signature
        # but remain unimplemented for now
        #č ten fire je hrozný. Výhodit U prostor 
        #č (jsou tam nepřesné cdf transformace)
        #č po úpravě přídat hull._update() na začátku.
    def fire(hull, ns, use_MC=False): # boom
        sample_U = hull.sample.U
        
        U_mins = np.nanmin(sample_U, axis=0)
        U_maxs = np.nanmax(sample_U, axis=0)
        
        #č min nebo max?
        if np.nanmax(U_mins) > (1-np.nanmin(U_maxs)):
            #č expandujeme se dolu
            var = np.nanargmax(U_mins)
            value = U_mins[var]
            t = np.linspace(value, 0, ns, endpoint=False)
        else:
            #č expandujeme se nahoru
            var = np.nanargmin(U_maxs)
            value = U_maxs[var]
            t = np.linspace(value, 1, ns, endpoint=False)
        
        boom = np.random.random((ns, hull.sample.nvar))
        boom[:, var] = t
        
        return hull.sample.f_model.new_sample(boom, space='U')
    

class DirectHull:
    # take some global functions
    fire = fire
    shot = shot
    _orth_helper = _orth_helper
    get_orth_outside = get_orth_outside
    get_orth_equations = get_orth_equations
    
    _2FORM_helper = _2FORM_helper
    get_2FORM_outside = get_2FORM_outside
    get_2FORM_equations = get_2FORM_equations
    
    
    def __init__(hull, sample, direct_plan, space='G'):
        hull.sample = sample
        hull.direct_plan = direct_plan
        hull.space = space
        
        hull.regen()
        
    def regen(hull):
        hull._npoints = 0
        
        hull.bp = np.full(len(hull.direct_plan), -np.inf)
        #hull.update()
    
    #č nejsem jist, jestli ten update vůbec dělat.
    #č lze navrhnout třidu aj tak, že sama bude hlídat změny.
    #č Jenomže, co kdybychom ten automatický update nechtěli?
    def _update(hull):
        if hull._npoints < hull.npoints:
            #hull.points = getattr(hull.sample, hull.space)
            new_points = hull.points[hull._npoints:]
            
            A = hull.direct_plan @ new_points.T
            new_bp = np.nanmax(A, axis=1)
            hull.bp = np.nanmax((new_bp, hull.bp), axis=0)
            
            hull._npoints = hull.npoints

    @property
    def points(hull):
        return getattr(hull.sample, hull.space)
        
    @property
    def npoints(hull):
        return len(hull.sample)
        
    @property
    def nsimplex(hull):
        return len(hull.direct_plan)
        
    @property
    def A(hull):
        return hull.direct_plan
        
    @property
    def b(hull):
        hull._update()
        return -hull.bp
        
    @property
    def equations(hull):
        return np.hstack((hull.A, hull.b[:,None]))

    def get_hyperplane_distances(self, nodes):
        self._update()
        x = getattr(nodes, self.space)
        
        #E [normal, offset] forming the hyperplane equation of the facet (see Qhull documentation for more)
        A = self.A
        b = self.b
        
        # N=ns, E - number of hyperplane equations
        ExN = A @ x.T + np.atleast_2d(b).T
        return np.nanmax(ExN, axis=0)
        
    def query(self, nodes):
        self._update()
        x = getattr(nodes, self.space)
        
        #E [normal, offset] forming the hyperplane equation of the facet (see Qhull documentation for more)
        A = self.A
        b = self.b
        
        # N=ns, E - number of hyperplane equations
        ExN = A @ x.T + np.atleast_2d(b).T
        i = np.argmax(ExN, axis=0)
        d = np.take_along_axis(ExN, np.atleast_2d(i), axis=0).reshape(-1)
        return d, i

    def is_inside(hull, nodes):
        hull._update()
        x = getattr(nodes, hull.space)
        
        #E [normal, offset] forming the hyperplane equation of the facet (see Qhull documentation for more)
        A = hull.direct_plan
        bp = np.atleast_2d(hull.bp).T
        
        # N=ns, E - number of hyperplane equations
        ExN = A @ x.T
        higher = np.all(ExN < bp, axis=0)
        return higher
    
    def is_outside(hull, nodes): 
        return ~hull.is_inside(nodes)
        
    def get_design_points(hull):
        hull._update()
        sample_model = -hull.A * hull.b.reshape(-1,1)
        return hull.sample.f_model.new_sample(sample_model, space=hull.space)
    
    def get_exploration_vector(hull):
        hull._update()
        to_fire = np.nanargmax(hull.b)
        return hull.A[to_fire], hull.b[to_fire], hull.sample
    
    # shortcut for Ghull
    # valid only if space==G
    def get_r(hull):
        if hull.space=='G':
            hull._update()
            return np.min(hull.bp)
        else:
            return 0
    
    


class CompleteHull:
    # take some global functions
    fire = fire
    shot = shot
    _orth_helper = _orth_helper
    get_orth_outside = get_orth_outside
    get_orth_equations = get_orth_equations
    
    _2FORM_helper = _2FORM_helper
    get_2FORM_outside = get_2FORM_outside
    get_2FORM_equations = get_2FORM_equations
    
    def __init__(hull, sample, direct_plan, space='G'):
        hull.sample = sample
        hull.direct_plan = direct_plan
        hull.space = space
        
        hull.regen()
        
    def regen(hull):
        hull._npoints = 0
        hull.mins = np.full(hull.sample.nvar, np.inf)
        hull.maxs = np.full(hull.sample.nvar, -np.inf)
        
        hull.bp = np.full(len(hull.direct_plan), -np.inf)
        hull.bm = np.full(len(hull.direct_plan), np.inf)
        
        #hull.update()
    
    #č nejsem jist, jestli ten update vůbec dělat.
    #č lze navrhnout třidu aj tak, že sama bude hlídat změny.
    #č Jenomže, co kdybychom ten automatický update nechtěli?
    def _update(hull):
        if hull._npoints < hull.npoints:
            #hull.points = getattr(hull.sample, hull.space)
            new_points = hull.points[hull._npoints:]
            
            new_mins = np.nanmin(new_points, axis=0)
            new_maxs = np.nanmax(new_points, axis=0)
            
            hull.mins = np.nanmin((new_mins, hull.mins), axis=0)
            hull.maxs = np.nanmax((new_maxs, hull.maxs), axis=0)
            
            A = hull.direct_plan @ new_points.T
            new_bp = np.nanmax(A, axis=1)
            new_bm = np.nanmin(A, axis=1)
            
            hull.bp = np.nanmax((new_bp, hull.bp), axis=0)
            hull.bm = np.nanmin((new_bm, hull.bm), axis=0)
            
            hull._npoints = hull.npoints

    @property
    def points(hull):
        return getattr(hull.sample, hull.space)
        
    @property
    def npoints(hull):
        return len(hull.sample)
        
    @property
    def nsimplex(hull):
        return 2 * (len(hull.direct_plan) + hull.sample.nvar)
        
    @property
    def A(hull):
        hull._update()
        #č žádná optimizace, ale kdo tu funkci bude spouštět?
        diag = np.diag(np.ones(hull.sample.nvar))
        return np.vstack((diag, -diag, -hull.direct_plan, hull.direct_plan))
        
    @property
    def b(hull):
        hull._update()
        return np.concatenate((-hull.maxs, hull.mins, hull.bm, -hull.bp))
        
    @property
    def equations(hull):
        hull._update()
        #č žádná optimizace, ale kdo tu funkci bude spouštět?
        diag = np.diag(np.ones(hull.sample.nvar))
        
        A = np.vstack((diag, -diag, -hull.direct_plan, hull.direct_plan))
        b = np.concatenate((-hull.maxs, hull.mins, hull.bm, -hull.bp))
        return np.hstack((A,b[:,None]))

    def is_inside(hull, nodes):
        hull._update()
        x = getattr(nodes, hull.space)
        
        more = np.all(x < hull.maxs, axis=1)
        less = np.all(x > hull.mins, axis=1)
        
        
        #E [normal, offset] forming the hyperplane equation of the facet (see Qhull documentation for more)
        A = hull.direct_plan
        bp = np.atleast_2d(hull.bp).T
        bm = np.atleast_2d(hull.bm).T
        
        # N=ns, E - number of hyperplane equations
        ExN = A @ x.T
        higher = np.all(ExN < bp, axis=0)
        lower = np.all(ExN > bm, axis=0)
        return np.all((more, less, higher, lower), axis=0)
    
    def is_outside(hull, nodes): 
        return ~hull.is_inside(nodes)
        
    def get_design_points(hull):
        hull._update()
        sample_model = -hull.A * hull.b.reshape(-1,1)
        return hull.sample.f_model.new_sample(sample_model, space=hull.space)
        
    # shortcut for Ghull
    # valid only if space==G
    def get_r(hull):
        if hull.space=='G':
            hull._update()
            return min(-np.max(hull.mins), np.min(hull.maxs), -np.max(hull.bm), np.min(hull.bp))
        else:
            return 0
    
            




QHullEstimation = namedtuple('QHullEstimation', (
                                                'nsim',
                                                'nvar',
                                                'nfacets',
                                                'r', 'R',
                                                'inner',
                                                'shell',
                                                'outer',
                                                'chi_outside',
                                                'orth_outside',
                                                #'tn_scheme',
                                                #'tn_scheme_points',
                                                'inside',
                                                'outside'
                                                ))


def get_nsphere_const(nvar, const=1):
    if nvar == 2:
        return const * 2 * np.pi
    elif nvar == 1:
        return const * 2
    else:
        return get_nsphere_const(nvar - 2, const * 2 * np.pi / (nvar - 2) )

class QHull:
    # take some global function
    _orth_helper = _orth_helper
    #get_orth_outside = get_orth_outside
    get_orth_equations = get_orth_equations
    
    _2FORM_helper = _2FORM_helper
    #get_2FORM_outside = get_2FORM_outside
    get_2FORM_equations = get_2FORM_equations
    
    def __init__(self, sample, space='G', incremental=True, auto_update=True, tn_scheme=None):
        self.sample = sample
        self.incremental = incremental
        self.space = space
        self.auto_update = auto_update
        
        self.sball = sball.Sball(sample.nvar)
        self.shell = sball.Shell(sample.nvar)
        self.fallback_plan = quadpy.un.mysovskikh_1(sample.nvar).points
        
        if tn_scheme is None:
            self.tn_scheme = quadpy.tn.grundmann_moeller(sample.nvar - 1, 5)
        else:
            self.tn_scheme = tn_scheme
        
        nvar = sample.nvar
        #self.chi_const = 2**((nvar - 1) / 2) * special.gamma(nvar - 1/2) / special.gamma(nvar / 2) 
        self.chi_like_const = np.sqrt(np.pi) / np.sqrt(2) / (2 * np.pi)**(nvar/2)
        self.nsphere_surface_area = get_nsphere_const(nvar)
    
    
    
    def regen(self):
        points = getattr(self.sample, self.space)
        self.convex_hull = spatial.ConvexHull(points, incremental=self.incremental)
        
    
    def __getattr__(self, attr):
        #č branime se rekurzii
        # defend against recursion
        #оӵ рекурсилы пезьдэт!
        if attr == 'convex_hull':
            #č zkusme rychle konvexní obálky sestavit
            #č a ihned ji vrátit
            self.regen()
            return self.convex_hull
        
        elif attr == 'enough_points':
            return self.sample.nvar < self.sample.nsim
            
        elif attr == 'A':
            return self.convex_hull.equations[:,:-1]
        elif attr == 'b':
            return self.convex_hull.equations[:,-1]
            
        elif attr == 'points':
            if self.enough_points:
                return self.convex_hull.points
            else:
                return getattr(self.sample, self.space)
                
        elif attr == 'npoints':
            if self.enough_points:
                return self.convex_hull.npoints
            else:
                return len(self.sample)
        
        elif attr == 'nsimplex':
            if self.enough_points:
                return self.convex_hull.nsimplex
            else:
                return 0
            
            
        #ё По всем вопросам обращайтесь 
        #ё на нашу горячую линию    
        else:
            self._update() #č dycky čerstý chleba!
            return getattr(self.convex_hull, attr)
            
    def _update(hull):
        if hull.auto_update:
            hull.update()            
    
    def update(self):
        if self.enough_points and (self.convex_hull.npoints < self.sample.nsim):
            if self.incremental:
                points = getattr(self.sample, self.space)  
                self.convex_hull.add_points(points[self.convex_hull.npoints:])
            else:
                self.regen()
    
    
    def get_hyperplane_distances(self, nodes):
        if self.enough_points:
            self._update()
            x = getattr(nodes, self.space)
            
            #E [normal, offset] forming the hyperplane equation of the facet (see Qhull documentation for more)
            A = self.convex_hull.equations[:,:-1]
            b = self.convex_hull.equations[:,-1]
            
            # N=ns, E - number of hyperplane equations
            ExN = A @ x.T + np.atleast_2d(b).T
            return np.nanmax(ExN, axis=0)
        else:
            return DirectHull(self.sample, self.fallback_plan, self.space).get_hyperplane_distances(nodes)
        
    def query(self, nodes):
        if self.enough_points:
            self._update()
            x = getattr(nodes, self.space)
            
            #E [normal, offset] forming the hyperplane equation of the facet (see Qhull documentation for more)
            A = self.convex_hull.equations[:,:-1]
            b = self.convex_hull.equations[:,-1]
            
            # N=ns, E - number of hyperplane equations
            ExN = A @ x.T + np.atleast_2d(b).T
            i = np.argmax(ExN, axis=0)
            d = np.take_along_axis(ExN, np.atleast_2d(i), axis=0).reshape(-1)
            return d, i
        else:
            return DirectHull(self.sample, self.fallback_plan, self.space).query(nodes)
        
    def is_inside(self, nodes):
        if self.enough_points:
            self._update()
            x = getattr(nodes, self.space)
            
            #E [normal, offset] forming the hyperplane equation of the facet (see Qhull documentation for more)
            A = self.convex_hull.equations[:,:-1]
            b = self.convex_hull.equations[:,-1]
            
            # N=ns, E - number of hyperplane equations
            ExN = A @ x.T + np.atleast_2d(b).T
            mask = np.all(ExN < 0, axis=0)
            return mask
        else:
            return np.full(len(nodes), False)
    
    def is_outside(hull, nodes): 
        if hull.enough_points:
            return ~hull.is_inside(nodes)
        else:
            return np.full(len(nodes), True)
        
    def get_design_points(hull):
        hull._update()
        sample_model = -hull.A * hull.b.reshape(-1,1)
        return hull.sample.f_model.new_sample(sample_model, space=hull.space)
        
    def get_design_point(hull):
        hull._update()
        to_fire = np.nanargmax(hull.b) #č tak, pro jistotu
        sample_model = -hull.A[to_fire] * hull.b[to_fire]
        return hull.sample.f_model.new_sample(sample_model, space=hull.space)
    
    def get_exploration_vector(hull):
        hull._update()
        if hull.enough_points:
            to_sample = np.nanargmax(hull.b)
            sample = hull.sample[hull.simplices[to_sample]]
            return hull.A[to_sample], hull.b[to_sample], sample
        else:
            return DirectHull(hull.sample, hull.fallback_plan, hull.space).get_exploration_vector()
        
        
    # shortcut for Ghull
    # valid only if space==G
    def get_r(hull):
        if hull.space=='G':
            if hull.enough_points:
                hull._update()
                b = hull.convex_hull.equations[:,-1]
                return -np.nanmax(b)
            else:
                return 0
        else:
            return 0
    
    def get_R(self):
        assert self.space == 'G'
        sum_squared = np.sum(np.square(self.sample.G), axis=1)
        #index = np.argmax(sum_squared)
        return np.sqrt(np.nanmax(sum_squared))
    
    def shot(hull, ns, use_MC=False):
        try:
            # take global function for shot()
            return shot(hull, ns, use_MC)
        except:
            pass
            
    def fire(hull, ns, use_MC=False):
        try:
            # take global function for fire()
            return fire(hull, ns, use_MC)
        except:
            pass
    
    def get_orth_outside(hull):
        try:
            return get_orth_outside(hull)
        except:
            #č asi máme problém s triangulací 
            #č odvažně vratíme jedničku
            #č neřikejte mi, že musím pěčlivějc zpracovavat chyby!
            return 1
    
    def get_2FORM_outside(hull):
        try:
            return get_2FORM_outside(hull)
        except:
            #č asi máme problém s triangulací 
            #č odvažně vratíme jedničku
            #č neřikejte mi, že musím pěčlivějc zpracovavat chyby!
            return 1
    
    def get_norm_outside(hull):
        hull._update()
        if hull.space != 'G':
            raise
        
        vertices_model = hull.points[hull.simplices].transpose((1, 0, 2))
        result = hull.tn_scheme.integrate(hull._outside_callback, vertices_model)
        
        return np.sum(result) * hull.chi_like_const
        
        
    def get_chi_outside(hull):
        hull._update()
        if hull.space != 'G':
            raise
        
        
        vertices_model = hull.points[hull.simplices].transpose((1, 0, 2))
        result = hull.tn_scheme.integrate(hull._chi_outside_callback, vertices_model)
        mask = result > 0 #č takto zapsana podmínka pokryvá i Nan
        if not np.all(mask):
            number = len(mask) - np.count_nonzero(mask)
            print("QHull: Negative values in %s facets have appeared during integration" % number)
            return np.sum(result, where=mask) / hull.nsphere_surface_area
        return np.sum(result) / hull.nsphere_surface_area
        
#    # quadpy
#    def _norm_inside_callback(hull, x):
#        # x.shape == (simplex_dim + 1, nsimplex, scheme_npoints) #(3, 26, 56)
#        
#        cdfs = stats.norm.cdf(x)
#        pdfs = stats.norm.pdf(x)
#        
#        for i in range(hull.sample.nvar):
#            cdfs[i] *= np.prod(pdfs[:i], axis=0)
#            cdfs[i] *= np.prod(pdfs[i+1:], axis=0)
#            cdfs[i] *= np.atleast_2d(hull.A[:, i]).T 
#        
#        
#        # n_values x nsimplex x scheme_points
#        return cdfs

        
    
    
    def _outside_callback(hull, x):
        # x.shape == (simplex_dim + 1, nsimplex, scheme_npoints) #(3, 26, 56)
        
        #č přijde velké, obrovské numpy pole
        #č a já bych chtěl, aby se tu zbytečně nealokovalo
        
        result = np.einsum('ijk,ijk->jk', x, x) # r**2
        np.sqrt(result, out=result) # r
        
        #result = r / np.sqrt(2) # r / sqrt(2)
        np.divide(result, np.sqrt(2), out=result)
        #special.gammaincc(hull.sample.nvar - 1/2, result, out=result) # F
        special.erfc(result, out=result) 
        
#        #č normalizujeme normály. Jenže normály samotné dodáme později
#        result /= r 
#        
#        # A = nsimplex x nvar
#        # x = nvar x nsimplex x scheme_npoints
#        # normals = nsimplex x scheme_npoints
#        #normals = np.einsum('ij,jik->ik', hull.A, x)
#        np.einsum('ij,jik->ik', hull.A, x, out=r) # normals
#        result *= r 
        
        # n_values x nsimplex x scheme_points
        return result 

    def _outside_normals_callback(hull, x):
        # x.shape == (simplex_dim + 1, nsimplex, scheme_npoints) #(3, 26, 56)
        
        #č přijde velké, obrovské numpy pole
        #č a já bych chtěl, aby se tu zbytečně nealokovalo
        
        r = np.einsum('ijk,ijk->jk', x, x) # r**2
        np.sqrt(r, out=r) # r
        
        result = r / np.sqrt(2) # r / sqrt(2)
        #np.divide(result, np.sqrt(2), out=result)
        #special.gammaincc(hull.sample.nvar - 1/2, result, out=result) # F
        special.erfc(result, out=result) 
        
        #č normalizujeme normály. Jenže normály samotné dodáme později
        result /= r 
        
        # A = nsimplex x nvar
        # x = nvar x nsimplex x scheme_npoints
        # normals = nsimplex x scheme_npoints
        #normals = np.einsum('ij,jik->ik', hull.A, x)
        np.einsum('ij,jik->ik', hull.A, x, out=r) # normals
        result *= r 
        
        # n_values x nsimplex x scheme_points
        return result 


    def _chi_outside_callback(hull, x):
        # x.shape == (simplex_dim + 1, nsimplex, scheme_npoints) #(3, 26, 56)
        
        nvar = hull.sample.nvar
        
        #č přijde velké, obrovské numpy pole
        #č a já bych chtěl, aby se tu zbytečně nealokovalo
        
        result = np.einsum('ijk,ijk->jk', x, x) # r**2
        r_nvar = np.power(result, nvar/2) # r**(nvar-1) (chi) * r (to normalize)
        
        np.divide(result, 2, out=result) # r**2 / 2
        special.gammaincc(nvar / 2, result, out=result) # F
        
        #č normalizujeme normály. Jenže normály samotné dodáme později
        result /= r_nvar 
        
        # A = nsimplex x nvar
        # x = nvar x nsimplex x scheme_npoints
        # normals = nsimplex x scheme_npoints
        #normals = np.einsum('ij,jik->ik', hull.A, x)
        np.einsum('ij,jik->ik', hull.A, x, out=r_nvar) # normals
        result *= r_nvar
        
        # n_values x nsimplex x scheme_points
        return result 

    def get_convex_hull_estimation(hull):
        hull._update()
        
        r = hull.get_r()
        R = hull.get_R()
        if r<0:
            hull.shell.set_bounds(0, R)
        else:
            hull.shell.set_bounds(r, R)
        
        outer = hull.shell.pf
        shell = hull.shell.p_shell
        
        if hull.enough_points:
            chi_outside = hull.get_chi_outside()
        else:
            chi_outside = 0
        
        orth_outside = hull.get_orth_outside()
        
        r_outside = outer + shell
        outside = min(r_outside, chi_outside)
        outside = max(outside, orth_outside, outer)
        
        return QHullEstimation(
                              hull.npoints,
                              hull.sample.nvar,
                              hull.nsimplex,
                              r, R,
                              hull.shell.ps,
                              shell,
                              outer,
                              chi_outside,
                              orth_outside,
                              #'tn_scheme',
                              #'tn_scheme_points',
                              1 - outside,
                              outside
                              )
                        

class QHullCubature(QHull):
    
    def get_chi_outside(hull):
        hull._update()
        
        if hull.space != 'G':
            raise
        
        
        integrals = 0
        # if first time runned
        if 'facets' not in dir(hull):
            hull.facets = facets = dict()
            ncubature = len(hull.tn_scheme.weights)
            hull._x = np.empty((hull.sample.nvar, ncubature))
            hull._r = np.empty(ncubature)
            hull._result = np.empty(ncubature)
            for indices, normal in zip(hull.simplices, hull.A):
                facet_integral = hull.get_facet_outside(indices, normal)
                facets[indices.tobytes()] = facet_integral
                integrals += facet_integral
            
            return integrals / hull.nsphere_surface_area
        
        facets = hull.facets
        new_facet_dict = dict()
        for indices, normal in zip(hull.simplices, hull.A):
            key = indices.tobytes()
            if key in facets:
                facet_integral = facets[key]
            else:
                facet_integral = hull.get_facet_outside(indices, normal)
            new_facet_dict[key] = facet_integral
            integrals += facet_integral
            
        hull.facets = new_facet_dict
        return integrals / hull.nsphere_surface_area
            

            

    def get_facet_outside(hull, indices, normal):
        vertices_model = hull.points[indices]
        
        vol = quadpy.tn.get_vol(vertices_model)
        if not np.isfinite(vol):
            print("QHull: Incorrect area has occured in facet %s" % indices)
            return 0
        
        nvar = len(normal)
        x = hull._x
        r_nvar = hull._r
        result = hull._result
        
        # nvar x n_integration_nodes
        # Transform the points `xi` from the reference simplex onto `simplex`.
        # same as quadpy.tn.transform(hull.tn_scheme.points, vertices_model.T)
        #np.dot(simplex, points)
        np.matmul(vertices_model.T, hull.tn_scheme.points, out=x)
        
        np.einsum('ij,ij->j', x, x, out=result) # r**2
        np.power(result, nvar/2, out=r_nvar) # r**(nvar-1) (chi) * r (to normalize)
        
        np.divide(result, 2, out=result) # r**2 / 2
        special.gammaincc(nvar / 2, result, out=result) # F
        
        #č normalizujeme normály. Jenže normály samotné dodáme později
        result /= r_nvar 
        
        #č normála
        np.dot(normal, x, out=r_nvar)
        result *= r_nvar
        
        # facet_outside = integral / unit_ball_surface_area
        integral = vol * np.inner(result, hull.tn_scheme.weights)
        if integral > 0:
            return integral
        else:
            print("QHull: Negative value has appeared in facet %s during integration" % indices)
            return 0



# Gaussian brick
#č Gaussovská cihla
#
# it was a mistake to design previous classes without explicit update()
class Grick:
    # take some global functions
    fire = fire
    shot = shot
    
    
    def get_FORM_outside(self):
        return stats.norm.sf(self.get_r())
    
    
    def __init__(hull, sample, direct_plan, nrandom=50, auto_update=True):
        hull.sample = sample
        hull.direct_plan = direct_plan
        hull.space = 'G'
        hull.ndim = sample.nvar
        hull.nrandom = nrandom #č počet náhodných normalových věktorů
        
        hull.auto_update = auto_update
        
        hull.regen()
        
        
    def regen(hull):
        hull._npoints = 0
        hull.mins = np.full(hull.ndim, np.inf)
        hull.maxs = np.full(hull.ndim, -np.inf)
        
        hull.bp_dp = np.full(len(hull.direct_plan), -np.inf)
        hull.bm_dp = np.full(len(hull.direct_plan), np.inf)
        
        hull.bp = np.full(hull.ndim, -np.inf)
        hull.bm = np.full(hull.ndim, np.inf)
        
        hull.orth_basis = np.eye(hull.ndim) 
        
        hull.update()
    
    
    def _update(hull):
        if hull.auto_update:
            hull.update()
    
    # it was a mistake to design previous classes without explicit update()
    def update(hull):
        if hull._npoints < hull.npoints:
            hull._points = hull.sample.G
            
            new_points = hull._points[hull._npoints:]
            
            new_mins = np.nanmin(new_points, axis=0)
            new_maxs = np.nanmax(new_points, axis=0)
            
            np.nanmin((new_mins, hull.mins), axis=0, out=hull.mins)
            np.nanmax((new_maxs, hull.maxs), axis=0, out=hull.maxs)
            
            new_bp, new_bm = get_bp_bm(hull.direct_plan, new_points)
            np.nanmax((new_bp, hull.bp_dp), axis=0, out=hull.bp_dp)
            np.nanmin((new_bm, hull.bm_dp), axis=0, out=hull.bm_dp)
            
            
            new_bp, new_bm = get_bp_bm(hull.orth_basis, new_points)
            np.nanmax((new_bp, hull.bp), axis=0, out=hull.bp)
            np.nanmin((new_bm, hull.bm), axis=0, out=hull.bm)
            
            hull._gen_orth_basis()
                
            hull._npoints = hull.npoints


    def gen_random_Ab(hull):
        ns = hull.ndim * 2 + len(hull.direct_plan) + hull.nrandom
        #č necháme vygenerovat maticu náhodných čisel
        #č ale použijeme jen část z ní
        #č moje zkušenost je, že np.ones a np.random.randn běží stejně rychle
        A = np.random.randn(ns, hull.ndim) #random directions
        A[:hull.ndim] = np.eye(hull.ndim)
        A[hull.ndim:hull.ndim*2] = hull.orth_basis
        A[hull.ndim*2:ns-hull.nrandom] = hull.direct_plan
        
        # rand_dir: prepare ns random directions on a unit d-sphere
        rand_dir = A[ns-hull.nrandom:]
        
        lengths = np.sum(np.square(rand_dir), axis=1)
        lengths = np.sqrt(lengths, out=lengths) #lengths of each radius-vector
        
        # scale all radii-vectors to unit length
        # use [:,None] to get an transposed 2D array
        np.divide(rand_dir, lengths[:,None], out=rand_dir) 
        
        b = np.empty(ns) 
        #č Nám jde o basis. Dáme ty nejlepší b-čka.
        #č znaménka vektorů, tj. směry dopředu nebo dozadu v této fázi nevadí
        np.nanmax((-hull.maxs, hull.mins), axis=0, out=b[:hull.ndim])
        np.nanmax((-hull.bp, hull.bm), axis=0, out=b[hull.ndim:hull.ndim*2])
        np.nanmax((-hull.bp_dp, hull.bm_dp), axis=0, out=b[hull.ndim*2:ns-hull.nrandom])
        
        rbp, rbm = get_bp_bm(rand_dir, hull._points)
        np.nanmax((-rbp, rbm), axis=0, out=b[ns-hull.nrandom:])
        
        return A, b


    def _gen_orth_basis(hull):
        A, b = hull.gen_random_Ab()
        
        #č je to špatné z hlediska testování,
        #č ale nevím jak z toho.
        #č pro 2D musím udělat vyjimku z "předposlední"
        if hull.ndim > 2:
            hull.orth_basis = _get_nD_orth_basis_from_normals(A, b)
        else:
            to_fire = np.nanargmax(b)
            a = A[to_fire]
            x, y = a
            hull.orth_basis = np.array([[x, y],[-y, x]])
            
        
        #č musí tam bejt G coordinates
        hull.bp, hull.bm = get_bp_bm(hull.orth_basis, hull._points)
        
        
        
        
    
    
        
        
    def get_orth_outside(hull):
        hull._update()
        return calculate_brick_complement_probability(hull.bm, hull.bp)


    def get_orth_equations(hull):
        hull._update()
        return hull.equations


    def get_2FORM_outside(hull):
        hull._update()
        return stats.norm.cdf(hull.bm[0]) + stats.norm.sf(hull.bp[0])
                
    def get_2FORM_equations(hull):
        hull._update()
        A = np.vstack((-hull.orth_basis[0], hull.orth_basis[0]))
        b = np.array([[hull.bm[0]],[-hull.bp[0]]])
        return np.hstack((A,b))  


    @property
    def points(hull):
        if hull.auto_update:
            return getattr(hull.sample, hull.space)
        else:
            return hull._points
    
        
    @property
    def npoints(hull):
        if hull.auto_update:
            return len(hull.sample)
        else:
            return hull._npoints
        
    
    
    @property #č stejně nikdo to nebude spouštět
    def nsimplex(hull):
        return hull.sample.nvar * 2
        
        
    @property
    def A(hull):
        hull._update()
        #č žádná optimizace, ale stejně nikdo to nebude spouštět
        return np.vstack((-hull.orth_basis, hull.orth_basis))
        
    @property
    def b(hull):
        hull._update()
        return np.concatenate((hull.bm, -hull.bp))
        
    @property
    def equations(hull):
        hull._update()
        #č žádná optimizace, ale stejně nikdo to nebude spouštět
        A = np.vstack((-hull.orth_basis, hull.orth_basis))
        b = np.concatenate((hull.bm, -hull.bp))
        return np.hstack((A,b[:,None]))

    def is_inside(hull, nodes):
        hull._update()
        x = nodes.G
        
        #E [normal, offset] forming the hyperplane equation of the facet (see Qhull documentation for more)
        bp = np.atleast_2d(hull.bp).T
        bm = np.atleast_2d(hull.bm).T
        
        # N=ns, E - number of hyperplane equations
        ExN = hull.orth_basis @ x.T
        higher = np.all(ExN < bp, axis=0)
        lower = np.all(ExN > bm, axis=0)
        return np.all((higher, lower), axis=0)
    
    def is_outside(hull, nodes): 
        return ~hull.is_inside(nodes)
        
    def get_design_points(hull):
        hull._update()
        sample_model = -hull.A * hull.b.reshape(-1,1)
        return hull.sample.f_model.new_sample(sample_model, space=hull.space)
        
    def get_exploration_vector(hull):
        hull._update()
        if hull.bm[0] > (-hull.bp[0]):
            return -hull.orth_basis[0], hull.bm[0], hull.sample
        else:
            return hull.orth_basis[0], -hull.bp[0], hull.sample
        
        
        
    def get_r(hull):
        hull._update()
        "calculates minimal signed distance to planes. Can therefore be negative"
        #č ukazalo se, že náhodou další orthogonály můžou trefit menší poloměr
        #return min(-hull.bm[0], hull.bp[0])
        return np.min((-hull.bm, hull.bp))
            
            
            
            
            
            

        


