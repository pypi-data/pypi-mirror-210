#!/usr/bin/env python
# coding: utf-8

import numpy as np
from scipy.spatial import Delaunay, KDTree
from scipy.optimize import linprog



#
# Qhull
#

class Qframe(Delaunay):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.coplanar.size:
            print("Qframe: coplanar points ", self.coplanar)
            
            
    def is_couple(self, couple_indices):
        i, j = couple_indices
        ii = self.simplices
        return np.any(np.sum((ii == i) | (ii == j), axis=1) == 2)
    
    def generate_wireframe(self, callback=lambda:True):
        n = self.npoints
        size = n * (n - 1) // 2
        self.condensed_contacts = np.zeros(size, dtype=bool)
        
        for simplex in self.simplices:
            self._handle_simplex(simplex)
            if callback():
                break
        
        
    def _handle_simplex(self, simplex):
        if len(simplex) > 3:
            i = simplex[0]
            jj = simplex[1:]
            self._handle_simplex(jj)
            for j in jj:
                self._set_contact(i, j)
        else:
            i, j, k = simplex
            self._set_contact(i, j)
            self._set_contact(j, k)
            self._set_contact(k, i)
            
            
        
    def _set_contact(self, x, y):
        i, j = min(x, y), max(x, y)
        m = self.npoints
        entry = m * i + j - ((i + 2) * (i + 1)) // 2
        self.condensed_contacts[entry] = True




def convex_solver_test(points, tries_to_fix=1, tol=1e-7):
    tri = Delaunay(points)
    CS = ConvexSpline(points)
    
    false_positives = []
    false_negatives = []
    
    ii = tri.simplices
    for i in range(len(points)): 
        for j in range(i):
            tri_status = np.any(np.sum((ii == i) | (ii == j), axis=1) == 2)
            CS_status = CS.is_couple((i,j), tries_to_fix=tries_to_fix, tol=tol)
            if tri_status == CS_status:
                print(i, j, tri_status)
            elif tri_status and not CS_status:
                print(i, j, "False negative! QHull says %s, but CS thinks %s" % (tri_status, CS_status))
                false_negatives.append((i,j))
            else:
                print(i, j, "False positive! QHull says %s, but CS thinks %s" % (tri_status, CS_status))
                false_positives.append((i,j))
    
    if false_positives or false_negatives:
        print("False positives: ", false_positives)
        print("False negatives: ", false_negatives)
    else:
        print("Test succesfully passed")
            




#
# DirectContact
#

#č zda existuje přímy kontakt, prostě na usečce
class DirectContact(KDTree):
    """
    č Obecně, skoro pro každou dimenzi v rozmězí od 2D do 100D
    č nejlevnější bylo 
    č 1. strom s pár bodíků
    č 2. ConvexSolver
    č 3. strom s nsim bodíků
    """
    def is_couple(self, couple_indices, **kwargs):
        i, j = couple_indices
        
        half_point = np.mean(self.data[[i, j]], axis=0)
        
        __dd, ii = self.query(half_point, k=2, **kwargs)
        #č pro jediný bod jednoducha kontrola je rychlejší 
        #č jak volání numpy množinových funkcí
        return (i in ii) and (j in ii)



#
# Gabriel
#

#č zda existuje přímy kontakt, prostě na usečce
class Gabriel:
    def __init__(self, points):
        self.points = points
        nsim, ndim = points.shape
        
        self.b = np.sum(np.square(points), axis=1)
        self._mask = np.empty(nsim, dtype=bool)
        
        
    def is_couple(self, couple_indices):
        i, j = couple_indices
        
        mask = self._mask
        if len(mask) < 3:
            return True
        mask[:] = True
        mask[[i, j]] = False
        
        X = self.points
        b = self.b
        
        test = b[mask] - X[mask] @ X[i] - X[mask] @ X[j] + np.inner(X[i], X[j])
        
        return np.all(test >= 0)
        

#
# ConvexSolver
#


def get_offsets(a, X):
    #č nejak tuším, že v poslední dimenzi 
    #č znaménko normál musí být jednotné
    # a = a * -np.sign(a[-1])
    a = a * (1 - 2 * (a[-1] > 0)) 
    b = X @ a
    return b


