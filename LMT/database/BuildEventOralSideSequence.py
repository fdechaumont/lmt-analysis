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
import numpy as np
from database.Event import *
from database.Measure import *
from affine import Affine
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from database.EventTimeLineCache import getEventTimeLineCached


def reBuildEvent( connection, tmin=None, tmax=None, pool = None ): 
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
    '''
    Event OralSide Sequence
    '''
    nbAnimal = pool.getNbAnimals()
    
    contact = {}
    oralOral = {}
    oralGenital = {}
    oralOralDico = {}
    oralGenitalDico = {}
    
    EVENT_MIN_LEN = 10
    
    for idAnimalB in pool.animalDictionnary.keys():
        print(pool.animalDictionnary[idAnimalB])
        meanSizeB = pool.animalDictionnary[idAnimalB].getMeanBodyLength( tmax = tmax )
        
        for idAnimalA in pool.animalDictionnary.keys():
            if( idAnimalB == idAnimalA ):
                continue
            
            '''
            contact[idAnimalA, idAnimalB] = EventTimeLine( connection, "Contact", idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax )
            '''
            oralOral[idAnimalA, idAnimalB] = getEventTimeLineCached( connection, "Oral-oral Contact", idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax )
            oralGenital[idAnimalA, idAnimalB] = getEventTimeLineCached( connection, "Oral-genital Contact", idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax )
            
            oralOralDico[idAnimalA, idAnimalB] = oralOral[idAnimalA, idAnimalB].getDictionnary()
            oralGenitalDico[idAnimalA, idAnimalB] = oralGenital[idAnimalA, idAnimalB].getDictionnary()
        
    
    

    window = 60

    '''    
    oral oral followed by a oral-genital
    '''
    eventName ="seq oral oral - oral genital"
    print ( eventName )                    
    
    for idAnimalA in range( 1 , nbAnimal+1 ):
        
        for idAnimalB in range( 1 , nbAnimal+1 ):
            if( idAnimalA == idAnimalB ):
                continue
        
                    
            selOO_OG_TimeLine = EventTimeLine( None, eventName , idAnimalA , idAnimalB , None , None , loadEvent=False )
            
            print( selOO_OG_TimeLine.eventNameWithId ) 
                    
            oralOralTimeLine = oralOral[ idAnimalA , idAnimalB ]
            
            oralGeniDico = oralGenitalDico[ idAnimalA , idAnimalB ]         
            oralGeniTimeLine = oralGenital[ idAnimalA , idAnimalB ]
            
            for event in oralOralTimeLine.eventList:
                
                endFrame = event.endFrame
                
                if ( event.duration() >= EVENT_MIN_LEN ):
                    continue

                for t in range ( endFrame , endFrame+window+1 ):
                    
                    if ( t in oralGeniDico ):
                        
                        event2 = oralGeniTimeLine.getEventAt( t )
                        
                        if ( event2.duration() >= EVENT_MIN_LEN ):
                        
                            start = event.startFrame
                            end = event2.endFrame
                            
                            selOO_OG_TimeLine.addEvent( Event( start, end ) )                        
                            break
                
            selOO_OG_TimeLine.endRebuildEventTimeLine(connection)
                    
    
    window = 60

    '''    
    oral A genital B followed by oral oral
    '''
    eventName ="seq oral geni - oral oral"
    print ( eventName )                    
    
    for idAnimalA in range( 1 , nbAnimal+1 ):
        
        for idAnimalB in range( 1 , nbAnimal+1 ):
            if( idAnimalA == idAnimalB ):
                continue
        
                    
            selOG_OO_TimeLine = EventTimeLine( None, eventName , idAnimalA , idAnimalB , None , None , loadEvent=False )
            
            print( selOG_OO_TimeLine.eventNameWithId ) 
                    
            oralGenitalTimeLine = oralGenital[ idAnimalA , idAnimalB ]
            
            ooDico = oralOralDico[ idAnimalA , idAnimalB ]         
            oralOralTimeLine = oralOral[ idAnimalA , idAnimalB ]
            
            for event in oralGenitalTimeLine.eventList:
                
                endFrame = event.endFrame
                
                if ( event.duration() >= EVENT_MIN_LEN ):
                    continue
                                
                for t in range ( endFrame , endFrame+window+1 ):
                    
                    if ( t in ooDico ):
                
                        event2 = oralOralTimeLine.getEventAt( t )
                                
                        if ( event2.duration() >= EVENT_MIN_LEN ):
                                
                            start = event.startFrame
                            end = event2.endFrame
                            
                            selOG_OO_TimeLine.addEvent( Event( start, end ) )                        
                            break
                
            selOG_OO_TimeLine.endRebuildEventTimeLine(connection)
                    
    
        
    # log process
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Oral Side Sequence" , tmin=tmin, tmax=tmax )

                    
    print( "Rebuild event finished." )
        
    