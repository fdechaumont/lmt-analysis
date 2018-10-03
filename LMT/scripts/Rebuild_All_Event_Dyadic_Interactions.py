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
    BuildEventOralSideSequence
    
from tkinter.filedialog import askopenfilename

if __name__ == '__main__':
    
    print("Code launched.")
    
    
    ''' to get a GUI window to select file '''    
    
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    
    max_dur = 3*oneDay
    
    '''oneMinute*240'''
    
    for file in files:
        
        print(file)
        connection = sqlite3.connect( file )        
                
        #continue

    
        BuildDataBaseIndex.buildDataBaseIndex( connection )
    
        BuildEventDetection.reBuildEvent( connection, tmin=0, tmax=max_dur )

        BuildEventOralOralContact.reBuildEvent( connection, tmin=0, tmax=max_dur )        
        BuildEventOralGenitalContact.reBuildEvent( connection, tmin=0, tmax=max_dur )
        
        BuildEventSideBySide.reBuildEvent( connection, tmin=0, tmax=max_dur )        
        BuildEventSideBySideOpposite.reBuildEvent( connection, tmin=0, tmax=max_dur )        

        BuildEventTrain2.reBuildEvent( connection, tmin=0, tmax=max_dur )
                         
        BuildEventMove.reBuildEvent( connection, tmin=0, tmax=max_dur )
        
        BuildEventFollowZone.reBuildEvent( connection, tmin=0, tmax=max_dur )
        BuildEventRear5.reBuildEvent( connection, tmin=0, tmax=max_dur )
        
        BuildEventSocialApproach.reBuildEvent( connection, tmin=0, tmax=max_dur )
        BuildEventSocialEscape.reBuildEvent( connection, tmin=0, tmax=max_dur )
        BuildEventApproachRear.reBuildEvent( connection, tmin=0, tmax=max_dur )
        BuildEventGroup2.reBuildEvent( connection, tmin=0, tmax=max_dur )
       
        BuildEventStop.reBuildEvent( connection, tmin=0, tmax=max_dur )
        BuildEventWaterPoint.reBuildEvent(connection, tmin=0, tmax=max_dur)
        BuildEventApproachContact.reBuildEvent( connection, tmin=0, tmax=max_dur )
        BuildEventWallJump.reBuildEvent(connection, tmin=0, tmax=max_dur)
        BuildEventSAP.reBuildEvent(connection,  tmin=0, tmax=max_dur)

        BuildEventOralSideSequence.reBuildEvent( connection, tmin=0, tmax=max_dur )
       
        
    print( "*** ALL JOBS DONE ***")
        
        