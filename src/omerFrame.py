import numpy as np
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *

class omerFrame:
    
    def __init__(self, obj):
        self.populate(obj)
        self.colordef = { '0': Qt.black, '1':Qt.gray, '2':Qt.blue, '3':Qt.red, '4':Qt.yellow, '5':Qt.green }

    def populate(self, obj):
        self.objects = obj
        self.bare_positions = np.array(self.objects[:,2:], dtype=np.float64)
        self.bare_sizes = np.array(self.objects[:,1], dtype=np.float64)
        
    def applyTransform(self, transform):
        pos1_ind = 0

        print self.bare_positions[:,pos1_ind+3:].shape, transform.shape
        self.transformed_positions_1 = np.dot(self.bare_positions[:,pos1_ind:pos1_ind+3],transform)
        self.transformed_positions_2 = np.dot(self.bare_positions[:,pos1_ind+3:],transform)

        pos1_ind = 2
        self.objects[:,pos1_ind:] = np.hstack((self.transformed_positions_1, self.transformed_positions_2))
        self.objects[:,1] = self.bare_sizes*np.linalg.det(transform)**(1./3.)

    def displayCircles(self, painter):
        painter.setPen(Qt.black)
        painter.setBrush(Qt.yellow)
        circles = self.objects[ self.objects[:,0] == 'c' ]
        circles = circles[np.argsort(circles[:,3])] # sort according to z-coord

        pos1_ind = 2
        sqrt2 = np.sqrt(2) 
        for c in circles:
            rad = c[1]
            shift = sqrt2*c[1]
            objectAttrs = QRectF(c[pos1_ind]-shift, c[pos1_ind+2]-shift, 2*rad, 2*rad)
            painter.drawEllipse(objectAttrs)
        
    def display(self, painter, transform, layer_list):
        self.applyTransform(transform)
        self.displayCircles(painter)
