from string import *
import sys
import numpy as np
import pandas as pd
import io
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *
import omerFrame

class omerFile:
    def __init__(self, filename):
        
        self.is_file=True

        self.max = [40.,0.,40.]
        self.min = [-40.,0.,-40.]
        
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

        names = ['a', 'r', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6']
        myframe = pd.read_table(filename, sep=" ", names=names)
        splitpoints = np.nonzero(np.array(pd.isnull(myframe['a'])))[0]
        print splitpoints
        whole_array = np.array(myframe)
        print whole_array[:10,:]
        split_array = np.split(whole_array, splitpoints)
        
        print "Got split array ", len(split_array)
        exit 
        self.frames = []
        for frame in split_array:
            self.frames.append(omerFrame.omerFrame(frame))


