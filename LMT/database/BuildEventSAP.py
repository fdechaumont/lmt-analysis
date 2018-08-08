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

def reBuildEvent( connection, tmin=None, tmax=None ):
    
    ''' 
    Animal A is stopped (built-in event):
    Move social: animal A is stopped and in contact with any other animal.
    Move isolated: animal A is stopped and not in contact with any other animal.
    ''' 
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    
    
    for idAnimalA in pool.animalDictionnary:
        
        animal = pool.animalDictionnary[idAnimalA]
                
        SAPTimeLine = EventTimeLine( connection, "SAP", idAnimalA, minFrame=tmin, maxFrame=tmax, loadEvent=False )

        animal.loadDetection( )

        #f = animal.getCountFramesSpecZone( start , start+oneMinute*30 , xa=143, ya=190, xb=270, yb=317 )
        result = animal.getSapDictionnary( tmin , tmax )
            
        SAPTimeLine.reBuildWithDictionnary( result )
        SAPTimeLine.endRebuildEventTimeLine(connection)
        animal.clearDetection()
    
        
    # log process
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event SAP" , tmin=tmin, tmax=tmax )

               
    print( "Rebuild event finished." )
        
    