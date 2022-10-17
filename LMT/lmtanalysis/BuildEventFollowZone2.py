'''
Created on 6 sept. 2017

@author: Fab
'''
import sqlite3
from time import *

from affine import Affine

from lmtanalysis.Chronometer import Chronometer
from lmtanalysis.Animal import *
from lmtanalysis.Detection import *
from lmtanalysis.Measure import  SPEED_THRESHOLD_LOW
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
import copy
from copy import deepcopy

eventName = "FollowZone New2"  # FIX: CHECK IF that's not over propagated

FOLLOW_CORRIDOR_DURATION = 30

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, eventName )

'''
def line( x1, x2 , y1, y2 ):
    x1, y1 = [x1, y1], [x2, y2]    
    plt.plot(x1, y1, marker = 'o')    


def checkZone ( massA_x, massA_y, angleA, width, length, massB_x, massB_y, angleB ):

    dbDif= math.atan2( math.sin(angleB-angleA), math.cos(angleB-angleA) )
    dif = math.fabs( dbDif ) # FIX: CheCK IF THIS DHOULD BE THERE

    if ( dif < math.pi/4):
        #transfer the referential: position of B in the new space
        x,y = transformPoint(angleB, massA_x, massA_y, massB_x, massB_y)
        #print(x,y)
        
        #if (x>-0.5*width and x<0.5*width and y>-3*length and y<0):  # FIX > est ce qu'on est bien dans la transfo ?
        if (x>-0.5*width and x<0.5*width and y>-0.5*width and y<0):  # FIX > est ce qu'on est bien dans la transfo ?
        #if ( x >-20 and x < 20 and y > -100 and y < 0 ):
            return True

    
def transformPoint(angleB, massA_x, massA_y, massB_x, massB_y):
    
    #transform the origin of the space so that the mass center of animalB is the origin of the new space
        
 
    Affine.identity()

    x = massA_x - massB_x
    y = massA_y - massB_y

    rotation = Affine.rotation(90- math.degrees( angleB ) ) * ( x , y )
    
    return rotation[0], rotation[1]
'''

def isSameWay( detA, detB ):
    
    vectAX = detA.frontX - detA.backX
    vectAY = detA.frontY - detA.backY

    vectBX = detB.frontX - detB.backX
    vectBY = detB.frontY - detB.backY
    
    scalarProduct = vectAX * vectBX + vectAY * vectBY
    
    if ( scalarProduct >= 0 ): #same direction
        return True
    
    return False

def isAFollowingB( t , animalA , dicA , animalB , dicB ):
    
    # False is detection A does not exist at t
    if t not in dicA:
        return False
    
    # False is detection B does not exist at t
    if t not in dicB:
        return False
    
    # False if at least for the current t animals are not in the same direction. Could be wrong if animals are spinning around while following but filters out a number of complex situation
    if not isSameWay( dicA[t], dicB[t] ):
        return False
        
    detectionA = dicA[t]
    
    # check if in the past B was in A location
    for timeB in range( t-FOLLOW_CORRIDOR_DURATION,t+1 ):
        
        # check if detection B exists:
        if not timeB in dicB:
            continue
        
        detectionB = dicB[timeB]
        
        distance = detectionA.getDistanceTo( detectionB )  
        
        # discard if distance is too large between detections
        if distance == None:
            continue
        
        if distance > 10: # PLEASE FIX: THIS IS TO DEFINE
            continue
                         
        # discard if animals are not going the same way ( scalar test )
        if not isSameWay( detectionA, detectionB ):
            continue
        
        # discard if angle between animals is not ok
        angleA = detectionA.getDirection()
        angleB = detectionB.getDirection()
        dbDif= math.atan2( math.sin(angleB-angleA), math.cos(angleB-angleA) )
        dif = math.fabs( dbDif )
        if ( dif > math.pi/4):
            continue
        
        
        return True
        
    '''
    
    if t in contactDic[idAnimalA, idAnimalB]:
                    continue
                                
                
                for time in range( t-animalA.parameters.FOLLOW_CORRIDOR_DURATION, t+1, 2):
                    
                    # does A exists at tested time ?
                    if not time in dicA:
                        continue
                
                    # is a in the track of B ?
                    try:
                        angleA = pool.animalDictionnary[idAnimalA].getDirection(time)
                        angleB = pool.animalDictionnary[idAnimalB].getDirection(time)
                    except:
                        continue
                    
                    if ( checkZone( dicA[time].massX, dicA[time].massY, angleA, 
                                        animalA.parameters.FOLLOW_CORRIDOR_WIDTH, animalA.parameters.FOLLOW_CORRIDOR_LENGTH, 
                                        dicB[time].massX, dicB[time].massY, angleB ) == True):
                        resultDic[t]=True
                        break
    
    '''
    
    
    
    return False
    

