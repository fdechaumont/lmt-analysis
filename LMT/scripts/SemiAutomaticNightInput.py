'''
Created on 07 mar. 2019
This code is based on the script ManualNightInput.py

@author: Nicolas
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
    
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


def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "night" )
    
   
def insertNightEvent( file ):
    
    connection = sqlite3.connect( file )     
                
    print( "--------------")
    print( "Current file: ", file )
    print("Flush")
    flush( connection )
    
    print( "--------------")
    print( "Loading existing events...")
    nightTimeLine = EventTimeLine( connection, "night" , None, None, None , None )        
    
    print( "--------------")    
    print( "Event list:" )
    for event in nightTimeLine.eventList:
        print( event )
    print( "--------------")
    
    startNight = input( "Start night frame:" )
    if not startNight.isdigit():
        print("Error on start night")
    startNight = int(startNight)
    nightDuration = input( "Night duration (in frames):" )
    if not nightDuration.isdigit():
        print("Error on night duration")
    numberOfNight = input( "Number of night:" )
    if not numberOfNight.isdigit():
        print("Error on number of night")
        
    lightDuration = 24*oneHour-int(nightDuration)
    
    for i in range(0,int(numberOfNight)):
        startFollowingNight = startNight+ i*int(nightDuration) + i*int(lightDuration)
        endFollowingNight = startNight + i*int(lightDuration) + (i+1)*int(nightDuration)
        nightTimeLine.addEvent( Event( startFollowingNight, endFollowingNight) )
        print ( "Night ", i)
        print ("following night start: ", startFollowingNight )
        print ( "following night end: ", endFollowingNight )
    
    nightTimeLine.endRebuildEventTimeLine(connection)
    print(nightTimeLine.getNumberOfEvent())
    
    

if __name__ == '__main__':
    
    print("Code launched.")
    
    files = getFilesToProcess()

    chronoFullBatch = Chronometer("Full batch" )    
        
    if ( files != None ):
    
        for file in files:
            try:
                print ( "Processing file" , file )
                insertNightEvent( file )

            except FileProcessException:
                print ( "STOP PROCESSING FILE " + file , file=sys.stderr  )
              
    print( "*** ALL JOBS DONE ***")
        
        