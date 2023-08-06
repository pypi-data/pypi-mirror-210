#!/usr/bin/env python
# coding: utf-8


#č nazvy proměnných jsou v angličtině
#č Ale komenty teda ne)

#č otázkou je, kdo je uživatelem modulu.
#č zatím ho potřebujou jenom vnejší skripty, 
#č které dostávájí data z csv souborů a žádné skřiňky nevytvařejí.
#č Proto funkce v tomto modulu zatím-prozátím nebudou spolehát na
#č ax.sample_box

from scipy import stats # for tri_beta_plot

#č sehnaní datarámu necháme uživateli
def tri_estimation_fill(ax, df):
    #xkcd_green = (167, 255, 181) # xkcd:light seafoam green #a7ffb5
    green = "#A7FFB5"
    #xkcd_red   = (253, 193, 197) # xkcd: pale rose (#fdc1c5)
    red   = "#FDC1C5"
    #xkcd_cream = (255, 243, 154) # let's try xkcd: dark cream (#fff39a)
    cream = "#FFF39A"
    grey = "#DDDDDD"
    
    o = df['outside'].to_numpy()
    s = df['success'].to_numpy()
    f = df['failure'].to_numpy()
    m = df['mix'].to_numpy()
    kwargs = {'colors': (red, cream, grey, green),
            'labels': ("failure domain", "mixed domain",\
             "outside domain", "success domain")}
    if len(df.index) > 1000:
        kwargs['rasterized'] = True
    return ax.stackplot(df.index, f, m, o, s, **kwargs)


#č sehnaní datarámu necháme uživateli
#
#č musím trochu davat bacha,
#č externí skripta df-ko vytvařejí sámi jak chcou
#č proto se nemá obecně spolehat na korektní index
def shell_estimation_fill(ax, df, use_df_index=False):
    if use_df_index:
        x = df.index
    else:
        x = df['nsim'].to_numpy()
    
    shell_color = "#ECCEAF"  #"#FFFD95"
    outer_color = "#CCCCCC"
    colors = (outer_color, shell_color)
    outer = df['outer'].to_numpy()
    shell = outer + df['shell'].to_numpy()
    labels = ("outer", "annulus")
    return ax.stackplot(x, outer, shell, labels=labels, colors=colors)


#č sehnaní datarámu necháme uživateli
# inverted
def trii_estimation_fill(ax, df):
    #xkcd_green = (167, 255, 181) # xkcd:light seafoam green #a7ffb5
    green = "#A7FFB5"
    #xkcd_red   = (253, 193, 197) # xkcd: pale rose (#fdc1c5)
    red   = "#FDC1C5"
    #xkcd_cream = (255, 243, 154) # let's try xkcd: dark cream (#fff39a)
    cream = "#FFF39A"
    grey = "#DDDDDD"
    colors = (grey, red, cream, green)
    o = df['outside'].to_numpy()
    s = df['success'].to_numpy()
    f = df['failure'].to_numpy()
    m = df['mix'].to_numpy()
    labels = ("out of sampling domain estimation", "failure domain estimation",\
             "mixed simplices measure", "success domain estimation")
    return ax.stackplot(df.index, o, f, m, s, labels=labels, colors=colors)


#č ok, tak uděláme všecko dohromady
#č datarám, jako vždy, uživatel donese svůj vlastní
def tri_estimation_plot(ax, df, pf_exact=None, pf_exact_method="$p_f$",
                         plot_outside=True, plot_mix=True, **kwargs):
    # some default values
