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
            
            plt.figure(  figsize= ( 22,3 ) )

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
            y_pos = []
            for animalNumber in animalPool.animalDictionary:
                print("loading")       
                animal = animalPool.animalDictionary[animalNumber]
                labels.append( animal.RFID[-6:] + " " + animal.genotype )
                onHouseTimeLine = EventTimeLine( connection, "onHouse" , animalNumber )
                y_pos.append( animalNumber )
                
                ys = []
                xs = []
                
                for e in onHouseTimeLine.eventList:
                    ys.append( animalNumber )
                    xs.append( e.startFrame / (30 * 60 * 60 ) )
                
                plt.scatter( xs,ys , c= getAnimalColor( animalNumber ))
                    
            #plt.ylim( 0 , 5 )
            #plt.tight_layout()                
            
            plt.yticks( y_pos , labels)
            plt.ylabel("Animal")
            plt.savefig(file+"_onHouse_timeline.png")
            
            
            
            #plt.show()
            
    chronoFullBatch.printTimeInS()
 
    print("All Done")
                
                
            
            
            