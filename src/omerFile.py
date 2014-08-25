from string import *
import sys
import numpy as np
import pandas as pd
import io

class omerFile:
    
    def __init__(self, filename, layers):
        
        self.instream=io.open(str(filename), 'r')
        self.is_file=True



        #            self.is_file=False # means that we deal with stdin
        self.layers = layers
        self.layer=0
        self.color=0
        
        self.get_snapshot()
    
    def Lx(self):
        return 50.

    def Ly(self):
        return 50.

    def Lz(self):
        return 50.


    def __iter__(self):
        return self.positions.__iter__()
        
        
    def parse(self,line):

        values=split(line)
        try:
            cmd = values[0]
        except IndexError:
            return 1

        if cmd == 'y':
            self.layer = int(values[1])
        elif cmd == '@':
            self.color = int(values[1])
        elif cmd == 'r':
            self.radius = float(values[1])
        elif cmd == 'c':
            position = np.mat([float(values[j]) for j in range(1,4)])
            objectType = 'c'
            objectColor = self.color
            objectRadius = self.radius
            self.layers[self.layer].addObject([objectType, objectColor, objectRadius, position])
        elif cmd == 'l':
            position1 = np.mat([float(values[j]) for j in range(1,4)])
            position2 = np.mat([float(values[j]) for j in range(4,7)])
            objectType = 'l'
            objectColor = self.color
            objectRadius = self.radius
            self.layers[self.layer].addObject([objectType, objectColor, objectRadius, position1, position2])
            
            
        return 0
        
        
    def get_snapshot(self, verbose=False):

        for layer in self.layers:
            layer.clear()

        switch=0
        count=0
        for line in self.instream:
            if len(line)==0: # eof
                return 1
        

            switch+=self.parse(line)

            if switch==1:
                break


    def rewind(self): # go to beginning of the file
        if self.is_file:
            self.instream.seek(0)
            self.reset_members()
            return
        else:
            sys.stderr.write("Cannot rewind")
            sys.stderr.write("Input is %s".str(instream))
            sys.exit(1)


    def getData(self): # go to beginning of the file
        my_cols=['object','f0','f1','f2','f3','f4','f5']
        dattype = {'object': np.str, 'f0': np.float, 'f1': np.float, 'f2': np.float, 'f3': np.float, 'f4': np.float, 'f5': np.float}
        self.in_table = pd.read_table('y_D3N512VF0.48Bidi1.4_0.5Cubic_1_fric1_tlub3_sr0.05.yap', sep=' ', names=my_cols, dtype=dattype)
        
        self.in_table[self.in_table['object']=='y']['f0'] == 1
