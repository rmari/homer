#!/opt/local/bin/python
#coding=utf-8
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *
import numpy as np

import sys, os
import io
#self_path=os.path.dirname(os.path.abspath(sys.argv[0]))
#sys.path.append(self_path+'/cython')
import pyLF_DEM_posfile_reading



class drawConfiguration(QGLWidget):
    speed=10

    def __init__(self, stream, parent=None):
        QGLWidget.__init__(self, parent)
        # setGeometry(x_pos, y_pos, width, height)
        

        self.timer = QBasicTimer()
    
        self.pos_stream=pyLF_DEM_posfile_reading.Pos_Stream(stream)
        Box=[self.pos_stream.Lx(),self.pos_stream.Ly(), self.pos_stream.Lz()]
        self.setBox(Box)

        self.positions=dict()

        ratio = self.L[2]/self.L[0]
        sizeX = 800
        sizeY = sizeX*ratio

        self.setGeometry(400, 400, sizeX, sizeY)

        self.scaleX = self.width()/self.L[0]
        self.scaleY = self.height()/self.L[2]

        self.setWindowTitle('omer viewer')

        print self.width(), self.height()
#        self.connect(self.timer, SIGNAL("timeout()"), self.update)

        self.rotation = np.mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        spheres = [ QGraphicsEllipseItem(0,0,50,50) ]


    def start(self):
        self.timer.start(drawConfiguration.speed,self)



    def setBox(self, BoxSize):
        self.L=BoxSize

    def setConfiguration(self, pos, radius):
        self.positions=pos
        self.radius=radius

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.pos_stream.get_snapshot()
#            self.setConfiguration(self.pos_stream.positions_copy(), self.pos_stream.radius_copy())
            print self.pos_stream.time()
            self.update()
        else:
            QWidget.timerEvent(self, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_R:
            self.rotation = np.identity(3)
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
            
            
            
        
    def paintEvent(self, event):

        paint = QPainter()
        paint.begin(self)


        paint.setRenderHint(QPainter.Antialiasing)
        # make a white drawing background
        paint.setBrush(Qt.white)
        paint.drawRect(event.rect())

        # draw yellow circles
        paint.setPen(Qt.black)
        paint.setBrush(Qt.yellow)
        
        if len(self.pos_stream.positions)==0:
            return
        
        positions = np.concatenate([self.pos_stream.positions[str(i)] for i in self.pos_stream.range() ])

        pos = (positions*self.rotation)

        objects_to_paint = []
        for i in range(len(pos)):
            
            radx = self.pos_stream.radius[str(i)]*self.scaleX
            rady = radx

            pointX=pos[i].item(0)*self.scaleX
            pointY=-pos[i].item(2)*self.scaleY

            center = QRectF(pointX, pointY, 2*radx, 2*rady)

            objects_to_paint.append([-pos[i].item(1), center])
            
        objects_to_paint.sort(key=lambda obj: obj[0]) # draw objects in front last

        paint.setTransform(QTransform().translate(0.5*self.width(), 0.5*self.height()))
        for obj in objects_to_paint:
            paint.drawEllipse(obj[1])

        paint.end()

def init():
    
    arg_nb=2
    if len(sys.argv) != arg_nb :
        print "   Utilisation: ", sys.argv[0], "INPUT_FILE"
        exit(1)
        
    input_stream=io.open(str(sys.argv[1]), 'r', buffering=1000000)
    return input_stream


app = QApplication([])    

stream=init()
SimuViewer=drawConfiguration(stream)
SimuViewer.show()
SimuViewer.start()

app.exec_()
