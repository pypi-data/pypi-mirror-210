#!/usr/bin/env python
# coding: utf-8


from . import qt_box_functions as gui


wt = gui.select_test_case()

#č funkce read_box() buď vytvoří Reader object
#č kterým nahradí wt.sample_box,
#č nebo - je-li uživatel odmitné zvolit nějaký soubor
#č ponechá původní samplebox
gui.read_box(wt)

gui.setup_dicebox(wt)

gui.show_box(wt)


