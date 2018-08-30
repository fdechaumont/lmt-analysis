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
    BuildEventStop, BuildEventWaterPoint

from tkinter.filedialog import askopenfilename
from database.Util import getMinTMaxTAndFileNameInput




if __name__ == '__main__':
    
    print("Code launched.")
    '''
    compute behavioural traits for each individual within a group of mice having the same genotype/strain
    computation of individual and social traits.
    '''
   
        
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    tmin, tmax, text_file = getMinTMaxTAndFileNameInput()

    '''
    min_dur = 48*oneHour
    max_dur = 72*oneHour
    '''
        
    
    
    #behaviouralEventOneMouse = ["Approach contact", "Approach rear", "Break contact", "Contact", "FollowZone Isolated", "Group2", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Social escape", "Train2"]
    behaviouralEventOneMouse = ["Contact", "Group2", "Group3", "Group 3 break", "Group 3 make", "Group4", "Group 4 break", "Group 4 make", "Huddling", "Move isolated", "Move in contact", "Nest3", "Rearing", "Rear isolated", "Rear in contact", "Stop isolated", "WallJump", "Water Zone", "Approach contact", "Approach rear", "Break contact", "FollowZone Isolated", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Social escape", "Train2"]
    behaviouralEventTwoMice = None
    behaviouralEventTwoMice = ["Approach contact", "Approach rear", "Break contact", "Contact", "FollowZone Isolated", "Group2", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Social escape", "Train2"] 
    '''
    behaviouralEventOneMouse = ["Group3", "Water Zone"]
    behaviouralEventTwoMice = ["Contact", "Oral-genital Contact"] 
    '''
    
    '''
    text_file = open ("measures_identity_profile_cc2_social_day3.txt", "w")
    '''
    
    for file in files:
        
        print(file)
        connection = sqlite3.connect( file )
        
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        '''
        pool.loadDetection( start = min_dur, end = max_dur)
        
        for idAnimalA in pool.animalDictionnary.keys():
            
            print ( pool.animalDictionnary[idAnimalA].RFID )
            #total distance traveled
            totalDistance = pool.animalDictionnary[idAnimalA].getDistance(tmin = min_dur, tmax = max_dur)
            resTotalDistance = [file, pool.animalDictionnary[idAnimalA].RFID, min_dur, max_dur, totalDistance]
            text_file.write( "{}\t{}\t{}\t{}\t{}\n".format( file, pool.animalDictionnary[idAnimalA].RFID, min_dur, max_dur, totalDistance ) ) 
        
        '''
        
        ''' 
        #old output
        for behavEvent in behaviouralEventOneMouse:
            
            print( "computing individual event: {}".format(behavEvent))    
            behavEventTimeLine = {}
        
            for idAnimalA in pool.animalDictionnary.keys():
                behavEventTimeLine[idAnimalA] = EventTimeLine( connection, behavEvent, idAnimalA, minFrame=tmin, maxFrame=tmax )
                
                event = behavEventTimeLine[idAnimalA]
                
                totalEventDuration = event.getTotalLength()
                nbEvent = event.getNumberOfEvent(minFrame = tmin, maxFrame = tmax )

                
                print(event.eventName, event.idA, totalEventDuration, nbEvent)
                
                resOneMouse = [file, event.eventName, pool.animalDictionnary[idAnimalA].RFID, totalEventDuration, nbEvent]
                text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( file, event.eventName, pool.animalDictionnary[idAnimalA].RFID, tmin, tmax, totalEventDuration, nbEvent ) ) 
        '''            
        
        animal ={}
        
        for idAnimalA in pool.animalDictionnary.keys():
        
            print( "computing individual animal: {}".format( idAnimalA ))
            rfid = pool.animalDictionnary[idAnimalA].RFID
            print( "RFID: ".format( rfid ) )
            animal[rfid] = {}
            ''' store the animal '''
            animal[rfid]["animal"] = pool.animalDictionnary[idAnimalA]

            for behavEvent in behaviouralEventOneMouse:
                
                print( "computing individual event: {}".format(behavEvent))    
                
                behavEventTimeLine = EventTimeLine( connection, behavEvent, idAnimalA, minFrame=tmin, maxFrame=tmax )
                
                totalEventDuration = behavEventTimeLine.getTotalLength()
                nbEvent = behavEventTimeLine.getNumberOfEvent(minFrame = tmin, maxFrame = tmax )
                
                animal[rfid][behavEventTimeLine.eventName+" TotalLen"] = totalEventDuration
                animal[rfid][behavEventTimeLine.eventName+" Nb"] = nbEvent
                
                print(behavEventTimeLine.eventName, behavEventTimeLine.idA, totalEventDuration, nbEvent)
            
        print ("writing...")
        
        if ( behaviouralEventTwoMice != None ):
            
            for behavEvent in behaviouralEventTwoMice:
                
                print( "computing {} density".format(behavEvent))
                
                for idAnimalA in pool.animalDictionnary.keys():
                    for idAnimalB in pool.animalDictionnary.keys():
                        if ( idAnimalA == idAnimalB ):
                            continue
                    
                        behavEventTimeLine[idAnimalA, idAnimalB] = EventTimeLine( connection, behavEvent, idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax )
                        
                        event = behavEventTimeLine[idAnimalA, idAnimalB]
                            
                        totalEventDuration = event.getTotalLength()
                        nbEvent = event.getNumberOfEvent(minFrame = tmin, maxFrame = tmax)
                
                            
                        print( behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalB].RFID )
                    
                        resSame = [file, behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalB].RFID, tmin, tmax, totalEventDuration, nbEvent]
                    
                        text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( file, behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalB].RFID, tmin, tmax, totalEventDuration, nbEvent ) ) 
        
    text_file.write( "\n" )
    text_file.close()
                
                
            
            
            