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

import numpy as np
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *
import sys

command_coding = { 'y':0, '@':1, 'r':3, 'c':4, 'l':5, 's':6 }
fidelity_scale = [ Qt.SolidPattern, Qt.Dense2Pattern, Qt.Dense6Pattern, Qt.NoBrush ]

class homerFrame(object):

    __slots__ = [ 'pos2_ind', 'width_scale', 'size_ind', 'fidelity', 'sticks', 'layers', 'lines_labels', 'sticks_labels', 'pos1_ind', 'circles', 'circles_labels', 'layer_ind', 'obj_nb', 'painter_methods', 'color_ind', 'lines', 'colordef', 'ordering'] # saves some memory usage by avoiding dict of attributes


    def __init__(self, obj):
        self.colordef = np.array([Qt.black, Qt.gray, Qt.white, Qt.green, Qt.yellow, Qt.red, Qt.blue])
        self.populate(obj)

    def populate(self, obj):
        obj_nb = (obj[:,0].shape)[0]

        self.pos1_ind = 1
        self.pos2_ind = 4

        self.size_ind = 7
        self.color_ind = 8
        self.layer_ind = 9

        size_pos = np.nonzero(obj[:,0] == command_coding['r'])[0]
        bare_sizes = np.zeros(obj_nb)
        for i in range(len(size_pos)-1):
            bare_sizes[size_pos[i]:size_pos[i+1]] = obj[size_pos[i],1]
#        print bare_sizes.shape, obj.shape, size_pos.shape, size_pos[-1]
        bare_sizes[size_pos[-1]:] = obj[size_pos[-1],1]

        color_pos = np.nonzero(obj[:,0] == command_coding['@'])[0]
        bare_colors = np.empty(obj_nb, dtype=np.int)

        for i in range(len(color_pos)-1):
            bare_colors[color_pos[i]:color_pos[i+1]] = int(obj[color_pos[i],1])
        bare_colors[color_pos[-1]:] = int(obj[color_pos[-1],1])

        layer_pos = np.nonzero(obj[:,0] == command_coding['y'])[0]
        bare_layers = np.empty(obj_nb, dtype=np.int)

        for i in range(len(color_pos)-1):
            bare_layers[layer_pos[i]:layer_pos[i+1]] = int(obj[layer_pos[i],1])-1
        bare_layers[layer_pos[-1]:] = int(obj[layer_pos[-1],1])-1
        
        all_objects = np.hstack((obj, np.reshape(bare_sizes,(obj_nb,1)), np.reshape(bare_colors,(obj_nb,1)), np.reshape(bare_layers,(obj_nb,1))))

        # remove non-object commands
        real_obj_indices = -np.isnan(obj[:,2])
        all_objects = all_objects[real_obj_indices]

        self.obj_nb = (all_objects[:,0].shape)[0]

        self.layers = all_objects[:,self.layer_ind]

        self.painter_methods = np.empty((self.obj_nb,4), dtype=np.object)

        self.circles_labels = np.nonzero(all_objects[:,0] == command_coding['c'])[0]
        self.painter_methods[self.circles_labels,0] = 1
        self.circles = np.array(all_objects[self.circles_labels][:,[self.color_ind, self.size_ind, self.pos1_ind, self.pos1_ind+1, self.pos1_ind+2]], dtype=np.float32)
        self.lines_labels = np.nonzero(all_objects[:,0] == command_coding['l'])[0]
        self.painter_methods[self.lines_labels,0] = 2
        self.lines = np.array(all_objects[self.lines_labels][:,[self.color_ind, self.size_ind, self.pos1_ind, self.pos1_ind+1, self.pos1_ind+2,self.pos2_ind, self.pos2_ind+1, self.pos2_ind+2]], dtype=np.float32)
        self.sticks_labels = np.nonzero(all_objects[:,0] == command_coding['s'])[0]
        self.painter_methods[self.sticks_labels,0] = 2
        self.sticks = np.array(all_objects[self.sticks_labels][:,[self.color_ind, self.size_ind, self.pos1_ind, self.pos1_ind+1, self.pos1_ind+2,self.pos2_ind, self.pos2_ind+1, self.pos2_ind+2]], dtype=np.float32)

        self.fidelity = fidelity_scale[0]

        self.pos1_ind = 2
        self.pos2_ind = 5

        self.size_ind = 1
        self.color_ind = 0
#        self.layer_ind = 1

#        self.painter_methods[self.circles_labels, 1] = self.getCirclesPens()
#        self.painter_methods[self.circles_labels, 2] = self.getCirclesBrushes()
#        self.painter_methods[self.lines_labels, 1] = self.getLinesPens()
#        self.painter_methods[self.lines_labels, 2] = self.getLinesBrushes()
#        self.painter_methods[self.sticks_labels, 1] = self.getSticksPens()
#        self.painter_methods[self.sticks_labels, 2] = self.getSticksBrushes()
        self.width_scale = 1


    def getCirclesPens(self):
        pcolor = Qt.black
        pthickness = 1
        pens = np.array([ QPen(pcolor) for i in self.circles_labels ])
        pens_nb = self.circles_labels.shape[0]
        for i in range(pens_nb):
            p = pens[i]
            p.setWidthF(0)
        return pens


    def getCirclesBrushes(self):
        return self.getBrush(self.circles)
        
    def getLinesPens(self):
        return self.getPen(self.lines)

    def getLinesBrushes(self):
        return QBrush(Qt.SolidPattern)

    def getSticksPens(self):
        return self.getPen(self.sticks)

    def getSticksBrushes(self):
        return QBrush(Qt.SolidPattern)

    def getLineF(self,pos):
        return np.array([QLineF(np.ravel(a)[0], -np.ravel(a)[2], np.ravel(a)[3], -np.ravel(a)[5]) for a in pos]) # need to ravel (which is ugly) as for a weird reason pr.ndim=2, but a in pr is sometimes (not always) such that a.ndim=2 . It looks like a numpy bug.


    def getRectF(self, pos, rad):
        pr = np.column_stack((pos,rad))
        pr[:,0] = pr[:,0] - pr[:,3]
        pr[:,2] = -pr[:,2] - pr[:,3]
        pr[:,3] = 2*pr[:,3]
        
