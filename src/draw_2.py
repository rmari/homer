#!/opt/local/bin/python
#coding=utf-8


from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *

import sys, os
import io
#self_path=os.path.dirname(os.path.abspath(sys.argv[0]))
#sys.path.append(self_path+'/cython')
import pyLF_DEM_posfile_reading
import numpy as np

class omerSphere(QGraphicsEllipseItem):
    def __init__(self, position, radius, parent=None):
        
        self.pos = np.array(position)
        self.rad = radius

    
    def paint(self, painter):
        painter.drawEllipse(self.pos[0], self.pos[1], self.rad, self.rad)
        

class omerViewer(QWidget):
    speed=10

    def __init__(self, stream, parent=None):

        QWidget.__init__(self,parent)
        self.pos_stream=pyLF_DEM_posfile_reading.Pos_Stream(stream)

        self.setGeometry(400, 400, 850, 850)
        self.setWindowTitle('omer viewer')

        self.scene = QGraphicsScene(self)        
        self.view = QGraphicsView(self)
        self.view.setScene(self.scene)
        self.view.setViewport(QGLWidget())
        self.spheres=[]
#        self.setupScene()
        
        self.scene.setSceneRect(-410, -410, 840, 840)

        self.view.show()

        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL("timeout()"), self.update)

        Box=[self.pos_stream.Lx(),self.pos_stream.Ly(), self.pos_stream.Lz()]
        self.setBox(Box)


        self.centerX = 0
        self.centerY = 0
        self.scaleX = self.width()/self.L[0]
        self.scaleY = self.height()/self.L[2]



    def start(self):
        self.timer.start(self.speed)


    def setBox(self, BoxSize):
        self.L=BoxSize

#    def timerEvent(self, event):
    def nextConfiguration(self):
        self.pos_stream.get_snapshot()
        print self.pos_stream.time()
        self.update()

#    def keyPressEvent(self, event):
#        if event.key() == Qt.Key_R:
#            self.transform.rotate(45)
#            self.update()

    def paintEvent(self, event):
        self.pos_stream.get_snapshot()
        print self.pos_stream.time()

        
        for item in self.spheres:
            self.scene.removeItem(item)

        self.spheres=[]

        for i in self.pos_stream.range():

            j=str(i)
            radx = self.pos_stream.radius[j]*self.scaleX
            rady = radx

            pointX=(self.pos_stream.positions[j][0]+self.centerX)*self.scaleX
            pointY=-(self.pos_stream.positions[j][2]+self.centerY)*self.scaleY

            sphere = QGraphicsEllipseItem(pointX, pointY, radx, rady)
            
            sphere.setZValue(1)
            sphere.setPen(QPen(Qt.black, 1))
            sphere.setBrush(QBrush(Qt.yellow))

            self.scene.addItem(sphere)
            self.spheres.append(sphere)


        self.scene.update()



class omerScene(QGraphicsScene):

    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)








def init():
    
    arg_nb=2
    if len(sys.argv) != arg_nb :
        print "   Utilisation: ", sys.argv[0], "INPUT_FILE"
        exit(1)
        
    input_stream=io.open(str(sys.argv[1]), 'r')
    return input_stream


app = QApplication([])    

stream=init()
SimuViewer = omerViewer(stream)
SimuViewer.show()
SimuViewer.start()


app.exec_()
