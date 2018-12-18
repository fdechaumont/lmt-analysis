'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis import BuildEventTrain3, BuildEventTrain4, BuildEventTrain2, BuildEventFollowZone, BuildEventRear5, BuildEventFloorSniffing,\
    BuildEventSocialApproach, BuildEventSocialEscape, BuildEventApproachContact,BuildEventOralOralContact,\
    BuildEventApproachRear, BuildEventGroup2, BuildEventGroup3, BuildEventGroup4, BuildEventOralGenitalContact, \
    BuildEventStop, BuildEventWaterPoint, \
    BuildEventMove, BuildEventGroup3MakeBreak, BuildEventGroup4MakeBreak,\
    BuildEventSideBySide, BuildEventSideBySideOpposite, BuildEventDetection,\
    BuildDataBaseIndex, BuildEventWallJump, BuildEventSAP,\
    BuildEventOralSideSequence, CheckWrongAnimal,\
    CorrectDetectionIntegrity
    
from psutil import virtual_memory

from tkinter.filedialog import askopenfilename
from lmtanalysis.TaskLogger import TaskLogger
import sys
import traceback
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.EventTimeLineCache import flushEventTimeLineCache,\
    disableEventTimeLineCache

''' minT and maxT to process the analysis (in frame '''
maxT = 5*oneDay
minT = 0

USE_CACHE_LOAD_DETECTION_CACHE = True

class FileProcessException(Exception):
    pass

def process( file ):

    print(file)
    
    chronoFullFile = Chronometer("File " + file )
    
    connection = sqlite3.connect( file )        
        
    # TODO: flush events,
    # recompute per segment of 24h.

    try:

        CheckWrongAnimal.check( connection, tmin=0, tmax=maxT )
        
        # Warning: this process will alter the lmtanalysis
        #CorrectDetectionIntegrity.correct( connection, tmin=0, tmax=maxT )
                        
        BuildDataBaseIndex.buildDataBaseIndex( connection, force=False )
            
        BuildEventDetection.reBuildEvent( connection, file, tmin=0, tmax=maxT )

        animalPool = None
        
        if ( USE_CACHE_LOAD_DETECTION_CACHE ):
            print("Caching load of animal detection...")
            animalPool = AnimalPool( )
            animalPool.loadAnimals( connection )
            animalPool.loadDetection( start = 0, end = maxT )
            print("Caching load of animal detection done.")

        chrono = Chronometer("Oral oral contact" )
        BuildEventOralOralContact.reBuildEvent( connection, file, tmin=0, tmax=maxT, pool = animalPool )        
        chrono.printTimeInS()

        chrono = Chronometer("Oral genital contact" )
        BuildEventOralGenitalContact.reBuildEvent( connection, file, tmin=0, tmax=maxT, pool = animalPool )
        chrono.printTimeInS()
        
        chrono = Chronometer("Side by side" )
        BuildEventSideBySide.reBuildEvent( connection, file, tmin=0, tmax=maxT, pool = animalPool )        
        chrono.printTimeInS()

        chrono = Chronometer("Side by side opposite" )
        BuildEventSideBySideOpposite.reBuildEvent( connection, file, tmin=0, tmax=maxT, pool = animalPool )        
        chrono.printTimeInS()
    

        chrono = Chronometer("Train 2" )
        BuildEventTrain2.reBuildEvent( connection, file, tmin=0, tmax=maxT , pool = animalPool )
        chrono.printTimeInS()
        
        chrono = Chronometer("Train 3" )
        BuildEventTrain3.reBuildEvent( connection, file, tmin=0, tmax=maxT , pool = animalPool )   
        chrono.printTimeInS()

        chrono = Chronometer("Train 4" )
        BuildEventTrain4.reBuildEvent( connection, file, tmin=0, tmax=maxT , pool = animalPool )    
        chrono.printTimeInS()
        
        chrono = Chronometer("Move" )      
        BuildEventMove.reBuildEvent( connection, file, tmin=0, tmax=maxT )
        chrono.printTimeInS()
           
        chrono = Chronometer("FollowZone" )      
        BuildEventFollowZone.reBuildEvent( connection, file, tmin=0, tmax=maxT, pool = animalPool )
        chrono.printTimeInS()
        
        chrono = Chronometer("Rear" )      
        BuildEventRear5.reBuildEvent( connection, file, tmin=0, tmax=maxT, pool = animalPool )
        chrono.printTimeInS()
        
        chrono = Chronometer("Social approach" )      
        BuildEventSocialApproach.reBuildEvent( connection, file, tmin=0, tmax=maxT, pool = animalPool )
        chrono.printTimeInS()
        
        chrono = Chronometer("Social escape" )      
        BuildEventSocialEscape.reBuildEvent( connection, file, tmin=0, tmax=maxT, pool = animalPool )
        chrono.printTimeInS()

        chrono = Chronometer("Social approach rear" )      
        BuildEventApproachRear.reBuildEvent( connection, file, tmin=0, tmax=maxT )
        chrono.printTimeInS()
        
        chrono = Chronometer("group2" )      
        BuildEventGroup2.reBuildEvent( connection, file, tmin=0, tmax=maxT )
        chrono.printTimeInS()
        
        chrono = Chronometer("group3" )      
        BuildEventGroup3.reBuildEvent( connection, file, tmin=0, tmax=maxT )
        chrono.printTimeInS()

        chrono = Chronometer("group4" )      
        BuildEventGroup4.reBuildEvent( connection, file, tmin=0, tmax=maxT )
        chrono.printTimeInS()
        
        chrono = Chronometer("group4 make break" )      
        BuildEventGroup4MakeBreak.reBuildEvent( connection, file, tmin=0, tmax=maxT )
        chrono.printTimeInS()

        chrono = Chronometer("group3 make break" )      
        BuildEventGroup3MakeBreak.reBuildEvent( connection, file, tmin=0, tmax=maxT )
        chrono.printTimeInS()
        
        chrono = Chronometer("stop" )      
        BuildEventStop.reBuildEvent( connection, file, tmin=0, tmax=maxT )
        chrono.printTimeInS()

        chrono = Chronometer("waterpoint" )      
        BuildEventWaterPoint.reBuildEvent(connection, file, tmin=0, tmax=maxT, pool = animalPool )
        chrono.printTimeInS()

        chrono = Chronometer("approach contact" )      
        BuildEventApproachContact.reBuildEvent( connection, file, tmin=0, tmax=maxT )
        chrono.printTimeInS()

        chrono = Chronometer("wall jump" )      
        BuildEventWallJump.reBuildEvent(connection, file, tmin=0, tmax=maxT , pool = animalPool )
        chrono.printTimeInS()

        chrono = Chronometer("sap" )      
        BuildEventSAP.reBuildEvent(connection,  file, tmin=0, tmax=maxT , pool = animalPool )
        chrono.printTimeInS()
    
        chrono = Chronometer("oral side sequence" )
        BuildEventOralSideSequence.reBuildEvent( connection, file, tmin=0, tmax=maxT, pool = animalPool )
        chrono.printTimeInS()

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
    
    mem = virtual_memory()
    availableMemoryGB = mem.total / 1000000000
    print( "Total memory on computer: (GB)", availableMemoryGB ) 
    
    if availableMemoryGB < 16:
        print( "Not enough memory to use cache load of events.")
        disableEventTimeLineCache()
    
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
        
        