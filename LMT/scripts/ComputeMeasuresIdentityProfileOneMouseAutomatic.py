'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
import os

from lmtanalysis.FileUtil import getFigureBehaviouralEventsLabelsFrench, behaviouralEventOneMouse, behaviouralEventOneMouseDic, getFigureBehaviouralEventsLabels, categoryList,\
    getJsonFilesToProcess, getJsonFilesWithSpecificNameToProcess
from lmtanalysis.Animal import *
import numpy as np
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
import colorsys
from collections import Counter
import seaborn as sns
import matplotlib.patches as mpatches


from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import getMinTMaxTAndFileNameInput, getColorGeno,\
    getColorGenoTreatment
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.FileUtil import *
from lmtanalysis.Util import getFileNameInput, getStarsFromPvalues
import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas
from scipy.stats import mannwhitneyu, kruskal, ttest_1samp, wilcoxon
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import random
from random import randint
from scipy.stats.morestats import shapiro

def computeProfile(file, minT, maxT, behaviouralEventList):
    
    connection = sqlite3.connect( file )
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    
    indList = []
    for animal in pool.animalDictionary.keys():
        print("computing individual animal: {}".format(animal))
        rfid = pool.animalDictionary[animal].RFID
        indList.append(rfid)

    sortedIndList = sorted(indList)
    print('sorted list: ', sortedIndList)
    groupName = sortedIndList[0]
    for ind in sortedIndList[1:]:
        print('ind: ', ind)
        groupName+='_'
        groupName+=ind

    animalData = {}
    for animal in pool.animalDictionary.keys():
        
        print( "computing individual animal: {}".format( animal )) 
        rfid = pool.animalDictionary[animal].RFID
        print( "RFID: {}".format( rfid ) )
        animalData[rfid]= {}        
        #store the animal
        animalData[rfid]["animal"] = pool.animalDictionary[animal].name
        animalObject = pool.animalDictionary[animal]
        animalData[rfid]["file"] = file
        animalData[rfid]["rfid"] = rfid
        animalData[rfid]['genotype'] = pool.animalDictionary[animal].genotype
        animalData[rfid]['sex'] = pool.animalDictionary[animal].sex
        animalData[rfid]['group'] = groupName
        animalData[rfid]['strain'] = pool.animalDictionary[animal].strain
        animalData[rfid]['age'] = pool.animalDictionary[animal].age
                
        genoA = None
        try:
            genoA=pool.animalDictionary[animal].genotype
        except:
            pass
                    
        for behavEvent in behaviouralEventList:
            
            print( "computing individual event: {}".format(behavEvent))    
            
            behavEventTimeLine = EventTimeLineCached( connection, file, behavEvent, animal, minFrame=minT, maxFrame=maxT )
            #clean the behavioural event timeline:
            behavEventTimeLine.mergeCloseEvents(numberOfFrameBetweenEvent=1)
            behavEventTimeLine.removeEventsBelowLength(maxLen=3)

            totalEventDuration = behavEventTimeLine.getTotalLength()
            nbEvent = behavEventTimeLine.getNumberOfEvent(minFrame = minT, maxFrame = maxT )
            print( "total event duration: " , totalEventDuration )                
            animalData[rfid][behavEventTimeLine.eventName+" TotalLen"] = totalEventDuration
            animalData[rfid][behavEventTimeLine.eventName+" Nb"] = nbEvent
            if nbEvent == 0:
                meanDur = 0
            else:
                meanDur = totalEventDuration / nbEvent
            animalData[rfid][behavEventTimeLine.eventName+" MeanDur"] = meanDur
            
            print(behavEventTimeLine.eventName, genoA, behavEventTimeLine.idA, totalEventDuration, nbEvent, meanDur)

        #compute the total distance traveled (unit = m)
        COMPUTE_TOTAL_DISTANCE = True
        if ( COMPUTE_TOTAL_DISTANCE == True ):
            animalObject.loadDetection( start=minT, end=maxT, lightLoad = True )
            animalData[rfid]["totalDistance"] = animalObject.getDistance( tmin=minT,tmax=maxT)/100
        else:
            animalData[rfid]["totalDistance"] = "totalDistance"


    connection.close()
        
    return animalData


def computeProfilePair(file, minT, maxT, behaviouralEventListSingle, behaviouralEventListSocial):

    print("Start computeProfilePair")

    connection2 = sqlite3.connect(file)
    print(connection2)

    pool = AnimalPool()
    pool.loadAnimals(connection2)

    pair = []
    genotype = []
    sex = []
    age = []
    strain = []
    for animal in pool.animalDictionary.keys():
        rfid = pool.animalDictionary[animal].RFID
        geno = pool.animalDictionary[animal].genotype
        sexAnimal = pool.animalDictionary[animal].sex
        ageAnimal = pool.animalDictionary[animal].age
        strainAnimal = pool.animalDictionary[animal].strain
        pair.append(rfid)
        genotype.append(geno)
        sex.append(sexAnimal)
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

        #compute the profile for single behaviours
        for behavEvent in behaviouralEventListSingle:

            print("computing individual event: {}".format(behavEvent))

            behavEventTimeLine = EventTimeLineCached(connection2, file, behavEvent, animal, minFrame=minT, maxFrame=maxT)
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

            print(behavEventTimeLine.eventName, pool.animalDictionary[animal].genotype, behavEventTimeLine.idA, totalEventDuration, nbEvent, meanDur)

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


def computeProfilePairFromPause(file, experimentDuration, behaviouralEventListSingle, behaviouralEventListSocial):

    print("Start computeProfilePair")

    connection2 = sqlite3.connect(file)
    print(connection2)

    pool = AnimalPool()
    pool.loadAnimals(connection2)
    minT = getStartTestPhase(pool)
    print('minT: '+str(minT))
    maxT = minT + experimentDuration

    print('maxT: '+str(maxT))

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
        #treatmentAnimal = pool.animalDictionary[animal].treatment
        ageAnimal = pool.animalDictionary[animal].age
        strainAnimal = pool.animalDictionary[animal].strain
        pair.append(rfid)
        genotype.append(geno)
        sex.append(sexAnimal)
        #treatment.append(treatmentAnimal)
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
    
    #treatmentPair = ('{}_{}'.format(treatment[0], treatment[1]))

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
    #animalData[pairName]['treatment'] = treatmentPair
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

        #compute the profile for single behaviours
        for behavEvent in behaviouralEventListSingle:

            print("computing individual event: {}".format(behavEvent))

            behavEventTimeLine = EventTimeLineCached(connection2, file, behavEvent, animal, minFrame=minT, maxFrame=maxT)
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

            print(behavEventTimeLine.eventName, pool.animalDictionary[animal].genotype, behavEventTimeLine.idA, totalEventDuration, nbEvent, meanDur)

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


def getProfileValues( profileData, night=None, event=None):
    dataDic = {}
    dataDic["genotype"] = []
    dataDic["value"] = []
    dataDic["meanValue"] = []
    dataDic["exp"] = []
    dataDic['sex'] = []
    dataDic['age'] = []
    dataDic['strain'] = []
    dataDic['group'] = []
    
    for file in profileData.keys():
        print('#####', profileData[file][str(night)].keys())
        for animal in profileData[file][str(night)].keys():
            if not '-' in animal:
                dataDic["value"].append(profileData[file][str(night)][animal][event])
                dataDic["meanValue"].append(np.mean(profileData[file][str(night)][animal][event]))
                dataDic["exp"].append(profileData[file][str(night)][animal]["file"])
                dataDic["genotype"].append(profileData[file][str(night)][animal]["genotype"])
                dataDic["sex"].append(profileData[file][str(night)][animal]["sex"])
                dataDic["age"].append(profileData[file][str(night)][animal]["age"])
                dataDic["strain"].append(profileData[file][str(night)][animal]["strain"])
                dataDic["group"].append(profileData[file][str(night)][animal]["group"])
    
    return dataDic


def getProfileValuesNoGroup(profileData, night='0', event=None):
    dataDic = {}
    dataDic["genotype"] = []
    dataDic["value"] = []
    dataDic["meanValue"] = []
    dataDic["exp"] = []
    dataDic['sex'] = []
    dataDic['age'] = []
    dataDic['strain'] = []
    dataDic['group'] = []

    for file in profileData.keys():
        # print(profileData[file].keys())
        for animal in profileData[file][str(night)].keys():
            if not '_' in animal:
                dataDic["value"].append(profileData[file][str(night)][animal][event])
                dataDic["meanValue"].append(np.mean(profileData[file][str(night)][animal][event]))
                dataDic["exp"].append(profileData[file][str(night)][animal]["file"])
                dataDic["genotype"].append(profileData[file][str(night)][animal]["genotype"])
                dataDic["sex"].append(profileData[file][str(night)][animal]["sex"])
                dataDic["age"].append(profileData[file][str(night)][animal]["age"])
                dataDic["strain"].append(profileData[file][str(night)][animal]["strain"])
                dataDic["group"].append(profileData[file][str(night)][animal]["file"])

    return dataDic


def getProfileValuesPairs(profileData, night='0', event=None):
    dataDic = {}
    dataDic["genotype"] = []
    dataDic["value"] = []
    dataDic["group"] = []
    dataDic["exp"] = []
    dataDic["age"] = []
    dataDic["sex"] = []
    dataDic["strain"] = []

    for file in profileData.keys():
        #print(profileData[file].keys())
        for animal in profileData[file][str(night)].keys():
            #if '-' in animal:
            dataDic["value"].append(profileData[file][str(night)][animal][event])
            dataDic["exp"].append(profileData[file][str(night)][animal]["file"])
            dataDic["group"].append(profileData[file][str(night)][animal]["group"])
            dataDic["genotype"].append(profileData[file][str(night)][animal]["genotype"])
            dataDic["age"].append(profileData[file][str(night)][animal]["age"])
            dataDic["sex"].append(profileData[file][str(night)][animal]["sex"])
            dataDic["strain"].append(profileData[file][str(night)][animal]["strain"])

    return dataDic

def getProfileValuesPairsWithMode(profileData, night='0', event=None, mode=None):
    dataDic = {}
    dataDic['id'] = []
    dataDic["genotype"] = []
    dataDic["value"] = []
    dataDic["group"] = []
    dataDic["exp"] = []
    dataDic["age"] = []
    dataDic["sex"] = []
    dataDic["strain"] = []

    for file in profileData.keys():
        for animal in profileData[file][str(night)].keys():
            if mode == 'dyadic':
                if '_' in animal:
                    print('no _: ', animal)
                    dataDic['id'].append(profileData[file][str(night)][animal]["animal"])
                    dataDic["value"].append(profileData[file][str(night)][animal][event])
                    dataDic["exp"].append(profileData[file][str(night)][animal]["file"])
                    dataDic["group"].append(profileData[file][str(night)][animal]["group"])
                    dataDic["genotype"].append(profileData[file][str(night)][animal]["genotype"])
                    dataDic["age"].append(profileData[file][str(night)][animal]["age"])
                    dataDic["sex"].append(profileData[file][str(night)][animal]["sex"])
                    dataDic["strain"].append(profileData[file][str(night)][animal]["strain"])
            if mode == 'single':
                if not '_' in animal:
                    dataDic['id'].append(profileData[file][str(night)][animal]["animal"])
                    if "totalDistance" in event:
                        dataDic["value"].append(profileData[file][str(night)][animal]["totalDistance"])
                    else:
                        dataDic["value"].append(profileData[file][str(night)][animal][event])
                    dataDic["exp"].append(profileData[file][str(night)][animal]["file"])
                    dataDic["group"].append(profileData[file][str(night)][animal]["group"])
                    dataDic["genotype"].append(profileData[file][str(night)][animal]["genotype"])
                    dataDic["age"].append(profileData[file][str(night)][animal]["age"])
                    dataDic["sex"].append(profileData[file][str(night)][animal]["sex"])
                    dataDic["strain"].append(profileData[file][str(night)][animal]["strain"])

    return dataDic

def plotProfileDataDuration( profileData, behaviouralEventList, night, valueCat ):
    fig, axes = plt.subplots(nrows=4, ncols=6, figsize=(14, 12))
    
    row=0
    col=0
    fig.suptitle(t="{} of events (night {})".format(valueCat, night), y=1.2, fontweight= 'bold')
    
    #plot the data for each behavioural event
    for behavEvent in behaviouralEventList+['totalDistance']:

        singlePlotPerEventProfile(profileData, night, valueCat, behavEvent, ax=axes[row, col])
        
        if col<5:
            col+=1
            row=row
        else:
            col=0
            row+=1

    fig.tight_layout()    
    fig.savefig( "FigProfile{}_Events_night_{}.pdf".format( valueCat, night ) ,dpi=100)
    plt.close( fig )


def plotProfileDataDurationPerGroup( profileData, behaviouralEventList, night, valueCat, genoRef, text_file ):
    if valueCat == ' TotalLen':
        nRow = 3
        nCol = 5
    if valueCat == ' Nb':
        nRow = 4
        nCol = 5
    if valueCat == ' MeanDur':
        nRow = 4
        nCol = 4
        
    fig, axes = plt.subplots(nrows=nRow, ncols=nCol, figsize=(nCol*2.2, nRow*3))
    
    row=0
    col=0
    fig.suptitle(t="{} of events (night {})".format(valueCat, night), y=1.2, fontweight= 'bold')
    letterList = list(string.ascii_uppercase)
    k = 0
    #plot the data for each behavioural event
    for behavEvent in behaviouralEventList:
        ax = axes[row, col]
        singlePlotPerEventProfilePerGroup(profileData, night, valueCat, behavEvent, ax=ax, genoRef=genoRef, letter = letterList[k], text_file=text_file)
           
        text_file.write("Test for the event: {} night {}".format( behavEvent, night ) )
        
        profileValueDictionary = getProfileValues(profileData=profileData, night=night, event=behavEvent)
        k += 1
        dfData = pandas.DataFrame({'group': profileValueDictionary["exp"],
                                   'genotype': profileValueDictionary["genotype"],
                                   'value': profileValueDictionary["value"]})

        maxCol = nCol - 1
        if col<maxCol:
            col+=1
            row=row
        else:
            col=0
            row+=1

    fig.tight_layout()    
    fig.savefig( "FigProfile_{}_Events_night_{}.pdf".format( valueCat, night ) ,dpi=100)
    fig.savefig( "FigProfile_{}_Events_night_{}.png".format( valueCat, night ) ,dpi=300)
    plt.close( fig )


