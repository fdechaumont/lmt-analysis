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
import matplotlib.pyplot as plt
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.Parameters import getAnimalTypeParameters
from lmtanalysis.TaskLogger import TaskLogger

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Get away" )


def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None, animalType=None ):
    '''    
    Get away: at least 1 animal should move, mouse A speed > mouse B speed & mouse A getting away from B.

    ''' 
    parameters = getAnimalTypeParameters( animalType )
    
    print("Escape")
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
    
    nbAnimal = pool.getNbAnimals()

    
            
    for animal in range( 1 , nbAnimal+1 ):
        
        for idAnimalB in range( 1 , nbAnimal+1 ):
            if( animal == idAnimalB ):
                continue
                        
            eventName = "Get away"        
            print ( eventName )
            
            getAwayTimeLine = EventTimeLine( None, eventName , animal , idAnimalB , None , None , loadEvent=False )

            result={}
            
            for t in range ( tmin, tmax+1 ):                
            
                animalA = pool.animalDictionary[animal]
                animalB = pool.animalDictionary[idAnimalB]
                
                if not ( t-1 in animalA.detectionDictionary ):
                    continue                
                if not ( t+1 in animalA.detectionDictionary ):
                    continue

                if not ( t-1 in animalB.detectionDictionary ):
                    continue                
                if not ( t+1 in animalB.detectionDictionary ):
                    continue
                                            
                speedA = animalA.getSpeed( t )
                speedB = animalB.getSpeed( t )
                
                if ( speedB > speedA ):
                    continue
                
                if ( speedA > parameters.SPEED_THRESHOLD_LOW or speedB > parameters.SPEED_THRESHOLD_LOW ):
                    
                    dAStart = animalA.detectionDictionary[t-1]
                    dAEnd = animalA.detectionDictionary[t+1]
                    dBStart = animalB.detectionDictionary[t-1]
                    dBEnd = animalB.detectionDictionary[t+1]
                    
                    distStart = dAStart.getDistanceTo( dBStart, parameters )
                    distEnd = dAEnd.getDistanceTo( dBEnd , parameters )
                    
                    if distStart != None and distEnd != None:
                        if( distStart < distEnd ):
                            result[t] = True
            
            
            getAwayTimeLine.reBuildWithDictionary( result )
            
            getAwayTimeLine.endRebuildEventTimeLine(connection)
        
    # log process
    
    t = TaskLogger( connection )
    t.addLog( "Build Event Get Away" , tmin=tmin, tmax=tmax )

             
    print( "Rebuild event finished." )
        
    