#    Copyright 2014 Romain Mari
#    This file is part of Homer.
#
#    Homer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *
import numpy as np

import sys, os

import homerFile
import homerScene

class homerWidget(QGLWidget):

    updated = Signal(int)
    read_chunk = Signal()

    def __init__(self, filename, parent=None):

        QGLWidget.__init__(self, QGLFormat(QGL.SampleBuffers), parent)
        self.parent = parent
        
        scene = homerScene.homerScene(self)
        
        self.timer = QBasicTimer()

        self.fname = filename

        self.initWindow()
        
        self.infile=homerFile.homerFile(self.fname)
        self.infile.read_chunk()

        bd = self.infile.getBoundaries()
        
        xmin = bd[0,0]
        xmax = bd[0,1]
        ymin = bd[1,0]
        ymax = bd[1,1]
        
        self.scale = 0.8*self.width()/(xmax-xmin)
#        print -self.scale*xmin,self.scale*ymax
        self.init_offset = QPointF(-self.scale*xmin+0.1*self.width(),self.scale*ymax+0.1*self.width())

        self.offset = self.init_offset
        

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
        self.fidelity_max = 4

        self.installEventFilter(self)

        pal = QPalette()
        pal.setColor(QPalette.Window, homerFile.color_palette[1])
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        self.prefactor = str()

        self.translation = [0, 0]
        
        self.selection_corner1 = QPointF(0,0)
        self.selection_corner2 = QPointF(self.width(),self.height())

        self.target_layer = "all"

        self.relatives = []

        self.verbosity = True
        self.speed=0
        self.is_slave = False

        self.show()

    def initWindow(self):
