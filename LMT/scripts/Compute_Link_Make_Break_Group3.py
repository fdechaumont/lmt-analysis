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
    text_file = open ("test_link_make_break_group3_shank2_"+setName+".txt", "w")
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
        group3Dictionary = {}
        
        
        for animal in pool.animalDictionnary.keys():
            if ( pool.animalDictionnary[animal].genotype == "WT" ):
                animalWTDictionary[animal] = pool.animalDictionnary[animal]
            
            if ( pool.animalDictionnary[animal].genotype == "KO" ):
                animalKODictionary[animal] = pool.animalDictionnary[animal]
        
            animalMakeGroupDictionary[animal] = EventTimeLine( connection, "Group 3 make", animal, minFrame=tmin, maxFrame=tmax )
            animalBreakGroupDictionary[animal] = EventTimeLine( connection, "Group 3 break", animal, minFrame=tmin, maxFrame=tmax )
            group3Dictionary[animal] = EventTimeLine( connection, "Group3", animal, minFrame=tmin, maxFrame=tmax )
        
        
        ''' calculating how many groups of 3 WKK were created by WT or by KO and broken by WT or KO'''
        wtMakeWtBreakGroup3WKK = EventTimeLine( None, "WT make & WT break Group3" , loadEvent=False )
        koMakeWtBreakGroup3WKK = EventTimeLine( None, "KO make & WT break Group3" , loadEvent=False )
        wtMakeKoBreakGroup3WKK = EventTimeLine( None, "WT make & KO break Group3" , loadEvent=False )
        koMakeKoBreakGroup3WKK = EventTimeLine( None, "KO make & KO break Group3" , loadEvent=False )
        
        for animal in animalWTDictionary.keys():
            for event in group3Dictionary[animal].eventList:
                
                frameToCkeckMake = event.startFrame-1
                frameToCkeckBreak = event.endFrame+1
                
                for idAnimalB in animalWTDictionary.keys():
                    for idAnimalC in animalWTDictionary.keys(): 
                        if ( animalMakeGroupDictionary[idAnimalB].hasEvent( frameToCkeckMake ) and animalBreakGroupDictionary[idAnimalC].hasEvent( frameToCkeckBreak) ):
                            wtMakeWtBreakGroup3WKK.addEvent( event)
                            
                    for idAnimalC in animalKODictionary.keys(): 
                        if ( animalMakeGroupDictionary[idAnimalB].hasEvent( frameToCkeckMake ) and animalBreakGroupDictionary[idAnimalC].hasEvent( frameToCkeckBreak) ):
                            wtMakeKoBreakGroup3WKK.addEvent( event)
                            
                for idAnimalB in animalKODictionary.keys():
                    for idAnimalC in animalWTDictionary.keys(): 
                        if ( animalMakeGroupDictionary[idAnimalB].hasEvent( frameToCkeckMake ) and animalBreakGroupDictionary[idAnimalC].hasEvent( frameToCkeckBreak) ):
                            koMakeWtBreakGroup3WKK.addEvent( event)
                            
                    for idAnimalC in animalKODictionary.keys(): 
                        if ( animalMakeGroupDictionary[idAnimalB].hasEvent( frameToCkeckMake ) and animalBreakGroupDictionary[idAnimalC].hasEvent( frameToCkeckBreak) ):
                            koMakeKoBreakGroup3WKK.addEvent( event)
                        
        print("Group 3 WKK")                
        print ( ["WT", "WT"], wtMakeWtBreakGroup3WKK.getNbEvent(), wtMakeWtBreakGroup3WKK.getMeanEventLength() )
        print ( ["KO", "KO"], koMakeKoBreakGroup3WKK.getNbEvent(), koMakeKoBreakGroup3WKK.getMeanEventLength() )
        print ( ["WT", "KO"], wtMakeKoBreakGroup3WKK.getNbEvent(), wtMakeKoBreakGroup3WKK.getMeanEventLength() )
        print ( ["KO", "WT"], koMakeWtBreakGroup3WKK.getNbEvent(), koMakeWtBreakGroup3WKK.getMeanEventLength() )   
       
        text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( file, "Group 3 WKK", "WT make & WT break Group3", wtMakeWtBreakGroup3WKK.getNbEvent(), wtMakeWtBreakGroup3WKK.getMeanEventLength() , "WT make & KO break group3", wtMakeKoBreakGroup3WKK.getNbEvent(), wtMakeKoBreakGroup3WKK.getMeanEventLength(), "KO make & WT break group3", koMakeWtBreakGroup3WKK.getNbEvent(), koMakeWtBreakGroup3WKK.getMeanEventLength(), "KO make & KO break group3", koMakeKoBreakGroup3WKK.getNbEvent(), koMakeKoBreakGroup3WKK.getMeanEventLength() ) )     
        
        
        ''' calculating how many groups of 3 WKK were created by WT or by KO and broken by WT or KO'''
        wtMakeWtBreakGroup3WWK = EventTimeLine( None, "WT make & WT break Group3" , loadEvent=False )
        koMakeWtBreakGroup3WWK = EventTimeLine( None, "KO make & WT break Group3" , loadEvent=False )
        wtMakeKoBreakGroup3WWK = EventTimeLine( None, "WT make & KO break Group3" , loadEvent=False )
        koMakeKoBreakGroup3WWK = EventTimeLine( None, "KO make & KO break Group3" , loadEvent=False )
        
        for animal in animalKODictionary.keys():
            for event in group3Dictionary[animal].eventList:
                
                frameToCkeckMake = event.startFrame-1
                frameToCkeckBreak = event.endFrame+1
                
                for idAnimalB in animalWTDictionary.keys():
                    for idAnimalC in animalWTDictionary.keys(): 
                        if ( animalMakeGroupDictionary[idAnimalB].hasEvent( frameToCkeckMake ) and animalBreakGroupDictionary[idAnimalC].hasEvent( frameToCkeckBreak) ):
                            wtMakeWtBreakGroup3WWK.addEvent( event)
                            
                    for idAnimalC in animalKODictionary.keys(): 
                        if ( animalMakeGroupDictionary[idAnimalB].hasEvent( frameToCkeckMake ) and animalBreakGroupDictionary[idAnimalC].hasEvent( frameToCkeckBreak) ):
                            wtMakeKoBreakGroup3WWK.addEvent( event)
                            
                for idAnimalB in animalKODictionary.keys():
                    for idAnimalC in animalWTDictionary.keys(): 
                        if ( animalMakeGroupDictionary[idAnimalB].hasEvent( frameToCkeckMake ) and animalBreakGroupDictionary[idAnimalC].hasEvent( frameToCkeckBreak) ):
                            koMakeWtBreakGroup3WWK.addEvent( event)
                            
                    for idAnimalC in animalKODictionary.keys(): 
                        if ( animalMakeGroupDictionary[idAnimalB].hasEvent( frameToCkeckMake ) and animalBreakGroupDictionary[idAnimalC].hasEvent( frameToCkeckBreak) ):
                            koMakeKoBreakGroup3WWK.addEvent( event)
                        
        print("Group 3 WWK")                
        print ( ["WT", "WT"], wtMakeWtBreakGroup3WWK.getNbEvent(), wtMakeWtBreakGroup3WWK.getMeanEventLength() )
        print ( ["KO", "KO"], koMakeKoBreakGroup3WWK.getNbEvent(), koMakeKoBreakGroup3WWK.getMeanEventLength() )
        print ( ["WT", "KO"], wtMakeKoBreakGroup3WWK.getNbEvent(), wtMakeKoBreakGroup3WWK.getMeanEventLength() )
        print ( ["KO", "WT"], koMakeWtBreakGroup3WWK.getNbEvent(), koMakeWtBreakGroup3WWK.getMeanEventLength() )   
       
        text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( file, "Group 3 WWK", "WT make & WT break Group3", wtMakeWtBreakGroup3WWK.getNbEvent(), wtMakeWtBreakGroup3WWK.getMeanEventLength() , "WT make & KO break group3", wtMakeKoBreakGroup3WWK.getNbEvent(), wtMakeKoBreakGroup3WWK.getMeanEventLength(), "KO make & WT break group3", koMakeWtBreakGroup3WWK.getNbEvent(), koMakeWtBreakGroup3WWK.getMeanEventLength(), "KO make & KO break group3", koMakeKoBreakGroup3WWK.getNbEvent(), koMakeKoBreakGroup3WWK.getMeanEventLength() ) )     
   
              
    text_file.write( "\n" )
    text_file.close()