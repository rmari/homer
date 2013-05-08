#!/usr/bin/python
#coding=utf-8


# #!/opt/local/bin/python
from PySide.QtCore import *
from PySide.QtGui import *

import sys, os
import io
import proxy
#self_path=os.path.dirname(os.path.abspath(sys.argv[0]))
#sys.path.append(self_path+'/cython')
import pyLF_DEM_posfile_reading

class omerScene(QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.button = QPushButton()
        self.camera = proxy.omerCamera()

    def mouseMoveEvent(self, event):
        if event.buttons() and LeftButton:
            delta = QPointF(event.scenePos()-event.lastScenePos())
            rotation = delta.X()
            
            self.setRotationY(rotation+self.RotationY())

            matrix = QTransform()
            matrix.rotate(self.RotationY(), YAxis)
            self.setTransform(matrxi)

    def setPointOfView():
        transform = QTransform()
        transform.translate(-self.camera.pos.X(), -self.camera.pos.Y())
        transform = transform*QTransform().rotate(self.camera.angle, YAxis)
        scale = self.camera.zpos
        transform = transform*QTransform().scale(scale, scale)

        self.setTransform(transform)



class omerViewer(QWidget):
    speed=10

    def __init__(self, stream, parent=None):
        QWidget.__init__(self, parent)

        self.setWindowTitle('omer viewer')
        self.setGeometry(400, 400, 850, 850)

        self.scene = omerScene(self)

        self.timer = QBasicTimer()
    
        self.pos_stream=pyLF_DEM_posfile_reading.Pos_Stream(stream)


        Box=[self.pos_stream.Lx(),self.pos_stream.Ly(), self.pos_stream.Lz()]
        self.setBox(Box)

        self.spheres =  []

        self.setupScene()

        self.scaleX = self.width()/self.L[0]
        self.scaleY = self.height()/self.L[2]
#        self.connect(self.scene.rotation, SIGNAL("angleChanged()"), self.update)

        self.view = QGraphicsView(self.scene, self)
#        self.view.setSceneRect(-400, -400, 850, 850)  
        self.view.show()
        
    def setupScene(self):
#        self.scene.setSceneRect(-600, -600, 850, 850)

        for i in range(self.pos_stream.np()):
            sphere = QGraphicsEllipseItem(0, 0, 50, 50)
            
            sphere.setPen(QPen(Qt.black, 1))
            sphere.setBrush(QBrush(Qt.yellow))
  
            sphere.setZValue(1)
            sphere.setPos(i * 5, 10 )
            self.scene.addItem(sphere)
            self.spheres.append(sphere)
        
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
            print self.pos_stream.time()
            self.update()
        else:
            QWidget.timerEvent(self, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_R:
            self.rotation.setAngle(45)
            self.rotation.setOrigin(QPoint(0, 0))
            self.update()

    def paintEvent(self, event):
        
        
        for i in self.pos_stream.range():
            j=str(i)
            radx = self.pos_stream.radius[j]*self.scaleX
            rady = radx
            pointX=(self.pos_stream.positions[j][0]+self.scene.camera.pos.x())*self.scaleX
            pointY=-(self.pos_stream.positions[j][2]+self.scene.camera.pos.y())*self.scaleY

            center = QPoint(pointX, pointY)
            self.spheres[i].setPos(center)

        self.scene.setRotation(self.rotation)
        self.scene.update()

def init():
    
    arg_nb=2
    if len(sys.argv) != arg_nb :
        print "   Utilisation: ", sys.argv[0], "INPUT_FILE"
        exit(1)
        
    input_stream=io.open(str(sys.argv[1]), 'r', buffering=1000000)
    return input_stream


app = QApplication([])    

stream=init()
SimuViewer=omerViewer(stream)
SimuViewer.show()
SimuViewer.start()

app.exec_()
