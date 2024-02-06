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
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.Parameters import getAnimalTypeParameters
from lmtanalysis.TaskLogger import TaskLogger

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "in house corner" )
    deleteEventTimeLineInBase(connection, "over house" )


def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None, animalType=None ): 
    
    parameters = getAnimalTypeParameters( animalType )
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax, lightLoad=False )
    

    for animal in pool.animalDictionary.keys():
        print(pool.animalDictionary[animal])
        
        eventName1 = "in house corner"
        eventName2 = "over house"        
                
        houseCornerTimeLine = EventTimeLine( None, eventName1 , animal , None , None , None , loadEvent=False )
        overHouseTimeLine = EventTimeLine( None, eventName2 , animal , None , None , None , loadEvent=False )
                        
        resultHouseCorner={}
        resultOverHouse={}
        
        animalA = pool.animalDictionary[animal]
        #print ( animalA )
        dicA = animalA.detectionDictionary
        
        '''        
           if cornerNb==4:
        corner=(100,-350)
        distance = 200

        animalsInCorner = []
        
        for animal in pool.getAnimalList():
            d = animal.getDistanceToPoint( t , corner[0] , -corner[1] )        
            if d!=None:
                
                
                if d < distance: # distance to corner
                    animalsInCorner.append( animal )
                    #return animal
        
        return animalsInCorner
        ''' 
        
        for t in dicA.keys():
            dist = dicA[t].getDistanceToPoint( xPoint = 100, yPoint = 350)
            if dist == None: # bottom left corner
                continue
            if dist < 200:
                resultHouseCorner[t] = True
            
            if dist < 100 and dist> 25:
                if dicA[t].massZ > 130:
                    resultOverHouse[t] = True
                        
        houseCornerTimeLine.reBuildWithDictionary( resultHouseCorner )
        houseCornerTimeLine.endRebuildEventTimeLine(connection)
        
        overHouseTimeLine.reBuildWithDictionary( resultOverHouse )
        overHouseTimeLine.mergeCloseEvents( 30 )
        overHouseTimeLine.endRebuildEventTimeLine(connection)
    
        
    # log process
    
    t = TaskLogger( connection )
    t.addLog( "Build Event House" , tmin=tmin, tmax=tmax )

    print( "Rebuild event finished." )
        
        
        
        
        
        
        
    