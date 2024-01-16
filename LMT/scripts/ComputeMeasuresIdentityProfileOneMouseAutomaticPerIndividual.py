'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3

from lmtanalysis.FileUtil import getFigureBehaviouralEventsLabelsFrench
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
from lmtanalysis.Util import getMinTMaxTAndFileNameInput, getMinTMaxTInput,\
    getColorGeno
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.FileUtil import *
from lmtanalysis.Util import getFileNameInput, getStarsFromPvalues
import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas
from scipy.stats import mannwhitneyu, kruskal, ttest_1samp, ttest_ind
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from lmtanalysis.BehaviouralSequencesUtil import genoList
from scipy.stats.morestats import wilcoxon
import os
from scipy.stats._morestats import shapiro


def computeProfilePerIndividual(file, minT, maxT, genoList, categoryList, behaviouralEventListTwoMice):
    
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
        groupName+ind

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
        animalData[rfid]['genotype'] = pool.animalDictionary[animal].genotype
        animalData[rfid]['sex'] = pool.animalDictionary[animal].sex
        animalData[rfid]['group'] = groupName
        animalData[rfid]['strain'] = pool.animalDictionary[animal].strain
        animalData[rfid]['age'] = pool.animalDictionary[animal].age
        for cat in categoryList:
            for behavEvent in behaviouralEventListTwoMice:
                animalData[rfid][behavEvent+cat] = {}
                for geno in genoList:
                    animalData[rfid][behavEvent+cat][geno] = {}

        genoA = None
        try:
            genoA=pool.animalDictionary[animal].genotype
        except:
            pass

        for behavEvent in behaviouralEventListTwoMice:
            
            print( "computing individual event: {}".format(behavEvent)) 
            for idAnimalB in pool.animalDictionary.keys():
                if animal == idAnimalB:
                    continue
                
                genoB = pool.animalDictionary[idAnimalB].genotype
                behavEventTimeLine = EventTimeLineCached( connection, file, behavEvent, animal, idAnimalB, minFrame=minT, maxFrame=maxT )
                #clean the behavioural event timeline:
                behavEventTimeLine.mergeCloseEvents(numberOfFrameBetweenEvent=1)
                behavEventTimeLine.removeEventsBelowLength(maxLen=3)
    
                totalEventDuration = behavEventTimeLine.getTotalLength()
                nbEvent = behavEventTimeLine.getNumberOfEvent(minFrame = minT, maxFrame = maxT )
                print( "total event duration: " , totalEventDuration )                
                animalData[rfid][behavEventTimeLine.eventName+" TotalLen"][genoB][pool.animalDictionary[idAnimalB].RFID] = totalEventDuration
                animalData[rfid][behavEventTimeLine.eventName+" Nb"][genoB][pool.animalDictionary[idAnimalB].RFID] = nbEvent
                if nbEvent == 0:
                    meanDur = 0
                else:
                    meanDur = totalEventDuration / nbEvent
                animalData[rfid][behavEventTimeLine.eventName+" MeanDur"][genoB][pool.animalDictionary[idAnimalB].RFID] = meanDur
                
                print(behavEventTimeLine.eventName, genoA, behavEventTimeLine.idA, genoB, behavEventTimeLine.idB, totalEventDuration, nbEvent, meanDur)

    connection.close()
        
    return animalData



def getProfileValuesProportionPerGenotype( profileData, night='0', event=None):
    #extract the profile values as a proportion of total duration or total number of events; valid only for the TotalLen or Nb of events
    dataDic = {}
    dataDic['rfid'] = []
    dataDic['genotype'] = []
    dataDic["sameGenoRaw"] = []
    dataDic["diffGenoRaw"] = []
    dataDic["sameGeno"] = []
    dataDic["diffGeno"] = []
    dataDic["exp"] = []
    dataDic['sex'] = []
    dataDic['age'] = []
    dataDic['strain'] = []
    dataDic['group'] = []
    dataDic['totalRaw'] = []
    
    for file in profileData.keys():
        #print(profileData[file].keys())
        for rfid in profileData[file][str(night)].keys():
            dataDic['rfid'].append( rfid )
            genoA = profileData[file][str(night)][rfid]['genotype']
            dataDic['genotype'].append( genoA )
            dataDic['sex'].append( profileData[file][str(night)][rfid]['sex'] )
            dataDic['group'].append( profileData[file][str(night)][rfid]['group'] )
            dataDic['strain'].append( profileData[file][str(night)][rfid]['strain'] )
            dataDic['age'].append( profileData[file][str(night)][rfid]['age'] )
            dataDic["exp"].append( file )


            for genoPossible in profileData[file][str(night)][rfid][event].keys():
                valList = []
                for ind in profileData[file][str(night)][rfid][event][genoPossible].keys():
                    valList.append( profileData[file][str(night)][rfid][event][genoPossible][ind] )
                value = np.sum( valList )

                if genoPossible == genoA:
                    dataDic['sameGenoRaw'].append( value )
                else:
                    dataDic['diffGenoRaw'].append( value )

    #compute the total amount (length or number) of events
    for i in range(len(dataDic['rfid'])):
        dataDic['totalRaw'].append( dataDic['sameGenoRaw'][i] + dataDic['diffGenoRaw'][i] )

    #compute the proportion of the behaviour for total length and number of events
    for i in range(len(dataDic['rfid'])):
        dataDic['sameGeno'].append( dataDic['sameGenoRaw'][i] / dataDic['totalRaw'][i] * 100)
        dataDic['diffGeno'].append( dataDic['diffGenoRaw'][i] / dataDic['totalRaw'][i] * 100)

    print(dataDic)
    return dataDic


