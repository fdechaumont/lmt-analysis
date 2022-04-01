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
    deleteEventTimeLineInBase(connection, "Move" )
    deleteEventTimeLineInBase(connection, "Move isolated" )
    deleteEventTimeLineInBase(connection, "Move in contact" )


def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None  ):
    ''' 
    Animal A is stopped (built-in event): revert the event to have move events
    Move social: animal A is moving and in contact with another animal.
    Move isolated: animal A is moving and not in contact with any other animal.
    ''' 
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )

    if len(pool.animalDictionnary.keys()) == 1:
        print('Only one animal in database.')
        '''if the animal has been tested alone, only the move isolated event will be computed.'''
        moveSourceTimeLine = {}

        animal = 1
        ''' Load source stop timeLine and revert it to get the move timeline
        If the animal is not detected, this will result in a move. To avoid this we mask with the detection.
        '''
        moveSourceTimeLine[animal] = EventTimeLine(connection, "Stop", animal, minFrame=tmin, maxFrame=tmax, inverseEvent=True)
        detectionTimeLine = EventTimeLine(connection, "Detection", animal, minFrame=tmin, maxFrame=tmax)
        moveSourceTimeLine[animal].keepOnlyEventCommonWithTimeLine(detectionTimeLine)

        # initialisation of a dic for isolated move
        moveIsolatedResult = {}

        ''' loop over eventlist'''
        for moveEvent in moveSourceTimeLine[animal].eventList:
            for t in range(moveEvent.startFrame, moveEvent.endFrame + 1):
                moveIsolatedResult[t] = True


        ''' save move isolated at the end of the complete process for animalA'''
        moveIsolatedResultTimeLine = EventTimeLine(None, "Move isolated", idA=animal, idB=None, idC=None, idD=None, loadEvent=False)
        moveIsolatedResultTimeLine.reBuildWithDictionnary(moveIsolatedResult)
        moveIsolatedResultTimeLine.endRebuildEventTimeLine(connection)


    else:
        print('More than one animal in database.')
        isInContactSourceDictionnary = {}
        moveSourceTimeLine = {}
        moveIsolatedTimeLine = {}

        for animal in pool.animalDictionnary.keys():
            ''' Load source stop timeLine and revert it to get the move timeline
            If the animal is not detected, this will result in a move. To avoid this we mask with the detection.
            '''
            moveSourceTimeLine[animal] = EventTimeLine( connection, "Stop", animal, minFrame=tmin, maxFrame=tmax, inverseEvent=True )
            detectionTimeLine = EventTimeLine( connection, "Detection", animal, minFrame=tmin, maxFrame=tmax )
            moveSourceTimeLine[animal].keepOnlyEventCommonWithTimeLine( detectionTimeLine )
            
            #by default let's say that all move are isolated; next we will extract frames which are in contact from this time line.
            moveIsolatedTimeLine[animal] = moveSourceTimeLine[animal]
            
            ''' load contact dictionary with another animal '''
            for animalB in pool.animalDictionnary.keys():
                if animal == animalB:
                    print('Same identity')
                    continue
                else:
                    isInContactSourceDictionnary[(animal, animalB)] = EventTimeLineCached( connection, file, "Contact", animal, animalB, minFrame=tmin, maxFrame=tmax ).getDictionnary()

        moveIsolatedDic = {}
        for animal in pool.animalDictionnary.keys():
            #initialisation of a dic for isolated move
            moveIsolatedDic[animal] = moveIsolatedTimeLine[animal].getDictionary()

            for animalB in pool.animalDictionnary.keys():
                # initialisation of a dic for move in contact for each individual of the cage
                framesToRemoveFromMoveIsolatedTimeLine = []
                moveSocialResult = {}
                if animal == animalB:
                    print('Same identity')
                    continue
                else:
                    ''' loop over eventlist'''
                    for moveEvent in moveIsolatedTimeLine[animal].eventList:

                        ''' for each event we seek in t and search a match in isInContactDictionnary between animal and animalB '''
                        for t in range ( moveEvent.startFrame, moveEvent.endFrame+1 ) :
                            if t in isInContactSourceDictionnary[(animal, animalB)]:
                                moveSocialResult[t] = True
                                framesToRemoveFromMoveIsolatedTimeLine.append(t)

                    ''' save move social at the end of the search for each animal'''
                    # clean the dictionary of the move and stop events from frames that are overlapping with exclusive contacts
                    for t in framesToRemoveFromMoveIsolatedTimeLine:
                        moveIsolatedDic[animal].pop(t, None)
                        
                    moveSocialResultTimeLine = EventTimeLine( None, "Move in contact" , idA=animal , idB=animalB , idC=None , idD=None , loadEvent=False )
                    moveSocialResultTimeLine.reBuildWithDictionnary( moveSocialResult )
                    moveSocialResultTimeLine.endRebuildEventTimeLine(connection)

            ''' save move isolated at the end of the complete process for animalA'''
            moveIsolatedResultTimeLine = EventTimeLine(None, "Move isolated", idA=animal, idB=None, idC=None, idD=None, loadEvent=False)
            moveIsolatedResultTimeLine.reBuildWithDictionnary(moveIsolatedDic[animal])
            moveIsolatedResultTimeLine.endRebuildEventTimeLine(connection)


        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Move" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
        
    