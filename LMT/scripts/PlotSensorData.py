'''
Created on 22 nov. 2019

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *

def process( file ):

    print(file)
        
    connection = sqlite3.connect( file )
    
    # build sensor data
    animalPool = AnimalPool( )
    animalPool.loadAnimals( connection )
    animalPool.buildSensorData(file , show=True )