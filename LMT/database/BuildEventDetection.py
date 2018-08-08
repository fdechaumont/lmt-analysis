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

def loadDetectionMap( connection, idAnimalA, start=None, end=None ):
    
        chrono = Chronometer("Build event detection: Load detection map")
        print( "processing animal ID: {}".format( idAnimalA ))

        result = {}
                
        cursor = connection.cursor()
        query = "SELECT FRAMENUMBER FROM DETECTION WHERE ANIMALID={}".format( idAnimalA )

        if ( start != None ):
            query += " AND FRAMENUMBER>={}".format(start )
        if ( end != None ):
            query += " AND FRAMENUMBER<={}".format(end )
            
        print( query )
        cursor.execute( query )
        
        rows = cursor.fetchall()
        cursor.close()    
        
        for row in rows:
            frameNumber = row[0]
            result[frameNumber] = True;
        
        print ( " detections loaded in {} seconds.".format( chrono.getTimeInS( )) )
        
        return result


def reBuildEvent( connection, tmin=None, tmax=None ): 
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    #pool.loadDetection( start = tmin, end = tmax )
    
    for idAnimalA in range( 1 , 5 ):
        
        eventName = "Detection"        
        print ( eventName )
            
        detectionTimeLine = EventTimeLine( None, eventName , idAnimalA , None , None , None , loadEvent=False )
         
        result = loadDetectionMap( connection , idAnimalA, tmin, tmax )
                                       
        #animal = pool.animalDictionnary[idAnimalA]
        #animal.loadDetection()
                    
        detectionTimeLine.reBuildWithDictionnary( result );
        detectionTimeLine.endRebuildEventTimeLine(connection)
    
    # log process
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Detection" , tmin=tmin, tmax=tmax )

       
    print( "Rebuild event finished." )
        
    