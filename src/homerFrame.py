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

        size_pos = np.nonzero(obj[:,0] == command_coding['r'])[0]
        bare_sizes = np.zeros(obj_nb)
        for i in range(len(size_pos)-1):
            bare_sizes[size_pos[i]:size_pos[i+1]] = obj[size_pos[i],1]
        bare_sizes[size_pos[-1]:] = obj[size_pos[-1],1]

        color_pos = np.nonzero(obj[:,0] == command_coding['@'])[0]
        bare_colors = np.empty(obj_nb, dtype=np.int)

        for i in range(len(color_pos)-1):
            bare_colors[color_pos[i]:color_pos[i+1]] = int(obj[color_pos[i],1])
        bare_colors[color_pos[-1]:] = int(obj[color_pos[-1],1])

        layer_pos = np.nonzero(obj[:,0] == command_coding['y'])[0]
        bare_layers = np.empty(obj_nb, dtype=np.int)

        for i in range(len(color_pos)-1):
            bare_layers[layer_pos[i]:layer_pos[i+1]] = int(obj[layer_pos[i],1])
        bare_layers[layer_pos[-1]:] = int(obj[layer_pos[-1],1])
        
        all_objects = np.hstack((obj, np.reshape(bare_sizes,(obj_nb,1)), np.reshape(bare_colors,(obj_nb,1)), np.reshape(bare_layers,(obj_nb,1))))

        # remove non-object commands
        real_obj_indices = -np.isnan(obj[:,2])
        all_objects = all_objects[real_obj_indices]

        self.obj_nb = (all_objects[:,0].shape)[0]

        self.z_coords = np.zeros(self.obj_nb)
        self.layers = all_objects[:,self.layer_ind]

        self.painter_methods = np.empty((self.obj_nb,4), dtype=np.object)

        self.circles_labels = np.nonzero(all_objects[:,0] == command_coding['c'])[0]
        self.painter_methods[self.circles_labels,0] = 1
        self.circles = np.array(all_objects[self.circles_labels][:,[self.color_ind, self.size_ind, self.pos1_ind, self.pos1_ind+1, self.pos1_ind+2]])
        self.lines_labels = np.nonzero(all_objects[:,0] == command_coding['l'])[0]
        self.painter_methods[self.lines_labels,0] = 2
        self.lines = np.array(all_objects[self.lines_labels][:,[self.color_ind, self.size_ind, self.pos1_ind, self.pos1_ind+1, self.pos1_ind+2,self.pos2_ind, self.pos2_ind+1, self.pos2_ind+2]])
        self.sticks_labels = np.nonzero(all_objects[:,0] == command_coding['s'])[0]
        self.painter_methods[self.sticks_labels,0] = 2
        self.sticks = np.array(all_objects[self.sticks_labels][:,[self.color_ind, self.size_ind, self.pos1_ind, self.pos1_ind+1, self.pos1_ind+2,self.pos2_ind, self.pos2_ind+1, self.pos2_ind+2]])

        self.fidelity = fidelity_scale[0]

        self.pos1_ind = 2
        self.pos2_ind = 5

        self.size_ind = 1
        self.color_ind = 0
#        self.layer_ind = 1

        self.painter_methods[self.circles_labels, 1] = self.getCirclesPens()
        self.painter_methods[self.circles_labels, 2] = self.getCirclesBrushes()
        self.painter_methods[self.lines_labels, 1] = self.getLinesPens()
        self.painter_methods[self.lines_labels, 2] = self.getLinesBrushes()
        self.painter_methods[self.sticks_labels, 1] = self.getSticksPens()
        self.painter_methods[self.sticks_labels, 2] = self.getSticksBrushes()
        self.width_scale = 1

        all_objects = np.array([])
        size_pos = np.array([])
        bare_sizes = np.array([])
        color_pos = np.array([])
        bare_colors = np.array([])
        layer_pos = np.array([])
        bare_layers = np.array([])

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
        self.transformed_lines_positions = np.hstack((np.dot(self.lines[:,self.pos1_ind:self.pos1_ind+3],transform),np.dot(self.lines[:,self.pos2_ind:self.pos2_ind+3],transform)))
        self.transformed_sticks_positions = np.hstack((np.dot(self.sticks[:,self.pos1_ind:self.pos1_ind+3],transform), np.dot(self.sticks[:,self.pos2_ind:self.pos2_ind+3],transform)))
        self.transformed_circles_positions =  np.dot(self.circles[:,self.pos1_ind:self.pos1_ind+3],transform)


        scale = np.linalg.det(transform)**(1./3.)
        self.transformed_lines_sizes = 1
        self.transformed_sticks_sizes = self.sticks[:,self.size_ind]*scale
        self.transformed_circles_sizes = self.circles[:,self.size_ind]*scale

        
        self.z_coords[self.circles_labels] = -self.transformed_circles_positions[:,1] 
        self.z_coords[self.lines_labels] = -self.transformed_lines_positions[:,1] 
        self.z_coords[self.sticks_labels] = -self.transformed_sticks_positions[:,1] 

        
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

    def displayCircles(self):
        objectAttrs = self.getRectF(self.transformed_circles_positions, self.transformed_circles_sizes)
        self.painter_methods[self.circles_labels,3] = objectAttrs

    def displayLines(self):
        objectAttrs = self.getLineF(self.transformed_lines_positions)
        self.painter_methods[self.lines_labels,3] = objectAttrs

    def displaySticks(self):
        objectAttrs = self.getLineF(self.transformed_sticks_positions)
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
            displayed_obj = np.logical_or(displayed_obj, self.layers == d )

        self.ordering = np.argsort(self.z_coords[displayed_obj])

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

