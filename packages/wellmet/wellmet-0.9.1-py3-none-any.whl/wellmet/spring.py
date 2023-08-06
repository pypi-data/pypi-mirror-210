#!/usr/bin/env python
# coding: utf-8

import numpy as np


#č v statistice rozptyl jednotlyvých měření charakterizuje přesnost
# https://en.wikipedia.org/wiki/Inverse-variance_weighting
#č z teorii chyb měření
#č mame-li změřené dvě části l_1 a l_2, co musejí dohromady dat L,
#č můžeme spočítat odchylku delta = L - l_1 - l_2
#č Znamé-li přesnost jednotlivých měření 1/var_1 a 1/var_2,
#č můžeme tvrdit, že opravy jsou:
# v_1 = delta * var_1 / (var_1 + var_2)
# v_2 = delta * var_2 / (var_1 + var_2)
#č a tedy, že výrovnáné hodnoty jsou:
# l_1' = l_1 + v_1
# l_2' = l_2 + v_2
#č problemem je, že takovéto lineární vyrovnání může davat záporné hodnoty

#č zkusme hledat řešení v mechanice,
#č využijme pružinovou analogii.
#č Máme-li soustavu několika (třeba dvou) pružin, zapojených sériově,
#č kterou zatížíme sílou F, tak deformace soustavy bude:
#č delta_1 + delta_2 = delta = F/k_1 + F/k_2 = F*c_1 + F*c_2
# delat_1 = delta * c_1 / (c_1 + c_2)
# delat_2 = delta * c_2 / (c_1 + c_2)

#č takhle jsme přišli na ekvivalenci nějakého lineárního vyrovnavaní 
#č a sériové soustavy pružin.
#č A teď ten trik - uvažovat deformace těch pružin nelineárně,
#č znemožnit stlačení do záporných délek

# d_epsilon = d_l / l
#č True strain = ln(l/L) = ln(l) - ln(L), kde
#č l je delka pružiny (prutu) po deformaci
#č L je původní délka

#č definujme sílu jako F = strain(epsilon) * tuhost(EA), tj.
# k = EA/l
# poddajnost(c) = původní_délka(l) / EA
# EA = l / c
#č EA vnímáme jako přirozenou charakteristiku, vlastnost
#č u těch charakteristik tuhostí-poddajností 
#č lze všimnout jistou analogii s betama (nebo s CoV),
#č ale liší se jednotky, dělíme rozptílem, nikoliv směrodatnou odchylkou!
#č nebo epsilon = F * poddajnost(c) / původní_délka(l)
#č (výpočet za použití poddajností je hodně jednodušší a přehlednější)
#č řešíme soustavu rovnic
# l_1 + l_2 + l_100500 = L 
# F_1 = F_2 = F_100500 = F
#č zde L je délka soustavy
#č F je síla, působicí na soustavu


def get_true_strain_spring_solution(lenghts, flexibilities, L=1):
    """calculates corrected data for bounded statistically estimated values. 
    It uses nonlinear spring analogy, based on logarithmic strain ε,
     also called, true strain or Hencky strain"""
    #č tohle musí hlídat volající kód
    assert np.all(np.isfinite(lenghts)) and np.all(lenghts > 0)
    assert np.all(np.isfinite(flexibilities)) and np.all(flexibilities > 0)
    
    Ls = lenghts #č původní
    ls = lenghts #č vystupní
    cs = flexibilities
    #č EA vnímáme jako přirozenou charakteristiku, vlastnost
    #č EA jsou z hlediska statistiky vahami
    EAs = lenghts / flexibilities 
    #L = L
    
    i = 0 #č počet iterací
    sum_ls = np.sum(ls)
    
    
    
    #č V tlaku - (záporný) přírůstek síly může (ale nemusí!) narůstat
    #č v tahu Newtonová metoda může nejdřív soustavu 
    #č roztahnout do nekonečna a teprve pak stlačovat zpatky
    #č Právě kvůli tomu v tahu můžou vylezt nekonečna
    #č Jistě máme epsilon bound, definovaný jako delta_L / min(lenghts):
    #
    # linear_epsilon_max = delta_L / min(lenghts),
    #
    #č ale nemůžeme jej použit přímo pro výpočet síly,
    #č F_max vždy vyjde větší jak samotné F-ko za normálního výpočtu:
    #
    # F = delta_L / np.sum(cs)
    # F_max = max(delta_L / flexibilities)
    # F_supermax = linear_epsilon_max * max(EAs)
    # F_supermax = delta_L / min(lenghts) * max(lenghts / flexibilities)
    # F <= F_max <= F_supermax
    #
    
    
    # let's try first approximation
    #č Mám dojem, že se známenko může změnit pouze po první iteraci
    #č Zde může být jak tlak, tak i tah, dále - pouze tlak
    if sum_ls != L:
        #č zaporná - zkracovat, kladná - prodlužovat
        delta_L = L - sum_ls
        # linear approximation
        #č odhadneme sílu
        F = delta_L / np.sum(cs)
        
        #č aha. To je právě ta věc.
        #č nemůžeme rovnou spočítat délky
        #č musíme jít bočnou cestou přes true strain
        # delta_i = F * c_i
        #ls += F * c #ё нихрена подобного!
        
        #č epsilon = F * poddajnost(c) / původní_délka(l)
        epsilons = F / EAs
        ls = np.exp(epsilons) * Ls
        
        i += 1 #č počet iterací
        sum_ls = np.sum(ls)
        print("spring:", i, "delta", delta_L, "F", F)
    
    #č nechcu explicitně výjadřovat přesnost
    #č raději budu sledovat vyši přírůstků.
    #č neplatí, že první iterace musí být větší jak ty další
    #č V tlaku - (záporný) přírůstek síly může (ale nemusí!) narůstat
    #č Doufám, že žádná nekonečna, nanky zde nevylezou
    delta_F = -1 #č ať projdeme kontrolou
    while (sum_ls != L) and (delta_F < 0): # while 1 + 1e-20 != 1
        #č zaporná - zkracovat, kladná - prodlužovat
        delta_L = L - sum_ls
        
        cs = ls / EAs
        # linear approximation
        #č teď bacha, sílu musíme počítat v přirůstcích
        delta_F = delta_L / np.sum(cs)
        F += delta_F
        
        #č epsilon = F * poddajnost(c) / původní_délka(l)
        epsilons = F / EAs
        ls = np.exp(epsilons) * Ls

        i += 1 #č počet iterací
        sum_ls = np.sum(ls)
        print("spring:", i, "delta", delta_L, "F", F)
    
    return ls
        
        
        