def getProfileValuesMeanDurationPerGenotype(profileData, night='0', event=None):
    #extract profile values for mean duration only since it computes the raw values and not proportion
    dataDic = {}
    dataDic['rfid'] = []
    dataDic['genotype'] = []
    dataDic["sameGeno"] = []
    dataDic["diffGeno"] = []
    dataDic["exp"] = []
    dataDic['sex'] = []
    dataDic['age'] = []
    dataDic['strain'] = []
    dataDic['group'] = []

    for file in profileData.keys():
        # print(profileData[file].keys())
        for rfid in profileData[file][str(night)].keys():
            dataDic['rfid'].append(rfid)
            genoA = profileData[file][str(night)][rfid]['genotype']
            dataDic['genotype'].append(genoA)
            dataDic['sex'].append(profileData[file][str(night)][rfid]['sex'])
            dataDic['group'].append(profileData[file][str(night)][rfid]['group'])
            dataDic['strain'].append(profileData[file][str(night)][rfid]['strain'])
            dataDic['age'].append(profileData[file][str(night)][rfid]['age'])
            dataDic["exp"].append(file)

            for genoPossible in profileData[file][str(night)][rfid][event].keys():
                valList = []
                for ind in profileData[file][str(night)][rfid][event][genoPossible].keys():
                    valList.append(profileData[file][str(night)][rfid][event][genoPossible][ind])
                value = np.mean(valList)

                if genoPossible == genoA:
                    dataDic['sameGeno'].append(value)
                else:
                    dataDic['diffGeno'].append(value)

    print(dataDic)
    return dataDic


def plotProfilePerIndividualPerGenotype( axes, row, col, profileData, night, valueCat, behavEvent, text_file ):
    # plot the data for each behavioural event
    event = behavEvent + valueCat

    if valueCat == ' MeanDur':
        profileValueDictionary = getProfileValuesMeanDurationPerGenotype(profileData=profileData, night=night,
                                                                       event=event)
    else:
        profileValueDictionary = getProfileValuesProportionPerGenotype(profileData=profileData, night=night, event=event)

    y = profileValueDictionary["sameGeno"]
    x = profileValueDictionary["genotype"]
    group = profileValueDictionary["exp"]

    genotypeCat = list(Counter(x))
    genotypeCat.sort(reverse=True)
    print('genotype list: ', genotypeCat)

    print("y: ", y)
    print("x: ", x)
    #print("group: ", group)
    experimentType = Counter(group)
    print("Nb of experiments: ", len(experimentType))

    if valueCat == ' MeanDur':
        unit = '(frames)'
        yMin = min(y) - 0.2 * max(y)
        yMax = max(y) + 0.2 * max(y)
    else:
        unit = '(%)'
        yMin = 0
        yMax = 100
        axes[row, col].axhline(100/3, ls='--', c='grey')

    axes[row, col].set_xlim(-0.5, 1.5)
    axes[row, col].set_ylim( yMin, yMax)
    sns.boxplot(x, y, ax=axes[row, col], order=genotypeCat, linewidth=0.5, showmeans=True,
                meanprops={"marker": 'o',
                           "markerfacecolor": 'white',
                           "markeredgecolor": 'black',
                           "markersize": '10'}, showfliers=False)
    #sns.stripplot(x, y, jitter=True, hue=group, s=5, ax=axes[row, col])
    sns.stripplot(x, y, jitter=True, order=genotypeCat, color='black', s=5, ax=axes[row, col])
    axes[row, col].set_title(behavEvent)

    axes[row, col].set_ylabel("{} {}".format(valueCat, unit))
    axes[row, col].legend().set_visible(False)
    axes[row, col].spines['right'].set_visible(False)
    axes[row, col].spines['top'].set_visible(False)


    print("event dyadic: ", event)
    text_file.write("Test for the event: {} night {} ".format(event, night))
    text_file.write('\n')

    dfData = pandas.DataFrame({'group': profileValueDictionary["exp"],
                               'genotype': profileValueDictionary["genotype"],
                               'value': profileValueDictionary["sameGeno"]})

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
    print( 'Mann-Whitney U test ({} {} ind, {} {} ind) {}: U={}, p={}'.format(len(data[genotypeCat[0]]), genotypeCat[0], len(data[genotypeCat[1]]), genotypeCat[1], event, U, p) )
    text_file.write('Mann-Whitney U test ({} {} ind, {} {} ind) {}: U={}, p={}'.format(len(data[genotypeCat[0]]), genotypeCat[0], len(data[genotypeCat[1]]), genotypeCat[1], event, U, p))
    axes[row, col].text(x=0.5, y=yMin+0.95*(yMax-yMin), s = getStarsFromPvalues(p,numberOfTests=1), fontsize=14, ha='center' )
    text_file.write('\n')



