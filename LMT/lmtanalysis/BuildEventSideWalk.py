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
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
#from affine import Affine
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
    
def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "SideWalk" )

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
    
    for animal in pool.animalDictionnary.keys():
        print(pool.animalDictionnary[animal])
                    
        eventName = "SideWalk".format( animal )
                
        print ( eventName )
                
        sideWalkTimeLine = EventTimeLine( None, eventName, animal , None, None, None, loadEvent=False )
                
        result={}
        
        animalA = pool.animalDictionnary[animal]
        dicA = animalA.detectionDictionnary
            
        for t in dicA.keys():
            speedX, speedY = pool.animalDictionnary[animal].getSpeedVector(t)
            
            if ( speedX == None or speedY == None ):
                continue
            
            if not pool.animalDictionnary[animal].getDetectionAt( t ).isHeadAndTailDetected():
                continue
                    
            angleA = pool.animalDictionnary[animal].getDirection(t)
            
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
        deleteEventTimeLineInBase(connection, eventName, animal, None, None, None ) #None is assumed as the name of the event contains the id description
        print ( "Saving timeLine: " + eventName )
        sideWalkTimeLine.saveTimeLine(connection)
    
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Side Walk" )

    print( "Rebuild event finished." )
        
    