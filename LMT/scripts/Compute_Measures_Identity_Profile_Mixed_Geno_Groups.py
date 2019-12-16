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
from lmtanalysis.EventTimeLineCache import EventTimeLineCached




if __name__ == '__main__':
    
    print("Code launched.")
    '''
    compute behavioural traits for each individual within a group of mice having the same genotype/strain
    computation of individual and social traits.
    '''
   
        
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    tmin, tmax, text_file = getMinTMaxTAndFileNameInput()

        
    
    '''
    #behaviouralEventOneMouse = ["Approach contact", "Approach rear", "Break contact", "Contact", "FollowZone Isolated", "Group2", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Social escape", "Train2"]
    behaviouralEventOneMouse = ["Contact", "Group2", "Group3", "Group 3 break", "Group 3 make", "Group4", "Group 4 break", "Group 4 make", "Huddling", "Move isolated", "Move in contact", "Nest3", "Rearing", "Rear isolated", "Rear in contact", "Stop isolated", "WallJump", "Water Zone", "Approach contact", "Approach rear", "Break contact", "FollowZone Isolated", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Get away", "Train2"]
    #behaviouralEventTwoMice = None
    behaviouralEventTwoMice = ["Approach contact", "Approach rear", "Break contact", "Contact", "FollowZone Isolated", "Group2", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Get away", "Train2"] 
    '''
    behaviouralEventOneMouse = ["Group3", "Water Zone"]
    behaviouralEventTwoMice = ["Contact", "Oral-genital Contact"] 
    
    
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
        
        for animal in pool.animalDictionnary.keys():
            
            print ( pool.animalDictionnary[animal].RFID )
            #total distance traveled
            totalDistance = pool.animalDictionnary[animal].getDistance(tmin = min_dur, tmax = max_dur)
            resTotalDistance = [file, pool.animalDictionnary[animal].RFID, min_dur, max_dur, totalDistance]
            text_file.write( "{}\t{}\t{}\t{}\t{}\n".format( file, pool.animalDictionnary[animal].RFID, min_dur, max_dur, totalDistance ) ) 
        
        '''

        nightEventTimeLine = EventTimeLineCached( connection, file, "night", minFrame=tmin, maxFrame=tmax )
        n = 1
        
        for eventNight in nightEventTimeLine.getEventList():
            
            startNight = eventNight.startFrame
            endNight = eventNight.endFrame
            print("Night: ", n)

    
            
            for animal in pool.animalDictionnary.keys():
            
                for behavEvent in behaviouralEventOneMouse:
                    
                    print( "computing individual event: {}".format(behavEvent))    
                    
                    behavEventTimeLine = EventTimeLine( connection, behavEvent, animal, minFrame=startNight, maxFrame=endNight )
                    
                    totalEventDuration = behavEventTimeLine.getTotalLength()
                    nbEvent = behavEventTimeLine.getNumberOfEvent(minFrame = startNight, maxFrame = endNight )
                
                    print(behavEventTimeLine.eventName, behavEventTimeLine.idA, totalEventDuration, nbEvent)
                    text_file.write( "night{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( n, file, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[animal].genotype, startNight, endNight, behavEvent, totalEventDuration, nbEvent ) )
            
            print ("writing one mouse events...")
            
            if ( behaviouralEventTwoMice != None ):
                
                for behavEvent in behaviouralEventTwoMice:
                    
                    print( "computing {} event".format(behavEvent))
                    
                    for animal in pool.animalDictionnary.keys():
                        for idAnimalB in pool.animalDictionnary.keys():
                            if ( animal == idAnimalB ):
                                continue
                        
                            behavEventTimeLine = EventTimeLine( connection, behavEvent, animal, idAnimalB, minFrame=startNight, maxFrame=endNight )

                            totalEventDuration = behavEventTimeLine.getTotalLength()
                            nbEvent = behavEventTimeLine.getNumberOfEvent(minFrame = startNight, maxFrame = endNight)
                    
                                
                            print( behavEvent, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[idAnimalB].RFID )
                        
                            text_file.write( "night{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( n, file, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[animal].genotype, pool.animalDictionnary[idAnimalB].RFID, pool.animalDictionnary[idAnimalB].genotype, startNight, endNight, behavEvent, totalEventDuration, nbEvent ) ) 
            
            n+=1
            
    text_file.write( "\n" )
    text_file.close()
    
    print('Job done')
                
                
            
            
            