#        prl = [ravel(a) for a in pr]
        return np.array([ QRectF(np.ravel(a)[0], np.ravel(a)[2], np.ravel(a)[3], np.ravel(a)[3]) for a in pr ]) # need to ravel (which is ugly) as for a weird reason pr.ndim=2, but a in pr is sometimes (not always) such that a.ndim=2 . It looks like a numpy bug.

    def getBrush(self,v):
        fid = fidelity_scale[self.fidelity]
        c = self.colordef[v[:,self.color_ind].astype(np.int)]
        return np.array([ QBrush(col,fid) for col in c ])

    def getPen(self,v):
        c = self.colordef[v[:,self.color_ind].astype(np.int)]
        w = v[:,self.size_ind]

        pens = np.array([ QPen(col) for col in c ])
        for i in range(len(pens)):
            p = pens[i]
            p.setWidthF(float(w[i]))

        return pens

    def generatePainters(self, painter, transform, layer_list, fidelity):
        # 1 apply geometrical transform to coords
        transformed_lines_positions = np.hstack((np.dot(self.lines[:,self.pos1_ind:self.pos1_ind+3],transform),np.dot(self.lines[:,self.pos2_ind:self.pos2_ind+3],transform)))
        transformed_sticks_positions = np.hstack((np.dot(self.sticks[:,self.pos1_ind:self.pos1_ind+3],transform), np.dot(self.sticks[:,self.pos2_ind:self.pos2_ind+3],transform)))
        transformed_circles_positions =  np.dot(self.circles[:,self.pos1_ind:self.pos1_ind+3],transform)

        scale = np.linalg.det(transform)**(1./3.)
        transformed_lines_sizes = 1
        transformed_sticks_sizes = self.sticks[:,self.size_ind]*scale
        transformed_circles_sizes = self.circles[:,self.size_ind]*scale

        # 2 generate associated qt geometric shapes
        objectAttrs = self.getRectF(transformed_circles_positions, transformed_circles_sizes)
        self.painter_methods[self.circles_labels,3] = objectAttrs

        objectAttrs = self.getLineF(transformed_lines_positions)
        self.painter_methods[self.lines_labels,3] = objectAttrs

        objectAttrs = self.getLineF(transformed_sticks_positions)
        self.painter_methods[self.sticks_labels,3] = objectAttrs

        self.painter_methods[self.circles_labels, 1] = self.getCirclesPens()
        self.painter_methods[self.circles_labels, 2] = self.getCirclesBrushes()
        self.painter_methods[self.lines_labels, 1] = self.getLinesPens()
        self.painter_methods[self.lines_labels, 2] = self.getLinesBrushes()
        self.painter_methods[self.sticks_labels, 1] = self.getSticksPens()
        self.painter_methods[self.sticks_labels, 2] = self.getSticksBrushes()


        # 3 order according to z coord
        z_coords = np.zeros(self.obj_nb)
        z_coords[self.circles_labels] = -transformed_circles_positions[:,1] 
        z_coords[self.lines_labels] = -transformed_lines_positions[:,1] 
        z_coords[self.sticks_labels] = -transformed_sticks_positions[:,1] 

        # 4 filter out layers
        displayed_obj = np.zeros(self.obj_nb, dtype=np.bool)
        displayed_nb = np.nonzero(layer_list)[0]
        for d in displayed_nb:
            displayed_obj = np.logical_or(displayed_obj, self.layers == d )

        self.ordering= np.argsort(np.compress(displayed_obj,z_coords))
        pcalls = np.take(np.compress(displayed_obj,self.painter_methods, axis=0),self.ordering, axis=0)
        pcalls[ pcalls[:,0] == 1,0] = painter.drawEllipse 
        pcalls[ pcalls[:,0] == 2,0] = painter.drawLine
        
        self.painter_methods[self.circles_labels, 1] = None
        self.painter_methods[self.circles_labels, 2] = None
        self.painter_methods[self.lines_labels, 1] = None
        self.painter_methods[self.lines_labels, 2] = None
        self.painter_methods[self.sticks_labels, 1] = None
        self.painter_methods[self.sticks_labels, 2] = None
        return pcalls
        
    def display(self, painter, transform, layer_list, fidelity):
        self.fidelity = fidelity_scale[fidelity]

        self.width_scale = (np.linalg.det(transform)**(1./3.))


        for [paintMethod, pen, brush, paintArgs] in self.generatePainters(painter, transform, layer_list, fidelity):
            pen.setWidthF(self.width_scale*pen.widthF())
            painter.setPen(pen)

            brush.setStyle(self.fidelity)
            painter.setBrush(brush)
            paintMethod(paintArgs)
            pen.setWidthF(pen.widthF()/self.width_scale)
    
        self.ordering = np.array([])



