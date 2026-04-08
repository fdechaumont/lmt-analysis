'''
Created on 8 janv. 2025

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *

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
import json
from scripts.contactMatrix.XlsOut import XlsOut


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
                
                result[ f"{eventName} nbEvent {animalA.RFID} {animalB.RFID}" ] = nbEvent
                result[ f"{eventName} duration {animalA.RFID} {animalB.RFID}" ] = duration
                result[ f"{eventName} meanDuration {animalA.RFID} {animalB.RFID}" ] = meanDuration
                
    return result
                
    

def computeMatrix( files ):
    
    # compute and save matrices
    
    for file in files:
                
        
                
        resultDic = computeMatrixFile( file )

        with open( f"{file}.json", 'w') as fp:
            json.dump( resultDic , fp, indent=4)

def extractData( xlsOut, result ):
    # matrix view
    
    
    
    animalDic = result["animals"]
    print( animalDic )
    
    behaviorList = ["Contact", "Break contact", "Approach contact"]
    
    animalList = list( animalDic.keys() )    

    dataTypes = ["nbEvent" , "duration" , "meanDuration"]

    for eventName in behaviorList:

        
        for dataType in dataTypes:
        
            xlsOut.addLine( [ "event", dataType, eventName ] )            
            
            names= [""]
            for animalB in animalList:
                names.append( f"{animalB}/{animalDic[animalB]['genotype']}"  )
            xlsOut.addLine( names )
                
            for animalA in animalList:
                line = [ f"{animalA}/{animalDic[animalA]['genotype']}" ]
                for animalB in animalList:
                    
                    value = result[ f"{eventName} {dataType} {animalA} {animalB}" ]
                    line.append( value )
                xlsOut.addLine( line )
            
            xlsOut.insertLine()
                
    xlsOut.insertLine()
                 

def extractDataInRow( xlsOut, result, file ):
    
    # row view
    
    '''
    id1 rfid
    geno
    id2 rfid
    geno
    
    dpi
    gr
    nightnb
    '''
    
    
    
    animalDic = result["animals"]
    print( animalDic )
    
    behaviorList = ["Contact", "Break contact", "Approach contact"]
    
    animalList = list( animalDic.keys() )    

    dataTypes = ["nbEvent" , "duration" , "meanDuration"]
    
    dpi = "no dpi found"
    gr = "no gr found"
    nightnb= "no night nb found"
    
    strList = str(file).split(" ")
    for s in strList:
        if s.startswith("J"):
            dpi = s[1:]
        
        if "gr" in s and len(s)==3:
            gr = s[-1]
            
        if "ni.sqlite" in s:
            nightnb = s[0]
            
    xlsOut.insertLine()

    # labels
    
    row = []
    row.append("")
    row.append("")
    row.append("")
    row.append("")
    
    row.append( "dpi")
    row.append( "gr")
    row.append( "nightNb")
    row.append( "file name")
    
    for eventName in behaviorList:
        for dataType in dataTypes:                    
            row.append( f"{eventName} {dataType}" )
    xlsOut.addLine( row )
    print( row )

    # data
    for animalA in animalList:
                
        for animalB in animalList:
            if animalA == animalB:
                continue
            
            row = []                    
            
            row.append( animalA )
            row.append( animalDic[animalA]['genotype'] )

            row.append( animalB )
            row.append( animalDic[animalB]['genotype'] )
    
            row.append( dpi )
            row.append( gr )
            row.append( nightnb )
            row.append( file.name)
    
            for eventName in behaviorList:
                for dataType in dataTypes:
                    value = result[ f"{eventName} {dataType} {animalA} {animalB}" ]
                    row.append( value )
    
            value = result[ f"{eventName} {dataType} {animalA} {animalB}" ]
        
            xlsOut.addLine( row )
            print( row )

    '''
    for eventName in behaviorList:

        
        for dataType in dataTypes:
        
            xlsOut.addLine( [ "event", dataType, eventName ] )            
            
            names= [""]
            for animalB in animalList:
                names.append( f"{animalB}/{animalDic[animalB]['genotype']}"  )
            xlsOut.addLine( names )
                
            for animalA in animalList:
                line = [ f"{animalA}/{animalDic[animalA]['genotype']}" ]
                for animalB in animalList:
                    
                    value = result[ f"{eventName} {dataType} {animalA} {animalB}" ]
                    line.append( value )
                xlsOut.addLine( line )
            
            xlsOut.insertLine()
            
                
    
    '''
                 


    
    
    '''
    duration = result[ f"{eventName} duration {animalA.RFID} {animalB.RFID}" ] 
    meanDuration = result[ f"{eventName} meanDuration {animalA.RFID} {animalB.RFID}" ]
    '''
                
    
    
    
    
    
    
    

def computeMatrixResult(files):
        

    xlsOut = XlsOut("output.xlsx")
    
    xlsOut.addLine( [ "read order is col animal doing something to row animal" ] )
    xlsOut.insertLine()
    
    for file in files:
                
        xlsOut.insertLine()
        xlsOut.addLine( [ "file", file ] )
        xlsOut.insertLine()
        
        with open( f"{file}.json" , 'r') as file:
            print( "loading " , file )
            data = json.load(  file )   
             
            extractDataInRow( xlsOut , data, file )
             
        
        '''
        resultDic = computeMatrixFile( file )

        with open( f"{file}.json", 'w') as fp:
            json.dump( resultDic , fp, indent=4)
        '''
    xlsOut.close()
    
    

if __name__ == '__main__':

    print("1. process")
    print("2. extract")
    a = input("command: ")
    
    if "1" in a:
        files = getFilesToProcess()
        computeMatrix(files)
        
    if "2" in a:
        files = getFilesToProcess()
        computeMatrixResult(files)
    
    
    