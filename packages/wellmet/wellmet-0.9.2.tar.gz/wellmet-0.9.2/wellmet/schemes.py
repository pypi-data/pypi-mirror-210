#!/usr/bin/env python
# coding: utf-8

import quadpy

un_spheres = [
    "dobrodeev_1978",
    "mysovskikh_1",
    "mysovskikh_2",
    "stroud_un_3_1",
    "stroud_un_3_2",
    "stroud_un_5_1",
    "stroud_un_5_2",
    "stroud_un_5_3",
    "stroud_un_5_4",
    "stroud_un_7_2",
    "stroud_un_7_1",
    "stroud_un_11_1",
#    "stroud_1967", # dup of "stroud_un_7_1"
#    "stroud_1969", # dup of "stroud_un_11_1"
]

#č Bacha! Lidstvo nemusí nutně dočkat 
#č ukončení výpočtu této funkce
def get_all_un_sphere_schemes(dim):
    schemes = dict()
    for item in un_spheres:
        Scheme = getattr(quadpy.un, item)
        try:
            scheme = Scheme(dim)
            schemes[scheme.name] = scheme
        except:
            pass
            
    return schemes



# up to degree 7. Ought to be enough for anybody
#č 7 stupňů musí stačit každému
def get_all_tn_simplex_schemes(dim):
    #č současný qt_plot vytahuje schemata ze slovníku
    #č aspoň netřeba v dlouhém seznamu dohledávat 
    schemes = dict()
    # Grundmann, Möller
    for i in range(8):
        scheme = quadpy.tn.grundmann_moeller(dim, i)
        schemes[scheme.name] = scheme
    # Silvester
    for i in range(7):
        scheme = quadpy.tn.silvester(dim, variant="open", n=i+1, symbolic=False)
        schemes[scheme.name] = scheme
        scheme = quadpy.tn.silvester(dim, variant="closed", n=i+1, symbolic=False)
        schemes[scheme.name] = scheme
    
    # Laufer, Hammer and Stroud
    for item in tn_simplices:
        Scheme = getattr(quadpy.tn, item)
        try:
            scheme = Scheme(dim)
            schemes[scheme.name] = scheme
        except:
            print(item, "Excluded")
        
    return schemes
    
    # v - has points at vertices
    # i - scheme has not integration points at vertices
    #
    # p - positive, all weights are positive
    # n - scheme has negative weights as well
tn_simplices = [
                'stroud_tn_1_1', # i p # single centroid point
                'stroud_tn_1_2', # v p # vertices only # laufer_1
                'stroud_tn_2_1a', # i p, positive, stejné váhy # ndim + 1 points # Hammer-Stround 1a # umísuje bodíky s odstupem od středu směrem k vrcholům
                'stroud_tn_2_1b', # i p, positive, stejné váhy # ndim + 1 points # Hammer-Stround 1b # umísuje bodíky na stěny simplexu 
                'stroud_tn_2_2', # negative # laufer_2
                'stroud_tn_3_1', # i negative
                'stroud_tn_3_2', # v negative
                'stroud_tn_3_3', # v negative pro ndim >=4
                'stroud_tn_3_4', # i p, positive # 45 points at 8D # Stroud 1966-II
                'stroud_tn_3_5', # v negative pro ndim >=7
                'stroud_tn_3_6a', # i p, positive, stejné váhy # 72 points at 8D # Stroud 1964a # obecně ndim <= 9 
                'stroud_tn_3_6b', # i p, positive, stejné váhy # 72 points at 8D # Stroud 1964b
                'stroud_tn_3_7', # v, positive pro ndim <= 9 # 94 points at 8D
                'stroud_tn_3_8', # v, positive pro ndim <= 9 # 102 points at 8D
                'stroud_tn_3_9', # v n # laufer_3
                'stroud_tn_3_10', # i n (depends on dimension)
                'stroud_tn_3_11', # v n (depends on dimension)
                'stroud_tn_4_1', # v negative # laufer_4 n>=3
                'stroud_tn_5_1', # i n
                'stroud_tn_5_2', # v negative # laufer_5 n>=4
                'walkington_1', # i p # single centroid point
                'walkington_2', # bůhvíco, positive # I have strong suspicious, that it places points outside the simplex
                'walkington_3', # i negative
                'walkington_5', #owntest n=2,3 
                'walkington_7' #owntest n=3
                ]

tn_simplices_2d = [
                'stroud_tn_1_1', 
                'stroud_tn_1_2', # laufer_1
                'stroud_tn_2_1a', 
                'stroud_tn_2_1b', 
                'stroud_tn_2_2', # laufer_2
                'stroud_tn_3_1', 
                'stroud_tn_3_2', 
                'stroud_tn_3_3', 
                'stroud_tn_3_4', 
                'stroud_tn_3_6a', 
                'stroud_tn_3_6b',
                'stroud_tn_3_8', 
                'stroud_tn_3_9', # laufer_3 
                'walkington_1', 
                'walkington_2', 
                'walkington_3', 
                'walkington_5', #owntest n=2,3 
                ]
                
def get_t2_keys():
    return list(quadpy.t2.schemes.keys()).extend(tn_simplices_2d)
    
def get_t3_keys():
    return list(quadpy.t3.schemes.keys()).extend(tn_simplices)
    
def get_t2_scheme(key):
    try:
        return quadpy.t2.schemes[key]()
    except KeyError:
        Scheme = getattr(quadpy.tn, key)
        return Scheme(2)

def get_t3_scheme(key):
    try:
        return quadpy.t3.schemes[key]()
    except KeyError:
        Scheme = getattr(quadpy.tn, key)
        return Scheme(3)
        
        
def get_tn_keys(ndim):
    keys = ['Grundmann-Möller', 'Silvester open', 'Silvester closed']
    if ndim == 2:
        keys.extend(quadpy.t2.schemes.keys())
        keys.extend(tn_simplices_2d)
    elif ndim == 3:
        keys.extend(quadpy.t3.schemes.keys())
        keys.extend(tn_simplices)
        keys.remove('stroud_tn_5_2')
    elif ndim == 4:
        keys.extend(tn_simplices)
        keys.remove('walkington_5')
        keys.remove('walkington_7')
    elif ndim == 5:
        keys.extend(tn_simplices)
        keys.remove('stroud_tn_3_10')
        keys.remove('stroud_tn_3_11')
        keys.remove('walkington_5')
        keys.remove('walkington_7')
        
    else:
        keys.extend(tn_simplices)
        keys.remove('walkington_5')
        keys.remove('walkington_7')
    return keys


def get_tn_scheme(key, ndim, degree=5):
    if key == 'Grundmann-Möller': #č husté, ale záporné schema. 
        #č n=0 odpovidá jednomu bodíku v těžišti
        #č n=1 odpovidá ndim+1 bodům (šíkmě rovině)
        return quadpy.tn.grundmann_moeller(ndim, degree)
    elif key == 'Silvester open': #č husté positivní (pro degree 1) schema. 
        #č n=1 odpovidá odpovidá ndim+1 bodům (šíkmě rovině). Positivní.
        return quadpy.tn.silvester(ndim, variant="open", n=degree, symbolic=False)
    elif key == 'Silvester closed': #č na hranici, nic dovnitř nedává
        #č n=1 odpovídá bodíkům jen ve vrcholech
        return quadpy.tn.silvester(ndim, variant="closed", n=degree, symbolic=False)
    elif ndim == 2:
        return get_t2_scheme(key)
    elif ndim == 3:
        return get_t3_scheme(key)
    else:
        Scheme = getattr(quadpy.tn, key)
        return Scheme(ndim)
    
    
    
    
            
