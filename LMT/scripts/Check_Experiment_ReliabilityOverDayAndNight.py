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
from lmtanalysis.EventTimeLineCache import EventTimeLineCached

def computeReliabilityOverSpecificTimePeriods(c, minT, maxT, text_file):    
    ##########################################################################
    '''Compute total recording duration'''
    print ("##############################################################")
    query = f"SELECT MIN(TIMESTAMP) FROM FRAME WHERE FRAMENUMBER >= {minT} AND FRAMENUMBER < {maxT}";
    c.execute( query )
    rows = c.fetchall()
    for row in rows:
        realStartTime = datetime.datetime.fromtimestamp(row[0]/1000)
        realStartInSeconds = row[0]/1000
    
    #return realStartTime
    print( "Time of event start: {}".format(realStartTime) )
    text_file.write ( "Time of event start: {}\n".format(realStartTime) )
    
    query = f"SELECT MAX(TIMESTAMP) FROM FRAME WHERE FRAMENUMBER >= {minT} AND FRAMENUMBER < {maxT}";
    c.execute( query )
    rows = c.fetchall()
    for row in rows:
        realEndTime = datetime.datetime.fromtimestamp(row[0]/1000)
        realEndInSeconds = row[0]/1000
    
    #return realEndTime
    print( "Time of event end: {}".format(realEndTime) )
    text_file.write( "Time of event end: {}\n".format(realEndTime) )
    #Total duration of experiment based on timestamp
    realDurationInSeconds = realEndInSeconds - realStartInSeconds + 1
    print( "Real duration of event: {} s ({} frames)".format( realDurationInSeconds, realDurationInSeconds*30 ) )
    text_file.write( "Real duration of event: {} s ({} frames)\n".format( realDurationInSeconds, realDurationInSeconds*30 ) )
    
    ##########################################################################
    '''Compute the total number of frames recorded'''
    print ("##############################################################")
    query = f"SELECT * FROM FRAME WHERE FRAMENUMBER >= {minT} AND FRAMENUMBER < {maxT}";
    c.execute( query )
    framesRecorded = c.fetchall()
    nbFramesRecorded = len(framesRecorded)
    print ( "Number of frames recorded:  {} frames ({} seconds or {} minutes or {} hours or {} days)".format(nbFramesRecorded, nbFramesRecorded/oneSecond, nbFramesRecorded/oneMinute, nbFramesRecorded/oneHour, nbFramesRecorded/oneDay))
    text_file.write( "Number of frames recorded:  {} frames ({} seconds or {} minutes or {} hours or {} days)\n".format(nbFramesRecorded, nbFramesRecorded/oneSecond, nbFramesRecorded/oneMinute, nbFramesRecorded/oneHour, nbFramesRecorded/oneDay) )
    
    query = f"SELECT MIN(FRAMENUMBER) FROM FRAME WHERE FRAMENUMBER >= {minT} AND FRAMENUMBER < {maxT}";
    c.execute( query )
    minFrames = c.fetchall()
    for minFrame in minFrames:
        startFrame = minFrame[0]
    
    query = f"SELECT MAX(FRAMENUMBER) FROM FRAME WHERE FRAMENUMBER >= {minT} AND FRAMENUMBER < {maxT}";
    c.execute( query )
    maxFrames = c.fetchall()
    for maxFrame in maxFrames:
        endFrame = maxFrame[0]  
    
    durationEvent = endFrame - startFrame +1
    print ("Event duration based on frames: {} frames".format(durationEvent) ) 
    
    nbOmittedFrames = realDurationInSeconds*oneSecond - nbFramesRecorded
    print ( "Number of frames omitted: {} ({} % of the total event duration)".format (nbOmittedFrames, 100*nbOmittedFrames/(realDurationInSeconds*oneSecond)) )
    text_file.write( "Number of frames omitted: {} ({} % of the total event duration)\n".format (nbOmittedFrames, 100*nbOmittedFrames/(realDurationInSeconds*oneSecond)) )
    text_file.write("\n")
    
    print ("##############################################################")
    
    ##########################################################################
    '''Number of animals detected and rate of detection'''
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    pool.loadDetection( start = startFrame, end = endFrame, lightLoad=True)
    print ("##############################################################")
    
    for animal in pool.animalDictionary.keys():
        
        nbOfDetections = pool.animalDictionary[animal].getNumberOfDetection(tmin = startFrame, tmax = endFrame)
        missedDetection = 1-nbOfDetections/nbFramesRecorded
        
        print ( "Animal {}: {} missed detections over {} frames recorded ({} %)".format( pool.animalDictionary[animal].RFID, nbFramesRecorded-nbOfDetections, nbFramesRecorded, missedDetection*100 ) )
        text_file.write( "Animal {}: {} missed detections over {} frames recorded ({} %)\n".format( pool.animalDictionary[animal].RFID, nbFramesRecorded-nbOfDetections, nbFramesRecorded, missedDetection*100 ) )
        '''Note: The score can be low, if the animals are often huddled in the nest and not identified individually.'''
    
    ##########################################################################
    '''Number of RFID match'''
    print ("##############################################################")
    
    for animal in pool.animalDictionary.keys():
        nbOfRfidMatch = rfidMatchTimeLine[animal].getNumberOfEvent(minFrame=startFrame, maxFrame=endFrame)
        nbOfRfidMismatch = rfidMismatchTimeLine[animal].getNumberOfEvent(minFrame=startFrame, maxFrame=endFrame)
        print( "Number of RFID match for animal {}: {} (rate: {} events/min)".format( pool.animalDictionary[animal].RFID, nbOfRfidMatch, nbOfRfidMatch/(durationEvent*30*60) ) )
        print( "Number of RFID mismatch for animal {}: {} (rate: {} events/min)".format( pool.animalDictionary[animal].RFID, nbOfRfidMismatch, nbOfRfidMismatch/(durationEvent*30*60) ) )
        text_file.write( "Number of RFID match for animal {}: {} (rate: {} events/min)\n".format( pool.animalDictionary[animal].RFID, nbOfRfidMatch, nbOfRfidMatch/(durationEvent*30*60) ) )
        text_file.write( "Number of RFID mismatch for animal {}: {} (rate: {} events/min)\n".format( pool.animalDictionary[animal].RFID, nbOfRfidMismatch, nbOfRfidMismatch/(durationEvent*30*60) ) )
        
    print ("##############################################################")
    ##########################################################################
    '''Check events'''
    text_file.write( "\n" )
    text_file.write("Total number of each event type:\n")
    for event in behaviouralEvents:
        eventTimeLine = EventTimeLine( connection, event, minFrame=startFrame, maxFrame=endFrame )
        nbOfEvents = eventTimeLine.getNumberOfEvent(minFrame=startFrame, maxFrame=endFrame)
        text_file.write("{}:\t {}\n".format(event, nbOfEvents))
    
    text_file.write( "\n" )    
    text_file.write( "##############################################################\n" )
    ##########################################################################
        


