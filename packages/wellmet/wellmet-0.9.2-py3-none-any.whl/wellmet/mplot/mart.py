#!/usr/bin/env python
# coding: utf-8


#č nazvy proměnných jsou v angličtině
#č Ale komenty teda ne)

import numpy as np
import matplotlib.tri as mtri
import matplotlib.path as mpath
import matplotlib.colors as mcolor
import matplotlib.patches as mpatches

from .. import misc as wmisc

#č Tahlensta blbost je použita funkcí tripcolor()
#č Je třeba jú překopat na Triangulation třidu,
#č která get_events má jako svůj method.
def get_events(sb, simplices): #simplices = bx.tri.simplices
    """
    Metoda musí simplexům přiřazovat jev 
    0=success, 1=failure, 2=mix
    """
    in_failure = np.isin(simplices, sb.failure_points)
    has_failure = in_failure.any(axis=1)
    all_failure = in_failure.all(axis=1)
    return np.int8(np.where(has_failure, np.where(all_failure, 1, 2), 0))

#č napadlo mě, že bych mohl matplotlibovskému Axes
#č přiřazovat (připsavat, zadávat) atribut 'space'
#č Daválo by to smysl, ne? U všeho ostatního, u sample boksů
#č ne vždy na jedném sabplotu někdo potřebuje
#č kreslit z různejch prostoru.
#č Zkrátka, funkce v tomto modulu požadujou aby 
#č ax.space a ax.sample_box byl nastaven!

# ax.space and ax.sample_box attributes should (expected to) be set up!


def scatter_sample(ax, sample, **kwargs):
    xy = getattr(sample, ax.space)
    x, y = xy[:,:2].T
    return ax.scatter(x, y, **kwargs)

def plot_sample(ax, sample, *args, **kwargs):
    xy = getattr(sample, ax.space)
    x, y = xy[:,:2].T
    return ax.plot(x, y, *args, **kwargs)



def scatter_points(ax, **kwargs):
    xy = getattr(ax.sample_box, ax.space)
    nsim = len(xy)
    x, y = xy[:,:2].T
    
    failsi = ax.sample_box.failsi
    
    try: # proxy denotes to implicitly-known values
        proxy = ax.sample_box.proxy.astype(bool) 
    except AttributeError:
        proxy = np.full(nsim, False, dtype=bool)
    
    scatter_list = []
    
    #č byl jsem svědkem, že matplotlib zlobil ve 3D 
    #č kvůli tomu, že nebyl žádný safe vzorek
    #č proto raději budu přidávat tečky podmíněne
    mask = np.all((~failsi, ~proxy), axis=0)
    if np.any(mask): #success
        scatter_list.append(ax.scatter(x[mask], y[mask], c='g', marker='P', **kwargs))
    
    mask = np.all((failsi, ~proxy), axis=0)
    if np.any(mask): #failures
        scatter_list.append(ax.scatter(x[mask], y[mask], c='r', marker='X', **kwargs))
    
    mask = np.all((~failsi, proxy), axis=0)
    if np.any(mask): #proxy_successes
        scatter_list.append(ax.scatter(x[mask], y[mask], c='#77AC30', marker='h', **kwargs))
    
    mask = np.all((failsi, proxy), axis=0)
    if np.any(mask): #proxy_failures
        scatter_list.append(ax.scatter(x[mask], y[mask], c='#D95319', marker='H', **kwargs))
    
    return scatter_list # success, failures, proxy_successes, proxy_failures
    

