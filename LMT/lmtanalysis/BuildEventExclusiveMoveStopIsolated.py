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
from lmtanalysis.BehaviouralSequencesUtil import exclusiveEventList

def flush( connection ):
    ''' flush event in database '''
    for exclusiveEvent in exclusiveEventList[-3:-1]:
        deleteEventTimeLineInBase(connection, exclusiveEvent)

def reBuildEvent( connection, file, tmin=None, tmax=None , pool = None ):
    moveEventList = ['Move isolated', 'Stop isolated']

    moveEventListExclusive = exclusiveEventList[-3:-1]

    eventPairs = {'Move isolated': 'Move isolated exclusive',
                  'Stop isolated': 'Stop isolated exclusive'}

    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )

    ''' load the existing timelines for animal '''
    timeLine = {}
    dicoContact = {}
    for event in moveEventList+exclusiveEventList[:-3]:
        timeLine[event] = {}
        dicoContact[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            timeLine[event][animal] = EventTimeLineCached( connection, file, event, animal, minFrame=tmin, maxFrame=tmax )
            dicoContact[event][animal] = timeLine[event][animal].getDictionary(minFrame=tmin, maxFrame=tmax)

    ''' create the timelines of the different exclusive moves '''
    timeLineExclusive = {}
    for event in moveEventListExclusive:
        timeLineExclusive[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            timeLineExclusive[event][animal] = EventTimeLine(None, event, animal, loadEvent=False)

    #generate the dico of the different move events and initiate the list of frames to remove from each timeline
    moveDicoExclusive = {}
    framesToRemove = {}
    for event in moveEventList:
        moveDicoExclusive[eventPairs[event]] = {}
        framesToRemove[eventPairs[event]] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            moveDicoExclusive[eventPairs[event]][animal] = timeLine[event][animal].getDictionary(minFrame=tmin, maxFrame=tmax)
            framesToRemove[eventPairs[event]][animal] = []

    ###########################################################################
    #exclude the move and stop events where animals are in contacts
    for animal in range(1, pool.getNbAnimals() + 1):
        for moveEvent in exclusiveEventList[-3:-1]:
            for t in moveDicoExclusive[moveEvent][animal].keys():
                for contactEvent in exclusiveEventList[:-3]:
                    if t in dicoContact[contactEvent][animal].keys():
                        print('t = ', t, 'in', moveEvent, ' and in ', contactEvent)
                        framesToRemove[moveEvent][animal].append(t)

    ###########################################################################
    # clean the dictionary of the move and stop events from frames that are overlapping with exclusive contacts
    for animal in range(1, pool.getNbAnimals() + 1):
        for moveEvent in exclusiveEventList[-3:-1]:
            for t in framesToRemove[moveEvent][animal]:
                moveDicoExclusive[moveEvent][animal].pop(t, None)

    #####################################################
    #reduild all events based on dictionary
    for moveEvent in exclusiveEventList[-3:-1]:
        for animal in range(1, pool.getNbAnimals() + 1):
            timeLineExclusive[moveEvent][animal].reBuildWithDictionnary(moveDicoExclusive[moveEvent][animal])
            timeLineExclusive[moveEvent][animal].endRebuildEventTimeLine(connection)

    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Exclusive move and stop events" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
        
    