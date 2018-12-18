'''
Created on 18 dec. 2018

@author: Fab
'''

import sqlite3
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Measure import oneHour

if __name__ == '__main__':
    
    #ask the user for database to process
    files = getFilesToProcess()
    
    for file in files:
        
        # connect to database
        connection = sqlite3.connect( file )
        
        # create an animalPool, which basically contains your animals
        animalPool = AnimalPool()
        
        # load infos about the animals
        animalPool.loadAnimals( connection )
        
        # load all detection (positions) of all animals for the first hour
        animalPool.loadDetection( start = 0, end = oneHour )
        
        # filter detection by animalSpeed (speed is in centimeters per second)
        animalPool.filterDetectionByInstantSpeed( 30, 70 )
        
        # plot and show trajectory
        animalPool.plotTrajectory( title="Trajectories filtered by speed (between 30 to 70 cm/s) ")

    
    