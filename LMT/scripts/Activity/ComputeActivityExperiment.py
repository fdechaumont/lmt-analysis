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
from Util import getDatetimeFromFrame
from Parameters import getAnimalTypeParameters
from ZoneArena import getZoneCoordinatesFromCornerCoordinatesOpenfieldArea
from lmtanalysis.AnimalType import AnimalType
from Animal_LMTtoolkit import AnimalPoolToolkit
from FileUtil import getFilesToProcess
import json


class ActivityExperiment:
    def __init__(self, file, tStartPeriod=1, durationPeriod=24, timebin=10):
        '''
        :param file: path of the experiment file
        :param animalType: the animalType to get animalType's parameters
        :param tStartExperiment: the first frame of the investigated period
        :param durationExperiment: duration in hours of the experiment
        :param timebin: timebin in minutes to compute the distance travelled
        '''
        # global animalType
        self.file = file
        self.name = file.split('.sqlite')[0].split('\\')[-1].split("/")[-1]
        self.animalType = animalType
        self.tStartPeriod = tStartPeriod   # framenumber
        self.durationPeriod = durationPeriod*oneHour  # duration in number of frame
        self.tStopFramePeriod = self.tStartPeriod+self.durationPeriod    # convert in framenumber
        self.durationPeriod = durationPeriod    # duration in hours
        self.durationPeriodInFrame = durationPeriod*oneMinute    # duration in number of frame
        self.timebin = timebin # timebin in minutes
        self.timebinInFrame = timebin*oneMinute # timebin in number of frame
        # Get start datetime and end datetime for metadata
        connection = sqlite3.connect(self.file)
        self.startDatetime = getDatetimeFromFrame(connection, self.tStartPeriod)
        self.endDatetime = getDatetimeFromFrame(connection, self.tStopFramePeriod)
        connection.close()
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
        self.parameters = getAnimalTypeParameters(animalType)
        self.wholeCageCoordinates = getZoneCoordinatesFromCornerCoordinatesOpenfieldArea(self.animalType)

        self.activity = {}
        self.totalDistance = {}
        self.results = {}
        self.reorganizedResults = {}


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
        metadata = {
            'animalType': animalTypeString,
            'wholeCageCoordinates': self.wholeCageCoordinates,
            'startFrame': self.tStartPeriod,
            'durationExperiment': self.durationPeriod,
            'timeBin': self.timebin,
            # 'animals': self.animals,
            'startDatetime': self.startDatetime.strftime("%d/%m/%Y %H:%M:%S.%f"),
            'endDatetime': self.endDatetime.strftime("%d/%m/%Y %H:%M:%S.%f")
        }
        return metadata

    def extractActivityPerAnimalStartEndInput(self):
        '''
        Load animals information and detections into an AnimalPool
        '''
        connection = sqlite3.connect(self.file)
        pool = AnimalPoolToolkit()
        pool.loadAnimals(connection)
        pool.loadDetection(start=self.tStartPeriod, end=self.tStopFramePeriod, lightLoad=True)
        connection.close()

        return pool


    def computeActivityPerTimeBin(self):
        self.activity = {}
        self.totalDistance = {}
        self.results = {}

        for animal in self.pool.animalDictionary.keys():
            rfid = self.pool.animalDictionary[animal].RFID
            self.activity[rfid] = self.pool.animalDictionary[animal].getDistancePerBin(binFrameSize=self.timebinInFrame,
                                                                             minFrame=self.tStartPeriod, maxFrame=self.tStopFramePeriod)
            self.totalDistance[rfid] = self.pool.animalDictionary[animal].getDistance(tmin=self.tStartPeriod, tmax=self.tStopFramePeriod)

            nTimeBins = len(self.activity[rfid])
            print(nTimeBins)

            timeLine = [0]
            for t in range(1, nTimeBins):
                x = timeLine[t - 1] + self.timebin
                timeLine.append(x)

            self.results[rfid] = {'animal': rfid, 'totalDistance': self.totalDistance[rfid]}
            for time, distance in zip(timeLine, self.activity[rfid]):
                self.results[rfid][f"t{time}"] = distance


        return {'totalDistance': self.totalDistance, 'activity': self.activity, 'results': self.results}


    def getAllResults(self):
        return {'metadata': self.getMetadata(), 'totalDistance': self.totalDistance, 'activity': self.activity, 'results': self.results}


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





class ActivityExperimentPool:
    def __init__(self):
        self.activityExperiments = []
        self.results = {}
        self.reorganizedResultsPerIndividual = {}
        self.reorganizedResults = {}
        self.sexesList = []
        self.genotypeList = []

    def addActivityExperiment(self, experiment):
        self.activityExperiments.append(experiment)

    def addActivityExperimentWithDialog(self, tStartPeriod=0, durationPeriod=24, timebin=10):
        files = getFilesToProcess()
        if (files != None):
            for file in files:
                # create the activity experiment
                print(file)
                experiment = ActivityExperiment(file, tStartPeriod=tStartPeriod, durationPeriod=durationPeriod, timebin=timebin)
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
            experiment.exportReorganizedResultsToJsonFile()
        return self.results


    def organizeResults(self):
        '''
        Organize the results of the activity experiment
        '''
        pass


    def exportReorganizedResultsToJsonFile(self, nameFile="activityResults"):
        jsonFile = json.dumps(self.reorganizedResults, indent=4)
        with open(f"{nameFile}.json", "w") as outputFile:
            outputFile.write(jsonFile)




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
experimentPool = ActivityExperimentPool()
experimentPool.addActivityExperimentWithDialog(1, 1, 10)
experimentPool.computeActivityBatch()
# experimentPool.organizeResults()
# experimentPool.exportReorganizedResultsAsTable("nameTableFile")
# experimentPool.exportReorganizedResultsToJsonFile("nameJsonFile")