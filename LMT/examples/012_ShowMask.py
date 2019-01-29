'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3

from lmtanalysis.Animal import AnimalPool
from lmtanalysis.FileUtil import getFilesToProcess

def process( file ):

    print ("**********************")
    print(file)
    print ("**********************")
    connection = sqlite3.connect( file )        
        
    animalPool = AnimalPool( )
    animalPool.loadAnimals( connection )
    
    # show the mask of animals at frame 300
    animalPool.showMask( 300 )
          

if __name__ == '__main__':
    
    print("Code launched.")
     
    files = getFilesToProcess()
    
    for file in files:

        process( file )
        
    print( "*** ALL JOBS DONE ***")

            
        