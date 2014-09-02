import numpy as np
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *

#from numba import autojit
#from numba import jit, void, int_, float32


command_coding = { 'y':0, '@':1, 'r':3, 'c':4, 'l':5, 's':6 }
fidelity_scale = [ Qt.SolidPattern, Qt.Dense2Pattern, Qt.Dense6Pattern, Qt.NoBrush ]




class homerFrame:

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

        self.bare_positions = np.array(obj[:,self.pos1_ind:], dtype=np.float64)
        self.bare_positions[:,[1,2,4,5]] = -self.bare_positions[:,[1,2,4,5]]

        size_pos = np.nonzero(obj[:,0] == command_coding['r'])[0]
        self.bare_sizes = np.zeros(obj_nb)

        for i in range(len(size_pos)-1):
            self.bare_sizes[size_pos[i]:size_pos[i+1]] = obj[size_pos[i],1]
        self.bare_sizes[size_pos[-1]:] = obj[size_pos[-1],1]

        color_pos = np.nonzero(obj[:,0] == command_coding['@'])[0]
        self.bare_colors = np.empty(obj_nb, dtype=np.int)

        for i in range(len(color_pos)-1):
            self.bare_colors[color_pos[i]:color_pos[i+1]] = int(obj[color_pos[i],1])
        self.bare_colors[color_pos[-1]:] = int(obj[color_pos[-1],1])

        layer_pos = np.nonzero(obj[:,0] == command_coding['y'])[0]
        self.bare_layers = np.empty(obj_nb, dtype=np.int)

        for i in range(len(color_pos)-1):
            self.bare_layers[layer_pos[i]:layer_pos[i+1]] = int(obj[layer_pos[i],1])
        self.bare_layers[layer_pos[-1]:] = int(obj[layer_pos[-1],1])
        
        self.objects = np.hstack((obj, np.reshape(self.bare_sizes,(obj_nb,1)), np.reshape(self.bare_colors,(obj_nb,1)), np.reshape(self.bare_layers,(obj_nb,1))))
        all_objects = np.hstack((obj, np.reshape(self.bare_sizes,(obj_nb,1)), np.reshape(self.bare_colors,(obj_nb,1)), np.reshape(self.bare_layers,(obj_nb,1))))

        # remove non-object commands
        real_obj_indices = -np.isnan(self.bare_positions[:,2])
        self.objects = self.objects[real_obj_indices]
        all_objects = all_objects[real_obj_indices]
        self.bare_positions = self.bare_positions[real_obj_indices]
        self.bare_sizes = self.bare_sizes[real_obj_indices]

        self.obj_nb = (all_objects[:,0].shape)[0]

        self.painter_methods = np.empty((self.obj_nb,4), dtype=np.object)


        self.circles_labels = np.nonzero(all_objects[:,0] == command_coding['c'])[0]
        self.painter_methods[self.circles_labels,0] = 1
        self.circles = all_objects[self.circles_labels][:,[self.color_ind, self.layer_ind, self.size_ind, self.pos1_ind, self.pos1_ind+1, self.pos1_ind+2]]
        self.lines_labels = np.nonzero(all_objects[:,0] == command_coding['l'])[0]
        self.painter_methods[self.lines_labels,0] = 2
        self.lines = all_objects[self.lines_labels][:,[self.color_ind, self.layer_ind, self.size_ind, self.pos1_ind, self.pos1_ind+1, self.pos1_ind+2,self.pos2_ind, self.pos2_ind+1, self.pos2_ind+2]]
        self.sticks_labels = np.nonzero(all_objects[:,0] == command_coding['s'])[0]
        self.painter_methods[self.sticks_labels,0] = 2
        self.sticks = all_objects[self.sticks_labels][:,[self.color_ind, self.layer_ind, self.size_ind, self.pos1_ind, self.pos1_ind+1, self.pos1_ind+2,self.pos2_ind, self.pos2_ind+1, self.pos2_ind+2]]

        self.fidelity = fidelity_scale[0]

        self.pos1_ind = 3
        self.pos2_ind = 6

        self.size_ind = 2
        self.color_ind = 0
        self.layer_ind = 1

        self.painter_methods[self.circles_labels, 1] = self.getCirclesPens()
        self.painter_methods[self.circles_labels, 2] = self.getCirclesBrushes()
        self.painter_methods[self.lines_labels, 1] = self.getLinesPens()
        self.painter_methods[self.lines_labels, 2] = self.getLinesBrushes()
        self.painter_methods[self.sticks_labels, 1] = self.getSticksPens()
        self.painter_methods[self.sticks_labels, 2] = self.getSticksBrushes()
        print self.painter_methods[:10]
        self.width_scale = 1


    def getCirclesPens(self):
        pcolor = Qt.black
        pthickness = 1
        pens = [ QPen(pcolor) for i in self.circles_labels ]
        for i in range(len(pens)):
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

    def applyTransform(self, transform):

        transformed_positions_1 = np.dot(self.bare_positions[:,0:3],transform)
        transformed_positions_2 = np.dot(self.bare_positions[:,3:6],transform)

        all_objects[:,self.pos1_ind:self.pos1_ind+6] = np.hstack((transformed_positions_1, transformed_positions_2))
        all_objects[:,self.size_ind] = self.bare_sizes*np.linalg.det(transform)**(1./3.)



    def getLineF(self,v):
        return np.array([QLineF(a[self.pos1_ind], a[self.pos1_ind+2], a[self.pos2_ind], a[self.pos2_ind+2]) for a in v])


    def getRectF(self,v):
        rad = v[:,self.size_ind]
        v[:,self.pos1_ind] = v[:,self.pos1_ind]-rad
        v[:,self.pos1_ind+2] = v[:,self.pos1_ind+2]-rad
        return np.array([ QRectF(a[self.pos1_ind], a[self.pos1_ind+2], 2*a[self.size_ind], 2*a[self.size_ind]) for a in v ])

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

    def displayCircles(self):
        c = self.objects[self.circles_labels]
        objectAttrs = self.getRectF(c)
        self.painter_methods[self.circles_labels,3] = objectAttrs

    def displayLines(self):
        l = self.objects[self.lines_labels]
        objectAttrs = self.getLineF(l)
        self.painter_methods[self.lines_labels,3] = objectAttrs

    def displaySticks(self):
        s = self.objects[self.sticks_labels]
        objectAttrs = self.getLineF(s)
        self.painter_methods[self.sticks_labels,3] = objectAttrs

    def display(self, painter, transform, layer_list, fidelity):
        self.fidelity = fidelity_scale[fidelity]
        self.applyTransform(transform)

        self.displayCircles()
        self.displayLines()
        self.displaySticks()

        displayed_obj = np.zeros(self.obj_nb, dtype=np.bool)
        displayed_nb = np.nonzero(layer_list)[0]
        for d in displayed_nb:
            displayed_obj = np.logical_or(displayed_obj, self.objects[:,self.layer_ind] == d )

        self.masked_objects = self.objects[displayed_obj]
        
        self.ordering = np.argsort(self.masked_objects[:,self.pos1_ind+1])
        pcalls = self.painter_methods[displayed_obj][self.ordering]

        pcalls[ pcalls[:,0] == 1,0] = painter.drawEllipse 
        pcalls[ pcalls[:,0] == 2,0] = painter.drawLine

        self.width_scale = (np.linalg.det(transform)**(1./3.))

        for [paintMethod, pen, brush, paintArgs] in pcalls:
            pen.setWidthF(self.width_scale*pen.widthF())
            painter.setPen(pen)

            brush.setStyle(self.fidelity)
            painter.setBrush(brush)
            paintMethod(paintArgs)
            pen.setWidthF(pen.widthF()/self.width_scale)

