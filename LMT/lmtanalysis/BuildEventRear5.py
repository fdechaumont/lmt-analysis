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
from lmtanalysis.EventTimeLineCache import EventTimeLineCached

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Rear isolated" )
    deleteEventTimeLineInBase(connection, "Rear in contact" )


def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None ): 
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
    
    '''
    Event Rear5:
    - the animal is rearing
    - distinction between rearing in contact with one or several animals and rearing isolated from the others
    '''
        
    contact = {}
    
    for animal in pool.animalDictionnary.keys():
        print(pool.animalDictionnary[animal])
        
        contact[animal] = EventTimeLineCached( connection, file, "Contact", animal, minFrame=tmin, maxFrame=tmax )
        contactDico = contact[animal].getDictionnary()
        
        eventName1 = "Rear isolated"
        eventName2 = "Rear in contact"
        print ( "A rears")        
                
        rearSocialTimeLine = EventTimeLine( None, eventName2 , animal , None , None , None , loadEvent=False )
        rearIsolatedTimeLine = EventTimeLine( None, eventName1 , animal , None , None , None , loadEvent=False )
                
        resultSocial={}
        resultIsolated={}
        
        animalA = pool.animalDictionnary[animal]
        #print ( animalA )
        dicA = animalA.detectionDictionnary
            
        for t in dicA.keys():
            
            slope = dicA[t].getBodySlope()
            if ( slope == None):
                continue
            
            if ( abs( slope ) < BODY_SLOPE_THRESHOLD ):
                continue;
                
            if (t in contactDico.keys()):
                #print("social")
                resultSocial[t] = True
            
            else:
                #print("isolated")
                resultIsolated[t] = True
    
        rearSocialTimeLine.reBuildWithDictionnary( resultSocial )
        rearIsolatedTimeLine.reBuildWithDictionnary( resultIsolated )
        
        rearSocialTimeLine.endRebuildEventTimeLine( connection )
        rearIsolatedTimeLine.endRebuildEventTimeLine( connection )
        
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Rear5" , tmin=tmin, tmax=tmax )

                
    print( "Rebuild event finished." )
        
        
        
        
        
        
        
    