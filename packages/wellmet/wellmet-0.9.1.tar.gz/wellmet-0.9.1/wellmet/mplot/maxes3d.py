#!/usr/bin/env python
# coding: utf-8

# Axes level functions (for Matplotlib)
# Tier3 module => suppose dirty unsupported code

#č Založme nový modul pro funkce (procedury),
#č které sice stejně jako mart pracují na urovni axes,
#č ale na rozdil od atomických funkcí mart modulu
#č udělaj z prazdných os hotový obrazek.


from . import mart
from . import mart3d

# it is mostly for qt_plot, it offers availiable options to user
__all__ = ['tri_plot', 'plot3D', 'plot_points_3D',
         'candidates_drawing', 'plane_under_density', 
         'qhull_under_density', 'dhull_under_density']

def plot3D(ax3d):
    mart3d.scatter_points(ax3d)
    
    ax3d.set_xlabel("$x_1$")
    ax3d.set_ylabel("$x_2$")
    ax3d.set_zlabel("$x_3$")


def plot_points_3D(ax3d):
    mart3d.scatter_points(ax3d, markers=('.', '.', '.', '.'), alpha=0.5, rasterized=True)
    
    ax3d.set_xlabel("$x_1$")
    ax3d.set_ylabel("$x_2$")
    ax3d.set_zlabel("$x_3$")


#č ten [plot] zásadně vytvaří své struktury, nepouzívá oné ze skříňky,
#č protože já vím, že v těch obrázcích, ve kterých chcu ho použit,
#č můde být třeba použit řez a skříňka tedy potřebné struktury může nemít
def tri_plot(ax3d, tri_space=None, lw=0.3, nrid=200):
    from .. import simplex as six
    if tri_space is None:
        tri_space = ax3d.space
    
    Tri = six.JustCubatureTriangulation(ax3d.sample_box, tn_scheme=None, \
                                    tri_space=tri_space, issi=None,\
                                    weighting_space=None, \
                                    incremental=False,\
                                    on_add_simplex=None,\
                                    on_delete_simplex=None)
    
    if tri_space == ax3d.space:
        mart3d.tri_plot(ax3d, Tri=Tri, ns=2, color="#74747445", lw=lw/1.4, zorder=100, rasterized=True)
    else:
        mart3d.tri_plot(ax3d, Tri=Tri, ns=nrid, color="#74747445", lw=lw/1.4, zorder=100, rasterized=True)
    
    mart3d.scatter_points(ax3d)
    
    ax3d.set_xlabel("$x_1$")
    ax3d.set_ylabel("$x_2$")
    ax3d.set_zlabel("$x_3$")
    

    
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
     alpha=None, linewidths=None, edgecolors=None, plotnonfinite=False)
    mart.plot_the_best_candidate(ax, "^", color='#3D0D5B')
    
    mart.scatter_points(ax)    
    
    
    
def plane_under_density(ax3d, lim=3, pudorys=-0.2, jemnost=30):
    mart.scatter_points(ax3d, zs=pudorys, s=3)#, zorder=300000)
    #ax3d.set_zbound()
    #ax3d.set_frame_on(False)
    #ax3d.grid(False)
    
    ax3d.margins(0)
    ax3d.set_xlim(-lim, lim)
    ax3d.set_ylim(-lim, lim)
    #ax3d.set_xlabel('$x_1$') #ošklivý
    #ax3d.set_ylabel('$x_2$') #ošklivý
    #ax3d.set_axis_off() # vypne aj dolní panev
    #ax3d.set_zlim(pudorys, 5)
    ax3d.set_xticklabels([])
    ax3d.set_yticklabels([])
    
    mart3d.density_surface(ax3d, alpha=0.8, rcount=50, edgecolor='black', linewidth=0.3, color='#4472C4')
    
    
def qhull_under_density(ax3d, lim=3, pudorys=-0.2, jemnost=30, hezkymodře=(85/255, 70/255, 1, 1)):
    import numpy as np
    #from matplotlib import colors
    from .. import convex_hull as khull

    qhull = khull.QHull(ax3d.sample_box, space=ax3d.space)
    
    mart.scatter_points(ax3d, zs=pudorys, s=3)#, zorder=300000)
    #ax3d.set_zbound()
    #ax3d.set_frame_on(False)
    #ax3d.grid(False)
    
    ax3d.margins(0)
    ax3d.set_xlim(-lim, lim)
    ax3d.set_ylim(-lim, lim)
    #ax3d.set_xlabel('$x_1$') #ošklivý
    #ax3d.set_ylabel('$x_2$') #ošklivý
    #ax3d.set_axis_off() # vypne aj dolní panev
    #ax3d.set_zlim(pudorys, 5)
    ax3d.set_xticklabels([])
    ax3d.set_yticklabels([])
    
    mart3d.density_colored_surface(ax3d, qhull, alpha=0.8, rcount=50, edgecolor='black', linewidth=0.3, colors=('#B9E40E', '#808080'))
    
    list_of_lines2D = mart.qhull_plot(ax3d, qhull, zs=pudorys, linewidth=0.5, color=hezkymodře)
    for line2d in list_of_lines2D:
        mart3d.wall(ax3d, line2d, zmin=0, zmax=0.03, facecolor=hezkymodře, edgecolor=hezkymodře, linewidth=0.0, alpha=1)
    


def dhull_under_density(ax3d, ndir=10, lim=3, pudorys=-0.2, jemnost=30, hezkymodře=(85/255, 70/255, 1, 1)):
    import numpy as np
    #from matplotlib import colors
    from .. import convex_hull as khull
    from .. import sball
    
    direct_plan = sball.get_random_directions(ndir, 2)
    dhull = khull.DirectHull(ax3d.sample_box, direct_plan, space=ax3d.space)
    
    mart.scatter_points(ax3d, zs=pudorys, s=3)#, zorder=300000)
    #ax3d.set_zbound()
    #ax3d.set_frame_on(False)
    #ax3d.grid(False)
    
    ax3d.margins(0)
    ax3d.set_xlim(-lim, lim)
    ax3d.set_ylim(-lim, lim)
    #ax3d.set_xlabel('$x_1$') #ošklivý
    #ax3d.set_ylabel('$x_2$') #ošklivý
    #ax3d.set_axis_off() # vypne aj dolní panev
    #ax3d.set_zlim(pudorys, 5)
    ax3d.set_xticklabels([])
    ax3d.set_yticklabels([])
    
    mart3d.density_colored_surface(ax3d, dhull, alpha=0.8, rcount=50, edgecolor='black', linewidth=0.3, colors=('#B9E40E', '#808080'))
    
    list_of_lines2D = mart.dhull_plot(ax3d, dhull, linewidth=0.5, color=hezkymodře)
    
