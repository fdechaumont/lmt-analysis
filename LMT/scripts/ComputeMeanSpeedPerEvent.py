'''
Created on 10. May 2021

@author: Elodie
'''

import matplotlib.pyplot as plt
from lmtanalysis.Animal import *
from lmtanalysis.Event import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.Measure import *
import numpy as np; np.random.seed(0)
from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import getMinTMaxTAndFileNameInput, getMinTMaxTInput
import sqlite3
import seaborn as sns
from lmtanalysis.FileUtil import getFilesToProcess, getJsonFileToProcess

from scripts.ComputeMeasuresIdentityProfileOneMouseAutomatic import *
from USV.experimentList.experimentList import getExperimentList,\
    getAllExperimentList
from USV.lib.vocUtil import cleanVoc, colorAge
from USV.usvEventsCorrelations.Compute_Speed_Duration_Events_With_USV import *
from scipy.spatial.transform import rotation
from USV.figure.figParameter import *
from _collections import OrderedDict
from USV.figure.figUtil import getStarsFromPvalues, addJitter
from scipy.stats.stats import mannwhitneyu
from scipy.stats.morestats import wilcoxon

def computeSpeedDurationPerEvent(animalData, files, tmin, tmax, eventToTest=None):
    print("Compute the speed and duration of specific events ")
    for file in files:
        connection = sqlite3.connect(file)
        pool = AnimalPool()
        pool.loadAnimals(connection)
        pool.loadDetection(tmin, tmax, lightLoad=True)
        rfidList = []
        for animal in pool.animalDictionnary.keys():
            print("computing individual animal: {}".format(animal))
            rfid = pool.animalDictionnary[animal].RFID
            rfidList.append(rfid)

        group = rfidList[0]
        for n in range(1, len(rfidList)):
            group=group+'-'+rfidList[n]

        animalData[file] = {}

        nightEventTimeLine = EventTimeLineCached(connection, file, "night", minFrame=tmin, maxFrame=tmax)
        n = 1

        for eventNight in nightEventTimeLine.getEventList():
            minT = eventNight.startFrame
            maxT = eventNight.endFrame
            print("Night: ", n)
            animalData[file][n] = {}

            for animal in pool.animalDictionnary.keys():
                print("computing individual animal: {}".format(animal))
                rfid = pool.animalDictionnary[animal].RFID
                print("RFID: {}".format(rfid))
                animalData[file][n][rfid] = {}
                # store the animal
                animalData[file][n][rfid]["animal"] = pool.animalDictionnary[animal].name
                animalObject = pool.animalDictionnary[animal]
                animalData[file][n][rfid]["file"] = file
                animalData[file][n][rfid]['genotype'] = pool.animalDictionnary[animal].genotype
                animalData[file][n][rfid]['sex'] = pool.animalDictionnary[animal].sex
                animalData[file][n][rfid]['strain'] = pool.animalDictionnary[animal].strain
                animalData[file][n][rfid]['age'] = pool.animalDictionnary[animal].age
                animalData[file][n][rfid]['group'] = group

                print("computing individual event: {}".format(eventToTest))

                behavEventTimeLine = EventTimeLineCached(connection, file, eventToTest, animal, minFrame=minT, maxFrame=maxT)
                animalData[file][n][rfid]['DurationSpeed'] = []
                animalData[file][n][rfid]['speed'] = []
                for event in behavEventTimeLine.getEventList():
                    results = getDurationSpeed(event=event, animal=animalObject)
                    #print('duration, speed: ', results)
                    animalData[file][n][rfid]['DurationSpeed'].append( results )
                    animalData[file][n][rfid]['speed'].append(results[1])

            n += 1
        connection.close()

    with open("durationSpeedData_{}.json".format(eventToTest), 'w') as jFile:
        json.dump(animalData, jFile, indent=3)

    print("json file created for all data")


def plotBoxplotSpeedPerEvent(dataDic, ax, eventToTest):
    y = dataDic["meanValue"]
    x = dataDic["genotype"]
    genotypeType = list(Counter(x).keys())
    print(genotypeType)
    group = dataDic["exp"]

    print("y: ", y)
    print("x: ", x)
    print("group: ", group)
    experimentType = Counter(group)
    print("Nb of experiments: ", len(experimentType))

    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(min(y) - 0.2 * max(y), max(y) + 0.2 * max(y))
    sns.boxplot(x, y, order=[genotypeType[1], genotypeType[0]], ax=ax, linewidth=0.5, showmeans=True,
                meanprops={"marker": 'o',
                           "markerfacecolor": 'white',
                           "markeredgecolor": 'black',
                           "markersize": '8'}, showfliers=False, width=0.4)
    sns.stripplot(x, y, order=[genotypeType[1], genotypeType[0]], jitter=True, color='black', hue=group, s=5,
                  ax=ax)
    ax.set_title('{} night {}'.format(eventToTest, n))
    ax.set_ylabel("mean speed (cm/s)")
    ax.legend().set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)