#č podoba tamtamtoho tehdejšího prvního pokusu.
#č Jen pro srandu. Pro historickej záznam
def convex_solver(points, line_indices, tries_to_fix=1, tol=1e-7):
    i, j = line_indices
    
    X = points
    __nsim, ndim = X.shape
    
    basis = np.random.random((ndim, ndim))
    
    #č QR rozklad jede po sloupcich
    basis[:, 0] = X[j] - X[i]
    
    for dim in range(1, ndim-1):
        #č co jsem viděl, numpy matici Q normalizuje
        #č a první sloupec zůstavá (skoro) tím samým, co byl před tím
        basis[:, :dim+1], __ = np.linalg.qr(basis[:, :dim+1])
        
        # get constrain
        a = basis[:, dim]
        b = get_offsets(a, X)
        if np.max(b) - np.max(b[[i, j]]) < tol:
            return True
        else:
            idx = np.argmax(b)
            basis[:, dim] = basis[:, 1]
            basis[:, 1] = X[idx] - X[i]
            
            
    
    for __ in range(ndim + tries_to_fix):
        basis, __ = np.linalg.qr(basis)
        
        # get constrain
        a = basis[:, -1]
        b = get_offsets(a, X)
        if np.max(b) - np.max(b[[i, j]]) < tol:
            return True
        else:
            idx = np.argmax(b)
            basis[:, 2:] = basis[:, 1:-1]
            basis[:, 1] = X[idx] - X[i]
    
    basis, __ = np.linalg.qr(basis)
    a = basis[:, -1]
    b = get_offsets(a, X)
    return np.max(b) - np.max(b[[i, j]]) < tol


        
        
#č Hlavní pointa ConvexSpline třídy:
#č Využit navíc geometrických informací, které už předem známé:
#č 1. Známe souřadnice vzorků. 
#č 2. Víme, že přímka mezí těmi dvěma vzorky leží v hyperrovině
#č 3. Vždyť to my zvedáme na povrch convexního paraboloidu!
#č    Můžeme tedy v každém její bodě najit tečnou hyperrovinu.    
def convex_spline(points, couple_indices, tries_to_fix=1, tol=1e-7):
    i, j = couple_indices

    X = points
    __nsim, ndim = X.shape
    
    
    
    
    basis = np.random.random((ndim, ndim))
    #č první vektor musí být zadán přímkou mezí vzorky
    #č jinak se posype náš předpoklad, že leží v hyperrovině
    #č a žádné výsledky "za", "před" hyperrovinou nebudou nic znamenat
    basis[:, 0] = X[j] - X[i] #č QR rozklad jede po sloupcich
    
    #č jako indice zkusme použit bod na usečce uprostřed mezí vzorky
    half_point = np.mean(X[[i, j]], axis=0) 
    
    #č všechy souřadnice jsou dány radius-vektorem od středu,
    #č ale poslední souřadnice je to naše zvednutí, 
    #č kde bychom mohli zkusit dát korrektnější směr.
    #č Mně humpolackými uvahami o tečně paraboly 
    #č na caru paríru vyšlo něco jako
    #č že stačí dát poslední složku 0,5.
    #č Jakože čím je roloměr je větší, 
    #č tím je "svislá" složka automaticky měnší.
    #č Jakože netřeba ani normalizovat, ani nic "složitě" počítat
    half_point[-1] = -0.5
    
    #č ten náš radius-vektor není ortogonální 
    #č k přímce, na které leží ty naši dva vzorky
    #č QR rozklad je ortogonalizuje 
    #č a vygeneruje další ortogonalní vektory
    basis[:, 1] = half_point
    basis, __ = np.linalg.qr(basis)
    
    
    #č vytahneme náš ortogonalizovaný odhad 
    #č normálního vektoru
    a = basis[:, 1]
    b = get_offsets(a, X)
    
    if np.max(b) - np.max(b[[i, j]]) < tol:
        #č bylo to myšleno jako jakési zoufalství
        #č ale funguje překvapivě dobře
        return True 
    else:
        idx = np.argmax(b)
        #č nahradíme v jedničce naš odhad normálního vektoru
        #č nalezenou překažkou.
        #č Zbytek bazí jíž byl ortogonální 
        #č k té naši pomyšlené normále
        basis[:, 1] = X[idx] - X[i]
    
    #č Ve zbytku pokračujeme jako vždycky.
    #č Pořad ndim pokusu u False párečku
    for __ in range(ndim + tries_to_fix):
        basis, __ = np.linalg.qr(basis)
        
        # get constrain
        a = basis[:, -1]
        b = get_offsets(a, X)
        if np.max(b) - np.max(b[[i, j]]) < tol:
            return True
        else:
            idx = np.argmax(b)
            basis[:, 2:] = basis[:, 1:-1]
            basis[:, 1] = X[idx] - X[i]
    
    basis, __ = np.linalg.qr(basis)
    a = basis[:, -1]
    b = get_offsets(a, X)
    return np.max(b) - np.max(b[[i, j]]) < tol







        
