#!/usr/bin/env python
# coding: utf-8

# Axes level functions (for Matplotlib)

#č Založme nový modul pro funkce (procedury),
#č které sice stejně jako mart pracují na urovni axes,
#č ale na rozdil od atomických funkcí mart modulu
#č udělaj z prazdných os hotový obrazek.
#č mplot.show2D() může použivat tuhle nabídku obrázků.
#
#č funkce v tomto modulu dostávájí jako parameter jedině ax
#č ax ale má nastavené atributy .space a .sample_box

import numpy as np
from . import mart
from . import mgraph

from matplotlib import colors as mcolors
from matplotlib import ticker
from matplotlib import patches as mpatches
from matplotlib import lines as mlines


# it is mostly for qt_plot, it offers availiable options to user
__all__ =   [
            'tri_vector_plot',
            'GRaph',
            'rbf_plot', 'rbf_density_plot', 'rbf_diagram',
            'candidates_plot', 'rejection_sampling_plot', 
            'candidates_sampling_plot',
            'convex_hull_plot', 'tri_plot', 'tri_nodes_plot',
            'tri_R_plot', 'tri_GK_plot', 'tri_G_plot',
            'tri_R_nodes_plot', 'tri_GK_nodes_plot',
            'convergence_diagram', 'convergence_legend', 
            'convergence_square', 'beta_diagram',
            'just_points', 'just_points_really',
            'base_drawing', 'candidates_drawing',
            'just_qhull', 'qhull_plot', 'qhull_infinite',
            'dhull_scheme_plot', 'dhull_random_plot',
            'bhull_plot', 'bhull_infinite',
            'shull_plot',
            'completehull_plot'
            ]

#č ten [plot] zásadně vytvaří své struktury, nepouzívá oné ze skříňky,
#č protože já vím, že v těch obrázcích, ve kterých chcu ho použit,
#č můde být třeba použit řez a skříňka tedy potřebné struktury může nemít
def tri_vector_plot(ax, tri_space=None, linewidths=[0.7, 0.5, 0.4, 0.3, 0.2, 0.1], 
                ms=3, mew=0.6, lw=0.7, data_offset=1, nrid=200):
    from .. import simplex as six
    if tri_space is None:
        tri_space = ax.space
        
    import quadpy
    tn_scheme = quadpy.tn.stroud_tn_3_6b(2)
            
    Tri = six.GaussCubatureIntegration(ax.sample_box, tn_scheme, incremental=False)
    Tri.get_pf_estimation()
    ax.sample_box.Tri = Tri
    mart.setup(ax)
    if tri_space == ax.space:
        #mart.triplot(ax, color="#B2B2B2", lw=lw/1.4, zorder=100)
        s = (1, 1, 1, 0) #'xkcd:light seafoam green' #a7ffb5
        f = '#fdc1c500' #(253/255, 193/255, 197/255, 1) # '#fdc1c5' #'xkcd: pale rose' # (#fdc1c5)
        m = '#FFF39A00'#(255/255, 243/255, 154/255, 1)#'#FFF39A' #'xkcd: dark cream' # (255, 243, 154, 255)
        sfm_colors = [s, f, m]
        mart.tripcolor(ax, sfm_colors=sfm_colors, color="#B2B2B200", 
                                    linewidth=lw/1.4/2, zorder=100)
    else:
        mart.tri_plot(ax, Tri=Tri, color="#B2B2B2", lw=lw/1.4, zorder=100, rasterized=True)
    
    mart.simplex_vectors(ax, color='grey', zorder=10500)#, scale_units='height', scale=0.0025) #width=0.003,
    
    mart.plot_points(ax, ms=ms, mew=mew, zorder=100500)
    #č curly a boundaries raději nakreslíme co nejpozději
    mart.curly(ax, nrid=nrid, linewidths=linewidths)
    try:
        mart.plot_boundaries(ax, lw=lw, zorder=1050, nrod=nrid)
    except:
        pass
    min_coord = np.abs(np.min(getattr(ax.sample_box, ax.space)))
    mart.setup_labels(ax, data_offset=data_offset * min_coord)



