'''
Created on 24 Septembre 2021

@author: Elodie
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

def process( file ):

    print(file)
    #extract the name of the individual from the name of the file; adjust position!!!
    print('ind name: ', file[46:49])
    ind = str(file[46:49])
    '''print('ind name: ', file[53:56])
    ind = str(file[53:56])'''
        
    
    connection = sqlite3.connect( file )
    
    c = connection.cursor()
    query = "UPDATE ANIMAL SET GENOTYPE = 'WT'";
    c.execute(query)
    query = "UPDATE ANIMAL SET AGE = '3mo'";
    c.execute( query )
    query = "UPDATE ANIMAL SET SEX = 'male'";
    c.execute( query )
    query = "UPDATE ANIMAL SET STRAIN = 'C57BL/6J'";
    c.execute( query )
    query = "UPDATE ANIMAL SET SETUP = '2'";
    c.execute(query)
    query = "UPDATE ANIMAL SET NAME = '{}'".format(ind);
    c.execute(query)

    connection.commit()
    c.close()
    connection.close()

    

def processAll():
    
    
    files = getFilesToProcess()

    chronoFullBatch = Chronometer("Full batch" )    
        
    if ( files != None ):
    
        for file in files:
                print ( "Processing file" , file )
                process( file )
        
    chronoFullBatch.printTimeInS()
    print( "*** ALL JOBS DONE ***")

if __name__ == '__main__':
    
    print("Code launched.")
    processAll()
    