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
from Event import EventTimeLine
from lmtanalysis.AnimalType import AnimalType
from lmtanalysis.FileUtil import *
from Parameters import getAnimalTypeParameters
from ZoneArena import getZoneCoordinatesFromCornerCoordinatesOpenfieldArea, getSmallerZoneFromCornerCoordinatesAndMargin, getSmallerZoneFromGivenWholeCageCoordinatesAndMargin
from Openfield.ComputeOpenfield import computeOpenfield
from ComputeDyadic import computeProfilePairFromPause
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def exportReorganizedResultsAsTable(reorganizedResults, typeData):
    '''
    reorganisedResults: a dictionary to convert into pandas dataframe
    typeData: could be habituationPhase or socialPhase
    '''
    if typeData != "habituationPhase" and typeData != "socialPhase":
        print("typeData should be habituationPhase or socialPhase")
        return "typeData should be habituationPhase or socialPhase"
    else:
        if typeData == "habituationPhase":
            tempDict = {}
            for experiment in reorganizedResults["habituationPhase"]:
                for variable in reorganizedResults["habituationPhase"][experiment]:
                    if variable != 'trajectory' and variable != 'distancePerBin':
                        for sex in reorganizedResults["habituationPhase"][experiment][variable]:
                            for genotype in reorganizedResults["habituationPhase"][experiment][variable][sex]:
                                if len(reorganizedResults["habituationPhase"][experiment][variable][sex][genotype]) > 0:
                                    for animal in reorganizedResults["habituationPhase"][experiment][variable][sex][genotype]:
                                        if animal not in tempDict:
                                            tempDict[animal] = {
                                                'Mouse label': animal,
                                                'Genotype': genotype,
                                                'Gender': sex
                                            }
                                        tempDict[animal][variable] = reorganizedResults["habituationPhase"][experiment][variable][sex][genotype][animal]

        if typeData == "socialPhase":
            tempDict = {}
            listOfColumns = []
            counter = 0
            for experiment in reorganizedResults["socialPhase"]:
                for animal in reorganizedResults["socialPhase"][experiment]:
                    counter += 1
                    tempDict[counter] = {
                        'Mouse label': animal
                    }
                    for variable in reorganizedResults["socialPhase"][experiment][animal]:
                        tempDict[counter][variable] = reorganizedResults["socialPhase"][experiment][animal][variable]
                        if variable not in listOfColumns:
                            listOfColumns.append(variable)

            for number in tempDict:
                for variable in listOfColumns:
                    if variable not in tempDict[number]:
                        tempDict[number][variable] = np.nan

        table = pd.DataFrame([v for k, v in tempDict.items()])
        return table