def get_semi_true_strain_spring_solution(lenghts, flexibilities, L=1):
    """calculates corrected data for bounded statistically estimated values. 
    It uses nonlinear spring analogy, based on true strain in compression 
    and engineering (Cauchy) strain in tension"""
    
    sum_ls = np.sum(lenghts)
    if sum_ls == L:
        print("spring: no action needed")
        return lenghts
    
    #č tohle musí hlídat volající kód
    assert np.all(np.isfinite(lenghts)) and np.all(lenghts > 0)
    assert np.all(np.isfinite(flexibilities)) and np.all(flexibilities > 0)
    
    Ls = lenghts #č původní
    ls = lenghts #č vystupní
    cs = flexibilities
    
    
    #č v tahu Newtonová metoda mohla by nejdřív soustavu 
    #č roztahnout do nekonečna a teprve pak stlačovat zpatky
    #č Právě kvůli tomu v tahu mohly by vylezt nekonečna
    #
    #č Zde pointa je v tom, že nepotřebujeme precizní pružiny,
    #č postačí nám, když tlak budeme omezovat, 
    #č aby nám délky neujely do záporných hodnot,
    #č zatímco v tahu jednoduše použit lineárné řešení
    
    #č zaporná - zkracovat, kladná - prodlužovat
    delta_L = L - sum_ls
    # linear approximation
    #č odhadneme sílu
    F = delta_L / np.sum(cs)
    
    if F > 0:  #č je třeba roztahovat
        ls += F * cs
        print("spring: tension; linear solution is used.", "Delta=", delta_L)
        return ls
    
    else: #compression, prepare for iteration
        #č EA vnímáme jako přirozenou charakteristiku, vlastnost
        #č EA jsou z hlediska statistiky vahami
        EAs = lenghts / flexibilities 
        
        #č epsilon = F * poddajnost(c) / původní_délka(l)
        epsilons = F / EAs
        ls = np.exp(epsilons) * Ls
        
        i = 1 #č počet iterací
        sum_ls = np.sum(ls)
        print("spring: compression #", i, "delta=", delta_L, "F=", F)
    
    #č nechcu explicitně výjadřovat přesnost
    #č raději budu sledovat vyši přírůstků.
    #č neplatí, že první iterace musí být větší jak ty další
    #č V tlaku - (záporný) přírůstek síly může (ale nemusí!) narůstat
    #č Mám dojem, že se známenko může změnit pouze po první iteraci
    #č Doufám, že žádná nekonečna, nanky zde nevylezou
    delta_F = - np.inf #č ať projdeme kontrolou
    while (sum_ls != L) and (F + delta_F < F): # while 1 + 1e-20 != 1
        #č zaporná - zkracovat, kladná - prodlužovat
        delta_L = L - sum_ls
        
        cs = ls / EAs
        # linear approximation
        #č teď bacha, sílu musíme počítat v přirůstcích
        delta_F = delta_L / np.sum(cs)
        F += delta_F
        
        #č epsilon = F * poddajnost(c) / původní_délka(l)
        epsilons = F / EAs
        ls = np.exp(epsilons) * Ls

        i += 1 #č počet iterací
        sum_ls = np.sum(ls)
        print("spring: compression #", i, "delta=", delta_L, "F=", F)
    
    return ls 
        
        
