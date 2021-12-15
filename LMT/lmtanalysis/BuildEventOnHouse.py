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
from lmtanalysis.FileUtil import getFilesToProcess

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "onHouse" )

def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None, showGraph = False ): 
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
    
    '''
    centerX = 512/2
    centerY = 424/2
    
    if ( showGraph ):
        plt.figure( 1 )
    '''
    
    # find threshold
    massZs = []
    headZs = []
    backZs = []

    '''
    for animal in pool.animalDictionnary.keys():
        
        animalA = pool.animalDictionnary[animal]        
        dicA = animalA.detectionDictionnary
        for t in dicA.keys():
            
            massZs.append( dicA[t].massZ )
            
            if dicA[t].frontZ > 0:
                headZs.append( dicA[t].frontZ )
            
            if dicA[t].backZ > 0:
                backZs.append( dicA[t].backZ )
            
    headZThreshold = np.percentile( headZs, 95 )
    massZThreshold = np.percentile( massZs, 95 )
    backZThreshold = np.percentile( backZs, 95 )
    '''
    headZThreshold = 50 -20
    massZThreshold = 148 -20
    backZThreshold = 30 -20 
    eventName = "onHouse"
    
    '''
    for animal in pool.animalDictionnary.keys():
        print(pool.animalDictionnary[animal])
        t = 335794
        animalA = pool.animalDictionnary[animal]        
        dicA = animalA.detectionDictionnary
        print( "mass: " , dicA[t].massZ )
        print( "head: " , dicA[t].frontZ )
        print( "back: " , dicA[t].backZ )
        
    
    quit()
    '''
    
    #deleteEventTimeLineInBase(connection, "onHouse" )
    
    for animal in pool.animalDictionnary.keys():
        print(pool.animalDictionnary[animal])
               
        print ( "X is on the house")        
        print ( eventName )
                
        onHouseTimeLine = EventTimeLine( None, eventName , animal , None , None , None , loadEvent=False )
        centerZoneTimeLineDic = EventTimeLine( connection, "Center Zone" , animal ).getDictionary()
        
        result={}
        
        animalA = pool.animalDictionnary[animal]        
        dicA = animalA.detectionDictionnary
        
        for t in dicA.keys():
            
            if not t in centerZoneTimeLineDic:
                # avoid rearing on wall
                continue
            
            massOk = False
            headOk = False
            backOk = False
            
            if dicA[t].massZ > massZThreshold:
                massOk = True
            
            if dicA[t].frontZ > 0:
                if dicA[t].frontZ > headZThreshold:
                    headOk = True
                    
            if dicA[t].backZ > 0:
                if dicA[t].backZ > backZThreshold:
                    backOk = True
                            
            if massOk and headOk : # and backOk
                result[t] = True
                #print ( t , dicA[t].massZ , dicA[t].frontZ ) 
        
        
        '''
        print( np.percentile( allVals, 95 ) )
        print( np.percentile( allVals, 99 ) )

        plt.figure( 1 )
        plt.hist( allVals , bins = 1000 )
        plt.show()
        '''
                
        
        onHouseTimeLine.reBuildWithDictionnary( result )  
        onHouseTimeLine.removeEventsBelowLength( 5 )
        onHouseTimeLine.mergeCloseEvents( 30 )          
        onHouseTimeLine.endRebuildEventTimeLine(connection)
        print( onHouseTimeLine )
        #quit()
        
    '''
    if ( showGraph ):
        plt.show()
    '''
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Wall Jump" , tmin=tmin, tmax=tmax )

     
    print( "Rebuild event finished." )
        
if __name__ == '__main__':
    
    files = getFilesToProcess()

    chronoFullBatch = Chronometer("Full batch" )

    if ( files != None ):

        for file in files:
            
            print ( "Processing file" , file )
            connection = sqlite3.connect( file )
            animalPool = AnimalPool( )
            animalPool.loadAnimals( connection )
            
            '''
            currentMinT = 335794-30
            currentMaxT = 335794+30
            '''
            
            
            currentMinT = 0
            #currentMaxT = 60*oneMinute
            
            #currentMaxT = 6*oneHour #3*oneDay
            currentMaxT = 3*oneDay
            
            animalPool.loadDetection( start = currentMinT, end = currentMaxT )
            reBuildEvent( connection, file, tmin=currentMinT, tmax=currentMaxT, pool = animalPool )
            
            
            
    chronoFullBatch.printTimeInS()
    print( "*** ALL JOBS DONE ***")

        
        
        
        
        
    