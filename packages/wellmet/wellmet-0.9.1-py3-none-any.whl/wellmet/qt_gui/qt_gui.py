#!/usr/bin/env python
# coding: utf-8

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtWidgets
from pyqtgraph.Qt import QtCore

from pyqtgraph import console

import numpy as np
from . import qt_graph_widgets as gw
from . import qt_pairwise
from .. import reader


### Define a top-level widget to hold everything
class QtGuiWindow(QtWidgets.QMainWindow):
    #č box_runned dublikuje slice_changed
    # do not redraw twice!
    box_runned = QtCore.pyqtSignal()
    space_changed = QtCore.pyqtSignal()
    slice_changed = QtCore.pyqtSignal()
    redraw_called = QtCore.pyqtSignal()
    estimation_added = QtCore.pyqtSignal()
    
    # INHERITED by gl_plot
    # snad pri vykreslování argy-kvargy nevádí
    def __init__(self, sample_box, space='R', *args, **kwargs):
        
        #E former self.w = QtGui.QMainWindow()
        self.app = pg.mkQApp()
        super().__init__()
        try:
            self.setWindowTitle("%sD: %s" %(sample_box.nvar, sample_box.gm_signature))
        except:
            self.setWindowTitle("%sD nodes" % sample_box.nvar)
        
        # for debug
        # container for errors
        # to trace errors
        self.errors = []
        
        self.kwargs = kwargs
        self.sample_box = sample_box
        #sample_box.sample_box._log = self.logger
        self.last_shot = None
        try:
            self.space = self.sample_box.tri_space
        except AttributeError:
            self.space = space
        
        # "zapnuté" prostory
        #self.spaces = ['R', 'aR', 'Rn', 'aRn', 'P', 'aP', 'GK', 'aGK', 'G', 'aG', 'U', 'aU']
        self.spaces = ['R', 'aR', 'Rn', 'aRn', 'P', 'GK', 'G', 'aG', 'U', 'aU']

        # initialize central widget
        self.initialize_central_widget()
        
        # common setup
        self.setup()

        self.plot_setup()
        
        ## Display the widget as a new window
        self.show()

        #
        self.redraw_called.emit()
        
        ## Start the Qt event loop
        self.app.exec_()
    
    def setup_menubar(self):    
        self.bar = self.menuBar()
        self.file_menu = self.bar.addMenu("File")
        #č kontejner jen aby Python mně Cečkové objekty nevymazal
        self.file_actions = [] 
        load_coordinates_action = QtGui.QAction("Load coordinates", self)
        load_coordinates_action.triggered.connect(self.load_coordinates)
        self.file_menu.addAction(load_coordinates_action)
        self.file_actions.append(load_coordinates_action)
        
        export_coordinates_action = QtGui.QAction("Export coordinates", self)
        export_coordinates_action.triggered.connect(self.export_coordinates)
        self.file_menu.addAction(export_coordinates_action)
        self.file_actions.append(export_coordinates_action)
        
        import_samples_action = QtGui.QAction("Import samples", self)
        import_samples_action.triggered.connect(self.import_samples)
        self.file_menu.addAction(import_samples_action)
        self.file_actions.append(import_samples_action)
        
        export_samples_action = QtGui.QAction("Export samples", self)
        export_samples_action.triggered.connect(self.export_samples)
        self.file_menu.addAction(export_samples_action)
        self.file_actions.append(export_samples_action)
        
        self.view = self.bar.addMenu("View")
        
        self.graph_menu = self.bar.addMenu("Box")
        self.add_random_points_action = QtGui.QAction("Add random points", self)
        self.add_random_points_action.triggered.connect(self.add_random_points)
        self.graph_menu.addAction(self.add_random_points_action)
        self.batch_run_action = QtGui.QAction("Batch run", self)
        self.batch_run_action.triggered.connect(self.batch_run)
        self.graph_menu.addAction(self.batch_run_action)
        #self.gen_dmatrix_action = QtGui.QAction("Matrix view...", self)
        #self.gen_dmatrix_action.triggered.connect(self.gen_dmatrix)
        #self.graph_menu.addAction(self.gen_dmatrix_action)
        
        # optional feature
        self.initialize_matplotlib_menu()
        
    # should be INHERITED by gl_plot
    def initialize_matplotlib_menu(self):
        try: # entire optional functionality
            from ..mplot import show_ax, show_ax3d, show_fig
            from ..mplot import maxes
            from ..mplot import maxes3d
            from ..mplot import mfigs
            from ..mplot import misc as mmisc
            self.matplotlib_menu = self.bar.addMenu("Matplotlib")
            self.matplotlib_actions = []
            
            self.matplotlib_2D_menu = self.matplotlib_menu.addMenu("2D plots")
            self._setup_mpl_submenu(self.matplotlib_2D_menu, maxes, show_ax)
            
            self.matplotlib_3D_menu = self.matplotlib_menu.addMenu("3D plots")
            self._setup_mpl_submenu(self.matplotlib_3D_menu, maxes3d, show_ax3d)
                
            self.matplotlib_figs_menu = self.matplotlib_menu.addMenu("Complex plots")
            self._setup_mpl_submenu(self.matplotlib_figs_menu, mfigs, show_fig)
            
            self.matplotlib_misc_menu = self.matplotlib_menu.addMenu("Others")
            for smthng in mmisc.__all__:
                mpl_action = QtGui.QAction(smthng, self)
                show_mpl = self._mpl_prepare_fn(getattr(mmisc, smthng))
                mpl_action.triggered.connect(show_mpl)
                self.matplotlib_misc_menu.addAction(mpl_action)
                # prevent GC from wiping out both Qt object and our function
                self.matplotlib_actions.append((mpl_action, show_mpl))
                
        except ImportError as e:
            msg = "Matplotlib related features are unavailiable"
            print(self.__class__.__name__ + ":", msg, repr(e))
    
    def _setup_mpl_submenu(self, menu, module, handler):
        for drawing in module.__all__:
            mpl_action = QtGui.QAction(drawing, self)
            # do not really understand what I am doing :(
            # try to show_mpl remember its actual drawing string
            show_mpl = self._mpl_prepare_show_fn(handler, getattr(module, drawing))
            mpl_action.triggered.connect(show_mpl)
            menu.addAction(mpl_action)
            # prevent GC from wiping out both Qt object and our function
            self.matplotlib_actions.append((mpl_action, show_mpl))
    
    def _mpl_prepare_show_fn(self, show, to_draw):
        return lambda: show(to_draw, self.get_sample_box(), space=self.space)
        
    def _mpl_prepare_fn(self, fn):
        return lambda: fn(sample_box=self.get_sample_box(), space=self.space)
        
    def get_sample_box(self):
        nsim = self.slider.value()
        if nsim == self.sample_box.nsim:
            return self.sample_box
        else:
            return self.sample_box[:nsim]
    
    # INHERITED by gl_plot
    # intended as a common setup function
    def setup(self):    
        
        
        self.setup_menubar()
        
        ### Create some widgets to be placed inside
        self.combo_space = pg.ComboBox(items=self.spaces, default=self.space)
        self.combo_space.activated[str].connect(self.change_space)
        
        
        self.label_nsim = QtWidgets.QLabel()
        self.label_nsim.setText(str(self.sample_box.nsim))
        
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.valueChanged.connect(self._slider_chainged)
        self.slider.sliderReleased.connect(lambda:self.slice_changed.emit())
        self.slider.setMaximum(self.sample_box.nsim)
        self.slider.setValue(self.sample_box.nsim)
        
        #č jen aby se slider probral, když uživatel ručně přídá bodíky
        self.redraw_called.connect(self.wake_up_slider)
        self.box_runned.connect(self.wake_up_slider)
        
        self.btn = QtWidgets.QPushButton('run box')
        self.btn.clicked.connect(self.run_sb)
        
