#!/usr/bin/env python
# coding: utf-8


#č nazvy proměnných jsou v angličtině
#č Ale komenty teda ne)

import numpy as np
from matplotlib import colors
import matplotlib.tri as mtri

# copied from simplex module
# just don't want every time import simplex and its dependencies
def get_events(sx, simplices=None):
    """
    Metoda musí simplexům přiřazovat jev 
    0=success, 1=failure, 2=mix
    """
    if simplices is None:
        simplices = sx.tri.simplices
    
    in_failure = np.isin(simplices, sx.sample_box.failure_points)
    has_failure = in_failure.any(axis=1)
    all_failure = in_failure.all(axis=1)
    return np.int8(np.where(has_failure, np.where(all_failure, 1, 2), 0))


def get_g_model_wireframe_data(shape_share, limits, space='R', ngrid=50):
    xmin, xmax, ymin, ymax = limits
    
    # endpoint=True by default
    # we'll get len(.) == ngrid
    # ngrid 51 is an default maximum for MPL
    # (otherwise MPL will downsample)
    x = np.linspace(xmin, xmax, ngrid)
    y = np.linspace(ymin, ymax, ngrid)
    X, Y = np.meshgrid(x, y)
    XY = np.vstack((X.reshape(-1), Y.reshape(-1))).T
    
    if space == 'R':
        g_values = shape_share.gm(XY).g_values
    else:
        XY_sample = shape_share.f_model.new_sample(XY, space)
        g_values = shape_share.gm(XY_sample).g_values
    
    Z = g_values.reshape(ngrid, ngrid)
    return X, Y, Z


#č napadlo mě, že bych mohl matplotlibovskému Axes
#č přiřazovat (připsavat, zadávat) atribut 'space'
#č Daválo by to smysl, ne? U všeho ostatního, u sample boksů
#č nejsem jist, ale mám pocit, že na jedném sablotu někdo potřebuje
#č kreslit z různejch prostoru.
#č Zkrátka, funkce v tomto modulu požadujou aby 
#č ax.space a ax.sample_box byl nastaven!

# ax.space and ax.sample_box attributes should (expected to) be set up!


def scatter_points(ax3d, zs=None, markers=('P', 'X', 'h', 'H'), **kwargs):
    sample = getattr(ax3d.sample_box, ax3d.space)
    nsim = len(sample)
    if zs is not None:
        x, y = sample[:,:2].T
    elif ax3d.sample_box.nvar == 2:
        x, y = sample[:,:2].T
        #zs = ax3d.sample_box.pdf(ax3d.space)
        zs = ax3d.sample_box.g_values
    else:
        x, y, zs = sample[:,:3].T
    
    failsi = ax3d.sample_box.failsi
    
    try: # proxy denotes to implicitly-known values
        proxy = ax3d.sample_box.proxy
    except AttributeError:
        proxy = np.full(nsim, False, dtype=bool)
    
    sm, fm, psm, pfm = markers
    
    mask = np.all((~failsi, ~proxy), axis=0)
    success = ax3d.scatter(x[mask], y[mask], zs=zs[mask], c='g', marker=sm, **kwargs)
    
    mask = np.all((failsi, ~proxy), axis=0)
    failures = ax3d.scatter(x[mask], y[mask], zs=zs[mask], c='r', marker=fm, **kwargs)
    
    mask = np.all((~failsi, proxy), axis=0)
    proxy_successes = ax3d.scatter(x[mask], y[mask], zs=zs[mask],\
                             c='#77AC30', marker=psm, **kwargs)
    
    mask = np.all((failsi, proxy), axis=0)
    proxy_failures = ax3d.scatter(x[mask], y[mask], zs=zs[mask],\
                             c='#D95319', marker=pfm, **kwargs)
    
    return success, failures, proxy_successes, proxy_failures



