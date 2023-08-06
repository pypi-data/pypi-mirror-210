#!/usr/bin/env python
# coding: utf-8

"""
tohle je mezivrstva mezi simplexovymi odhady v boxu a grafy v qt_plot
(Kdybych věřil, že je to jen pro qt_plot, tak ten modul nevytvařím)

#Podle kódu pyqtgraph a matplotlib už je jasný, že musím vracet 2 numpy vektory.
#Asi nebudu zahrnovat .zerosafe() - je to jen zvlaštnost pyqtgraph
#Není úplně jasně, zda mám dělat třídu (stateful), 
#nebo mám se omezit jen na funkci (stateless)
#Minule přišel jsem na potřebu stateful, 
#ale už si nepamatuji proč.

není aktuální, ale ty estimátory furt nemám promyšlený.
Podstata problému spočívá v tom, že současný DiceBox
ukladá odhady dvěma různejma způsoby, přičemž 
TRI odhady jsou ukladány jako slovníky (strukturováně).
Pro ty strukturovaná data Pandas (aj obecně tabulka)
není ideální volba. Na druhou stranu chceme jednoduše
všechno co máme nakreslit a vyexportovat do Excelu.
"""

import numpy as np
#č právě kvůli pandas davam tohle do separatního modulu
#č normálně kód WellMet pandas nevyžaduje
import pandas as pd 
        

def get_estimation_data(estimations, metric):
    metric_dict = dict()
    #č new-style: šecko leží dohromady a každý z toho
    #č bere co chce a jak chce
    #č ne že by to bylo nějak šetrný
    #č estimation je slovníkem
    for estimation in estimations:
        #č nsim musí mäť každej odhad
        #č pokud nemá - je třeba jej prostě opravit
        nsim = estimation['nsim']
        try: 
            metric_dict[nsim] = estimation[metric]
        except KeyError as e:
            pass #print(self.__class__.__name__ + ":", repr(e))
    
    #č nikdo neslibil, že budou v pořadí
    x = np.sort(tuple(metric_dict.keys()))
    y = np.array(tuple(metric_dict.values()))[np.argsort(tuple(metric_dict.keys()))]
    return x, y


def proxy(dice_box, nsim):
    proxy = dice_box.proxy
    index = np.array(nsim)-1
    #č indexy musíme o jedničku změnšit
    #č výsledek nikoliv. Takže v cajku.
    return np.cumsum(~proxy.astype(bool))[index]


#č vysledek dlouhého přemyšlení, co a jak mám udělat.
#č nic lepšího nenapadá: 
#č pandas není vhodný pro strukturována data
#č (možná aj strukturování není úplně na místě), 
#č ale exportovat do Excelčíku se mi taky chce
def get_tri_data_frame(dice_box, sources=['box', 'user'], apply_proxy=False):
    
    #č přeneseme rozhodování do volajícího kódu