#        self.btn2 = QtWidgets.QPushButton('connect/disconnect')
#        self.btn2.setCheckable(True)
#        self.btn2.clicked.connect(self.bx_connect)
        
        self.btn3 = QtWidgets.QPushButton('redraw')
        self.btn3.clicked.connect(lambda:self.redraw_called.emit())
        
        
        ## Create a grid layout to manage the widgets size and position
        self.layout = pg.LayoutWidget()
        self.setCentralWidget(self.layout)
        #self.w.setLayout(self.layout)

        # 
        self.list_view = QtWidgets.QListWidget()
        
        ## Add widgets to the layout in their proper positions
        #self.layout.addWidget(self.list_view, 0, 0, 2, 1) 
        self.layout.addWidget(self.combo_space, 0, 0)   
        self.layout.addWidget(self.slider, 0, 1)   
        self.layout.addWidget(self.label_nsim, 0, 2)
        self.layout.addWidget(self.btn, 0, 3) 
        #self.layout.addWidget(self.btn2, 0, 4)
        self.layout.addWidget(self.btn3, 0, 4) 
        self.layout.addWidget(self.central_widget, 1, 0, 1, 5)
        


        # status bar, mainly to observe BlackBox
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.btn_continue = QtWidgets.QPushButton('continue')
        self.continue_label = QtWidgets.QLabel()
