'''
Created on 6 sept. 2017

@author: Fab
'''
import sqlite3
from time import *
from database.Chronometer import Chronometer
from database.Animal import *
from database.Detection import *
from database.Measure import *
import matplotlib.pyplot as plt
import numpy as np
from database.Event import *
from database.Measure import *
from database.EventTimeLineCache import EventTimeLineCached

def reBuildEvent( connection, file, tmin=None, tmax=None ): 
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    #pool.loadDetection( start = tmin, end = tmax )
    
    contactDicoDico = {}
    approachDico = {}
    for idAnimalA in range( 1 , pool.getNbAnimals()+1 ):
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if ( idAnimalA == idAnimalB ):
                continue
            ''' I take the dictionnary of event of the contact event, that's why I put DicoDico '''
            contactDicoDico[idAnimalA, idAnimalB] = EventTimeLineCached( connection, file, "Contact", idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax ).getDictionnary()
            ''' This one is the dico of event '''
            approachDico[idAnimalA, idAnimalB] = EventTimeLineCached( connection, file, "Social approach", idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax ) #fait une matrice de toutes les aproches à deux possibles

    for idAnimalA in range( 1 , pool.getNbAnimals()+1 ):
        
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if( idAnimalA == idAnimalB ):
                continue
            
            eventName = "Approach contact"        
            print ( eventName )
            
            appContactTimeLine = EventTimeLine( None, eventName , idAnimalA , idAnimalB , None , None , loadEvent=False )
                                       
            for eventApp in approachDico[idAnimalA, idAnimalB].eventList:
                
                ''' new code: '''
                
                for t in range( eventApp.endFrame - TIME_WINDOW_BEFORE_EVENT, eventApp.endFrame + TIME_WINDOW_BEFORE_EVENT + 1 ):
                    
                    if ( t in contactDicoDico[idAnimalA, idAnimalB] ):
                        appContactTimeLine.eventList.append(eventApp)
                        break
                   
                   
                ''' old code(slow)
                
                bug: est ce que ca n aurait pas du etre eventContact.startFrame ? ou eventApp.endFrame-TIME_WINDOW_BEFORE_EVENT, eventApp.endFrame+TIME_WINDOW_BEFORE_EVENT ?
                
                for eventContact in contactDicoDico[idAnimalA, idAnimalB].eventList:
                    if (eventApp.overlapInT(eventContact.endFrame-TIME_WINDOW_BEFORE_EVENT, eventContact.endFrame+TIME_WINDOW_BEFORE_EVENT) == True):
                        appContactTimeLine.eventList.append(eventApp)
                '''
            
            appContactTimeLine.endRebuildEventTimeLine(connection)
    
    # log process
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Approach Contact" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
        
    