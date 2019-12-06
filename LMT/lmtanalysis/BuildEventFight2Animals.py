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
    ad = animalA.detectionDictionnary
    bd = animalB.detectionDictionnary
    
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
    
    aDic = animal.detectionDictionnary
    
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

        dA = animal.detectionDictionnary
        
        for t in range( startFrame, endFrame + 1 ):
            
            if not (t in dA):
                continue
                
            detection = dA[ t ]            
                    
            dist = math.hypot( target.massX - detection.massX, target.massY - detection.massY )
        
            if dist > MAX_DISTANCE_THRESHOLD:                
                continue
            
            maxDistanceTo = max ( dist, maxDistanceTo )
        
        return maxDistanceTo


def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None  ):
    
    ''' 
    Animal A is fighting with animal B.
    Based on particle number
    Only for 2 animals. Still experimental
    ''' 
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
    
    # work only with 2 animals at the moment. Should test with 4 later on.
    
    if ( len ( pool.getAnimalList( ) ) != 2 ):
        print( "Fight behavior only work with 2 animals at the moment")
        return    
    
    # get number of particle    
    
    particleDictionnary = pool.getParticleDictionnary( start = tmin, end = tmax )
    
    fightTimeLine = EventTimeLine( None, "Fight" , loadEvent=False )
    
    contactDictionnary = EventTimeLineCached( connection, file, "Contact", minFrame=tmin, maxFrame=tmax ).getDictionnary( tmin, tmax )
    
    followZoneTimeLine = {}
    followZoneTimeLine[1,2]= EventTimeLineCached( connection, file, "FollowZone Isolated", idA = 1, idB = 2, minFrame=tmin, maxFrame=tmax )
    followZoneTimeLine[2,1]= EventTimeLineCached( connection, file, "FollowZone Isolated", idA = 2, idB = 1, minFrame=tmin, maxFrame=tmax )
    
    moveEventTimeLine = {}
    moveEventTimeLine[1] =  EventTimeLineCached( connection, file, "Move", idA = 1, minFrame=tmin, maxFrame=tmax )
    moveEventTimeLine[2] =  EventTimeLineCached( connection, file, "Move", idA = 2, minFrame=tmin, maxFrame=tmax )
    
    animalA = pool.getAnimalList()[0];
    animalB = pool.getAnimalList()[1];
        
    
    
    result = {}
    
    for t in range ( tmin, tmax + 1 ):
        
        window = 10
                
        posStart = getPosition( t-window , animalA, animalB )
        posEnd = getPosition( t+window , animalA, animalB )
        
        distStartToEnd = posStart.getDistanceTo( posEnd )
        
        if ( distStartToEnd == None ):
            continue
        
        if  distStartToEnd > (2*window) * 2:
            continue
        
        nbParticle = 0
        
        sum = 0
        count = 0
        
        for windowsT in range ( -window, window+1 ):
            
            currentT = t+windowsT 
            if currentT in particleDictionnary:
                sum += particleDictionnary[ currentT ]
                count +=1
            
        if count > 0:
            nbParticle = sum/ count
                
        #print( nbParticle )
        
        if nbParticle < 3:
            continue    
            
        #result[t] = True    
            
        
        nbAnimalDetected = 0
        if t in animalA.detectionDictionnary:
            nbAnimalDetected+=1
        if t in animalB.detectionDictionnary:
            nbAnimalDetected+=1
                
        if t in contactDictionnary:
            result[t] = True
            continue
        
        if (nbAnimalDetected == 1 ):
            result[t] = True
            continue
                 
        #print ( str(t) , "\t" , str ( particleDictionnary[t] ) )
    
    
    fightTimeLine.reBuildWithDictionnary( result )
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
    
    winTimeLine[1] = EventTimeLine( None, "Won Fight", idA = 1, loadEvent=False )
    lostTimeLine[1] = EventTimeLine( None, "Lost Fight", idA = 1, loadEvent=False )
    winTimeLine[2] = EventTimeLine( None, "Won Fight", idA = 2, loadEvent=False )
    lostTimeLine[2] = EventTimeLine( None, "Lost Fight", idA = 2, loadEvent=False )

    getsToFightTimeLine[1] = EventTimeLine( None, "Gets to Fight", idA = 1, loadEvent=False )
    getsToFightTimeLine[2] = EventTimeLine( None, "Gets to Fight", idA = 2, loadEvent=False )


    ''' gets to the fight '''
    
    
    for event in fightTimeLine.getEventList():
        
        tFight = event.startFrame
        print ("Process gets to fight at t = " + str( tFight ))

        posFight = getPosition( tFight , animalA, animalB )
        
        window = 2 * oneSecond
        tPreFight = event.startFrame - window
        
        detA = getAveragePosition( animalA, tPreFight , tFight )
        detB = getAveragePosition( animalB, tPreFight , tFight )
        
        distA = detA.getDistanceTo( posFight )
        distB = detB.getDistanceTo( posFight )

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
       
        nbMoveA = moveEventTimeLine[1].getTotalDurationEvent( tPreFight, tFight )
        nbMoveB = moveEventTimeLine[2].getTotalDurationEvent( tPreFight, tFight )
       
        if ( nbMoveA > nbMoveB / 2 ):
            print("found with move")
            getsToFightTimeLine[1].addEvent( Event( tPreFight - oneSecond , tPreFight + 2 * oneSecond ) )
            continue
        if ( nbMoveB > nbMoveA / 2 ):
            print("found with move")
            getsToFightTimeLine[2].addEvent( Event( tPreFight - oneSecond , tPreFight + 2 * oneSecond ) )
            continue

        
        ''' Try with follow '''
        
        nbFollowAB = followZoneTimeLine[1,2].getTotalDurationEvent( tPreFight, tFight )
        nbFollowBA = followZoneTimeLine[2,1].getTotalDurationEvent( tPreFight, tFight )
        print( "nb Follow AB: " , str( nbFollowAB ))
        print( "nb Follow BA: " , str( nbFollowBA ))
        
        if ( nbFollowAB > 5 or nbFollowBA > 5 ):
            print( "Found with follow")
            if ( nbFollowAB > nbFollowBA ):
                getsToFightTimeLine[1].addEvent( Event( tPreFight - oneSecond , tPreFight + 2 * oneSecond ) )
                continue
            else:
                getsToFightTimeLine[2].addEvent( Event( tPreFight - oneSecond , tPreFight + 2 * oneSecond ) )                
                continue
        
        ''' try with distance '''

        
    
        
        print ("found with distance")
        if ( distA > distB ):
            getsToFightTimeLine[1].addEvent( Event( tPreFight - oneSecond , tPreFight + 2 * oneSecond ) )
        else:
            getsToFightTimeLine[2].addEvent( Event( tPreFight - oneSecond , tPreFight + 2 * oneSecond ) )
            
        
                            
    getsToFightTimeLine[1].endRebuildEventTimeLine(connection)
    getsToFightTimeLine[2].endRebuildEventTimeLine(connection)
    
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
        
        nbFollowAB = followZoneTimeLine[1,2].getTotalDurationEvent( tFight, tPostFight )
        nbFollowBA = followZoneTimeLine[2,1].getTotalDurationEvent( tFight, tPostFight )
        print( "nb Follow AB: " , str( nbFollowAB ))
        print( "nb Follow BA: " , str( nbFollowBA ))
        
        if ( nbFollowAB > 5 or nbFollowBA > 5 ):
            print( "Found with follow")
            if ( nbFollowAB > nbFollowBA ):
                lostTimeLine[2].addEvent( Event( tPostFight, tPostFight + 90 ) )
                winTimeLine[1].addEvent( Event( tPostFight, tPostFight + 90 ) )
                continue
            else:
                lostTimeLine[1].addEvent( Event( tPostFight, tPostFight + 90 ) )
                winTimeLine[2].addEvent( Event( tPostFight, tPostFight + 90 ) )
                continue

        ''' with distances '''
        
        detA = getAveragePosition( animalA, tFight+oneSecond , tPostFight )
        detB = getAveragePosition( animalB, tFight+oneSecond , tPostFight )
        
        '''
        if ( tPostFight in animalA.detectionDictionnary 
             and tPostFight in animalB.detectionDictionnary
             ):
        '''
        print("compute winner for t = " + str( tFight ) )
        print("fight loc = " + str( posFight.massX ) + "," + str( posFight.massY ) )
        print("mean A = " + str( detA.massX ) + "," + str( detA.massY ) )
        print("mean B = " + str( detB.massX ) + "," + str( detB.massY ) )
        
        '''
        detA = animalA.detectionDictionnary[tPostFight]
        detB = animalB.detectionDictionnary[tPostFight]
        '''
        
        distA = detA.getDistanceTo( posFight )
        distB = detB.getDistanceTo( posFight )
        
        if ( distA == None or distB == None ):
            continue
        
        print("found with distances")
        if ( distA > distB ):
            # a lost
            lostTimeLine[1].addEvent( Event( tPostFight, tPostFight + 90 ) )
            winTimeLine[2].addEvent( Event( tPostFight, tPostFight + 90 ) )
        else:
            # a wins
            winTimeLine[1].addEvent( Event( tPostFight, tPostFight + 90 ) )
            lostTimeLine[2].addEvent( Event( tPostFight, tPostFight + 90 ) )
                
    winTimeLine[1].endRebuildEventTimeLine(connection)
    winTimeLine[2].endRebuildEventTimeLine(connection)
    lostTimeLine[1].endRebuildEventTimeLine(connection)
    lostTimeLine[2].endRebuildEventTimeLine(connection)

    '''
    for idAnimalA in range( 1 , pool.getNbAnimals()+1 ):
        
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if( idAnimalA == idAnimalB ):
                continue
            
            
            eventName = "Oral-genital Contact"        
            print ( eventName )
            
            result ={}
            animalA = pool.animalDictionnary.get( idAnimalA )
            animalB = pool.animalDictionnary.get( idAnimalB )            
            
            OralGenitalTimeLine = EventTimeLine( None, eventName , idAnimalA , idAnimalB , loadEvent=False )

            for t in animalA.detectionDictionnary.keys() :
                
                if ( t in animalB.detectionDictionnary ):
                    detA = animalA.detectionDictionnary[t]
                    detB = animalB.detectionDictionnary[t]
                    
                    if distHeadBack( detA, detB ) < MAX_DISTANCE_HEAD_HEAD_GENITAL_THRESHOLD:
                        result[t] = True
            
            OralGenitalTimeLine.reBuildWithDictionnary( result )
            OralGenitalTimeLine.endRebuildEventTimeLine(connection)
    '''
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Fight/win/lost" , tmin=tmin, tmax=tmax )
        
                   
    print( "Rebuild event finished." )
    