#!/usr/bin/env python

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

import homerWidget


def init():
    
    arg_nb_min=2
    if len(sys.argv) < arg_nb_min :
        print("   Utilisation: ", sys.argv[0], "INPUT_FILES")
        exit(1)
        
    return sys.argv[1:]



app = QApplication([])    

filenames=init()
widgets = [ homerWidget.homerWidget(f) for f in filenames ]

path = os.path.dirname(os.path.abspath(__file__))
app.setWindowIcon(QIcon(path+'/../img/icon.png'))

cnt = 0
for w in widgets:
    w.setRelatives(widgets, cnt)
    cnt = cnt+1

sys.exit(app.exec_())