def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None ): 
    
    '''
    Event FollowZone:
    - ok: the two animals are moving at a speed >5 cm/s (SPEED_THRESHOLD_LOW)
    - ok: animals must not be in contact
    
    - not ok: the angles between the two animals are less than 45� apart considering head tail direction
    - ok: the mass center of the follower is within a follow zone of 1* mean body length of width and 3* mean body lengths of length
    
    
    NOT CONSIDERED YET: - either the animal B is in contact with another one (FollowZone Social) or the animal B is not in contact with any other animal (except A at the end of the follow event; FollowZone Isolated)
    
    - update 17 may 2018: now works with n animals    
    
    '''
    
    
    # create dedicated pool as we will alter detection pool with filters (I.e: we don't use the pool cache)
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    pool.loadDetection( start = tmin, end = tmax )
    
    # filter detection by speed. Keep only the detection that are over SPEED_THRESHOLD_LOW.
    #pool.filterDetectionByInstantSpeed( pool.getAnimalList()[0].parameters.SPEED_THRESHOLD_LOW , 1000 ) # for the rat compatible version
    pool.filterDetectionByInstantSpeed( SPEED_THRESHOLD_LOW*2 , 1000 )
    
    # remove all detection where head and tail are missing
    pool.filterDetectionToKeepOnlyHeadTailDetection()
    
    
    # load the contact matrix dictionary    
    contactDic = {}    
    for idAnimalA in pool.animalDictionnary:
        print(pool.animalDictionnary[idAnimalA])
        for idAnimalB in pool.animalDictionnary:
            if( idAnimalA == idAnimalB ):
                continue
            contactDic[idAnimalA, idAnimalB] = EventTimeLineCached( connection, file, "Contact", idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax ).getDictionary()
            
            
    #init empty result EventTimeLine matrix
    followIsolatedTimeLine = {}
    for idAnimalA in pool.animalDictionnary:
        for idAnimalB in pool.animalDictionnary:
            if( idAnimalA == idAnimalB ):
                continue                                        
            followIsolatedTimeLine[idAnimalA, idAnimalB] = EventTimeLine( None, eventName , idAnimalA , idAnimalB , None , None , loadEvent=False )

    # init empty result timeline Dictionary.
    followIsolatedTimeLineDic = {}
    
    for idAnimalA in pool.animalDictionnary:

        animalA = pool.animalDictionnary[idAnimalA]
        dicA = animalA.detectionDictionnary
        
        for idAnimalB in pool.animalDictionnary:
            
            # discard if animals are the same.
            if( idAnimalA == idAnimalB ):
                continue
            
            # result dictionary for the current pair tested.            
            resultDic = {}

            animalB = pool.animalDictionnary[idAnimalB]
            dicB = animalB.detectionDictionnary
            
            '''
            # discard if animals are currently in contact at t
            if t in contactDic[idAnimalA, idAnimalB]:
                continue
            '''
                
            # Starting "is A following B ?"
                        
            for t in dicB:            
                if isAFollowingB( t , animalA , dicA , animalB , dicB ):
                    resultDic[t]=True

            # remove all contact situation
            for t in contactDic[idAnimalA, idAnimalB]:
                if t in resultDic:
                    resultDic.pop( t )
            
            '''
            
            # test if B is followed by A at t
            for t in dicB:
                
                if t in contactDic[idAnimalA, idAnimalB]:
                    continue
                                
                
                for time in range( t-animalA.parameters.FOLLOW_CORRIDOR_DURATION, t+1, 2):
                    
                    # does A exists at tested time ?
                    if not time in dicA:
                        continue
                
                    # is a in the track of B ?
                    try:
                        angleA = pool.animalDictionnary[idAnimalA].getDirection(time)
                        angleB = pool.animalDictionnary[idAnimalB].getDirection(time)
                    except:
                        continue
                    
                    if ( checkZone( dicA[time].massX, dicA[time].massY, angleA, 
                                        animalA.parameters.FOLLOW_CORRIDOR_WIDTH, animalA.parameters.FOLLOW_CORRIDOR_LENGTH, 
                                        dicB[time].massX, dicB[time].massY, angleB ) == True):
                        resultDic[t]=True
                        break
            '''
            followIsolatedTimeLineDic[idAnimalA, idAnimalB] = resultDic

    '''
    for idAnimalA in pool.animalDictionnary:
        for idAnimalB in pool.animalDictionnary:
            if( idAnimalA == idAnimalB ):
                continue
            resultIsoDic = {}
            
            animalA = pool.animalDictionnary[idAnimalA]
            animalB = pool.animalDictionnary[idAnimalB]

            dicA = animalA.detectionDictionnary
            dicB = animalB.detectionDictionnary
                    
            for t in dicB:
                
                debug  = False
                if t==  354:
                    debug = True
                    print( f"A:{animalA}")
                    print( f"B:{animalB}")
                
                if t in contactDic[idAnimalA, idAnimalB]:
                    continue
                                                               
                if not t in dicA:
                    continue
                
                speedA = pool.animalDictionnary[idAnimalA].getSpeed(t)
                
                if debug:
                    print( f"SpeedA: {speedA}" )
                #speedB = pool.animalDictionnary[idAnimalB].getSpeed(t)
                #angleB = pool.animalList[idAnimalB].getDirection(t)
                
                if speedA == None:
                    if debug:
                        print( f"SpeedA none: {speedA}" )
                    continue

                if speedA < animalA.parameters.SPEED_THRESHOLD_LOW:
                    if debug:
                        print( f"SpeedA too low: {speedA}" )
                    continue
                
                angleA = pool.animalDictionnary[idAnimalA].getDirection(t)
                if debug:
                    print( f"angleA : {angleA}" )
                    
                for time in range( t-animalA.parameters.FOLLOW_CORRIDOR_DURATION, t+1, 2):
                    
                    if debug:
                        print( f"time: {time} ------------------------" )
                                        
                    if not time in dicB:                        
                        continue
                    
                    speedB = pool.animalDictionnary[idAnimalB].getSpeed(time)
                    if speedB == None:
                        continue
                    
                    if speedB < animalB.parameters.SPEED_THRESHOLD_LOW:
                        continue
                    
                    angleB = None
                    if time in pool.animalDictionnary[idAnimalB].detectionDictionnary:
                        angleB = pool.animalDictionnary[idAnimalB].detectionDictionnary[time].getDirection()
                        
                    if angleB == None:
                        continue

                    if debug:
                        print( f"angleB: {angleB}" )

                    if ( checkZone( dicA[t].massX, dicA[t].massY, angleA, 
                                        animalA.parameters.FOLLOW_CORRIDOR_WIDTH, animalA.parameters.FOLLOW_CORRIDOR_LENGTH, 
                                        dicB[time].massX, dicB[time].massY, angleB ) == True):
 
                        resultIsoDic[t] = True
                        if debug:
                            print( f"MATCH: A:{t} B:{time}" )
                        break
            
            
            
    '''
            
    #rebuild timelines with dictionaries
    for idAnimalA in pool.animalDictionnary:
        for idAnimalB in pool.animalDictionnary:
            if( idAnimalB == idAnimalA ):
                continue
            followIsolatedTimeLine[idAnimalA, idAnimalB].reBuildWithDictionnary( followIsolatedTimeLineDic[idAnimalA, idAnimalB] )
            
            # FIXME: those 2 smoothing filters could be at call process. Design choice needed.
            # filter out accidental events
            followIsolatedTimeLine[idAnimalA, idAnimalB].removeEventsBelowLength( 7 )
            # create continuity in the events
            followIsolatedTimeLine[idAnimalA, idAnimalB].mergeCloseEvents( 10 )
                        
            followIsolatedTimeLine[idAnimalA, idAnimalB].endRebuildEventTimeLine(connection)
                
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( eventName , tmin=tmin, tmax=tmax )
              
    print( "Rebuild event finished." )
    return
    
            
    
            
        
        
    