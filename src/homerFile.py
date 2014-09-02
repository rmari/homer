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
        
        self.frames = []
        self.init = True
        self.read_all = False
        
    def Lx(self):
        return self.max[0]-self.min[0]

    def Ly(self):
        return self.max[1]-self.min[1]

    def Lz(self):
        return self.max[2]-self.min[2]


    def parse_raw_frame(self, raw_frame):
        self.objects = obj
        obj_nb = (self.objects[:,0].shape)[0]

        self.pos1_ind = 1
        self.pos2_ind = 4

        self.size_ind = 7
        self.color_ind = 8
        self.layer_ind = 9

        self.bare_positions = np.array(self.objects[:,self.pos1_ind:], dtype=np.float64)
        self.bare_positions[:,[1,2,4,5]] = -self.bare_positions[:,[1,2,4,5]]

        size_pos = np.nonzero(self.objects[:,0] == command_coding['r'])[0]
        self.bare_sizes = np.zeros(obj_nb)

        for i in range(len(size_pos)-1):
            self.bare_sizes[size_pos[i]:size_pos[i+1]] = self.objects[size_pos[i],1]
        self.bare_sizes[size_pos[-1]:] = self.objects[size_pos[-1],1]

        color_pos = np.nonzero(self.objects[:,0] == command_coding['@'])[0]
        self.bare_colors = np.empty(obj_nb, dtype=np.int)

        for i in range(len(color_pos)-1):
            self.bare_colors[color_pos[i]:color_pos[i+1]] = int(self.objects[color_pos[i],1])
        self.bare_colors[color_pos[-1]:] = int(self.objects[color_pos[-1],1])

        layer_pos = np.nonzero(self.objects[:,0] == command_coding['y'])[0]
        self.bare_layers = np.empty(obj_nb, dtype=np.int)

        for i in range(len(color_pos)-1):
            self.bare_layers[layer_pos[i]:layer_pos[i+1]] = int(self.objects[layer_pos[i],1])
        self.bare_layers[layer_pos[-1]:] = int(self.objects[layer_pos[-1],1])
        
        self.objects = np.hstack((self.objects, np.reshape(self.bare_sizes,(obj_nb,1)), np.reshape(self.bare_colors,(obj_nb,1)), np.reshape(self.bare_layers,(obj_nb,1))))

        # remove non-object commands
        real_obj_indices = -np.isnan(self.bare_positions[:,2])
        self.objects = self.objects[real_obj_indices]
        self.bare_positions = self.bare_positions[real_obj_indices]
        self.bare_sizes = self.bare_sizes[real_obj_indices]


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

        in_raw_data.astype(np.float)
        framepoints = np.nonzero(np.array(pd.isnull(in_raw_data['a'])))[0]

        whole_array = np.array(in_raw_data)
        raw_data_frames = np.split(whole_array, framepoints)
        
        frame = raw_data_frames[0]
        if self.init:
            self.init = False
        else:
            self.frames.append(homerFrame.homerFrame(np.vstack((self.truncated_array, frame))))
            
        for frame in raw_data_frames[1:-1]:
            self.frames.append(homerFrame.homerFrame(frame))

        self.truncated_array = raw_data_frames[-1]


        self.max = np.array([in_raw_data['p1'].max(), in_raw_data['p2'].max(), in_raw_data['p3'].max()])
        self.min = np.array([in_raw_data['p1'].min(), in_raw_data['p2'].min(), in_raw_data['p3'].min()])

        return True

