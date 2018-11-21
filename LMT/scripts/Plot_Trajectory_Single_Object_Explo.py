'''
Created on 21 nov. 2018

@author: Elodie
'''


import matplotlib.pyplot as plt
import numpy as np; np.random.seed(0)
import sqlite3
from database.Animal import *
from tkinter.filedialog import askopenfilename


if __name__ == '__main__':
    
    print("Code launched.")
    
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    '''
    for file in files:
        connection = sqlite3.connect( file )
         
        pool = AnimalPool()
        pool.loadAnimals( connection )
        
        plt.figure( 2, figsize=(13,6) )
        
        #draw the trajectory in the first phase, without the object
        pool.loadDetection( start=0 , end= 28*oneMinute )
        plt.subplot(121)
        pool.animalDictionnary[1].plotTrajectory( show = False, title = "First phase " )
        
        
        #draw the trajectory in the second phase, with the object
        pool.loadDetection( start=32*oneMinute , end= 60*oneMinute )
        plt.subplot(122)
        pool.animalDictionnary[1].plotTrajectory( title = "Second phase " )
        
        plt.show()
    '''
    nbFiles = len(files)
    print(nbFiles)
    plt.figure( 2*nbFiles, figsize=(13,6*nbFiles) )
        
    n = 1
    m = 1
        
    for file in files:
        connection = sqlite3.connect( file )
             
        pool = AnimalPool()
        pool.loadAnimals( connection )
            
        #draw the trajectory in the first phase, without the object
        pool.loadDetection( start=0 , end= 28*oneMinute )
        plt.subplot(n,2,m)
        pool.animalDictionnary[1].plotTrajectory( show = False, title = "First phase " )
            
            
        #draw the trajectory in the second phase, with the object
        pool.loadDetection( start=32*oneMinute , end= 60*oneMinute )
        plt.subplot(n,2,m+1)
        pool.animalDictionnary[1].plotTrajectory( show = False, title = "Second phase " )
           
        n = n+1
        m = m+2
     
    plt.show()    