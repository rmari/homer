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

from string import *
import sys
import numpy as np
import pandas as pd
import io
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *
import homerFrame

command_coding = { 'y':0, '@':1, 'r':3, 'c':4, 'l':5, 's':6 }

class homerFile:
    def __init__(self, filename):
        
        self.is_file=True

        self.chunksize = 500000
        names = ['a', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6']
        self.reader = pd.read_table(filename, delim_whitespace=True, names=names, iterator=True)
#        self.reader = pd.read_table(filename, delimiter='\n', iterator=True)        
        self.frames = []
        self.init = True
        self.read_all = False
        
    def Lx(self):
        return self.max[0]-self.min[0]

    def Ly(self):
        return self.max[1]-self.min[1]

    def Lz(self):
        return self.max[2]-self.min[2]

    def read_chunk(self):
        if self.read_all:
            return False

        in_raw_data = self.reader.get_chunk(self.chunksize)

        if in_raw_data.shape[0] < self.chunksize:
            self.read_all = True
        if in_raw_data.empty:
            return False

        for k in command_coding:
            in_raw_data.replace(to_replace=k,value=command_coding[k],inplace=True)

        in_raw_data.astype(np.float32)
        framepoints = np.nonzero(np.array(pd.isnull(in_raw_data['p1'])))[0] # removes empty lines and lines with only one field

        whole_array = np.array(in_raw_data, dtype=np.float32)
        raw_data_frames = np.split(whole_array, framepoints)

        frame = raw_data_frames[0]
        if self.init:
            self.init = False
            if len(raw_data_frames) == 1:
                self.frames.append(homerFrame.homerFrame(frame))
        else:
            self.frames.append(homerFrame.homerFrame(np.vstack((self.truncated_array, frame))))
            

        for frame in raw_data_frames[1:-1]:
            frame = frame[1:] 
            if frame.size>0:
                self.frames.append(homerFrame.homerFrame(frame))

        self.truncated_array = raw_data_frames[-1]

        self.max = np.array([in_raw_data['p1'].max(), in_raw_data['p2'].max(), in_raw_data['p3'].max()])
        self.min = np.array([in_raw_data['p1'].min(), in_raw_data['p2'].min(), in_raw_data['p3'].min()])

        del in_raw_data
        return True