def singlePlotPerEventProfile(profileData, night, valueCat, behavEvent, ax):
    if behavEvent != 'totalDistance':
        event = behavEvent + valueCat

    elif behavEvent == 'totalDistance':
        event = behavEvent
    print("event: ", event)

    profileValueDictionary = getProfileValues(profileData=profileData, night=night, event=event)
    yval = profileValueDictionary["value"]
    x = profileValueDictionary["genotype"]
    genotypeType = list(Counter(x).keys())
    print(genotypeType)
    genotypeType.sort(reverse=True)
    print('x labels: ', genotypeType)
    group = profileValueDictionary["exp"]

    if (valueCat == ' TotalLen') & (behavEvent != 'totalDistance'):
        y = [i / 30 for i in yval]
    else:
        y = yval


    print("y: ", y)
    print("x: ", x)
    print("group: ", group)
    experimentType = Counter(group)
    print("Nb of experiments: ", len(experimentType))

    ax.set_xlim(-0.5, len(genotypeType))
    ax.set_ylim(min(y) - 0.2 * max(y), max(y) + 0.2 * max(y))
    sns.boxplot(x=x, y=y, order=genotypeType, ax=ax, linewidth=0.5, showmeans=True,
                meanprops={"marker": 'o',
                           "markerfacecolor": 'white',
                           "markeredgecolor": 'black',
                           "markersize": '8'}, color='white', showfliers=False, width=0.4)
    #sns.stripplot(x=x, y=y, order=genotypeType, jitter=True, color='black', hue=group, s=5, ax=ax)
    sns.stripplot(x=x, y=y, order=genotypeType, jitter=True, hue=group, s=5, ax=ax)
    ax.set_title(behavEvent)
    labelTxtDic = {' TotalLen': 'duration (s)', ' MeanDur': 'mean duration (frames)', ' Nb': 'occurrences'}
    labelTxt = labelTxtDic[valueCat]
    if behavEvent == 'totalDistance':
        labelTxt = 'total distance (m)'
    ax.set_ylabel(labelTxt)
    ax.legend().set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    print('x tick labels: ', genotypeType)
    ax.set_xticklabels(genotypeType, rotation=30, fontsize=10, horizontalalignment='right')


def singlePlotPerEventProfilePerGroup(profileData, night, valueCat, behavEvent, genoRef, ax, letter, text_file):
    
    event = behavEvent
    print("event: ", event)

    profileValueDictionary = getProfileValues(profileData=profileData, night=night, event=event)
    yval = profileValueDictionary["value"]
    x = profileValueDictionary["genotype"]
    genotypeType = list(Counter(x).keys())
    print(genotypeType)
    genotypeType.sort(reverse=True)
    print('x labels: ', genotypeType)
    group = profileValueDictionary["exp"]

    if (valueCat == ' TotalLen') & (behavEvent != 'totalDistance'):
        y = [i / 30 for i in yval]
    else:
        y = yval


    print("y: ", y)
    print("x: ", x)
    print("group: ", group)
    experimentType = Counter(group)
    print("Nb of experiments: ", len(experimentType))

    ax.set_xlim(-0.5, len(genotypeType))
    yMin = min(y) - 0.2 * max(y)
    yMax = max(y) + 0.2 * max(y)
    ax.set_ylim(yMin, yMax)
    sns.boxplot(x=x, y=y, order=genotypeType, ax=ax, linewidth=0.5, showmeans=True,
                meanprops={"marker": 'o',
                           "markerfacecolor": 'white',
                           "markeredgecolor": 'black',
                           "markersize": '8'}, color='white', showfliers=False, width=0.4)
    #sns.stripplot(x=x, y=y, order=genotypeType, jitter=True, color='black', hue=group, s=5, ax=ax)
    sns.stripplot(x=x, y=y, order=genotypeType, jitter=True, hue=group, s=5, ax=ax)
    if behavEvent == 'totalDistance':
        titleEvent = behavEvent
    else:
        titleEvent = behavEvent[0:behavEvent.find(valueCat)]
    ax.set_title(getFigureBehaviouralEventsLabels(titleEvent))
    labelTxtDic = {' TotalLen': 'duration (s)', ' MeanDur': 'mean duration (frames)', ' Nb': 'occurrences'}
    labelTxt = labelTxtDic[valueCat]
    if behavEvent == 'totalDistance':
        labelTxt = 'total distance (m)'
    ax.set_ylabel(labelTxt)
    ax.legend().set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    print('x tick labels: ', genotypeType)
    ax.set_xticklabels(genotypeType, rotation=30, fontsize=10, horizontalalignment='right')
      
    
    text_file.write("Test for the event: {} night {}".format( event, night ) )
        
    profileValueDictionary = getProfileValues(profileData=profileData, night=night, event=event)
    
    dfData = pandas.DataFrame({'group': profileValueDictionary["exp"],
                               'genotype': profileValueDictionary["genotype"],
                               'value': profileValueDictionary["value"]})

    
    #pandas.DataFrame(dfData).info()
    #Mixed model: variable to explain: value; fixed factor = genotype; random effect: group
    #create model:
    model = smf.mixedlm("value ~ genotype", dfData, groups = dfData["group"])
    #run model: 
    result = model.fit()
    #print summary
    print(result.summary())
    p = extractPValueFromLMMResult(result, keyword=genoRef)
    print(p)
    
    ax.text(0.5, yMax-0.1*(yMax-yMin), getStarsFromPvalues(p[0], 1), fontsize=18, horizontalalignment='center', color='black', weight='bold')

    #ax.text(x=-0.1, y = yMax, s=letter, fontsize=22, fontweight='bold', horizontalalignment='left', transform=ax.transAxes)
    
    text_file.write(result.summary().as_text())
    text_file.write('\n')
    

def singlePlotPerEventProfilePairs(profileData, night, valueCat, behavEvent, ax, image, imgPos, zoom, letter):
    if behavEvent != 'totalDistance':
        event = behavEvent + valueCat

    elif behavEvent == 'totalDistance':
        event = behavEvent
    print("event: ", event)

    profileValueDictionary = getProfileValuesPairs(profileData=profileData, night=night, event=event)
    yval = profileValueDictionary["value"]
    x = profileValueDictionary["genotype"]
    genotypeType = list(Counter(x).keys())
    print(genotypeType)
    group = profileValueDictionary["exp"]

    if valueCat == ' TotalLen':
        y = [i / 30 for i in yval]
    else:
        y = yval


    print("y: ", y)
    print("x: ", x)
    print("group: ", group)
    experimentType = Counter(group)
    print("Nb of experiments: ", len(experimentType))

    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(min(y) - 0.1 * (max(y) - min(y)), max(y) + 0.3 * (max(y) - min(y)))
    sns.boxplot(x=x, y=y, order=[genotypeType[0], genotypeType[1]], ax=ax, linewidth=0.5, showmeans=True,
                meanprops={"marker": 'o',
                           "markerfacecolor": 'white',
                           "markeredgecolor": 'black',
                           "markersize": '8'}, showfliers=False, width=0.4)
    sns.stripplot(x=x, y=y, order=[genotypeType[0], genotypeType[1]], jitter=True, color='black', hue=group, s=5,
                  ax=ax)
    ax.set_title( getFigureBehaviouralEventsLabelsFrench(behavEvent), y=1.05 )
    ax.set_ylabel("{} (s)".format(valueCat))
    ax.legend().set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.text(-1, max(y) + 0.4 * (max(y) - min(y)), letter, fontsize=20, horizontalalignment='center', color='black',
            weight='bold')

    behavSchema = mpimg.imread(image)
    imgBox = OffsetImage(behavSchema, zoom=zoom)
    imageBox = AnnotationBbox(imgBox, imgPos, frameon=False)
    ax.add_artist(imageBox)

    #stats
    df = pandas.DataFrame(profileValueDictionary)
    genotypeType[0]
    val = {}
    for geno in genotypeType:
        val[geno] = df['value'][df['genotype']==geno]
        print(geno, val[geno])
    W, p = mannwhitneyu(val[genotypeType[0]], val[genotypeType[1]])
    print('Mann-Whitney U test for {}: W={} p={}'.format( behavEvent, W, p ))
    ax.text(0.5, max(y) - 0.05 * (max(y)-min(y)), getStarsFromPvalues(p, 1), fontsize=20, horizontalalignment='center', color='black', weight='bold')


def singlePlotPerEventProfileBothSexes(profileDataM, profileDataF, night, valueCat, behavEvent, ax, letter, text_file, image, imgPos, zoom):
    if behavEvent != 'totalDistance':
        event = behavEvent + valueCat

    elif behavEvent == 'totalDistance':
        event = behavEvent
    print("event: ", event)

    #upload data for males:
    profileValueDictionaryM = getProfileValues(profileData=profileDataM, night=night, event=event)
    yvalM = profileValueDictionaryM["value"]
    xM = profileValueDictionaryM["genotype"]
    genotypeTypeM = list(Counter(xM).keys())
    print(genotypeTypeM)
    groupM = profileValueDictionaryM["exp"]
    sexM = ['male'] * len(xM)

    # upload data for females:
    profileValueDictionaryF = getProfileValues(profileData=profileDataF, night=night, event=event)
    yvalF = profileValueDictionaryF["value"]
    xF = profileValueDictionaryF["genotype"]
    genotypeTypeF = list(Counter(xF).keys())
    print(genotypeTypeF)
    groupF = profileValueDictionaryF["exp"]
    sexF = ['female'] * len(xF)

    #merge data for males and females:
    yval = yvalM + yvalF
    x = xM + xF
    group = groupM + groupF
    sex = sexM + sexF
    genotypeType = list(Counter(x).keys())
    print(genotypeType)


    if valueCat == ' TotalLen':
        y = [i / 30 for i in yval]
    else:
        y = yval


    print("y: ", y)
    print("x: ", x)
    print("group: ", group)
    experimentType = Counter(group)
    print("Nb of experiments: ", len(experimentType))

    ax.text(-1, max(y) + 0.5 * (max(y) - min(y)), letter, fontsize=18, horizontalalignment='center', color='black', weight='bold')
    ax.set_ylim(min(y) - 0.2 * (max(y)-min(y)), max(y) + 0.4 * (max(y)-min(y)))
    bp = sns.boxplot(x=sex, y=y, hue=x, hue_order=reversed(genotypeType), ax=ax, linewidth=0.5, showmeans=True,
                meanprops={"marker": 'o',
                           "markerfacecolor": 'white',
                           "markeredgecolor": 'black',
                           "markersize": '8'}, showfliers=False, width=0.8, dodge=True)
    # Add transparency to colors
    '''for patch in bp.artists:
        r, g, b, a = patch.get_facecolor()
        patch.set_facecolor((r, g, b, .7))'''

    sns.stripplot(x=sex, y=y, hue=x, hue_order=reversed(genotypeType), jitter=True, color='black', s=5,
                  dodge=True, ax=ax)
    ax.set_title(behavEvent, y=1, fontsize=14)
    ax.xaxis.set_tick_params(direction="in")
    ax.tick_params(axis='x', labelsize=14)
    ax.yaxis.set_tick_params(direction="in")
    ax.tick_params(axis='y', labelsize=12)
    if valueCat == ' TotalLen':
        ylabel = 'total duration (s)'
    if valueCat == ' Nb':
        ylabel = 'occurrences'
    if valueCat == ' MeanDur':
        ylabel = 'mean duration (s)'
    elif valueCat == '':
        if event == 'totalDistance':
            ylabel = 'distance (m)'
        else:
            ylabel = event+' (m)'
        
    ax.set_ylabel(ylabel, fontsize=14)
    ax.legend().set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    behavSchema = mpimg.imread(image)
    imgBox = OffsetImage(behavSchema, zoom=zoom)
    imageBox = AnnotationBbox(imgBox, imgPos, frameon=False)
    ax.add_artist(imageBox)


    # Mixed model: variable to explain: value; fixed factor = genotype; random effect: group
    dataDict = {'value': y, 'sex': sex, 'genotype': x, 'group': group}
    dfDataBothSexes = pd.DataFrame(dataDict)
    n = 0
    for sexClass in ['male', 'female']:
        dfData = dfDataBothSexes[dfDataBothSexes['sex'] == sexClass]
        # create model:
        model = smf.mixedlm("value ~ genotype", dfData, groups=dfData["group"])
        # run model:
        result = model.fit()
        # print summary
        print(behavEvent, sexClass)
        print(result.summary())
        text_file.write('{} {} {}'.format(behavEvent, valueCat, sexClass))
        text_file.write(result.summary().as_text())
        text_file.write('\n')
        p, sign = extractPValueFromLMMResult(result=result, keyword='+')
        #add p-values on the plot
        ax.text(n, max(y) + 0.1 * (max(y)-min(y)), getStarsFromPvalues(p, 1), fontsize=16, horizontalalignment='center', color='black', weight='bold')
        n += 1


