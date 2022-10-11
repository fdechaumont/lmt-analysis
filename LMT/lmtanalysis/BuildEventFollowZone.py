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
from lmtanalysis.Measure import *
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
import copy
from copy import deepcopy


def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "FollowZone Isolated New" )


def line( x1, x2 , y1, y2 ):
    x1, y1 = [x1, y1], [x2, y2]    
    plt.plot(x1, y1, marker = 'o')    


def checkZone ( massA_x, massA_y, angleA, meanSizeB, massB_x, massB_y, angleB ):

    dbDif= math.atan2( math.sin(angleB-angleA), math.cos(angleB-angleA) )
    dif = math.fabs( dbDif ) 

    if ( dif < math.pi/4):
        #transfer the referential: position of B in the new space
        x,y = transformPoint(angleB, massA_x, massA_y, massB_x, massB_y)
        #print(x,y)
        
        if (x>-0.5*meanSizeB and x<0.5*meanSizeB and y>-meanSizeB and y<0):
        #if ( x >-20 and x < 20 and y > -100 and y < 0 ):
            return True

    
def transformPoint(angleB, massA_x, massA_y, massB_x, massB_y):
    '''
    transform the origin of the space so that the mass center of animalB is the origin of the new space
    '''
 
    Affine.identity()

    x = massA_x - massB_x
    y = massA_y - massB_y

    rotation = Affine.rotation(90- math.degrees( angleB ) ) * ( x , y )
    
    return rotation[0], rotation[1]


