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
from sqlalchemy.sql.expression import false



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
    setName = "night 1"
    min_dur = 0*oneDay
    max_dur = min_dur+ 23*oneHour
    '''
    
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
    

    behaviouralEventTwoMice = ["Approach contact", "Approach rear", "Break contact", "Contact", "FollowZone Isolated", "Group2", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Social escape", "Train2"] 

    for file in files:
        
        print(file)
        connection = sqlite3.connect( file )
        
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        
        MODE_MULTI_GENOTYPE =False
        if ( len ( pool.getGenotypeList() ) > 1 ):
            MODE_MULTI_GENOTYPE = True
            
        print ("Mode multi genotype: " , MODE_MULTI_GENOTYPE )
        animal = {}
        
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
                        
                nbEventsSameGeno = getNumberOfEventWithList(connection, behavEvent, idAnimalA, animalSameGeno, minFrame=tmin, maxFrame=tmax)
                durEventsSameGeno = getDurationOfEventWithList(connection, behavEvent, idAnimalA, animalSameGeno, minFrame=tmin, maxFrame=tmax)
                
                nbEventsDiffGeno = 0
                durEventsDiffGeno = 0
                
                if ( MODE_MULTI_GENOTYPE == True ):                            
                    nbEventsDiffGeno = getNumberOfEventWithList(connection, behavEvent, idAnimalA, animalDiffGeno, minFrame=tmin, maxFrame=tmax)
                    durEventsDiffGeno = getDurationOfEventWithList(connection, behavEvent, idAnimalA, animalDiffGeno, minFrame=tmin, maxFrame=tmax)
                        
                print( behavEvent, pool.animalDictionnary[idAnimalA].RFID )
                
                resSame = [file, behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalA].genotype, "sameGeno", durEventsSameGeno, nbEventsSameGeno]
                text_file.write( "{}\n".format( resSame ) )
                if ( MODE_MULTI_GENOTYPE == True ):
                    resDiff = [file, behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalA].genotype, "diffGeno", durEventsDiffGeno, nbEventsDiffGeno]
                    text_file.write( "{}\n".format( resDiff ) )
                         
        ''' matrix output '''        
        text_file.write( "\n****** diadic OutPut:\n" )
            
        for behavEvent in behaviouralEventTwoMice:
                
            
            print( "computing {} ".format(behavEvent))
            
            for idAnimalA in pool.animalDictionnary.keys():
                for idAnimalB in pool.animalDictionnary.keys():
                    if ( idAnimalA == idAnimalB ):
                        continue
                
                    event = EventTimeLine( connection, behavEvent, idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax )
                    
                    totalEventDuration = event.getTotalLength()
                    nbEvent = event.getNumberOfEvent(minFrame = tmin, maxFrame = tmax)
            
                    print( behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalB].RFID )
                
                    resSame = [file, behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalB].RFID, tmin, tmax, totalEventDuration, nbEvent]
                
                    text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( file, behavEvent, pool.animalDictionnary[idAnimalA].RFID, pool.animalDictionnary[idAnimalB].RFID, tmin, tmax, totalEventDuration, nbEvent ) ) 
                     
                         
                    
    text_file.write( "\n" )
    text_file.close()
       
    print ("done.")
            
         
                
                
            
            
            