def singlePlotPerEventProfileBothSexesPerGroup(profileDataM, profileDataF, night, valueCat, behavEvent, ax, letter, text_file, image, imgPos, zoom):
    
    event = behavEvent
    print("event: ", event)

    #upload data for males:
    profileValueDictionaryM = getProfileValues(profileData=profileDataM, night=night, event=event)
    yvalM = profileValueDictionaryM["value"]
    xM = profileValueDictionaryM["genotype"]
    genotypeTypeM = list(Counter(xM).keys())
    print(genotypeTypeM)
    groupM = profileValueDictionaryM["exp"]
    sexM = ['male'] * len(xM)

    # upload data for females:
    profileValueDictionaryF = getProfileValues(profileData=profileDataF, night=night, event=event)
    yvalF = profileValueDictionaryF["value"]
    xF = profileValueDictionaryF["genotype"]
    genotypeTypeF = list(Counter(xF).keys())
    print(genotypeTypeF)
    groupF = profileValueDictionaryF["exp"]
    sexF = ['female'] * len(xF)

    #merge data for males and females:
    yval = yvalM + yvalF
    x = xM + xF
    group = groupM + groupF
    sex = sexM + sexF
    genotypeType = list(Counter(x).keys())
    print(genotypeType)

    paletteDic = getColorPalette(genoList = genotypeType)

    if valueCat == ' TotalLen':
        if event != 'totalDistance':
            y = [i / 30 for i in yval]
        if event == 'totalDistance':
            y = yval
    else:
        y = yval


    print("y: ", y)
    print("x: ", x)
    print("group: ", group)
    experimentType = Counter(group)
    print("Nb of experiments: ", len(experimentType))

    ax.text(-0.3, 1.05, letter, fontsize=18, horizontalalignment='center', color='black', weight='bold', transform=ax.transAxes)
    ax.set_ylim(min(y) - 0.2 * (max(y)-min(y)), max(y) + 0.4 * (max(y)-min(y)))
    bp = sns.boxplot(x=sex, y=y, hue=x, hue_order=reversed(genotypeType), ax=ax, linewidth=0.5, showmeans=True,
                meanprops={"marker": 'o',
                           "markerfacecolor": 'white',
                           "markeredgecolor": 'black',
                           "markersize": '8'}, showfliers=False, width=0.8, palette=paletteDic, dodge=True)
    # Add transparency to colors
    '''for patch in bp.artists:
        r, g, b, a = patch.get_facecolor()
        patch.set_facecolor((r, g, b, .7))'''

    sns.stripplot(x=sex, y=y, hue=x, hue_order=reversed(genotypeType), jitter=True, color='black', s=5,
                  dodge=True, ax=ax)
    
    if event == 'totalDistance':
        titleEvent = event
    else:
        titleEvent = event[0:event.find(valueCat)]
    print('###########title: ', titleEvent)
    ax.set_title(getFigureBehaviouralEventsLabels(titleEvent), y=1, fontsize=12)
    
    ax.xaxis.set_tick_params(direction="in")
    ax.tick_params(axis='x', labelsize=14)
    ax.yaxis.set_tick_params(direction="in")
    ax.tick_params(axis='y', labelsize=12)
    if valueCat == ' TotalLen':
        ylabel = 'total duration (s)'
    if valueCat == ' Nb':
        ylabel = 'occurrences'
    if valueCat == ' MeanDur':
        ylabel = 'mean duration (frames)'
    
    if event == 'totalDistance':
        ylabel = 'distance (m)'
        
        
    ax.set_ylabel(ylabel, fontsize=14)
    ax.legend().set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    behavSchema = mpimg.imread(image)
    imgBox = OffsetImage(behavSchema, zoom=zoom)
    imageBox = AnnotationBbox(imgBox, imgPos, frameon=False)
    ax.add_artist(imageBox)


    # Mixed model: variable to explain: value; fixed factor = genotype; random effect: group
    dataDict = {'value': y, 'sex': sex, 'genotype': x, 'group': group}
    dfDataBothSexes = pd.DataFrame(dataDict)
    n = {"male": 0.25, "female": 0.75}
    for sexClass in ['male', 'female']:
        dfData = dfDataBothSexes[dfDataBothSexes['sex'] == sexClass]
        # create model:
        model = smf.mixedlm("value ~ genotype", dfData, groups=dfData["group"])
        # run model:
        result = model.fit()
        # print summary
        print(behavEvent, sexClass)
        print(result.summary())
        text_file.write('{} {} {}'.format(behavEvent, valueCat, sexClass))
        text_file.write(result.summary().as_text())
        text_file.write('\n')
        p, sign = extractPValueFromLMMResult(result=result, keyword='wt')
        #add p-values on the plot
        ax.text(n[sexClass], 0.9, getStarsFromPvalues(p, 1), fontsize=16, horizontalalignment='center', color='black', weight='bold', transform=ax.transAxes)

        

def singlePlotPerEventProfilePairBothSexes(profileDataM, profileDataF, night, valueCat, behavEvent, ax, letter, text_file, image, zoom, mode):
    if behavEvent != 'totalDistance':
        event = behavEvent + valueCat

    elif behavEvent == 'totalDistance':
        event = behavEvent
    print("event: ", event)

    #upload data for males:
    profileValueDictionaryM = getProfileValues(profileData=profileDataM, night=night, event=event)
    yvalM = profileValueDictionaryM["value"]
    xM = profileValueDictionaryM["genotype"]
    genotypeTypeM = list(Counter(xM).keys())
    print(genotypeTypeM)
    groupM = profileValueDictionaryM["exp"]
    sexM = ['male'] * len(xM)

    # upload data for females:
    profileValueDictionaryF = getProfileValues(profileData=profileDataF, night=night, event=event)
    yvalF = profileValueDictionaryF["value"]
    xF = profileValueDictionaryF["genotype"]
    genotypeTypeF = list(Counter(xF).keys())
    print(genotypeTypeF)
    groupF = profileValueDictionaryF["exp"]
    sexF = ['female'] * len(xF)

    #merge data for males and females:
    yval = yvalM + yvalF
    x = xM + xF
    group = groupM + groupF
    sex = sexM + sexF
    genotypeType = list(Counter(x).keys())
    print(genotypeType)
    orderedGenotypeType = list(sorted(genotypeType))
    print(orderedGenotypeType)
    print('order graph: ', list(reversed(orderedGenotypeType)))

    if valueCat == ' TotalLen':
        y = [i / 30 for i in yval]
    else:
        y = yval


    print("y: ", y)
    print("x: ", x)
    print("group: ", group)
    experimentType = Counter(group)
    print("Nb of experiments: ", len(experimentType))

    ax.text(-1, max(y) + 0.5 * (max(y) - min(y)), letter, fontsize=20, horizontalalignment='center', color='black', weight='bold')
    ax.set_ylim(min(y) - 0.2 * (max(y)-min(y)), max(y) + 0.4 * (max(y)-min(y)))
    bp = sns.boxplot(x=sex, y=y, hue=x, hue_order=list(reversed(orderedGenotypeType)), ax=ax, linewidth=0.5, showmeans=True,
                meanprops={"marker": 'o',
                           "markerfacecolor": 'white',
                           "markeredgecolor": 'black',
                           "markersize": '8'}, showfliers=False, width=0.8, dodge=True)
    # Add transparency to colors
    '''for patch in bp.artists:
        r, g, b, a = patch.get_facecolor()
        patch.set_facecolor((r, g, b, .7))'''

    sns.stripplot(x=sex, y=y, hue=x, hue_order=list(reversed(orderedGenotypeType)), jitter=True, color='black', s=5,
                  dodge=True, ax=ax)
    ax.set_title(behavEvent, y=1, fontsize=14)
    ax.xaxis.set_tick_params(direction="in")
    ax.tick_params(axis='x', labelsize=14)
    ax.yaxis.set_tick_params(direction="in")
    ax.tick_params(axis='y', labelsize=12)
    if valueCat == ' TotalLen':
        ylabel = 'total duration (s)'
    if valueCat == ' Nb':
        ylabel = 'occurrences'
    if valueCat == ' MeanDur':
        ylabel = 'mean duration (s)'
    elif valueCat == '':
        ylabel = event+' (m)'
    ax.set_ylabel(ylabel, fontsize=14)
    ax.legend().set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    behavSchema = mpimg.imread(image)
    imgBox = OffsetImage(behavSchema, zoom=zoom)
    imageBox = AnnotationBbox(imgBox, (0.5, max(y) + 0.25 * (max(y)-min(y))), frameon=False)
    ax.add_artist(imageBox)


    #Mann-Whitney U tests:
    dataDict = {'value': y, 'sex': sex, 'genotype': x, 'group': group}
    dfDataBothSexes = pd.DataFrame(dataDict)
    if mode == 'dyadic':
        n = 0
        dfData = {}
        for sexClass in ['male', 'female']:
            dfData[sexClass] = {}
            for geno in reversed(genotypeType):
                dfData[sexClass][geno] = dfDataBothSexes[(dfDataBothSexes['sex'] == sexClass) & (dfDataBothSexes['genotype'] == geno)]
                print(geno, dfData[sexClass][geno])
            U, p = mannwhitneyu(dfData[sexClass][orderedGenotypeType[-1]]['value'], dfData[sexClass][orderedGenotypeType[-2]]['value'])
            print('means of ', orderedGenotypeType[-1], np.mean(dfData[sexClass][orderedGenotypeType[-1]]['value']), 'mean of ', orderedGenotypeType[-2],
                  np.mean(dfData[sexClass][orderedGenotypeType[-2]]['value']))
            # add p-values on the plot
            ax.text(n, max(y) + 0.2 * (max(y)-min(y)), getStarsFromPvalues(p, 1), fontsize=18, horizontalalignment='center', color='black', weight='bold')
            n += 1


    elif mode == 'single':
        n = 0
        for sexClass in ['male', 'female']:
            dfData = dfDataBothSexes.loc[dfDataBothSexes['sex']==sexClass, :]

            """print("event single: ", event)
            text_file.write("Test for the event: {} night {}".format(event, night))

            dfData = pandas.DataFrame({'group': profileValueDictionary["exp"],
                                       'genotype': profileValueDictionary["genotype"],
                                       'value': profileValueDictionary["value"]})
"""
            genotypeCat = list(Counter(dfData['genotype']).keys())
            genotypeCat.sort(reverse=True)
            print(genotypeCat)
            data = {}
            for k in [0, 1]:
                data[genotypeCat[k]] = dfData['value'][dfData['genotype'] == genotypeCat[k]]
            print('means of ', genotypeCat[0], np.mean(data[genotypeCat[0]]), 'mean of ', genotypeCat[1],
                  np.mean(data[genotypeCat[1]]))
            # create model: value as a function of genotype, with the factor of the cage:
            model = smf.mixedlm("value ~ genotype", dfData, groups=dfData["group"])
            # run model:
            result = model.fit()
            # print summary
            print(result.summary())
            '''p, sign = extractPValueFromLMMResult(result=result, keyword=genotypeCat[1])
            axes[row, col].text(x=0.5, y=max(y)+ 0.1 * max(y),
                                s=getStarsFromPvalues(p, numberOfTests=1), fontsize=14, ha='center')'''
            p, sign = extractPValueFromLMMResult(result=result, keyword=genotypeCat[0])
            ax.text(x=n, y=max(y) + 0.2 * (max(y)-min(y)),
                                s=getStarsFromPvalues(p, numberOfTests=1), fontsize=18, ha='center')
            '''p, sign = extractPValueFromLMMResult(result=result, keyword=genotypeCat[1])
            axes[row, col].text(x=1, y=max(y) + 0.1 * max(y),
                                s=getStarsFromPvalues(p, numberOfTests=1), fontsize=14, ha='center')'''
            text_file.write(result.summary().as_text())
            text_file.write('\n')

            n += 1


def plotProfileDataDurationPairs( ax, profileData, night, valueCat, behavEvent, mode, text_file, letter=None ):
    # plot the data for each behavioural event
    if behavEvent != 'totalDistance':
        event = behavEvent + valueCat

    elif behavEvent == 'totalDistance':
        event = behavEvent
    print("event: ", event)

    #profileValueDictionary = getProfileValuesPairs(profileData=profileData, night=night, event=event)
    profileValueDictionary = getProfileValuesPairsWithMode(profileData=profileData, night=night, event=event, mode=mode)
    yval = profileValueDictionary["value"]
    x = profileValueDictionary["genotype"]
    
    if (valueCat == ' TotalLen') & (behavEvent != 'totalDistance'):
        y = [i / 30 for i in yval]
    else:
        y = yval
        
    group = profileValueDictionary["exp"]

    genotypeCat = list(Counter(x))
    genotypeCat.sort(reverse=True)
    print('genotype list: ', genotypeCat)

    #print("y: ", y)
    #print("x: ", x)
    #print("group: ", group)
    experimentType = Counter(group)
    print("Nb of experiments: ", len(experimentType))
    #generate color palette
    my_pal = getColorPalette( genoList = genotypeCat )
    
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(min(y) - 0.2 * (max(y)-min(y)), max(y) + 0.4 * (max(y)-min(y)))
    sns.boxplot(x=x, y=y, ax=ax, hue=x, order=genotypeCat, linewidth=0.5, showmeans=True,
                meanprops={"marker": 'o',
                           "markerfacecolor": 'white',
                           "markeredgecolor": 'black',
                           "markersize": '10'}, showfliers=False, palette=my_pal )
    #sns.stripplot(x=x, y=y, jitter=True, hue=group, s=5, ax=ax)
    sns.stripplot(x=x, y=y, jitter=True, order=genotypeCat, color='black', s=5, ax=ax)
    ax.set_title(getFigureBehaviouralEventsLabels(behavEvent), y=1, fontsize=16, weight='bold')
    
    ax.xaxis.set_tick_params(direction="in")
    ax.tick_params(axis='x', labelsize=14)
    ax.yaxis.set_tick_params(direction="in")
    ax.tick_params(axis='y', labelsize=12)
    if valueCat == ' TotalLen':
        ylabel = 'total duration (s)'
    if valueCat == ' Nb':
        ylabel = 'occurrences'
    if valueCat == ' MeanDur':
        ylabel = 'mean duration (frames)'
    
    if event == 'totalDistance':
        ylabel = 'distance (m)'
    ax.set_ylabel(ylabel, fontsize=14)
    #xlabels = [getShorterGenoNames(longGenoName=x) for x in genotypeCat]
    xlabels = genotypeCat
    ax.set_xticklabels(xlabels, fontsize=12)
    
    ax.legend().set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.text(x=-1, y=max(y) + 0.2 * max(y), s=letter, fontsize=18, weight='bold')

    if mode == 'dyadic':

        print("event dyadic: ", event)
        text_file.write("Test for the event: {} night {} ".format(event, night))
        text_file.write('\n')

        dfData = pandas.DataFrame({'group': profileValueDictionary["exp"],
                                   'genotype': profileValueDictionary["genotype"],
                                   'value': profileValueDictionary["value"]})

        # Mann-Whitney U test, non parametric, small sample size
        genotypeCat = list(Counter(dfData['genotype']).keys())
        genotypeCat.sort(reverse=True)
        print('genotype list: ', genotypeCat)
        data = {}
        for k in [0,1]:
            data[genotypeCat[k]] = dfData['value'][dfData['genotype'] == genotypeCat[k]]
        U, p = mannwhitneyu( data[genotypeCat[0]], data[genotypeCat[1]])
        print('means of ', genotypeCat[0], np.mean(data[genotypeCat[0]]), 'mean of ', genotypeCat[1], np.mean(data[genotypeCat[1]]))
        print( 'Mann-Whitney U test ({} {} cages, {} {} cages) {}: U={}, p={}'.format(len(data[genotypeCat[0]]), genotypeCat[0], len(data[genotypeCat[1]]), genotypeCat[1], event, U, p) )
        text_file.write('Mann-Whitney U test ({} {} cages, {} {} cages) {}: U={}, p={}'.format(len(data[genotypeCat[0]]), genotypeCat[0], len(data[genotypeCat[1]]), genotypeCat[1], event, U, p))
        ax.text(x=0.5, y=max(y) + 0.25 * (max(y)-min(y)), s = getStarsFromPvalues(p,numberOfTests=1), fontsize=16, ha='center' , weight='bold')
        text_file.write('\n')

    elif mode == 'single':

        print("event single: ", event)
        text_file.write("Test for the event: {} night {}".format(event, night))

        dfData = pandas.DataFrame({'group': profileValueDictionary["exp"],
                                   'genotype': profileValueDictionary["genotype"],
                                   'value': profileValueDictionary["value"]})
        #dfData.loc[dfData["genotype"] != "Baseline"]
        
        genotypeCat = list(Counter(dfData['genotype']).keys())
        genotypeCat.sort(reverse=True)
        print(genotypeCat)
        data = {}
        for k in [0,1]:
            data[genotypeCat[k]] = dfData['value'][dfData['genotype'] == genotypeCat[k]]
        print('means of ', genotypeCat[0], np.mean(data[genotypeCat[0]]), 'mean of ', genotypeCat[1], np.mean(data[genotypeCat[1]]))
        # create model: value as a function of genotype, with the factor of the cage:
        model = smf.mixedlm("value ~ genotype", dfData, groups=dfData["group"])
        # run model:
        result = model.fit()
        # print summary
        print(result.summary())
        '''p, sign = extractPValueFromLMMResult(result=result, keyword=genotypeCat[1])
        ax.text(x=0.5, y=max(y)+ 0.1 * max(y),
                            s=getStarsFromPvalues(p, numberOfTests=1), fontsize=14, ha='center')'''
        p, sign = extractPValueFromLMMResult(result=result, keyword=genotypeCat[0])
        ax.text(x=0.5, y=max(y) + 0.25 * (max(y)-min(y)),
                            s=getStarsFromPvalues(p, numberOfTests=1), fontsize=16, ha='center', weight='bold')
        '''p, sign = extractPValueFromLMMResult(result=result, keyword=genotypeCat[1])
        ax.text(x=1, y=max(y) + 0.1 * max(y),
                            s=getStarsFromPvalues(p, numberOfTests=1), fontsize=14, ha='center')'''
        text_file.write(result.summary().as_text())
        text_file.write('\n')


