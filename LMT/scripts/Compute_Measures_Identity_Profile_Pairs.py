'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis import BuildEventTrain3, BuildEventTrain4, BuildEventFollowZone, BuildEventRear5, BuildEventFloorSniffing,\
    BuildEventSocialApproach, BuildEventSocialEscape, BuildEventApproachContact,\
    BuildEventApproachRear, BuildEventGroup2, BuildEventGroup3, BuildEventGroup4,\
    BuildEventStop, BuildEventWaterPoint

from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import getMinTMaxTAndFileNameInput, level
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.FileUtil import getFilesToProcess, addJitter
from scipy.stats import mannwhitneyu
import pandas as pd


def computeProfilePairs(files, tmin, tmax, text_file, animalDic ):

    for file in files:

        print(file)
        connection = sqlite3.connect(file)

        pool = AnimalPool()
        pool.loadAnimals(connection)

        genoList = []
        rfidList = []

        animalDic[file] = {}

        for animal in pool.animalDictionnary.keys():

            print("computing individual animal: {}".format(animal))
            rfid = pool.animalDictionnary[animal].RFID
            print("RFID: ".format(rfid))
            animalDic[file][rfid] = {}
            ''' store the animal '''
            # animalDic[rfid]["animal"] = pool.animalDictionnary[animal]

            genoA = None
            try:
                genoA = pool.animalDictionnary[animal].genotype
            except:
                pass

            animalDic[file][rfid][genoA] = {}
            genoList.append(genoA)
            rfidList.append(rfid)

            COMPUTE_TOTAL_DISTANCE = True
            if (COMPUTE_TOTAL_DISTANCE == True):
                pool.animalDictionnary[animal].loadDetection(lightLoad=True)
                animalDic[file][rfid][genoA]['distance'] = pool.animalDictionnary[animal].getDistance(tmin=tmin,
                                                                                                      tmax=tmax)

            for behavEvent in behaviouralEvents:
                print("computing individual event: {}".format(behavEvent))
                behavEventTimeLine = EventTimeLineCached(connection, file, behavEvent, animal, minFrame=tmin,
                                                         maxFrame=tmax)

                totalEventDuration = behavEventTimeLine.getTotalLength()
                nbEvent = behavEventTimeLine.getNumberOfEvent(minFrame=tmin, maxFrame=tmax)
                print("total event duration: ", totalEventDuration)
                animalDic[file][rfid][genoA][behavEventTimeLine.eventName + " TotalLen"] = totalEventDuration
                animalDic[file][rfid][genoA][behavEventTimeLine.eventName + " Nb"] = nbEvent

                print(behavEventTimeLine.eventName, genoA, behavEventTimeLine.idA, totalEventDuration, nbEvent)

        rfidPair = '{}-{}'.format(rfidList[0], rfidList[1])
        animalDic[file][rfidPair] = {}
        pairType = '{}-{}'.format(genoList[0], genoList[1])
        animalDic[file][rfidPair][pairType] = {}
        animalDic[file][rfidPair][pairType]['distance'] = 'NA'

        for behavEvent in behaviouralEvents:
            print("computing individual event: {}".format(behavEvent))
            behavEventTimeLine = EventTimeLineCached(connection, file, behavEvent, minFrame=tmin, maxFrame=tmax)

            totalEventDuration = behavEventTimeLine.getTotalLength()
            nbEvent = behavEventTimeLine.getNumberOfEvent(minFrame=tmin, maxFrame=tmax)
            print("total event duration: ", totalEventDuration)
            animalDic[file][rfidPair][pairType][behavEventTimeLine.eventName + " TotalLen"] = totalEventDuration
            animalDic[file][rfidPair][pairType][behavEventTimeLine.eventName + " Nb"] = nbEvent

            print(behavEventTimeLine.eventName, pairType, totalEventDuration, nbEvent)

        print(animalDic)

        print("writing...")

        ''' 
        file    strain    sex    genotype   group    day    exp    idA    idB    minTime    maxTime 
        '''
        header = ["file", "strain", "sex", "genotype", "group", "day", "exp", "RFID", "minTime", "maxTime"]
        for name in header:
            text_file.write("{}\t".format(name))

        ''' write event keys '''
        firstAnimalKey = next(iter(animalDic[file]))
        print('firstAnimal: ', firstAnimalKey)
        genoFirstAnimal = list(animalDic[file][firstAnimalKey].keys())[0]
        eventDic = animalDic[file][firstAnimalKey][genoFirstAnimal]
        for k in eventDic.keys():
            print('k: ', k)
            text_file.write("{}\t".format(k.replace(" ", "")))
        text_file.write("\n")

        for rfidAnimal in animalDic[file].keys():
            print(rfidAnimal)
            animalId = rfidAnimal
            animalGeno = list(animalDic[file][rfidAnimal].keys())[0]

            text_file.write("{}\t".format(file))
            text_file.write("{}\t".format("strain"))
            text_file.write("{}\t".format("sex"))
            text_file.write("{}\t".format(animalGeno))
            text_file.write("{}\t".format("group"))
            text_file.write("{}\t".format("day"))
            text_file.write("{}\t".format("exp"))
            text_file.write("{}\t".format(animalId))
            text_file.write("{}\t".format(tmin))
            text_file.write("{}\t".format(tmax))

            for kEvent in animalDic[file][animalId][animalGeno].keys():
                text_file.write("{}\t".format(animalDic[file][animalId][animalGeno][kEvent]))
            text_file.write("\n")

    text_file.write("\n")
    text_file.close()

    # Create a json file to store the computation
    jsonFileName = 'profile_unidentified_pairs.json'
    with open(jsonFileName, 'w') as fp:
        json.dump(animalDic, fp, indent=4)

    print("json file with acoustic measurements created for ", jsonFileName)
    print("done.")
    return animalDic



