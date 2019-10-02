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

class FileProcessException(Exception):
    pass

   
def process( file ):
    
    connection = sqlite3.connect( file )     

    print( "--------------")
    print( "Current file: ", file )
    print( "Loading existing events...")
    nightTimeLine = EventTimeLine( connection, "night" , None, None, None , None )        
    
    
    print( "--------------")    
    print( "Event list:" )
    for event in nightTimeLine.eventList:
        print( event )
    print( "--------------")
    
    nightTimeLine.removeEventsOverT(maxT=1050000)
    
    while True:
        print( "Manually add night event:")
        startFrame = input( "Start Frame (return to cancel):" )
        if not startFrame.isdigit():
            return
        
        endFrame = input( "End Frame (return to cancel):" )
        if not endFrame.isdigit():
            return
        
        nightTimeLine.addEvent( Event( int(startFrame), int(endFrame) ) )
        nightTimeLine.endRebuildEventTimeLine(connection)

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
              
    print( "*** ALL JOBS DONE ***")
        
        