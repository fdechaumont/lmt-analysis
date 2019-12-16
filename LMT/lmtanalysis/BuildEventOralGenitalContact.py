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

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Oral-genital Contact" )

def distHeadBack( detA, detB ):
    
    hx = detA.frontX
    hy = detA.frontY
    bx = detB.backX
    by = detB.backY
    
    if ( hx == -1 or hy == -1 or bx == -1 or by == -1 ):
        return 100000
    
    return math.hypot( hx-bx, hy-by )
    
def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None ): 
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
    
    for animal in range( 1 , pool.getNbAnimals()+1 ):
        
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if( animal == idAnimalB ):
                continue
            
            ''' MAX_DISTANCE_HEAD_HEAD_GENITAL_THRESHOLD '''
            
            eventName = "Oral-genital Contact"        
            print ( eventName )
            
            result ={}
            animalA = pool.animalDictionnary.get( animal )
            animalB = pool.animalDictionnary.get( idAnimalB )            
            
            OralGenitalTimeLine = EventTimeLine( None, eventName , animal , idAnimalB , loadEvent=False )

            for t in animalA.detectionDictionnary.keys() :
                
                if ( t in animalB.detectionDictionnary ):
                    detA = animalA.detectionDictionnary[t]
                    detB = animalB.detectionDictionnary[t]
                    
                    if distHeadBack( detA, detB ) < MAX_DISTANCE_HEAD_HEAD_GENITAL_THRESHOLD:
                        result[t] = True
            
            OralGenitalTimeLine.reBuildWithDictionnary( result )
            OralGenitalTimeLine.endRebuildEventTimeLine(connection)
    
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Oral Genital Contact" , tmin=tmin, tmax=tmax )
        
                   
    print( "Rebuild event finished." )
        
    