import numpy as np
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *

from numba import autojit
from numba import jit, void, int_, float32

pos1_ind = 1
pos2_ind = 4

size_ind = 7
color_ind = 8
layer_ind = 9

colordef = np.array([Qt.black, Qt.gray, Qt.blue, Qt.red, Qt.yellow, Qt.green, Qt.green, Qt.black, Qt.gray, Qt.blue, Qt.red, Qt.yellow])
command_coding = { 'y':0, '@':1, 'r':3, 'c':4, 'l':5, 's':6 }

def displayCircles(obj, painter_calls, painter):
    
    circles_labels = np.nonzero(obj[:,0] == command_coding['c'])[0]
    
    brush = QBrush(Qt.SolidPattern)
    pen = QPen()
    pen.setColor(Qt.black)
    
    for i in circles_labels:
        
        c = obj[i]
        color = colordef[c[color_ind]]
        
        
        brush.setColor(color)

        rad = c[size_ind]
        objectAttrs = QRectF(c[pos1_ind]-rad, -c[pos1_ind+2]-rad, 2*rad, 2*rad)
        painter_calls[i] = np.array([pen,brush,painter.drawEllipse,objectAttrs])
        
#            painter.drawEllipse(objectAttrs)

def displayLines(obj, painter_calls,painter):
    
    lines_labels = np.nonzero(obj[:,0] == command_coding['l'])[0]
    pen = QPen()
    brush = QBrush()
    
    for i in lines_labels:
        l = obj[i]
        color = colordef[l[color_ind]]
        pen.setColor(color)

        objectAttrs = QLineF(l[pos1_ind], -l[pos1_ind+2], l[pos2_ind], -l[pos2_ind+2])
        painter_calls[i] = np.array([pen,brush,painter.drawLine,objectAttrs])
#            painter.drawLine(objectAttrs)
        
def displaySticks(obj, painter_calls, painter):

    sticks_labels = np.nonzero(obj[:,0] == command_coding['s'])[0]
    pen = QPen()
    brush = QBrush()
    
    for i in sticks_labels:
        s = obj[i]
        
        thickness = s[size_ind]
        pen.setWidth(thickness)
        color = colordef[s[color_ind]]
        pen.setColor(color)
        
        
        objectAttrs = QLineF(s[pos1_ind], -s[pos1_ind+2], s[pos2_ind], -s[pos2_ind+2])
        
        painter_calls[i] = np.array([pen,brush,painter.drawLine,objectAttrs])
        
#            painter.drawLine(objectAttrs)




def display_obj(painter, obj):
    obj = obj[np.argsort(obj[:,pos1_ind+1])]
#        print obj[:,self.pos1_ind+1]

    print "d"

    painter_calls = np.empty((obj.shape[0],4), dtype=np.object)
    
    
    
    displayCircles(obj, painter_calls, painter)
    displayLines(obj, painter_calls, painter)
    displaySticks(obj, painter_calls, painter)
    print "e"
    painter_calls = painter_calls[ np.nonzero(painter_calls[:,0]) ]

    for [pen, brush, paintMethod, paintArgs] in painter_calls:
        painter.setPen(pen)
        painter.setBrush(brush)
        paintMethod(paintArgs)
        #            print paintMethod
        #            print paintArgs
    print "f"

display_obj_jit = jit(display_obj)


def getLineF(v):
    return np.array([QLineF(a[pos1_ind], -a[pos1_ind+2], a[pos2_ind], -a[pos2_ind+2]) for a in v])


def getPen(a):
    pen = QPen(colordef[a[color_ind]])
    pen.setWidth(a[size_ind])
    return pen

def getRectF(v):
    rad = v[:,size_ind]
    v[:,pos1_ind] = v[:,pos1_ind]-rad
    v[:,pos1_ind+2] = -v[:,pos1_ind+2]-rad
    return np.array([ QRectF(a[pos1_ind], a[pos1_ind+2], 2*a[size_ind], 2*a[size_ind]) for a in v ])

def getBrush(v):
    c = colordef[v[:,color_ind].astype(np.int)]
    return np.array([ QBrush(col) for col in c ])

