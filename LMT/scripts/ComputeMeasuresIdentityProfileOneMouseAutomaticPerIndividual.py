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
from lmtanalysis.Util import getMinTMaxTAndFileNameInput, getMinTMaxTInput
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.FileUtil import *
from lmtanalysis.Util import getFileNameInput, getStarsFromPvalues
import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas
from scipy.stats import mannwhitneyu, kruskal, ttest_1samp
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from lmtanalysis.BehaviouralSequencesUtil import genoList


def computeProfilePerIndividual(file, minT, maxT, genoList, categoryList, behaviouralEventListTwoMice):
    
    connection = sqlite3.connect( file )
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    
    indList = []
    for animal in pool.animalDictionnary.keys():
        print("computing individual animal: {}".format(animal))
        rfid = pool.animalDictionnary[animal].RFID
        indList.append(rfid)

    sortedIndList = sorted(indList)
    print('sorted list: ', sortedIndList)
    groupName = sortedIndList[0]
    for ind in sortedIndList[1:]:
        print('ind: ', ind)
        groupName+ind

    animalData = {}
    for animal in pool.animalDictionnary.keys():
        
        print( "computing individual animal: {}".format( animal ))
        rfid = pool.animalDictionnary[animal].RFID
        print( "RFID: {}".format( rfid ) )
        animalData[rfid]= {}        
        #store the animal
        animalData[rfid]["animal"] = pool.animalDictionnary[animal].name
        animalObject = pool.animalDictionnary[animal]
        animalData[rfid]["file"] = file
        animalData[rfid]['genotype'] = pool.animalDictionnary[animal].genotype
        animalData[rfid]['sex'] = pool.animalDictionnary[animal].sex
        animalData[rfid]['group'] = groupName
        animalData[rfid]['strain'] = pool.animalDictionnary[animal].strain
        animalData[rfid]['age'] = pool.animalDictionnary[animal].age
        for cat in categoryList:
            for behavEvent in behaviouralEventListTwoMice:
                animalData[rfid][behavEvent+cat] = {}
                for geno in genoList:
                    animalData[rfid][behavEvent+cat][geno] = {}

        genoA = None
        try:
            genoA=pool.animalDictionnary[animal].genotype
        except:
            pass

        for behavEvent in behaviouralEventListTwoMice:
            
            print( "computing individual event: {}".format(behavEvent)) 
            for idAnimalB in pool.animalDictionnary.keys():
                if animal == idAnimalB:
                    continue
                
                genoB = pool.animalDictionnary[idAnimalB].genotype
                behavEventTimeLine = EventTimeLineCached( connection, file, behavEvent, animal, idAnimalB, minFrame=minT, maxFrame=maxT )
                #clean the behavioural event timeline:
                behavEventTimeLine.mergeCloseEvents(numberOfFrameBetweenEvent=1)
                behavEventTimeLine.removeEventsBelowLength(maxLen=3)
    
                totalEventDuration = behavEventTimeLine.getTotalLength()
                nbEvent = behavEventTimeLine.getNumberOfEvent(minFrame = minT, maxFrame = maxT )
                print( "total event duration: " , totalEventDuration )                
                animalData[rfid][behavEventTimeLine.eventName+" TotalLen"][genoB][pool.animalDictionnary[idAnimalB].RFID] = totalEventDuration
                animalData[rfid][behavEventTimeLine.eventName+" Nb"][genoB][pool.animalDictionnary[idAnimalB].RFID] = nbEvent
                if nbEvent == 0:
                    meanDur = 0
                else:
                    meanDur = totalEventDuration / nbEvent
                animalData[rfid][behavEventTimeLine.eventName+" MeanDur"][genoB][pool.animalDictionnary[idAnimalB].RFID] = meanDur
                
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


def getProfileValuesProportionPerGenotypeFullRepresentation(profileData, night='0', event=None):
    # extract the profile values as a proportion of total duration or total number of events; valid only for the TotalLen or Nb of events
    dataDic = {}
    dataDic['rfid'] = []
    dataDic['genotype'] = []
    dataDic['genoOther'] = []
    dataDic['value'] = []
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

                value = np.sum(valList)

                if genoPossible == genoA:
                    dataDic['sameGenoRaw'].append(value)
                else:
                    dataDic['diffGenoRaw'].append(value)

    # compute the total amount (length or number) of events
    for i in range(len(dataDic['rfid'])):
        dataDic['totalRaw'].append(dataDic['sameGenoRaw'][i] + dataDic['diffGenoRaw'][i])

    # compute the proportion of the behaviour for total length and number of events
    for i in range(len(dataDic['rfid'])):
        dataDic['sameGeno'].append(dataDic['sameGenoRaw'][i] / dataDic['totalRaw'][i] * 100)
        dataDic['diffGeno'].append(dataDic['diffGenoRaw'][i] / dataDic['totalRaw'][i] * 100)

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



