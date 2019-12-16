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

from tkinter.filedialog import askopenfile, askopenfilename
from lmtanalysis.Util import getMinTMaxTAndFileNameInput





if __name__ == '__main__':
    
    print("Code launched.")

    
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    tmin, tmax, text_file = getMinTMaxTAndFileNameInput()

    
    '''
    max_dur = 23*oneHour
    text_file = open ("test_make_break_group4_shank3_23h.txt", "w")
    '''
    
    '''
    max_dur = 3*oneDay
    text_file = open ("test_make_break_group4_shank3_all.txt", "w")
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
        group4Dictionary = {}
        
        for animal in pool.animalDictionnary.keys():
            if ( pool.animalDictionnary[animal].genotype == "WT" ):
                animalWTDictionary[animal] = pool.animalDictionnary[animal]
            
            if ( pool.animalDictionnary[animal].genotype == "KO" ):
                animalKODictionary[animal] = pool.animalDictionnary[animal]
        
            animalMakeGroupDictionary[animal] = EventTimeLine( connection, "Group 4 make", animal, minFrame=tmin, maxFrame=tmax )
            group4Dictionary[animal] = EventTimeLine( connection, "Group4", animal, minFrame=tmin, maxFrame=tmax )
        
        ''' calculating how many groups of were created by WT and by KO '''
        wtMakeGroup4 = 0
        koMakeGroup4 = 0
        
        result = {}
            
        for groupKey in group4Dictionary:
            
            group = group4Dictionary[groupKey]
            
            for event in group.eventList:
                
                frameToCkeck = event.startFrame-1
                
                for animal in pool.animalDictionnary.keys():
                    
                    animal = pool.animalDictionnary[animal]
                    animalType = ""
                    if animal in animalWTDictionary:
                        animalType= "WT"
                    else:
                        animalType = "KO"
                     
                    if ( animalMakeGroupDictionary[animal].hasEvent( frameToCkeck ) ):
                        
                        if ( not ( animalType ) in result ):
                            result[ animalType ] = 0
                            
                        result[ animalType ] +=1
        print("Make group 4")                
        print ( result["WT"] )
        print ( result["KO"] )
                    
        resMakeGroup4 = [ file, "Make Group 4", "WT make group4", result["WT"], "KO make group4", result["KO"] ]    
        
        
        ''' separate wild-type and KO animals '''
        animalKODictionary = {}
        animalWTDictionary = {}
        animalMakeGroupDictionary = {}
        group4Dictionary = {}
        
        for animal in pool.animalDictionnary.keys():
            if ( pool.animalDictionnary[animal].genotype == "WT" ):
                animalWTDictionary[animal] = pool.animalDictionnary[animal]
            
            if ( pool.animalDictionnary[animal].genotype == "KO" ):
                animalKODictionary[animal] = pool.animalDictionnary[animal]                    
        
            animalMakeGroupDictionary[animal] = EventTimeLine( connection, "Group 4 break", animal, minFrame=tmin, maxFrame=tmax )
            group4Dictionary[animal] = EventTimeLine( connection, "Group4", animal, minFrame=tmin, maxFrame=tmax )
        
        ''' calculating how many groups of were created by WT and by KO '''
        wtBreakGroup4 = 0
        koBreakGroup4 = 0
        
        result = {}
            
        for groupKey in group4Dictionary:
            
            group = group4Dictionary[groupKey]
            
            for event in group.eventList:
                
                frameToCkeck = event.startFrame-1
                
                for animal in pool.animalDictionnary.keys():
                    
                    animal = pool.animalDictionnary[animal]
                    animalType = ""
                    if animal in animalWTDictionary:
                        animalType= "WT"
                    else:
                        animalType = "KO"
                     
                    if ( animalMakeGroupDictionary[animal].hasEvent( frameToCkeck ) ):
                        
                        if ( not ( animalType ) in result ):
                            result[ animalType ] = 0
                            
                        result[ animalType ] +=1
        print("Break group 4")                
        print ( result["WT"] )
        print ( result["KO"] )
                    
        resBreakGroup4 = [ file, "Break Group 4", "WT break group4", result["WT"], "KO break group4", result["KO"] ] 
        
        
        
        text_file.write( "{}\t{}\n".format( resMakeGroup4, resBreakGroup4 ) )     
            
        

                
    text_file.write( "\n" )
    text_file.close()