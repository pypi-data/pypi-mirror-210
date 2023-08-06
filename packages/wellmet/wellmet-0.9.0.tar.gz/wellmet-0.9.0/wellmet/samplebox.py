#!/usr/bin/env python
# coding: utf-8

"""
SampleBox = sample_R(f_model) + g_values
"""


import numpy as np


class SampleBox:
    """
    SampleBox = sample_R(f_model) + g_values
    
    .sampled_plan object
    .g_values
    .failsi
    
    Souřadnice primárně z prostoru modelu, ty co jsme rovnou
    posilali do g_modelu!
    """
    
        # nechtěl bys nazvy proměnných?
    def __new__(cls, sample_object, g_values=(), gm_signature=''):
        """
        Jedname tvrdě - není-li vstup konzistentní, 
        tak sbox vůbec nevytvaříme
        """
        g_values = np.atleast_1d(g_values)
        if len(sample_object) == len(g_values):
            sb = super(SampleBox, cls).__new__(cls)
            # nepotrebujeme žádné rozdělení, nic
            sb.sampled_plan = sample_object
            sb.g_values = g_values
            sb.gm_signature = gm_signature
            return sb
        else:
            raise ValueError("Sample and g_value hasn't the same length. Zkrátka, do sebe nepatří")
    
        
    def __str__(sb):
        return  '%s: %s at %s' %(sb.gm_signature, sb.g_values, sb.sampled_plan)
        
    def __repr__(sb):
        return  'SampleBox(%s, %s, %s)' %(repr(sb.sampled_plan), repr(sb.g_values), repr(sb.gm_signature))
        
    def __len__(sb):
        return len(sb.g_values)
        
        
    def __call__(sb):
        # я ваще хз
        # offer next sample?
        # do calculation?
        # add to this sample?
        # return new instance?
        # мар, сакра, кароно?
        
        # finally, we will offer sample to sample
        # like BlackBox does
        return sb.sampled_plan(1)
    
        
    def __getitem__(sb, slice):
        return SampleBox(sb.sampled_plan[slice], sb.g_values[slice], sb.gm_signature)
        
        
    def __getattr__(sb, attr):
        if attr == 'samplebox':
            return sb
        elif attr == 'failsi':
            # ~(g_values>0) to handle nan
            return ~(sb.g_values>0)
        elif attr == 'success_points':
            return np.argwhere(sb.g_values>0).reshape(-1)
        elif attr == 'failure_points':
            return np.argwhere(~(sb.g_values>0)).reshape(-1)
        elif attr == 'failure_samples':
            return sb[~(sb.g_values>0)]
        elif attr == 'success_samples':
            return sb[sb.g_values>0]
            
        # to je jistě k samplovi
        else:
            return getattr(sb.sampled_plan, attr)
        
        
    def add_sample(sb, input_sb):
        input_sb.consistency_check()
        
        # ты чьих будешь?
        # where are you from?
        # are you one of us?
        if sb.gm_signature == input_sb.gm_signature:
            # dá se tuhle kontrolu jednoduše napálit, ale to neřeším
            sb.sampled_plan.add_sample(input_sb.sampled_plan)
            sb.g_values = np.append(sb.g_values, input_sb.g_values)
            
            return sb.consistency_check()
            
            # je to pro případ prázdného sample_boxu
        elif sb.gm_signature == '':
            # dá se tuhle kontrolu jednoduše napálit, ale to neřeším
            sb.sampled_plan.add_sample(input_sb.sampled_plan)
            sb.g_values = np.append(sb.g_values, input_sb.g_values)
            sb.gm_signature = input_sb.gm_signature
            return sb.consistency_check()
        else:
            #raise ValueError("Merge sa nám nějak nepovedol")
            print(sb.gm_signature, input_sb.gm_signature)
            print(type(sb.gm_signature), type(input_sb.gm_signature))
            raise ValueError("gm_signatures are unequal. You are probably trying to merge data from different sources")
                
    def new_sample(sb, input_sb):
        """
        We want to create new SampleBox object with our distribution (f_model)
        but with data of input_sb (just like f_model.new_sample() does)
        """
        return SampleBox(sb.sampled_plan.new_sample(input_sb), input_sb.g_values, input_sb.gm_signature)
        
    def consistency_check(sb):
        if len(sb.sampled_plan)==len(sb.g_values):
            return True
        else:
            # уг тодӥськы чик мар кароно
            # ConsistencyError
            raise ValueError('SampleBox is in an inconsistent state and nobody knows what to do with it')
            
