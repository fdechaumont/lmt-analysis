'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis import BuildEventTrain3, BuildEventTrain4, BuildEventFollowZone, BuildEventRear5, BuildEventFloorSniffing,\
    BuildEventSocialApproach, BuildEventSocialEscape, BuildEventApproachContact,\
    BuildEventApproachRear, BuildEventGroup2, BuildEventGroup3, BuildEventGroup4,\
    BuildEventStop, BuildEventWaterPoint

from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import getMinTMaxTAndFileNameInput





if __name__ == '__main__':
    
    print("Code launched.")
    '''
    compute behavioural traits for each individual for two mice (one for the tested strain and one control mouse)
    computation of individual and social traits.
    '''
 
        
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    tmin, tmax, text_file = getMinTMaxTAndFileNameInput()

    
    behaviouralEventOneMouse = ["Nest4"]
    
    
    for file in files:
        
        print(file)
        connection = sqlite3.connect( file )
        
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        
        #pool.loadDetection( start = tmin, end = tmax, lightLoad =True )
        
        for behavEvent in behaviouralEventOneMouse:
            
            print( "computing individual event: {}".format(behavEvent))    
            behavEventTimeLine = EventTimeLine( connection, behavEvent, minFrame=tmin, maxFrame=tmax )
            data =[]        
            for event in behavEventTimeLine.eventList:
                data.append( event.duration() )
            behavEventTimeLine.plotEventDurationDistributionHist(nbBin=3000)
            text_file.write( "{}\t{}\n".format ( file, data ) )
            
    text_file.write( "\n" )
    text_file.close()
                
    print( "FINISHED" )
                
            
            
            