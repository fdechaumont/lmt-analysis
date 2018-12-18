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
    

from lmtanalysis.TaskLogger import TaskLogger
import sys
import traceback
from lmtanalysis.FileUtil import getFilesToProcess

maxT = 3*oneDay


class FileProcessException(Exception):
    pass

def getScalarProduct( a, b ):

    return a.x * b.x + a.y * b.y;

def isSameSign( a, b ):
    if ( a >= 0 and b >= 0 ):
         return True;
    if ( a < 0 and b < 0 ):
        return True;
    return False;


def process( file ):

    print(file)
    
    chronoFullFile = Chronometer("File " + file )
    
    connection = sqlite3.connect( file )        
        
                        
    try:

        animalPool = None
        
        print("Caching load of animal detection...")
        animalPool = AnimalPool( )
        animalPool.loadAnimals( connection )
        animalPool.loadDetection( start = 0, end = maxT )
        print("Caching load of animal detection done.")

        text_file = open ( "bad orientation.txt", "a")
  
        nb = {}
        totalLen = {}
  
        for animal in animalPool.getAnimalList():
            
            badOrientationTimeLine = EventTimeLine( None, "bad orientation auto" , animal.baseId , None , None , None , loadEvent=False )
            print ("Processing", animal )
            for t in range( 0, maxT ):
                
                orientation = animal.getOrientationVector( t )
                speedVector = animal.getSpeedVector( t )
                speed = animal.getSpeed( t )

                if ( orientation != None and speedVector != None and speed != None ):
                    if ( speed > SPEED_THRESHOLD_HIGH ):
                        
                        scalar = getScalarProduct( orientation , speedVector )
                        
                        if ( scalar > 0 ):
                            badOrientationTimeLine.addPunctualEvent( t )
           
            # we remove small durations event as we cannot be sure they are not artefact, so we keep only events longer than 1s
            badOrientationTimeLine.removeEventsBelowLength( 30 )
            print ( "Total len in frame: " , badOrientationTimeLine.getTotalLength( ) )
            totalLen[animal] = badOrientationTimeLine.getTotalLength( )
            nb[animal] = badOrientationTimeLine.getNbEvent()
            
            badOrientationTimeLine.endRebuildEventTimeLine(connection)

        text_file.write( "{}\t".format( file ) )
        for resKey in totalLen.keys():
            text_file.write( "animal\t{}\tnb\t{}\ttotalLen\t{}\t".format( animal.RFID , nb[resKey], totalLen[resKey] ) )     
        text_file.write( "\n" ) 
        text_file.close()

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
    
    
    '''    
    for file in files:

        
        try:
            process( file )
        except FileProcessException:
            print ( "STOP PROCESSING FILE " + file , file=sys.stderr  )
        
    '''     
    chronoFullBatch.printTimeInS()
    print( "*** ALL JOBS DONE ***")
        
        