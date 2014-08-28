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
        
        self.timer = QBasicTimer()

        self.infile=omerFile.omerFile(filename)
        self.infile.read_chunk()

        self.scale = 0.7*self.width()/self.infile.Lx()

        self.initWindow()
        
        self.transform = self.scale*np.identity(3)

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

    def initWindow(self):
        ratio = self.infile.Lz()/self.infile.Lx()
        self.windowSizeX = 800
        self.windowSizeY = self.windowSizeX*ratio
        self.windowLocationX = 400
        self.windowLocationY = self.windowLocationX

        self.setGeometry(self.windowLocationX, self.windowLocationY, self.windowSizeX, self.windowSizeY)

        self.setWindowTitle('omer viewer')

    def start(self):
        self.timer.start(self.speed,self)

    def incrementFrame(self):
        if(self.frame_nb < len(self.infile.frames)-1):
            self.frame_nb = self.frame_nb+1
            return True
        else:
            new_frames = self.infile.read_chunk()
            if new_frames:
                self.frame_nb = self.frame_nb+1
                return True
            else:
                return False

    def decrementFrame(self):
        if(self.frame_nb > 0):
            self.frame_nb = self.frame_nb-1
            return True
        else:
            return False

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if self.forward_anim:
                self.incrementFrame()
            else:
                self.decrementFrame()
            self.update() 
        else:
            QWidget.timerEvent(self, event)

    def layerSwitch(self,label):
        self.layer_activity[label] = -self.layer_activity[label]
        
    def eventFilter(self, obj, event):
        
        if obj == self:
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
            
        else:
            return False 



    def keyPressEvent(self, event):
        catched = False
        e = event.key()
        if e == Qt.Key_Tab:
            self.transform = self.scale*np.identity(3)
            catched = True
        elif e == Qt.Key_F1:
            self.layerSwitch(0)
            catched = True
        elif e == Qt.Key_F2:
            self.layerSwitch(1)
            catched = True
        elif e == Qt.Key_F3:
            self.layerSwitch(2)
            catched = True
        elif e == Qt.Key_F4:
            self.layerSwitch(3)
            catched = True
        elif e == Qt.Key_F5:
            self.layerSwitch(4)
            catched = True
        elif e == Qt.Key_F6:
            self.layerSwitch(5)
            catched = True
        elif e == Qt.Key_F7:
            self.layerSwitch(6)
            catched = True
        elif e == Qt.Key_F8:
            self.layerSwitch(7)
            catched = True
        elif e == Qt.Key_F9:
            self.layerSwitch(8)
            catched = True
        elif e == Qt.Key_F10:
            self.layerSwitch(9)
            catched = True
        elif e == Qt.Key_F11:
            self.layerSwitch(10)
            catched = True
        elif e == Qt.Key_F12:
            self.layerSwitch(11)
            catched = True
        elif e == Qt.Key_N:
            if self.timer.isActive():
                self.timer.stop()
            self.incrementFrame()
            catched = True
        elif e == Qt.Key_P:
            if self.timer.isActive():
                self.timer.stop()
            self.decrementFrame()
            catched = True
        elif e == Qt.Key_G:
            if self.timer.isActive():
                self.timer.stop()
            self.frame_nb = 0
            catched = True
        elif e == Qt.Key_Asterisk:
            factor = 1.05
            self.scale *= factor
            self.transform = factor*self.transform
            catched = True
        elif e == Qt.Key_Slash:
            factor = 1.05
            self.scale /= factor
            self.transform = self.transform/factor
            catched = True
        elif e == Qt.Key_Q:
            QCoreApplication.instance().quit()
            catched = True
        elif e == Qt.Key_Minus:
            if self.fidelity < self.fidelity_max:
                self.fidelity = self.fidelity + 1
            catched = True
        elif e == Qt.Key_Plus:
            if self.fidelity > self.fidelity_min:
                self.fidelity = self.fidelity - 1
            catched = True
        elif e == Qt.Key_Space:
            self.timer.stop()
            catched = True

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
            
            
    def writeLabels(self, paint):
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

            
        
    def paintEvent(self, event):
        global paint
        paint = QPainter()
        paint.begin(self)

        paint.setRenderHint(QPainter.Antialiasing)

        paint.setTransform(QTransform().translate(0.5*self.width(), 0.5*self.height()))
        
        frame = self.infile.frames[self.frame_nb]
        frame.display(paint,self.transform, self.layer_activity, self.fidelity)

        self.writeLabels(paint)

        paint.end()