def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None ): 
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )

    '''
    Event FollowZone:
    - the two animals are moving at a speed >5 cm/s (SPEED_THRESHOLD_LOW)
    - the angles between the two animals are less than 45° apart
    - the mass center of the follower is within a follow zone of one mean body length of width and two mean body lengths of length
    - either the animal B is in contact with another one (FollowZone Social) or the animal B is not in contact with any other animal (except A at the end of the follow event; FollowZone Isolated)
    
    - update 17 may 2018: now works with n animals    
    
    '''
    
    contact = {}
    anogenitalContact = {}
    sideSideContact = {}
    for idAnimalB in pool.animalDictionnary:
        print(pool.animalDictionnary[idAnimalB])
        meanSizeB = pool.animalDictionnary[idAnimalB].getMeanBodyLength( tmax = tmax )
        anogenitalContact[idAnimalB] = EventTimeLineCached( connection, file, "Oral-genital Contact", idAnimalB, minFrame=tmin, maxFrame=tmax )
            
        
        for idAnimalA in pool.animalDictionnary:
            if( idAnimalB == idAnimalA ):
                continue
            contact[idAnimalA, idAnimalB] = EventTimeLineCached( connection, file, "Contact", idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax )
            
            
    #initiate empty timelines
    followIsolatedTimeLine = {}
    for idAnimalA in pool.animalDictionnary:
        for idAnimalB in pool.animalDictionnary:
            if( idAnimalA == idAnimalB ):
                continue
            eventName = "FollowZone Isolated New"
            print ( "A follow B")        
            print ( eventName )
            followIsolatedTimeLine[idAnimalA, idAnimalB] = EventTimeLine( None, eventName , idAnimalA , idAnimalB , None , None , loadEvent=False )
            
    
    followIsolatedTimeLineDic = {}
    #generate the list of all animals in the experiment
    allAnimals = list( pool.animalDictionnary.keys() )
    dicAnogenitalContactAToOtherAnimal = {}
    for idAnimalA in pool.animalDictionnary:
        dicAnogenitalContactAToOtherAnimal[ idAnimalA ] = anogenitalContact[ idAnimalA ].getDictionnary()
        
        for idAnimalB in pool.animalDictionnary:
            if( idAnimalA == idAnimalB ):
                continue
            allOtherAnimals = allAnimals.copy()
            allOtherAnimals.remove( idAnimalB )

            resultIso={}
            
            animalA = pool.animalDictionnary[idAnimalA]
            animalB = pool.animalDictionnary[idAnimalB]

            dicA = animalA.detectionDictionnary
            dicB = animalB.detectionDictionnary
            
            dicContactBToOtherAnimal = {}
            for idOtherAnimal in allOtherAnimals :                
                dicContactBToOtherAnimal[ idOtherAnimal ] = contact[ idAnimalB, idOtherAnimal ].getDictionnary()

            for t in dicB:
                
                testContactWithOtherAnimal=False

                for idOtherAnimal in allOtherAnimals :
                    if ( t in dicContactBToOtherAnimal[ idOtherAnimal ] ):
                        testContactWithOtherAnimal = True
                        break
                    if ( t in dicAnogenitalContactAToOtherAnimal[ idAnimalA ]):
                        testContactWithOtherAnimal = True
                        break
                
                if testContactWithOtherAnimal==True:
                    continue
               
                if ( t in dicA ):
                    speedA = pool.animalDictionnary[idAnimalA].getSpeed(t)
                    speedB = pool.animalDictionnary[idAnimalB].getSpeed(t)
                    #angleB = pool.animalList[idAnimalB].getDirection(t)
                    angleA = pool.animalDictionnary[idAnimalA].getDirection(t)
                    
                    if (speedA == None or speedB == None):
                        continue
                    
                    if ( speedA>animalA.parameters.SPEED_THRESHOLD_LOW and speedB>animalB.parameters.SPEED_THRESHOLD_LOW ):

                        time = t
                        #angleB = pool.animalDictionnary[idAnimalB].getDirection(time)
                        
                        
                        for time in range( t-15, t+1, 2):
                        #time = t
                            try:
                                angleB = pool.animalDictionnary[idAnimalB].getDirection(time)
                                if ( checkZone( dicA[t].massX, dicA[t].massY, angleA, meanSizeB, dicB[time].massX, dicB[time].massY, angleB ) == True):
         
                                    resultIso[t] = True
                                    break
                            except:
                                pass                

            followIsolatedTimeLineDic[idAnimalA, idAnimalB] = resultIso 
    
    #exclude events where both animals are in reciprocal follow
    cleanFollowDictionary = copy.deepcopy( followIsolatedTimeLineDic ) #copy the existing timeline before cleaning it from follow events that are occurring in contact
    for idAnimalA in pool.animalDictionnary:
        remainingAnimals = list( pool.animalDictionnary.keys() )
        remainingAnimals.remove(idAnimalA)
        
        for idAnimalB in remainingAnimals:
            for t in followIsolatedTimeLineDic[idAnimalA, idAnimalB]:
                if t in followIsolatedTimeLineDic[idAnimalB, idAnimalA]:
                    cleanFollowDictionary[idAnimalA, idAnimalB].pop(t)
                    
                animalA = pool.animalDictionnary[idAnimalA]
                animalB = pool.animalDictionnary[idAnimalB]
                speedA = animalA.getSpeed(t)
                speedB = animalB.getSpeed(t)
                if (speedA<=animalA.parameters.SPEED_THRESHOLD_LOW+2 and speedB<=animalB.parameters.SPEED_THRESHOLD_LOW):
                    cleanFollowDictionary[idAnimalA, idAnimalB].pop(t)
                    
                else:
                    continue
            
            print('########end remaining animals: ', remainingAnimals)
            
    
    #rebuild timelines with dictionaries
    for idAnimalA in pool.animalDictionnary:
        for idAnimalB in pool.animalDictionnary:
            if( idAnimalB == idAnimalA ):
                continue
            followIsolatedTimeLine[idAnimalA, idAnimalB].reBuildWithDictionnary( cleanFollowDictionary[idAnimalA, idAnimalB] )
            
            followIsolatedTimeLine[idAnimalA, idAnimalB].endRebuildEventTimeLine(connection)
            
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Follow Zone" , tmin=tmin, tmax=tmax )

              
    print( "Rebuild event finished." )
        
    