'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from database.Event import *

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
    
    
    '''
    min_dur = 0*oneHour
    max_dur = 23*oneHour
    '''
    
    
    '''
    text_file = open ("test_link_make_break_group4_shank2_"+setName+".txt", "w")
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
        animalBreakGroupDictionary = {}
        
        group4Dictionary = EventTimeLine( connection, "Group4", None, minFrame=tmin, maxFrame=tmax )
        
        for animal in pool.animalDictionnary.keys():
            if ( pool.animalDictionnary[animal].genotype == "WT" ):
                animalWTDictionary[animal] = pool.animalDictionnary[animal]
            
            if ( pool.animalDictionnary[animal].genotype == "KO" ):
                animalKODictionary[animal] = pool.animalDictionnary[animal]
        
            animalMakeGroupDictionary[animal] = EventTimeLine( connection, "Group 4 make", animal, minFrame=tmin, maxFrame=tmax )
            animalBreakGroupDictionary[animal] = EventTimeLine( connection, "Group 4 break", animal, minFrame=tmin, maxFrame=tmax )
            
        
        ''' calculating how many groups of were created by WT or by KO and broken by WT or KO'''
        wtMakeWtBreakGroup4 = EventTimeLine( None, "WT make & WT break Group4" , loadEvent=False )
        koMakeWtBreakGroup4 = EventTimeLine( None, "KO make & WT break Group4" , loadEvent=False )
        wtMakeKoBreakGroup4 = EventTimeLine( None, "WT make & KO break Group4" , loadEvent=False )
        koMakeKoBreakGroup4 = EventTimeLine( None, "KO make & KO break Group4" , loadEvent=False )
        
        print ( "animal WT: " , animalWTDictionary )
        print ( "animal KO: " , animalKODictionary )
        
        for event in group4Dictionary.eventList:
            
            frameToCkeckMake = event.startFrame-1
            frameToCkeckBreak = event.endFrame+1    #enlever le +1 pour les bases "processed"
        
            inner = "" 
            for animal in pool.animalDictionnary.keys():
                if ( animalMakeGroupDictionary[animal].hasEvent( frameToCkeckMake ) ):
                    #print ( "ok", animal )
                    inner = animal

            outer = "" 
            for animal in pool.animalDictionnary.keys():
                if ( animalBreakGroupDictionary[animal].hasEvent( frameToCkeckBreak) ):
                    print ( "outer:", animal )
                    outer = animal
                    
            print ( "in:", inner, " out:", outer)
                
            for animal in animalWTDictionary.keys():
                for idAnimalB in animalWTDictionary.keys(): 
                    if ( animalMakeGroupDictionary[animal].hasEvent( frameToCkeckMake ) and animalBreakGroupDictionary[idAnimalB].hasEvent( frameToCkeckBreak) ):
                        print("Add 1")
                        wtMakeWtBreakGroup4.addEvent( event)
                        
            for animal in animalWTDictionary.keys():
                for idAnimalB in animalKODictionary.keys(): 
                    if ( animalMakeGroupDictionary[animal].hasEvent( frameToCkeckMake ) and animalBreakGroupDictionary[idAnimalB].hasEvent( frameToCkeckBreak) ):
                        print("Add 2")
                        wtMakeKoBreakGroup4.addEvent( event)
                        
            for animal in animalKODictionary.keys():
                for idAnimalB in animalWTDictionary.keys(): 
                    if ( animalMakeGroupDictionary[animal].hasEvent( frameToCkeckMake ) and animalBreakGroupDictionary[idAnimalB].hasEvent( frameToCkeckBreak) ):
                        print("Add 3")
                        koMakeWtBreakGroup4.addEvent( event)
                        
            for animal in animalKODictionary.keys():
                for idAnimalB in animalKODictionary.keys(): 
                    if ( animalMakeGroupDictionary[animal].hasEvent( frameToCkeckMake ) and animalBreakGroupDictionary[idAnimalB].hasEvent( frameToCkeckBreak) ):
                        print("Add 4")
                        koMakeKoBreakGroup4.addEvent( event)
                        
        print("Group 4")                
        print ( ["WT", "WT"], wtMakeWtBreakGroup4.getNbEvent(), wtMakeWtBreakGroup4.getMeanEventLength() )
        print ( ["KO", "KO"], koMakeKoBreakGroup4.getNbEvent(), koMakeKoBreakGroup4.getMeanEventLength() )
        print ( ["WT", "KO"], wtMakeKoBreakGroup4.getNbEvent(), wtMakeKoBreakGroup4.getMeanEventLength() )
        print ( ["KO", "WT"], koMakeWtBreakGroup4.getNbEvent(), koMakeWtBreakGroup4.getMeanEventLength() )   
       
        text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( file, "WT make & WT break Group 4", wtMakeWtBreakGroup4.getNbEvent(), wtMakeWtBreakGroup4.getMeanEventLength() , "WT make & KO break group4", wtMakeKoBreakGroup4.getNbEvent(), wtMakeKoBreakGroup4.getMeanEventLength(), "KO make & WT break group4", koMakeWtBreakGroup4.getNbEvent(), koMakeWtBreakGroup4.getMeanEventLength(), "KO make & KO break group4", koMakeKoBreakGroup4.getNbEvent(), koMakeKoBreakGroup4.getMeanEventLength() ) )     
   
              
    text_file.write( "\n" )
    text_file.close()