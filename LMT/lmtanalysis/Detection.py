'''
Created on 12 sept. 2017

@author: Fab
'''

import math
from lmtanalysis.Measure import *

class Detection():

    __slots__ = ('massX', 'massY','massZ','massPoint','frontX','frontY','frontZ','frontPoint','backX','backY','backZ','backPoint','rearing','lookUp','lookDown','mask','frame' )

    def __init__(self, massX, massY, massZ=None, frontX=None, frontY=None, frontZ=None, backX=None, backY=None, backZ=None, rearing=None, lookUp=None, lookDown=None , lightLoad = False , frame = None ):
        
        self.massX = massX
        self.massY = massY
        self.frame = frame
        
        if lightLoad:
            return
        
        self.massZ = massZ
        self.massPoint = Point( massX , massY )
            
        self.frontX = frontX
        self.frontY = frontY
        self.frontZ = frontZ
        self.frontPoint = Point( frontX , frontY )

        self.backX = backX
        self.backY = backY
        self.backZ = backZ
        self.backPoint = Point( backX , backY )

        self.rearing = rearing
        self.lookUp = lookUp
        self.lookDown = lookDown
        
    
    def setMask( self, mask ):
        self.mask = mask
        
    def isHeadAndTailDetected(self):
        
        if ( self.frontX == -1 or self.frontY == -1 or self.backX == -1 or self.backY == -1 ):
            return False
        
        return True
    
    def getBodySize(self):
        return math.hypot(self.frontX-self.backX, self.frontY-self.backY)
    
    
    def getBodySlope(self):
        '''
        calculate the instantaneous slope of the animal between nose and tail
        '''
        
        if (self.frontZ==0 or self.backZ==0):
            return None
        else:  
            bodySlope = (self.frontZ - self.backZ)
        
        return bodySlope
    
    def getMassCenterPoint(self):
        return Point( self.massX , self.massY )

    def getFrontPoint(self):
        return Point( self.frontX , self.frontY )
    
    def getBackPoint(self):
        return Point( self.backX , self.backY )
    
    def getDirection(self):
        '''
        determines the direction of the animal using the head and the mass center
        '''
        #angleDir = math.atan2(self.frontY-self.massY, self.frontX-self.massX)
        angleDir = math.atan2(self.frontY-self.backY, self.frontX-self.backX)
        return angleDir
            
    
    def getDistanceTo (self, detectionB):
        '''
        determine the distance between the focal animal and animalB at one specified time point t
        check before that both animals are detected at this time point
        '''
        distanceTo = None

        if ( detectionB == None ):
            return None
        
        if (detectionB.massX == None):
            return None
        
        if (math.hypot( self.massX - detectionB.massX, self.massY - detectionB.massY ) > MAX_DISTANCE_THRESHOLD): #if the distance calculated between the two individuals is too large, discard
            print("WARNING: Detection.getDistanceTo : Distance Max reached. returning None")
            return None
        
        else:
            distanceTo = math.hypot( self.massX - detectionB.massX, self.massY - detectionB.massY )
            return distanceTo
    
    
    def getDistanceToPoint (self, xPoint, yPoint):
        '''
        determine the distance between the focal animal and a specific point in the arena
        '''

        distanceToPoint = math.hypot( self.massX - xPoint, self.massY - yPoint )
        return distanceToPoint
    
    
    def isInZone (self, xa=149, xb=363, ya=98, yb=318):
        '''
        check whether a detection of animal A is located in the specified zone of the cage
        Default zone is the center xa=149, xb=363, ya=318, yb=98
        '''
        x1 = min( xa, xb )
        x2 = max( xa, xb )
        y1 = min( ya, yb )
        y2 = max( ya, yb )
        
        if ( self.massX > x1 and self.massX < x2 and self.massY > y1 and self.massY < y2 ):
            return True
        
        return False
    
    
    def isRearing(self):
        '''
        determine whether the animal is rearing at this detection
        '''
        if (self.getBodySlope() == None):
            return False
                
        if (self.getBodySlope() > -BODY_SLOPE_THRESHOLD and self.getBodySlope() < BODY_SLOPE_THRESHOLD):
            return False
        
        else:
            return True
        
    def isRearingZ(self):
        '''
        determine whether the animal is rearing at this detection, using the old criteria from the first version
        '''
        if (self.frontZ == None):
            return False
                
        if (self.frontZ < FRONT_REARING_THRESHOLD):
            return False
        
        else:
            return True