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


def rotateConfiguration(pos_array, angleX, angleY):

    rotation

class drawConfiguration(QGLWidget):
    speed=10

    def __init__(self, stream, parent=None):
        QGLWidget.__init__(self, parent)
        # setGeometry(x_pos, y_pos, width, height)
        
        self.setGeometry(400, 400, 850, 850)
        self.setWindowTitle('omer viewer')

        self.timer = QBasicTimer()
    
        self.pos_stream=pyLF_DEM_posfile_reading.Pos_Stream(stream)
        Box=[self.pos_stream.Lx(),self.pos_stream.Ly(), self.pos_stream.Lz()]
        self.setBox(Box)

        self.positions=dict()

        self.centerX = +0.5*self.L[0]
        self.centerY = -0.5*self.L[2]
        self.scaleX = self.width()/self.L[0]
        self.scaleY = self.height()/self.L[2]
#        self.connect(self.timer, SIGNAL("timeout()"), self.update)

        self.transform = QTransform()
        self.rotation = QGraphicsRotation()
        
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
            self.transform.rotate(45, Qt.YAxis)
            self.update()

    def mouseEvent(self, event):
        if event.button() == Qt.LeftButton:
            
    def paintEvent(self, event):

        paint = QPainter()
        paint.begin(self)

        # optional
#        paint.setRenderHint(QPainter.Antialiasing)
        paint.setTransform(self.transform)
        # make a white drawing background
        paint.setBrush(Qt.white)
        paint.drawRect(event.rect())

        # draw red circles
        paint.setPen(Qt.black)
        paint.setBrush(Qt.yellow)
        
#        for i in self.pos_stream.range():
        positions=self.pos_stream.positions

        for i in positions:
            
            radx = self.pos_stream.radius[i]*self.width()/self.L[0]
            rady = radx
            pointX=(positions[i][0]+self.centerX)*self.scaleX
            pointY=-(positions[i][2]+self.centerY)*self.scaleY

            center = QPoint(pointX, pointY)
            paint.drawEllipse(center, radx, rady)

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
