#!/usr/bin/env python
# coding: utf-8

# Monkey patch module
# Just import it to make MPL unpredictable

# taken from StackOverflow
# https://stackoverflow.com/questions/16488182/removing-axes-margins-in-3d-plot
# © HYRY, 2013
# license: CC BY-SA 3.0
###patch start###
from mpl_toolkits.mplot3d.axis3d import Axis
if not hasattr(Axis, "_get_coord_info_old"):
    def _get_coord_info_new(self, renderer):
        mins, maxs, centers, deltas, tc, highs = self._get_coord_info_old(renderer)
        mins += deltas / 4
        maxs -= deltas / 4
        return mins, maxs, centers, deltas, tc, highs
    Axis._get_coord_info_old = Axis._get_coord_info  
    Axis._get_coord_info = _get_coord_info_new
###patch end###
