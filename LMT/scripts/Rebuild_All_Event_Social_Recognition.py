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
    BuildEventOralSideSequence
    
from tkinter.filedialog import askopenfilename

if __name__ == '__main__':
    
    print("Code launched.")
    

    
    ''' to get a GUI window to select file '''    
    
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    #files = [ "c:/testbase/valid4.sqlite" ]    
    
    maxT = 3*oneMinute
    
    '''oneMinute*240'''
    
    for file in files:
        
        print(file)
        connection = sqlite3.connect( file )        
                
        #continue

        '''
        working
        '''

        BuildDataBaseIndex.buildDataBaseIndex( connection )
    
        BuildEventDetection.reBuildEvent( connection, tmin=0, tmax=maxT )

        BuildEventOralOralContact.reBuildEvent( connection, tmin=0, tmax=maxT )        
        BuildEventOralGenitalContact.reBuildEvent( connection, tmin=0, tmax=maxT )
        
        BuildEventSideBySide.reBuildEvent( connection, tmin=0, tmax=maxT )        
        BuildEventSideBySideOpposite.reBuildEvent( connection, tmin=0, tmax=maxT )        

        BuildEventTrain2.reBuildEvent( connection, tmin=0, tmax=maxT )
        BuildEventTrain3.reBuildEvent( connection, tmin=0, tmax=maxT )   

                 
        BuildEventMove.reBuildEvent( connection, tmin=0, tmax=maxT )
           

        BuildEventRear5.reBuildEvent( connection, tmin=0, tmax=maxT )
        
        BuildEventSocialApproach.reBuildEvent( connection, tmin=0, tmax=maxT )
        BuildEventSocialEscape.reBuildEvent( connection, tmin=0, tmax=maxT )
        BuildEventApproachRear.reBuildEvent( connection, tmin=0, tmax=maxT )
        BuildEventGroup2.reBuildEvent( connection, tmin=0, tmax=maxT )
        BuildEventGroup3.reBuildEvent( connection, tmin=0, tmax=maxT )

        BuildEventGroup3MakeBreak.reBuildEvent( connection, tmin=0, tmax=maxT )

        BuildEventStop.reBuildEvent( connection, tmin=0, tmax=maxT )

        BuildEventApproachContact.reBuildEvent( connection, tmin=0, tmax=maxT )
        BuildEventWallJump.reBuildEvent(connection, tmin=0, tmax=maxT)
        BuildEventSAP.reBuildEvent(connection,  tmin=0, tmax=maxT)

        BuildEventOralSideSequence.reBuildEvent( connection, tmin=0, tmax=maxT )

             
    print( "*** ALL JOBS DONE ***")
        
        