def plot_points(ax, ls='', **kwargs):
    xy = getattr(ax.sample_box, ax.space)
    nsim = len(xy)
    x, y = xy[:,:2].T
    
    failsi = ax.sample_box.failsi
    
    try: # proxy denotes to implicitly-known values
        proxy = ax.sample_box.proxy.astype(bool) 
    except AttributeError:
        proxy = np.full(nsim, False, dtype=bool)
    
    plot_list = []
    
    #č byl jsem svědkem, že matplotlib zlobil ve 3D 
    #č kvůli tomu, že nebyl žádný safe vzorek
    #č proto raději budu přidávat tečky podmíněne
    mask = np.all((~failsi, ~proxy), axis=0)
    if np.any(mask): #success
        plot_list.append(ax.plot(x[mask], y[mask], mec='g', mfc='g',\
                         marker='P', ls=ls, **kwargs))
    
    mask = np.all((failsi, ~proxy), axis=0)
    if np.any(mask): #failures
        plot_list.append(ax.plot(x[mask], y[mask], mec='r', mfc='r',\
                         marker='X', ls=ls, **kwargs))
    
    mask = np.all((~failsi, proxy), axis=0)
    if np.any(mask): #proxy_successes
        plot_list.append(ax.plot(x[mask], y[mask], mec='#77AC30', mfc=(0,0,0,0),\
                         marker='h', ls=ls, **kwargs))
    
    mask = np.all((failsi, proxy), axis=0)
    if np.any(mask): #proxy_failures
        plot_list.append(ax.plot(x[mask], y[mask], mec='#D95319', mfc=(0,0,0,0),\
                         marker='H', ls=ls, **kwargs))
    
    return plot_list # success, failures, proxy_successes, proxy_failures


#č triplot - pokud ax.space == tri_space
#č tri_plot - pokud ax.space != Tri.tri_space
def tri_plot(ax, Tri=None, fmt='-', ns=100, **kwargs):
    if ax.sample_box.nvar == 2:
        lines = []
        
        if Tri is None:
            Tri = ax.sample_box.Tri
        
        # take coordinates in the space, where triangulation has been performed
        sampled_plan_tri = getattr(ax.sample_box, Tri.tri_space)
        
        #č mohli bychom zde machrovat se zkracenou smyčkou,
        #č mohli bychom jednoduše zavolat zabudovanou v matplotlib funkciju,
        #č my ale vůbec kontrolovat rovnost prostorů nebudeme, 
        #č nechť to dělá volající kód
        
        #if ax.space == Tri.tri_space:
        #   #return triplot(ax, **kwargs)
        #   
        #    #for simplex_id in simplex_ids:
        #    #    triangle = simplices[simplex_id]
        #    #    pos = sampled_plan_tri[triangle[[0,1,2,0]]]
             
        for triangle in Tri.tri.simplices:
            x_tri_1 = np.linspace(sampled_plan_tri[triangle[0],0], sampled_plan_tri[triangle[1],0], ns, endpoint=False)
            y_tri_1 = np.linspace(sampled_plan_tri[triangle[0],1], sampled_plan_tri[triangle[1],1], ns, endpoint=False)
            x_tri_2 = np.linspace(sampled_plan_tri[triangle[1],0], sampled_plan_tri[triangle[2],0], ns, endpoint=False)
            y_tri_2 = np.linspace(sampled_plan_tri[triangle[1],1], sampled_plan_tri[triangle[2],1], ns, endpoint=False)
            x_tri_3 = np.linspace(sampled_plan_tri[triangle[2],0], sampled_plan_tri[triangle[0],0], ns, endpoint=True)
            y_tri_3 = np.linspace(sampled_plan_tri[triangle[2],1], sampled_plan_tri[triangle[0],1], ns, endpoint=True)
            
            tri_bound_tri = np.concatenate(((x_tri_1, y_tri_1), (x_tri_2, y_tri_2), (x_tri_3, y_tri_3)), axis=1).T
            #č vytvořme sample
            tri_bound = ax.sample_box.f_model.new_sample(tri_bound_tri, space=Tri.tri_space)
            
            xy = getattr(tri_bound, ax.space)
            x, y = xy.T
            lines.append(ax.plot(x, y, fmt, **kwargs))
        
        return lines


