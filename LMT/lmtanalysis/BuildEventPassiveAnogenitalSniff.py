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
    deleteEventTimeLineInBase(connection, "Passive oral-genital Contact" )

def reBuildEvent( connection, file, tmin=None, tmax=None , pool = None ): 

    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax , lightLoad=True )

    ''' load the contact timeline for each pair of animals '''
    anogenitalSniffTimeLine = {}
    passiveAnogenitalSniffTimeLine = {}
    for animal in range( 1 , pool.getNbAnimals()+1 ):
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if ( animal == idAnimalB ):
                continue
            anogenitalSniffTimeLine[animal, idAnimalB] = EventTimeLineCached( connection, file, "Oral-genital Contact", animal, idAnimalB, minFrame=tmin, maxFrame=tmax )

            # create an empty timeline for other contacts
            passiveAnogenitalSniffTimeLine[idAnimalB, animal] = EventTimeLine(None, 'Passive oral-genital Contact', idAnimalB, animal, loadEvent=False)

    anogenitalSniffDico = {}
    for animal in range(1, pool.getNbAnimals() + 1):
        for idAnimalB in range(1, pool.getNbAnimals() + 1):
            if (animal == idAnimalB):
                continue
            anogenitalSniffDico[animal, idAnimalB] = anogenitalSniffTimeLine[animal, idAnimalB].getDictionary(minFrame=tmin, maxFrame=tmax)

            passiveAnogenitalSniffTimeLine[idAnimalB, animal].reBuildWithDictionnary(anogenitalSniffDico[animal, idAnimalB])
            passiveAnogenitalSniffTimeLine[idAnimalB, animal].endRebuildEventTimeLine(connection)


    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Passive oral-genital Contact" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
        
    