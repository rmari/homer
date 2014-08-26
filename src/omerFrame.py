import numpy as np
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *

class omerFrame:
    
    def __init__(self):
        layer_nb = 12
        self.layers=[omerLayer.omerLayer() for i in range(layer_nb)]

    def populate(self, obj):
        self.objects = obj.asarray()

    def rotate(self, rotation):
        
