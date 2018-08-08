'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from database.Animal import *
import matplotlib.pyplot as plt
from database.Event import *
from database.Measure import *
import os
from tkinter.filedialog import askopenfilename


if __name__ == '__main__':
    
    print("Code launched.")

    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    
    min_dur = 0
    max_dur = 3*oneDay
    text_file = open ("btbr_3days_distance_per_time_bin.txt", "w")

    
    resultDistance= []
    
    for file in files:

        print(file)
        connection = sqlite3.connect( file )
        
        #cursor = connection.cursor()

        pool = AnimalPool( )
        pool.loadAnimals( connection )

        pool.loadDetection( start = min_dur, end = max_dur)

        for animal in pool.animalDictionnary.keys():
            
            print ( pool.animalDictionnary[animal].RFID )

            dt = pool.animalDictionnary[animal].getDistancePerBin(binFrameSize = 20*oneMinute, maxFrame = max_dur)
            
            res = [file, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[animal].genotype, pool.animalDictionnary[animal].user1, *dt]
            resultDistance.append(res)
            text_file.write( "{}\n".format( res ) ) 

        
        #print(resultDistance)
        
   
    
    text_file.write( "\n" )
    text_file.close()
        
    