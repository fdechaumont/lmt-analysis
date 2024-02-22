'''
Created by Nicolas Torquet at 12/02/2024
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence

Compatible with LMT-toolkit
'''


'''
This script computes the dyadic (2 mice) experiments:
The protocol is an adaptation of the occupant-newcomer experiment often used to study social interactions.

Setup :
Transparent cage of 50 x 50 cm with a new sawdust bottom. 
Kinect at 63 cm high from the floor.


Habituation phase of the tested mouse:
The test mouse is placed in the cage and allowed to explore the environment for n minutes (20 minutes but this parameter can be different). 
The LMT acquisition is started once the animal is placed in the cage.

Social interaction phase:
After the n minutes habituation period, the acquisition of LMT is paused and a control mouse of the same genetic background and age as the test mouse is introduced. 
The introduced mouse must not be known by the tested mouse. 
Once this mouse is introduced, a second LMT acquisition session is started (the pause is ) and the animals are allowed to interact 
for m minutes (30 minutes but this parameter can be different).

Analysis :
The habituation phase analysis will focus on the activity and the exploration of the tested mouse (like an openfield experiment).
The social interaction phase will compute the activity of each animal as well as the social aspects (types of contacts, approaches, follow-up, etc).
'''

from lmtanalysis.Measure import oneMinute
import sqlite3
import json
from experimental.Animal_LMTtoolkit import AnimalPool
from Event import EventTimeLine
from lmtanalysis.AnimalType import AnimalType
from lmtanalysis.FileUtil import *
from Parameters import getAnimalTypeParameters
from ZoneArena import getZoneCoordinatesFromCornerCoordinatesOpenfieldArea, getSmallerZoneFromCornerCoordinatesAndMargin, getSmallerZoneFromGivenWholeCageCoordinatesAndMargin
from Openfield.ComputeOpenfield import computeOpenfield
from ComputeMeasuresIdentityProfileOneMouseAutomatic import computeProfilePairFromPause



class DyadicExperiment:
    def __init__(self, file, tStartHabituationPhase=0, durationHabituationPhase=15, durationSocialPhase=25):
        '''
        :param file: path of the experiment file
        :param animalType: the animalType to get animalType's parameters
        :param tStartHabituationPhase: the first frame of the habituation phase
        :param durationHabituationPhase: the last frame of the habituation phase
        :param durationSocialPhase: duration in minutes of the social phase
        '''
        # global animalType
        self.file = file
        self.name = file.split('.sqlite')[0].split('\\')[-1].split("/")[-1]
        self.animalType = animalType
        self.tStartFrameHabituationPhase = tStartHabituationPhase   # framenumber
        self.durationHabituationPhase = durationHabituationPhase*oneMinute  # duration in number of frame
        self.tStopFrameHabituationPhase = self.tStartFrameHabituationPhase+self.durationHabituationPhase    # convert in framenumber
        self.durationSocialPhase = durationSocialPhase*oneMinute    # duration in number of frame

        ''' 
        Cage parameters default to animalType parameters but can be modified
        cage coordinates have this format:
        {'xa': 168, 'xb': 343, 'ya': 120, 'yb': 296}
        '''
        self.parameters = getAnimalTypeParameters(animalType)
        self.wholeCageCoordinates = getZoneCoordinatesFromCornerCoordinatesOpenfieldArea(self.animalType)
        self.centerCageCoordinates = getSmallerZoneFromCornerCoordinatesAndMargin(self.parameters.CENTER_MARGIN, self.animalType)
        self.wholeCageCoordinatesWithoutBorder = getSmallerZoneFromCornerCoordinatesAndMargin(self.parameters.CAGE_MARGIN, self.animalType)

        '''
        Behavior list default can be modified
        In FileUtil (2024-02-16):
        behaviouralEventOneMouseSingle = ["Move isolated", "Move in contact", "Stop isolated", "Rear isolated",
                                          "Rear in contact", "Oral-genital Contact", "Train2", "FollowZone",
                                          "Social approach", "Approach contact", "Break contact"]
        behaviouralEventOneMouseSocial = ["Contact", "Group2", "Oral-oral Contact", "Oral-genital Contact",
                                          "Side by side Contact", "Side by side Contact, opposite way",
                                          "Train2", "FollowZone",
                                          "Social approach", "Approach contact",
                                          "Break contact"]
        '''
        self.behaviouralEventOneMouseSingle = behaviouralEventOneMouseSingle
        self.behaviouralEventOneMouseSocial = behaviouralEventOneMouseSocial


    def getName(self):
        return self.name

    def setWholeCageCoordinates(self, wholeCageCoordinates):
        '''
        :param wholeCageCoordinates: format like {'xa': 168, 'xb': 343, 'ya': 120, 'yb': 296}
        '''
        self.wholeCageCoordinates = wholeCageCoordinates

    def getWholeCageCoordinates(self):
        return self.wholeCageCoordinates

    def setCenterCageCoordinates(self, centerMargin, wholeCageCoordinates):
        '''
        :param centerMargin: in centimeters
        :param wholeCageCoordinates: has to be like {xa = 111, xb = 400, ya = 63, yb = 353}
        '''
        self.centerCageCoordinates = getSmallerZoneFromGivenWholeCageCoordinatesAndMargin(centerMargin, wholeCageCoordinates, self.animalType)

    def getCenterCageCoordinates(self):
        return self.centerCageCoordinates

    def setWholeCageCoordinatesWithoutBorder(self, cageMargin, wholeCageCoordinates):
        '''
        :param cageMargin: in centimeters
        :param wholeCageCoordinates: has to be like {xa = 111, xb = 400, ya = 63, yb = 353}
        '''
        self.wholeCageCoordinatesWithoutBorder = getSmallerZoneFromGivenWholeCageCoordinatesAndMargin(cageMargin, wholeCageCoordinates, self.animalType)

    def getWholeCageCoordinatesWithoutBorder(self):
        return self.wholeCageCoordinatesWithoutBorder

    def getMetadata(self):
        animalTypeString = str(self.animalType).split('.')[1]
        metadata = {
            'animalType': animalTypeString,
            'wholeCageCoordinates': self.wholeCageCoordinates,
            'centerCageCoordinates': self.centerCageCoordinates,
            'wholeCageCoordinatesWithoutBorder': self.wholeCageCoordinatesWithoutBorder
        }
        return metadata


    def setBehaviouralEventOneMouseSingle(self, behaviouralEventOneMouseSingle):
        '''
        :param behaviouralEventOneMouseSingle: list of variables
        '''
        self.behaviouralEventOneMouseSingle = behaviouralEventOneMouseSingle

    def setBehaviouralEventOneMouseSocial(self, behaviouralEventOneMouseSocial):
        '''
        :param behaviouralEventOneMouseSocial: list of variables
        '''
        self.behaviouralEventOneMouseSocial = behaviouralEventOneMouseSocial


    def computeDyadicHabituationPhase(self):
        '''
        Compute the habituation phase of the dyadic experiment.
        Return the activity and the exploration of the tested mouse

        Default:
            - tmin = 0
            - tmax = 15 minutes
            - centerZone as define
            - sap_interestZone as define: whole cage without border
            - coordinates of the whole cage: xa = 111, xb = 400, ya = 63, yb = 353
            - center zone: xa = 168, xb = 343, ya = 120, yb = 296
            - whole cage without border (3cm): xa = 128, xb = 383, ya = 80, yb =336
        '''

        self.dataHabituation = computeOpenfield(self.file, self.centerCageCoordinates, self.wholeCageCoordinatesWithoutBorder,
                                tmin=self.tStartFrameHabituationPhase, tmax=self.tStopFrameHabituationPhase)

        return self.dataHabituation



    def computeDyadicSocialPhase(self):
        '''
        Compute the activity and the social interactions of the tested mouse with the new comer
        Computing from the last frame +1 with a pause event to tmax (last frame +1 + tmax)
        '''
        self.dataSocial = computeProfilePairFromPause(self.file, self.durationSocialPhase, self.behaviouralEventOneMouseSingle, self.behaviouralEventOneMouseSocial)

        return self.dataSocial

    def getAllResults(self):
        return {'metadata': self.getMetadata(), 'dataHabituation': self.dataHabituation, 'dataSocial': self.dataSocial}

    def computeWholeDyadicExperiment(self):
        self.computeDyadicHabituationPhase()
        self.computeDyadicSocialPhase()

        return self.getAllResults()



