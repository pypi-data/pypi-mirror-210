#!/usr/bin/env python
# coding: utf-8


# nazvy proměnných jsou v angličtině
# Ale komenty teda ne)


import numpy as np
from . import mart
from . import maxes
from . import maxes3d
from matplotlib import ticker


__all__ = [
            'convergence_diagram', 'convergence_legend', 'double_proxy_diagram', 
            'four_branch_convergence', 'beta_diagram', 'double_diagram', 'suspension_3d', 
            'double_tri_R_plot', 'double_tri_R_twins_plot', 'double_100_plot', 'G_U_distortion',
            'double_pprod_R_plot', 'double_mprod_R_plot',
            'triple_vector_plot',
            'triple_plot', 'triple_wide', 'triple_wide_50_100', 'triple_plot_50_100', 
            'triple_nodes_plot', 'triple_wide_25_50',
            'triple_plot_35_50', 'convex_plot_7', 'quadruple_plot',
            'qhull_under_density', 'plane_under_density', 'dhull_vs_complete'
            ]

space_labels = {
    'R': r'$\mathcal{R}$',
    'Rn': r'$\mathcal{R}^{\mathrm{n}}$',
    'P': r'$\mathcal{P}$',
    'GK': r'$\mathcal{G}^{\mathrm{c}}$',
    'G': r'$\mathcal{G}$',
    'U': r'$\mathcal{U}$'
    }

tri_kwargs = {
    1: dict(ms=3, mew=0.6, lw=0.7, linewidths=[0.7, 0.5, 0.4, 0.3, 0.2, 0.1]),
    32: dict(ms=2.5, mew=0.5, lw=0.7, linewidths=[0.7, 0.5, 0.4, 0.3, 0.2, 0.1]),
    2: dict(ms=2.5, mew=0.4, lw=0.7, linewidths=[0.7, 0.5, 0.4, 0.3, 0.2, 0.1]),
    3: dict(ms=2.2, mew=0.1, lw=0.5, linewidths=np.array([0.7, 0.5, 0.4, 0.3, 0.2, 0.1]) / 1.5)
    }


def suspension_3d(fig, sample_box, space):
    ax3d = fig.add_subplot(121,  projection='3d', azim=-90.0001, elev=89)
    ax3d.space = space
    ax3d.sample_box = sample_box[0:300]
    maxes3d.tri_plot(ax3d)
    ax3d.set_zticks([])
    
    ax = fig.add_subplot(122)
    ax.sample_box = sample_box
    maxes.convergence_square(ax)
    fig.set_figwidth(19/2.54)


def beta_diagram(fig, sample_box, space, lim=100):
    fig.set_figheight(2)
    ax = fig.add_subplot(111)
    ax.sample_box = sample_box
    maxes.beta_diagram(ax)
    #ax.set_ylim(1e-5, 1)
    #ax.set_xlim(0, lim)
    ticks = [0, 80, 160, 240, 320, 400, 480]
    ax.xaxis.set_major_locator(ticker.FixedLocator(locs=ticks))


def convergence_diagram(fig, sample_box, space, lim=1000):
    fig.set_figheight(1.8)
    ax = fig.add_subplot(111)
    ax.sample_box = sample_box
    maxes.convergence_diagram(ax)
    ax.set_xlim(0, lim)

def convergence_legend(fig, sample_box, space, lim=1000):
    fig.set_figheight(2)
    ax = fig.add_subplot(111)
    ax.sample_box = sample_box
    maxes.convergence_legend(ax)
    #ax.legend(bbox_to_anchor=(0.5, -0.25), ncol=2, loc='upper center')
    ax.set_xlim(0, lim)

def four_branch_convergence(fig, sample_box, space, lim=100):
    fig.set_figheight(2)
    ax = fig.add_subplot(111)
    ax.sample_box = sample_box
    maxes.convergence_legend(ax)
    #ax.legend(bbox_to_anchor=(0.5, -0.25), ncol=2, loc='upper center')
    ax.set_ylim(1e-5, 1)
    ax.set_xlim(0, lim)
    seq = ["0", r"$\bm{4}$", r"$\bm{26}$", "50", "75", "100"]
    ticks = [0, 4, 26, 50, 75, 100]
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(seq))
    ax.xaxis.set_major_locator(ticker.FixedLocator(locs=ticks))

