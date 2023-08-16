'''
Created on 23 mai 2023

@author: eye
'''
import sqlite3
from time import *
from lmtanalysis.Chronometer import Chronometer
from lmtanalysis.Animal import *
from lmtanalysis.Detection import *
from lmtanalysis.Measure import *
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
#from affine import Affine
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from lmtanalysis.TaskLogger import TaskLogger
from lmtanalysis import EventTimeLineCache
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.Parameters import *

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Corner" )
    deleteEventTimeLineInBase(connection, "Corner 0" )
    deleteEventTimeLineInBase(connection, "Corner 1" )
    deleteEventTimeLineInBase(connection, "Corner 2" )
    deleteEventTimeLineInBase(connection, "Corner 3" )
    
def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None, animalType = None ): 
    
    parameters = getAnimalTypeParameters( animalType )
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax, lightLoad=True )
    '''
    Event Corner Stop
    - the animal is in idling for more than a certain time in one of the corners of the cage
    corner 0: up left; corner 1: up right; corner 2: low right; corner 3: low left
    '''
    
    for animal in pool.animalDictionary.keys():
        print(pool.animalDictionary[animal])
        
        eventName = "Corner"
        print ( "A is idling in the corner zone")        
        print ( eventName )
        
        cornerTimeLine = {}
        for k in [0, 1, 2, 3]:
            cornerTimeLine[k] = EventTimeLine( None, f"{eventName} {k}" , animal , None , None , None , loadEvent=False )
       
        animalA = pool.animalDictionary[animal]
        print( 'Animal RFID: ', animalA.RFID )
        dicA = animalA.detectionDictionary
        
        resultCorner = {}
        for k in [0, 1, 2, 3]:
            resultCorner[k] = {}
        
        for t in dicA.keys():
            for k in [0, 1, 2, 3]:
                distanceToEventLocation = animalA.getDistanceToPoint( t, parameters.cornerCoordinatesOpenFieldArea[k][0], parameters.cornerCoordinatesOpenFieldArea[k][1] )
                if distanceToEventLocation == None:
                    print('Distance cannot be computed.')
                    break
                if (distanceToEventLocation <= parameters.MAX_DISTANCE_TO_POINT*1):
                    resultCorner[k][t] = True
                    
                    break
        
        for k in [0, 1, 2, 3]:
            cornerTimeLine[k].reBuildWithDictionary( resultCorner[k] )
            cornerTimeLine[k].removeEventsBelowLength( maxLen = parameters.MIN_DURATION_IN_CORNER )
            cornerTimeLine[k].mergeCloseEvents( numberOfFrameBetweenEvent = 3 )
            cornerTimeLine[k].endRebuildEventTimeLine(connection)        
    
    
    # log process
    
    t = TaskLogger( connection )
    t.addLog( "Build Event Corner" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
        