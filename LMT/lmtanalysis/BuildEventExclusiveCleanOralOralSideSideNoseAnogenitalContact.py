'''
Created on 15 Feb. 2022

@author: Elodie
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
from lmtanalysis.BehaviouralSequencesUtil import exclusiveEventList, contactTypeList

def flush( connection ):
    ''' flush event in database '''
    for exclusiveEvent in exclusiveEventList[:-3]:
        deleteEventTimeLineInBase(connection, exclusiveEvent)

def reBuildEvent( connection, file, tmin=None, tmax=None , pool = None ):

    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )

    ''' load the existing timelines for each pair of animals '''
    timeLine = {}
    for event in contactTypeList:
        timeLine[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                timeLine[event][animal, idAnimalB] = EventTimeLineCached( connection, file, event, animal, idAnimalB, minFrame=tmin, maxFrame=tmax )

    ''' create the timelines of the different exclusive contacts '''
    timeLineExclusive = {}
    for event in exclusiveEventList[:-3]:
        timeLineExclusive[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                timeLineExclusive[event][animal, idAnimalB] = EventTimeLine(None, event, animal, idAnimalB, loadEvent=False)

    #generate the dico of the different contact types
    contactDico = {}
    for event in contactTypeList:
        contactDico[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                contactDico[event][animal, idAnimalB] = timeLine[event][animal, idAnimalB].getDictionary(minFrame=tmin, maxFrame=tmax)


    # initiate the list of frames to remove from each timeline
    framesToRemove = {}
    for exclusiveEvent in exclusiveEventList[:-3]:
        framesToRemove[exclusiveEvent] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                framesToRemove[exclusiveEvent][animal, idAnimalB] = []

    # initiate the dico that will be used to reconstruct the exclusive timelines
    contactDicoExclusive = {}
    for exclusiveEvent in exclusiveEventList[:-3]:
        print('############# ', exclusiveEvent)
        contactDicoExclusive[exclusiveEvent] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                contactDicoExclusive[exclusiveEvent][animal, idAnimalB] = {}

    # save the dictionary of contact types as exclusive contacts before cleaning them
    eventPairs = {}
    for event in contactTypeList:
        eventPairs[event] = event+' exclusive'

    for event in eventPairs.keys():
        contactDicoExclusive[eventPairs[event]] = contactDico[event]

    ###########################################################################
    # clean the timelines of contactTypes where different contactTypes are overlapping and are not intuitive
    for animal in range(1, pool.getNbAnimals() + 1):
        for idAnimalB in range(1, pool.getNbAnimals() + 1):
            if (animal == idAnimalB):
                continue
            eventA = 'Oral-oral Contact'
            eventB = 'Oral-genital Contact'
            for t in contactDico[eventA][animal, idAnimalB].keys():
                if t in contactDico[eventB][animal, idAnimalB].keys():
                    contactDicoExclusive['Other contact exclusive'][animal, idAnimalB][t] = True
                    framesToRemove[eventA+' exclusive'][animal, idAnimalB].append(t)
                    framesToRemove[eventB+' exclusive'][animal, idAnimalB].append(t)

            eventA = 'Oral-oral Contact'
            eventB = 'Passive oral-genital Contact'
            for t in contactDico[eventA][animal, idAnimalB].keys():
                if t in contactDico[eventB][animal, idAnimalB].keys():
                    contactDicoExclusive['Other contact exclusive'][animal, idAnimalB][t] = True
                    framesToRemove[eventA + ' exclusive'][animal, idAnimalB].append(t)
                    framesToRemove[eventB + ' exclusive'][animal, idAnimalB].append(t)

            eventA = 'Oral-oral Contact'
            eventB = 'Side by side Contact, opposite way'
            for t in contactDico[eventA][animal, idAnimalB].keys():
                if t in contactDico[eventB][animal, idAnimalB].keys():
                    contactDicoExclusive['Other contact exclusive'][animal, idAnimalB][t] = True
                    framesToRemove[eventA + ' exclusive'][animal, idAnimalB].append(t)
                    framesToRemove[eventB + ' exclusive'][animal, idAnimalB].append(t)

            eventA = 'Side by side Contact'
            eventB = 'Side by side Contact, opposite way'
            for t in contactDico[eventA][animal, idAnimalB].keys():
                if t in contactDico[eventB][animal, idAnimalB].keys():
                    contactDicoExclusive['Other contact exclusive'][animal, idAnimalB][t] = True
                    framesToRemove[eventA + ' exclusive'][animal, idAnimalB].append(t)
                    framesToRemove[eventB + ' exclusive'][animal, idAnimalB].append(t)

            eventA = 'Side by side Contact'
            eventB = 'Oral-genital Contact'
            for t in contactDico[eventA][animal, idAnimalB].keys():
                if t in contactDico[eventB][animal, idAnimalB].keys():
                    contactDicoExclusive['Other contact exclusive'][animal, idAnimalB][t] = True
                    framesToRemove[eventA + ' exclusive'][animal, idAnimalB].append(t)
                    framesToRemove[eventB + ' exclusive'][animal, idAnimalB].append(t)

            eventA = 'Side by side Contact'
            eventB = 'Passive oral-genital Contact'
            for t in contactDico[eventA][animal, idAnimalB].keys():
                if t in contactDico[eventB][animal, idAnimalB].keys():
                    contactDicoExclusive['Other contact exclusive'][animal, idAnimalB][t] = True
                    framesToRemove[eventA + ' exclusive'][animal, idAnimalB].append(t)
                    framesToRemove[eventB + ' exclusive'][animal, idAnimalB].append(t)


    ###########################################################################
    #exclude the side-side opposite contacts where animals are also in oral-genital sniffing
    for animal in range(1, pool.getNbAnimals() + 1):
        for idAnimalB in range(1, pool.getNbAnimals() + 1):
            if (animal == idAnimalB):
                continue

            for t in contactDico["Side by side Contact, opposite way"][animal, idAnimalB].keys():
                if t in contactDico['Oral-genital Contact'][animal, idAnimalB].keys():
                    if t not in contactDicoExclusive['Other contact exclusive'][animal, idAnimalB].keys():
                        framesToRemove['Side by side Contact, opposite way exclusive'][animal, idAnimalB].append(t)
                        framesToRemove['Oral-genital Contact exclusive'][animal, idAnimalB].append(t)
                        framesToRemove['Passive oral-genital Contact exclusive'][idAnimalB, animal].append(t)
                        contactDicoExclusive["Oral-genital and Side by side Contact, opposite way exclusive"][animal, idAnimalB][t] = True

                elif t in contactDico['Passive oral-genital Contact'][animal, idAnimalB].keys():
                    if t not in contactDicoExclusive['Other contact exclusive'][animal, idAnimalB].keys():
                        framesToRemove['Side by side Contact, opposite way exclusive'][animal, idAnimalB].append(t)
                        framesToRemove['Passive oral-genital Contact exclusive'][animal, idAnimalB].append(t)
                        framesToRemove['Oral-genital Contact exclusive'][idAnimalB, animal].append(t)
                        contactDicoExclusive['Oral-genital passive and Side by side Contact, opposite way exclusive'][animal, idAnimalB][t] = True

                else:
                    contactDicoExclusive["Side by side Contact, opposite way exclusive"][animal, idAnimalB][t] = True

    ###########################################################################
    # exclude the side-side contacts where animals are also in oral-oral sniffing
    for animal in range(1, pool.getNbAnimals() + 1):
        for idAnimalB in range(1, pool.getNbAnimals() + 1):
            if (animal == idAnimalB):
                continue

            for t in contactDico["Side by side Contact"][animal, idAnimalB].keys():
                if t in contactDico['Oral-oral Contact'][animal, idAnimalB].keys():
                    framesToRemove['Side by side Contact exclusive'][animal, idAnimalB].append(t)
                    framesToRemove['Oral-oral Contact exclusive'][animal, idAnimalB].append(t)
                    framesToRemove['Other contact exclusive'][animal, idAnimalB].append(t)
                    contactDicoExclusive["Oral-oral and Side by side Contact exclusive"][animal, idAnimalB][t] = True

                else:
                    contactDicoExclusive["Side by side Contact exclusive"][animal, idAnimalB][t] = True


    #############################################################
    # taking out the frames from the exclusive timelines
    for event in exclusiveEventList[:-3]:
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                for t in framesToRemove[event][animal, idAnimalB]:
                    contactDicoExclusive[event][animal, idAnimalB].pop(t, None)


    #####################################################
    #reduild all events based on dictionary
    for event in exclusiveEventList[:-3]:
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue

                timeLineExclusive[event][animal, idAnimalB].reBuildWithDictionnary(contactDicoExclusive[event][animal, idAnimalB])
                timeLineExclusive[event][animal, idAnimalB].endRebuildEventTimeLine(connection)


    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Exclusive oral-oral, oral-genital & side-side contacts" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
        
    