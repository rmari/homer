#    Copyright 2014 Romain Mari
#    This file is part of Homer.
#
#    Homer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import os
import numpy as np
from PyQt4 import QtCore
import homerFrame
import numpy.core.defchararray as charray

color_fname = "homer_palette.py"
if os.path.isfile(color_fname):
    sys.path.append(".")
    import homer_palette
    color_palette = np.array(homer_palette.color_palette, dtype=np.object)
else:
    color_palette = np.array([QtCore.Qt.black, QtCore.Qt.gray, QtCore.Qt.white,
                              QtCore.Qt.green, QtCore.Qt.yellow, QtCore.Qt.red,
                              QtCore.Qt.blue, QtCore.Qt.magenta,
                              QtCore.Qt.darkGreen, QtCore.Qt.cyan,
                              QtCore.Qt.gray, QtCore.Qt.white, QtCore.Qt.green,
                              QtCore.Qt.yellow, QtCore.Qt.red, QtCore.Qt.blue,
                              QtCore.Qt.magenta, QtCore.Qt.darkGreen,
                              QtCore.Qt.cyan], dtype=np.object)


class homerFile:
    def __init__(self, filename):

        self.is_file = True
        self.fname = filename
        self.chunksize = 10000000    # 10000000
        self.frames = []
        self.infile = open(self.fname, 'rb')
        self.trailing_frame = []
        self.trailing_attributes = []
        self.last_layer = 0
        self.last_color = color_palette[0]
        self.last_thickness = 0
        self.eof = False

    def getBoundaries(self):
        return self.frames[0].getBoundaries()

    def read_chunk(self):

        ftype = np.float32
        if len(self.trailing_frame) > 0:
            in_raw_data =\
                np.append(self.trailing_frame,
                          np.array(self.infile.readlines()))
        else:
            in_raw_data = np.array(self.infile.readlines())
        # check eof
        if in_raw_data.shape[0] == 0:
            return False

        # ensure we have at least one frame
        # while not np.any(in_raw_data == b'\n'):
        #     b = np.array(self.infile.readlines(self.chunksize))
        #     if b.shape[0] == 0:
        #         break
        #     in_raw_data = np.vstack((in_raw_data, b))

        # framebreaks are lines with carriage return
        framebreaks = in_raw_data == b'\n'

        # remove the framebreaks lines in the raw data,
        # and keep a correct count of the break locations
        in_raw_data = in_raw_data[np.logical_not(framebreaks)]
        framebreaks = np.nonzero(framebreaks)[0]
        framebreaks -= np.arange(len(framebreaks))

        # keep the bit after the last framebreak for next time,
        # as it is an incomplete frame
        in_raw_data, self.trailing_frame =\
            np.split(in_raw_data, framebreaks[[-1]])
        framebreaks = framebreaks[:-1]

        # these are the commands, 'y', 'r', 'c', etc
        cmd = np.genfromtxt(in_raw_data, usecols=0, dtype=np.str)

        # now we want to propagate any attribute definition
        # like color, layer and thickness to the underneath commands,
        # up to the next attribute definition of the same kind

        # start with layer changes: we want to get an array 'layers',
        # with the same size as 'cmd', containing the layer
        # associated with every single line
        lswitch = cmd == 'y'
        layer_switches = np.empty(np.count_nonzero(lswitch)+2, dtype=np.int)
        layer_switches[0] = 0
        layer_switches[1:-1] = np.nonzero(lswitch)[0]
        layer_switches[-1] = len(cmd)
        layers = np.empty(len(layer_switches)-1, dtype=np.uint8)
        layers[0] = self.last_layer
        layers[1:] = np.genfromtxt(in_raw_data[layer_switches[1:-1]],
                                   usecols=1, dtype=np.uint8)
        layers = np.repeat(layers, np.diff(layer_switches))
        self.last_layer = layers[-1]

        # same for thicknesses
        tswitch = cmd == 'r'
        thickness_switches =\
            np.empty(np.count_nonzero(tswitch)+2, dtype=np.int)
        thickness_switches[0] = 0
        thickness_switches[1:-1] = np.nonzero(tswitch)[0]
        thickness_switches[-1] = len(cmd)
        thicknesses = np.empty(len(thickness_switches)-1, dtype=np.float32)
        thicknesses[0] = self.last_thickness
        thicknesses[1:] = np.genfromtxt(in_raw_data[thickness_switches[1:-1]],
                                        usecols=1, dtype=ftype)
        thicknesses = np.repeat(thicknesses, np.diff(thickness_switches))
        self.last_thickness = thicknesses[-1]

        # same for colors
        cswitch = cmd == '@'
        color_switches = np.empty(np.count_nonzero(cswitch)+2, dtype=np.int)
        color_switches[0] = 0
        color_switches[1:-1] = np.nonzero(cswitch)[0]
        color_switches[-1] = len(cmd)
        colors = np.empty(len(color_switches)-1, dtype=np.object)
        colors[0] = self.last_color
        colors[1:] =\
            color_palette[np.genfromtxt(in_raw_data[color_switches[1:-1]],
                                        usecols=1, dtype=np.int)]
        colors = np.repeat(colors, np.diff(color_switches))

        # now we will remove the attribute def lines from our arrays
        attribute_idx = np.logical_or(lswitch, tswitch)
        attribute_idx = np.logical_or(attribute_idx, cswitch)
        not_attribute_idx = np.logical_not(attribute_idx)
        in_raw_data = in_raw_data[not_attribute_idx]
        cmd = cmd[not_attribute_idx]
        layers = layers[not_attribute_idx]
        thicknesses = thicknesses[not_attribute_idx]
        colors = colors[not_attribute_idx]
        # correct the framebreak locations accordingly
        # by counting every attribute change between
        # every successive framebreaks
        framebreaks -= np.cumsum(np.histogram(np.nonzero(attribute_idx)[0],
                                              np.append(0, framebreaks))[0])

        # print(len(cmd), framebreaks[-10:])
        circles_idx = np.nonzero(cmd == 'c')[0]
        if len(circles_idx):
            circles_pos = np.genfromtxt(in_raw_data[circles_idx],
                                        usecols=[1, 2, 3], dtype=ftype)
            circles_pos[:, 2] = -circles_pos[:, 2]
            circles_colors = colors[circles_idx]
            circles_thicknesses = thicknesses[circles_idx]
            circles_layers = layers[circles_idx]
            cbreaks = np.digitize(framebreaks, circles_idx)
            circles_pos = np.split(circles_pos, cbreaks)
            circles_colors = np.split(circles_colors, cbreaks)
            circles_thicknesses = np.split(circles_thicknesses, cbreaks)
            circles_layers = np.split(circles_layers, cbreaks)

        lines_idx = np.nonzero(cmd == 'l')[0]
        if len(lines_idx):
            lines_pos = np.genfromtxt(in_raw_data[lines_idx],
                                      usecols=np.arange(1, 7), dtype=ftype)

            lines_pos[:, [2, 5]] = -lines_pos[:, [2, 5]]
            lines_colors = colors[lines_idx]
            lines_thicknesses = thicknesses[lines_idx]
            lines_layers = layers[lines_idx]
            lbreaks = np.digitize(framebreaks, lines_idx)
            lines_pos = np.split(lines_pos, lbreaks)
            lines_colors = np.split(lines_colors, lbreaks)
            lines_thicknesses = np.split(lines_thicknesses, lbreaks)
            lines_layers = np.split(lines_layers, lbreaks)

        sticks_idx = np.nonzero(cmd == 's')[0]
        if len(sticks_idx):
            sticks_pos = np.genfromtxt(in_raw_data[sticks_idx],
                                       usecols=np.arange(1, 7), dtype=ftype)
            sticks_pos[:, [2, 5]] = -sticks_pos[:, [2, 5]]
            sticks_colors = colors[sticks_idx]
            sticks_thicknesses = thicknesses[sticks_idx]
            sticks_layers = layers[sticks_idx]
            sbreaks = np.digitize(framebreaks, sticks_idx)
            sticks_pos = np.split(sticks_pos, sbreaks)
            sticks_colors = np.split(sticks_colors, sbreaks)
            sticks_thicknesses = np.split(sticks_thicknesses, sbreaks)
            sticks_layers = np.split(sticks_layers, sbreaks)

        polygons_idx = np.nonzero(cmd == 'p')[0]
        if len(polygons_idx):
            polygons_sizes = np.genfromtxt(in_raw_data[polygons_idx],
                                           usecols=1, dtype=np.int16)
            pos = []
            for idx in polygons_idx:
                pos += in_raw_data[idx].split()
            pos = np.array(pos).reshape((-1, 3))
            pos[:, 2] = -pos[:, 2]
            polygons_pos = (polygons_sizes, )
            polygons_colors = colors[polygons_idx]
            polygons_thicknesses = thicknesses[polygons_idx]
            polygons_layers = layers[polygons_idx]
            pbreaks = np.digitize(framebreaks, polygons_idx)
            polygons_sizes = np.split(polygons_sizes, pbreaks)
            pos = np.split(pos, pbreaks)
            polygons_pos = list(zip(polygons_sizes, pos))
            polygons_colors = np.split(polygons_colors, pbreaks)
            polygons_thicknesses = np.split(polygons_thicknesses, pbreaks)
            polygons_layers = np.split(polygons_layers, pbreaks)

        texts_idx = np.nonzero(cmd == 't')[0]
        if len(texts_idx):
            texts =\
                np.array([t[-1].decode().strip("\n") for t in
                          charray.split(in_raw_data[texts_idx], maxsplit=4)])
            texts_xyz = np.genfromtxt(in_raw_data[texts_idx],
                                      usecols=[1, 2, 3], dtype=ftype)
            texts_xyz[:, 2] = -texts_xyz[:, 2]
            texts_pos = (texts_xyz, texts)
            texts_colors = colors[texts_idx]
            texts_thicknesses = thicknesses[texts_idx]
            texts_layers = layers[texts_idx]
            tbreaks = np.digitize(framebreaks, texts_idx)
            texts_xyz = np.split(texts_xyz, tbreaks)
            texts = np.split(texts, tbreaks)
            texts_pos = list(zip(texts_xyz, texts))
            texts_colors = np.split(texts_colors, tbreaks)
            texts_thicknesses = np.split(texts_thicknesses, tbreaks)
            texts_layers = np.split(texts_layers, tbreaks)

        for i in range(len(framebreaks)+1):
            obj_vals = dict()
            obj_attrs = dict()
            o = 'c'
            if len(circles_idx) and len(circles_pos[i]):
                obj_vals[o] = circles_pos[i]
                obj_attrs[o] = {'y': circles_layers[i],
                                '@': circles_colors[i],
                                'r': circles_thicknesses[i]}

            o = 's'
            if len(sticks_idx) and len(sticks_pos[i]):
                obj_vals[o] = sticks_pos[i]
                obj_attrs[o] = {'y': sticks_layers[i],
                                '@': sticks_colors[i],
                                'r': sticks_thicknesses[i]}
            o = 'l'
            if len(lines_idx) and len(lines_pos[i]):
                obj_vals[o] = lines_pos[i]
                obj_attrs[o] = {'y': lines_layers[i],
                                '@': lines_colors[i],
                                'r': lines_thicknesses[i]}

            o = 'p'
            if len(polygons_idx) and len(polygons_pos[i]):
                obj_vals[o] = polygons_pos[i]
                obj_attrs[o] = {'y': polygons_layers[i],
                                '@': polygons_colors[i],
                                'r': polygons_thicknesses[i]}

            o = 't'
            if len(texts_idx) and len(texts_pos[i]):
                obj_vals[o] = texts_pos[i]
                obj_attrs[o] = {'y': texts_layers[i],
                                '@': texts_colors[i],
                                'r': texts_thicknesses[i]}

            self.frames.append(homerFrame.homerFrame(obj_vals, obj_attrs))
        self.is_init = False
        return True