def plotProfilePerIndividualPerGenotypeFullRepresentation( ax, profileData, night, valueCat, behavEvent, text_file ):
    # plot the data for each behavioural event
    event = behavEvent + valueCat

    if valueCat == ' MeanDur':
        profileValueDictionaryTransit = getProfileValuesMeanDurationPerGenotype(profileData=profileData, night=night,
                                                                       event=event)
    else:
        profileValueDictionaryTransit = getProfileValuesProportionPerGenotype(profileData=profileData, night=night, event=event)

    profileValueDictionary = {'group': [], 'rfid': [], 'genotype': [], 'genoOther': [], 'value': []}
    for n in range(len(profileValueDictionaryTransit['rfid'])):
        profileValueDictionary['group'].append(profileValueDictionaryTransit['exp'][n])
        profileValueDictionary['rfid'].append(profileValueDictionaryTransit['rfid'][n])
        profileValueDictionary['genotype'].append(profileValueDictionaryTransit['genotype'][n])
        profileValueDictionary['genoOther'].append('same')
        profileValueDictionary['value'].append(profileValueDictionaryTransit['sameGeno'][n])

    for n in range(len(profileValueDictionaryTransit['rfid'])):
        profileValueDictionary['group'].append(profileValueDictionaryTransit['exp'][n])
        profileValueDictionary['rfid'].append(profileValueDictionaryTransit['rfid'][n])
        profileValueDictionary['genotype'].append(profileValueDictionaryTransit['genotype'][n])
        profileValueDictionary['genoOther'].append('diff')
        profileValueDictionary['value'].append(profileValueDictionaryTransit['diffGeno'][n])

    y = profileValueDictionary['value']
    x = profileValueDictionary['genotype']
    genoOther = profileValueDictionary['genoOther']

    genotypeCat = list(Counter(x))
    genotypeCat.sort(reverse=True)
    print('genotype list: ', genotypeCat)

    print("y: ", y)
    print("x: ", x)
    print('geno other: ', genoOther)

    if valueCat == ' MeanDur':
        unit = '(frames)'
        yMin = min(y) - 0.2 * max(y)
        yMax = max(y) + 0.2 * max(y)
    else:
        unit = '(%)'
        yMin = 0
        yMax = 100
        ax.axhline(100 / 3, ls='--', c='grey')
        ax.axhline(100 * 2 / 3, ls='--', c='grey')

    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim( yMin, yMax)
    colorList = ['black', 'darkgrey']
    bp = sns.boxplot(x, y, ax=ax, order=genotypeCat, hue=genoOther, hue_order=['same', 'diff'], linewidth=0.5, showmeans=True,
                meanprops={"marker": 'o',
                           "markerfacecolor": 'white',
                           "markeredgecolor": 'black',
                           "markersize": '10'}, palette = {'same': colorList[0], 'diff': colorList[1]}, showfliers=False)

    sns.stripplot(x, y, jitter=True, order=genotypeCat, hue=genoOther, hue_order=['same', 'diff'], dodge=True, palette=['grey', 'lightgrey'], s=5, ax=ax)
    
    ax.set_title(getFigureBehaviouralEventsLabels(behavEvent), fontsize=16)

    ax.set_ylabel("{} {}".format(valueCat, unit), fontsize=16)
    ax.tick_params(axis='x', labelsize=16)
    ax.tick_params(axis='y', labelsize=14)
    ax.legend().set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)


    print("event dyadic: ", event)
    text_file.write("Test for the event: {} night {} ".format(event, night))
    text_file.write('\n')

    dfData = pandas.DataFrame({'group': profileValueDictionary["group"],
                               'genotype': profileValueDictionary["genotype"],
                               'genoOther': profileValueDictionary['genoOther'],
                               'value': profileValueDictionary["value"]})
    genotypeCat = list(Counter(dfData['genotype']).keys())
    genotypeCat.sort(reverse=True)
    print(dfData)
    print('genotype list: ', genotypeCat)
    otherGenoList = ['same', 'diff']
    pos = {'same': 0, 'diff': 1, genotypeCat[0]: -0.25, genotypeCat[1]: 0.75}

    if valueCat == ' MeanDur':
        # Wilcoxon paired test, non parametric, small sample size
        # compare the two genotypes for the mean duration of events spent with same or with different genotypes

        for genoB in otherGenoList:
            data = {}
            for k in [0,1]:
                data[genotypeCat[k]] = dfData['value'][(dfData['genotype'] == genotypeCat[k]) & (dfData['genoOther'] == genoB)]
            U, p = wilcoxon( data[genotypeCat[0]], data[genotypeCat[1]] , nan_policy='omit')
            
            print('means of mean duration with ', genoB, ' geno: ', genotypeCat[0], np.mean(data[genotypeCat[0]]), 'versus ', genotypeCat[1], np.mean(data[genotypeCat[1]]))
            print( 'Wilcoxon paired test ({} {} ind, {} {} ind) {}: U={}, p={}'.format(len(data[genotypeCat[0]]), genotypeCat[0], len(data[genotypeCat[1]]), genotypeCat[1], event, U, p) )
            text_file.write('Wilcoxon paired test ({} {} ind, {} {} ind) {}: U={}, p={}'.format(len(data[genotypeCat[0]]), genotypeCat[0], len(data[genotypeCat[1]]), genotypeCat[1], event, U, p))
            ax.text(x=pos[genoB], y=yMin+0.95*(yMax-yMin), s = getStarsFromPvalues(p, U, numberOfTests=1), fontsize=15, ha='center' )
            text_file.write('\n')

    elif valueCat in [' TotalLen', ' Nb']:
        data = {}
        for k in [0, 1]:
            data[genotypeCat[k]] = dfData['value'][(dfData['genotype'] == genotypeCat[k]) & (dfData['genoOther'] == 'same')]
            print('############ ', data[genotypeCat[k]])
            
            results = ttest_1samp(data[genotypeCat[k]], 100/3, nan_policy='omit')
            T = results.statistic
            p = results.pvalue
            
            print('means of prop with same geno: ', genotypeCat[k], np.mean(data[genotypeCat[k]]))
            print('One sample t-test ({} {} ind) {}: T={}, p={}'.format(len(data[genotypeCat[k]]), genotypeCat[k], event, T, p))
            text_file.write('One-sample t-test ({} {} ind) {}: T={}, p={}'.format(len(data[genotypeCat[k]]), genotypeCat[k], event, T, p))
            
            ax.text(x=pos[genotypeCat[k]], y=yMin + 0.95 * (yMax - yMin), s=getStarsFromPvalues(p, T, numberOfTests=1),
                                fontsize=14, ha='center')
            text_file.write('\n')


