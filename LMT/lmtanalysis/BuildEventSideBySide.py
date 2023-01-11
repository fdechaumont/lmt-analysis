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
from lmtanalysis.Parameters import getAnimalTypeParameters
from lmtanalysis.TaskLogger import TaskLogger

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Side by side Contact" )

def distHeadHead( detA, detB ):
    
    hx = detA.frontX
    hy = detA.frontY
    bx = detB.frontX
    by = detB.frontY
    
    if ( hx == -1 or hy == -1 or bx == -1 or by == -1 ):
        return 100000
    
    return math.hypot( hx-bx, hy-by )

def distBackBack( detA, detB ):
    
    hx = detA.backX
    hy = detA.backY
    bx = detB.backX
    by = detB.backY
    
    if ( hx == -1 or hy == -1 or bx == -1 or by == -1 ):
        return 100000
    
    return math.hypot( hx-bx, hy-by )

def isSameWay( detA, detB ):
    
    vectAX = detA.frontX - detA.backX
    vectAY = detA.frontY - detA.backY

    vectBX = detB.frontX - detB.backX
    vectBY = detB.frontY - detB.backY
    
    scalarProduct = vectAX * vectBX + vectAY * vectBY
    
    if ( scalarProduct >= 0 ): #same direction
        return True
    
    return False
    

def isSideBySide( detA, detB, parameters ):
    
    if not detA.isHeadAndTailDetected():
        return False
    
    if not detB.isHeadAndTailDetected():
        return False
    
    if not isSameWay( detA, detB ):
        return False
    
    if distHeadHead( detA, detB ) > parameters.MAX_DISTANCE_HEAD_HEAD_GENITAL_THRESHOLD*2:
        return False

    if distBackBack( detA, detB ) > parameters.MAX_DISTANCE_HEAD_HEAD_GENITAL_THRESHOLD*2:
        return False
    
    return True

    
def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None, animalType=None ): 
    
    parameters = getAnimalTypeParameters( animalType)
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
    
    for animal in range( 1 , pool.getNbAnimals()+1 ):
        
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if( animal == idAnimalB ):
                continue
            
            eventName = "Side by side Contact"        
            print ( eventName )
            
            result ={}
            animalA = pool.animalDictionnary.get( animal )
            animalB = pool.animalDictionnary.get( idAnimalB )            
            
            SideBySideTimeLine = EventTimeLine( None, eventName , animal , idAnimalB , loadEvent=False )

            for t in animalA.detectionDictionary.keys() :
                
                if ( t in animalB.detectionDictionary ):

                    detA = animalA.detectionDictionary[t]
                    detB = animalB.detectionDictionary[t]
                    
                    if ( isSideBySide( detA, detB, parameters ) == True ):
                                                
                        result[t] = True
                        
            SideBySideTimeLine.reBuildWithDictionary( result )
            SideBySideTimeLine.endRebuildEventTimeLine(connection)
            
        
    # log process
    
    t = TaskLogger( connection )
    t.addLog( "Build Event Side by side" , tmin=tmin, tmax=tmax )

               
    print( "Rebuild event finished." )
        
    