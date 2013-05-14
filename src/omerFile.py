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

        self.max = [0.,0.,0.]
        self.min = [0.,0.,0.]
        
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
        
        
    def parse(self,line):

        values=split(line)
        try:
            cmd = str(values[0])
        except IndexError:
            return 1

        if cmd == 'y':
            self.layer = int(values[1])
        elif cmd == '@':
            col=int(values[1])
            if col > 5:
                col=0
            self.color = self.colordef[str(col)]

        elif cmd == 'r':
            self.radius = float(values[1])
        elif cmd == 'c':
            position = np.mat([float(values[j]) for j in range(1,4)])
            self.updateBoundaries(position)
            objectType = 'c'
            objectColor = self.color
            objectRadius = self.radius
            self.layers[self.layer].addObject(objectType, [objectColor, objectRadius, position])
        elif cmd == 'l':
#            print values
#            print len(values), range(4,7)
            position1 = np.mat([float(values[j]) for j in range(1,4)])
            position2 = np.mat([float(values[j]) for j in range(4,7)])
            self.updateBoundaries(position1)
            self.updateBoundaries(position2)
            objectType = 'l'
            objectColor = self.color
            objectRadius = self.radius
            self.layers[self.layer].addObject(objectType, [objectColor, objectRadius, position1, position2])
            
            
        return 0
        
        
    def updateBoundaries(self, pos):
        for i in range(3):
            if pos.item(i) > self.max[i]:
                self.max[i] = pos.item(i)
            if pos.item(i) < self.min[i]:
                self.min[i] = pos.item(i)


    def get_snapshot(self, verbose=False):

        for layer in self.layers:
            layer.clear()

        switch=0
        count=0
        for line in self.instream:
            switch+=self.parse(line)

            if switch==1:
                break


        if switch == 0: # eof
            return 1
        

    def rewind(self): # go to beginning of the file
        if self.is_file:
            self.instream.seek(0)
            self.reset_members()
            return
        else:
            sys.stderr.write("Cannot rewind")
            sys.stderr.write("Input is %s".str(instream))
            sys.exit(1)