def plot_points(ax3d, zs=None, markers=('P', 'X', 'h', 'H'), ls='', **kwargs):
    sample = getattr(ax3d.sample_box, ax3d.space)
    nsim = len(sample)
    if zs is not None:
        x, y = sample[:,:2].T
    elif ax3d.sample_box.nvar == 2:
        x, y = sample[:,:2].T
        #zs = ax3d.sample_box.pdf(ax3d.space)
        zs = ax3d.sample_box.g_values
    else:
        x, y, zs = sample[:,:3].T
    
    failsi = ax3d.sample_box.failsi
    
    try: # proxy denotes to implicitly-known values
        proxy = ax3d.sample_box.proxy
    except AttributeError:
        proxy = np.full(nsim, False, dtype=bool)
    
    sm, fm, psm, pfm = markers
    
    plot_list = []
    
    #č byl jsem svědkem, že matplotlib zlobil ve 3D 
    #č kvůli tomu, že nebyl žádný safe vzorek
    #č proto raději budu přidávat tečky podmíněne
    mask = np.all((~failsi, ~proxy), axis=0)
    if np.any(mask): #success
        plot_list.append(ax3d.plot(x[mask], y[mask], mec='g', mfc='g',\
                         marker=sm, ls=ls, **kwargs))
    
    mask = np.all((failsi, ~proxy), axis=0)
    if np.any(mask): #failures
        plot_list.append(ax3d.plot(x[mask], y[mask], mec='r', mfc='r',\
                         marker=fm, ls=ls, **kwargs))
    
    mask = np.all((~failsi, proxy), axis=0)
    if np.any(mask): #proxy_successes
        plot_list.append(ax3d.plot(x[mask], y[mask], mec='#77AC30', mfc=(0,0,0,0),\
                         marker=psm, ls=ls, **kwargs))
    
    mask = np.all((failsi, proxy), axis=0)
    if np.any(mask): #proxy_failures
        plot_list.append(ax3d.plot(x[mask], y[mask], mec='#D95319', mfc=(0,0,0,0),\
                         marker=pfm, ls=ls, **kwargs))
    
    return plot_list # success, failures, proxy_successes, proxy_failures



def tri_plot(ax, Tri=None, fmt='-', ns=100, **kwargs):
    if ax.sample_box.nvar == 3:
        lines = []
        
        if Tri is None:
            Tri = ax.sample_box.Tri
        
        # take coordinates in the space, where triangulation has been performed
        sampled_plan_tri = getattr(ax.sample_box, Tri.tri_space)
        
        #č mohli bychom zde machrovat se zkracenou smyčkou,
        #č my ale vůbec kontrolovat rovnost prostorů nebudeme, 
        #č nechť to dělá volající kód
        
        #if ax.space == Tri.tri_space:
        #   #return triplot(ax, **kwargs)
        #   
        #    #for simplex_id in simplex_ids:
        #    #    triangle = simplices[simplex_id]
        #    #    pos = sampled_plan_tri[triangle[[0,1,2,0]]]
             
        for simplex in Tri.tri.simplices:
            simplex_tri = sampled_plan_tri[simplex]
            x_tri_1 = np.linspace(simplex_tri[0,0], simplex_tri[1,0], ns, endpoint=False)
            y_tri_1 = np.linspace(simplex_tri[0,1], simplex_tri[1,1], ns, endpoint=False)
            z_tri_1 = np.linspace(simplex_tri[0,2], simplex_tri[1,2], ns, endpoint=False)
            
            x_tri_2 = np.linspace(simplex_tri[1,0], simplex_tri[2,0], ns, endpoint=False)
            y_tri_2 = np.linspace(simplex_tri[1,1], simplex_tri[2,1], ns, endpoint=False)
            z_tri_2 = np.linspace(simplex_tri[1,2], simplex_tri[2,2], ns, endpoint=False)
            
            x_tri_3 = np.linspace(simplex_tri[2,0], simplex_tri[3,0], ns, endpoint=True)
            y_tri_3 = np.linspace(simplex_tri[2,1], simplex_tri[3,1], ns, endpoint=True)
            z_tri_3 = np.linspace(simplex_tri[2,2], simplex_tri[3,2], ns, endpoint=True)
                
            
            tri_bound_tri = np.concatenate(((x_tri_1, y_tri_1, z_tri_1),\
                                            (x_tri_2, y_tri_2, z_tri_2),\
                                            (x_tri_3, y_tri_3, z_tri_3)), axis=1).T
            # vytvořme sample
            tri_bound = ax.sample_box.f_model.new_sample(tri_bound_tri, space=Tri.tri_space)
            
            xyz = getattr(tri_bound, ax.space)
            x, y, z = xyz.T
            lines.append(ax.plot(x, y, z, fmt, **kwargs))
        
        
            #
            #čs a eště raz
            #
        for simplex in Tri.tri.simplices:
            simplex_tri = sampled_plan_tri[simplex]
            x_tri_1 = np.linspace(simplex_tri[1,0], simplex_tri[3,0], ns, endpoint=False)
            y_tri_1 = np.linspace(simplex_tri[1,1], simplex_tri[3,1], ns, endpoint=False)
            z_tri_1 = np.linspace(simplex_tri[1,2], simplex_tri[3,2], ns, endpoint=False)
            
            x_tri_2 = np.linspace(simplex_tri[3,0], simplex_tri[0,0], ns, endpoint=False)
            y_tri_2 = np.linspace(simplex_tri[3,1], simplex_tri[0,1], ns, endpoint=False)
            z_tri_2 = np.linspace(simplex_tri[3,2], simplex_tri[0,2], ns, endpoint=False)
            
            x_tri_3 = np.linspace(simplex_tri[0,0], simplex_tri[2,0], ns, endpoint=True)
            y_tri_3 = np.linspace(simplex_tri[0,1], simplex_tri[2,1], ns, endpoint=True)
            z_tri_3 = np.linspace(simplex_tri[0,2], simplex_tri[2,2], ns, endpoint=True)
                
            tri_bound_tri = np.concatenate(((x_tri_1, y_tri_1, z_tri_1),\
                                            (x_tri_2, y_tri_2, z_tri_2),\
                                            (x_tri_3, y_tri_3, z_tri_3)), axis=1).T
        
            # vytvořme sample
            tri_bound = ax.sample_box.f_model.new_sample(tri_bound_tri, space=Tri.tri_space)
            
            xyz = getattr(tri_bound, ax.space)
            x, y, z = xyz.T
            lines.append(ax.plot(x, y, z, fmt, **kwargs))
        
        return lines




