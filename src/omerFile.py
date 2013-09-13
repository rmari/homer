from string import *
import sys
import numpy as np
import io
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *

class omerFile:
    def __init__(self, filename, layers):
        
        self.instream=io.open(str(filename), 'r')
        self.is_file=True

        #            self.is_file=False # means that we deal with stdin
        self.layers = layers
        self.layer=0
        self.color=0
        self.colordef = { '0': Qt.black, '1':Qt.gray, '2':Qt.blue, '3':Qt.red, '4':Qt.yellow, '5':Qt.green }
        self.parser_dict = {'c': self.cparse,'l': self.lparse, 'r': self.rparse, 'y': self.yparse, '@': self.atparse }

        self.max = [40.,0.,40.]
        self.min = [-40.,0.,-40.]
        
        self.chunksize = 100000

        while self.Lx() == 0.:
            self.get_snapshot()
    


        
    def Lx(self):
        return self.max[0]-self.min[0]

    def Ly(self):
        return self.max[1]-self.min[1]

    def Lz(self):
        return self.max[2]-self.min[2]


    def __iter__(self):
        return self.positions.__iter__()
        

    @profile    
    def cparse(self,values):
        cattrs = np.asmatrix(values[1:], dtype=float)
#        position = np.mat([float(values[j]) for j in range(1,4)])
#        self.updateBoundaries(position)
        self.layers[self.layer].addObject('c', cattrs, [self.color, self.radius])

    @profile        
    def lparse(self,values):
        lattrs = np.asmatrix(values[1:], dtype=float)
#        position1 = np.mat([float(values[j]) for j in range(1,4)])
#        position2 = np.mat([float(values[j]) for j in range(4,7)])

#        self.layers[self.layer].addObject('l', lattrs, [self.color, self.radius])

    def atparse(self,values):
        col=int(values[1])
        if col > 5:
            col=0

        self.color = self.colordef[str(col)]

    def rparse(self,values):
        self.radius = float(values[1]) 

    def yparse(self,values):
        self.layer = int(values[1])

    def updateBoundaries(self, pos):
        for i in range(3):
            if pos.item(i) > self.max[i]:
                self.max[i] = pos.item(i)
            if pos.item(i) < self.min[i]:
                self.min[i] = pos.item(i)



    @profile
    def get_snapshot(self, verbose=False):

        for layer in self.layers:
            layer.clear()


#    def get_chunk(self):
#       lines = self.instream.readlines()

        for line in self.instream:
            values=split(line)
            try:
                self.parser_dict[values[0]](values)
            except IndexError:
                return 0


            
        return 1 # eof
        

    def rewind(self): # go to beginning of the file
        if self.is_file:
            self.instream.seek(0)
            self.reset_members()
            return
        else:
            sys.stderr.write("Cannot rewind")
            sys.stderr.write("Input is %s".str(instream))
            sys.exit(1)

