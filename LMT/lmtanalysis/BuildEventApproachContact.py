'''
Created on 6 sept. 2017

@author: Fab
'''
import sqlite3
from time import *
from lmtanalysis.Chronometer import Chronometer
from lmtanalysis.Animal import *
from lmtanalysis.Detection import *
from lmtanalysis.Measure import *
import matplotlib.pyplot as plt
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached


def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Approach contact" )

def reBuildEvent( connection, file, tmin=None, tmax=None , pool = None ): 
    
    '''
    This event represents the approaches that is just before a contact (longer than 3 frames); if the speeds of the two animals
    involved in the contact are not different enough, the animal approaching cannot be defined and therefore the event is not computed 
    for this contact.
    This event is a reduction of distance between two animals, one going more quickly than the other, until they get in contact.
    This event ends at the frame just before the contact and lasts the whole time of approach.
    '''
    
    #pool = AnimalPool( )
    #pool.loadAnimals( connection )
    #pool.loadDetection( start = tmin, end = tmax )
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax , lightLoad=True )
    
    eventName = "Approach contact"        
    print ( eventName )
    print('Computing ', eventName)
            
    #upload the timelines of interest
    contactDico = {}
    approachDico = {}
    for animal in range( 1 , pool.getNbAnimals()+1 ):
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if ( animal == idAnimalB ):
                continue
            #charge the contact timelines as a dictionary of timelines
            contactDico[animal, idAnimalB] = EventTimeLineCached( connection, file, "Contact", animal, idAnimalB, minFrame=tmin, maxFrame=tmax )
            #charge the approach timelines as a dictionary of timelines
            approachDico[animal, idAnimalB] = EventTimeLineCached( connection, file, "Approach", animal, idAnimalB, minFrame=tmin, maxFrame=tmax ) #fait une matrice de toutes les approches à deux possibles
    
    #initiate the timeline of approach before a contact
    appContactTimeLineDico = {}
    appContactTimeLineDicoDico = {}
    for animal in range( 1 , pool.getNbAnimals()+1 ):
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if ( animal == idAnimalB ):
                continue
            
            appContactTimeLineDico[ animal, idAnimalB ] = EventTimeLine( None, eventName , animal , idAnimalB , None , None , loadEvent=False )
            appContactTimeLineDicoDico[ animal, idAnimalB ] = {}
    
    #upload the dictionary for each approach timeline
    approachDicoDico = {}
    for animal in range( 1 , pool.getNbAnimals()+1 ):
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if( animal == idAnimalB ):
                continue
            
            #upload the dictionary for each approach timeline:
            approachDicoDico[animal, idAnimalB] = approachDico[animal, idAnimalB].getDictionary()
            
    #check who approached who before the contact
    for animal in range( 1 , pool.getNbAnimals()+1 ):
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if( animal == idAnimalB ):
                continue
            
            #clean the contact timeline to keep only events longer than 3 frames
            contactDico[animal, idAnimalB].mergeCloseEvents(numberOfFrameBetweenEvent=1)
            contactDico[animal, idAnimalB].removeEventsBelowLength(maxLen=3)
            
            
            for contactEvent in contactDico[animal, idAnimalB].eventList:
                frameBeforeContact = contactEvent.startFrame - 1
                #if the frame before the contact is within the approach timeline of A to B, then add the corresponding approach event to the approach contact timeline
                if frameBeforeContact in approachDicoDico[animal, idAnimalB]:
                    #print('A approaches B')
                    approachEvent = approachDico[animal, idAnimalB].getEventAt( frameBeforeContact )
                    for t in range (approachEvent.startFrame, frameBeforeContact + 1):
                        appContactTimeLineDicoDico[animal, idAnimalB][t] = True
                
                #if the frame before the contact is within the approach timeline of B to A, then add the corresponding approach event to the approach contact timeline
                elif frameBeforeContact in approachDicoDico[idAnimalB, animal]:
                    #print('B approaches A')
                    approachEvent = approachDico[idAnimalB, animal].getEventAt( frameBeforeContact )
                    for t in range (approachEvent.startFrame, frameBeforeContact + 1):
                        appContactTimeLineDicoDico[idAnimalB, animal][t] = True
                
                #if the frame before the contact is not within any approach timeline, then go to the next contact event
                else:
                    #print('Not possible to decide who is approaching who.')
                    continue
                
 
    for animal in range( 1 , pool.getNbAnimals()+1 ):
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if( animal == idAnimalB ):
                continue
            appContactTimeLineDico[animal, idAnimalB].reBuildWithDictionnary( appContactTimeLineDicoDico[animal, idAnimalB] )
            appContactTimeLineDico[animal, idAnimalB].endRebuildEventTimeLine( connection )
    
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Approach Contact" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
        
    