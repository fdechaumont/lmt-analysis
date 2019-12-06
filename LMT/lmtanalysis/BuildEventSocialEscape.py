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

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Social escape" )


def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None ): 
    
    print("STARTING SOCIAL ESCAPE")
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
    
    nbAnimal = pool.getNbAnimals()

    # loading all the escape of animals    
    getAwayDico = {}
    for animal in range( 1 , nbAnimal+1 ):
        for idAnimalB in range( 1 , nbAnimal+1 ):
            if ( animal == idAnimalB ):
                continue
            
            getAwayDico[animal, idAnimalB] = EventTimeLineCached( connection, file, "Get away", animal, idAnimalB, minFrame=tmin, maxFrame=tmax )

    #cache mean body len
    twoMeanBodyLen = {}
    for idAnimal in range( 1 , nbAnimal+1 ):
        
        meanBodyLength = pool.animalDictionnary[idAnimal].getMeanBodyLength()
        # init value
        twoMeanBodyLen[idAnimal] = None
        # set value
        if meanBodyLength != None:
            twoMeanBodyLen[idAnimal] = 2*meanBodyLength
        
    
    for animal in range( 1 , nbAnimal+1 ):
        
        for idAnimalB in range( 1 , nbAnimal+1 ):
            if( animal == idAnimalB ):
                continue
            
            eventName = "Social escape"        
            print ( eventName )
            
            socEscTimeLine = EventTimeLine( None, eventName , animal , idAnimalB , None , None , loadEvent=False )
                           
            result={}
            
            dicA = getAwayDico[ animal , idAnimalB ].getDictionnary()
            
            twoMeanBodyLengthB = twoMeanBodyLen[ idAnimalB ]
            
            for t in dicA.keys():
                dist = pool.animalDictionnary[animal].getDistanceTo(t, pool.animalDictionnary[idAnimalB])
                
                if ( dist == None ):
                    continue
                    
                if ( dist >= 0 and dist <= twoMeanBodyLengthB ):
                    result[t]=True
            
            
            socEscTimeLine.reBuildWithDictionnary( result )
            
            socEscTimeLine.endRebuildEventTimeLine(connection)
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Social Escape" , tmin=tmin, tmax=tmax )

             
    print( "Rebuild event finished." )
        
    