def plotProfilePerIndividualPerGenotypeOnlySameGenotype( ax, profileData, night, valueCat, behavEvent, text_file ):
    # plot the data for each behavioural event
    
    event = behavEvent + valueCat

    if valueCat == ' MeanDur':
        profileValueDictionaryTransit = getProfileValuesMeanDurationPerGenotype(profileData=profileData, night=night,
                                                                       event=event)
    else:
        profileValueDictionaryTransit = getProfileValuesProportionPerGenotype(profileData=profileData, night=night, event=event)

    profileValueDictionary = {'group': [], 'rfid': [], 'genotype': [], 'genoOther': [], 'value': []}
    for n in range(len(profileValueDictionaryTransit['rfid'])):
        profileValueDictionary['group'].append(profileValueDictionaryTransit['exp'][n])
        profileValueDictionary['rfid'].append(profileValueDictionaryTransit['rfid'][n])
        profileValueDictionary['genotype'].append(profileValueDictionaryTransit['genotype'][n])
        profileValueDictionary['genoOther'].append('same')
        profileValueDictionary['value'].append(profileValueDictionaryTransit['sameGeno'][n])

    for n in range(len(profileValueDictionaryTransit['rfid'])):
        profileValueDictionary['group'].append(profileValueDictionaryTransit['exp'][n])
        profileValueDictionary['rfid'].append(profileValueDictionaryTransit['rfid'][n])
        profileValueDictionary['genotype'].append(profileValueDictionaryTransit['genotype'][n])
        profileValueDictionary['genoOther'].append('diff')
        profileValueDictionary['value'].append(profileValueDictionaryTransit['diffGeno'][n])

    y = profileValueDictionary['value']
    x = profileValueDictionary['genotype']
    genoOther = profileValueDictionary['genoOther']

    genotypeCat = list(Counter(x))
    genotypeCat.sort(reverse=True)
    print('genotype list: ', genotypeCat)

    print("y: ", y)
    print("x: ", x)
    print('geno other: ', genoOther)

    if valueCat == ' MeanDur':
        unit = '(frames)'
        yMin = min(y) - 0.2 * max(y)
        yMax = max(y) + 0.2 * max(y)
    

        ax.set_xlim(-0.5, 1.5)
        ax.set_ylim( yMin, yMax)
        colorList = ['black', 'darkgrey']
        bp = sns.boxplot(x, y, ax=ax, order=genotypeCat, hue=genoOther, hue_order=['same', 'diff'], linewidth=0.5, showmeans=True,
                    meanprops={"marker": 'o',
                               "markerfacecolor": 'white',
                               "markeredgecolor": 'black',
                               "markersize": '10'}, palette = {'same': colorList[0], 'diff': colorList[1]}, showfliers=False)
    
        sns.stripplot(x, y, jitter=True, order=genotypeCat, hue=genoOther, hue_order=['same', 'diff'], palette=['grey', 'lightgrey'], dodge=True, s=5, ax=ax)
        
        ax.set_title(getFigureBehaviouralEventsLabels(behavEvent), fontsize=16)
    
        ax.set_ylabel("{} {}".format(valueCat, unit), fontsize=16)
        ax.tick_params(axis='x', labelsize=16)
        ax.tick_params(axis='y', labelsize=14)
        ax.legend().set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
    
    
        print("event dyadic: ", event)
        text_file.write("Test for the event: {} night {} ".format(event, night))
        text_file.write('\n')
    
        dfData = pandas.DataFrame({'group': profileValueDictionary["group"],
                                   'genotype': profileValueDictionary["genotype"],
                                   'genoOther': profileValueDictionary['genoOther'],
                                   'value': profileValueDictionary["value"]})
        genotypeCat = list(Counter(dfData['genotype']).keys())
        genotypeCat.sort(reverse=True)
        print(dfData)
        print('genotype list: ', genotypeCat)
        otherGenoList = ['same', 'diff']
        pos = {'same': 0, 'diff': 1, genotypeCat[0]: -0.25, genotypeCat[1]: 0.75}

    
        # Wilcoxon test, non parametric, small sample size
        # compare the two genotypes for the mean duration of events spent with same or with different genotypes

        for genoB in otherGenoList:
            data = {}
            for k in [0,1]:
                data[genotypeCat[k]] = dfData['value'][(dfData['genotype'] == genotypeCat[k]) & (dfData['genoOther'] == genoB)]
            
            print('means of mean duration with ', genoB, ' geno: ', genotypeCat[0], np.mean(data[genotypeCat[0]]), 'versus ', genotypeCat[1], np.mean(data[genotypeCat[1]]))
            
            #test normality of data
            W0, pNorm0 = shapiro(data[genotypeCat[0]])
            W1, pNorm1 = shapiro(data[genotypeCat[1]])
            #test equality of variance
            f, p_value = f_test(group1=data[genotypeCat[0]], group2=data[genotypeCat[1]])
        
            if (pNorm0 >= 0.05) & (pNorm1 >= 0.05) & (p_value > 0.05):
                print('Normal data')
                results = ttest_ind(data[genotypeCat[0]], data[genotypeCat[1]])
                T = results.statistic
                p = results.pvalue
                print( 'T test ({} {} ind, {} {} ind) {}: U={}, p={}'.format(len(data[genotypeCat[0]]), genotypeCat[0], len(data[genotypeCat[1]]), genotypeCat[1], event, T, p) )
                text_file.write('T Test ({} {} ind, {} {} ind) {}: U={}, p={}'.format(len(data[genotypeCat[0]]), genotypeCat[0], len(data[genotypeCat[1]]), genotypeCat[1], event, T, p))
            
            else:
                print('Data not normally distributed')
                U, p = wilcoxon( data[genotypeCat[0]], data[genotypeCat[1]])
                print( 'Wilcoxon paired test ({} {} ind, {} {} ind) {}: U={}, p={}'.format(len(data[genotypeCat[0]]), genotypeCat[0], len(data[genotypeCat[1]]), genotypeCat[1], event, U, p) )
                text_file.write('Wilcoxon paired test ({} {} ind, {} {} ind) {}: U={}, p={}'.format(len(data[genotypeCat[0]]), genotypeCat[0], len(data[genotypeCat[1]]), genotypeCat[1], event, U, p))
            ax.text(x=pos[genoB], y=yMin+0.95*(yMax-yMin), s = getStarsFromPvalues(p,numberOfTests=1), fontsize=15, ha='center' )
            text_file.write('\n')

    elif valueCat in [' TotalLen', ' Nb']:
        unit = '(%)'
        #yMin = min(y) - 0.2 * max(y)
        #yMax = max(y) + 0.2 * max(y)
        yMin = 10
        yMax = 60
        ax.set_xlim(-0.5, 0.5)
        ax.set_ylim( yMin, yMax)
        
        ax.axhline(100 / 3, ls='--', c='grey')
                
        colorList = ['black', 'darkgrey']
        bp = sns.boxplot(x, y, ax=ax, order=genotypeCat, hue=genoOther, hue_order=['same'], linewidth=0.5, showmeans=True,
                    meanprops={"marker": 'o',
                               "markerfacecolor": 'white',
                               "markeredgecolor": 'black',
                               "markersize": '10'}, palette = {'same': colorList[0]}, showfliers=False)
    
        sns.stripplot(x, y, jitter=True, order=genotypeCat, hue=genoOther, color=[getColorGeno(genotypeCat[0]), getColorGeno(genotypeCat[1])], hue_order=['same'], palette=['grey'], s=5, ax=ax)
        
        ax.set_title(getFigureBehaviouralEventsLabels(behavEvent), fontsize=16)
    
        ax.set_ylabel("{} {}".format(valueCat, unit), fontsize=16)
        ax.tick_params(axis='x', labelsize=16)
        ax.tick_params(axis='y', labelsize=14)
        ax.legend().set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
    
    
        print("event dyadic: ", event)
        text_file.write("Test for the event: {} night {} ".format(event, night))
        text_file.write('\n')
    
        dfData = pandas.DataFrame({'group': profileValueDictionary["group"],
                                   'genotype': profileValueDictionary["genotype"],
                                   'genoOther': profileValueDictionary['genoOther'],
                                   'value': profileValueDictionary["value"]})
        genotypeCat = list(Counter(dfData['genotype']).keys())
        genotypeCat.sort(reverse=True)
        print(dfData)
        print('genotype list: ', genotypeCat)
        otherGenoList = ['same', 'diff']
        pos = {'same': 0, 'diff': 1, genotypeCat[0]: 0, genotypeCat[1]: 1}
        data = {}
        for k in [0, 1]:
            data[genotypeCat[k]] = dfData['value'][(dfData['genotype'] == genotypeCat[k]) & (dfData['genoOther'] == 'same')]
            #print('############ ', data[genotypeCat[k]])
            W, pNorm = shapiro(data[genotypeCat[k]])
        
            if pNorm >= 0.05:
                print('Normal data')
                results = ttest_1samp(data[genotypeCat[k]], 100/3)
                T = results.statistic
                p = results.pvalue
            if pNorm < 0.05:
                print('non normal data')
                yVal = [val - 100/3 for val in data[genotypeCat[k]]]
                results = wilcoxon(yVal, alternative="two-sided")
                T = results.statistic
                p = results.pvalue
        
            print('means of prop with same geno: ', genotypeCat[k], np.mean(data[genotypeCat[k]]))
            if pNorm >= 0.05:
                print('One sample t-test ({} {} ind) {}: T={}, p={}'.format(len(data[genotypeCat[k]]), genotypeCat[k], event, T, p))
                text_file.write('One-sample t-test ({} {} ind) {}: T={}, p={}'.format(len(data[genotypeCat[k]]), genotypeCat[k], event, T, p))
            if pNorm < 0.05:
                print('Wilcoxon test ({} {} ind) {}: T={}, p={}'.format(len(data[genotypeCat[k]]), genotypeCat[k], event, T, p))
                text_file.write('Wilcoxon test ({} {} ind) {}: T={}, p={}'.format(len(data[genotypeCat[k]]), genotypeCat[k], event, T, p))
           
            ax.text(x=pos[genotypeCat[k]], y=yMin + 0.95 * (yMax - yMin), s=getStarsFromPvalues(p, numberOfTests=1),
                                fontsize=14, ha='center')
            text_file.write('\n')
            

