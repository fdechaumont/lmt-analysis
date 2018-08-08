'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from database.Animal import *
import matplotlib.pyplot as plt
from database.Event import *
from database.Measure import *
from tkinter.filedialog import askopenfilename
from tabulate import tabulate


if __name__ == '__main__':
    ''' 
    Compute the number of frames of the different events used for manual validation of the system
    '''
        
    print("Code launched.")


    files = askopenfilename( title="Choose a set of file to process", multiple=1 )

    
    behaviouralEvents = ["badSegmentation", "badIdentity", "badOrientation", "Detection", "Head detected"]
    
    minTime = 2*oneMinute
    maxTime = minTime + 10*oneMinute
    
    text_file = open ("manual_validation.txt", "w")
    
    for file in files:
    
        print(file)
        
        connection = sqlite3.connect( file )
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        
        for behavEvent in behaviouralEvents:
            
            print( "estimating {} for validation".format(behavEvent))
            behavEventTimeLine = {}
            for idAnimalA in range( 1 , pool.getNbAnimals()+1 ):
            
                behavEventTimeLine[idAnimalA] = EventTimeLine( connection, behavEvent, idAnimalA, minFrame=minTime, maxFrame=maxTime )
                
                event = behavEventTimeLine[idAnimalA]
                
                totalEventDuration = event.getTotalLength()
                meanEventDuration = event.getMeanEventLength()
                maxEventDuration = event.getMaxEventLength()
                minEventDuration = event.getMinEventLength()

                genoA = None
                try:
                    genoA=pool.animalList[idAnimalA].genotype
                except:
                    pass
                
                
                print(event.eventName, genoA, event.idA, minTime, maxTime, totalEventDuration, meanEventDuration, maxEventDuration, minEventDuration)
                
                res = [file, event.eventName, event.idA, genoA, minTime, maxTime, totalEventDuration, meanEventDuration, maxEventDuration, minEventDuration]
                text_file.write( "{}\n".format( res ) ) 
                
        
    text_file.write( "\n" )
    text_file.close()
    

    
    
    
    