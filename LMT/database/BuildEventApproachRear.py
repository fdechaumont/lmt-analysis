'''
Created on 6 sept. 2017

@author: Fab
'''
import sqlite3
from time import *
from database.Chronometer import Chronometer
from database.Animal import *
from database.Detection import *
from database.Measure import *
import matplotlib.pyplot as plt
import numpy as np
from database.Event import *
from database.Measure import *
from database.EventTimeLineCache import getEventTimeLineCached

def reBuildEvent( connection, file, tmin=None, tmax=None ):
    ''' 
    Animal A is approaching the animal B, that is in a reared posture at the end of the approach of animal A.
    Social approaches are considered, meaning that the two animals are within 2 body lengths of one another.
    Rearings are considered "in contact" given that the computation is done on the last second of an approach.
    ''' 
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    #pool.loadDetection( start = tmin, end = tmax )
    
    rearDico = {}
    approachDico = {}
    dicoEventRearAnimal = {}
    for idAnimalA in range( 1 , 5 ):

        rearDico[idAnimalA] = EventTimeLine( connection, "Rear in contact", idAnimalA, None, minFrame=tmin, maxFrame=tmax )
        dicoEventRearAnimal[idAnimalA] = rearDico[idAnimalA].getDictionnary()

        for idAnimalB in range( 1 , 5 ):
            if ( idAnimalA == idAnimalB ):
                continue
             
            approachDico[idAnimalA, idAnimalB] = getEventTimeLineCached( connection, file, "Social approach", idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax ) #fait une matrice de toutes les aproches à deux possibles

    for idAnimalA in range( 1 , 5 ):
        
        for idAnimalB in range( 1 , 5 ):
            if( idAnimalA == idAnimalB ):
                continue
            
            eventName = "Approach rear"        
            print ( eventName )
            
            appRearTimeLine = EventTimeLine( None, eventName , idAnimalA , idAnimalB , None , None , loadEvent=False )
            
            
            for eventApp in approachDico[idAnimalA, idAnimalB].eventList:
                
                ''' new code: '''
                
                for t in range( eventApp.endFrame - TIME_WINDOW_BEFORE_EVENT, eventApp.endFrame + TIME_WINDOW_BEFORE_EVENT + 1 ):
                    
                    if ( t in dicoEventRearAnimal[idAnimalB] ):
                        appRearTimeLine.eventList.append(eventApp)
                        break
                        
                '''
                previous(slow) code
                
                for eventRear in rearDico[idAnimalB].eventList:
                    if (eventRear.overlapInT(eventApp.endFrame-TIME_WINDOW_BEFORE_EVENT, eventApp.endFrame+TIME_WINDOW_BEFORE_EVENT) == True):
                        appRearTimeLine.eventList.append(eventApp)
                '''
                
            appRearTimeLine.endRebuildEventTimeLine(connection)
            
    # log process
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Approach Rear" , tmin=tmin, tmax=tmax )

       
    print( "Rebuild event finished." )
        
    