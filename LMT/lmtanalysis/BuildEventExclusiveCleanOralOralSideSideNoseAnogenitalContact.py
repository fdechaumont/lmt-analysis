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
    deleteEventTimeLineInBase(connection, "Other contact exclusive")

    deleteEventTimeLineInBase(connection, "Oral-genital Contact exclusive" )
    deleteEventTimeLineInBase(connection, "Side-side Contact, opposite exclusive")
    deleteEventTimeLineInBase(connection, "Oral-genital and Side-side Contact, opposite exclusive")
    deleteEventTimeLineInBase(connection, "Oral-genital passive and Side-side Contact, opposite exclusive")
    deleteEventTimeLineInBase(connection, "Passive oral-genital Contact exclusive")

    deleteEventTimeLineInBase(connection, "Oral-oral Contact exclusive")
    deleteEventTimeLineInBase(connection, "Side-side Contact exclusive")
    deleteEventTimeLineInBase(connection, "Oral-oral and Side-side Contact exclusive")

def reBuildEvent( connection, file, tmin=None, tmax=None , pool = None ):
    exclusiveEventList = ['Oral-oral Contact exclusive', 'Side-side Contact exclusive', 'Oral-genital Contact exclusive',
                       'Passive oral-genital Contact exclusive', 'Side-side Contact, opposite exclusive',
                       'Oral-oral and Side-side Contact exclusive',
                       'Oral-genital and Side-side Contact, opposite exclusive',
                       'Oral-genital passive and Side-side Contact, opposite exclusive', 'Other contact exclusive']

    contactTypeList = ["Oral-oral Contact", "Oral-genital Contact", "Passive oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Other contact"]

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
    for event in exclusiveEventList:
        timeLineExclusive[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                timeLineExclusive[event][animal, idAnimalB] = EventTimeLine(None, event, animal, idAnimalB, loadEvent=False)

    #generate the dico of the different contact types and initiate the list of frames to remove from each timeline
    contactDico = {}
    framesToRemove = {}
    for event in contactTypeList:
        contactDico[event] = {}
        framesToRemove[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                contactDico[event][animal, idAnimalB] = timeLine[event][animal, idAnimalB].getDictionary(minFrame=tmin, maxFrame=tmax)
                framesToRemove[event][animal, idAnimalB] = []

    # initiate the list of frames to remove from each timeline
    for event in exclusiveEventList:
        framesToRemove[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                framesToRemove[event][animal, idAnimalB] = []

    #initiate the dico that will be used to reconstruct the exclusve timelines
    contactDicoExclusive = {}
    for event in exclusiveEventList:
        contactDicoExclusive[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                contactDicoExclusive[event][animal, idAnimalB] = {}

    # save the dictionary of contact types as exclusive contacts before cleaning them
    eventPairs = {'Oral-oral Contact': 'Oral-oral Contact exclusive',
                  'Side by side Contact': 'Side-side Contact exclusive',
                  'Side by side Contact, opposite way': 'Side-side Contact, opposite exclusive',
                  'Oral-genital Contact': 'Oral-genital Contact exclusive',
                  'Passive oral-genital Contact': 'Passive oral-genital Contact exclusive',
                  'Other contact': 'Other contact exclusive'}
    for eventPair in eventPairs.keys():
        contactDicoExclusive[eventPairs[eventPair]] = contactDico[eventPair]

    ###########################################################################
    # clean the timelines of contactTypes where different contactTypes are overlapping
    for animal in range(1, pool.getNbAnimals() + 1):
        for idAnimalB in range(1, pool.getNbAnimals() + 1):
            if (animal == idAnimalB):
                continue

            for t in contactDico['Oral-oral Contact'][animal, idAnimalB].keys():
                if t in contactDico['Oral-genital Contact'][animal, idAnimalB].keys():
                    contactDicoExclusive['Other contact exclusive'][animal, idAnimalB][t] = True
                    framesToRemove['Oral-oral Contact exclusive'][animal, idAnimalB].append(t)
                    framesToRemove['Oral-genital Contact exclusive'][animal, idAnimalB].append(t)
                    framesToRemove['Oral-genital and Side-side Contact, opposite exclusive'][animal, idAnimalB].append(t)
                    framesToRemove['Oral-oral and Side-side Contact exclusive'][animal, idAnimalB].append(t)

                if t in contactDico['Passive oral-genital Contact'][animal, idAnimalB].keys():
                    contactDicoExclusive['Other contact exclusive'][animal, idAnimalB][t] = True
                    framesToRemove['Oral-oral Contact exclusive'][animal, idAnimalB].append(t)
                    framesToRemove['Passive oral-genital Contact exclusive'][animal, idAnimalB].append(t)
                    framesToRemove['Oral-genital passive and Side-side Contact, opposite exclusive'][animal, idAnimalB].append(t)
                    framesToRemove['Oral-oral and Side-side Contact exclusive'][animal, idAnimalB].append(t)

    ###########################################################################
    #exclude the side-side opposite contacts where animals are also in oral-genital sniffing
    for animal in range(1, pool.getNbAnimals() + 1):
        for idAnimalB in range(1, pool.getNbAnimals() + 1):
            if (animal == idAnimalB):
                continue

            for t in contactDico["Side by side Contact, opposite way"][animal, idAnimalB].keys():
                if t in contactDico['Oral-genital Contact'][animal, idAnimalB].keys():
                    framesToRemove['Side-side Contact, opposite exclusive'][animal, idAnimalB].append(t)
                    framesToRemove['Oral-genital Contact exclusive'][animal, idAnimalB].append(t)
                    framesToRemove['Passive oral-genital Contact exclusive'][idAnimalB, animal].append(t)
                    contactDicoExclusive["Oral-genital and Side-side Contact, opposite exclusive"][animal, idAnimalB][t] = True

                elif t in contactDico['Passive oral-genital Contact'][animal, idAnimalB].keys():
                    framesToRemove['Side-side Contact, opposite exclusive'][animal, idAnimalB].append(t)
                    framesToRemove['Passive oral-genital Contact exclusive'][animal, idAnimalB].append(t)
                    framesToRemove['Oral-genital Contact exclusive'][idAnimalB, animal].append(t)
                    contactDicoExclusive["Oral-genital passive and Side-side Contact, opposite exclusive"][animal, idAnimalB][t] = True

                else:
                    contactDicoExclusive["Side-side Contact, opposite exclusive"][animal, idAnimalB][t] = True

    ###########################################################################
    # exclude the side-side contacts where animals are also in oral-oral sniffing
    for animal in range(1, pool.getNbAnimals() + 1):
        for idAnimalB in range(1, pool.getNbAnimals() + 1):
            if (animal == idAnimalB):
                continue

            for t in contactDico["Side by side Contact"][animal, idAnimalB].keys():
                if t in contactDico['Oral-oral Contact'][animal, idAnimalB].keys():
                    framesToRemove['Side-side Contact exclusive'][animal, idAnimalB].append(t)
                    framesToRemove['Oral-oral Contact exclusive'][animal, idAnimalB].append(t)
                    contactDicoExclusive["Oral-oral and Side-side Contact exclusive"][animal, idAnimalB][t] = True

                else:
                    contactDicoExclusive["Side-side Contact exclusive"][animal, idAnimalB][t] = True


    ###########################################################################
    # clean the dictionary of the contactTypes from frames that are overlaping with other contactTypes
    for event in contactTypeList:
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                for t in framesToRemove[event][animal, idAnimalB]:
                    contactDico[event][animal, idAnimalB].pop(t, None)



    ############################################################################
    #  clean the dictionary of exclusive events that can co-occur but that are not intuitive (but link to the contact distance threshold used to reconstruct the contactTypes)
    # selecting the frames from the side-side timelines which are also in oral-oral, oral-genital and passive oral-genital timelines
    for animal in range(1, pool.getNbAnimals() + 1):
        for idAnimalB in range(1, pool.getNbAnimals() + 1):
            if (animal == idAnimalB):
                continue

            for t in contactDicoExclusive['Oral-oral Contact exclusive'][animal, idAnimalB]:
                if t in contactDicoExclusive['Side-side Contact, opposite exclusive'][animal, idAnimalB]:
                    framesToRemove['Side-side Contact, opposite exclusive'][animal, idAnimalB].append(t)

            for t in contactDicoExclusive["Oral-genital Contact exclusive"][animal, idAnimalB]:
                if t in contactDicoExclusive['Side-side Contact exclusive'][animal, idAnimalB]:
                    framesToRemove['Side-side Contact exclusive'][animal, idAnimalB].append(t)

            for t in contactDicoExclusive["Passive oral-genital Contact exclusive"][animal, idAnimalB]:
                if t in contactDicoExclusive['Side-side Contact exclusive'][animal, idAnimalB]:
                    framesToRemove['Side-side Contact exclusive'][animal, idAnimalB].append(t)


    # taking out the frames from the exclusive timelines
    for event in exclusiveEventList:
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                for t in framesToRemove[event][animal, idAnimalB]:
                    contactDicoExclusive[event][animal, idAnimalB].pop(t, None)


    #####################################################
    #reduild all events based on dictionary
    for event in exclusiveEventList:
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue

                timeLineExclusive[event][animal, idAnimalB].reBuildWithDictionnary(contactDicoExclusive[event][animal, idAnimalB])
                timeLineExclusive[event][animal, idAnimalB].endRebuildEventTimeLine(connection)


    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Exclusive oral-oral, oral-genital & side-side opposite contacts" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
        
    