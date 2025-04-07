'''
Created by Nicolas Torquet at 14/02/2024
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence

Code derived from ComputeActivityHabituationOpenfield code
Compatible with LMT-toolkit
'''


'''
Setup :
Transparent cage of 50 x 50 cm with a new sawdust bottom. 
Kinect at 63 cm high from the floor.
'''


from lmtanalysis.Measure import oneMinute
import sqlite3
import json
from experimental.Animal_LMTtoolkit import AnimalPoolToolkit
from Event import EventTimeLine
from Parameters import getAnimalTypeParameters



openfieldVariableList = ['totDistance', 'distancePerBin', 'centerDistance', 'centerTime', 'nbSap', 'rearTotal Nb', 'rearTotal Duration',
                    'rearCenter Nb', 'rearCenter Duration', 'rearPeriphery Nb', 'rearPeriphery Duration']




def computeOpenfield(file, centerCageCoordinates, wholeCageCoordinatesWithoutBorder, tmin=0, tmax=15*oneMinute, variableList=openfieldVariableList, getTrajectory=False):
    '''
    :param file: the sqlite file to process
    :param tmin: the first frame of the session
    :param tmax: the last frame of the session
    :param centerCageCoordinates: format like {'xa': 168, 'xb': 343, 'ya': 120, 'yb': 296}
    :param wholeCageCoordinates: format like {'xa': 168, 'xb': 343, 'ya': 120, 'yb': 296}
    Compute the openfield experiment
    Return the activity and the exploration of the tested mouse
    '''

    data = {}

    connection = sqlite3.connect(file)

    # TODO: check if Animal class is ok (treatment column)
    pool = AnimalPoolToolkit()
    pool.loadAnimals(connection)
    genoList = pool.getGenotypeList()
    sexesList = pool.getSexList()
    treatmentsList = pool.getTreatmentList()

    for val in variableList:
        data[val] = {}
        for sex in sexesList:
            data[val][sex] = {}
            for geno in genoList:
                data[val][sex][geno] = {}
                for treatment in treatmentsList:
                    data[val][sex][geno][treatment] = {}

    data['trajectory'] = {}

    animal = pool.animalDictionary[1]
    animal.loadDetection(tmin, tmax)
    sex = animal.sex
    geno = animal.genotype
    rfid = animal.RFID
    treatment = animal.treatment
    # strain = animal.strain
    # age = animal.age
    # setup = animal.setup
    if getTrajectory:
        trajectory = animal.getTrajectory()
    else:
        trajectory = "No trajectory"
    data['trajectory'][rfid] = trajectory


    dt1 = animal.getDistance(tmin=tmin, tmax=tmax)  # compute the total distance traveled in the whole cage
    # get distance per time bin
    dBin = animal.getDistancePerBin(binFrameSize=1 * oneMinute, minFrame=tmin, maxFrame=tmax)

    # get distance and time spent in the middle of the cage
    d1 = animal.getDistanceSpecZone(tmin, tmax, xa=centerCageCoordinates['xa'], xb=centerCageCoordinates['xb'], ya=centerCageCoordinates['ya'],
                                    yb=centerCageCoordinates['yb'])  # compute the distance traveled in the center zone
    t1 = animal.getCountFramesSpecZone(tmin, tmax, xa=centerCageCoordinates['xa'], xb=centerCageCoordinates['xb'], ya=centerCageCoordinates['ya'],
                                       yb=centerCageCoordinates['yb'])  # compute the time spent in the center zone


    '''#get the number of frames in sap in whole cage
    sap1 = len(animal.getSap(tmin=tmin, tmax=tmax, xa = 111, xb = 400, ya = 63, yb = 353))'''
    # get the number of frames in sap in whole cage but without counting the border to filter out SAPs against the wall
    sap1 = len(animal.getSap(tmin=tmin, tmax=tmax, xa=wholeCageCoordinatesWithoutBorder['xa'], xb=wholeCageCoordinatesWithoutBorder['xb'],
                             ya=wholeCageCoordinatesWithoutBorder['ya'], yb=wholeCageCoordinatesWithoutBorder['yb']))
    # fill the data dictionary with the computed data for each file:
    data['totDistance'][sex][geno][treatment][rfid] = dt1 / 100
    # convert distance from cm to meter
    data['distancePerBin'][sex][geno][treatment][rfid] = [distanceBin / 100 for distanceBin in dBin]
    data['centerDistance'][sex][geno][treatment][rfid] = d1 / 100
    data['centerTime'][sex][geno][treatment][rfid] = t1 / 30
    data['nbSap'][sex][geno][treatment][rfid] = sap1

    # get the number and time of rearing
    rearTotalTimeLine = EventTimeLine(connection, "Rear isolated", minFrame=tmin, maxFrame=tmax,
                                      loadEventIndependently=True)
    rearCenterTimeLine = EventTimeLine(connection, "Rear in center", minFrame=tmin, maxFrame=tmax,
                                       loadEventIndependently=True)
    rearPeripheryTimeLine = EventTimeLine(connection, "Rear at periphery", minFrame=tmin, maxFrame=tmax,
                                          loadEventIndependently=True)

    data['rearTotal Nb'][sex][geno][treatment][rfid] = rearTotalTimeLine.getNbEvent()
    data['rearTotal Duration'][sex][geno][treatment][rfid] = rearTotalTimeLine.getTotalLength() / 30
    data['rearCenter Nb'][sex][geno][treatment][rfid] = rearCenterTimeLine.getNbEvent()
    data['rearCenter Duration'][sex][geno][treatment][rfid] = rearCenterTimeLine.getTotalLength() / 30
    data['rearPeriphery Nb'][sex][geno][treatment][rfid] = rearPeripheryTimeLine.getNbEvent()
    data['rearPeriphery Duration'][sex][geno][treatment][rfid] = rearPeripheryTimeLine.getTotalLength() / 30

    connection.close()

    return data