#č triplot() jednoduše volá zabudovanou do matplotlibu funkci
def triplot(ax, **kwargs):
    xy = getattr(ax.sample_box, ax.space)
    x, y = xy[:,:2].T
    
    return ax.triplot(x, y, **kwargs)


def tripcolor(ax, sfm_colors=None, **kwargs):
    xy = getattr(ax.sample_box, ax.space)
    x, y = xy[:,:2].T
    tri = mtri.Triangulation(x, y)
    
    if sfm_colors is None:
        # make a color map of fixed colors
        s = '#a7ffb5' #'xkcd:light seafoam green' #a7ffb5
        f = '#fdc1c5' #'xkcd: pale rose' # (#fdc1c5)
        m = '#FFF39A' #'xkcd: dark cream' # (255, 243, 154, 255)
        sfm_colors = [s, f, m]
    
    if 'cmap' not in kwargs:
        # 0=success, 1=failure, 2=mix
        kwargs['cmap'] = mcolor.ListedColormap(sfm_colors)
    if 'norm' not in kwargs:
        kwargs['norm'] = mcolor.NoNorm()
    
    # same as facecolors
    C = get_events(ax.sample_box, tri.get_masked_triangles())
    
    #č tak to má bejt, aby MPL jednoznačně bral barvy jako barvy obličejů
    #č jenomže to může zlobit
    return ax.tripcolor(tri, facecolors=C, **kwargs)
    

def plot_boundaries(ax, fmt='-b', nrod=200, **kwargs):
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    limits = np.array([[xmin, ymin], [xmax, ymax]])
    bounds = ax.sample_box.get_2D_boundary(nrod=nrod, viewport_sample=limits,\
                                             viewport_space=ax.space)
    lines = []
    for bound in bounds:
        xy = getattr(bound, ax.space)
        x, y = xy[:,:2].T
        lines.append(ax.plot(x, y, fmt, **kwargs))
    
    return lines



def scatter_candidates(ax, **kwargs):
    """
    Plot all nodes series from ax.sample_box.candidates_index list.
    Function extracts ax.sample_box.potential attribute from nodes 
    and uses it for colormapping. 
    Max value is taken from ax.sample_box.highest_bid
    Returns nothing.
    example:
    scatter_candidates(ax, s=100.500, marker='.', cmap='plasma', alpha=0.5, linewidths=None, *, edgecolors=None, plotnonfinite=False)
    """
    potential = ax.sample_box.potential
    maxcb = ax.sample_box.highest_bid
    
    #č a teď jdeme!
    for id, cb in ax.sample_box.candidates_index.items():
        values = getattr(cb, potential)
        x, y = getattr(cb, ax.space)[:,:2].T
        ax.scatter(x, y, c=values, vmin=0, vmax=maxcb, **kwargs)


def plot_the_best_candidate(ax, *args, **kwargs):
    """
    Plots ax.sample_box.bidder node.
    Returns nothing.
    example:
    plot_the_best_candidate(ax, "^", color='green')
    """
    xy = getattr(ax.sample_box.bidder, ax.space)
    x, y = xy[:,:2].T
    return ax.plot(x, y, *args, **kwargs)



def simplex_vectors(ax, **kwargs):
    Tri = ax.sample_box.Tri
    if ax.space != Tri.tri_space:
        raise
    
    result = Tri.perform_sensitivity_analysis()
    vectors = result.vectors
    probabilities = result.shares
    
    ED = Tri.tri.points
    simplices = Tri.tri.simplices
    #pos = getattr(self.w.sample_box, self.w.space)[:,:2]
    