def plotProfileUnidentifiedPairs( profileDic):

    #convert dictionary into a dataframe:

    eventList = []
    genoList = []
    for fileKey in profileDic.keys():
        for idKey in profileDic[fileKey].keys():
            for genoKey in profileDic[fileKey][idKey].keys():
                genoList.append( genoKey )
                for eventKey in profileDic[fileKey][idKey][genoKey].keys():
                   eventList.append( eventKey )

    eventNb = []
    eventDuration = []
    for eventElement in level( eventList ):
        if 'Nb' in eventElement:
            eventNb.append( eventElement )
        if 'TotalLen' in eventElement:
            eventDuration.append( eventElement )


    data = {}
    for event in eventList:
        data[event] = {}
        for geno in genoList:
            data[event][geno] = []

    for fileKey in profileDic.keys():
        for idKey in profileDic[fileKey].keys():
            for genoKey in profileDic[fileKey][idKey].keys():
               for eventKey in profileDic[fileKey][idKey][genoKey].keys():
                   data[eventKey][genoKey].append( profileDic[fileKey][idKey][genoKey][eventKey] )

    '''plots the profile for pairs of mice, according to the type of pairs'''
    # generate plots
    #eventList = eventNb
    #eventList = eventDuration
    eventListComplete = [eventDuration, eventNb]

    #fig.suptitle(t="Nb of events", y=1.2, fontweight='bold')
    nPlot = 0
    # plot the data for each behavioural event
    for eventList in eventListComplete:
        fig, axes = plt.subplots(nrows=5, ncols=5, figsize=(20, 22), sharey=False)
        row = 0
        col = 0
        for behavEvent in eventList:
            print("event: ", behavEvent)

            yWtWt = data[behavEvent]['WT-WT']
            #yHzHz = data[behavEvent]['HZ-HZ']
            yKoKo = data[behavEvent]['KO-KO']
            xWtWt = [1] * len(yWtWt)
            #xHzHz = [2] * len(yHzHz)
            xKoKo = [3] * len(yKoKo)

            yMax = np.amax([np.amax(yWtWt), np.amax(yKoKo)])
            yMin = np.amin([np.amin(yWtWt), np.amin(yKoKo)])

            ax = axes[row][col]
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            #ax.set_xticks([ 1, 2, 3 ])
            ax.set_xticks([1, 3])
            #ax.set_xticklabels(['WT-WT', 'HZ-HZ', 'KO-KO'], rotation = 45, FontSize=12)
            ax.set_xticklabels(['WT-WT', 'KO-KO'], rotation = 45, FontSize=12)
            ax.set_ylabel(behavEvent, FontSize=14)
            ax.legend().set_visible(False)
            ax.xaxis.set_tick_params(direction="in")
            ax.set_xlim(0, 4)
            #ax.set_ylim(0.94*yMin, 1.06*yMax)
            ax.tick_params(axis='y', labelsize=14)

            # plot points for WT and KO:
            ax.scatter(addJitter(xWtWt, 0.08), yWtWt, marker='o', s=16, c='steelblue')
            #ax.scatter(addJitter(xHzHz, 0.08), yHzHz, marker='o', s=16, c='grey')
            ax.scatter(addJitter(xKoKo, 0.08), yKoKo, marker='o', s=16, c='darkorange')
            print('points added')
            try:
                U, p = mannwhitneyu(yWtWt, yKoKo, alternative='two-sided')
                print(behavEvent, ' U = ', U, 'p = ', p, getStarsFromPvalues(p, 1))
                ax.text(2, yMax - 0.06 * (yMax - yMin), getStarsFromPvalues(p, 1),
                        FontSize=20, horizontalalignment='center', color='black', weight='bold')
            except:
                print('stats not possible!')
                continue

            if col < 4:
                col += 1
                row = row
            else:
                col = 0
                row += 1

        fig.tight_layout()
        plt.show()
        fig.savefig("profile_unidentified_pairs_dgkk_{}.pdf".format(nPlot), dpi=100)
        plt.close(fig)
        print("Plots saved as pdf.")
        nPlot += 1