def GRaph(ax, df=None, ls='', **kwargs):
    from .. import sball
    ax.margins(0)
    #ax.yaxis.set_ticks_position('right')
    #ax.yaxis.set_label_position('right')
    ax.set_xlabel(r"Limit-state evaluations, $N_{\mathrm{sim}}$")
    ax.set_ylabel(r"$\rho$")
    
    s_ball = sball.Sball(ax.sample_box.nvar)
    
    
    secax = ax.secondary_yaxis(1, functions=(s_ball.sf, s_ball.isf))
    secax.set_ylabel(r"$S_{\chi} (\rho; N_{\mathrm{var}})$")
    secax.yaxis.set_major_locator(ticker.LogLocator())
    secax.yaxis.set_major_formatter(ticker.LogFormatterMathtext())

    lengths = np.sum(np.square(ax.sample_box.G), axis=1)
    lengths = np.sqrt(lengths, out=lengths) #lengths of each radius-vector
    
    x = np.arange(len(lengths)) + 1
    y = lengths
    
    failsi = ax.sample_box.failsi
    
    try: # proxy denotes to implicitly-known values
        proxy = ax.sample_box.proxy.astype(bool) 
    except AttributeError:
        proxy = np.full(len(lengths), False, dtype=bool)
    
    
    #č byl jsem svědkem, že matplotlib zlobil ve 3D 
    #č kvůli tomu, že nebyl žádný safe vzorek
    #č proto raději budu přidávat tečky podmíněne
    mask = np.all((~failsi, ~proxy), axis=0)
    if np.any(mask): #success
        ax.plot(x[mask], y[mask], mec='g', mfc='g', marker='P', ls=ls, **kwargs)
    
    mask = np.all((failsi, ~proxy), axis=0)
    if np.any(mask): #failures
        ax.plot(x[mask], y[mask], mec='r', mfc='r', marker='X', ls=ls, **kwargs)
    
    mask = np.all((~failsi, proxy), axis=0)
    if np.any(mask): #proxy_successes
        ax.plot(x[mask], y[mask], 
                mec='#77AC30', mfc=(0,0,0,0), marker='h', ls=ls, **kwargs)
    
    mask = np.all((failsi, proxy), axis=0)
    if np.any(mask): #proxy_failures
        ax.plot(x[mask], y[mask], 
                mec='#D95319', mfc=(0,0,0,0), marker='H', ls=ls, **kwargs)
                
    
    if np.any(failsi): 
        ax.axhline(np.min(y[failsi]), c='r', zorder=-1, **kwargs)
    
    if df is None:
        try:
            import pandas as pd
            df = pd.DataFrame(ax.sample_box.box_estimations)
            df.index = df.nsim.to_numpy()
        except BaseException as e:
            print(repr(e))
            return 
        
    x = df.nsim.to_numpy()
    r = df.r.to_numpy()
    R = df.R.to_numpy()
    ax.fill_between(x, r, y2=R, color='#C3C3C3', step='post', zorder=-20)
    
    if 'r_safe' in df:
        y = df['r_safe'].to_numpy()
        y2 = df['R_safe'].to_numpy()
        mask = y >= 0
            
        ax.fill_between(x[mask], y[mask], y2[mask], color='#A7FFB5', step='post', zorder=-100)
    
    if 'r_failure' in df:
        y = df['r_failure'].to_numpy()
        y2 = df['R_failure'].to_numpy()
        mask = y >= 0
        
        ax.fill_between(x[mask], y[mask], y2[mask], color='#FDC1C5', step='post', zorder=-50)
        
    if 'r_mixed' in df:
        y = df['r_mixed'].to_numpy()
        y2 = df['R_mixed'].to_numpy()
        mask = y >= 0
            
        ax.fill_between(x[mask], y[mask], y2[mask], color='#FFF39A', step='post', zorder=-30)
    
    
    
    if 'r_exact' in dir(ax.sample_box): 
        ax.axhline(ax.sample_box.r_exact, c='b', zorder=-2, **kwargs)
    
    
    ax.set_facecolor('#E1E1E1')
    
    
    
    