#    offsets = {}
#    for key, vector in result.unique_id_vectors.items():
#        offsets[key] = np.mean(Tri.get_finalized_supports(vector))
        
    
    X = []
    Y = []
    U = []
    V = []
    for simplex_id, vector in vectors.items():
        centroid = np.mean(ED[simplices[simplex_id]], axis=0)
        #offset_fix = (offsets[id(vector)] - np.inner(centroid, vector.normal))
        #placement = centroid + vector.normal * offset_fix
        x, y = centroid #placement
        X.append(x)
        Y.append(y)
        u, v = -vector.normal * probabilities[simplex_id]
        U.append(u)
        V.append(v)
    
    
    return ax.quiver(X, Y, U, V, **kwargs)



def qhull_polygon(ax, qhull, **kwargs):
    x, y = qhull.points[qhull.vertices].T
    return ax.fill(x, y, **kwargs)


                
def qhull_plot(ax, qhull=None, fmt='-', ns=100, **kwargs):
    if ax.sample_box.nvar == 2: #č jinak nic nedeláme
        if qhull is None:
            qhull = ax.sample_box.convex_hull
            
        if ax.space == qhull.space:
            points = qhull.points
            lines = []
            for simplex in qhull.simplices:
                xy = points[simplex]
                x, y = xy.T
                lines.append(ax.plot(x, y, fmt, **kwargs))
            return lines
        
        else:
            #оӵ кулэ ӧвӧл обновлять экран карыны
            sampled_plan_tri = qhull.points
            for simplex in qhull.simplices:
                start_id, end_id = simplex
                
                x_bound = np.linspace(sampled_plan_tri[start_id,0], sampled_plan_tri[end_id,0], ns, endpoint=True)
                y_bound = np.linspace(sampled_plan_tri[start_id,1], sampled_plan_tri[end_id,1], ns, endpoint=True)
                
                # sample compatible
                #оӵ малы транспонировать кароно? Озьы кулэ!
                bound_tri = np.vstack((x_bound, y_bound)).T
                #č vytvořme sample
                bound = ax.sample_box.f_model.new_sample(bound_tri, space=qhull.space)
                
                xy = getattr(bound, ax.space)
                x, y = xy.T
                lines.append(ax.plot(x, y, fmt, **kwargs))
                
            return lines



def dhull_plot(ax, hull, **kwargs):
    #č zatím uděláme jen pro 2D infinite lajny
    design_points = hull.get_design_points()
    lines = []
    if (hull.sample.nvar == 2) and (ax.space == hull.space):
        for equation in hull.equations:
            #č ve 2D bych očekával v rovnici pouze 3 hodnoty (já potřebuji směry)
            x, y, offset = equation
            design_point = [-x*offset, -y*offset] #č offset je prej zápornej
            slope = np.divide(-x, y)
            lines.append(ax.axline(design_point, slope=slope, **kwargs))
    return lines
            
def bhull_plot(ax, bhull, **kwargs):
    if ax.space == bhull.space:
        point = bhull.mins[:2]
        x1, y1 = point
        x2, y2 = bhull.maxs[:2]
        if 'fill' not in kwargs:
            kwargs['fill'] = False
        frame = mpatches.Rectangle(point, x2-x1, y2-y1, **kwargs)
        return ax.add_patch(frame) 

def shull_plot(ax, hull, **kwargs):
    from ..ghull import Ghull
    ghull = Ghull(hull)
    R = ghull.get_R()
    if 'fill' not in kwargs:
        kwargs['fill'] = False
    return gcircle(ax, r=R, **kwargs)