def plotProfileDataDurationPairsDiffGeno( axes, row, col, profileData, night, valueCat, behavEvent, mode, text_file ):
    # plot the data for each behavioural event
    if behavEvent != 'totalDistance':
        event = behavEvent + valueCat

    elif behavEvent == 'totalDistance':
        event = behavEvent
    print("event: ", event)

    profileValueDictionary = getProfileValuesPairsWithMode(profileData=profileData, night=night, event=event, mode=mode)
    yval = profileValueDictionary["value"]
    if (valueCat == ' TotalLen') & (behavEvent != 'totalDistance'):
        y = [i / 30 for i in yval]
    else:
        y = yval
    x = profileValueDictionary["genotype"]
    group = profileValueDictionary["exp"]
    
    genotypeCat = list(Counter(x))
    genotypeCat.sort(reverse=True)
    print('genotype list: ', genotypeCat)

    #print("y: ", y)
    #print("x: ", x)
    #print("group: ", group)
    experimentType = Counter(group)
    print("Nb of experiments: ", len(experimentType))

    axes[row, col].set_xlim(-0.5, 1.5)
    axes[row, col].set_ylim(min(y) - 0.2 * max(y), max(y) + 0.2 * max(y))
    sns.boxplot(x=x, y=y, ax=axes[row, col], order=genotypeCat, linewidth=0.5, showmeans=True,
                meanprops={"marker": 'o',
                           "markerfacecolor": 'white',
                           "markeredgecolor": 'black',
                           "markersize": '10'}, showfliers=False, palette=[getColorGeno(geno) for geno in genotypeCat])
    #sns.stripplot(x=x, y=y, jitter=True, hue=group, s=5, ax=axes[row, col])
    sns.stripplot(x=x, y=y, jitter=True, order=genotypeCat, color='black', s=5, ax=axes[row, col])
    axes[row, col].set_title(behavEvent)
    if event == 'totalDistance':
        valueCat = 'distance'
        unit = '(m)'
    else:
        if valueCat == ' Nb':
            unit = '(occurrences)'
        else:
            unit = '(frames)'
    axes[row, col].set_ylabel("{} {}".format(valueCat, unit))
    xlabels = [getShorterGenoNames(longGenoName=x) for x in genotypeCat]
    axes[row, col].set_xticklabels(xlabels, fontsize=12)
    axes[row, col].legend().set_visible(False)
    axes[row, col].spines['right'].set_visible(False)
    axes[row, col].spines['top'].set_visible(False)


    print("event dyadic: ", event)
    text_file.write("Test for the event: {} night {} ".format(event, night))
    text_file.write('\n')

    dfData = pandas.DataFrame({'group': profileValueDictionary["exp"],
                               'genotype': profileValueDictionary["genotype"],
                               'value': profileValueDictionary["value"]})
    print(list(dfData['group']))
    
    # Mann-Whitney U test, non parametric, small sample size
    genotypeCat = list(Counter(dfData['genotype']).keys())
    genotypeCat.sort(reverse=True)
    print('genotype list: ', genotypeCat)
    data = {}
    for k in [0,1]:
        data[genotypeCat[k]] = dfData['value'][dfData['genotype'] == genotypeCat[k]]
    try:
        U, p = mannwhitneyu( data[genotypeCat[0]], data[genotypeCat[1]])
    except:
        print('test not possible')
        U = 'NA'
        p = 'NA'
    print('means of ', genotypeCat[0], np.mean(data[genotypeCat[0]]), 'mean of ', genotypeCat[1], np.mean(data[genotypeCat[1]]))
    print( 'Mann-Whitney U test ({} {} cages, {} {} cages) {}: U={}, p={}'.format(len(data[genotypeCat[0]]), genotypeCat[0], len(data[genotypeCat[1]]), genotypeCat[1], event, U, p) )
    text_file.write('Mann-Whitney U test ({} {} cages, {} {} cages) {}: U={}, p={}'.format(len(data[genotypeCat[0]]), genotypeCat[0], len(data[genotypeCat[1]]), genotypeCat[1], event, U, p))
    axes[row, col].text(x=0.5, y=max(y) + 0.05 * max(y), s = getStarsFromPvalues(p,numberOfTests=1), fontsize=20, ha='center' )
    text_file.write('\n')


def testProfileData(profileData=None, night=0, eventListNames=None, valueCat="", text_file=None):
    for behavEvent in eventListNames:
        if behavEvent == 'totalDistance':
            event = behavEvent
        elif behavEvent != 'totalDistance':
            event = behavEvent+valueCat

        print("event: ", event)
        text_file.write("Test for the event: {} night {}".format( event, night ) )
        
        profileValueDictionary = getProfileValues(profileData=profileData, night=night, event=event)
        
        dfData = pandas.DataFrame({'group': profileValueDictionary["exp"],
                                   'genotype': profileValueDictionary["genotype"],
                                   'value': profileValueDictionary["value"]})

        
        #pandas.DataFrame(dfData).info()
        #Mixed model: variable to explain: value; fixed factor = genotype; random effect: group
        #create model:
        model = smf.mixedlm("value ~ genotype", dfData, groups = dfData["group"])
        #run model: 
        result = model.fit()
        #print summary
        print(result.summary())
        text_file.write(result.summary().as_text())
        text_file.write('\n')

def testProfileDataPerGroup(profileData=None, night=0, eventListNames=None, valueCat="", text_file=None):
    for behavEvent in eventListNames:
        event = behavEvent

        print("event: ", event)
        text_file.write("Test for the event: {} night {}".format( event, night ) )
        
        profileValueDictionary = getProfileValues(profileData=profileData, night=night, event=event)
        
        dfData = pandas.DataFrame({'group': profileValueDictionary["exp"],
                                   'genotype': profileValueDictionary["genotype"],
                                   'value': profileValueDictionary["value"]})

        
        #pandas.DataFrame(dfData).info()
        #Mixed model: variable to explain: value; fixed factor = genotype; random effect: group
        #create model:
        model = smf.mixedlm("value ~ genotype", dfData, groups = dfData["group"])
        #run model: 
        result = model.fit()
        #print summary
        print(result.summary())
        text_file.write(result.summary().as_text())
        text_file.write('\n')


def mergeProfileOverNights( profileData, categoryList, behaviouralEventOneMouse ):
    #merge data from the different nights
    mergeProfile = {}
    for file in profileData.keys():
        nightList = list( profileData[file].keys() )
        print('###############night List: ', nightList)
        mergeProfile[file] = {}
        mergeProfile[file]['all nights'] = {}
        for rfid in profileData[file][nightList[0]].keys():
            print('rfid: ', rfid)
            mergeProfile[file]['all nights'][rfid] = {}
            mergeProfile[file]['all nights'][rfid]['animal'] = profileData[file][nightList[0]][rfid]['animal']
            mergeProfile[file]['all nights'][rfid]['genotype'] = profileData[file][nightList[0]][rfid]['genotype']
            mergeProfile[file]['all nights'][rfid]['file'] = profileData[file][nightList[0]][rfid]['file']
            mergeProfile[file]['all nights'][rfid]['sex'] = profileData[file][nightList[0]][rfid]['sex']
            mergeProfile[file]['all nights'][rfid]['age'] = profileData[file][nightList[0]][rfid]['age']
            mergeProfile[file]['all nights'][rfid]['strain'] = profileData[file][nightList[0]][rfid]['strain']
            mergeProfile[file]['all nights'][rfid]['group'] = profileData[file][nightList[0]][rfid]['group']


            for cat in categoryList:
                traitList = [trait+cat for trait in behaviouralEventOneMouse]
                for event in traitList:
                    print('event: ', event)
                    try:
                        dataNight = 0
                        for night in profileData[file].keys():
                            dataNight += profileData[file][night][rfid][event]

                        if ' MeanDur' in event:
                            mergeProfile[file]['all nights'][rfid][event] = dataNight / len(profileData[file].keys())
                        else:
                            mergeProfile[file]['all nights'][rfid][event] = dataNight
                    except:
                        print('No event of this name: ', rfid, event)
                        continue
            try:
                distNight = 0
                for night in profileData[file].keys():
                    distNight += profileData[file][night][rfid]['totalDistance']
            except:
                print('No calculation of distance possible.', rfid)
                distNight = 'totalDistance'

            mergeProfile[file]['all nights'][rfid]['totalDistance'] = distNight

    return mergeProfile

def extractControlData(profileData, genoControl, behaviouralEventOneMouse):
    categoryList = [' TotalLen', ' Nb', ' MeanDur']
    nightList = list(profileData[list(profileData.keys())[0]].keys())
    print('nights: ', nightList)

    wtData = {}
    for file in profileData.keys():
        wtData[file] = {}
        for night in nightList:
            wtData[file][night] = {}
            temporaryWT = {}
            for cat in categoryList:
                traitList = [trait + cat for trait in behaviouralEventOneMouse]
                for event in traitList:
                    temporaryWT[event] = []
            temporaryWT['totalDistance'] = []

            for rfid in profileData[file][night].keys():
                if profileData[file][night][rfid]['genotype'] == genoControl:
                    temporaryWT['totalDistance'].append(profileData[file][night][rfid]['totalDistance'])
                    for cat in categoryList:
                        traitList = [trait + cat for trait in behaviouralEventOneMouse]
                        for event in traitList:
                            temporaryWT[event].append(profileData[file][night][rfid][event])

            wtData[file][night]['mean totalDistance'] = np.mean(temporaryWT['totalDistance'])
            wtData[file][night]['std totalDistance'] = np.std(temporaryWT['totalDistance'])
            for cat in categoryList:
                traitList = [trait + cat for trait in behaviouralEventOneMouse]
                for event in traitList:
                    wtData[file][night]['mean ' + event] = np.mean(temporaryWT[event])
                    wtData[file][night]['std ' + event] = np.std(temporaryWT[event])
    return wtData

def extractCageData(profileData, behaviouralEventOneMouse):
    categoryList = [' TotalLen', ' Nb', ' MeanDur']
    nightList = list(profileData[list(profileData.keys())[0]].keys())
    print('nights: ', nightList)

    wtData = {}
    for file in profileData.keys():
        wtData[file] = {}
        for night in nightList:
            wtData[file][night] = {}
            temporaryWT = {}
            for cat in categoryList:
                traitList = [trait + cat for trait in behaviouralEventOneMouse]
                for event in traitList:
                    temporaryWT[event] = []
            temporaryWT['totalDistance'] = []

            for rfid in profileData[file][night].keys():
                temporaryWT['totalDistance'].append(profileData[file][night][rfid]['totalDistance'])
                for cat in categoryList:
                    traitList = [trait + cat for trait in behaviouralEventOneMouse]
                    for event in traitList:
                        temporaryWT[event].append(profileData[file][night][rfid][event])

            wtData[file][night]['mean totalDistance'] = np.mean(temporaryWT['totalDistance'])
            wtData[file][night]['std totalDistance'] = np.std(temporaryWT['totalDistance'])
            for cat in categoryList:
                traitList = [trait + cat for trait in behaviouralEventOneMouse]
                for event in traitList:
                    wtData[file][night]['mean ' + event] = np.mean(temporaryWT[event])
                    wtData[file][night]['std ' + event] = np.std(temporaryWT[event])
    return wtData


