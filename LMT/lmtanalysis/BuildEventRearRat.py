'''
Created on 6 sept. 2017

@author: Fab
'''
import sqlite3
import numpy as np
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
from lmtanalysis.Parameters import getAnimalTypeParameters
from lmtanalysis.TaskLogger import TaskLogger

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Rearing" )
    deleteEventTimeLineInBase(connection, "RearR isolated" )
    deleteEventTimeLineInBase(connection, "RearR in contact" )
    deleteEventTimeLineInBase(connection, "Rear isolated" )
    deleteEventTimeLineInBase(connection, "Rear in contact" )


def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None, animalType=None ): 
    
    parameters = getAnimalTypeParameters( animalType)
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
    
    '''
    Event RearRat:
    - the animal is rearing
    - distinction between rearing in contact with one or several animals and rearing isolated from the others
    '''
        
    contact = {}
    
    for animal in pool.animalDictionary.keys():
        print(pool.animalDictionary[animal])
        
        contact[animal] = EventTimeLineCached( connection, file, "Contact", animal, minFrame=tmin, maxFrame=tmax )
        contactDico = contact[animal].getDictionary()
        
        eventName1 = "Rear isolated"
        eventName2 = "Rear in contact"
        print ( "A rears")        
                
        rearSocialTimeLine = EventTimeLine( None, eventName2 , animal , None , None , None , loadEvent=False )
        rearIsolatedTimeLine = EventTimeLine( None, eventName1 , animal , None , None , None , loadEvent=False )
                
        resultSocial={}
        resultIsolated={}
        
        animalA = pool.animalDictionary[animal]
        #print ( animalA )
        dicA = animalA.detectionDictionary
        slopeDic = {}
        
        #get the slope at each detection
        for t in dicA.keys():
            slopeDic[t] = dicA[t].getBackSlope()
        
        #compute the mean slope
        slopeList = []
        for t in slopeDic.keys():
            slopeList.append( slopeDic[t])
        print(f"slopeList ({len(slopeList)}): {slopeList[180:200]}")
        
        cleanSlopeList = [i for i in slopeList if i is not None]
        
        meanSlope = np.nanmean( cleanSlopeList )
        stdSlope = np.nanstd( cleanSlopeList )
        print (f"mean +/- std: {meanSlope}+/-{stdSlope}")
        
        #keep only detections where slope is above the threshold = mean + 0.5 std
        for t in dicA.keys():
            
            slope = slopeDic[t]
            if ( slope == None):
                continue
            
            if ( abs( slope ) < (meanSlope + 0.5*stdSlope) ):
                continue;
                
            if (t in contactDico.keys()):
                #print("social")
                resultSocial[t] = True
            
            else:
                #print("isolated")
                resultIsolated[t] = True
    
        rearSocialTimeLine.reBuildWithDictionary( resultSocial )
        rearIsolatedTimeLine.reBuildWithDictionary( resultIsolated )
        
        rearSocialTimeLine.endRebuildEventTimeLine( connection )
        rearIsolatedTimeLine.endRebuildEventTimeLine( connection )
        
        
    # log process
    
    t = TaskLogger( connection )
    t.addLog( "Build Event RearRat" , tmin=tmin, tmax=tmax )

                
    print( "Rebuild event finished." )
        
        
        
        
        
        
        
    