def plotProfilePerIndividualPerGenotypeFullRepresentation( axes, row, col, profileData, night, valueCat, behavEvent, text_file ):
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
    print( 'Mann-Whitney U test ({} {} cages, {} {} cages) {}: U={}, p={}'.format(len(data[genotypeCat[0]]), genotypeCat[0], len(data[genotypeCat[1]]), genotypeCat[1], event, U, p) )
    text_file.write('Mann-Whitney U test ({} {} cages, {} {} cages) {}: U={}, p={}'.format(len(data[genotypeCat[0]]), genotypeCat[0], len(data[genotypeCat[1]]), genotypeCat[1], event, U, p))
    axes[row, col].text(x=0.5, y=yMin+0.95*(yMax-yMin), s = getStarsFromPvalues(p,numberOfTests=1), fontsize=14, ha='center' )
    text_file.write('\n')




if __name__ == '__main__':
    
    print("Code launched.")
    # set font
    from matplotlib import rc, gridspec

    rc('font', **{'family': 'serif', 'serif': ['Arial']})
    #List of events to be computed within the behavioural profile2, and header for the computation of the total distance travelled.
   
    behaviouralEventOneMouseSocial = ["Contact", "Group2", "Oral-oral Contact", "Oral-genital Contact",
                                "Side by side Contact", "Side by side Contact, opposite way",
                                "Train2", "FollowZone Isolated",
                                "Social approach", "Approach contact",
                                "Get away", "Break contact"]

    genoListLocal = ['B6N', 'B6J']
    categoryList = [' TotalLen', ' Nb', ' MeanDur']

    while True:

        question = "Do you want to:"
        question += "\n\t [1] compute profile data for each individual taking into account the interacting individual (save json file)?"
        question += "\n\t [2] plot profile values (in proportion for TotalLen or Nb and raw values for MeanDur) according to the interaction with same or different genotype?"
        question += "\n"
        answer = input(question)


        if answer == "1":
            #compute profiles per individual according to their genotype
            files = getFilesToProcess()
            tmin, tmax = getMinTMaxTInput()

            profileData = {}
            nightComputation = input("Compute profile only during night events (Y or N)? ")

            for file in files:

                print(file)
                connection = sqlite3.connect( file )

                profileData[file] = {}

                pool = AnimalPool( )
                pool.loadAnimals( connection )

                if nightComputation == "N":
                    minT = tmin
                    maxT = tmax
                    n = 0
                    #Compute profile2 data and save them in a text file
                    profileData[file][n] = computeProfilePerIndividual(file=file, minT=minT, maxT=maxT, genoList=genoListLocal, categoryList=categoryList, behaviouralEventListTwoMice=behaviouralEventOneMouseSocial)
                    addToFile = 'no_night'
                    

                else:
                    nightEventTimeLine = EventTimeLineCached( connection, file, "night", minFrame=tmin, maxFrame=tmax )
                    n = 1
                    addToFile = 'over_night'

                    for eventNight in nightEventTimeLine.getEventList():
                        minT = eventNight.startFrame
                        maxT = eventNight.endFrame
                        print("Night: ", n)
                        #Compute profile2 data and save them in a text file
                        profileData[file][n] = computeProfilePerIndividual(file=file, minT=minT, maxT=maxT, genoList=genoListLocal, categoryList=categoryList, behaviouralEventListTwoMice=behaviouralEventOneMouseSocial)
                        
                        n+=1
                        print("Profile data saved.")

            # Create a json file to store the computation
            with open("profile_data_per_ind_{}.json".format(addToFile), 'w') as fp:
                json.dump(profileData, fp, indent=4)
            print("json file with profile measurements created.")

            print('Job done.')

            break

        if answer == "2":
            #plot profile values according to the interaction with same or different genotypes for the totalLen and Nb of events
            print('Choose the profile json file to process.')
            file = getJsonFileToProcess()
            text_file = getFileNameInput()
            nightComputation = input("Plot profile only during night events (Y or N or merged)? ")

            # create a dictionary with profile data
            with open(file) as json_data:
                profileData = json.load(json_data)
            print("json file for profile data re-imported.")

            if nightComputation == "N":
                n = 0
                for valueCat in [' TotalLen', ' Nb']:
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
                    plt.show()
                    fig.savefig('profiles_per_geno_{}.pdf'.format(valueCat), dpi=300)

            print('Job done.')
            break


        if answer == "3":
            #plot profile values according to the interaction with same or different genotypes with all combinations
            print('Choose the profile json file to process.')
            file = getJsonFileToProcess()
            text_file = getFileNameInput()
            nightComputation = input("Plot profile only during night events (Y or N or merged)? ")

            # create a dictionary with profile data
            with open(file) as json_data:
                profileData = json.load(json_data)
            print("json file for profile data re-imported.")

            if nightComputation == "N":
                n = 0
                for valueCat in categoryList:
                    fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(16, 9))
                    row = 0
                    col = 0
                    fig.suptitle(t="{} of events (night {})".format(valueCat, n), y=1.2, fontweight='bold')
                    for event in behaviouralEventOneMouseSocial:
                        plotProfilePerIndividualPerGenotypeFullRepresentation(axes=axes, row=row, col=col, profileData=profileData, night=n, valueCat=valueCat, behavEvent=event, text_file=text_file )
                        if col < 3:
                            col += 1
                            row = row
                        else:
                            col = 0
                            row += 1

                    plt.tight_layout()
                    plt.show()
                    fig.savefig('profiles_per_geno_{}.pdf'.format(valueCat), dpi=300)

            print('Job done.')
            break

            