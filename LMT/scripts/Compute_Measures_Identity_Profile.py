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



def getNumberOfEventWithList( connection, eventName, animal , animalList, minFrame=None, maxFrame=None ):
    
    sumOfEvent = 0
    for animalCandidate in animalList:
        
        timeLine = EventTimeLine( connection , eventName , animal , animalCandidate.baseId, minFrame=minFrame, maxFrame=maxFrame )
        sumOfEvent += timeLine.getNbEvent()
    
    return sumOfEvent


def getDurationOfEventWithList( connection, eventName, animal , animalList, minFrame=None, maxFrame=None ):
    
    durationOfEvent = 0
    for animalCandidate in animalList:
        
        timeLine = EventTimeLine( connection , eventName , animal , animalCandidate.baseId, minFrame=minFrame, maxFrame=maxFrame )
        durationOfEvent += timeLine.getTotalLength()
    
    return durationOfEvent



if __name__ == '__main__':
    
    print("Code launched.")
 
   
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
    
    
    behaviouralEventOneMouse = ["Side by side Contact, opposite way"]
    #behaviouralEventOneMouse = ["Look down", "Huddling", "WallJump", "SAP", "Move isolated", "Stop isolated", "Rear isolated", "Nest3", "Move in contact", "Rear in contact", "Contact",  "Side by side Contact", "Side by side Contact, opposite way", "Oral-oral Contact", "Oral-genital Contact", "Group2", "Group3", "Train2", "Train3", "Train4", "FollowZone Isolated", "Social approach", "Approach rear", "Approach contact", "Group 3 make", "Group 4 make", "Social escape", "Break contact", "Group 3 break", "Group 4 break", "seq oral oral - oral genital", "seq oral geni - oral oral"]
    #behaviouralEventOneMouse = ["Group3", "Group 3 break", "Group 3 make", "Group4", "Group 4 break", "Group 4 make", "Huddling", "Move isolated", "Move in contact", "Nest3", "Rearing", "Rear isolated", "Rear in contact", "Stop isolated", "WallJump", "Water Zone"]
    behaviouralEventTwoMice = None
    #behaviouralEventTwoMice = ["Approach contact", "Approach rear", "Break contact", "Contact", "FollowZone Isolated", "Group2", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Social escape", "Train2"] 
    
    #text_file = open ("test_measures_individual_profile_shank3_23h_7907.txt", "w")
    
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    tmin, tmax, text_file = getMinTMaxTAndFileNameInput()

    for file in files:
        
        print(file)
        connection = sqlite3.connect( file )
        
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        '''
        pool.loadDetection( start = min_dur, end = max_dur)
        
        for animal in pool.animalDictionnary.keys():
            
            print ( pool.animalDictionnary[animal].RFID )
            #total distance traveled
            totalDistance = pool.animalDictionnary[animal].getDistance(tmin = min_dur, tmax = max_dur)
            resTotalDistance = [file, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[animal].genotype, pool.animalDictionnary[animal].user1, max_dur, totalDistance]
            text_file.write( "{}\n".format( resTotalDistance ) ) 
        '''    
        
        '''
        new version for one animal export
        '''
        
        animal = {}

        for animal in pool.animalDictionnary.keys():
        
            print( "computing individual animal: {}".format( animal ))
            rfid = pool.animalDictionnary[animal].RFID
            print( "RFID: ".format( rfid ) )
            animal[rfid] = {}
            ''' store the animal '''
            animal[rfid]["animal"] = pool.animalDictionnary[animal]
            genoA = None
            try:
                genoA=pool.animalDictionnary[animal].genotype
            except:
                pass
                        
            for behavEvent in behaviouralEventOneMouse:
                
                print( "computing individual event: {}".format(behavEvent))    
                
                behavEventTimeLine = EventTimeLine( connection, behavEvent, animal, minFrame=tmin, maxFrame=tmax )
                
                totalEventDuration = behavEventTimeLine.getTotalLength()
                nbEvent = behavEventTimeLine.getNumberOfEvent(minFrame = tmin, maxFrame = tmax )
                
                animal[rfid][behavEventTimeLine.eventName+" TotalLen"] = totalEventDuration
                animal[rfid][behavEventTimeLine.eventName+" Nb"] = nbEvent
                
                print(behavEventTimeLine.eventName, genoA, behavEventTimeLine.idA, totalEventDuration, nbEvent)
            
        print ("writing...")
        
        ''' 
        file    strain    sex    group    day    exp    idA    idB    minTime    maxTime    tot_dist
        '''
        header = ["file","strain","sex","group","day","exp","RFID","minTime","maxTime","tot_dist"]
        for name in header:
            text_file.write( "{}\t".format ( name ) ) 
        
        ''' write event keys '''
        firstAnimalKey = next(iter(animal))
        firstAnimal = animal[firstAnimalKey]
        for k in firstAnimal.keys():
            text_file.write( "{}\t".format( k.replace(" ", "") ) )
        text_file.write("\n")
        
        for kAnimal in animal:
            text_file.write( "{}\t".format( file ) )
            text_file.write( "{}\t".format( "strain" ) )
            text_file.write( "{}\t".format( "sex" ) )
            text_file.write( "{}\t".format( "group" ) )
            text_file.write( "{}\t".format( "day" ) )
            text_file.write( "{}\t".format( "exp" ) )
            text_file.write( "{}\t".format( animal[kAnimal]["animal"].RFID ) )
            text_file.write( "{}\t".format( tmin ) )
            text_file.write( "{}\t".format( tmax ) )

            COMPUTE_TOTAL_DISTANCE = True
            if ( COMPUTE_TOTAL_DISTANCE == True ):
                animal[kAnimal]["animal"].loadDetection()
                text_file.write( "{}\t".format( animal[kAnimal]["animal"].getDistance( tmin=tmin,tmax=tmax) ) )
            else:
                text_file.write( "{}\t".format( "totalDistance" ) )

            for kEvent in firstAnimal.keys():
                text_file.write( "{}\t".format( animal[kAnimal][kEvent] ) )
            text_file.write( "\n" );
            
        print ("done.")
            
                   
            #resOneMouse = [file, behavEventTimeLine.eventName, pool.animalDictionnary[animal].RFID, genoA, pool.animalDictionnary[animal].user1, totalEventDuration, nbEvent]
            #text_file.write( "{}\n".format( resOneMouse ) ) 
        
        '''
        for behavEvent in behaviouralEventOneMouse:
            
            print( "computing individual event: {}".format(behavEvent))    
            behavEventTimeLine = {}
        
            for animal in pool.animalDictionnary.keys():
                
                
                
                behavEventTimeLine[animal] = EventTimeLine( connection, behavEvent, animal, minFrame=tmin, maxFrame=tmax )
                
                event = behavEventTimeLine[animal]
                
                totalEventDuration = event.getTotalLength()
                nbEvent = event.getNumberOfEvent(minFrame = tmin, maxFrame = tmax )

                genoA = None
                try:
                    genoA=pool.animalDictionnary[animal].genotype
                except:
                    pass
                
                
                print(event.eventName, genoA, event.idA, totalEventDuration, nbEvent)
                
                resOneMouse = [file, event.eventName, pool.animalDictionnary[animal].RFID, genoA, pool.animalDictionnary[animal].user1, totalEventDuration, nbEvent]
                text_file.write( "{}\n".format( resOneMouse ) ) 
        '''
                
        if behaviouralEventTwoMice != None:
        
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
                            
                    nbEventsSameGeno = getNumberOfEventWithList(connection, behavEvent, animal, animalSameGeno, minFrame=tmin, maxFrame=tmax)
                    durEventsSameGeno = getDurationOfEventWithList(connection, behavEvent, animal, animalSameGeno, minFrame=tmin, maxFrame=tmax)
                    nbEventsDiffGeno = getNumberOfEventWithList(connection, behavEvent, animal, animalDiffGeno, minFrame=tmin, maxFrame=tmax)
                    durEventsDiffGeno = getDurationOfEventWithList(connection, behavEvent, animal, animalDiffGeno, minFrame=tmin, maxFrame=tmax)
                
                
                            
                    print( behavEvent, pool.animalDictionnary[animal].RFID )
                    
                    resSame = [file, behavEvent, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[animal].genotype, "sameGeno", durEventsSameGeno, nbEventsSameGeno]
                    resDiff = [file, behavEvent, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[animal].genotype, "diffGeno", durEventsDiffGeno, nbEventsDiffGeno]
                    text_file.write( "{}\n{}\n".format( resSame, resDiff ) ) 
                
                     
                
    text_file.write( "\n" )
    text_file.close()
                
                
            
            
            