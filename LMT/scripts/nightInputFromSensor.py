

import sqlite3
from lmtanalysis.Animal import *
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from tkinter.filedialog import askopenfilename
import sys
from lmtanalysis.FileUtil import getFilesToProcess


class FileProcessException(Exception):
    pass


def getDateTime(animalPool, frame):
    if frame > 0:

        datetime = getDatetimeFromFrame(animalPool.conn, frame)
        if datetime != None:
            realTime = getDatetimeFromFrame(animalPool.conn, frame).strftime('%d-%m (%b)-%Y %H:%M:%S')
            return realTime
    return None


def process(file):
    connection = sqlite3.connect(file)

    print("--------------")
    print("Current file: ", file)

    nightTimeLine = EventTimeLine(connection, "night", None, None, None, None)
    nightTimeLine.eventList.clear()

    connection = sqlite3.connect(file)
    # build sensor data
    animalPool = AnimalPool()
    animalPool.loadAnimals(connection)
    autoNightList = animalPool.plotSensorData(
        sensor="LIGHTVISIBLEANDIR", minValue=40, saveFile=file + "_log_light visible.pdf", show=True, autoNight=True)

    # show nights

    nightNumber = 1

    if autoNightList == None:
        print("No sensor data found.")
        return

    for autoNight in autoNightList:
        print("Night #", str(nightNumber))
        print("Starts at {} ({})".format( getDateTime(animalPool, autoNight[0]), autoNight[0]))
        print("Ends at {} ({}) ".format( getDateTime(animalPool, autoNight[1]), autoNight[1]))

        nightNumber += 1

    # ask confirmation

    answer = input("Set night(s) with autoNight data ? [y/n]:")
    if answer.lower() == "y":
        print("Setting events...")

        nightTimeLine = EventTimeLine(connection, "night", None, None, None, None)
        nightTimeLine.eventList.clear()

        for autoNight in autoNightList:
            nightTimeLine.addEvent(Event(autoNight[0], autoNight[1]))

        nightTimeLine.endRebuildEventTimeLine(connection, deleteExistingEvent=True)
        print("Setting events... Done")
    else:
        print("autoNight canceled.")


print("Code launched.")

files = getFilesToProcess()

if (files != None):

    for file in files:
        try:
            print("Processing file", file)
            process(file)
        except FileProcessException:
            print("STOP PROCESSING FILE " + file, file=sys.stderr)

print("*** ALL JOBS DONE ***")