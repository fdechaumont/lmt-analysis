'''
Created on 20 mars 2019

@author: nicolas
'''

import sqlite3
import datetime as dt
from datetime import datetime
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.Util import *
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
from scripts.Compute_Measures_Identity_Profile import getNumberOfEventWithList
from astropy.units import microsecond

class FileProcessException(Exception):
    pass

if __name__ == '__main__':
    print("Code launched.")
    
    '''
       files = getFilesToProcess()
    
        chronoFullBatch = Chronometer("Full batch" )
        if ( files != None ):
            
            for file in files:
                try:
                    print ( "Processing file" , file )
                    numberOfFrames = getNumberOfFrames(file)
                    print(numberOfFrames)
                    
                except FileProcessException:
                    print ( "STOP PROCESSING FILE " + file , file=sys.stderr  )
        
        print( "*** ALL JOBS DONE ***")
    '''
    print("hop")
    print(dt.time())
    print("gna")
    
    timestamp = 1515570902366
    #print(str(timestamp)[:-3])
    #timestamp = 14792497997.70
    #laDate = datetime.fromtimestamp(int(str(timestamp)[:10]))
    #laDate = datetime.fromtimestamp(int(str(timestamp))/1000)
    #ladate = laDate.replace(hour=laDate.hour, minute=laDate.minute, second=laDate.second , microsecond=int(str(timestamp)[10:]))
    #print(laDate)
    
    files = getFilesToProcess()
    print("debut de la manip: ")
    chronoFullBatch = Chronometer("Full batch" )    
    
    if( files != None ):
    
        for file in files:
            try:
                connection = sqlite3.connect( file )
                print("***************** test night *****************")
                hop1=getDatetimeFromFrame(connection, 7132)
                hop2=getDatetimeFromFrame(connection, 10732)
                print(hop1)
                print(hop2)
                
                print ( "Processing file" , file )
                startXp = getStartInDatetime(connection)
                endXp = getEndInDatetime(connection)
                print(startXp)
                print(endXp)
                print ("test hors de l'xp")
                targetDate = getDatetimeFromFrame(connection, 5332)
                print(targetDate)
                dateDuMoment = recoverFrame(connection , "2018-01-10 10:58:00")
                
                connection.close()           
 

            except FileProcessException:
                print ( "STOP PROCESSING FILE " + file , file=sys.stderr  )
                

              
    print( "*** ALL JOBS DONE ***")
    
    
    
    
    
    #FDT = '%Y-%m-%d %H:%M:%S'
    #testDate = datetime.strptime('2019-03-13 19:00:00', FDT)
    #print(testDate)
    '''
    FMT = '%H:%M:%S'
    nightHour = datetime.strptime('19:00:00', FMT)
    dayHour = datetime.strptime('07:30:00', FMT)
    tdelta =  nightHour - dayHour
    print(tdelta)
    
    heureNuit = dt.time(19, 0, 0)
    heureJour = dt.time(7, 0, 0)
    print(heureNuit)
    print(heureJour)
    print(heureJour-heureNuit)
    '''
    