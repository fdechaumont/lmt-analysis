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
    

    pool = AnimalPool( )
    pool.loadAnimals( connection )
    #pool.loadDetection( start = tmin, end = tmax )
    
    
    ''' load contact matrix '''
    contact = {}
    group4In = {}
    group4Out = {}
    
    for idAnimalA in range( 1 , 5 ):
        contact[idAnimalA] = getEventTimeLineCached( connection, "Contact", idAnimalA, minFrame=tmin, maxFrame=tmax )
        group4In[idAnimalA] = EventTimeLine( connection, "Group 4 make", idAnimalA, loadEvent=False )
        group4Out[idAnimalA] = EventTimeLine( connection, "Group 4 break", idAnimalA, loadEvent=False )
        

    ''' process group '''
    
    for idAnimalA in range( 1 , 5 ):
        for idAnimalB in range( 1 , 5 ):
            for idAnimalC in range( 1 , 5 ):
                for idAnimalD in range( 1 , 5 ):

                    ''' check impossible combination (avoid 2 animals with same id) '''
                    
                    test = {}
                    test[idAnimalA] = True
                    test[idAnimalB] = True
                    test[idAnimalC] = True
                    test[idAnimalD] = True
                    if not len ( test.keys() ) == 4:
                        continue 
                    
                    ''' process group '''

                    group4 = getEventTimeLineCached( connection, "Group4", idAnimalA, idAnimalB, idAnimalC, minFrame=tmin, maxFrame=tmax )
                    
                    eventList = group4.getEventList()
                    
                    for event in eventList:
                        
                        t = event.startFrame-1
    
                        if ( not contact[idAnimalA].hasEvent( t ) ):                        
                            group4In[idAnimalA].addPunctualEvent( t )
    
                        if ( not contact[idAnimalB].hasEvent( t ) ):                        
                            group4In[idAnimalB].addPunctualEvent( t )
    
                        if ( not contact[idAnimalC].hasEvent( t ) ):                        
                            group4In[idAnimalC].addPunctualEvent( t )

                        if ( not contact[idAnimalD].hasEvent( t ) ):                        
                            group4In[idAnimalD].addPunctualEvent( t )
                            
                        t = event.endFrame+1
    
                        if ( not contact[idAnimalA].hasEvent( t ) ):                        
                            group4Out[idAnimalA].addPunctualEvent( t )
    
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
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Group4 Make Break" , tmin=tmin, tmax=tmax )
                                                
    print( "Rebuild event finished." )
        
    