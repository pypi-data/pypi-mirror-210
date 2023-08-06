#!/usr/bin/env python
# coding: utf-8

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtWidgets
from pyqtgraph.Qt import QtCore

import numpy as np

from ..voronoi import ContactVoronoi

CV = None

##č (jednotka dočasnosti - jeden furt)

class ContactVoronoiBaseWidget(pg.LayoutWidget):
	#mixed_added = QtCore.pyqtSignal(int)
	#mixed_updated = QtCore.pyqtSignal(int)
	#mixed_deleted = QtCore.pyqtSignal(int)
	
	def gen_cv(self): 
		
		model_space = self.param.child('model_space').value()
		ns = self.param.child('ns').value()
		p_base = self.param.child('p_base').value()
		workers = self.param.child('workers').value()
		global CV = ContactVoronoi(self.w.get_sample_box(), self.get_hull(), 
						model_space=model_space, ns=ns, p_base=p_base,
						auto_update=True, workers=workers)
#						on_add_mixed=self.add_mixed_callback,
#						on_update_mixed=self.update_mixed_callback, 
#						on_delete_mixed=self.delete_mixed_callback)
			
	def get_cv(self): 
		if CV is None:
			self.gen_cv()	
		return CV
			
			


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


class ContactVoronoiBaseWidget(pg.LayoutWidget):
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
            
            if self.param.getValues()['check_all'][0]:
                for i in range(nsim-1, -1, -1):
                    # keep the GUI responsive :)
                    self.show()
                    self.w.app.processEvents()
                    if self.stopbtn.isChecked():
                        break
                    preentry = nsim * i - ((i + 2) * (i + 1)) // 2
                    for j in range(i+1, nsim):
                        self.check_contact(preentry + j, i, j)
            else:
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
        #č check_all ovlivňuje discover(). discover ho i kontroluje
        params.append({'name': 'check_all', 'title': 'all contacts', 
                        'type': 'bool', 'value': True,
                        'tip': 'allows to skip "green" contacts'})
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
            
        
        

