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
    
    #pool = AnimalPool( )
    #pool.loadAnimals( connection )
    #pool.loadDetection( start = tmin, end = tmax )
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax , lightLoad=True )
        
    contactDicoDico = {}
    approachDico = {}
    for animal in range( 1 , pool.getNbAnimals()+1 ):
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if ( animal == idAnimalB ):
                continue
            ''' I take the dictionnary of event of the contact event, that's why I put DicoDico '''
            contactDicoDico[animal, idAnimalB] = EventTimeLineCached( connection, file, "Contact", animal, idAnimalB, minFrame=tmin, maxFrame=tmax ).getDictionnary()
            ''' This one is the dico of event '''
            approachDico[animal, idAnimalB] = EventTimeLineCached( connection, file, "Social approach", animal, idAnimalB, minFrame=tmin, maxFrame=tmax ) #fait une matrice de toutes les approches à deux possibles

    for animal in range( 1 , pool.getNbAnimals()+1 ):
        
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if( animal == idAnimalB ):
                continue
            
            eventName = "Approach contact"        
            print ( eventName )
            
            appContactTimeLine = EventTimeLine( None, eventName , animal , idAnimalB , None , None , loadEvent=False )
                                       
            for eventApp in approachDico[animal, idAnimalB].eventList:
                
                ''' new code: '''
                
                for t in range( eventApp.endFrame - TIME_WINDOW_BEFORE_EVENT, eventApp.endFrame + TIME_WINDOW_BEFORE_EVENT + 1 ):
                    
                    if ( t in contactDicoDico[animal, idAnimalB] ):
                        appContactTimeLine.eventList.append(eventApp)
                        break
                   
                   
                ''' old code(slow)
                
                bug: est ce que ca n aurait pas du etre eventContact.startFrame ? ou eventApp.endFrame-TIME_WINDOW_BEFORE_EVENT, eventApp.endFrame+TIME_WINDOW_BEFORE_EVENT ?
                
                for eventContact in contactDicoDico[animal, idAnimalB].eventList:
                    if (eventApp.overlapInT(eventContact.endFrame-TIME_WINDOW_BEFORE_EVENT, eventContact.endFrame+TIME_WINDOW_BEFORE_EVENT) == True):
                        appContactTimeLine.eventList.append(eventApp)
                '''
            
            appContactTimeLine.endRebuildEventTimeLine(connection)
    
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Approach Contact" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
        
    