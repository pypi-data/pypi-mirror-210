#!/usr/bin/env python
# coding: utf-8

import gc
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtWidgets
from pyqtgraph.Qt import QtCore

import numpy as np
from scipy import spatial # for distance matrix
from .. import wireframe
from .. import reader


#č pg trik, aby GC nám nevymazal paměť
windows = set()

### Define a top-level widget to hold everything
class MatrixWindow(QtWidgets.QMainWindow):
    #č box_runned dublikuje slice_changed
    # do not redraw twice!
    box_runned = QtCore.pyqtSignal()
    space_changed = QtCore.pyqtSignal(str)
    metric_changed = QtCore.pyqtSignal(str)
    slice_changed = QtCore.pyqtSignal(int)
    redraw_called = QtCore.pyqtSignal()
    
    
    def __init__(self, sample_box, space='R', parent=None, *args, **kwargs):
        try:
            self.box_runned = parent.box_runned
            self.app = parent.app
        except:
            self.app = pg.mkQApp() #оӵ кулэ-а?
            ## Start the Qt event loop
            self.app.exec_()
            
        super().__init__()
        
        #č pg trik, aby GC nám nevymazal paměť
        windows.add(self)
        
        
        
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
        self.space = space
        self.metric = 'euclidean'
        
        # "zapnuté" prostory
        #self.spaces = ['R', 'aR', 'Rn', 'aRn', 'P', 'aP', 'GK', 'aGK', 'G', 'aG', 'U', 'aU']
        self.spaces = ['R', 'aR', 'Rn', 'aRn', 'P', 'GK', 'G', 'aG', 'U', 'aU']
        
        #self.metrics = ['1', '2', 'inf']
        self.metrics = ['euclidean', 'cityblock', 'chebyshev',
                        'seuclidean', 'sqeuclidean', 'cosine',
                        'correlation', 
                        'canberra', 'braycurtis', 'mahalanobis' ]
        
        # common setup
        self.setup()
        
        ## Display the widget as a new window
        self.show()

        #
        self.redraw_called.emit()
        
        
    
    def closeEvent(self, event):
        #č nejsem 100% jist co dělám.
        #č Ale když už ImageView API 
        #č vysloveně nabízí "korektní" .close()
        #č tak deme do toho
        self.image_view.close()
        windows.discard(self)
        event.accept() # let the window close
    
    
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
        
        
    def get_sample_box(self):
        nsim = self.slider.value()
        if nsim == self.sample_box.nsim:
            return self.sample_box
        else:
            return self.sample_box[:nsim]
    
    
    # intended as a common setup function
    def setup(self):    
        self.setup_menubar()
        
        ### Create some widgets to be placed inside
        self.combo_metric = pg.ComboBox(items=self.metrics, default=self.metric)
        self.combo_metric.activated[str].connect(self.change_metric)
        
        self.combo_space = pg.ComboBox(items=self.spaces, default=self.space)
        self.combo_space.activated[str].connect(self.change_space)
        
        
        self.label_nsim = QtWidgets.QLabel()
        self.label_nsim.setText(str(self.sample_box.nsim))
        
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.valueChanged.connect(self._slider_chainged)
        self.slider.sliderReleased.connect(lambda:self.slice_changed.emit(self.slider.value()))
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

        ## Create a grid layout to manage the widgets size and position
        self.layout = pg.LayoutWidget()
        self.setCentralWidget(self.layout)
        
        self.list_view = QtWidgets.QListWidget()

        self.image_view = MView(self, parent=self.layout)
        
        self.btn3 = QtWidgets.QPushButton('auto levels')
        self.btn3.clicked.connect(lambda:self.image_view.autoLevels())
        
        

        
        
        
        ## Add widgets to the layout in their proper positions
        #self.layout.addWidget(self.list_view, 0, 0, 2, 1) 
        self.layout.addWidget(self.combo_metric, 0, 0)  
        self.layout.addWidget(self.combo_space, 0, 1)   
        self.layout.addWidget(self.slider, 0, 2)   
        self.layout.addWidget(self.label_nsim, 0, 3)
        self.layout.addWidget(self.btn, 0, 4) 
        #self.layout.addWidget(self.btn2, 0, 4)
        self.layout.addWidget(self.btn3, 0, 5) 
        self.layout.addWidget(self.image_view, 1, 0, 1, 6)
        


        # status bar, mainly to observe BlackBox
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        
        self.dm = DistanceMatrix(self)
        
        # Dockables, najzajimavejší věc
        self.dockables = []
        
        
        
        dock = QtWidgets.QDockWidget("View", self)
        dock.setWidget(self.list_view)
        self.dockables.append(dock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        
        
        dock = QtWidgets.QDockWidget("Contacts", self)
        dock.setWidget(ContactWidget(self, dock))
        self.dockables.append(dock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        
        
        
        for dock in self.dockables:
            self.view.addAction(dock.toggleViewAction())
            #dock.setFloating(True)
    
    
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
            self.slice_changed.emit(value)
            
    
    def change_space(self, space):
        self.space = space
        self.space_changed.emit(space)
        
    def change_metric(self, metric):
        self.metric = metric
        self.metric_changed.emit(metric)
        
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
                    

        

# piece of code from pyqtgraph examples
class CustomViewBox(pg.ViewBox):
    ## reimplement mouseDragEvent to disable continuous axis zoom
    def mouseDragEvent(self, ev, axis=None):
        if ev.button() == QtCore.Qt.MouseButton.RightButton:
            ev.ignore()
        else:
            pg.ViewBox.mouseDragEvent(self, ev, axis=axis)




right_button = QtCore.Qt.MouseButton.RightButton
left_button = QtCore.Qt.MouseButton.LeftButton

class MView(pg.ImageView):
    mouse_moved = QtCore.pyqtSignal(int, int)
    mouse_clicked = QtCore.pyqtSignal(int, int)
    mouse_double_clicked = QtCore.pyqtSignal(int, int)
    mouse_right_dragged = QtCore.pyqtSignal(int, int)
    
        
    def __init__(self, w, *args, **kwargs):
        self.vb = CustomViewBox()
        self.pi = pg.PlotItem(viewBox=self.vb)
        super().__init__(*args, view=self.pi, **kwargs) #axisOrder='row-major',
        
        w.slice_changed.connect(self.on_slice_changed)
        self.app = w.app
        
        self.nsim = nsim = w.slider.value()
        
        self.data = np.empty((3, nsim, nsim))
        self.data[2] = -1 #č kvuli ContactWidgetu
        
        self.show()
        #self.setImage(data, levelMode='rgba')
        #self.setBackground('w')
        
        
        self.ar_item = QtWidgets.QListWidgetItem('auto range')
        self.ar_item.setFlags(self.ar_item.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.ar_item.setCheckState(QtCore.Qt.Checked)
        w.list_view.addItem(self.ar_item)
        
        self.al_item = QtWidgets.QListWidgetItem('auto levels')
        self.al_item.setFlags(self.al_item.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.al_item.setCheckState(QtCore.Qt.Checked)
        w.list_view.addItem(self.al_item)
        
        
        
        self.proxy  = pg.SignalProxy(self.pi.scene().sigMouseMoved, 
                                    rateLimit=60, slot=self.on_mouse_moved)
        self.x = -1
        self.y = -1
                                    
        self.pi.scene().sigMouseClicked.connect(self.on_click)
        
    
    def __setattr__(self, attr, value):
        if attr == 'red':
            self.data[0] = value
        elif attr == 'green':
            self.data[1] = value
        elif attr == 'blue':
            self.data[2] = value
        else:
            self.__dict__[attr] = value
            
            
            
    def __getattr__(self, attr):
        if attr == 'red':
            return self.data[0]
        if attr == 'green':
            return self.data[1]
        if attr == 'blue':
            return self.data[2]
        raise AttributeError(attr)
    
    
    def on_slice_changed(self, nsim):
        #č resize nejde. Ani s gc. Asi pyqtgraph drží referenci
        #č i když já pekně vím, že ta data kopíruje a pro Qt normalizuje
        self.data = np.empty((3, nsim, nsim))
        #č zelené-červené barvy přepíše distance matrix
        #č za modrou ale nikdo zodpovednost nenese
        self.data[2] = -1 #č kvuli ContactWidgetu 
        self.nsim = nsim
    
    
    def update(self, **kwargs):
        if 'autoRange' not in kwargs:
            kwargs['autoRange'] = self.ar_item.checkState()
        if 'autoLevels' not in kwargs:
            kwargs['autoLevels'] = self.al_item.checkState()
        
        self.setImage(self.data.T, levelMode='rgba', **kwargs)
        
    
    def on_mouse_moved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.pi.sceneBoundingRect().contains(pos):
            mousePoint = self.pi.vb.mapSceneToView(pos)
            x = int(mousePoint.x())
            y = int(mousePoint.y())
            if (x >= 0) and (x < self.nsim) and (y >= 0) and (y < self.nsim):
                self._mouse_moved(x, y)
            else:
                self._mouse_moved(-1, -1)
        else:
            self._mouse_moved(-1, -1)
            
    def _mouse_moved(self, x, y):
        if (x != self.x) or (y != self.y):
            self.x = x
            self.y = y
            self.mouse_moved.emit(x, y)
            if self.app.mouseButtons() == right_button:
                self.mouse_right_dragged.emit(x, y)
            
            
    
    def on_click(self, evt):
        if self.x == -1:
            return None
        if evt.double():
            self.mouse_double_clicked.emit(self.x, self.y)
        elif evt.button() == left_button:
            self.mouse_clicked.emit(self.x, self.y)
            



class DistanceMatrix:
    def __init__(self, w):
        self.w = w
        
        w.image_view.mouse_moved.connect(self.on_mouse_moved)
        
        w.metric_changed.connect(self.on_some_stuff_changed)
        w.space_changed.connect(self.on_some_stuff_changed)
        w.slice_changed.connect(self.on_nsim_changed)
        w.redraw_called.connect(self.on_some_stuff_changed)
        
        n = w.slider.value() 
        self.condensed_matrix = np.empty(n * (n - 1) // 2)
        self.nsim = n
        
    def on_nsim_changed(self, n):
        self.condensed_matrix.resize(n * (n - 1) // 2)
        self.nsim = n
        
        self.on_some_stuff_changed()
    
    def on_some_stuff_changed(self, *args, **kwargs):
        sample_box = self.w.get_sample_box()
        nsim = sample_box.nsim
        if nsim > 0:
            X = getattr(sample_box, self.w.space)
            spatial.distance.pdist(X, self.w.metric, out=self.condensed_matrix)
            
            mask = np.zeros((nsim, nsim))
            
            failure_points = sample_box.failure_points 
            mask[failure_points] += 0.5
            mask[:, failure_points] += 0.5
            
            dmatrix = spatial.distance.squareform(self.condensed_matrix)
            
            self.w.image_view.red = dmatrix * mask
            self.w.image_view.green = dmatrix * (1 - mask)
            self.w.image_view.update()
        
        self.w.statusBar.showMessage("")
    
    
    def on_mouse_moved(self, x, y):
        if x == -1:
            self.w.statusBar.showMessage("")
            return None
            
        if x != y:
            m = self.nsim
            i, j = min(x, y), max(x, y)
            entry = m * i + j - ((i + 2) * (i + 1)) // 2
            val = self.condensed_matrix[entry]
        else:
            val = 0
        msg = "distance between %d and %d is %g" % (x, y, val)
        self.w.statusBar.showMessage(msg)







class ContactWidget(pg.LayoutWidget):
    def __init__(self, w,  parent=None):
        super().__init__(parent)
        self.w = w
        
        w.image_view.mouse_moved.connect(self.on_mouse_moved)
        w.image_view.mouse_clicked.connect(self.on_mouse_dragged)
        w.image_view.mouse_double_clicked.connect(self.on_double_click)
        w.image_view.mouse_right_dragged.connect(self.on_mouse_dragged)
        
        w.space_changed.connect(self.on_space_changed)
        w.slice_changed.connect(self.on_nsim_changed)
        #w.redraw_called.connect(self.hide)
        
        n = w.slider.value() 
        size = n * (n - 1) // 2
        self.condensed_contacts = np.zeros(size, dtype=np.int8)
        self.mask = np.tri(n, k=-1, dtype=bool).T
        self.nsim = n
        
        self.setup()
        self.kwargs = {}
        self.check_contact = self.peacefully_check_contact
        self.got_user_consent = False
        self.setup_CS()
        
    def on_nsim_changed(self, n):
        try:
            del self.qframe
            del self.condensed_qontacts
        except AttributeError:
            pass
        size = n * (n - 1) // 2
        gc.collect()
        self.condensed_contacts.resize(size)
        self.condensed_contacts[:] = 0
        self.mask = np.tri(n, k=-1, dtype=bool).T
        self.nsim = n
        
        self.on_space_changed()
    
    def on_space_changed(self, *args, **kwargs):
        self.setup_CS()
    
    
    def on_mouse_moved(self, x, y):
        if (x == -1) or (x == y):
            self.status_label.setText("")
            return None
            
        m = self.nsim
        i, j = min(x, y), max(x, y)
        entry = m * i + j - ((i + 2) * (i + 1)) // 2
        try:
            if self.condensed_qontacts[entry]:
                self.status_label.setText("There is DEFINITELY contact between %d and %d" % (x, y))
            else:
                self.status_label.setText("There is definitely NO contact between %d and %d" % (x, y))
        except AttributeError:
            val = self.condensed_contacts[entry]
            if val > 0:
                self.status_label.setText("There IS contact between %d and %d" % (x, y))
            elif val < 0:
                self.status_label.setText("There is NO contact between %d and %d" % (x, y))
            else:
                self.status_label.setText("")
        
        
    def on_mouse_dragged(self, x, y):
        if (x == -1) or (x == y):
            return None
            
        m = self.nsim
        i, j = min(x, y), max(x, y)
        entry = m * i + j - ((i + 2) * (i + 1)) // 2
        val = self.check_contact(entry, i, j)
        self.show()
        
        if val > 0:
            self.status_label.setText("There IS contact between %d and %d" % (x, y))
        else:
            self.status_label.setText("There is NO contact between %d and %d" % (x, y))
            
    def on_double_click(self, x, y):
        if (x == -1) or (x == y):
            return None
            
        m = self.nsim
        i, j = min(x, y), max(x, y)
        entry = m * i + j - ((i + 2) * (i + 1)) // 2
        val = self.force_check_contact(entry, i, j)
        self.show()
        
        if val > 0:
            self.status_label.setText("There IS contact between %d and %d" % (x, y))
        else:
            self.status_label.setText("There is NO contact between %d and %d" % (x, y))
            
        
    def discover(self):
        nsim = self.nsim
        if  nsim > 0:
            self.stopbtn.setEnabled(True)
            self.stopbtn.setCheckable(True)
            
            if self.param.getValues()['check_events'][0] == 'All pairs':
                for i in range(nsim-1, -1, -1):
                    # keep the GUI responsive :)
                    self.show()
                    self.w.app.processEvents()
                    if self.stopbtn.isChecked():
                        break
                    preentry = nsim * i - ((i + 2) * (i + 1)) // 2
                    for j in range(i+1, nsim):
                        self.check_contact(preentry + j, i, j)
            elif self.param.getValues()['check_events'][0] == 'Failure and mixed pairs':
                failsi = self.w.get_sample_box().failsi
                for i in range(nsim-1, -1, -1):
                    # keep the GUI responsive :)
                    self.show()
                    self.w.app.processEvents()
                    if self.stopbtn.isChecked():
                        break
                    preentry = nsim * i - ((i + 2) * (i + 1)) // 2
                    if failsi[i]: #č první je červený
                        for j in range(i+1, nsim):
                            self.check_contact(preentry + j, i, j)
                    else:
                        for j in range(i+1, nsim):
                            if failsi[j]:
                                self.check_contact(preentry + j, i, j)
            else: # 'Mixed pairs only'
                failsi = self.w.get_sample_box().failsi
                for i in range(nsim-1, -1, -1):
                    # keep the GUI responsive :)
                    self.show()
                    self.w.app.processEvents()
                    if self.stopbtn.isChecked():
                        break
                    preentry = nsim * i - ((i + 2) * (i + 1)) // 2
                    if failsi[i]: #č první je červený
                        for j in range(i+1, nsim):
                            if not failsi[j]:
                                self.check_contact(preentry + j, i, j)
                    else:
                        for j in range(i+1, nsim):
                            if failsi[j]:
                                self.check_contact(preentry + j, i, j)
            self.stopbtn.setChecked(False)
            self.stopbtn.setEnabled(False)
            self.show()


    def force_check_contact(self, entry, i, j):
        val = -1 + 2 * self.CS.is_couple((i, j), **self.kwargs)
        self.condensed_contacts[entry] = val
        #č není to úplně ideální kód style. Nastavit a zaroveň vrácet :(
        return val 
        
    
    def peacefully_check_contact(self, entry, i, j):
        val = self.condensed_contacts[entry]
        if val == 0:
            return self.force_check_contact(entry, i, j)
        else:
            return val
        
        
    def setup(self):
        self.toolbar = QtWidgets.QToolBar(self)
        
        action = self.toolbar.addAction("discover", self.discover)
        btn = self.toolbar.widgetForAction(action)
        btn.setAutoRaise(False)
        btn.setToolTip("Searches for a common facets between Voronoi cells")
        
        action = self.toolbar.addAction("stop", self.stop)
        self.stopbtn = btn = self.toolbar.widgetForAction(action)
        btn.setAutoRaise(False)
        btn.setCheckable(True)
        btn.setChecked(False)
        btn.setEnabled(False)
        
        
        action = self.toolbar.addAction("Qhull check", self.check)
        btn = self.toolbar.widgetForAction(action)
        btn.setAutoRaise(False)
        btn.setToolTip("Compare with exact Qhull wireframe")
        
        action = self.toolbar.addAction("show", self.show)
        btn = self.toolbar.widgetForAction(action)
        btn.setAutoRaise(False)
        
        action = self.toolbar.addAction("hide", self.hide)
        btn = self.toolbar.widgetForAction(action)
        btn.setAutoRaise(False)
        
        action = self.toolbar.addAction("clear", self.clear)
        btn = self.toolbar.widgetForAction(action)
        btn.setAutoRaise(False)
        
        action = self.toolbar.addAction("mask", self.clear_non_blue)
        btn = self.toolbar.widgetForAction(action)
        btn.setAutoRaise(False)
        
        self.addWidget(self.toolbar, row=0, col=0)
        
        
        #оӵ остальной (люкет) уллапала
        
        ### Create ParameterTree widget
        self.ptree = pg.parametertree.ParameterTree()
        self._set_param()
        self.ptree.setParameters(self.param, showTop=False)
        
        self.addWidget(self.ptree, row=1, col=0)
        
        self.status_label = QtWidgets.QLabel()
        #self.status_label.setText()
        self.addWidget(self.status_label, row=2, col=0)
        
    def stop(self):
        self.stopbtn.setChecked(True)
        
    def qframe_callback(self):
        # keep the GUI responsive :)
        self.w.app.processEvents()
        
        self.dlg += 1
        return self.dlg.wasCanceled()
  
    
            
    @staticmethod
    def get_user_consent():
        return QtWidgets.QMessageBox.question(None, 
            "Performing triangulation in high dimensions may take a while...",
            "Would you like to start Qhull anyway?"
            ) == QtWidgets.QMessageBox.Yes
        
        
    def get_qhull(self):
        try:
            return True, self.qframe
        except AttributeError:
            sample_box = self.w.get_sample_box()
            if (sample_box.nvar < 10) or self.got_user_consent or self.get_user_consent():
                self.got_user_consent = True
                sample_space = getattr(sample_box, self.w.space)
                self.qframe = wireframe.Qframe(sample_space)
                return True, self.qframe
            else:
                return False, None
        
        
    def check(self):
        if self.get_qhull()[0]:
            with pg.ProgressDialog("Going over all the simplices..", 0, 
                                    self.qframe.nsimplex, cancelText='Stop', 
                                    busyCursor=True) as dlg:
                self.dlg = dlg
                self.qframe.generate_wireframe(self.qframe_callback)
                if not self.dlg.wasCanceled():
                    self.condensed_qontacts = self.qframe.condensed_contacts
                    self.show()
            
        
        
    def clear(self):
        self.condensed_contacts[:] = 0
        try:
            del self.qframe
            del self.condensed_qontacts
        except AttributeError:
            pass
            
        self.w.image_view.blue[self.mask] = -1
        self.w.image_view.update()
    
    def clear_non_blue(self):
        vmask = self.condensed_contacts != 1
        Mmask = spatial.distance.squareform(vmask)
        self.w.image_view.red[Mmask] = 0
        self.w.image_view.green[Mmask] = 0
        self.w.image_view.update()
    
    def show(self):
        try:
            self.w.image_view.blue[self.mask] = self.condensed_qontacts * 2 - 1
            self.w.image_view.blue[self.mask] -= self.condensed_contacts
            self.w.image_view.blue[self.mask] /= 2
        except AttributeError:
            self.w.image_view.blue[self.mask] = self.condensed_contacts
        self.w.image_view.update(autoRange=False)
    
    def hide(self):
        self.w.image_view.blue[self.mask] = -1
        self.w.image_view.update()

        
    def _set_param(self):
        params = list()
        #č check_ ovlivňuje discover(). discover ho i kontroluje
        params.append({'name': 'check_events', 'title': 'pairs to search', 
                        'type': 'list', 'value': True,
                        'values': ['All pairs', 'Failure and mixed pairs', 'Mixed pairs only'],
                        'tip': 'adjacency search for specified pairs'})
        params.append({'name': 'force_update', 'title': 'reevaluate', 
                        'type': 'bool', 'value': False,
                        'tip': "always reevaluate even discovered contacts"})
        params.append({'name': 'method', 'type': 'list', 'value': 'ConvexLinear', 
                     'values': ['DirectContact', 'Gabriel', 'ConvexSolver', 'ConvexLinear', 'LinearSolver', 'LocalizedHull', 'Qhull'],
                     'title': "method"})
        
        params.append({'name': 'solver', 'title': "solver", 'type': 'list', 'value': 'convex_sprite',
                    'values': ['convex_solver', 'convex_spline', 'convex_sort', 'convex_sprite', 'convex_slice'],  
                    'tip': "Versions from the earliest (the worst) to the latest (the best). Names have no any special meaning."})
                     
        params.append({'name': 'tries_to_fix', 'type': 'int', 
                    'limits': (0, float('inf')), 'value': 1, 'default': 1, 
                    'title': "additional tries", 
                    'tip': "Number of additional (over required ndim) tries to rotate hyperplane and find the contact."})   
            
        params.append({'name': 'tol', 'type': 'float', 
                    'title': "tolerance", 
                    'limits': (0, float('inf')), 'value': 1e-5, 'default': 1e-7})   
                    
        self.param = pg.parametertree.Parameter.create(name='params', type='group', children=params)
        
        #č chlapi tomu svému stromu dali zabrat
        #č udělali i signaly
        p = self.param.child('force_update')
        p.sigValueChanged.connect(self.check_method_changed)
        
        p = self.param.child('solver')
        p.sigValueChanged.connect(self.cs_solver_changed)
        
        p = self.param.child('method')
        p.sigValueChanged.connect(self.method_changed)
        
        
        p = self.param.child('tries_to_fix')
        p.sigValueChanged.connect(self.ttf_changed)
        
        p = self.param.child('tol')
        p.sigValueChanged.connect(self.tol_changed)
        
    
    def ttf_changed(self, parameter):
        self.kwargs['tries_to_fix'] = parameter.value()
        
    def tol_changed(self, parameter):
        self.kwargs['tol'] = parameter.value()
        
        
    def check_method_changed(self, parameter):
        if parameter.value():
            self.check_contact = self.force_check_contact
        else:
            self.check_contact = self.peacefully_check_contact
        
    def cs_solver_changed(self, parameter):
        #č ale.. lezeme do vnítřku cizí třídy..
        solver = getattr(wireframe, parameter.value())
        self.CS.convex_solver = solver
        
    def method_changed(self, parameter):
        self.setup_CS()
        method = parameter.value()
        if method in ('ConvexSolver', 'ConvexLinear'):
            self.param.child('solver').show()
            self.param.child('tries_to_fix').show()
            self.param.child('tol').show()
        elif method in ('LocalizedHull', 'LinearSolver'):
            self.param.child('solver').hide()
            self.param.child('tries_to_fix').hide()
            self.param.child('tol').show()
        else:
            self.param.child('solver').hide()
            self.param.child('tries_to_fix').hide()
            self.param.child('tol').hide()
        
#        if method == 'LinearSolver':
#           self.param.child('force_update').setReadonly()
#           self.param.child('force_update').setValue(False)
#        else:
#           self.param.child('force_update').setReadonly(False)
        
        
    def setup_CS(self):
        sample_box = self.w.get_sample_box()
        sample_space = getattr(sample_box, self.w.space)
        
        #č kvůli Qhull se může stát, že budeme muset zachovat starý CS
        #č proto opatrně mažeme kwargs no a tak.
        method = self.param.child('method').value()
        if method == 'Qhull':
            status, qframe = self.get_qhull()
            if status:
                self.CS = qframe
                self.kwargs.clear()
            else:
                self.param.child('method').setToDefault()
        elif method == 'DirectContact':
            self.CS = wireframe.DirectContact(sample_space)
            self.kwargs.clear()
        elif method == 'Gabriel':
            self.CS = wireframe.Gabriel(sample_space)
            self.kwargs.clear()
        elif method == 'ConvexSolver':
            solver = getattr(wireframe, self.param.child('solver').value())
            self.CS = wireframe.ConvexSolver(sample_space, convex_solver=solver)
            #self.kwargs.clear() #č aby se to neztratilo až bude 100500 metodů
            self.kwargs['tries_to_fix'] = self.param.getValues()['tries_to_fix'][0]
            self.kwargs['tol'] = self.param.getValues()['tol'][0]
        elif method == 'ConvexLinear':
            solver = getattr(wireframe, self.param.child('solver').value())
            self.CS = wireframe.ConvexLinear(sample_space, convex_solver=solver)
            #self.kwargs.clear() #č aby se to neztratilo až bude 100500 metodů
            self.kwargs['tries_to_fix'] = self.param.getValues()['tries_to_fix'][0]
            self.kwargs['tol'] = self.param.getValues()['tol'][0]
        elif method == 'LinearSolver':
            self.CS = wireframe.LinearSolver(sample_space)
            self.kwargs.clear()
            self.kwargs['tol'] = self.param.getValues()['tol'][0]
        elif method == 'LocalizedHull':
            self.CS = wireframe.LocalizedHull(sample_space)
            self.kwargs.clear()
            self.kwargs['tol'] = self.param.getValues()['tol'][0]
        else:
            raise ValueError("ContactWidget: unknown method")
            
        
        

