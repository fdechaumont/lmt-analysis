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
    deleteEventTimeLineInBase(connection, "Group4" )


def reBuildEvent( connection, file, tmin=None, tmax=None , pool = None ):
    '''
    four animals are in contact. (equivalent to group2 and group3)
    ''' 
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    #pool.loadDetection( start = tmin, end = tmax )
    
    
    contact = {}
    group2 = {}
    for animal in range( 1 , 5 ):    
        contact[animal] = EventTimeLineCached( connection, file, "Contact", animal, minFrame=tmin, maxFrame=tmax ) #fait une matrice de tous les contacts à deux possibles
        group2[animal] = EventTimeLineCached(connection, file, "Group2", animal, minFrame=tmin, maxFrame=tmax )
        
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
                
                    eventName = "Group4"        
                    print ( eventName )
                    
                    groupTimeLine = EventTimeLine( None, eventName , animal , idAnimalB , idAnimalC , idAnimalD , loadEvent=False )
                    
                    result={}
                    
                    dicA = contact[ animal ].getDictionnary()
                    dicB = contact[ idAnimalB ].getDictionnary()
                    dicC = contact[ idAnimalC ].getDictionnary()
                    dicD = contact[ idAnimalD ].getDictionnary()
                    
                    dicGroup2A = group2[ animal ].getDictionnary()
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
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Group4" , tmin=tmin, tmax=tmax )
          
    
    print( "Rebuild event finished." )
        
    