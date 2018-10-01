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

def reBuildEvent( connection, tmin=None, tmax=None ):
    
    ''' 
    Animal A is stopped (built-in event):
    Stop social: animal A is stopped and in contact with any other animal.
    Stop isolated: animal A is stopped and not in contact with any other animal.
    ''' 
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    #pool.loadDetection( start = tmin, end = tmax )
    
    isInContactSourceDictionnary = {}
    stopSourceTimeLine = {}
    
    for idAnimalA in range( 1 , 5 ):
        ''' Load source stop timeLine '''
        stopSourceTimeLine[idAnimalA] = getEventTimeLineCached( connection, "Stop", idAnimalA, minFrame=tmin, maxFrame=tmax )
        ''' load contact dictionnary with whatever animal '''
        isInContactSourceDictionnary[idAnimalA] = getEventTimeLineCached( connection, "Contact", idAnimalA, minFrame=tmin, maxFrame=tmax ).getDictionnary()
                    
    eventName2 = "Stop in contact"
    eventName1 = "Stop isolated"        
    
    for idAnimalA in range( 1 , 5 ):

        print ( eventName1, eventName2 )
                
        stopSocialResult = {}
        stopIsolatedResult = {}
        
        ''' loop over eventlist'''
        for stopEvent in stopSourceTimeLine[idAnimalA].eventList:
        
            ''' for each event we seek in t and search a match in isInContactDictionnary '''
            for t in range ( stopEvent.startFrame, stopEvent.endFrame+1 ) :
                if t in isInContactSourceDictionnary[idAnimalA]:
                    stopSocialResult[t] = True
                else:
                    stopIsolatedResult[t] = True
        
        ''' save stop social '''
        stopSocialResultTimeLine = EventTimeLine( None, eventName2 , idAnimalA , None , None , None , loadEvent=False )
        stopSocialResultTimeLine.reBuildWithDictionnary( stopSocialResult )
        stopSocialResultTimeLine.endRebuildEventTimeLine(connection)

        ''' save stop isolated '''
        stopIsolatedResultTimeLine = EventTimeLine( None, eventName1 , idAnimalA , None , None , None , loadEvent=False )
        stopIsolatedResultTimeLine.reBuildWithDictionnary( stopIsolatedResult )
        stopIsolatedResultTimeLine.endRebuildEventTimeLine(connection)

        
    # log process
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Stop" , tmin=tmin, tmax=tmax )

                   
    print( "Rebuild event finished." )
        
    