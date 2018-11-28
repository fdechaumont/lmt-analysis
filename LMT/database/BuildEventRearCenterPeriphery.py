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
from database.EventTimeLineCache import EventTimeLineCached

def reBuildEvent( connection, file, tmin=None, tmax=None ):
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    #pool.loadDetection( start = tmin, end = tmax )
    
    rear = {}
    for idAnimalA in range( 1 , 5 ):
        rear[idAnimalA] = EventTimeLineCached( connection, file, "Rear isolated", idAnimalA, minFrame=tmin, maxFrame=tmax )
    
    center = {}
    for idAnimalA in range( 1 , 5 ):
        center[idAnimalA] = EventTimeLineCached(connection, file, "Center Zone", idAnimalA, minFrame=tmin, maxFrame=tmax )
    
    periphery = {}
    for idAnimalA in range( 1 , 5 ):
        periphery[idAnimalA] = EventTimeLineCached(connection, file, "Periphery Zone", idAnimalA, minFrame=tmin, maxFrame=tmax )
    
    
    for idAnimalA in range( 1 , 5 ):
        
        eventName1 = "Rear in center"        
        print ( eventName1 )
        
        eventName2 = "Rear at periphery"
        print ( eventName2 )                    
        
        rearCenterTimeLine = EventTimeLine( None, eventName1 , idAnimalA , None , None , None , loadEvent=False )
        rearPeripheryTimeLine = EventTimeLine( None, eventName2 , idAnimalA , None , None , None , loadEvent=False )
                   
        resultCenter={}
        resultPeriphery={}
        dicRear = rear[ idAnimalA ].getDictionnary()
        dicCenter = center[ idAnimalA ].getDictionnary()
        dicPeriphery = periphery[ idAnimalA ].getDictionnary()
        
        for t in dicRear.keys():
            if ( t in dicCenter ):
                resultCenter[t] = True
                
            if (t in dicPeriphery ):
                resultPeriphery[t] = True
                            
        rearCenterTimeLine.reBuildWithDictionnary( resultCenter )               
        rearPeripheryTimeLine.reBuildWithDictionnary( resultPeriphery )            
        
        rearCenterTimeLine.endRebuildEventTimeLine(connection)
        rearPeripheryTimeLine.endRebuildEventTimeLine(connection)
                    
        
    # log process
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Rear in center" , tmin=tmin, tmax=tmax )
    t.addLog( "Build Event Rear at periphery" , tmin=tmin, tmax=tmax ) 
                    
    print( "Rebuild event finished." )
        
    