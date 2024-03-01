'''
Created by Nicolas Torquet at 01/03/2024
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''
import sqlite3
from Animal_LMTtoolkit import AnimalPoolToolkit
from EventTimeLineCache import EventTimeLineCached
from lmtanalysis.Util import getStartTestPhase


def computeProfilePairFromPause(file, experimentDuration, behaviouralEventListSingle, behaviouralEventListSocial):
    print("Start computeProfilePair")

    connection2 = sqlite3.connect(file)
    print(connection2)

    pool = AnimalPoolToolkit()
    pool.loadAnimals(connection2)
    minT = getStartTestPhase(pool)
    print('minT: ' + str(minT))
    maxT = minT + experimentDuration

    print('maxT: ' + str(maxT))

    pair = []
    genotype = []
    sex = []
    treatment = []
    age = []
    strain = []
    for animal in pool.animalDictionary.keys():
        rfid = pool.animalDictionary[animal].RFID
        geno = pool.animalDictionary[animal].genotype
        sexAnimal = pool.animalDictionary[animal].sex
        # treatmentAnimal = pool.animalDictionary[animal].treatment
        ageAnimal = pool.animalDictionary[animal].age
        strainAnimal = pool.animalDictionary[animal].strain
        pair.append(rfid)
        genotype.append(geno)
        sex.append(sexAnimal)
        # treatment.append(treatmentAnimal)
        age.append(ageAnimal)
        strain.append(strainAnimal)

    pairName = ('{}_{}'.format(min(pair), max(pair)))
    genoPair = ('{}_{}'.format(genotype[0], genotype[1]))
    agePair = age[0]
    if sex[0] == sex[1]:
        sexPair = sex[0]
    else:
        sexPair = 'mixed'
    print('pair: ', pairName, genoPair, sexPair)

    # treatmentPair = ('{}_{}'.format(treatment[0], treatment[1]))

    if strain[0] == strain[1]:
        strainPair = strain[0]
    else:
        strainPair = '{}_{}'.format(strain[0], strain[1])

    animalData = {}
    animalData[pairName] = {}
    animalData[pairName]['genotype'] = genoPair
    animalData[pairName]["file"] = file
    animalData[pairName]["animal"] = pairName
    animalData[pairName]['sex'] = sexPair
    # animalData[pairName]['treatment'] = treatmentPair
    animalData[pairName]['age'] = agePair
    animalData[pairName]['strain'] = strainPair
    animalData[pairName]['group'] = pairName
    animalData[pairName]["totalDistance"] = "totalDistance"

    for animal in pool.animalDictionary.keys():

        print("computing individual animal: {}".format(animal))
        rfid = pool.animalDictionary[animal].RFID
        print("RFID: {}".format(rfid))
        animalData[rfid] = {}
        # store the animal
        animalData[rfid]["animal"] = pool.animalDictionary[animal].name
        animalObject = pool.animalDictionary[animal]
        animalData[rfid]["file"] = file
        animalData[rfid]["rfid"] = rfid
        animalData[rfid]['genotype'] = pool.animalDictionary[animal].genotype
        animalData[rfid]['sex'] = pool.animalDictionary[animal].sex
        animalData[rfid]['age'] = pool.animalDictionary[animal].age
        animalData[rfid]['strain'] = pool.animalDictionary[animal].strain
        animalData[rfid]['group'] = pairName

        # compute the profile for single behaviours
        for behavEvent in behaviouralEventListSingle:

            print("computing individual event: {}".format(behavEvent))

            behavEventTimeLine = EventTimeLineCached(connection2, file, behavEvent, animal, minFrame=minT,
                                                     maxFrame=maxT)
            # clean the behavioural event timeline:
            behavEventTimeLine.mergeCloseEvents(numberOfFrameBetweenEvent=1)
            behavEventTimeLine.removeEventsBelowLength(maxLen=3)

            totalEventDuration = behavEventTimeLine.getTotalLength()
            nbEvent = behavEventTimeLine.getNumberOfEvent(minFrame=minT, maxFrame=maxT)
            print("total event duration: ", totalEventDuration)
            animalData[rfid][behavEventTimeLine.eventName + " TotalLen"] = totalEventDuration
            animalData[rfid][behavEventTimeLine.eventName + " Nb"] = nbEvent
            if nbEvent == 0:
                meanDur = 0
            else:
                meanDur = totalEventDuration / nbEvent
            animalData[rfid][behavEventTimeLine.eventName + " MeanDur"] = meanDur

            print(behavEventTimeLine.eventName, pool.animalDictionary[animal].genotype, behavEventTimeLine.idA,
                  totalEventDuration, nbEvent, meanDur)

        # compute the total distance traveled per individual
        COMPUTE_TOTAL_DISTANCE = True
        if COMPUTE_TOTAL_DISTANCE == True:
            animalObject.loadDetection(start=minT, end=maxT, lightLoad=True)
            animalData[rfid]["totalDistance"] = animalObject.getDistance(tmin=minT, tmax=maxT) / 100
        else:
            animalData[rfid]["totalDistance"] = "totalDistance"

    # Compute the profiles for both individuals of the pair together
    for behavEvent in behaviouralEventListSocial:

        print("computing individual event: {}".format(behavEvent))

        behavEventTimeLine = EventTimeLineCached(connection2, file, behavEvent, minFrame=minT, maxFrame=maxT)
        # clean the behavioural event timeline:
        behavEventTimeLine.mergeCloseEvents(numberOfFrameBetweenEvent=1)
        behavEventTimeLine.removeEventsBelowLength(maxLen=3)

        totalEventDuration = behavEventTimeLine.getTotalLength()
        nbEvent = behavEventTimeLine.getNumberOfEvent(minFrame=minT, maxFrame=maxT)
        print("total event duration: ", totalEventDuration)
        animalData[pairName][behavEventTimeLine.eventName + " TotalLen"] = totalEventDuration
        animalData[pairName][behavEventTimeLine.eventName + " Nb"] = nbEvent
        if nbEvent == 0:
            meanDur = 0
        else:
            meanDur = totalEventDuration / nbEvent
        animalData[pairName][behavEventTimeLine.eventName + " MeanDur"] = meanDur

        print(behavEventTimeLine.eventName, genoPair, pairName, totalEventDuration, nbEvent, meanDur)

    connection2.close()

    return animalData

