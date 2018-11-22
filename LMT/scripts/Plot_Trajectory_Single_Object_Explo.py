'''
Created on 21 nov. 2018

@author: Elodie
'''


import matplotlib.pyplot as plt
import numpy as np; np.random.seed(0)
import sqlite3
from database.Animal import *
from tkinter.filedialog import askopenfilename

def plot( ax , animal, title ):
    xList, yList = animal.getTrajectoryData( )
            
    ax.plot( xList, yList, color=animal.getColor(), linestyle='-', linewidth=1, alpha=0.5, label= animal.name )
    ax.set_title( title + " " + animal.RFID )
    ax.legend().set_visible(False)
    #ax.xlim(90, 420)
    #ax.ylim(-370, -40)

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
    '''
    
    nbFiles = len(files)
    print(nbFiles)
    fig, axes = plt.subplots( nrows = nbFiles, ncols = 2, figsize = (13,6*nbFiles) )

    n = 0
        
    for file in files:
        connection = sqlite3.connect( file )
             
        pool = AnimalPool()
        pool.loadAnimals( connection )
            
        #draw the trajectory in the first phase, without the object
        pool.loadDetection( start=0 , end= 28*oneMinute )
        
        plot ( axes[n,0], pool.animalDictionnary[1] , title = "First phase" )
        #pool.animalDictionnary[1].plotTrajectory( show = False, title = "First phase " )
        #axes[n,0].legend().set_visible(False)
        
        #add the frames where the animal is in SAP
        sapDico = pool.animalDictionnary[1].getSapDictionnary()
        print(sapDico)
        #for (i in sapDico.key()):
              
            
        #draw the trajectory in the second phase, with the object
        pool.loadDetection( start=32*oneMinute , end= 60*oneMinute )
        #axes[n,1]
        #pool.animalDictionnary[1].plotTrajectory( show = False, title = "Second phase " )
        plot ( axes[n,1], pool.animalDictionnary[1] , title = "Second phase" )
        #axes[n,1].legend().set_visible(False)
           
        n = n+1
    
    fig.suptitle('Single object exploration', fontsize=14, fontweight='bold') 
    plt.show()
    #fig.savefig('single_obj_explo.pdf', transparent=False, dpi=80, bbox_inches="tight")     
       