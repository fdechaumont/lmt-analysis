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
import sys
import matplotlib.pyplot as plt

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "WallJump" )

def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None, showGraph = False ): 
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
    
    centerX = 512/2
    centerY = 424/2
    
    if ( showGraph ):
        plt.figure( 1 )
    
    
    
    for animal in pool.animalDictionnary.keys():
        print(pool.animalDictionnary[animal])
        
        if ( showGraph ):    
            plt.subplot(2,2, animal )
        
        eventName = "WallJump"
        print ( "A is jumping against the wall")        
        print ( eventName )
                
        JumpWallTimeLine = EventTimeLine( None, eventName , animal , None , None , None , loadEvent=False )
        
        result={}
        
        animalA = pool.animalDictionnary[animal]
        #print ( animalA )
        dicA = animalA.detectionDictionnary

        amplitude = 28
        window = 6
        threshold = 100
        angleTolerance = math.pi/8
        maxMissingDetection = 3
            
        for t in dicA.keys():

            #check if data is available
            numberOfDataNotAvailable = 0
            for tt in range( t, t+window+1 ):
                if ( not ( tt in dicA ) ):
                    numberOfDataNotAvailable +=1
                
            if ( numberOfDataNotAvailable > maxMissingDetection ):
                continue            

            jumpFound= False
            totalDistance = 0

            dis1 = math.hypot( dicA[t].massX - centerX, dicA[t].massY - centerY )
            dis2 = math.hypot( dicA[t].frontX - centerX, dicA[t].frontY - centerY )
            dis3 = math.hypot( dicA[t].backX - centerX, dicA[t].backY - centerY )

            distanceStart = min( dis1, dis2, dis3 )

            ''' check orientation to the external of the cage '''
            orientationValid = True
            for tt in range( t, t+window+1 ):
                
                if ( tt in dicA ):
                
                    directionAnimalA = dicA[tt].getDirection()
                    directionCenterAnimal = math.atan2( centerY - dicA[tt].massY, centerX - dicA[tt].massX )
                    
                    #same direction
                    angleDif1 = math.atan2( math.sin(directionCenterAnimal-directionAnimalA), math.cos(directionCenterAnimal-directionAnimalA) )
                    angleDif1 = math.fabs( angleDif1 ) 
                    
                    #opposite direction
        
                    angleDif2 = math.atan2( math.sin(directionCenterAnimal+math.pi-directionAnimalA), math.cos(directionCenterAnimal+math.pi-directionAnimalA) )
                    angleDif2 = math.fabs( angleDif2 ) 
                    
                    angleDif = min( angleDif1 , angleDif2 )
                    
                    if ( angleDif > angleTolerance ):
                        orientationValid = False
                        break
                
            if not orientationValid:
                continue

            ''' check if animal trajectory match jump model '''

            xList = []
            yList = []

            for tt in range( t, t+window+1 ): 
        
                if ( tt in dicA ):                    
                    
                    dis1 = math.hypot( dicA[tt].massX - centerX, dicA[tt].massY - centerY )
                    dis2 = math.hypot( dicA[tt].frontX - centerX, dicA[tt].frontY - centerY )
                    dis3 = math.hypot( dicA[tt].backX - centerX, dicA[tt].backY - centerY )
                    
                    distanceToCenter = min( dis1, dis2, dis3 )
                    
                    #distanceToCenter = math.hypot( dicA[tt].massX - centerX, dicA[tt].massY - centerY )
                    
                    distanceToStart = distanceToCenter - distanceStart
                    idealSin = math.sin( 2*math.pi * ( tt-t - math.pi/2 ) / window ) * amplitude/2 + amplitude/2 
                    #idealSin = math.sin( 2*math.pi * ( tt-t - math.pi/2 ) / window ) * 15
                    distance = math.pow( idealSin - distanceToStart , 2 )
    
                    totalDistance+= distance
                    xList.append( tt-t )
                    yList.append( distanceToCenter - distanceStart )                
            
            totalDistance/=window
                        
            if ( totalDistance < threshold ):
                jumpFound = True
                
                if ( showGraph ):
                    plt.plot( xList, yList, linestyle='-', linewidth=1 )            
                
                #print( "jump found. dist={} and t={}".format( totalDistance,t+window/2 ) )
                                       
            if ( jumpFound ):
                ''' build the event on a thinner range to avoid event overlap and automatic continuity '''
                for tt in range( t+2, t+window-2 ): 
                    result[tt] = True
                
        xList = []
        yList = [] 
        
        if ( showGraph ):
            for tt in range( t, t+window+1 ): 
                idealSin = math.sin( 2*math.pi * ( tt-t - math.pi/2 ) / window ) * amplitude/2 + amplitude/2
                xList.append( tt-t )
                yList.append( idealSin )
            plt.plot( xList, yList, linestyle='--', linewidth=4 )
        
        JumpWallTimeLine.reBuildWithDictionnary( result )            
        JumpWallTimeLine.endRebuildEventTimeLine(connection)
        
    if ( showGraph ):
        plt.show()
    
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Wall Jump" , tmin=tmin, tmax=tmax )

     
    print( "Rebuild event finished." )
        
        
        
        
        
        
        
    