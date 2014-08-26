import numpy as np
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *

class omerFrame:
    
    def __init__(self, obj):
        self.colordef = np.array([Qt.black, Qt.gray, Qt.blue, Qt.red, Qt.yellow, Qt.green, Qt.green, Qt.black, Qt.gray, Qt.blue, Qt.red, Qt.yellow])
        self.populate(obj)


    def populate(self, obj):
        self.objects = obj
        obj_nb = (self.objects[:,0].shape)[0]

        self.pos1_ind = 1
        self.pos2_ind = 4

        self.size_ind = 7
        self.color_ind = 8
        self.layer_ind = 9

        self.bare_positions = np.array(self.objects[:,self.pos1_ind:], dtype=np.float64)

        size_pos = np.nonzero(self.objects[:,0] == 'r')[0]
        self.bare_sizes = np.zeros(obj_nb)

        for i in range(len(size_pos)-1):
            self.bare_sizes[size_pos[i]:size_pos[i+1]] = self.objects[size_pos[i],1]
        self.bare_sizes[size_pos[-1]:] = self.objects[size_pos[i],1]

        color_pos = np.nonzero(self.objects[:,0] == '@')[0]
        self.bare_colors = np.empty(obj_nb, dtype=np.int)

        for i in range(len(color_pos)-1):
            self.bare_colors[color_pos[i]:color_pos[i+1]] = int(self.objects[color_pos[i],1])
        self.bare_colors[color_pos[-1]:] = int(self.objects[color_pos[-1],1])

        layer_pos = np.nonzero(self.objects[:,0] == 'y')[0]
        self.bare_layers = np.empty(obj_nb, dtype=np.int)

        for i in range(len(color_pos)-1):
            self.bare_layers[layer_pos[i]:layer_pos[i+1]] = int(self.objects[layer_pos[i],1])
        self.bare_layers[layer_pos[-1]:] = int(self.objects[layer_pos[-1],1])
        
        self.objects = np.hstack((self.objects, np.reshape(self.bare_sizes,(obj_nb,1)), np.reshape(self.bare_colors,(obj_nb,1)), np.reshape(self.bare_layers,(obj_nb,1))))

        
    def applyTransform(self, transform):

#        print self.bare_positions[:,self.pos1_ind+3:].shape, transform.shape
        self.transformed_positions_1 = np.dot(self.bare_positions[:,0:3],transform)
        self.transformed_positions_2 = np.dot(self.bare_positions[:,3:6],transform)


        self.objects[:,self.pos1_ind:self.pos1_ind+6] = np.hstack((self.transformed_positions_1, self.transformed_positions_2))
        self.objects[:,self.size_ind] = self.bare_sizes*np.linalg.det(transform)**(1./3.)

    def displayCircles(self, painter):

        circles = self.masked_objects[ self.masked_objects[:,0] == 'c' ]
        circles = circles[np.argsort(circles[:,3])] # sort according to z-coord
 
        for c in circles:
            color = self.colordef[c[self.color_ind]]
            painter.setPen(Qt.black)
            painter.setBrush(color)

            rad = c[self.size_ind]
            objectAttrs = QRectF(c[self.pos1_ind]-rad, -c[self.pos1_ind+2]-rad, 2*rad, 2*rad)
            painter.drawEllipse(objectAttrs)


    def displayLines(self, painter):
        pen = QPen()


        lines = self.masked_objects[ self.masked_objects[:,0] == 'l' ]
        lines = lines[np.argsort(lines[:,self.pos1_ind+1])] # sort according to z-coord


        sqrt2 = np.sqrt(2) 
        for l in lines:
            color = self.colordef[l[self.color_ind]]
            pen.setColor(color)
            painter.setPen(pen)

            objectAttrs = QLineF(l[self.pos1_ind], -l[self.pos1_ind+2], l[self.pos2_ind], -l[self.pos2_ind+2])
            painter.drawLine(objectAttrs)


    def displaySticks(self, painter):

        pen = QPen()


        lines = self.masked_objects[ self.masked_objects[:,0] == 's' ]
        lines = lines[np.argsort(lines[:,self.pos1_ind+1])] # sort according to z-coord

        sqrt2 = np.sqrt(2) 
        for l in lines:
            thickness = l[self.size_ind]
            pen.setWidth(thickness)
            color = self.colordef[l[self.color_ind]]
            pen.setColor(color)

            painter.setPen(pen)

            objectAttrs = QLineF(l[self.pos1_ind], -l[self.pos1_ind+2], l[self.pos2_ind], -l[self.pos2_ind+2])
            painter.drawLine(objectAttrs)

        
    def display(self, painter, transform, layer_list):
        
        self.applyTransform(transform)
        obj_nb = (self.objects[:,0].shape)[0]

        displayed_obj = np.zeros(obj_nb, dtype=np.bool)
        displayed_nb = np.nonzero(layer_list)[0]
        for d in displayed_nb:
            displayed_obj = np.logical_or(displayed_obj, self.objects[:,self.layer_ind] == d )

        print displayed_nb
        print displayed_obj.shape
        print self.objects.shape

        self.masked_objects = self.objects[displayed_obj]
        print self.masked_objects.shape

        self.displayCircles(painter)
        self.displayLines(painter)
        self.displaySticks(painter)
        
        