#        self.continue_layout = QtGui.QHBoxLayout()
#        self.continue_layout.addWidget(self.btn_continue)
#        self.continue_layout.addWidget(self.continue_label)
        self.statusBar.addWidget(self.btn_continue)
        self.statusBar.addWidget(self.continue_label)
        self.btn_continue.hide()
        self.continue_label.hide()
        
        #self.statusBar.showMessage("Vitáme vás u nás!")


        
        
        # Dockables, najzajimavejší věc
        self.dockables = []
        
        
        dock = QtWidgets.QDockWidget("Interactive python console", self)
        dock.setWidget(console.ConsoleWidget(
                    namespace={**locals(), **globals(), 'box':self.sample_box}))
        self.dockables.append(dock)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock)
        

#        dock = QtWidgets.QDockWidget("BlackBox output", self)
#        self.output_label = QtWidgets.QLabel()
#        dock.setWidget(self.output_label)
#        self.dockables.append(dock)
#        self.tabifyDockWidget(self.dockables[0], dock)
        
        #č graphy už nemusí jít po stm widgetech
        self.setup_graph_widgets()


        dock = dock_l = QtWidgets.QDockWidget("Box tree", self)
        dock.setWidget(BoxTreeWidget(self, dock))
        self.dockables.append(dock)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
        
        
        
        dock = QtWidgets.QDockWidget("View", self)
        dock.setWidget(self.list_view)
        self.dockables.append(dock)
        self.tabifyDockWidget(dock_l, dock)
        
        
        
        
        for dock in self.dockables:
            self.view.addAction(dock.toggleViewAction())
            #dock.setFloating(True)
      
        #self.w.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.items)
       
    def setup_graph_widgets(self):
        if not hasattr(self.sample_box, 'estimations'):
            dock = QtWidgets.QDockWidget("GRaph", self)
            dock.setWidget(gw.GRaph(self, None, dock))
            self.dockables.append(dock)
            self.tabifyDockWidget(self.dockables[0], dock)
            
            return
            
        if hasattr(self.sample_box, 'box_estimations'):
            dock = QtWidgets.QDockWidget("Estimation data", self)
            widget = EstimationTableWidget(self.sample_box.box_estimations, 
                                                        self.box_runned, dock)
            dock.setWidget(widget)
            self.dockables.append(dock)
            self.tabifyDockWidget(self.dockables[0], dock)
            
            self.box_estimation_data = gw.BoxEstimationData(
                        self.sample_box.box_estimations, self.box_runned, self)
        else:
            self.box_estimation_data = \
                            gw.SimplexEstimationData(self.sample_box, self)
            
        
        if hasattr(self.sample_box, 'pf_exact'):
            pf_exact = self.sample_box.pf_exact
            
            dock = QtWidgets.QDockWidget("Error graph", self)
            dock.setWidget(gw.ErrorGraph(pf_exact, self.box_estimation_data,  dock))
            self.dockables.append(dock)
            self.tabifyDockWidget(self.dockables[0], dock)
        else:
            pf_exact = -1
            
        dock = QtWidgets.QDockWidget("Estimation graph", self)
        widget = gw.EstimationGraph(pf_exact, self.box_estimation_data,  dock)
        dock.setWidget(widget)
        self.dockables.append(dock)
        self.tabifyDockWidget(self.dockables[0], dock)
        
        
        dock = QtWidgets.QDockWidget("GRaph", self)
        dock.setWidget(gw.GRaph(self, self.box_estimation_data, dock))
        self.dockables.append(dock)
        self.tabifyDockWidget(self.dockables[0], dock)
       
    csv_filter = "CSV files (*.csv)"
    npy_filter = "NumPy binary files (*.npy)"
    txt_filter = "Text files (*.txt)"
    gz_filter = "Compressed text files (*.gz)"
       
    def load_coordinates(self):
        """
        Loads numpy data and adds them to the sample_box
        """ 
        nodes = None
        filter = self.npy_filter + ';;' + self.txt_filter + ';;' + self.gz_filter
        wt = self.sample_box
        
        try:
            filename, filter = pg.FileDialog.getOpenFileName(
                    parent=self, 
                    caption="Load coordinates",
                    directory="store/%s_%sD.npy" % (wt.gm_signature, wt.nvar),
                    filter=filter, 
                    initialFilter=self.npy_filter,
                    #options=pg.FileDialog.Option.DontConfirmOverwrite
                    )
            if filename:
                if filter == self.npy_filter:
                    raw_nodes = np.load(filename) 
                else:
                    raw_nodes = np.loadtxt(filename) 
                
                # create sample
                nodes = wt.f_model.new_sample(sample=raw_nodes, \
                                    space=self.space, extend=False)
                
        except BaseException as e:
            print(self.__class__.__name__ + ":", \
                            " coordinates loading failed", repr(e))
                            
        #č zde jíž nemá cenu chytat chyby. Sbohem!
        if nodes is not None:
            # run!
            wt.run_sample(nodes)
            self.box_runned.emit()
        
        
    def export_coordinates(self):
        """
        Exports current sample box coordinates
        """ 
        filter = self.npy_filter + ';;' + self.txt_filter + ';;' + self.gz_filter
        wt = self.sample_box
        
        filename, filter = pg.FileDialog.getSaveFileName(
                parent=self, 
                caption="Export coordinates",
                directory="store/%s_%sD.npy" % (wt.gm_signature, wt.nvar),
                #filter=csv_filter,
                filter=filter, 
                initialFilter=self.npy_filter,
                #options=pg.FileDialog.Option.DontConfirmOverwrite
                )
        if filename:
            nsim = self.slider.value()
            nodes = self.sample_box.f_model[:nsim]
            raw_nodes = getattr(nodes, self.space)
            try:
                if filter == self.npy_filter:
                    np.save(filename, raw_nodes, allow_pickle=False)
                else:
                    np.savetxt(filename, raw_nodes) 
            except BaseException as e:
                print(self.__class__.__name__ + ":", \
                            " coordinates export failed", repr(e)) 
        
        
        
    def import_samples(self):
        wt = self.sample_box
        
        filename, __filter = pg.FileDialog.getOpenFileName(
                parent=self, 
                caption="Import samples",
                directory="store/%s_%sD.csv" % (wt.gm_signature, wt.nvar),
                #filter=csv_filter,
                filter=self.csv_filter, # + ";;All files(*)", 
                initialFilter=self.csv_filter,
                #options=pg.FileDialog.Option.DontConfirmOverwrite
                )
        if filename and (filename[-4:]=='.csv'):
            #č Reader vždy dopíše '.csv' na konci souboru
            #č nechcu to teď měnit
            filename = filename[:-4]
            
            #č nechcu chytat žádné chyby. Sbohem!
            sample_box = reader.reader(filename, f_model=wt.f_model)
            wt.add_sample(sample_box)
            self.box_runned.emit()

    def export_samples(self):
        wt = self.sample_box
        
        filename, __filter = pg.FileDialog.getSaveFileName(
                parent=self, 
                caption="Export samples",
                directory="store/%s_%sD.csv" % (wt.gm_signature, wt.nvar),
                #filter=csv_filter,
                filter=self.csv_filter, # + ";;All files(*)", 
                initialFilter=self.csv_filter,
                #options=pg.FileDialog.Option.DontConfirmOverwrite
                )
        if filename:
            #č Reader vždy dopíše '.csv' na konci souboru
            #č nechcu to teď měnit
            if filename[-4:]=='.csv':
                filename = filename[:-4]
            nsim = self.slider.value()
            reader.export(filename, wt[:nsim])


    #
    #č Tlačítka!
    #

    # INHERITED by gl_plot
    def _slider_chainged(self, value):
        #č .setMaximum() nezpůsobuje emitování slice_changed, jsem zkontroloval
        self.slider.setMaximum(self.sample_box.nsim)
        self.label_nsim.setText(str(value))
        if not self.slider.isSliderDown(): # co to vůbec děla?
            self.slice_changed.emit()
            
    # INHERITED by gl_plot
    def change_space(self, space):
        self.space = space
        self.space_changed.emit()
        #self.plot_widget_2d()
        #self.slice_plot_data()
        
    # INHERITED by gl_plot
    def run_sb(self):
        with pg.BusyCursor():
            self.last_shot = self.sample_box()
            self.box_runned.emit()

    def wake_up_slider(self):
        # slider
        #č zpusobí slice_changed
        self.slider.setMaximum(self.sample_box.nsim)
        self.slider.setValue(self.sample_box.nsim)
        
    # INHERITED by gl_plot
    def bx_connect(self):
        if self.btn2.isChecked():
            try:
                self.sample_box.connect(self.logger)
            except BaseException as e:
                print(self.__class__.__name__ + ":", "connection to BlackBox failed", repr(e))
        else:
            try:
                self.sample_box.disconnect()
            except BaseException as e:
                print(self.__class__.__name__ + ":", "error while disconnecting of BlackBox", repr(e))
        
    # INHERITED by gl_plot
    def logger(self, *args, msg="", indent=0, **kwargs):
        self.continue_label.setText("BlackBox: " + msg)
        self.output_label.setText(str(args) + str(kwargs))
        
        loop = QtCore.QEventLoop()
        self.btn_continue.clicked.connect(loop.quit)
        self.btn_continue.show()
        self.continue_label.show()
        # i want to clear status bar temporaly
        status = self.statusBar.currentMessage()
        self.statusBar.clearMessage()
        
        loop.exec_()  # Execution stops here until finished called  
        
        self.btn_continue.hide()
        self.continue_label.hide()
        self.statusBar.showMessage(status)
        
    def add_random_points(self):
        ns, ok = QtWidgets.QInputDialog.getInt(
                    self,"Add random points","number", value=1, min=1)
        if ok:
            wt = self.sample_box
            nodes = wt.f_model(ns)
            wt.run_sample(nodes)
            self.box_runned.emit()
        
    def batch_run(self):
        runs, ok = QtWidgets.QInputDialog.getInt(
                    self,"Batch run","runs", value=100, min=1)
  
        if ok:
            with pg.ProgressDialog("Running..", 0, runs,\
                         cancelText='Stop', busyCursor=True) as dlg:
                for i in range(runs):
                    # keep the GUI responsive :)
                    self.app.processEvents()
                    
                    self.last_shot = self.sample_box()
                
                    # slider
                    #č zpusobí slice_changed
                    self.slider.setMaximum(self.sample_box.nsim)
                    self.slider.setValue(self.sample_box.nsim)
                    
                    self.box_runned.emit()
                    
                    dlg += 1
                    if dlg.wasCanceled():
                        break
                    
    
    def gen_dmatrix(self):
        qt_pairwise.MatrixWindow(self.sample_box, self.space, parent=self)
         