#    #č nejdřív proxy. None znamená podle přitomosti
#    if apply_proxy is None:
#        if hasattr(dice_box, 'proxy'):
#            apply_proxy = True
#        else:
#            apply_proxy = False
    
    #č teď zdroje (zjednodušeně). Zatím netřeba nic komplikovat
    #č po těch pomocných funkcích budu chtit df s nastaveným index=nsim
    #č a sloupcem nsim (ten je spíš pro nás, lidé). proxy nemají řešit
    
    #č je tu fakt velkej bordel s těmi odhadama
    #č to jistě budu muset překopávat
    tri_box_estimator = 'TRI_overall_estimations'
    if ('box' in sources) and (tri_box_estimator in dice_box.guessbox.estimations):
        df_box = get_tri_box_df(dice_box, tri_box_estimator)
    else: #č pak nakrmíme pd.concat'u
        df_box = None
    
    if 'user' in sources:
        df_user = get_tri_user_df(dice_box)
    else: #č pak nakrmíme pd.concat'u
        df_user = None
    
    #č předbežně:
    #č nejdřív concat (spojime zdroje dohromady)
    df = pd.concat((df_box, df_user), sort=False)
    
    #č pak deduplicate 
    #č (aby se převzaly odhady se stejným nsim z posledního zdroje)
    df = df.groupby(level=0).last()
    
    #č dale vytřídíme odhady dle nsim
    df.sort_values('nsim', inplace=True)
    
    #č pokud použiváme proxy, tak je vložit, vyhodit ďupy, nahradit index
    if apply_proxy:
        #č teoreticky index a nsim musejí bejt stejné
        nsim = df.index
        nsim_proxy = proxy(dice_box, nsim)
        #č oboje nsim a nsim_proxy jsou pro lide, aby zahrivalo srdce
        #č předpokladá se, že volající kód bude použivat index
        df.insert(loc=0, column='nsim (proxy)', value=nsim_proxy)
        #č nahradit index, pak vyhodit ďupy
        df.index = nsim_proxy
        df = df.groupby(level=0).last()
        
    #č když ne - tak jenom nahradíme index a vypadneme otsuď 
    #č Alexi, co? vždyť ten index už nemusíme řešit, ten musí bejt v pořádku!
    
    #č vemte ten svůj pitomej rám
    #č a na shledanou!
    return df
    
    
    
    

def get_tri_box_df(dice_box, tri_estimation_name='TRI_overall_estimations'):
    #č chyby nechť chytá volající kód!
    data = dice_box.guessbox.estimations[tri_estimation_name]
    nsim, tri_data = data
    # it can be effectively done with pandas
    df = pd.DataFrame(tri_data, index=nsim)
    # -1 = 'outside', 0=success, 1=failure, 2=mix
    df.rename(columns={-1:'outside', 0:'success', 1:'failure', 2:'mix'}, inplace=True)
    df.insert(loc=0, column='nsim', value=nsim)
    
    
    if 'vertex_estimation' in dice_box.guessbox.estimations:
        data = dice_box.guessbox.estimations['vertex_estimation']
        nsim, y = data
        #č zatím nevidím důvod komplikovat
        #č ale je tu předpoklad konzistenci skříňky
        df['vertex_estimation'] = y 
    
    if 'weighted_vertex_estimation' in dice_box.guessbox.estimations:
        data = dice_box.guessbox.estimations['weighted_vertex_estimation']
        nsim, y = data
        #č zatím nevidím důvod komplikovat
        #č ale je tu předpoklad konzistenci skříňky
        df['weighted_vertex_estimation'] = y 
        
    return df
            




def get_tri_user_df(dice_box):
    metrics = ['TRI_estimation', \
                 'vertex_estimation', 'weighted_vertex_estimation']
                            
    metadict = dict()
    for metric in metrics:
        metadict[metric] = dict()
    
    #č new-style: šecko leží dohromady a každý si z toho
    #č bere co chce a jak chce
    #č ne že by to bylo nějak šetrný
    #č estimation je slovníkem
    for estimation in dice_box.estimations:
        # nsim musí mäť každej odhad
        # pokud nemá - je třeba jej prostě opravit
        nsim = estimation['nsim']
        for metric in metrics:
            #č tuším __contains__ je lehčí jak exception
            if metric in estimation:
                metadict[metric][nsim] = estimation[metric]
    
    #č vytahneme 'TRI_estimation' z metrik aj ze slovníku
    tri_estimation = metadict.pop(metrics.pop(0)) # == 
    #č zda se, že zde nic nehodí chybu, aj kdyby žádné odhady nebyly
    nsim = tuple(tri_estimation.keys())
    # it can be effectively done with pandas
    df = pd.DataFrame(tuple(tri_estimation.values()), index=nsim)
    # -1 = 'outside', 0=success, 1=failure, 2=mix
    df.rename(columns={-1:'outside', 0:'success', 1:'failure', 2:'mix'}, inplace=True)
    df.insert(loc=0, column='nsim', value=nsim)
    #df.sort_values('nsim', inplace=True) #č zbytečně
    
    #č musely tam zůstat jenom 'vertex_estimation' 
    #č a 'weighted_vertex_estimation'
    for metric in metrics:
        s = pd.Series(metadict[metric])
        df[metric] = s
    
    return df

