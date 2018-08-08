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

def reBuildEvent( connection, tmin=None, tmax=None ): 
    
    '''
    two animals are following each others with nose-to-anogenital contacts
    animals are moving    
    '''
    
    deleteEventTimeLineInBase(connection, "Train2" )
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    pool.loadDetection( start = tmin, end = tmax )
                
    contactHeadGenital = {}
    for idAnimalA in range( 1,5 ):
        for idAnimalB in range( 1 , 5 ):
            if ( idAnimalA == idAnimalB ):
                continue
            contactHeadGenital[idAnimalA, idAnimalB] = EventTimeLine( connection, "Oral-genital Contact", idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax )

    '''
    contact = {}
    for idAnimalA in range( 1, 5 ):
        contact[idAnimalA] = EventTimeLine( connection, "Contact", idAnimalA, minFrame=tmin, maxFrame=tmax )
    '''
            
    for idAnimalA in range( 1 , 5 ):
        
        for idAnimalB in range( 1 , 5 ):

            if( idAnimalA == idAnimalB ):
                continue
                            
            eventName = "Train2"        
            print ( eventName )
            
            trainTimeLine = EventTimeLine( None, eventName , idAnimalA , idAnimalB, loadEvent=False )
            
            result={}
            
            dicAB = contactHeadGenital[ idAnimalA , idAnimalB ].getDictionnary()
            
            for t in dicAB.keys():
                speedA = pool.animalDictionnary[idAnimalA].getSpeed(t)
                speedB = pool.animalDictionnary[idAnimalB].getSpeed(t)
                        
                if ( speedA != None and speedB != None ):
                    if ( speedA > SPEED_THRESHOLD_HIGH and speedB > SPEED_THRESHOLD_HIGH ):
                        result[t]=True
            
            trainTimeLine.reBuildWithDictionnary( result )
            trainTimeLine.removeEventsBelowLength( 5 )            
            trainTimeLine.endRebuildEventTimeLine(connection)
    
        
    # log process
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Train2" , tmin=tmin, tmax=tmax )

                
    print( "Rebuild event finished." )
        
    
    
    