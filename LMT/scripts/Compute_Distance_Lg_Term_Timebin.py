'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
import os
from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import getMinTMaxTAndFileNameInput


if __name__ == '__main__':
    
    print("Code launched.")

    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    tmin, tmax, text_file = getMinTMaxTAndFileNameInput()

    '''
    min_dur = 0
    max_dur = 3*oneDay
    text_file = open ("btbr_3days_distance_per_time_bin.txt", "w")
    '''

    
    
    
    for file in files:

        print(file)
        connection = sqlite3.connect( file )
        
        #cursor = connection.cursor()

        pool = AnimalPool( )
        pool.loadAnimals( connection )

        pool.loadDetection( start = tmin, end = tmax, lightLoad=True)

        for animal in pool.animalDictionnary.keys():
            
            print ( pool.animalDictionnary[animal].RFID )

            dt = pool.animalDictionnary[animal].getDistancePerBin(binFrameSize = 20*oneMinute, maxFrame = tmax )
            
            res = [file, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[animal].genotype, pool.animalDictionnary[animal].user1, *dt]
            
            text_file.write( "{}\n".format( res ) ) 
        
           
    
    text_file.write( "\n" )
    text_file.close()
        
    