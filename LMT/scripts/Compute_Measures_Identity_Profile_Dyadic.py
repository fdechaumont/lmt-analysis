'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from database.Animal import *
import matplotlib.pyplot as plt
from database.Event import *
from database.Measure import *
from database import BuildEventTrain3, BuildEventTrain4, BuildEventFollowZone, BuildEventRear5, BuildEventFloorSniffing,\
    BuildEventSocialApproach, BuildEventSocialEscape, BuildEventApproachContact,\
    BuildEventApproachRear, BuildEventGroup2, BuildEventGroup3, BuildEventGroup4,\
    BuildEventStop, BuildEventWaterPoint, BuildEventSequentialRearing, BuildEventSequentialRearing2

from tkinter.filedialog import askopenfilename





if __name__ == '__main__':
    
    print("Code launched.")
    '''
    compute behavioural traits for each individual for two mice (one for the tested strain and one control mouse)
    computation of individual and social traits.
    '''
 
        
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    
    min_dur = 10*oneSecond
    max_dur = min_dur + 10*oneMinute
    
    #behaviouralEventOneMouse = ["Contact", "Group2"]
    behaviouralEventOneMouse = ["Contact", "Group2", "Huddling", "Move isolated", "Move in contact", "Rearing", "Rear isolated", "Rear in contact", "Stop isolated", "WallJump"]
    behaviouralEventTwoMice = ["Approach contact", "Approach rear", "Break contact", "Contact", "FollowZone Isolated", "Group2", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Social escape", "Train2"] 
    
    text_file = open ("measures_individual_profile_dlx_dyadic.txt", "w")
    
    for file in files:
        
        print(file)
        connection = sqlite3.connect( file )
        
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        
        pool.loadDetection( start = min_dur, end = max_dur)
        
        for idAnimalA in pool.animalDictionnary.keys():
            
            print ( pool.animalDictionnary[idAnimalA].RFID )
            #total distance traveled
            totalDistance = pool.animalDictionnary[idAnimalA].getDistance(tmin = min_dur, tmax = max_dur)
            resTotalDistance = [file, pool.animalDictionnary[idAnimalA].RFID, min_dur, max_dur, totalDistance]
            text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\n".format( file, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalA].genotype, min_dur, max_dur, totalDistance ) ) 
  
            
        for behavEvent in behaviouralEventOneMouse:
            
            print( "computing individual event: {}".format(behavEvent))    
            behavEventTimeLine = {}
        
            for idAnimalA in pool.animalDictionnary.keys():
                behavEventTimeLine[idAnimalA] = EventTimeLine( connection, behavEvent, idAnimalA, minFrame=min_dur, maxFrame=max_dur )
                
                event = behavEventTimeLine[idAnimalA]
                
                totalEventDuration = event.getTotalLength()
                nbEvent = event.getNumberOfEvent(minFrame = min_dur, maxFrame = max_dur)

                
                print(event.eventName, event.idA, totalEventDuration, nbEvent)
                
                resOneMouse = [file, event.eventName, pool.animalDictionnary[idAnimalA].RFID, totalEventDuration, nbEvent]
                text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( file, event.eventName, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalA].genotype, min_dur, max_dur, totalEventDuration, nbEvent ) ) 
                       
                

        for behavEvent in behaviouralEventTwoMice:
            
            print( "computing {} density".format(behavEvent))
            
            for idAnimalA in pool.animalDictionnary.keys():
                for idAnimalB in pool.animalDictionnary.keys():
                    if ( idAnimalA == idAnimalB ):
                        continue
                
                    behavEventTimeLine[idAnimalA, idAnimalB] = EventTimeLine( connection, behavEvent, idAnimalA, idAnimalB, minFrame=min_dur, maxFrame=max_dur )
                    
                    event = behavEventTimeLine[idAnimalA, idAnimalB]
                        
                    totalEventDuration = event.getTotalLength()
                    nbEvent = event.getNumberOfEvent(minFrame = min_dur, maxFrame = max_dur)
            
                        
                    print( behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalB].RFID )
                
                    resSame = [file, behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalB].RFID, min_dur, max_dur, totalEventDuration, nbEvent]
                
                    text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( file, behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalA].genotype, pool.animalDictionnary[idAnimalB].RFID, pool.animalDictionnary[idAnimalB].genotype, min_dur, max_dur, totalEventDuration, nbEvent ) ) 
            

    text_file.write( "\n" )
    text_file.close()
                
                
            
            
            