#        ratio = self.infile.Lz()/self.infile.Lx()
        ratio = 1
        self.windowSizeX = 500
        self.windowSizeY = self.windowSizeX*ratio
        self.windowLocationX = 400
        self.windowLocationY = self.windowLocationX

        self.setGeometry(self.windowLocationX, self.windowLocationY, self.windowSizeX, self.windowSizeY)

        self.setWindowTitle("Homer - "+self.fname)
        path = os.path.dirname(os.path.abspath(__file__))
        self.setWindowIcon(QIcon(path+'/../img/icon.png'))
        
    def setRelatives(self,relatives, own_label):
        self.relatives = relatives
        self.label = own_label
        for r in self.relatives:
            if r != self:
                r.updated.connect(self.slaveUpdate)
                r.read_chunk.connect(self.slaveReadChunk)

    def start(self):
        self.timer.start(self.speed,self)

    @Slot()
    def slaveReadChunk(self):
        self.infile.read_chunk()
        
    def readChunk(self):
        new_frames = self.infile.read_chunk()
        self.read_chunk.emit()
        return new_frames
            
    def incrementOneFrame(self):
        if(self.frame_nb < len(self.infile.frames)-1):
            self.frame_nb = self.frame_nb+1
            return True
        else:
            new_frames = self.readChunk()
            if new_frames:
                self.frame_nb = self.frame_nb+1
                return True
            else:
                return False
        
    def incrementFrame(self,inc_nb):
        count = 1
        while self.incrementOneFrame() and count<inc_nb:
            count = count+1

    def decrementFrame(self, dec_nb):
        if(self.frame_nb >= dec_nb):
            self.frame_nb = self.frame_nb-dec_nb
            return True
        else:
            return False

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if self.forward_anim:
                self.incrementOneFrame()
            else:
                self.decrementFrame(1)
            self.update() 
        else:
            QWidget.timerEvent(self, event)

    def layerSwitch(self,label):
        self.layer_activity[label] = -self.layer_activity[label]
        

    def keyPressEvent(self, event):
        catched = False
        e = event.key()
        m = event.modifiers()

        if e == Qt.Key_Tab:
            self.transform = self.scale*np.identity(3)
            self.offset = self.init_offset
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
        elif e == Qt.Key_N and m != Qt.SHIFT:
            if self.timer.isActive():
                self.timer.stop()
            try:
                inc_nb = int(self.prefactor)
                self.incrementFrame(inc_nb)
            except ValueError:
                self.incrementFrame(1)
            catched = True
        elif e == Qt.Key_P and m != Qt.SHIFT:
            if self.timer.isActive():
                self.timer.stop()
            try:
                dec_nb = int(self.prefactor)
                self.decrementFrame(dec_nb)
            except ValueError:
                self.decrementFrame(1)
            catched = True
        elif e == Qt.Key_G and m != Qt.SHIFT:
            if self.timer.isActive():
                self.timer.stop()
            try:
                f_nb = int(self.prefactor)
                self.frame_nb = f_nb
            except ValueError:
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
            if self.fidelity > self.fidelity_min:
                self.fidelity = self.fidelity - 1
            catched = True
        elif e == Qt.Key_Plus:
            if self.fidelity < self.fidelity_max:
                self.fidelity = self.fidelity + 1
            catched = True
        elif e == Qt.Key_Space:
            self.timer.stop()
            catched = True
        elif e == Qt.Key_V:
            self.verbosity = not self.verbosity
            catched = True
        elif e == Qt.Key_N and m == Qt.SHIFT:
            try:
                inc_nb = int(self.prefactor)
                self.speed = int(1000./inc_nb) # timer timeout in msec
            except ValueError:
                pass
            self.forward_anim = True
            self.start()
            event.accept()
            catched = True
        elif e == Qt.Key_P and m == Qt.SHIFT:
            try:
                inc_nb = int(self.prefactor)
                self.speed = int(1000./inc_nb) # timer timeout in msec
            except ValueError:
                pass
            self.forward_anim = False
            self.start()
            catched = True
        elif e == Qt.Key_G and m == Qt.SHIFT:
            while self.incrementOneFrame():
                pass
            self.update()
            catched = True
        elif e == Qt.Key_L:
            try:
                l_nb = int(self.prefactor)
                self.target_layer = l_nb
            except ValueError:
                self.target_layer = "all"
            catched = True

        t = event.text()
        try:
            i = int(t)
            self.prefactor = self.prefactor + t
        except ValueError:
            if catched:
                self.prefactor = ""
                
        self.update()
        return catched


    def mousePressEvent(self, event):
        modifier = QApplication.keyboardModifiers()
        if event.button() == Qt.LeftButton:
            self.current_point = event.posF()
            self.translate = False
            self.select = False
            self.rotate = False
            if modifier == Qt.ShiftModifier:
                self.translate = True
            elif modifier == Qt.ControlModifier:
                self.select = True
                self.selection_corner1 = self.current_point
            else:
                self.rotate = True

                
    def mouseMoveEvent(self, event):
        self.previous_point = self.current_point
        self.current_point = event.posF()
        if self.translate:
            translateX = self.offset.x() + (self.current_point.x() - self.previous_point.x())
            translateY = self.offset.y() + (self.current_point.y() - self.previous_point.y())
            self.offset = QPointF(translateX, translateY)
        elif self.rotate:
            angleY = -4*(self.current_point.x() - self.previous_point.x())/self.width()
            
            sinAngleY = np.sin(angleY)
            cosAngleY = np.cos(angleY)
            generator = np.mat([[cosAngleY, -sinAngleY, 0], [sinAngleY, cosAngleY, 0], [0, 0, 1]])
            self.transform = generator*self.transform
            
            angleX = 4*(self.current_point.y() - self.previous_point.y())/self.height()
            
            sinAngleX = np.sin(angleX)
            cosAngleX = np.cos(angleX)
            generator = np.mat([[1, 0, 0], [0, cosAngleX, -sinAngleX], [0, sinAngleX, cosAngleX]])
            self.transform = generator*self.transform
        elif self.select: # rotate
            self.selection_corner2 = self.current_point

        self.update()
            
            
    def writeLabels(self, paint):
        pen = QPen()

        rlocation = np.array([ 0.01*self.width(), 0.01*self.height() ])

        bgcolor = QColor(0,0,0,150)
        wratio = 0.8
        rect = QRectF(0,0, 100, 280)
        brush = QBrush()
        brush.setColor(bgcolor)
        brush.setStyle(Qt.SolidPattern)
        paint.setBrush(brush)
        pen.setColor(bgcolor)
        paint.setPen(pen)
        paint.drawRect(rect)
        
        activecolor = Qt.white
        inactivecolor = Qt.gray

        rsize = [ 120, 18 ]
        
        pen.setColor(activecolor)
        paint.setPen(pen)
        rect = QRectF(rlocation[0], rlocation[1], rsize[0], rsize[1])
        paint.drawText(rect, Qt.AlignLeft, "Frame "+str(self.frame_nb+1)+" (n p)")
        rlocation[1] = rlocation[1]+rsize[1]
        rsize = [ 95, 18 ]
        pen.setColor(activecolor)
        paint.setPen(pen)
        rect = QRectF(rlocation[0], rlocation[1], rsize[0], rsize[1])
        paint.drawText(rect, Qt.AlignLeft, "Texture "+str(self.fidelity)+" (+ -)")

        rlocation[1] = rlocation[1]+rsize[1]
        rsize = [ 95, 18 ]
        for i in range(self.layer_nb):
            rect = QRectF(rlocation[0], rlocation[1]+(i+1)*rsize[1], rsize[0], rsize[1])
            if self.layer_activity[i] == True:
                pen.setColor(activecolor)
            else:
                pen.setColor(inactivecolor)
            paint.setPen(pen)
            paint.drawText(rect, Qt.AlignLeft, self.layer_labels[i])

        infoheight = 15
        bgcolor = QColor(0,0,0,200)
        wratio = 0.8
        rect = QRectF(0, self.height()-infoheight, wratio*self.width(), infoheight)
        brush = QBrush()
        brush.setColor(bgcolor)
        brush.setStyle(Qt.SolidPattern)
        paint.setBrush(brush)
        pen.setColor(bgcolor)
        paint.setPen(pen)
        paint.drawRect(rect)
        pen.setColor(activecolor)
        paint.setPen(pen)        
        paint.drawText(rect, Qt.AlignLeft, self.prefactor)

        rect = QRectF(wratio*self.width(), self.height()-infoheight, self.width(), infoheight)
        pen.setColor(bgcolor)
        paint.setPen(pen)
        paint.drawRect(rect)
        pen.setColor(Qt.red)
        paint.setPen(pen)
        if self.target_layer != "all":
            paint.drawText(rect, Qt.AlignLeft, "Layer "+str(self.target_layer))
        else:
            paint.drawText(rect, Qt.AlignLeft, "All layers")
            
    @Slot(int)
    def slaveUpdate(self, master_label):
        self.is_slave = True
        master = self.relatives[master_label]

        self.transform=master.transform
        self.offset = master.offset
        self.frame_nb = master.frame_nb
        self.layer_activity = master.layer_activity
        self.fidelity = master.fidelity
        self.update()

    def paintEvent(self, event):
        paint = QPainter()
        paint.begin(self)
        paint.setRenderHint(QPainter.Antialiasing)

        self.translation = [self.offset.x(), self.offset.y()]

        selection_width = self.selection_corner2.x()-self.selection_corner1.x()
        selection_height = self.selection_corner2.y()-self.selection_corner1.y()
        selection_x = self.selection_corner1.x()-0.5*self.width()
        selection_y = self.selection_corner1.y()-0.5*self.height()
        selection_rect = QRectF(selection_x,selection_y,selection_width,selection_height)

        frame = self.infile.frames[self.frame_nb]
#        print self.translation
        frame.display(paint,self.transform, self.translation, self.layer_activity, self.fidelity,selection_rect)


        if self.verbosity:
            self.writeLabels(paint)
            
        paint.end()

        if len(self.relatives) and not self.is_slave:
            self.updated.emit(self.label)
