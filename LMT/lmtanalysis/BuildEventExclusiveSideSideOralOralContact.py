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
    deleteEventTimeLineInBase(connection, "Oral-oral Contact exclusive" )
    deleteEventTimeLineInBase(connection, "Side-side Contact exclusive")
    deleteEventTimeLineInBase(connection, "Oral-oral and Side-side Contact exclusive")

def reBuildEvent( connection, file, tmin=None, tmax=None , pool = None ): 

    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax , lightLoad=True )

    ''' load the existing timelines for each pair of animals '''
    timeLine = {}
    for event in ["Oral-oral Contact", "Side by side Contact"]:
        timeLine[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                timeLine[event][animal, idAnimalB] = EventTimeLineCached( connection, file, event, animal, idAnimalB, minFrame=tmin, maxFrame=tmax )

    ''' create the timelines of the different exclusive contacts '''
    timeLineExclusive = {}
    for event in ["Oral-oral Contact exclusive", "Side-side Contact exclusive", "Oral-oral and Side-side Contact exclusive"]:
        timeLineExclusive[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                timeLineExclusive[event][animal, idAnimalB] = EventTimeLine(None, event, animal, idAnimalB, loadEvent=False)

    contactDico = {}
    framesToRemove = {}
    for event in ["Oral-oral Contact", "Side by side Contact"]:
        contactDico[event] = {}
        framesToRemove[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                contactDico[event][animal, idAnimalB] = timeLine[event][animal, idAnimalB].getDictionary(minFrame=tmin, maxFrame=tmax)
                framesToRemove[event][animal, idAnimalB] = []

    contactDicoExclusive = {}
    for event in ["Oral-oral Contact exclusive", "Side-side Contact exclusive", "Oral-oral and Side-side Contact exclusive"]:
        contactDicoExclusive[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                contactDicoExclusive[event][animal, idAnimalB] = {}

    framesSideSide = {}
    framesOralOral = {}
    for animal in range(1, pool.getNbAnimals() + 1):
        for idAnimalB in range(1, pool.getNbAnimals() + 1):
            if (animal == idAnimalB):
                continue
            framesSideSide[animal, idAnimalB] = contactDico["Side by side Contact"][animal, idAnimalB].keys()
            framesOralOral[animal, idAnimalB] = contactDico['Oral-oral Contact'][animal, idAnimalB].keys()

            for t in framesSideSide[animal, idAnimalB]:
                print('t', t)

                if t in framesOralOral[animal, idAnimalB]:
                    framesToRemove['Side by side Contact'][animal, idAnimalB].append(t)
                    framesToRemove['Oral-oral Contact'][animal, idAnimalB].append(t)
                    contactDicoExclusive["Oral-oral and Side-side Contact exclusive"][animal, idAnimalB][t] = True

                else:
                    contactDicoExclusive["Side-side Contact exclusive"][animal, idAnimalB][t] = True

    for animal in range(1, pool.getNbAnimals() + 1):
        for idAnimalB in range(1, pool.getNbAnimals() + 1):
            if (animal == idAnimalB):
                continue
            for event in ["Oral-oral Contact", "Side by side Contact"]:
                for t in framesToRemove[event][animal, idAnimalB]:
                    contactDico[event][animal, idAnimalB].pop( t, None)

    for animal in range(1, pool.getNbAnimals() + 1):
        for idAnimalB in range(1, pool.getNbAnimals() + 1):
            if (animal == idAnimalB):
                continue

            timeLineExclusive["Side-side Contact exclusive"][animal, idAnimalB].reBuildWithDictionnary(contactDico["Side by side Contact"][animal, idAnimalB])
            timeLineExclusive["Side-side Contact exclusive"][animal, idAnimalB].endRebuildEventTimeLine(connection)

            timeLineExclusive["Oral-oral Contact exclusive"][animal, idAnimalB].reBuildWithDictionnary(
                contactDico["Oral-oral Contact"][animal, idAnimalB])
            timeLineExclusive["Oral-oral Contact exclusive"][animal, idAnimalB].endRebuildEventTimeLine(
                connection)

            timeLineExclusive["Oral-oral and Side-side Contact exclusive"][animal, idAnimalB].reBuildWithDictionnary(
                contactDicoExclusive["Oral-oral and Side-side Contact exclusive"][animal, idAnimalB])
            timeLineExclusive["Oral-oral and Side-side Contact exclusive"][animal, idAnimalB].endRebuildEventTimeLine(
                connection)

    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Exclusive oral-oral and side-side contacts" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
        
    