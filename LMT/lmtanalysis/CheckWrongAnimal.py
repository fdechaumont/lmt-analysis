'''
Created on 6 sept. 2017

@author: Fab

In some record, we do have an extra animal with None for all parameters.
This script should be used to detect those animal in databases.

'''
import sqlite3
from time import *

from lmtanalysis.Animal import *
from lmtanalysis.Detection import *
from lmtanalysis.Measure import *
import matplotlib.pyplot as plt
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.Chronometer import Chronometer


def check( connection, tmin=None, tmax=None ): 
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )

    '''
    get the number of expected animals
    '''
    
    nbAnimals = pool.getNbAnimals()
    print("nb animals: " , nbAnimals )
    for animal in pool.getAnimalList():
        if ( animal.name == None ):
            print( "!!!! None animal detected with lmtanalysis id: " , animal.baseId ) 
    
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Correct wrong animal" , tmin=tmin, tmax=tmax )

       
    print( "Rebuild event finished." )
        
    