'''
Created on 26 avr. 2019

@author: Elodie
'''

import sqlite3
import math
import time
import datetime
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
import os
from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import getMinTMaxTAndFileNameInput, getFileNameInput,\
    getNumberOfFrames
from lmtanalysis.FileUtil import getFilesToProcess



if __name__ == '__main__':
    '''This script allows to have an overview of the quality of the tracking for the whole experiment.'''
    
    behaviouralEvents = ["Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Social escape", "Approach contact", "Approach rear", "Break contact", "Get away", "FollowZone Isolated", "Train2", "Group2", "Group3", "Group 3 break", "Group 3 make", "Group4", "Group 4 break", "Group 4 make", "Huddling", "Move isolated", "Move in contact", "Nest3", "Nest4", "Rearing", "Rear isolated", "Rear in contact", "Stop isolated", "WallJump", "Water Zone", "USV seq"]
    
    files = getFilesToProcess()
    
    text_file = getFileNameInput()
    
    for file in files:
        print( file )
        connection = sqlite3.connect( file )
        c = connection.cursor()
        text_file.write( file )
        text_file.write("\n")
        
        ##########################################################################
        '''Compute total recording duration'''
        print ("##############################################################")
        query = "SELECT MIN(TIMESTAMP) FROM FRAME";
        c.execute( query )
        rows = c.fetchall()
        for row in rows:
            realStartTime = datetime.datetime.fromtimestamp(row[0]/1000)
            realStartInSeconds = row[0]/1000
        
        #return realStartTime
        print( "Time of experiment start: {}".format(realStartTime) )
        text_file.write ( "Time of experiment start: {}\n".format(realStartTime) )
        
        query = "SELECT MAX(TIMESTAMP) FROM FRAME";
        c.execute( query )
        rows = c.fetchall()
        for row in rows:
            realEndTime = datetime.datetime.fromtimestamp(row[0]/1000)
            realEndInSeconds = row[0]/1000
        
        #return realEndTime
        print( "Time of experiment end: {}".format(realEndTime) )
        text_file.write( "Time of experiment end: {}\n".format(realEndTime) )
        #Total duration of experiment based on timestamp
        realDurationInSeconds = realEndInSeconds - realStartInSeconds + 1
        print( "Real duration of experiment: {} s ({} frames)".format( realDurationInSeconds, realDurationInSeconds*30 ) )
        text_file.write( "Real duration of experiment: {} s ({} frames)\n".format( realDurationInSeconds, realDurationInSeconds*30 ) )
        
        ##########################################################################
        '''Compute the total number of frames recorded'''
        #nbFramesRecorded = getNumberOfFrames(file)
        print ("##############################################################")
        query = "SELECT * FROM FRAME";
        c.execute( query )
        framesRecorded = c.fetchall()
        nbFramesRecorded = len(framesRecorded)
        print ( "Number of frames recorded:  {} frames ({} seconds or {} minutes or {} hours or {} days)".format(nbFramesRecorded, nbFramesRecorded/oneSecond, nbFramesRecorded/oneMinute, nbFramesRecorded/oneHour, nbFramesRecorded/oneDay))
        text_file.write( "Number of frames recorded:  {} frames ({} seconds or {} minutes or {} hours or {} days)\n".format(nbFramesRecorded, nbFramesRecorded/oneSecond, nbFramesRecorded/oneMinute, nbFramesRecorded/oneHour, nbFramesRecorded/oneDay) )
        
        query = "SELECT MIN(FRAMENUMBER) FROM FRAME";
        c.execute( query )
        minFrames = c.fetchall()
        for minFrame in minFrames:
            startFrame = minFrame[0]
        
        query = "SELECT MAX(FRAMENUMBER) FROM FRAME";
        c.execute( query )
        maxFrames = c.fetchall()
        for maxFrame in maxFrames:
            endFrame = maxFrame[0]  
        
        durationExp = endFrame - startFrame +1
        print ("Experiment duration based on frames: {} frames".format(durationExp) ) 
        
        nbOmittedFrames = realDurationInSeconds*oneSecond - nbFramesRecorded
        print ( "Number of frames omitted: {} ({} % of the total experiment duration)".format (nbOmittedFrames, 100*nbOmittedFrames/(realDurationInSeconds*oneSecond)) )
        text_file.write( "Number of frames omitted: {} ({} % of the total experiment duration)\n".format (nbOmittedFrames, 100*nbOmittedFrames/(realDurationInSeconds*oneSecond)) )
        text_file.write("\n")
        
        print ("##############################################################")
        ##########################################################################
        '''Number of animals detected and rate of detection'''
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = startFrame, end = endFrame, lightLoad=True)
        print ("##############################################################")
        
        for animal in pool.animalDictionnary.keys():
            
            nbOfDetections = pool.animalDictionnary[animal].getNumberOfDetection(tmin = startFrame, tmax = endFrame)
            missedDetection = 1-nbOfDetections/nbFramesRecorded
            
            print ( "Animal {}: {} missed detections over {} frames recorded ({} %)".format( pool.animalDictionnary[animal].RFID, nbFramesRecorded-nbOfDetections, nbFramesRecorded, missedDetection*100 ) )
            text_file.write( "Animal {}: {} missed detections over {} frames recorded ({} %)\n".format( pool.animalDictionnary[animal].RFID, nbFramesRecorded-nbOfDetections, nbFramesRecorded, missedDetection*100 ) )
            '''Note: The score can be low, if the animals are often huddled in the nest and not identified individually.'''
        
        ##########################################################################
        '''Number of RFID match'''
        print ("##############################################################")
        
        for animal in pool.animalDictionnary.keys():
            rfidMatchTimeLine = EventTimeLine( connection, "RFID MATCH", idA = animal )
            rfidMismatchTimeLine = EventTimeLine( connection, "RFID MISMATCH", idA = animal )
            nbOfRfidMatch = rfidMatchTimeLine.getNumberOfEvent(minFrame=startFrame, maxFrame=endFrame)
            nbOfRfidMismatch = rfidMismatchTimeLine.getNumberOfEvent(minFrame=startFrame, maxFrame=endFrame)
            print( "Number of RFID match for animal {}: {} (rate: {} events/min)".format( pool.animalDictionnary[animal].RFID, nbOfRfidMatch, nbOfRfidMatch/(durationExp*30*60) ) )
            print( "Number of RFID mismatch for animal {}: {} (rate: {} events/min)".format( pool.animalDictionnary[animal].RFID, nbOfRfidMismatch, nbOfRfidMismatch/(durationExp*30*60) ) )
            text_file.write( "Number of RFID match for animal {}: {} (rate: {} events/min)\n".format( pool.animalDictionnary[animal].RFID, nbOfRfidMatch, nbOfRfidMatch/(durationExp*30*60) ) )
            text_file.write( "Number of RFID mismatch for animal {}: {} (rate: {} events/min)\n".format( pool.animalDictionnary[animal].RFID, nbOfRfidMismatch, nbOfRfidMismatch/(durationExp*30*60) ) )
            
        print ("##############################################################")
        ##########################################################################
        '''Check events'''
        text_file.write( "\n" )
        text_file.write("Total number of each event type:\n")
        for event in behaviouralEvents:
            eventTimeLine = EventTimeLine( connection, event )
            nbOfEvents = eventTimeLine.getNumberOfEvent(minFrame=None, maxFrame=None)
            text_file.write("{}:\t {}\n".format(event, nbOfEvents))
        
        text_file.write( "\n" )    
        text_file.write( "##############################################################\n" )
        ##########################################################################
    text_file.write( "\n" )
    
    text_file.close()
    
    print("job done")