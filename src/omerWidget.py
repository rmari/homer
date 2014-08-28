#!/Users/LevichFellow/anaconda/bin/python
##!/usr/bin/python
#coding=utf-8
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *
import numpy as np

import sys, os

import omerFile




class omerWidget(QWidget):
    speed=0

    def __init__(self, filename, parent=None):
        QWidget.__init__(self, parent)
        # setGeometry(x_pos, y_pos, width, height)
        
        self.timer = QBasicTimer()
    
        self.pos_stream=omerFile.omerFile(filename)
        Box=[self.pos_stream.Lx(),self.pos_stream.Ly(), self.pos_stream.Lz()]
        self.setBox(Box)

        self.positions=dict()

        ratio = self.L[2]/self.L[0]
        self.windowSizeX = 800
        self.windowSizeY = self.windowSizeX*ratio
        self.windowLocationX = 400
        self.windowLocationY = self.windowLocationX

        self.setGeometry(self.windowLocationX, self.windowLocationY, self.windowSizeX, self.windowSizeY)

        self.scale = 0.7*self.width()/self.L[0]

        self.setWindowTitle('omer viewer')

#        self.connect(self.timer, SIGNAL("timeout()"), self.update)
        
        self.transform = self.scale*np.identity(3)

        spheres = [ QGraphicsEllipseItem(0,0,50,50) ]

#        self.bg_layer = omerLayer.omerBackgroundLayer(Box)

        self.frame_nb = 0

        self.layer_nb=12
        self.layer_activity = np.ones(self.layer_nb, dtype=np.bool)
        self.layer_labels = [] 

        for i in range(self.layer_nb):
            label = "Layer "+str(i+1)+" (F"+str(i+1)+")"
            self.layer_labels.append(label)

        self.fidelity = 0
        self.fidelity_min = 0
        self.fidelity_max = 3

        sc_ShiftN = QShortcut(QKeySequence("Shift+N"), self)

        self.installEventFilter(self)

        pal = QPalette()
        pal.setColor(QPalette.Window, Qt.gray)
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        
        self.show()

    def start(self):
        self.timer.start(self.speed,self)



    def setBox(self, BoxSize):
        self.L=BoxSize

    def setConfiguration(self, pos, radius):
        self.positions=pos
        self.radius=radius


    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if(self.frame_nb < len(self.pos_stream.frames)-1):
                self.frame_nb = self.frame_nb+1
                self.update()
            else:
                return
        else:
            QWidget.timerEvent(self, event)

    def layerSwitch(self,label):
        self.layer_activity[label] = -self.layer_activity[label]
        
    def eventFilter(self, obj, event):
        if obj == self:
