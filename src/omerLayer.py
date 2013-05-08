import numpy as np

class omerLayer:

    def __init__(self):
        self.objects = []
        self.rotated_objects = []
        self.sizeX = 0.
        self.sizeY = 0.
        self.maxX = 0
        self.maxY = 0
        self.minX = 0
        self.minY = 0

    def addObject(self, objectDefList):
        self.objects.append(objectDefList)


    def clear(self):
        del self.objects[:]

