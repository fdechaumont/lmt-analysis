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
import networkx as nx

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Nest4_" )
    '''
    could extends to those:
    deleteEventTimeLineInBase(connection, "Nest3" )
    deleteEventTimeLineInBase(connection, "Group2" )
    deleteEventTimeLineInBase(connection, "Group3" )
    deleteEventTimeLineInBase(connection, "Group4" )
    '''


def reBuildEvent( connection, file, tmin=None, tmax=None , pool = None ):
    '''
    Nest 3
    Nest 4
    Group 2
    Group 3
    Group 4
    ''' 
    print("[NEST 4] : Assume that there is no occlusion")
    
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax , lightLoad=True )
    
    # check if given max is more than available detection 
    '''
    maxT = pool.getMaxDetectionT()
    if ( tmax > maxT ):
        tmax = maxT
    '''
    
    #pool.loadDetection( start = tmin, end = tmax )
    
    if ( len ( pool.getAnimalList() ) != 4 ):
        print( "[NEST4 Cancelled] 4 animals are required to build nest 4.")
        return
    
    contact = {}
    
    
    for animal in range( 1 , 5 ):
        for idAnimalB in range( 1 , 5 ):
            if animal != idAnimalB:    
                contact[animal,idAnimalB] = EventTimeLineCached( connection, file, "Contact", animal, idAnimalB, minFrame=tmin, maxFrame=tmax ).getDictionnary() #fait une matrice de tous les contacts à deux possibles
    
    stopDictionnary = {}
        
    for animal in range( 1 , 5 ):
        stopDictionnary[animal] = EventTimeLineCached( connection, file, "Stop", animal, minFrame=tmin, maxFrame=tmax ).getDictionnary()
    
    
    
    '''
    nest3TimeLine = {}
    
    for animal in range( 1 , 5 ):
        nest3TimeLine = EventTimeLine( None, "Nest3" , animal, loadEvent=False )
    '''
    nest4TimeLine = EventTimeLine( None, "Nest4_" , loadEvent=False )
    
    pool.loadAnonymousDetection()
    
    '''
    group2TimeLine = {}
    for animal in range( 1 , 5 ):
        for idAnimalB in range( 1 , 5 ):
            if ( animal != idAnimalB ):
                group2TimeLine[animal,idAnimalB] = EventTimeLine( None, "Group2" , animal , idAnimalB , loadEvent=False )

    group3TimeLine = {}
    for animal in range( 1 , 5 ):
        for idAnimalB in range( 1 , 5 ):
            if( animal != idAnimalB ):
                for idAnimalC in range( 1 , 5 ):
                    if ( animal != idAnimalC and idAnimalB != idAnimalC ):
                        group3TimeLine[animal,idAnimalB] = EventTimeLine( None, "Group3" , animal , idAnimalB , idAnimalC, loadEvent=False )
    
    group4TimeLine = EventTimeLine( None, "Group4" , loadEvent=False )
    '''
        
    
    animalList = pool.getAnimalList() 
    
    result = {}
    
    for t in range( tmin, tmax+1 ):
        
        
        isNest = False
        
        nbAnimalAtT = 0
        animalDetectedList = []
        
        
        anonymousDetectionList = pool.getAnonymousDetection( t )
        
        for animal in animalList:
            if t in animal.detectionDictionnary:                
                animalDetectedList.append( animal )
        
        #print( str(t) + " : " + str( nbAnimalAtT ) )
                    
    
        #print("TEST")
        graph = nx.Graph()
        # add nodes
        
        for animal in animalDetectedList:
            graph.add_node( animal )
            nbAnimalAtT+=1
            
        for animalA in animalDetectedList:
            for animalB in animalDetectedList:
                if animalA != animalB:
                    # add an edge
                    if t in contact[animalA.baseId,animalB.baseId]:
                        graph.add_edge( animalA, animalB )
        
        # check with anonymous detection. Check contact
        if anonymousDetectionList!= None:
            
            nbAnimalAtT+=len(anonymousDetectionList)
            
            # manage anonymous
            #print( t , "manage anonymous")
            '''
            # load all masks
            for animal in animalDetectedList:
                animal.loadMask( t )
            '''
            
            for detectionA in anonymousDetectionList: # anonymous with anonymous
                for detectionB in anonymousDetectionList: # anonymous with anonymous
                    if detectionA != detectionB:
                        distance = detectionA.getDistanceTo( detectionB )
                        if distance != None:
                            if distance < DISTANCE_CONTACT_MASS_CENTER:
                                graph.add_edge( detectionA, detectionB )
                                #print("Adding edge with mask (det anonymous to det anonymous)")
                    
            for detection in anonymousDetectionList:
                for animal in animalDetectedList:
                    distance = detection.getDistanceTo(animal.getDetectionAt( t ) )
                    if distance != None:
                        if distance < DISTANCE_CONTACT_MASS_CENTER:
                            #if detection.getMask().isInContactWithMask( animal.getDetectionAt ( t ).getMask() ):
                            graph.add_edge( animal, detection )
                            #print("Adding edge with mask")
        
        # list of CC from the biggest to the smallest
        #listCC = sorted(nx.connected_components( graph ), key=len, reverse=True)
        
        if nbAnimalAtT == 0:            
            isNest = True
        
        # list of CC from the biggest to the smallest
        listCC = sorted(nx.connected_components( graph ), key=len, reverse=True)
        
        #largestCC = len ( max(nx.connected_components( graph ), key=len) )

        '''
        for animal in animalList:
            if t in animal.detectionDictionnary:
                nbAnimalAtT+=1
                animalDetectedList.append( animal )
        
        #print( str(t) + " : " + str( nbAnimalAtT ) )
        
        if nbAnimalAtT == 0:            
            isNest = True
            
        if not isNest:
            #print("TEST")
            graph = nx.Graph();
            # add nodes
            for animal in animalDetectedList:
                graph.add_node( animal )
            for animalA in animalDetectedList:
                for animalB in animalDetectedList:
                    if animalA != animalB:
                        # add an edge
                        if t in contact[animalA.baseId,animalB.baseId]:
                            graph.add_edge( animalA, animalB )
            
            
            
            
            # check connected components. If the biggest group gets all animal, we got a nest4
            largestCC = len ( max(nx.connected_components( graph ), key=len) )
            
            #print( str( t ) + " : " + str ( len( largestCC ) ) )
            
            #print( str( t ) + " : " + str ( largestCC ) + " / " + str( nbAnimalAtT ) )
        '''    
        if len ( listCC ) == 0 :
            continue
        
        #print( t , len ( listCC[0] ) , nbAnimalAtT )
        
        if len ( listCC[0] ) == nbAnimalAtT:
        
        #if largestCC == nbAnimalAtT :
            
            # check if animals in the nest are stopped.
            allStoppedInBiggestGroup = True
            for animal in animalDetectedList:
                if isinstance( animal , Animal ):
                    if not ( t in stopDictionnary[animal.baseId] ):
                        allStoppedInBiggestGroup = False
                        break

            if allStoppedInBiggestGroup:
                isNest= True                     
                     
        if isNest == True:
            #print( "ADD PUNCTUAL")
            result[t] = True;
            
            
            
    nest4TimeLine.reBuildWithDictionnary( result )
    # remove very small events
    nest4TimeLine.removeEventsBelowLength( 2 )
    # merge flashing events
    nest4TimeLine.mergeCloseEvents( 3 )
    nest4TimeLine.endRebuildEventTimeLine(connection)
        
    
    '''
    for animal in range( 1 , 5 ):
        
        for idAnimalB in range( 1 , 5 ):
            if( animal == idAnimalB ):
                continue
            
            for idAnimalC in range( 1 , 5 ):
                if( animal == idAnimalC ):
                    continue
                if( idAnimalB == idAnimalC ):
                    continue
                
                for idAnimalD in range( 1 , 5 ):
                    if( animal == idAnimalD ):
                        continue
                    if( idAnimalB == idAnimalD ):
                        continue
                    if( idAnimalC == idAnimalD ):
                        continue
                
                    eventName = "Group4"        
                    print ( eventName )
                    
                    groupTimeLine = EventTimeLine( None, eventName , animal , idAnimalB , idAnimalC , idAnimalD , loadEvent=False )
                    
                    result={}
                    
                    dicA = contact[ animal ].getDictionnary()
                    dicB = contact[ idAnimalB ].getDictionnary()
                    dicC = contact[ idAnimalC ].getDictionnary()
                    dicD = contact[ idAnimalD ].getDictionnary()
                    
                    dicGroup2A = group2[ animal ].getDictionnary()
                    dicGroup2B = group2[ idAnimalB ].getDictionnary()
                    dicGroup2C = group2[ idAnimalC ].getDictionnary()
                    dicGroup2D = group2[ idAnimalD ].getDictionnary()
                    
                    for t in dicA.keys():
                        if ( t in dicB and t in dicC and t in dicD ):
                            if ( t in dicGroup2A or t in dicGroup2B or t in dicGroup2C or t in dicGroup2D):
                                continue
                            else:
                                result[t]=True
                    
    groupTimeLine.reBuildWithDictionnary( result )
    
    groupTimeLine.endRebuildEventTimeLine(connection)
          
    '''                
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Nest4" , tmin=tmin, tmax=tmax )
          
    
    print( "Rebuild event finished." )
        
    