#            print event.type()
            if event.type() == QEvent.ShortcutOverride:
                k =  event.key() 
                m = event.modifiers()
                
                if k == Qt.Key_N and m == Qt.SHIFT:
                    self.start()
                    return True
            else:
                return False
            
        else:
            return False 



    def keyPressEvent(self, event):
        catched = False
        e = event.key()
        if e == Qt.Key_Tab:
            self.transform = self.scale*np.identity(3)
            cached = True
        elif e == Qt.Key_F1:
            self.layerSwitch(0)
            cached = True
        elif e == Qt.Key_F2:
            self.layerSwitch(1)
            cached = True
        elif e == Qt.Key_F3:
            self.layerSwitch(2)
            cached = True
        elif e == Qt.Key_F4:
            self.layerSwitch(3)
            cached = True
        elif e == Qt.Key_F5:
            self.layerSwitch(4)
            cached = True
        elif e == Qt.Key_F6:
            self.layerSwitch(5)
            cached = True
        elif e == Qt.Key_F7:
            self.layerSwitch(6)
            cached = True
        elif e == Qt.Key_F8:
            self.layerSwitch(7)
            cached = True
        elif e == Qt.Key_F9:
            self.layerSwitch(8)
            cached = True
        elif e == Qt.Key_F10:
            self.layerSwitch(9)
            cached = True
        elif e == Qt.Key_F11:
            self.layerSwitch(10)
            cached = True
        elif e == Qt.Key_F12:
            self.layerSwitch(11)
            cached = True
        elif e == Qt.Key_N:
            if self.timer.isActive():
                self.timer.stop()
            if(self.frame_nb < len(self.pos_stream.frames)-1):
                self.frame_nb = self.frame_nb+1
            cached = True
        elif e == Qt.Key_P:
            if self.timer.isActive():
                self.timer.stop()
            if self.frame_nb > 0:
                self.frame_nb = self.frame_nb-1
            cached = True
        elif e == Qt.Key_G:
            if self.timer.isActive():
                self.timer.stop()
            self.frame_nb = 0
            cached = True
        elif e == Qt.Key_Asterisk:
            factor = 1.05
            self.scale *= factor
            self.transform = factor*self.transform
            cached = True
        elif e == Qt.Key_Slash:
            factor = 1.05
            self.scale /= factor
            self.transform = self.transform/factor
            cached = True
        elif e == Qt.Key_Q:
            QCoreApplication.instance().quit()
            cached = True
        elif e == Qt.Key_Minus:
            if self.fidelity < self.fidelity_max:
                self.fidelity = self.fidelity + 1
            cached = True
        elif e == Qt.Key_Plus:
            if self.fidelity > self.fidelity_min:
                self.fidelity = self.fidelity - 1
            cached = True
        elif e == QKeySequence(Qt.Key_Shift + Qt.Key_N):
            self.start()
            cached = True
        self.update()
        return catched

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.current_point = event.posF()

    def mouseMoveEvent(self, event):
        self.previous_point = self.current_point
        self.current_point = event.posF()
        
        angleY = 4*(self.current_point.x() - self.previous_point.x())/self.width()
        
        sinAngleY = np.sin(angleY)
        cosAngleY = np.cos(angleY)
        generator = np.mat([[cosAngleY, -sinAngleY, 0], [sinAngleY, cosAngleY, 0], [0, 0, 1]])
        self.transform = generator*self.transform

        angleX = -4*(self.current_point.y() - self.previous_point.y())/self.height()
        
        sinAngleX = np.sin(angleX)
        cosAngleX = np.cos(angleX)
        generator = np.mat([[1, 0, 0], [0, cosAngleX, -sinAngleX], [0, sinAngleX, cosAngleX]])
        self.transform = generator*self.transform

        self.update()
            
            
            
        
    def paintEvent(self, event):
        global paint
        paint = QPainter()
        paint.begin(self)


        paint.setRenderHint(QPainter.Antialiasing)
        # make a white drawing background
        paint.setBrush(Qt.gray)
        paint.drawRect(event.rect())

        paint.setTransform(QTransform().translate(0.5*self.width(), 0.5*self.height()))
        
        frame = self.pos_stream.frames[self.frame_nb]
        frame.display(paint,self.transform, self.layer_activity, self.fidelity)

        pen = QPen()
        rlocation = np.array([ -0.49*self.width(), -0.49*self.height() ])
        rsize = [ 100, 18 ]

        pen.setColor(Qt.black)
        paint.setPen(pen)
        rect = QRectF(rlocation[0], rlocation[1], rsize[0], rsize[1])
        paint.drawText(rect, Qt.AlignLeft, "Frame "+str(self.frame_nb+1)+" (n p)")
        rlocation[1] = rlocation[1]+rsize[1]
        rsize = [ 95, 18 ]
        pen.setColor(Qt.black)
        paint.setPen(pen)
        rect = QRectF(rlocation[0], rlocation[1], rsize[0], rsize[1])
        paint.drawText(rect, Qt.AlignLeft, "Texture "+str(self.fidelity_max-self.fidelity)+" (+ -)")

        rlocation[1] = rlocation[1]+rsize[1]
        rsize = [ 95, 18 ]
        for i in range(self.layer_nb):
            rect = QRectF(rlocation[0], rlocation[1]+(i+1)*rsize[1], rsize[0], rsize[1])
            if self.layer_activity[i] == True:
                pen.setColor(Qt.black)
            else:
                pen.setColor(Qt.lightGray)
            paint.setPen(pen)
            paint.drawText(rect, Qt.AlignLeft, self.layer_labels[i])


#            self.layer_labels[i].setText(label)
#            self.layer_labels[i].show()


        paint.end()