def double_diagram(fig, sample_box, space, lim=1000):
    ax1 = ax = fig.add_subplot(211)
    ax.sample_box = sample_box
    maxes.convergence_diagram(ax)
    ax.set_xlim(0, lim)
    ax.set_xlabel('')
    
    ax = fig.add_subplot(212)
    ax.sample_box = sample_box
    maxes.convergence_diagram(ax)
    #ax.sharex(ax1)
    
def double_proxy_diagram(fig, sample_box, space, lim=1000):
    ax1 = ax = fig.add_subplot(211)
    ax.sample_box = sample_box
    maxes.convergence_diagram(ax)
    ax.set_xlim(0, lim)
    ax.set_xlabel('')
    
    ax = fig.add_subplot(212)
    ax.sample_box = sample_box
    maxes.convergence_diagram(ax, sources=['box'], apply_proxy=True)
    ax.sharex(ax1)

def convex_plot_7(fig, sample_box, space):
    ax1 = ax = fig.add_subplot(121)
    ax.sample_box = sample_box[0:7]
    ax.space = space
    
    maxes.convex_hull_plot(ax, tri_space=None, linewidths=[0.7, 0.5, 0.4, 0.3])
    #ax.set_title(space_labels[space], pad=10)
    ax = fig.add_subplot(122)
    ax.sample_box = sample_box
    ax.space = space
    maxes.convex_hull_plot(ax, tri_space=None, linewidths=[0.7, 0.5, 0.4, 0.3])
    #ax.set_title(space_labels[space], pad=10)
    ax.sharey(ax1)


def double_tri_R_twins_plot(fig, sample_box, space):
    ax1 = ax = fig.add_subplot(121)
    ax.sample_box = sample_box
    ax.space = 'R'
    try:
        tn_scheme = sample_box.Tri.tn_scheme
    except:
        import quadpy
        tn_scheme = quadpy.tn.grundmann_moeller(sample_box.nvar, 5)
        
    maxes.tri_nodes_plot(ax, tri_space='R', tn_scheme=tn_scheme)
    ax.set_title(r'$\mathcal{R}$', pad=10)
    ax = fig.add_subplot(122)
    ax.sample_box = sample_box
    ax.space = 'G'
    maxes.tri_nodes_plot(ax, tri_space='R', tn_scheme=tn_scheme)
    ax.set_title(r'$\mathcal{G}$', pad=10)
    y_bound = ax.get_ybound()
    ax1.sharey(ax)
    ax.set_ybound(y_bound)

def double_pprod_R_plot(fig, sample_box, space):
    ax1 = ax = fig.add_subplot(121)
    ax.sample_box = sample_box
    ax.space = 'R'
    try:
        tn_scheme = sample_box.Tri.tn_scheme
    except:
        import quadpy
        tn_scheme = quadpy.tn.grundmann_moeller(sample_box.nvar, 5)
    #linewidths = np.array([0.7, 0.5, 0.4, 0.3, 0.2, 0.1]) / 2
    maxes.tri_nodes_plot(ax, tri_space='R', tn_scheme=tn_scheme, nrid=2000,
                data_offset=0.95, **tri_kwargs[2])
    ax.set_title(space_labels[space], pad=10)
    ax.set_xlim(0, 34)
    ax.set_ylim(0, 34)
    ax = fig.add_subplot(122)
    ax.sample_box = sample_box
    ax.space = 'G'
    maxes.tri_nodes_plot(ax, tri_space='R', tn_scheme=tn_scheme, nrid=2000,
                data_offset=0.7, **tri_kwargs[3])
                #ms=1.5, mew=0.4, lw=0.35, linewidths=linewidths)
    from scipy import stats
    beta = -stats.norm.ppf(ax.sample_box.pf_exact) * np.sqrt(2) #č beta-nebeta
    ax.plot([-beta*5/4, beta/4], [beta/4, -beta*5/4], '-b', lw=0.5, zorder=1150)
    ax.xaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    ax.yaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    ax.set_title(space_labels['G'], pad=10)