#č na rozdil od předchozího spline, 
#č sort nesestavuje hned ortogonální k normále bazi, dělá to postupně
#č klíčovým stalo to, že v každem kroku obnovujeme původní odhad normály
def convex_sort(points, couple_indices, tries_to_fix=1, tol=1e-7):
    i, j = couple_indices

    X = points
    __nsim, ndim = X.shape
    
    
    
    
    basis = np.empty((ndim, ndim))
    #č první vektor musí být zadán přímkou mezí vzorky
    #č jinak se posype náš předpoklad, že leží v hyperrovině
    #č a žádné výsledky "za", "před" hyperrovinou nebudou nic znamenat
    basis[:, 0] = X[j] - X[i] #č QR rozklad jede po sloupcich
    
    #č jako indice zkusme použit bod na usečce uprostřed mezí vzorky
    half_point = np.mean(points[[i, j]], axis=0) 
    
    
    #č všechy souřadnice jsou dány radius-vektorem od středu,
    #č ale poslední souřadnice je to naše zvednutí, 
    #č kde bychom mohli zkusit dát korrektnější směr.
    #č Mně humpolackými uvahami o tečně paraboly 
    #č na caru paríru vyšlo něco jako
    #č že stačí dát poslední složku 0,5.
    #č Jakože čím je roloměr větší, 
    #č tím je "svislá" složka automaticky měnší.
    #č Jakože netřeba ani normalizovat, ani nic "složitě" počítat
    half_point[-1] = -0.5
    basis[:, 1] = half_point
    
    #č ten náš radius-vektor není ortogonální 
    #č k přímce, na které leží ty naši dva vzorky
    #č musíme ho (QR rozkladem) ortogonalizovat
    for dim in range(1, ndim-1):
        #č co jsem viděl, numpy matici Q normalizuje
        #č a první sloupec zůstavá (skoro) tím samým, co byl před tím
        basis[:, :dim+1], __ = np.linalg.qr(basis[:, :dim+1])
        
        # get constrain
        a = basis[:, dim]
        b = get_offsets(a, X)
        if (np.max(b) - np.max(b[[i, j]])) < tol:
            return True
        
        #else:
        idx = np.argmax(b)
        basis[:, 2:dim+1] = basis[:, 1:dim]
        basis[:, 1] = X[idx] - X[i]
        basis[:, dim+1] = half_point
    
    
    
    for __ in range(tries_to_fix):
        basis, __ = np.linalg.qr(basis)
        # get constrain
        a = basis[:, -1]
        b = get_offsets(a, X)
        if (np.max(b) - np.max(b[[i, j]])) < tol:
            return True
        idx = np.argmax(b)
        basis[:, 2:] = basis[:, 1:-1]
        basis[:, 1] = X[idx] - X[i]
    
    
    basis, __ = np.linalg.qr(basis)
    a = basis[:, -1]
    b = get_offsets(a, X)
    return (np.max(b) - np.max(b[[i, j]])) < tol






