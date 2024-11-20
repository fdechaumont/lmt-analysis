'''
Created by Nicolas Torquet at 15/11/2024
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''

import sqlite3
from Animal_LMTtoolkit import *


def findFirstFrameFromTime(file, time):
    '''
    the time must have this format: hh:mm
    for example 14:23
    '''
    startDateXp = getStartInDatetime(file)
    timeConverted = datetime.datetime.strptime(time, '%H:%M').time()
    dateFromTime = datetime.datetime.combine(startDateXp.date(), timeConverted)
    if dateFromTime<startDateXp:
        dateFromTime + datetime.timedelta(days=1)
    numberOfFramesFromStartToTime = ((dateFromTime-startDateXp).days*24*60*60+(dateFromTime-startDateXp).seconds)*30
    return numberOfFramesFromStartToTime


def extractActivityPerAnimalStartEndInput(file, tmin, tmax):
    connection = sqlite3.connect(file)

    pool = AnimalPoolToolkit()
    pool.loadAnimals(connection)

    pool.loadDetection(start=tmin, end=tmax, lightLoad=True)

    connection.close()

    return pool


def getActivitiesFromSeveralFiles(files, startTime, endTime):
    '''
    return a list of pool
    '''
    activityData = []
    for file in files:
        tmin = findFirstFrameFromTime(file, startTime)
        # tmax = findLastFrameFromTime(file, endTime)
        tmax = endTime + tmin
        activityData.append(extractActivityPerAnimalStartEndInput(file, tmin, tmax))
    return (activityData, tmin, tmax)


def getActivityPerTimeBin(AnimalData, timeBin, tmin, tmax):
    print("Get activity for animal "+AnimalData.RFID)
    # print("tmin: "+str(tmin))
    # print("tmax: "+str(tmax))
    # print("timeBin: "+str(timeBin))
    print(AnimalData.getDistancePerBin(binFrameSize=timeBin * oneMinute, minFrame=tmin, maxFrame=tmax))
    return [x / 100 for x in AnimalData.getDistancePerBin(binFrameSize=timeBin * oneMinute, minFrame=tmin, maxFrame=tmax)]


def computeActivityFromStartTimeToEndTimeWithTimebin():
    pass