#    if not ax.get_xlabel():
#        ax.set_xlabel('Number of simulations')
#    if not ax.get_ylabel():
#        ax.set_ylabel('Probability measure')
        
    # fill
    tri_estimation_fill(ax, df)
    
    #č blbost, ale uspořadal jsem tu prvky tak,
    #č aby se hezky kreslily v legendě
    
    if (len(df.index) > 1000) and ('rasterize' not in kwargs):
        kwargs['rasterized'] = True
    
    lw = kwargs.pop('lw', kwargs.pop('linewidth', 1.5))
    
    try:
        v = df['vertex_estimation'].to_numpy()
        #vr = df['vertex_ratio_estimation'].to_numpy()
        #wr = df['weighted_ratio_estimation'].to_numpy()
        #ax.plot(df.index, vr, '-m', label="$p_f$ vertex ratio estimation", zorder=10500, lw=lw/2, **kwargs)
        #ax.plot(df.index, wr, '-', label="$p_f$ wegthed ratio estimation", color='darkmagenta', zorder=10500, lw=lw/2, **kwargs)
        ax.plot(df.index, v, '-r', label="simple $p_f$ estimation", zorder=100500, lw=lw, **kwargs)
    except:
        pass
#        v = df['vertex_estimation'].to_numpy()
#        wv = df['weighted_vertex_estimation'].to_numpy()
#        ax.plot(df.index, wv, '-r', label="weighted $p_f$ estimation", zorder=100500, **kwargs)
#        ax.plot(df.index, v, '-m', label="simple $p_f$ estimation", zorder=10500, **kwargs)
    
    
    #č teď čáry
    if plot_outside:
        o = df['outside'].to_numpy()
        ax.plot(df.index, o, '-', color="#AAAAAA", \
                label="outside domain estimation", zorder=150, **kwargs)
                
    if plot_mix:
        m = df['mix'].to_numpy()
        ax.plot(df.index, m, '-', color="#FF8000", \
                label="mixed domain estimation", zorder=1050, **kwargs)
    
    if pf_exact is not None:
        ax.axhline(pf_exact, c='b', label=pf_exact_method, **kwargs)
    

#č ok, tak uděláme všecko dohromady
#č datarám, jako vždy, uživatel donese svůj vlastní
def tri_beta_plot(ax, df, pf_exact=None, pf_exact_method="$p_f$",
                         plot_outside=True, plot_mix=True, **kwargs):
    
    #č blbost, ale uspořadal jsem tu prvky tak,
    #č aby se hezky kreslily v legendě
    
    v = -stats.norm.ppf(df['vertex_estimation'].to_numpy())
    #wv = -stats.norm.ppf(df['weighted_vertex_estimation'].to_numpy())
    #ax.plot(df.index, wv, '-r', label="weighted $p_f$ estimation", zorder=100500, **kwargs)
    ax.plot(df.index, v, '-r', label="vertex $p_f$ estimation", zorder=10500, **kwargs)
    
    
    #č teď čáry
    if plot_outside:
        o = -stats.norm.ppf(df['outside'].to_numpy())
        ax.plot(df.index, o, '-', color="#AAAAAA", \
                label="outside domain estimation", zorder=150, **kwargs)
                
    if plot_mix:
        m = -stats.norm.ppf(df['mix'].to_numpy())
        ax.plot(df.index, m, '-', color="#FF8000", \
                label="mixed domain estimation", zorder=1050, **kwargs)
    
    if pf_exact is not None:
        ax.axhline(-stats.norm.ppf(pf_exact), c='b', label=pf_exact_method, **kwargs)

    

#č ok, tak uděláme všecko dohromady
#č datarám, jako vždy, uživatel donese svůj vlastní
def shell_estimation_plot(ax, df, use_df_index=False, **kwargs):
    
    # fill
    shell_estimation_fill(ax, df, use_df_index)
    
    #č teď čáry
    if use_df_index:
        x = df.index
    else:
        x = df['nsim'].to_numpy()
    
    #č je to ten opravdový outside z tri plot 
    #č ponecháme i jeho původní barvu
    o = df['outside'].to_numpy()
    ax.plot(x, o, '-', color="#AAAAAA", \
            label="outside estimation", **kwargs)
    
    y = df['FORM_outside'].to_numpy()
    ax.plot(x, y, '-', color="tab:purple", \
            label="hyperplane outside approximation", **kwargs)
    
    y = df['2FORM_outside'].to_numpy()
    ax.plot(x, y, '-', color="tab:pink", \
            label="two hyperplanes outside approximation", **kwargs)
    
    y = df['orth_outside'].to_numpy()
    ax.plot(x, y, '-', color="tab:brown", \
            label="hypercube outside approximation", **kwargs)


