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

    tmin, tmax, text_file = getMinTMaxTAndFileNameInput()

    '''
    max_dur = 23*oneHour
    text_file = open ("test_make_break_group3_shank3_23h.txt", "w")
    '''

    '''
    max_dur = 3*oneDay
    text_file = open ("test_make_break_group3_shank3_all.txt", "w")
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
        
            animalMakeGroupDictionary[animal] = EventTimeLine( connection, "Group 3 make", animal, minFrame=tmin, maxFrame=tmax )
            group3Dictionary[animal] = EventTimeLine( connection, "Group3", animal, minFrame=tmin, maxFrame=tmax )
        
        ''' calculating how many groups of WKK and of KWW were created by WT and by KO '''
        wtMakeGroup3WKK = 0
        koMakeGroup3WKK = 0
        wtMakeGroup3KWW = 0
        koMakeGroup3KWW = 0
        
        result = {}
            
        for groupKey in group3Dictionary:
            
            group = group3Dictionary[groupKey]
            
            groupType=""
            if groupKey in animalWTDictionary:
                groupType= "WKK"
            else:
                groupType = "KWW"
                
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
                        
                        if ( not ( animalType , groupType ) in result ):
                            result[ animalType, groupType ] = 0
                            
                        result[ animalType, groupType ] +=1
        print("Make group 3")                
        print ( result["WT", "WKK"] )
        print ( result["WT", "KWW"] )
        print ( result["KO", "WKK"] )
        print ( result["KO", "KWW"] )
                    
        resMakeGroup3 = [ file, "Make Group 3", "WT make WKK", result["WT", "WKK"], "KO male WKK", result["KO", "WKK"], "WT make KWW", result["WT", "KWW"], "KO make KWW", result["KO", "KWW"] ]    
        
        
        ''' separate wild-type and KO animals '''
        animalKODictionary = {}
        animalWTDictionary = {}
        animalBreakGroupDictionary = {}
        group3Dictionary = {}
        
        for animal in pool.animalDictionnary.keys():
            if ( pool.animalDictionnary[animal].genotype == "WT" ):
                animalWTDictionary[animal] = pool.animalDictionnary[animal]
            
            if ( pool.animalDictionnary[animal].genotype == "KO" ):
                animalKODictionary[animal] = pool.animalDictionnary[animal]
        
            animalBreakGroupDictionary[animal] = EventTimeLine( connection, "Group 3 break", animal, minFrame=tmin, maxFrame=tmax )
            group3Dictionary[animal] = EventTimeLine( connection, "Group3", animal, minFrame=tmin, maxFrame=tmax )
        
        ''' calculating how many groups of WKK and of KWW were broken by WT and by KO '''
        wtBreakGroup3WKK = 0
        koBreakGroup3WKK = 0
        wtBreakGroup3KWW = 0
        koBreakGroup3KWW = 0
        
        result = {}
            
        for groupKey in group3Dictionary:
            
            group = group3Dictionary[groupKey]
            
            groupType=""
            if groupKey in animalWTDictionary:
                groupType= "WKK"
            else:
                groupType = "KWW"
                
            for event in group.eventList:
                
                frameToCkeck = event.endFrame+1
                
                for animal in pool.animalDictionnary.keys():
                    
                    animal = pool.animalDictionnary[animal]
                    animalType = ""
                    if animal in animalWTDictionary:
                        animalType= "WT"
                    else:
                        animalType = "KO"
                     
                    if ( animalBreakGroupDictionary[animal].hasEvent( frameToCkeck ) ):
                        
                        if ( not ( animalType , groupType ) in result ):
                            result[ animalType, groupType ] = 0
                            
                        result[ animalType, groupType ] +=1
        print("Break group 3")                
        print ( result["WT", "WKK"] )
        print ( result["WT", "KWW"] )
        print ( result["KO", "WKK"] )
        print ( result["KO", "KWW"] )
                    
        resBreakGroup3 = [ file, "Break Group 3", "WT break WKK", result["WT", "WKK"], "KO break WKK", result["KO", "WKK"], "WT break KWW", result["WT", "KWW"], "KO break KWW", result["KO", "KWW"] ] 
        
        
        
        
        text_file.write( "{}\t{}\n".format( resMakeGroup3, resBreakGroup3 ) )     
            
        

                
    text_file.write( "\n" )
    text_file.close()