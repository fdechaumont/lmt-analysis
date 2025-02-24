'''
Created by Nicolas Torquet at 28/01/2025
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''


import sqlite3
from Activity.ComputeActivityExperiment import changeStringKeysToIntKeys
from Animal_LMTtoolkit import AnimalPoolToolkit
from FileUtil import behaviouralEventOneMouse, getFilesToProcess
from lmtanalysis.Event import EventTimeLine
import json
from lmtanalysis.Measure import oneMinute, oneHour
from lmtanalysis.AnimalType import AnimalType
from datetime import datetime, timedelta
from Util import getDatetimeFromFrame, getNumberOfFrames, getStartInDatetime
from ZoneArena import getZoneCoordinatesFromCornerCoordinatesOpenfieldArea


class EventsPerTimeBin:
    def __init__(self, file, tStartPeriod=1, durationPeriod=24, timebin=10):
        '''
        :param file: path of the experiment file -> events of the file needs to be rebuild
        :param tStartExperiment: the first frame of the investigated period
        :param durationExperiment: duration in hours of the experiment
        :param timebin: timebin in minutes to compute the distance travelled
        '''
        # global animalType
        self.animalType = animalType
        self.file = file
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
            self.durationPeriodInFrame = durationPeriod*oneHour    # duration in number of frame
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


    def convertFrameNumberForTimeBinTimeline(self, frameNumber):
        # axe en minute depuis le début de période!
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


    def getEventsPerTimeBin(self):
        if '.sqlite' in self.file:
            if self.maxFrame == None:
                self.maxFrame = self.getMaxDetectionT()

            eventList = {}
            self.totalDistance = {}
            self.results = {}

            for animal in self.pool.animalDictionary.keys():
                rfid = self.pool.animalDictionary[animal].RFID
                eventList[rfid] = {}
                for behavior in behaviouralEventOneMouse:
                    eventList[rfid][behavior] = []

                    distanceList = []
                    t = self.minFrame

                    connection = sqlite3.connect(self.file)
                    eventList[rfid][behavior] = EventTimeLine(connection, behavior, idA=animal.baseId, minFrame=t,
                                                              maxFrame=t + self.binFrameSize).eventList
                    connection.close()
                #     while (t < self.maxFrame):
                #         eventList[rfid][behavior] = EventTimeLine(connection, behavior, idA=animal.baseId, minFrame=t, maxFrame=t + self.binFrameSize).eventList
                #         distanceBin = self.getDistance(t, t + self.binFrameSize)
                #         print("Distance bin n:{} value:{}".format(t, distanceBin))
                #         distanceList.append(distanceBin)
                #         t = t + self.binFrameSize + 1
                #
                #     return distanceList
                #
                # # timebin à mettre en place: boucle
                # eventList[rfid][behavior] = EventTimeLine(connection, behavior, idA=animal.baseId).eventList
                # activity[rfid] = self.pool.animalDictionary[animal].getDistancePerBin(binFrameSize=self.timebinInFrame,
                #                                                                  minFrame=self.tStartPeriod, maxFrame=self.tStopFramePeriod)
                # self.totalDistance[rfid] = self.pool.animalDictionary[animal].getDistance(tmin=self.tStartPeriod, tmax=self.tStopFramePeriod)
                #
                # nTimeBins = len(activity[rfid])
                # print(nTimeBins)
                #
                # timeLine = [0]
                # for t in range(1, nTimeBins):
                #     x = timeLine[t - 1] + self.timebin
                #     timeLine.append(x)
                #
                # self.results[rfid] = {}
                # for time, distance in zip(timeLine, activity[rfid]):
                #     self.results[rfid][time] = distance

            self.getNightTimeLine()

            # return {'totalDistance': self.totalDistance, 'results': self.results}

        else:
            print("Experiment from json: cannot use getEventsPerTimeBin()")
            return False





if __name__ == '__main__':
    def setAnimalType( aType ):
        global animalType
        animalType = aType


    ### for test
    ## single experiment
    setAnimalType(AnimalType.MOUSE)

    files = getFilesToProcess()
    connection = sqlite3.connect(files[0])
    pool = AnimalPoolToolkit()
    pool.loadAnimals(connection)
    pool.loadDetection(lightLoad=True)
    maxFrame = getNumberOfFrames(files[0])


    eventList = {}

    for animal in pool.animalDictionary.keys():
        rfid = pool.animalDictionary[animal].RFID
        eventList[rfid] = {}
        for behavior in behaviouralEventOneMouse:
            eventList[rfid][behavior] = []

            distanceList = []

            eventList[rfid][behavior] = EventTimeLine(connection, behavior, minFrame=0, maxFrame=maxFrame,
                                                      idA=pool.animalDictionary[animal].baseId).eventList

    connection.close()

    timebin = 10
    timebinInFrame = 10 * oneMinute

    # il va falloir affiner pour savoir si on prend en compte les frames qui sont sur deux timebin

    nbOfTimeBins = round(maxFrame / timebinInFrame)

    eventPerTimeBin = {}
    for animal in eventList:
        eventPerTimeBin[animal] = {}
        for behavior in eventList[animal]:
            eventPerTimeBin[animal][behavior] = []
            startWindow = 0
            for window in range(0, nbOfTimeBins):
                nbFrameOfEvent = 0
                for frame in range(startWindow, startWindow + timebinInFrame):
                    for event in eventList[animal][behavior]:
                        if frame >= event.startFrame and frame < event.endFrame:
                            print(f'frame {frame} in event (start: {event.startFrame} - end: {event.endFrame})')
                            nbFrameOfEvent += 1
                        # if frame > event.endFrame:
                        #     break
                eventPerTimeBin[animal][behavior].append(nbFrameOfEvent)
                startWindow += timebinInFrame



