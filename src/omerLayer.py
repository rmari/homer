import numpy as np
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *

class omerLayer:
    
    def __init__(self):
        self.objects = []
        self.rotated_objects = []

        self.appendPosition = { "c":self.appendCirclePosition, "l":self.appendLinePosition }
        self.appendObject = { "c":self.appendCircleObject, "l":self.appendLineObject }
        self.bare_positions = np.array([])

    def appendCirclePosition(self, objectAttrs):
        if len(self.objects)>0:
            self.bare_positions = np.concatenate([self.bare_positions, objectAttrs[-1]])
        else:
            self.bare_positions = np.matrix(objectAttrs[-1])

    def appendLinePosition(self, objectAttrs):
#        print len(self.objects), len(self.bare_positions)
        if len(self.objects)>0:
            self.bare_positions = np.concatenate([self.bare_positions, objectAttrs[-2], objectAttrs[-1]])
        else:
            self.bare_positions = np.concatenate([objectAttrs[-2], objectAttrs[-1]])


    # for circles: objectAttrs is [color, radius, position]
    def appendCircleObject(self, objectAttrs):
        self.appendCirclePosition(objectAttrs)
        self.objects.append([self.circlePaint, objectAttrs[0], objectAttrs[1], len(self.bare_positions)-1])

    # for lines: objectAttrs is [color, radius, position1, position2]
    def appendLineObject(self, objectAttrs):
        self.appendLinePosition(objectAttrs)
        self.objects.append([self.linePaint, objectAttrs[0], objectAttrs[1], len(self.bare_positions)-2, len(self.bare_positions)-1])

    def addObject(self, objectDefList):
        self.objects.append(objectDefList)

    def addObject(self, objectType, objectAttrs):
        self.appendObject[objectType](objectAttrs)

    def clear(self):
        del self.objects[:]
        

    def rotate(self, rotation):
        if len(self.objects)>0:
            self.rotated_positions = self.bare_positions*rotation

    def circlePaint(self, painter, obj, scale):
        painter.setPen(Qt.black)
        painter.setBrush(Qt.yellow)
        radius = obj[2]*scale
        
        pos = self.rotated_positions[obj[3]]
        pointX=pos.item(0)*scale
        pointY=-pos.item(2)*scale

        objectAttrs = QRectF(pointX, pointY, 2*radius, 2*radius)

        painter.drawEllipse(objectAttrs)
        

    def linePaint(self, painter, obj, scale):
        radius = obj[2]*scale

        pen = QPen(obj[1])
        pen.setWidth(radius)
        painter.setPen(pen)

        pos1 = self.rotated_positions[obj[3]]
        pos2 = self.rotated_positions[obj[4]]
        point1X=pos1.item(0)*scale
        point1Y=-pos1.item(2)*scale
        point2X=pos2.item(0)*scale
        point2Y=-pos2.item(2)*scale
        

        objectAttrs = QLineF(point1X, point1Y, point2X, point2Y)
        painter.drawLine(objectAttrs)

    def paintObjects(self, painter, scale):
        for obj in self.objects:
            obj[0](painter, obj, scale)


class omerBackgroundLayer(omerLayer):
    def __init__(self, Box):
        omerLayer.__init__(self)
        
        thickness=0.2
        self.appendLineObject([Qt.black, thickness, np.matrix([-0.5*Box[0],-0.5*Box[1],-0.5*Box[2]]), np.matrix([0.5*Box[0],-0.5*Box[1],-0.5*Box[2]])])
        self.appendLineObject([Qt.black, thickness, np.matrix([-0.5*Box[0],+0.5*Box[1],-0.5*Box[2]]), np.matrix([0.5*Box[0],+0.5*Box[1],-0.5*Box[2]])])
        self.appendLineObject([Qt.black, thickness, np.matrix([-0.5*Box[0],-0.5*Box[1],+0.5*Box[2]]), np.matrix([0.5*Box[0],-0.5*Box[1],+0.5*Box[2]])])
        self.appendLineObject([Qt.black, thickness, np.matrix([-0.5*Box[0],+0.5*Box[1],+0.5*Box[2]]), np.matrix([0.5*Box[0],+0.5*Box[1],+0.5*Box[2]])])

        self.appendLineObject([Qt.black, thickness, np.matrix([-0.5*Box[0],-0.5*Box[1],-0.5*Box[2]]), np.matrix([-0.5*Box[0],+0.5*Box[1],-0.5*Box[2]])])
        self.appendLineObject([Qt.black, thickness, np.matrix([+0.5*Box[0],-0.5*Box[1],-0.5*Box[2]]), np.matrix([+0.5*Box[0],+0.5*Box[1],-0.5*Box[2]])])
        self.appendLineObject([Qt.black, thickness, np.matrix([-0.5*Box[0],-0.5*Box[1],+0.5*Box[2]]), np.matrix([-0.5*Box[0],+0.5*Box[1],+0.5*Box[2]])])
        self.appendLineObject([Qt.black, thickness, np.matrix([+0.5*Box[0],-0.5*Box[1],+0.5*Box[2]]), np.matrix([+0.5*Box[0],+0.5*Box[1],+0.5*Box[2]])])

        self.appendLineObject([Qt.black, thickness, np.matrix([-0.5*Box[0],-0.5*Box[1],-0.5*Box[2]]), np.matrix([-0.5*Box[0],-0.5*Box[1],+0.5*Box[2]])])
        self.appendLineObject([Qt.black, thickness, np.matrix([+0.5*Box[0],-0.5*Box[1],-0.5*Box[2]]), np.matrix([+0.5*Box[0],-0.5*Box[1],+0.5*Box[2]])])
        self.appendLineObject([Qt.black, thickness, np.matrix([-0.5*Box[0],+0.5*Box[1],-0.5*Box[2]]), np.matrix([-0.5*Box[0],+0.5*Box[1],+0.5*Box[2]])])
        self.appendLineObject([Qt.black, thickness, np.matrix([+0.5*Box[0],+0.5*Box[1],-0.5*Box[2]]), np.matrix([+0.5*Box[0],+0.5*Box[1],+0.5*Box[2]])])

