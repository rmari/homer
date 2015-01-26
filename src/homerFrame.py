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

brush_fidelity = [ Qt.NoBrush, Qt.Dense6Pattern, Qt.Dense3Pattern, Qt.SolidPattern, Qt.SolidPattern]
pen_fidelity = [ Qt.DotLine, Qt.DashLine, Qt.DashLine, Qt.SolidLine, Qt.SolidLine]


class homerFrame(object):

    __slots__ = [ 'fidelity', 'sticks', 'sticks_attrs', 'circles', 'circles_attrs', 'lines', 'lines_attrs', 'polygon_sizes', 'polygon_coords', 'polygons_attrs', 'texts_coords', 'texts_labels', 'texts_attrs', 'painter', 'layer_list', 'colordef', 'transform', 'scale', 'selection', 'translate'] # saves some memory usage by avoiding dict of attributes

    def __init__(self, obj_vals, obj_attrs):
        self.colordef = np.array([Qt.black, Qt.gray, Qt.white, Qt.green, Qt.yellow, Qt.red, Qt.blue, Qt.magenta, Qt.darkGreen, Qt.cyan, Qt.gray, Qt.white, Qt.green, Qt.yellow, Qt.red, Qt.blue, Qt.magenta, Qt.darkGreen, Qt.cyan])
        
        obj_types = obj_vals.keys()
        ftype = np.float32
        empty_attrs = np.empty(0, dtype=[('r', ftype), ('@', ftype), ('y', ftype)])
        if 'l' in obj_types:
            self.lines=obj_vals['l']
            self.lines_attrs=obj_attrs['l']
        else:
            self.lines = np.zeros((0,6))
            self.lines_attrs=empty_attrs
        if 's' in obj_types:
            self.sticks=obj_vals['s']
            self.sticks_attrs=obj_attrs['s']
        else:
            self.sticks=np.zeros((0,6))
            self.sticks_attrs=empty_attrs
        if 'c' in obj_types:
            self.circles=obj_vals['c']
            self.circles_attrs=obj_attrs['c']
        else:
            self.circles=np.zeros((0,3))
            self.circles_attrs=empty_attrs
        if 'p' in obj_types:
            self.polygon_sizes=obj_vals['p'][0]
            self.polygon_coords=obj_vals['p'][1]
            self.polygons_attrs=obj_attrs['p']
        else:
            self.polygon_sizes=np.zeros((0,1))
            self.polygon_coords=np.zeros((0,3))
            self.polygons_attrs=empty_attrs
        if 't' in obj_types:
            self.texts_coords=obj_vals['t'][0]
            self.texts_labels=obj_vals['t'][1]
            self.texts_attrs=obj_attrs['t']
        else:
            self.texts_coords=np.zeros((0,3))
            self.texts_labels=np.empty(0,dtype=np.str)
            self.texts_attrs=empty_attrs

            ###

        self.fidelity = 0

        self.scale = 1



    def getBoundaries(self):
        extrema_pos = np.zeros((2,2))

        tobe_stacked = (np.reshape(self.lines,(-1,3)),np.reshape(self.sticks,(-1,3)),self.circles,self.polygon_coords, self.texts_coords)

        all_pos = np.vstack( tobe_stacked )
        extrema_pos[0,0] = np.min(all_pos[:,0])
        extrema_pos[0,1] = np.max(all_pos[:,0])
        extrema_pos[1,0] = np.min(all_pos[:,2])
        extrema_pos[1,1] = np.max(all_pos[:,2])
        
        return extrema_pos

    def generatePainters(self):

        #  filter out layers
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

        polygons_nb = self.polygon_sizes.shape[0]
        displayed_polygons = np.zeros(polygons_nb, dtype=np.bool)
        if polygons_nb:
            for d in displayed_nb:
                displayed_polygons = np.logical_or(displayed_polygons, self.polygons_attrs['y'] == d )
                displayed_polygons_coords = np.repeat(displayed_polygons,self.polygon_sizes)
        else:
            displayed_polygons_coords = np.zeros(0,dtype=np.bool)

        texts_nb = self.texts_labels.shape[0]
        displayed_texts = np.zeros(texts_nb, dtype=np.bool)
        for d in displayed_nb:
            displayed_texts = np.logical_or(displayed_texts, self.texts_attrs['y'] == d )

            
        # 1bis filter out selection
        #        displayed_obj = np.logical_and(centerx>self.selection[0], displayed_obj)
        #        displayed_obj = np.logical_and(centerx<self.selection[2], displayed_obj)
        #        displayed_obj = np.logical_and(centery>self.selection[1], displayed_obj)
        #        displayed_obj = np.logical_and(centery<self.selection[3], displayed_obj)



        disp_l_nb = np.count_nonzero(displayed_lines)
        disp_c_nb = np.count_nonzero(displayed_circles)
        disp_s_nb = np.count_nonzero(displayed_sticks)
        disp_p_nb = np.count_nonzero(displayed_polygons)
        disp_t_nb = np.count_nonzero(displayed_texts)
        
        slice_start = 0
        slice_end = 0
        slice_end += disp_c_nb
        c_slice = slice(slice_start,slice_end)
        slice_start = slice_end
        slice_end += disp_l_nb
        l_slice = slice(slice_start,slice_end)
        slice_start = slice_end
        slice_end += disp_s_nb
        s_slice = slice(slice_start,slice_end)
        slice_start = slice_end
        slice_end += disp_p_nb
        p_slice = slice(slice_start,slice_end)
        slice_start = slice_end
        slice_end += disp_t_nb
        t_slice = slice(slice_start,slice_end)

        disp_nb = slice_end


        
        # 2 apply geometrical transform to coords
        transformed_lines_positions = np.hstack((np.dot(self.lines[displayed_lines,:3],self.transform),np.dot(self.lines[displayed_lines,3:6],self.transform))) + np.hstack((self.translate,self.translate))
        transformed_sticks_positions = np.hstack((np.dot(self.sticks[displayed_sticks,:3],self.transform), np.dot(self.sticks[displayed_sticks,3:6],self.transform))) + np.hstack((self.translate,self.translate))
        transformed_circles_positions =  np.dot(self.circles[displayed_circles,:3],self.transform) + self.translate
        transformed_polygons_positions =  np.dot(self.polygon_coords[displayed_polygons_coords],self.transform) + self.translate

        transformed_texts_positions =  np.dot(self.texts_coords[displayed_texts],self.transform) + self.translate

        transformed_sticks_sizes = self.scale*self.sticks_attrs['r'][displayed_sticks]
        transformed_circles_sizes = self.circles_attrs['r'][displayed_circles]*self.scale

        # 3 create and fill the array of data needed to paint
        pcalls = np.empty(disp_nb, dtype=[('drawMethod',np.object),('penColor',np.object),('penThickness',np.object),('brushColor',np.object),('shapeMethod',np.object),('shapeArgs',np.ndarray),('z',np.float32)])


        pcalls['drawMethod'][c_slice] = self.painter.drawEllipse
        pcalls['drawMethod'][l_slice] = self.painter.drawLine
        pcalls['drawMethod'][s_slice] = self.painter.drawLine
        pcalls['drawMethod'][p_slice] = self.painter.drawPolygon
        pcalls['drawMethod'][t_slice] = self.painter.drawText

        if self.fidelity > 3:
            pcalls['penColor'][c_slice] = Qt.black
        else:
            pcalls['penColor'][c_slice] = self.colordef[self.circles_attrs['@'][displayed_circles].astype(np.int)]
        pcalls['penColor'][l_slice] = self.colordef[self.lines_attrs['@'][displayed_lines].astype(np.int)]
        pcalls['penColor'][s_slice] = self.colordef[self.sticks_attrs['@'][displayed_sticks].astype(np.int)]
        if self.fidelity > 3:
            pcalls['penColor'][p_slice] = Qt.black
        else:
            pcalls['penColor'][p_slice] = self.colordef[self.polygons_attrs['@'][displayed_polygons].astype(np.int)]
        pcalls['penColor'][t_slice] = self.colordef[self.texts_attrs['@'][displayed_texts].astype(np.int)]
            
        pcalls['penThickness'][c_slice] = 1
        pcalls['penThickness'][l_slice] = 1
        pcalls['penThickness'][s_slice] = self.scale*self.sticks_attrs['r'][displayed_sticks]
        pcalls['penThickness'][p_slice] = 1
        pcalls['penThickness'][t_slice] = 1

        pcalls['brushColor'][c_slice] = self.colordef[self.circles_attrs['@'][displayed_circles].astype(np.int)]
        pcalls['brushColor'][l_slice] = Qt.black
        pcalls['brushColor'][s_slice] = Qt.black
        pcalls['brushColor'][p_slice] = self.colordef[self.polygons_attrs['@'][displayed_polygons].astype(np.int)]
        pcalls['brushColor'][t_slice] = Qt.black
        
        # 3bis generate associated qt geometric shape coords
        if disp_c_nb > 0:
            pr = np.column_stack((transformed_circles_positions,transformed_circles_sizes))
            pr[:,0] = pr[:,0] - pr[:,3]
            pr[:,2] = pr[:,2] - pr[:,3]
            pr[:,3] = 2*pr[:,3]

            pcalls['shapeMethod'][c_slice] = QRectF
            
            pcalls['shapeArgs'][c_slice] = np.split(pr[:,[0,2,3,3]], disp_c_nb)
            pcalls['z'][c_slice] = np.ravel(-pr[:,1])
            
        if disp_l_nb > 0:
            pcalls['shapeMethod'][l_slice] = QRectF
            pcalls['shapeArgs'][l_slice] = np.split(transformed_lines_positions[:,[0,2,3,5]],disp_l_nb)
            pcalls['z'][l_slice] = -np.ravel(transformed_lines_positions[:,1])

        if disp_s_nb > 0:
            pcalls['shapeMethod'][s_slice] = QRectF
            pcalls['shapeArgs'][s_slice] =  np.split(transformed_sticks_positions[:,[0,2,3,5]],disp_s_nb)
            pcalls['z'][s_slice] = -np.ravel(transformed_sticks_positions[:,1])

        if disp_p_nb > 0:
            pcalls['shapeMethod'][p_slice] = None
            arg_array = np.empty(disp_p_nb,dtype=np.object)
            start = 0
            end = 0

            all_qpts = []
            for ps in self.polygon_sizes[displayed_polygons]:
                start=end
                end += ps
                qpts = []
                for j in range(start,end):
                    qpts.append(QPointF(transformed_polygons_positions[j,0], transformed_polygons_positions[j,2]))

                all_qpts.append(qpts)

            pcalls['shapeArgs'][p_slice] = all_qpts
            z_vertices_indices = np.cumsum(self.polygon_sizes[displayed_polygons])-1
            pcalls['z'][p_slice] = -np.ravel(transformed_polygons_positions[z_vertices_indices,1])

        if disp_t_nb > 0:
            pcalls['shapeMethod'][t_slice] = self.texts_labels[displayed_texts]
            pcalls['shapeArgs'][t_slice] = np.split(transformed_texts_positions[:,[0,2]], disp_t_nb)
            pcalls['z'][t_slice] = -np.ravel(transformed_texts_positions[:,1])
            
        # 4 order according to z coord
        ordering= np.argsort(pcalls['z'][:])
        pcalls = pcalls[ordering]

        return pcalls


    def display(self, painter, transform, translate, layer_list, fidelity, selection):
        self.fidelity = fidelity
        self.painter = painter
        self.layer_list = layer_list
        self.transform = transform
        self.translate = np.array([translate[0],0,translate[1]])
        self.scale = np.linalg.det(transform)**(1./3.)
        self.selection = np.array([selection.left(), selection.top(), selection.right(), selection.bottom()])

        pen = QPen()
        brush = QBrush()
        
        brush.setStyle(brush_fidelity[self.fidelity])
        pf = pen_fidelity[self.fidelity]

        a = 20
        pen.setColor(Qt.black)
        pen.setWidthF(10.)
        painter.setPen(pen)
        
        rect = QRectF(QPointF(0,0),QPointF(a,0))
        poly = QPolygonF([QPointF(0,0),QPointF(a,0),QPointF(a,a),QPointF(0,a)])
        
        for [paintMethod, pcolor, pthickness, bcolor, shapeMethod, shapeArgs, z] in self.generatePainters():
            pen.setColor(pcolor)
            pen.setWidthF(pthickness)
            
            brush.setColor(bcolor)
            shapeArgs = np.ravel(shapeArgs)

            if paintMethod == self.painter.drawEllipse:
                [p1,p2,p3,p4] = shapeArgs
                painter.setPen(pen)
                painter.setBrush(brush)
                paintMethod(p1,p2,p3,p4)
            if paintMethod == self.painter.drawLine:
                [p1,p2,p3,p4] = shapeArgs
                pen.setStyle(pf)
                painter.setPen(pen)
                painter.setBrush(brush)
                paintMethod(p1,p2,p3,p4)
                pen.setStyle(Qt.SolidLine)
            if paintMethod == self.painter.drawPolygon:
                painter.setPen(pen)
                painter.setBrush(brush)
                paintMethod(shapeArgs)
            if paintMethod == self.painter.drawText:
                [p1,p2] = shapeArgs
                painter.setPen(pen)
                painter.setBrush(brush)
                paintMethod(p1,p2,shapeMethod)
            




        
