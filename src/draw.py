#!/opt/local/bin/python
#coding=utf-8
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *
import numpy as np

import sys, os

import omerFile
import omerLayer



class omerViewer(QGLWidget):
    speed=10

    def __init__(self, filename, parent=None):
        QGLWidget.__init__(self, parent)
        # setGeometry(x_pos, y_pos, width, height)
        
        self.layers=[omerLayer.omerLayer() for i in range(12)]
        self.timer = QBasicTimer()
    
        self.pos_stream=omerFile.omerFile(filename, self.layers)
        Box=[self.pos_stream.Lx(),self.pos_stream.Ly(), self.pos_stream.Lz()]
        self.setBox(Box)

        self.positions=dict()

        ratio = self.L[2]/self.L[0]
        sizeX = 800
        sizeY = sizeX*ratio

        self.setGeometry(400, 400, sizeX, sizeY)

        self.scale = self.width()/self.L[0]

        self.setWindowTitle('omer viewer')

        print self.width(), self.height()
#        self.connect(self.timer, SIGNAL("timeout()"), self.update)

        self.rotation = np.mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        spheres = [ QGraphicsEllipseItem(0,0,50,50) ]

        self.active_layer=1

    def start(self):
        self.timer.start(self.speed,self)



    def setBox(self, BoxSize):
        self.L=BoxSize

    def setConfiguration(self, pos, radius):
        self.positions=pos
        self.radius=radius

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.pos_stream.get_snapshot()
#            self.setConfiguration(self.pos_stream.positions_copy(), self.pos_stream.radius_copy())
            self.update()
        else:
            QWidget.timerEvent(self, event)

    def keyPressEvent(self, event):
        e = event.key()
        if e == Qt.Key_R:
            self.rotation = np.identity(3)
        elif e == Qt.Key_F1:
            self.active_layer = 1
        elif e == Qt.Key_F2:
            self.active_layer = 2
        elif e == Qt.Key_F3:
            self.active_layer = 3
        elif e == Qt.Key_F4:
            self.active_layer = 4
        elif e == Qt.Key_F5:
            self.active_layer = 5
        elif e == Qt.Key_F6:
            self.active_layer = 7
        elif e == Qt.Key_F7:
            self.active_layer = 7
        elif e == Qt.Key_F8:
            self.active_layer = 8
        elif e == Qt.Key_F9:
            self.active_layer = 9
        elif e == Qt.Key_F10:
            self.active_layer = 10
        elif e == Qt.Key_F11:
            self.active_layer = 11
        elif e == Qt.Key_F12:
            self.active_layer = 12
        elif e == Qt.Key_F13:
            self.active_layer = 13



        self.update()
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.current_point = event.posF()

    def mouseMoveEvent(self, event):
        self.previous_point = self.current_point
        self.current_point = event.posF()
        
        angleY = -(self.current_point.x() - self.previous_point.x())/self.width()
        
        sinAngleY = np.sin(angleY)
        cosAngleY = np.cos(angleY)
        generator = np.mat([[cosAngleY, -sinAngleY, 0], [sinAngleY, cosAngleY, 0], [0, 0, 1]])
        self.rotation = generator*self.rotation

        angleX = -(self.current_point.y() - self.previous_point.y())/self.height()
        
        sinAngleX = np.sin(angleX)
        cosAngleX = np.cos(angleX)
        generator = np.mat([[1, 0, 0], [0, cosAngleX, -sinAngleX], [0, sinAngleX, cosAngleX]])
        self.rotation = generator*self.rotation

        self.update()
            
            
            
        
    def catChoice(self, a):
        if len(a) ==4:
            return a[-1]
        else:
            return np.concatenate([a[-2], a[-1]])
    def paintEvent(self, event):

        paint = QPainter()
        paint.begin(self)


        paint.setRenderHint(QPainter.Antialiasing)
        # make a white drawing background
        paint.setBrush(Qt.white)
        paint.drawRect(event.rect())


        objects_to_paint = []       

        for layer in [self.layers[self.active_layer]]:

            if len(layer.objects) > 0:
                rotated_pos = np.concatenate([ self.catChoice(layer.objects[i])  for i in range(len(layer.objects))])*self.rotation

                j=0
                for i in range(len(layer.objects)):
                    if layer.objects[i][0] == 'c':
                        
                        # draw yellow circles
                        paint.setPen(Qt.black)
                        paint.setBrush(Qt.yellow)
                        radius = layer.objects[i][2]*self.scale
                        
                        pointX=rotated_pos[j].item(0)*self.scale
                        pointY=-rotated_pos[j].item(2)*self.scale
                        
                        objectAttrs = QRectF(pointX, pointY, 2*radius, 2*radius)
                        j = j+1
                        
                    elif layer.objects[i][0] == 'l':
                        
                        
                        radius = layer.objects[i][2]*self.scale
                        
                    # draw Gray black
                        pen = QPen(Qt.black)
                        pen.setWidth(radius)
                        paint.setPen(pen)
                        
                        point1X=rotated_pos[j].item(0)*self.scale
                        point1Y=-rotated_pos[j].item(2)*self.scale
                        point2X=rotated_pos[j+1].item(0)*self.scale
                        point2Y=-rotated_pos[j+1].item(2)*self.scale
                        
                        
                        objectAttrs = QLineF(point1X, point1Y, point2X, point2Y)
                        
                        j = j+2
                        

                    objects_to_paint.append([-rotated_pos[i].item(1), layer.objects[i][0], objectAttrs])
            
            print len(objects_to_paint)
        objects_to_paint.sort(key=lambda obj: obj[0]) # draw objects in front last

        paint.setTransform(QTransform().translate(0.5*self.width(), 0.5*self.height()))
        for obj in objects_to_paint:
            if obj[1] == 'c':
                paint.drawEllipse(obj[2])
            elif obj[1] == 'l':
                paint.drawLine(obj[2])

        paint.end()

def init():
    
    arg_nb=2
    if len(sys.argv) != arg_nb :
        print "   Utilisation: ", sys.argv[0], "INPUT_FILE"
        exit(1)
        
    return sys.argv[1]




app = QApplication([])    

filename=init()
SimuViewer=omerViewer(filename)
SimuViewer.show()
SimuViewer.start()

app.exec_()
