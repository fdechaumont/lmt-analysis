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
#from affine import Affine
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from lmtanalysis.EventTimeLineCache import EventTimeLineCached

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "seq oral oral - oral genital" )
    deleteEventTimeLineInBase(connection, "seq oral geni - oral oral" )

def reBuildEvent( connection, file,  tmin=None, tmax=None, pool = None ): 
    
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
        
        for animal in pool.animalDictionnary.keys():
            if( idAnimalB == animal ):
                continue
            
            '''
            contact[animal, idAnimalB] = EventTimeLine( connection, "Contact", animal, idAnimalB, minFrame=tmin, maxFrame=tmax )
            '''
            oralOral[animal, idAnimalB] = EventTimeLineCached( connection, file, "Oral-oral Contact", animal, idAnimalB, minFrame=tmin, maxFrame=tmax )
            oralGenital[animal, idAnimalB] = EventTimeLineCached( connection, file, "Oral-genital Contact", animal, idAnimalB, minFrame=tmin, maxFrame=tmax )
            
            oralOralDico[animal, idAnimalB] = oralOral[animal, idAnimalB].getDictionnary()
            oralGenitalDico[animal, idAnimalB] = oralGenital[animal, idAnimalB].getDictionnary()
        
    
    

    window = 60

    '''    
    oral oral followed by a oral-genital
    '''
    eventName ="seq oral oral - oral genital"
    print ( eventName )                    
    
    for animal in range( 1 , nbAnimal+1 ):
        
        for idAnimalB in range( 1 , nbAnimal+1 ):
            if( animal == idAnimalB ):
                continue
        
                    
            selOO_OG_TimeLine = EventTimeLine( None, eventName , animal , idAnimalB , None , None , loadEvent=False )
            
            print( selOO_OG_TimeLine.eventNameWithId ) 
                    
            oralOralTimeLine = oralOral[ animal , idAnimalB ]
            
            oralGeniDico = oralGenitalDico[ animal , idAnimalB ]         
            oralGeniTimeLine = oralGenital[ animal , idAnimalB ]
            
            for event in oralOralTimeLine.eventList:
                
                endFrame = event.endFrame
                
                if ( event.duration() <= EVENT_MIN_LEN ):  # discard too short events
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
    
    for animal in range( 1 , nbAnimal+1 ):
        
        for idAnimalB in range( 1 , nbAnimal+1 ):
            if( animal == idAnimalB ):
                continue
        
                    
            selOG_OO_TimeLine = EventTimeLine( None, eventName , animal , idAnimalB , None , None , loadEvent=False )
            
            print( selOG_OO_TimeLine.eventNameWithId ) 
                    
            oralGenitalTimeLine = oralGenital[ animal , idAnimalB ]
            
            ooDico = oralOralDico[ animal , idAnimalB ]         
            oralOralTimeLine = oralOral[ animal , idAnimalB ]
            
            for event in oralGenitalTimeLine.eventList:
                
                endFrame = event.endFrame
                
                if ( event.duration() <= EVENT_MIN_LEN ): # discard too short events
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
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Oral Side Sequence" , tmin=tmin, tmax=tmax )

                    
    print( "Rebuild event finished." )
        
    