'''
Created on 18 dec. 2018

@author: Fab
'''

import sqlite3
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Measure import *
from lmtanalysis.Event import EventTimeLine, plotMultipleTimeLine

if __name__ == '__main__':
    
    #ask the user for database to process
    files = getFilesToProcess()
    
    minT = 6*oneHour
    #maxT = 3*oneDay
    maxT = (6+1)*oneHour

    for file in files:
        
        # connect to database
        connection = sqlite3.connect( file )
        
        # create an animalPool, which basically contains your animals
        animalPool = AnimalPool()
        
        # load infos about the animals
        animalPool.loadAnimals( connection )
        animalPool.loadDetection( 0, 1*oneHour )
        
        '''
        min = 0
        max = 24*oneHour        
        for animal in animalPool.getAnimalList():
            bt = animal.getBodyThreshold( tmin= min, tmax = max )
            bs = animal.getMedianBodyHeight( tmin= min , tmax = max )
            print (  "min:\t" , str(min), "\tmax:\t", str(max), "\tAnimal:\t" , str(animal.baseId), "\tBT:\t " , str(bt) , "\tBS:\t" , str(bs) )

        print("---")
        for start in range( 0,24 ):
            print("**********")
            min = start*oneHour
            max = (start+1)*oneHour        
            for animal in animalPool.getAnimalList():
                bt = animal.getBodyThreshold( tmin= min, tmax = max )
                bs = animal.getMedianBodyHeight( tmin= min , tmax = max )
                print (  "min:\t" , str(min), "\tmax:\t", str(max), "\tAnimal:\t" , str(animal.baseId), "\tBT:\t " , str(bt) , "\tBS:\t" , str(bs) )
        
        quit()
        
        '''
        
        eventTimeLineList = []

        naiveMoveTimeLine = EventTimeLine( connection, "Stop", idA = 1, minFrame=minT, maxFrame=maxT, inverseEvent=True )
        print( "MOVE")
        print( "Naive move Total time: " , str ( naiveMoveTimeLine.getTotalLength() ) )
        naiveMoveTimeLine.plotTimeLine()
        
        detectionMoveTimeLine = EventTimeLine( connection, "Detection", idA = 1, minFrame=minT, maxFrame=maxT )
        eventTimeLineList.append( detectionMoveTimeLine )
             
        eventTimeLineList.append( naiveMoveTimeLine )

        eventTimeLine = EventTimeLine( connection, "Move", idA = 1, minFrame = minT, maxFrame = maxT )
        
        for event in eventTimeLine.getEventList():
            print (event)
        
        print( "Total time corrected move: " , str ( eventTimeLine.getTotalLength() ) )
        
        eventTimeLineList.append( eventTimeLine )
        
        eventTimeLine.plotTimeLine()
        
        plotMultipleTimeLine( eventTimeLineList )
        
        for i in range( 0 , 100 ):
            print("---")
            print ( naiveMoveTimeLine.getEventList()[i] )
            print ( eventTimeLine.getEventList()[i] )
    
    