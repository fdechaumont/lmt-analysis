'''
Created on 16 Feb 2022

@author: Elodie
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.FileUtil import *
from lmtanalysis.Util import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.BehaviouralSequencesUtil import exclusiveEventList, exclusiveEventsLabels

if __name__ == '__main__':
    '''This code allows to check whether events are exclusive'''
    print("Code launched.")

    tmin, tmax = getMinTMaxTInput()
    files = getFilesToProcess()

    
    for file in files:
        print(file)
        connection = sqlite3.connect(file)
        pool = AnimalPool()
        pool.loadAnimals(connection)

        for animal in pool.animalDictionary.keys():
            print("computing individual animal: {}".format(animal))
            rfid = pool.animalDictionary[animal].RFID

            #load contact timeline for animal
            contactTimeLine = EventTimeLineCached( connection, file, 'Contact', animal, None, minFrame=tmin, maxFrame=tmax )
            contactTimeLine.plotEventDurationDistributionHist(nbBin = 100)

            #load timelines for exclusive events for animal:
            eventTimeLine = {}
            dicoEvent = {}
            results = {}
            for exclusiveEvent in exclusiveEventList:
                eventTimeLine[exclusiveEvent] = EventTimeLineCached( connection, file, exclusiveEvent, animal, None, minFrame=tmin, maxFrame=tmax )
                dicoEvent[exclusiveEvent] = eventTimeLine[exclusiveEvent].getDictionary(minFrame=tmin, maxFrame=tmax)
                results[exclusiveEvent] = 0

            timeLineList = []
            for exclusiveEvent in exclusiveEventList:
                timeLineList.append(eventTimeLine[exclusiveEvent])
            plotMultipleTimeLine(timeLineList, show=True, minValue=tmin)

            '''Check the first frame of each contact, to see in which exclusive events the frame is'''
            for event in contactTimeLine.eventList:
                firstFrame = event.startFrame
                lastFrame = event.endFrame
                for exclusiveEvent in exclusiveEventList:
                    if eventTimeLine[exclusiveEvent].hasEvent(firstFrame):
                        results[exclusiveEvent] += 1



            print(results)

    print('Job done.')
