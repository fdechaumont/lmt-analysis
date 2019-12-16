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
    deleteEventTimeLineInBase(connection, "Group2" )


def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None  ):
 

    pool = AnimalPool( )
    pool.loadAnimals( connection )
    #pool.loadDetection( start = tmin, end = tmax )
    
    
    contact = {}
    for animal in range( 1 , 5 ):
        for idAnimalB in range( 1 , 5 ):
            if ( animal == idAnimalB ):
                continue
            contact[animal, idAnimalB] = EventTimeLineCached( connection, file, "Contact", animal, idAnimalB, minFrame=tmin, maxFrame=tmax ) #fait une matrice de tous les contacts à deux possibles

    for animal in range( 1 , 5 ):
        
        for idAnimalB in range( 1 , 5 ):
            if( animal == idAnimalB ):
                continue
            
            for idAnimalC in range( 1 , 5 ):
                if( animal == idAnimalC ):
                    continue
                if( idAnimalB == idAnimalC ):
                    continue
                
                for idAnimalD in range( 1 , 5 ):
                    if( animal == idAnimalD ):
                        continue
                    if( idAnimalB == idAnimalD ):
                        continue
                    if( idAnimalC == idAnimalD ):
                        continue
                
                    eventName = "Group2"        
                    print ( eventName )
                    
                    groupTimeLine = EventTimeLine( None, eventName , animal , idAnimalB , None , None , loadEvent=False )
                    
                    result={}
                    
                    dicAB = contact[ animal , idAnimalB ].getDictionnary()
                    dicAC = contact[ animal , idAnimalC ].getDictionnary()
                    dicAD = contact[ animal , idAnimalD ].getDictionnary()
                    dicBC = contact[ idAnimalB , idAnimalC ].getDictionnary()
                    dicBD = contact[ idAnimalB , idAnimalD ].getDictionnary()
                    
                    
                    for t in dicAB.keys():
                        if ( t in dicAC or t in dicAD or t in dicBC or t in dicBD ):
                            continue
                        
                        else:
                            result[t]=True
                    
                    
            groupTimeLine.reBuildWithDictionnary( result )
            
            groupTimeLine.endRebuildEventTimeLine(connection)
    
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Group 2" , tmin=tmin, tmax=tmax )

                           
    print( "Rebuild event finished." )
        
    