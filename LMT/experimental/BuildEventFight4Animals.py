'''
Created on 11 fev 2019

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
from lmtanalysis.MeasureOld import MAX_DISTANCE_THRESHOLD

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Fight" )    
    deleteEventTimeLineInBase(connection, "Won Fight" )
    deleteEventTimeLineInBase(connection, "Lost Fight" )
    deleteEventTimeLineInBase(connection, "Gets to Fight" )

def getPosition( t, animalA, animalB ):
    '''
    return mean position of available animals
    (0,0) if no detection available
    '''
    ad = animalA.detectionDictionary
    bd = animalB.detectionDictionary
    
    x = 0
    y = 0
    nb = 0

    if t in ad:
        x+=ad[t].massX
        y+=ad[t].massY
        nb+=1
        
    if t in bd:
        x+=bd[t].massX
        y+=bd[t].massY
        nb+=1

    if nb > 0:
        x /= nb
        y /= nb
        
    return Detection( x , y )

def getAveragePosition( animal , start, end ):
    
    x = 0
    y = 0
    count = 0
    
    aDic = animal.detectionDictionary
    
    for t in range ( start, end+1 ):
        if t in aDic:
            
            x+= aDic[t].massX
            y+= aDic[t].massY
            count+=1
    
    if count > 0:
        x/=count
        y/=count
        
    return Detection( x , y )

    
def getMaxDistanceTo ( animal , target , startFrame, endFrame ):
        '''
        returns the maximum distance from this detection to detectionB, considering time window
        '''
        
        maxDistanceTo = 0
        if ( target == None ):
            return None

        dA = animal.detectionDictionary
        
        for t in range( startFrame, endFrame + 1 ):
            
            if not (t in dA):
                continue
                
            detection = dA[ t ]            
                    
            dist = math.hypot( target.massX - detection.massX, target.massY - detection.massY )
        
            if dist > MAX_DISTANCE_THRESHOLD:                
                continue
            
            maxDistanceTo = max ( dist, maxDistanceTo )
        
        return maxDistanceTo


def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None ):
    
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        
    for animalA in pool.getAnimalList():
        for animalB in pool.getAnimalList():
            if animalA!=animalB:
                reBuildEventDuo( connection, file, animalA.baseId, animalB.baseId, tmin=tmin, tmax=tmax, pool = pool )


def reBuildEventDuo( connection, file, idA, idB, tmin=None, tmax=None, pool = None ):
        
    ''' 
    Animal A is fighting with animal B.
    Based on particle number
    Only for 2 animals. Still experimental
    ''' 
    
    ''' use the pool provided or creates it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
        
    # get number of particle    
    
    particleDictionary = pool.getParticleDictionary( start = tmin, end = tmax )
    
    fightTimeLine = EventTimeLine( None, "Fight" , idA = idA, idB=idB, loadEvent=False )
    
    contactDictionary = {}
    contactDictionary[idA,idB] = EventTimeLineCached( connection, file, "Contact", idA =idA, idB =idB, minFrame=tmin, maxFrame=tmax ).getDictionary( tmin, tmax )
    
    followZoneTimeLine = {}
    followZoneTimeLine[idA,idB]= EventTimeLineCached( connection, file, "FollowZone Isolated", idA = idA, idB = idB, minFrame=tmin, maxFrame=tmax )
    followZoneTimeLine[idB,idA]= EventTimeLineCached( connection, file, "FollowZone Isolated", idA = idB, idB = idA, minFrame=tmin, maxFrame=tmax )
    
    moveEventTimeLine = {}
    moveEventTimeLine[idA] =  EventTimeLineCached( connection, file, "Move", idA = idA, minFrame=tmin, maxFrame=tmax )
    moveEventTimeLine[idB] =  EventTimeLineCached( connection, file, "Move", idA = idB, minFrame=tmin, maxFrame=tmax )
    
    
    #animalA = pool.getAnimalList()[idA-1];
    #animalB = pool.getAnimalList()[idB-1];
    animalA = pool.getAnimalWithId( idA )
    animalB = pool.getAnimalWithId( idB )
     
    
    parameters = ParametersMouse()
    
    result = {}
    
    for t in range ( tmin, tmax + 1 ):
        
        window = 10
                
        posStart = getPosition( t-window , animalA, animalB )
        posEnd = getPosition( t+window , animalA, animalB )
        
        distStartToEnd = posStart.getDistanceTo( posEnd, parameters )
        
        if ( distStartToEnd == None ):
            continue
        
        if  distStartToEnd > (2*window) * 2:
            continue
        
        nbParticle = 0
        
        sum = 0
        count = 0
        
        for windowsT in range ( -window, window+1 ):
            
            currentT = t+windowsT 
            if currentT in particleDictionary:
                sum += particleDictionary[ currentT ]
                count +=1
            
        if count > 0:
            nbParticle = sum/ count
                
        #print( nbParticle )
        
        if nbParticle < 3:
            continue    
            
        #result[t] = True    
            
        
        nbAnimalDetected = 0
        if t in animalA.detectionDictionary:
            nbAnimalDetected+=1
        if t in animalB.detectionDictionary:
            nbAnimalDetected+=1
                
        if t in contactDictionary[idA,idB]:
            result[t] = True
            continue
        
        if (nbAnimalDetected == 1 ):
            result[t] = True
            continue
                 
    
    
    fightTimeLine.reBuildWithDictionary( result )
    #fightTimeLine.plotTimeLine()
    fightTimeLine.mergeCloseEvents( 30 )
    #fightTimeLine.plotTimeLine()
    fightTimeLine.removeEventsBelowLength( 3 );
    #fightTimeLine.plotTimeLine()

    fightTimeLine.endRebuildEventTimeLine(connection)
    
    '''
    find fight winner
    get the location of the fight and seek for the one far from the fight a few sec after
    '''
    winTimeLine = {}
    lostTimeLine = {}
    getsToFightTimeLine = {}
    
    winTimeLine[idA] = EventTimeLine( None, "Won Fight", idA = idA, loadEvent=False )
    lostTimeLine[idA] = EventTimeLine( None, "Lost Fight", idA = idA, loadEvent=False )
    winTimeLine[idB] = EventTimeLine( None, "Won Fight", idA = idB, loadEvent=False )
    lostTimeLine[idB] = EventTimeLine( None, "Lost Fight", idA = idB, loadEvent=False )

    getsToFightTimeLine[idA] = EventTimeLine( None, "Gets to Fight", idA = idA, loadEvent=False )
    getsToFightTimeLine[idB] = EventTimeLine( None, "Gets to Fight", idA = idB, loadEvent=False )


    ''' gets to the fight '''
    
    
    for event in fightTimeLine.getEventList():
        
        tFight = event.startFrame
        print ("Process gets to fight at t = " + str( tFight ))

        posFight = getPosition( tFight , animalA, animalB )
        
        window = 2 * oneSecond
        tPreFight = event.startFrame - window
        
        detA = getAveragePosition( animalA, tPreFight , tFight )
        detB = getAveragePosition( animalB, tPreFight , tFight )
        
        distA = detA.getDistanceTo( posFight, parameters )
        distB = detB.getDistanceTo( posFight, parameters )

        distMaxA = getMaxDistanceTo( animalA, posFight , tPreFight , tFight )
        distMaxB = getMaxDistanceTo( animalB, posFight , tPreFight , tFight )
        
        if ( distA == None or distB == None ):
            continue
        
        maxDist = max ( distMaxA, distMaxB )
        print ( "t=\t" , str(tFight) , "\tPre fight MaxDist = \t" + str ( maxDist ) )
        if maxDist < 100:
            print("Too close. Discarded")
            continue
        
        ''' try with move '''
       
        nbMoveA = moveEventTimeLine[idA].getTotalDurationEvent( tPreFight, tFight )
        nbMoveB = moveEventTimeLine[idB].getTotalDurationEvent( tPreFight, tFight )
       
        if ( nbMoveA > nbMoveB / 2 ):
            print("found with move")
            getsToFightTimeLine[idA].addEvent( Event( tPreFight - oneSecond , tPreFight + 2 * oneSecond ) )
            continue
        if ( nbMoveB > nbMoveA / 2 ):
            print("found with move")
            getsToFightTimeLine[idB].addEvent( Event( tPreFight - oneSecond , tPreFight + 2 * oneSecond ) )
            continue

        
        ''' Try with follow '''
        
        nbFollowAB = followZoneTimeLine[idA,idB].getTotalDurationEvent( tPreFight, tFight )
        nbFollowBA = followZoneTimeLine[idB,idA].getTotalDurationEvent( tPreFight, tFight )
        print( "nb Follow AB: " , str( nbFollowAB ))
        print( "nb Follow BA: " , str( nbFollowBA ))
        
        if ( nbFollowAB > 5 or nbFollowBA > 5 ):
            print( "Found with follow")
            if ( nbFollowAB > nbFollowBA ):
                getsToFightTimeLine[idA].addEvent( Event( tPreFight - oneSecond , tPreFight + 2 * oneSecond ) )
                continue
            else:
                getsToFightTimeLine[idB].addEvent( Event( tPreFight - oneSecond , tPreFight + 2 * oneSecond ) )                
                continue
        
        ''' try with distance '''

        
    
        
        print ("found with distance")
        if ( distA > distB ):
            getsToFightTimeLine[idA].addEvent( Event( tPreFight - oneSecond , tPreFight + 2 * oneSecond ) )
        else:
            getsToFightTimeLine[idB].addEvent( Event( tPreFight - oneSecond , tPreFight + 2 * oneSecond ) )
            
        
                            
    getsToFightTimeLine[idA].endRebuildEventTimeLine(connection)
    getsToFightTimeLine[idB].endRebuildEventTimeLine(connection)
    
    for event in fightTimeLine.getEventList():
        
        
        tFight = event.endFrame
        print ("Process get to the fight at t = " , str(tFight ))

        posFight = getPosition( tFight , animalA, animalB )
        
        delayAfterFight = 3 * oneSecond
        
        tPostFight = tFight + delayAfterFight
        
        closestEvent, closestEventTDistance = fightTimeLine.getClosestEventFromFrame( tPostFight )
        if  closestEventTDistance < delayAfterFight:
            # means another fight is occuring. This one is not finished yet.
            continue

        ''' Try with follow '''
        
        nbFollowAB = followZoneTimeLine[idA,idB].getTotalDurationEvent( tFight, tPostFight )
        nbFollowBA = followZoneTimeLine[idB,idA].getTotalDurationEvent( tFight, tPostFight )
        print( "nb Follow AB: " , str( nbFollowAB ))
        print( "nb Follow BA: " , str( nbFollowBA ))
        
        if ( nbFollowAB > 5 or nbFollowBA > 5 ):
            print( "Found with follow")
            if ( nbFollowAB > nbFollowBA ):
                lostTimeLine[idB].addEvent( Event( tPostFight, tPostFight + 90 ) )
                winTimeLine[idA].addEvent( Event( tPostFight, tPostFight + 90 ) )
                continue
            else:
                lostTimeLine[idA].addEvent( Event( tPostFight, tPostFight + 90 ) )
                winTimeLine[idB].addEvent( Event( tPostFight, tPostFight + 90 ) )
                continue

        ''' with distances '''
        
        detA = getAveragePosition( animalA, tFight+oneSecond , tPostFight )
        detB = getAveragePosition( animalB, tFight+oneSecond , tPostFight )
        
        '''
        if ( tPostFight in animalA.detectionDictionary 
             and tPostFight in animalB.detectionDictionary
             ):
        '''
        print("compute winner for t = " + str( tFight ) )
        print("fight loc = " + str( posFight.massX ) + "," + str( posFight.massY ) )
        print("mean A = " + str( detA.massX ) + "," + str( detA.massY ) )
        print("mean B = " + str( detB.massX ) + "," + str( detB.massY ) )
        
        '''
        detA = animalA.detectionDictionary[tPostFight]
        detB = animalB.detectionDictionary[tPostFight]
        '''
        
        distA = detA.getDistanceTo( posFight, parameters )
        distB = detB.getDistanceTo( posFight , parameters )
        
        if ( distA == None or distB == None ):
            continue
        
        print("found with distances")
        if ( distA > distB ):
            # a lost
            lostTimeLine[idA].addEvent( Event( tPostFight, tPostFight + 90 ) )
            winTimeLine[idB].addEvent( Event( tPostFight, tPostFight + 90 ) )
        else:
            # a wins
            winTimeLine[idA].addEvent( Event( tPostFight, tPostFight + 90 ) )
            lostTimeLine[idB].addEvent( Event( tPostFight, tPostFight + 90 ) )
                
    winTimeLine[idA].endRebuildEventTimeLine(connection)
    winTimeLine[idB].endRebuildEventTimeLine(connection)
    lostTimeLine[idA].endRebuildEventTimeLine(connection)
    lostTimeLine[idB].endRebuildEventTimeLine(connection)

  
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Fight/win/lost 4 animals" , tmin=tmin, tmax=tmax )
        
                   
    print( "Rebuild event finished." )
    