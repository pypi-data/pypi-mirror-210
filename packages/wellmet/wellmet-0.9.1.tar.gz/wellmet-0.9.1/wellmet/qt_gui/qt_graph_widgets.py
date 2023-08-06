#!/usr/bin/env python
# coding: utf-8

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtWidgets
from pyqtgraph.Qt import QtCore

import numpy as np
import pandas as pd # required for estimation graph



from .. import stm_df


#č nastavovaní mezí není filosofií pyqtgraph
#č v jejich examples byly použity pouze jednou - 
#č v ukázce možností ViewBox.
#č Už vím proč - sice zoomovaní příjemnější, když graf nikam neutiká,
#č ale až se naraží na limity, pg začně měnit proporce, 
#č které se už nezmění zpatky jen otačením kolečka myši.
#č Navíc setLimits nešikovně lame autoRange
def set_xlimits(plot_widget, xmin_lim, xmax_lim):
    #č není veřejná, není ale ani soukromá. vrací [x, y]
    x, y = plot_widget.getPlotItem().getViewBox().autoRangeEnabled()
    plot_widget.setLimits(xMin=xmin_lim, xMax=xmax_lim)
    if not x:
        [[xmin, __xmax], __y_range] = plot_widget.getPlotItem().viewRange()
        #č chcu aby x pokryval i čerstvě přidáná data
        plot_widget.setRange(xRange=(xmin, xmax_lim), padding=0)
        
    #č ten uvnitř volá i autoRange() na přislušných osech
    plot_widget.enableAutoRange(x=x, y=y)



def update_xrange(plot_widget, xmax):
    #č není veřejná, není ale ani soukromá. vrací [x, y]
    x, y = plot_widget.getPlotItem().getViewBox().autoRangeEnabled()
    if not x:
        [[xmin, _xmax], __y_range] = plot_widget.getPlotItem().viewRange()
        #č chcu aby x pokryval i čerstvě přidáná data
        plot_widget.setRange(xRange=(xmin, max(_xmax, xmax)), padding=0)
        
        #č ten uvnitř volá i autoRange() na přislušných osech
        plot_widget.enableAutoRange(x=x, y=y)