## DEPRECATED
## use qhull_plot instead
#def convex_plot(ax, fmt='-m', ns=100, qhull=None, **kwargs):
#    if ax.sample_box.nvar == 2: #č jinak nic nedeláme
#       if qhull is None:
#           simplices = ax.sample_box.convex_hull.simplices
#        else:
#           simplices = qhull.simplices
#        
#        if tri_space is None:
#           
#        # convex hull should be made in the same space as triangulation, 
#        # Will we take coordinates in the triangulation space, I guess?
#        sampled_plan_tri = getattr(ax.sample_box, ax.sample_box.tri_space)
#        
#        # hmm...
#        lines = []
#        if ax.space == ax.sample_box.tri_space:
#            for simplex in simplices:
#                xy = sampled_plan_tri[simplex]
#                x, y = xy.T
#                lines.append(ax.plot(x, y, fmt, **kwargs))
#                    
#    else:
#        #оӵ кулэ ӧвӧл обновлять экран карыны
#        for simplex in simplices:
#            start_id, end_id = simplex
#            
#            x_bound = np.linspace(sampled_plan_tri[start_id,0], sampled_plan_tri[end_id,0], ns, endpoint=True)
#            y_bound = np.linspace(sampled_plan_tri[start_id,1], sampled_plan_tri[end_id,1], ns, endpoint=True)
#            
#            # sample compatible
#            #оӵ малы транспонировать кароно? Озьы кулэ!
#            bound_tri = np.vstack((x_bound, y_bound)).T
#            #č vytvořme sample
#            bound = ax.sample_box.f_model.new_sample(bound_tri, space=ax.sample_box.tri_space)
#            
#            xy = getattr(bound, ax.space)
#            x, y = xy.T
#            lines.append(ax.plot(x, y, fmt, **kwargs))
#                
#                
#    return lines



def rbf_density_colormesh(ax, ngrid=500, **kwargs):
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    
    x = np.linspace(xmin, xmax, ngrid, endpoint=True)
    y = np.linspace(ymin, ymax, ngrid, endpoint=True)
    X, Y = np.meshgrid(x, y)
    
    XY = np.vstack((X.reshape(-1), Y.reshape(-1))).T
    z = ax.sample_box.sample_pdf(XY, ax.space)
    Z = z.reshape(ngrid, ngrid)
    
    #č s tou alphou mně to nějak nepovedlo
    #č matplotlib ji nějak ignoruje 
    #č a podle toho, co vidím v kódu
    #č není to problém kolormapy LinearSegmentedColormap
#    cdict = {'red':[[0.0,  253/255, 253/255],
#                   [0.9999,  253/255, 167/255],
#                   [1.0,  167/255, 167/255]],
#         'green': [[0.0,  193/255, 193/255],
#                   [0.9999,  193/255, 1.0],
#                   [1.0,  1.0, 1.0]],
#         'blue':  [[0.0,  197/255, 197/255],
#                   [0.9999,  197/255, 181/255],
#                   [1.0,  181/255, 181/255]],
#         'alpha':  [[0.0,  1.0, 1.0],
#                   [0.9999,  1.0, 0.2],
#                   [1.0,  0.2, 0.2]]}
    
    cdict = {'red':[[0.0,  1.0, 1.0],
                   [0.99999,  253/255, 167/255],
                   [1.0,  167/255, 167/255]],
         'green': [[0.0,  1.0, 1.0],
                   [0.99999,  0/255, 1],
                   [1.0,  1.0, 1.0]],
         'blue':  [[0.0,  1.0, 1.0],
                   [0.99999,  17/255, 181/255],
                   [1.0,  181/255, 181/255]]}
                   

    cmap = mcolor.LinearSegmentedColormap('red_density', segmentdata=cdict, N=2560)
    #cmap = mcolors.ListedColormap(['#A7FFB5', '#FDC1C5'])
    rbf_values = wmisc.RBF_surrogate(ax.sample_box, ax.space).rbf(X, Y)
    #Z = np.log(Z/np.max(Z[rbf_values <= 0]))
    #C = -Z/np.min(Z) * (rbf_values <= 0) + 1/250 * (rbf_values > 0)
    Z = Z / np.max(Z[rbf_values <= 0])
    C = (np.sqrt(Z)-1) * (rbf_values <= 0) + 1/250 * (rbf_values > 0)
    return ax.pcolormesh(X, Y, C, cmap=cmap, shading='nearest', edgecolors='face',
                        zorder=-100, rasterized=True, **kwargs)
    