def plotProfileValuesPerGenotype(night, categoryList, behaviouralEventOneMouseSocial, profileData, text_file):
                for valueCat in categoryList:
                    fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(12, 9))
                    row = 0
                    col = 0
                    fig.suptitle(t="{} of events (night {})".format(valueCat, n), y=1.2, fontweight='bold')
                    for event in behaviouralEventOneMouseSocial:
                        plotProfilePerIndividualPerGenotype(axes=axes, row=row, col=col, profileData=profileData, night=n, valueCat=valueCat, behavEvent=event, text_file=text_file )
                        if col < 3:
                            col += 1
                            row = row
                        else:
                            col = 0
                            row += 1

                    plt.tight_layout()
                    #plt.show()
                    fig.savefig('profiles_per_geno_night_{}_{}.pdf'.format(n, valueCat), dpi=300)


def mergeProfilePerGenotypeOverNights( profileData, categoryList, behaviouralEventOneMouseSocial, genoList ):
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
                #traitList = [trait+cat for trait in behaviouralEventOneMouseSocial]
                traitList = [trait+cat for trait in behaviouralEventOneMouseSocial[cat]]
            
                for trait in traitList:
                    print(trait)
                    mergeProfile[file]['all nights'][rfid][trait] = {}
                    for genoInteractor in genoList:
                        mergeProfile[file]['all nights'][rfid][trait][genoInteractor] = {}
                        for interactor in profileData[file][nightList[0]][rfid][trait][genoInteractor].keys():
                            dataNight = 0
                            for night in profileData[file].keys():
                                dataNight += profileData[file][night][rfid][trait][genoInteractor][interactor]
                
                            if ' MeanDur' in trait:
                                mergeProfile[file]['all nights'][rfid][trait][genoInteractor][interactor] = dataNight / len(profileData[file].keys())
                            else:
                                mergeProfile[file]['all nights'][rfid][trait][genoInteractor][interactor] = dataNight

    

    return mergeProfile


