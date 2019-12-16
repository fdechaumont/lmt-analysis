'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *

from lmtanalysis import BuildEventTrain3, BuildEventTrain4, BuildEventFollowZone, BuildEventRear5, BuildEventFloorSniffing,\
    BuildEventSocialApproach, BuildEventSocialEscape, BuildEventApproachContact,\
    BuildEventApproachRear, BuildEventGroup2, BuildEventGroup3, BuildEventGroup4,\
    BuildEventStop, BuildEventWaterPoint

from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import getMinTMaxTAndFileNameInput


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
        
        for animal in pool.animalDictionnary.keys():
            if ( pool.animalDictionnary[animal].genotype == "WT" ):
                animalWTDictionary[animal] = pool.animalDictionnary[animal]
            
            if ( pool.animalDictionnary[animal].genotype == "KO" ):
                animalKODictionary[animal] = pool.animalDictionnary[animal]
        
            group3Dictionary[animal] = EventTimeLine( connection, "Group3", animal, minFrame=tMin, maxFrame=tMax )
        
        ''' calculating how many groups of WKK and of KWW longer than one second were created '''
        Group3WKK = 0
        Group3KWW = 0
        
            
        for animal in animalWTDictionary:
            for event in group3Dictionary[animal].eventList:
                
                if event.duration() >= 1:
                    Group3WKK +=1
                    
        for animal in animalKODictionary:
            
            for event in group3Dictionary[animal].eventList:
                
                if event.duration() >= 1:
                    Group3KWW +=1
        
                            
        resGroup3 = [ "WKK", Group3WKK, "KWW", Group3KWW ]   
        print(resGroup3) 
        
        
    
        text_file.write( "{}\t{}\t{}\t{}\t{}\n".format( file, "WKK", Group3WKK, "KWW", Group3KWW ) )     
            
        

                
    text_file.write( "\n" )
    text_file.close()
    
    print("job done")