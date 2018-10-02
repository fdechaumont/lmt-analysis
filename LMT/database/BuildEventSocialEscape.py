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

def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None ): 
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
    
    nbAnimal = pool.getNbAnimals()
    
    escapeDico = {}
    for idAnimalA in range( 1 , nbAnimal+1 ):
        for idAnimalB in range( 1 , nbAnimal+1 ):
            if ( idAnimalA == idAnimalB ):
                continue
            
            escapeDico[idAnimalA, idAnimalB] = getEventTimeLineCached( connection, file, "Escape", idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax )

    #cache mean body len
    twoMeanBodyLen = {}
    for idAnimal in range( 1 , nbAnimal+1 ):
        twoMeanBodyLen[idAnimal] = 2*pool.animalDictionnary[idAnimal].getMeanBodyLength()
        
    
    for idAnimalA in range( 1 , nbAnimal+1 ):
        
        for idAnimalB in range( 1 , nbAnimal+1 ):
            if( idAnimalA == idAnimalB ):
                continue
            
            eventName = "Social escape"        
            print ( eventName )
            
            socEscTimeLine = EventTimeLine( None, eventName , idAnimalA , idAnimalB , None , None , loadEvent=False )
                           
            result={}
            
            dicA = escapeDico[ idAnimalA , idAnimalB ].getDictionnary()
            
            twoMeanBodyLengthB = twoMeanBodyLen[ idAnimalB ]
            
            for t in dicA.keys():
                dist = pool.animalDictionnary[idAnimalA].getDistanceTo(t, pool.animalDictionnary[idAnimalB])
                
                if ( dist == None ):
                    continue
                    
                if ( dist >= 0 and dist <= twoMeanBodyLengthB ):
                    result[t]=True
            
            
            socEscTimeLine.reBuildWithDictionnary( result )
            
            socEscTimeLine.endRebuildEventTimeLine(connection)
    
        
    # log process
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Social Escape" , tmin=tmin, tmax=tmax )

             
    print( "Rebuild event finished." )
        
    