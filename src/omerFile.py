from string import *
import sys
import numpy as np
import pandas as pd
import io
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *
import omerFrame

command_coding = { 'y':0, '@':1, 'r':3, 'c':4, 'l':5, 's':6 }

class omerFile:
    def __init__(self, filename):
        
        self.is_file=True

        self.chunksize = 500000
        names = ['a', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6']
        self.reader = pd.read_table(filename, delim_whitespace=True, names=names, iterator=True)
        
        self.frames = []
        self.init = True
        self.read_all = False
        
    def Lx(self):
        return self.max[0]-self.min[0]

    def Ly(self):
        return self.max[1]-self.min[1]

    def Lz(self):
        return self.max[2]-self.min[2]



    def atparse(self,values):
        col=int(values[1])
        if col > 5:
            col=0

        self.color = self.colordef[str(col)]


    def updateBoundaries(self, pos):
        for i in range(3):
            if pos.item(i) > self.max[i]:
                self.max[i] = pos.item(i)
            if pos.item(i) < self.min[i]:
                self.min[i] = pos.item(i)

    def read_chunk(self):
        if self.read_all:
            return False

        myframe = self.reader.get_chunk(self.chunksize)

        if myframe.shape[0] < self.chunksize:
            self.read_all = True
        if myframe.empty:
            return False

        for k in command_coding:
            myframe.replace(to_replace=k,value=command_coding[k],inplace=True)

        myframe.astype(np.float)
        splitpoints = np.nonzero(np.array(pd.isnull(myframe['a'])))[0]

        whole_array = np.array(myframe)
        split_array = np.split(whole_array, splitpoints)
        
        frame = split_array[0]
        if self.init:
            self.init = False
        else:
            self.frames.append(omerFrame.omerFrame(np.vstack((self.truncated_array, frame))))
            
        for frame in split_array[1:-1]:
            self.frames.append(omerFrame.omerFrame(frame))

        self.truncated_array = split_array[-1]


        self.max = np.array([myframe['p1'].max(), myframe['p2'].max(), myframe['p3'].max()])
        self.min = np.array([myframe['p1'].min(), myframe['p2'].min(), myframe['p3'].min()])

        return True