def convex_sprite(X, couple_indices, tries_to_fix=1, tol=1e-7):
    i, j = couple_indices
    __nsim, ndim = X.shape
    
    # sprite does not mean anything. Just a word
    #č místo vyslovéné bazi budeme vektory ukladat do 
    #č jakési obecné matici
    sprite = np.empty((ndim + tries_to_fix, ndim))
    #č první vektor musí být zadán přímkou mezí vzorky
    #č jinak se posype náš předpoklad, že leží v hyperrovině
    #č a žádné výsledky "za", "před" hyperrovinou nebudou nic znamenat
    baseline = X[j] - X[i]
    sprite[-2] = baseline
    
    #č jako indice zkusme použit bod na usečce uprostřed mezí vzorky
    half_point = np.mean(X[[i, j]], axis=0) 
    
    
    #č všechy souřadnice jsou dány radius-vektorem od středu,
    #č ale poslední souřadnice je to naše zvednutí, 
    #č kde bychom mohli zkusit dát korrektnější směr.
    #č Mně humpolackými uvahami o tečně paraboly 
    #č na caru paríru vyšlo něco jako
    #č že stačí dát poslední složku 0,5.
    #č Jakože čím je roloměr větší, 
    #č tím je "svislá" složka automaticky měnší.
    #č Jakože netřeba ani normalizovat, ani nic "složitě" počítat
    half_point[-1] = -0.5
    sprite[-1] = half_point
    
    #č ten náš radius-vektor není ortogonální 
    #č k přímce, na které leží ty naši dva vzorky
    #č musíme ho (QR rozkladem) ortogonalizovat
    for dim in range(1, ndim-1):
        basis, __ = np.linalg.qr(sprite[-dim-1:].T) 
        
        # get constrain
        a = basis[:, -1]
        b = get_offsets(a, X)
        if (np.max(b) - np.max(b[[i, j]])) < tol:
            return True
        
        #else:
        idx = np.argmax(b)
        sprite[-dim-1] = X[idx] - X[i]
        sprite[-dim-2] = baseline
    
    
    #č tady máme
    #č sprite[-ndim+1] = nějaký vektor
    #č sprite[-ndim] = baseline
    
    for t in range(tries_to_fix):
        basis, __ = np.linalg.qr(sprite[-ndim-t:].T)
        # get constrain
        a = basis[:, -1]
        b = get_offsets(a, X)
        if (np.max(b) - np.max(b[[i, j]])) < tol:
            return True
        idx = np.argmax(b)
        sprite[-ndim-t] = X[idx] - X[i]
        sprite[-ndim-1-t] = baseline
    
    assert (sprite[0] == baseline).all()
    
    basis, __ = np.linalg.qr(sprite.T)
    a = basis[:, -1]
    b = get_offsets(a, X)
    return (np.max(b) - np.max(b[[i, j]])) < tol



def get_longest(O, A, B):
    a_i = O - A
    a_j = O - B
    if np.inner(a_i[:-1], a_i[:-1]) > np.inner(a_j[:-1], a_j[:-1]):
        return a_i
    else:
        return a_j


