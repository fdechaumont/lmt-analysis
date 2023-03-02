'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *


from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import getMinTMaxTAndFileNameInput
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.FileUtil import getFilesToProcess




if __name__ == '__main__':
    
    print("Code launched.")
 
    files = getFilesToProcess()

    chronoFullBatch = Chronometer("Full batch" )

    if ( files != None ):

        for file in files:
            
            print ( "Processing file" , file )
            connection = sqlite3.connect( file )
            animalPool = AnimalPool( )
            animalPool.loadAnimals( connection )
            currentMinT = 0
            #currentMaxT = 60*oneMinute
            currentMaxT = 3*oneDay
                
            labels = []
            vals = []
            valsNb = []
                    
            for animalNumber in animalPool.animalDictionary:
                onHouseTimeLine = EventTimeLine( connection, "onHouse" , animalNumber )
                
                animal = animalPool.animalDictionary[animalNumber]
                labels.append( animal.RFID[-6:] + " " + animal.genotype )
                vals.append ( onHouseTimeLine.getTotalLength() )
                valsNb.append( onHouseTimeLine.getNumberOfEvent( ) )
        
            plt.figure(  )
            y_pos = np.arange( len( labels ) )
            plt.bar( y_pos , vals )
            plt.xticks( y_pos , labels)
            plt.ylabel("Total duration (frame)")
            plt.savefig(file+"_onHouse_duration.png")
            
            plt.figure(  )
            y_pos = np.arange( len( labels ) )
            plt.bar( y_pos , valsNb )
            plt.xticks( y_pos , labels)
            plt.ylabel("Number of events")
            plt.savefig(file+"_onHouse_nbEvent.png")
            
            
            #plt.show()
            
    chronoFullBatch.printTimeInS()
 
    print("All Done")
                
                
            
            
            