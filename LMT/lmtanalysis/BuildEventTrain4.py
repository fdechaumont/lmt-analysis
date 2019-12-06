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
from lmtanalysis.EventTimeLineCache import EventTimeLineCached

class Train2():
    
    def __init__(self, idA, idB ):
        self.idA = idA
        self.idB = idB

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Train4" )

def reBuildEvent( connection, file, tmin=None, tmax=None , pool = None ): 

    ''' use pool cache if available '''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        if ( len ( pool.getAnimalList( ) ) < 4 ):
            print("Train 4 cannot be computed on an experiment with less than 4 animals")
            return
        pool.loadDetection( start = tmin, end = tmax )    
    
    '''
    three animals are following each others with nose-to-anogenital contacts
    animals are moving
    
    this is a combination of Train2 events (train2 events must be calculated before this event)
    '''

    #deleteEventTimeLineInBase(connection, "Train4" )

    ''' build a list of train 2 for each time point '''
    
    time = {}
    train4 = {}
    
    for animal in range( 1, pool.getNbAnimals()+1 ):
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if ( animal == idAnimalB ):
                continue
            train2TimeLine = EventTimeLineCached( connection, file, "Train2", animal, idAnimalB, minFrame=tmin, maxFrame=tmax )
            for t in train2TimeLine.getDictionnary():
                train = Train2( animal, idAnimalB )
                
                if ( not t in time ):
                    time[t] =[]
                    
                #print ( t , ":" , train.idA , " -> ", train.idB , "*" )
                time[t].append( train )
    

    for t in time:
        trainList = time[t]
        
        for train1st in trainList:
            
            for train2nd in trainList:
                
                if ( train1st == train2nd ):
                    continue

                for train3rd in trainList:
                    
                    if ( train3rd == train1st or train3rd == train2nd):
                        continue
                    
                    isValid = ""
                    ''' test chain link between train2 events '''
                   
                    if train1st.idB == train2nd.idA and train2nd.idB == train3rd.idA :
                        
                        id1 = train1st.idA
                        id2 = train1st.idB
                        id3 = train2nd.idB
                        id4 = train3rd.idB
    
                        if not (id1, id2, id3,id4) in train4:    
                            train4[id1,id2,id3,id4] = {} 
                        
                        train4[id1,id2,id3,id4][t]=True
                        
                        isValid = ": validated train 4"
                    #print ( t , ":" , train1st.idA , " -> ", train1st.idB, "--->", train2nd.idA , " -> ", train2nd.idB , " -> ", train3rd.idA , " -> ", train3rd.idB , isValid )


    ''' save data '''
            
    for animal in range( 1 , pool.getNbAnimals()+1 ):
    
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            
            for idAnimalC in range( 1 , pool.getNbAnimals()+1 ):

                for idAnimalD in range( 1 , pool.getNbAnimals()+1 ):

                    if (animal, idAnimalB, idAnimalC, idAnimalD) in train4:
                        
                        trainTimeLine = EventTimeLine( None, "Train4" , animal , idAnimalB, idAnimalC, idAnimalD, loadEvent=False )
                        
                        trainTimeLine.reBuildWithDictionnary( train4[animal,idAnimalB,idAnimalC,idAnimalD] )
                        #trainTimeLine.removeEventsBelowLength( 5 )            
                        trainTimeLine.endRebuildEventTimeLine(connection)
                    
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Train4" , tmin=tmin, tmax=tmax )

    print( "Rebuild event finished." )
    
    return
   
    
    