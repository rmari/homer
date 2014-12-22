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
#import pandas as pd
import io
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *
import homerFrame

command_coding = { 'y':0, '@':1, 'r':3, 'c':4, 'l':5, 's':6 }

class homerFile:
    def __init__(self, filename):
        
        self.is_file=True
        self.fname=filename
        self.chunksize = 1000000#10000000
        self.frames = []
        self.is_init = True
        self.read_all = False
        self.infile = open(self.fname,'r')

        
    def Lx(self):
        return self.max[0]-self.min[0]

    def Ly(self):
        return self.max[1]-self.min[1]

    def Lz(self):
        return self.max[2]-self.min[2]

    def read_chunk(self):
        if self.read_all:
            return False

        ftype = np.float32

        in_raw_data = np.core.defchararray.partition(np.asarray(self.infile.readlines(self.chunksize), dtype=np.str_), ' ')[:,[0,2]]
        while not np.any(in_raw_data[:,0]=='\n'):
            b = np.core.defchararray.partition(np.asarray(self.infile.readlines(self.chunksize), dtype=np.str_), ' ')[:,[0,2]]
            in_raw_data=np.vstack((in_raw_data,b))
        
        obj_nb = np.shape(in_raw_data)[0]

        attributes = np.zeros(obj_nb, dtype=[('r', ftype), ('@', ftype), ('y', ftype)])

        all_att_mask = np.ones(obj_nb, dtype=np.bool)
        for at in ['r','@','y']:
            att_mask = in_raw_data[:,0]==at
            all_att_mask -= att_mask
            pos = np.nonzero(att_mask)[0]
            if not self.is_init:
                attributes[at][:pos[0]] = self.trailing_attributes[at][-1]
                
            if len(pos)>0:
                for i in range(len(pos)-1):
                    attributes[at][pos[i]:pos[i+1]] = in_raw_data[:,1][pos[i]]
                attributes[at][pos[-1]:] = in_raw_data[:,1][pos[-1]]

        in_raw_data = in_raw_data[all_att_mask]
        attributes = attributes[all_att_mask]
        if not self.is_init:
            print self.trailing_frame.shape,in_raw_data.shape
            print self.trailing_attributes.shape,attributes.shape
            in_raw_data = np.vstack((self.trailing_frame,in_raw_data))
            attributes = np.concatenate((self.trailing_attributes,attributes))
        
        framebreaks = np.nonzero(in_raw_data[:,0]=='\n')[0]+1

        
        # now split frames
        in_raw_data = np.split(in_raw_data, framebreaks)
        attributes = np.split(attributes, framebreaks)

        # and split according to object types
        obj_list = ['c','s','l']
        obj_vals = dict()
        obj_attrs = dict()
        for i in range(len(in_raw_data)-1):
            
            frame = in_raw_data[i][:-1]
            attrs = attributes[i][:-1]
    
            obj_masks = {o: frame[:,0]==o for o in obj_list}
    
            o='c'
            obj_vals[o] = np.genfromtxt(frame[:,1][obj_masks[o]], dtype='3f32')
            obj_attrs[o] = attrs[obj_masks[o]]
    
            o='s'
            obj_vals[o] = np.genfromtxt(frame[:,1][obj_masks[o]], dtype='6f32')
            obj_attrs[o] = attrs[obj_masks[o]]
    
            o='l'
            obj_vals[o] = np.genfromtxt(frame[:,1][obj_masks[o]], dtype='6f32')
            obj_attrs[o] = attrs[obj_masks[o]]
            self.frames.append(homerFrame.homerFrame(obj_vals, obj_attrs))

        self.trailing_frame = in_raw_data[-1]
        self.trailing_attributes = attributes[-1]
        print self.trailing_frame
        print np.any(self.trailing_frame[:,0]=='\n')
        self.is_init = False
        return True

