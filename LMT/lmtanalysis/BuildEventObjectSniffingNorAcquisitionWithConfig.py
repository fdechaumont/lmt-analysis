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
    deleteEventTimeLineInBase(connection, "SniffRight" )
    deleteEventTimeLineInBase(connection, "SniffLeft" )
    deleteEventTimeLineInBase(connection, "SniffRightFar")
    deleteEventTimeLineInBase(connection, "SniffLeftFar")


def reBuildEvent( connection, exp, phase, objectPosition, radiusObjects, objectTuple, tmin=None, tmax=None, pool = None, vibrissae=3 ):
    deleteEventTimeLineInBase(connection, "SniffRight" )
    deleteEventTimeLineInBase(connection, "SniffLeft")
    deleteEventTimeLineInBase(connection, "SniffRightFar")
    deleteEventTimeLineInBase(connection, "SniffLeftFar")
    deleteEventTimeLineInBase(connection, "UpRight")
    deleteEventTimeLineInBase(connection, "UpLeft")


    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
        pool.filterDetectionByInstantSpeed(0, 70)
    '''
    Event SniffRight
    - the animal's nose is in a zone 3 cm around the object at the right
    
    Event SniffLeft
    - the animal's nose is in a zone 3 cm around the object at the left
    
    Event upRight
    - the animal is on the object located on the right
    
    Event upLeft
    - the animal is on the object located on the left
    '''
    
    for animal in pool.animalDictionnary.keys():
        print(pool.animalDictionnary[animal])
        
        eventNameSniffRight = "SniffRight"
        print ( "A is around the object located on the right")
        print ( eventNameSniffRight )
        
        eventNameSniffLeft = "SniffLeft"
        print ( "A is around object located on the left")
        print ( eventNameSniffLeft )

        eventNameSniffRightFar = "SniffRightFar"
        print("A is around the object located on the right, at a distance")
        print(eventNameSniffRight)

        eventNameSniffLeftFar = "SniffLeftFar"
        print("A is around object located on the left, at a distance")
        print(eventNameSniffLeft)

        eventNameUpRight = "UpRight"
        print("A is on the object located on the right")
        print(eventNameUpRight)

        eventNameUpLeft = "UpLeft"
        print("A is on object located on the left")
        print(eventNameUpLeft)
                
        sniffRightTimeLine = EventTimeLine( None, eventNameSniffRight, animal , None , None , None , loadEvent=False )
        sniffLeftTimeLine = EventTimeLine( None, eventNameSniffLeft, animal , None , None , None , loadEvent=False )
        sniffRightTimeLineFar = EventTimeLine(None, eventNameSniffRightFar, animal, None, None, None, loadEvent=False)
        sniffLeftTimeLineFar = EventTimeLine(None, eventNameSniffLeftFar, animal, None, None, None, loadEvent=False)
        upRightTimeLine = EventTimeLine(None, eventNameUpRight, animal, None, None, None, loadEvent=False)
        upLeftTimeLine = EventTimeLine(None, eventNameUpLeft, animal, None, None, None, loadEvent=False)

        resultSniffRight = {}
        resultSniffLeft = {}
        resultSniffRightFar = {}
        resultSniffLeftFar = {}
        resultUpRight = {}
        resultUpLeft = {}
        
        animalA = pool.animalDictionnary[animal]
        setup = animalA.setup
        objectLeft = objectTuple[0]
        objectRight = objectTuple[1]
        #print ( animalA )
        dicA = animalA.detectionDictionnary

        for t in dicA.keys():
            #print(t)
            distanceNoseLeft = animalA.getDistanceNoseToPoint(t=t, xPoint=objectPosition[setup]['left'][0], yPoint=-objectPosition[setup]['left'][1])
            distanceMassLeft = animalA.getDistanceToPoint(t=t, xPoint=objectPosition[setup]['left'][0], yPoint=-objectPosition[setup]['left'][1])
            #print('distance left: ', distanceNoseLeft)
            if distanceNoseLeft == None:
                print('no nose detected for frame ', t)

            else:
                if distanceNoseLeft <= radiusObjects[objectLeft] + vibrissae / scaleFactor:
                    print('t: ', t, distanceNoseLeft)
                    # check if the animal is on the object:
                    if distanceMassLeft <= radiusObjects[objectLeft]:
                        resultUpLeft[t] = True
                    else:
                        resultSniffLeft[t] = True

                if distanceNoseLeft <= radiusObjects[objectLeft] + 2*vibrissae / scaleFactor:
                    print('t: ', t, distanceNoseLeft)
                    # check if the animal is on the object:
                    if distanceMassLeft > radiusObjects[objectLeft]:
                        resultSniffLeftFar[t] = True

            distanceNoseRight = animalA.getDistanceNoseToPoint(t=t, xPoint=objectPosition[setup]['right'][0], yPoint=-objectPosition[setup]['right'][1])
            distanceMassRight = animalA.getDistanceToPoint(t=t, xPoint=objectPosition[setup]['right'][0], yPoint=-objectPosition[setup]['right'][1])
            #print('distance right: ', distanceNoseRight)
            if distanceNoseRight == None:
                print('no nose detected for frame ', t)

            else:
                if distanceNoseRight <= radiusObjects[objectRight] + vibrissae / scaleFactor:
                    # check if the animal is on the object:
                    if distanceMassRight <= radiusObjects[objectRight]:
                        resultUpRight[t] = True
                    else:
                        resultSniffRight[t] = True

                if distanceNoseRight <= radiusObjects[objectRight] + 2*vibrissae / scaleFactor:
                    # check if the animal is on the object:
                    if distanceMassRight > radiusObjects[objectRight]:
                        resultSniffRightFar[t] = True

        sniffRightTimeLine.reBuildWithDictionnary( resultSniffRight )
        sniffRightTimeLine.endRebuildEventTimeLine(connection)

        sniffLeftTimeLine.reBuildWithDictionnary(resultSniffLeft)
        sniffLeftTimeLine.endRebuildEventTimeLine(connection)

        sniffRightTimeLineFar.reBuildWithDictionnary(resultSniffRightFar)
        sniffRightTimeLineFar.endRebuildEventTimeLine(connection)

        sniffLeftTimeLineFar.reBuildWithDictionnary(resultSniffLeftFar)
        sniffLeftTimeLineFar.endRebuildEventTimeLine(connection)

        upRightTimeLine.reBuildWithDictionnary(resultUpRight)
        upRightTimeLine.endRebuildEventTimeLine(connection)

        upLeftTimeLine.reBuildWithDictionnary(resultUpLeft)
        upLeftTimeLine.endRebuildEventTimeLine(connection)


    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Sniff Right" , tmin=tmin, tmax=tmax )
    t.addLog( "Build Event Sniff Left" , tmin=tmin, tmax=tmax )
    t.addLog("Build Event Sniff Right Far", tmin=tmin, tmax=tmax)
    t.addLog("Build Event Sniff Left Far", tmin=tmin, tmax=tmax)
    t.addLog("Build Event Up Right", tmin=tmin, tmax=tmax)
    t.addLog("Build Event Up Left", tmin=tmin, tmax=tmax)

    print( "Rebuild event finished." )
        
        
        
        
        
        
        
    