def convex_slice(X, couple_indices, tries_to_fix=1, tol=1e-7):
    i, j = couple_indices
    nsim, ndim = X.shape
    
    mask = np.full(nsim, True)
    mask[[i, j]] = False
    
    #č jako indice zkusme použit bod na usečce uprostřed mezí vzorky
    #
    #č všechy souřadnice jsou dány radius-vektorem od středu,
    #č ale poslední souřadnice je to naše zvednutí, 
    #č kde bychom mohli zkusit dát korrektnější směr.
    #č Mně humpolackými uvahami o tečně paraboly 
    #č na caru paríru vyšlo něco jako
    #č že stačí dát poslední složku 0,5.
    #č Jakože čím je roloměr větší, 
    #č tím je "svislá" složka automaticky měnší.
    #č Jakože netřeba ani normalizovat, ani nic "složitě" počítat
    half_point = np.mean(X[[i, j]], axis=0) 
    half_point[-1] = -0.5
    
    b = get_offsets(half_point, X)
    if (np.max(b[mask]) - np.min(b[[i, j]])) < tol:
        return True
    
    #č nepovedlo. Tak deme na věc
    idxs = []
    
    # sprite does not mean anything. Just a word
    #č místo vyslovéné bazi budeme vektory ukladat do 
    #č jakési obecné matici
    sprite = np.empty((ndim + tries_to_fix, ndim))
    baseline = X[j] - X[i]
    sprite[-2] = baseline
    sprite[-1] = half_point
    
    
    
    for dim in range(1, ndim-1):
        basis, __ = np.linalg.qr(sprite[-dim-1:].T) 
        
        # get constrain
        a = basis[:, -1]
        b = get_offsets(a, X)
        #č u kontrol musím taky hlídat, aby argmax nebyl i, nebo j
        if (np.max(b[mask]) - np.max(b[[i, j]])) < tol:
            print(idxs)
            return True
        
        #else:
        idx = np.argmax(b)
        idxs.append(idx)
        sprite[-dim-1] = get_longest(X[idx], X[i], X[j])
        sprite[-dim-2] = baseline
    
    
    #č tady máme
    #č sprite[-ndim+1] = nějaký vektor
    #č sprite[-ndim] = baseline
    
    for t in range(tries_to_fix):
        basis, __ = np.linalg.qr(sprite[-ndim-t:].T)
        # get constrain
        a = basis[:, -1]
        b = get_offsets(a, X)
        #č u kontrol musím taky hlídat, aby argmax nebyl i, nebo j
        if (np.max(b[mask]) - np.max(b[[i, j]])) < tol:
            print(idxs)
            return True
        idx = np.argmax(b)
        idxs.append(idx)
        sprite[-ndim-t] = get_longest(X[idx], X[i], X[j])
        sprite[-ndim-1-t] = baseline
    
    assert (sprite[0] == baseline).all()
    
    basis, __ = np.linalg.qr(sprite.T)
    a = basis[:, -1]
    b = get_offsets(a, X)
    print(idxs)
    return (np.max(b[mask]) - np.min(b[[i, j]])) < tol






class ConvexSolver:
    """
    č Hlavní pointa třídy:
    č pokud dva body zvednuté na povrch convexního paraboloidu
    č v prostoru ndim+1 (feature space, quadratic kernel)
    č lze lineárně separovat (hyperrovinou) od ostatních bodů,
    č znamená to, že v původním prostoru 
    č jejich Voroného buňky budou mít společnou stěnu (kontakt),
    č neboli, což je totež, u Delone triangulace by měly společné simplexy
    
    č nebudeme puntičkařit a pro jednoduchost předepíšeme,
    č nechť dva body zájmu leží přímo v hyperrovině
    č (bude to hlasít existence rozhraní i v degenerovaných případech
    č jako např. tří teček na jedné přímce. Mně to ale nevadí)
    """
    def __init__(self, points, convex_solver=convex_sprite):
        nsim, ndim = points.shape
        
        self.lifted_points = np.empty((nsim, ndim + 1))
        self.lifted_points[:, :ndim] = points
        # kind of datascience. feature space, quadratic kernel...
        self.lifted_points[:, -1] = np.sum(np.square(points), axis=1)
        
        self.convex_solver = convex_solver
        
    def is_couple(self, couple_indices, *args, **kwargs):
        return self.convex_solver(self.lifted_points, couple_indices, *args, **kwargs)











