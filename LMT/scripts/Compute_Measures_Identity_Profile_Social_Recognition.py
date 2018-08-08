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

    files = askopenfilename( title="Choose a set of files to process", multiple=1)
    #files = ["/Users/elodie/Documents/2018_04_shank2_miscellanous_paper/2017_social_recognition/shank2_databases_social_recognition/20170320_4648-4722_juv1-4678.sqlite"]
    
    min_dur = 10*oneSecond
    max_dur = min_dur + 2*oneMinute
    
    behaviouralEventOneMouse = ["Group3", "Group 3 break", "Group 3 make", "Move isolated", "Move in contact", "Rearing", "Rear isolated", "Rear in contact", "Stop isolated", "WallJump"]
    behaviouralEventTwoMice = ["Approach contact", "Approach rear", "Break contact", "Contact", "Group2", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Social escape", "Train2"] 
    
    
    text_file = open ("shank2_social_recognition.txt", "w")
    
    for file in files:
        
        print(file)
        connection = sqlite3.connect( file )
        
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        
        
        for behavEvent in behaviouralEventOneMouse:
            
            print( "computing individual event: {}".format(behavEvent))    
            behavEventTimeLine = {}
        
            for idAnimalA in pool.animalDictionnary.keys():
                behavEventTimeLine[idAnimalA] = EventTimeLine( connection, behavEvent, idAnimalA, minFrame=0, maxFrame=max_dur )
                
                event = behavEventTimeLine[idAnimalA]
                
                totalEventDuration = event.getTotalLength()
                nbEvent = event.getNumberOfEvent(minFrame = min_dur, maxFrame = max_dur)

                genoA = None
                try:
                    genoA=pool.animalDictionnary[idAnimalA].genotype
                except:
                    pass
                
                
                print(event.eventName, genoA, event.idA, totalEventDuration, nbEvent)
                
                resOneMouse = [file, event.eventName, pool.animalDictionnary[idAnimalA].RFID, genoA, totalEventDuration, nbEvent]
                text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\n".format( file, event.eventName, pool.animalDictionnary[idAnimalA].RFID, genoA, totalEventDuration, nbEvent ) ) 
                       
                
        
        
        for behavEvent in behaviouralEventTwoMice:
            
            print( "computing {} density".format(behavEvent))
            
            for idAnimalA in pool.animalDictionnary:
                animalDiffGeno = []
                animalB6Geno = []
                
                for animal in pool.animalDictionnary:
                    if ( pool.animalDictionnary[animal].baseId == pool.animalDictionnary[idAnimalA].baseId ):
                        continue
                    
                    if pool.animalDictionnary[animal].genotype == "B6":
                        animalB6Geno.append( pool.animalDictionnary[animal] )
                    else:
                        animalDiffGeno.append( pool.animalDictionnary[animal] )
                        
                nbEventsB6Geno = getNumberOfEventWithList(connection, behavEvent, idAnimalA, animalB6Geno, minFrame=min_dur, maxFrame=max_dur)
                durEventsB6Geno = getDurationOfEventWithList(connection, behavEvent, idAnimalA, animalB6Geno, minFrame=min_dur, maxFrame=max_dur)
                nbEventsDiffGeno = getNumberOfEventWithList(connection, behavEvent, idAnimalA, animalDiffGeno, minFrame=min_dur, maxFrame=max_dur)
                durEventsDiffGeno = getDurationOfEventWithList(connection, behavEvent, idAnimalA, animalDiffGeno, minFrame=min_dur, maxFrame=max_dur)
            
            
                        
                print( behavEvent, pool.animalDictionnary[idAnimalA].RFID )
                
                resSame = [file, behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalA].genotype, "B6", durEventsB6Geno, nbEventsB6Geno]
                resDiff = [file, behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalA].genotype, "diffGeno", durEventsDiffGeno, nbEventsDiffGeno]
                text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( file, behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalA].genotype, "B6", durEventsB6Geno, nbEventsB6Geno ) ) 
            
        
        
                
    text_file.write( "\n" )
    text_file.close()
                
                
            
            
            