#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
#
# This file is part of Honeybee.
#
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> and Saeran Vasanthakumar <saeranv@gmail.com>
# Honeybee is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 3 of the License,
# or (at your option) any later version.
#
# Honeybee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
#
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to divide up a brep (polysurface) representative of a building floor into smaller volumes that roughly correspond to how a generic EnergyPlus model should be zoned.
This zoning divide up each floor into a core and perimeter zones, which helps account for the different microclimates you would get on each of the different orientations of a building.
Note: This component is intended mainly for convex geometry. Most concave geometries will fail, and any shapes with holes in them will fail. You should therefore prepare the
massing of your building by dividing it into convex volumes before using this component.
_
If you have a single mass representing two towers off of a podium, the two towers are not a continuous mass and you should therefore send each tower and the podium in as a separate Brep into this component.
Core and perimeter zoneing should work for almost all masses where all walls are planar.
While this component can usually get you the most of the way there, it is still recommended that you bake the output and check the geometry in Rhino before turning the breps into HBZones.
_
The assumption about an E+ zone is that the air is well mixed and all at the same temperature.
Therefore, it is usually customary to break up a building depending on the areas where you would expect different building microclimates to exist.
This includes breaking up the building into floors (since each floor can have a different microclimate) and breaking up each floor into a core zone and perimeter zones (since each side of the buidling gets a different amount of solar gains and losses/gains through the envelope).
This component helps break up building masses in such a manner.
-
Provided by Honeybee 0.0.64

    Args:
        _bldgFloors: A Closed brep or list of closed breps representing building floors. In this WIP only convex geometries and very simple concave geometries will succeed. You should prepare the massing of your building by dividing it into convex volumes before using this component. You can use the Honeybee_SplitBuildingMass2Floors to generate floors from a building mass.
        _perimeterZoneDepth: A number for perimeter depths in Rhino model units that will be used to divide up each floor of the building into core and perimeter zones.
    Returns:
        readMe!: ...
        splitBldgZones: A series of breps that correspond to the recommended means of breaking up building geometry into zones for energy simulations. All zones for each floor will have its own list.