class LocalizedHull:
    """
    č Hlavní pointa třídy:
    č pokud dva body zvednuté na povrch convexního paraboloidu
    č v prostoru ndim+1 (feature space, quadratic kernel)
    č lze lineárně separovat (hyperrovinou) od ostatních bodů,
    č znamená to, že v původním prostoru 
    č jejich Voroného buňky budou mít společnou stěnu (kontakt),
    č neboli, což je totež, u Delone triangulace by měly společné simplexy
    
    č nebudeme puntičkařit a pro jednoduchost předepíšeme,
    č nechť dva body zájmu leží přímo v hyperrovině
    č (bude to hlasít existence rozhraní i v degenerovaných případech
    č jako např. tří teček na jedné přímce. Mně to ale nevadí)
    """
    def __init__(self, points):
        nsim, ndim = points.shape
        
        self.points = points
        
        self._basis = np.empty((ndim + 1, ndim + 1), dtype=float)
        self._mask = np.empty(nsim, dtype=bool)
        
        self.lifted_points = np.empty((nsim, ndim + 1))
        self.lifted_points[:, :ndim] = points
        # kind of datascience. feature space, quadratic kernel...
        self.lifted_points[:, -1] = np.sum(np.square(points), axis=1)

    def get_tri_basis(self, tri, idxs):
        for simplex in tri.simplices:
            if (0 in simplex) and (1 in simplex):
                indices = np.array(idxs)[simplex]
                basis = self.lifted_points[indices]
                basis = basis - basis[-1]
                basis, __ = np.linalg.qr(basis.T)
                return True, basis
        return False, None
                
            
        
    def is_couple(self, couple_indices, tol=1e-7):
        i, j = couple_indices
        X = self.lifted_points
        nsim, ndim = X.shape
        
        if nsim < 3:
            return True
        
        mask = self._mask
        mask[:] = True
        mask[[i, j]] = False
        
        #č jako indice zkusme použit bod na usečce uprostřed mezí vzorky
        #
        #č všechy souřadnice jsou dány radius-vektorem od středu,
        #č ale poslední souřadnice je to naše zvednutí, 
        #č kde bychom mohli zkusit dát korrektnější směr.
        #č Mně humpolackými uvahami o tečně paraboly 
        #č na caru paríru vyšlo něco jako
        #č že stačí dát poslední složku 0,5.
        #č Jakože čím je roloměr větší, 
        #č tím je "svislá" složka automaticky měnší.
        #č Jakože netřeba ani normalizovat, ani nic "složitě" počítat
        half_point = np.mean(X[[i, j]], axis=0) 
        half_point[-1] = -0.5
        
        b = get_offsets(half_point, X)
        if (np.max(b[mask]) - np.min(b[[i, j]])) < tol:
            return True
        
        #č nepovedlo. Tak deme na věc
        idxs = [i, j]
        basis = self._basis
        #č první vektor musí být zadán přímkou mezí vzorky
        #č jinak se posype náš předpoklad, že leží v hyperrovině
        #č a žádné výsledky "za", "před" hyperrovinou nebudou nic znamenat
        basis[:, 0] = X[j] - X[i] #č QR rozklad jede po sloupcich
        basis[:, 1] = half_point
        
        #č ten náš radius-vektor není ortogonální 
        #č k přímce, na které leží ty naši dva vzorky
        #č musíme ho (QR rozkladem) ortogonalizovat
        for dim in range(1, ndim-1):
            #č co jsem viděl, numpy matici Q normalizuje
            #č a první sloupec zůstavá (skoro) tím samým, co byl před tím
            basis[:, :dim+1], __ = np.linalg.qr(basis[:, :dim+1])
            
            # get constrain
            a = basis[:, dim]
            b = get_offsets(a, X)
            if (np.max(b) - np.max(b[[i, j]])) < tol:
                return True
            
            #else:
            idx = np.argmax(b)
            idxs.append(idx)
            basis[:, 2:dim+1] = basis[:, 1:dim]
            basis[:, 1] = X[idx] - X[i]
            basis[:, dim+1] = half_point
        
        #č Doufám, že idxs budou unikatní
        assert len(idxs) == len(set(idxs))
        
        #č v tuhle chvili máme ndim indexů
        #č což bude stačít na jeden simplex 
        #č v původním ndim-1 prostoru.
        indices = np.array(idxs)
        basis = X[indices]
        basis = basis - basis[-1]
        basis, __ = np.linalg.qr(basis.T)
        # get constrain
        a = basis[:, -1]
        b = get_offsets(a, X)
        if (np.max(b) - np.max(b[[i, j]])) < tol:
            return True
        
        #č Doufám, že idxs budou unikatní
        assert len(idxs) == len(set(idxs))
        
        idx = np.argmax(b)
        idxs.append(idx)
        
        #č Dále už jedeme triangulací
        tri = Delaunay(self.points[idxs], incremental=True)
        
        while True:
            if tri.coplanar.size:
                return True
                
            status, basis = self.get_tri_basis(tri, idxs)
            if not status:
                return False
            
            # get constrain
            a = basis[:, -1]
            b = get_offsets(a, X)
            if (np.max(b) - np.max(b[[i, j]])) < tol:
                return True
            
            #č Doufám, že idxs budou unikatní
            assert len(idxs) == len(set(idxs))
            
            idx = np.argmax(b)
            idxs.append(idx)
            tri.add_points(np.atleast_2d(self.points[idx]))





