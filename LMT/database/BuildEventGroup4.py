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
    four animals are in contact. (equivalent to group2 and group3)
    ''' 
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    #pool.loadDetection( start = tmin, end = tmax )
    
    
    contact = {}
    group2 = {}
    for idAnimalA in range( 1 , 5 ):    
        contact[idAnimalA] = getEventTimeLineCached( connection, "Contact", idAnimalA, minFrame=tmin, maxFrame=tmax ) #fait une matrice de tous les contacts à deux possibles
        group2[idAnimalA] = getEventTimeLineCached(connection, "Group2", idAnimalA, minFrame=tmin, maxFrame=tmax )
        
    for idAnimalA in range( 1 , 5 ):
        
        for idAnimalB in range( 1 , 5 ):
            if( idAnimalA == idAnimalB ):
                continue
            
            for idAnimalC in range( 1 , 5 ):
                if( idAnimalA == idAnimalC ):
                    continue
                if( idAnimalB == idAnimalC ):
                    continue
                
                for idAnimalD in range( 1 , 5 ):
                    if( idAnimalA == idAnimalD ):
                        continue
                    if( idAnimalB == idAnimalD ):
                        continue
                    if( idAnimalC == idAnimalD ):
                        continue
                
                    eventName = "Group4"        
                    print ( eventName )
                    
                    groupTimeLine = EventTimeLine( None, eventName , idAnimalA , idAnimalB , idAnimalC , idAnimalD , loadEvent=False )
                    
                    result={}
                    
                    dicA = contact[ idAnimalA ].getDictionnary()
                    dicB = contact[ idAnimalB ].getDictionnary()
                    dicC = contact[ idAnimalC ].getDictionnary()
                    dicD = contact[ idAnimalD ].getDictionnary()
                    
                    dicGroup2A = group2[ idAnimalA ].getDictionnary()
                    dicGroup2B = group2[ idAnimalB ].getDictionnary()
                    dicGroup2C = group2[ idAnimalC ].getDictionnary()
                    dicGroup2D = group2[ idAnimalD ].getDictionnary()
                    
                    for t in dicA.keys():
                        if ( t in dicB and t in dicC and t in dicD ):
                            if ( t in dicGroup2A or t in dicGroup2B or t in dicGroup2C or t in dicGroup2D):
                                continue
                            else:
                                result[t]=True
                    
                    
    groupTimeLine.reBuildWithDictionnary( result )
    
    groupTimeLine.endRebuildEventTimeLine(connection)
          
        
    # log process
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Group4" , tmin=tmin, tmax=tmax )
          
    
    print( "Rebuild event finished." )
        
    