def rbf_diagram(ax):
    from .. import misc as wmisc
    rbf_stm = []
    x = list(range(2, ax.sample_box.nsim))
    for i in x:
        rbf = wmisc.RBF_surrogate(ax.sample_box[:i])
        rbf_stm.append(rbf.get_pf_estimation(2000000))
        print(i, repr(np.array(rbf_stm)))
    
    
    ax.plot(np.array(x), np.array(rbf_stm))
    
    

def rbf_plot(ax, nrid=500):
    tri_plot(ax)
    x_bound = ax.get_xbound()
    y_bound = ax.get_ybound()
    mart.rbf_colormesh(ax, nrid)
    ax.set_xbound(x_bound)
    ax.set_ybound(y_bound)

def rbf_density_plot(ax, nrid=500):
    tri_plot(ax)
    x_bound = ax.get_xbound()
    y_bound = ax.get_ybound()
    mart.rbf_density_colormesh(ax, nrid)
    ax.set_xbound(x_bound)
    ax.set_ybound(y_bound)

def rejection_sampling_plot(ax, linewidths=[0.7, 0.5, 0.4, 0.3, 0.2, 0.1]):
    from .. import simplex as six
    
    #č možná zrovna zde nebudem robiť vědu a použijme tringulaciju ze skříňky?
    nodes = ax.sample_box.f_model(1000)
    # -1 = 'out', 0=success, 1=failure, 2=mix
    event_ids = six.filter(ax.sample_box.Tri, nodes)
    mart.plot_sample(ax, nodes[event_ids==-1], ls='', marker='.',\
                         mec="#00007E", mfc="#00007E", ms=1.5, alpha=0.5,\
                         rasterized=True)
    mart.plot_sample(ax, nodes[event_ids==2], ls='', marker='.',\
                         mec="#00007E", mfc="#00007E", ms=1.5, alpha=0.5,\
                         rasterized=True)
    
    mart.setup(ax)
    mart.curly(ax, linewidths=linewidths)
    mart.triplot(ax, color="#B2B2B2", lw=0.5, zorder=1000)
    mart.plot_points(ax, ms=5, zorder=100500)
    try:
        mart.plot_boundaries(ax, lw=0.7, zorder=10500)
    except:
        pass
    ax.xaxis.set_major_formatter(ticker.NullFormatter())
    ax.yaxis.set_major_formatter(ticker.NullFormatter())
    ax.xaxis.set_major_locator(ticker.NullLocator())
    ax.yaxis.set_major_locator(ticker.NullLocator())


def candidates_sampling_plot(ax, linewidths=[0.7, 0.5, 0.4, 0.3, 0.2, 0.1]):
    from .. import simplex as six
    from .. import estimation as stm
    
    def _stm_draw_nodes(*args, **kwargs):
        #č v tomto plot bude šilený bordel v tom, kdo kolbek spouští
        #č a kdo mu co tam posílá. Na event a na nodes spolehat ale můžeme
        #
        # callback's signature: sx, indices=, simplex=, nodes=, cell_stats=
        # positional "sx" is Tri object itself
        # "indices" are numbers of simplex vertices
        # "simplex" are vertices itself
        # "nodes" is what we really want to draw
        
        event = kwargs['cell_stats']['event']
        
        if event in ('mix', 'outside'):
            mart.plot_sample(ax, kwargs['nodes'], ls='', marker='.',\
                         mec="#00007E", mfc="#00007E", ms=1.5, alpha=0.5,\
                         rasterized=True)
        
    data = stm.fast_simplex_estimation(ax.sample_box, model_space=ax.space,\
                                  sampling_space=ax.space, \
                                   weighting_space=ax.space,\
                                    outside_budget=1000, \
                                     simplex_budget=100,\
                                    callback=_stm_draw_nodes, design=None)    
    
    mart.setup(ax)
    mart.curly(ax, linewidths=linewidths)
    mart.triplot(ax, color="#B2B2B2", lw=0.5, zorder=1000)
    mart.plot_points(ax, ms=5, zorder=100500)
    try:
        mart.plot_boundaries(ax, lw=0.7, zorder=10500)
    except:
        pass
    ax.xaxis.set_major_formatter(ticker.NullFormatter())
    ax.yaxis.set_major_formatter(ticker.NullFormatter())
    ax.xaxis.set_major_locator(ticker.NullLocator())
    ax.yaxis.set_major_locator(ticker.NullLocator())