#č ok, tak uděláme všecko dohromady
#č datarám, jako vždy, uživatel donese svůj vlastní
def trii_estimation_plot(ax, df, pf_exact=None, pf_exact_method="$p_f$"):
    # some default values
#    if not ax.get_xlabel():
#        ax.set_xlabel('Number of simulations')
#    if not ax.get_ylabel():
#        ax.set_ylabel('Probability measure')
    # fill
    trii_estimation_fill(ax, df)
    
    #č teď čáry
    v = df['vertex_estimation'].to_numpy()
    wv = df['weighted_vertex_estimation'].to_numpy()
    # v trii grafu máme outside zdolu
    mask = v > 0
    o = df['outside'].to_numpy()[mask]
    vo = v[mask] + o
    wvo = wv[mask] + o
    ax.plot(df.index[mask], vo, '-m', label="simple $p_f$ estimation")
    ax.plot(df.index[mask], wvo, '-r', label="weighted $p_f$ estimation")
    
    if pf_exact is not None:
        ax.axhline(pf_exact, c='b', label=pf_exact_method)
    
    
        
##xkcd_green = (167, 255, 181) # xkcd:light seafoam green #a7ffb5
#green = (0, 255, 38, 96) 
##xkcd_red   = (253, 193, 197) # xkcd: pale rose (#fdc1c5)
#red   = (253, 0, 17, 96)
##xkcd_cream = (255, 243, 154) # let's try xkcd: dark cream (#fff39a)
#cream = (255, 221, 0, 96)
#grey = (196, 196, 196, 96)
        
class SimplexErrorGraph:
        
            
    def show_labels(self):
        self.setLabel('left', "Failure probability estimation error")
        self.setLabel('bottom', "Number of simulations")
        
    
    def setup(self, *args, **kwargs):
        
        #xkcd_red   = (253, 193, 197) # xkcd: pale rose (#fdc1c5)
        #red   = (253, 0, 17, 96)
        
        #self.pen_f = self.plot(x, y, brush=red)#, name="failure domain estimation")
        #self.pen_f.setZValue(-100)
        
        
        pen = pg.mkPen(color='m', width=2)
        self.pen_vertex = self.plot(x, y, pen=pen, name="simple pf estimation")
        pen = pg.mkPen(color='r', width=2) #(118, 187, 255)
        self.pen_weighted_vertex = self.plot(x, y, pen=pen, name="weighted pf estimation")
        
        
    
    #č když se někde objeví nula se zapnutým LogModem - 
    #č qtpygraph hned spadne a není možne ten pad zachytit
    def zerosafe(self, x, y, fallback_y=None): 
        x = np.array(x)
        y = np.array(y)
        if fallback_y is None:
            fallback_y = y
        y = np.where(y > 0, y, fallback_y)
        mask = y > 0
        return x[mask], y[mask]
        
    
    def redraw(self):
        #č neotravujme uživatele chybovejma hlaškama
        if hasattr(self.simplex_data.dice_box, 'pf_exact'):
            try: #ё тут всё что угодно может пойти не так
                pf_exact = self.simplex_data.dice_box.pf_exact
                
                df = self.simplex_data.df
                #č zapíšeme do data rámu, snad nikomu nebude vadit
                df['vertex_estimation_error'] = df['vertex_estimation'] - pf_exact
                df['weighted_vertex_estimation_error'] = df['weighted_vertex_estimation'] - pf_exact
                
                v = df['vertex_estimation_error'].abs()
                wv = df['weighted_vertex_estimation_error'].abs()
                
                x, y = self.zerosafe(v.index, v.to_numpy())
                self.pen_vertex.setData(x, y)
                
                x, y = self.zerosafe(wv.index, wv.to_numpy())
                self.pen_weighted_vertex.setData(x, y)
            
                
            except BaseException as e:
                print(self.__class__.__name__ + ":", repr(e))


