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
    deleteEventTimeLineInBase(connection, "Other contact" )

def reBuildEvent( connection, file, tmin=None, tmax=None , pool = None ): 

    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        #pool.loadDetection( start = tmin, end = tmax , lightLoad=True )

    ''' load the contact timeline for each pair of animals '''
    contactTimeLine = {}
    otherContactTimeLine = {}
    for animal in range( 1 , pool.getNbAnimals()+1 ):
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if ( animal == idAnimalB ):
                continue
            contactTimeLine[animal, idAnimalB] = EventTimeLineCached( connection, file, "Contact", animal, idAnimalB, minFrame=tmin, maxFrame=tmax )

            # create an empty timeline for other contacts
            otherContactTimeLine[animal, idAnimalB] = EventTimeLine(None, 'Other contact', animal, idAnimalB, loadEvent=False)

    ''' load the timelines of the different specific contacts '''
    timeLine = {}
    for event in ["Oral-oral Contact", "Oral-genital Contact", "Passive oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way"]:
        timeLine[event] = {}
        for animal in range(1, pool.getNbAnimals() + 1):
            for idAnimalB in range(1, pool.getNbAnimals() + 1):
                if (animal == idAnimalB):
                    continue
                timeLine[event][animal, idAnimalB] = EventTimeLineCached(connection, file, event, animal, idAnimalB, minFrame=tmin, maxFrame=tmax)
                '''# clean the specific contact timelines:
                timeLine[event][animal, idAnimalB].mergeCloseEvents(numberOfFrameBetweenEvent=1)
                timeLine[event][animal, idAnimalB].removeEventsBelowLength(maxLen=3)'''

    contactDico = {}
    for animal in range(1, pool.getNbAnimals() + 1):
        for idAnimalB in range(1, pool.getNbAnimals() + 1):
            if (animal == idAnimalB):
                continue
            contactDico[animal, idAnimalB] = contactTimeLine[animal, idAnimalB].getDictionary(minFrame=tmin, maxFrame=tmax)

            eventDico = {}
            for event in ["Oral-oral Contact", "Oral-genital Contact", "Passive oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way"]:
                eventDico[event] = timeLine[event][animal, idAnimalB].getDictionary(minFrame=tmin, maxFrame=tmax)
                '''remove the frames where the animals are in specific contacts'''
                for t in eventDico[event].keys():
                    contactDico[animal, idAnimalB].pop(t, None)

            otherContactTimeLine[animal, idAnimalB].reBuildWithDictionnary(contactDico[animal, idAnimalB])
            otherContactTimeLine[animal, idAnimalB].endRebuildEventTimeLine(connection)


    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Other contact" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
        
    