def candidates_plot(ax):
    tri_plot(ax, tri_space=None, linewidths=[0.7, 0.5, 0.4, 0.3], data_offset=0.4)
    blue_colors = ["#BDBDFF", "#9999FF", "#00007E", "#000057"]
    blue_cmap = mcolors.LinearSegmentedColormap.from_list("bluecmap", blue_colors)
    mart.scatter_candidates(ax, s=1.5, marker='.', cmap=blue_cmap, rasterized=True)
    mart.plot_the_best_candidate(ax, "^", color='#000057')
    mart.plot_points(ax, ms=5, zorder=1005000)
    
#    if ax.space in ('G', 'GK'):
#        ax.xaxis.set_label_coords(1, 0.47)
#        ax.set_xlabel("$x_1$")
#        ax.text(0.47, 1, '$x_2$', ha='right',va='top', transform=ax.transAxes)
#    else:
#        ax.set_xlabel("$x_1$")
#        ax.set_ylabel("$x_2$")

def convergence_square(ax):
    convergence_diagram(ax)
    ax.set_box_aspect(1)
    ax.secondary_yaxis('right')

def convergence_diagram(ax):
    #č pokorně jedeme použiť guessbox
    #č nic jiného nebylo pořádně implementováno
    #from .. import stm_df 
    #df = stm_df.get_tri_data_frame(ax.sample_box, sources, apply_proxy)
    import pandas as pd
    df = pd.DataFrame(ax.sample_box.box_estimations)
    df.index = df.nsim.to_numpy()
    try:
        pf_exact = ax.sample_box.pf_exact
        pf_exact_method = ax.sample_box.pf_exact_method
        mgraph.tri_estimation_plot(ax, df, pf_exact=pf_exact, \
                            pf_exact_method=pf_exact_method, plot_outside=True)
    except:
        mgraph.tri_estimation_plot(ax, df, plot_outside=True)
    ax.margins(0)
    ax.set_yscale('log')
    ax.set_xlabel(r"Limit-state evaluations, $N_{\mathrm{sim}}$")
    #ax.set_xlabel("Number of points")
    ax.set_ylabel("Probability measure")


def beta_diagram(ax, df=None):
    if df is None:
        try:
            import pandas as pd
            df = pd.DataFrame(ax.sample_box.box_estimations)
            df.index = df.nsim.to_numpy()
        except BaseException as e:
            print(repr(e))
            return 
    try:
        pf_exact = ax.sample_box.pf_exact
        pf_exact_method = ax.sample_box.pf_exact_method
        mgraph.tri_beta_plot(ax, df, pf_exact=pf_exact, \
                            pf_exact_method=pf_exact_method, plot_outside=True)
    except:
        mgraph.tri_beta_plot(ax, df, plot_outside=True)
    ax.margins(0)
    ax.set_xlabel(r"Limit-state evaluations, $N_{\mathrm{sim}}$")
    #ax.set_xlabel("Number of points")
    ax.set_ylabel(r"Reliability index, $\beta$")

    