def rbf_colormesh(ax, ngrid=500, **kwargs):
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    
    x = np.linspace(xmin, xmax, ngrid, endpoint=True)
    y = np.linspace(ymin, ymax, ngrid, endpoint=True)
    X, Y = np.meshgrid(x, y)

    cmap = mcolor.ListedColormap(['#A7FFB5', '#FDC1C5'])
    rbf_values = wmisc.RBF_surrogate(ax.sample_box, ax.space).rbf(X, Y)
    C = rbf_values < 0
    return ax.pcolormesh(X, Y, C, cmap=cmap, shading='nearest', zorder=-100, rasterized=True, **kwargs)



def gcircle(ax, r=1, nrod=200, **kwargs):
    if ax.space == 'G':
        circle = mpatches.Circle((0,0), r, **kwargs)
    else:
        sample = wmisc.get_isodistances(ax.sample_box.f_model, r, nrod=200)
        xy = getattr(sample, ax.space)[:,:2]
        circle = mpatches.Polygon(xy, **kwargs)
    
    #č vrací add_patch něco?
    return ax.add_patch(circle)


def uframe(ax, **kwargs):
    if ax.space in ('P', 'aP', 'U', 'aU'):
        alpha = ax.sample_box.alpha
        frame = mpatches.Rectangle((0,0), alpha[0], alpha[1], fill=False, **kwargs)
        return ax.add_patch(frame) 


def lsf_boundary(ax, ngrid=200, limits=None, **kwargs):
        
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
        
    if limits is not None: # G-čko zlobí
        lxmin, lxmax, lymin, lymax = limits
        xmin = min(xmin, lxmin)
        xmax = max(xmax, lxmax)
        ymin = min(ymin, lymin)
        ymax = max(ymax, lymax)
    
    x = np.linspace(xmin, xmax, ngrid)
    y = np.linspace(ymin, ymax, ngrid)
    X, Y = np.meshgrid(x, y)
    XY = np.vstack((X.reshape(-1), Y.reshape(-1))).T
    sb = ax.sample_box.gm(ax.sample_box.f_model.new_sample(XY, space=ax.space))
    Z = sb.g_values
    return ax.contour(X, Y, Z.reshape(ngrid, ngrid), np.zeros(1), **kwargs)


def isocurves(ax, ngrid=200, limits=None, ncurves=5, **kwargs):
    r = ncurves + 1 #č jakási rezerva, mám už plné zuby s těmi limity
    sample = wmisc.get_isodistances(ax.sample_box.f_model, r, nrod=ngrid)
    xy = getattr(sample, ax.space)[:,:2]
        
    xmin, ymin = np.min(xy, axis=0)
    xmax, ymax = np.max(xy, axis=0)
        
    if limits is not None: # G-čko zlobí
        lxmin, lxmax, lymin, lymax = limits
        xmin = min(xmin, lxmin)
        xmax = max(xmax, lxmax)
        ymin = min(ymin, lymin)
        ymax = max(ymax, lymax)
    
    x = np.linspace(xmin, xmax, ngrid)
    y = np.linspace(ymin, ymax, ngrid)
    X, Y = np.meshgrid(x, y)
    XY = np.vstack((X.reshape(-1), Y.reshape(-1))).T
    Z = ax.sample_box.f_model.sample_pdf(XY, ax.space)
    
    
    const = 1 / (xmax - xmin) / (ymax - ymin)
    r_levels = np.arange(ncurves) + 1
    levels = wmisc.isolevels_2d(Z, const, np.flip(r_levels), from_top=False)
    return ax.contour(X, Y, Z.reshape(ngrid, ngrid), levels, **kwargs)



def number_points(ax, **kwargs):
    points_coordinates = getattr(ax.sample_box, ax.space)[:,:2]
    x, y = points_coordinates.T
    labels = []
    for i in range(ax.sample_box.nsim):
        labels.append(ax.text(x[i], y[i], str(i+1), **kwargs))
    return labels


