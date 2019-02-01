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
    
    for file in files:
        
        # connect to database
        connection = sqlite3.connect( file )
        
        # create an animalPool, which basically contains your animals
        animalPool = AnimalPool()
        
        # load infos about the animals
        animalPool.loadAnimals( connection )
        animalPool.loadDetection( 0, 3*24*oneHour )
        
        min = 0
        max = 24*oneHour        
        for animal in animalPool.getAnimalList():
            bt = animal.getBodyThreshold( tmin= min, tmax = max )
            bs = animal.getMedianBodyHeight( tmin= min , tmax = max )
            print (  "min:\t" , str(min), "\tmax:\t", str(max), "\tAnimal:\t" , str(animal.baseId), "\tBT:\t " , str(bt) , "\tBS:\t" , str(bs) )

        min = 24*oneHour    
        max = 2*24*oneHour        
        for animal in animalPool.getAnimalList():
            bt = animal.getBodyThreshold( tmin= min, tmax = max )
            bs = animal.getMedianBodyHeight( tmin= min , tmax = max )
            print (  "min:\t" , str(min), "\tmax:\t", str(max), "\tAnimal:\t" , str(animal.baseId), "\tBT:\t " , str(bt) , "\tBS:\t" , str(bs) )

        min = 2*24*oneHour    
        max = 3*24*oneHour        
        for animal in animalPool.getAnimalList():
            bt = animal.getBodyThreshold( tmin= min, tmax = max )
            bs = animal.getMedianBodyHeight( tmin= min , tmax = max )
            print (  "min:\t" , str(min), "\tmax:\t", str(max), "\tAnimal:\t" , str(animal.baseId), "\tBT:\t " , str(bt) , "\tBS:\t" , str(bs) )


        print("---")
        for start in range( 0,3*24 ):
            print("**********")
            min = start*oneHour
            max = (start+1)*oneHour        
            for animal in animalPool.getAnimalList():
                bt = animal.getBodyThreshold( tmin= min, tmax = max )
                bs = animal.getMedianBodyHeight( tmin= min , tmax = max )
                print (  "min:\t" , str(min), "\tmax:\t", str(max), "\tAnimal:\t" , str(animal.baseId), "\tBT:\t " , str(bt) , "\tBS:\t" , str(bs) )
        
        quit()
        
        '''
        moveSourceTimeLine = EventTimeLine( connection, "Stop", 1, minFrame=0, maxFrame=15*oneMinute, inverseEvent=True )
        print( "MOVE")
        print( "Total time: " , str ( moveSourceTimeLine.getTotalLength() ) )
             
        eventTimeLine = EventTimeLine( connection, "Move", idA = 1, minFrame = 0, maxFrame = oneHour )
        
        for event in eventTimeLine.getEventList():
            print (event)
        
        print( "Total time: " , str ( eventTimeLine.getTotalLength() ) )
        
        eventTimeLine.plotTimeLine()
        '''
        
            
    
    