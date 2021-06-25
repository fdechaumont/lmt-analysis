'''
Created on 2. February 2021

@author: Elodie
'''
import sqlite3
from time import *
from lmtanalysis.Chronometer import Chronometer
from lmtanalysis.Animal import *
from lmtanalysis.Detection import *
from lmtanalysis.Measure import *
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
#from affine import Affine
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "SniffFamiliar" )
    deleteEventTimeLineInBase(connection, "SniffNew" )


def reBuildEvent( connection, objectPosition, radiusObjects, objectTuple, side, tmin=None, tmax=None, pool = None ):
    deleteEventTimeLineInBase(connection, "SniffFamiliar" )
    deleteEventTimeLineInBase(connection, "SniffNew")
    deleteEventTimeLineInBase(connection, "upFamiliar")
    deleteEventTimeLineInBase(connection, "upNew")


    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
        pool.filterDetectionByInstantSpeed(0, 70)
    '''
    Event SniffFamiliar
    - the animal's nose is in a zone 3 cm around the familiar object
    
    Event SniffNew
    - the animal's nose is in a zone 3 cm around the new object
    
    Event upFamiliar
    - the animal is on the familiar object
    
    Event upNew
    - the animal is on the new object
    '''
    
    for animal in pool.animalDictionnary.keys():
        print(pool.animalDictionnary[animal])
        
        eventNameSniffFamiliar = "SniffFamiliar"
        print ( "A is around the familiar object")
        print ( eventNameSniffFamiliar )
        
        eventNameSniffNew = "SniffNew"
        print ( "A is around new object")
        print ( eventNameSniffNew )

        eventNameUpFamiliar = "UpFamiliar"
        print("A is on the familiar object")
        print(eventNameUpFamiliar)

        eventNameUpNew = "UpNew"
        print("A is on new object")
        print(eventNameUpNew)
                
        sniffFamiliarTimeLine = EventTimeLine( None, eventNameSniffFamiliar , animal , None , None , None , loadEvent=False )
        sniffNewTimeLine = EventTimeLine( None, eventNameSniffNew , animal , None , None , None , loadEvent=False )
        upFamiliarTimeLine = EventTimeLine(None, eventNameUpFamiliar, animal, None, None, None, loadEvent=False)
        upNewTimeLine = EventTimeLine(None, eventNameUpNew, animal, None, None, None, loadEvent=False)

        resultSniffFamiliar = {}
        resultSniffNew = {}
        resultUpFamiliar = {}
        resultUpNew = {}
        
        animalA = pool.animalDictionnary[animal]
        setup = int(animalA.setup)
        objectFamiliar = objectTuple[side]
        objectNew = objectTuple[side]
        #print ( animalA )
        dicA = animalA.detectionDictionnary

        sideCage = {0: 'left', 1: 'right'}
        if side == 0:
            sideFam = 1
        elif side == 1:
            sideFam = 0

        for t in dicA.keys():
            #print(t)
            distanceNoseFamiliar = animalA.getDistanceNoseToPoint(t=t, xPoint=objectPosition[setup][sideCage[sideFam]][0], yPoint=-objectPosition[setup][sideCage[sideFam]][1])
            distanceMassFamiliar = animalA.getDistanceToPoint(t=t, xPoint=objectPosition[setup][sideCage[sideFam]][0], yPoint=-objectPosition[setup][sideCage[sideFam]][1])
            #print('distance left: ', distanceNoseFamiliar)
            if distanceNoseFamiliar == None:
                print('no nose detected for frame ', t)

            else:
                if distanceNoseFamiliar <= radiusObjects[objectFamiliar] + 3 / scaleFactor:
                    # check if the animal is on the object:
                    if distanceMassFamiliar <= radiusObjects[objectFamiliar]:
                        resultUpFamiliar[t] = True
                    else:
                        resultSniffFamiliar[t] = True

            distanceNoseNew = animalA.getDistanceNoseToPoint(t=t, xPoint=objectPosition[setup][sideCage[side]][0], yPoint=-objectPosition[setup][sideCage[side]][1])
            distanceMassNew = animalA.getDistanceToPoint(t=t, xPoint=objectPosition[setup][sideCage[side]][0], yPoint=-objectPosition[setup][sideCage[side]][1])
            #print('distance right: ', distanceNoseNew)
            if distanceNoseNew == None:
                print('no nose detected for frame ', t)

            else:
                if distanceNoseNew <= radiusObjects[objectNew] + 3 / scaleFactor:
                    # check if the animal is on the object:
                    if distanceMassNew <= radiusObjects[objectNew]:
                        resultUpNew[t] = True
                    else:
                        resultSniffNew[t] = True

        sniffFamiliarTimeLine.reBuildWithDictionnary( resultSniffFamiliar )
        sniffFamiliarTimeLine.endRebuildEventTimeLine(connection)

        sniffNewTimeLine.reBuildWithDictionnary(resultSniffNew)
        sniffNewTimeLine.endRebuildEventTimeLine(connection)

        upFamiliarTimeLine.reBuildWithDictionnary(resultUpFamiliar)
        upFamiliarTimeLine.endRebuildEventTimeLine(connection)

        upNewTimeLine.reBuildWithDictionnary(resultUpNew)
        upNewTimeLine.endRebuildEventTimeLine(connection)

    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Sniff Familiar" , tmin=tmin, tmax=tmax )
    t.addLog( "Build Event Sniff New" , tmin=tmin, tmax=tmax )
    t.addLog("Build Event Up Familiar", tmin=tmin, tmax=tmax)
    t.addLog("Build Event Up New", tmin=tmin, tmax=tmax)

    print( "Rebuild event finished." )
        
        
        
        
        
        
        
    