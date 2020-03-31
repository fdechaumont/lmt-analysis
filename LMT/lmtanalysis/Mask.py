'''
Created on 12 sept. 2017

@author: Fab
'''

import math
from lmtanalysis.Measure import *
import zlib
from lxml import etree

import matplotlib
#matplotlib fix for mac
#matplotlib.use('TkAgg')

import matplotlib.pyplot as plt

class Mask():
    '''
    Binary mask of an animal at a given t.
    '''    
    
    def __init__(self, data, color="black"  ):
        
        x = 0
        y = 0
        w = 0
        h = 0
        boolMaskData = None
        
        tree = etree.fromstring( data )
        for user in tree.xpath("/root/ROI/boundsX"):
            x = int(user.text)
        for user in tree.xpath("/root/ROI/boundsY"):
            y = int(user.text)
        for user in tree.xpath("/root/ROI/boundsW"):
            w = int(user.text)
        for user in tree.xpath("/root/ROI/boundsH"):
            h = int(user.text)
        for user in tree.xpath("/root/ROI/boolMaskData"):
            boolMaskData = user.text

        self.x = x
        self.y = y 
        self.width = w
        self.height = h        
        self.unzip( boolMaskData )
        self.color = color
        
        #mask = Mask( x , y , w , h , boolMaskData, self.getColor() )

    
    def getPerimeter(self ):
        
        dicA = {}

        def isOnPerimeter( x , y ):
            
            nonlocal dicA

            for xx in range( -1,2 ):
                for yy in range( -1,2 ):
                    if ( x+xx , y+ yy ) not in dicA:
                        return True                
            
        # create a mask map
        for i in range( len( self.pointsX ) ):
            dicA[(self.pointsX[i], self.pointsY[i])] = True
            
        nbPointPerimeter = 0
        
        for i in range( len ( self.pointsX ) ):
            
            x = self.pointsX[i]
            y = self.pointsY[i]
            
            if isOnPerimeter( x , y ):
                nbPointPerimeter+=1
            
        return nbPointPerimeter
        
        
        
    def getRoundness(self):
        
        '''
        if not hasattr(self, 'pointX'):
            print( "none")
            return None
        '''
        try:
            area = len( self.pointsX )
            '''
            circularity = 4.0 * area / ( self.getPerimeter() * longAxis );
            '''
            roundness = ( self.getPerimeter()**2 ) / ( 4.0 * math.pi * area )
            return roundness;
        except:
            print("Problem in Mask.getRoundness()" )
            
        return None
        
    def showMask(self , color = None , ax = None ):
        '''
        show the mask in a figure
        '''
        if ( color == None ):
            color = self.color
        
        if ( ax == None ):
            fig, ax = plt.subplots()
            ax.scatter( self.pointsX, self.pointsY , c=color )
            plt.show()
        else:
            ax.scatter( self.pointsX, self.pointsY , c=color )
    
    def isInContactWithMask(self, mask ):
        
        dicA = {}
        # create a first map with the self mask and 1 pix of dilation
        for i in range( len( self.pointsX ) ):
            for x in range( -1,2 ):
                for y in range( -1,2 ):
                    dicA[(self.pointsX[i]+x, self.pointsY[i]+y)] = True
        # check if a point overlaps
        for i in range( mask.pointsX ):
            if (mask.pointsX[i], mask.pointsY[i]) in dicA:
                return True
        
        return False
            
    def getNbPoint(self):
        return len( self.pointsX )
    
    def unzip(self, maskDataZipped ):
        
        # re fill 0 and put space instead of : separator
        if maskDataZipped == None:
            return    
        s = maskDataZipped.split(":")
        s2 = ""
        for value in s:
            if ( len(value) == 1 ):
                s2+="0"
            s2+=value+" "
            
        #print ( s2 )
        #print ("************")
        b = bytearray.fromhex( s2 )
        
        #print("uncompressed: ")
        uncompressed= zlib.decompress( b )
        
        #print ( uncompressed )
                    
        self.pointsX= []
        self.pointsY= []
                
        index = 0
        for y in range( self.y , self.y+ self.height ):
            for x in range( self.x , self.x+ self.width ):
                        
                if ( uncompressed[index] == 1 ):
                    self.pointsX.append( x )
                    self.pointsY.append( -y )
                
                index+=1
                
        
        