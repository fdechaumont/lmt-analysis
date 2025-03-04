'''
Created by Nicolas Torquet at 18/11/2024
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''


'''
This script computes the activity (distance travelled) of each animal for a given timebin.

Setup :
Transparent cage of 50 x 50 cm with a new sawdust bottom. 
Kinect at 63 cm high from the floor.
'''

import sqlite3
from lmtanalysis.Measure import oneMinute, oneHour
from Util import getDatetimeFromFrame, getNumberOfFrames, getStartInDatetime, getStartTestPhase
from Parameters import getAnimalTypeParameters
from ZoneArena import getZoneCoordinatesFromCornerCoordinatesOpenfieldArea
from lmtanalysis.AnimalType import AnimalType
from Animal_LMTtoolkit import AnimalPoolToolkit
from FileUtil import getFilesToProcess, getJsonFileToProcess
import json
import matplotlib.pyplot as plt
from Event import EventTimeLine
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


def completeDicoFromKey(dico: dict, keyList: list):
    '''
    Recursive function to structure dico from a list of keys
    '''
    dico[keyList[0]] = {}
    if len(keyList[1:]) > 0:
        completeDicoFromKey(dico[keyList[0]], keyList[1:])
    return dico

def completeDicoFromValues(mergedDictPart: dict, inConstructionDict: dict, keywordList: list):
    '''
    Recursive function to structure dico from values of dico and keylist
    '''
    if mergedDictPart[keywordList[0]] not in inConstructionDict:
        inConstructionDict[mergedDictPart[keywordList[0]]] = {}
    if len(keywordList[1:]) > 0:
        completeDicoFromValues(mergedDictPart, inConstructionDict[mergedDictPart[keywordList[0]]], keywordList[1:])
    else:
        inConstructionDict[mergedDictPart[keywordList[0]]][mergedDictPart['rfid']] = mergedDictPart
    return inConstructionDict


def changeStringKeysToIntKeys(dico: dict):
    return {int(key): value for key, value in dico.items()}


def findFirstFrameFromTime(file, time):
    '''
    the time must have this format: hh:mm
    for example 14:23
    '''
    startDateXp = getStartInDatetime(file)
    timeConverted = datetime.strptime(time, '%H:%M').time()
    dateFromTime = datetime.combine(startDateXp.date(), timeConverted)
    if dateFromTime<startDateXp:
        dateFromTime + timedelta(days=1)
    numberOfFramesFromStartToTime = ((dateFromTime-startDateXp).days*24*60*60+(dateFromTime-startDateXp).seconds)*30
    return numberOfFramesFromStartToTime


def mergeDataFromReorganizedDico(resultDict: dict, mergeDict: dict, nbOfLevel: int):
    '''
    Recursive function to merge data by keys
    '''
    if nbOfLevel == 0:
        for animal in resultDict:
            mergeDict[animal] = resultDict[animal]['results']
            if 'tabResult' not in mergeDict:
                mergeDict['tabResult'] = np.array(resultDict[animal]['results'].keys())

    else:
        for key in resultDict.keys():
            if key not in mergeDict.keys():
                mergeDict[key] = {}
            mergeDataFromReorganizedDico(resultDict[key], mergeDict[key], nbOfLevel-1)

    return mergeDict


def convertResultFromJsonIntoExcel(jsonFile):
    '''
    :param jsonFile: result json file from method exportReorganizedResultsToJsonFile of class ActivityExperimentPoolFromStartFrame
    '''
    name = jsonFile.split('.json')[0].split('\\')[-1].split("/")[-1]
    # Get data from json
    with open(jsonFile, "r") as f:
        data = json.load(f)
    ### json structure:
    # treatment
    #   Individu
    #       totalDistance
    #       results
    #           "0": xxxx
    #           "t": yyyy
    #       id
    #       name
    #       rfid
    #       genotype
    #       sex
    #       age
    #       strain
    #       treatment
    for treatment in data:
        for animal in data[treatment]:
            if 'distancePerTimeBin' not in locals():
                distancePerTimeBin = pd.DataFrame(columns=['animal', 'treatment', 'total distance'] + list(
                    range(0, len(data[treatment][animal]['results']))))
            newRow = [animal, treatment, data[treatment][animal]['totalDistance']]
            for key in data[treatment][animal]["results"]:
                newRow.append(data[treatment][animal]["results"][key])
            distancePerTimeBin.loc[len(distancePerTimeBin)] = newRow

    distancePerTimeBin.to_excel(f"{name}.xlsx", index=False, engine='xlsxwriter')


class ActivityExperiment:
    def __init__(self, file, tStartPeriod=1, durationPeriod=24, timebin=10):
        '''
        :param file: path of the experiment file
        :param tStartExperiment: the first frame of the investigated period
        :param durationExperiment: duration in hours of the experiment
        :param timebin: timebin in minutes to compute the distance travelled
        '''
        # global animalType
        self.animalType = animalType
        self.parameters = getAnimalTypeParameters(animalType)
        self.file = file
        # self.activity = {}
        self.totalDistance = {}
        self.results = {}
        self.reorganizedResults = {}
        if ".json" in file:
            self.name = file.split('.json')[0].split('\\')[-1].split("/")[-1]
            # Get data from json
            with open(self.file, "r") as f:
                data = json.load(f)
                self.wholeCageCoordinates = data['metadata']['wholeCageCoordinates']
                self.tStartPeriod = data['metadata']['startFrame']
                self.durationPeriod = data['metadata']['durationExperiment']
                self.timebin = data['metadata']['timeBin']
                self.startDatetime = datetime.strptime(data['metadata']['startDatetime'], "%d/%m/%Y %H:%M:%S.%f")
                self.endDatetime = datetime.strptime(data['metadata']['endDatetime'], "%d/%m/%Y %H:%M:%S.%f")
                self.tStartPeriod = data['metadata']['tStartPeriod']
                self.tStopFramePeriod = data['metadata']['tStopFramePeriod']
                self.durationPeriod = data['metadata']['durationPeriod']
                self.durationPeriodInFrame = data['metadata']['durationPeriodInFrame']
                self.timebinInFrame = data['metadata']['timebinInFrame']
                self.numberOfTimeBin = data['metadata']['numberOfTimeBin']
                self.animals = data['metadata']['animals']
                self.nights = data['metadata']['nights']
                for animal in self.animals:
                    self.totalDistance[animal] = data[animal]['totalDistance']
                    self.results[animal] = data[animal]['results']
                    self.results[animal] = changeStringKeysToIntKeys(self.results[animal])



        else:
            self.tStartPeriod = tStartPeriod   # framenumber
            self.durationPeriod = durationPeriod  # duration in hours
            self.durationPeriodInFrame = round(durationPeriod*oneHour)    # duration in number of frame
            self.tStopFramePeriod = self.tStartPeriod+self.durationPeriodInFrame    # convert in framenumber
            self.timebin = timebin # timebin in minutes
            self.timebinInFrame = timebin*oneMinute # timebin in number of frame

            self.name = file.split('.sqlite')[0].split('\\')[-1].split("/")[-1]
            # Get start datetime and end datetime for metadata
            connection = sqlite3.connect(self.file)
            self.startDatetime = getDatetimeFromFrame(connection, self.tStartPeriod)
            self.endDatetime = getDatetimeFromFrame(connection, self.tStopFramePeriod)
            connection.close()
            if self.endDatetime is None:
                self.tStopFramePeriod = getNumberOfFrames(file)
                connection = sqlite3.connect(self.file)
                self.endDatetime = getDatetimeFromFrame(connection, self.tStopFramePeriod)
                connection.close()
            self.numberOfTimeBin = (self.tStopFramePeriod - self.tStartPeriod) / self.timebinInFrame
            # Get animalPool to compute activity
            self.pool = self.extractActivityPerAnimalStartEndInput()
            self.animals = {}
            for animal in self.pool.animalDictionary:
                print(self.pool.animalDictionary[animal])
                self.animals[self.pool.animalDictionary[animal].RFID] = {
                    'id': self.pool.animalDictionary[animal].baseId,
                    'name': self.pool.animalDictionary[animal].name,
                    'rfid': self.pool.animalDictionary[animal].RFID,
                    'genotype': self.pool.animalDictionary[animal].genotype,
                    'sex': self.pool.animalDictionary[animal].sex,
                    'age': self.pool.animalDictionary[animal].age,
                    'strain': self.pool.animalDictionary[animal].strain,
                    'treatment': self.pool.animalDictionary[animal].treatment
                }

            ''' 
            Cage parameters default to animalType parameters but can be modified
            cage coordinates have this format:
            {'xa': 168, 'xb': 343, 'ya': 120, 'yb': 296}
            '''
            self.wholeCageCoordinates = getZoneCoordinatesFromCornerCoordinatesOpenfieldArea(self.animalType)

            self.nights = []




    def getName(self):
        return self.name

    def setWholeCageCoordinates(self, wholeCageCoordinates):
        '''
        :param wholeCageCoordinates: format like {'xa': 168, 'xb': 343, 'ya': 120, 'yb': 296}
        '''
        self.wholeCageCoordinates = wholeCageCoordinates

    def getWholeCageCoordinates(self):
        return self.wholeCageCoordinates

    def getMetadata(self):
        animalTypeString = str(self.animalType).split('.')[1]
        if self.startDatetime:
            startDatetime = self.startDatetime.strftime("%d/%m/%Y %H:%M:%S.%f")
        else:
            startDatetime = None
        if self.endDatetime:
            endDatetime = self.endDatetime.strftime("%d/%m/%Y %H:%M:%S.%f")
        else:
            endDatetime = None
        metadata = {
            'animalType': animalTypeString,
            'wholeCageCoordinates': self.wholeCageCoordinates,
            'startFrame': self.tStartPeriod,
            'durationExperiment': self.durationPeriod,
            'timeBin': self.timebin,
            'startDatetime': startDatetime,
            'endDatetime': endDatetime,
            'tStartPeriod': self.tStartPeriod,
            'tStopFramePeriod': self.tStopFramePeriod,
            'durationPeriod': self.durationPeriod,
            'durationPeriodInFrame': self.durationPeriodInFrame,
            'timebinInFrame':self.timebinInFrame,
            'numberOfTimeBin': self.numberOfTimeBin,
            'animals': self.animals,
            'nights': self.nights
        }
        return metadata

    def extractActivityPerAnimalStartEndInput(self):
        '''
        Load animals information and detections into an AnimalPool
        '''
        if '.sqlite' in self.file:
            connection = sqlite3.connect(self.file)
            pool = AnimalPoolToolkit()
            pool.loadAnimals(connection)
            pool.loadDetection(start=self.tStartPeriod, end=self.tStopFramePeriod, lightLoad=True)
            connection.close()

            return pool
        else:
            print("Experiment from json: cannot use extractActivityPerAnimalStartEndInput()")
            return False


    def computeActivityPerTimeBin(self):
        if '.sqlite' in self.file:
            activity = {}
            self.totalDistance = {}
            self.results = {}

            print(f"maxFrame: {self.tStopFramePeriod}")

            for animal in self.pool.animalDictionary.keys():
                rfid = self.pool.animalDictionary[animal].RFID
                activity[rfid] = self.pool.animalDictionary[animal].getDistancePerBin(binFrameSize=self.timebinInFrame,
                                                                                 minFrame=self.tStartPeriod, maxFrame=self.tStopFramePeriod)
                self.totalDistance[rfid] = self.pool.animalDictionary[animal].getDistance(tmin=self.tStartPeriod, tmax=self.tStopFramePeriod)

                nTimeBins = len(activity[rfid])
                print(nTimeBins)

                timeLine = [0]
                for t in range(1, nTimeBins):
                    x = timeLine[t - 1] + self.timebin
                    timeLine.append(x)

                self.results[rfid] = {}
                for time, distance in zip(timeLine, activity[rfid]):
                    self.results[rfid][time] = distance

            self.getNightTimeLine()

            return {'totalDistance': self.totalDistance, 'results': self.results}

        else:
            print("Experiment from json: cannot use computeActivityPerTimeBin()")
            return False


    def getAllResults(self):
        return {'metadata': self.getMetadata(), 'totalDistance': self.totalDistance, 'results': self.results}


    def organizeResults(self):
        '''
        Organize the results dict in a new dict organizedResults
        reorganizedResults like
        {
            'metadata': experimentMetaData,
            'rfid': {
                'ID': ID,
                'sex': sex,
                'name': name,
                'genotype': genotype,
                'var1': var1,
                ...
                'totalDistance': totalDistance,
                'results': results
            }
        }
        '''
        self.reorganizedResults = {
            'metadata': self.getMetadata(),
        }

        for rfid in self.results:
            self.reorganizedResults[rfid] = {
                'totalDistance': self.totalDistance[rfid],
                'results': self.results[rfid]
            }
            for key, value in self.animals[rfid].items():
                self.reorganizedResults[rfid][key] = value


    def exportReorganizedResultsToJsonFile(self, nameFile="activityResults"):
        self.organizeResults()
        jsonFile = json.dumps(self.reorganizedResults, indent=4)
        with open(f"{self.name}_{nameFile}.json", "w") as outputFile:
            outputFile.write(jsonFile)

    def convertFrameNumberForTimeBinTimeline(self, frameNumber):
        # axe in minute from the beginning of the period
        return ((frameNumber - self.tStartPeriod)/self.timebinInFrame)*self.timebin

    def getNightTimeLine(self):
        if '.sqlite' in self.file:
            self.nights = []
            connection = sqlite3.connect(self.file)
            nightTimeLineList = []
            nightTimeLine = EventTimeLine(connection, "night")
            nightTimeLineList.append(nightTimeLine)
            connection.close()

            for nightEvent in nightTimeLine.getEventList():
                if nightEvent.startFrame >= self.tStartPeriod and nightEvent.startFrame <= self.tStopFramePeriod:
                    if nightEvent.endFrame >= self.tStopFramePeriod:
                        nightEvent.endFrame = self.tStopFramePeriod

                    self.nights.append(
                            {'startFrame': self.convertFrameNumberForTimeBinTimeline(nightEvent.startFrame),
                             'endFrame': self.convertFrameNumberForTimeBinTimeline(nightEvent.endFrame)})
        else:
            print("Experiment from json: cannot use getNightTimeLine()")
            return False

    def plotNightTimeLine(self):
        ax = plt.gca()
        for nightEvent in self.nights:
            ax.axvspan(nightEvent['startFrame'], nightEvent['endFrame'], alpha=0.1, color='black')
            ax.text(nightEvent['startFrame'] + (nightEvent['endFrame'] - nightEvent['startFrame']) / 2, 100, "dark phase",
                    fontsize=8, ha='center')

    def plotActivity(self):
        if len(self.results) == 0:
            print("No results")
        else:
            fig, ax = plt.subplots(1, 1, figsize=(8, 2))
            ax = plt.gca()  # get current axis
            ax.set_xlabel("time")

            for animal in self.results:
                print("plot: ")
                print(self.results[animal])
                ax.plot(self.results[animal].keys(), self.results[animal].values(), linewidth=0.6, label=f"{animal}: {round(self.totalDistance[animal])}")
            plt.title(self.name)
            ax.legend(loc="upper center")
            self.plotNightTimeLine()

            plt.show()
            fig.savefig(f"activity_{self.name}.pdf")


class ActivityExperimentPool:
    def __init__(self, startTimePeriod, durationPeriod=24, timebin=10):
        '''
        dateStartPeriod: start time (hour and minute) in string format like "14:02"
        durationPeriod: duration in hour of the period from the dateStartPeriod
        timebin: time bin in minutes
        '''
        self.activityExperiments = []
        self.results = {}
        self.mergedResults = {}
        self.reorganizedResultsPerIndividual = {}
        self.reorganizedResults = {}
        self.sexesList = []
        self.genotypeList = []
        self.startTimePeriod = startTimePeriod
        self.durationPeriod = durationPeriod
        self.timebin = timebin
        self.meanResults = {}

    def addActivityExperiment(self, experiment):
        self.activityExperiments.append(experiment)

    def addActivityExperimentWithDialog(self):
        files = getFilesToProcess()
        if (files != None):
            for file in files:
                # create the activity experiment*
                print(file)
                tStartPeriod = findFirstFrameFromTime(file, self.startTimePeriod)
                experiment = ActivityExperiment(file, tStartPeriod=tStartPeriod, durationPeriod=self.durationPeriod, timebin=self.timebin)
                self.addActivityExperiment(experiment)

    def setWholeCageCoordinatesExperimentPool(self, wholeCageCoordinates):
        '''
        :param wholeCageCoordinates: format like {'xa': 168, 'xb': 343, 'ya': 120, 'yb': 296}
        '''
        for experiment in self.activityExperiments:
            experiment.setWholeCageCoordinates(wholeCageCoordinates)


    def computeActivityBatch(self):
        '''
        Compute a batch of activity experiment
        '''
        for experiment in self.activityExperiments:
            self.results[experiment.getName()] = experiment.computeActivityPerTimeBin()
            del experiment.pool
            experiment.exportReorganizedResultsToJsonFile()
            experiment.plotActivity()
        return self.results

    def ExportReorganizedResultsAndPlotActivityBatch(self):
        '''
        Compute a batch of activity experiment
        '''
        for experiment in self.activityExperiments:
            experiment.exportReorganizedResultsToJsonFile()
            experiment.plotActivity()
        return self.results


    def mergeResults(self):
        '''
        Organize the results of the activity experiment
        '''
        if len(self.activityExperiments) == 0:
            print("There is no experiment yet")
        else:
            for experiment in self.activityExperiments:
                self.mergedResults[experiment.getName()] = experiment.reorganizedResults


    def exportResultsSortedBy(self, filters: list):
        '''
        filters: list of filters to sort the results
        Filters could be genotype, sex, treatment, strain or age
        If values for a filter is None in a database, None will be returned as a key in the reorganizedResults
        results have to be merged first
        Return the results sorted by the given filters
        '''
        if len(self.mergedResults) == 0:
            self.mergedResults()

        # check filters
        acceptedFilters = ["genotype", "sex", "age", "strain", "treatment"]
        for filter in filters:
            print(filter)
            if filter not in acceptedFilters:
                print(f"Filter {filter} not accepted")
                return False


        for experiment in self.mergedResults:
            for animal in self.mergedResults[experiment].keys():
                if animal != 'metadata':
                    print(animal)
                    self.reorganizedResults = completeDicoFromValues(self.mergedResults[experiment][animal], self.reorganizedResults, filters)



    def exportReorganizedResultsToJsonFile(self, nameFile="activityResults"):
        jsonFile = json.dumps(self.reorganizedResults, indent=4)
        with open(f"{nameFile}.json", "w") as outputFile:
            outputFile.write(jsonFile)


    def setMeanActivityFromPool(self):
        if len(self.reorganizedResults) == 0:
            print("results need to be organized first")
        else:
            self.meanResults = {}



class ActivityExperimentPoolFromStartFrame(ActivityExperimentPool):
    '''
    Class ActivityExperimentPoolFromStartFrame derived from ActivityExperimentPool
    This class is more appropriate for dyadic experiments
    '''
    def __init__(self, startFrame = 0, durationPeriod=15, timebin=5):
        '''
        startFrame: first frame number
        durationPeriod: duration in minutes of the period from the dateStartPeriod
        timebin: time bin in minutes
        '''
        self.activityExperiments = []
        self.results = {}
        self.mergedResults = {}
        self.reorganizedResultsPerIndividual = {}
        self.reorganizedResults = {}
        self.sexesList = []
        self.genotypeList = []
        self.startFrame = startFrame
        self.durationPeriod = (durationPeriod*oneMinute)/oneHour
        self.timebin = timebin
        self.meanResults = {}

    def addActivityExperimentWithDialog(self):
        files = getFilesToProcess()
        if (files != None):
            for file in files:
                # create the activity experiment*
                print(file)
                print(f"Duration: {self.durationPeriod}")
                if self.startFrame == "pause":
                    connection = sqlite3.connect(file)
                    pool = AnimalPoolToolkit()
                    pool.loadAnimals(connection)
                    self.startFrame = getStartTestPhase(pool)
                    connection.close()
                experiment = ActivityExperiment(file, tStartPeriod=self.startFrame, durationPeriod=self.durationPeriod, timebin=self.timebin)
                self.addActivityExperiment(experiment)




if __name__ == '__main__':

    def setAnimalType( aType ):
        global animalType
        animalType = aType


    ### for test
    ## single experiment
    setAnimalType(AnimalType.MOUSE)

    # file = r"C:\Users\torquetn\Documents\20200909_test_temp_Experiment 3580.sqlite"
    # xp = ActivityExperiment(file, 1, 1, 10)
    # dataManip = xp.computeActivityPerTimeBin()

    ## experiment pool test
    # experimentPool = ActivityExperimentPool("17:00", 48, 10)
    # experimentPool.addActivityExperimentWithDialog()
    # experimentPool.computeActivityBatch()
    # experimentPool.mergeResults()
    # filterList = ["treatment", "sex"]
    # experimentPool.exportResultsSortedBy(filterList)
    # experimentPool.exportReorganizedResultsToJsonFile()

    # experimentPool.organizeResults()
    # experimentPool.exportReorganizedResultsAsTable("nameTableFile")
    # experimentPool.exportReorganizedResultsToJsonFile("nameJsonFile")



    #### Morphine Project
    # experimentPoolHabituation = ActivityExperimentPoolFromStartFrame(0, 15, 5)
    # experimentPoolHabituation.addActivityExperimentWithDialog()
    # experimentPoolHabituation.computeActivityBatch()
    # experimentPoolHabituation.mergeResults()
    # filterList = ["treatment"]
    # experimentPoolHabituation.exportResultsSortedBy(filterList)
    # experimentPoolHabituation.exportReorganizedResultsToJsonFile(nameFile="habituation_session5")
    #
    #
    # experimentPoolInteraction = ActivityExperimentPoolFromStartFrame("pause", 25, 5)
    # experimentPoolInteraction.addActivityExperimentWithDialog()
    # experimentPoolInteraction.computeActivityBatch()
    # experimentPoolInteraction.mergeResults()
    # filterList = ["treatment"]
    # experimentPoolInteraction.exportResultsSortedBy(filterList)
    # experimentPoolInteraction.exportReorganizedResultsToJsonFile(nameFile="interaction_session5")
    #
    # ## Export to excel file
    # jsonFileHabituation = getJsonFileToProcess()
    # convertResultFromJsonIntoExcel(jsonFileHabituation)
    # jsonFileIntraction = getJsonFileToProcess()
    # convertResultFromJsonIntoExcel(jsonFileIntraction)


    ### Morphine -> distance travelled in center of the arena and time spend per timebin (during habituation phase)