def convergence_legend(ax):
    convergence_diagram(ax)
    
    #č nejsem jist, jestli by šlo přehodit pořadí u stackplotu
    #č proto vytvařením legendy už neotravujeme mgraph
    #č ale sámi tu něco nahodíme
    proxy_handles = list()
    proxy_handles.append(mpatches.Patch(color='#A7FFB5', label=r"$\pazocal{S}^{\left(N_{\mathrm{sim}}\right)}$"))
    proxy_handles.append(mpatches.Patch(color='#DDDDDD', label=r"$\pazocal{O}^{\left(N_{\mathrm{sim}}\right)}$"))
    proxy_handles.append(mpatches.Patch(color='#FFF39A', label=r"$\pazocal{M}^{\left(N_{\mathrm{sim}}\right)}$"))
    proxy_handles.append(mpatches.Patch(color='#FDC1C5', label=r"$\pazocal{F}^{\left(N_{\mathrm{sim}}\right)}$"))
    
    proxy_handles.append(mlines.Line2D([], [], color='b', label=r'$p_{\pazocal{F}}$'))
    #proxy_handles.append(mlines.Line2D([], [], color='m', label=r"$p_{\mathrm{f,v}}^{\left(N_{\mathrm{sim}}\right)}$"))
    proxy_handles.append(mlines.Line2D([], [], color='r', label=r"$p_{\mathrm{f,v}}^{\left(N_{\mathrm{sim}}\right)}$"))
    proxy_handles.append(mlines.Line2D([], [], color='#AAAAAA', \
                label=r"$p_{\pazocal{O}}^{\left(N_{\mathrm{sim}}\right)}$"))
    
    ax.set_xlabel(r"Number of $g\left( \bm{x} \right)$ evaluations, $N_{\mathrm{sim}}$")
    #ax.set_box_aspect(0.5)
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', handles=proxy_handles, frameon=True, borderaxespad=0,
                handlelength=1, handletextpad = 0.6)
    #             frameon=True)#, mode="expand")
    #ax.legend(bbox_to_anchor=(0.5, -0.25), ncol=2, loc='upper center', handles=proxy_handles)


#č ten [plot] zásadně vytvaří své struktury, nepouzívá oné ze skříňky,
#č protože já vím, že v těch obrázcích, ve kterých chcu ho použit,
#č můde být třeba použit řez a skříňka tedy potřebné struktury může nemít
def tri_nodes_plot(ax, tri_space=None, tn_scheme=None, ms=3, mew=0.6, lw=0.7,
                     linewidths=[0.7, 0.5, 0.4, 0.3, 0.2, 0.1], nrid=200,
                     data_offset=1):
    from .. import simplex as six
    if tri_space is None:
        tri_space = ax.space
    
    #č já tuhle funkciju potřebuju ne abych kreslil bodíky ve vrcholech
    if tn_scheme is None:
        try:
            tn_scheme = ax.sample_box.Tri.tn_scheme
        except:
            import quadpy
            tn_scheme = quadpy.tn.grundmann_moeller(ax.sample_box.nvar, 5)
            
    
    def _draw_nodes(*args, **kwargs):
        # callback's signature: sx, indices=, simplex=, nodes=, cell_stats=
        # positional "sx" is Tri object itself
        # "indices" are numbers of simplex vertices
        # "simplex" are vertices itself
        # "nodes" is what we really want to draw
        
        event = kwargs['cell_stats']['event']
        
        if event == 'mix':
            color = '#FFF39A' #'xkcd: dark cream' # (255, 243, 154, 255)
        elif event == 'failure':
            color = '#fdc1c5' #'xkcd: pale rose' # (#fdc1c5)
        elif event == 'success':
            color = '#a7ffb5' #'xkcd:light seafoam green' #a7ffb5
        else:
            assert 100500 < 0 #оӵ мар лэсьтӥське татын?
            
        mart.plot_sample(ax, kwargs['nodes'], ls='', marker='.',\
                         mew=0, mfc=color, ms=2, alpha=0.5, rasterized=True)
        
        
        
    
    #č vytvařím vlastní tringulaciju zde vécemeně kvůli callbackům
    #č jde, samozřejmě všecko udělat jínak, 
    #č ale nechcu zrovna zde z toho robiť vědu
    Tri = six.JustCubatureTriangulation(ax.sample_box, tn_scheme=tn_scheme, \
                                    tri_space=tri_space, issi=None,\
                                    weighting_space=None, \
                                    incremental=False,\
                                    on_add_simplex=_draw_nodes,\
                                    on_delete_simplex=None)
    
    mart.setup(ax)
    Tri.integrate()
    if tri_space == ax.space:
        mart.triplot(ax, color="#B2B2B2", lw=lw/1.4, zorder=100)
    else:
        mart.tri_plot(ax, Tri=Tri, color="#B2B2B2", lw=lw/1.4, zorder=100, rasterized=True)
    
    mart.plot_points(ax, ms=ms, mew=mew, zorder=100500)
    #č curly a boundaries raději nakreslíme co nejpozději
    mart.curly(ax, nrid=nrid, linewidths=linewidths)
    try:
        mart.plot_boundaries(ax, lw=lw, zorder=1050, nrod=nrid)
    except:
        pass
    min_coord = np.abs(np.min(getattr(ax.sample_box, ax.space)))
    mart.setup_labels(ax, data_offset=data_offset * min_coord)