class DyadicExperimentPool:
    def __init__(self):
        self.dyadicExperiments = []
        self.results = {}
        self.reorganizedResults = {}

    def addDyadicExperiment(self, experiment):
        self.dyadicExperiments.append(experiment)

    def addDyadicExperimentWithDialog(self):
        files = getFilesToProcess()
        if (files != None):
            for file in files:
                # create the Dyadic experiment
                experiment = DyadicExperiment(file)
                self.addDyadicExperiment(experiment)


    def getResults(self):
        return self.results

    def computeDyadicBatch(self):
        '''
        Compute a batch of dyadic experiment
        '''
        for experiment in self.dyadicExperiments:
            self.results[experiment.getName()] = experiment.computeWholeDyadicExperiment()
        return self.results

    def organizeResults(self):
        '''
        Organize the results dict in a new dict organizedResults
        organizedResults like
        {
            'metadata': {
                'experimentName': experimentMetaData,
            },
            'habituationPhase': {
                'M' or 'Male': {
                    'geno1': {
                        'ID': ID,
                        'rfid': rfid,
                        'var1': var1,
                        ...
                        'experimentName': experimentname
                    }
                },
                'F' or 'Female': {
                    'geno1': {
                        'ID': ID,
                        'rfid': rfid,
                        'var1': var1,
                        ...
                        'experimentName': experimentname
                    }
                }
            },
            'socialPhase': {
                the same as habituation phase
            }
        }
        '''
        for experiment in self.results:
            print(experiment)


def setAnimalType( aType ):
    global animalType
    animalType = aType

### for test

# file = r"D:\base test manip dyadic\2024-02-05-h46-Experiment 1494.sqlite"
# setAnimalType(AnimalType.MOUSE)
# xp = DyadicExperiment(file)
# data = xp.computeDyadicHabituationPhase()
# dataSocial = xp.computeDyadicSocialPhase()
# dataManip = xp.computeWholeDyadicExperiment()

## experiment pool test
experimentPool = DyadicExperimentPool()
experimentPool.addDyadicExperimentWithDialog()
experimentPool.computeDyadicBatch()
# experimentPool.organizeResults()