def generateMutantData(profileData, genoMutant, wtData, categoryList, behaviouralEventOneMouse):
    nightList = list(profileData[list(profileData.keys())[0]].keys())
    print('nights: ', nightList)

    koData = {}
    for file in profileData.keys():
        koData[file] = {}
        for night in nightList:
            koData[file][night] = {}
            temporaryKO = {}
            for cat in categoryList:
                traitList = [trait + cat for trait in behaviouralEventOneMouse]
                for event in traitList:
                    temporaryKO[event] = []
            temporaryKO['totalDistance'] = []

            for rfid in profileData[file][night].keys():
                if profileData[file][night][rfid]['genotype'] == genoMutant:
                    koData[file][night][rfid] = {}
                    koData[file][night][rfid]['totalDistance'] = (profileData[file][night][rfid]['totalDistance'] - wtData[file][night]['mean totalDistance']) / wtData[file][night]['std totalDistance']
                    for cat in categoryList:
                        traitList = [trait + cat for trait in behaviouralEventOneMouse]
                        for event in traitList:
                            koData[file][night][rfid][event] = (profileData[file][night][rfid][event] - wtData[file][night]['mean ' + event]) / wtData[file][night]['std '+ event]

    return koData


def generateZScoreData(profileData, cageData, categoryList, behaviouralEventOneMouse):
    nightList = list(profileData[list(profileData.keys())[0]].keys())
    print('nights: ', nightList)

    zScoreData = {}
    for file in profileData.keys():
        zScoreData[file] = {}
        for night in nightList:
            zScoreData[file][night] = {}
            

            for rfid in profileData[file][night].keys():
                zScoreData[file][night][rfid] = {}
                zScoreData[file][night][rfid]['genotype'] = profileData[file][night][rfid]['genotype']
                zScoreData[file][night][rfid]['sex'] = profileData[file][night][rfid]['sex']
                zScoreData[file][night][rfid]['group'] = profileData[file][night][rfid]['group']
                zScoreData[file][night][rfid]['strain'] = profileData[file][night][rfid]['strain']
                zScoreData[file][night][rfid]['age'] = profileData[file][night][rfid]['age']
                zScoreData[file][night][rfid]['totalDistance'] = (profileData[file][night][rfid]['totalDistance'] - cageData[file][night]['mean totalDistance']) / cageData[file][night]['std totalDistance']
                for cat in categoryList:
                    traitList = [trait + cat for trait in behaviouralEventOneMouse]
                    for event in traitList:
                        print('value ind: ', profileData[file][night][rfid][event])
                        print('mean value cage: ', cageData[file][night]['mean ' + event])
                        print('std value cage: ', cageData[file][night]['std '+ event])
                        if cageData[file][night]['std '+ event] != 0:
                            zScoreData[file][night][rfid][event] = (profileData[file][night][rfid][event] - cageData[file][night]['mean ' + event]) / cageData[file][night]['std '+ event]
                        else:
                            zScoreData[file][night][rfid][event] = 'NA'
                            
    return zScoreData


def plotZScoreProfileAuto(ax, koDataframe, night, eventListForTest, eventListForLabels, cat):
    selectedDataframe = koDataframe[(koDataframe['night'] == night)]
    pos = 0
    colorList = []
    for event in eventListForTest:
        valList = selectedDataframe['value'][selectedDataframe['trait'] == event]

        try:
            T, p = ttest_1samp(valList, popmean=0, nan_policy='omit')
            print('p=', p)
            # if np.isnan(p) == True:
            if getStarsFromPvalues(p, numberOfTests=1) == 'NA':
                print('no test conducted.')
                pos += 1
                continue

            else:
                color = 'grey'
                if p < 0.05:
                    print(night, event, T, p)
                    
                    if T > 0:
                        color = 'red'
                    elif T < 0:
                        color = 'blue'
                    elif T == 0:
                        color = 'grey'
                    ax.text(-2.95, pos, s=getStarsFromPvalues(p, numberOfTests=1), c=color, fontsize=21)

                colorList.append(color)
                print('event position: ', event, pos, T, p, getStarsFromPvalues(p, numberOfTests=1), color)
                pos += 1
        except:
            pos += 1
            colorList.append('grey')
            continue

    print('######## colorList: ', colorList)
    # ax.set_xlim(-0.5, 1.5)
    # ax.set_ylim(min(selectedDataframe['value']) - 0.2 * max(selectedDataframe['value']), max(selectedDataframe['value']) + 0.2 * max(selectedDataframe['value']))
    ax.set_xlim(-3, 3)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_title('night {}'.format(night))

    if cat == ' TotalLen':
        ax.add_patch(mpatches.Rectangle((-3, -1), width=6, height=4.4, facecolor='grey', alpha=0.3))
        ax.text(-2.6, 1.6, s='ACTIVITY', color='white', fontsize=16, fontweight='bold', rotation='vertical',
                verticalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((-3, 3.6), width=6, height=1.8, facecolor='grey', alpha=0.3))
        ax.text(-2.6, 4.5, s='EXPLO', color='white', fontsize=16, fontweight='bold', rotation='vertical',
                verticalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((-3, 5.6), width=6, height=6.8, facecolor='grey', alpha=0.3))
        ax.text(-2.6, 8.8, s='CONTACT', color='white', fontsize=16, fontweight='bold', rotation='vertical',
                verticalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((-3, 12.6), width=6, height=2.8, facecolor='grey', alpha=0.3))
        ax.text(-2.6, 13.55, s='FOLLOW', color='white', fontsize=16, fontweight='bold', rotation='vertical',
                verticalalignment='center')
    
    elif cat == ' Nb':
        ax.add_patch(mpatches.Rectangle((-3, -1), width=6, height=3.4, facecolor='grey', alpha=0.3))
        ax.text(-2.6, 1.1, s='ACTIVITY', color='white', fontsize=14, fontweight='bold', rotation='vertical',
                verticalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((-3, 2.6), width=6, height=1.8, facecolor='grey', alpha=0.3))
        ax.text(-2.6, 3.5, s='EXPLO', color='white', fontsize=14, fontweight='bold', rotation='vertical',
                verticalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((-3, 4.6), width=6, height=6.8, facecolor='grey', alpha=0.3))
        ax.text(-2.6, 7.9, s='CONTACT', color='white', fontsize=14, fontweight='bold', rotation='vertical',
                verticalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((-3, 11.6), width=6, height=2.8, facecolor='grey', alpha=0.3))
        ax.text(-2.6, 12.4, s='FOLLOW', color='white', fontsize=14, fontweight='bold', rotation='vertical',
                verticalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((-3, 14.6), width=6, height=2.8, facecolor='grey', alpha=0.3))
        ax.text(-2.6, 15.05, s='APPROACH', color='white', fontsize=14, fontweight='bold', rotation='vertical',
                verticalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((-3, 17.6), width=6, height=4.3, facecolor='grey', alpha=0.3))
        ax.text(-2.6, 18, s='ESCAPE', color='white', fontsize=14, fontweight='bold', rotation='vertical',
                verticalalignment='center')

    elif cat == ' MeanDur':
        ax.add_patch(mpatches.Rectangle((-3, -1), width=6, height=3.4, facecolor='grey', alpha=0.3))
        ax.text(-2.6, 1.1, s='ACTIVITY', color='white', fontsize=14, fontweight='bold', rotation='vertical',
                verticalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((-3, 2.6), width=6, height=1.8, facecolor='grey', alpha=0.3))
        ax.text(-2.6, 3.45, s='EXPLO', color='white', fontsize=14, fontweight='bold', rotation='vertical',
                verticalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((-3, 4.6), width=6, height=6.8, facecolor='grey', alpha=0.3))
        ax.text(-2.6, 7.8, s='CONTACT', color='white', fontsize=14, fontweight='bold', rotation='vertical',
                verticalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((-3, 11.6), width=6, height=2.8, facecolor='grey', alpha=0.3))
        ax.text(-2.6, 12.55, s='FOLLOW', color='white', fontsize=14, fontweight='bold', rotation='vertical',
                verticalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((-3, 14.6), width=6, height=0.8, facecolor='grey', alpha=0.3))
        ax.text(-2.6, 14, s='APP.', color='white', fontsize=14, fontweight='bold', rotation='vertical',
                verticalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((-3, 15.6), width=6, height=0.9, facecolor='grey', alpha=0.3))
        ax.text(-2.6, 15.05, s='ESC.', color='white', fontsize=14, fontweight='bold', rotation='vertical',
                verticalalignment='center')


    meanprops = dict(marker='D', markerfacecolor='white', markeredgecolor='black')
    bp = sns.boxplot(data=selectedDataframe, y='trait', x='value', ax=ax, width=0.5, orient='h', meanprops=meanprops,
                     showmeans=True, linewidth=0.4, palette=colorList, saturation=0.5)


    #sns.stripplot(data=selectedDataframe, y='trait', x='value', ax=ax, color='black', orient='h')
    sns.swarmplot(data=selectedDataframe, y='trait', x='value', ax=ax, color='black', orient='h')
    # this following swarmplot should be used instead of the previous one if you want to see whether animals from the same cage are similar
    # sns.swarmplot(data=selectedDataframe, y='trait', x='value', ax=ax, hue='exp', orient='h')
    ax.vlines(x=0, ymin=-6, ymax=30, colors='grey', linestyles='dashed')
    # ax.vlines(x=-1, ymin=-1, ymax=30, colors='grey', linestyles='dotted')
    # ax.vlines(x=1, ymin=-1, ymax=30, colors='grey', linestyles='dotted')


    bp.legend().set_visible(False)

    ax.set_xlabel('Z-score per cage', fontsize=18)
    ax.set_ylabel('Behavioral events {}'.format(cat), fontsize=18)
    
    ax.set_yticklabels(eventListForLabels, rotation=0, fontsize=15, horizontalalignment='right')
    ax.set_xticklabels([-3, -2, -1, 0, 1, 2, 3], fontsize=14)
    ax.legend().set_visible(False)


def plotZScoreProfileAutoHorizontal(ax, cat, koDataframe, night, eventListForTest, eventListForLabels):
    selectedDataframe = koDataframe[(koDataframe['night'] == night)]
    pos = 0
    colorList = []
    for event in eventListForTest:
        print('Event: ', event)

        valList = selectedDataframe['value'][selectedDataframe['trait'] == event]
        print("values: ", valList)
        W, pNorm = shapiro(valList)
        if pNorm >= 0.05:
            print("####normal data")
            T, p = ttest_1samp(valList, popmean=0, nan_policy='omit')
        elif pNorm < 0.05:
            print("####data not normal")
            T, p = wilcoxon(valList, alternative="two-sided")
        print('p=', p)
        
        if np.isnan(p) == True:
            #if getStarsFromPvalues(p, numberOfTests=1) == 'NA':
            print('no test conducted.')
            color = 'grey'
            pos += 1
            continue

        else:
            color = 'grey'
            if p < 0.05:
                print(night, event, T, p)
                
                if np.mean(valList) > 0:
                    color = 'red'
                elif np.mean(valList) < 0:
                    color = 'blue'
                """elif T == 0:
                    color = 'grey'"""
                ax.text(pos, -1.97, s=getStarsFromPvalues(p, numberOfTests=1), fontsize=21, c=color, ha='center')
        colorList.append(color)
        #print('event position: ', event, pos, T, p, getStarsFromPvalues(p, numberOfTests=1), color)
        pos += 1
    

    print('##################colorList: ', colorList)
    
    # ax.set_ylim(min(selectedDataframe['value']) - 0.2 * max(selectedDataframe['value']), max(selectedDataframe['value']) + 0.2 * max(selectedDataframe['value']))
    ax.set_ylim(-2, 2.2)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    if cat == ' TotalLen':
        ax.set_xlim(-1, 32)
        ax.add_patch(mpatches.Rectangle((-1, -3), width=4.4, height=6, facecolor='grey', alpha=0.3))
        ax.text(1.6, 2, s='ACTIVITY', color='white', fontsize=16, fontweight='bold', rotation='horizontal',
                horizontalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((3.6, -3), width=1.8, height=6, facecolor='grey', alpha=0.3))
        ax.text(4.5, 2, s='EXPLO', color='white', fontsize=16, fontweight='bold', rotation='horizontal',
                horizontalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((5.6, -3), width=6.8, height=6, facecolor='grey', alpha=0.3))
        ax.text(8.8, 2, s='CONTACT', color='white', fontsize=16, fontweight='bold', rotation='horizontal',
                horizontalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((12.6, -3), width=2.8, height=6, facecolor='grey', alpha=0.3))
        ax.text(14, 2, s='FOLLOW', color='white', fontsize=16, fontweight='bold', rotation='horizontal',
                horizontalalignment='center')

    
    elif cat == ' Nb':
        ax.set_xlim(-1, 32)
        ax.add_patch(mpatches.Rectangle((-1, -3), width=3.4, height=6, facecolor='grey', alpha=0.3))
        ax.text(1, 2, s='ACTIVITY', color='white', fontsize=16, fontweight='bold', rotation='horizontal',
                horizontalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((2.6, -3), width=1.8, height=6, facecolor='grey', alpha=0.3))
        ax.text(3.5, 2, s='EXPLO', color='white', fontsize=16, fontweight='bold', rotation='horizontal',
                horizontalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((4.6, -3), width=6.8, height=6, facecolor='grey', alpha=0.3))
        ax.text(7.9, 2, s='CONTACT', color='white', fontsize=16, fontweight='bold', rotation='horizontal',
                horizontalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((11.6, -3), width=2.8, height=6, facecolor='grey', alpha=0.3))
        ax.text(13.15, 2, s='FOLLOW', color='white', fontsize=16, fontweight='bold', rotation='horizontal',
                horizontalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((14.6, -3), width=2.8, height=6, facecolor='grey', alpha=0.3))
        ax.text(16.05, 2, s='APPROACH', color='white', fontsize=16, fontweight='bold', rotation='horizontal',
                horizontalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((17.6, -3), width=4.3, height=6, facecolor='grey', alpha=0.3))
        ax.text(19.1, 2, s='ESCAPE', color='white', fontsize=16, fontweight='bold', rotation='horizontal',
                horizontalalignment='center')
        
    elif cat == ' MeanDur':
        ax.set_xlim(-1, 30)
        ax.add_patch(mpatches.Rectangle((-1, -3), width=3.4, height=6, facecolor='grey', alpha=0.3))
        ax.text(1.1, 2, s='ACTIVITY', color='white', fontsize=16, fontweight='bold', rotation='horizontal',
                horizontalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((2.6, -3), width=1.8, height=6, facecolor='grey', alpha=0.3))
        ax.text(3.45, 2, s='EXPLO', color='white', fontsize=16, fontweight='bold', rotation='horizontal',
                horizontalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((4.6, -3), width=6.8, height=6, facecolor='grey', alpha=0.3))
        ax.text(7.8, 2, s='CONTACT', color='white', fontsize=16, fontweight='bold', rotation='horizontal',
                horizontalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((11.6, -3), width=2.8, height=6, facecolor='grey', alpha=0.3))
        ax.text(13.05, 2, s='FOLLOW', color='white', fontsize=16, fontweight='bold', rotation='horizontal',
                horizontalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((14.6, -3), width=0.8, height=6, facecolor='grey', alpha=0.3))
        ax.text(15.05, 2, s='APP.', color='white', fontsize=16, fontweight='bold', rotation='horizontal',
                horizontalalignment='center')
    
        ax.add_patch(mpatches.Rectangle((15.6, -3), width=0.9, height=6, facecolor='grey', alpha=0.3))
        ax.text(16.02, 2, s='ESC.', color='white', fontsize=16, fontweight='bold', rotation='horizontal',
                horizontalalignment='center')
    

    meanprops = dict(marker='D', markerfacecolor='white', markeredgecolor='black')
    bp = sns.boxplot(data=selectedDataframe, x='trait', y='value', ax=ax, width=0.5, meanprops=meanprops,
                     showmeans=True, linewidth=0.4, palette=colorList, saturation=0.3, showfliers=False)
    
    sns.swarmplot(data=selectedDataframe, x='trait', y='value', ax=ax, color='black')
    # this following swarmplot should be used instead of the previous one if you want to see whether animals from the same cage are similar
    #sns.swarmplot(data=selectedDataframe, y='trait', x='value', ax=ax, hue='exp', orient='h')
    ax.hlines(y=0, xmin=-6, xmax=30, colors='grey', linestyles='dashed')

    ax.set_ylabel('Z-score per cage', fontsize=18)
    ax.set_xlabel('', fontsize=18)

    ax.set_xticklabels(eventListForLabels, rotation=45, fontsize=15, horizontalalignment='right')
    ax.set_yticks([-2, -1, 0, 1, 2])
    ax.set_yticklabels([-2, -1, 0, 1, 2], fontsize=14)
    ax.legend().set_visible(False)



