#!/usr/bin/env python
# coding: utf-8


# Monkey patch module
# Removes side panes on Axes3D plot
# Just import it to make MPL unpredictable

import numpy as np
from matplotlib import artist
from mpl_toolkits.mplot3d.axis3d import Axis
from mpl_toolkits.mplot3d.axis3d import art3d, proj3d, move_from_center, tick_update_position

from mpl_toolkits.mplot3d.axes3d import Axes3D
from matplotlib.axes import Axes


@artist.allow_rasterization
def draw(self, renderer):
    self.label._transform = self.axes.transData
    renderer.open_group('axis3d', gid=self.get_gid())

    ticks = self._update_ticks()

    info = self._axinfo
    index = info['i']

    mins, maxs, centers, deltas, tc, highs = self._get_coord_info(renderer)

    # Determine grid lines
    minmax = np.where(highs, maxs, mins)
    maxmin = np.where(highs, mins, maxs)

    # Draw main axis line
    juggled = info['juggled']
    edgep1 = minmax.copy()
    edgep1[juggled[0]] = maxmin[juggled[0]]

    edgep2 = edgep1.copy()
    edgep2[juggled[1]] = maxmin[juggled[1]]
    pep = np.asarray(
        proj3d.proj_trans_points([edgep1, edgep2], renderer.M))
    centpt = proj3d.proj_transform(*centers, renderer.M)
    self.line.set_data(pep[0], pep[1])
    self.line.draw(renderer)

    # Grid points where the planes meet
    xyz0 = np.tile(minmax, (len(ticks), 1))
    xyz0[:, index] = [tick.get_loc() for tick in ticks]

    # Draw labels
    # The transAxes transform is used because the Text object
    # rotates the text relative to the display coordinate system.
    # Therefore, if we want the labels to remain parallel to the
    # axis regardless of the aspect ratio, we need to convert the
    # edge points of the plane to display coordinates and calculate
    # an angle from that.
    # TODO: Maybe Text objects should handle this themselves?
    dx, dy = (self.axes.transAxes.transform([pep[0:2, 1]]) -
              self.axes.transAxes.transform([pep[0:2, 0]]))[0]

    lxyz = 0.5 * (edgep1 + edgep2)

    # A rough estimate; points are ambiguous since 3D plots rotate
    ax_scale = self.axes.bbox.size / self.figure.bbox.size
    ax_inches = np.multiply(ax_scale, self.figure.get_size_inches())
    ax_points_estimate = sum(72. * ax_inches)
    deltas_per_point = 48 / ax_points_estimate
    default_offset = 21.
    labeldeltas = (
        (self.labelpad + default_offset) * deltas_per_point * deltas)
    axmask = [True, True, True]
    axmask[index] = False
    lxyz = move_from_center(lxyz, centers, labeldeltas, axmask)
    tlx, tly, tlz = proj3d.proj_transform(*lxyz, renderer.M)
    self.label.set_position((tlx, tly))
    if self.get_rotate_label(self.label.get_text()):
        angle = art3d._norm_text_angle(np.rad2deg(np.arctan2(dy, dx)))
        self.label.set_rotation(angle)
    self.label.set_va(info['label']['va'])
    self.label.set_ha(info['label']['ha'])
    self.label.draw(renderer)

    # Draw Offset text

    # Which of the two edge points do we want to
    # use for locating the offset text?
    if juggled[2] == 2:
        outeredgep = edgep1
        outerindex = 0
    else:
        outeredgep = edgep2
        outerindex = 1

    pos = move_from_center(outeredgep, centers, labeldeltas, axmask)
    olx, oly, olz = proj3d.proj_transform(*pos, renderer.M)
    self.offsetText.set_text(self.major.formatter.get_offset())
    self.offsetText.set_position((olx, oly))
    angle = art3d._norm_text_angle(np.rad2deg(np.arctan2(dy, dx)))
    self.offsetText.set_rotation(angle)
    # Must set rotation mode to "anchor" so that
    # the alignment point is used as the "fulcrum" for rotation.
    self.offsetText.set_rotation_mode('anchor')

    #----------------------------------------------------------------------
    # Note: the following statement for determining the proper alignment of
    # the offset text. This was determined entirely by trial-and-error
    # and should not be in any way considered as "the way".  There are
    # still some edge cases where alignment is not quite right, but this
    # seems to be more of a geometry issue (in other words, I might be
    # using the wrong reference points).
    #
    # (TT, FF, TF, FT) are the shorthand for the tuple of
    #   (centpt[info['tickdir']] <= pep[info['tickdir'], outerindex],
    #    centpt[index] <= pep[index, outerindex])
    #
    # Three-letters (e.g., TFT, FTT) are short-hand for the array of bools
    # from the variable 'highs'.
    # ---------------------------------------------------------------------
    if centpt[info['tickdir']] > pep[info['tickdir'], outerindex]:
        # if FT and if highs has an even number of Trues
        if (centpt[index] <= pep[index, outerindex]
                and np.count_nonzero(highs) % 2 == 0):
            # Usually, this means align right, except for the FTT case,
            # in which offset for axis 1 and 2 are aligned left.
            if highs.tolist() == [False, True, True] and index in (1, 2):
                align = 'left'
            else:
                align = 'right'
        else:
            # The FF case
            align = 'left'
    else:
        # if TF and if highs has an even number of Trues
        if (centpt[index] > pep[index, outerindex]
                and np.count_nonzero(highs) % 2 == 0):
            # Usually mean align left, except if it is axis 2
            if index == 2:
                align = 'right'
            else:
                align = 'left'
        else:
            # The TT case
            align = 'right'

    self.offsetText.set_va('center')
    self.offsetText.set_ha(align)
    self.offsetText.draw(renderer)

    if self.axes._draw_grid and len(ticks):
        # Grid lines go from the end of one plane through the plane
        # intersection (at xyz0) to the end of the other plane.  The first
        # point (0) differs along dimension index-2 and the last (2) along
        # dimension index-1.
        lines = np.stack([xyz0, xyz0, xyz0], axis=1)
        
        lines[:, 0, index - 2] = maxmin[index - 2]
        lines[:, 2, index - 1] = maxmin[index - 1]
        
        lines[:, :, 2] = np.min(lines[:, :, 2])
        #print("lajny:", lines[:, :, 2])
        self.gridlines.set_segments(lines)
        self.gridlines.set_color(info['grid']['color'])
        self.gridlines.set_linewidth(info['grid']['linewidth'])
        self.gridlines.set_linestyle(info['grid']['linestyle'])
        self.gridlines.draw(renderer, project=True)

    # Draw ticks
    tickdir = info['tickdir']
    tickdelta = deltas[tickdir]
    if highs[tickdir]:
        ticksign = 1
    else:
        ticksign = -1

    for tick in ticks:
        # Get tick line positions
        pos = edgep1.copy()
        pos[index] = tick.get_loc()
        pos[tickdir] = (
            edgep1[tickdir]
            + info['tick']['outward_factor'] * ticksign * tickdelta)
        x1, y1, z1 = proj3d.proj_transform(*pos, renderer.M)
        pos[tickdir] = (
            edgep1[tickdir]
            - info['tick']['inward_factor'] * ticksign * tickdelta)
        x2, y2, z2 = proj3d.proj_transform(*pos, renderer.M)

        # Get position of label
        default_offset = 8.  # A rough estimate
        labeldeltas = (
            (tick.get_pad() + default_offset) * deltas_per_point * deltas)

        axmask = [True, True, True]
        axmask[index] = False
        pos[tickdir] = edgep1[tickdir]
        pos = move_from_center(pos, centers, labeldeltas, axmask)
        lx, ly, lz = proj3d.proj_transform(*pos, renderer.M)

        tick_update_position(tick, (x1, x2), (y1, y2), (lx, ly))
        tick.tick1line.set_linewidth(
            info['tick']['linewidth'][tick._major])
        tick.draw(renderer)

    renderer.close_group('axis3d')
    self.stale = False

