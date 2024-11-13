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
    We distinguish the speed of the move by using one threshold
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
    
    #create the dictionary to rebuild the timeline    
    moveHighSpeedTimeLineDic = {}
    
    for idAnimalA in pool.animalDictionary:
        animalA = pool.animalDictionary[idAnimalA]
        moveHighSpeedTimeLineDic[idAnimalA] = {}
        
        print(pool.animalDictionary[idAnimalA])
        animalA.filterDetectionByInstantSpeed(parameters.HIGH_SPEED_MOVE_THRESHOLD, parameters.MAXIMUM_SPEED_THRESHOLD)
        
        moveHighSpeedTimeLine[idAnimalA].reBuildWithDictionary( animalA.detectionDictionary )
        moveHighSpeedTimeLine[idAnimalA].endRebuildEventTimeLine(connection)
            
    
    # log process
    t = TaskLogger( connection )
    t.addLog( f"Move high speed ({parameters.HIGH_SPEED_MOVE_THRESHOLD}-{parameters.MAXIMUM_SPEED_THRESHOLD})" , tmin=tmin, tmax=tmax )
    
    print( "Rebuild event finished." )
        
    