#!/usr/bin/env python
# coding: utf-8

import sys
from . import qt_testcases
from . import qt_dicebox
from .. import reader
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets


def select_test_case():
    return qt_testcases.SelectTestCaseWidget().box


def read_box(wt):
    """
    Funkce read_box() buď vytvoří Reader object
    kterým nahradí wt.sample_box,
    nebo - je-li uživatel odmitné zvolit nějaký soubor
    ponechá původní samplebox
    """ 
    app = pg.mkQApp()
    csv_filter = "CSV files (*.csv)"
    filename, __filter = pg.FileDialog.getSaveFileName(
            parent=None, 
            caption="open/store",
            directory="store/%s_%sD.csv" % (wt.gm_signature, wt.nvar),
            #filter=csv_filter,
            filter=csv_filter + ";;All files(*)", 
            initialFilter=csv_filter,
            options=pg.FileDialog.Option.DontConfirmOverwrite
            )
    if filename:
        #č Reader vždy dopíše '.csv' na konci souboru
        #č nechcu to teď měnit
        if filename[-4:]=='.csv':
            filename = filename[:-4]
        #č Reader sám zavolá SampleBox 
        wt.sample_box = reader.Reader(filename, wt.samplebox.sampled_plan)
        
def setup_dicebox(wt):
    qt_dicebox.SetupDiceBoxWidget(wt)
            

def show_box(box):
    #č pokud jsme ve 3D a uživatel vysloveně chce,
    #č otevřeme mu 3D okinko
    #č jinak import qt_plot a jedeme
    
    if box.nvar == 3:
        answer = QtWidgets.QMessageBox.question(None, "Show 3D case", "Would you like to start 3D view window?")
        if answer == QtWidgets.QMessageBox.Yes:
            from . import gl_plot
            gl_plot.QtGuiPlot3D(box)
            
            #č já nevím, co uživatel bude chtit,
            #č ale asi bych ho neotravoval 2D pohledem
            #č po uzavření 3D okna
            sys.exit()
    
    #č defaultní vetev
    from . import qt_plot
    qt_plot.QtGuiPlot2D(box)

