'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis import BuildEventTrain3, BuildEventTrain4, BuildEventFollowZone, BuildEventRear5, BuildEventFloorSniffing,\
    BuildEventSocialApproach, BuildEventSocialEscape, BuildEventApproachContact,\
    BuildEventApproachRear, BuildEventGroup2, BuildEventGroup3, BuildEventGroup4,\
    BuildEventStop, BuildEventWaterPoint

from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import getMinTMaxTAndFileNameInput





if __name__ == '__main__':
    
    print("Code launched.")
    '''
    compute behavioural traits for each individual for two mice (one for the tested strain and one control mouse)
    computation of individual and social traits.
    '''
 
        
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    tmin, tmax, text_file = getMinTMaxTAndFileNameInput()

    '''
    min_dur = 10*oneSecond
    max_dur = min_dur + 10*oneMinute
    '''
    
    behaviouralEventOneMouse = ["Contact", "Group2", "Huddling", "Move isolated", "Move in contact", "Rearing", "Rear isolated", "Rear in contact", "Stop isolated", "WallJump"]
    behaviouralEventTwoMice = ["Approach contact", "Approach rear", "Break contact", "Contact", "FollowZone Isolated", "Group2", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Social escape", "Train2"] 
    
    for file in files:
        
        print(file)
        connection = sqlite3.connect( file )
        
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        
        pool.loadDetection( start = tmin, end = tmax )
        
        for animal in pool.animalDictionnary.keys():
            
            print ( pool.animalDictionnary[animal].RFID )
            #total distance traveled
            totalDistance = pool.animalDictionnary[animal].getDistance(tmin = tmin , tmax = tmax )
            resTotalDistance = [file, pool.animalDictionnary[animal].RFID, tmin, tmax, totalDistance]
            text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\n".format( file, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[animal].genotype, tmin, tmax, totalDistance ) ) 
  
            
        for behavEvent in behaviouralEventOneMouse:
            
            print( "computing individual event: {}".format(behavEvent))    
            behavEventTimeLine = {}
        
            for animal in pool.animalDictionnary.keys():
                behavEventTimeLine[animal] = EventTimeLine( connection, behavEvent, animal, minFrame=tmin, maxFrame=tmax )
                
                event = behavEventTimeLine[animal]
                
                totalEventDuration = event.getTotalLength()
                nbEvent = event.getNumberOfEvent(minFrame = tmin, maxFrame = tmax)

                
                print(event.eventName, event.idA, totalEventDuration, nbEvent)
                
                resOneMouse = [file, event.eventName, pool.animalDictionnary[animal].RFID, totalEventDuration, nbEvent]
                text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( file, event.eventName, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[animal].genotype, tmin, tmax, totalEventDuration, nbEvent ) ) 
                       
                

        for behavEvent in behaviouralEventTwoMice:
            
            print( "computing {} density".format(behavEvent))
            
            for animal in pool.animalDictionnary.keys():
                for idAnimalB in pool.animalDictionnary.keys():
                    if ( animal == idAnimalB ):
                        continue
                
                    behavEventTimeLine[animal, idAnimalB] = EventTimeLine( connection, behavEvent, animal, idAnimalB, minFrame=tmin, maxFrame=tmax )
                    
                    event = behavEventTimeLine[animal, idAnimalB]
                        
                    totalEventDuration = event.getTotalLength()
                    nbEvent = event.getNumberOfEvent(minFrame = tmin, maxFrame = tmax)
            
                        
                    print( behavEvent, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[idAnimalB].RFID )
                
                    resSame = [file, behavEvent, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[idAnimalB].RFID, tmin, tmax, totalEventDuration, nbEvent]
                
                    text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( file, behavEvent, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[animal].genotype, pool.animalDictionnary[idAnimalB].RFID, pool.animalDictionnary[idAnimalB].genotype, tmin, tmax, totalEventDuration, nbEvent ) ) 
            

    text_file.write( "\n" )
    text_file.close()
                
    print( "FINISHED" )
                
            
            
            