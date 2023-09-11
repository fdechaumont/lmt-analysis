'''
Created by Nicolas Torquet at 12/05/2023
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''
import datetime
import sqlite3
from lmtanalysis.Animal import *
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Util import convert_to_d_h_m_s, getMinTMaxTAndFileNameInput
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class FileProcessException(Exception):
    pass

def frameToTimeTicker(x, y):
    hour = x.strftime("%H")
    minute = x.strftime("%M")
    return "{1:02d}:{2:02d}".format(int(hour), int(minute))


def convert_timebin_to_d_h_m_s( x, timeBin ):
    """ x = timebin to convert, timebin in minutes """
    """Return the tuple of days, hours, minutes and seconds."""
    #seconds = frames / 30
    seconds, f = divmod( x*timeBin, 60)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    return days, hours, minutes, seconds, f

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


def findLastFrameFromTime(file, time):
    '''
    the time must have this format: hh:mm
    for example 14:23
    '''
    endDateXp = getEndInDatetime(file)
    timeConverted = datetime.datetime.strptime(time, '%H:%M').time()
    dateFromTime = datetime.datetime.combine(endDateXp.date(), timeConverted)
    if dateFromTime>endDateXp:
        dateFromTime - datetime.timedelta(days=1)
    numberOfFramesFromTimeToEnd = ((endDateXp-dateFromTime).days*24*60*60+(endDateXp-dateFromTime).seconds)*30
    frameNumberOfTheTime = getNumberOfFrames(file)-numberOfFramesFromTimeToEnd
    return frameNumberOfTheTime




def plotNightTimeLine(file):
    print(file)
    connection = sqlite3.connect(file)

    nightTimeLineList = []

    pool = AnimalPool()
    pool.loadAnimals(connection)
    # print( "Event: " + event)
    print("Loading event for file " + file)

    nightTimeLine = EventTimeLine(connection, "night")

    nightTimeLineList.append(nightTimeLine)

    ax = plt.gca()
    for nightEvent in nightTimeLine.getEventList():
        ax.axvspan(nightEvent.startFrame, nightEvent.endFrame, alpha=0.1, color='black')

        ax.text(nightEvent.startFrame + (nightEvent.endFrame - nightEvent.startFrame) / 2, 100, "dark phase",
                fontsize=8, ha='center')



def plotActivityPerAnimalWholeExperiment(file, timeBin):
    print(file)
    connection = sqlite3.connect(file)

    pool = AnimalPool()
    pool.loadAnimals(connection)

    tmin = 0
    tmax = getNumberOfFrames(file)

    pool.loadDetection(start=tmin, end=tmax, lightLoad=True)

    startTime = getStartInDatetime(file)
    endTime = getEndInDatetime(file)

    ''' build the plot '''
    fig, ax = plt.subplots(1, 1, figsize=(8, 2))
    ax = plt.gca()  # get current axis
    ax.set_xlabel("time")
    # ax.set_xlim([0, 7776000])

    # ax.set_ylim([0, 250])

    ''' set x axis '''
    # formatter = matplotlib.ticker.FuncFormatter(frameToTimeTicker)
    # ax.xaxis.set_major_formatter(formatter)
    # ax.tick_params(labelsize=6)
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(30 * 60 * 60 * 12))
    # ax.xaxis.set_minor_locator(ticker.MultipleLocator(30 * 60 * 60))

    dt = {}
    totalDistance = {}

    for animal in pool.animalDictionary.keys():
        print(pool.animalDictionary[animal].RFID)
        dt[animal] = pool.animalDictionary[animal].getDistancePerBin(binFrameSize=timeBin * oneMinute, minFrame=tmin, maxFrame=tmax)
        totalDistance[animal] = pool.animalDictionary[animal].getDistance(tmin=tmin, tmax=tmax)

    nTimeBins = len(dt[1])
    print(nTimeBins)

    abs = [60 * oneMinute]
    for t in range(1, nTimeBins):
        x = abs[t - 1] + timeBin * oneMinute
        abs.append(x)

    for animal in pool.animalDictionary.keys():
        ax.plot(abs, dt[animal], linewidth=0.6)

    # Nights
    cursor = connection.cursor()
    query = 'select * from event where NAME="night"'

    cursor.execute(query)

    rows = cursor.fetchall()
    if len(rows) > 0:
        plotNightTimeLine(file)

    plt.show()

    connection.close()


def extractActivityPerAnimalWholeExperiment(file, timeBin):
    print(file)
    connection = sqlite3.connect(file)

    pool = AnimalPool()
    pool.loadAnimals(connection)

    tmin = 0
    tmax = getNumberOfFrames(file)

    pool.loadDetection(start=tmin, end=tmax, lightLoad=True)

    startTime = getStartInDatetime(file)

    activity = {}
    totalDistance = {}
    results = {}

    for animal in pool.animalDictionary.keys():
        rfid= pool.animalDictionary[animal].RFID
        activity[rfid] = pool.animalDictionary[animal].getDistancePerBin(binFrameSize=timeBin * oneMinute, minFrame=tmin, maxFrame=tmax)
        totalDistance[rfid] = pool.animalDictionary[animal].getDistance(tmin=tmin, tmax=tmax)

        nTimeBins = len(activity[rfid])
        print(nTimeBins)

        timeLine = [0]
        for t in range(1, nTimeBins):
            x = timeLine[t - 1] + timeBin
            timeLine.append(x)

        results[rfid] = {'animal': rfid, 'totalDistance': totalDistance[rfid]}
        for time, distance in zip(timeLine, activity[rfid]):
            results[rfid][f"t{time}"] = distance

    connection.close()

    return {'timeLine': timeLine, 'totalDistance': totalDistance, 'activity':activity, 'startTime': startTime.strftime("%d/%m/%Y %H:%M:%S.%f"), 'results': results}


def extractActivityPerAnimalStartEndInput(file, tmin, tmax):
    connection = sqlite3.connect(file)

    pool = AnimalPool()
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


def orderDataByTreatmentFromListOfPool(listOfPool, tmin, tmax, timeBin):
    '''
    listOfPool: a list of pool containing information about mice and activity data
    return a dico where data are ordered by treatment
    '''
    output = {}
    for animalPool in listOfPool:
        for animal in animalPool.getAnimalDictionary():
            animalData = animalPool.animalDictionary[animal]
            activity = getActivityPerTimeBin(animalData, timeBin, tmin, tmax)
            if animalData.user1 not in output.keys():
                output[animalData.user1] = {
                    animalData.RFID:
                    {
                        'rfid': animalData.RFID,
                        'name': animalData.name,
                        'genotype': animalData.genotype,
                        'age': animalData.age,
                        'sex': animalData.sex,
                        'strain': animalData.strain,
                        'setup': animalData.setup,
                        'treatment': animalData.user1,
                        'activity': activity
                    }
                }
            else:
                output[animalData.user1][animalData.RFID] = {
                        'rfid': animalData.RFID,
                        'name': animalData.name,
                        'genotype': animalData.genotype,
                        'age': animalData.age,
                        'sex': animalData.sex,
                        'strain': animalData.strain,
                        'setup': animalData.setup,
                        'treatment': animalData.user1,
                        'activity': activity
                    }
            print(activity)
            print(animalPool.animalDictionary[animal].user1)
    return output



def fromRawDataToMeanAndSEM(input):
    """
    input: orderDataByTreatmentFromListOfPool output
    return: dico of treatment with mean and sem for each
    """
    output = {}
    preOutput = {}

    for treatment in input.keys():
        tempData = pd.DataFrame()
        output[treatment] = {}
        for animal in input[treatment]:
            print(input[treatment][animal]['rfid'])
            print(input[treatment][animal]['activity'])
            tempData[input[treatment][animal]['rfid']] = input[treatment][animal]['activity']
        preOutput[treatment] = tempData

    for treatment in preOutput:
        output[treatment]['mean'] = preOutput[treatment].mean(axis=1)
        output[treatment]['sem'] = preOutput[treatment].sem(axis=1)

        # To save data into json files
        preOutput[treatment] = preOutput[treatment].to_json()
    with open(f"activity_raw_data.json", 'w') as fp:
        json.dump(preOutput, fp, indent=4)

    return output


def plotActivityFromStartTimeToEndTimeByTreatment(files, startTime, endTime, timeBin, treatmentList):
    ''' Get the data to plot '''
    activityData = getActivitiesFromSeveralFiles(files, startTime, endTime)
    tmin = activityData[1]
    tmax = activityData[2]
    print(tmin)
    print(tmax)
    if tmin > tmax:
        print("problem tmin > tmax")
    dataTemp = orderDataByTreatmentFromListOfPool(activityData[0], tmin, tmax, timeBin)
    dataToPlot = fromRawDataToMeanAndSEM(dataTemp)


    ''' Night events '''
    timeConverted = datetime.datetime.combine(datetime.datetime.now().date(), datetime.datetime.strptime(startTime, '%H:%M').time())
    nightStartTime = datetime.datetime.combine(datetime.datetime.now().date(), datetime.datetime.strptime("19:00", '%H:%M').time())
    nightDurationInTimeBin = 12*60/timeBin

    nightStartInTimeBin = (((nightStartTime - timeConverted).seconds)/60)/timeBin
    nightEndInTimeBin = nightStartInTimeBin + nightDurationInTimeBin

    nightEventTimeLine = []
    # while (nightStartFrame < tmax) and (nightEndFrame < tmax):
    for i in range(0, 3):
        print(f'start {nightStartInTimeBin} to end {nightEndInTimeBin}')
        nightEventTimeLine.append((nightStartInTimeBin, nightEndInTimeBin))
        nightStartInTimeBin += 24*60/timeBin
        nightEndInTimeBin += 24*60/timeBin




    ''' Build the plot '''
    fig, ax = plt.subplots(1, 1, figsize=(8, 2))
    ax = plt.gca()  # get current axis
    ax.set_xlabel("time")
    # ax.set_xlim([0, 7776000])
    # ax.set_ylim([0, 250])

    colorTreatment1 = ["steelblue", "dodgerblue"]
    colorTreatment2 = ["orangered", "darkorange"]
    colorTreatment3 = ["orangered", "darkgreen"]
    colorTreatmentList = ["dodgerblue", "darkorange", "darkgreen"]

    for night in nightEventTimeLine:
        ax.axvspan(night[0], night[1], alpha=0.1, color='black')



    # nTimeBins = len(dt[1])
    # abs = [10 * oneMinute]
    # for t in range(1, nTimeBins):
    #     x = abs[t - 1] + timeBin * oneMinute
    #     abs.append(x)

    j = 0
    for treatment in dataToPlot.keys():
        # for animal in dataToPlot[treatment]:
        ax.plot(range(0, len(dataToPlot[treatment]['mean'])), dataToPlot[treatment]['mean'], color=colorTreatmentList[j], linewidth=0.6, label=treatment)
        plt.fill_between(range(0, len(dataToPlot[treatment]['mean'])), dataToPlot[treatment]['mean']+dataToPlot[treatment]['sem'], dataToPlot[treatment]['mean']-dataToPlot[treatment]['sem'], alpha=0.1)
        plt.legend(loc="upper left")
        nbTimeBin = len(dataToPlot[treatment]['mean'])
        j+=1

    ''' set x axis '''
    ax.set_xlabel("time")
    # print("startTime:" + datetime.datetime.combine(datetime.datetime.now().date(), datetime.datetime.strptime(startTime, '%H:%M').time()).strftime("%H:%M"))
    # # timeAxis = [datetime.datetime.strptime(startTime, '%H:%M').time().strftime("%H:%M")]
    # timeAxis = [datetime.datetime.combine(datetime.datetime.now().date(), datetime.datetime.strptime(startTime, '%H:%M').time())]
    # for bin in range(1, nbTimeBin):
    #     # previousTime = datetime.datetime.strptime(timeAxis[-1], '%H:%M')
    #     previousTime = timeAxis[-1]
    #     # print(timeAxis[-1])
    #     currentTime = previousTime+datetime.timedelta(seconds=60*timeBin)
    #     timeAxis.append(currentTime)
    # formatter = matplotlib.ticker.FuncFormatter(frameToTimeTicker(timeAxis))
    # ax.xaxis.set_major_formatter(formatter)
    # ax.tick_params(labelsize=6)
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(30 * 60 * 60 * 12))
    # ax.xaxis.set_minor_locator(ticker.MultipleLocator(30 * 60 * 60))



    plt.tight_layout()
    plt.savefig( "activity.pdf", dpi=100)
    plt.savefig( "activity.jpg", dpi=300)

    plt.show()


    print('**** End of the process ****')
    return dataToPlot



if __name__ == '__main__':
    print("Code launched.")

    while True:
        question = "Do you want to:"
        question += "\n\t [1] Plot the activity of mice during the whole experiment?"
        question += "\n\t [2] Plot the activity of mice by treatment during from a start time to a end time?"
        question += "\n\t [3] Extract activity data of mice during the whole experiment?"
        question += "\n"
        answer = input(question)

        if answer == '1':
            print("Plot the activity of mice during the whole experiment.")
            files = getFilesToProcess()
            timeBin = int(input("Please enter the time bin in minute"))
            if (files != None):
                for file in files:
                    try:
                        print("Processing file", file)
                        plotActivityPerAnimalWholeExperiment(file, timeBin)
                    except FileProcessException:
                        print("STOP PROCESSING FILE " + file, file=sys.stderr)
            break

        if answer == '2':
            print("Plot the activity of mice during from a start time to a end time?")
            files = getFilesToProcess()
            print("Please enter a start time in this format: hh:mm like 01:06")
            startTime = input()
            # print("Please enter an end time in this format: hh:mm like 01:06")
            # endTime = input()
            print("Please enter the duration of the experiment")
            print("Enter time information in frame. You can also set in days, hour, minutes")
            print("valid entries: 100, 1d, 1.5d, 23.5h, 1d 2h 3m 4s 5f")
            endTime = getFrameInput("Ending t")
            print("Please enter a timebin in minutes")
            timeBin = int(input())
            print("**** Process started ****")
            treatment1 = "control"
            treatment2 = "GFP"
            treatment3 = "scfr"
            treatmentList = [treatment1, treatment2, treatment3]
            results = plotActivityFromStartTimeToEndTimeByTreatment(files, startTime, endTime, timeBin, treatmentList)
            for group in results:
                results[group]['mean'] = results[group]['mean'].to_json()
                results[group]['sem'] = results[group]['sem'].to_json()
                with open(f"activity_{group}_timeBin{timeBin}min.json", 'w') as fp:
                    json.dump(results[group], fp, indent=4)
            break

        if answer == '3':
            print('Extract activity data of mice during the whole experiment')
            files = getFilesToProcess()
            timeBin = int(input("Please enter the time bin in minute"))
            if (files != None):
                for file in files:
                    try:
                        print("Processing file", file)
                        dicoResult = extractActivityPerAnimalWholeExperiment(file, timeBin)
                    except FileProcessException:
                        print("STOP PROCESSING FILE " + file, file=sys.stderr)
            break

