#!/usr/bin/env python
# coding: utf-8

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtWidgets
from pyqtgraph.Qt import QtCore


import numpy as np

#č vzdávám se.
#č quadpy tak se stavá povinnou závislostí
#č potrebuju pro HullEstimation widget
import quadpy 


from .. import estimation as stm
from .. import misc
from .. import sball
from .. import schemes
from .. import convex_hull as khull
#č pro mě je zvykem jako ghull označovat objekt třídy Ghull
#č nikoliv čerstvě oddelený modul
from ..ghull import Ghull, Shell_MC, Shell_IS, Shell_1DS
from . import qt_gui

    

class QtGuiPlot2D(qt_gui.QtGuiWindow):
    def initialize_central_widget(self):
        self.central_widget = pg.PlotWidget()
        self.central_widget.setBackground('w')
        self.px_size = 3.5
        self.ncircles = 5
        self.redraw_called.connect(self.central_widget.clear)
        

    
    def plot_setup(self):
        self.view_items = []
        self.view_items.append(BasePlotting(self))
        self.view_items.append(UnitCube(self))
        self.view_items.append(AspectLock(self))
        self.view_items.append(LastShot(self))
        self.view_items.append(BoxRecomendation(self))
        self.view_items.append(Numbers(self))
        self.view_items.append(Circles(self))
        self.view_items.append(Isocurves(self))
        self.view_items.append(Boundaries(self))
        self.view_items.append(ConvexHull2D(self))
        self.view_items.append(Arrows(self))
        self.view_items.append(Triangulation(self))
        
        
        

        dock = dock_r = QtWidgets.QDockWidget("Simplex-based pf estimation", self)
        dock.setWidget(FastSimplexEstimationWidget(self, dock))
        self.view.addAction(dock.toggleViewAction())
        self.dockables.append(dock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        
        
        dock = QtWidgets.QDockWidget("Tesselation-based pf estimation", self)
        dock.setWidget(VoronoiEstimationWidget(self, dock))
        self.view.addAction(dock.toggleViewAction())
        self.dockables.append(dock)
        #self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        self.tabifyDockWidget(dock_r, dock)
        
        
        #dock = QtWidgets.QDockWidget("Ghull", self)
        #dock.setWidget(HullEstimationWidget(self, dock))
        #self.view.addAction(dock.toggleViewAction())
        #self.dockables.append(dock)
        #self.tabifyDockWidget(dock_r, dock)
        
        #dock = QtWidgets.QDockWidget("Blackbox's candidates", self)
        #dock.setWidget(CandidatesWidget(self, dock))
        #self.view.addAction(dock.toggleViewAction())
        #self.dockables.append(dock)
        #self.tabifyDockWidget(dock_r, dock)





"""
==============
оӵ Суред люкет
č Kreslicí prvky
E Drawing items
=================
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""
        

class Series:
    def __init__(self, w, autoredraw=True):
        self.w = w
        self.w.space_changed.connect(self.space_update)
        self.w.redraw_called.connect(self._redraw)
        # redraw policy
        self.autoredraw = autoredraw
        self.items = {}


    def add_serie(self, sample, index=None, **plot_kwargs):
        plot_item = self._draw(sample, plot_kwargs)
        
        if index is None:
            index = len(self.items)
        elif index in self.items:
            # kind of update, then
            #č musíme korektně odebrat předchozí kresbu
            self.remove_item(index)
            
        self.items[index] = [sample, plot_item, plot_kwargs]
        return plot_item
    
    
    def _draw(self, sample, plot_dict):
        pos = getattr(sample, self.w.space)[:,:2]
        mask = np.all(np.isfinite(pos), axis=1)
        return self.w.central_widget.plot(pos[mask], **plot_dict)
        
        
    def clear(self):
        for item in self.items.values():
            __sample, plot_item, __plot_dict = item
            self.w.central_widget.removeItem(plot_item)
        self.items.clear()
     
    def remove_item(self, index):
        __sample, plot_item, __plot_dict = self.items.pop(index)
        self.w.central_widget.removeItem(plot_item)
            
            
    def hide(self, index=None):
        if index is None:
            for item in self.items.values():
                __sample, plot_item, __plot_dict = item
                plot_item.hide()
        else:
            __sample, plot_item, __plot_dict = self.items[index]
            plot_item.hide()
        
    def show(self, index=None):
        if index is None:
            for item in self.items.values():
                __sample, plot_item, __plot_dict = item
                plot_item.show()
        else:
            __sample, plot_item, __plot_dict = self.items[index]
            plot_item.show()
        
        
    def _redraw(self):
        if self.autoredraw:
            for item in self.items.values():
                sample, _invalid_plot_item, plot_dict = item
                item[1] = self._draw(sample, plot_dict)
        else:
            self.items.clear()
    
    
    def space_update(self):
        for item in self.items.values():
            sample, plot_item, __plot_dict = item
            
            pos = getattr(sample, self.w.space)[:,:2]
            mask = np.all(np.isfinite(pos), axis=1)
            plot_item.setData(pos[mask])
    
    

#č Kružničky chcete?
#ё Кружочки ннада?
#оӵ Гаусслэн котыресез
class Giracles(Series):
    def __init__(self, w, autoredraw=True, nrod=200):
        super().__init__(w, autoredraw)
        
        self.setup(nrod)

    def setup(self, nrod):
        phi = np.linspace(0, 6.283185307, nrod, endpoint=True)
        cos_phi = np.cos(phi)
        sin_phi = np.sin(phi)
        
        self.prebound = np.array((cos_phi, sin_phi)).T

    
    def add_circle(self, r=1, index=None, **plot_kwargs):
        f_model = self.w.sample_box.f_model
        sample_G = self.prebound * r
        sample = f_model.new_sample(sample_G, space='G', extend=True)
        return self.add_serie(sample, index=index, **plot_kwargs)
        



class InfiniteLines(Series):

    def add_line(self, space='G', index=None, **plot_kwargs):
        plot_item = self.w.central_widget.addLine(**plot_kwargs)
        if space == self.w.space:
            plot_item.show()
        else:
            plot_item.hide()
                
        if index is None:
            index = len(self.items)
        elif index in self.items:
            # kind of update, then
            #č musíme korektně odebrat předchozí kresbu
            self.remove_item(index)
            
        self.items[index] = [space, plot_item, plot_kwargs]
        return plot_item
    
    def _redraw(self):
        if self.autoredraw:
            for item in self.items.values():
                space, _invalid_plot_item, plot_dict = item
                item[1] = self.w.central_widget.addLine(**plot_dict)
        else:
            self.items.clear()
    
    
    def space_update(self):
        for item in self.items.values():
            space, plot_item, __plot_dict = item
            if space == self.w.space:
                plot_item.show()
            else:
                plot_item.hide()


"""
==============
у График люкет
č Grafické prvky
E Drawing modules
=================
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""


class BasePlotting:
    def __init__(self, w):
        self.w = w
        #self.w.box_runned.connect(self.redraw) #č dublikuje slice_changed
        self.w.space_changed.connect(self.plot)
        self.w.slice_changed.connect(self.plot)
        self.w.redraw_called.connect(self.redraw)
        
    
    def redraw(self):
        plot_widget = self.w.central_widget
        #size=self.w.px_size*1.5
        pos = () #np.empty((nsim, 4))
        size = self.w.px_size * 2
        self.failures = plot_widget.plot(pos, pen=None, symbol='x', symbolPen='r',\
                    symbolSize=size*1.5,  name='Failures') # symbolBrush=0.2,
        self.failures.setZValue(100)
        
        self.proxy_failures = plot_widget.plot(pos, pen=None, symbol='p', symbolPen=0.5,\
                symbolSize=size, symbolBrush=(217,83,25), name='Proxy failures')
        self.proxy_failures.setZValue(95)
        
        self.successes = plot_widget.plot(pos, pen=None, symbol='+', \
                    symbolSize=size*1.5, symbolPen='g',  name='Successes')
        self.successes.setZValue(90)
        
        self.proxy_successes = plot_widget.plot(pos, pen=None, symbol='p', symbolPen=0.5, \
                symbolSize=size, symbolBrush=(119,172,48), name='Proxy successes')
        self.proxy_successes.setZValue(85)
        
        
        self.nodes = plot_widget.plot(pos, pen=None, symbol='o', symbolPen=0.5, \
                symbolSize=size, name='Nodes')
        self.nodes.setZValue(80)
        
        self.plot()
        
    def plot(self):
        nsim = self.w.slider.value()
        
        sample_box = self.w.sample_box[:nsim]
        
        pos = getattr(sample_box, self.w.space)[:,:2]
        if hasattr(sample_box, 'failsi'): #č to je normálně sample_box
            failsi = sample_box.failsi
            
            try: # proxy denotes to implicitly-known values
                proxy = sample_box.proxy.astype(bool)
            except AttributeError:
                proxy = np.full(nsim, False, dtype=bool)
            
            mask = np.all((failsi, ~proxy), axis=0)
            self.draw(self.failures, pos[mask])
            
            mask = np.all((~failsi, ~proxy), axis=0)
            self.draw(self.successes, pos[mask])
            
            mask = np.all((failsi, proxy), axis=0)
            self.draw(self.proxy_failures, pos[mask])
            
            mask = np.all((~failsi, proxy), axis=0)
            self.draw(self.proxy_successes, pos[mask])
            
        else: #č není to teda sample_box... 
            #č snad se nám povede nakreslit aspoň tečky?
            self.draw(self.nodes, pos)
        
            
    @staticmethod
    def draw(plot_item, data):
        #č musím to udělat takhle
        #č jinač to zlobí při posunutích slajderu
        if len(data):
            plot_item.setData(data)
            plot_item.show()
        else:
            plot_item.hide()




class Numbers:
    def __init__(self, w):
        
        self.w = w
        self.w.slice_changed.connect(self.replot)
        self.w.space_changed.connect(self.replot)
        self.w.redraw_called.connect(self.redraw)

        self.item = QtWidgets.QListWidgetItem('Numbers')
        self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.item.setCheckState(QtCore.Qt.Unchecked)
        self.w.list_view.addItem(self.item)

        
        self.w.list_view.itemChanged.connect(self.show_slot)
            
        
        

    def redraw(self):
        self.plot_items = []
        self.replot()


    def show_slot(self, item):
        if item is self.item:
            if self.item.checkState():
                #for item in self.plot_items:
                #    item.show()
                
                #оӵ Мед сюредалоз!
                self.replot()
                
            else: #оӵ Медам сюреда!
                for item in self.plot_items:
                    item.hide()
            

    
    def replot(self):
        """
        on space_chainged
        or something like this
        when we need to completely
        redraw
        """
        if self.item.checkState():
            nsim = self.w.slider.value()
            sample = self.w.sample_box.f_model[:nsim]
            pos = getattr(sample, self.w.space)[:,:2]
            
            plot_widget = self.w.central_widget
            
            for i in range(min(nsim, len(self.plot_items))):
                self.plot_items[i].setPos(*pos[i])
                self.plot_items[i].show()
            
            if len(self.plot_items) < nsim:
                for i in range(len(self.plot_items), nsim):
                    item = pg.TextItem(str(i))
                    plot_widget.addItem(item)
                    item.setPos(*pos[i])
                    self.plot_items.append(item)
            else:
                for i in range(nsim, len(self.plot_items)):
                    self.plot_items[i].hide()
            


class Arrows:
    def __init__(self, w):
        self.w = w
        if self.w.sample_box.nvar == 2:
            self.w.box_runned.connect(self.replot)
            self.w.space_changed.connect(self.replot)
            self.w.redraw_called.connect(self.redraw)
    
            self.item = QtWidgets.QListWidgetItem('Simplex arrows')
            self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
            self.item.setCheckState(QtCore.Qt.Unchecked)
            self.w.list_view.addItem(self.item)
    
            self.w.list_view.itemChanged.connect(self.show_slot)
        

    def redraw(self):
        self.plot_items = []
        self.replot()


    def show_slot(self, item):
        if item is self.item:
            if self.item.checkState():
                #for item in self.plot_items:
                #    item.show()
                
                #оӵ Мед сюредалоз!
                self.replot()
                
            else: #оӵ Медам сюреда!
                for item in self.plot_items:
                    item.hide()
            

    
    def replot(self):
        """
        on space_chainged
        or something like this
        when we need to completely
        redraw
        """
        if self.item.checkState():
            try: #оӵ Мед сюредалоз!
                if self.w.space != self.w.sample_box.Tri.tri_space:
                    return
                
                result = self.w.sample_box.Tri.perform_sensitivity_analysis()
                
                vectors = result.vectors
                
                nmixed = len(vectors)
                points = self.w.sample_box.Tri.tri.points
                simplices = self.w.sample_box.Tri.tri.simplices
                #pos = getattr(self.w.sample_box, self.w.space)[:,:2]
                
                
                plot_widget = self.w.central_widget
                
                for i in range(min(nmixed, len(self.plot_items))):
                    simplex_id, vector = vectors.popitem()
                    centroid = np.mean(points[simplices[simplex_id]], axis=0)
                    #probability = probabilities[simplex_id]
                    self.plot_items[i].setStyle(angle=self.get_angle(vector.normal))
                    self.plot_items[i].setPos(*centroid)
                    self.plot_items[i].show()
                
                if len(vectors):
                    for simplex_id, vector in vectors.items():
                        item = pg.ArrowItem(angle=self.get_angle(vector.normal), 
                                            tailLen=40, brush='gray')
                        plot_widget.addItem(item)
                        centroid = np.mean(points[simplices[simplex_id]], axis=0)
                        item.setPos(*centroid)
                        self.plot_items.append(item)
                else:
                    for i in range(nmixed, len(self.plot_items)):
                        self.plot_items[i].hide()
                
                    
            except BaseException as e:
                msg = "error during update"
                print(self.__class__.__name__ + ":",msg, repr(e))
                
                
                
                
    @staticmethod                
    def get_angle(vector):
        x, y = -vector 
        return np.rad2deg(np.arccos(x)) * -np.sign(y)






class UnitCube:
    def __init__(self, w):
        self.w = w
        self.w.space_changed.connect(self.plot)
        self.w.redraw_called.connect(self.redraw)
        

    def redraw(self):
        plot_widget = self.w.central_widget
        self.frame = plot_widget.plot(pos=(), pen='k')
        self.plot()
        

    def plot(self):
        if self.w.space in ('P', 'U'):
            self.frame.setData((0,0,1,1,0), (0,1,1,0,0))
            self.frame.show()
        elif self.w.space in ('aP', 'aU'):
            x, y, *__ = (*self.w.sample_box.alpha,)
            self.frame.setData((0,0,x,x,0), (0,y,y,0,0))
            self.frame.show()
        else:
            self.frame.hide()






class AspectLock:
    def __init__(self, w):
        self.w = w

        self.item = QtWidgets.QListWidgetItem('Equal aspect')
        self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.item.setCheckState(QtCore.Qt.Checked)
        self.w.central_widget.setAspectLocked(lock=True, ratio=1)
        self.w.list_view.addItem(self.item)
        self.w.list_view.itemChanged.connect(self.set_aspect)

    def set_aspect(self):
        plot_widget = self.w.central_widget
        if self.item.checkState():
            plot_widget.setAspectLocked(lock=True, ratio=1)
        else:
            plot_widget.setAspectLocked(lock=False, ratio=1)
            
            


class LastShot:
    def __init__(self, w):
        self.w = w
        self.w.box_runned.connect(self.plot)
        self.w.space_changed.connect(self.plot)
        self.w.redraw_called.connect(self.redraw)

        self.item = QtWidgets.QListWidgetItem('Last point')
        self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.item.setCheckState(QtCore.Qt.Checked)
        self.w.list_view.addItem(self.item)
        self.w.list_view.itemChanged.connect(self.show_slot)
        
    def show_slot(self, item):
        if item is self.item:
            self.plot()

    def redraw(self):
        pos = ()
        plot_widget = self.w.central_widget
        self.last = plot_widget.plot(pos, pen=None, symbol='o', symbolPen='c',  name='Last point', symbolBrush=None)
        self.shot = plot_widget.plot(pos, pen=None, symbol='+', symbolPen='c',  name='Last point')
        self.last.setZValue(110)
        self.shot.setZValue(110)
        
        self.plot()

    def plot(self):
        if self.item.checkState() and (self.w.last_shot is not None):
            pos = getattr(self.w.last_shot, self.w.space)[:,:2]
            self.last.setData(pos)
            self.shot.setData(pos)
            self.last.show()
            self.shot.show()
        else:
            self.last.hide()
            self.shot.hide()



class BoxRecomendation:
    def __init__(self, w):
        self.w = w
        self.w.box_runned.connect(self.plot)
        self.w.space_changed.connect(self.plot)
        self.w.redraw_called.connect(self.redraw)

        self.item = QtWidgets.QListWidgetItem('Next point')
        self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.item.setCheckState(QtCore.Qt.Unchecked)
        self.w.list_view.addItem(self.item)
        self.w.list_view.itemChanged.connect(self.show_slot)
        
    def show_slot(self, item):
        if item is self.item:
            self.plot()

    def redraw(self):
        pos = ()
        plot_widget = self.w.central_widget
        self.next = plot_widget.plot(pos, pen=None, symbol='t1', symbolPen='c',  name='Next point')
        self.next.setZValue(111)
        
        self.plot()

    def plot(self):
        if self.item.checkState():
            next_node = self.w.sample_box.dicebox()
            pos = getattr(next_node, self.w.space)[:,:2]
            self.next.setData(pos)
            self.next.show()
        else:
            self.next.hide()



#č Kružničky chcete?
#ё Кружочки ннада?
class Circles:
    def __init__(self, w):
        self.w = w
        self.w.space_changed.connect(self.plot)
        self.w.redraw_called.connect(self.redraw)
        
        self.name = 'Circles'
        self.item = QtWidgets.QListWidgetItem(self.name)
        self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.item.setCheckState(QtCore.Qt.Checked)
        self.w.list_view.addItem(self.item)
        self.w.list_view.itemChanged.connect(self.show_slot)
        
        self.color = 'k'
        self.z_value = -1

    def redraw(self):
        pos = ()
        plot_widget = self.w.central_widget
        
        self.circles = []
        ncircles = self.w.ncircles
        for r in range(ncircles):
            pen = pg.mkPen(color=self.color, width=self.w.px_size*(1-r/ncircles))
            circle = plot_widget.plot(pos=pos, pen=pen, name=self.name)
            circle.setZValue(self.z_value)
            self.circles.append(circle)
        
        self.plot()
        
    def show_slot(self, item):
        if item is self.item:
            self.plot()

    def plot(self):
        if self.item.checkState():
            
            f_model = self.w.sample_box.f_model
            
            nrod = 200
            phi = np.linspace(0, 6.283185307, nrod, endpoint=True)
            cos_phi = np.cos(phi)
            sin_phi = np.sin(phi)
            for i in range(len(self.circles)):
                r = i + 1
                bound_x = r * cos_phi
                bound_y = r * sin_phi
                
                
                #оӵ малы транспонировать кароно? Озьы кулэ!
                bound = np.array((bound_x, bound_y)).T
                f = f_model.new_sample(bound, space='G', extend=True)
                pos = getattr(f, self.w.space)[:,:2]
                self.circles[i].setData(pos)
                self.circles[i].show()
            
        else:
            for circle in self.circles:
                circle.hide()


class Isocurves:
    def __init__(self, w):
        self.w = w
        self.w.space_changed.connect(self.on_space_changed)
        self.w.redraw_called.connect(self.redraw)

        self.contour_item = QtWidgets.QListWidgetItem('Isolevels') # Density contours
        self.contour_item.setFlags(self.contour_item.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.contour_item.setCheckState(QtCore.Qt.Unchecked)
        self.w.list_view.addItem(self.contour_item)
        
        self.isocurve_item = QtWidgets.QListWidgetItem('Isocurves') 
        self.isocurve_item.setFlags(self.isocurve_item.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.isocurve_item.setCheckState(QtCore.Qt.Unchecked)
        self.w.list_view.addItem(self.isocurve_item)
        
        self.w.list_view.itemChanged.connect(self.show_slot)
        
        self.z_value = 1
        self.ngrid = 300

    def redraw(self):
        self.curves = []
        if self.contour_item.checkState() or self.isocurve_item.checkState():
            #č nejdřív data
            f_model = self.w.sample_box.f_model
           
            ns = 100 #č levný IS
            sample = np.random.randn(ns, 2)*3
            self.f = f_model.new_sample(sample, space='G', extend=True)
            
            self.on_space_changed()
           
    def on_space_changed(self):
        if self.contour_item.checkState() or self.isocurve_item.checkState():
            points = getattr(self.f, self.w.space)
                
            #č valčím s nekoněčno
            mask = np.all(np.isfinite(points), axis=1)
            
            self.max = np.max(points[mask], axis=0)
            self.min = np.min(points[mask], axis=0)
    
            ngrid = self.ngrid
            grid = np.mgrid[0:ngrid,0:ngrid].T.reshape(-1, 2)
            # scale
            grid = self.grid_scale(grid)
        
            f_model = self.w.sample_box.f_model
            self.pdf = f_model.sample_pdf(grid, space=self.w.space)
            #č pokud tam budou nanka, pak nikdo nic nedostane
            #č u současných f_modelů však nemají být
            self.pdf = np.nan_to_num(self.pdf, copy=False)
            #č reshape, flip a rot90 dle dokumentaci vracej view
            #č povede-li to numpy, data nebudou žrat další místo v paměti
            self.data = self.pdf.reshape((ngrid, ngrid))
            #č bůhví co ta pomocná funkce očekává za vstup
            #č a co je zvykem u těch borců co pracujou s obrázky 
            #č zkrátka, empiricky - buď zde flipnout a pootočit
            #č nebo tam dále prohodit souřadnice
            self.data = np.flip(self.data, axis=0)
            self.data = np.rot90(self.data, k=-1)
            
                
            self.plot()
            
        
    def show_slot(self, item):
        #č ne že by to bylo úplně ideální, ale ponechám dva druhy isočár sdruženými
        #č společný plot, společný redraw a společné self.curves
        if (item is self.contour_item) or (item is self.isocurve_item):
            if 'f' in self.__dict__:
                self.plot()
            else:
                self.redraw()
    
    def grid_scale(self, grid):
        # scale
        _grid = grid * (self.max - self.min) / (self.ngrid-1)
        # loc
        _grid = _grid + self.min
        return _grid
    
    def plot(self):
        #č zejmena tady je to nepříjemný
        #č třeba bude překreslovat jednu položky
        #č když jen odcvaknutá druhá
        for curve in self.curves:
            self.w.central_widget.removeItem(curve)
        
        ncurves = self.w.ncircles
        if self.contour_item.checkState():
            levels = np.linspace(self.pdf.max(), 0, ncurves+1, endpoint=False)[1:]
            self._draw_curves(levels, 'Isolevels', (170, 85, 0))
            
        if self.isocurve_item.checkState():
            const = 1 / np.prod(self.max - self.min)
            r_levels = np.arange(ncurves) + 1
            #č P prostor doopravdy zlobí, takže nějak tak    
            levels = misc.isolevels_2d(self.pdf, const, r_levels, from_top=False)
            self._draw_curves(levels, 'Isocurves', (100, 45, 0))
            
    def _draw_curves(self, levels, name, color):
        ncurves = self.w.ncircles
        plot_widget = self.w.central_widget
        for r in range(ncurves):
            pen = pg.mkPen(color=color, width=self.w.px_size*(1-r/ncurves))
            
            v = levels[r]
            
            #č vrací souřadnice v prostoru "gridu"
            lines = pg.functions.isocurve(self.data, v, connected=True)
            for line in lines:
                grid = np.array(line) 
                #grid = np.flip(grid, axis=1)
                
                #č tady mám výsledek dvouletého výzkumu
                grid = grid - 0.5
                
                # scale
                grid = self.grid_scale(grid) 
                curve = plot_widget.plot(grid, pen=pen, name=name)
                curve.setZValue(self.z_value)
                self.curves.append(curve)



class Boundaries:
    def __init__(self, w):
        self.w = w
        self.w.space_changed.connect(self.plot)
        self.w.redraw_called.connect(self.redraw)

        self.item = QtWidgets.QListWidgetItem('Boundaries')
        self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.item.setCheckState(QtCore.Qt.Checked)
        self.w.list_view.addItem(self.item)
        self.w.list_view.itemChanged.connect(self.show_slot)
        

    def redraw(self):
        pos = ()
        plot_widget = self.w.central_widget
        
        self.bounds = []
        # ne všichni majó definované hranice
        try:
            for bound in self.w.sample_box.get_2D_boundary(nrod=1000):
                item = plot_widget.plot(pos=pos, pen='b', name='Boundaries')
                item.setZValue(70)
                self.bounds.append((bound, item))
        except AttributeError:
            pass #print("čo sa děje?")
        
        self.plot()
        
    def show_slot(self, item):
        if item is self.item:
            self.plot()

    def plot(self):
        if self.item.checkState():
            for bound, item in self.bounds:
                pos = getattr(bound, self.w.space)[:,:2]
                mask = np.all(np.isfinite(pos), axis=1)
                item.setData(pos[mask])
                item.show()
            
        else:
            for bound, item in self.bounds:
                item.hide()




class Triangulation:
    def __init__(self, w):
        
        self.w = w
        if self.w.sample_box.nvar == 2:
            self.w.box_runned.connect(self.update)
            self.w.space_changed.connect(self.replot)
            self.w.redraw_called.connect(self.redraw)
    
            self.item = QtWidgets.QListWidgetItem('Triangulation')
            self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
            self.item.setCheckState(QtCore.Qt.Unchecked)
            self.w.list_view.addItem(self.item)
    
            
            self.w.list_view.itemChanged.connect(self.show_slot)
            
            self.spatial = 'tri'
        
        

    def redraw(self):
        self.simplices = np.empty((0,3), dtype=int)
        self.plot_items = []
        self.replot()


    def show_slot(self, item):
        if item is self.item:
            if (self.w.sample_box.nvar==2) and self.item.checkState():
                #for item in self.plot_items:
                #    item.show()
                
                #оӵ Мед сюредалоз!
                self.replot()
                
            else: #оӵ Медам сюреда!
                for item in self.plot_items:
                    item.hide()
            

    
    def replot(self):
        """
        on space_chainged
        or something like this
        when we need to completely
        redraw the triangulation
        """
        if self.item.checkState():
            try:
                spatial = getattr(self.w.sample_box, self.spatial)
                self.simplices = spatial.simplices
                for item in self.plot_items:
                    item.hide()
                self.draw_simplices(range(len(self.simplices)))
                    
            except BaseException as e:
                msg = "error during replot"
                print(self.__class__.__name__ + ":",msg, repr(e))
            


    def update(self):
        # update triangulation
        if self.item.checkState():
            try: #оӵ Мед сюредалоз!
                former_simplices = self.simplices 
                spatial = getattr(self.w.sample_box, self.spatial)
                self.simplices = spatial.simplices
                
                #č počet simplexů může se přidaním bodů změnšit
                #č (hlavně u ConvexHull, ale coplanar taky může vyskočit)
                if len(self.simplices) < len(former_simplices):
                    self.replot()
                else:
                    #č zkontrolujeme co se změnilo
                    equal_mask = former_simplices == self.simplices[:len(former_simplices)]
                    changed_simplices_ids = np.argwhere(~equal_mask.all(axis=1)).reshape(-1)
                    self.draw_simplices(changed_simplices_ids)
                    
                    #č teď nové simplexy
                    #ё simplexy свежего разлива
                    self.draw_simplices(range(len(former_simplices), len(self.simplices)))
                    
            except BaseException as e:
                msg = "error during update"
                print(self.__class__.__name__ + ":",msg, repr(e))
        
    
                
    
    def set_plot_data(self, pos, simplex_id):
        if simplex_id < len(self.plot_items):
            # Update the data
            plot_item = self.plot_items[simplex_id]
            plot_item.setData(pos)
            plot_item.show()
        else: #č spolehám na korektnost volajícího kódu
            #оӵ Суредасько
            plot_widget = self.w.central_widget
            plot_item = plot_widget.plot(pos, pen=0.7)
            self.plot_items.append(plot_item)
                
    
    #č já jsem tu všecko překopal protože .plot() a .setData() jsou nejžravejší na čas
    #č a nemá žádnou cenu je provadet hned vedle sebe (spouští totéž dvakrát)
    def draw_simplices(self, simplex_ids):
        # take coordinates in the space, where triangulation has been performed
        sampled_plan_tri = getattr(self.w.sample_box, self.w.sample_box.tri_space)
        
        if self.w.space == self.w.sample_box.tri_space:
            for simplex_id in simplex_ids:
                triangle = self.simplices[simplex_id]
                pos = sampled_plan_tri[triangle[[0,1,2,0]]]
                
                self.set_plot_data(pos, simplex_id)
                    
        else:
            ns = 100
            with pg.BusyCursor():
                for simplex_id in simplex_ids:
                    triangle = self.simplices[simplex_id]
                    # keep the GUI responsive :)
                    # it was quite slow on my target machine
                    self.w.app.processEvents()
                    
                    x_tri_1 = np.linspace(sampled_plan_tri[triangle[0],0], sampled_plan_tri[triangle[1],0], ns, endpoint=False)
                    y_tri_1 = np.linspace(sampled_plan_tri[triangle[0],1], sampled_plan_tri[triangle[1],1], ns, endpoint=False)
                    x_tri_2 = np.linspace(sampled_plan_tri[triangle[1],0], sampled_plan_tri[triangle[2],0], ns, endpoint=False)
                    y_tri_2 = np.linspace(sampled_plan_tri[triangle[1],1], sampled_plan_tri[triangle[2],1], ns, endpoint=False)
                    x_tri_3 = np.linspace(sampled_plan_tri[triangle[2],0], sampled_plan_tri[triangle[0],0], ns, endpoint=True)
                    y_tri_3 = np.linspace(sampled_plan_tri[triangle[2],1], sampled_plan_tri[triangle[0],1], ns, endpoint=True)
                    
                    tri_bound_tri = np.concatenate(((x_tri_1, y_tri_1), (x_tri_2, y_tri_2), (x_tri_3, y_tri_3)), axis=1).T
                    #č vytvořme sample
                    tri_bound = self.w.sample_box.f_model.new_sample(tri_bound_tri, space=self.w.sample_box.tri_space)
                    pos = getattr(tri_bound, self.w.space)
                    
                    self.set_plot_data(pos, simplex_id)
                



class ConvexHull2D(Triangulation):
    def __init__(self, w):
        
        self.w = w
        if self.w.sample_box.nvar == 2:
            self.w.box_runned.connect(self.update)
            self.w.space_changed.connect(self.replot)
            self.w.redraw_called.connect(self.redraw)
    
            self.item = QtWidgets.QListWidgetItem('Convex hull')
            self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
            self.item.setCheckState(QtCore.Qt.Checked)
            self.w.list_view.addItem(self.item)
    
            
            self.w.list_view.itemChanged.connect(self.show_slot)
            
            self.spatial = 'convex_hull'
        
        

    def redraw(self):
        self.simplices = np.empty((0,2), dtype=int)
        self.plot_items = []
        self.replot()

        
                
                
    
    #č já jsem tu všecko překopal protože .plot() a .setData() jsou nejžravejší na čas
    #č a nemá žádnou cenu je provadet hned vedle sebe (spouští totéž dvakrát)
    def draw_simplices(self, simplex_ids):
        
        # convex hull should be made in the same space as triangulation, I guess
        # take coordinates in the triangulation space
        sampled_plan_tri = getattr(self.w.sample_box, self.w.sample_box.tri_space)
        
        plot_widget = self.w.central_widget
        
        if self.w.space == self.w.sample_box.tri_space:
            for simplex_id in simplex_ids:
                pos = sampled_plan_tri[self.simplices[simplex_id]]
                
                self.set_plot_data(pos, simplex_id)
                    
        else:
            ns = 100
            #оӵ кулэ ӧвӧл обновлять экран карыны
            for simplex_id in simplex_ids:
                start_id, end_id = self.simplices[simplex_id]
                
                x_bound = np.linspace(sampled_plan_tri[start_id,0], sampled_plan_tri[end_id,0], ns, endpoint=True)
                y_bound = np.linspace(sampled_plan_tri[start_id,1], sampled_plan_tri[end_id,1], ns, endpoint=True)
                
                # sample compatible
                #оӵ малы транспонировать кароно? Озьы кулэ!
                bound_tri = np.vstack((x_bound, y_bound)).T
                #č vytvořme sample
                bound = self.w.sample_box.f_model.new_sample(bound_tri, space=self.w.sample_box.tri_space)
                pos = getattr(bound, self.w.space)
                
                self.set_plot_data(pos, simplex_id)


    
        
"""
=============
Эскерон виӝет 
Widgety odhadů
Estimation widgets
===================
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""

class FastSimplexEstimationWidget(QtWidgets.QSplitter):
    # I'd like to get access to the samplebox stuff via the container's reference, 
    def __init__(self, samplebox_item,  parent=None, *args, **kwargs):
        super().__init__(parent)
        # sb like samplebox, of course
        self.sb_item = samplebox_item
        
        self.sb_item.box_runned.connect(self.on_box_run)
        self.sb_item.slice_changed.connect(self.self_clear)
        self.sb_item.space_changed.connect(self.on_space_changed)
        self.sb_item.redraw_called.connect(self.redraw)
        #☺ na internetu všichni tak dělaj
        self.setup()
        
    def setup(self):
        self.setOrientation(QtCore.Qt.Vertical)
        self.layout = pg.LayoutWidget(self)
        params = list()
        params.append({'name': 'method', 'type': 'list', \
                     'values': ['fast_sampling', 'full_sampling',\
                      'fast_cubature', 'full_cubature'], 'value': 'fast_sampling'})
        params.append({'name': 'model space', 'type': 'list', \
                        'values': self.sb_item.spaces, 'value': 'Rn'})
        params.append({'name': 'sampling space', 'type': 'list',\
                        'values': ['None'] + self.sb_item.spaces, 'value': 'None'})
        params.append({'name': 'weighting space', 'type': 'list',\
                        'values': ['None'] + self.sb_item.spaces, 'value': 'None'})
        designs = ['None']
        if 'designs' in self.sb_item.kwargs:
            designs.extend(self.sb_item.kwargs['designs'].keys())
        params.append({'name': 'design', 'type': 'list', \
                     'values': designs, 'value': 'None'})
        params.append({'name': 'outside budget', 'type': 'int', \
                    'limits': (1, float('inf')), 'value': 1000, 'default': 1000})    
        params.append({'name': 'nodes per simplex', 'type': 'int', \
                    'limits': (1, float('inf')), 'value': 100, 'default': 100})  
            
        ##ё костыли        
        #if 'schemes' not in self.sb_item.kwargs:
        #    self.sb_item.kwargs['schemes'] = schemes.get_all_tn_simplex_schemes(self.sb_item.sample_box.nvar)
        #schema = list(self.sb_item.kwargs['schemes'].keys())
        
        tschemes = ['None'] + schemes.get_tn_keys(self.sb_item.sample_box.nvar)
            
        params.append({'name': 'scheme', 'type': 'list', \
                     'title': "cubature scheme", \
                     'values': tschemes, 'value': tschemes[0]})
        params.append({'name': 'degree', 'type': 'int', \
                    'title': "degree",\
                    'limits': (0, float('inf')), 'value': 5, 'default': 5,\
                    'tip': "Used only with Grundmann-Möller and Silvester cubaturas"})
        params.append({'name': 'node (pixel) size', 'type': 'float',\
                 'limits': (0, float('inf')), 'value': 3.5, 'default': self.sb_item.px_size})
        xkcd_green = (167, 255, 181, 255) # xkcd:light seafoam green #a7ffb5
        xkcd_red   = (253, 193, 197, 255) # xkcd: pale rose (#fdc1c5)
        xkcd_cream = (255, 243, 154, 255) # let's try xkcd: dark cream (#fff39a)
        params.append({'name': 'failure', 'type': 'colormap', \
                        'value': pg.colormap.ColorMap((0,1), [xkcd_red, xkcd_red])})
        params.append({'name': 'success', 'type': 'colormap', \
                        'value': pg.colormap.ColorMap((0,1), [xkcd_green, xkcd_green])})
        params.append({'name': 'mix', 'type': 'colormap', \
                        'value': pg.colormap.ColorMap((0,1), [xkcd_cream, xkcd_cream])})
        params.append({'name': 'Run with the box', 'type': 'bool', 'value': False }) # 'tip': "This is a checkbox"
        
        ### Create tree of Parameter objects
        self.param = pg.parametertree.Parameter.create(name='params', type='group', children=params)
        # I don't know why that signals do not work for me
        # Only sigTreeStateChanged works, but I don't want to struggle with it
        # May be I'll report the issue 
        #self.param.sigValueChanged.connect(self.param_changed)
        #self.param.sigValueChanging.connect(self.param_changing)
        
        ### Create ParameterTree widget
        self.ptree = pg.parametertree.ParameterTree()
        self.ptree.setParameters(self.param, showTop=False)
        
        self.layout.addWidget(self.ptree, row=0, col=0, colspan=4)
        
        
        
        self.btn0 = QtWidgets.QPushButton('(no graphics)') # 'estimate \n (no graphics)'
        self.layout.addWidget(self.btn0, row=1, col=0)
        self.btn0.clicked.connect(self.run_stm)
        
        self.btn = QtWidgets.QPushButton('estimate')
        self.layout.addWidget(self.btn, row=1, col=1)
        self.btn.clicked.connect(self.go_stm)
        
        self.btn2 = QtWidgets.QPushButton('redraw')
        self.layout.addWidget(self.btn2, row=1, col=2)
        self.btn2.clicked.connect(self.recolor)
        
        self.btn3 = QtWidgets.QPushButton('hide')
        self.layout.addWidget(self.btn3, row=1, col=3)
        self.btn3.clicked.connect(self.hide)
        
        self.addWidget(self.layout)
        
        self.table = pg.TableWidget(sortable=False)
        self.addWidget(self.table)
        

        
        # pro začatek postačí
        # triangulaci kreslím jen v 2D
        self.triangulation = [] 
        self.simplices = []
        self.max_simplices = {'success':0, 'failure':0, 'mix':0}


    def hide(self):
        #č nejdřív triangulace
        for tri_bound, plot_item in self.triangulation:
            plot_item.hide()
            # keep the GUI responsive :)
            #self.sb_item.app.processEvents()

        #č teď tečičky
        for nodes, plot_item, cell_stats in self.simplices:
            plot_item.hide()
            # keep the GUI responsive :)
            #self.sb_item.app.processEvents()
        
        
    def recolor(self):
        with pg.BusyCursor():
            # keep the GUI responsive :)
            self.sb_item.app.processEvents()
            #č nejdřív triangulace
            for tri_bound, plot_item in self.triangulation:
                plot_item.show()
                
                
            #č teď tečičky    
            for nodes, plot_item, cell_stats in self.simplices:
                event = cell_stats['event']
                if event in self.max_simplices:
                    cell_probability = cell_stats['cell_probability']
                    cm = self.param.getValues()[event][0] #č očekávám tam kolor mapu
                    blue_intensity = cell_probability / self.max_simplices[event]
                    color = cm.mapToQColor(blue_intensity)
                else: # outside
                    color = 0.6
                #symbolSize = np.sqrt(nodes.w / min(nodes.w)) # not bad
                size = self.param.getValues()['node (pixel) size'][0]
                plot_item.setSymbolBrush(color)
                plot_item.setSymbolSize(size)
                plot_item.show()
                # keep the GUI responsive :)
                #self.sb_item.app.processEvents()

        

    def on_space_changed(self, *args, **kwargs):
        #with pg.BusyCursor():
        #self.hide()
        # keep the GUI responsive :)
        #self.sb_item.app.processEvents()
        #č nejdřív triangulace
        for tri_bound, plot_item in self.triangulation:
            pos = getattr(tri_bound, self.sb_item.space)
            plot_item.setData(pos)
            #plot_item.show()
            # keep the GUI responsive :)
            #self.sb_item.app.processEvents()

        #č teď tečičky
        for nodes, plot_item, cell_stats in self.simplices:
            pos = getattr(nodes, self.sb_item.space)[:,:2]
            plot_item.setData(pos)
            #plot_item.show()
            # keep the GUI responsive :)
            #self.sb_item.app.processEvents()


    #č ten hlavní modul se dočkal na překopávání
    def on_box_run(self, *args, **kwargs):
        #č je třeba zkontrolovat autorun a restartovat výpočet
        if self.param.getValues()['Run with the box'][0]:
            self.run_stm()
        #else:
        #    self.self_clear()
    
        
    def redraw(self, *args, **kwargs):
        self.triangulation.clear()
        self.simplices.clear()
        self.max_simplices['success'] = 0
        self.max_simplices['failure'] = 0
        self.max_simplices['mix'] = 0
            
        
    def self_clear(self):
        # odebereme prvky-propísky z hlavního plotu
        for tri_bound, plot_item in self.triangulation:
            self.sb_item.central_widget.removeItem(plot_item)
        for nodes, plot_item, cell_stats in self.simplices:
            self.sb_item.central_widget.removeItem(plot_item)
        
        self.redraw()
    
    def go_stm(self): self.start_stm(callback=self.callback)
    def run_stm(self): self.start_stm()
    def start_stm(self, callback=None):
        # indikace
        #self.setDisabled(True)
        with pg.BusyCursor():
            nsim = self.sb_item.slider.value()
            sample_box = self.sb_item.sample_box[:nsim]
            #☺ Krucinal, kdo ten OrderedDict vymyslel?
            params = self.param.getValues()
            model_space = params['model space'][0]
            sampling_space = params['sampling space'][0]
            if sampling_space == 'None':
                sampling_space = None
            weighting_space = params['weighting space'][0]
            if weighting_space == 'None':
                weighting_space = None
            outside_budget = params['outside budget'][0]
            simplex_budget = params['nodes per simplex'][0]
            
            design = params['design'][0]
            if design == 'None':
                design = None
            else:
                design = self.sb_item.kwargs['designs'][design]
                
            tschemes = params['scheme'][0]
            degree = params['degree'][0]
            if tschemes == 'None':
                scheme = None
            else:
                scheme = schemes.get_tn_scheme(tschemes, sample_box.nvar, degree)
            
            #č je třeba skrýt prvky z minula
            self.self_clear()

            try:
                
                if params['method'][0] == 'fast_cubature':
                    method = stm.fast_simplex_cubature
                    data = method(sample_box, scheme, model_space=model_space,\
                                  sampling_space=sampling_space,\
                                   weighting_space=weighting_space,\
                                    outside_budget=outside_budget, \
                                    callback=callback, design=design)
                                    
                elif params['method'][0] == 'full_cubature':
                    method = stm.full_simplex_cubature
                    data = method(sample_box, scheme, model_space=model_space,\
                                   weighting_space=weighting_space,\
                                    callback=callback)
                else:
                    if params['method'][0] == 'full_sampling':
                        method = stm.full_simplex_estimation
                    else: # 'fast_sampling'
                        method = stm.fast_simplex_estimation
                    data = method(sample_box, model_space=model_space,\
                                  sampling_space=sampling_space, \
                                   weighting_space=weighting_space,\
                                    outside_budget=outside_budget, \
                                     simplex_budget=simplex_budget,\
                                    callback=callback, design=design)
                
                if hasattr(self.sb_item.sample_box, 'estimations'):
                    self.sb_item.sample_box.estimations.append(data)
                    self.sb_item.estimation_added.emit()
                self.table.setData(data)
            except BaseException as e:
                msg = "error during estimation "
                error_msg = self.__class__.__name__ + ": " + msg + repr(e)
                print(error_msg)
        # indikace
        #self.setEnabled(True)     
        
        
        
            
        
    def callback(self, sx=None, nodes=None, cell_stats=None, simplex=None, *args, **kwargs):
        plot_widget = self.sb_item.central_widget
        #č stm trianguľaciju pokažde provadí znovu, proto skoro nemá cenu drbat se s její znovupoužitím
        if (simplex is not None) and (simplex.nvar==2):
        
            ns = 100
            # take coordinates in the space, where triangulation has been performed
            simplex_tri = getattr(simplex, sx.tri_space)
            x_tri_1 = np.linspace(simplex_tri[0,0], simplex_tri[1,0], ns, endpoint=False)
            y_tri_1 = np.linspace(simplex_tri[0,1], simplex_tri[1,1], ns, endpoint=False)
            x_tri_2 = np.linspace(simplex_tri[1,0], simplex_tri[2,0], ns, endpoint=False)
            y_tri_2 = np.linspace(simplex_tri[1,1], simplex_tri[2,1], ns, endpoint=False)
            x_tri_3 = np.linspace(simplex_tri[2,0], simplex_tri[0,0], ns, endpoint=True)
            y_tri_3 = np.linspace(simplex_tri[2,1], simplex_tri[0,1], ns, endpoint=True)
                
            tri_bound_tri = np.concatenate(((x_tri_1, y_tri_1), (x_tri_2, y_tri_2),\
                                             (x_tri_3, y_tri_3)), axis=1).T
            # vytvořme sample
            tri_bound = self.sb_item.sample_box.f_model.new_sample(tri_bound_tri, space=sx.tri_space)
            
            # draw 
            pos = getattr(tri_bound, self.sb_item.space)
            plot_item = plot_widget.plot(pos, pen='k')
            plot_item.setZValue(50)
            
            # uložíme data
            self.triangulation.append((tri_bound, plot_item))
            
            #plot_item.show()
        
        
        #    
        # tečičky
        #
        pos = getattr(nodes, self.sb_item.space)[:,:2]
        event = cell_stats['event']
        cell_probability = cell_stats['cell_probability']
        if event in self.max_simplices:
            cm = self.param.getValues()[event][0] #č očekávám tam kolor mapu
            
            #č chcu ještě na konci prekreslit s různejma barvičkama, podle obsahu pravděpodobnosti
            # zkontrolujeme probability
            if self.max_simplices[event] < cell_probability:
                self.max_simplices[event] = cell_probability
                # a hned všecko dotyčné přebarvíme podle obsahu pravděpodobnosti
                for self_simplex in self.simplices:
                    if event == self_simplex[2]['event']:
                        # zde cell_probability se rovná self.p_cell_max[event]
                        # ale bacha! Nesplet se jinde!
                        #č nechť zůstane starý nazev
                        blue_intensity = self_simplex[2]['cell_probability'] / cell_probability
                        color = cm.mapToQColor(blue_intensity)
                        self_simplex[1].setSymbolBrush(color)
            
            
            intensity = cell_probability / self.max_simplices[event]
            #č tam prostě MUSÍ být tuple
            color = cm.mapToQColor(intensity)
            
        
        else: # outside
            color = 0.6
        
        
        # draw tečičky
        #
        
        #symbolSize = np.sqrt(nodes.w / min(nodes.w)) # not bad
        size = self.param.getValues()['node (pixel) size'][0]
        #brush = pg.mkBrush(color)
        plot_item = plot_widget.plot(pos, pen=None, symbol='o', symbolPen=pg.mkPen(None), symbolBrush=color,\
                                     symbolSize=size, name='IS localized nodes')
        plot_item.setZValue(40)

        # uložíme data
        self.simplices.append((nodes, plot_item, cell_stats))
        
        
        # keep the GUI responsive :)
        self.sb_item.app.processEvents()
        
        




class VoronoiEstimationWidget(QtWidgets.QSplitter):
    """
    addLabel(text=' ', row=None, col=None, rowspan=1, colspan=1, **kargs)
    """
    # I'd like to get access to the samplebox stuff via the container's reference, 
    # INHERETED by gl_plot
    def __init__(self, samplebox_item,  parent=None, *args, **kwargs):
        super().__init__(parent)
        # sb like samplebox, of course
        self.sb_item = samplebox_item
        
        self.sb_item.box_runned.connect(self.on_box_run)
        self.sb_item.slice_changed.connect(self.self_clear)
        self.sb_item.space_changed.connect(self.on_space_changed)
        self.sb_item.redraw_called.connect(self.redraw)
        #☺ na internetu všichni tak dělaj
        self.setup()
    
    # INHERETED by gl_plot
    def setup(self):
        self.setOrientation(QtCore.Qt.Vertical)
        self.layout = pg.LayoutWidget(self)
        # model_space='Rn', sampling_space=None, p_norm=1, budget=20000
        params = [{'name': 'method', 'type': 'list', 'values': ['Voronoi_tesselation','Voronoi_2_point_estimation'], 'value': 'Voronoi_2_point_estimation'}]
        params.append({'name': 'model space', 'type': 'list', 'values': self.sb_item.spaces, 'value': 'Rn'})
        params.append({'name': 'sampling space', 'type': 'list', 'values': ['None'] + self.sb_item.spaces, 'value': 'None'})
        params.append({'name': 'p-norm', 'type': 'float', 'limits': (1, float('inf')), 'value': 1, 'default': np.inf})
        params.append({'name': 'budget', 'type': 'float', 'limits': (1, float('inf')), 'value': 20000, 'default': 20000})
        self.coloring_modes = ['simple_coloring', 'cell_probability_coloring','node_pf_coloring']
        params.append({'name': 'coloring', 'type': 'list', 'values': self.coloring_modes, 'value': self.coloring_modes[1]})
        params.append({'name': 'node (pixel) size', 'type': 'float', 'limits': (0, float('inf')), 'value': 3, 'default': 1})
        params.append({'name': 'Run with the box', 'type': 'bool', 'value': False }) # 'tip': "This is a checkbox"
        
        ### Create tree of Parameter objects
        self.param = pg.parametertree.Parameter.create(name='params', type='group', children=params)
        # I don't know why that signals do not work for me
        # Only sigTreeStateChanged works, but I don't want to struggle with it
        # May be I'll report the issue 
        #self.param.sigValueChanged.connect(self.param_changed)
        #self.param.sigValueChanging.connect(self.param_changing)
        
        ### Create ParameterTree widget
        self.ptree = pg.parametertree.ParameterTree()
        self.ptree.setParameters(self.param, showTop=False)
        
        self.layout.addWidget(self.ptree, row=0, col=0, colspan=3)
        
        
        self.btn = QtWidgets.QPushButton('estimate')
        self.layout.addWidget(self.btn, row=1, col=0)
        self.btn.clicked.connect(self.run_stm)
        
        self.btn2 = QtWidgets.QPushButton('redraw')
        self.layout.addWidget(self.btn2, row=1, col=1)
        self.btn2.clicked.connect(self.recolor)
        
        self.btn3 = QtWidgets.QPushButton('hide')
        self.layout.addWidget(self.btn3, row=1, col=2)
        self.btn3.clicked.connect(self.hide)
        
        self.addWidget(self.layout)
        
        self.table = pg.TableWidget(sortable=False)
        self.addWidget(self.table)
        
        # pro začatek postačí
        self.cells = []
        # probability of the biggest cell
        # used for coloring
        self.p_cell_max = {'success':0, 'failure':0}
     
     
    # INHERETED by gl_plot
    def on_box_run(self, *args, **kwargs):
        # je třeba zkontrolovat autorun a restartovat výpočet
        if self.param.getValues()['Run with the box'][0]:
            self.run_stm()
        #else:
            #self.self_clear()
    
    # INHERETED by gl_plot
    def hide(self):
        for nodes, plot_item, cell_stats in self.cells:
            plot_item.hide()
            # keep the GUI responsive :)
            #self.sb_item.app.processEvents()
    
    # INHERETED by gl_plot
    def redraw(self, *args, **kwargs):
        self.cells.clear()
        self.p_cell_max['success'] = 0
        self.p_cell_max['failure'] = 0
    
    ## I'll rename after main widget refactoring
    # refactoring already done, why I should rename?
    # INHERETED by gl_plot
    def recolor(self):
        # indikace
        #self.setDisabled(True)
        with pg.BusyCursor():
            # Krucinal, kdo ten OrderedDict vymyslel?
            params = self.param.getValues()
            coloring = params['coloring'][0]
            
            # přebarvíme nějak tečičky 
            # callback vybírám ze svého kódu, ten musí bejt v pořádku
            # ne že by to bylo dokonalé bezpečný, 
            # ale na lokálním počítači asi to není až tak zavadný
            coloring_function = getattr(self, coloring)
            
            # hura! Jedeme!
            coloring_function()
            
            
        # indikace
        #self.setEnabled(True)
    
    
    def on_space_changed(self, *args, **kwargs):
        # teď tečičky
        for nodes, plot_item, cell_stats in self.cells:
            pos = getattr(nodes, self.sb_item.space)[:,:2]
            plot_item.setData(pos)
        
        
    # INHERETED by gl_plot
    def self_clear(self):
        # odebereme prvky-propísky z hlavního plotu
        for nodes, plot_item, cell_stats in self.cells:
            self.sb_item.central_widget.removeItem(plot_item)
        
        self.redraw()
        


    # INHERETED by gl_plot
    def run_stm(self):
        # indikace
        #self.setDisabled(True)
        with pg.BusyCursor():
            nsim = self.sb_item.slider.value()
            sample_box = self.sb_item.sample_box[:nsim]
            # Krucinal, kdo ten OrderedDict vymyslel?
            params = self.param.getValues()
            method = params['method'][0]
            model_space = params['model space'][0]
            sampling_space = params['sampling space'][0]
            if sampling_space == 'None':
                sampling_space = None
            p_norm = params['p-norm'][0]
            budget = params['budget'][0]
            coloring = params['coloring'][0]
            
            # je třeba skrýt prvky z minula
            self.self_clear()
            
            
            # přebarvíme nějak tečičky 
            # callback vybírám ze svého kódu, ten musí bejt v pořádku
            # ne že by to bylo dokonalé bezpečný, 
            # ale na lokálním počítači asi to není až tak zavadný
            coloring_function = getattr(self, coloring)
            
            
            try:
                stm_function = getattr(stm, method)
                # model_space='Rn', sampling_space=None, p_norm=1, budget=20000
                data = stm_function(sample_box, model_space=model_space, sampling_space=sampling_space,\
                                                     p_norm=p_norm, budget=budget, callback=coloring_function)
                
                if hasattr(self.sb_item.sample_box, 'estimations'):
                    self.sb_item.sample_box.estimations.append(data)
                    self.sb_item.estimation_added.emit()
                self.table.setData(data)
                    
            except BaseException as e:
                msg = "error during estimation "
                error_msg = self.__class__.__name__ + ": " + msg + repr(e)
                print(error_msg)
                
            
            
        # indikace
        #self.setEnabled(True)
    
        
        
            
        
    def node_pf_coloring(self, estimation=None, nodes=None, cell_stats=None, out_nodes=None, *args, **kwargs):
        """
        if nodes and cell_stats  provided we will add them to self.cells
        otherwise function redraw items in self.cells
        """
        plot_widget = self.sb_item.central_widget
        if nodes is None:
            for cell in self.cells:
                nodes, plot_item, cell_stats = cell
                # odebereme prvky z hlavního plotu
                # zde je třeba prvky vygenerovat znovu 
                # protože nikdo neví co tam bylo před tím
                # takhle, nechce se mi drbat s tím, co tam bylo před tím
                # komplikace ze strany pyqtgraph
                plot_widget.removeItem(plot_item)
                
                # bacha, potřebuji prvek uložiť in-place
                cell[1] = self.node_pf_scatter_plot(nodes, cell_stats)
        
        # máme nodes, tj. jedeme poprvé        
        else:
            plot_item = self.node_pf_scatter_plot(nodes, cell_stats)
            
            # uložíme data
            self.cells.append([nodes, plot_item, cell_stats])
            
            # keep the GUI responsive :)
            self.sb_item.app.processEvents()
            
            
            
            
    def node_pf_scatter_plot(self, nodes, cell_stats):
        pos = getattr(nodes, self.sb_item.space)[:,:2]
        symbol_size = self.param.getValues()['node (pixel) size'][0]
        plot_widget = self.sb_item.central_widget
        # zas, нет ножек - нет мультиков
        # node_pf_estimations nemusejí bejt
        try:
            # zkusmě pro jednoduchost 
            # čírou RGB hračku
            npf = nodes.node_pf_estimations
            colors = tuple((npf[i]*255, (1-npf[i])*255, 0) for i in range(len(pos))) 
            # sice dokumentace popisuje víc možností zadávání, 
            # ale toto zadávání různejch barviček je pro mě jediné fungujicí. Drbal jsem s tím do znechucení
            # je v podstatě opsané z příkladu
            # rovnou přes PlotDataItem mi nefunguje
            # žádné jiné možností zadávání já jsem v zdrojacích 
            # pyqtgraph (konkretně v PlotDataItem a v ScatterPlotItem) neuviděl
            # tuším, že je to neunosně drahý
            list_of_dicts = list({'pos': pos[i], 'size':symbol_size, 'pen': colors[i], 'brush':colors[i], 'symbol':'o'} for i in range(len(pos)))
            plot_item = pg.ScatterPlotItem(list_of_dicts)
            plot_widget.addItem(plot_item)
            return plot_item
            
        except BaseException as e:
            msg = "node_pf_coloring has problems "
            error_msg = self.__class__.__name__ + ": " + msg + repr(e)
            print(error_msg)
            #self.error.emit(error_msg)
            # simple coloring
            event = cell_stats['event']
            color = self.get_color(event)
            #symbolSize = np.sqrt(nodes.w / min(nodes.w)) # not bad
            return plot_widget.plot(pos, pen=None, symbol='o', symbolPen=color, symbolBrush=color, symbolSize=symbol_size, name='IS localized nodes')
        

        
        
    
    def simple_coloring(self, nodes=None, cell_stats=None, *args, **kwargs):
        """
        if nodes and cell_stats  provided we will add them to self.cells
        otherwise function redraw items in self.cells
        """
        symbol_size = self.param.getValues()['node (pixel) size'][0]
        plot_widget = self.sb_item.central_widget
        if nodes is None:
            for cell in self.cells:
                nodes, plot_item, cell_stats = cell
                # odebereme prvky z hlavního plotu
                # zde je třeba prvky vygenerovat znovu 
                # protože nikdo neví co tam bylo před tím
                # takhle, nechce se mi drbat s tím, co tam bylo před tím
                # komplikace ze strany pyqtgraph
                plot_widget.removeItem(plot_item)
                
                # draw 
                pos = getattr(nodes, self.sb_item.space)[:,:2]
                #x, y = (*getattr(nodes, self.sb_item.space).T,)
                
                event = cell_stats['event']
                color = self.get_color(event)
                #symbolSize = np.sqrt(nodes.w / min(nodes.w)) # not bad
                # bacha, potřebuji prvek uložiť in-place
                cell[1] = plot_widget.plot(pos, pen=None, symbol='o',\
                        symbolPen=color, symbolBrush=color, symbolSize=symbol_size, name='IS localized nodes')
        
        # máme nodes, tj. jedeme poprvé        
        else:
            # draw tečičky
            #
            pos = getattr(nodes, self.sb_item.space)[:,:2]
            
            event = cell_stats['event']
            color = self.get_color(event)
            #symbolSize = np.sqrt(nodes.w / min(nodes.w)) # not bad
            plot_item = plot_widget.plot(pos, pen=None, symbol='o',\
                     symbolPen=color, symbolBrush=color, symbolSize=symbol_size, name='IS localized nodes')
            
            # uložíme data
            self.cells.append([nodes, plot_item, cell_stats])
            
            # keep the GUI responsive :)
            self.sb_item.app.processEvents()
    
        
            
    def cell_probability_coloring(self, nodes=None, cell_stats=None, *args, **kwargs):
        """
        if nodes and cell_stats  provided we will add them to self.cells
        otherwise function redraw items in self.cells
        """
        symbol_size = self.param.getValues()['node (pixel) size'][0]
        plot_widget = self.sb_item.central_widget
        if nodes is None:
            # odebereme prvky z hlavního plotu
            # zde je třeba prvky vygenerovat znovu 
            # protože nikdo neví co tam bylo před tím
            # takhle, nechce se mi drbat s tím, co tam bylo před tím
            # komplikace ze strany pyqtgraph
            for nodes, plot_item, cell_stats in self.cells:
                plot_widget.removeItem(plot_item)
                
                event = cell_stats['event']
                cell_probability = cell_stats['cell_probability']
                if self.p_cell_max[event] < cell_probability:
                    self.p_cell_max[event] = cell_probability
                
            # přebarvíme tečičky podle obsahu pravděpodobnosti
            for cell in self.cells:
                nodes, plot_item, cell_stats = cell
                # draw 
                pos = getattr(nodes, self.sb_item.space)[:,:2]
                #x, y = (*getattr(nodes, self.sb_item.space).T,)
                
                event = cell_stats['event']
                cell_probability = cell_stats['cell_probability']
                # bez modrého - maximální intenzita
                blue_intensity = 1 - cell_probability / self.p_cell_max[event]
                color = self.get_color(event, blue_intensity)
                #symbolSize = np.sqrt(nodes.w / min(nodes.w)) # not bad
                # bacha, potřebuji prvek vložit zpätky
                cell[1] = plot_widget.plot(pos, pen=None, symbol='o',\
                            symbolPen=color, symbolBrush=color, symbolSize=symbol_size, name='IS localized nodes')
        
        # máme nodes, tj. jedeme poprvé        
        else:
            event = cell_stats['event']
            cell_probability = cell_stats['cell_probability']
            # zkontrolujeme probability
            if self.p_cell_max[event] < cell_probability:
                self.p_cell_max[event] = cell_probability
                # a hned všecko dotyčné přebarvíme podle obsahu pravděpodobnosti
                for cell in self.cells:
                    if event == cell[2]['event']:
                        # bez modrého - maximální intenzita
                        # zde cell_probability se rovná self.p_cell_max[event]
                        # ale bacha! Nesplet se jinde!
                        blue_intensity = 1 - cell[2]['cell_probability'] / cell_probability
                        color = self.get_color(event, blue_intensity)
                        # bacha, potřebuji prvek vložit zpätky
                        cell[1].setSymbolBrush(color)
                        cell[1].setSymbolPen(color)
            
            # bez modrého - maximální intenzita
            blue_intensity = 1 - cell_probability / self.p_cell_max[event]
            color = self.get_color(event, blue_intensity)
            
            
            # draw tečičky
            #
            pos = getattr(nodes, self.sb_item.space)[:,:2]
            #x, y = (*getattr(nodes, self.sb_item.space).T,)
            
            #symbolSize = np.sqrt(nodes.w / min(nodes.w)) # not bad
            plot_item = plot_widget.plot(pos, pen=None, symbol='o',\
                        symbolPen=color, symbolBrush=color, symbolSize=symbol_size, name='IS localized nodes')
            
            # uložíme data
            self.cells.append([nodes, plot_item, cell_stats])
            
            # keep the GUI responsive :)
            self.sb_item.app.processEvents()
        
                
                
    def get_color(self, event, blue_intensity=None):
        """
        get color for 'simple_coloring' or 'cell_probability_coloring'
        """
        # generally
        if event == 'success':
            color = [167, 255, 181]# xkcd:light seafoam green #a7ffb5
        elif event == 'failure':
            color = [253, 193, 197] # xkcd: pale rose (#fdc1c5)
        # já vím, že Voronoi nemá 'mix', эн но юа
        else:# 'mix'
            color = [255, 243, 154] # let's try xkcd: dark cream (#fff39a)
            
        if blue_intensity is not None:
            # let's play with blue a little bit
            # chcu mít korektní výstup
            # aspoň v něčem chcu být jistý
            if blue_intensity > 1:
                color[2] = 255
            elif blue_intensity < 0:
                color[2] = 0
            else:
                # pyqtgraph žere barvy i s čarkou
                # ale my je mu davat nebudeme
                color[2] = int(blue_intensity*255) 
            
        return tuple(color)            
                    







class HullEstimationWidget(pg.LayoutWidget):
    # I'd like to get access to the samplebox stuff via the container's reference, 
    def __init__(self, samplebox_item,  parent=None, *args, **kwargs):
        super().__init__(parent)
        # sb like samplebox, of course
        self.sb_item = samplebox_item
        
        self.giracle = Giracles(w=samplebox_item, autoredraw=False, nrod=200)
        #č Ghull se zkomplikoval. Musím integraci řešit zvlášť
        # Serie for integration nodes
        self.serint = Series(w=samplebox_item, autoredraw=False)
        #ё hyperplanes? Кого ты обманываешь, Alexi?
        #č tak. už je to equation_planes :)
        self.equation_planes = InfiniteLines(w=samplebox_item, autoredraw=False)
        
        # signals handling:
        # box_runned - handled by .on_box_run() method
        # space_changed - handled automatically by smart items
        # slice_changed - setted up clear() on smart items
        # redraw_called - handled automatically by smart items
        # estimation_added - class does not handle the signal
        #                   nor emits the signal itself 
        #                   (as does not save estimations anywhere for now)
        
        # todo: design estimation record 
        
        self.sb_item.box_runned.connect(self.on_box_run)
        #č Alexi, ten signal může té funkce posilát bůhví co navíc.
        #č (ano. clear() nebere žádné argumenty, takže v cajku)
        self.sb_item.slice_changed.connect(self.giracle.clear)
        self.sb_item.slice_changed.connect(self.equation_planes.clear)
        #č ty naše chytré prvky giracle a equation_planes 
        #č hlídají space_changed a redraw_called sami.
        
        self.schemes = dict()
        self.ndim = self.sb_item.sample_box.nvar
        #☺ na internetu všichni tak dělaj
        self.setup()
        
    def setup(self):
        #č já teďkom dědím ne QSplitter, ale LayoutWidget
        #оӵ Кужым кариськы, Олёш!
        
        #č zkusíme nový (pro WellMet) UI, uživatelské rozhraní
        #оӵ кнопка вылын
        #self.layout = self.addLayout(row=0, col=0)
        #self.tool_layout = QtGui.QHBoxLayout()
        #self.layout.addLayout(self.tool_layout, 0, 0)
        #self.addWidget(self.layout, row=0, col=0)
        
        #č toolbar je obecně super věc, ale mě zlobí umístění v layoutu
        self.toolbar = QtWidgets.QToolBar(self)
        #č jmenovitě, roztažení mě nefunguje vůbec
        #size_policy = self.toolbar.sizePolicy()
        #size_policy.setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        #self.toolbar.setSizePolicy(size_policy)
        
        #č draw_convex_hull ja navržena tak, aby brala jíž hotový hull
#        if self.ndim == 2:
#            action = self.toolbar.addAction("draw convex hull", self.draw_convex_hull)
#            btn = self.toolbar.widgetForAction(action)
#            btn.setAutoRaise(False)
        
        action = self.toolbar.addAction("shell out!", self.get_shell_estimation)
        btn = self.toolbar.widgetForAction(action)
        btn.setAutoRaise(False)
        btn.setToolTip("Creates Ghull object")
        #btn.setSizePolicy(size_policy)
        
        action = self.toolbar.addAction("integrate", self.integrate)
        btn = self.toolbar.widgetForAction(action)
        btn.setAutoRaise(False)
        btn.setToolTip("Only uses Ghull object created before")
        #btn.setSizePolicy(size_policy)
        
        action = self.toolbar.addAction("shot!", self.shot)
        btn = self.toolbar.widgetForAction(action)
        btn.setAutoRaise(False)
        
        action = self.toolbar.addAction("fire!", self.fire)
        btn = self.toolbar.widgetForAction(action)
        btn.setAutoRaise(False)
        #btn.setSizePolicy(size_policy)
        
        action = self.toolbar.addAction("boom!", self.boom)
        btn = self.toolbar.widgetForAction(action)
        btn.setAutoRaise(False)
        
        action = self.toolbar.addAction("hide", self.hide)
        btn = self.toolbar.widgetForAction(action)
        btn.setAutoRaise(False)
        #btn.setSizePolicy(size_policy)
        
        action = self.toolbar.addAction("show", self.show)
        btn = self.toolbar.widgetForAction(action)
        btn.setAutoRaise(False)
        
        action = self.toolbar.addAction("clear", self.clear)
        btn = self.toolbar.widgetForAction(action)
        btn.setAutoRaise(False)
        
        #self.tool_layout.addWidget(self.toolbar)
        self.addWidget(self.toolbar, row=0, col=0)
        
        
        #оӵ остальной (люкет) уллапала
        
        ### Create ParameterTree widget
        self.ptree = pg.parametertree.ParameterTree()
        self._set_param()
        self.ptree.setParameters(self.param, showTop=False)
        
        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.ptree)
        
        self.table = pg.TableWidget(sortable=False)
        self.splitter.addWidget(self.table)
        
        #self.addWidget(self.splitter, row=1, col=0, colspan=5)
        self.addWidget(self.splitter, row=1, col=0)
    
    def hide(self):
        self.serint.hide()
        self.giracle.hide()
        self.equation_planes.hide()
        
    def show(self):
        self.serint.show()
        self.giracle.show()
        self.equation_planes.show()
        
    def clear(self):
        self.serint.clear()
        self.giracle.clear()
        self.equation_planes.clear()
    
    #оӵ DirectHull понна гинэ
    #č pouze pro DirectHull
    def get_scheme(self):
        scheme = self.param.getValues()['scheme'][0]
        if scheme == 'random':
            ndir = self.param.getValues()['ndir'][0]
            return sball.get_random_directions(ndir, self.ndim)
        elif scheme in self.schemes:
            return self.schemes[scheme].points
        else:
            Scheme = getattr(quadpy.un, scheme)
            self.schemes[scheme] = Scheme(self.ndim)
            return self.schemes[scheme].points

        
    def _set_param(self):
        params = list()
        params.append({'name': 'method', 'type': 'list', 'value': 'DirectHull', \
                     'values': ['SBall', 'BrickHull', 'DirectHull', 'CompleteHull', 'QHull', 'Grick']})
        params.append({'name': 'space', 'type': 'list', 'tip': "Not used for SBall and Grick", \
                    'values': self.sb_item.spaces, 'value': 'G'})
                    
        schemes_list = schemes.un_spheres + ['random']
        params.append({'name': 'scheme', 'type': 'list', \
                     'values': schemes_list, 'value': schemes_list[0], \
                     'tip': "Used only for Grick, DirectHull and CompleteHull. Generation can take for a while"})
        params.append({'name': 'ndir', 'type': 'int', \
                    'limits': (1, float('inf')), 'value': 1000, 'default': 1000, \
                    'title': "number of random directions", \
                    'tip': "Used only for Grick or for random scheme in DirectHull (or CompleteHull)"})   
            
        params.append({'name': 'integrator', 'title': "integrator", 'type': 'list', \
                    'values': ['MC', 'IS', '1DS'], 'value': '1DS' })
        params.append({'name': 'nonG_reduction', 'type': 'float', \
                    'title': "non Gaussian reduction", \
                    'limits': (0, 1), 'value': 0.9, 'default': 0.9,\
                    'tip': "Applied when Ghull integrates non Gaussian convex hulls"})   
        
        params.append({'name': 'use_MC', 'title': "use MC", 'type': 'bool', 'value': False, \
                    'tip': "Used for shot(), fire() and boom() functions"})   
        
        params.append({'name': 'budget', 'type': 'int',  \
                    'limits': (1, float('inf')), 'value': 1000, 'default': 1000,\
                    'tip': "Number of simulations for optimal importance sampling"})   
                    
        params.append({'name': 'node (pixel) size', 'type': 'float',\
                 'limits': (0, float('inf')), 'value': 3.5, 'default': self.sb_item.px_size})
        #ё больше калорий богу калорий!
        params.append({'name': 'r', 'type': 'color', 'value': (189, 204, 0, 255) })
        params.append({'name': 'inside', 'type': 'color', 'value': (133, 172, 102, 255) })
        params.append({'name': 'convex_hull', 'type': 'color', 'value': (85, 170, 255, 255) }) # (186, 109, 0, 255)
        params.append({'name': 'fire', 'type': 'color', 'value': (245, 117, 0, 255) })
        params.append({'name': 'orth', 'type': 'color', 'value': (255, 0, 0, 255) })
        params.append({'name': 'outside', 'type': 'color', 'value': 0.6})
        params.append({'name': 'R', 'type': 'color', 'value': (85, 85, 255, 255) })
        params.append({'name': 'Update as the box runned', 'type': 'bool', 'value': False }) # 'tip': "This is a checkbox"
        params.append({'name': 'index', 'title': "replace previous", 'type': 'bool', 'value': True })
        
        ### Create tree of Parameter objects
        # I don't know why that signals do not work for me
        # Only sigTreeStateChanged works, but I don't want to struggle with it
        # May be I'll report the issue 
        #self.param.sigValueChanged.connect(self.param_changed)
        #self.param.sigValueChanging.connect(self.param_changing)
        self.param = pg.parametertree.Parameter.create(name='params', type='group', children=params)
    
    def get_ghull(self): 
        integrator = self.param.getValues()['integrator'][0]
        if integrator == 'MC':
            Integrator = Shell_MC
        elif integrator == 'IS':
            Integrator = Shell_IS
        elif integrator == '1DS':
            Integrator = Shell_1DS
        nonG_reduction = self.param.getValues()['nonG_reduction'][0]
        hull = self.get_hull()
        self.ghull = Ghull(hull, Integrator=Integrator, non_Gaussian_reduction=nonG_reduction)
        return self.ghull
                        
        
    #č jistě potřebuji něco, co zpracuje parameter_tree 
    #č a vratí platný hull pro Ghull
    def get_hull(self):
        #č bez semplu se neobejde
        nsim = self.sb_item.slider.value()
        sample = self.sb_item.sample_box.f_model[:nsim]
        
        # ['SBall', 'BrickHull', 'DirectHull', 'QHull', 'Grick']
        hull_model = self.param.getValues()['method'][0]
        if hull_model == 'SBall':
            return khull.GBall(sample)
        elif hull_model == 'BrickHull':
            space = self.param.getValues()['space'][0]
            return khull.BrickHull(sample, space)
        elif hull_model == 'DirectHull':
            space = self.param.getValues()['space'][0]
            direct_plan = self.get_scheme()
            return khull.DirectHull(sample, direct_plan, space)
        elif hull_model == 'CompleteHull':
            space = self.param.getValues()['space'][0]
            direct_plan = self.get_scheme()
            return khull.CompleteHull(sample, direct_plan, space)
        elif hull_model == 'QHull':
            space = self.param.getValues()['space'][0]
            #č tento widget pokažde generuje obálku znovu
            return khull.QHull(sample, space, incremental=False)
        elif hull_model == 'Grick':
            direct_plan = self.get_scheme()
            ndir = self.param.getValues()['ndir'][0]
            return khull.Grick(sample, direct_plan, nrandom=ndir, auto_update=True)
        else:
            raise ValueError("HullEstimationWidget: co to je za obálku?")

    #č ten hlavní modul se dočkal na překopávání
    def on_box_run(self, *args, **kwargs):
        self.clear()
        #č je třeba zkontrolovat autorun a restartovat výpočet
        if self.param.getValues()['Update as the box runned'][0]:
            self.get_shell_estimation()
    
    def index(self, index):
        if self.param.getValues()['index'][0]: # replace previous
            return index
        else:
            return None
    
    def draw_planes(self, equations, space, **kwargs):
        if self.ndim == 2:
            #č musíme něco zavolat na self.equation_planes
            #č equation_planes má funkci add_line()
            #č add_line(self, space='G', index=None, **plot_kwargs)
            #č která pak plot_kwargs přeposilá funkci addLine()
            #č na central widgetu. 
            #č To vše skončí ve pyqtgrafové InfiniteLine třidě.
            #č ta moje třida InfiniteLines sama se stará o shodování prostorů
            #č indexy posilat nebudeme (s nimi je to trošku komplikovanější)
            
            #pos = list() #č navrhové body nakreslíme všechny dohromady
            for equation in equations:
                #č ve 2D bych očekával v rovnici pouze 3 hodnoty (já potřebuji směry)
                x, y, offset = equation
                design_point = [-x*offset, -y*offset]
                #self.sb_item.central_widget.plot(np.array([pos, pos]), symbol='o')
    #                    if y < 0: #č tak to aspoň kreslí
    #                        angle = np.rad2deg(np.arcsin(x))
    #                    else:
    #                        angle = np.rad2deg(np.arccos(y))
                    
                if (x*y) < 0: #č tak to aspoň kreslí
                    angle = np.rad2deg(np.arccos(np.abs(y)))
                else:
                    angle = np.rad2deg(np.arccos(-np.abs(y)))
                self.equation_planes.add_line(space=space, pos=design_point, angle=angle, **kwargs)
                
                
    
    def draw_convex_hull(self, hull):
        try:
            if self.param.getValues()['index'][0]: # replace previous
                self.equation_planes.clear()
            
            #č zatím uděláme jen pro 2D infinite lajny
            design_points = hull.get_design_points()
            
            size = self.param.getValues()['node (pixel) size'][0]
            color = self.param.getValues()['convex_hull'][0] #č tam bude barva
            
            self.giracle.add_serie(design_points, z=31, index=self.index('design points'),\
                            pen=None, symbol='o', symbolPen=pg.mkPen(None), \
                            symbolBrush=color, symbolSize=size, name='design points')
            self.draw_planes(hull.equations, space=hull.space, z=29,  pen=color)
                            
                            
            # orth
            color = self.param.getValues()['orth'][0] #č tam bude barva
            #self.giracle.add_serie(FORM_points, z=32, index=self.index('2FORM points'),\
            #                pen=None, symbol='o', symbolPen=pg.mkPen(None), \
            #                symbolBrush=color, symbolSize=size, name='2FORM points')
            self.draw_planes(hull.get_orth_equations(), space=hull.space, z=30,  pen=color)
            
            
            # 2FORM
            color = self.param.getValues()['fire'][0] #č tam bude barva
            #self.giracle.add_serie(FORM_points, z=32, index=self.index('2FORM points'),\
            #                pen=None, symbol='o', symbolPen=pg.mkPen(None), \
            #                symbolBrush=color, symbolSize=size, name='2FORM points')
            self.draw_planes(hull.get_2FORM_equations(), space=hull.space, z=30,  pen=color)
                            
                            
        except BaseException as e:
            msg = "draw_convex_hull error "
            error_msg = self.__class__.__name__ + ": " + msg + repr(e)
            print(error_msg)
            self.sb_item.errors.append(e)
           
    def draw_ghull(self, r, R):
        # r-circle
        if r < 0:
            r = 0
        color = self.param.getValues()['r'][0] #č tam bude barva
        #č krucí, nevím co mám dělat s indexama. 
        #č co mám dělat s předchozí kresbou? Nechame
        self.giracle.add_circle(r=r, index=self.index('r'),z=32, pen=color, name='r')
        
        # R-circle. #č Při kreslení nahradíme předchozí.
        color = self.param.getValues()['R'][0] #č tam bude barva
        self.giracle.add_circle(R, z=32, index=self.index('R'), pen=color, name='R')
            
        
        
    
    def get_shell_estimation(self):
        ghull = self.get_ghull()
        self.draw_convex_hull(ghull.hull)

        try:
            shell_estimation, global_stats = ghull.get_shell_estimation()
            
#            if hasattr(self.sb_item.sample_box, 'estimations'):
#                self.sb_item.sample_box.estimations.append(data)
#                self.sb_item.estimation_added.emit()
            self.table.setData({**global_stats, 'shell_estimation':shell_estimation})
            
            self.draw_ghull(global_stats['r'], global_stats['R'])
            
        except BaseException as e:
            msg = "error during estimation "
            error_msg = self.__class__.__name__ + ": " + msg + repr(e)
            print(error_msg)
            self.sb_item.errors.append(e)
        
        
    def shot(self):
        ghull = self.get_ghull()
        self.draw_candidates(ghull.hull.shot)
        
    def fire(self):
        ghull = self.get_ghull()
        self.draw_candidates(ghull.hull.fire)
        
    def boom(self):
        ghull = self.get_ghull()
        self.draw_candidates(ghull.boom)
    
    def draw_candidates(self, source_function):
        #č špatně rozumím, co tím bylo mysleno
        #č že jsem chtěl kreslit náhodné směry?
        ##č zatím máme issue s náhodným planem
        ##č kdyby něco - vyřeším přes ukladání 
        ##č náhodných plánů v parameter_tree
        
        self.draw_convex_hull(self.ghull.hull)
        
        #☺ Krucinal, kdo ten OrderedDict vymyslel?
        params = self.param.getValues()
        ns = params['budget'][0]
        use_MC = params['use_MC'][0]
        try:
            fire = source_function(ns, use_MC=use_MC)
            # draw tečičky
            color = self.param.getValues()['fire'][0] #č tam bude barva
            size = self.param.getValues()['node (pixel) size'][0]
            #brush = pg.mkBrush(color)
            self.giracle.add_serie(fire, z=30, index=self.index('fire'),\
                        pen=None, symbol='o', symbolPen=pg.mkPen(None), \
                        symbolBrush=color, symbolSize=size, name='fire')

        except BaseException as e:
            msg = "error "
            error_msg = self.__class__.__name__ + ": " + msg + repr(e)
            print(error_msg)
            self.sb_item.errors.append(e)        
    
    def integration_callback(self, nodes):
        #č draw tečičky
        size = self.param.getValues()['node (pixel) size'][0]
        plot_params = {'pen':None, 'symbol':'o', 'symbolSize':size, \
                        'symbolPen':pg.mkPen(None)}
        #brush = pg.mkBrush(color)
        mask = nodes.is_outside
        
        index = 'inside'
        color = self.param.getValues()[index][0] #č tam bude barva
        self.serint.add_serie(nodes[~mask], z=30,\
                    symbolBrush=color, name=index, **plot_params)
        
        index = 'outside'
        color = self.param.getValues()[index][0] #č tam bude barva
        self.serint.add_serie(nodes[mask], z=30, \
                    symbolBrush=color, name=index, **plot_params)
                    
        # keep the GUI responsive :)
        self.sb_item.app.processEvents()
            
            
            
    def integrate(self):
        #č integrace se stala stateful
        #č a musím jú taky testovat
        if 'ghull' not in self.__dict__:
            ghull = self.get_ghull()
        else:
            ghull = self.ghull
        nsim = self.sb_item.slider.value()
        sample = self.sb_item.sample_box.f_model[:nsim]
        #č teď - saháme do vnitřku naších obliběných tříd
        ghull.hull.sample = sample
        ghull.sample = sample
        
        self.draw_convex_hull(ghull.hull)
        
        
        #☺ Krucinal, kdo ten OrderedDict vymyslel?
        params = self.param.getValues()
        budget = params['budget'][0]
        
        if self.param.getValues()['index'][0]: # replace previous
            self.serint.clear()

        try:
            data = ghull.integrate(budget, callback_all=self.integration_callback)
            ghull_estimation, convex_hull_estimation, global_stats = data
            
            #if hasattr(self.sb_item.sample_box, 'estimations'):
                #self.sb_item.sample_box.estimations.append(data)
                #self.sb_item.estimation_added.emit()
            self.table.setData({**global_stats, "ghull_estimation":ghull_estimation,\
                               "convex_hull_estimation": convex_hull_estimation})
                                
            self.draw_ghull(global_stats['r'], global_stats['R'])
            
            
        except ValueError as e: #BaseException
            msg = "error during estimation "
            error_msg = self.__class__.__name__ + ": " + msg + repr(e)
            print(error_msg)  
            self.sb_item.errors.append(e)

        # draw DP
        if ghull.hull.space != 'G':
            size = self.param.getValues()['node (pixel) size'][0] + 3
            plot_params = {'pen':None, 'symbol':'t2', 'symbolSize':size, \
                            'symbolPen':pg.mkPen(None)}
            
            #color = self.param.getValues()[index][0] #č tam bude barva
            self.serint.add_serie(ghull.gint.DP, z=35, index='DP', name='DP', **plot_params)





"""
===========
♥ Чыры-пыры 
č Jiné
E Miscellaneous
===============
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""

        
        
class CandidatesWidget(pg.LayoutWidget):
    """
    """
    # I'd like to get access to the samplebox stuff via the container's reference, 
    # but relying to Qt's parent mechanism makes me worry.
    def __init__(self, samplebox_item,  parent=None, *args, **kwargs):
        super().__init__(parent)
        # sb like samplebox, of course
        self.sb_item = samplebox_item
        
        #self.sb_item.box_runned.connect(self.on_box_run)
        self.sb_item.slice_changed.connect(self.rerun)
        self.sb_item.space_changed.connect(self.rerun)
        self.sb_item.redraw_called.connect(self.redraw)
        #☺ na internetu všichni tak dělaj
        self.setup()
        
    def setup(self):
        # 1
        #
        self.autorun = QtWidgets.QCheckBox('Show')
        self.autorun.stateChanged.connect(self.rerun)
        self.addWidget(self.autorun)
        
        self.btn = QtWidgets.QPushButton('redraw')
        self.addWidget(self.btn, row=0, col=1)
        self.btn.clicked.connect(self.rerun)
        
        # 2
        #
        
        self.attr = pg.ComboBox(items=self.get_items())
        #self.attr.activated.connect(self.redraw)
        self.addWidget(self.attr, row=1, col=0, colspan=2)
        
        # 3
        #
        self.gradient = pg.GradientWidget(self, orientation='right')
        self.gradient.setColorMap(pg.colormap.ColorMap((0,1),\
                         [(255, 255, 255, 255), (67, 0, 81, 255)]))
        self.addWidget(self.gradient, row=2, col=1)
        
        
        
        #E pens, i.e. handles of PlotItem
        self.pens = []


    def get_items(self):
        try: #č výbrat libovolný vzorek
            nodes = next(iter(self.sb_item.sample_box.candidates_index.values()))
            return self.get_items_from_nodes(nodes)
        except:
            return []
    
    @staticmethod
    def get_items_from_nodes(nodes):
        try:
            #č predpokladam pandas verzi CandyBox'u
            return list(nodes.df.columns)
        except:
            #č CandyNodes?
            return list(nodes.kwargs.keys()) + list(nodes.attrs.keys())

    def run_stm(self):
        #č indikace
        #self.setDisabled(True)
        plot_widget = self.sb_item.central_widget
        with pg.BusyCursor():
            
            color_map = self.gradient.colorMap()
            
            try:#č může se tu stat cokoliv
                #č je třeba mít seznam aktualní
                self.attr.setItems(self.get_items())
                
                #č neplest s self.attr!
                attr = self.attr.currentText()
                
                #č kruci, nejdřív je třeba najít maxvalue, minvalue je implicitně nula
                maxvalue = -np.inf
                minvalue = np.inf
                for id, cb in self.sb_item.sample_box.candidates_index.items():
                    array = np.atleast_1d(getattr(cb, attr))
                    if len(array):
                        maxcb = np.nanmax(array)
                        mincb = np.nanmin(array)
                        if maxcb > maxvalue:
                            maxvalue = maxcb
                            maxitem = cb[np.nanargmax(array)]
                        if mincb < minvalue:
                            minvalue = mincb
                
                #č zvlášť nakreslím maximální hodnotu
                pos = getattr(maxitem, self.sb_item.space)[:,:2]
                max_item = plot_widget.plot(pos, data=maxvalue, pen=None, symbol='t1',\
                                             symbolBrush=color_map.mapToQColor(1))
                max_item.setZValue(130)
                self.pens.append(max_item)
                    
                #č a teď jdeme!
                for id, cb in self.sb_item.sample_box.candidates_index.items():
                    array = np.atleast_1d(getattr(cb, attr))
                    if np.isnan(array).any():
                        msg = "%s candidates has nans in %s attribute"%(id, attr)
                        error_msg = self.__class__.__name__ + ": " + msg
                        print(error_msg)
                    mask = np.isfinite(array)
                    values = array[mask]
                    norm_values = (values - minvalue) / (maxvalue - minvalue)
                    
                    pos = getattr(cb, self.sb_item.space)[mask][:,:2]
                    
                    #č sehnal jsem toto ze zdrojaků pyqtgraph
                    style = dict(pen=None, symbol='o', symbolSize=self.sb_item.px_size, symbolPen=pg.mkPen(None))
                    style['symbolBrush'] = np.array([pg.functions.mkBrush(*x) for x in color_map.map(norm_values)])
                    pen = plot_widget.plot(pos, data=values, **style)
                    pen.setZValue(-1)
                    self.pens.append(pen)
                
            except BaseException as e:
                msg = ""
                error_msg = self.__class__.__name__ + ": " + msg + repr(e)
                print(error_msg)
            
            
            
        # indikace
        #self.setEnabled(True)
        

        
    #č současně ten hlavní modul se pokusí zavolat redraw při zpouštění boxu
    #č ten hlavní modul se těší na překopávání
    def rerun(self, *args, **kwargs):
        #č uklizení budu chtit jednoznačně 
        self.self_clear()
        #č a teď řešíme, zda je třeba restartovat výpočet
        if self.autorun.isChecked():
            self.run_stm()

    def redraw(self, *args, **kwargs):
        self.pens.clear()
            
        
    def self_clear(self):
        #č odebereme prvky-propísky z hlavního plotu
        for plot_item in self.pens:
            self.sb_item.central_widget.removeItem(plot_item)
        
        self.pens.clear()
    
    
        #E not implementeed yet on the main window side        
#    def on_space_changed(self, *args, **kwargs):
#        pass    
        

        
