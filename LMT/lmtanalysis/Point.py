'''
Created on 6 sept. 2017

@author: Fab
'''

import math

class Point:
    '''
    classdocs
    '''


    __slots__ = ('x', 'y' )


    def __init__(self, x,y):
        self.x = x;
        self.y = y;
        
    def distanceTo(self , p ):
        return math.hypot( self.x-p.x , self.y-p.y )
        
        