def limit_state_wireframe(ax3d, **kwargs):
    xmin, xmax = ax3d.get_xlim()
    ymin, ymax = ax3d.get_ylim()
    limits = (xmin, xmax, ymin, ymax)
    
    if 'rcount' in kwargs:
        ngrid = kwargs['rcount']
    else:
        ngrid = 50
    
    X, Y, Z = get_g_model_wireframe_data(ax3d.sample_box,\
                             limits, space=ax3d.space, ngrid=ngrid)
        
    return ax3d.plot_wireframe(X, Y, Z, **kwargs)


def limit_state_surface(ax3d, **kwargs):
    xmin, xmax = ax3d.get_xlim()
    ymin, ymax = ax3d.get_ylim()
    limits = (xmin, xmax, ymin, ymax)
    
    if 'rcount' in kwargs:
        ngrid = kwargs['rcount']
    else:
        ngrid = 50
    
    X, Y, Z = get_g_model_wireframe_data(ax3d.sample_box,\
                             limits, space=ax3d.space, ngrid=ngrid)
    
    # make a color map of fixed colors
    if 'cmap' not in kwargs:
        kwargs['cmap'] = colors.ListedColormap(['red', 'green'])
    if 'norm' not in kwargs:
        kwargs['norm'] = colors.BoundaryNorm([0], kwargs['cmap'].N, extend='both')
        
    return ax3d.plot_surface(X, Y, Z, **kwargs)


def density_surface(ax3d, **kwargs):
    xmin, xmax = ax3d.get_xlim()
    ymin, ymax = ax3d.get_ylim()
    
    if 'rcount' in kwargs:
        ngrid = kwargs['rcount']
    else:
        ngrid = 50
    
    x = np.linspace(xmin, xmax, ngrid)
    y = np.linspace(ymin, ymax, ngrid)
    X, Y = np.meshgrid(x, y)
    XY = np.vstack((X.reshape(-1), Y.reshape(-1))).T
    z = ax3d.sample_box.sample_pdf(XY, ax3d.space)
    Z = z.reshape(ngrid, ngrid)
    
    return ax3d.plot_surface(X, Y, Z, **kwargs)
    

