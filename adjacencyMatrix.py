# -------------------------------
# Make a Adjacency Matrix with Arcpy 10.3 and a pair of feature clases from a geodatabase
# one for lines that connect the network and the other for edges
# note that you must have a license for ArcGIS for Desktop to use it but with some changes will be possible to use some other GIS library
#
# @diegopajarito

import arcpy        # ArcPy is the python library for ArcGIS tools
import sys
import os
import numpy
import datetime     # just to be fancy with times, start stop and time

st = time.time()
print("Start Time: " + datetime.datetime.fromtimestamp(st).strftime('%Y-%m-%d %H:%M:%S'))

#you must use a path to get your geodatabase, where those feature clases (Shapefiles) are stored
arcpy.env.workspace = r'D:/Geo-C/Utils/Network/New File Geodatabase.gdb'

# define the path to those two layers
axis = r'stretsCastellon/ejes'
arcpy.MakeFeatureLayer_management(axis, 'axis_lyr')
edges = r'stretsCastellon/sources'
arcpy.MakeFeatureLayer_management(edges, 'edges_lyr')

#Create a matrix with zeros, the size is defined by the nnumber of nodes of the network
arcpy.SelectLayerByAttribute_management('edges_lyr','NEW_SELECTION', '1 = 1')
matrixSize = int(arcpy.GetCount_management('edges_lyr')[0]) # it counts the number of nodes in the edges layer from a foo selection
matrix = numpy.zeros(shape=(matrixSize,matrixSize), dtype=numpy.int8)

#It makes two loops. The first one for going though each line of the netwokr
with arcpy.da.SearchCursor(axis, ['OBJECTID']) as cursor_a:
    for row_a in cursor_a:
        axis_id = row_a[0]
        arcpy.SelectLayerByAttribute_management('axis_lyr','NEW_SELECTION', '"OBJECTID " = ' + str(row_a[0]))
        matchcount = int(arcpy.GetCount_management('axis_lyr')[0])
        #for each line you identify the nodes that intersect it using ArcGIS Select By Location Tool and the intersect spatial relationship
        arcpy.SelectLayerByLocation_management('edges_lyr', 'intersect', 'axis_lyr')
        matchcount = int(arcpy.GetCount_management('edges_lyr')[0])
        if matchcount == 2:
            # just edges with exactly two nodes connection will be considered in the adjacency matrix
            with arcpy.da.SearchCursor('edges_lyr', ['OBJECTID']) as cursor_e:
                edges = [0,0]
                count = 0
                for row_e in cursor_e:
                    edges[count] = row_e[0]
                    count = count + 1
            # you will change zeros by one at that positions where two nodes are conected
            matrix[edges[0]-1][edges[1]-1] = 1
            matrix[edges[1]-1][edges[0]-1] = 1
        else:
            print('edge {} does not have 2 edges'.format(row_a[0]))

#save the matrix in a text file, it will be used in R
numpy.savetxt('./adjancencyMatrix.txt', matrix.astype(int), fmt='%i', delimiter=';')

#Print some times
ft = time.time()
print("Finish Time: " + datetime.datetime.fromtimestamp(ft).strftime('%Y-%m-%d %H:%M:%S'))
tt = ft - st
print("Total Time: " + datetime.datetime.fromtimestamp(tt).strftime('%H:%M:%S'))