def double_mprod_R_plot(fig, sample_box, space):
    ax1 = ax = fig.add_subplot(121)
    ax.sample_box = sample_box
    ax.space = 'R'
    try:
        tn_scheme = sample_box.Tri.tn_scheme
    except:
        import quadpy
        tn_scheme = quadpy.tn.grundmann_moeller(sample_box.nvar, 5)
    #linewidths = np.array([0.7, 0.5, 0.4, 0.3, 0.2, 0.1]) / 2
    maxes.tri_nodes_plot(ax, tri_space='R', tn_scheme=tn_scheme, nrid=2000,
                data_offset=100, **tri_kwargs[2])
    
    ax.set_title(space_labels[space], pad=10)
    ax.set_xlim(0, 3800)
    ax.set_ylim(0, 3800)
    ax = fig.add_subplot(122)
    ax.sample_box = sample_box
    ax.space = 'G'
    maxes.tri_nodes_plot(ax, tri_space='R', tn_scheme=tn_scheme, nrid=2000,
                data_offset=0.7, **tri_kwargs[3])
                #ms=1.5, mew=0.4, lw=0.35, linewidths=linewidths)
    from scipy import stats
    beta = -stats.norm.ppf(ax.sample_box.pf_exact) * np.sqrt(2) #č beta-nebeta
    ax.plot([-beta/4, beta*5/4], [beta*5/4, -beta/4], '-b', lw=0.5, zorder=1150)
    ax.set_title(space_labels['G'], pad=10)


def double_tri_R_plot(fig, sample_box, space):
    ax1 = ax = fig.add_subplot(121)
    ax.sample_box = sample_box
    ax.space = 'R'
    try:
        tn_scheme = sample_box.Tri.tn_scheme
    except:
        import quadpy
        tn_scheme = quadpy.tn.grundmann_moeller(sample_box.nvar, 5)
        
    linewidths = np.array([0.7, 0.5, 0.4, 0.3, 0.2, 0.1]) / 2
    maxes.tri_nodes_plot(ax, tri_space='R', tn_scheme=tn_scheme, nrid=2000,
                ms=1.5, mew=0.4, lw=0.35, linewidths=linewidths)
    ax.set_title(space_labels[space], pad=10)
    ax = fig.add_subplot(122)
    ax.sample_box = sample_box
    ax.space = 'G'
    maxes.tri_nodes_plot(ax, tri_space='R', tn_scheme=tn_scheme, nrid=2000,
                ms=1.5, mew=0.4, lw=0.35, linewidths=linewidths)
    ax.set_title(space_labels['G'], pad=10)
    
    
    
    
def G_U_distortion(fig, sample_box, space):
    try:
        tn_scheme = sample_box.Tri.tn_scheme
    except:
        import quadpy
        tn_scheme = quadpy.tn.grundmann_moeller(sample_box.nvar, 5)
    ms=3
    mew=0.6
    lw=0.7
    linewidths=[0.7, 0.5, 0.4, 0.3, 0.2, 0.1]
    nrid=100
    
    from .. import simplex as six
    
    
    def _draw_nodes(*args, **kwargs):
        # callback's signature: sx, indices=, simplex=, nodes=, cell_stats=
        # positional "sx" is Tri object itself
        # "indices" are numbers of simplex vertices
        # "simplex" are vertices itself
        # "nodes" is what we really want to draw
        
        event = kwargs['cell_stats']['event']
        
        if event == 'mix':
            color = (149/255, 173/255, 1, 0.7)
            mart.plot_sample(ax1, kwargs['nodes'], ls='', marker='.',\
                         mew=0, mfc=color, ms=2.8, alpha=0.5, rasterized=True)
            mart.plot_sample(ax, kwargs['nodes'], ls='', marker='.',\
                         mew=0, mfc=color, ms=2.8, alpha=0.5, rasterized=True)
        
    
    Tri = six.JustCubatureTriangulation(sample_box, tn_scheme=tn_scheme, \
                                    tri_space='U', issi=None,\
                                    weighting_space=None, \
                                    incremental=False,\
                                    on_add_simplex=_draw_nodes,\
                                    on_delete_simplex=None)
    
    
    ax1 = ax = fig.add_subplot(121)
    ax.sample_box = sample_box
    ax.space = 'G'
    ax.set_aspect(1)
    ax.set_box_aspect(1)
    ax.margins(0)
    ax.set_title(space_labels[ax.space])#, pad=10)
    x_label="$x_1$"; y_label="$x_2$"
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    mart.tri_plot(ax, Tri=Tri, color="#B2B2B2", lw=lw/1.4, zorder=100, rasterized=True)
    mart.plot_points(ax, ms=ms, mew=mew, zorder=100500)
    mart.number_points(ax, ha="left", va="bottom", zorder=1005000)
    try:
        mart.plot_boundaries(ax, lw=lw, zorder=1050, nrod=nrid)
    except:
        pass
    
    ax = fig.add_subplot(122)
    ax.sample_box = sample_box
    ax.space = 'U'
    ax.set_aspect(1)
    ax.set_box_aspect(1)
    ax.margins(0)
    ax.set_title(space_labels[ax.space])#, pad=10)
    ax.set_xlabel(x_label)
    #ax.set_ylabel(y_label)
    mart.triplot(ax, color="#B2B2B2", lw=lw/1.4, zorder=100)
    mart.plot_points(ax, ms=ms, mew=mew, zorder=100500)
    mart.number_points(ax, ha="left", va="bottom", zorder=1005000)
    try:
        mart.plot_boundaries(ax, lw=lw, zorder=1050, nrod=nrid)
    except:
        pass
        
    Tri.integrate()
    
    
    