if __name__ == '__main__':
    
    print("Code launched.")
 
    
    behaviouralEvents = ["Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Social escape", "Approach contact", "Approach rear", "Break contact", "FollowZone Isolated", "Train2", "Group2", "Huddling", "Move isolated", "Move in contact", "Rearing", "Rear isolated", "Rear in contact", "Stop isolated", "WallJump", "Water Zone"]
    while True:
        question = "Do you want to:"
        question += "\n\t generate the [j]son file for a profile on pairs of mice?"
        question += "\n\t [p]lot profiles for the different pairs"
        question += "\n\t [sp]lot only a subset of variables"
        question += "\n"
        answer = input(question)

        if answer == 'j':
            files = getFilesToProcess()
            tmin, tmax, text_file = getMinTMaxTAndFileNameInput()

            animalDic = {}

            profileDic = computeProfilePairs(files, tmin, tmax, text_file, animalDic)
            break

        if answer == 'p':
            # open the json file
            jsonFileName = "profile_unidentified_pairs.json"
            with open(jsonFileName) as json_data:
                profileDic = json.load(json_data)
            print("json file re-imported.")

            plotProfileUnidentifiedPairs( profileDic )

            break

        if answer == 'sp':
            '''This script allows to select a few variables to plot them, focusing on social events for unidentified pairs'''
            shortEventList = ["Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact",
                                 "Side by side Contact, opposite way", "Approach rear", "FollowZone Isolated", "Train2"]

            eventDuration = []
            eventNb = []
            for event in shortEventList:
                evDur = event+' TotalLen'
                evNb = event+' Nb'
                eventDuration.append( evDur )
                eventNb.append( evNb )

            eventListComplete = [eventDuration, eventNb]

            # open the json file
            jsonFileName = "profile_unidentified_pairs.json"
            with open(jsonFileName) as json_data:
                profileDic = json.load(json_data)
            print("json file re-imported.")

            genoList = []
            for fileKey in profileDic.keys():
                for idKey in profileDic[fileKey].keys():
                    for genoKey in profileDic[fileKey][idKey].keys():
                        genoList.append(genoKey)



            data = {}
            for event in eventDuration+eventNb:
                data[event] = {}
                for geno in genoList:
                    data[event][geno] = []

            for fileKey in profileDic.keys():
                for idKey in profileDic[fileKey].keys():
                    for genoKey in profileDic[fileKey][idKey].keys():
                        for eventKey in eventDuration+eventNb:
                            data[eventKey][genoKey].append(profileDic[fileKey][idKey][genoKey][eventKey])

            '''plots the profile for pairs of mice, according to the type of pairs'''
            # generate plots
            # eventList = eventNb
            # eventList = eventDuration


            # fig.suptitle(t="Nb of events", y=1.2, fontweight='bold')
            nPlot = 0
            # plot the data for each behavioural event
            for eventList in eventListComplete:
                fig, axes = plt.subplots(nrows=2, ncols=4, figsize=(12, 6), sharey=False)
                row = 0
                col = 0
                for behavEvent in eventList:
                    print("event: ", behavEvent)

                    yWtWt = data[behavEvent]['WT-WT']
                    # yHzHz = data[behavEvent]['HZ-HZ']
                    yKoKo = data[behavEvent]['KO-KO']
                    xWtWt = [1] * len(yWtWt)
                    # xHzHz = [2] * len(yHzHz)
                    xKoKo = [3] * len(yKoKo)

                    if 'TotalLen' in behavEvent:
                        yWtWt = np.array(yWtWt)/30
                        yKoKo = np.array(yKoKo)/30

                    yMax = np.amax([np.amax(yWtWt), np.amax(yKoKo)])
                    yMin = np.amin([np.amin(yWtWt), np.amin(yKoKo)])

                    ax = axes[row][col]
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    # ax.set_xticks([ 1, 2, 3 ])
                    ax.set_xticks([1, 3])
                    # ax.set_xticklabels(['WT-WT', 'HZ-HZ', 'KO-KO'], rotation = 45, FontSize=12)
                    ax.set_xticklabels(['WT-WT', 'KO-KO'], rotation=45, FontSize=12)
                    ax.set_ylabel(behavEvent, FontSize=11)
                    ax.legend().set_visible(False)
                    ax.xaxis.set_tick_params(direction="in")
                    ax.set_xlim(0, 4)
                    # ax.set_ylim(0.94*yMin, 1.06*yMax)
                    ax.tick_params(axis='y', labelsize=14)

                    # plot points for WT and KO:
                    ax.scatter(addJitter(xWtWt, 0.08), yWtWt, marker='o', s=16, c='steelblue')
                    # ax.scatter(addJitter(xHzHz, 0.08), yHzHz, marker='o', s=16, c='grey')
                    ax.scatter(addJitter(xKoKo, 0.08), yKoKo, marker='o', s=16, c='darkorange')
                    print('points added')
                    try:
                        U, p = mannwhitneyu(yWtWt, yKoKo, alternative='two-sided')
                        print(behavEvent, ' U = ', U, 'p = ', p, getStarsFromPvalues(p, 1))
                        ax.text(2, yMax - 0.06 * (yMax - yMin), getStarsFromPvalues(p, 1),
                                FontSize=14, horizontalalignment='center', color='black')
                    except:
                        print('stats not possible!')
                        continue

                    if col < 3:
                        col += 1
                        row = row
                    else:
                        col = 0
                        row += 1

                fig.tight_layout()
                plt.show()
                fig.savefig("social_unidentified_pairs_dgkk_{}.pdf".format(nPlot), dpi=100)
                plt.close(fig)
                print("Plots saved as pdf.")
                nPlot += 1
            break











                
                
            
            
            