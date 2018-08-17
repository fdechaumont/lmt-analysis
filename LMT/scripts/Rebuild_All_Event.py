'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from database.Animal import *
import matplotlib.pyplot as plt
from database.Event import *
from database.Measure import *
from database import BuildEventTrain3, BuildEventTrain4, BuildEventTrain2, BuildEventFollowZone, BuildEventRear5, BuildEventFloorSniffing,\
    BuildEventSocialApproach, BuildEventSocialEscape, BuildEventApproachContact,BuildEventOralOralContact,\
    BuildEventApproachRear, BuildEventGroup2, BuildEventGroup3, BuildEventGroup4, BuildEventOralGenitalContact, \
    BuildEventStop, BuildEventWaterPoint, \
    BuildEventMove, BuildEventGroup3MakeBreak, BuildEventGroup4MakeBreak,\
    BuildEventSideBySide, BuildEventSideBySideOpposite, BuildEventDetection,\
    BuildDataBaseIndex, BuildEventWallJump, BuildEventSAP,\
    BuildEventOralSideSequence, CheckWrongAnimal,\
    CorrectDetectionIntegrity
    
    
from tkinter.filedialog import askopenfilename
from database.TaskLogger import TaskLogger
import sys
import traceback

max_dur = 3*oneDay
USE_CACHE_LOAD_DETECTION_CACHE = True

class FileProcessException(Exception):
    pass

def process( file ):

    print(file)
    connection = sqlite3.connect( file )        
        
    #t = TaskLogger( connection )
    #t.addLog( "Rebuild all event launch" )
                
    try:

        CheckWrongAnimal.check( connection, tmin=0, tmax=max_dur )
        
        # Warning: this process will alter the database
        CorrectDetectionIntegrity.correct( connection, tmin=0, tmax=max_dur )
         
        ''' now performed directly by LMT as it creates the database to store data (in java) '''               
        #BuildDataBaseIndex.buildDataBaseIndex( connection, force=False )
            
        BuildEventDetection.reBuildEvent( connection, tmin=0, tmax=max_dur )

        animalPool = None
        
        if ( USE_CACHE_LOAD_DETECTION_CACHE ):
            print("Caching load of animal detection...")
            animalPool = AnimalPool( )
            animalPool.loadAnimals( connection )
            animalPool.loadDetection( start = 0, end = max_dur )
            print("Caching load of animal detection done.")

        BuildEventOralOralContact.reBuildEvent( connection, tmin=0, tmax=max_dur, pool = animalPool )        
        BuildEventOralGenitalContact.reBuildEvent( connection, tmin=0, tmax=max_dur, pool = animalPool )
        
        BuildEventSideBySide.reBuildEvent( connection, tmin=0, tmax=max_dur, pool = animalPool )        
        BuildEventSideBySideOpposite.reBuildEvent( connection, tmin=0, tmax=max_dur, pool = animalPool )        
    
        BuildEventTrain2.reBuildEvent( connection, tmin=0, tmax=max_dur , pool = animalPool )
        '''
        BuildEventTrain3.reBuildEvent( connection, tmin=0, tmax=max_dur , pool = animalPool )   
        BuildEventTrain4.reBuildEvent( connection, tmin=0, tmax=max_dur , pool = animalPool )    
        '''      
        BuildEventMove.reBuildEvent( connection, tmin=0, tmax=max_dur )
           
        BuildEventFollowZone.reBuildEvent( connection, tmin=0, tmax=max_dur, pool = animalPool )
        BuildEventRear5.reBuildEvent( connection, tmin=0, tmax=max_dur, pool = animalPool )
        
        BuildEventSocialApproach.reBuildEvent( connection, tmin=0, tmax=max_dur, pool = animalPool )
        BuildEventSocialEscape.reBuildEvent( connection, tmin=0, tmax=max_dur, pool = animalPool )
        BuildEventApproachRear.reBuildEvent( connection, tmin=0, tmax=max_dur )
        BuildEventGroup2.reBuildEvent( connection, tmin=0, tmax=max_dur )
        '''
        BuildEventGroup3.reBuildEvent( connection, tmin=0, tmax=max_dur )
        BuildEventGroup4.reBuildEvent( connection, tmin=0, tmax=max_dur )
        
        BuildEventGroup4MakeBreak.reBuildEvent( connection, tmin=0, tmax=max_dur )
        BuildEventGroup3MakeBreak.reBuildEvent( connection, tmin=0, tmax=max_dur )
        '''
    
        BuildEventStop.reBuildEvent( connection, tmin=0, tmax=max_dur )
        BuildEventWaterPoint.reBuildEvent(connection, tmin=0, tmax=max_dur, pool = animalPool )
        BuildEventApproachContact.reBuildEvent( connection, tmin=0, tmax=max_dur )
        BuildEventWallJump.reBuildEvent(connection, tmin=0, tmax=max_dur , pool = animalPool )
        BuildEventSAP.reBuildEvent(connection,  tmin=0, tmax=max_dur , pool = animalPool )
    
        BuildEventOralSideSequence.reBuildEvent( connection, tmin=0, tmax=max_dur, pool = animalPool )
        
    except:
        
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        error = ''.join('!! ' + line for line in lines)
        
        t = TaskLogger( connection )
        t.addLog( error )
        
        print( error, file=sys.stderr ) 
        
        raise FileProcessException()
        

if __name__ == '__main__':
    
    print("Code launched.")
     
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    
    for file in files:
        '''
        from multiprocessing.dummy import Pool as ThreadPool 
        pool = ThreadPool(4) 
        results = pool.map( process, files )
        pool.close()
        pool.join()
        '''
        try:
            process( file )
        except FileProcessException:
            print ( "STOP PROCESSING FILE " + file , file=sys.stderr  )
        
    print( "*** ALL JOBS DONE ***")
        
        