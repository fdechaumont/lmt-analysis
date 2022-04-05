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
    eventUndetected = 'Undetected exclusive'
    deleteEventTimeLineInBase(connection, eventUndetected)

def reBuildEvent( connection, file, tmin=None, tmax=None , pool = None ):
    eventUndetected = 'Undetected exclusive'
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )

    ''' load the existing detection timeline for animal '''
    detectionTimeLine = {}
    dicoDetection = {}
    undetectedTimeLine = {}
    for animal in range(1, pool.getNbAnimals() + 1):
        detectionTimeLine[animal] = EventTimeLineCached( connection, file, 'Detection', animal, minFrame=tmin, maxFrame=tmax )
        dicoDetection[animal] = detectionTimeLine[animal].getDictionary(minFrame=tmin, maxFrame=tmax)
        undetectedTimeLine[animal] = EventTimeLine(None, eventUndetected, animal, loadEvent=False)

    '''select the frames where the animals are not detected'''
    undetectedDico = {}
    for animal in range(1, pool.getNbAnimals() + 1):
        undetectedDico[animal] = {}
        for t in range(tmin, tmax+1):
            if t not in dicoDetection[animal]:
                undetectedDico[animal][t] = True


    #####################################################
    #reduild all events based on dictionary
    for animal in range(1, pool.getNbAnimals() + 1):
        undetectedTimeLine[animal].reBuildWithDictionnary(undetectedDico[animal])
        undetectedTimeLine[animal].endRebuildEventTimeLine(connection)

    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Exclusive undetected events" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
        
    