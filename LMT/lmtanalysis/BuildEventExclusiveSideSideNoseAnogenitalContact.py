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
    deleteEventTimeLineInBase(connection, "Oral-genital Contact exclusive" )
    deleteEventTimeLineInBase(connection, "Side-side Contact, opposite exclusive")
    deleteEventTimeLineInBase(connection, "Oral-genital and Side-side Contact, opposite exclusive")
    deleteEventTimeLineInBase(connection, "Oral-genital passive and Side-side Contact, opposite exclusive")
    deleteEventTimeLineInBase(connection, "Passive oral-genital Contact exclusive")

def reBuildEvent( connection, file, tmin=None, tmax=None , pool = None ): 

    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax , lightLoad=True )

    ''' load the existing timelines for each pair of animals '''
    timeLine = {}
    for event in ["Oral-genital Contact", "Passive oral-genital Contact", "Side by side Contact, opposite way"]:
        timeLine[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                timeLine[event][animal, idAnimalB] = EventTimeLineCached( connection, file, event, animal, idAnimalB, minFrame=tmin, maxFrame=tmax )

    ''' create the timelines of the different exclusive contacts '''
    timeLineExclusive = {}
    for event in ["Oral-genital Contact exclusive", "Passive oral-genital Contact exclusive", "Side-side Contact, opposite exclusive", "Oral-genital and Side-side Contact, opposite exclusive", "Oral-genital passive and Side-side Contact, opposite exclusive"]:
        timeLineExclusive[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                timeLineExclusive[event][animal, idAnimalB] = EventTimeLine(None, event, animal, idAnimalB, loadEvent=False)

    contactDico = {}
    framesToRemove = {}
    for event in ["Oral-genital Contact", "Passive oral-genital Contact", "Side by side Contact, opposite way"]:
        contactDico[event] = {}
        framesToRemove[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                contactDico[event][animal, idAnimalB] = timeLine[event][animal, idAnimalB].getDictionary(minFrame=tmin, maxFrame=tmax)
                framesToRemove[event][animal, idAnimalB] = []

    contactDicoExclusive = {}
    for event in ["Oral-genital Contact exclusive", "Passive oral-genital Contact exclusive",
                  "Side-side Contact, opposite exclusive", "Oral-genital and Side-side Contact, opposite exclusive", "Oral-genital passive and Side-side Contact, opposite exclusive"]:
        contactDicoExclusive[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                contactDicoExclusive[event][animal, idAnimalB] = {}


    framesSideSide = {}
    framesOralGenital = {}
    framesOralGenitalPassive = {}
    for animal in range(1, pool.getNbAnimals() + 1):
        for idAnimalB in range(1, pool.getNbAnimals() + 1):
            if (animal == idAnimalB):
                continue
            framesSideSide[animal, idAnimalB] = contactDico["Side by side Contact, opposite way"][animal, idAnimalB].keys()
            framesOralGenital[animal, idAnimalB] = contactDico['Oral-genital Contact'][animal, idAnimalB].keys()
            framesOralGenitalPassive[animal, idAnimalB] = contactDico['Passive oral-genital Contact'][animal, idAnimalB].keys()

            for t in framesSideSide[animal, idAnimalB]:
                if t in framesOralGenital[animal, idAnimalB]:
                    framesToRemove['Side by side Contact, opposite way'][animal, idAnimalB].append(t)
                    framesToRemove['Oral-genital Contact'][animal, idAnimalB].append(t)
                    contactDicoExclusive["Oral-genital and Side-side Contact, opposite exclusive"][animal, idAnimalB][t] = True

                elif t in framesOralGenitalPassive[animal, idAnimalB]:
                    framesToRemove['Side by side Contact, opposite way'][animal, idAnimalB].append(t)
                    framesToRemove['Passive oral-genital Contact'][animal, idAnimalB].append(t)
                    contactDicoExclusive["Oral-genital passive and Side-side Contact, opposite exclusive"][animal, idAnimalB][t] = True

                else:
                    contactDicoExclusive["Side-side Contact, opposite exclusive"][animal, idAnimalB][t] = True


    for event in ["Oral-genital Contact", 'Passive oral-genital Contact', "Side by side Contact, opposite way"]:
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                for t in framesToRemove[event][animal, idAnimalB]:
                    contactDico[event][animal, idAnimalB].pop( t, None)

    for animal in range(1, pool.getNbAnimals() + 1):
        for idAnimalB in range(1, pool.getNbAnimals() + 1):
            if (animal == idAnimalB):
                continue

            timeLineExclusive["Side-side Contact, opposite exclusive"][animal, idAnimalB].reBuildWithDictionnary(contactDico["Side by side Contact, opposite way"][animal, idAnimalB])
            timeLineExclusive["Side-side Contact, opposite exclusive"][animal, idAnimalB].endRebuildEventTimeLine(connection)

            timeLineExclusive["Oral-genital Contact exclusive"][animal, idAnimalB].reBuildWithDictionnary(
                contactDico["Oral-genital Contact"][animal, idAnimalB])
            timeLineExclusive["Oral-genital Contact exclusive"][animal, idAnimalB].endRebuildEventTimeLine(
                connection)

            timeLineExclusive["Passive oral-genital Contact exclusive"][idAnimalB, animal].reBuildWithDictionnary(
                contactDico["Passive oral-genital Contact"][idAnimalB, animal])
            timeLineExclusive["Passive oral-genital Contact exclusive"][idAnimalB, animal].endRebuildEventTimeLine(
                connection)

            timeLineExclusive["Oral-genital and Side-side Contact, opposite exclusive"][animal, idAnimalB].reBuildWithDictionnary(
                contactDicoExclusive["Oral-genital and Side-side Contact, opposite exclusive"][animal, idAnimalB])
            timeLineExclusive["Oral-genital and Side-side Contact, opposite exclusive"][animal, idAnimalB].endRebuildEventTimeLine(
                connection)

            timeLineExclusive["Oral-genital passive and Side-side Contact, opposite exclusive"][idAnimalB, animal].reBuildWithDictionnary(
                contactDicoExclusive["Oral-genital passive and Side-side Contact, opposite exclusive"][idAnimalB, animal])
            timeLineExclusive["Oral-genital passive and Side-side Contact, opposite exclusive"][idAnimalB, animal].endRebuildEventTimeLine(
                connection)


    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Exclusive oral-genital & side-side opposite contacts" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
        
    