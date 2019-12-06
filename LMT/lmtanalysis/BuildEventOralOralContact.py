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


def distHeadHead( detA, detB ):
    
    hx = detA.frontX
    hy = detA.frontY
    bx = detB.frontX
    by = detB.frontY
    
    if ( hx == -1 or hy == -1 or bx == -1 or by == -1 ):
        return 100000
    
    return math.hypot( hx-bx, hy-by )


def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Oral-oral Contact" )

def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None ): 
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
    
    ''' deleteEventTimeLineInBase(connection, "Oral-oral Contact" ) '''
        
    '''
    contactDico = {}
    approachDico = {}
    for animal in range( 1 , pool.getNbAnimals()+1 ):
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if ( animal == idAnimalB ):
                continue
            
            contactDico[animal, idAnimalB] = EventTimeLine( connection, "Contact", animal, idAnimalB, minFrame=tmin, maxFrame=tmax )
            approachDico[animal, idAnimalB] = EventTimeLine( connection, "Social approach", animal, idAnimalB, minFrame=tmin, maxFrame=tmax ) #fait une matrice de toutes les aproches à deux possibles
    '''

    for animal in range( 1 , pool.getNbAnimals()+1 ):
        
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if( animal == idAnimalB ):
                continue
            
            ''' MAX_DISTANCE_HEAD_HEAD_GENITAL_THRESHOLD '''
            
            eventName = "Oral-oral Contact"        
            print ( eventName )
            
            result ={}
            animalA = pool.animalDictionnary.get( animal )
            animalB = pool.animalDictionnary.get( idAnimalB )            
            
            OralOralTimeLine = EventTimeLine( None, eventName , animal , idAnimalB , loadEvent=False )

            for t in animalA.detectionDictionnary.keys() :
                
                if ( t in animalB.detectionDictionnary ):
                    detA = animalA.detectionDictionnary[t]
                    detB = animalB.detectionDictionnary[t]
                            
                  
                                     
                    if distHeadHead( detA, detB ) < MAX_DISTANCE_HEAD_HEAD_GENITAL_THRESHOLD:
                        result[t] = True
            
            OralOralTimeLine.reBuildWithDictionnary( result )
            OralOralTimeLine.endRebuildEventTimeLine(connection)
            
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Oral Oral Contact" , tmin=tmin, tmax=tmax )
               
    print( "Rebuild event finished." )
        
    