if __name__ == '__main__':
    
    print("Code launched.")
    # set font
    from matplotlib import rc, gridspec

    rc('font', **{'family': 'serif', 'serif': ['Arial']})
    
    categoryList = [' TotalLen', ' Nb', ' MeanDur']

    while True:

        question = "Do you want to:"
        question += "\n\t [1] compute profile data for each individual taking into account the interacting individual (save json file)?"
        question += "\n\t [2] plot profile values (in proportion for TotalLen or Nb and raw values for MeanDur) according to the interaction with same or different genotype?"
        question += "\n\t [3] plot profile values according to the interaction with same or different genotypes with all combinations?"
        question += "\n"
        answer = input(question)


        if answer == "1":
            #compute profiles per individual according to their genotype
            files = getFilesToProcess()
            tmin, tmax = getMinTMaxTInput()

            nightComputation = input("Compute profile only during night events (Y or N)? ")

            for file in files:
                #initialize the result dic
                profileData = {}
                
                print(file)
                #get the path and the name of file
                head, tail = os.path.split(file)
                
                print(file)
                connection = sqlite3.connect( file )

                profileData[file] = {}

                pool = AnimalPool( )
                pool.loadAnimals( connection )
                
                genotypeList = pool.getGenotypeList()
                '''for animalId in pool.animalDictionary.keys():
                    geno = pool.animalDictionary[animalId].genotype
                    genotypeList.append(geno)'''
                
                genotypeCat = list(Counter(genotypeList))
                genotypeCat.sort(reverse=True)
                print('genotype list: ', genotypeCat)
                genoListLocal = genotypeCat

                if nightComputation == "N":
                    minT = tmin
                    maxT = tmax
                    n = 0
                    #Compute profile2 data and save them in a text file
                    profileData[file][n] = computeProfilePerIndividual(file=file, minT=minT, maxT=maxT, genoList=genoListLocal, categoryList=categoryList, behaviouralEventListTwoMice=behaviouralEventOneMouseSocial)
                    addToFile = f'no_night_{os.path.splitext(os.path.basename(tail))[0]}'
                    

                else:
                    nightEventTimeLine = EventTimeLineCached( connection, file, "night", minFrame=tmin, maxFrame=tmax )
                    n = 1
                    addToFile = f'over_night_{os.path.splitext(os.path.basename(tail))[0]}'

                    for eventNight in nightEventTimeLine.getEventList():
                        minT = eventNight.startFrame
                        maxT = eventNight.endFrame
                        print("Night: ", n)
                        #Compute profile2 data and save them in a text file
                        #profileData[file][n] = computeProfilePerIndividual(file=file, minT=minT, maxT=maxT, genoList=genoListLocal, categoryList=categoryList, behaviouralEventListTwoMice=behaviouralEventOneMouseSocial)
                        profileData[file][n] = computeProfilePerIndividual(file=file, minT=minT, maxT=maxT, genoList=genoListLocal, categoryList=categoryList, behaviouralEventListTwoMice=["FollowZone"])
                        
                        n+=1
                        print("Profile data saved.")

                # Create a json file to store the computation
                with open("{}/profile_data_per_ind_{}_{}_{}.json".format(head, addToFile, tmin, tmax), 'w') as fp:
                    json.dump(profileData, fp, indent=4)
                print("json file with profile measurements created.")

            print('Job done.')

            break


        if answer == "2":
            #plot profile values according to the interaction with same or different genotypes for the totalLen and Nb of events
            print('Choose the profile json files to process.')
            files = getJsonFilesToProcess()
            # create a dictionary with profile data
            profileData = mergeJsonFilesForProfiles(files)
            print("json file for profile data re-imported.")
            
            text_file = getFileNameInput()
            nightComputation = input("Plot profile only during night events (Y or N or merged)? ")

            if nightComputation == "N":
                n = 0
                plotProfileValuesPerGenotype( night=n, categoryList=categoryList, behaviouralEventOneMouseSocial=behaviouralEventOneMouseSocial, profileData=profileData, text_file=text_file)
            
            elif nightComputation == "Y":
                numberOfNightList = list(profileData[list(profileData.keys())[0]].keys())
                
                for n in numberOfNightList:
                    plotProfileValuesPerGenotype( night=n, categoryList=categoryList, behaviouralEventOneMouseSocial=behaviouralEventOneMouseSocial, profileData=profileData, text_file=text_file)
            
            elif nightComputation == 'merged':
                #generate automatically the list of genotypes
                firstFile = list(profileData.keys())[0]
                firstNight = list(profileData[firstFile].keys())[0]
                firstRfid = list(profileData[firstFile][firstNight].keys())[0]
                genoListLocal = list(profileData[firstFile][firstNight][firstRfid]['Contact TotalLen'].keys())
                
                mergedProfilePerGeno = mergeProfilePerGenotypeOverNights( profileData=profileData, categoryList=categoryList, behaviouralEventOneMouseSocial=behaviouralEventOneMouseSocial, genoList=genoListLocal )
                print('merged profile: ')
                print( mergedProfilePerGeno )
                
                n = 'all nights'
                plotProfileValuesPerGenotype( night=n, categoryList=categoryList, behaviouralEventOneMouseSocial=behaviouralEventOneMouseSocial, profileData=mergedProfilePerGeno, text_file=text_file)
              
            print('Job done.')
            break


        if answer == "3":
            #plot profile values according to the interaction with same or different genotypes with all combinations
            print('Choose the profile json files to process.')
            files = getJsonFilesToProcess()
            # create a dictionary with profile data
            profileData = mergeJsonFilesForProfiles(files)
            print("json file for profile data re-imported.")
            text_file = getFileNameInput()
            nightComputation = input("Plot profile only during night events (Y or N or merged)? ")

            if nightComputation == "N":
                n = 0
                for valueCat in categoryList:
                    fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(16, 9))
                    row = 0
                    col = 0
                    fig.suptitle(t="{} of events (night {})".format(valueCat, n), y=1.2, fontweight='bold')
                    for event in behaviouralEventOneMouseSocial:
                        plotProfilePerIndividualPerGenotypeFullRepresentation(ax=axes[row, col], profileData=profileData, night=n, valueCat=valueCat, behavEvent=event, text_file=text_file )
                        if col < 3:
                            col += 1
                            row = row
                        else:
                            col = 0
                            row += 1

                    plt.tight_layout()
                    #plt.show()
                    fig.savefig('profiles_per_geno_all_config_night_{}_{}.pdf'.format(n, valueCat), dpi=300)
                    fig.savefig('profiles_per_geno_all_config_night_{}_{}.png'.format(n, valueCat), dpi=300)
                    
            
            if nightComputation == "Y":
                numberOfNightList = list(profileData[list(profileData.keys())[0]].keys())
                
                for night in numberOfNightList:
                    for valueCat in categoryList:
                        fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(16, 9))
                        row = 0
                        col = 0
                        fig.suptitle(t="{} of events (night {})".format(valueCat, n), y=1.2, fontweight='bold')
                        for event in behaviouralEventOneMouseSocial:
                            plotProfilePerIndividualPerGenotypeFullRepresentation(ax=axes[row, col], profileData=profileData, night=night, valueCat=valueCat, behavEvent=event, text_file=text_file )
                            if col < 3:
                                col += 1
                                row = row
                            else:
                                col = 0
                                row += 1
    
                        plt.tight_layout()
                        #plt.show()
                        fig.savefig('profiles_per_geno_all_config_night_{}_{}.pdf'.format(night, valueCat), dpi=300)
                        fig.savefig('profiles_per_geno_all_config_night_{}_{}.png'.format(night, valueCat), dpi=300)
                        
            
            if nightComputation == "merged":
                #generate automatically the list of genotypes
                firstFile = list(profileData.keys())[0]
                firstNight = list(profileData[firstFile].keys())[0]
                firstRfid = list(profileData[firstFile][firstNight].keys())[0]
                genoListLocal = list(profileData[firstFile][firstNight][firstRfid]['Contact TotalLen'].keys())
                
                mergedProfilePerGeno = mergeProfilePerGenotypeOverNights( profileData=profileData, categoryList=categoryList, behaviouralEventOneMouseSocial=behaviouralEventOneMouseSocial, genoList=genoListLocal )
                
                n = 'all nights'
                for valueCat in categoryList:
                    fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(16, 9))
                    row = 0
                    col = 0
                    fig.suptitle(t="{} of events (night {})".format(valueCat, n), y=1.2, fontweight='bold')
                    for event in behaviouralEventOneMouseSocial:
                        plotProfilePerIndividualPerGenotypeFullRepresentation(ax=axes[row, col], profileData=mergedProfilePerGeno, night=n, valueCat=valueCat, behavEvent=event, text_file=text_file )
                        if col < 3:
                            col += 1
                            row = row
                        else:
                            col = 0
                            row += 1

                    plt.tight_layout()
                    #plt.show()
                    fig.savefig('profiles_per_geno_all_config_{}_{}.pdf'.format(n, valueCat), dpi=300)
                    fig.savefig('profiles_per_geno_all_config_{}_{}.png'.format(n, valueCat), dpi=300)

            print('Job done.')
            break

            