def getPen(v):
    c = colordef[v[:,color_ind].astype(np.int)]
    w = v[:,size_ind]
    
    return np.array([ QPen(QBrush(col), width) for (col, width) in zip(c,w) ])


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

        size_pos = np.nonzero(self.objects[:,0] == command_coding['r'])[0]
        self.bare_sizes = np.zeros(obj_nb)

        for i in range(len(size_pos)-1):
            self.bare_sizes[size_pos[i]:size_pos[i+1]] = self.objects[size_pos[i],1]
        self.bare_sizes[size_pos[-1]:] = self.objects[size_pos[-1],1]

        color_pos = np.nonzero(self.objects[:,0] == command_coding['@'])[0]
        self.bare_colors = np.empty(obj_nb, dtype=np.int)

        for i in range(len(color_pos)-1):
            self.bare_colors[color_pos[i]:color_pos[i+1]] = int(self.objects[color_pos[i],1])
        self.bare_colors[color_pos[-1]:] = int(self.objects[color_pos[-1],1])

        layer_pos = np.nonzero(self.objects[:,0] == command_coding['y'])[0]
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


        circles_labels = np.nonzero(self.masked_objects[:,0] == command_coding['c'])[0]

        pen = QPen()
        pen.setColor(Qt.black)

        c = self.masked_objects[circles_labels]

        pcolor = Qt.black
        pthickness = 1
        pen = QPen(pcolor)
        pen.setWidth(pthickness)

        brush = getBrush(c)
        objectAttrs = getRectF(c)

        self.painter_calls[circles_labels,0] = pen
        self.painter_calls[circles_labels,1] = brush
        self.painter_calls[circles_labels,2] = painter.drawEllipse
        self.painter_calls[circles_labels,3] = objectAttrs


#            painter.drawEllipse(objectAttrs)


    def displayLines(self, painter):

        lines_labels = np.nonzero(self.masked_objects[:,0] == command_coding['l'])[0]

        l = self.masked_objects[lines_labels]

        brush = QBrush(Qt.SolidPattern)
        pen = getPen(l)
        objectAttrs = getLineF(l)
        
        self.painter_calls[lines_labels,0] = pen
        self.painter_calls[lines_labels,1] = brush
        self.painter_calls[lines_labels,2] = painter.drawLine
        self.painter_calls[lines_labels,3] = objectAttrs

        # for i in lines_labels:
        #     l = self.masked_objects[i]
        #     color = self.colordef[l[self.color_ind]]
        #     pen.setColor(color)

        #     objectAttrs = QLineF(l[self.pos1_ind], -l[self.pos1_ind+2], l[self.pos2_ind], -l[self.pos2_ind+2])
        #     self.painter_calls[i] = np.array([pen,brush,painter.drawLine,objectAttrs])
#            painter.drawLine(objectAttrs)


    def displaySticks(self, painter):

        sticks_labels = np.nonzero(self.masked_objects[:,0] == command_coding['s'])[0]
        s = self.masked_objects[sticks_labels]

        brush = QBrush(Qt.SolidPattern)
        pen = getPen(s)
        objectAttrs = getLineF(s)

        self.painter_calls[sticks_labels,0] = pen
        self.painter_calls[sticks_labels,1] = brush
        self.painter_calls[sticks_labels,2] = painter.drawLine
        self.painter_calls[sticks_labels,3] = objectAttrs

        # for i in sticks_labels:
        #     s = self.masked_objects[i]

        #     thickness = s[self.size_ind]
        #     pen.setWidth(thickness)
        #     color = self.colordef[s[self.color_ind]]
        #     pen.setColor(color)


        #     objectAttrs = QLineF(s[self.pos1_ind], -s[self.pos1_ind+2], s[self.pos2_ind], -s[self.pos2_ind+2])
            
        #     self.painter_calls[i] = np.array([pen,brush,painter.drawLine,objectAttrs])

#            painter.drawLine(objectAttrs)


    def display(self, painter, transform, layer_list):

        self.applyTransform(transform)
        obj_nb = (self.objects[:,0].shape)[0]

        displayed_obj = np.zeros(obj_nb, dtype=np.bool)
        displayed_nb = np.nonzero(layer_list)[0]
        for d in displayed_nb:
            displayed_obj = np.logical_or(displayed_obj, self.objects[:,self.layer_ind] == d )
            
            
        displayed_obj = np.logical_and(displayed_obj, -np.isnan(self.bare_positions[:,2]) ) # remove color/layer/radius entries

        self.masked_objects = self.objects[displayed_obj]
        
        self.masked_objects = self.masked_objects[np.argsort(self.masked_objects[:,self.pos1_ind+1])]

#        display_obj(painter, self.masked_objects)

        self.painter_calls = np.empty((self.masked_objects.shape[0],4), dtype=np.object)
        


        self.displayCircles(painter)
        self.displayLines(painter)
        self.displaySticks(painter)

        self.painter_calls = self.painter_calls[ np.nonzero(self.painter_calls[:,0]) ]

        for [pen, brush, paintMethod, paintArgs] in self.painter_calls:
            painter.setPen(pen)
            painter.setBrush(brush)
            paintMethod(paintArgs)

