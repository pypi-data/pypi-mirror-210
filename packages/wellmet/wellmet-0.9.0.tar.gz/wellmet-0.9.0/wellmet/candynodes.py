#!/usr/bin/env python
# coding: utf-8

"""
č chce se ukladat meta infa k bodíkům.
č CandyBox nepodporuje zadání jednoduchých atributů
č pro celou sadů bodíků. Navíc je těžký a hrozně ošklivý.
č CandyNodes je myšleno jako jednoduchá alternativa
č pro použití uvnitř skříňky, která nejde do vzorků.
"""

class CandyNodes:
    #č to je vše co má samotné CandyNodes
    #č žádný další majetek nepozoruji
    __slots__ = 'sampling_plan', 'attrs', 'kwargs'
    
    def __new__(cls, sample_object, attrs=None, /, **kwargs):
        """
        č Jedname tvrdě - není-li vstup konzistentní, 
        č tak tenhle box vůbec nevytvaříme
        """
        cb = super().__new__(cls)
        cb.sampling_plan = sample_object
        cb.kwargs = kwargs
        if attrs is None:
            cb.attrs = {}
        else:
            cb.attrs = attrs
        
        
        
#        for key, value in kwargs.items():
#            if hasattr(value, '__getitem__') and hasattr(value, "__len__"):
#                cb.kwargs[key] = value
#            else:
#                cb.attrs[key] = value
        
        
        if cb.consistency_check():
            return cb
        else:
            raise ValueError("Sample and given values hasn't the same length. Zkrátka, do sebe nepatří")
            
            
        
    def __repr__(cb):
        return 'CandyNodes(%s, %s, **%s)' % (repr(cb.sampling_plan),\
                                         repr(cb.attrs), repr(cb.kwargs))
        
    def __len__(cb):
        return len(cb.sampling_plan)
        
        
    def __call__(cb, *args, **kwargs):
        # Call meaning is different for underlaying f_models and upper Boxes,
        # however SampleBox expect f_model under.
        # Also CandyNodes tryes to be "better f_model", 
        # so should behave similarly
        f = cb.sampling_plan(*args, **kwargs)
        return CandyNodes(f)
            
    
    def __getitem__(cb, subscript):
        #č subscript vratí nový instance
        #č s nezávislými slovníky.
        #č sice numpy matice uvnitř zůstanou závislé
        #č ale atributy CandyNodes - nikoliv.
        cn = CandyNodes(cb.sampling_plan[subscript])
        #ё нам можна
        cn.attrs.update(cb.attrs)
        #č Sice nechavám na uživateli co vloží do slovníku 
        #č a jak se to bude slajsiť, ale pořad očekavám ideomatické chování
        #č Ošetřuji případ jednoduchého indexu (array[i]), 
        #č který z kontejneru vratí osamelý prvek
        #č a slice, který zas vratí odříznutý kontejněr.
        #č Numpy ještě může brát bulové pole jako index
        if isinstance(subscript, slice) or hasattr(subscript, "__len__"):
            dest_dict = cn.kwargs
        else:
            dest_dict = cn.attrs
        for key, data in cb.kwargs.items():
            dest_dict[key] = data[subscript]
        return cn
        
        
    def __setattr__(cb, key, value):
        try:
            super().__setattr__(key, value)
        except AttributeError:
            #č zde musím hlídat aby attrs a kwargs neobsahovaly stejné klíče
            if hasattr(value, '__getitem__') and hasattr(value, "__len__"):
                if len(cb) != len(value):
                    raise ValueError("Sample and given values hasn't the same length. Zkrátka, do sebe nepatří")
                cb.kwargs[key] = value
                cb.attrs.pop(key, None)
            else:
                cb.attrs[key] = value
                cb.kwargs.pop(key, None)
        
    def __delattr__(cb, key):
        cb.kwargs.pop(key, None)
        cb.attrs.pop(key, None)
        
        
    def __getattr__(cb, attr):
        #č candybox, třeba, nikdy jsem nepoužil
        if attr == 'candynodes':
            return cb
            
        #č hledáme obraceně
        #č nejdřív se zeptame f_model,
        #č teprve když ten nič nemá  
        #č mrkneme atribut u sebe
        try:
            return getattr(cb.sampling_plan, attr)
        except AttributeError:
            if attr in cb.kwargs:
                value = cb.kwargs[attr]
                if len(cb)==len(value):
                    return value
                else:
                    #ё у нас есть дата, но мы их вам недадим)
                    #č zde nechť bude KeyError
                    raise KeyError("CandyNodes: well, we have some data, but they are not consistent, so we haven't")
            elif attr in cb.attrs:
                return cb.attrs[attr]
            else: #č implicitně slovníky hazej KeyError, kterej nechcem
                raise AttributeError
            
            
    def set_attrs(cb, *args, **kwargs):
        #č Je tu nepřijemnost pro uživatele třídy.
        #č Pokud kwargy jíž obsahují klíč,
        #č tak pořád se bude vrácet on protože má přednost.
        #č Nechcu to řešit.
        cb.attrs.update(*args, **kwargs) 
        
        
     
     #č Funkce musí být definována, 
     #č jinak se automaticky zavolá add_sample f-modelu,
     #č a o tom ani nedozvíme
    def add_sample(cb, input, **kwargs):
        #č výkon může zaviset na tom, co posíláme f_modelu: 
        #č f_model, nebo bůhvíco mu neznámého
        #č navíc, uvnitř f_model vůbec nemusí být
        if hasattr(input, 'candynodes'): #sweety_input:
            input = input.sampling_plan
        cb.sampling_plan.add_sample(input, **kwargs)
        #č co mám dělat s kwargy?
        #č doplňovat? Nemám jak - nehlídám a netrvám na numpy
        #č může být v datech cokoli
        #č Hazet chybu? Vyhozovat kwargy?
        if cb.kwargs:
            cb.kwargs.clear()
        
        
    
    #č netuším, kdo to potřebuje v novém kódě
    def new_sample(cb, input=None, **kwargs):
        #č pokud input není, vrácíme samy sobě.
        if input is None:
            return CandyNodes(cb.sampling_plan.new_sample(**kwargs))
            
        #č jinak konvertujem vstup na naše rozdělení
        #č čo to je za vstup?
        if hasattr(input, 'candynodes'): #sweety_input:
            cn = CandyNodes(cb.sampling_plan.new_sample(input.sampling_plan, **kwargs))
            cn.attrs.update(input.attrs)
            cn.kwargs.update(input.kwargs)
            return cn
            
        #č nesladký vstup
        return CandyNodes(cb.sampling_plan.new_sample(input, **kwargs))
        
        
        
    def consistency_check(cb):
        # řvat na celé město nebudeme
        sample_len = len(cb.sampling_plan)
        return all(sample_len == len(cb.kwargs[key]) for key in cb.kwargs)
