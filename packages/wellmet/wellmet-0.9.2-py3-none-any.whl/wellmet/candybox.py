#!/usr/bin/env python
# coding: utf-8

"""
 we need to go deeper...
☺ больше ящиков богу ящиков!

č chce se ještě někam ukladat meta infa od blackboxů 
č K tomu využijme pitonovskej dak tajping a zkusíme strčit tohle mezi
č f-modelem a normálním SampleBoxem. Snad to postačí.
č Když ne - bude třeba šecko překopat.
č (však do souboru CandyBox zatím nepůjde - k tomu je potřeba podpora Readeru.)
"""

#č Nechce se mi tahnout do projektu Pandas jako rekuajred dependensi,
#č ale ani já sam pořadně nerozumím proč 
#č asi proto, že se spíše jedná o pomocnou boční "sekondari" funkcionalitu
try:
    import pandas as pd
    #č pr🐱ozatím je mi šuma ohledně toho, zda píšu do kopii, nebo do slajsu
    #č prozatím zapís do slajsu nejspíš znamená, že původní data jíž nejsou nutná
    #č prozatím se mi nechce robiť explicitné kopii, 
    #č a zatím ponechavám sber odpadů samotnému Pandas
    
    #E disable SettingWithCopyWarning 
    #E Current WellMet policy: if writing to slice have occured, it probably means
    #E original df no more needed
    pd.set_option('mode.chained_assignment', None)
except ImportError:
    print("CandyBox: error of import Pandas. CandyBox will work in Pandas-free mode")

import numpy as np

class CandyBox:

    def __new__(cls, sample_object, df=None, **kwargs):
        """
        Jedname tvrdě - není-li vstup konzistentní, 
        tak tenhle box vůbec nevytvaříme
        """
        cb = super().__new__(cls)
        cb.sampling_plan = sample_object
        
        if df is not None:
            cb.df = df
        else:
            # obalime čísly
            for key in kwargs:
                if not hasattr(kwargs[key], '__getitem__'):
                    kwargs[key] = (kwargs[key],)
                
                
            try:
                cb.df = pd.DataFrame(kwargs)
                # chcem jednoduché numpy-like chovaní
                cb.df.reset_index(inplace=True)
            except NameError: # if there is no "pandas as pd"
                cb.kwargs = kwargs
        if cb.consistency_check():
            return cb
        else:
            raise ValueError("Sample and given values hasn't the same length. Zkrátka, do sebe nepatří")
            
        
    
        
