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
    deleteEventTimeLineInBase(connection, "Nest3_" )


def reBuildEvent( connection, file, tmin=None, tmax=None , pool = None ):
    '''
    Nest 3
    ''' 
    print("[NEST 3] : Assume that there is no occlusion, does not work with anonymous animals")
    
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax , lightLoad=True )
        
    if ( len ( pool.getAnimalList() ) != 4 ):
        print( "[NEST3 Cancelled] 4 animals are required to build nest3.")
        return
    
    contact = {}
        
    for idAnimalA in range( 1 , 5 ):
        for idAnimalB in range( 1 , 5 ):
            if idAnimalA != idAnimalB:    
                contact[idAnimalA, idAnimalB] = EventTimeLineCached( connection, file, "Contact", idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax ).getDictionnary()

    stopDictionnary = {}
        
    for idAnimalA in range( 1 , 5 ):
        stopDictionnary[idAnimalA] = EventTimeLineCached( 
            connection, file, "Stop", idA=idAnimalA, minFrame=tmin, maxFrame=tmax ).getDictionnary()
    
    nest3TimeLine = {}
    
    for idAnimalA in range( 1 , 5 ):
        # the id will be the one excluded from nest.
        nest3TimeLine[idAnimalA] = EventTimeLine( None, "Nest3_" , idA = idAnimalA , loadEvent=False )
    
    pool.loadAnonymousDetection()
    
    animalList = pool.getAnimalList() 
    
    result = {}
    for idAnimalA in range( 1 , 5 ):
        result[idAnimalA] = {}
    
    for t in range( tmin, tmax+1 ):
                
        isNest = False
        
        nbAnimalAtT = 0
        animalDetectedList = []
        
        anonymousDetectionList = pool.getAnonymousDetection( t )
        
        for animal in animalList:
            if t in animal.detectionDictionnary:
                nbAnimalAtT+=1
                animalDetectedList.append( animal )
        
        #print( str(t) + " : " + str( nbAnimalAtT ) )
                    
    
        #print("TEST")
        graph = nx.Graph()
        # add nodes
        for animal in animalDetectedList:
            graph.add_node( animal )
        for animalA in animalDetectedList:
            for animalB in animalDetectedList:
                if animalA != animalB:
                    # add an edge
                    if t in contact[animalA.baseId,animalB.baseId]:
                        graph.add_edge( animalA, animalB )
        
        # check with anonymous detection. Check contact
        if anonymousDetectionList!= None:
            # manage anonymous
            # print( t , "manage anonymous")
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
                                # print("Adding edge with mask (det anonymous to det anonymous)")
                    
            for detection in anonymousDetectionList:
                for animal in animalDetectedList:
                    distance = detection.getDistanceTo(animal.getDetectionAt( t ) )
                    if distance != None:
                        if distance < DISTANCE_CONTACT_MASS_CENTER:
                            #if detection.getMask().isInContactWithMask( animal.getDetectionAt ( t ).getMask() ):
                            graph.add_edge( animal, detection )
                            # print("Adding edge with mask")
        
        # list of CC from the biggest to the smallest
        listCC = sorted(nx.connected_components( graph ), key=len, reverse=True)
        
        if ( len( listCC ) == 2 ): # we have 2 groups
            
            # check if animals in the biggest group are stopped.
            allStoppedInBiggestGroup = True
            for animal in list( listCC[0] ):
                if isinstance( animal , Animal ):
                    if not ( t in stopDictionnary[animal.baseId] ):
                        allStoppedInBiggestGroup = False
                        break
                
            if allStoppedInBiggestGroup:
                if ( len( listCC[1] ) == 1 ): # the 2nd group (and the smallest) has only one mouse
                    animal = list(listCC[1])[0]
                    if isinstance( animal , Animal ):                
                        result[ animal.baseId ][ t ] = True
                 
            
    for idAnimalA in range( 1 , 5 ):
            
        # the id will be the one excluded from nest.
        nest3TimeLine[idAnimalA].reBuildWithDictionnary( result[idAnimalA] )
        # remove very small events
        nest3TimeLine[idAnimalA].removeEventsBelowLength( 2 )
        # merge flashing events
        nest3TimeLine[idAnimalA].mergeCloseEvents( 3 )
        nest3TimeLine[idAnimalA].endRebuildEventTimeLine(connection)
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Nest3" , tmin=tmin, tmax=tmax )
          
    

    print( "Rebuild event finished." )
        
    