class GRaph(pg.PlotWidget):
    update_xrange = update_xrange
    
    def __init__(self, stream, box_data=None, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        #č tím potokem je myšleno hlavní okínko
        self.stream = stream
        self.box_data = box_data
        if box_data is not None:
            box_data.estimations_updated.connect(self.stm_replot)
            self.setup_context_menu(box_data.TRI_menu)
        
        self.stream.box_runned.connect(self.replot)
        self.stream.slice_changed.connect(self.replot)
            
        self.stream.redraw_called.connect(self.redraw)
        
        self.redraw()
    
        
        
        
        
        
    def redraw(self):
        self.clear()
        self.setBackground('w')
        #č y limita v podstatě znemožní Log y graf
        #size=self.w.px_size*1.5
        
        # box part
        pos = () #np.empty((nsim, 4))
        size = self.stream.px_size * 2
        self.failures = self.plot(pos, pen=None, symbol='x', symbolPen='r',\
                    symbolSize=size*1.5,  name='Failures') # symbolBrush=0.2,
        self.failures.setZValue(100)
        
        self.proxy_failures = self.plot(pos, pen=None, symbol='p', symbolPen=0.5,\
                symbolSize=size, symbolBrush=(217,83,25), name='Proxy failures')
        self.proxy_failures.setZValue(95)
        
        self.successes = self.plot(pos, pen=None, symbol='+', \
                    symbolSize=size*1.5, symbolPen='g',  name='Successes')
        self.successes.setZValue(90)
        
        self.proxy_successes = self.plot(pos, pen=None, symbol='p', symbolPen=0.5, \
                symbolSize=size, symbolBrush=(119,172,48), name='Proxy successes')
        self.proxy_successes.setZValue(85)
        
        
        self.nodes = self.plot(pos, pen=None, symbol='o', symbolPen=0.5, \
                symbolSize=size, name='Nodes')
        self.nodes.setZValue(80)
        
        
        self.f_max_ruler = self.addLine(y=0, pen='r') 
        self.f_min_ruler = self.addLine(y=0, pen='r') 
            
        pen = pg.mkPen(color='b', width=1.5) # blue
        if hasattr(self.stream.sample_box, 'r_exact'):
            exact_name = "r_exact"
            y = self.stream.sample_box.r_exact
            self.r_exact = self.addLine(y=y, pen=pen, name=exact_name) 
            #č aby se nám něco zobrazovalo v legendu
            self.r_exact_PR = self.plot((), (), pen=pen, name=exact_name)
            self.f_min_ruler.show()
        
        if hasattr(self.stream.sample_box, 'R_exact'):
            exact_name = "R_exact"
            y = self.stream.sample_box.R_exact
            self.R_exact = self.addLine(y=y, pen=pen, name=exact_name) 
            #č aby se nám něco zobrazovalo v legendu
            self.R_exact_PR = self.plot((), (), pen=pen, name=exact_name)
            self.f_max_ruler.show()
        else:
            self.f_max_ruler.hide()
        
        self.replot()
        
        
        
        # estimation part
        if self.box_data is not None:
            x = y = () # zde jen vytvoříme kostru, nakrmime daty v .redraw()
            
            #xkcd_green = (167, 255, 181) # xkcd:light seafoam green #a7ffb5
            green = (159, 255, 173) 
            xkcd_red   = (253, 193, 197) # xkcd: pale rose (#fdc1c5)
            red = xkcd_red #(253, 0, 17)
            #xkcd_cream = (255, 243, 154) # let's try xkcd: dark cream (#fff39a)
            cream = (255, 242, 159)
            grey = (233, 233, 233)
            
            self.r_success = self.plot(x, y) 
            self.r_success.setZValue(-1000)
            self.R_success = self.plot(x, y) 
            self.R_success.setZValue(-1000)
            
            self.fill_s = pg.FillBetweenItem(self.r_success, self.R_success)
            #self.fill_mix.setData(name="mixed simplices measure")
            self.fill_s.setBrush(green)
            self.fill_s.setZValue(-1000)
            self.addItem(self.fill_s)
            
            self.r_f = self.plot(x, y)
            self.r_f.setZValue(-500)
            self.R_f = self.plot(x, y)
            self.R_f.setZValue(-500)
            
            self.fill_f = pg.FillBetweenItem(self.r_f, self.R_f)
            #self.fill_mix.setData(name="mixed simplices measure")
            self.fill_f.setBrush(red)
            self.fill_f.setZValue(-500)
            self.addItem(self.fill_f)
            
            self.r_mix = self.plot(x, y)
            self.r_mix.setZValue(-150)
            self.R_mix = self.plot(x, y)
            self.R_mix.setZValue(-150)
            
            self.fill_mix = pg.FillBetweenItem(self.r_mix, self.R_mix)
            #self.fill_mix.setData(name="mixed simplices measure")
            self.fill_mix.setBrush(cream)
            self.fill_mix.setZValue(-150)
            self.addItem(self.fill_mix)
            
            self.r = self.plot(x, y)
            self.r.setZValue(-10)
            self.R = self.plot(x, y)
            self.R.setZValue(-10)
            
            #self.pen_outside = self.plot(x, y)
            self.fill_outside = pg.FillBetweenItem(self.r, self.R)
            #self.fill_outside.setData(name="out of sampling domain estimation")
            self.fill_outside.setBrush(grey)
            self.fill_outside.setZValue(-10)
            self.addItem(self.fill_outside)
        
            self.stm_replot(self.box_data.df)
        
        
        
        
        
    def replot(self):
        nsim = self.stream.slider.value()
        
        sample_box = self.stream.sample_box[:nsim]
        
        lengths = np.sum(np.square(sample_box.G), axis=1)
        lengths = np.sqrt(lengths, out=lengths) #lengths of each radius-vector
        
        
        pos = np.empty((nsim, 2))
        pos[:,0] = np.arange(nsim)
        pos[:,1] = lengths
        
        if hasattr(sample_box, 'failsi'): #č to je normálně sample_box
            failsi = sample_box.failsi
            
            if np.any(failsi):
                f_radia = lengths[failsi]
                if hasattr(self.stream.sample_box, 'R_exact'):
                    self.f_max_ruler.setPos(np.max(f_radia))
                    self.f_max_ruler.show()
                self.f_min_ruler.setPos(np.min(f_radia))                
                self.f_min_ruler.show()
            else:
                self.f_max_ruler.hide()
                self.f_min_ruler.hide()
            
            try: # proxy denotes implicitly-known values
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
            self.f_max_ruler.hide()
            self.f_min_ruler.hide()
        
            
    @staticmethod
    def draw(plot_item, data):
        #č musím to udělat takhle
        #č jinač to zlobí při posunutích slajderu
        if len(data):
            plot_item.setData(data)
            plot_item.show()
        else:
            plot_item.hide()





    def setup_context_menu(self, menu):
        # creates instance of LegendItem 
        # and saves it into plotItem.legend
        self.legend = self.addLegend()
    
        self.plotItem.ctrl.xGridCheck.setChecked(True)
        self.plotItem.ctrl.yGridCheck.setChecked(True)
        
        # delete build-in Transforms (with Log_x and Log_y) options, 
        # they can cause uncachable exception (on any zero in data) and crash
        self.plotItem.ctrlMenu.removeAction(self.plotItem.ctrlMenu.actions()[0])
        
        #č já se bojím. radší to uložím
        self.custom_menu = self.plotItem.vb.menu.addMenu("TRI options")
        
        self.plotItem.vb.menu.addMenu(menu)
        
        self.legend_chk = QtGui.QAction("Legend", self.custom_menu) 
        self.legend_chk.setCheckable(True)
        self.legend_chk.triggered.connect(lambda: self.legend.setVisible(self.legend_chk.isChecked()))
        self.custom_menu.addAction(self.legend_chk)
        # apply custom menu option
        self.legend.setVisible(self.legend_chk.isChecked())

        self.laction = QtGui.QAction("Show labels", self.custom_menu)
        self.laction.triggered.connect(self.show_labels)
        self.custom_menu.addAction(self.laction)
        
            
    def show_labels(self):
        self.setLabel('left', "Distsnce from origin in G space")
        self.setLabel('bottom', "Number of simulations")
    
        
    @staticmethod
    def _set_data(plot_item, serie):
        x, y = serie.index.to_numpy() - 1, serie.to_numpy()
        mask = y >= 0
        plot_item.setData(x[mask], y[mask])


    def stm_replot(self, df):
        if len(df) < 2: #č nevím proč hazí chyby. Asi kvůli zadané širce.
            return 
        
        if 'r' in df:
            self._set_data(self.r, df['r'])
            self._set_data(self.R, df['R'])
        
        if 'r_safe' in df:
            self._set_data(self.r_success, df['r_safe'])
            self._set_data(self.R_success, df['R_safe'])
            
        if 'r_mixed' in df:
            self._set_data(self.r_mix, df['r_mixed'])
            self._set_data(self.R_mix, df['R_mixed'])
            
            
        if 'r_failure' in df:
            self._set_data(self.r_f, df['r_failure'])
            self._set_data(self.R_f, df['R_failure'])
        
        
        xmax = df.index.max() 
        self.update_xrange(xmax*1.02)








"""
=============
График виӝет 
Grafy
Estimation graph widgets
========================
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""
        
        
#č na tuto třídu kladu požadavek aby kdyby něco uměla přepinat mezi zdroje
#č teď to nepotřebuji a nevím jestli to vůbec budu chtit v budoucnu.
#č Proto ji nechám teď vazanou jen na skřiňku.
class BoxEstimationData(QtCore.QObject):
    estimations_updated = QtCore.pyqtSignal(pd.DataFrame)
    
    def __init__(self, box_estimations, signal, parent=None):
        #č QObject má jediný parametr a tím je parent
        super().__init__(parent=parent)
        self.box_estimations = box_estimations
        signal.connect(self.recalculate)
        
        self.setup_context_menu()
        self.recalculate()
        
        
    def setup_context_menu(self):
        self.TRI_menu = QtWidgets.QMenu("WellMet")
        
#        self.TRI_overall_chk = QtGui.QAction("TRI_overall_estimations", self.TRI_menu) 
#        self.TRI_overall_chk.setCheckable(True)
#        self.TRI_overall_chk.setChecked(True)
#        self.TRI_overall_chk.triggered.connect(self.recalculate)
#        self.TRI_menu.addAction(self.TRI_overall_chk)
#        
#        self.simplex_chk = QtGui.QAction("Simplex estimations", self.TRI_menu) 
#        self.simplex_chk.setCheckable(True)
#        self.simplex_chk.setChecked(True)
#        self.simplex_chk.triggered.connect(self.recalculate)
#        self.TRI_menu.addAction(self.simplex_chk)
        
#        # year, it was
#        ## hope, it is temporary
#        #self.sources_action_group = QtGui.QActionGroup(self.TRI_menu)
#        #self.sources_action_group.addAction(self.TRI_overall_chk)
#        #self.sources_action_group.addAction(self.simplex_chk)
        
        #self.TRI_menu.addSeparator()
        
#        self.proxy_chk = QtGui.QAction("Proxy", self.TRI_menu) 
#        self.proxy_chk.setCheckable(True)
#        self.proxy_chk.setChecked(hasattr(self.dice_box, 'proxy'))
#        self.proxy_chk.triggered.connect(self.recalculate)
#        self.TRI_menu.addAction(self.proxy_chk)
#        
#        self.TRI_menu.addSeparator()
        
        self.reaction = QtGui.QAction("Update", self.TRI_menu)
        self.reaction.triggered.connect(self.recalculate)
        self.TRI_menu.addAction(self.reaction)
        
        self.excelaction = QtGui.QAction("Export to Excel", self.TRI_menu)
        self.excelaction.triggered.connect(self.export_to_excel)
        self.TRI_menu.addAction(self.excelaction)
        
        
    def export_to_excel(self):
        #č já bych nechtěl, aby mně export najednou spadl 
        #č z jakéhokoliv důvodu
        try:
            proposal_filename = '.xlsx'
            filename, *__ = pg.FileDialog.getSaveFileName(None, 'Export to Excel',\
                                         proposal_filename, initialFilter='*.xlsx')
            if filename:
                self.df.to_excel(filename)
        except BaseException as e:
            print(self.__class__.__name__ + ":", repr(e))
        
        
    def recalculate(self):
        self.df = df = pd.DataFrame(self.box_estimations)
        try:
            df.index = df.nsim
            #č odhady skříňky netřeba sortirovat.
            #č až se tu objeví něco dalšího, dodáme sort.
            self.estimations_updated.emit(df)
            
        except BaseException as e:
            print(self.__class__.__name__ + ":", repr(e))




class ErrorGraph(pg.PlotWidget):
    
    update_xrange = update_xrange
    
    def __init__(self, pf_exact, box_data, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.pf_exact = pf_exact
        
        self.box_data = box_data
        box_data.estimations_updated.connect(self.redraw)
        
        self.setup_context_menu(box_data.TRI_menu)
        self.setup()
        self.redraw(box_data.df)
        
    def setup_context_menu(self, menu):
        # creates instance of LegendItem 
        # and saves it into plotItem.legend
        self.legend = self.addLegend()
    
        self.plotItem.ctrl.xGridCheck.setChecked(True)
        self.plotItem.ctrl.yGridCheck.setChecked(True)
        
        # menu of SimplexEstimationData
        self.plotItem.vb.menu.addMenu(menu)
        
        #č já se bojím. radší to uložím
        self.custom_menu = self.plotItem.vb.menu.addMenu("Error graph")
        
        self.legend_chk = QtGui.QAction("Legend", self.custom_menu) 
        self.legend_chk.setCheckable(True)
        self.legend_chk.triggered.connect(lambda: self.legend.setVisible(self.legend_chk.isChecked()))
        self.custom_menu.addAction(self.legend_chk)
        # apply custom menu option
        self.legend.setVisible(self.legend_chk.isChecked())

        self.laction = QtGui.QAction("Show labels", self.custom_menu)
        self.laction.triggered.connect(self.show_labels)
        self.custom_menu.addAction(self.laction)
        
            
    def show_labels(self):
        self.setLabel('left', "Failure probability estimation error")
        self.setLabel('bottom', "Number of simulations")
        
    
    def setup(self, *args, **kwargs):
        self.clear()
        self.setBackground('w')
        x = y = () # zde jen vytvoříme kostru, nakrmime daty v .redraw()
        
        # We will use logMode by default
        self.setLogMode(y=True)
        
        pen = pg.mkPen(color='m', width=2)
        self.pen_over = self.plot(x, y, pen=pen, name="pf overestimation")
        pen = pg.mkPen(color='r', width=2) #(118, 187, 255)
        self.pen_pf = self.plot(x, y, pen=pen, name="pf estimation")
        pen = pg.mkPen(color='darkMagenta', width=2) #(118, 187, 255)
        self.pen_under = self.plot(x, y, pen=pen, name="pf underestimation")
    
    
    def redraw(self, df):
        #č nevadí, ale není to slušné
#        #č zapíšeme do data rámu, snad nikomu nebude vadit
#        df['vertex_estimation_error'] = df['vertex_estimation'] - pf_exact
#        df['weighted_vertex_estimation_error'] = df['weighted_vertex_estimation'] - pf_exact
        
        if len(df) < 2: #č nevím proč hazí chyby. Asi kvůli zadané širce.
            return 
        
        if 'vertex_estimation' in df:
            v = (df['vertex_estimation'] - self.pf_exact).abs()
            self.pen_pf.setData(v.index.to_numpy(), v.to_numpy())
        if 'weighted_vertex_estimation' in df:
            wv = (df['weighted_vertex_estimation'] - self.pf_exact).abs()
            self.pen_under.setData(wv.index.to_numpy(), wv.to_numpy())
            
        xmax = df.index.max() 
        self.update_xrange(xmax*1.02)





class EstimationGraph(pg.PlotWidget):
    
    update_xrange = update_xrange
    
    def __init__(self, pf_exact, box_data, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.pf_exact = pf_exact
        
        self.box_data = box_data
        box_data.estimations_updated.connect(self.redraw)
        
        self.setup_context_menu(box_data.TRI_menu)
        self.setup()
        self.replot()
        
    def setup_context_menu(self, menu):
        # creates instance of LegendItem 
        # and saves it into plotItem.legend
        self.legend = self.addLegend()
    
        self.plotItem.ctrl.xGridCheck.setChecked(True)
        self.plotItem.ctrl.yGridCheck.setChecked(True)
        
        # delete build-in Transforms (with Log_x and Log_y) options, 
        # they can cause uncachable exception (on any zero in data) and crash
        self.plotItem.ctrlMenu.removeAction(self.plotItem.ctrlMenu.actions()[0])
        
        #č já se bojím. radší to uložím
        self.custom_menu = self.plotItem.vb.menu.addMenu("TRI options")
        
        self.plotItem.vb.menu.addMenu(menu)
        
        self.legend_chk = QtGui.QAction("Legend", self.custom_menu) 
        self.legend_chk.setCheckable(True)
        self.legend_chk.triggered.connect(lambda: self.legend.setVisible(self.legend_chk.isChecked()))
        self.custom_menu.addAction(self.legend_chk)
        # apply custom menu option
        self.legend.setVisible(self.legend_chk.isChecked())
        
        self.log_x_chk = QtGui.QAction("Log X", self.custom_menu)
        self.log_x_chk.setCheckable(True)
        self.log_x_chk.triggered.connect(lambda: self.setLogMode(x=self.log_x_chk.isChecked()))
        self.custom_menu.addAction(self.log_x_chk)
        
        self.log_y_chk = QtGui.QAction("Log Y", self.custom_menu)
        self.log_y_chk.setCheckable(True)
        self.log_y_chk.setChecked(True)
        self.log_y_chk.triggered.connect(self.replot)
        self.custom_menu.addAction(self.log_y_chk)

        self.laction = QtGui.QAction("Show labels", self.custom_menu)
        self.laction.triggered.connect(self.show_labels)
        self.custom_menu.addAction(self.laction)
        
            
    def show_labels(self):
        self.setLabel('left', "Probability measure")
        self.setLabel('bottom', "Number of simulations")
        
    
    
#       self.legend.addItem(self.pen_success, "success domain estimation")
#        self.legend.addItem(self.pen_outside, "out of sampling domain estimation")
#        self.legend.addItem(self.pen_mix, "mixed simplices measure")
#        self.legend.addItem(self.pen_f, "failure domain estimation")
    def setup(self, *args, **kwargs):
        self.clear()
        self.setBackground('w')
        
        x = y = () # zde jen vytvoříme kostru, nakrmime daty v .redraw()
        
        #xkcd_green = (167, 255, 181) # xkcd:light seafoam green #a7ffb5
        green = (0, 255, 38, 96) 
        #xkcd_red   = (253, 193, 197) # xkcd: pale rose (#fdc1c5)
        red   = (253, 0, 17, 96)
        #xkcd_cream = (255, 243, 154) # let's try xkcd: dark cream (#fff39a)
        cream = (255, 221, 0, 96)
        grey = (196, 196, 196, 96)
        
        self.pen_f = self.plot(x, y, brush=red)#, name="failure domain estimation")
        self.pen_f.setZValue(-100)
        
        self.pen_success = self.plot(x, y, brush=green) #, name="success domain estimation") 
        self.pen_success.setZValue(-100)
        
        self.pen_outmix = self.plot(x, y)
        
        self.fill_mix = pg.FillBetweenItem(self.pen_f, self.pen_outmix)
        #self.fill_mix.setData(name="mixed simplices measure")
        self.fill_mix.setBrush(cream)
        self.fill_mix.setZValue(-100)
        self.addItem(self.fill_mix)
        
        #self.pen_outside = self.plot(x, y)
        self.fill_outside = pg.FillBetweenItem(self.pen_outmix, self.pen_success)
        #self.fill_outside.setData(name="out of sampling domain estimation")
        self.fill_outside.setBrush(grey)
        self.fill_outside.setZValue(-100)
        self.addItem(self.fill_outside)
        
        self.one_ruler = self.addLine(y=1, pen='k') 
        self.zero_ruler = self.addLine(y=0, pen='k') 
            
        if self.pf_exact > 0:
            exact_name = "exact solution"
            pen = pg.mkPen(color='b', width=1.5) # blue
            self.pen_exact = self.addLine(y=self.pf_exact, pen=pen, name=exact_name) 
            #č aby se nám něco zobrazovalo v legendu
            self.pen_exact_PR = self.plot(x, y, pen=pen, name=exact_name)
            
        pen = pg.mkPen(color='grey', width=2)
        self.pen_outside = self.plot(x, y, pen=pen, name="outside probability")
        pen = pg.mkPen(color='orange', width=2)
        self.pen_mixed = self.plot(x, y, pen=pen, name="mixed probability")
        
        pen = pg.mkPen(color='m', width=2)
        self.pen_over = self.plot(x, y, pen=pen, name="pf overestimation")
        pen = pg.mkPen(color='r', width=2) #(118, 187, 255)
        self.pen_pf = self.plot(x, y, pen=pen, name="pf estimation")
        pen = pg.mkPen(color='darkMagenta', width=2) #(118, 187, 255)
        self.pen_under = self.plot(x, y, pen=pen, name="pf underestimation")
        
        
    def replot(self, *args, **kwargs):
        if self.log_y_chk.isChecked():
            self.one_ruler.hide()
            
            if self.pf_exact > 0:
                self.pen_exact.setPos(np.log10(self.pf_exact))
                
                
            self.setLogMode(y=True)
            #self.pen_f.setPen(pg.mkPen(color=(255, 0, 0), width=3)) #, style=QtCore.Qt.DashLine)
            self.pen_f.setPen(None)
            self.pen_f.setFillLevel(None)
            self.pen_success.setFillLevel(0)
            
        else:
            self.one_ruler.show()
            
            if self.pf_exact > 0:
                self.pen_exact.setPos(self.pf_exact)
            
                
            self.setLogMode(y=False)
            self.pen_f.setPen(None)
            self.pen_f.setFillLevel(0)
            self.pen_success.setFillLevel(1)
        
        self.redraw(self.box_data.df)
        
    @staticmethod
    def _set_data(plot_item, serie):
        plot_item.setData(serie.index.to_numpy(), serie.to_numpy())


    def redraw(self, df):
        if len(df) < 2: #č nevím proč hazí chyby. Asi kvůli zadané širce.
            return 
        
        if 'vertex_ratio_estimation' in df:
            self._set_data(self.pen_over, df['vertex_ratio_estimation'])
        
        if 'vertex_estimation' in df:
            self._set_data(self.pen_pf, df['vertex_estimation'])
        
        if 'weighted_vertex_estimation' in df:
            self._set_data(self.pen_under, df['weighted_vertex_estimation'])
        if 'weighted_ratio_estimation' in df:
            self._set_data(self.pen_under, df['weighted_ratio_estimation'])
        
        self._set_data(self.pen_outside, df.outside)
        self._set_data(self.pen_mixed, df.mix)
        
        #č outside by neměl klesnout do nuly.
        #č aj kdyby něco - jen se pokazí maliňko zalivky
        success = df.failure + df.mix + df.outside
        outmix = df.failure + df.mix
        failure = df.failure
        
        #č qtpygraph už nespadne kvuli nule se zapnutým LogModem
        #č ale pořad se to hodí pro zalivky.
        #č Jsou vazany na pen_f, pen_outmix a pen_success
        # (in case of LogPlot) fallback values also used
        if self.log_y_chk.isChecked():
            outmix.where(outmix > 0, success, inplace=True)
            failure = failure.where(failure > 0, outmix)
        
        self._set_data(self.pen_success, success)
        self._set_data(self.pen_f, failure)
        self._set_data(self.pen_outmix, outmix)
        
        xmax = df.index.max() 
        self.update_xrange(xmax*1.02)

            


#
# DEPRECATED
# 


def get_estimation_data(estimations, metric):
    metric_dict = dict()
    # new-style: šecko leží dohromady a každý z toho
    # bere co chce a jak chce
    # ne že by to bylo nějak šetrný
    # estimation je slovníkem
    for estimation in estimations:
        # nsim musí mäť každej odhad
        # pokud nemá - je třeba jej prostě opravit
        nsim = estimation['nsim']
        try: 
            metric_dict[nsim] = estimation[metric]
        except KeyError as e:
            pass #print(self.__class__.__name__ + ":", repr(e))
    
    # nikdo neslibil, že budou v pořadí
    x = np.sort(tuple(metric_dict.keys()))
    y = np.array(tuple(metric_dict.values()))[np.argsort(tuple(metric_dict.keys()))]
    return x, y


class SimplexEstimationData(QtCore.QObject):
    #š budeme mӓť svůj vlastní signaľčík
    estimations_updated = QtCore.pyqtSignal(pd.DataFrame)
    
    def __init__(self, dice_box, stream=None, *args, **kwargs):
        super().__init__(stream, *args, **kwargs)
        self.dice_box = dice_box
        #č je zřejmě, že tím potokem bylo myšleno hlavní okínko
        #č asi aby nepadalo, když nenajde signaly
        self.stream = stream
        if stream is not None:
            self.stream.box_runned.connect(self.recalculate)
            self.stream.estimation_added.connect(self.recalculate)
        
        self.setup_context_menu()
        self.recalculate()
        
        
    def setup_context_menu(self):
        # simplex_data_menu
        self.TRI_menu = QtWidgets.QMenu("TRI sources", self.stream)
        
        self.TRI_overall_chk = QtGui.QAction("TRI_overall_estimations", self.TRI_menu) 
        self.TRI_overall_chk.setCheckable(True)
        self.TRI_overall_chk.setChecked(True)
        self.TRI_overall_chk.triggered.connect(self.recalculate)
        self.TRI_menu.addAction(self.TRI_overall_chk)
        
        self.simplex_chk = QtGui.QAction("Simplex estimations", self.TRI_menu) 
        self.simplex_chk.setCheckable(True)
        self.simplex_chk.setChecked(True)
        self.simplex_chk.triggered.connect(self.recalculate)
        self.TRI_menu.addAction(self.simplex_chk)
        
        # year, it was
        ## hope, it is temporary
        #self.sources_action_group = QtGui.QActionGroup(self.TRI_menu)
        #self.sources_action_group.addAction(self.TRI_overall_chk)
        #self.sources_action_group.addAction(self.simplex_chk)
        
        self.TRI_menu.addSeparator()
        
        self.proxy_chk = QtGui.QAction("Proxy", self.TRI_menu) 
        self.proxy_chk.setCheckable(True)
        self.proxy_chk.setChecked(hasattr(self.dice_box, 'proxy'))
        self.proxy_chk.triggered.connect(self.recalculate)
        self.TRI_menu.addAction(self.proxy_chk)
        
        self.TRI_menu.addSeparator()
        
        self.reaction = QtGui.QAction("Update", self.TRI_menu)
        self.reaction.triggered.connect(self.recalculate)
        self.TRI_menu.addAction(self.reaction)
        
        self.excelaction = QtGui.QAction("Export to Excel", self.TRI_menu)
        self.excelaction.triggered.connect(self.export_to_excel)
        self.TRI_menu.addAction(self.excelaction)
        
        
    def export_to_excel(self):
        #č já bych nechtěl, aby mně export najednou spadl 
        #č z jakéhokoliv důvodu
        try:
            proposal_filename = self.dice_box.guessbox.filename
            if proposal_filename:
                proposal_filename += '.xlsx'
            else:
                proposal_filename = self.dice_box.gm_signature + '.xlsx'
            filename, *__ = pg.FileDialog.getSaveFileName(self.stream, 'Export to Excel',\
                                         proposal_filename, initialFilter='*.xlsx')
            self.df.to_excel(filename)
        except BaseException as e:
            print(self.__class__.__name__ + ":", repr(e))
        
        
    def recalculate(self):
        try:
            # sources=['box', 'user']
            sources = list()
            if self.TRI_overall_chk.isChecked():
                sources.append('box')
            if self.simplex_chk.isChecked():
                sources.append('user')
                
            self.df = stm_df.get_tri_data_frame(self.dice_box, sources=sources,\
                                        apply_proxy=self.proxy_chk.isChecked())
            self.estimations_updated.emit(self.df)
            
        except BaseException as e:
            print(self.__class__.__name__ + ":", repr(e))
        



        






class VoronoiEstimationGraph(pg.PlotWidget):
    def __init__(self, black_box, samplebox_item, parent=None, *args, **kwargs):
        super().__init__(parent)
        self.sb_item = samplebox_item
        self.sb_item.box_runned.connect(self.redraw)
        self.sb_item.estimation_added.connect(self.redraw)
        
        self.black_box = black_box
        self.setBackground('w')
        self.setLimits(xMin=-0.45)
        
        self.reaction = QtGui.QAction("Redraw", self.plotItem.ctrlMenu)
        self.reaction.triggered.connect(self.redraw)
        self.plotItem.ctrlMenu.insertAction(self.plotItem.ctrlMenu.actions()[0], self.reaction)
        
        
        
        # implicitně Y je v logaritmickem měřítku
        self.setLogMode(False, True)

        x = y = () # zde jen vytvoříme kostru, nakrmíme daty v .redraw()
        
        
        # nechapu, proč těm Itemům ríkám "propíska" 
        # propíska? Их есть у нас!
        
        self.Voronoi_2_point_upper_bound = self.plot(x, y, pen='y')
        self.Voronoi_2_point_lower_bound = self.plot(x, y, pen='y')
        
        fill_color = (255, 243, 154) # let's try xkcd: dark cream (#fff39a)
        self.fill = pg.FillBetweenItem(self.Voronoi_2_point_upper_bound, self.Voronoi_2_point_lower_bound, fill_color)
        self.addItem(self.fill)
        
        self.Voronoi_2_point_failure_rate = self.plot(x, y, pen=(195,46,212))
        self.Voronoi_2_point_pure_failure_rate = self.plot(x, y, pen='m')
        self.Voronoi_failure_rate = self.plot(x, y, pen='r')
        
        self.pen_exact = self.plot(x, y, pen='b') # blue
        self.pen_one = self.plot(x, y, pen='k') # black
        
        self.redraw()
    
   
    def redraw(self):
        # kruci, ještě navic i generovať pokažde znovu...
        metrics = {'Voronoi_2_point_upper_bound':{},\
                    'Voronoi_2_point_lower_bound':{},\
                    'Voronoi_2_point_failure_rate':{},\
                    'Voronoi_2_point_pure_failure_rate':{},\
                    'Voronoi_failure_rate':{},}
        xmin = np.inf
        xmax = -np.inf
        try: # тут всё что угодно может пойти не так
            # new-style: šecko leží dohromady a každý z toho
            # bere co chce a jak chce
            # ne že by to bylo nějak šetrný
            # estimation je slovníkem
            for estimation in self.black_box.estimations:
                # nsim musí mäť každej odhad
                # pokud nemá - je třeba jej prostě opravit
                nsim = estimation['nsim']
                
                
                for metric, metric_dict in metrics.items():
                    try: 
                        if estimation[metric] > 0:
                            metric_dict[nsim] = estimation[metric]
                            if nsim > xmax:
                                xmax = nsim
                            if nsim < xmin:
                                xmin = nsim
                    except KeyError as e:
                        pass #print(self.__class__.__name__ + ":", repr(e))
            
            for metric, metric_dict in metrics.items():
                pen = getattr(self, metric)
                # nikdo neslibil, že budou v pořadí
                x = np.sort(tuple(metric_dict.keys()))
                y = np.array(tuple(metric_dict.values()))[np.argsort(tuple(metric_dict.keys()))]
                pen.setData(x, y)
                
            if (xmax - xmin) > 0:
                self.pen_one.setData((xmin,xmax), (1, 1))
                if hasattr(self.black_box, 'pf_exact'):
                    # poslední. I když spadne, tak už nikomu moc nevadí
                    self.pen_exact.setData((xmin,xmax), (self.black_box.pf_exact, self.black_box.pf_exact))
        
        except BaseException as e:
            print(self.__class__.__name__ + ":", repr(e))
        
        
        # pen_f.opts['logMode']
        # pen_outside.setLogMode(False, False)
        #setLogMode(False, False)
        #f = pg.FillBetweenItem(curves[i], curves[i+1], brushes[i])
        #win.addItem(f)







