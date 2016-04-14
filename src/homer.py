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

from __future__ import print_function
from PySide.QtGui import QApplication, QIcon

import sys
import os

import homerWidget


def init():
    arg_nb_min = 2
    if len(sys.argv) != arg_nb_min:
        print("\n   Utilisation: ", sys.argv[0], "INPUT_FILE\n")
        exit(1)
    return sys.argv[1]

app = QApplication([])

filename = init()
widgets = homerWidget.homerWidget(filename)

path = os.path.dirname(os.path.abspath(__file__))
app.setWindowIcon(QIcon(path+'/../img/icon.png'))

sys.exit(app.exec_())
