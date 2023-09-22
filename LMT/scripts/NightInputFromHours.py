'''
Created by Nicolas Torquet at 31/08/2023
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''

import sys

from lmtanalysis.Util import getStartInDatetime, getEndInDatetime, getNumberOfFrames
from lmtanalysis.Event import *
from lmtanalysis.FileUtil import getFilesToProcess
import datetime
from lmtanalysis.TaskLogger import TaskLogger


timeUnit = {
    'frame(s)': 1,
    'second(s)': 30,
    'minute(s)': 30*60,
    'hour(s)': 30*60*60,
    'day(s)': 30*60*60*24,
    'week(s)': 30*60*60*24*7,
}


class FileProcessException(Exception):
    pass


def flush(connection, event='night'):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, event)


def findFrameFromDatetime(file, theDatetime: datetime.datetime):
    """
    Check first if theDatetime is between the start and the end of the experiment: return 'outOfExperiment' if not
    Else, return the clothest FRAMENUMBER from a given datetime
    theDatetime must have a datetime format
    """
    # check if theDatetime between the start and the end of the experiment
    experimentStart = getStartInDatetime(file)
    experimentEnd = getEndInDatetime(file)
    if theDatetime < experimentStart or theDatetime > experimentEnd:
        print(f"{theDatetime} out of the experiment")
        return 'outOfExperiment'
    else:
        connection = sqlite3.connect(file)
        c = connection.cursor()
        theTimestamp = theDatetime.timestamp()*1000
        print("Searching closest frame in database....")

        query = f"SELECT FRAMENUMBER, TIMESTAMP FROM FRAME WHERE TIMESTAMP>{theTimestamp - 10000} AND TIMESTAMP<{theTimestamp + 10000}"
        c.execute(query)
        all_rows = c.fetchall()

        closestFrame = 0
        smallestDif = 100000000

        for row in all_rows:
            ts = int(row[1])
            dif = abs(ts - theTimestamp)
            if dif < smallestDif:
                smallestDif = dif
                closestFrame = int(row[0])

        connection.close()

        print("Closest Frame in selected database is: " + str(closestFrame))
        print("Distance to target: " + str(smallestDif) + " milliseconds")
        return closestFrame





def buildNightEvent(file, nightStartHour, nightEndHour):
    '''
    Rebuild night events from start time and end time (datete.time format)
    '''
    connection = sqlite3.connect(file)

    print("--------------")
    print("Current file: ", file)
    print("Flush")
    flush(connection)

    print("--------------")
    print("Loading existing events...")
    nightTimeLine = EventTimeLine(connection, "night", None, None, None, None, loadEvent=False)

    print("--------------")
    print("Event list:")
    for event in nightTimeLine.eventList:
        print(event)
    print("--------------")

    startTimeOfTheExperiment = getStartInDatetime(file)
    endTimeOfTheExperiment = getEndInDatetime(file)
    experimentTotalNumberOfFrame = getNumberOfFrames(file)

    dateStart = startTimeOfTheExperiment.date()
    # timeFromStartXpToNight = datetime.datetime.combine(dateStart, nightStartHour) - startTimeOfTheExperiment

    tempTimeStartNight = datetime.datetime.combine(dateStart, nightStartHour)
    tempTimeEndNight = datetime.datetime.combine(dateStart, nightEndHour)

    # check night period (during natural night or during day period)
    typicalCircadianRythm = tempTimeStartNight > tempTimeEndNight
    if typicalCircadianRythm:
        tempTimeEndNight = tempTimeEndNight+datetime.timedelta(days=1)
    nightDuration = tempTimeEndNight - tempTimeStartNight
    nightDurationInFrame = nightDuration.seconds*30
    timeBetweenTwoNightInFrame = timeUnit['day(s)']-nightDurationInFrame

    # experience started during light or night period
    if startTimeOfTheExperiment > tempTimeStartNight and startTimeOfTheExperiment < tempTimeEndNight:
        # experiment started during night period: startTimeOfTheExperiment is the first time for the night
        tempStartNightFrame = 0
    else:
        # experiment started during light period: tempTimeStartNight is the first time for the night
        # tempStartNightFrame = (tempTimeStartNight-startTimeOfTheExperiment).seconds*30
        tempStartNightFrame = findFrameFromDatetime(file, tempTimeStartNight)
        if tempStartNightFrame > experimentTotalNumberOfFrame:
            print(f"{file}: there is no night in this experiment")
            return 'no night'

    # tempEndNightFrame = tempStartNightFrame + nightDurationInFrame
    tempEndNightFrame = findFrameFromDatetime(file, tempTimeEndNight)

    while tempStartNightFrame < experimentTotalNumberOfFrame:
        if tempEndNightFrame > experimentTotalNumberOfFrame:
            tempEndNightFrame = experimentTotalNumberOfFrame
        nightTimeLine.addEvent(Event(tempStartNightFrame, tempEndNightFrame))
        # tempStartNightFrame = tempStartNightFrame + nightDurationInFrame + timeBetweenTwoNightInFrame
        # tempEndNightFrame = tempStartNightFrame + nightDurationInFrame
        tempTimeStartNight = tempTimeStartNight + + datetime.timedelta(days=1)
        tempTimeEndNight = tempTimeEndNight + datetime.timedelta(days=1)
        tempStartNightFrame = findFrameFromDatetime(file, tempTimeStartNight)
        tempEndNightFrame = findFrameFromDatetime(file, tempTimeEndNight)
        if tempEndNightFrame == 'outOfExperiment':
            tempEndNightFrame = experimentTotalNumberOfFrame
        if tempStartNightFrame == 'outOfExperiment':
            break


    nightTimeLine.endRebuildEventTimeLine(connection)
    print(nightTimeLine.getNumberOfEvent())
    t = TaskLogger(connection)
    t.addLog("Build Event Night", tmin=0, tmax=experimentTotalNumberOfFrame)

    connection.close()
    print(f"{file}: night events built")




if __name__ == '__main__':
    print("Code launched.")

    files = getFilesToProcess()
    startHour = input("Please enter the hour of the start of the night in this format: hh:mm")
    endHour = input("Please enter the hour of the end of the night in this format: hh:mm")

    startTimeNight = datetime.time(hour=int(startHour.split(':')[0]), minute=int(startHour.split(':')[1]))
    endTimeNight = datetime.time(hour=int(endHour.split(':')[0]), minute=int(endHour.split(':')[1]))

    # nightDuration = datetime.datetime.strptime(startHour, '%H:%M') - datetime.datetime.strptime(endHour, '%H:%M')

    chronoFullBatch = Chronometer("Full batch")


    if (files != None):
        for file in files:
            try:
                print("Processing file", file)
                buildNightEvent(file, startTimeNight, endTimeNight)
            except FileProcessException:
                print("STOP PROCESSING FILE " + file, file=sys.stderr)

    print("*** ALL JOBS DONE ***")