"""
===========
♥ Чыры-пыры 
č Jiné
E Miscellaneous
===============
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""


class EstimationTableWidget(pg.TableWidget):
    def __init__(self, estimations, signal,  parent=None):
        super().__init__(parent)
        # sb like samplebox, of course
        self.estimations = estimations
        signal.connect(self.update)
        
        self.setFormat('%g')
        self.update(self.estimations)
        
        

    def update(self, *args, **kwargs):
        nrow = self.rowCount()
        if nrow >= len(self.estimations):
            return 
            
        if nrow:
            self.appendData(self.estimations[nrow:])
        elif hasattr(self.estimations[0], '_asdict'):
            # in case of namedtuples
            self.setData([self.estimations[0]._asdict()])
            self.appendData(self.estimations[1:])
        else:
            self.setData(self.estimations)
            




class BoxTreeWidget(pg.LayoutWidget):
    """
    """
    # I'd like to get access to the samplebox stuff via the container's reference, 
    # but relying to Qt's parent mechanism makes me worry.
    def __init__(self, samplebox_item,  parent=None, *args, **kwargs):
        super().__init__(parent)
        # sb like samplebox, of course
        self.sb_item = samplebox_item
        
        
        self.btn = QtWidgets.QPushButton('update')
        self.addWidget(self.btn, row=0, col=0)
        self.btn.clicked.connect(self.update)
        
        #self.tree = pg.DataTreeWidget(self, data=self.get_data(samplebox_item))
        self.tree = pg.DataTreeWidget(self, data=dict())
        self.addWidget(self.tree, row=1, col=0)

    def update(self, *args, **kwargs):
        try:
            self.tree.setData(self.get_data(self.sb_item), hideRoot=True)
        except BaseException as e:
            msg = ""
            error_msg = self.__class__.__name__ + ": " + msg + repr(e)
            print(error_msg)
            
    @staticmethod
    def get_data(self): #č nenechej si splest tím "self", je to prostě reference na QtGuiPlot2D
        data_tree = dict()
        data_tree['self.sample_box'] = self.sample_box.__dict__
        try: # shapeshare
            data_tree['self.sample_box.shapeshare'] = self.sample_box.shapeshare.__dict__
        except AttributeError:
            pass
        try:
            data_tree['self.sample_box.dicebox'] = self.sample_box.dicebox.__dict__
        except AttributeError:
            pass
        try:
            data_tree['self.sample_box.reader'] = self.sample_box.reader.__dict__
        except AttributeError:
            pass
        try:
            data_tree['self.sample_box.samplebox'] = self.sample_box.samplebox.__dict__
        except AttributeError:
            pass
        try:
            data_tree['self.sample_box.candybox'] = self.sample_box.candybox.__dict__
        except AttributeError:
            pass
        try:
            data_tree['self.sample_box.f_model'] = self.sample_box.f_model.__dict__
        except AttributeError:
            pass
            
        return data_tree


        
