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
    deleteEventTimeLineInBase(connection, "Stop in contact" )
    deleteEventTimeLineInBase(connection, "Stop isolated" )



def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None ):
    
    
    ''' 
    Animal A is stopped (built-in event):
    Stop in contact: animal A is stopped and in contact with another animal.
    Stop isolated: animal A is stopped and not in contact with any other animal.
    ''' 
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )

    if len(pool.animalDictionnary.keys()) == 1:
        print('Only one animal in database.')
        # if the animal has been tested alone, only the stop isolated event will be computed.'''
        stopSourceTimeLine = {}

        animal = 1
        # Load source stop timeLine and revert it to get the move timeline
        # If the animal is not detected, this will result in a move. To avoid this we mask with the detection.
        
        stopSourceTimeLine[animal] = EventTimeLine(connection, "Stop", animal, minFrame=tmin, maxFrame=tmax, inverseEvent=False)
        detectionTimeLine = EventTimeLine(connection, "Detection", animal, minFrame=tmin, maxFrame=tmax)
        stopSourceTimeLine[animal].keepOnlyEventCommonWithTimeLine(detectionTimeLine)

        # initialisation of a dic for isolated stop
        stopIsolatedResult = {}

        # loop over eventlist
        for stopEvent in stopSourceTimeLine[animal].eventList:
            for t in range(stopEvent.startFrame, stopEvent.endFrame + 1):
                stopIsolatedResult[t] = True

        # save stop isolated at the end of the complete process for animalA
        stopIsolatedResultTimeLine = EventTimeLine(None, "Stop isolated", idA=animal, idB=None, idC=None, idD=None, loadEvent=False)
        stopIsolatedResultTimeLine.reBuildWithDictionnary(stopIsolatedResult)
        stopIsolatedResultTimeLine.endRebuildEventTimeLine(connection)


    else:
        print('More than one animal in database.')
        isInContactSourceDictionnary = {}
        stopSourceTimeLine = {}
        stopIsolatedTimeLine = {}

        for animal in pool.animalDictionnary.keys():
            # Load source stop timeLine
            # If the animal is not detected, this will result in a stop. To avoid this we mask with the detection.
            
            stopSourceTimeLine[animal] = EventTimeLine( connection, "Stop", animal, minFrame=tmin, maxFrame=tmax, inverseEvent=False )
            detectionTimeLine = EventTimeLine( connection, "Detection", animal, minFrame=tmin, maxFrame=tmax )
            stopSourceTimeLine[animal].keepOnlyEventCommonWithTimeLine( detectionTimeLine )
            
            #by default let's say that all stops are isolated; next we will extract frames which are in contact from this time line.
            stopIsolatedTimeLine[animal] = stopSourceTimeLine[animal]
            
            # load contact dictionary with another animal
            for animalB in pool.animalDictionnary.keys():
                if animal == animalB:
                    print('Same identity')
                    continue
                else:
                    isInContactSourceDictionnary[(animal, animalB)] = EventTimeLineCached( connection, file, "Contact", animal, animalB, minFrame=tmin, maxFrame=tmax ).getDictionnary()

        stopIsolatedDic = {}
        for animal in pool.animalDictionnary.keys():
            #initialisation of a dic for isolated stop
            stopIsolatedDic[animal] = stopIsolatedTimeLine[animal].getDictionary()

            for animalB in pool.animalDictionnary.keys():
                # initialisation of a dic for stop in contact for each individual of the cage
                framesToRemoveFromStopIsolatedTimeLine = []
                stopSocialResult = {}
                if animal == animalB:
                    print('Same identity')
                    continue
                
                # loop over eventlist
                for stopEvent in stopIsolatedTimeLine[animal].eventList:

                    # for each event we seek in t and search a match in isInContactDictionnary between animal and animalB
                    for t in range ( stopEvent.startFrame, stopEvent.endFrame+1 ) :
                        if t in isInContactSourceDictionnary[(animal, animalB)]:
                            stopSocialResult[t] = True
                            framesToRemoveFromStopIsolatedTimeLine.append(t)                        

                # save stop social at the end of the search for each animal
                # clean the dictionary of the stop events from frames that are overlapping with exclusive contacts
                
                for t in framesToRemoveFromStopIsolatedTimeLine:
                    stopIsolatedDic[animal].pop( t, None )                    
                    
                stopSocialResultTimeLine = EventTimeLine( None, "Stop in contact" , idA=animal , idB=animalB , idC=None , idD=None , loadEvent=False )
                stopSocialResultTimeLine.reBuildWithDictionnary( stopSocialResult )
                stopSocialResultTimeLine.endRebuildEventTimeLine(connection)

            # save stop isolated at the end of the complete process for animalA
            stopIsolatedResultTimeLine = EventTimeLine(None, "Stop isolated", idA=animal, idB=None, idC=None, idD=None, loadEvent=False)
            stopIsolatedResultTimeLine.reBuildWithDictionnary(stopIsolatedDic[animal])
            stopIsolatedResultTimeLine.endRebuildEventTimeLine(connection)



        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Stop" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
    
    
    