def plotBoxplotSpeedPerEventPerSex(dataDic, ax, eventToTest, age):
    dfData = pandas.DataFrame({'group': dataDic["exp"],
                               'age': dataDic["age"],
                               'sex': dataDic["sex"],
                               'value': dataDic["meanValue"]})
    print(dfData)

    dfDataAge = dfData.loc[dfData['age'] == age, :]
    print(dfDataAge)
    y = dfDataAge["value"]
    x = dfDataAge["sex"]

    group = dfDataAge["group"]

    print("y: ", y)
    print("x: ", x)
    print("group: ", group)
    experimentType = Counter(group)
    print("Nb of experiments: ", len(experimentType))

    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(min(y) - 0.2 * max(y), max(y) + 0.2 * max(y))
    sns.boxplot(x, y, order=['male', 'female'], ax=ax, linewidth=0.5, showmeans=True,
                meanprops={"marker": 'o',
                           "markerfacecolor": 'white',
                           "markeredgecolor": 'black',
                           "markersize": '8'}, showfliers=False, width=0.4)
    sns.stripplot(x, y, order=['male', 'female'], jitter=True, color='black', hue=group, s=5,
                  ax=ax)
    ax.set_title('{} night {}'.format(eventToTest, n))
    ax.set_ylabel("mean speed (cm/s)")
    ax.legend().set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)


def testSpeedData(profileData=None, night=0, event=None ):

    print("event: ", event, 'night: ', night)

    profileValueDictionary = getProfileValues(profileData=profileData, night=night, event=event)

    dfData = pandas.DataFrame({'group': profileValueDictionary["exp"],
                               'genotype': profileValueDictionary["genotype"],
                               'value': profileValueDictionary["meanValue"]})

    # Mixed model: variable to explain: value; fixed factor = genotype; random effect: group
    # create model:
    model = smf.mixedlm("value ~ genotype", dfData, groups=dfData["group"])
    # run model:
    result = model.fit()
    # print summary
    print(result.summary())

def testSpeedDataBetweenSexes(profileData=None, night=0, event=None, age=None ):

    print("event: ", event, 'night: ', night, 'age: ', age)

    profileValueDictionary = getProfileValuesNoGroup(profileData=profileData, night=night, event=event)

    dfData = pandas.DataFrame({'group': profileValueDictionary["exp"],
                               'age': profileValueDictionary["age"],
                               'sex': profileValueDictionary["sex"],
                               'value': profileValueDictionary["meanValue"]})

    dfDataAge = dfData.loc[dfData['age'] == age, :]

    # Mixed model: variable to explain: value; fixed factor = genotype; random effect: group
    # create model:
    model = smf.mixedlm("value ~ sex", dfDataAge, groups=dfDataAge["group"])
    # run model:
    result = model.fit()
    # print summary
    print(result.summary())


if __name__ == '__main__':
    '''
    This codes allows to test whether events are different in speed and duration if they occur with USVs or if they occur without USVs.
    '''
    print("Code launched.")

    # set font
    from matplotlib import rc

    rc('font', **{'family': 'serif', 'serif': ['Arial']})

    eventListToTest = ["Contact", "Approach contact", "Break contact", "Get away", "FollowZone Isolated",
                       "Oral-genital Contact", "Train2", "longChase"]
    behavEventListShort = ["Contact", "Approach contact", "Break contact", "FollowZone Isolated",
                           "Oral-genital Contact", "Train2"]
    behavEventListShortPoints = ["Train2", "FollowZone Isolated", "Approach contact", "Break contact"]

    while True:

        question = "Do you want to:"
        question += "\n\t [c] compute the speed and duration for a specific event?"
        question += "\n\t [p] plot the mean speed of animals in a specific event between genotypes"
        question += "\n\t [3] plot the mean speed of animals in a specific event between sexes for each age"
        question += "\n"
        answer = input(question)

        if answer == "c":
            eventToTest = 'Approach contact'
            #eventToTest = 'Get away'
            animalData = {}
            files = getFilesToProcess()
            computeSpeedDurationPerEvent(animalData=animalData, files=files, tmin=0, tmax=3*oneDay, eventToTest=eventToTest)

            break

        if answer == 'p':
            jsonFile = getJsonFileToProcess()
            with open(jsonFile) as json_data:
                durationSpeedData = json.load(json_data)
            print("json file re-imported.")

            eventToTest = 'Break contact'
            nightList = ['1', '2', '3']

            fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 6), sharey=True)

            col = 0

            for n in nightList:
                dataDic = getProfileValues( durationSpeedData, night = str(n), event='speed' )
                testSpeedData(profileData=durationSpeedData, night = str(n), event='speed' )
                ax = axes[col]
                plotBoxplotSpeedPerEvent(dataDic, ax, eventToTest)
                col += 1

            fig.tight_layout()
            fig.savefig('Fig_meanSpeed_{}.pdf'.format(eventToTest), dpi=300)
            plt.close(fig)

            print('Job done.')

            break

        if answer == '3':
            '''This option provides the speed of the mice for each age class to compare between sexes'''
            jsonFile = getJsonFileToProcess()
            with open(jsonFile) as json_data:
                durationSpeedData = json.load(json_data)
            print("json file re-imported.")


            eventToTest = 'Get away'
            nightList = ['1', '2', '3']

            age = '2mo'

            fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 6), sharey=True)

            col = 0

            for n in nightList:
                dataDic = getProfileValuesNoGroup( durationSpeedData, night = str(n), event='speed' )
                testSpeedDataBetweenSexes(profileData=durationSpeedData, night = str(n), event='speed', age=age )
                ax = axes[col]
                plotBoxplotSpeedPerEventPerSex(dataDic, ax, eventToTest, age=age)
                col += 1

            fig.tight_layout()
            fig.savefig('Fig_meanSpeed_{}_{}.pdf'.format(eventToTest, age), dpi=300)
            plt.close(fig)

            print('Job done.')

            break