def double_100_plot(fig, sample_box, space, lim=100):
    #fig.set_figwidth(19/2.54)
    ax = fig.add_subplot(122)
    ax.sample_box = sample_box
    ax.space = space
    try:
        tn_scheme = sample_box.Tri.tn_scheme
    except:
        import quadpy
        tn_scheme = quadpy.tn.grundmann_moeller(sample_box.nvar, 5)
    maxes.tri_nodes_plot(ax, tri_space=None, tn_scheme=tn_scheme, **tri_kwargs[2])
    ax.xaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    ax.yaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    #ax.set_title(space_labels[space], pad=10)
    ax = fig.add_subplot(121, sharex=ax, sharey=ax)
    ax.sample_box = sample_box[0:lim]
    ax.space = space
    maxes.tri_nodes_plot(ax, tri_space=None, tn_scheme=tn_scheme, **tri_kwargs[2])
    #ax.set_title(space_labels[space], pad=10)
    ax.xaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    ax.yaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))


def quadruple_plot(fig, sample_box, space, npoints=[50, 100, 200]):
    #fig.set_figwidth(19/2.54)
    ax = fig.add_subplot(224)
    ax.sample_box = sample_box
    ax.space = space
    try:
        tn_scheme = sample_box.Tri.tn_scheme
    except:
        import quadpy
        tn_scheme = quadpy.tn.grundmann_moeller(sample_box.nvar, 5)
    maxes.tri_nodes_plot(ax, tri_space=None, tn_scheme=tn_scheme, **tri_kwargs[2])
    ax.xaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    ax.yaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    #ax.set_title(space_labels[space], pad=10)
    ax = fig.add_subplot(223, sharex=ax, sharey=ax)
    ax.sample_box = sample_box[0:npoints[2]]
    ax.space = space
    maxes.tri_nodes_plot(ax, tri_space=None, tn_scheme=tn_scheme, **tri_kwargs[2])
    #ax.set_title(space_labels[space], pad=10)
    ax.xaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    ax.yaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    ax = fig.add_subplot(222, sharex=ax, sharey=ax)
    ax.sample_box = sample_box[0:npoints[1]]
    ax.space = space
    maxes.tri_nodes_plot(ax, tri_space=None, tn_scheme=tn_scheme, **tri_kwargs[2])
    #ax.set_title(space_labels[space], pad=10)
    ax.xaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    ax.yaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    ax = fig.add_subplot(221, sharex=ax, sharey=ax)
    ax.sample_box = sample_box[0:npoints[0]]
    ax.space = space
    maxes.tri_nodes_plot(ax, tri_space=None, tn_scheme=tn_scheme, **tri_kwargs[2])
    #ax.set_title(space_labels[space], pad=10)
    ax.xaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    ax.yaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    

def triple_wide(fig, sample_box, space):
    triple_plot(fig, sample_box, space)
    fig.set_figwidth(19/2.54)

def triple_wide_50_100(fig, sample_box, space):
    triple_plot(fig, sample_box, space, npoints=[50, 100])
    fig.set_figwidth(19/2.54)

def triple_plot_50_100(fig, sample_box, space):
    triple_plot(fig, sample_box, space, npoints=[50, 100])

def triple_plot_35_50(fig, sample_box, space):
    triple_plot(fig, sample_box, space, npoints=[35, 50])
    
def triple_wide_25_50(fig, sample_box, space):
    triple_vector_plot(fig, sample_box, space, npoints=[25, 50])
    fig.set_figwidth(19/2.54)

