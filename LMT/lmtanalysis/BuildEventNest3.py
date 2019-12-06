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
    deleteEventTimeLineInBase(connection, "Nest3" )


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
        
    for idAanimal in range( 1 , 5 ):
        for idAnimalB in range( 1 , 5 ):
            if idAanimal != idAnimalB:    
                contact[idAanimal, idAnimalB] = EventTimeLineCached( connection, file, "Contact", idAanimal, idAnimalB, minFrame=tmin, maxFrame=tmax ).getDictionnary()

    stopDictionnary = {}
        
    for idAanimal in range( 1 , 5 ):
        stopDictionnary[idAanimal] = EventTimeLineCached( connection, file, "Stop", idAanimalinFrame=tmin, maxFrame=tmax ).getDictionnary()
    
    nest3TimeLine = {}
    
    for idAanimal in range( 1 , 5 ):
        # the id will be the one excluded from nest.
        nest3TimeLine[idAanimal] = EventTimeLine( None, "Nest3" , idAanimaloadEvent=False )
    
    
    animalList = pool.getAnimalList() 
    
    result = {}
    for idAanimal in range( 1 , 5 ):
        result[idAanimal] = {}
    
    for t in range( tmin, tmax+1 ):
                
        isNest = False
        
        nbAnimalAtT = 0
        animalDetectedList = []
        
        for animal in animalList:
            if t in animal.detectionDictionnary:
                nbAnimalAtT+=1
                animalDetectedList.append( animal )
        
        #print( str(t) + " : " + str( nbAnimalAtT ) )
                    
    
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
        
        # list of CC from the biggest to the smallest
        listCC = sorted(nx.connected_components( graph ), key=len, reverse=True)
        
        if ( len( listCC ) == 2 ): # we have 2 groups
            
            # check if animals in the biggest group are stopped.
            allStoppedInBiggestGroup = True
            for animal in list( listCC[0] ):
                if not ( t in stopDictionnary[animal.baseId] ):
                    allStoppedInBiggestGroup = False
                    break
                
            if allStoppedInBiggestGroup:
                if ( len( listCC[1] ) == 1 ): # the 2nd group (and the smallest) has only one mouse
                    animal = list(listCC[1])[0]                
                    result[ animal.baseId ][ t ] = True
                 
        
        '''
        largestCC = len ( max(nx.connected_components( graph ), key=len) )
        
        #print( str( t ) + " : " + str ( len( largestCC ) ) )
        
        print( str( t ) + " : " + str ( largestCC ) + " / " + str( nbAnimalAtT ) )
        
        if largestCC == nbAnimalAtT :
            isNest= True         
        
                     
        if isNest == True:
            print( "ADD PUNCTUAL")
            result[t] = True;
        ''' 
    
    for idAanimal range( 1 , 5 ):
        # the id will be the one excluded from nest.
        nest3TimeLine[idAanimaleBuildWithDictionnary( result[idAanimal
        
        # remove very small events
        nest3TimeLine[idAanimalemoveEventsBelowLength( 2 )
        nest3TimeLine[idAanimalergeCloseEvents( 3 )
        
        nest3TimeLine[idAanimalndRebuildEventTimeLine(connection)
            
    #nest4TimeLine.reBuildWithDictionnary( result )
    
    #nest4TimeLine.endRebuildEventTimeLine(connection)
         
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Nest3" , tmin=tmin, tmax=tmax )
          
    

    print( "Rebuild event finished." )
        
    