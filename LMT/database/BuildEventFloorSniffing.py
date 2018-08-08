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



def reBuildEvent( connection, tmin, tmax ): 
    '''
    Event Floor sniffing:
    - the animal is sniffing the floor
    '''
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    pool.loadDetection( start = tmin, end = tmax )
    
    for idAnimalA in pool.animalDictionnary.keys():
        print(pool.animalDictionnary[idAnimalA])
        
        eventName = "Floor sniffing"
        print ( "A sniffs the floor")        
        print ( eventName )
                
        trainTimeLine = EventTimeLine( None, eventName , idAnimalA , None , None , None , loadEvent=False )
                
        result={}
        
        animalA = pool.animalDictionnary[idAnimalA]
        #print ( animalA )
        dicA = animalA.detectionDictionnary
            
        for t in dicA.keys():
            if (animalA.getBodySlope(t) == None):
                continue
            
            if (animalA.getBodySlope(t) >= -25 and animalA.getBodySlope(t) <= -15):
                #print("floor sniffing")
                result[t] = True
                
        
        trainTimeLine.reBuildWithDictionnary( result )
                
        trainTimeLine.endRebuildEventTimeLine(connection)
    
        
    # log process
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Floor sniffing" , tmin=tmin, tmax=tmax )

    print( "Rebuild event finished." )
        
        
        
        
        
        
        
    