if __name__ == '__main__':
    '''This script allows to have an overview of the quality of the tracking for days and nights separately.'''
    
    behaviouralEvents = ["Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Social escape", "Approach contact", "Break contact", "FollowZone Isolated", "Train2", "Group2", "Group3", "Group 3 break", "Group 3 make", "Group4", "Group 4 break", "Group 4 make", "Move isolated", "Move in contact", "Rear isolated", "Rear in contact", "Stop isolated"]
    
    files = getFilesToProcess()
    
    for file in files:
        print( file )
        head, tail = os.path.split(file)
        text_file_name = f"{head}/reliability_per_night_day.txt"
        text_file = open ( text_file_name, "w")
        connection = sqlite3.connect( file )
        c = connection.cursor()
        text_file.write( file )
        text_file.write("\n")
        
        #determine end frame of the experiment
        query = "SELECT MAX(FRAMENUMBER) FROM FRAME";
        c.execute( query )
        rows = c.fetchall()
        for row in rows:
            endFrame = row[0]
        print(endFrame)


        pool = AnimalPool( )
        pool.loadAnimals( connection )
        rfidMatchTimeLine = {}
        rfidMismatchTimeLine = {}
        for animal in pool.animalDictionary.keys():
            rfidMatchTimeLine[animal] = EventTimeLine( connection, "RFID MATCH", idA = animal )
            rfidMismatchTimeLine[animal] = EventTimeLine( connection, "RFID MISMATCH", idA = animal )
        
        #upload night timeline
        nightEventTimeLine = EventTimeLineCached( connection, file, "night", minFrame = 0, maxFrame = endFrame )
        n = 1
        for eventNight in nightEventTimeLine.getEventList():
            minT = eventNight.startFrame
            maxT = eventNight.endFrame
            print("Night: ", n)
            text_file.write(f"Computation for night {n} \n")
            computeReliabilityOverSpecificTimePeriods(c, minT, maxT, text_file)
            n += 1
            
        #build day timeline
        dayEventTimeLine = EventTimeLine(connection, "night", minFrame = 0, maxFrame = endFrame, inverseEvent=True)
        d = 1
        for eventDay in dayEventTimeLine.getEventList():
            minT = eventDay.startFrame
            maxT = eventDay.endFrame
            print("Day: ", d)
            text_file.write(f"Computation for day {d} \n")
            computeReliabilityOverSpecificTimePeriods(c, minT, maxT, text_file)
            d += 1
            
    
        text_file.write( "\n" )
        
        text_file.close()
    
    print("job done")