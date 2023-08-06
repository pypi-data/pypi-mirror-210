#!/usr/bin/env python
# coding: utf-8

import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtWidgets
from pyqtgraph.Qt import QtCore


import numpy as np
import pandas as pd # required for estimation graph

from scipy import spatial

from .. import estimation as stm
from .. import simplex as six
from . import qt_gui
from . import qt_plot


### Define a top-level widget to hold everything
class QtGuiPlot3D(qt_gui.QtGuiWindow):
    #sb_runned = QtCore.pyqtSignal()
    
    def initialize_central_widget(self):
        self.central_widget = gl.GLViewWidget()
        self.redraw_called.connect(self.redraw_plot)
        
        self.base_plotting = BasePlotting(self)
        self.px_size = 5

    def redraw_plot(self):
        try:
            self.central_widget.clear()
            self.central_widget.reset()
        except: #č 0.10 ještě neměla ty funkce
            for item in self.central_widget.items:
                item._setView(None)
            self.central_widget.items = []
            self.central_widget.update()
        self.central_widget.opts['fov'] = 3

        

    def plot_setup(self):
        self.view_items = []
        self.view_items.append(UnitCube(self))
        self.view_items.append(Axes(self))
        self.view_items.append(Grid(self))
        self.view_items.append(LastShot(self))
        self.view_items.append(Density(self))
        self.view_items.append(ConvexHull(self))
        self.view_items.append(Facets(self))
        self.view_items.append(Wireframe(self))
        

        dock = dock_r = QtWidgets.QDockWidget("Simplex-based pf estimation", self)
        dock.setWidget(SimplexEstimationWidget(self, dock))
        self.view.addAction(dock.toggleViewAction())
        self.dockables.append(dock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        
        #!
        dock = QtWidgets.QDockWidget("Tesselation-based pf estimation", self)
        dock.setWidget(VoronoiEstimationWidget(self, dock))
        self.view.addAction(dock.toggleViewAction())
        self.dockables.append(dock)
        #self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        self.tabifyDockWidget(dock_r, dock)
        
        
        dock = QtWidgets.QDockWidget("Blackbox's candidates", self)
        dock.setWidget(CandidatesWidget(self, dock))
        self.view.addAction(dock.toggleViewAction())
        self.dockables.append(dock)
        self.tabifyDockWidget(dock_r, dock)


        
        



class BasePlotting(gl.GLScatterPlotItem):
    def __init__(self, w):
        super().__init__()
        self.w = w
        #self.w.box_runned.connect(self.redraw) #č dublikuje slice_changed
        self.w.space_changed.connect(self.plot)
        self.w.slice_changed.connect(self.plot)
        self.w.redraw_called.connect(self.redraw)
        
    #č důležité je, že GLScatterPlotItem nemá .redraw()
    def redraw(self):
        self.plot()
        self.w.central_widget.addItem(self)
        
    def plot(self):
        nsim = self.w.slider.value()
        
        pos = getattr(self.w.sample_box, self.w.space)[:nsim][:,:3]
        color = np.empty((nsim, 4))
        failsi = self.w.sample_box.failsi[:nsim]
        color[failsi] = (1, 0, 0, 1)
        color[~failsi] = (0, 1, 0, 1)

        self.setData(pos=pos, color=color, size=self.w.px_size*1.5)





class UnitCube(gl.GLBoxItem):
    def __init__(self, w):
        super().__init__()
        self.w = w
        self.w.space_changed.connect(self.plot)
        self.w.redraw_called.connect(self.redraw)

        self.item = QtWidgets.QListWidgetItem('Unit cube')
        self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.item.setCheckState(QtCore.Qt.Checked)
        self.w.list_view.addItem(self.item)
        self.w.list_view.itemChanged.connect(self.plot)
        

    def redraw(self):
        self.plot()
        self.w.central_widget.addItem(self)

    def plot(self):
        if self.item.checkState() and (self.w.space in ('P', 'U')):
            self.setSize(1, 1, 1)
            self.show()
        elif self.item.checkState() and (self.w.space in ('aP', 'aU')):
            x, y, z, *__ = (*self.w.sample_box.alpha,)
            self.setSize(x, y, z)
            self.show()
        else:
            self.hide()


class LastShot(gl.GLScatterPlotItem):
    def __init__(self, w):
        super().__init__()
        self.w = w
        self.w.box_runned.connect(self.plot)
        self.w.space_changed.connect(self.plot)
        self.w.redraw_called.connect(self.redraw)

        self.item = QtWidgets.QListWidgetItem('Last shot')
        self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.item.setCheckState(QtCore.Qt.Checked)
        self.w.list_view.addItem(self.item)
        self.w.list_view.itemChanged.connect(self.plot)
        

    def redraw(self):
        self.plot()
        self.w.central_widget.addItem(self)

    def plot(self):
        if self.item.checkState() and (self.w.last_shot is not None):
            pos = getattr(self.w.last_shot, self.w.space)[:,:3]
            self.setData(pos=pos, color=(0, 0, 1, .7), size=self.w.px_size*2)
            self.show()
        else:
            self.hide()



#č Nekreslí to co má (vidím pouze jednu čáru)

##class Axes(gl.GLAxisItem):
##    def __init__(self, w):
##        super().__init__()
##        self.w = w
##        self.w.redraw_called.connect(self.redraw)
##
##        self.item = QtWidgets.QListWidgetItem('Axes')
##        self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
##        self.item.setCheckState(QtCore.Qt.Checked)
##        self.w.list_view.addItem(self.item)
##        self.w.list_view.itemChanged.connect(self.plot)
##        
##
##    def redraw(self):
##        self.plot()
##        self.w.central_widget.addItem(self)
##
##    def plot(self):
##        if self.item.checkState():
##            self.show()
##        else:
##            self.hide()


class Axes:
    def __init__(self, w):
        pos = np.array([[0,0,0],[1,0,0], [0,0,0],[0,1,0], [0,0,0],[0,0,1]])
        color = np.array([[255, 0, 0, 255],[0, 0, 0, 0], [0, 255, 0, 255],[0, 0, 0, 0], [0, 0, 255, 255],[0, 0, 0, 0]])
        self.axes = gl.GLLinePlotItem(pos=pos, color=color, width=2, mode='lines')
        
        self.w = w
        self.w.redraw_called.connect(self.redraw)

        self.item = QtWidgets.QListWidgetItem('Axes')
        self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.item.setCheckState(QtCore.Qt.Checked)
        self.w.list_view.addItem(self.item)
        self.w.list_view.itemChanged.connect(self.plot)
        

    def redraw(self):
        self.plot()
        self.w.central_widget.addItem(self.axes)

    def plot(self):
        if self.item.checkState():
            self.axes.show()
        else:
            self.axes.hide()



class Grid:
    def __init__(self, w):
        self.gx = gl.GLGridItem()
        self.gx.setSize(10, 10, 1)
        self.gx.rotate(90, 0, 1, 0)
        #gx.translate(-5, 0, 5)
        
        self.gy = gl.GLGridItem()
        self.gy.setSize(10, 10, 1)
        self.gy.rotate(90, 1, 0, 0)
        #gy.translate(0, -10, 10)
        
        self.gz = gl.GLGridItem()
        self.gz.setSize(10, 10, 1)
        #self.gz.translate(0, 0, 0)
        
        self.w = w
        self.w.space_changed.connect(self.plot)
        self.w.redraw_called.connect(self.redraw)

        self.item = QtWidgets.QListWidgetItem('Grid')
        self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.item.setCheckState(QtCore.Qt.Unchecked)
        self.w.list_view.addItem(self.item)
        self.w.list_view.itemChanged.connect(self.plot)
        

    def redraw(self):
        self.plot()
        self.w.central_widget.addItem(self.gx)
        self.w.central_widget.addItem(self.gy)
        self.w.central_widget.addItem(self.gz)

    def plot(self):
        if self.item.checkState():# and (self.w.space in ( 'Rn', 'GK', 'G')):
            self.gx.show()
            self.gy.show()
            self.gz.show()
        else:
            self.gx.hide()
            self.gy.hide()
            self.gz.hide()



#č mění se význám, semantika třídy
#č teď to není nástroj pro kontrolu skříňky, ale
#č ale pro zobrazování hezkých obrázků
#č teď se mi to víc hodí do krámu
class ConvexHull(gl.GLMeshItem):
    def __init__(self, w):
        ## Mesh item will automatically compute face normals.
        super().__init__(smooth=True, shader='edgeHilight') # edgeHilight shaded
        #self.setGLOptions('opaque')
        self.nsim = -1
        self.space = ''
        
        self.w = w
        #č já asi nechcu ani snažit sa něčo zobraziť
        #č z více dimenzí
        if self.w.sample_box.nvar == 3:
            self.w.slice_changed.connect(self.plot)
            #č slice_changed postačí, zahrnuje i box_runned 
            #self.w.box_runned.connect(self.plot)
            self.w.space_changed.connect(self.plot)
            self.w.redraw_called.connect(self.redraw)

            self.failure_item = QtWidgets.QListWidgetItem('ConvexHull Failure')
            self.failure_item.setFlags(self.failure_item.flags() | QtCore.Qt.ItemIsUserCheckable)
            self.failure_item.setCheckState(QtCore.Qt.Checked)
            self.w.list_view.addItem(self.failure_item)

            self.success_item = QtWidgets.QListWidgetItem('ConvexHull Success')
            self.success_item.setFlags(self.success_item.flags() | QtCore.Qt.ItemIsUserCheckable)
            self.success_item.setCheckState(QtCore.Qt.Checked)
            self.w.list_view.addItem(self.success_item)

            
            self.w.list_view.itemChanged.connect(self.plot)
        

    def redraw(self):
        self.plot()
        self.w.central_widget.addItem(self)

    def recalculate(self):
        nsim = self.w.slider.value()
        sample_box = self.w.sample_box[:nsim]

        self.space = self.w.space
        points = getattr(sample_box, self.w.space)
        qhull = spatial.ConvexHull(points, incremental=False)
        
        
        self.points = points
        self.simplices = qhull.simplices
        self.events = six.get_events(sample_box, self.simplices)
        
        nodes_colors = np.empty((nsim, 4))
        nodes_colors[sample_box.failsi] = np.array([253, 93, 97, 0])/255 
        nodes_colors[~sample_box.failsi] = np.array([67, 255, 81, 0])/255
        
        self.vertex_colors = nodes_colors

        # marker
        self.nsim = nsim

#č kus kódu jako historická památka
#č doposud si pamatuji, jak jsem tu kvůli vlástní chybě bojoval s ConvexHull'em
#č pak ConvexHull byl reabilitován
##        if (self.w.sample_box.nsim != len(self.w.sample_box.convex_hull.points)):
##            #č ConvexHull nemichá vzorky a nedělá ďupy - byla to chyba v Blackboxu
##            print(self.__class__.__name__ + \
##                  ": convex hull points mismatch. Switching to the failsafe code.")
##            sampled_plan_tri = getattr(self.w.sample_box, self.w.sample_box.tri_space)
##            tree = spatial.cKDTree(sampled_plan_tri)
##            self.points = self.w.sample_box.convex_hull.points
##            dd, ii = tree.query(self.points, k=1, p=2)
##
##            self.simplices = self.w.sample_box.convex_hull.simplices
##            box_facets = ii[self.simplices.reshape(-1)].reshape(-1, 3)
##            self.events = self.w.sample_box.get_events(box_facets)
##
##
##            nodes_colors = np.empty((self.w.sample_box.nsim, 4))
##            nodes_colors[self.w.sample_box.failsi] = np.array([253, 93, 97, 0])/255 
##            nodes_colors[~self.w.sample_box.failsi] = np.array([67, 255, 81, 0])/255
##            
##
##            self.vertex_colors = nodes_colors[ii]



    def plot(self):
        if (self.failure_item.checkState() + self.success_item.checkState())\
                               and (self.w.slider.value() > 3):
            try:
                if (self.nsim != self.w.slider.value()) or (self.space != self.w.space):
                    self.recalculate()
                    
                #face_colors = np.empty((len(self.simplices), 4), dtype=np.int16)
                # sorry for that
                if self.failure_item.checkState():
                    mask_1 = self.events==1
                else:
                    mask_1 = self.events==100500

                if self.success_item.checkState():
                    mask_0 = self.events==0
                else:
                    mask_0 = self.events==100500

                #mask_2 = self.events!=2

                mask = np.any([mask_0, mask_1], axis=0)

                
                self.setMeshData(vertexes=self.points, faces=self.simplices[mask], vertexColors=self.vertex_colors, \
                                 drawEdges=True, edgeColor=(1, 1, 0, 1))
                
                self.show()
            except BaseException as e:
                msg = "nepovedlo se nám spočítat konvexní obálku "
                error_msg = self.__class__.__name__ + ": " + msg + repr(e)
                print(error_msg)
        else:
            self.hide()
        
                
        
#č mění se význám, semantika třídy
#č teď to není nástroj pro kontrolu skříňky, ale
#č ale pro zobrazování hezkých obrázků
#č teď se mi to víc hodí do krámu
class Facets(gl.GLMeshItem):
    def __init__(self, w):
        ## Mesh item will automatically compute face normals.
        super().__init__(smooth=True, shader='shaded') # edgeHilight shaded
        #self.setGLOptions('opaque')
        self.nsim = -1
        self.space = ''
        
        self.w = w
        #č já asi nechcu ani snažit sa něčo zobraziť
        #č z více dimenzí
        if self.w.sample_box.nvar == 3: 
            self.w.slice_changed.connect(self.plot)
            #č slice_changed postačí, zahrnuje i box_runned 
            #self.w.box_runned.connect(self.plot)
            self.w.space_changed.connect(self.plot)
            self.w.redraw_called.connect(self.redraw)

            self.failure_item = QtWidgets.QListWidgetItem('Failure facets')
            self.failure_item.setFlags(self.failure_item.flags() | QtCore.Qt.ItemIsUserCheckable)
            self.failure_item.setCheckState(QtCore.Qt.Checked)
            self.w.list_view.addItem(self.failure_item)

            self.success_item = QtWidgets.QListWidgetItem('Success facets')
            self.success_item.setFlags(self.success_item.flags() | QtCore.Qt.ItemIsUserCheckable)
            self.success_item.setCheckState(QtCore.Qt.Checked)
            self.w.list_view.addItem(self.success_item)

            
            self.w.list_view.itemChanged.connect(self.plot)
        

    def redraw(self):
        self.plot()
        self.w.central_widget.addItem(self)

    def recalculate(self):
        nsim = self.w.slider.value()
        sample_box = self.w.sample_box[:nsim]
        
        self.space = self.w.space
        points = getattr(sample_box, self.w.space)
        tri = spatial.Delaunay(points, incremental=False)
        
        self.points = points

        self.simplices = tri.simplices
        self.s_events = six.get_events(sample_box, self.simplices)

        self.mixed_simplices = self.simplices[self.s_events==2]

        #č ježíšmaria, co se tu děje?
        self.facets = np.vstack((self.mixed_simplices[:,:3], self.mixed_simplices[:,1:],\
                                 self.mixed_simplices[:,[0,2,3]], self.mixed_simplices[:,[0,1,3]]))

        # f_events
        self.events = six.get_events(sample_box, self.facets)
                    

        self.nodes_colors = np.empty((nsim, 4))
        self.nodes_colors[sample_box.failsi] = np.array([203, 83, 87, 0])/255 
        self.nodes_colors[~sample_box.failsi] = np.array([57, 205, 71, 0])/255
        
        
        # marker
        self.nsim = nsim


    def plot(self):
        if (self.failure_item.checkState() + self.success_item.checkState())\
                               and (self.w.slider.value() > 3):
            
            try:
                if (self.nsim != self.w.slider.value()) or (self.space != self.w.space):
                    self.recalculate()
                
                #face_colors = np.empty((len(self.simplices), 4), dtype=np.int16)
                # sorry for that
                if self.failure_item.checkState():
                    mask_1 = self.events==1
                else:
                    mask_1 = self.events==100500

                if self.success_item.checkState():
                    mask_0 = self.events==0
                else:
                    mask_0 = self.events==100500

                #mask_2 = self.events!=2

                mask = np.any([mask_0, mask_1], axis=0)

                self.setMeshData(vertexes=self.points, faces=self.facets[mask], vertexColors=self.nodes_colors, \
                                 drawEdges=True, edgeColor=(1, 1, 0, 1))
                
                self.show()
            except BaseException as e:
                msg = "nepovedlo se nám spočítat stěny "
                error_msg = self.__class__.__name__ + ": " + msg + repr(e)
                print(error_msg)
        else:
            self.hide()   

        
        

#č mění se význám, semantika třídy
#č teď to není nástroj pro kontrolu skříňky, ale
#č ale pro zobrazování hezkých obrázků
#č teď se mi to víc hodí do krámu
class Wireframe(gl.GLMeshItem):
    def __init__(self, w):
        super().__init__(smooth=False, drawFaces=False, drawEdges=True) 
        self.nsim = -1
        self.space = ''
        
        self.w = w
        #č já asi nechcu ani snažit sa něčo zobraziť
        #č z více dimenzí
        if self.w.sample_box.nvar == 3: 
            self.w.slice_changed.connect(self.plot)
            #č slice_changed postačí, zahrnuje i box_runned 
            #self.w.box_runned.connect(self.plot)
            self.w.space_changed.connect(self.plot)
            self.w.redraw_called.connect(self.redraw)

            self.item = QtWidgets.QListWidgetItem('Wireframe')
            self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
            self.item.setCheckState(QtCore.Qt.Checked)
            self.w.list_view.addItem(self.item)

            
            self.w.list_view.itemChanged.connect(self.plot)
        

    def redraw(self):
        self.plot()
        self.w.central_widget.addItem(self)

    def recalculate(self):
        nsim = self.w.slider.value()
        sample_box = self.w.sample_box[:nsim]
        
        self.space = self.w.space
        points = getattr(sample_box, self.w.space)
        tri = spatial.Delaunay(points, incremental=False)
        
        self.points = points
        self.simplices = tri.simplices


        self.facets = np.vstack((self.simplices[:,:3], self.simplices[:,1:],\
                                 self.simplices[:,[0,2,3]], self.simplices[:,[0,1,3]]))



        self.setMeshData(vertexes=self.points, faces=self.facets, drawEdges=True, edgeColor=(0.5, 0.5, 0.5, 1))
        
        # marker
        self.nsim = nsim


    def plot(self):
        if self.item.checkState() and (self.w.slider.value() > 3):
            
            try:
                if (self.nsim != self.w.slider.value()) or (self.space != self.w.space):
                    self.recalculate()
                self.show()
            except BaseException as e:
                msg = "nepovedlo se nám spočítat stěny "
                error_msg = self.__class__.__name__ + ": " + msg + repr(e)
                print(error_msg)
        else:
            self.hide()
        
        


#☺ čota mne ne chočetsa eto dělať
            
##class FlexFrame(GLLinePlotItem):
##    def __init__(self, w):
##        super().__init__(smooth=False, drawFaces=False, drawEdges=True) 
##        self.nsim = -1
##        
##        pos = np.array([[0,0,0],[1,0,0], [0,0,0],[0,1,0], [0,0,0],[0,0,1]])
##        color = np.array([[255, 0, 0, 255],[0, 0, 0, 0], [0, 255, 0, 255],[0, 0, 0, 0], [0, 0, 255, 255],[0, 0, 0, 0]])
##        self.axes = gl.GLLinePlotItem(pos=pos, color=color, width=2, mode='lines')
##        
##        self.w = w
##        self.w.slice_changed.connect(self.plot)
##        self.w.space_changed.connect(self.plot)
##        self.w.redraw_called.connect(self.redraw)
##
##        self.item = QtWidgets.QListWidgetItem('FlexFrame')
##        self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
##        self.item.setCheckState(QtCore.Qt.Checked)
##        self.w.list_view.addItem(self.item)
##        self.w.list_view.itemChanged.connect(self.plot)
##
##
##    def recalculate(self):
##        self.points = self.w.sample_box.tri.points
##
##        self.simplices = self.w.sample_box.tri.simplices
##
##
##        self.facets = np.vstack((self.simplices[:,:3], self.simplices[:,1:],\
##                                 self.simplices[:,[0,2,3]], self.simplices[:,[0,1,3]]))
##
##
##
##        self.setMeshData(vertexes=self.points, faces=self.facets, drawEdges=True, edgeColor=(0.5, 0.5, 0.5, 1))
##
##        
##        
##        # take coordinates in the space, where triangulation has been performed
##        sampled_plan_tri = getattr(self.sample_box, self.sample_box.tri_space)
##        ns = 100
##        
##        if len(self.triangulation) < len(self.sample_box.tri.simplices):
##            x = y = ()
##            gap = len(self.sample_box.tri.simplices) - len(self.triangulation)
##            for __ in range(gap):
##                self.triangulation.append(self.plotWidget.plot(x, y, pen=0.7))
##        
##        for triangle, plot_item in zip(self.sample_box.tri.simplices, self.triangulation):
##            x_tri = np.linspace(sampled_plan_tri[triangle[0],0], sampled_plan_tri[triangle[1],0], ns, endpoint=False)
##            y_tri = np.linspace(sampled_plan_tri[triangle[0],1], sampled_plan_tri[triangle[1],1], ns, endpoint=False)
##            x_tri = np.append(x_tri, np.linspace(sampled_plan_tri[triangle[1],0], sampled_plan_tri[triangle[2],0], ns, endpoint=False))
##            y_tri = np.append(y_tri, np.linspace(sampled_plan_tri[triangle[1],1], sampled_plan_tri[triangle[2],1], ns, endpoint=False))
##            x_tri = np.append(x_tri, np.linspace(sampled_plan_tri[triangle[2],0], sampled_plan_tri[triangle[0],0], ns, endpoint=True))
##            y_tri = np.append(y_tri, np.linspace(sampled_plan_tri[triangle[2],1], sampled_plan_tri[triangle[0],1], ns, endpoint=True))
##            
##            tri_bound_tri = np.array((x_tri, y_tri)).T
##            # vytvořme sample
##            tri_bound = self.sample_box.sampled_plan.new_sample(tri_bound_tri, space=self.sample_box.tri_space)
##            
##            # Update the data
##            #print("Суредасько", tri_bound)
##            plot_item.setData(*getattr(tri_bound, self.space).T)
##                    
##
##
##
##        
##        # marker
##        self.nsim = self.w.sample_box.nsim
##
##
##    def redraw(self):
##        self.plot()
##        self.w.central_widget.addItem(self.axes)
##
##    def plot(self):
##        if self.item.checkState():
##            try:
##                self.recalculate()
##            except BaseException as e:
##                msg = "error during triangulation drawing"
##                error_msg = self.__class__.__name__ + ": " + msg + repr(e)
##                print(error_msg)
##                
##            self.axes.show()
##        else:
##            self.axes.hide()




class Density:
    def __init__(self, w):
        self.w = w
        #č já asi nechcu ani snažit sa něčo zobraziť
        #č z více dimenzí
        if self.w.sample_box.nvar == 3: 
            self.w.space_changed.connect(self.plot)
            self.w.redraw_called.connect(self.redraw)

            
            self.v = gl.GLVolumeItem(self.recalculate())
            self.space = self.w.space
            self.v.scale(0.1, .10, .10)
            self.v.translate(-5,-5,-5)

            self.item = QtWidgets.QListWidgetItem('Density')
            self.item.setFlags(self.item.flags() | QtCore.Qt.ItemIsUserCheckable)
            self.item.setCheckState(QtCore.Qt.Unchecked)
            self.w.list_view.addItem(self.item)

            self.w.list_view.itemChanged.connect(self.plot)
        

    def redraw(self):
        self.plot()
        self.w.central_widget.addItem(self.v)

    def recalculate(self):
        #č strašně drahý, nechce se mi to pořádně udělat
        #data = np.fromfunction(lambda i,j,k:self.w.sample_box.pdf((np.array([[i,j,k]])-[50, 50, 50])/10, self.w.space), (100,100,100))

        # ničemu nerozumím
        grid = (np.mgrid[0:100,0:100, 0:100].T.reshape(-1, 3) - [50, 50, 50])/10
        shape = (100, 100, 100)
        sample = np.array((grid[:, 2], grid[:, 1], grid[:, 0])).T
        data = self.w.sample_box.sample_pdf(sample, self.w.space)
        data = data.reshape((100, 100, 100))
        
        d2 = np.empty(data.shape + (4,), dtype=np.ubyte)
        d2[..., 0] = np.full(shape, 0)
        d2[..., 1] = np.full(shape, 200)
        d2[..., 2] = np.full(shape, 200)
        d2[..., 3] = data * (255./data.max())

        return d2
        
        


    def plot(self):
        if self.item.checkState():
            if self.w.space != self.space:
                self.v.setData(self.recalculate())
                self.space = self.w.space
            self.v.show()
        else:
            self.v.hide()   







"""
=============
Эскерон виӝет 
Widgety odhadů
Estimation widgets
===================
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""

        
        
class SimplexEstimationWidget(qt_plot.FastSimplexEstimationWidget):
        
        
    def callback(self, sx=None, nodes=None, cell_stats=None, simplex=None, *args, **kwargs):
        # stm trianguľaciju pokažde provadí znovu, proto skoro nemá cenu drbat se s její znovupoužitím
        if (simplex is not None) and (simplex.nvar==3):
            ns = 30
            
            
            simplex_tri = getattr(simplex, sx.tri_space)
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
            tri_bound = self.sb_item.sample_box.sampled_plan.new_sample(tri_bound_tri,\
                                                                        space=sx.tri_space)
            
            # draw 
            pos = getattr(tri_bound, self.sb_item.space)
            plot_item = gl.GLLinePlotItem(pos=pos)
            self.sb_item.central_widget.addItem(plot_item)
            
            # uložíme data
            self.triangulation.append((tri_bound, plot_item))

            #
            #čs a eště raz
            #
            simplex_tri = getattr(simplex, sx.tri_space)
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
            tri_bound = self.sb_item.sample_box.sampled_plan.new_sample(tri_bound_tri,\
                                                                        space=sx.tri_space)
            
            # draw 
            pos = getattr(tri_bound, self.sb_item.space)
            plot_item = gl.GLLinePlotItem(pos=pos)
            self.sb_item.central_widget.addItem(plot_item)
            
            # uložíme data
            self.triangulation.append((tri_bound, plot_item))



            
        
        
        #    
        # tečičky
        #

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
                        color = cm.mapToFloat(blue_intensity)
                        #č tam prostě MUSÍ být tuple
                        self_simplex[1].setData(color=tuple(color))

            blue_intensity = cell_probability / self.max_simplices[event]
            color = cm.mapToFloat(blue_intensity)
        else: # outside
            color = (0.6, 0.6, 0.6, 1)
        
        
        # draw tečičky
        #
        pos = getattr(nodes, self.sb_item.space)[:,:3]
        
        #symbolSize = np.sqrt(nodes.w / min(nodes.w)) # not bad
        size = self.param.getValues()['node (pixel) size'][0]
        #č tam prostě MUSÍ být tuple
        plot_item = gl.GLScatterPlotItem(pos=pos, size=size, color=tuple(color))
        self.sb_item.central_widget.addItem(plot_item)
        
        # uložíme data
        self.simplices.append((nodes, plot_item, cell_stats))
        
        
        
        # keep the GUI responsive :)
        self.sb_item.app.processEvents()



        
            
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
                    color = cm.mapToFloat(blue_intensity)
                else: # outside
                    color = (0.6, 0.6, 0.6, 1)
                #symbolSize = np.sqrt(nodes.w / min(nodes.w)) # not bad
                size = self.param.getValues()['node (pixel) size'][0]
                #č tam prostě MUSÍ být tuple
                plot_item.setData(size=size, color=tuple(color))
                plot_item.show()
        

    def on_space_changed(self, *args, **kwargs):
        # nejdřív triangulace
        for tri_bound, plot_item in self.triangulation:
            pos = getattr(tri_bound, self.sb_item.space)
            plot_item.setData(pos=pos)
            plot_item.show()

        # teď tečičky
        for nodes, plot_item, cell_stats in self.simplices:
            pos = getattr(nodes, self.sb_item.space)[:,:3]
            plot_item.setData(pos=pos)
            plot_item.show()
            





class VoronoiEstimationWidget(qt_plot.VoronoiEstimationWidget):

        

    def on_space_changed(self, *args, **kwargs):
        # teď tečičky
        for nodes, plot_item, cell_stats in self.cells:
            pos = getattr(nodes, self.sb_item.space)[:,:3]
            plot_item.setData(pos=pos)
        
    
        
        
            
        
    def node_pf_coloring(self, estimation=None, nodes=None, cell_stats=None, out_nodes=None, *args, **kwargs):
        """
        if nodes and cell_stats  provided we will add them to self.cells
        otherwise function redraw items in self.cells
        """
        
        symbol_size = self.param.getValues()['node (pixel) size'][0]
        if nodes is None:
            for nodes, plot_item, cell_stats in self.cells:
                colors = self.node_pf_colors(nodes, cell_stats)
                plot_item.setData(color=colors, size=symbol_size)
                plot_item.show()
                
        
        # máme nodes, tj. jedeme poprvé        
        else:
            colors = self.node_pf_colors(nodes, cell_stats)
            pos = getattr(nodes, self.sb_item.space)[:,:3]
            plot_item = gl.GLScatterPlotItem(pos=pos, size=symbol_size, color=colors)
            self.sb_item.central_widget.addItem(plot_item)
            
            # uložíme data
            self.cells.append((nodes, plot_item, cell_stats))
            
            # keep the GUI responsive :)
            self.sb_item.app.processEvents()
            
            
            
            
    def node_pf_colors(self, nodes, cell_stats):
        
            
        # zas, нет ножек - нет мультиков
        # node_pf_estimations nemusejí bejt
        try:
            # zkusmě pro jednoduchost 
            # čírou RGB hračku
            npf = nodes.node_pf_estimations
            cm = pg.colormap.ColorMap((0,1), [(0, 255, 0, 255), (255, 0, 0, 255)])
            return cm.mapToFloat(npf)
            
        except BaseException as e:
            msg = "node_pf_coloring has problems "
            error_msg = self.__class__.__name__ + ": " + msg + repr(e)
            print(error_msg)
            # simple coloring
            event = cell_stats['event']
            return self.get_color(event)
        

        
        
    
    def simple_coloring(self, nodes=None, cell_stats=None, *args, **kwargs):
        """
        if nodes and cell_stats  provided we will add them to self.cells
        otherwise function redraw items in self.cells
        """
        symbol_size = self.param.getValues()['node (pixel) size'][0]
        
        if nodes is None:
            for nodes, plot_item, cell_stats in self.cells:
                event = cell_stats['event']
                color = self.get_color(event)
                #symbolSize = np.sqrt(nodes.w / min(nodes.w)) # not bad
                plot_item.setData(color=color, size=symbol_size)
                plot_item.show()
        
        # máme nodes, tj. jedeme poprvé        
        else:
            # draw tečičky
            #
            pos = getattr(nodes, self.sb_item.space)[:,:3]
            
            event = cell_stats['event']
            color = self.get_color(event)
            #symbolSize = np.sqrt(nodes.w / min(nodes.w)) # not bad
            plot_item = gl.GLScatterPlotItem(pos=pos, size=symbol_size, color=color)
            self.sb_item.central_widget.addItem(plot_item)
            
            # uložíme data
            self.cells.append((nodes, plot_item, cell_stats))
            
            # keep the GUI responsive :)
            self.sb_item.app.processEvents()
    
        
            
    def cell_probability_coloring(self, nodes=None, cell_stats=None, *args, **kwargs):
        """
        if nodes and cell_stats  provided we will add them to self.cells
        otherwise function redraw items in self.cells
        """
        symbol_size = self.param.getValues()['node (pixel) size'][0]
        
        if nodes is None:
            for nodes, plot_item, cell_stats in self.cells:
                event = cell_stats['event']
                cell_probability = cell_stats['cell_probability']
                if self.p_cell_max[event] < cell_probability:
                    self.p_cell_max[event] = cell_probability
                
            # přebarvíme tečičky podle obsahu pravděpodobnosti
            for nodes, plot_item, cell_stats in self.cells:
                # draw 
                #pos = getattr(nodes, self.sb_item.space)[:,:3]
                #x, y = (*getattr(nodes, self.sb_item.space).T,)
                
                event = cell_stats['event']
                cell_probability = cell_stats['cell_probability']
                # bez modrého - maximální intenzita
                blue_intensity = 1 - cell_probability / self.p_cell_max[event]
                color = self.get_color(event, blue_intensity)
                #symbolSize = np.sqrt(nodes.w / min(nodes.w)) # not bad
                plot_item.setData(color=color, size=symbol_size)
                plot_item.show()
        
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
                        cell[1].setData(color=color)
            
            # bez modrého - maximální intenzita
            blue_intensity = 1 - cell_probability / self.p_cell_max[event]
            color = self.get_color(event, blue_intensity)
            
            
            # draw tečičky
            #
            pos = getattr(nodes, self.sb_item.space)[:,:3]
            plot_item = gl.GLScatterPlotItem(pos=pos, size=symbol_size, color=color)
            self.sb_item.central_widget.addItem(plot_item)
            
            # uložíme data
            self.cells.append((nodes, plot_item, cell_stats))
            
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
            
        return (*(np.array(color)/255), 1)


"""
===========
♥ Чыры-пыры 
č Jiné
E Miscellaneous
===============
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""

        
        
class CandidatesWidget(qt_plot.CandidatesWidget):


    def run_stm(self):
        #č indikace
        #self.setDisabled(True)
        with pg.BusyCursor():
            
            color_map = self.gradient.colorMap()
            
            try:#č může se tu stat cokoliv
                #č načíst sloupce prostě z libovolného vzorku
                cb = self.sb_item.sample_box.candidates_index.values().__iter__().__next__()
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
                pos = getattr(maxitem, self.sb_item.space)[:,:3]
                max_item = gl.GLScatterPlotItem(pos=pos, size=self.sb_item.px_size*2, color=color_map.mapToFloat(1))
                self.sb_item.central_widget.addItem(max_item)
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
                    
                    pos = getattr(cb, self.sb_item.space)[mask][:,:3]
                    color = color_map.mapToFloat(norm_values)
                    pen = gl.GLScatterPlotItem(pos=pos, size=self.sb_item.px_size, color=color)
                    self.sb_item.central_widget.addItem(pen)
                    self.pens.append(pen)
                
            except BaseException as e:
                msg = ""
                error_msg = self.__class__.__name__ + ": " + msg + repr(e)
                print(error_msg)
            
            
            
        # indikace
        #self.setEnabled(True)
        

    
        

        