def density_colored_surface(ax3d, hull, colors=('#7735C2', '#808080'), **kwargs):
    xmin, xmax = ax3d.get_xlim()
    ymin, ymax = ax3d.get_ylim()
    
    inside_color, outside_color = colors
    
    if 'rcount' in kwargs:
        ngrid = kwargs['rcount']
    else:
        ngrid = 50
    
    x = np.linspace(xmin, xmax, ngrid)
    y = np.linspace(ymin, ymax, ngrid)
    X, Y = np.meshgrid(x, y)
    XY = np.vstack((X.reshape(-1), Y.reshape(-1))).T
    z = ax3d.sample_box.sample_pdf(XY, ax3d.space)
    Z = z.reshape(ngrid, ngrid)
    
    # for facecolors
    _x = np.linspace(xmin, xmax, ngrid-1, endpoint=False) + (xmax-xmin)/(ngrid-1)/2
    _y = np.linspace(ymin, ymax, ngrid-1, endpoint=False) + (ymax-ymin)/(ngrid-1)/2
    _X, _Y = np.meshgrid(_x, _y)
    _XY = np.vstack((_X.reshape(-1), _Y.reshape(-1))).T
    facecolors = np.full(len(_XY), inside_color)
    mask = hull.is_outside(hull.sample.f_model.new_sample(_XY, space=ax3d.space))
    facecolors[mask] = outside_color
    facecolors = facecolors.reshape(ngrid-1, ngrid-1)
    
    return ax3d.plot_surface(X, Y, Z, facecolors = facecolors, **kwargs)

    
def tri_surface(ax3d, **kwargs):
    xy = getattr(ax3d.sample_box, ax3d.space)
    x, y = xy.T
    z = ax3d.sample_box.g_values
    if 'zs' in kwargs:
        z = kwargs.pop('zs')
    else:
        z = ax3d.sample_box.pdf(ax3d.space)
    return ax3d.plot_trisurf(x, y, z, **kwargs)
    



# from Matplotlib sources:
# "TODO: Support custom face colours"
    
#def tri_colored_surface(ax3d, **kwargs):
#    xy = getattr(ax3d.sample_box, ax3d.space)
#    x, y = xy.T
#    z = ax3d.sample_box.g_values
#    tri = mtri.Triangulation(x, y)
#    colors = get_simplices_colors(ax3d.sample_box, tri.get_masked_triangles())
#    return ax3d.plot_trisurf(tri, z, color=colors, **kwargs)


def tri_colored_surfaces(ax3d, **kwargs):
    xy = getattr(ax3d.sample_box, ax3d.space)
    x, y = xy.T
    if 'zs' in kwargs:
        z = kwargs.pop('zs')
    else:
        z = ax3d.sample_box.g_values
    if 'tri_colors' in kwargs:
        tri_colors = kwargs.pop('tri_colors')
    else:
        tri_colors = ("xkcd:light seafoam green", "xkcd:pale rose", "xkcd:dark cream")
    tri = mtri.Triangulation(x, y)
    triangles = tri.get_masked_triangles()
    events = get_events(ax3d.sample_box, triangles)
    # 0=success, 1=failure, 2=mix
    surf = list()
    if np.any(events==0):
        surf.append(ax3d.plot_trisurf(x, y, triangles[events==0], z, color=tri_colors[0], **kwargs))
    if np.any(events==1):
        surf.append(ax3d.plot_trisurf(x, y, triangles[events==1], z, color=tri_colors[1], **kwargs))
    if np.any(events==2):
        surf.append(ax3d.plot_trisurf(x, y, triangles[events==2], z, color=tri_colors[2], **kwargs))
    return surf



def wall(ax3d, lines2d, zmin=0, zmax=1, **kwargs):
    surf = list()
    for line2d in lines2d:
        x = line2d.get_xdata()
        y = line2d.get_ydata()
        _x = np.concatenate((x, x))
        _y = np.concatenate((y, y))
        _z = np.concatenate([np.full(len(x), zmin), np.full(len(x), zmax)])
        tri = mtri.Triangulation(_x, _z)
        triangles = tri.get_masked_triangles()
        surf.append(ax3d.plot_trisurf(_x, _y, _z, triangles=triangles, **kwargs))
    
    
