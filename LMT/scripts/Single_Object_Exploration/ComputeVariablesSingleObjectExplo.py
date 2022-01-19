'''
Created on 21 nov. 2018

@author: Elodie
'''


import matplotlib.pyplot as plt
import numpy as np;

from lmtanalysis.FileUtil import getFilesToProcess

np.random.seed(0)
import sqlite3
from lmtanalysis.Animal import *
from lmtanalysis.Event import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from tkinter.filedialog import askopenfilename
from matplotlib.patches import *
from matplotlib.collections import PatchCollection
from lmtanalysis.Util import *
from lmtanalysis.Measure import *
from matplotlib import patches
from collections import Counter

if __name__ == '__main__':

    print("Code launched.")

    '''Computation of :
    x distance travelled in both phases
    x distance and time spent in the center and at the periphery in first phase
    x distance and time spent in the object zone and away in the second phase
    x stretch attend posture in the object zone and away in the second phase
    mean speed in both phases
    speed variations in both phases
    x events in both phases: move isolated, stop isolated, SAP, rearing at the periphery, rearing in the center
    jerking aspect of the movement: speed variations?
    '''

    durationPhase1 = 20 * oneMinute
    durationPhase2 = 20 * oneMinute

    singleBehaviouralEventList = ['Stop', 'Center Zone', 'Periphery Zone', 'Rear isolated', 'Rear in centerWindow', 'Rear at periphery', 'SAP', 'WallJump']

    files = getFilesToProcess()

    #determine the strains available in the dataset
    completeStrainList = []
    for file in files:
        connection = sqlite3.connect(file)  # connection to the database
        pool = AnimalPool()
        pool.loadAnimals(connection)  # upload all the animals from the database
        animal = pool.animalDictionnary[1]
        sex = animal.sex
        strain = animal.strain
        completeStrainList.append(strain)
        connection.close()

    strainlist = list(Counter(completeStrainList).keys())
    sexList = ['male', 'female']

    #initialise data storage dictionary
    animalData = {}
    for strainElement in strainlist:
        animalData[strainElement] = {}
        for sexElement in sexList:
            animalData[strainElement][sexElement] = {}

    #extract data from the files of the dataset
    for file in files:
        print('#################################')
        print('file: ', file)
        connection = sqlite3.connect(file)  # connection to the database
        pool = AnimalPool()
        pool.loadAnimals(connection)  # upload all the animals from the database
        animal = pool.animalDictionnary[1]
        animal.loadDetection(start=0, end=oneHour)
        rfid = animal.RFID
        sex = animal.sex
        strain = animal.strain
        animalData[strain][sex][rfid] = {}

        animalData[strain][sex][rfid]['age'] = animal.age
        animalData[strain][sex][rfid]['genotype'] = animal.genotype
        animalData[strain][sex][rfid]['setup'] = animal.setup

        animalData[strain][sex][rfid]['dist_tot1'] = animal.getDistance(0, durationPhase1)
        animalData[strain][sex][rfid]['dist_center1'] = animal.getDistanceSpecZone(0, durationPhase1, xa = 168, xb = 343, ya = 120, yb = 296)
        animalData[strain][sex][rfid]['time_center1'] = animal.getCountFramesSpecZone(0, durationPhase1, xa = 168, xb = 343, ya = 120, yb = 296)
        animalData[strain][sex][rfid]['dist_obj1'] = animal.getDistanceSpecZone(0, durationPhase1, xa=120, xb=250, ya=210, yb=340)
        animalData[strain][sex][rfid]['time_obj1'] = animal.getCountFramesSpecZone(0, durationPhase1, xa=120, xb=250, ya=210, yb=340)
        animalData[strain][sex][rfid]['sap1'] = len(animal.getSap(tmin=0, tmax=durationPhase1, xa=120, xb=250, ya=210, yb=340))

        animalData[strain][sex][rfid]['dist_tot2'] = animal.getDistance(tmin=getStartTestPhase(pool=pool), tmax=getStartTestPhase(pool=pool) + durationPhase2)
        animalData[strain][sex][rfid]['dist_center2'] = animal.getDistanceSpecZone(tmin=getStartTestPhase(pool=pool), tmax=getStartTestPhase(pool=pool) + durationPhase2, xa=168, xb=343, ya=120, yb=296)
        animalData[strain][sex][rfid]['time_center2'] = animal.getCountFramesSpecZone(tmin=getStartTestPhase(pool=pool), tmax=getStartTestPhase(pool=pool) + durationPhase2, xa=168, xb=343, ya=120, yb=296)
        animalData[strain][sex][rfid]['dist_obj2'] = animal.getDistanceSpecZone(tmin=getStartTestPhase(pool=pool), tmax=getStartTestPhase(pool=pool) + durationPhase2, xa=120, xb=250, ya=210,
                                        yb=340)
        animalData[strain][sex][rfid]['time_obj2'] = animal.getCountFramesSpecZone(tmin=getStartTestPhase(pool=pool), tmax=getStartTestPhase(pool=pool) + durationPhase2, xa=120, xb=250, ya=210,
                                           yb=340)
        animalData[strain][sex][rfid]['sap2'] = len(animal.getSap(tmin=getStartTestPhase(pool=pool), tmax=getStartTestPhase(pool=pool) + durationPhase2, xa=120, xb=250, ya=210, yb=340))

        #phase 1:
        minT = 0
        maxT = minT + durationPhase1
        for behavEvent in singleBehaviouralEventList:

            print("computing individual event: {}".format(behavEvent))
            #behavEventTimeLine = EventTimeLineCached(connection, file, behavEvent, animal, minFrame=minT, maxFrame=maxT)
            behavEventTimeLine = EventTimeLine(connection, behavEvent, minFrame=minT, maxFrame=maxT)

            # clean the behavioural event timeline:
            behavEventTimeLine.mergeCloseEvents(numberOfFrameBetweenEvent=1)
            behavEventTimeLine.removeEventsBelowLength(maxLen=3)

            totalEventDuration = behavEventTimeLine.getTotalLength()
            nbEvent = behavEventTimeLine.getNumberOfEvent(minFrame=minT, maxFrame=maxT)
            print("total event duration: ", totalEventDuration)
            animalData[strain][sex][rfid][behavEventTimeLine.eventName + " TotalLen1"] = totalEventDuration
            animalData[strain][sex][rfid][behavEventTimeLine.eventName + " Nb1"] = nbEvent
            if nbEvent == 0:
                meanDur = 0
            else:
                meanDur = totalEventDuration / nbEvent
            animalData[strain][sex][rfid][behavEventTimeLine.eventName + " MeanDur1"] = meanDur

            print('phase 1', behavEventTimeLine.eventName)

        #phase 2:
        minT = getStartTestPhase(pool=pool)
        maxT = minT + durationPhase2
        for behavEvent in singleBehaviouralEventList:

            print("computing individual event: {}".format(behavEvent))
            #behavEventTimeLine = EventTimeLineCached(connection, file, behavEvent, animal, minFrame=minT, maxFrame=maxT)
            behavEventTimeLine = EventTimeLine(connection, behavEvent, minFrame=minT, maxFrame=maxT)
            # clean the behavioural event timeline:
            behavEventTimeLine.mergeCloseEvents(numberOfFrameBetweenEvent=1)
            behavEventTimeLine.removeEventsBelowLength(maxLen=3)

            totalEventDuration = behavEventTimeLine.getTotalLength()
            nbEvent = behavEventTimeLine.getNumberOfEvent(minFrame=minT, maxFrame=maxT)
            print("total event duration: ", totalEventDuration)
            animalData[strain][sex][rfid][behavEventTimeLine.eventName + " TotalLen2"] = totalEventDuration
            animalData[strain][sex][rfid][behavEventTimeLine.eventName + " Nb2"] = nbEvent
            if nbEvent == 0:
                meanDur = 0
            else:
                meanDur = totalEventDuration / nbEvent
            animalData[strain][sex][rfid][behavEventTimeLine.eventName + " MeanDur2"] = meanDur

            print('phase 2', behavEventTimeLine.eventName)

        connection.close()

    with open("profile_data_single_object_explo_CC.json", 'w') as fp:
        json.dump(animalData, fp, indent=4)
    print("json file with profile measurements created.")