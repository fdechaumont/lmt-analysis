'''
Created on 29 avr. 2019

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
    CorrectDetectionIntegrity, BuildEventNest4, BuildEventNest3, BuildEventFight, BuildEventGetAway
    
from psutil import virtual_memory

from tkinter.filedialog import askopenfilename
from lmtanalysis.TaskLogger import TaskLogger
import sys
import traceback
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.EventTimeLineCache import flushEventTimeLineCache,\
    disableEventTimeLineCache

from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from astropy.table.bst import MinValue


class FileProcessException(Exception):
    pass

def process( file ):

    print(file)
    
    chronoFullFile = Chronometer("File " + file )
    
    connection = sqlite3.connect( file )
    

    try:

        animalPool = AnimalPool( )
        animalPool.loadAnimals( connection )
        
        animalPool.buildSensorData( file )
        '''
        animalPool.createAutomaticDayNightEvent( )        
        animalPool.plotNight( False , saveFile = file+"_auto day night.pdf" )

        animalPool.plotSensorData( sensor = "TEMPERATURE" , minValue = 10, saveFile = file+"_log_temperature.pdf", show = False )
        animalPool.plotSensorData( sensor = "SOUND" , saveFile = file+"_log_sound level.pdf" , show = False )
        animalPool.plotSensorData( sensor = "HUMIDITY" , minValue = 5 , saveFile = file+"_log_humidity.pdf" ,show = False )        
        animalPool.plotSensorData( sensor = "LIGHTVISIBLE" , minValue = 40 , saveFile = file+"_log_light visible.pdf", show = False  )
        animalPool.plotSensorData( sensor = "LIGHTVISIBLEANDIR" , minValue = 50 , saveFile = file+"_log_light visible and infra.pdf", show = False  )
        '''

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
        