#    def __str__(cb):
#       # if pandas
#       if 'df' in cb.__dict__:
#           return 'CandyBox: %s' % cb.df
#       # if not
#       else:
#           return 'CandyBox: %s' % cb.kwargs
        
    def __repr__(cb):
        # if pandas
        if 'df' in cb.__dict__:
            # df je na svědomi pandas
            return 'CandyBox(%s, df=%s)' % (repr(cb.sampling_plan), repr(cb.df))
        # if not
        else:
            return 'CandyBox(%s, **%s)' % (repr(cb.sampling_plan), repr(cb.kwargs))
        
    def __len__(cb):
        return len(cb.sampling_plan)
        
        
    def __call__(cb, *args, **kwargs):
        # Houston, we've got a problem...
        # call meaning is different for underlaying f_models and upper Boxes
        # but SampleBox expect f_model under
        
        # hovnokód, překopat
        f = cb.sampling_plan(*args, **kwargs)
        if len(f) == 0:
            return CandyBox(f)
        else:
            return f
        
        
    
        
    def __getitem__(cb, slice):
        # if pandas
        if 'df' in cb.__dict__:
            df = cb.df.iloc[slice]
            #☺ нельзя так просто взять и накраить DataFrame
            # pandas zlobí (o kousek víc jak numpy)
            if not isinstance(df, pd.DataFrame):
                # pravděpodobně když se nám vrátí serie, tak bude interpretována jako sloup
                # fakt mi nic spolehlivějšího nenapadá
                df = pd.DataFrame(df).T
                
            # chcem jednoduché numpy-like chovaní
            # dělá problémy
            df.reset_index(drop=True, inplace=True)
            return CandyBox(cb.sampling_plan[slice], df=df)
        # if not
        else:
            sliced_dict = dict()
            for key in cb.kwargs:
                ##č nechám na uživateli, co vloží do slovníku a jak to bude slajsiť
                #č sice furt podporuju variantu s těmi slovníky
                #č ale potrebuju aby chování bylo trochu víc předvidatelné
                sliced_dict[key] = np.atleast_1d(cb.kwargs[key][slice])
            return CandyBox(cb.sampling_plan[slice], **sliced_dict)
        
    def __setattr__(cb, key, value):
        # to je vše co má samotný CandyBox
        # žádný další majetek u něho nepozoruji
        if key in ('sampling_plan', 'df', 'kwargs'):
            cb.__dict__[key] = value
        elif len(cb) == len(value):
            # if pandas
            if 'df' in cb.__dict__:
                # df je na svědomi pandas
                cb.df.loc[:, key] = value
            # if not
            else:
                cb.kwargs[key] = value
        else:
            raise ValueError("Sample and given values hasn't the same length. Zkrátka, do sebe nepatří")
        
        
    def __getattr__(cb, attr):
        # branime sa rekurzii
        # defend against recursion
        if attr == 'sampling_plan':
            raise AttributeError
            
        elif attr == 'candybox':
            return cb
            
        # hledáme obraceně
        # nejdřív se zeptame f_model,
        # teprve když ten nič nemá  
        # mrkneme atribut u sebe
        try:
            return getattr(cb.sampling_plan, attr)
        except AttributeError:
            return cb._lookup(attr)
            
    def _lookup(cb, attr):
        # if pandas
        if 'df' in cb.__dict__:
            if attr in cb.df:
                # zkusím převést na numpy, protože 
                # Pandasovy indexy jen zlobí
                # a stejně nikdo je nepouživá a na ně nespolehá
                # další kód by neměl furt řešit, co ta bombonjera má uvnitř
                # i když je to škoda, že nepujde měnit jednotlivé hodnoty
                try:
                    return cb.df[attr].to_numpy()
                except AttributeError:
                    return np.array(cb.df[attr])
                
                # zkusím nepřevadět na numpy, protože chcu mäť možnost hodnoty měnit
                # pri slajsech resetuju indexy, takže musí to být v pohodě
                # doufám, že tím нищего не поломаju
                # šecko se tím zkazilo a je taky otázkou 
                # zda je to vhodně když se furt robej slajsy
                # nechám to na uživatelském kódu
                #return cb.df[attr]
            else: # implicitně pandas hodí KeyError, kterej nechcem
                raise AttributeError
        
        # if not
        elif attr in cb.kwargs:
            value = cb.kwargs[attr]
            if len(cb)==len(value):
                return cb.kwargs[attr]
            else:
                # у нас есть дата, но мы их вам недадим)
                # zde nechť bude KeyError
                raise KeyError("CandyBox: well, we have some data, but they are not consistent, so we haven't")
                
        else: # implicitně slovníky (stejně jako pandas) hazej KeyError, kterej nechcem
            raise AttributeError
            
        
        
    def add_sample(cb, input):
        """
        hlavní požadavek - jsou-li samply uspěšně sjednoceny,
        tak ty blbé zbytky nesmejí mi hodit chybu!
        котлеты - отдельно, мухи - отдельно
        """
        
        # čo to je za vstup?
        sweety_input = hasattr(input, 'sampling_plan')
            
        #
        # котлеты
        #
        # nechcu zde try-catch blok
        if sweety_input:
            cb.sampling_plan.add_sample(input.sampling_plan)
        else:
            cb.sampling_plan.add_sample(input)
        
        
        # мухи
        if sweety_input:
            # if pandas
            if 'df' in cb.__dict__:
                #if 'df' in input.__dict__: # jen pro formu kontrola
                # pandas musí mít i tamtenhle objekt, žejo?
                cb.df = cb.df.append(input.df, ignore_index=True)
            # if not
            else:
                # zjednodušený join
                sample_len = len(cb.sampling_plan)
                for key in cb.kwargs:
                    # ani nebudu kontrolovat
                    #if isinstance(key, np.ndarray):
                        
                    if key in input.kwargs:
                        cb.kwargs[key] = np.append(cb.kwargs[key], input.kwargs[key])
                    else:
                        fill_len = sample_len - len(cb.kwargs[key])
                        full = (None for __ in range(fill_len))
                        cb.kwargs[key] = np.append(cb.kwargs[key], (*full,))
                
                
        else: # nesladký vstup
            sample_len = len(cb.sampling_plan)
            # if pandas
            if 'df' in cb.__dict__:
                fill_len = sample_len - len(cb.df)
                full_df = pd.DataFrame(index=range(fill_len))
                cb.df = cb.df.append(full_df, ignore_index=True)
            # if not
            else:
                for key in cb.kwargs:
                    fill_len = sample_len - len(cb.kwargs[key])
                    full = (None for __ in range(fill_len))
                    cb.kwargs[key] = np.append(cb.kwargs[key], (*full,))

                
    #E we'll see, if .new_sample will be needed
    #E year, we need it
    #♥ мыным выль сэмпл кулэ!
    def new_sample(cb, input=None, space='R'):
        # už je to stavá matoucím
        # pokud input je, děláme tohle
        # vrácíme samy sobě
        if input is None:
            return CandyBox(cb.sampling_plan())
            
        # pokud input není, děláme vonohle
        # konvertujem vstup na naše rozdělení
        else:
            # čo to je za vstup?
            if hasattr(input, 'sampling_plan'): #sweety_input:
                # if pandas
                if hasattr(input, 'df'):
                    return CandyBox(cb.sampling_plan.new_sample(input.sampling_plan, space=space), df=input.df)
                    
                # if there is no pandas DataFrame
                # we suppose there is dictionary in input.kwargs
                else:
                    return CandyBox(cb.sampling_plan.new_sample(input.sampling_plan, space=space), **input.kwargs)
                
            # nesladký vstup
            else:
                return cb.sampling_plan.new_sample(input, space)
        
        
        
            
            
        
    def consistency_check(cb):
        # řvat na celé město nebudeme
        # if pandas
        if 'df' in cb.__dict__:
            return len(cb.sampling_plan)==len(cb.df)
        # if not
        else:
            sample_len = len(cb.sampling_plan)
            return all(sample_len == len(cb.kwargs[key]) for key in cb.kwargs)
