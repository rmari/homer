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
from __future__ import division
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
import PySide.QtOpenGL as QtOpenGL
import numpy as np

import sys
import os

import homerFile


class homerWidget(QtOpenGL.QGLWidget):

    def __init__(self, filename, parent=None):

        QtOpenGL.QGLWidget.__init__(
            self, QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent)
        self.parent = parent
        self.timer = QtCore.QBasicTimer()

        self.fname = filename

        self.initWindow()

        self.infile = homerFile.homerFile(self.fname)
        self.infile.read_chunk()

        bd = self.infile.getBoundaries()

        xmin = bd[0, 0]
        xmax = bd[0, 1]
        ymax = bd[1, 1]

        self.scale = 0.8*self.width()/(xmax-xmin)

        self.init_offset = QtCore.QPointF(-self.scale*xmin+0.1*self.width(),
                                          self.scale*ymax+0.1*self.width())

        self.offset = self.init_offset

        color_fname = "homer_config.py"
        if os.path.isfile(color_fname):
            sys.path.append(".")
            import homer_config
            self.init_transform = np.array(homer_config.init_transform)
        else:
            self.init_transform = np.identity(3)
        self.transform = self.scale*self.init_transform

        self.frame_nb = 0

        self.layer_nb = 12
        self.layer_activity = np.ones(self.layer_nb, dtype=np.bool)
        self.layer_labels = []

        for i in range(self.layer_nb):
            label = "Layer "+str(i+1)+" (F"+str(i+1)+")"
            self.layer_labels.append(label)

        self.fidelity = 4
        self.fidelity_min = 0
        self.fidelity_max = 4

        self.installEventFilter(self)

        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Window, homerFile.color_palette[1])
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        self.prefactor = str()

        self.translation = [0, 0]

        self.selection_corner1 = QtCore.QPointF(0, 0)
        self.selection_corner2 = QtCore.QPointF(self.width(), self.height())

        self.target_layer = "all"

        self.verbosity = True
        self.speed = 0
        self.is_slave = False
        self.update_nb = 0
        self.show()

    def initWindow(self):
        #  ratio = self.infile.Lz()/self.infile.Lx()
        ratio = 1
        self.windowSizeX = 500
        self.windowSizeY = self.windowSizeX*ratio
        self.windowLocationX = 400
        self.windowLocationY = self.windowLocationX

        self.setGeometry(self.windowLocationX, self.windowLocationY,
                         self.windowSizeX, self.windowSizeY)

        self.setWindowTitle("Homer - "+self.fname)
        path = os.path.dirname(os.path.abspath(__file__))
        self.setWindowIcon(QtGui.QIcon(path+'/../img/icon.png'))

    def start(self):
        self.timer.start(self.speed, self)

    def readChunk(self):
        new_frames = self.infile.read_chunk()
        self.read_chunk.emit()
        return new_frames

    def switchFrameNb(self, new_frame_nb):
        self.former_frame_nb = self.frame_nb
        self.frame_nb = new_frame_nb

    def goToFrame(self, nb):
        while nb > len(self.infile.frames)-1:
            new_frames = self.readChunk()
            if not new_frames:
                self.switchFrameNb(len(self.infile.frames)-1)
                return
        self.switchFrameNb(nb)

    def incrementOneFrame(self):
        if(self.frame_nb < len(self.infile.frames)-1):
            self.switchFrameNb(self.frame_nb+1)
            return True
        else:
            new_frames = self.readChunk()
            if new_frames:
                self.switchFrameNb(self.frame_nb+1)
                return True
            else:
                return False

    def incrementFrame(self, inc_nb):
        count = 1
        while self.incrementOneFrame() and count < inc_nb:
            count = count+1

    def decrementFrame(self, dec_nb):
        if(self.frame_nb >= dec_nb):
            self.switchFrameNb(self.frame_nb-dec_nb)
            return True
        else:
            return False

    def setXRotation(self, angleX):
        sinAngleX = np.sin(angleX)
        cosAngleX = np.cos(angleX)
        generator = np.mat([[1, 0, 0],
                            [0, cosAngleX, -sinAngleX],
                            [0, sinAngleX, cosAngleX]])
        self.transform = generator*self.transform

    def setYRotation(self, angleY):
        sinAngleY = np.sin(angleY)
        cosAngleY = np.cos(angleY)
        generator = np.mat([[cosAngleY, -sinAngleY, 0],
                            [sinAngleY, cosAngleY, 0],
                            [0, 0, 1]])
        self.transform = generator*self.transform

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if self.forward_anim:
                self.incrementOneFrame()
            else:
                self.decrementFrame(1)
            self.update()
        else:
            QtGui.QWidget.timerEvent(self, event)

    def layerSwitch(self, label):
        self.layer_activity[label] = -self.layer_activity[label]

    def handleFrameSwitchKey(self, e, m):
        caught = False
        stop_anim = True
        if e == QtCore.Qt.Key_N and m != QtCore.Qt.SHIFT:
            try:
                inc_nb = int(self.prefactor)
                self.incrementFrame(inc_nb)
            except ValueError:
                self.incrementFrame(1)
            caught = True
        elif e == QtCore.Qt.Key_P and m != QtCore.Qt.SHIFT:
            try:
                dec_nb = int(self.prefactor)
                self.decrementFrame(dec_nb)
            except ValueError:
                self.decrementFrame(1)
            caught = True
        elif e == QtCore.Qt.Key_G and m != QtCore.Qt.SHIFT:
            try:
                f_nb = int(self.prefactor)-1
                self.goToFrame(f_nb)
            except ValueError:
                self.switchFrameNb(0)
            caught = True
        elif e == QtCore.Qt.Key_Z:
            self.switchFrameNb(self.former_frame_nb)
            caught = True
        elif e == QtCore.Qt.Key_N and m == QtCore.Qt.SHIFT:
            try:
                inc_nb = int(self.prefactor)
                self.speed = int(1000./inc_nb)  # timer timeout in msec
            except ValueError:
                pass
            self.forward_anim = True
            self.start()
            caught = True
            stop_anim = False
        elif e == QtCore.Qt.Key_P and m == QtCore.Qt.SHIFT:
            try:
                inc_nb = int(self.prefactor)
                self.speed = int(1000./inc_nb)  # timer timeout in msec
            except ValueError:
                pass
            self.forward_anim = False
            self.start()
            caught = True
            stop_anim = False
        elif e == QtCore.Qt.Key_G and m == QtCore.Qt.SHIFT:
            while self.incrementOneFrame():
                pass
            self.update()
            caught = True
        elif e == QtCore.Qt.Key_Space:
            caught = True

        if caught and stop_anim:
            if self.timer.isActive():
                self.timer.stop()

        return caught

    def handlePointOfViewKey(self, e, m):
        caught = False
        if e == QtCore.Qt.Key_Tab and m != QtCore.Qt.SHIFT:
            self.transform = self.scale*self.init_transform
            caught = True
        elif e == QtCore.Qt.Key_Tab and m == QtCore.Qt.SHIFT:
            self.offset = self.init_offset
            caught = True
        elif e == QtCore.Qt.Key_Asterisk:
            factor = 1.05
            self.scale *= factor
            self.transform = factor*self.transform
            caught = True
        elif e == QtCore.Qt.Key_Slash:
            factor = 1.05
            self.scale /= factor
            self.transform = self.transform/factor
            caught = True
        elif e == QtCore.Qt.Key_Minus:
            if self.fidelity > self.fidelity_min:
                self.fidelity = self.fidelity - 1
            caught = True
        elif e == QtCore.Qt.Key_Plus:
            if self.fidelity < self.fidelity_max:
                self.fidelity = self.fidelity + 1
            caught = True
        elif e == QtCore.Qt.Key_Up:
            if m != QtCore.Qt.SHIFT:
                try:
                    angleX = -np.deg2rad(float(self.prefactor))
                except ValueError:
                    angleX = -0.1
            else:
                angleX = -0.5*np.pi
            self.setXRotation(angleX)
            caught = True
        elif e == QtCore.Qt.Key_Down:
            if m != QtCore.Qt.SHIFT:
                try:
                    angleX = np.deg2rad(float(self.prefactor))
                except ValueError:
                    angleX = 0.1
            else:
                angleX = 0.5*np.pi
            self.setXRotation(angleX)
            caught = True
        elif e == QtCore.Qt.Key_Left:
            if m != QtCore.Qt.SHIFT:
                try:
                    angleY = np.deg2rad(float(self.prefactor))
                except ValueError:
                    angleY = 0.1
            else:
                angleY = 0.5*np.pi
            self.setYRotation(angleY)
            caught = True
        elif e == QtCore.Qt.Key_Right:
            if m != QtCore.Qt.SHIFT:
                try:
                    angleY = -np.deg2rad(float(self.prefactor))
                except ValueError:
                    angleY = -0.1
            else:
                angleY = -0.5*np.pi
            self.setYRotation(angleY)
            caught = True

        return caught

    def handleLayerKey(self, e, m):
        caught = False

        if e == QtCore.Qt.Key_F1:
            self.layerSwitch(0)
            caught = True
        elif e == QtCore.Qt.Key_F2:
            self.layerSwitch(1)
            caught = True
        elif e == QtCore.Qt.Key_F3:
            self.layerSwitch(2)
            caught = True
        elif e == QtCore.Qt.Key_F4:
            self.layerSwitch(3)
            caught = True
        elif e == QtCore.Qt.Key_F5:
            self.layerSwitch(4)
            caught = True
        elif e == QtCore.Qt.Key_F6:
            self.layerSwitch(5)
            caught = True
        elif e == QtCore.Qt.Key_F7:
            self.layerSwitch(6)
            caught = True
        elif e == QtCore.Qt.Key_F8:
            self.layerSwitch(7)
            caught = True
        elif e == QtCore.Qt.Key_F9:
            self.layerSwitch(8)
            caught = True
        elif e == QtCore.Qt.Key_F10:
            self.layerSwitch(9)
            caught = True
        elif e == QtCore.Qt.Key_F11:
            self.layerSwitch(10)
            caught = True
        elif e == QtCore.Qt.Key_F12:
            self.layerSwitch(11)
            caught = True
        elif e == QtCore.Qt.Key_L:
            try:
                l_nb = int(self.prefactor)
                self.target_layer = l_nb
            except ValueError:
                self.target_layer = "all"
            caught = True
        return caught

    def handleKey(self, e, m):
        if e == QtCore.Qt.Key_Q:
            caught = True
            # for an unknown reason, bad crash on Gnome 3
            # (Gnome is made unusable, forcing logout)
            # if Q is the very first event received.
            # So we test for update_nb
            if self.update_nb > 3:
                self.close()
        elif e == QtCore.Qt.Key_V:
            self.verbosity = not self.verbosity
            caught = True
        else:
            caught = self.handleLayerKey(e, m)
            if not caught:
                caught = self.handlePointOfViewKey(e, m)
            if not caught:
                caught = self.handleFrameSwitchKey(e, m)
        return caught

    def keyPressEvent(self, event):
        e = event.key()
        m = event.modifiers()
        if e == QtCore.Qt.Key_Return:  # repeat previous action
            e, m, self.prefactor = self.old_e, self.old_m, self.old_prefactor
        self.old_prefactor = self.prefactor
        caught = self.handleKey(e, m)

        t = event.text()
        if e != QtCore.Qt.Key_Return:
            try:
                i = int(t)
                self.prefactor = self.prefactor + t
            except ValueError:
                if caught:
                    self.prefactor = ""

        if caught:
            self.old_e, self.old_m = e, m

        self.update()
        return caught

    def mousePressEvent(self, event):
        modifier = QtGui.QApplication.keyboardModifiers()
        if event.button() == QtCore.Qt.LeftButton:
            self.current_point = event.posF()
            self.translate = False
            self.select = False
            self.rotate = False
            if modifier == QtCore.Qt.ShiftModifier:
                self.translate = True
            elif modifier == QtCore.Qt.ControlModifier:
                self.select = True
                self.selection_corner1 = self.current_point
            else:
                self.rotate = True

    def mouseMoveEvent(self, event):
        self.previous_point = self.current_point
        self.current_point = event.posF()
        if self.translate:
            translateX = self.offset.x()\
                + (self.current_point.x() - self.previous_point.x())
            translateY = self.offset.y()\
                + (self.current_point.y() - self.previous_point.y())
            self.offset = QtCore.QPointF(translateX, translateY)
        elif self.rotate:
            angleY = self.current_point.x() - self.previous_point.x()
            angleY *= -4/self.width()
            sinAngleY = np.sin(angleY)
            cosAngleY = np.cos(angleY)
            generator = np.mat([[cosAngleY, -sinAngleY, 0],
                                [sinAngleY, cosAngleY, 0],
                                [0, 0, 1]])
            self.transform = generator*self.transform

            angleX = self.current_point.y() - self.previous_point.y()
            angleX *= 4/self.height()

            sinAngleX = np.sin(angleX)
            cosAngleX = np.cos(angleX)
            generator = np.mat([[1, 0, 0],
                                [0, cosAngleX, -sinAngleX],
                                [0, sinAngleX, cosAngleX]])
            self.transform = generator*self.transform
        elif self.select:  # rotate
            self.selection_corner2 = self.current_point

        self.update()

    def writeLabels(self, paint):
        pen = QtGui.QPen()

        rlocation = np.array([15, 15])

        bgcolor = QtGui.QColor(0, 0, 0, 150)
        wratio = 0.8
        rect = QtCore.QRectF(0, 0, 140, 300)
        brush = QtGui.QBrush()
        brush.setColor(bgcolor)
        brush.setStyle(QtCore.Qt.SolidPattern)
        paint.setBrush(brush)
        pen.setColor(bgcolor)
        paint.setPen(pen)
        paint.drawRect(rect)

        activecolor = QtCore.Qt.white
        inactivecolor = QtCore.Qt.gray

        rsize = [120, 18]

        pen.setColor(activecolor)
        paint.setPen(pen)
        rect = QtCore.QRectF(rlocation[0], rlocation[1], rsize[0], rsize[1])
        paint.drawText(rect, QtCore.Qt.AlignLeft,
                       "Frame "+str(self.frame_nb+1)+" (n p)")
        rlocation[1] = rlocation[1]+rsize[1]
        rsize = [95, 18]
        pen.setColor(activecolor)
        paint.setPen(pen)
        rect = QtCore.QRectF(rlocation[0], rlocation[1], rsize[0], rsize[1])
        paint.drawText(rect, QtCore.Qt.AlignLeft,
                       "Texture "+str(self.fidelity)+" (+ -)")

        rlocation[1] = rlocation[1]+rsize[1]
        rsize = [100, 18]
        for i in range(self.layer_nb):
            rect = QtCore.QRectF(rlocation[0], rlocation[1]+(i+1)*rsize[1],
                                 rsize[0], rsize[1])
            if self.layer_activity[i]:
                pen.setColor(activecolor)
            else:
                pen.setColor(inactivecolor)

            paint.setPen(pen)
            paint.drawText(rect, QtCore.Qt.AlignLeft, self.layer_labels[i])

        infoheight = 20
        bgcolor = QtGui.QColor(30, 30, 30, 200)
        wratio = 0.8
        xdivide = wratio*self.width()
        rect = QtCore.QRectF(0, self.height()-infoheight+2,
                             xdivide, infoheight+2)
        brush = QtGui.QBrush()
        brush.setColor(bgcolor)
        brush.setStyle(QtCore.Qt.SolidPattern)
        paint.setBrush(brush)
        pen.setColor(bgcolor)
        paint.setPen(pen)
        paint.drawRect(rect)
        pen.setColor(activecolor)
        paint.setPen(pen)
        rect = QtCore.QRectF(0, self.height()-infoheight+2,
                             xdivide-4, infoheight+2)
        paint.drawText(rect, QtCore.Qt.AlignRight, self.prefactor)

        rect = QtCore.QRectF(xdivide, self.height()-infoheight+2,
                             self.width(), infoheight+2)
        bgcolor = QtGui.QColor(0, 0, 0, 200)
        brush.setColor(bgcolor)
        brush.setStyle(QtCore.Qt.SolidPattern)
        paint.setBrush(brush)
        pen.setColor(bgcolor)
        paint.setPen(pen)
        paint.drawRect(rect)
        rect = QtCore.QRectF(xdivide+4, self.height()-infoheight+2,
                             self.width(), infoheight+2)
        pen.setColor(QtGui.QColor(220, 100, 0))
        paint.setPen(pen)
        if self.target_layer != "all":
            paint.drawText(rect, QtCore.Qt.AlignLeft,
                           "Layer "+str(self.target_layer))
        else:
            paint.drawText(rect, QtCore.Qt.AlignLeft, "All layers")

    def paintEvent(self, event):
        paint = QtGui.QPainter()
        paint.begin(self)
        paint.setRenderHint(QtGui.QPainter.Antialiasing)

        self.translation = [self.offset.x(), self.offset.y()]

        selection_width = self.selection_corner2.x()-self.selection_corner1.x()
        selection_height = self.selection_corner2.y()\
            - self.selection_corner1.y()
        selection_x = self.selection_corner1.x()-0.5*self.width()
        selection_y = self.selection_corner1.y()-0.5*self.height()
        selection_rect = QtCore.QRectF(selection_x, selection_y,
                                       selection_width, selection_height)

        frame = self.infile.frames[self.frame_nb]
        frame.display(paint, self.transform, self.translation,
                      self.layer_activity, self.fidelity, selection_rect)

        if self.verbosity:
            self.writeLabels(paint)

        paint.end()

        self.update_nb += 1
