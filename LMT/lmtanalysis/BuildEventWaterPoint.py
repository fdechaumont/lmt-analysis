'''
Created on 6 sept. 2017

@author: Fab
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
from affine import Affine
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Water Zone" )


def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None ): 
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
    '''
    Event Water Zone
    - the animal is in the zone around the water source
    '''
    
    for idAnimalA in pool.animalDictionnary.keys():
        print(pool.animalDictionnary[idAnimalA])
        
        eventName = "Water Zone"
        print ( "A is in the zone around the water source")        
        print ( eventName )
                
        waterZoneTimeLine = EventTimeLine( None, eventName , idAnimalA , None , None , None , loadEvent=False )
                
        result={}
        
        animalA = pool.animalDictionnary[idAnimalA]
        #print ( animalA )
        dicA = animalA.detectionDictionnary
            
        for t in dicA.keys():
            if (dicA[t].getDistanceToPoint(xPoint = 398, yPoint = 353) == None):
                continue
            
            if (dicA[t].getDistanceToPoint(xPoint = 398, yPoint = 353) <= MAX_DISTANCE_TO_POINT): 
                result[t] = True
                
        
        waterZoneTimeLine.reBuildWithDictionnary( result )
                
        waterZoneTimeLine.endRebuildEventTimeLine(connection)
    
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Water Point" , tmin=tmin, tmax=tmax )

    print( "Rebuild event finished." )
        
        
        
        
        
        
        
    