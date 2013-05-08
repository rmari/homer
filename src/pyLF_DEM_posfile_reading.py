import math
from string import *
import sys
import copy
import numpy as np


class Pos_Stream:
    
    
    def __init__(self, input_stream):

        self.instream=input_stream
        try:
            self.instream.tell()
            self.is_file=True
        except IOError:
            self.is_file=False # means that we deal with stdin

        
        err_str = ' ERROR LF_DEM_posfile_reading : incorrect input file, '

        # get N
        input_line=self.instream.readline()
        fields=split(input_line)
        if fields[0] != 'np':
            sys.stderr.write(err_str+'no particle number \n')
        else:
            self.N = int(fields[1])

        # get VF
        input_line=self.instream.readline()
        fields=split(input_line)
        if fields[0] != 'VF':
            sys.stderr.write(err_str+'no volume fraction \n')
        else:
            self.phi = float(fields[1])

        # get Lx
        input_line=self.instream.readline()
        fields=split(input_line)
        if fields[0] != 'Lx':
            sys.stderr.write(err_str+'no Lx \n')
        else:
            self.lx = float(fields[1])

        # get Ly
        input_line=self.instream.readline()
        fields=split(input_line)
        if fields[0] != 'Ly':
            sys.stderr.write(err_str+'no Ly \n')
        else:
            self.ly = float(fields[1])

        # get Lz
        input_line=self.instream.readline()
        fields=split(input_line)
        if fields[0] != 'Lz':
            sys.stderr.write(err_str+'no Lz \n')
        else:
            self.lz = float(fields[1])

        if self.Ly() == 0.: # 2d case
            self.V = self.Lx()*self.Lz()
            self.dim=2
        else:               # 3d case
            self.V = self.Lx()*self.Ly()*self.Lz()
            self.dim=3


        self.reset_members()
        
    def __iter__(self):
        return self.positions.__iter__()

    def reset_members(self):
        self.positions=dict()
        self.radius=dict()
        self.GUh_stress=dict()
        self.GUc_stress=dict()
        self.xFc_stress=dict()
        self.old_positions=dict()
        self.time_labels=dict()
        input_line=self.instream.readline()
        fields=split(input_line)
        self.current_time=float(fields[1])
        self.first_time=self.time()

        
    def positions_copy(self):
        return self.positions.copy()

    def positions_deepcopy(self):
        return copy.deepcopy(self.positions)


    def convert_input_pos(self,line):
        values=split(line)

        if(values[0] == '#'):
            self.current_time=float(values[1])
            return 1
        else:
            i=values[0]
#                self.positions[i]=[float(values[j])+0.5*self.cell_size for j in range(1,4)]
            self.positions[i]=np.array([float(values[j]) for j in range(2,5)])
            self.radius[i]=float(values[1])
            self.GUh_stress[i]=float(values[11])
            self.xFc_stress[i]=float(values[12])
            self.GUc_stress[i]=float(values[13])

        return 0
            
# end of convert_input(input_line)



    def get_snapshot(self, verbose=False):

        self.old_positions=self.positions.copy()
        self.positions.clear()
        switch=0
        
        count=0

#        self.time_labels[self.current_time]=self.instream.tell()
        self.time_labels[self.current_time]=-1

#        while True:
 #           line=self.instream.readline()

        for line in self.instream:
            if len(line)==0:
                return False # EOF
            
