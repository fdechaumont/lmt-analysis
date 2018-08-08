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
    
    isInContactSourceDictionnary = {}
    moveSourceTimeLine = {}
    
    for idAnimalA in range( 1 , 5 ):
        ''' Load source stop timeLine '''
        moveSourceTimeLine[idAnimalA] = EventTimeLine( connection, "Stop", idAnimalA, minFrame=tmin, maxFrame=tmax, inverseEvent=True )
        ''' load contact dictionnary with whatever animal '''
        isInContactSourceDictionnary[idAnimalA] = EventTimeLine( connection, "Contact", idAnimalA, minFrame=tmin, maxFrame=tmax ).getDictionnary()
                    
    
    for idAnimalA in range( 1 , 5 ):

        moveSocialResult = {}
        moveIsolatedResult = {}
        
        ''' loop over eventlist'''
        for moveEvent in moveSourceTimeLine[idAnimalA].eventList:
        
            ''' for each event we seek in t and search a match in isInContactDictionnary '''
            for t in range ( moveEvent.startFrame, moveEvent.endFrame+1 ) :
                if t in isInContactSourceDictionnary[idAnimalA]:
                    moveSocialResult[t] = True
                else:
                    moveIsolatedResult[t] = True
    
        ''' save move '''
        moveResultTimeLine = EventTimeLine( None, "Move" , idAnimalA , None , None , None , loadEvent=False )
        moveResultTimeLine.reBuildWithDictionnary( moveSourceTimeLine[idAnimalA].getDictionnary() )
        moveResultTimeLine.endRebuildEventTimeLine(connection)

        ''' save move isolated '''
        moveIsolatedResultTimeLine = EventTimeLine( None, "Move isolated" , idAnimalA , None , None , None , loadEvent=False )
        moveIsolatedResultTimeLine.reBuildWithDictionnary( moveIsolatedResult )
        moveIsolatedResultTimeLine.endRebuildEventTimeLine(connection)

        ''' save move social '''
        moveSocialResultTimeLine = EventTimeLine( None, "Move in contact" , idAnimalA , None , None , None , loadEvent=False )
        moveSocialResultTimeLine.reBuildWithDictionnary( moveSocialResult )
        moveSocialResultTimeLine.endRebuildEventTimeLine(connection)

        
    # log process
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Move" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
        
    