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
    Compute the duration of behavioural events for each combinations of animals
    '''
    #filename = askopenfilename()
    
    print("Code launched.")

    files = askopenfilename( title="Choose a set of file to process", multiple=1 )


    behaviouralEvents = ["Contact", "Oral-oral Contact", "Oral-genital Contact"]
    
    text_file = open ("shank3_long_term_event_duration_bis_night3_0889.txt", "w")
    
    for file in files:
    
        connection = sqlite3.connect( file )
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        
        for behavEvent in behaviouralEvents:
            
            print( "computing {} duration".format(behavEvent))
        
            timeLineList = []
            for idA in range( 1 , 5 ):
                for idB in range( 1 , 5 ):
                    if (idA == idB):
                        continue
                    '''
                    for idC in range( 1, 5 ):
                        if (idC == idA):
                            continue
                        if (idC == idB):
                            continue
                        
                        for idD in range( 1, 5 ):
                            if (idD == idA):
                                continue
                            if (idD == idB):
                                continue
                            if (idD == idC):
                                continue
                        '''
                    timeLine = EventTimeLine( connection, behavEvent, idA, idB, minFrame=52.67*oneHour, maxFrame=63.67*oneHour )
                    timeLineList.append( timeLine )
                                                           
            
            for event in timeLineList:
                eventDuration = event.getTotalLength()/oneSecond
                eventMeanDuration = event.getMeanEventLength()/oneSecond
                
                genoA = None
                try:
                    genoA=pool.animalList[event.idA].genotype
                except:
                    pass
                
                genoB = None
                try:
                    genoB=pool.animalList[event.idB].genotype
                except:
                    pass
                
                genoC = None
                try:
                    genoC=pool.animalList[event.idC].genotype
                except:
                    pass
                
                genoD = None
                try:
                    genoD=pool.animalList[event.idD].genotype
                except:
                    pass
                
                print(event.eventName, genoA, event.idA, genoB, event.idB, genoC, event.idC, genoD, event.idD, eventDuration, eventMeanDuration)
                #print(event.eventName, pool.animalList[event.idA].genotype, event.idA, pool.animalList[event.idB].genotype, event.idB, event.idC, event.idD, eventDuration)
                res = [event.eventName, pool.animalList[event.idA].genotype, event.idA, pool.animalList[event.idB].genotype, event.idB, event.idC, event.idD, eventDuration, eventMeanDuration]
                text_file.write( "{}\t{}\n".format( file, res ) ) 
            
        
    text_file.write( "\n" )
    text_file.close()
    

    
    
    
    