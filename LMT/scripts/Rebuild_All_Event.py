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
from database.FileUtil import getFilesToProcess
from database.EventTimeLineCache import flushEventTimeLineCache

max_dur = 5*oneDay
USE_CACHE_LOAD_DETECTION_CACHE = True

class FileProcessException(Exception):
    pass

def process( file ):

    print(file)
    
    chronoFullFile = Chronometer("File " + file )
    
    connection = sqlite3.connect( file )        
        
    #t = TaskLogger( connection )
    #t.addLog( "Rebuild all event launch" )
                
    try:

        CheckWrongAnimal.check( connection, tmin=0, tmax=max_dur )
        
        # Warning: this process will alter the database
        #CorrectDetectionIntegrity.correct( connection, tmin=0, tmax=max_dur )
                        
        BuildDataBaseIndex.buildDataBaseIndex( connection, force=False )
            
        BuildEventDetection.reBuildEvent( connection, file, tmin=0, tmax=max_dur )

        animalPool = None
        
        if ( USE_CACHE_LOAD_DETECTION_CACHE ):
            print("Caching load of animal detection...")
            animalPool = AnimalPool( )
            animalPool.loadAnimals( connection )
            animalPool.loadDetection( start = 0, end = max_dur )
            print("Caching load of animal detection done.")

        BuildEventOralOralContact.reBuildEvent( connection, file, tmin=0, tmax=max_dur, pool = animalPool )        
        BuildEventOralGenitalContact.reBuildEvent( connection, file, tmin=0, tmax=max_dur, pool = animalPool )
        
        BuildEventSideBySide.reBuildEvent( connection, file, tmin=0, tmax=max_dur, pool = animalPool )        
        BuildEventSideBySideOpposite.reBuildEvent( connection, file, tmin=0, tmax=max_dur, pool = animalPool )        
    

        BuildEventTrain2.reBuildEvent( connection, file, tmin=0, tmax=max_dur , pool = animalPool )
        
        BuildEventTrain3.reBuildEvent( connection, file, tmin=0, tmax=max_dur , pool = animalPool )   
        BuildEventTrain4.reBuildEvent( connection, file, tmin=0, tmax=max_dur , pool = animalPool )    
              
        BuildEventMove.reBuildEvent( connection, file, tmin=0, tmax=max_dur )
           
        BuildEventFollowZone.reBuildEvent( connection, file, tmin=0, tmax=max_dur, pool = animalPool )
        BuildEventRear5.reBuildEvent( connection, file, tmin=0, tmax=max_dur, pool = animalPool )
        
        BuildEventSocialApproach.reBuildEvent( connection, file, tmin=0, tmax=max_dur, pool = animalPool )
        BuildEventSocialEscape.reBuildEvent( connection, file, tmin=0, tmax=max_dur, pool = animalPool )
        BuildEventApproachRear.reBuildEvent( connection, file, tmin=0, tmax=max_dur )
        BuildEventGroup2.reBuildEvent( connection, file, tmin=0, tmax=max_dur )
        
        BuildEventGroup3.reBuildEvent( connection, file, tmin=0, tmax=max_dur )
        BuildEventGroup4.reBuildEvent( connection, file, tmin=0, tmax=max_dur )
        
        BuildEventGroup4MakeBreak.reBuildEvent( connection, file, tmin=0, tmax=max_dur )
        BuildEventGroup3MakeBreak.reBuildEvent( connection, file, tmin=0, tmax=max_dur )
        
        BuildEventStop.reBuildEvent( connection, file, tmin=0, tmax=max_dur )
        BuildEventWaterPoint.reBuildEvent(connection, file, tmin=0, tmax=max_dur, pool = animalPool )
        BuildEventApproachContact.reBuildEvent( connection, file, tmin=0, tmax=max_dur )
        BuildEventWallJump.reBuildEvent(connection, file, tmin=0, tmax=max_dur , pool = animalPool )
        BuildEventSAP.reBuildEvent(connection,  file, tmin=0, tmax=max_dur , pool = animalPool )
    
        BuildEventOralSideSequence.reBuildEvent( connection, file, tmin=0, tmax=max_dur, pool = animalPool )
        chronoFullFile.printTimeInS()
        
        
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
    
    files = getFilesToProcess()

    chronoFullBatch = Chronometer("Full batch" )    
        
    if ( files != None ):
    
        for file in files:
            try:
                print ( "Processing file" , file )
                process( file )
            except FileProcessException:
                print ( "STOP PROCESSING FILE " + file , file=sys.stderr  )
        
            flushEventTimeLineCache()
        
    chronoFullBatch.printTimeInS()
    print( "*** ALL JOBS DONE ***")
        
        