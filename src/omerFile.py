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

        self.chunksize = 100000
        self.read(filename)

        
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

    def read(self, filename):        
        print "a"
        names = ['a', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6']
        myframe = pd.read_table(filename, delim_whitespace=True, names=names)
        print "b"
        for k in command_coding:
            myframe.replace(to_replace=k,value=command_coding[k],inplace=True)

        print "c"
        myframe.astype(np.float)
        print "d"
        splitpoints = np.nonzero(np.array(pd.isnull(myframe['a'])))[0]
        print "e"
        whole_array = np.array(myframe)
        print "f"
        split_array = np.split(whole_array, splitpoints)
        print "g"
        self.frames = []
        for frame in split_array:
            self.frames.append(omerFrame.omerFrame(frame))
        print "e"

        self.max = np.array([myframe['p1'].max(), myframe['p2'].max(), myframe['p3'].max()])
        self.min = np.array([myframe['p1'].min(), myframe['p2'].min(), myframe['p3'].min()])

        print "f"