def tri_R_nodes_plot(ax, **kwargs):
    tri_nodes_plot(ax, tri_space='R', **kwargs)
    
def tri_G_plot(ax, **kwargs):
    tri_plot(ax, tri_space='G', **kwargs)
    
def tri_GK_nodes_plot(ax, **kwargs):
    tri_nodes_plot(ax, tri_space='GK', **kwargs)


#č ten [plot] zásadně vytvaří své struktury, nepouzívá oné ze skříňky,
#č protože já vím, že v těch obrázcích, ve kterých chcu ho použit,
#č můde být třeba použit řez a skříňka tedy potřebné struktury může nemít
def tri_plot(ax, tri_space=None, linewidths=[0.7, 0.5, 0.4, 0.3, 0.2, 0.1], 
                ms=3, mew=0.6, lw=0.7, data_offset=1, nrid=200):
    from .. import simplex as six
    if tri_space is None:
        tri_space = ax.space
    
    Tri = six.JustCubatureTriangulation(ax.sample_box, tn_scheme=None, \
                                    tri_space=tri_space, issi=None,\
                                    weighting_space=None, \
                                    incremental=False,\
                                    on_add_simplex=None,\
                                    on_delete_simplex=None)
    
    mart.setup(ax)
    if tri_space == ax.space:
        mart.triplot(ax, color="#B2B2B2", lw=lw/1.4, zorder=100)
    else:
        mart.tri_plot(ax, Tri=Tri, color="#B2B2B2", lw=lw/1.4, zorder=100, rasterized=True)
    
    mart.plot_points(ax, ms=ms, mew=mew, zorder=100500)
    #č curly a boundaries raději nakreslíme co nejpozději
    mart.curly(ax, nrid=nrid, linewidths=linewidths)
    try:
        mart.plot_boundaries(ax, lw=lw, zorder=1050, nrod=nrid)
    except:
        pass
    min_coord = np.abs(np.min(getattr(ax.sample_box, ax.space)))
    mart.setup_labels(ax, data_offset=data_offset * min_coord)
        
    

def tri_R_plot(ax, **kwargs):
    tri_plot(ax, tri_space='R', **kwargs)
    
def tri_GK_plot(ax, **kwargs):
    tri_plot(ax, tri_space='GK', **kwargs)

