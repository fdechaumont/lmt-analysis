'''
Created on 6 sept. 2017

@author: Fab
'''
import sqlite3
from time import *
from database.Chronometer import Chronometer
from database.Animal import *
from database.Detection import *
from database.Measure import *
import numpy as np
from database.Event import *
from database.Measure import *
from affine import Affine
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
    
    
def projectVector( x1, y1, x2, y2 ):
    '''
    Project vector 1 on vector 2
    '''
    x = ( x1*x2 + y1*y2 ) * x2
    y = ( x1*x2 + y1*y2 ) * y2
    
    return x,y

    
def rotateVector( x1, y1 ):
    '''
    Rotate PI/2
    '''
    x = -y1
    y = x1
    return x, y

def getVectorFromAngle( angle ):
    
    x = math.cos(angle)
    y = math.sin(angle)
    return x,y

def normVector( x, y ):
    '''
    Norm of the vector
    '''
    norm = math.sqrt( x*x + y*y )
    return norm

def reBuildEvent( connection ): 
    '''
    Event SideWalk:

    - Side velocity is over a threshold

    '''
    timeWindow =  oneHour*2
        
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    pool.loadDetection( start = 0, end = timeWindow )
    
    for idAnimalA in pool.animalDictionnary.keys():
        print(pool.animalDictionnary[idAnimalA])
                    
        eventName = "SideWalk [{}]".format( idAnimalA )
                
        print ( eventName )
                
        sideWalkTimeLine = EventTimeLine( None, eventName, idAnimalA , None, None, None, loadEvent=False )
                
        result={}
        
        animalA = pool.animalDictionnary[idAnimalA]
        dicA = animalA.detectionDictionnary
            
        for t in dicA.keys():
            speedX, speedY = pool.animalDictionnary[idAnimalA].getSpeedVector(t)
            
            if ( speedX == None or speedY == None ):
                continue
            
            angleA = pool.animalDictionnary[idAnimalA].getDirection(t)
            
            vectorSideX, vectorSideY = getVectorFromAngle( angleA + math.pi / 2 )
            
            xP, yP = projectVector( speedX , speedY , vectorSideX, vectorSideY )

            normSide = normVector( xP , yP )
            
            if ( normSide > 15 ):
                result[t]=True
            '''
            if ( t == 1128 ):
                print ( "speedX: " , speedX )
                print ( "speedY: " , speedY )

                print ( "angleA: " , angleA )
                print ( "sidex: " , vectorSideX )
                print ( "sidey: " , vectorSideY )
                print ( "xp: " , xP )
                print ( "yp: " , yP )
                print ( "norm: " , normSide )
            '''
        sideWalkTimeLine.reBuildWithDictionnary( result )

        #print("REMOVING SHORT EVENTS !")
        #sideWalkTimeLine.removeEventsBelowLength( 5 )
                
        if (len( sideWalkTimeLine.eventList) == 0):
            print("no event")
        else:
            print ( "Number of event: " , len( sideWalkTimeLine.eventList ) )
            print ( "Mean len of event: " , sideWalkTimeLine.getMeanEventLength() )
            print ( "first event frame: " , sideWalkTimeLine.timeLineList[0].startFrame )
        
        print ( "Delete old entry in base: " + eventName )
        deleteEventTimeLineInBase(connection, eventName, idAnimalA, None, None, None ) #None is assumed as the name of the event contains the id description
        print ( "Saving timeLine: " + eventName )
        sideWalkTimeLine.saveTimeLine(connection)
    
        
    # log process
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Side Walk" )

    print( "Rebuild event finished." )
        
    