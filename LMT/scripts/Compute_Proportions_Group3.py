'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from database.Animal import *
import matplotlib.pyplot as plt
from database.Event import *

from database import BuildEventTrain3, BuildEventTrain4, BuildEventFollowZone, BuildEventRear5, BuildEventFloorSniffing,\
    BuildEventSocialApproach, BuildEventSocialEscape, BuildEventApproachContact,\
    BuildEventApproachRear, BuildEventGroup2, BuildEventGroup3, BuildEventGroup4,\
    BuildEventStop, BuildEventWaterPoint

from tkinter.filedialog import askopenfilename
from database.Util import getMinTMaxTAndFileNameInput


if __name__ == '__main__':
    
    print("Code launched.")

    files = askopenfilename( title="Choose a set of file to process", multiple=1 )    
    
    tMin, tMax, text_file = getMinTMaxTAndFileNameInput()
    
    '''
    min_dur = 0*oneHour    
    max_dur = 23*oneHour    
    text_file = open ("test_proportions_group3_shank2_23h.txt", "w")
    '''
    '''
    min_dur = 0*oneHour    
    max_dur = 23*oneHour    
    text_file = open ("test_proportions_group3_shank3_23h.txt", "w")
    '''
    
    '''
    min_dur = 0*oneHour    
    max_dur = 24*3*oneHour    
    text_file = open ("test_proportions_group3_shank3_all.txt", "w")
    '''
    

    for file in files:
        
        print(file)
        connection = sqlite3.connect( file )
        
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        
        ''' separate wild-type and KO animals '''
        animalKODictionary = {}
        animalWTDictionary = {}
        animalMakeGroupDictionary = {}
        group3Dictionary = {}
        
        for idAnimalA in pool.animalDictionnary.keys():
            if ( pool.animalDictionnary[idAnimalA].genotype == "WT" ):
                animalWTDictionary[idAnimalA] = pool.animalDictionnary[idAnimalA]
            
            if ( pool.animalDictionnary[idAnimalA].genotype == "KO" ):
                animalKODictionary[idAnimalA] = pool.animalDictionnary[idAnimalA]
        
            group3Dictionary[idAnimalA] = EventTimeLine( connection, "Group3", idAnimalA, minFrame=tMin, maxFrame=tMax )
        
        ''' calculating how many groups of WKK and of KWW longer than one second were created '''
        Group3WKK = 0
        Group3KWW = 0
        
            
        for idAnimalA in animalWTDictionary:
            for event in group3Dictionary[idAnimalA].eventList:
                
                if event.duration() >= 1:
                    Group3WKK +=1
                    
        for idAnimalA in animalKODictionary:
            
            for event in group3Dictionary[idAnimalA].eventList:
                
                if event.duration() >= 1:
                    Group3KWW +=1
        
                            
        resGroup3 = [ "WKK", Group3WKK, "KWW", Group3KWW ]   
        print(resGroup3) 
        
        
    
        text_file.write( "{}\t{}\t{}\t{}\t{}\n".format( file, "WKK", Group3WKK, "KWW", Group3KWW ) )     
            
        

                
    text_file.write( "\n" )
    text_file.close()
    
    print("job done")