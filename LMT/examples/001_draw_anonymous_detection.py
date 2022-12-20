'''
Created on 18 dec. 2018

@author: Fab
'''

import sqlite3
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Measure import oneHour, oneMinute
import matplotlib.pyplot as plt

if __name__ == '__main__':
    
    
    #ask the user for database to process
    files = getFilesToProcess()
    
    for file in files:
        
        print( file )
        
        # connect to database
        connection = sqlite3.connect( file )
        
        # create an animalPool, which basically contains your animals
        animalPool = AnimalPool()
         
        # load infos about the animals
        animalPool.loadAnimals( connection )
        
        start = 0
        end = 10*oneMinute
        
        # load all detection (positions) of all animals for the first hour
        animalPool.loadAnonymousDetection( start = start, end = end )
        
        
        # get all points
        
        xList = []
        yList = []
        
        for t in range( start, end ):
            if t in animalPool.anonymousDetection:
                detections = animalPool.anonymousDetection[t]
                for d in detections:
                    xList.append( d.massX )
                    yList.append( -d.massY )
            
           
        fig, ax = plt.subplots( nrows = 1 , ncols = 1 , figsize=( 4, 1*4 ) , sharex='all', sharey='all'  )
        ax.scatter( xList, yList, color= "black" , s=1 , linewidth=1, alpha=0.05 )
        ax.set_xlim(90, 420)
        ax.set_ylim(-370, -40)
            
        plt.show()
        # plot and show trajectory
        #animalPool.plotTrajectory()

    
    
    