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
from sqlalchemy.sql.expression import false
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.FileUtil import getFilesToProcess




def getNumberOfEventWithList( connection, file, eventName, animal , animalList, minFrame=None, maxFrame=None ):
    
    sumOfEvent = 0
    for animalCandidate in animalList:
        
        timeLine = EventTimeLineCached( connection , file, eventName , animal , animalCandidate.baseId, minFrame=minFrame, maxFrame=maxFrame )
        sumOfEvent += timeLine.getNbEvent()
    
    return sumOfEvent


def getDurationOfEventWithList( connection, file, eventName, animal , animalList, minFrame=None, maxFrame=None ):
    
    durationOfEvent = 0
    for animalCandidate in animalList:
        
        timeLine = EventTimeLineCached( connection , file, eventName , animal , animalCandidate.baseId, minFrame=minFrame, maxFrame=maxFrame )
        durationOfEvent += timeLine.getTotalLength()
    
    return durationOfEvent


if __name__ == '__main__':
    
    print("Code launched.")
 
 
    files = getFilesToProcess()
    tmin, tmax, text_file = getMinTMaxTAndFileNameInput()

    #behaviouralEventTwoMice = ["Approach contact", "Approach rear", "Break contact", "Contact", "FollowZone Isolated", "Group2", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Get away", "Train2"] 
    behaviouralEventTwoMice = ["Get away"]
    

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
        
        nightEventTimeLine = EventTimeLineCached( connection, file, "night", minFrame=tmin, maxFrame=tmax )
        n = 1
        header = ["file","event", "RFID_A", "geno_A", "RFID_B", "geno_B", "minTime","maxTime","dur", "nb"]
        for name in header:
            text_file.write( "{}\t".format ( name ) ) 
        
        text_file.write( "{}\n".format ( "night" ) )    
                
        for eventNight in nightEventTimeLine.getEventList():
            
            minT = eventNight.startFrame
            maxT = eventNight.endFrame
            print("Night: ", n)
            
            for behavEvent in behaviouralEventTwoMice:
                        
                print( "computing {} density".format(behavEvent))
                
                for animal in pool.animalDictionnary:
                    animalDiffGeno = []
                    animalSameGeno = []
                    
                    for animal in pool.animalDictionnary:
                        if ( pool.animalDictionnary[animal].baseId == pool.animalDictionnary[animal].baseId ):
                            continue
                        
                        if pool.animalDictionnary[animal].genotype == pool.animalDictionnary[animal].genotype:
                            animalSameGeno.append( pool.animalDictionnary[animal] )
                        else:
                            animalDiffGeno.append( pool.animalDictionnary[animal] )
                            
                    nbEventsSameGeno = getNumberOfEventWithList(connection, file, behavEvent, animal, animalSameGeno, minFrame=minT, maxFrame=maxT)
                    durEventsSameGeno = getDurationOfEventWithList(connection, file, behavEvent, animal, animalSameGeno, minFrame=minT, maxFrame=maxT)
                    
                    nbEventsDiffGeno = 0
                    durEventsDiffGeno = 0
                    
                    if ( MODE_MULTI_GENOTYPE == True ):                            
                        nbEventsDiffGeno = getNumberOfEventWithList(connection, file, behavEvent, animal, animalDiffGeno, minFrame=minT, maxFrame=maxT)
                        durEventsDiffGeno = getDurationOfEventWithList(connection, file, behavEvent, animal, animalDiffGeno, minFrame=minT, maxFrame=maxT)
                            
                    print( behavEvent, pool.animalDictionnary[animal].RFID )
                    
                    resSame = [file, behavEvent, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[animal].genotype, "sameGeno", durEventsSameGeno, nbEventsSameGeno]
                    #text_file.write( "{}\n".format( resSame ) )
                    if ( MODE_MULTI_GENOTYPE == True ):
                        resDiff = [file, behavEvent, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[animal].genotype, "diffGeno", durEventsDiffGeno, nbEventsDiffGeno]
                        #text_file.write( "{}\n".format( resDiff ) )
                             
            ''' matrix output ''' 
            
                
            text_file.write( "night {}\n".format( n ) )
                
            for behavEvent in behaviouralEventTwoMice:
                    
                
                print( "computing {} ".format(behavEvent))
                
                for animal in pool.animalDictionnary.keys():
                    for idAnimalB in pool.animalDictionnary.keys():
                        if ( animal == idAnimalB ):
                            continue
                    
                        event = EventTimeLineCached( connection, file, behavEvent, animal, idAnimalB, minFrame=minT, maxFrame=maxT )
                        
                        totalEventDuration = event.getTotalLength()
                        nbEvent = event.getNumberOfEvent(minFrame = minT, maxFrame = maxT)
                
                        print( behavEvent, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[idAnimalB].RFID )
                    
                        resSame = [file, behavEvent, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[idAnimalB].RFID, minT, maxT, totalEventDuration, nbEvent]
                    
                        text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( file, behavEvent, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[animal].genotype, pool.animalDictionnary[idAnimalB].RFID, pool.animalDictionnary[idAnimalB].genotype, minT, maxT, totalEventDuration, nbEvent ) ) 
                         
            n+=1                 
                        
    text_file.write( "\n" )
    text_file.close()
       
    print ("done.")
            
         
                
                
            
            
            