#č ten [plot] zásadně vytvaří svou obálku, nepouzívá onou ze skříňky,
#č protože já vím, že v těch obrázcích, ve kterých chcu ho použit,
#č můde být třeba použit řez a skříňka tedy potřebné struktury může nemít
def convex_hull_plot(ax, tri_space=None, ms=3, mew=0.6, lw=0.7, nrid=200,
                    linewidths=[0.7, 0.5, 0.4, 0.3, 0.2, 0.1]):
    from .. import convex_hull as khull
    if tri_space is None:
        tri_space = ax.space
    
    mart.setup(ax)
    qhull = khull.QHull(ax.sample_box, space=tri_space, incremental=False)
    mart.qhull_plot(ax, qhull, color="#B2B2B2", lw=lw, zorder=100)
    mart.plot_points(ax, ms=ms, mew=mew, zorder=100500)
    #č curly a boundaries raději nakreslíme co nejpozději
    mart.curly(ax, nrid=nrid, linewidths=linewidths)
    try:
        mart.plot_boundaries(ax, lw=lw, zorder=1050, nrod=nrid)
    except:
        pass
    mart.setup_labels(ax)

def just_points(ax):
    ax.set_xlabel('$x_{1}$')
    ax.set_ylabel('$x_{2}$')
    
    ax.set_aspect(1)
    #ax.set_box_aspect(1)
    mart.scatter_points(ax)
    
def just_points_really(ax):
    ax.set_aspect(1)
    ax.set_frame_on(False)
    mart.scatter_points(ax)

def base_drawing(ax):
    mart.setup(ax)
    mart.curly(ax)
    try:
        mart.triplot(ax, color="grey", linewidth=0.4)
    except:
        pass
    mart.plot_boundaries(ax, linewidth=0.7)
    mart.scatter_points(ax)
    
    
def candidates_drawing(ax):
    try:
        mart.triplot(ax, color="grey", linewidth=0.4)
    except:
        pass
    mart.plot_boundaries(ax, linewidth=0.7)
    
    #č ax.scatter posílá parameter cmap Collections třídě.
    #č Třída mimo jiného dědí cm.ScalarMappable,
    #č která inicializaci deleguje funkci cm.get_cmap() ve (svém) modulu cm.
    # cmap='viridis_r' #cmap='plasma',
    mart.scatter_candidates(ax, s=5, marker='.', cmap='plasma_r',\
     alpha=None, linewidths=None, edgecolors=None, plotnonfinite=False, rasterized=True)
    mart.plot_the_best_candidate(ax, "^", color='#3D0D5B')
    
        
    
    

# defaults
hezkymodře = (85/255, 70/255, 1, 1)
inside_color = [(185/255, 228/255, 14/255, 1)]
outside_color = [(128/255, 128/255, 128/255, 0.5)]
hull_colors = (hezkymodře, inside_color, outside_color) # border_inside_outside

def just_qhull(ax, lw=1.5, **kwargs):
    from .. import convex_hull as khull
    qhull = khull.QHull(ax.sample_box, space=ax.space, incremental=False)
    border_color, _, __ = hull_colors

    # setup
    ax.set_aspect(1)
    #ax.set_box_aspect(3/4)
    #ax.set_xlim(-lim, lim)
    #ax.set_ylim(-lim, lim)
    ax.set_xlabel('$x_1$')
    ax.set_ylabel('$x_2$')
    
    mart.qhull_plot(ax, qhull, color=border_color, lw=lw, zorder=100, **kwargs)
    
    # finally samples
    #
    #mart.scatter_sample(ax, f, c='g', marker='P', zorder=1000) # why?
    mart.scatter_points(ax, zorder=100500)



def _hull_model_plot(ax, hull, hull_plot, ns=50000, lim=3, lw=1.5, s=4, hull_colors=hull_colors, **kwargs):
    border_color, inside_color, outside_color = hull_colors

    # setup
    ax.set_aspect(1)
    #ax.set_box_aspect(3/4)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_xlabel('$x_1$')
    ax.set_ylabel('$x_2$')
    
    nodes = ax.sample_box.f_model(ns)
    mask = hull.is_outside(nodes)
    mart.scatter_sample(ax, nodes[mask], c=outside_color, marker='.', s=s)
    mart.scatter_sample(ax, nodes[~mask], c=inside_color, marker='.', s=s)
    hull_plot(ax, hull, color=border_color, lw=lw, zorder=100, **kwargs)
    
    # finally samples
    #
    #mart.scatter_sample(ax, f, c='g', marker='P', zorder=1000) # why?
    mart.scatter_points(ax, zorder=100500)
    

    
    
    
