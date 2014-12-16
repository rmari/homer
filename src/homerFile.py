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
        self.chunksize = 100000000
        self.frames = []
        self.init = True
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
        #        in_raw_data = np.fromregex(self.infile, regexp, [('com', 'S1'), ('val', 'S1000')])

        in_raw_data = np.core.defchararray.partition(np.asarray(self.infile.readlines(self.chunksize), dtype=np.str_), ' ')[:,[0,2]]

        obj_nb = np.shape(in_raw_data)[0]

        attributes = np.zeros(obj_nb, dtype=[('r', ftype), ('@', ftype), ('y', ftype)])
        #attributes = {'r': np.zeros(obj_nb, dtype=ftype), '@': np.zeros(obj_nb, dtype=ftype), 'y': np.ones(obj_nb, dtype=ftype)} # size, color, layer
        all_att_mask = np.ones(obj_nb, dtype=np.bool)
        for at in ['r','@','y']:
            att_mask = in_raw_data[:,0]==at
            all_att_mask -= att_mask
            pos = np.nonzero(att_mask)[0]
            if len(pos)>0:
                for i in range(len(pos)-1):
                    attributes[at][pos[i]:pos[i+1]] = in_raw_data[:,1][pos[i]]
                attributes[at][pos[-1]:] = in_raw_data[:,1][pos[-1]]

        in_raw_data = in_raw_data[all_att_mask]
        attributes = attributes[all_att_mask]

        framebreaks = np.nonzero(in_raw_data[:,0]=='\n')
        # the regexp used to extract data from file considers every framebreak to be 
        # 'com'='\n' and 'val'='whatever comes on the next line'
        # so we have to treat specifically the lines coming right after framebreaks
#        splitcoms = np.asarray(list(np.core.defchararray.split(in_raw_data['val'][framebreaks], maxsplit=1)), dtype='S100')
#        in_raw_data['com'][framebreaks]=splitcoms[:,0]
#        in_raw_data['val'][framebreaks]=splitcoms[:,1]

        # now split frames
        in_raw_data = np.split(in_raw_data, framebreaks[0])
        attributes = np.split(attributes, framebreaks[0])

        # and split according to object types
        obj_list = ['c','s','l']
        obj_vals = dict()
        obj_attrs = dict()
        for i in range(len(in_raw_data)):
            frame = in_raw_data[i]
            attrs = attributes[i]
    
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


#        self.max = np.array([in_raw_data['p1'].max(), in_raw_data['p2'].max(), in_raw_data['p3'].max()])
#        self.min = np.array([in_raw_data['p1'].min(), in_raw_data['p2'].min(), in_raw_data['p3'].min()])

        del in_raw_data
        return True