def triple_nodes_plot(fig, sample_box, space, npoints=[25, 50]):
    ax = fig.add_subplot(131)
    ax.sample_box = sample_box[0:npoints[0]]
    ax.space = space
    try:
        tn_scheme = sample_box.Tri.tn_scheme
    except:
        import quadpy
        tn_scheme = quadpy.tn.grundmann_moeller(sample_box.nvar, 5)
    maxes.tri_nodes_plot(ax, tri_space=None, tn_scheme=tn_scheme)
    ax.set_title(space_labels[space], pad=10)
    
    ax = fig.add_subplot(132, sharex=ax, sharey=ax)
    ax.sample_box = sample_box[0:npoints[1]]
    ax.space = space
    maxes.tri_nodes_plot(ax, tri_space=None, tn_scheme=tn_scheme)
    ax.set_title(space_labels[space], pad=10)
    
    ax = fig.add_subplot(133, sharex=ax, sharey=ax)
    ax.sample_box = sample_box
    ax.space = space
    maxes.tri_nodes_plot(ax, tri_space=None, tn_scheme=tn_scheme)
    ax.set_title(space_labels[space], pad=10)

def triple_vector_plot(fig, sample_box, space, npoints=[25, 50]):
    ax = fig.add_subplot(131)
    ax.sample_box = sample_box[0:npoints[0]]
    ax.space = space
    
    maxes.tri_vector_plot(ax, tri_space=None)
    ax.set_title(space_labels[space], pad=10)
    
    ax = fig.add_subplot(132, sharex=ax, sharey=ax)
    ax.sample_box = sample_box[0:npoints[1]]
    ax.space = space
    maxes.tri_vector_plot(ax, tri_space=None)
    ax.set_title(space_labels[space], pad=10)
    
    ax = fig.add_subplot(133, sharex=ax, sharey=ax)
    ax.sample_box = sample_box
    ax.space = space
    maxes.tri_vector_plot(ax, tri_space=None)
    ax.set_title(space_labels[space], pad=10)

def triple_plot(fig, sample_box, space, npoints=[100, 200]):
    ax = fig.add_subplot(133)
    ax.sample_box = sample_box
    ax.space = space
    try:
        tn_scheme = sample_box.Tri.tn_scheme
    except:
        import quadpy
        tn_scheme = quadpy.tn.grundmann_moeller(sample_box.nvar, 5)
    maxes.convex_hull_plot(ax, **tri_kwargs[3])
    ax.xaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    ax.yaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    #ax.set_title(space_labels[space], pad=10)
    
    ax = fig.add_subplot(132, sharex=ax, sharey=ax)
    ax.sample_box = sample_box[0:npoints[1]]
    ax.space = space
    maxes.tri_plot(ax, **tri_kwargs[3])
    ax.xaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    ax.yaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    #ax.set_title(space_labels[space], pad=10)
    
    ax = fig.add_subplot(131, sharex=ax, sharey=ax)
    ax.sample_box = sample_box[0:npoints[0]]
    ax.space = space
    maxes.tri_nodes_plot(ax, tri_space=None, tn_scheme=tn_scheme, **tri_kwargs[3])
    ax.xaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    ax.yaxis.set_major_locator(ticker.FixedLocator(locs=[-6]))
    #ax.set_title(space_labels[space], pad=10)

def qhull_under_density(fig, sample_box, space):
    from . import _axis3d_margins_patch, _axes3d
    ax3d = fig.add_subplot(111, projection='3d')
    ax3d.sample_box = sample_box
    ax3d.space = space
    maxes3d.qhull_under_density(ax3d)

def plane_under_density(fig, sample_box, space):
    from . import _axis3d_margins_patch, _axes3d
    ax3d = fig.add_subplot(111, projection='3d')
    ax3d.sample_box = sample_box
    ax3d.space = space
    maxes3d.plane_under_density(ax3d)


def dhull_vs_complete(fig, sample_box, space):
    from .. import sball
    rand_dir = sball.get_random_directions(8, 2)
    
    ax = fig.add_subplot(121)
    ax.sample_box = sample_box
    ax.space = space
    maxes.dhull_random_plot(ax, rand_dir=rand_dir)
    ax = fig.add_subplot(122)
    ax.sample_box = sample_box
    ax.space = space
    maxes.completehull_plot(ax, rand_dir=rand_dir)
    


