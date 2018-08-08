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

    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    tmin, tmax, text_file = getMinTMaxTAndFileNameInput()
    
    '''
    min_dur = 10*oneSecond
    max_dur = min_dur + 2*oneMinute
    '''
    
    behaviouralEventOneMouse = ["Group3", "Group 3 break", "Group 3 make", "Move isolated", "Move in contact", "Rearing", "Rear isolated", "Rear in contact", "Stop isolated", "WallJump"]
    behaviouralEventTwoMice = ["Approach contact", "Approach rear", "Break contact", "Contact", "Group2", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Social escape", "Train2"] 
    
    '''
    text_file = open ("shank2_social_recognition.txt", "w")
    '''
    
    for file in files:
        
        print(file)
        connection = sqlite3.connect( file )
        
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        
        
        for behavEvent in behaviouralEventOneMouse:
            
            print( "computing individual event: {}".format(behavEvent))    
            behavEventTimeLine = {}
        
            for idAnimalA in pool.animalDictionnary.keys():
                behavEventTimeLine[idAnimalA] = EventTimeLine( connection, behavEvent, idAnimalA, minFrame=tmin, maxFrame=tmax )
                
                event = behavEventTimeLine[idAnimalA]
                
                totalEventDuration = event.getTotalLength()
                nbEvent = event.getNumberOfEvent(minFrame = tmin, maxFrame = tmax)

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
                        
                nbEventsB6Geno = getNumberOfEventWithList(connection, behavEvent, idAnimalA, animalB6Geno, minFrame=tmin, maxFrame=tmax)
                durEventsB6Geno = getDurationOfEventWithList(connection, behavEvent, idAnimalA, animalB6Geno, minFrame=tmin, maxFrame=tmax)
                nbEventsDiffGeno = getNumberOfEventWithList(connection, behavEvent, idAnimalA, animalDiffGeno, minFrame=tmin, maxFrame=tmax)
                durEventsDiffGeno = getDurationOfEventWithList(connection, behavEvent, idAnimalA, animalDiffGeno, minFrame=tmin, maxFrame=tmax)
            
            
                        
                print( behavEvent, pool.animalDictionnary[idAnimalA].RFID )
                
                resSame = [file, behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalA].genotype, "B6", durEventsB6Geno, nbEventsB6Geno]
                resDiff = [file, behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalA].genotype, "diffGeno", durEventsDiffGeno, nbEventsDiffGeno]
                text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( file, behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalA].genotype, "B6", durEventsB6Geno, nbEventsB6Geno ) ) 
            
        
        
                
    text_file.write( "\n" )
    text_file.close()
                
                
            
            
            