"""


ghenv.Component.Name = 'Honeybee_SplitFloor2ThermalZones'
ghenv.Component.NickName = 'Split2Zone'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import rhinoscriptsyntax as rs

from Rhino import RhinoApp
import heapq
import math
import copy

tolerance = sc.doc.ModelAbsoluteTolerance

def checkTheInputs():
    if len(_bldgFloors) != 0 and _bldgFloors[0] != None:
        #Check for guid
        for i,b in enumerate(_bldgFloors):
            if type(b)==type(rs.AddPoint(0,0,0)):
                _bldgFloors[i] = rs.coercebrep(b)

        brepSolid = []
        for brep in _bldgFloors:
            if brep.IsSolid == True:
                brepSolid.append(1)
            else:
                warning = "Building floors must be closed solids!"
                print warning
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        if sum(brepSolid) == len(_bldgFloors):
            checkData1 = True

    else:
        checkData1 = False
        print "Connect closed solid building floors to split them up into zones."

    if _perimeterZoneDepth != []:
        checkData2 = True
    else:
        checkData2 = False
        print "A value must be conneted for _perimeterZoneDepth in order to run."

    if checkData1 == True and checkData2 == True:
        checkData = True
    else: checkData = False

    return checkData


def is_near_zero(num,eps=1E-10):
    return abs(float(num)) < eps

class DoubleLinkedList(object):
    #Creates empty doubly linked list
    def __init__(self):
        self.size = 0
        self.head = None
        self.tail = None
    def __str__(self):
        L = []
        curr_node = self.head
        for i in xrange(self.size):
            L.append(curr_node.data)
            curr_node = curr_node.next
        return str(L)
    def IsEmpty(self):
        return self.size == 0
    def __len__(self):
        return self.size
    def reset_size(self):
        curr_node = self.head
        self.size = 0
        while curr_node != self.tail:
            self.size += 1
            curr_node = curr_node.next
        self.size += 1
    def append(self,data):
        new_node = DLLNode(data)
        if self.head == None:
            self.head = self.tail = new_node
        else:
            #Add new node to front of list
            new_node.prev = self.tail
            new_node.next = None
            self.tail.next = new_node
            self.tail = new_node
        #Now complete circle
        self.head.prev = self.tail
        self.tail.next = self.head
        self.size += 1
    def insert_node(self,new_node,prev_node):
        #Modify the list of active vertices/nodes
        #Swap node_A, node_B w/ V in LAV
        next_node = prev_node.next

        prev_node.next = new_node
        next_node.prev = new_node
        new_node.prev = prev_node
        new_node.next = next_node

        self.size += 1

        #change if prev/next node were head/tail
        if self.head == new_node.next:
            self.tail = new_node
        elif self.tail == new_node.prev:
            self.tail = new_node

    def remove_node(self,old_node):
        #change if prev/next node were head/tail
        if self.head == old_node:
            self.head = old_node.next
        elif self.tail == old_node:
            self.tail = old_node.prev

        next_node = old_node.next
        prev_node = old_node.prev

        next_node.prev = prev_node
        prev_node.next = next_node

        #Detach links from node
        old_node.next = None
        old_node.prev = None

        self.size -= 1

    def __getitem__(self, i):
        #Worst case O(n) time. Don't use if not neccessary
        curr_node = self.head
        for j in xrange(self.size):
            if i == j:
                return curr_node
            curr_node = curr_node.next
        return None
    def get_node_index(self,node_ref):
        #Worst case O(n) time. Don't use if not neccessary
        curr_node = self.head
        for j in xrange(self.size):
            if curr_node is node_ref:
                return j
            curr_node = curr_node.next
        return None
class DLLNode(object):
    def __init__(self,data):
        self.data = data
        self.next = None
        self.prev = None
    def __str__(self):
        return str(self.data)
class Vertex(object):
    def __init__(self,vertex,edge_prev=None,edge_next=None):
        self.vertex = vertex
        self.edge_prev = edge_prev
        self.edge_next = edge_next
        self.bisector_ray = None
        self.is_reflex = False
        self.is_processed = False
    def __str__(self):
        return str(self.vertex)
class Event(object):
    def __init__(self,int_vertex,node_A,node_B,length2edge,event_type="event",LAV=None):
        self.int_vertex = int_vertex
        self.node_A = node_A
        self.node_B = node_B
        self.event_type = event_type
        self.length2edge = length2edge
        self.LAV = LAV
        self.opposite_edge = None
    def __str__(self):
        return str(self.int_vertex)


#Adjacency list class make into own library
class _AdjGraphNode(object):
    #This is a bare bones private class
    def __init__(self,key,value,id,is_out_edge=False,adj_lst=None):
        #adj_lst: ['key1', 'key2' ....  'keyn']
        self.key = key
        self.id = id
        self.value = value
        self.is_out_edge = is_out_edge
        self.adj_lst = adj_lst if adj_lst!=None else []
    def num_neighbor(self):
        return len(self.adj_lst)
    def __repr__(self):
        return "id: " + str(self.id)
class AdjGraph(object):
    #Graph as adjacency list
    #Good ref for adj graphs: http://interactivepython.org/runestone/static/pythonds/Graphs/Implementation.html
    #adj_graph is a dict like this:
    #{key1: _AdjGraphNode.adj_lst = [2,4],
    # key2: _AdjGraphNode.adj_lst = [3,4],
    # key3: _AdjGraphNode.adj_lst = [4],
    # key4: _AdjGraphNode.adj_lst = [1]}
    #
    # 1<--->4
    # |  /  |
    # 2---->3
    #
    def __init__(self,adj_graph=None):
        self.adj_graph = adj_graph if adj_graph != None else {}
        self.num_node = len(self.adj_graph.keys())
    def vector2hash(self,vector,tol=4):
        #Tolerance set to
        myhash = "("
        for i in xrange(len(vector)):
            coordinate = vector[i]
            myhash += str(round(coordinate,tol))
            if i < len(vector)-1:
                myhash += ","
        myhash += ")"
        return myhash
    def add_node(self,key,value,is_out_edge=False):
        #_AdjGraphNode is a private class
        #Instantiate _AdjGraphNode, we creates key = num_node
        if key in self.adj_graph:
            n = self.adj_graph[key]
            print n.id, ' key already exists in adj_graph!'
            return self.adj_graph[key]
        id = len(self.adj_graph.keys())
        adj_graph_node = _AdjGraphNode(key,value,id,is_out_edge)
        #Now add it to the adj_graph
        self.adj_graph[key] = adj_graph_node
        self.num_node += 1
        return adj_graph_node
    def __getitem__(self,k):
        if k in self.adj_graph:
            return self.adj_graph[k]
        else:
            return None
    def keylst_2_nodelst(self,keylst):
        return map(lambda k: self.adj_graph[k],keylst)
    def add_directed_edge(self,key,key2add):
        #This function will add existing node key to adjacency list of
        #another node indicating a directed edge
        if key in self.adj_graph and key2add in self.adj_graph:
            node = self.adj_graph[key]
            if key2add in node.adj_lst or key2add == key:
                print 'key2add already in adj list or self-intersection'
                return None
            node.adj_lst.append(key2add)
        else:
            print 'key not in adj graph'
    def recurse_ccw(self,refn,nextn,lok,cycle,count):
        def get_ccw_angle(prev_dir,next_dir):
            #Input prev_dir vector and next_dir vector in CCW ordering
            #Output CCW angle between them in radians

            #Reverse prev_dir order for angle checking
            #We create a new vector b/c must be ccw order for reflex check
            reverse_prev_dir = prev_dir * -1.0
            #Use the dot product to find the angle
            dotprod = rc.Geometry.Vector3d.Multiply(reverse_prev_dir,next_dir)
            try:
                cos_angle = dotprod/(prev_dir.Length * next_dir.Length)
            except ZeroDivisionError:
                print 'ZeroDivisionError'
                cos_angle = 0.0

            # Get angle from dot product
            # This will be between 0 and pi
            # b/c -1 < cos theta < 1
            dotrad = math.acos(cos_angle)

            #Use 2d cross product (axby - bxay) to see if next_vector is right/left
            #This requires ccw ordering of vectors
            #If cross is positive (for ccw ordering) then next_vector is to left (inner)
            #If cross is negative (for ccw ordering) then next_vector is to right (outer)
            #If cross is equal then zero vector, then vectors are colinear. Assume inner.

            cross_z_sign = prev_dir[0] * next_dir[1] - prev_dir[1] * next_dir[0]
            #print 'deg: ', round(math.degrees(dotrad),2)
            #If reflex we must subtract 2pi from it to get reflex angle
            if cross_z_sign < 0.0:
                dotrad = 2*math.pi - dotrad
            return dotrad

        if True: pass #weird code folding glitch neccessitatest this
        #Input list of keys
        #output key with most ccw
        #Base case
        #print 'startid, chkid:', cycle[0].id, nextn.id
        cycle.append(nextn)
        cycle_id_lst = map(lambda n: n.id, cycle)
        if nextn.id == cycle_id_lst[0] or count > 20:
            return cycle

        #print 'cycle', cycle_id_lst

        #reference direction vector
        ref_edge_dir =  nextn.value - refn.value

        min_rad = float("Inf")
        min_node = None

        for i in xrange(len(lok)):
            k = lok[i]
            n2chk = self.adj_graph[k]
            #Make sure we don't backtrack
            if n2chk.id == cycle_id_lst[-2]:
                continue
            chk_edge_dir = n2chk.value - nextn.value
            #print 'chkccw', refn.id, '--', nextn.id, '--->', n2chk.id
            rad = get_ccw_angle(ref_edge_dir,chk_edge_dir)
            if rad < min_rad:
                min_rad = rad
                min_node = n2chk
            #print '---'
        #print 'min is', n2chk.id,':', round(math.degrees(rad),2)
        #print '---'
        alok = min_node.adj_lst

        return self.recurse_ccw(nextn,min_node,alok,cycle,count+1)
    def find_most_ccw_cycle(self):
        #def helper_most_ccw(lok):

        #Input adjacency graph
        #Output loc: listof (listof (listof pts in closed cycle))
        LOC = []
        keylst = self.get_sorted_keylst()
        for i in xrange(len(keylst)):
            key = keylst[i]
            root_node = self.adj_graph[key]
            if not root_node.is_out_edge:
                continue

            #Identify the next node on outer edge
            #b/c outer edge vertexes are placed first in adj graph
            #worst complexity <= O(n)
            for i in xrange(root_node.num_neighbor()):
                adj_key = root_node.adj_lst[i]
                neighbor = self.adj_graph[adj_key]
                if neighbor.is_out_edge:
                    next_node = neighbor
                    break

            #Now we recursively check most ccw
            n_adj_lst = next_node.adj_lst
            cycle = [root_node]
            try:
                cycle = self.recurse_ccw(root_node,next_node,n_adj_lst,cycle,0)
            except:
                pass
            #print '-------\n-----FINISHED CYCLE\n', cycle, '---\---\n'
            LOC.append(cycle)
        #print '-'
        return LOC
    def get_sorted_keylst(self):
        valuelst = self.adj_graph.values()
        valuelst.sort(key=lambda v: v.id)
        keylst = map(lambda v: v.key,valuelst)
        return keylst
    def is_near_zero(self,num,eps=1E-10):
        return abs(float(num)) < eps
    def __repr__(self):
        keylst = self.get_sorted_keylst()
        strgraph = ""
        for i in xrange(len(keylst)):
            key = keylst[i]
            node = self.adj_graph[key]
            strgraph += str(node.id) + ': '
            strgraph += str(map(lambda k: self.adj_graph[k].id,node.adj_lst))
            strgraph += '\n'
        return strgraph
    def __contains__(self,key):
        return self.adj_graph.has_key(key)

class Shape:
    """
    Temporary class for WIP!
    """
    def __init__(self,geom,flrcrv=None):
        def get_dim_bbox(b):
            ## counterclockwise, start @ bottom SW
            #      n_wt
            #      -----
            #      |   |
            # w_ht |   | e_ht = y_dist
            #      |   |
            #      -----
            #     s_wt = x_dist
            """    self.s_wt,self.e_ht,self.n_wt,self.w_ht """
            return b[:2],b[1:3],b[2:4],[b[3],b[0]]
        self.geom = geom
        self.bottom_crv = flrcrv
        self.base_matrix = None
        self.cplane = None
        self.normal = rc.Geometry.Vector3d(0,0,1)
        self.bbpts = self.get_boundingbox(self.geom,self.cplane)
        self.s_wt,self.e_ht,self.n_wt,self.w_ht = get_dim_bbox(self.bbpts)
        self.ew_vector = self.n_wt[1]-self.n_wt[0]
        self.ns_vector = self.e_ht[1]-self.e_ht[0]
        """
        print 'check ew'
        print self.primary_axis_vector.IsParallelTo(self.ew_vector)
        print self.primary_axis_vector.IsPerpendicularTo(self.ew_vector)
        print ''
        """
        self.set_base_matrix()
        # x,y,z distances
        self.x_dist = float(rs.Distance(self.s_wt[0],self.s_wt[1]))
        self.y_dist = float(rs.Distance(self.e_ht[0],self.e_ht[1]))
        self.cpt = rc.Geometry.AreaMassProperties.Compute(self.bottom_crv).Centroid

        try:
            if self.cplane == None:
                self.cplane = self.get_cplane_advanced(self.geom)
            self.primary_axis_vector = self.cplane.YAxis
        except Exception as e:
            print str(e)##sys.exc_traceback.tb_lineno
            self.cplane, self.primary_axis_vector = None, None
        self.ht = float(self.bbpts[4][2])
    def is_near_zero(self,num,eps=1E-10):
        return abs(float(num)) < eps
    def get_boundingbox(self,geom_,cplane_):
        def check_bbpts(b):
            ## check if 3d shape and if first 4 pts at bottom
            if b[0][2] > b[4][2]:
                b_ = b[4:] + b[:4]
                b = b_
            return b
        try:
            bbpts_ = rs.BoundingBox(geom_,cplane_)
            return check_bbpts(bbpts_)
        except Exception as e:
            print "Error @ get_boundingbox"
            #print str(e)#sys.exc_traceback.tb_lineno
    def get_shape_axis(self,crv=None):
        def helper_group_parallel(AL):
            ## Identifies parallel lines and groups them
            lop = []
            CULLDICT = {}
            for i,v in enumerate(AL):
                refdist = rs.Distance(v[0],v[1])
                refdir = v[1] - v[0]
                power_lst = []
                if i < len(AL)-1 and not CULLDICT.has_key(refdist):
                    power_lst.append(refdist)
                    AL_ = AL[i+1:]
                    for v_ in AL_:
                        currdist = rs.Distance(v_[0],v_[1])
                        currdir = v_[1] - v_[0]
                        if currdir.IsParallelTo(refdir) != 0 and not CULLDICT.has_key(currdist):
                            power_lst.append(currdist)
                            CULLDICT[currdist] = True
                if power_lst != []:
                    power_lst.sort(reverse=True)
                    power_num = reduce(lambda x,y: x+y,power_lst)
                else:
                    power_num = 0.
                lop.append(power_num)
            return lop

        ### Purpose: Input 2d planar curve
        ### and return list of vector axis based
        ### on prominence
        ##debug = sc.sticky['#debug']
        try:
            if crv==None:
                crv = self.bottom_crv
            axis_matrix = self.set_base_matrix(crv)
            if axis_matrix != []:
                axis_power_lst = helper_group_parallel(axis_matrix)
                pa_index = axis_power_lst.index(max(axis_power_lst))
                pa_vector = axis_matrix[pa_index][1]-axis_matrix[pa_index][0]
            else:
                #degenerate crv
                pa_vector = None
            self.primary_axis_vector = pa_vector
            return self.primary_axis_vector
        except Exception as e:
            print "Error @ shape.get_shape_axis"
            print str(e)#sys.exc_traceback.tb_lineno
    def get_cplane_advanced(self,g):
        def helper_define_axis_pts(primary_vec):
            ##(origin,x,y)
            o_pt_ = rc.Geometry.Point3d(0,0,0)
            y_pt_ = primary_vec
            z_pt_ = rc.Geometry.Vector3d(0,0,1)
            ## construct x_pt_ using the communitive property of crossproduct
            x_pt_ = rc.Geometry.Vector3d.CrossProduct(y_pt_,z_pt_)
            return o_pt_,x_pt_,y_pt_
        #try:
        if True:
            if self.is_guid(g):
                brep = rs.coercebrep(g)
            else: brep = g
            ##debug = sc.sticky['#debug']
            ## Get primary axis
            nc = self.bottom_crv.ToNurbsCurve()
            planar_pts = [nc.Points[i].Location for i in xrange(nc.Points.Count)]
            primary_axis_vector = self.get_shape_axis(self.bottom_crv)
            if primary_axis_vector:
                o_pt,x_pt,y_pt = helper_define_axis_pts(primary_axis_vector)
            else:
                #degenerate shape
                o_pt = rc.Geometry.Point3d(0,0,0)
                x_pt = rc.Geometry.Point3d(1,0,0)
                y_pt = rc.Geometry.Point3d(0,1,0)
            cplane = rc.Geometry.Plane(o_pt,x_pt,y_pt)
            return cplane
        #except Exception as e:
        #    print "Error @ shape.get_cplane_advanced"
        #    print str(e)#sys.exc_traceback.tb_lineno
    def move_geom(self,guidobj,dir_vector,copy=False):
        #Moves a geometry
        #Note, you MUST convert to guid and convert back to rc geom
        xf = rc.Geometry.Transform.Translation(dir_vector)
        xform = rs.coercexform(xf, True)
        guidid = rs.coerceguid(guidobj, False)
        guidid = sc.doc.Objects.Transform(guidid, xform, not copy)
        return guidid
    def get_long_short_axis(self):
        if (self.x_dist > self.y_dist):
            long_dist,short_dist = self.x_dist,self.y_dist
            long_axis,short_axis = 'EW','NS'
        else:
            long_dist,short_dist = self.y_dist,self.x_dist
            long_axis,short_axis = 'NS','EW'
        return long_axis,long_dist,short_axis,short_dist
    def get_bottom(self,g,refpt,tol=1.0,bottomref=0.0):
        ## Extract curves from brep according to input cpt lvl
        ##debug = sc.sticky['#debug']
        IsAtGroundPlane = False
        if abs(refpt[2]-bottomref) < 0.01:
            #print 'ground ref at:', refpt[2]
            refpt.Z += 1.0
            IsAtGroundPlane = True
        if g == None: g = self.geom
            ##debug.append(g)
        try:
            if g == None: g = self.geom
            #print g
            if self.is_guid(refpt): refpt = rs.coerce3dpoint(refpt)
            if self.is_guid(g): g = rs.coercebrep(g)
            plane = rc.Geometry.Plane(refpt,rc.Geometry.Vector3d(0,0,1))

            crv = g.CreateContourCurves(g,plane)[0]
            if IsAtGroundPlane==True:
                crv = sc.doc.Objects.AddCurve(crv)
                move_crv = self.move_geom(crv,rc.Geometry.Vector3d(0,0,-1.))
                crv = rs.coercecurve(move_crv)
            return crv
        except Exception as e:
            #print 'chk', refpt.Z
            ##debug.append(refpt)
            print "Error @ shape.get_bottom"
            print str(e)#sys.exc_traceback.tb_lineno
    def is_guid(self,geom):
            return type(rs.AddPoint(0,0,0)) == type(geom)
    def set_base_matrix(self,crv=None):
        ## Breaks up geometry into:
        ##[ [[vector1a,vector1b],  // line 1
        ##   [vector2a,vector2b],  // line 2
        ##          ....
        ##   [vectorna, vectornb]] // line n
        ## topological ordering preserved
        ## direction counterclockwise
        ## but can start from anywhere!
        ##debug = sc.sticky['#debug']

        if self.base_matrix == None:
            if crv == None:
                if self.bottom_crv == None:
                    bbrefpt = self.get_boundingbox(self.geom,None)[0]
                    self.bottom_crv = self.get_bottom(self.geom,bbrefpt,bottomref=bbrefpt[2])
                crv = self.bottom_crv

            segments = crv.DuplicateSegments()
            matrix = []
            for i in xrange(len(segments)):
                segment = segments[i]
                nc = segment.ToNurbsCurve()
                end_pts = [nc.Points[i_].Location for i_ in xrange(nc.Points.Count)]
                matrix.append(end_pts)
            self.base_matrix = matrix
        return self.base_matrix
    def check_colinear_pt(self,crv,testpt,tol=0.01):
        ## May need to swap with own method
        dist = ghcomp.CurveClosestPoint(testpt,crv)[2]
        IsColinear = True if abs(dist-0.)<tol else False
        return IsColinear
    def intersect_infinite_lines(self,line1,line2):
        #Input line1 and line2
        #where: line: (startpt,endpt)
        #and startpt and endpt are rc.Geometry.Point3d
        #Compute intersection of infinite lines
        #Return point of intersection
        ##debug = sc.sticky['#debug']
        intersect_pt = None
        #Convert to rhino common geometry obj
        line1 = rc.Geometry.Line(line1[0],line1[1])
        line2 = rc.Geometry.Line(line2[0],line2[1])

        int_exist,a,b = rc.Geometry.Intersect.Intersection.LineLine(line1,line2,0.001,False)
        if int_exist:
            intersect_pt = line2.PointAt(b)
        return intersect_pt
    def planar_intersect_ray_with_line(self,base_vector,direction_vector,linept1,linept2,refz=0.0):
        #Input: ray (basevector and dirvector), line (two pts)
        #Output: intersection point or else False
        #Will only take place in 2d at defined z ht
        #This function took me half a day to understand!

        r0 = base_vector
        r1 = direction_vector
        a = linept1
        b = linept2

        #For ray: r0,r1; and line: a,b
        #parametric form of ray: r0 + t_1*r1 = pt
        #parametric form of line: a + t_2*b = pt

        #ray: r0 + t * d
        #r0: base point
        #d: direction vector
        #t = scalar parameter t, where 0 <= t < infinity
        #if line segment, then 0 <= t <= 1 is the parametric form of a line.

        #Solve for r0 + t_1*r1 = a + t_2*b; two unknowns t_1, t_2
        #This can result in a lot of algebra, but essentially can
        #simplify to the vector operations below
        #Ref: http://stackoverflow.com/questions/14307158/how-do-you-check-for-intersection-between-a-line-segment-and-a-line-ray-emanatin

        ## This needs to have push/pop/transformation matrix
        ## so that it can work outside of z-axis
        def helper_flatten_z(lst,z):
            return rc.Geometry.Vector3d(lst[0],lst[1],z)

        ##debug = sc.sticky['#debug']
        z = 0.0 #flatten then unflatten
        a = helper_flatten_z(a,z)
        b = helper_flatten_z(b,z)

        #Correct the ordering of the line segment
        IsCCW = self.check_vertex_order(refline=[a,b])
        if not IsCCW:
            a,b = b,a

        r0 = helper_flatten_z(r0,z)
        r1 = helper_flatten_z(r1,z)
        ray_dir = r0+(r1*5) - r0#(r0+r1) - r0
        ##debug.append(rs.AddCurve([r0,ray_dir+r0]))
        ##debug.append(b)

        ortho = rc.Geometry.Vector3d(ray_dir.Y*-1.,ray_dir.X,z)
        aToO = r0 - a
        aToB = b - a
        point_intersect = False
        denominator = aToB * ortho
        #Check if zero: Then cos(90) = 0, or ray normal and segment
        #perpendicular therefore no intersection

        if not self.is_near_zero(denominator):
            cross_prod = rc.Geometry.Vector3d.CrossProduct(aToB,aToO)
            dot_prod = ortho * aToO
            t_1 = cross_prod.Length / denominator
            t_2 = dot_prod / denominator

            #t_1 = abs(t_1)
            #t_2 = abs(t_2)
            if (t_2 >= 0. and t_2 <= 1.) and t_1 >= 0.: #t_1 can go to infinity
                #print 't1', t_1
                #print 't2', t_2
                #print '--'
                ##debug.append(rs.AddCurve([r0,ray_dir+r0]))
                #Collision detected
                ix,iy = r0.X + (t_1 * ray_dir.X), r0.Y + (t_1 * ray_dir.Y)
                #print t_1
                point_intersect = rc.Geometry.Vector3d(ix,iy,refz)
        #if point_intersect:
            ##debug.append(point_intersect)
            ##debug.append(rs.AddCurve([r0,point_intersect]))
        return point_intersect
    def intersect_ray_with_line(self,base_vector,direction_vector,linept1,linept2,refz=None):
        #Input: ray (basevector and dirvector), line (two pts)
        #Output: intersection point or else False
        #Same as above but with rhinocommon library

        vertical_tolerance = -5.0
        r0 = base_vector
        r1 = direction_vector
        a = linept1
        b = linept2
        a.Z = a.Z + vertical_tolerance
        b.Z = b.Z + vertical_tolerance
        if refz==None: refz = self.ht
        refz -= vertical_tolerance
        ##debug = sc.sticky['#debug']

        #extrude as surface to check int
        upnormal = self.normal * refz
        upnormalcrv = rc.Geometry.Curve.CreateControlPointCurve([self.cpt,self.cpt + upnormal])
        reflinepath = rc.Geometry.Curve.CreateControlPointCurve([a,b])
        srf2int = rc.Geometry.SumSurface.Create(reflinepath,upnormalcrv)
        ray = rc.Geometry.Ray3d(r0,r1)
        point_intersect_lst = rc.Geometry.Intersect.Intersection.RayShoot(ray,[srf2int],1)
        if point_intersect_lst:
            point_intersect_lst = list(point_intersect_lst)
            ##debug.extend(point_intersect_lst)
            ##debug.append(self.cpt)
        return point_intersect_lst
    def intersect_ray_to_infinite_line(self,raypt,raydir,line):
        #Input: Ray(raystartpt, ray_dir_vector)
        #and Line (startpt, endpt)
        #Output intersection in direction of ray

        ray_line = (raypt,rc.Geometry.Point3d(raypt + raydir))
        int_pt = self.intersect_infinite_lines(ray_line,line)

        #Check validity of int_pt
        if not int_pt:
            return None
        #Identify if intpt same dir as ray dir
        ref_dir = raydir
        int_dir = rc.Geometry.Vector3d(int_pt-raypt)

        #If int_pt = start_pt then intpt "behind" vertex
        if self.is_near_zero(int_dir.Length):
            return None

        dotprod = ref_dir * int_dir
        cos_theta = dotprod/(ref_dir.Length * int_dir.Length)
        #if cos theta = 1 is parellel b/c cos(0) = 1
        if cos_theta < 0.0:
            return None

        return int_pt
    def extend_ray_to_line(self,chk_ray,lineref):
        #ray: (ray_origin (pt), ray_dir (vector))
        #line: control point curve
        #Output: line that is intersected
        chk_line = rc.Geometry.Curve.CreateControlPointCurve([chk_ray[0],chk_ray[0]+chk_ray[1]*2.],0)
        chk_line.SetStartPoint(chk_ray[0])
        #Checking t parameter: 0.0 = ray_origin, 1.0 = ray_endpt
        #b,t = chk_line.ClosestPoint(chk_ray[0],0.001)
        #print t < chk_line.Domain.Mid
        chk_line_end = rc.Geometry.CurveEnd.End
        int_line = chk_line.ExtendByLine(chk_line_end,[lineref])
        return int_line
    def get_inner_angle(self,v_prev,v_next,anglerad):
        #Input: v2,v1 as direction vectors facing away from ref pt, and angle to check
        # True if cross is positive
        # False if negative or zero
        #Ref: http://stackoverflow.com/questions/20252845/best-algorithm-for-detecting-interior-and-exterior-angles-of-an-arbitrary-shape
        IsPositive = v_next[0] * v_prev[1] > v_prev[0] * v_next[1]
        if not IsPositive:
            anglerad = 2.*math.pi - anglerad
        return anglerad
    def convert_shape_to_circular_double_linked_list(self):

        LAV = DoubleLinkedList()
        #Add all vertices and incident edges from polygon
        for i in xrange(len(self.base_matrix)):
            v = self.base_matrix[i][0]
            i -= 1
            #Edge data is stable. We don't relink it in LAV
            edge_prev = self.base_matrix[i]
            edge_next = self.base_matrix[i+1]
            vrt = Vertex(v,edge_prev,edge_next)
            LAV.append(vrt)
        return LAV
    def compute_interior_bisector_vector(self,LAV,angle_index=False):
        #Computes interior bisector ray for all vertices in LAV
        #If single_angle_index == index, will only check that vertice
        ##debug = sc.sticky['#debug']
        for i in xrange(LAV.size):
            curr_node = LAV[i]
            if type(angle_index)==type(1) and not self.is_near_zero(i-angle_index):
                continue

            edge_prev = curr_node.data.edge_prev
            edge_next = curr_node.data.edge_next

            # Get two vectors pointing AWAY from the curr_vertex
            # i.e <--- v --->
            dir_prev = edge_prev[0]-edge_prev[1]
            dir_next = edge_next[1]-edge_next[0]
            dir_prev.Unitize()
            dir_next.Unitize()

            # Get angle / Make this own function?
            dotprod = rc.Geometry.Vector3d.Multiply(dir_next,dir_prev)
            cos_angle = dotprod/(dir_next.Length * dir_prev.Length)
            dotrad = math.acos(cos_angle)

            inrad = self.get_inner_angle(dir_prev,dir_next,dotrad)

            if inrad > math.pi:
                curr_node.data.is_reflex = True
                ##debug.append(curr_node.data.vertex)

            #print 'deg:', round(math.degrees(inrad),2)
            #print 'is reflex:', curr_node.data.is_reflex

            #Flip the cross prod if dotprod gave outer angle
            if self.is_near_zero(abs(inrad - dotrad)):
                crossprod = rc.Geometry.Vector3d.CrossProduct(dir_prev,dir_next)
            else:
                crossprod = rc.Geometry.Vector3d.CrossProduct(dir_next,dir_prev)

            #Rotate next point CCW by inner_rad
            #We could also use unit vector addition to get biesctor
            dir_next.Rotate(-inrad/2.,crossprod)

            #Create bisector ray
            ray_origin = curr_node.data.vertex
            ray_dir = dir_next
            #Create ray tuple
            curr_node.data.bisector_ray = (ray_origin,ray_dir)

            xchk = 178.000124531
            xcor = curr_node.data.vertex[0]
            if True==False:#Sangle_index == 0 and i == 0: #and self.is_near_zero(abs(xcor-xchk),1):
                print curr_node.data.vertex[0]
                ##debug.append(curr_node.data.vertex)
                ptlst = [ray_origin,ray_origin+ray_dir*15.0]
                ##debug.append(rc.Geometry.Curve.CreateControlPointCurve(ptlst))
                ##debug.append(rc.Geometry.Curve.CreateControlPointCurve(edge_prev))
                ##debug.append(rc.Geometry.Curve.CreateControlPointCurve(edge_next))

        return LAV
    def find_opposite_edge_from_node(self,curr_node_,SLAV_,is_LOV=True,edge_event_=None,cchk=None):
        def distline2pt(v,w,p):
            ##This algorithm returns the minimum distance between
            ##line segment vw and point p
            ##Modified from http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
            ##This is the explaination from stackoverflow for ref:
            ##Consider the line extending the segment, parameterized as v + t (w - v).
            ##We find projection of point p onto the line.
            ##It falls where t = [(p-v) . (w-v)] / |w-v|^2
            ##We clamp t from [0,1] to handle points outside the segment vw.

            ##Convert to rc geometry
            v = rc.Geometry.Vector3d(v)
            w = rc.Geometry.Vector3d(w)
            p = rc.Geometry.Vector3d(p)

            ##Create dir vectors for line and point
            wv = w-v
            pv = p-v

            ##Calculate |w-v|^2 w/o costly sqrt
            lsq = wv.SquareLength
            # Check for zero line segment case: v == w
            if self.is_near_zero(lsq):
                return pv.Length

            ##ProjectionPVonWV = (w-v)/|w-v| * (w-v)/|w-v| * (p-v)
            ##simplfiied = projpv = (w-v) * ((p-v) * (w-v))/|w-v|^2
            ##Then: projpv - p == perpendicular line

            ##clamp_to_line: ((p-v) * (w-v))/|w-v|^2
            ##(w-v): wv
            ##projpv = clamp_to_line * wv
            clamp_to_line = (pv * wv)/lsq

            ##This is to handle points outside line segment. They will have
            ##obtuse angle so costheta < 0. in that case will clamp_to_line factor == 0.
            ##therefore if obtuse, clamp_to_line turns projpv into a zero vector and
            ##and will return (non perpendicular) distance from point v to p.
            clamp_to_line = max(0., min(1.,clamp_to_line))
            projpv = clamp_to_line * wv

            ##Instead of simply subtracting projpv-p, we first add it to v
            ##and then subtract it from p
            ##This is so that if p is outside of line segment, then projpv = 0 vector, so
            ##v - p will be our minimum distance.
            perpvector = (v + projpv) - p

            ##Return values
            perpgeom = rs.AddLine(projpv,p)
            perpline = rs.AddLine(v,w)
            perppt = rc.Geometry.Point3d(p)
            return perpvector.Length, (perpgeom,perpline,perppt)
        #Split event: when interior vertex hits opposite edge, splitting
        #polygon in two
        #Compute point B, where a 'split event' will occur
        #Returns opposite edge, B, and node_A if exists
        #print 'is_reflex', curr_node_.data.is_reflex
        #debug = sc.sticky["#debug"]
        raypt = curr_node_.data.bisector_ray[0]
        raydir = curr_node_.data.bisector_ray[1]

        ##debug.append(vertex_bisector_line[1])
        #Loop through LAV original edges
        min_dist = float("Inf")
        min_candidate_B = None
        min_edge_line = None
        min_node_A = None
        #print '\n\ncurrverte', curr_node_.data.vertex[0]
        debugisfirst = False
        #if self.is_near_zero(abs(curr_node_.data.vertex[0] - 434.),1.0):
        #    debugisfirst = True
        #if not debugisfirst:
        #    #debug.append(curr_node_.data.vertex)
        #print 'checking reflex ----------'
        #if edge_event_ != None:
        #    print 'This is second round LAV'#, edge_event_.opposite_edge
        #Botffy uses original edges (LOV) to calculate split events
        #But Felzel and Obdzel seem to suggest use active SLAV...

        for i in xrange(len(SLAV_)):
            LAV_ = SLAV_[i]
            for j in xrange(LAV_.size):
                #print '-\nj', j
                orig_node_ = LAV_[j]

                edge_line = [orig_node_.data.vertex,orig_node_.data.edge_next[1]]
                if edge_event_!= None:
                    opposite_edge = edge_event_.opposite_edge
                    orig_oppo_vec = opposite_edge[1] - opposite_edge[0]
                    orig_oppo_vec.Unitize()

                    edge_line_next_vec = orig_node_.data.edge_next[1] - orig_node_.data.vertex
                    edge_line_prev_vec = orig_node_.data.vertex - orig_node_.data.edge_prev[0]
                    edge_line_next_vec.Unitize()
                    edge_line_prev_vec.Unitize()
                    #print 'is parrallel', orig_oppo_vec.IsParallelTo(edge_line_next_vec,0.01)
                    #print 'is parrallel', orig_oppo_vec.IsParallelTo(edge_line_prev_vec, 0.01)

                    if orig_oppo_vec == edge_line_next_vec and edge_event_.opposite_edge[0] == orig_node_.data.vertex:
                        #print 'is next vec'
                        edge_line = [orig_node_.data.vertex, orig_node_.data.edge_next[1]]# orig_node_.next.data.vertex]#
                    elif orig_oppo_vec == edge_line_prev_vec and edge_event_.opposite_edge[0] == orig_node_.data.edge_prev[0]:
                        #print 'is prev vec'
                        edge_line = [orig_node_.data.edge_prev[0], orig_node_.data.vertex]#[orig_node_.prev.data.vertex,orig_node_.data.vertex]#
                    else:
                        #print 'cant find match'
                        edge_line = [orig_node_.data.vertex, orig_node_.data.edge_next[1]]#[orig_node_.data.vertex, orig_node_.next.data.vertex]
                        #break

                    #if norm == v.edge_left.v.normalized() and event.opposite_edge.p == v.edge_left.p:
        			#	x = v
        			#	y = x.prev
        			#elif norm == v.edge_right.v.normalized() and event.opposite_edge.p == v.edge_right.p:
        			#	y=v
        			#	x=y.next

                #print 'why is this failing'
                #print orig_node_.data.edge_next
                #print edge_line
                #print '-'
                #edge_line = orig_node_.data.edge_prev

                chk_next = edge_line == curr_node_.data.edge_next
                chk_prev = edge_line == curr_node_.data.edge_prev
                if chk_next or chk_prev:
                    continue

                bisect_int_pt = self.intersect_ray_to_infinite_line(raypt,raydir,edge_line)
                if not bisect_int_pt:
                    continue

                #Now we use edge_line to compute point B
                #pt_B: intersection btwn bisector at V and
                #bisector btwn least parrallel edge starting at V and edge_line

                #Choose least parallel edge for curr_node_.prev/next with edge_line
                #Maintain CCW ordering
                #Note that we are using pointers to edge_next/edge_prev
                edge_next_vec = curr_node_.data.edge_next[1] - curr_node_.data.edge_next[0]
                edge_prev_vec = curr_node_.data.edge_prev[1] - curr_node_.data.edge_prev[0]
                edge_line_vec = edge_line[1] - edge_line[0]

                edge_prev_vec.Unitize()
                edge_next_vec.Unitize()
                edge_line_vec.Unitize()

                #Use dot prod to get angle
                prev_rad = math.acos(edge_prev_vec * edge_line_vec)
                next_rad = math.acos(edge_next_vec * edge_line_vec)

                #Store this info carefully bc need it for Event creation
                if next_rad > prev_rad:
                    vertex_edge_line = curr_node_.data.edge_next
                else:
                    vertex_edge_line = curr_node_.data.edge_prev

                vertex_vec = vertex_edge_line[1]-vertex_edge_line[0]
                #vertex_vec.Unitize()

                #print 'print chk prallel', edge_line_vec.IsParallelTo(vertex_vec)

                #Intersection at edge
                edge_int_pt = self.intersect_infinite_lines(vertex_edge_line,edge_line)
                if not edge_int_pt:
                    continue

                #Now get bisector btwn edge_line and vertex_edge_line
                #B_bisect: edge_line_vec.unitize - vertex_edge_vec.unitize
                #^ Trying a cleaner way to get angle bisector!
                vertex_edge_vec = vertex_edge_line[1] - vertex_edge_line[0]
                #Unitize edge vectors to create rhombus for bisector
                vertex_edge_vec.Unitize()
                edge_line_vec.Unitize()
                #Get bisector by subtraction

                B_bisect_dir =  edge_line_vec - vertex_edge_vec

                B_bisect_dir.Unitize()



                Bline = [edge_int_pt, edge_int_pt + B_bisect_dir*50.0]
                #if j==2:
                #    pass##debug.extend(vertex_edge_line)
                    ##debug.append(curr_node_.data.vertex)
                rayline = [raypt, raypt + raydir]
                B = self.intersect_infinite_lines(Bline,rayline)
                if not B:
                    continue
                #if not debugisfirst:
                    #if j<=3:#if j==1:#if cchk >= j:
                    #    #debug.append(B)
                #if debugisfirst and j==0:
                #    #debug.append(B)
                #else:
                #    break
                #print 'B exists'

                #Check if B is bound by edge_line, and left,right bisectors of edge_line
                def is_pt_bound_by_vectors(pt2chk,ray2chk,direction="istoleft",chkdebug=False):
                    #Input: pt, and ray(raypt, raydir)
                    #Output: Bool if bound by area (i.e. inside)
                    #This function uses cross product to see if pt2chk is inside rays
                    boundvec = (ray2chk[0] + ray2chk[1]) - ray2chk[0]
                    chkvec = pt2chk - ray2chk[0]
                    boundvec.Unitize()
                    chkvec.Unitize()
                    if j==0 and debugisfirst:
                        pass##debug.append(ray2chk[0])
                        ##debug.append(ray2chk[0] + ray2chk[1])
                        ##debug.append(pt2chk)
                        ##debug.append(ray2chk[0])

                    crossprod2d = boundvec[0]*chkvec[1] - chkvec[0]*boundvec[1]
                    #print 'crossprod is: ', crossprod2d
                    #print 'actual cross', rc.Geometry.Vector3d.CrossProduct(boundvec,chkvec)
                    #print 'dir', direction
                    #print res = a[0] * b[1] - b[0] * a[1]

                    if self.is_near_zero(crossprod2d):
                        #print 'cross prod at 0, must be parallel edges'
                        #print 'print chk prallel', boundvec.IsParallelTo(chkvec)
                        IsBound = True
                    elif direction=="istoright":
                        IsBound = True if crossprod2d < 0.0 else False
                    else:
                        IsBound = True if crossprod2d > 0.0 else False
                    return IsBound

                #Create left/right bisectors from edge
                #Using node.next rather then node.data.edge_next... careful...
                def _cross(a, b):
                	res = a[0] * b[1] - b[0] * a[1]
                	return res

                """
                xleft =  _cross(edge.bisector_left.v.normalized(), (b - edge.bisector_left.p).normalized())  > 0
    			xright = _cross(edge.bisector_right.v.normalized(), (b - edge.bisector_right.p).normalized())  <  0
    			xedge =  _cross(edge.edge.v.normalized(), (b - edge.edge.p).normalized()) < 0
                """

                #if j==3 and not debugisfirst:
                #    #debug.append(orig_node_.data.vertex)
                #    #debug.append(orig_node_.next.data.vertex)
                    #edgeline = rc.Geometry.Curve.CreateControlPointCurve(edge_line)
                    ##debug.append(edgeline)

                leftray = orig_node_.data.bisector_ray
                IsLeftBound = is_pt_bound_by_vectors(B,leftray,direction="istoright",chkdebug=True)
                #if edge_event_: print 'isleftbound', IsLeftBound

                rightray = orig_node_.next.data.bisector_ray
                IsRightBound = is_pt_bound_by_vectors(B,rightray,direction="istoleft")
                #if edge_event_: print 'isrightbound', IsRightBound

                bottomray = (edge_line[0], edge_line_vec)
                IsBottomBound = is_pt_bound_by_vectors(B,bottomray,direction="istoleft")
                #if edge_event_: print 'isbottombound', IsBottomBound

                if not (IsLeftBound and IsRightBound and IsBottomBound):
                    continue

                #if debugisfirst and edge_event_ != None and j==1:
                #    debug.append(B)

                #print 'B is bound'
                #if debugisfirst and j==0:
                #    print 'this B is bound'
                    ##debug.append(B)

                #prevdist,g = distline2pt(pn1,pn2,int_prev.PointAtEnd)
                #B_dist,g_ = distline2pt(edge_line[0],edge_line[1],B)
                B_dist = B.DistanceTo(curr_node_.data.vertex)

                if min_dist > B_dist:
                    min_dist = B_dist
                    min_candidate_B = B
                    min_edge_line = edge_line
                    min_node_A = curr_node_

                #edgeline = rc.Geometry.Curve.CreateControlPointCurve(edge_line)
                ##debug.extend(min_edge_line)
                #edgeline = rc.Geometry.Curve.CreateControlPointCurve(vertex_edge_line)
                ##debug.append(edgeline)
                ##debug.append(edge_int_pt)
                #print '-'
        return min_edge_line, min_candidate_B, min_node_A
    def find_polygon_events(self,LAV,SLAV,PQ,angle_index=False,cchk=None):
        def distline2pt(v,w,p):
            ##This algorithm returns the minimum distance between
            ##line segment vw and point p
            ##Modified from http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
            ##This is the explaination from stackoverflow for ref:
            ##Consider the line extending the segment, parameterized as v + t (w - v).
            ##We find projection of point p onto the line.
            ##It falls where t = [(p-v) . (w-v)] / |w-v|^2
            ##We clamp t from [0,1] to handle points outside the segment vw.

            ##Convert to rc geometry
            v = rc.Geometry.Vector3d(v)
            w = rc.Geometry.Vector3d(w)
            p = rc.Geometry.Vector3d(p)

            ##Create dir vectors for line and point
            wv = w-v
            pv = p-v

            ##Calculate |w-v|^2 w/o costly sqrt
            lsq = wv.SquareLength
            # Check for zero line segment case: v == w
            if self.is_near_zero(lsq):
                return pv.Length

            ##ProjectionPVonWV = (w-v)/|w-v| * (w-v)/|w-v| * (p-v)
            ##simplfiied = projpv = (w-v) * ((p-v) * (w-v))/|w-v|^2
            ##Then: projpv - p == perpendicular line

            ##clamp_to_line: ((p-v) * (w-v))/|w-v|^2
            ##(w-v): wv
            ##projpv = clamp_to_line * wv
            clamp_to_line = (pv * wv)/lsq

            ##This is to handle points outside line segment. They will have
            ##obtuse angle so costheta < 0. in that case will clamp_to_line factor == 0.
            ##therefore if obtuse, clamp_to_line turns projpv into a zero vector and
            ##and will return (non perpendicular) distance from point v to p.
            clamp_to_line = max(0., min(1.,clamp_to_line))
            projpv = clamp_to_line * wv

            ##Instead of simply subtracting projpv-p, we first add it to v
            ##and then subtract it from p
            ##This is so that if p is outside of line segment, then projpv = 0 vector, so
            ##v - p will be our minimum distance.
            perpvector = (v + projpv) - p

            ##Return values
            perpgeom = rs.AddLine(projpv,p)
            perpline = rs.AddLine(v,w)
            perppt = rc.Geometry.Point3d(p)
            return perpvector.Length, (perpgeom,perpline,perppt)

        #debug = sc.sticky['#debug']
        #Create Priotity Queue from Python module
        #Ref: https://docs.python.org/2.7/library/heapq.html#priority-queue-implementation-notes

        #hypothenuse = sqrt(a^2 + b^2) = c; to get longest line
        side1 = self.get_long_short_axis()[1]
        side2 = self.get_long_short_axis()[3]
        linedim = math.sqrt(side1*side1 + side2*side2)

        debug_minev = None

        for i in xrange(LAV.size):
            curr_node = LAV[i]
            if type(angle_index)==type(1) and not self.is_near_zero(i-angle_index):
                continue

            curr_ray = curr_node.data.bisector_ray
            prev_ray = curr_node.prev.data.bisector_ray
            next_ray = curr_node.next.data.bisector_ray

            #In case of reflex angle, edge_event or split_event can occur
            split_event_pt = None
            if curr_node.data.is_reflex==True:
                #print 'found reflex'
                if angle_index==False:
                    split_event_line, split_event_pt, split_node_A = self.find_opposite_edge_from_node(curr_node,SLAV,cchk=cchk)
                else:
                    #print 'this is not LOV'
                    split_event_line, split_event_pt, split_node_A = self.find_opposite_edge_from_node(curr_node,SLAV,is_LOV=False,cchk=cchk)
                ##debug.append(split_event_pt)
            else:
                pass#print 'not reflex'
            #Get intersection
            p_start = curr_ray[0] + (curr_ray[1]*-1) * linedim
            p_end = curr_ray[0]+curr_ray[1]*linedim
            curr_line = rc.Geometry.Curve.CreateControlPointCurve([p_start,p_end],0)

            #!!!should check for parallel edge case
            int_prev = self.extend_ray_to_line(prev_ray,curr_line)
            int_next = self.extend_ray_to_line(next_ray,curr_line)

            #Get nodes from prevedge and nextedge for distance check
            #Use edge pointers we stored earlier as
            #we updated LAV. This edge pointer point back to original edges in polgon
            #but changes along with LAV

            pn1,pn2 = curr_node.data.edge_prev[0],curr_node.data.edge_prev[1]
            nn1,nn2 = curr_node.data.edge_next[0],curr_node.data.edge_next[1]

            ##--- Debug ---##
            def debug_dist2line(pn1,pn2,curr_node,int_prev,int_next):
                pdt,g1 = distline2pt(pn1,pn2,int_prev.PointAtEnd)
                ndt,g2 = distline2pt(nn1,nn2,int_next.PointAtEnd)

                #debug.append(curr_line)
                #debug.append(curr_node.prev.data.vertex)
                #debug.append(curr_node.data.vertex)
                ##debug.append(curr_ray[0]+curr_ray[1]*5)
                #debug.append(curr_node.next.data.vertex)
                ##debug.append(g1[0])#proj
                #debug.append(g1[1])#line
                #debug.append(g1[2])#pt
                ##debug.append(g2[0])#proj
                #debug.append(g2[1])#line
                #debug.append(g2[2])#pt
            ##debug_dist2line(pn1,pn2,curr_node,int_prev,int_next)
            ##--- Debug ---##

            event_tuple = []
            ##ref: __init__(self,int_vertex,node_A,node_B,length2edge):
            #node_A, node_B are the two nodes whose intersection creates new node
            if int_prev != None:
                #Calculate distance to original edge in polygon
                prevdist,g = distline2pt(pn1,pn2,int_prev.PointAtEnd)
                #Event: (I (point3d), Va (pointer to previos node in LAV), Vb (pointer to next node in LAV), current node, ....)
                prev_edge_event = Event(int_prev.PointAtEnd,curr_node.prev,curr_node,prevdist,"edge")#int_prev.GetLength(),curr_node)
                event_tuple.append(prev_edge_event)
            if int_next != None:
                #Calculate distance to edge
                nextdist,g = distline2pt(nn1,nn2,int_next.PointAtEnd)
                next_edge_event = Event(int_next.PointAtEnd,curr_node,curr_node.next,nextdist,"edge")#int_next.GetLength(),curr_node)
                event_tuple.append(next_edge_event)
            if split_event_pt != None:
                split_event_dist,g = distline2pt(split_event_line[0],split_event_line[1],split_event_pt)
                split_edge_event = Event(split_event_pt,split_node_A,split_event_line,split_event_dist,"split")
                split_edge_event.opposite_edge = split_event_line
                event_tuple.append(split_edge_event)
            #make edge_event
            #event_tuple.append(edge_event)

            if event_tuple:
                min_event = min(event_tuple, key=lambda e: e.length2edge)
                min_event.LAV = LAV #store pointer to LAV
                heapq.heappush(PQ,(min_event.length2edge,min_event))
                if angle_index:
                    debug_minev = min_event

            #print '-'
        #print '----'
        return PQ, debug_minev
    def shape_to_adj_graph(self):
        #Purpose: converts bottom of polygon into a adjacency list
        #Input: self base_matrix
        #Output: adjacency list polygon shape as directed cycles

        #Add all vertices from polygon
        ##base_matrix: listof (list of edge vertices)
        #Label of vertice is index (may have to change this to coordinates)
        #Instantiate with empty adjancencies
        ##debug = sc.sticky["#debug"]
        adjgraph = AdjGraph()
        for i in xrange(len(self.base_matrix)-1):
            prev_v = self.base_matrix[i-1][0]
            prev_key = adjgraph.vector2hash(prev_v)
            prev_node = adjgraph[prev_key]

            #If beggining need to add previous node
            if prev_node == None:
                prev_node = adjgraph.add_node(prev_key,prev_v,is_out_edge=True)
                first_key = prev_node.key
            curr_v = self.base_matrix[i][0]
            #add_node(key,value)
            curr_key = adjgraph.vector2hash(curr_v)
            curr_node = adjgraph.add_node(curr_key,curr_v,is_out_edge=True)
            adjgraph.add_directed_edge(prev_key,curr_key)
        #Make sure to connect last edge back to first edge
        adjgraph.add_directed_edge(curr_key,first_key)
        return adjgraph
    def update_shape_adj_graph(self,adj_graph_,exist_vertex,new_vertex,twoside=True):
        # Update our adjacency list
        #Get the key by hashing vertex
        exist_key = adj_graph_.vector2hash(exist_vertex)
        new_key = adj_graph_.vector2hash(new_vertex)
        #Get the node with the key
        exist_node = adj_graph_[exist_key]

        if new_key in adj_graph_:
            new_node = adj_graph_[new_key]
        else:
            new_node = adj_graph_.add_node(new_key,new_vertex)
            #print 'newnode', new_node

        #Add new node to graph
        adj_graph_.add_directed_edge(exist_key,new_key)
        if twoside == True:
            adj_graph_.add_directed_edge(new_key,exist_key)
        return adj_graph_
    def straight_skeleton(self,perimeter_depth,stepnum):
        ##debug = sc.sticky["#debug"]
        #Move this into its own repo/class
        #call bibil for shape libraries
        #thats how we can transition to HB

        ##Initialization of ABNunlo
        #Organize given vertices into LAV in SLAV
        #Set of LAV: (listof LAV)
        SLAV = []
        PQ = []

        #LAV: doubly linked list (DLL).
        #Initialize List of Active Vertices as Double Linked List
        LAV = self.convert_shape_to_circular_double_linked_list()
        adj_graph = self.shape_to_adj_graph()
        #Compute the vertex angle bisector (ray) bi
        LAV = self.compute_interior_bisector_vector(LAV)
        #Keep a copy of LAV for original polygon
        #LOV: List of Original Vertices
        LOV = copy.deepcopy(LAV)

        #Add LAV to SLAV
        SLAV.append(LAV)
        #Compute bisector intersections and maintain Priority Queue of Edge Events
        #An edge event is when a edge shrinks to point in Straight Skeleton
        PQ,minev = self.find_polygon_events(LAV,SLAV,PQ,cchk=stepnum)

        #Main skeleton algorithm
        ##--- Debug ---##
        #print 'length: ', len(PQ), ' vertices'
        count = 0
        create_geom = True
        debug_crv = stepnum
        ##--- Debug ---##
        #if True:
        #    return None
        while len(PQ) > 0 and count<=30:

            if count > stepnum:
                break
            #print '-'
            #print 'count: ', count
            #edge_event: int_vertex,int_arc,node_A,node_B,length2edge

            #Priority Queue as Heap data structure
            #time complexity for insertion is: O(nlogn)
            #space complexity is: O(1)
            #find minimum is O(1) time, so good for us!
            #heap absolutely, completely beats sorting arrays is a
            #situation where small numbers of items are removed or added,
            #and after each change you want to know again which is the
            #smallest element

            edge_event = heapq.heappop(PQ)[1]

            #Get specific LAV from SLAV using event class
            LAV_ = edge_event.LAV
            #print 'lav size', LAV_.size
            if edge_event.event_type == "edge":
                #print 'event type edge'

                #If not processed this edge will shrink to zero edge
                if edge_event.node_A.data.is_processed or edge_event.node_B.data.is_processed:
                    #print '0 peak'
                    count+=1
                    continue

                Vc_I_arc = None
                #Check for peak of the roof event
                #print 'eenA', edge_event.node_A.prev
                def debug_LAV_links(LA):
                    #print '---- ----'
                    #print 'checking LAV_ size is:', LAV.size
                    for cnt in xrange(LAV.size):
                        cn = LAV[cnt]
                        #if cnt > 4:
                        #    break
                        #print cnt, ":", self.vector2hash(cn.data.vertex,1)
                        #print ''
                        #if cnt == 5:
                            #debug.append(cn.next.data.vertex)
                        ##debug.append(cn.data.vertex)
                    #print '---- ----'

                ##debug_LAV_links(LAV_V1)
                ##debug.append(edge_event.node_A.data.vertex)
                #print edge_event.node_A.data.is_processed
                #break

                if edge_event.node_A.prev.prev is edge_event.node_B:
                    #print '3 peak'
                    new_int_vertex = edge_event.int_vertex
                    A_vertex = edge_event.node_A.data.vertex
                    B_vertex = edge_event.node_B.data.vertex
                    prev_A_vertex = edge_event.node_A.prev.data.vertex

                    #Update adjacency graph
                    adj_graph = self.update_shape_adj_graph(adj_graph,prev_A_vertex,new_int_vertex)
                    adj_graph = self.update_shape_adj_graph(adj_graph,A_vertex,new_int_vertex)
                    adj_graph = self.update_shape_adj_graph(adj_graph,B_vertex,new_int_vertex)

                    Vc_I_arc = rc.Geometry.Curve.CreateControlPointCurve([prev_A_vertex, new_int_vertex])
                    Va_I_arc = rc.Geometry.Curve.CreateControlPointCurve([A_vertex, new_int_vertex])
                    Vb_I_arc = rc.Geometry.Curve.CreateControlPointCurve([B_vertex, new_int_vertex])

                    #if create_geom and debug_crv >= 0 and debug_crv >= count:
                        ##debug.append(Va_I_arc)
                        ##debug.append(Vb_I_arc)
                        ##debug.append(Vc_I_arc)
                        #pass
                    edge_event.node_A.data.is_processed = True
                    edge_event.node_B.data.is_processed = True
                    count += 1

                    #Update the adjacency list
                    #tbd
                    continue

                new_int_vertex = edge_event.int_vertex
                A_vertex = edge_event.node_A.data.vertex
                B_vertex = edge_event.node_B.data.vertex
                #Update adjacency graph
                adj_graph = self.update_shape_adj_graph(adj_graph,A_vertex,new_int_vertex)
                adj_graph = self.update_shape_adj_graph(adj_graph, B_vertex,new_int_vertex)

                Va_I_arc = rc.Geometry.Curve.CreateControlPointCurve([A_vertex, new_int_vertex])
                Vb_I_arc = rc.Geometry.Curve.CreateControlPointCurve([B_vertex, new_int_vertex])
                #print '2 peak'
                if create_geom and debug_crv >= 0 and debug_crv >= count:
                    ##debug.append(Va_I_arc)
                    ##debug.append(Vb_I_arc)
                    pass

                #Pointer to appropriate edge for bisector compution
                #Note that these edges according to Felkel and Obdrsalek are NOT adjacent
                #edges, but actually original edges from polygon linked via LAV
                new_prev_edge = edge_event.node_A.data.edge_prev
                new_next_edge = edge_event.node_B.data.edge_next

                #Create new vertex node
                int_vertex_obj = Vertex(edge_event.int_vertex,new_prev_edge,new_next_edge)
                V = DLLNode(int_vertex_obj)

                LAV_.insert_node(V,edge_event.node_A)
                LAV_.remove_node(edge_event.node_A)
                LAV_.remove_node(edge_event.node_B)

                #Mark as processed
                edge_event.node_A.data.is_processed = True
                edge_event.node_B.data.is_processed = True

                #Now compute bisector and edge event for new V node
                V_index = LAV_.get_node_index(V)
                LAV_ = self.compute_interior_bisector_vector(LAV_,angle_index=V_index)
                PQ,minev = self.find_polygon_events(LAV_,SLAV,PQ,angle_index=V_index,cchk=count)
            else:
                #print 'split event type'
                #If not processed this edge will shrink to zero edge
                ##ref: __init__(self,int_vertex,node_A,node_B,length2edge):
                if edge_event.node_A.data.is_processed:# or edge_event.node_B==True:
                    count+=1
                    continue

                #if count == 2:
                #    #debug.append(edge_event.node_A.data.vertex)
                #    #debug.extend(edge_event.node_B)

                int_vertex = edge_event.int_vertex
                node_V = edge_event.node_A #this is the only node/vertex that points to I/int_vertex

                #C) Check for peak of the roof event
                ref_edge = edge_event.node_B
                if LAV_.size < 3:
                    Vb_H_arc = rc.Geometry.Curve.CreateControlPointCurve([LAV.head.data.vertex,LAV.head.next.data.vertex])
                    ##debug.append(Vb_H_arc)
                    #print 'LAV == 2'
                    count += 1
                    #edge_event.node_A.data.is_processed = True
                    continue

                if edge_event.node_A.next.next.data.vertex == ref_edge[0]:
                    pass#print '3 peak'
                    """
                    #edge_event.node_A.prev.prev.data.vertex == ref_edge[0]:
                    new_int_vertex = edge_event.int_vertex
                    A_vertex = edge_event.node_A.data.vertex
                    B_vertex = ref_edge[1]
                    prev_A_vertex = edge_event.node_A.prev.data.vertex

                    Vc_I_arc = rc.Geometry.Curve.CreateControlPointCurve([prev_A_vertex, new_int_vertex])
                    Va_I_arc = rc.Geometry.Curve.CreateControlPointCurve([A_vertex, new_int_vertex])
                    Vb_I_arc = rc.Geometry.Curve.CreateControlPointCurve([B_vertex, new_int_vertex])

                    #debug.append(Vc_I_arc)
                    #debug.append(Va_I_arc)
                    #debug.append(Vb_I_arc)

                    edge_event.node_A.data.is_processed = True
                    #edge_event.node_B = True
                    count += 1
                    continue
                    """

                #D) Output arc
                split_I_arc = rc.Geometry.Curve.CreateControlPointCurve([int_vertex, node_V.data.vertex])
                #Update adjacency graph
                adj_graph = self.update_shape_adj_graph(adj_graph,node_V.data.vertex,int_vertex)

                if create_geom and debug_crv >= 0 and debug_crv >= count:
                    pass##debug.append(split_I_arc)
                #print '2 peak'
                edge_event.node_A.data.is_processed = True
                #if count == 7:
                #    #debug.append(LAV_.head.next.data.vertex)

                #Find opposite edge from V
                #Botsky just uses original, Fezkel suggests do it again.
                opposite_edge, opposite_I, opposite_A = self.find_opposite_edge_from_node(node_V,SLAV,edge_event_=edge_event)
                #print 'does opposited edgevent exist????222', edge_event
                #opposite_A is the node that you are evaluating for split_events, likely won't be used
                if opposite_edge == None:
                    #print 'Opposite edge not found! line 1930'
                    count += 1
                    continue
                #Make two copies of V for our LAV splitting
                #Add pointer to edge. This is based on Figure 6 from Felkel and Obdrzalek
                vertex_V1 = Vertex(opposite_I,node_V.data.edge_prev,opposite_edge)
                vertex_V2 = Vertex(opposite_I,opposite_edge,node_V.data.edge_next)
                node_V1 = DLLNode(vertex_V1)
                node_V2 = DLLNode(vertex_V2)

                #E) Modify the SLAV
                #Match the correct nodes to vertex from opposite_edge event ref
                #The trick here is to ensure new opposite node may not be original original
                #watch out for LAVs that share a vertex but not same node linked in different LAV
                op_zero_node,op_one_node = None, None
                #opposite_vector = opposite_edge[1] - opposite_edge[0]
                for i in xrange(len(SLAV)):
                    LAV__ = SLAV[i]
                    for j in xrange(LAV__.size):
                        chk_zero_pt = LAV__[j].data.vertex
                        chk_one_pt = LAV__[j].next.data.vertex
                        #chk_vector = chk_one_pt - chk_zero_pt
                        #IsVector = opposite_vector.IsParallelTo(chk_vector)
                        IsLine = chk_zero_pt == opposite_edge[0] and chk_one_pt == opposite_edge[1]
                        if IsLine:
                            op_zero_node = LAV__[j]
                            op_one_node = LAV__[j].next
                            break
                    if op_zero_node != None:
                        break

                if op_zero_node == None or op_one_node == None:
                    #print 'opposite edge nodes not found!'
                    count += 1
                    continue

                def copy_DLL_from_node(old_LAV):
                    copy_LAV = DoubleLinkedList()
                    curr_node = old_LAV.head
                    while curr_node != old_LAV.tail:
                        copy_LAV.append(curr_node.data)
                        curr_node = curr_node.next
                    #get tail data in to
                    copy_LAV.append(curr_node.data)
                    return copy_LAV


                #Split LAV - V1
                node_V.prev.next = node_V1
                op_one_node.prev = node_V1
                node_V1.prev = node_V.prev
                node_V1.next = op_one_node
                #Copy LAV_ for V1
                LAV_.head = node_V1
                LAV_.tail = node_V1.prev
                LAV_V1 = copy_DLL_from_node(LAV_)


                #Split LAV - V2
                node_V.next.prev = node_V2
                op_zero_node.next = node_V2
                node_V2.next = node_V.next
                node_V2.prev = op_zero_node

                ##debug.append(node_V.next.data.vertex)
                ##debug.append(opposite_left_node.data.vertex)
                #Copy LAV_ for V2
                LAV_.head = node_V2
                LAV_.tail = node_V2.prev
                LAV_V2 = copy_DLL_from_node(LAV_)

                #remove node_V
                #LAV_.remove_node(node_V)
                node_V.next = None
                node_V.prev = None

                #opposite_left_node.is_processed = True
                #opposite_right_node.is_processed = True

                for i in xrange(len(SLAV)):
                    if SLAV[i] == LAV_:
                        SLAV[i] = None

                SLAV = filter(lambda n: n!=None,SLAV)
                SLAV.append(LAV_V1)
                SLAV.append(LAV_V2)
                #print 'LAV_V1', len(LAV_V1)
                #print 'LAV_V2', len(LAV_V2)

                for i in xrange(len(SLAV)):
                    LAV__ = SLAV[i]
                    if LAV__.size < 3:
                        for j in xrange(LAV__.size):
                            cn = LAV__[j]
                            cn.is_processed = True

                #Now compute bisector and edge event for new V1/2 node
                V1_index = LAV_V1.get_node_index(node_V1)
                V2_index = LAV_V2.get_node_index(node_V2)

                LAV_V1 = self.compute_interior_bisector_vector(LAV_V1,angle_index=V1_index)
                LAV_V2 = self.compute_interior_bisector_vector(LAV_V2,angle_index=V2_index)

                PQ,minev = self.find_polygon_events(LAV_V1,SLAV,PQ,angle_index=V1_index,cchk=count)

                def debug_LAV_links(LAV):
                    print '---- ----'
                    print 'checking LAV_ size is:', LAV.size
                    for cnt in xrange(LAV.size):
                        cn = LAV[cnt]
                        #if cnt > 4:
                        #    break
                        print cnt, ":", self.vector2hash(cn.data.vertex,1)
                        print ''
                        #if cnt == 5:
                        #    #debug.append(cn.next.data.vertex)
                        #debug.append(cn.data.vertex)
                    print '---- ----'

                ##debug.append(opposite_edge[0])
                ##debug.append(opposite_edge[1])
                ##debug.append(node_V.data.vertex)
                ##debug.append(node_V1.data.vertex)
                ##debug_LAV_links(LAV_V1)
                ##debug_LAV_links(LAV_V1)
                ##debug.append(LAV_V2.head.next.next.data.vertex)
                #break
                PQ,minev = self.find_polygon_events(LAV_V2,SLAV,PQ,angle_index=V2_index,cchk=count)
                #break
            count += 1

        #Take the cycles and create perimeter
        #print adj_graph

        #loc: listof (listof cycles)
        loc = adj_graph.find_most_ccw_cycle()
        #Get offset
        corner_style = rc.Geometry.CurveOffsetCornerStyle.Sharp
        core_crv_lst = self.bottom_crv.Offset(self.cpt,\
                                 self.normal,perimeter_depth,\
                                 sc.doc.ModelAbsoluteTolerance,corner_style)

        ##debug.extend(core_crv_lst)
        core_brep_lst = []
        split_zones = []
        if core_crv_lst == None:
            core_crv_lst = []
        if not self.is_near_zero(len(core_crv_lst)):
            for i in xrange(len(core_crv_lst)):
                core_crv_chk = core_crv_lst[i]
                if not core_crv_chk.IsClosed:
                    continue
                try:
                    core_extrusion = rc.Geometry.Extrusion.Create(core_crv_chk,\
                                                              self.ht-self.cpt[2],True)
                    core_brep = core_extrusion.ToBrep()
                    core_brep_lst.append(core_brep)
                except:
                    pass
        #debug.extend(core_brep_lst)
        split_zones.extend(core_brep_lst)
        #if len(core_brep_lst)>1:
        #    print 'we have multiple cores check the way we are diffing this:',\
        #     len(core_brep_lst)
        #Make preimeter breps

        for i in xrange(len(loc)):
            cycle = loc[i]
            ptlst = map(lambda n: n.value,cycle)

            # This is to deal with degenerate polygons (just two lines) by making it into a triangle
            # Could be a better solution for this.
            if len(ptlst) < 4:
                ptlst.append(ptlst[0])

            per_crv = rc.Geometry.PolylineCurve(ptlst)
            per_extrusion = rc.Geometry.Extrusion.Create(per_crv,self.ht-self.cpt[2],True)
            per_brep = per_extrusion.ToBrep()
            diff_per_lst = []
            if not self.is_near_zero(len(core_brep_lst)):
                for i in xrange(len(core_brep_lst)):
                    core_brep = core_brep_lst[i]
                    diff_per = rc.Geometry.Brep.CreateBooleanDifference(per_brep,\
                                                                        core_brep,sc.doc.ModelAbsoluteTolerance)

                    #If no difference, then just include original zone
                    if diff_per == None or self.is_near_zero(len(diff_per)):
                        diff_per_lst.append(per_brep)
                    else:
                        diff_per_lst.extend(diff_per)
            else:#if no core just include original zone
                diff_per_lst = [per_brep]
            split_zones.extend(diff_per_lst)
            ##debug.extend(diff_per_lst)


        """
        #For #debugging/checkign
        tnode.grammar.type['idlst'] = []
        tnode.grammar.type['ptlst'] = []
        for key in adj_graph.get_sorted_keylst():
            node = adj_graph[key]
            if True:#if node.id == 4:
                ##debug.append(node.value)
                tnode.grammar.type['idlst'].append(node.id)
                tnode.grammar.type['ptlst'].append(node.value)
                #adj_node_lst = adj_graph.get_adj_lst_as_node_lst(key)
                ##debug.extend(adj_node_lst)
        print 'final count: ', count
        print '--'
        """
        #print split_zones
        #print '--'
        adj_graph = None
        return [split_zones]


def main(mass, _perimeterZoneDepth):
    ##debug = sc.sticky['#debug']
    #Import the Ladybug Classes.
    if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()

        splitZones = []
        for i in xrange(len(mass)):
            mass_ = mass[i]

            if _perimeterZoneDepth < 0.001:
                splitZones.append([mass_])
                continue
            #bbBox = mass_.GetBoundingBox(rc.Geometry.Plane.WorldXY)
            #maxHeights = bbBox.Max.Z
            #minHeights = bbBox.Min.Z
            #splitters, flrCrvs, topIncl, nurbL, lastInclu = getFloorCrvs(mass_, [0, maxHeights-minHeights], maxHeights)
            #flrCrv = flrCrvs[0][0]
            mass_shape = Shape(mass_)#,#flrCrv)
            split_zones_per_mass = mass_shape.straight_skeleton(_perimeterZoneDepth,1000)

            splitZones.append(split_zones_per_mass)
            RhinoApp.Wait()
        return splitZones
    else:
        print "You should first let both Ladybug and Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return -1



def checkNonConvex(breps):
    """
    Temporary until I get the concave section working!
    Credit to Devang Chauhan for code from:
    https://github.com/mostaphaRoudsari/honeybee/blob/master/src/Honeybee_Find%20Non-Convex.py
    """
    #import the classes
    if sc.sticky.has_key('honeybee_release'):
        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            "Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1

        #Bringing NonConvexChecking class from Honeybee_Honeybee
        hb_NonConvexChecking = sc.sticky["honeybee_NonConvexChecking"]

        nonConvex = []
        faultyGeometry = []

        for brep in breps:
            surfaces = [brep.Faces.ExtractFace(i) for i in range(brep.Faces.Count)]
            for surface in surfaces:
                if hb_NonConvexChecking(surface).isConvex()[0] == False:
                    nonConvex.append(surface)
                if hb_NonConvexChecking(surface).isConvex()[1] > 0:
                    faultyGeometry.extend(hb_NonConvexChecking(surface).isConvex()[1])
        return (nonConvex , faultyGeometry)
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1


checkData = False
if _runIt == True:
    checkData = checkTheInputs()

    #---------------- TEMP ----------------------------
    brep4convexchk = copy.deepcopy(_bldgFloors)
    convex_result = checkNonConvex(brep4convexchk)
    if convex_result != -1:
        nonConvex, faultyGeometry = convex_result
        if len(faultyGeometry) > 0.0 or len(nonConvex) > 0.0:
            convex_error_msg = "You have a non-convex (or faulty) geometry, and this component mainly handles convex geometries (at this point). You should prepare the massing of your building by dividing it into convex volumes before using this component."
            print convex_error_msg
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, convex_error_msg)
    #---------------- TEMP ----------------------------


if checkData == True:
    #sc.sticky['#debug'] = []

    splitBldgMassesLists = main(_bldgFloors, _perimeterZoneDepth)

    if splitBldgMassesLists!= -1:
        pass#splitBldgMasses = DataTree[Object]()
        splitBldgZones = []
    names = DataTree[Object]()
    for i, buildingMasses in enumerate(splitBldgMassesLists):
        for j, mass in enumerate(buildingMasses):
            p = GH_Path(i,j)

            # in case mass is not a list change it to list
            try: mass[0]
            except: mass = [mass]
            #splitBldgMasses.Add(mass)
            splitBldgZones.extend(mass)

            newMass = []
            for brep in mass:
                if brep != None:
                    #Bake the objects into the Rhino scene to ensure that surface normals are facing the correct direction
                    sc.doc = rc.RhinoDoc.ActiveDoc #change target document
                    rs.EnableRedraw(False)
                    guid1 = [sc.doc.Objects.AddBrep(brep)]
                    if guid1:
                        a = [rs.coercegeometry(a) for a in guid1]
                        for g in a: g.EnsurePrivateCopy() #must ensure copy if we delete from doc

                        rs.DeleteObjects(guid1)

                    sc.doc = ghdoc #put back document
                    rs.EnableRedraw()
                    newMass.append(g)
                mass = newMass

            #try:
            #    splitBldgZones.AddRange(mass, p)
            #except:
            #    splitBldgZones.Add(mass, p)