if __name__ == '__main__':
    
    print("Code launched.")
    # set font
    from matplotlib import rc, gridspec

    rc('font', **{'family': 'serif', 'serif': ['Arial']})
    
    while True:

        question = "Do you want to:"
        question += "\n\t [1] compute profile data (save json file)?"
        question += "\n\t [2] compute profile data for pairs of same genotype animals (save json file)?"
        question += "\n\t [2a] compute profile data for pairs of different genotype animals (save json file)?"
        question += "\n\t [2b] compute profile data for pairs of same genotype animals from pause (save json file)?"
        question += "\n\t [3] plot and analyse profile data (from stored json files)?"
        question += "\n\t [4] plot and analyse profile data for pairs of same genotype animals (saved json files)?"
        question += "\n\t [4b] plot and analyse profile data for pairs of different genotype animals (saved json files)?"
        question += "\n\t [5] plot and analyse profile data after merging the different nigths?"
        question += "\n\t [6] plot KO profile data as centered and reduced data per cage?"
        question += "\n\t [7] plot KO profile data as centered and reduced data per cage with merged nights in horizontal way?"
        question += "\n"
        answer = input(question)

        if answer == "1":
            files = getFilesToProcess()
            tmin, tmax = getMinTMaxTInput()

            
            nightComputation = input("Compute profile only during night events (Y or N)? ")

            for file in files:
                #initialize the result dic
                profileData = {}
                
                print(file)
                #get the path and the name of file
                head, tail = os.path.split(file)
                
                connection = sqlite3.connect( file )

                profileData[file] = {}

                pool = AnimalPool( )
                pool.loadAnimals( connection )

                if nightComputation == "N":
                    minT = tmin
                    maxT = tmax
                    n = 0
                    #extension = tail[-24:-6]
                    extension = f'no_night_{os.path.splitext(os.path.basename(tail))[0]}'
                    print('extension: ', extension)
                
                    #Compute profile2 data and save them in a text file
                    profileData[file][n] = computeProfile(file = file, minT=minT, maxT=maxT, behaviouralEventList=behaviouralEventOneMouse)
                    

                if nightComputation == "Y":
                    nightEventTimeLine = EventTimeLineCached( connection, file, "night", minFrame=tmin, maxFrame=tmax )
                    n = 1
                    #extension = tail[-24:-6]
                    extension = f'over_night_{os.path.splitext(os.path.basename(tail))[0]}'
                    print('extension: ', extension)

                    for eventNight in nightEventTimeLine.getEventList():
                        minT = eventNight.startFrame
                        maxT = eventNight.endFrame
                        print("Night: ", n)
                        #Compute profile2 data and save them in a text file
                        #profileData[file][n] = computeProfile(file=file, minT=minT, maxT=maxT, behaviouralEventList=behaviouralEventOneMouse)
                        profileData[file][n] = computeProfile(file=file, minT=minT, maxT=maxT, behaviouralEventList=behaviouralEventOneRat)
                        
                        n+=1
                        print("Profile data saved.")
                else:
                    print("You did not use the suggested answers.")
                    break
                
                # Create a json file to store the computation
                with open( f"{head}/profile_data_{extension}_{tmin}_{tmax}.json", 'w') as fp:
                    json.dump(profileData, fp, indent=4)
                print(extension)
                print("json file with profile measurements created.")

            break

        if answer == "2":
            files = getFilesToProcess()
            tmin, tmax = getMinTMaxTInput()
            print ( files )

            
            nightComputation = input("Compute profile only during night events (Y or N)? ")

            for file in files:
                profileData = {}
                #get the path and the name of file
                head, tail = os.path.split(file)
                print(file)
                profileData[file] = {}

                if nightComputation == "N":
                    minT = tmin
                    maxT = tmax
                    n = 0
                    extension = 'no_night_{}'.format(os.path.splitext(os.path.basename(tail))[0])
                    #Compute profile2 data and save them in a text file
                    profileData[file][n] = computeProfilePair(file = file, minT=minT, maxT=maxT, behaviouralEventListSingle=behaviouralEventOneMouseSingle, behaviouralEventListSocial=behaviouralEventOneMouseSocial)
                    
                    
                if nightComputation == "Y":
                    connection = sqlite3.connect(file)
                    nightEventTimeLine = EventTimeLineCached( connection, file, "night", minFrame=tmin, maxFrame=tmax )
                    connection.close()
                    n = 1
                    extension = 'over_night_{}'.format(os.path.splitext(os.path.basename(tail))[0])
                    for eventNight in nightEventTimeLine.getEventList():
                        minT = eventNight.startFrame
                        maxT = eventNight.endFrame
                        print("Night: ", n)
                        #Compute profile2 data and save them in a text file
                        profileData[file][n] = computeProfilePair(file=file, minT=minT, maxT=maxT, behaviouralEventListSingle=behaviouralEventOneMouseSingle, behaviouralEventListSocial=behaviouralEventOneMouseSocial)
                        
                        n+=1
                        print("Profile data saved.")
                else:
                    print("You did not use the suggested answers.")
                    break
                
                # Create a json file to store the computation
                print('#############################')
                print(profileData)
                print('#############################')
                with open("{}/profile_data_pair_{}_{}_{}.json".format(head, extension, tmin, tmax), 'w') as fp:
                    json.dump(profileData, fp, indent=4)
                print("json file with profile measurements created.")

            break

        if answer == "2a":
            """compute profile for pairs of different genotypes"""
            files = getFilesToProcess()
            tmin, tmax = getMinTMaxTInput()
            print ( files )

            
            nightComputation = input("Compute profile only during night events (Y or N)? ")

            for file in files:
                profileData = {}
                #get the path and the name of file
                head, tail = os.path.split(file)
                print(file)
                profileData[file] = {}

                if nightComputation == "N":
                    minT = tmin
                    maxT = tmax
                    n = 0
                    extension = 'no_night_{}'.format(os.path.splitext(os.path.basename(tail))[0])
                    #Compute profile2 data and save them in a text file
                    profileData[file][n] = computeProfilePair(file = file, minT=minT, maxT=maxT, behaviouralEventListSingle=behaviouralEventOneMouseSingle+["Contact", "Group2", "Oral-oral Contact", "Side by side Contact", "Side by side Contact, opposite way"], behaviouralEventListSocial=behaviouralEventOneMouseSocial)
                    
                    
                elif nightComputation == "Y":
                    connection = sqlite3.connect(file)
                    nightEventTimeLine = EventTimeLineCached( connection, file, "night", minFrame=tmin, maxFrame=tmax )
                    connection.close()
                    n = 1
                    extension = 'over_night_{}'.format(os.path.splitext(os.path.basename(tail))[0])
                    for eventNight in nightEventTimeLine.getEventList():
                        minT = eventNight.startFrame
                        maxT = eventNight.endFrame
                        print("Night: ", n)
                        #Compute profile2 data and save them in a text file
                        profileData[file][n] = computeProfilePair(file=file, minT=minT, maxT=maxT, behaviouralEventListSingle=behaviouralEventOneMouseSingle+["Contact", "Group2", "Oral-oral Contact", "Side by side Contact", "Side by side Contact, opposite way"], behaviouralEventListSocial=behaviouralEventOneMouseSocial)
                        
                        n+=1
                        print("Profile data saved.")
                else:
                    print("You did not use the suggested answers.")
                    break
                
                # Create a json file to store the computation
                print('#############################')
                print(profileData)
                print('#############################')
                with open("{}/profile_data_pair_{}_{}_{}.json".format(head, extension, tmin, tmax), 'w') as fp:
                    json.dump(profileData, fp, indent=4)
                print("json file with profile measurements created.")

            break

        if answer == "2b":
            '''compute profile data for pairs of animals from pause (save json file)'''
            files = getFilesToProcess()
            experimentDuration = getExperimentDurationInput()
            print(files)

            

            for file in files:
                profileData = {}
                print(file)
                #get the path and the name of file
                head, tail = os.path.split(file)
                extension = 'no_night_{}'.format(os.path.splitext(os.path.basename(tail))[0])
                profileData[file] = {}

                n = 0
                # Compute profile2 data
                profileData[file][n] = computeProfilePairFromPause(file=file, experimentDuration=experimentDuration,
                                                                   behaviouralEventListSingle=behaviouralEventOneMouseSingle+["Contact", "Group2", "Oral-oral Contact", "Side by side Contact", "Side by side Contact, opposite way"],
                                                                   behaviouralEventListSocial=behaviouralEventOneMouseSocial)

                # Create a json file to store the computation
                with open("{}/profile_data_pair_from_pause_{}_{}.json".format(head, extension, experimentDuration), 'w') as fp:
                    json.dump(profileData, fp, indent=4)
                print("json file with profile measurements created.")

            break


        if answer == "3":
            nightComputation = input("Plot profile only during night events (Y or N or merged)? ")
            text_file = getFileNameInput()

            if nightComputation == "N":
                n = 0
                files = getJsonFilesToProcess()
                profileData = mergeJsonFilesForProfiles(files)
                
                print("json file for profile data re-imported.")
                #Plot profile2 data and save them in a pdf file
                print('data: ', profileData)
                plotProfileDataDuration(profileData=profileData, night=n, valueCat=" TotalLen", behaviouralEventList=behaviouralEventOneMouse)
                plotProfileDataDuration(profileData=profileData, night=n, valueCat=" Nb", behaviouralEventList=behaviouralEventOneMouse)
                plotProfileDataDuration(profileData=profileData, night=n, valueCat=" MeanDur", behaviouralEventList=behaviouralEventOneMouse)
                text_file.write( "Statistical analysis: mixed linear models" )
                text_file.write( "{}\n" )
                #Test profile2 data and save results in a text file
                testProfileData(profileData=profileData, night=n, eventListNames=behaviouralEventOneMouse, valueCat=" TotalLen", text_file=text_file)
                testProfileData(profileData=profileData, night=n, eventListNames=behaviouralEventOneMouse, valueCat=" Nb", text_file=text_file)
                testProfileData(profileData=profileData, night=n, eventListNames=behaviouralEventOneMouse, valueCat=" MeanDur", text_file=text_file)

                print("test for total distance")
                testProfileData(profileData=profileData, night=n, eventListNames=["totalDistance"], valueCat="", text_file=text_file)

            elif nightComputation == "Y":
                files = getJsonFilesToProcess()
                # create a dictionary with profile data from all json files
                profileData = mergeJsonFilesForProfiles(files)

                nightList = list(profileData[list(profileData.keys())[0]].keys())
                print('nights: ', nightList)

                for n in nightList:

                    print("Night: ", n)
                    #Plot profile2 data and save them in a pdf file
                    plotProfileDataDuration(profileData=profileData, night=str(n), valueCat=" TotalLen", behaviouralEventList=behaviouralEventOneMouse)
                    plotProfileDataDuration(profileData=profileData, night=str(n), valueCat=" Nb", behaviouralEventList=behaviouralEventOneMouse)
                    plotProfileDataDuration(profileData=profileData, night=str(n), valueCat=" MeanDur", behaviouralEventList=behaviouralEventOneMouse)
                    text_file.write( "Statistical analysis: mixed linear models" )
                    text_file.write( "{}\n" )
                    #Test profile2 data and save results in a text file
                    testProfileData(profileData=profileData, night=str(n), eventListNames=behaviouralEventOneMouse, valueCat=" TotalLen", text_file=text_file)
                    testProfileData(profileData=profileData, night=str(n), eventListNames=behaviouralEventOneMouse, valueCat=" Nb", text_file=text_file)
                    testProfileData(profileData=profileData, night=str(n), eventListNames=behaviouralEventOneMouse, valueCat=" MeanDur", text_file=text_file)

                    print("test for total distance")
                    testProfileData(profileData=profileData, night=str(n), eventListNames=["totalDistance"], valueCat="", text_file=text_file)


            elif nightComputation == "merged":
                n = 'all nights'
                files = getJsonFilesToProcess()
                print(files)
                # create a dictionary with profile data
                profileDataNotMerged = mergeJsonFilesForProfiles(files)
                
                profileData = mergeProfileOverNights(profileData=profileDataNotMerged, categoryList=categoryList,
                                                  behaviouralEventOneMouse=behaviouralEventOneMouse)

                print("json file for profile data re-imported and merged over nights.")
                #Plot profile2 data and save them in a pdf file
                print('data: ', profileData)
                plotProfileDataDuration(profileData=profileData, night=n, valueCat=" TotalLen", behaviouralEventList=behaviouralEventOneMouse)
                plotProfileDataDuration(profileData=profileData, night=n, valueCat=" Nb", behaviouralEventList=behaviouralEventOneMouse)
                plotProfileDataDuration(profileData=profileData, night=n, valueCat=" MeanDur", behaviouralEventList=behaviouralEventOneMouse)
                text_file.write( "Statistical analysis: mixed linear models" )
                text_file.write( "{}\n" )
                #Test profile2 data and save results in a text file
                testProfileData(profileData=profileData, night=n, eventListNames=behaviouralEventOneMouse, valueCat=" TotalLen", text_file=text_file)
                testProfileData(profileData=profileData, night=n, eventListNames=behaviouralEventOneMouse, valueCat=" Nb", text_file=text_file)
                testProfileData(profileData=profileData, night=n, eventListNames=behaviouralEventOneMouse, valueCat=" MeanDur", text_file=text_file)

                print("test for total distance")
                testProfileData(profileData=profileData, night=n, eventListNames=["totalDistance"], valueCat="", text_file=text_file)

            print ("Plots saved as pdf and analyses saved in text file.")

            text_file.close()
            break


        if answer == "4":
            nightComputation = input("Plot profile only during night events (Y or N or merged)? ")
            text_file = getFileNameInput()

            if nightComputation == "N":
                n = 0
                files = getJsonFilesToProcess()
                # create a dictionary with profile data
                profileData = mergeJsonFilesForProfiles(files)

                print("json file for profile data re-imported.")
                #Plot profile2 data and save them in a pdf file
                profileDataSingle = {}
                profileDataDyadic = {}
                for file in profileData.keys():
                    profileDataSingle[file] = {}
                    profileDataDyadic[file] = {}
                    for night in profileData[file].keys():
                        profileDataSingle[file][night] = {}
                        profileDataDyadic[file][night] = {}
                        for ind in profileData[file][night].keys():
                            if '_' in ind:
                                profileDataDyadic[file][night][ind] = profileData[file][night][ind]
                            else:
                                profileDataSingle[file][night][ind] = profileData[file][night][ind]

                print('data single: ', profileDataSingle)
                print('data dyadic: ', profileDataDyadic)

                for valueCat in categoryList:
                    fig, axes = plt.subplots(nrows=5, ncols=6, figsize=(14, 18))
                    row = 0
                    col = 0
                    fig.suptitle(t="{} of events (night {})".format(valueCat, n), y=1.2, fontweight='bold')
                    for event in behaviouralEventOneMouseSingle+['totalDistance']:
                        ax = axes[row][col]
                        plotProfileDataDurationPairs(ax=ax, profileData=profileDataSingle, night=n, valueCat=valueCat, behavEvent=event, mode='single', text_file=text_file )
                        if col < 5:
                            col += 1
                            row = row
                        else:
                            col = 0
                            row += 1

                    for event in behaviouralEventOneMouseSocial:
                        ax = axes[row][col]
                        plotProfileDataDurationPairs(ax=ax, profileData=profileDataDyadic,
                                                     night=n, valueCat=valueCat, behavEvent=event,
                                                     mode='dyadic',
                                                     text_file=text_file)
                        if col < 5:
                            col += 1
                            row = row
                        else:
                            col = 0
                            row += 1

                    fig.tight_layout()
                    fig.savefig("FigProfilePair_{}_Events_night_{}.pdf".format(valueCat, n), dpi=100)
                    fig.savefig("FigProfilePair_{}_Events_night_{}.jpg".format(valueCat, n), dpi=100)
                    plt.close(fig)


            elif nightComputation == "Y":
                files = getJsonFilesToProcess()
                # create a dictionary with profile data
                profileData = mergeJsonFilesForProfiles(files)
                print("json file for profile data re-imported.")

                nightList = list(profileData[list(profileData.keys())[0]].keys())
                print('nights: ', nightList)

                # Plot profile2 data and save them in a pdf file
                profileDataSingle = {}
                profileDataDyadic = {}
                for file in profileData.keys():
                    profileDataSingle[file] = {}
                    profileDataDyadic[file] = {}
                    for night in profileData[file].keys():
                        profileDataSingle[file][night] = {}
                        profileDataDyadic[file][night] = {}
                        for ind in profileData[file][night].keys():
                            if '_' in ind:
                                profileDataDyadic[file][night][ind] = profileData[file][night][ind]
                            else:
                                profileDataSingle[file][night][ind] = profileData[file][night][ind]

                print('data single: ', profileDataSingle)
                print('data dyadic: ', profileDataDyadic)

                for n in nightList:
                    print("Night: ", n)
                    for valueCat in categoryList:
                        fig, axes = plt.subplots(nrows=5, ncols=6, figsize=(14, 18))
                        row = 0
                        col = 0
                        fig.suptitle(t="{} of events (night {})".format(valueCat, n), y=1.2, fontweight='bold')
                        for event in behaviouralEventOneMouseSingle+['totalDistance']:
                            ax = axes[row][col]
                            plotProfileDataDurationPairs(ax=ax, profileData=profileDataSingle,
                                                         night=n, valueCat=valueCat, behavEvent=event,
                                                         mode = 'single',
                                                         text_file=text_file)
                            if col < 5:
                                col += 1
                                row = row
                            else:
                                col = 0
                                row += 1

                        for event in behaviouralEventOneMouseSocial:
                            ax = axes[row][col]
                            plotProfileDataDurationPairs(ax=ax, profileData=profileDataDyadic,
                                                         night=n, valueCat=valueCat, behavEvent=event,
                                                         mode='dyadic',
                                                         text_file=text_file)
                            if col < 5:
                                col += 1
                                row = row
                            else:
                                col = 0
                                row += 1

                        fig.tight_layout()
                        fig.savefig("FigProfilePair_{}_Events_night_{}.pdf".format(valueCat, n), dpi=100)
                        fig.savefig("FigProfilePair_{}_Events_night_{}.jpg".format(valueCat, n), dpi=100)
                        plt.close(fig)

            elif nightComputation == "merged":
                files = getJsonFilesToProcess()
                # create a dictionary with profile data
                profileData = mergeJsonFilesForProfiles(files)
                print("json file for profile data re-imported.")

                nightList = list(profileData[list(profileData.keys())[0]].keys())
                print('nights: ', nightList)

                # Plot profile2 data and save them in a pdf file
                profileDataSingle = {}
                profileDataDyadic = {}
                for file in profileData.keys():
                    profileDataSingle[file] = {}
                    profileDataDyadic[file] = {}
                    for night in profileData[file].keys():
                        profileDataSingle[file][night] = {}
                        profileDataDyadic[file][night] = {}
                        for ind in profileData[file][night].keys():
                            if '_' in ind:
                                profileDataDyadic[file][night][ind] = profileData[file][night][ind]
                            else:
                                profileDataSingle[file][night][ind] = profileData[file][night][ind]

                print('data single: ', profileDataSingle)
                print('data dyadic: ', profileDataDyadic)

                profileDataSingleMerged = mergeProfileOverNights(profileData=profileDataSingle, categoryList=categoryList,
                                                      behaviouralEventOneMouse=behaviouralEventOneMouseSingle)
                profileDataDyadicMerged = mergeProfileOverNights(profileData=profileDataDyadic,
                                                                 categoryList=categoryList,
                                                                 behaviouralEventOneMouse=behaviouralEventOneMouseSocial)
                print(profileDataSingleMerged)

                for n in ['all nights']:
                    print("Night: ", n)
                    for valueCat in categoryList:
                        fig, axes = plt.subplots(nrows=5, ncols=6, figsize=(14, 18))
                        row = 0
                        col = 0
                        fig.suptitle(t="{} of events (night {})".format(valueCat, n), y=1.2, fontweight='bold')
                        for event in behaviouralEventOneMouseSingle+['totalDistance']:
                            ax = axes[row][col]
                            plotProfileDataDurationPairs(ax=ax, profileData=profileDataSingleMerged,
                                                         night=n, valueCat=valueCat, behavEvent=event,
                                                         mode = 'single',
                                                         text_file=text_file)
                            if col < 5:
                                col += 1
                                row = row
                            else:
                                col = 0
                                row += 1

                        for event in behaviouralEventOneMouseSocial:
                            ax = axes[row][col]
                            plotProfileDataDurationPairs(ax=ax, profileData=profileDataDyadicMerged,
                                                         night=n, valueCat=valueCat, behavEvent=event,
                                                         mode='dyadic',
                                                         text_file=text_file)
                            if col < 5:
                                col += 1
                                row = row
                            else:
                                col = 0
                                row += 1

                        fig.tight_layout()
                        fig.savefig("FigProfilePair_{}_Events_night_{}.pdf".format(valueCat, n), dpi=100)
                        fig.savefig("FigProfilePair_{}_Events_night_{}.jpg".format(valueCat, n), dpi=100)
                        plt.close(fig)

            print ("Plots saved as pdf and analyses saved in text file.")

            text_file.close()
            break

        if answer == "4b":
            nightComputation = input("Plot profile only during night events (Y or N or merged)? ")
            text_file = getFileNameInput()

            if nightComputation == "N":
                n = 0
                files = getJsonFilesWithSpecificNameToProcess('profile_data')
                # create a dictionary with profile data
                profileData = mergeJsonFilesForProfiles(files)

                print("json file for profile data re-imported.")
                #Plot profile2 data and save them in a pdf file
                profileDataSingle = {}
                profileDataDyadic = {}
                for file in profileData.keys():
                    profileDataSingle[file] = {}
                    profileDataDyadic[file] = {}
                    for night in profileData[file].keys():
                        profileDataSingle[file][night] = {}
                        profileDataDyadic[file][night] = {}
                        for ind in profileData[file][night].keys():
                            if '_' in ind:
                                profileDataDyadic[file][night][ind] = profileData[file][night][ind]
                            else:
                                profileDataSingle[file][night][ind] = profileData[file][night][ind]

                print('data single: ', profileDataSingle)
                print('data dyadic: ', profileDataDyadic)

                for valueCat in categoryList:
                    fig, axes = plt.subplots(nrows=5, ncols=6, figsize=(14, 18))
                    row = 0
                    col = 0
                    fig.suptitle(t="{} of events (night {})".format(valueCat, n), y=1.2, fontweight='bold')
                    for event in behaviouralEventOneMouseSingle+['totalDistance']:
                        plotProfileDataDurationPairsDiffGeno(axes=axes, row=row, col=col, profileData=profileDataSingle, night=n, valueCat=valueCat, behavEvent=event, mode='single', text_file=text_file )
                        if col < 5:
                            col += 1
                            row = row
                        else:
                            col = 0
                            row += 1

                    for event in behaviouralEventOneMouseSocial:
                        plotProfileDataDurationPairsDiffGeno(axes=axes, row=row, col=col, profileData=profileDataDyadic,
                                                     night=n, valueCat=valueCat, behavEvent=event,
                                                     mode='dyadic',
                                                     text_file=text_file)
                        if col < 5:
                            col += 1
                            row = row
                        else:
                            col = 0
                            row += 1

                    fig.tight_layout()
                    fig.savefig("FigProfilePairDiffGeno_{}_Events_night_{}.pdf".format(valueCat, n), dpi=100)
                    fig.savefig("FigProfilePairDiffGeno_{}_Events_night_{}.jpg".format(valueCat, n), dpi=100)
                    plt.close(fig)


            elif nightComputation == "Y":
                files = getJsonFilesToProcess()
                # create a dictionary with profile data
                profileData = mergeJsonFilesForProfiles(files)
                print("json file for profile data re-imported.")

                nightList = list(profileData[list(profileData.keys())[0]].keys())
                print('nights: ', nightList)

                # Plot profile2 data and save them in a pdf file
                profileDataSingle = {}
                profileDataDyadic = {}
                for file in profileData.keys():
                    profileDataSingle[file] = {}
                    profileDataDyadic[file] = {}
                    for night in profileData[file].keys():
                        profileDataSingle[file][night] = {}
                        profileDataDyadic[file][night] = {}
                        for ind in profileData[file][night].keys():
                            if '_' in ind:
                                profileDataDyadic[file][night][ind] = profileData[file][night][ind]
                            else:
                                profileDataSingle[file][night][ind] = profileData[file][night][ind]

                print('data single: ', profileDataSingle)
                print('data dyadic: ', profileDataDyadic)

                for n in nightList:
                    print("Night: ", n)
                    for valueCat in categoryList:
                        fig, axes = plt.subplots(nrows=5, ncols=6, figsize=(14, 18))
                        row = 0
                        col = 0
                        fig.suptitle(t="{} of events (night {})".format(valueCat, n), y=1.2, fontweight='bold')
                        for event in behaviouralEventOneMouseSingle+['totalDistance']:
                            plotProfileDataDurationPairsDiffGeno(axes=axes, row=row, col=col, profileData=profileDataSingle,
                                                         night=n, valueCat=valueCat, behavEvent=event,
                                                         mode = 'single',
                                                         text_file=text_file)
                            if col < 5:
                                col += 1
                                row = row
                            else:
                                col = 0
                                row += 1

                        for event in behaviouralEventOneMouseSocial:
                            plotProfileDataDurationPairsDiffGeno(axes=axes, row=row, col=col, profileData=profileDataDyadic,
                                                         night=n, valueCat=valueCat, behavEvent=event,
                                                         mode='dyadic',
                                                         text_file=text_file)
                            if col < 5:
                                col += 1
                                row = row
                            else:
                                col = 0
                                row += 1

                        fig.tight_layout()
                        fig.savefig("FigProfilePairDiffGeno_{}_Events_night_{}.pdf".format(valueCat, n), dpi=100)
                        fig.savefig("FigProfilePairDiffGeno_{}_Events_night_{}.jpg".format(valueCat, n), dpi=100)
                        plt.close(fig)

            elif nightComputation == "merged":
                files = getJsonFilesToProcess()
                # create a dictionary with profile data
                profileData = mergeJsonFilesForProfiles(files)
                print("json file for profile data re-imported.")

                nightList = list(profileData[list(profileData.keys())[0]].keys())
                print('nights: ', nightList)

                # Plot profile2 data and save them in a pdf file
                profileDataSingle = {}
                profileDataDyadic = {}
                for file in profileData.keys():
                    profileDataSingle[file] = {}
                    profileDataDyadic[file] = {}
                    for night in profileData[file].keys():
                        profileDataSingle[file][night] = {}
                        profileDataDyadic[file][night] = {}
                        for ind in profileData[file][night].keys():
                            if '_' in ind:
                                profileDataDyadic[file][night][ind] = profileData[file][night][ind]
                            else:
                                profileDataSingle[file][night][ind] = profileData[file][night][ind]

                print('data single: ', profileDataSingle)
                print('data dyadic: ', profileDataDyadic)

                profileDataSingleMerged = mergeProfileOverNights(profileData=profileDataSingle, categoryList=categoryList,
                                                      behaviouralEventOneMouse=behaviouralEventOneMouseSingle)
                profileDataDyadicMerged = mergeProfileOverNights(profileData=profileDataDyadic,
                                                                 categoryList=categoryList,
                                                                 behaviouralEventOneMouse=behaviouralEventOneMouseSocial)
                print(profileDataSingleMerged)

                for n in ['all nights']:
                    print("Night: ", n)
                    for valueCat in categoryList:
                        fig, axes = plt.subplots(nrows=5, ncols=6, figsize=(14, 18))
                        row = 0
                        col = 0
                        fig.suptitle(t="{} of events (night {})".format(valueCat, n), y=1.2, fontweight='bold')
                        for event in behaviouralEventOneMouseSingle+['totalDistance']:
                            plotProfileDataDurationPairsDiffGeno(axes=axes, row=row, col=col, profileData=profileDataSingleMerged,
                                                         night=n, valueCat=valueCat, behavEvent=event,
                                                         mode = 'single',
                                                         text_file=text_file)
                            if col < 5:
                                col += 1
                                row = row
                            else:
                                col = 0
                                row += 1

                        for event in behaviouralEventOneMouseSocial:
                            plotProfileDataDurationPairsDiffGeno(axes=axes, row=row, col=col, profileData=profileDataDyadicMerged,
                                                         night=n, valueCat=valueCat, behavEvent=event,
                                                         mode='dyadic',
                                                         text_file=text_file)
                            if col < 5:
                                col += 1
                                row = row
                            else:
                                col = 0
                                row += 1

                        fig.tight_layout()
                        fig.savefig("FigProfilePairDiffGeno_{}_Events_night_{}.pdf".format(valueCat, n), dpi=100)
                        fig.savefig("FigProfilePairDiffGeno_{}_Events_night_{}.png".format(valueCat, n), dpi=100)
                        plt.close(fig)

            print ("Plots saved as pdf and analyses saved in text file.")

            text_file.close()
            break


        if answer == "5":
            print('Choose the profile json files to process.')
            files = getJsonFilesToProcess()
            # create a dictionary with profile data
            profileData = mergeJsonFilesForProfiles(files)
            print("json file for profile data re-imported.")

            print('Choose a name for the text file to store analyses results.')
            text_file = getFileNameInput()

            nightList = list(profileData[list(profileData.keys())[0]].keys())
            print('nights: ', nightList)


            mergeProfile = mergeProfileOverNights( profileData=profileData, categoryList=categoryList, behaviouralEventOneMouse=behaviouralEventOneMouse )

            n = 'all nights'

            plotProfileDataDuration(profileData=mergeProfile, night=n, valueCat=" TotalLen", behaviouralEventList=behaviouralEventOneMouse)
            plotProfileDataDuration(profileData=mergeProfile, night=n, valueCat=" Nb", behaviouralEventList=behaviouralEventOneMouse)
            plotProfileDataDuration(profileData=mergeProfile, night=n, valueCat=" MeanDur", behaviouralEventList=behaviouralEventOneMouse)
            text_file.write("Statistical analysis: mixed linear models")
            text_file.write("{}\n")
            # Test profile data and save results in a text file
            testProfileData(profileData=mergeProfile, night=n, eventListNames=behaviouralEventOneMouse[:-2],
                            valueCat=" TotalLen", text_file=text_file)
            testProfileData(profileData=mergeProfile, night=n, eventListNames=behaviouralEventOneMouse[:-2],
                            valueCat=" Nb", text_file=text_file)
            testProfileData(profileData=mergeProfile, night=n, eventListNames=behaviouralEventOneMouse[:-2],
                            valueCat=" MeanDur", text_file=text_file)

            print("test for total distance")
            testProfileData(profileData=mergeProfile, night=n, eventListNames=["totalDistance"], valueCat="",
                            text_file=text_file)


            text_file.close()
            print('Job done.')

            break
        

        if answer == "6":
            print('Choose the profile json files to process.')
            files = getJsonFilesToProcess()
            # create a dictionary with profile data
            profileData = mergeJsonFilesForProfiles(files)
            print("json file for profile data re-imported.")

            mergeProfile = mergeProfileOverNights( profileData=profileData, categoryList=categoryList, behaviouralEventOneMouse=behaviouralEventOneMouse )
            #If the profiles are computed over the nights separately as in the original json file:
            dataToUse = profileData
            #If the profiles are computed over the merged nights:
            #dataToUse = mergeProfile
            
            #select the control and tested genotypes
            #generate automatically the list of genotypes
            genotypeList = []
            firstFile = list(dataToUse.keys())[0]
            firstNight = list(dataToUse[firstFile].keys())[0]
            for rfid in dataToUse[firstFile][firstNight].keys():
                genotypeList.append(dataToUse[firstFile][firstNight][rfid]['genotype'])
            
            genotypeCat = list(Counter(genotypeList))
            genotypeCat.sort(reverse=True)
            print('genotype list: ', genotypeCat)
            genoListLocal = genotypeCat
            
            question = "Choose the genotype of the control animals:"
            question += f"\n\t [0] {genoListLocal[0]}"
            question += f"\n\t [1] {genoListLocal[1]}"
            question += "\n"
            answerGenoControl = input(question)
            genoControl = genoListLocal[int(answerGenoControl)]
            #compute the data for the control animal of each cage
            
            #wtData = extractControlData( profileData=dataToUse, genoControl=genoControl, behaviouralEventOneMouse=behaviouralEventOneMouse)
            wtData = extractCageData(profileData=dataToUse, behaviouralEventOneMouse=behaviouralEventOneMouse)
            #mergeProfile = mergeProfileOverNights(profileData=profileData, categoryList=categoryList )
            #wtData = extractControlData(profileData=mergeProfile, genoControl=genoControl)
            #print(wtData)
            
            question = "Choose the genotype of the mutant animals:"
            question += f"\n\t [0] {genoListLocal[0]}"
            question += f"\n\t [1] {genoListLocal[1]}"
            question += "\n"
            answerGenoMutant = input(question)
            genoMutant = genoListLocal[int(answerGenoMutant)]
            #compute the mutant data, centered and reduced for each cage
      
            koData = generateMutantData(profileData=dataToUse, genoMutant=genoMutant, wtData=wtData, categoryList=categoryList, behaviouralEventOneMouse=behaviouralEventOneMouse )

            print(koData)

            for cat in categoryList:
                fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(24, 12), sharey=True)
                koDataDic = {}
                for key in ['night', 'trait', 'rfid', 'exp', 'value']:
                    koDataDic[key] = []

                eventListForTest = [x+cat for x in behaviouralEventOneMouseDic[cat]]
                eventListForLabels = [getFigureBehaviouralEventsLabels(x) for x in behaviouralEventOneMouseDic[cat]]
                if cat == ' TotalLen':
                    eventListForTest = ['totalDistance'] + eventListForTest
                    eventListForLabels = ['distance'] + eventListForLabels

                for file in koData.keys():
                    for night in koData[file].keys():
                        for rfid in koData[file][night].keys():
                            for event in eventListForTest:
                                koDataDic['exp'].append(file)
                                koDataDic['night'].append(night)
                                koDataDic['rfid'].append(rfid)
                                koDataDic['trait'].append(event)
                                koDataDic['value'].append(koData[file][night][rfid][event])

                # print(koDataDic)

                koDataframe = pd.DataFrame.from_dict(koDataDic)
                # print(koDataframe)

                nightList = list(koData[list(koData.keys())[0]].keys())
                col = 0
                for night in nightList:
                    ax = axes[col]
                    plotZScoreProfileAuto(ax=ax, koDataframe=koDataframe, night=night, eventListForTest=eventListForTest, eventListForLabels=eventListForLabels, cat=cat)
                    col += 1

                plt.tight_layout()
                #plt.show()
                fig.savefig('profiles_zscores_{}.pdf'.format(cat), dpi=300)
                fig.savefig('profiles_zscores_{}.png'.format(cat), dpi=100)

            print('Job done.')

            break

        if answer == "7":
            print('Choose the profile json files to process.')
            files = getJsonFilesToProcess()
            # create a dictionary with profile data
            profileData = mergeJsonFilesForProfiles(files)
            print("json file for profile data re-imported.")

            mergeProfile = mergeProfileOverNights(profileData=profileData, categoryList=categoryList,
                                                  behaviouralEventOneMouse=behaviouralEventOneMouse)
            # If the profiles are computed over the nights separately as in the original json file:
            #dataToUse = profileData
            # If the profiles are computed over the merged nights:
            dataToUse = mergeProfile
            
            #generate automatically the list of genotypes
            genotypeList = []
            firstFile = list(dataToUse.keys())[0]
            firstNight = list(dataToUse[firstFile].keys())[0]
            for rfid in dataToUse[firstFile][firstNight].keys():
                genotypeList.append(dataToUse[firstFile][firstNight][rfid]['genotype'])
            
            genotypeCat = list(Counter(genotypeList))
            genotypeCat.sort(reverse=True)
            print('genotype list: ', genotypeCat)
            genoListLocal = genotypeCat
            
            question = "Choose the genotype of the control animals:"
            question += f"\n\t [0] {genoListLocal[0]}"
            question += f"\n\t [1] {genoListLocal[1]}"
            question += "\n"
            answerGenoControl = input(question)
            genoControl = genoListLocal[int(answerGenoControl)]

            # compute the data for the control animal of each cage

            #wtData = extractControlData(profileData=dataToUse, genoControl=genoControl,behaviouralEventOneMouse=behaviouralEventOneMouse)
            wtData = extractCageData(profileData=dataToUse, behaviouralEventOneMouse=behaviouralEventOneMouse)
            # mergeProfile = mergeProfileOverNights(profileData=profileData, categoryList=categoryList )
            # wtData = extractControlData(profileData=mergeProfile, genoControl=genoControl)
            # print(wtData)

            question = "Choose the genotype of the mutant animals:"
            question += f"\n\t [0] {genoListLocal[0]}"
            question += f"\n\t [1] {genoListLocal[1]}"
            question += "\n"
            answerGenoMutant = input(question)
            genoMutant = genoListLocal[int(answerGenoMutant)]
            
            # compute the mutant data, centered and reduced for each cage
            koData = generateMutantData(profileData=dataToUse, genoMutant=genoMutant, wtData=wtData,
                                        categoryList=categoryList, behaviouralEventOneMouse=behaviouralEventOneMouse)

            print(koData)

            for cat in categoryList:
                fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(18, 8), sharey=True)
                koDataDic = {}
                for key in ['night', 'trait', 'rfid', 'exp', 'value']:
                    koDataDic[key] = []
                
                
                # the list of events to be plotted is determined:
                eventListForTest = [x+cat for x in behaviouralEventOneMouseDic[cat]]
                eventListForLabels = [getFigureBehaviouralEventsLabels(x) for x in behaviouralEventOneMouseDic[cat]]
                if cat == ' TotalLen':
                    eventListForTest = ['totalDistance'] + eventListForTest
                    eventListForLabels = ['distance'] + eventListForLabels
                for file in koData.keys():
                    for night in koData[file].keys():
                        for rfid in koData[file][night].keys():
                            for event in eventListForTest:
                                koDataDic['exp'].append(file)
                                koDataDic['night'].append(night)
                                koDataDic['rfid'].append(rfid)
                                koDataDic['trait'].append(event)
                                koDataDic['value'].append(koData[file][night][rfid][event])
                
                #print(koDataDic)

                koDataframe = pd.DataFrame.from_dict(koDataDic)
                #print(koDataframe.head())

                nightList = list(koData[list(koData.keys())[0]].keys())
                col = 0
                for night in nightList:
                    ax = axes
                    plotZScoreProfileAutoHorizontal(ax=ax, cat=cat, koDataframe=koDataframe, night=night,
                                          eventListForTest=eventListForTest, eventListForLabels=eventListForLabels)
                    col += 1

                plt.tight_layout()
                #plt.show()
                fig.savefig('profiles_zscores_horizontal_{}.pdf'.format(cat), dpi=300)
                fig.savefig('profiles_zscores_horizontal_{}.png'.format(cat), dpi=100)

            print('Job done.')

            break

            