#č je to implicitní volba     
get_spring_solution = get_semi_true_strain_spring_solution
        
        
#č Mohli bychom počítat v tlaku Eulerem, v tahu - Greenem. 
#оӵ Кинлы со меда кулэ?
#
#def get_euler_almansi_strain_spring_solution(lenghts, flexibilities, L=1):
#    """calculates corrected data for bounded statistically estimated values. 
#    It uses nonlinear spring analogy, based on Euler-Almansi strain"""
#    #č tohle musí hlídat volající kód
#    assert np.all(np.isfinite(lenghts)) and np.all(lenghts > 0)
#    assert np.all(np.isfinite(flexibilities)) and np.all(flexibilities > 0)
#    
#    Ls = lenghts #č původní
#    ls = lenghts #č vystupní
#    cs = flexibilities
#    #č EA vnímáme jako přirozenou charakteristiku, vlastnost
#    #č EA jsou z hlediska statistiky vahami
#    EAs = lenghts / flexibilities 
#    #L = L
#    
#    i = 0 #č počet iterací
#    sum_ls = np.sum(ls)
#    
#    
#    # Euler-Almansi strain
#    # epsilon_EA = (l**2 - L**2) / 2 / l**2
#    
#    
#    #č V tlaku - (záporný) přírůstek síly může (ale nemusí!) narůstat
#    #č v tahu Newtonová metoda může nejdřív soustavu 
#    #č roztahnout do nekonečna a teprve pak stlačovat zpatky
#    #č Právě kvůli tomu v tahu můžou vylezt nekonečna
#    #č Jistě máme epsilon bound, definovaný jako delta_L / min(lenghts):
#    #
#    # linear_epsilon_max = delta_L / min(lenghts),
#    #
#    #č ale nemůžeme jej použit přímo pro výpočet síly,
#    #č F_max vždy vyjde větší jak samotné F-ko za normálního výpočtu:
#    #
#    # F = delta_L / np.sum(cs)
#    # F_max = max(delta_L / flexibilities)
#    # F_supermax = linear_epsilon_max * max(EAs)
#    # F_supermax = delta_L / min(lenghts) * max(lenghts / flexibilities)
#    # F <= F_max <= F_supermax
#    #
#    #č 
#    
#    while (sum_ls < L) and (delta_F < 0): #č je třeba roztahovat
#        #č zaporná - zkracovat, kladná - prodlužovat
#        #č takže delta_L musí být kladná
#        delta_L = L - sum_ls
#        
#        cs = ls / EAs
#        # linear approximation
#        #č teď bacha, sílu musíme počítat v přirůstcích
#        delta_F = delta_L / np.sum(cs)
#        F += delta_F
#        
#        #č epsilon = F * poddajnost(c) / původní_délka(l)
#        epsilons = F / EAs
#        ls = np.exp(epsilons) * Ls
#
#        i += 1 #č počet iterací
#        sum_ls = np.sum(ls)
#        print("spring:", i, "delta", delta_L, "F", F)
#    
#    
#    # let's try first approximation
#    if sum_ls != L:
#        #č zaporná - zkracovat, kladná - prodlužovat
#        delta_L = L - sum_ls
#        # linear approximation
#        #č odhadneme sílu
#        F = delta_L / np.sum(cs)
#        
#        #č aha. To je právě ta věc.
#        #č nemůžeme rovnou spočítat délky
#        #č musíme jít bočnou cestou přes true strain
#        # delta_i = F * c_i
#        #ls += F * c #ё нихрена подобного!
#        
#        #č epsilon = F * poddajnost(c) / původní_délka(l)
#        epsilons = F / EAs
#        ls = np.exp(epsilons) * Ls
#        
#        i += 1 #č počet iterací
#        sum_ls = np.sum(ls)
#        print("spring:", i, "delta", delta_L, "F", F)
#    
#    #č nechcu explicitně výjadřovat přesnost
#    #č raději budu sledovat vyši přírůstků.
#    #č neplatí, že první iterace musí být větší jak ty další
#    #č V tlaku - (záporný) přírůstek síly může (ale nemusí!) narůstat
#    #č v tahu, tuším, tahle Newtonová metoda může nejdřív soustavu 
#    #č roztahnout do nekonečna a teprve pak stlačovat zpatky
#    #č Mám dojem, že se známenko může změnit pouze po první iteraci
#    #č Doufám, že žádná nekonečna, nanky zde nevylezou
#    delta_F = -1 #č ať projdeme kontrolou
#    while (sum_ls != L) and (delta_F < 0): # while 1 + 1e-20 != 1
#        #č zaporná - zkracovat, kladná - prodlužovat
#        delta_L = L - sum_ls
#        
#        cs = ls / EAs
#        # linear approximation
#        #č teď bacha, sílu musíme počítat v přirůstcích
#        delta_F = delta_L / np.sum(cs)
#        F += delta_F
#        
#        #č epsilon = F * poddajnost(c) / původní_délka(l)
#        epsilons = F / EAs
#        ls = np.exp(epsilons) * Ls
#
#        i += 1 #č počet iterací
#        sum_ls = np.sum(ls)
#        print("spring:", i, "delta", delta_L, "F", F)
#    
#    return ls
        

