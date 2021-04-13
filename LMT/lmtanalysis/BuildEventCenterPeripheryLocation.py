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
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
#from affine import Affine
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Center Zone" )
    deleteEventTimeLineInBase(connection, "Periphery Zone" )
    

def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None ): 
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
    '''
    Event Center
    - the animal is in the center zone of the cage
    center zone: xa=149, xb=363, ya=318, yb=98
    
    Event Periphery
    - the animal is at the periphery of the cage (opposite event from Center)
    '''
    
    for animal in pool.animalDictionnary.keys():
        print(pool.animalDictionnary[animal])
        
        eventNameCenter = "Center Zone"
        print ( "A is in the center zone")        
        print ( eventNameCenter )
        
        eventNamePeriphery = "Periphery Zone"
        print ( "A is in the periphery zone")        
        print ( eventNamePeriphery )
                
        centerZoneTimeLine = EventTimeLine( None, eventNameCenter , animal , None , None , None , loadEvent=False )
        peripheryZoneTimeLine = EventTimeLine( None, eventNamePeriphery , animal , None , None , None , loadEvent=False )
                
        resultCenter={}
        resultPeriphery={}
        
        animalA = pool.animalDictionnary[animal]
        #print ( animalA )
        dicA = animalA.detectionDictionnary
            
        for t in dicA.keys():

            if (dicA[t].isInZone(xa=168, xb=343, ya=296, yb=120) == True):
                resultCenter[t] = True
                
            else:
                resultPeriphery[t] = True
                
        centerZoneTimeLine.reBuildWithDictionnary( resultCenter )
        centerZoneTimeLine.endRebuildEventTimeLine(connection)
    
        peripheryZoneTimeLine.reBuildWithDictionnary( resultPeriphery )
        peripheryZoneTimeLine.endRebuildEventTimeLine(connection)
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Center Zone" , tmin=tmin, tmax=tmax )
    t.addLog( "Build Event Periphery Zone" , tmin=tmin, tmax=tmax )

    print( "Rebuild event finished." )
        
        
        
        
        
        
        
    