'''
Created on 8 janv. 2025

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis import BuildEventTrain3, BuildEventTrain4, BuildEventFollowZone, BuildEventRear5, BuildEventFloorSniffing,\
    BuildEventSocialApproach, BuildEventSocialEscape, BuildEventApproachContact,\
    BuildEventApproachRear, BuildEventGroup2, BuildEventGroup3, BuildEventGroup4,\
    BuildEventStop, BuildEventWaterPoint

from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import getMinTMaxTAndFileNameInput, level
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.FileUtil import getFilesToProcess, addJitter
from scipy.stats import mannwhitneyu
import pandas as pd


def computeMatrixFile( file ):
    
    print( f"computing file {file}" )
        
        
    # pour Gaetano
    
    connection = sqlite3.connect(file)



    pool = AnimalPool()
    pool.loadAnimals(connection)
    
    behaviorList = ["Contact", "Break contact", "Approach contact"]
        
    result = {} 
    
    animalList = pool.getAnimalList()
    
    animalInfoDic = {}
    for animal in animalList:
        animalInfoDic[animal.RFID] = { "baseId": animal.baseId, "genotype": animal.genotype }
                
    result["animals"] = animalInfoDic
    
    
    # compute matrices
    
    for eventName in behaviorList:
        for animalA in animalList:
            for animalB in animalList:
                
                behaviorEventTimeLine = EventTimeLineCached( connection, file, eventName, idA = animalA.baseId, idB = animalB.baseId )
                
                nbEvent = behaviorEventTimeLine.getNbEvent()
                duration = behaviorEventTimeLine.getTotalLength()
                meanDuration = behaviorEventTimeLine.getMeanEventLength()
                
                result[ eventName, "nbEvent", animalA.RFID, animalB.RFID ] = nbEvent
                result[ eventName, "duration", animalA.RFID, animalB.RFID ] = duration
                result[ eventName, "meanDuration", animalA.RFID, animalB.RFID ] = meanDuration
                
                
                
    return result
                
    

def computeMatrix( files ):
    
    resultDic = {}
    
    for file in files:
                
        resultDic[file] = computeMatrixFile( file )

    import json
    with open( "data.json", 'w') as fp:
        json.dump( resultDic , fp, indent=4)

if __name__ == '__main__':


    files = getFilesToProcess()
    computeMatrix(files)
    
    
    