#            if verbose:
#                print line

            switch+=self.convert_input_pos(line)

            if switch==1:
                break

        if switch==1:
            return True



    def periodize(self,delta):

        xshift = self.time()
        deltax=delta[0]
        deltay=delta[1]
        deltaz=delta[2]


        if deltaz > 0.5*self.cell_size:
            deltaz = deltaz - self.cell_size
            deltax = deltax - xshift
        else:
            if deltaz < -0.5*self.cell_size:
                deltaz = deltaz + self.cell_size
                deltax = deltax + xshift

        if deltay > 0.5*self.cell_size:
            deltay = deltay - self.cell_size
        else:
            if deltay < -0.5*self.cell_size:
                deltay = deltay + self.cell_size

        if deltax > 0.5*self.cell_size:
            deltax = deltax - self.cell_size
        else:
            if deltax < -0.5*self.cell_size:
                deltax = deltax + self.cell_size

        return [deltax, deltay, deltaz]

    def pos(self,i):
        i=str(i)
        return self.positions[i]

    def rad(self,i):
        i=str(i)
        return self.radius[i]

    def periodized_pos(self,i):
        i=str(i)
        return self.periodize(self.positions[i])


    def pos_diff_vec(self,a,b):

        
        deltax=a[0]-b[0]
        deltay=a[1]-b[1]
        deltaz=a[2]-b[2]
        print "pos ", a
        print "pos ", b
        print [deltax, deltay, deltaz]
        [deltax, deltay, deltaz]=self.periodize([deltax, deltay, deltaz])
        print [deltax, deltay, deltaz]
        deltatot= math.sqrt(deltax*deltax+deltay*deltay+deltaz*deltaz)
        return [deltax, deltay, deltaz, deltatot]
    
    def pos_diff(self,i,j):
        i=str(i)
        j=str(j)

        return self.pos_diff_vec(self.positions[i],self.positions[j])


    def displacement(self, i):
        dr=self.pos_diff_vec(self.positions[i],self.old_positions[i])
        return dr

    def non_affine_displacement(self, i):
        dr=self.displacement(i)
        dt=self.time(0)-self.time(-1)
        dr[0]-=self.old_positions[i][1]*dt
        dr[3]=math.sqrt(dr[0]*dr[0]+dr[1]*dr[1]+dr[2]*dr[2])
        return dr

    def instant_relative_velocity(self,i,j):
        i=str(i)
        j=str(j)

        od=self.pos_diff_vec(self.old_positions[i],self.old_positions[j])
        nd=self.pos_diff_vec(self.positions[i],self.positions[j])
        v=[0.,0.,0.,0.]
        dt=self.time()-self.time(-1)
        for s in range(4):
            v[s]=(nd[s]-od[s])/dt
        return v

    def average_relative_velocity(self,i,j,avg_time, previous_position):
        i=str(i)
        j=str(j)
        
        od=self.pos_diff_vec(previous_position[i],previous_position[j])
        nd=self.pos_diff(i,j)
#        print i, j, od, nd

        v=[0.,0.,0.,0.]
        dt=avg_time
        for s in range(4):
            v[s]=(nd[s]-od[s])/dt
        return v
            
#end of pos_diff

    def velocity(self,i):
        
        i=str(i)
        #        print pos_diff_vec(positions[i],old_positions[i]) 
        dt=self.time(0)-self.time(-1)
        dr=self.pos_diff_vec(self.positions[i],self.old_positions[i])
        dxinf=self.positions[i][1]*dt # == gamma_dot*y*dt
        dr[0]-=dxinf
        return [ dr[j]/dt for j in range(4) ]


    def goto_time(self, required_time):
        if self.is_file:
            key_list=sorted(self.time_labels.keys())
            for time in key_list:
                if time >= required_time:
                    self.instream.seek(self.time_labels[time])
                    self.current_time=time
                    return
        else:
            sys.stderr.write("Cannot go to time %s".str(time))
            sys.stderr.write("Input is %s".str(instream))
            sys.exit(1)

    def rewind(self): # go to beginning of the file
        if self.is_file:
            self.instream.seek(0)
            self.reset_members()
            return
        else:
            sys.stderr.write("Cannot rewind")
            sys.stderr.write("Input is %s".str(instream))
            sys.exit(1)


    def time(self, t=0):
        if t==0:
            return self.current_time
        else:
            key_list=sorted(self.time_labels.keys())
            key_index=key_list.index(self.current_time)+t
            return self.time_labels[key_list[key_index]]

    def part_nb(self):
        return len(self.positions)
    
    def np(self):
        return self.N

    def rho(self):
        return self.N/self.V

    def range(self, u=0):
        return range(u,self.part_nb())

    def is_present(self, i):
        return (i in self.positions)

    def dimension(self):
        return self.dim

    
    def Lx(self):
        return self.lx

    def Ly(self):
        return self.ly

    def Lz(self):
        return self.lz
