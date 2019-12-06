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
    deleteEventTimeLineInBase(connection, "Group 4 make" )
    deleteEventTimeLineInBase(connection, "Group 4 break" )


def reBuildEvent( connection, file, tmin=None, tmax=None , pool = None ):
    

    pool = AnimalPool( )
    pool.loadAnimals( connection )
    #pool.loadDetection( start = tmin, end = tmax )
    
    
    ''' load contact matrix '''
    contact = {}
    group4In = {}
    group4Out = {}
    
    for animal in range( 1 , 5 ):
        contact[animal] = EventTimeLineCached( connection, file, "Contact", animal, minFrame=tmin, maxFrame=tmax )
        group4In[animal] = EventTimeLine( connection, "Group 4 make", animal, loadEvent=False )
        group4Out[animal] = EventTimeLine( connection, "Group 4 break", animal, loadEvent=False )
        

    ''' process group '''
    
    for animal in range( 1 , 5 ):
        for idAnimalB in range( 1 , 5 ):
            for idAnimalC in range( 1 , 5 ):
                for idAnimalD in range( 1 , 5 ):

                    ''' check impossible combination (avoid 2 animals with same id) '''
                    
                    test = {}
                    test[animal] = True
                    test[idAnimalB] = True
                    test[idAnimalC] = True
                    test[idAnimalD] = True
                    if not len ( test.keys() ) == 4:
                        continue 
                    
                    ''' process group '''

                    group4 = EventTimeLineCached( connection, file, "Group4", animal, idAnimalB, idAnimalC, minFrame=tmin, maxFrame=tmax )
                    
                    eventList = group4.getEventList()
                    
                    for event in eventList:
                        
                        t = event.startFrame-1
    
                        if ( not contact[animal].hasEvent( t ) ):                        
                            group4In[animal].addPunctualEvent( t )
    
                        if ( not contact[idAnimalB].hasEvent( t ) ):                        
                            group4In[idAnimalB].addPunctualEvent( t )
    
                        if ( not contact[idAnimalC].hasEvent( t ) ):                        
                            group4In[idAnimalC].addPunctualEvent( t )

                        if ( not contact[idAnimalD].hasEvent( t ) ):                        
                            group4In[idAnimalD].addPunctualEvent( t )
                            
                        t = event.endFrame+1
    
                        if ( not contact[animal].hasEvent( t ) ):                        
                            group4Out[animal].addPunctualEvent( t )
    
                        if ( not contact[idAnimalB].hasEvent( t ) ):                        
                            group4Out[idAnimalB].addPunctualEvent( t )
    
                        if ( not contact[idAnimalC].hasEvent( t ) ):                        
                            group4Out[idAnimalC].addPunctualEvent( t )

                        if ( not contact[idAnimalD].hasEvent( t ) ):                        
                            group4Out[idAnimalD].addPunctualEvent( t )

                
    ''' save all '''
    for idAnimal in range( 1 , 5 ):
        
        group4In[idAnimal].endRebuildEventTimeLine(connection)
        group4Out[idAnimal].endRebuildEventTimeLine(connection)

        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Group4 Make Break" , tmin=tmin, tmax=tmax )
                                                
    print( "Rebuild event finished." )
        
    