class DyadicExperiment:
    def __init__(self, file, tStartHabituationPhase=0, durationHabituationPhase=15, durationSocialPhase=25, getTrajectory = False):
        '''
        :param file: path of the experiment file
        :param animalType: the animalType to get animalType's parameters
        :param tStartHabituationPhase: the first frame of the habituation phase
        :param durationHabituationPhase: duration in minutes of the habituation phase
        :param durationSocialPhase: duration in minutes of the social phase
        :param getTrajectory: if True, get the trajectory of the animal during the habituation phase
        '''
        # global animalType
        self.file = file
        self.name = file.split('.sqlite')[0].split('\\')[-1].split("/")[-1]
        self.animalType = animalType
        self.animals = {}
        self.tStartFrameHabituationPhase = tStartHabituationPhase   # framenumber
        self.durationHabituationPhase = durationHabituationPhase*oneMinute  # duration in number of frame
        self.tStopFrameHabituationPhase = self.tStartFrameHabituationPhase+self.durationHabituationPhase    # convert in framenumber
        self.durationSocialPhase = durationSocialPhase*oneMinute    # duration in number of frame
        self.getTrajectory = getTrajectory

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


    def setTrajectory(self, getTrajectory):
        self.getTrajectory = getTrajectory

    def setWholeCageCoordinates(self, wholeCageCoordinates):
        '''
        :param wholeCageCoordinates: format like {'xa': 168, 'xb': 343, 'ya': 120, 'yb': 296}
        '''
        self.wholeCageCoordinates = wholeCageCoordinates

    def getWholeCageCoordinates(self):
        return self.wholeCageCoordinates

    def setCenterCageCoordinates(self, centerMargin):
        '''
        :param centerMargin: in centimeters
        '''
        self.centerCageCoordinates = getSmallerZoneFromGivenWholeCageCoordinatesAndMargin(centerMargin, self.wholeCageCoordinates, self.animalType)

    def getCenterCageCoordinates(self):
        return self.centerCageCoordinates

    def setWholeCageCoordinatesWithoutBorder(self, cageMargin):
        '''
        :param cageMargin: in centimeters
        '''
        self.wholeCageCoordinatesWithoutBorder = getSmallerZoneFromGivenWholeCageCoordinatesAndMargin(cageMargin, self.wholeCageCoordinates, self.animalType)

    def getWholeCageCoordinatesWithoutBorder(self):
        return self.wholeCageCoordinatesWithoutBorder

    def getMetadata(self):
        animalTypeString = str(self.animalType).split('.')[1]
        metadata = {
            'animalType': animalTypeString,
            'wholeCageCoordinates': self.wholeCageCoordinates,
            'centerCageCoordinates': self.centerCageCoordinates,
            'wholeCageCoordinatesWithoutBorder': self.wholeCageCoordinatesWithoutBorder,
            'animals': self.animals,
            'singleMouseVariables': self.behaviouralEventOneMouseSingle,
            'socialVariables': self.behaviouralEventOneMouseSocial
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
                                tmin=self.tStartFrameHabituationPhase, tmax=self.tStopFrameHabituationPhase, getTrajectory=self.getTrajectory)

        return self.dataHabituation



    def computeDyadicSocialPhase(self):
        '''
        Compute the activity and the social interactions of the tested mouse with the new comer
        Computing from the last frame +1 with a pause event to tmax (last frame +1 + tmax)
        extract animals information for metadata
        '''
        self.dataSocial = computeProfilePairFromPause(self.file, self.durationSocialPhase, self.behaviouralEventOneMouseSingle, self.behaviouralEventOneMouseSocial)

        # extract animals information for metadata
        for animal in self.dataSocial:
            if len(animal) <= 12:
                self.animals[animal] = {}
                self.animals[animal]['name'] = self.dataSocial[animal]['animal']
                self.animals[animal]['rfid'] = self.dataSocial[animal]['rfid']
                self.animals[animal]['genotype'] = self.dataSocial[animal]['genotype']
                self.animals[animal]['sex'] = self.dataSocial[animal]['sex']
                self.animals[animal]['age'] = self.dataSocial[animal]['age']
                self.animals[animal]['strain'] = self.dataSocial[animal]['strain']
                self.animals[animal]['group'] = self.dataSocial[animal]['group']

        return self.dataSocial


    def getTrajectoryHabituationPhase(self):
        return self.dataHabituation['trajectory']


    def plotTrajectoryHabituationPhase(self):
        for animal in self.dataHabituation['trajectory']:
            if self.dataHabituation['trajectory'][animal] != "No trajectory":
                frames, coordinates = zip(*self.dataHabituation['trajectory'][animal].items())
                x, y = zip(*coordinates)
                plt.plot(x, y)
                plt.title(f"{animal} trajectory - habituation phase")
                plt.show()
            else:
                print("No trajectory")

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
        self.reorganizedResultsPerIndividual = {}
        self.reorganizedResults = {}
        self.sexesList = []
        self.genotypeList = []

    def addDyadicExperiment(self, experiment):
        self.dyadicExperiments.append(experiment)

    def addDyadicExperimentWithDialog(self):
        files = getFilesToProcess()
        if (files != None):
            for file in files:
                # create the Dyadic experiment
                experiment = DyadicExperiment(file)
                self.addDyadicExperiment(experiment)


    def setWholeCageCoordinatesExperimentPool(self, wholeCageCoordinates):
        '''
        :param wholeCageCoordinates: format like {'xa': 168, 'xb': 343, 'ya': 120, 'yb': 296}
        '''
        for experiment in self.dyadicExperiments:
            experiment.setWholeCageCoordinates(wholeCageCoordinates)

    def setCenterCageCoordinatesExperimentPool(self, centerMargin):
        '''
        :param centerMargin: in centimeters
        '''
        for experiment in self.dyadicExperiments:
            experiment.setCenterCageCoordinates(centerMargin)

    def setWholeCageCoordinatesWithoutBorderExperimentPool(self, cageMargin):
        '''
        :param cageMargin: in centimeters
        '''
        for experiment in self.dyadicExperiments:
            experiment.setWholeCageCoordinatesWithoutBorder(cageMargin)

    def getResults(self):
        return self.results

    def computeDyadicBatch(self):
        '''
        Compute a batch of dyadic experiment
        '''
        for experiment in self.dyadicExperiments:
            self.results[experiment.getName()] = experiment.computeWholeDyadicExperiment()
        return self.results

    def organizeResultsPerIndividual(self):
        '''
        WARNING: If an animal is in several experiment, this function will give data from only one
        Organize the results dict in a new dict reorganizedResultsPerIndividual
        reorganizedResultsPerIndividual like
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
        if len(self.results) > 0:
            self.reorganizedResultsPerIndividual['metadata'] = {}
            self.reorganizedResultsPerIndividual['habituationPhase'] = {}
            self.reorganizedResultsPerIndividual['socialPhase'] = {}
            for experiment in self.results:
                if len(self.reorganizedResultsPerIndividual['metadata']) == 0:
                    self.reorganizedResultsPerIndividual['metadata'] = self.results[experiment]['metadata'].copy()
                    self.reorganizedResultsPerIndividual['metadata'].pop('animals')
                    self.reorganizedResultsPerIndividual['metadata']['experiments'] = {}
                self.reorganizedResultsPerIndividual['metadata']['experiments'][experiment] = self.results[experiment]['metadata']['animals']

                # Initialization
                habituationVariableList = list(self.results[experiment]['dataHabituation'].keys())
                sexesList = list(self.results[experiment]['dataHabituation'][habituationVariableList[0]].keys())
                genotypeList = list(self.results[experiment]['dataHabituation'][habituationVariableList[0]][sexesList[0]].keys())
                for sex in sexesList:
                    if sex not in self.sexesList:
                        self.sexesList.append(sex)
                        self.reorganizedResultsPerIndividual['habituationPhase'][sex] = {}
                        self.reorganizedResultsPerIndividual['socialPhase'][sex] = {}
                    for genotype in genotypeList:
                        if genotype not in self.genotypeList:
                            self.genotypeList.append(genotype)
                        if genotype not in self.reorganizedResultsPerIndividual['habituationPhase'][sex]:
                            self.reorganizedResultsPerIndividual['habituationPhase'][sex][genotype] = {}
                        if genotype not in self.reorganizedResults['socialPhase'][sex]:
                            self.reorganizedResultsPerIndividual['socialPhase'][sex][genotype] = {}

                        # habituation phase
                        for variable in habituationVariableList:
                            if variable != 'trajectory':
                                if variable not in self.reorganizedResultsPerIndividual['habituationPhase'][sex][genotype]:
                                    self.reorganizedResultsPerIndividual['habituationPhase'][sex][genotype][variable] = {}
                                for animal in self.results[experiment]['dataHabituation'][variable][sex][genotype].keys():
                                    if animal not in self.reorganizedResultsPerIndividual['habituationPhase'][sex][genotype][variable]:
                                        self.reorganizedResultsPerIndividual['habituationPhase'][sex][genotype][variable][animal] = {}
                                    self.reorganizedResultsPerIndividual['habituationPhase'][sex][genotype][variable][animal] = self.results[experiment]['dataHabituation'][variable][sex][genotype][animal]

                # social phase
                for animal in list(self.results[experiment]['dataSocial'].keys()):
                    sex = self.results[experiment]['dataSocial'][animal]['sex']
                    genotype = self.results[experiment]['dataSocial'][animal]['genotype']
                    if len(animal)<=12:
                        # one animal: events from this animal
                        for variable in list(self.results[experiment]['dataSocial'][animal].keys()):
                            if (variable not in self.results[experiment]['metadata']['animals'][animal] and (variable != 'animal') and (variable != 'file')):
                                if variable not in self.reorganizedResultsPerIndividual['socialPhase'][sex][genotype]:
                                    self.reorganizedResultsPerIndividual['socialPhase'][sex][genotype][variable] = {}
                                self.reorganizedResultsPerIndividual['socialPhase'][sex][genotype][variable][animal] = self.results[experiment]['dataSocial'][animal][variable]
                    else:
                        # two animals: shared events
                        # can be a mix of two sexes
                        if sex not in self.reorganizedResultsPerIndividual['socialPhase']:
                            self.reorganizedResultsPerIndividual['socialPhase'][sex] = {}
                        # can be a mix of two genotypes
                        if genotype not in self.reorganizedResultsPerIndividual['socialPhase'][sex]:
                            self.reorganizedResultsPerIndividual['socialPhase'][sex][genotype] = {}
                        for variable in list(self.results[experiment]['dataSocial'][animal].keys()):
                            if ((variable not in self.results[experiment]['metadata']['animals'][list(self.results[experiment]['metadata']['animals'].keys())[0]])
                                    and (variable != 'animal') and (variable != 'file')):
                                if variable not in self.reorganizedResultsPerIndividual['socialPhase'][sex][genotype]:
                                    self.reorganizedResultsPerIndividual['socialPhase'][sex][genotype][variable] = {}
                                self.reorganizedResultsPerIndividual['socialPhase'][sex][genotype][variable][animal] = self.results[experiment]['dataSocial'][animal][variable]
            print("Reorganization finished")
        else:
            print('There is no results to organize.')

    def organizeResults(self):
        '''
        Organize the results dict in a new dict organizedResults
        reorganizedResults like
        {
            'metadata': {
                'experimentName': experimentMetaData,
            },
            'habituationPhase': {
                'experimentName': {
                    'rfid': {
                        'ID': ID,
                        'sex': sex,
                        'name': name,
                        'genotype': genotype,
                        'var1': var1,
                        ...
                        'experimentName': experimentname
                    }
                },
            },
            'socialPhase': {
                the same as habituation phase
            }
        }
        '''
        if len(self.results) > 0:
            self.reorganizedResults['metadata'] = {}
            self.reorganizedResults['habituationPhase'] = {}
            self.reorganizedResults['socialPhase'] = {}

            for experiment in self.results:
                if len(self.reorganizedResults['metadata']) == 0:
                    self.reorganizedResults['metadata'] = self.results[experiment]['metadata'].copy()
                    self.reorganizedResults['metadata'].pop('animals')
                    self.reorganizedResults['metadata']['experiments'] = {}
                self.reorganizedResults['metadata']['experiments'][experiment] = self.results[experiment]['metadata']['animals']

                # Initialization
                self.reorganizedResults['habituationPhase'][experiment] = self.results[experiment]['dataHabituation']
                self.reorganizedResults['socialPhase'][experiment] = self.results[experiment]['dataSocial']

        else:
            print('There is no results to organize.')


    def getReorganizedResults(self):
        if len(self.reorganizedResults) > 0:
            return self.reorganizedResults
        else:
            return "There is no reorganized results."


    def exportReorganizedResultsAsTable(self, nameFile="dyadicResults"):
        if len(self.reorganizedResults) > 0:
            tableHabituationPhase = exportReorganizedResultsAsTable(self.reorganizedResults, "habituationPhase")
            tableSocialPhase = exportReorganizedResultsAsTable(self.reorganizedResults, "socialPhase")
            tableDyadicExperiment = pd.ExcelWriter(f'{nameFile}.xlsx', engine="xlsxwriter")
            tableHabituationPhase.to_excel(tableDyadicExperiment, sheet_name="HabituationPhase")
            tableSocialPhase.to_excel(tableDyadicExperiment, sheet_name="SocialPhase")
            tableDyadicExperiment.close()
        else:
            return "There is no reorganized results."


    def exportReorganizedResultsToJsonFile(self, nameFile="dyadicResults"):
        jsonFile = json.dumps(self.reorganizedResults, indent=4)
        with open(f"{nameFile}.json", "w") as outputFile:
            outputFile.write(jsonFile)



def setAnimalType( aType ):
    global animalType
    animalType = aType



if __name__ == '__main__':

    ### for test
    ## single experiment
    setAnimalType(AnimalType.MOUSE)


    # xp = DyadicExperiment(file, getTrajectory=True)
    # dataHabituation = xp.computeDyadicHabituationPhase()
    # dataSocial = xp.computeDyadicSocialPhase()
    # dataManip = xp.computeWholeDyadicExperiment()

    ## experiment pool test
    # experimentPool = DyadicExperimentPool()
    # experimentPool.addDyadicExperimentWithDialog()
    # experimentPool.setCenterCageCoordinatesExperimentPool(10)
    # experimentPool.computeDyadicBatch()
    # experimentPool.organizeResults()
    # experimentPool.exportReorganizedResultsAsTable("nameTableFile")
    # experimentPool.exportReorganizedResultsToJsonFile("nameJsonFile")