Axis.draw = draw



@artist.allow_rasterization
def draw(self, renderer):
    # draw the background patch
    self.patch.draw(renderer)
    self._frameon = False

    # first, set the aspect
    # this is duplicated from `axes._base._AxesBase.draw`
    # but must be called before any of the artist are drawn as
    # it adjusts the view limits and the size of the bounding box
    # of the axes
    locator = self.get_axes_locator()
    if locator:
        pos = locator(self, renderer)
        self.apply_aspect(pos)
    else:
        self.apply_aspect()

    # add the projection matrix to the renderer
    self.M = self.get_proj()
    renderer.M = self.M
    renderer.vvec = self.vvec
    renderer.eye = self.eye
    renderer.get_axis_position = self.get_axis_position

    # Calculate projection of collections and patches and zorder them.
    # Make sure they are drawn above the grids.
    zorder_offset = max(axis.get_zorder()
                        for axis in self._get_axis_list()) + 1
    for i, col in enumerate(
            sorted(self.collections,
                   key=lambda col: col.do_3d_projection(renderer),
                   reverse=True)):
        col.zorder = zorder_offset + i
    for i, patch in enumerate(
            sorted(self.patches,
                   key=lambda patch: patch.do_3d_projection(renderer),
                   reverse=True)):
        patch.zorder = zorder_offset + i

    if self._axis3don:
        # Draw panes first
        #print(self._get_axis_list())
        axis_list = self._get_axis_list()
        #axis_list[0].draw_pane(renderer)
        #axis_list[1].draw_pane(renderer)
        #for axis in self._get_axis_list():
        #    axis.draw_pane(renderer)
        
        # Then axes
        #print(self._get_axis_list())
        #for axis in self._get_axis_list():
        #    axis.draw(renderer)
        axis_list[0].draw(renderer)
        axis_list[1].draw(renderer)


    # Then rest
    Axes.draw(self, renderer)

Axes3D.draw = draw


