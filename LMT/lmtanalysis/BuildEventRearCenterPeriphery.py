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
    deleteEventTimeLineInBase(connection, "Rear in centerWindow" )
    deleteEventTimeLineInBase(connection, "Rear at periphery" )


def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None  ):
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    #pool.loadDetection( start = tmin, end = tmax )
    
    rear = {}
    for animal in range( 1 , 5 ):
        rear[animal] = EventTimeLineCached( connection, file, "Rear isolated", animal, minFrame=tmin, maxFrame=tmax )
    
    centerWindow = {}
    for animal in range( 1 , 5 ):
        centerWindow[animal] = EventTimeLineCached(connection, file, "Center Zone", animal, minFrame=tmin, maxFrame=tmax )
    
    periphery = {}
    for animal in range( 1 , 5 ):
        periphery[animal] = EventTimeLineCached(connection, file, "Periphery Zone", animal, minFrame=tmin, maxFrame=tmax )
    
    
    for animal in range( 1 , 5 ):
        
        eventName1 = "Rear in centerWindow"        
        print ( eventName1 )
        
        eventName2 = "Rear at periphery"
        print ( eventName2 )                    
        
        rearCenterTimeLine = EventTimeLine( None, eventName1 , animal , None , None , None , loadEvent=False )
        rearPeripheryTimeLine = EventTimeLine( None, eventName2 , animal , None , None , None , loadEvent=False )
                   
        resultCenter={}
        resultPeriphery={}
        dicRear = rear[ animal ].getDictionnary()
        dicCenter = centerWindow[ animal ].getDictionnary()
        dicPeriphery = periphery[ animal ].getDictionnary()
        
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
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Rear in centerWindow" , tmin=tmin, tmax=tmax )
    t.addLog( "Build Event Rear at periphery" , tmin=tmin, tmax=tmax ) 
                    
    print( "Rebuild event finished." )
        
    