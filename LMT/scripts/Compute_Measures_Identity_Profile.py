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


def getNumberOfEventWithList( connection, eventName, idAnimalA , animalList, minFrame=None, maxFrame=None ):
    
    sumOfEvent = 0
    for animalCandidate in animalList:
        
        timeLine = EventTimeLine( connection , eventName , idAnimalA , animalCandidate.baseId, minFrame=minFrame, maxFrame=maxFrame )
        sumOfEvent += timeLine.getNbEvent()
    
    return sumOfEvent


def getDurationOfEventWithList( connection, eventName, idAnimalA , animalList, minFrame=None, maxFrame=None ):
    
    durationOfEvent = 0
    for animalCandidate in animalList:
        
        timeLine = EventTimeLine( connection , eventName , idAnimalA , animalCandidate.baseId, minFrame=minFrame, maxFrame=maxFrame )
        durationOfEvent += timeLine.getTotalLength()
    
    return durationOfEvent



if __name__ == '__main__':
    
    print("Code launched.")
 
    setName = "night 1"
    min_dur = 0*oneDay
    max_dur = min_dur+ 23*oneHour
    
    '''
    setName = "night 2"
    min_dur = 1*oneDay
    max_dur = min_dur+ 23*oneHour
    '''

    '''
    setName = "night 3"
    min_dur = 2*oneDay
    max_dur = min_dur+ 23*oneHour
    '''

    '''
    setName = "all"
    min_dur = 0
    max_dur = 2*oneDay + 23*oneHour
    '''
    
    
    behaviouralEventOneMouse = ["Group 4 break", "Group 4 make"]
    #behaviouralEventOneMouse = ["Group3", "Group 3 break", "Group 3 make", "Group4", "Group 4 break", "Group 4 make", "Huddling", "Move isolated", "Move in contact", "Nest3", "Rearing", "Rear isolated", "Rear in contact", "Stop isolated", "WallJump", "Water Zone"]
    behaviouralEventTwoMice = ["Approach contact", "Approach rear", "Break contact", "Contact", "FollowZone Isolated", "Group2", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Social escape", "Train2"] 
    
    text_file = open ("test_measures_individual_profile_shank2_true_"+setName+".txt", "w")
    #text_file = open ("test_measures_individual_profile_shank3_23h_7907.txt", "w")
    
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    
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
            resTotalDistance = [file, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalA].genotype, pool.animalDictionnary[idAnimalA].user1, max_dur, totalDistance]
            text_file.write( "{}\n".format( resTotalDistance ) ) 
        '''    
            
        for behavEvent in behaviouralEventOneMouse:
            
            print( "computing individual event: {}".format(behavEvent))    
            behavEventTimeLine = {}
        
            for idAnimalA in pool.animalDictionnary.keys():
                behavEventTimeLine[idAnimalA] = EventTimeLine( connection, behavEvent, idAnimalA, minFrame=min_dur, maxFrame=max_dur )
                
                event = behavEventTimeLine[idAnimalA]
                
                totalEventDuration = event.getTotalLength()
                nbEvent = event.getNumberOfEvent(minFrame = min_dur, maxFrame = max_dur)

                genoA = None
                try:
                    genoA=pool.animalDictionnary[idAnimalA].genotype
                except:
                    pass
                
                
                print(event.eventName, genoA, event.idA, totalEventDuration, nbEvent)
                
                resOneMouse = [file, event.eventName, pool.animalDictionnary[idAnimalA].RFID, genoA, pool.animalDictionnary[idAnimalA].user1, totalEventDuration, nbEvent]
                text_file.write( "{}\n".format( resOneMouse ) ) 
                       
                
        
        
        for behavEvent in behaviouralEventTwoMice:
            
            print( "computing {} density".format(behavEvent))
            
            for idAnimalA in pool.animalDictionnary:
                animalDiffGeno = []
                animalSameGeno = []
                
                for animal in pool.animalDictionnary:
                    if ( pool.animalDictionnary[animal].baseId == pool.animalDictionnary[idAnimalA].baseId ):
                        continue
                    
                    if pool.animalDictionnary[animal].genotype == pool.animalDictionnary[idAnimalA].genotype:
                        animalSameGeno.append( pool.animalDictionnary[animal] )
                    else:
                        animalDiffGeno.append( pool.animalDictionnary[animal] )
                        
                nbEventsSameGeno = getNumberOfEventWithList(connection, behavEvent, idAnimalA, animalSameGeno, minFrame=min_dur, maxFrame=max_dur)
                durEventsSameGeno = getDurationOfEventWithList(connection, behavEvent, idAnimalA, animalSameGeno, minFrame=min_dur, maxFrame=max_dur)
                nbEventsDiffGeno = getNumberOfEventWithList(connection, behavEvent, idAnimalA, animalDiffGeno, minFrame=min_dur, maxFrame=max_dur)
                durEventsDiffGeno = getDurationOfEventWithList(connection, behavEvent, idAnimalA, animalDiffGeno, minFrame=min_dur, maxFrame=max_dur)
            
            
                        
                print( behavEvent, pool.animalDictionnary[idAnimalA].RFID )
                
                resSame = [file, behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalA].genotype, "sameGeno", durEventsSameGeno, nbEventsSameGeno]
                resDiff = [file, behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalA].genotype, "diffGeno", durEventsDiffGeno, nbEventsDiffGeno]
                text_file.write( "{}\n{}\n".format( resSame, resDiff ) ) 
            
                     
                
    text_file.write( "\n" )
    text_file.close()
                
                
            
            
            