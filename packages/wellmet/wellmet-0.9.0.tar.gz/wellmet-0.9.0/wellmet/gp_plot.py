#!/usr/bin/env python
# coding: utf-8

import PyGnuplot as gp
import os

# nikdo mi neuvěří, že by tohle postačílo a nebylo by nutné tohlensto furt úpravovat
def gp_plot(sample_box, space='R', terminal='png', filename=''):
    if not filename:
        filename = 'store/%s_%s_%s'%(sample_box.gm_signature, space, sample_box.nsim)
    if space in ['Rn', 'GK', 'G']:
        gp.c('set autoscale xy')
        gp.c('set size square')
        gp.c('set zeroaxis')
    elif space in ['P', 'U']:
        gp.c('set xrange [0:1]')
        gp.c('set yrange [0:1]')
        gp.c('set size square')
        #gp.c('set autoscale')
        gp.c('unset zeroaxis')
    else: # R teda?
        gp.c('set size noratio')
        gp.c('set autoscale')
        gp.c('unset zeroaxis')
        
    gp.c('set terminal ' + terminal)
    gp.c('set output "%s.%s"'%(filename, terminal))
    if os.name == 'posix':
        gp.c('set decimalsign locale "POSIX"')
    
    # legenda
    gp.c('unset key')
    
    # se mi zda, že gp bere data v řadcích
    f_name = "%s_failure.dat" % (filename)
    s_name = "%s_success.dat" % (filename)
    gp.s(getattr(sample_box.failure_samples, space).T, f_name)
    gp.s(getattr(sample_box.success_samples, space).T, s_name)
    
    
    # rozkaz, který předaváme gnuplotovi
    gp_plot = 'plot "%s" title "Success points" w p lc rgb "green", "%s" title "Failure points" w p lc rgb "red"' % (s_name, f_name)
    
    # Kružničky chcete?
    # Кружочки ннада?
    if space in ['Rn', 'G']:
        gp.c('set parametric')
        for i in range(5):
            lw = 2 - i*0.3
            gp_plot += ', cos(t)*%s,sin(t)*%s notitle w l lc rgb "black" lw %s'%(i+1, i+1, lw)
            
    # ne všichni majó definované hranice
    try:
        bounds = sample_box.get_2D_boundary()
    
        for i in range(len(bounds)):
            bound = getattr(bounds[i], space).T 
            gp.s(bound, "%s_boundary_%s.dat"%(filename, i+1))
            gp_plot += ', "%s_boundary_%s.dat" notitle w l lc rgb "blue"'%(filename, i+1)
    except AttributeError:
        pass
    
    # Plot!
    gp.c(gp_plot)



# nikdo mi neuvěří, že by tohle postačílo a nebylo by nutné tohlensto furt úpravovat
def plot(data2D, terminal='png', filename=''):
    if not filename:
        filename = 'store/plot_%s'%(len(data2D[0]))
        
    gp.c('set terminal ' + terminal)
    gp.c('set output "%s.%s"'%(filename, terminal))
    if os.name == 'posix':
        gp.c('set decimalsign locale "POSIX"')
    
    
    # se mi zda, že gp bere data v řadcích
    gp.s(data2D, filename+'.dat')
    
    # Plot!
    # rozkaz, který předaváme gnuplotovi
    gp.c('plot "%s.dat" ' % (filename))