def center_spines(ax, lw=0.4):
    # Move the left and bottom spines to x = 0 and y = 0, respectively.
    ax.spines["left"].set_position(("data", 0))
    ax.spines["bottom"].set_position(("data", 0))
    
    # Show the left and bottom spines
    ax.spines["left"].set_visible(True)
    ax.spines["bottom"].set_visible(True)
    
    # Set up linewidth
    ax.spines["left"].set_linewidth(lw)
    ax.spines["bottom"].set_linewidth(lw)
    
    # Hide the top and right spines.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    # instead of black triangles ">k"/"^k"
    vertices = np.array([[0, 1], [5, 0], [0, -1], [0, 1]])
    right_arrow = {
            'marker': mpath.Path(vertices, codes=None, closed=True),
            'markerfacecolor': 'black',
            'markeredgecolor': 'black',
            'markersize': 15
            }
    
    vertices = np.array([[-1, 0], [0, 5], [1, 0], [-1, 0]])
    up_arrow = {
            'marker': mpath.Path(vertices, codes=None, closed=True),
            'markerfacecolor': 'black',
            'markeredgecolor': 'black',
            'markersize': 15
            }
    
    # Draw arrows (as markers) at the end of the axes.  In each
    # case, one of the coordinates (0) is a data coordinate (i.e., y = 0 or x = 0,
    # respectively) and the other one (1) is an axes coordinate (i.e., at the very
    # right/top of the axes).  Also, disable clipping (clip_on=False) as the marker
    # actually spills out of the axes.
    ax.plot(1, 0, **right_arrow, transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(0, 1, **up_arrow, transform=ax.get_xaxis_transform(), clip_on=False)

#č před použitím bude třeba skutečně naimportovat ticker
def fix_locator(ax, loc):
    loc_x = mpl.ticker.FixedLocator(loc)
    ax.xaxis.set_major_locator(loc_x)
    loc_y = mpl.ticker.FixedLocator(loc)
    ax.yaxis.set_major_locator(loc_y)

#č něco_kulatého
def curly(ax, linewidths=[0.7, 0.5, 0.4, 0.3, 0.2, 0.1], nrid=200, color='k', **kwargs):
    if ax.space in ('U', 'aU'):
        return None
        
    elif (ax.sample_box.nvar == 2) and (ax.space in ('Rn', 'aRn', 'R', 'aR', 'P', 'aP')):
        limits = (*ax.get_xlim(), *ax.get_ylim())
        isocurves(ax, ngrid=nrid, limits=limits, ncurves=len(linewidths),\
                     linewidths=np.flip(linewidths), colors=[color], **kwargs)
        
    else:
        for i, lw in zip(range(len(linewidths)), linewidths):
            gcircle(ax, r=i+1, nrod=nrid, color=color, linewidth=lw, fill=False)


def setup(ax, lw=0.4): #č šup
    #ax.set_xlabel('$x_{1}$')
    #ax.set_ylabel('$x_{2}$')
    
    #ax.set_frame_on(False) #č pak se mi nezobrazí osy
    ax.set_aspect(1)
    #ax.set_box_aspect(1)
    if ax.space in ('P', 'aP', 'U', 'aU'):
        ax.margins(0)
        #ax.set_frame_on(False)
        #uframe(ax, linewidth=lw) 
    else:
        center_spines(ax, lw)


def setup_labels(ax, x_label="$x_1$", y_label="$x_2~$", data_offset=1):
    if ax.space in ('P', 'aP', 'U', 'aU'):
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
    else:
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        text = ax.text(1, -data_offset / np.abs(ymin), x_label, ha='center',va='top',
                                             transform=ax.get_yaxis_transform())
        text.set_in_layout(False)
        text = ax.text(-data_offset / np.abs(xmin), 1, y_label, ha='right',va='center', 
                                        transform=ax.get_xaxis_transform())
        text.set_in_layout(False)