#
# Voronoi adjacency by linear programming
#



class LinearSolver:
    """
    linprog:
    minimize c @ x
    such that:
    A_ub @ x <= b_ub
    A_eq @ x == b_eq
    lb <= x <= ub
    """
    
    def __init__(self, points):
        self.gabriel = Gabriel(points)
        
        
        self.points = points
        nsim, ndim = points.shape
        size = nsim * (nsim - 1) // 2
        self.condensed_contacts = np.zeros(size, dtype=bool)
        self.arange = np.arange(nsim)
        self.nsim = nsim
        
        self.A = A = np.empty((ndim + 1, nsim))
        A[:-1] = points.T
        A[-1] = 1
        
        self._b = np.empty(ndim + 1)
        self._b[-1] = 1
        
        self.c = np.sum(np.square(points), axis=1)
        
    def LP(self, couple_indices):
        i, j = couple_indices
        X = self.points
        
        midpoint = np.mean(X[[i, j]], axis=0)
        b_eq = self._b
        b_eq[:-1] = midpoint
        
        return linprog(self.c, A_eq=self.A, b_eq=b_eq)
        
    def is_couple(self, couple_indices, tol=1e-5):
        i, j = couple_indices
        if self._get_contact(i, j):
            return True
            
        if self.gabriel.is_couple(couple_indices):
            self._set_contact(i, j)
            return True
        
        result = self.LP(couple_indices)
        mask = result.x > tol
        self._handle_polytope(self.arange[mask])
        
        return mask[i] and mask[j]
        
        #X = self.points
        #test = (np.inner(X[i], X[i]) + np.inner(X[j], X[j])) / 2
        #return test <= (result.fun + tol)
        
    
    
    def _handle_polytope(self, polytope):
        if len(polytope) > 1:
            i = polytope[0]
            jj = polytope[1:]
            self._handle_polytope(jj)
            for j in jj:
                self._set_contact(i, j)
        
    def _set_contact(self, x, y):
        i, j = min(x, y), max(x, y)
        entry = self.nsim * i + j - ((i + 2) * (i + 1)) // 2
        self.condensed_contacts[entry] = True
        
    def _get_contact(self, x, y):
        i, j = min(x, y), max(x, y)
        entry = self.nsim * i + j - ((i + 2) * (i + 1)) // 2
        return self.condensed_contacts[entry]
        



class ConvexLinear(LinearSolver):
    def __init__(self, points, convex_solver=convex_sprite):
        super().__init__(points)
        
        nsim, ndim = points.shape
        self.lifted_points = np.empty((nsim, ndim + 1))
        self.lifted_points[:, :ndim] = points
        # kind of datascience. feature space, quadratic kernel...
        self.lifted_points[:, -1] = np.sum(np.square(points), axis=1)
        
        self.convex_solver = convex_solver
    
    def is_couple(self, couple_indices, tol=1e-5, **kwargs):
        i, j = couple_indices
        if self._get_contact(i, j):
            return True
            
        if self.gabriel.is_couple(couple_indices):
            self._set_contact(i, j)
            return True
        
        if self.convex_solver(self.lifted_points, couple_indices,  tol=tol, **kwargs):
            self._set_contact(i, j)
            return True
        
        result = self.LP(couple_indices)
        mask = result.x > tol
        self._handle_polytope(self.arange[mask])
        
        return mask[i] and mask[j]
    


