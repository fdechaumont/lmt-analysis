'''
Created on 31. March 2022

@author: Elodie
'''
import sqlite3
from time import *
from lmtanalysis.Chronometer import Chronometer
from lmtanalysis.Animal import *
from lmtanalysis.Detection import *
from lmtanalysis.Measure import *
import matplotlib.pyplot as plt
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.Parameters import getAnimalTypeParameters
from lmtanalysis.TaskLogger import TaskLogger


def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Move high speed" )

def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None, animalType = None  ):
    ''' 
    Animal A is stopped (built-in event): revert the event to have move events
    Animal A is moving at a instant speed within a specific range
    We distinguish the speed of the move by using one threshold computed as the third percentile of the mean speed of the animal during move events over one day of exp max
    ''' 
    parameters = getAnimalTypeParameters( animalType )
    
    # create dedicated pool as we will alter detection pool with filters (I.e: we don't use the pool cache)
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    pool.loadDetection( start = tmin, end = tmax , lightLoad=True )
    
    #initialise the move high speed timeline
    moveHighSpeedTimeLine = {}
    for idAnimalA in pool.animalDictionary:
        moveHighSpeedTimeLine[idAnimalA] = EventTimeLine( None, "Move high speed" , idAnimalA, None , None , loadEvent=False )
    
    #compute the threshold for speed category: the third percentile of the speed during move events
    speedPercentile = {}
    for idAnimalA in pool.animalDictionary:
        moveTimeLine = EventTimeLine( connection, "Stop", idAnimalA, minFrame=tmin, maxFrame=tmax, inverseEvent=True )
        if len(moveTimeLine.eventList) == 0:
            continue
        animalA = pool.animalDictionary[idAnimalA]
        speedList = []
        for t in moveTimeLine.getDictionary(minFrame=tmin, maxFrame=tmax):
            #print(animalA.getSpeed( t ))
            speedList.append( animalA.getSpeed( t ) )
        
        print(f"speedList: {len(speedList)}")
        speedListClean = [i for i in speedList if i is not None]
        print(f"speedListClean: {len(speedListClean)}")
        if len(speedListClean) == 0:
            continue
        
        speedPercentile[idAnimalA] = np.percentile( speedListClean , 75)
        print(f"speedList percentile: {speedPercentile[idAnimalA]}")
        
    
    #create the dictionary to rebuild the timeline    
    moveHighSpeedTimeLineDic = {}
    
    for idAnimalA in pool.animalDictionary:
        animalA = pool.animalDictionary[idAnimalA]
        if animalA.getNumberOfDetection(tmin = tmin, tmax=tmax) == 0:
            continue
        
        moveHighSpeedTimeLineDic[idAnimalA] = {}
        
        print(pool.animalDictionary[idAnimalA])
        print(f"speed percentile {idAnimalA}: {speedPercentile[idAnimalA]}")
        animalA.filterDetectionByInstantSpeed(speedPercentile[idAnimalA], parameters.MAXIMUM_SPEED_THRESHOLD)
        
        moveHighSpeedTimeLine[idAnimalA].reBuildWithDictionary( animalA.detectionDictionary )
        moveHighSpeedTimeLine[idAnimalA].endRebuildEventTimeLine(connection)
            
    
    # log process
    t = TaskLogger( connection )
    t.addLog( f"Move high speed (speed percentile)" , tmin=tmin, tmax=tmax )
    
    print( "Rebuild event finished." )
        
    