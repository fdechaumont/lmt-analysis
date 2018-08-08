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


def distHeadBack( detA, detB ):
    
    hx = detA.frontX
    hy = detA.frontY
    bx = detB.backX
    by = detB.backY
    
    if ( hx == -1 or hy == -1 or bx == -1 or by == -1 ):
        return 100000
    
    return math.hypot( hx-bx, hy-by )
    
def reBuildEvent( connection, tmin=None, tmax=None ): 
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    pool.loadDetection( start = tmin, end = tmax )
    

    for idAnimalA in range( 1 , pool.getNbAnimals()+1 ):
        
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if( idAnimalA == idAnimalB ):
                continue
            
            ''' MAX_DISTANCE_HEAD_HEAD_GENITAL_THRESHOLD '''
            
            eventName = "Oral-genital Contact"        
            print ( eventName )
            
            result ={}
            animalA = pool.animalDictionnary.get( idAnimalA )
            animalB = pool.animalDictionnary.get( idAnimalB )            
            
            OralGenitalTimeLine = EventTimeLine( None, eventName , idAnimalA , idAnimalB , loadEvent=False )

            for t in animalA.detectionDictionnary.keys() :
                
                if ( t in animalB.detectionDictionnary ):
                    detA = animalA.detectionDictionnary[t]
                    detB = animalB.detectionDictionnary[t]
                    
                    if distHeadBack( detA, detB ) < MAX_DISTANCE_HEAD_HEAD_GENITAL_THRESHOLD:
                        result[t] = True
            
            OralGenitalTimeLine.reBuildWithDictionnary( result )
            OralGenitalTimeLine.endRebuildEventTimeLine(connection)
    
        
    # log process
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Oral Genital Contact" , tmin=tmin, tmax=tmax )
        
                   
    print( "Rebuild event finished." )
        
    