#č sice nazev obsahuje DataFrame, dědiť my jeho, конечно же, nebudeme
#č pořadně nerozumím, proč tu třídu dělám. Valčím s komplicitou
#č zatím jsem rozhod, že je zbytečně dělat wrap .pf_exact'u a .pf_exact_method'u
#č patří navíc nahé skřiňce
#class BoxEstimationsDataFrame:
#    def __init__(self, dice_box):
#        self.dice_box = dice_box
#        
#        
#            
#    
#    #č aspoň něco
#    def __contains__(self, estimation):
#          return True 
#        
#            
#
#    def _pens_data_update(self):
#        df = self.df
#        nsim = df.nsim.to_numpy()
#        if self.proxy_chk.isChecked():
#            x = self.proxy(nsim)
#            df.insert(loc=0, column='nsim (proxy)', value=x)
#        else:
#            x = nsim
#        # (in case of LogPlot) fallback values also used
#        success_values = df.failure+df.mix+df.out
#        outmix_values = df.failure+df.mix
#        failure_fallback = np.where(outmix_values > 0, outmix_values, success_values)
#        self.pen_f.setData(*self.zerosafe(x, df.failure, failure_fallback))
#        self.pen_outmix.setData(*self.zerosafe(x, outmix_values, success_values))
#        self.pen_success.setData(*self.zerosafe(x, success_values))
#    
#    
#    def redraw(self):
#        xmin = np.inf
#        xmax = -np.inf
#        tri_estimation = dict()
#        try: # тут всё что угодно может пойти не так
#            # kruci, ještě navic i generovať pokažde znovu...
#        
#            # new-style: šecko leží dohromady a každý si z toho
#            # bere co chce a jak chce
#            # ne že by to bylo nějak šetrný
#            # estimation je slovníkem
#            for estimation in self.dice_box.estimations:
#                # nsim musí mäť každej odhad
#                # pokud nemá - je třeba jej prostě opravit
#                nsim = estimation['nsim']
#                try: 
#                    tri_estimation[nsim] = estimation['TRI_estimation']
#                    if nsim > xmax:
#                        xmax = nsim
#                    if nsim < xmin:
#                        xmin = nsim
#                        
#                except KeyError as e:
#                    pass #print(self.__class__.__name__ + ":", repr(e))
#            
#            #č neotravuj uživatele chybovejma hlaškama
#            if tri_estimation:
#                # it can be effectively done with pandas
#                self.df = df = pd.DataFrame(tuple(tri_estimation.values()))
#                # -1 = 'out', 0=success, 1=failure, 2=mix
#                df.rename(columns={-1:'out', 0:'success', 1:'failure', 2:'mix'}, inplace=True)
#                df.insert(loc=0, column='nsim', value=tuple(tri_estimation.keys()), allow_duplicates=False)
#                df.sort_values('nsim', inplace=True)
#
#                self._pens_data_update()
#            
#                nsim, y = get_estimation_data(self.dice_box.estimations, 'vertex_estimation')
#                df['vertex_estimation'] = y #č spolehám na konzistenci odhadů (ne úplně)
#                self.pen_vertex.setData(*self.zerosafe(self.proxy(nsim), y))
#                
#                nsim, y = get_estimation_data(self.dice_box.estimations, 'weighted_vertex_estimation')
#                df['weighted_vertex_estimation'] = y #č spolehám na konzistenci odhadů (ne úplně)
#                self.pen_weighted_vertex.setData(*self.zerosafe(self.proxy(nsim), y))
#        
#            
#        except BaseException as e:
#            print(self.__class__.__name__ + ":", repr(e))
#        
