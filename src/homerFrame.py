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
fidelity_scale = [ Qt.SolidPattern, Qt.Dense3Pattern, Qt.Dense6Pattern, Qt.NoBrush ]


class homerFrame(object):

#    __slots__ = [ 'pos2_ind', 'size_ind', 'fidelity', 'sticks', 'layers', 'lines_attrs', 'sticks_labels', 'pos1_ind', 'circles', 'circles_labels', 'layer_ind', 'obj_nb', 'painter_methods', 'painter', 'layer_list', 'color_ind', 'lines', 'colordef', 'ordering', 'transform', 'scale', 'selection', 'translate'] # saves some memory usage by avoiding dict of attributes

    def __init__(self, obj_vals, obj_attrs):
        self.colordef = np.array([Qt.black, Qt.gray, Qt.white, Qt.green, Qt.yellow, Qt.red, Qt.blue, Qt.magenta, Qt.darkGreen, Qt.cyan, Qt.black, Qt.gray, Qt.white, Qt.green, Qt.yellow, Qt.red, Qt.blue, Qt.magenta, Qt.darkGreen, Qt.cyan])

        self.lines=obj_vals['l']
        self.sticks=obj_vals['s']
        self.circles=obj_vals['c']
        self.lines_attrs=obj_attrs['l']
        self.sticks_attrs=obj_attrs['s']
        self.circles_attrs=obj_attrs['c']
        
        self.obj_nb = self.lines.shape[0] + self.sticks.shape[0] + self.circles.shape[0]

        ###

        self.fidelity = fidelity_scale[0]

        self.scale = 1



    def generatePainters(self):

        # 2 filter out layers
        displayed_nb = np.nonzero(self.layer_list)[0]

        lines_nb = self.lines.shape[0]
        displayed_lines = np.zeros(lines_nb, dtype=np.bool)
        for d in displayed_nb:
            displayed_lines = np.logical_or(displayed_lines, self.lines_attrs['y'] == d )
        sticks_nb = self.sticks.shape[0]
        displayed_sticks = np.zeros(sticks_nb, dtype=np.bool)
        for d in displayed_nb:
            displayed_sticks = np.logical_or(displayed_sticks, self.sticks_attrs['y'] == d )
        circles_nb = self.circles.shape[0]
        displayed_circles = np.zeros(circles_nb, dtype=np.bool)
        for d in displayed_nb:
            displayed_circles = np.logical_or(displayed_circles, self.circles_attrs['y'] == d )

            
        # 3 filter out selection
        #        centerx = self.painter_methods[:,p1]
        #        centery = self.painter_methods[:,p2]
        #        displayed_obj = np.logical_and(centerx>self.selection[0], displayed_obj)
        #        displayed_obj = np.logical_and(centerx<self.selection[2], displayed_obj)
        #        displayed_obj = np.logical_and(centery>self.selection[1], displayed_obj)
        #        displayed_obj = np.logical_and(centery<self.selection[3], displayed_obj)


        # 1 apply geometrical transform to coords
        transformed_lines_positions = np.hstack((np.dot(self.lines[displayed_lines,:3],self.transform),np.dot(self.lines[displayed_lines,3:6],self.transform)))
        transformed_sticks_positions = np.hstack((np.dot(self.sticks[displayed_sticks,:3],self.transform), np.dot(self.sticks[displayed_sticks,3:6],self.transform)))
        transformed_circles_positions =  np.dot(self.circles[displayed_circles,:3],self.transform)

        transformed_sticks_sizes = self.scale*self.sticks_attrs['r'][displayed_sticks]
        transformed_circles_sizes = self.circles_attrs['r'][displayed_circles]*self.scale



        disp_l_nb = np.count_nonzero(displayed_lines)
        disp_c_nb = np.count_nonzero(displayed_circles)
        disp_s_nb = np.count_nonzero(displayed_sticks)
        disp_nb = disp_c_nb + disp_l_nb +  disp_s_nb
        pcalls = np.empty((disp_nb,9), dtype=np.object)

        pcalls[:disp_c_nb,0] = self.painter.drawEllipse
        pcalls[disp_c_nb:,0] = self.painter.drawLine

        pcalls[:disp_c_nb,1] = Qt.black      
        pcalls[disp_c_nb:disp_c_nb+disp_l_nb,1] = self.colordef[self.lines_attrs['@'][displayed_lines].astype(np.int)]
        pcalls[disp_c_nb+disp_l_nb:,1] = self.colordef[self.sticks_attrs['@'][displayed_sticks].astype(np.int)]

        pcalls[:disp_c_nb,2] = 1
        pcalls[disp_c_nb:disp_c_nb+disp_l_nb,2] = 1
        pcalls[disp_c_nb+disp_l_nb:,2] = self.scale*self.sticks_attrs['r'][displayed_sticks] 

        pcalls[:disp_c_nb,3] = self.colordef[self.circles_attrs['@'][displayed_circles].astype(np.int)]
        pcalls[disp_c_nb:disp_c_nb+disp_l_nb,3] = Qt.black
        pcalls[disp_c_nb+disp_l_nb:,3] = Qt.black

        # 2 generate associated qt geometric shapes
        pr = np.column_stack((transformed_circles_positions,transformed_circles_sizes))
        pr[:,0] = pr[:,0] - pr[:,3]
        pr[:,2] = -pr[:,2] - pr[:,3]
        pr[:,3] = 2*pr[:,3]
        p1 = 4
        p2 = 5
        p3 = 6
        p4 = 7
        pcalls[:disp_c_nb,p1] = np.ravel(pr[:,0])+self.translate[0]
        pcalls[:disp_c_nb,p2] = np.ravel(pr[:,2])+self.translate[1]
        pcalls[:disp_c_nb,p3] = np.ravel(pr[:,3])
        pcalls[:disp_c_nb,p4] = np.ravel(pr[:,3])
        pcalls[:disp_c_nb,8] = np.ravel(-pr[:,1])
        

        pcalls[disp_c_nb:disp_c_nb+disp_l_nb,p1] = np.ravel(transformed_lines_positions[:,0])+self.translate[0]
        pcalls[disp_c_nb:disp_c_nb+disp_l_nb,p2] = -np.ravel(transformed_lines_positions[:,2])+self.translate[1]
        pcalls[disp_c_nb:disp_c_nb+disp_l_nb,p3] = np.ravel(transformed_lines_positions[:,3])+self.translate[0]
        pcalls[disp_c_nb:disp_c_nb+disp_l_nb,p4] = -np.ravel(transformed_lines_positions[:,5])+self.translate[1]
        pcalls[disp_c_nb:disp_c_nb+disp_l_nb,8] = -np.ravel(transformed_lines_positions[:,1])

        pcalls[disp_c_nb+disp_l_nb:,p1] = np.ravel(transformed_sticks_positions[:,0])+self.translate[0]
        pcalls[disp_c_nb+disp_l_nb:,p2] = -np.ravel(transformed_sticks_positions[:,2])+self.translate[1]
        pcalls[disp_c_nb+disp_l_nb:,p3] = np.ravel(transformed_sticks_positions[:,3])+self.translate[0]
        pcalls[disp_c_nb+disp_l_nb:,p4] = -np.ravel(transformed_sticks_positions[:,5])+self.translate[1]
        pcalls[disp_c_nb+disp_l_nb:,8] = -np.ravel(transformed_sticks_positions[:,1])

        # 3 order according to z coord
        z_coords = np.zeros(self.obj_nb)
        z_coords[:disp_c_nb] = -np.ravel(transformed_circles_positions[:,1])
        z_coords[disp_c_nb:disp_c_nb+disp_l_nb] = -np.ravel(transformed_lines_positions[:,1])
        z_coords[disp_c_nb+disp_l_nb:] = -np.ravel(transformed_sticks_positions[:,1])


        self.ordering= np.argsort(pcalls[:,8])
        pcalls = pcalls[self.ordering]

        return pcalls


    def display(self, painter, transform, translate, layer_list, fidelity, selection):
        self.fidelity = fidelity_scale[fidelity]
        self.painter = painter
        self.layer_list = layer_list
        self.transform = transform
        self.translate = translate
        self.scale = np.linalg.det(transform)**(1./3.)
        self.selection = np.array([selection.left(), selection.top(), selection.right(), selection.bottom()])
        print self.selection
        pen = QPen()
        brush = QBrush()
        brush.setStyle(self.fidelity)

        for [paintMethod, pcolor, pthickness, bcolor, paintArgs0, paintArgs1, paintArgs2, paintArgs3, z] in self.generatePainters():
            pen.setColor(pcolor)
            pen.setWidthF(pthickness)
            painter.setPen(pen)

            brush.setColor(bcolor)
            painter.setBrush(brush)

            paintMethod(paintArgs0, paintArgs1, paintArgs2, paintArgs3)
    
        self.ordering = np.array([])



