#!/Users/LevichFellow/anaconda/bin/python
##!/usr/bin/python
#coding=utf-8
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *
import numpy as np

import sys, os

import homerWidget

def init():
    
    arg_nb=2
    if len(sys.argv) != arg_nb :
        print "   Utilisation: ", sys.argv[0], "INPUT_FILE"
        exit(1)
        
    return sys.argv[1]



app = QApplication([])    

filename=init()
SimuViewer=homerWidget.homerWidget(filename)


sys.exit(app.exec_())