def qhull_plot(ax, **kwargs):
    from .. import convex_hull as khull
    qhull = khull.QHull(ax.sample_box, space=ax.space, incremental=False)
    _hull_model_plot(ax, qhull, mart.qhull_plot, **kwargs)
    
    #mart.qhull_polygon(ax, qhull, fc="white", ec="black", lw=0.75)


def qhull_infinite(ax, **kwargs):
    from .. import convex_hull as khull
    qhull = khull.QHull(ax.sample_box, space=ax.space, incremental=False)
    _hull_model_plot(ax, qhull, mart.dhull_plot, **kwargs)




def dhull_scheme_plot(ax, **kwargs):
    from .. import convex_hull as khull
    import quadpy
    
    scheme = quadpy.un.stroud_un_7_1(2)
    dhull = khull.DirectHull(ax.sample_box, scheme.points, space=ax.space)
    _hull_model_plot(ax, dhull, mart.dhull_plot, **kwargs)
    

def dhull_random_plot(ax, ndir=8, rand_dir=None, **kwargs):
    from .. import convex_hull as khull
    from .. import sball
    
    if rand_dir is None:
        rand_dir = sball.get_random_directions(ndir, 2)
    dhull = khull.DirectHull(ax.sample_box, rand_dir, space=ax.space)
    _hull_model_plot(ax, dhull, mart.dhull_plot, **kwargs)  
    
    
def bhull_plot(ax, **kwargs):
    from .. import convex_hull as khull
    
    bhull = khull.BrickHull(ax.sample_box, space=ax.space)
    _hull_model_plot(ax, bhull, mart.bhull_plot, **kwargs)
    
def bhull_infinite(ax, **kwargs):
    from .. import convex_hull as khull
    
    bhull = khull.BrickHull(ax.sample_box, space=ax.space)
    _hull_model_plot(ax, bhull, mart.dhull_plot, **kwargs)    
    
    
def shull_plot(ax, **kwargs):
    from .. import convex_hull as khull
    
    shull = khull.GBall(ax.sample_box)
    _hull_model_plot(ax, shull, mart.shull_plot, **kwargs)
    
    

def completehull_plot(ax, ndir=3, rand_dir=None, **kwargs):
    from .. import convex_hull as khull
    from .. import sball
    
    if rand_dir is None:
        rand_dir = sball.get_random_directions(ndir, 2)
    
    copletehull = khull.CompleteHull(ax.sample_box, rand_dir, space=ax.space)
    shull = khull.GBall(ax.sample_box)
    #_hull_model_plot(ax, copletehull, mart.dhull_plot, **kwargs)
    #_hull_model_plot(ax, copletehull, mart.shull_plot, ns=0, **kwargs)
    
    ns=50000
    lim=3
    lw=1.5
    s=4
    #hull_colors=hull_colors, **kwargs):
    border_color, inside_color, outside_color = hull_colors

    # setup
    ax.set_aspect(1)
    #ax.set_box_aspect(3/4)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_xlabel('$x_1$')
    ax.set_ylabel('$x_2$')
    
    nodes = ax.sample_box.f_model(ns)
    completemask = copletehull.is_outside(nodes)
    smask = shull.is_outside(nodes)
    mask = np.any([completemask, smask], axis=0)
    mart.scatter_sample(ax, nodes[mask], c=outside_color, marker='.', s=s)
    mart.scatter_sample(ax, nodes[~mask], c=inside_color, marker='.', s=s)
    mart.dhull_plot(ax, copletehull, color=border_color, lw=lw, zorder=100, **kwargs)
    mart.shull_plot(ax, shull, color=border_color, lw=lw/2, ls='--', zorder=100, **kwargs)
    
    # finally samples
    #
    #mart.scatter_sample(ax, f, c='g', marker='P', zorder=1000) # why?
    mart.scatter_points(ax, zorder=100500)
    
