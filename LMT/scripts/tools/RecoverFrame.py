'''
Created on 08 fevrier 2019

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

import time
import datetime
from conda._vendor.toolz.itertoolz import diff

class FileProcessException(Exception):
    pass
   
if __name__ == '__main__':
    
    print("Code launched.")
    
    print("This tools convert dates to timestamp, and then fetch in database which frame is the closest.")
    print("This code use local time. So be sure to query in the same timezone as the one of the database.")
    print("----------------------------------------------------------------------------------------------")
    files = getFilesToProcess()
    
    file = files[0];
    connection = sqlite3.connect( file )
    c = connection.cursor()
    
    # get timedate of 1st and last frame
    
    query = "SELECT FRAMENUMBER, TIMESTAMP FROM FRAME WHERE FRAMENUMBER=1";
    c.execute( query )
    all_rows = c.fetchall()
    #print( str( all_rows ) )
    startTS = int ( int ( all_rows[0][1] ) / 1000 )
    #print( startTS )
    #startDate = datetime.datetime.utcfromtimestamp( startTS ).strftime('%Y-%m-%d %H:%M:%S')    
    startDate = datetime.datetime.fromtimestamp( startTS ).strftime('%d-%m-%Y %H:%M:%S')
    
    query = "SELECT max(FRAMENUMBER) FROM FRAME";
    c.execute( query )
    all_rows = c.fetchall()
    maxFrame = all_rows[0][0]
    #print( "MaxFrame " + str( maxFrame ) )
    
    query = "SELECT FRAMENUMBER, TIMESTAMP FROM FRAME WHERE FRAMENUMBER={}".format( maxFrame );
    c.execute( query )
    all_rows = c.fetchall()
    endTS = int ( int ( all_rows[0][1] ) / 1000 )
    #endDate = datetime.datetime.utcfromtimestamp( endTS ).strftime('%Y-%m-%d %H:%M:%S')
    endDate = datetime.datetime.fromtimestamp( endTS ).strftime('%d-%m-%Y %H:%M:%S')
    
    print ( file )
    print ( "Start date of record : " + startDate )
    print ( "End date of record : " + endDate )
        
    #print(datetime.utcfromtimestamp(startTS).strftime('%Y/%m/%d %H:%M:%S'))
    

    
    
    while( True ):
        
        print ("----------- ")
        date = input( "dd-mm-YYYY hh:mm:ss : " )
        
        if ( len( date ) < 3 ):
            break
                
        timeStamp = time.mktime(datetime.datetime.strptime(date, "%d-%m-%Y %H:%M:%S").timetuple()) * 1000
    
        print( "TimeStamp * 1000 is : " + str( timeStamp ) )
    
        print( "Searching closest frame in database....")
        
        query = "SELECT FRAMENUMBER, TIMESTAMP FROM FRAME WHERE TIMESTAMP>{} AND TIMESTAMP<{}".format( timeStamp - 10000 , timeStamp + 10000 );
        
        c.execute( query )
        all_rows = c.fetchall()
        
        closestFrame = 0        
        smallestDif = 100000000
        
        for row in all_rows:
            
            ts = int ( row[1] )
            dif = abs( ts - timeStamp )
            if ( dif < smallestDif ):
                smallestDif = dif
                closestFrame = int (row[0] )
            
            # 10/01/2018 08:39:40
            # print( "Row : " + str( row ) )
        
        print( "Closest Frame in selected database is: " + str( closestFrame ) )
        print( "Distance to target: " + str( smallestDif ) + " milliseconds")
    
    
    
    print( "*** ALL JOBS DONE ***")
        
        