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
    CorrectDetectionIntegrity, BuildEventNest4, BuildEventNest3, BuildEventGetAway, BuildEventHuddling

    
from psutil import virtual_memory

from tkinter.filedialog import askopenfilename
from lmtanalysis.TaskLogger import TaskLogger
import sys
import traceback
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.EventTimeLineCache import flushEventTimeLineCache,\
    disableEventTimeLineCache


from lmtanalysis.EventTimeLineCache import EventTimeLineCached


''' minT and maxT to process the analysis (in frame '''
minT = 0

#maxT = 1 *oneMinute
maxT = 3*oneDay
#maxT = (6+1)*oneHour
''' time window to compute the events. '''
windowT = 1*oneDay
#windowT = 3*oneDay #int (0.5*oneDay)


USE_CACHE_LOAD_DETECTION_CACHE = True

class FileProcessException(Exception):
    pass


eventClassList = [
                
                BuildEventDetection,                  
                BuildEventOralOralContact,
                BuildEventOralGenitalContact,
                BuildEventSideBySide,
                BuildEventSideBySideOpposite,
                BuildEventTrain2,                  
                BuildEventTrain3,
                BuildEventTrain4,
                BuildEventMove,
                BuildEventFollowZone,
                BuildEventRear5,
                BuildEventSocialApproach,
                BuildEventGetAway,
                #BuildEventSocialEscape,
                BuildEventApproachRear,
                BuildEventGroup2,
                BuildEventGroup3,
                BuildEventGroup4,
                BuildEventGroup3MakeBreak,
                BuildEventGroup4MakeBreak,
                BuildEventStop,
                BuildEventWaterPoint,
                BuildEventApproachContact,
                BuildEventWallJump,
                BuildEventSAP,
                BuildEventOralSideSequence,                
                BuildEventNest3,
                BuildEventNest4
                   ]


def flushEvents( connection ):
    
    print("Flushing events...")

    for ev in eventClassList:
        
        chrono = Chronometer( "Flushing event " + str(ev) )
        ev.flush( connection );      
        chrono.printTimeInS()
    

def processTimeWindow( connection, file, currentMinT , currentMaxT ):
    
    CheckWrongAnimal.check( connection, tmin=currentMinT, tmax=currentMaxT )
    
    # Warning: enabling this process (CorrectDetectionIntegrity) will alter the database permanently
    # CorrectDetectionIntegrity.correct( connection, tmin=0, tmax=maxT )
                            
    # BuildEventDetection.reBuildEvent( connection, file, tmin=currentMinT, tmax=currentMaxT )

    animalPool = None
    
    flushEventTimeLineCache()
    
    if ( USE_CACHE_LOAD_DETECTION_CACHE ):
        print("Caching load of animal detection...")
        animalPool = AnimalPool( )
        animalPool.loadAnimals( connection )
        animalPool.loadDetection( start = currentMinT, end = currentMaxT )
        print("Caching load of animal detection done.")

    for ev in eventClassList:
        
        chrono = Chronometer( str( ev ) )
        ev.reBuildEvent( connection, file, tmin=currentMinT, tmax=currentMaxT, pool = animalPool )        
        chrono.printTimeInS()
        


def process( file ):

    print(file)
        
    mem = virtual_memory()
    availableMemoryGB = mem.total / 1000000000
    print( "Total memory on computer: (GB)", availableMemoryGB ) 
    
    if availableMemoryGB < 10:
        print( "Not enough memory to use cache load of events.")
        disableEventTimeLineCache()

    
    chronoFullFile = Chronometer("File " + file )
    
    connection = sqlite3.connect( file )
    
    # update missing fields
    try:
        connection = sqlite3.connect( file )    
        c = connection.cursor()            
        query = "ALTER TABLE EVENT ADD METADATA TEXT";
        c.execute( query )    
        connection.commit()
        #c.close()
        #connection.close()
    except:
        print( "METADATA field already exists" , file )
    
    BuildDataBaseIndex.buildDataBaseIndex( connection, force=False )
    
    # build sensor data
    animalPool = AnimalPool( )
    animalPool.loadAnimals( connection )
    #animalPool.buildSensorData(file)
    
    currentT = minT

    try:

        flushEvents( connection )
        
        while currentT < maxT:
                        
            currentMinT = currentT
            currentMaxT = currentT+ windowT
            if ( currentMaxT > maxT ):
                currentMaxT = maxT
                
            chronoTimeWindowFile = Chronometer("File "+ file+ " currentMinT: "+ str(currentMinT)+ " currentMaxT: " + str(currentMaxT) );
            processTimeWindow( connection, file, currentMinT, currentMaxT )    
            chronoTimeWindowFile.printTimeInS()
            
            currentT += windowT

                        

        print("Full file process time: ")
        chronoFullFile.printTimeInS()
    
        
        TEST_WINDOWING_COMPUTATION = False
        
        if ( TEST_WINDOWING_COMPUTATION ):
                
            print("*************")
            print("************* TEST START SECTION")
            print("************* Test if results are the same with or without the windowing.")
            
            # display and record to a file all events found, checking with rolling idA from None to 4. Save nbEvent and total len
            
            eventTimeLineList = []
            
            eventList = getAllEvents( connection )
            file = open("outEvent"+str(windowT)+".txt","w")  
            file.write( "Event name\nnb event\ntotal duration" )
            
            for eventName in eventList:
                for animal in range( 0,5 ):                
                        idA = animal 
                        if idA == 0:
                            idA = None
                        timeLine = EventTimeLineCached( connection, file, eventName, idA,  minFrame=minT, maxFrame=maxT )
                        eventTimeLineList.append( timeLine )
                        file.write( timeLine.eventNameWithId+"\t"+str(len(timeLine.eventList))+"\t"+str(timeLine.getTotalLength())+"\n" )            
            
            file.close() 
    
            #plotMultipleTimeLine( eventTimeLineList )
            
            print("************* END TEST")
            
        flushEventTimeLineCache()        
        
    except:
        
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        error = ''.join('!! ' + line for line in lines)
        
        t = TaskLogger( connection )
        t.addLog( error )
        flushEventTimeLineCache()
        
        print( error, file=sys.stderr ) 
        
        raise FileProcessException()
    
    
            
def getAllEvents( connection ):
    
    query = "select name from event group by name order by name"
    c = connection.cursor()     
    c.execute( query )    
    all_rows = c.fetchall()        
    header = [ "Name" ]
    data =[]    
    for row in all_rows:
        data.append( row[0] )
    return data

def processAll():
    
    
    files = getFilesToProcess()

    chronoFullBatch = Chronometer("Full batch" )    
        
    if ( files != None ):
    
        for file in files:
            try:
                print ( "Processing file" , file )
                process( file )
            except FileProcessException:
                print ( "STOP PROCESSING FILE " + file , file=sys.stderr  )
        
    chronoFullBatch.printTimeInS()
    print( "*** ALL JOBS DONE ***")

if __name__ == '__main__':
    
    print("Code launched.")
    processAll()
    
        
        