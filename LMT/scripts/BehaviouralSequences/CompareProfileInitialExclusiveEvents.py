'''
Created on 11 Mar. 2022

@author: Elodie
'''

import sqlite3
from random import randint

from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.FileUtil import *
from lmtanalysis.Util import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.BehaviouralSequencesUtil import exclusiveEventList, exclusiveEventsLabels, sexList, genoList, sexListGeneral, genoListGeneral
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scripts.ComputeMeasuresIdentityProfileOneMouseAutomatic import computeProfile, computeProfilePair, plotProfileDataDurationPairs, mergeProfileOverNights

import string


if __name__ == '__main__':
    # set font
    from matplotlib import rc, gridspec
    rc('font', **{'family': 'serif', 'serif': ['Arial']})
    letterList = list(string.ascii_uppercase)

    pd.set_option("display.max_rows", None, "display.max_columns", None)

    print("Code launched.")
    
    behaviouralEventInitial = ["Move isolated", "Stop isolated", "Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way"    ]
    categoryList = [' TotalLen', ' Nb', ' MeanDur']
    
    eventsSingle = {'init': [ "Move isolated", "Stop isolated", "Oral-genital Contact" ], 'exclu': ['Move isolated exclusive', 'Stop isolated exclusive', 'Oral-genital Contact exclusive',
                       'Passive oral-genital Contact exclusive', 'Undetected exclusive']}
    eventsDyadic = {'init': [ "Contact", "Oral-oral Contact", "Side by side Contact", "Side by side Contact, opposite way" ], 
                    'exclu': ['Oral-oral Contact exclusive', 'Side by side Contact exclusive', 
                       'Side by side Contact, opposite way exclusive',
                       'Oral-oral and Side by side Contact exclusive',
                       'Oral-genital and Side by side Contact, opposite way exclusive',
                       'Oral-genital passive and Side by side Contact, opposite way exclusive', 'Other contact exclusive']}
    
    while True:
        question = "Do you want to:"
        question += "\n\t [1] compute individual profile with initial or exclusive events?"
        question += "\n\t [2] plot profiles from initial and exclusive events?"
        question += "\n"
        answer = input(question)

        if answer == '1':
            #Compute profiles with initial event definitions
            files = getFilesToProcess()
            tmin, tmax, text_file = getMinTMaxTAndFileNameInput()
            eventTypes = input("Is this the computation for initial or exclusive events (init or exclu)?")
            singleEvents = eventsSingle[eventTypes]
            dyadicEvents = eventsDyadic[eventTypes]

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
                    profileData[file][n] = computeProfilePair(file=file, minT=minT, maxT=maxT,
                                                              behaviouralEventListSingle=singleEvents,
                                                              behaviouralEventListSocial=dyadicEvents)
                    text_file.write( "\n" )
                    # Create a json file to store the computation
                    with open("profile_data_{}_{}.json".format('no_night', eventTypes), 'w') as fp:
                        json.dump(profileData, fp, indent=4)
                    print("json file with profile measurements created.")


                else:
                    nightEventTimeLine = EventTimeLineCached( connection, file, "night", minFrame=tmin, maxFrame=tmax )
                    n = 1

                    for eventNight in nightEventTimeLine.getEventList():
                        minT = eventNight.startFrame
                        maxT = eventNight.endFrame
                        print("Night: ", n)
                        #Compute profile2 data and save them in a text file
                        profileData[file][n] = computeProfilePair(file=file, minT=minT, maxT=maxT,
                                                                  behaviouralEventListSingle=singleEvents,
                                                                  behaviouralEventListSocial=dyadicEvents)
                        text_file.write( "\n" )
                        n+=1
                        print("Profile data saved.")

                    # Create a json file to store the computation
                    with open("profile_data_{}_{}.json".format('over_night', eventTypes), 'w') as fp:
                        json.dump(profileData, fp, indent=4)
                    print("json file with profile measurements created.")


            text_file.write( "\n" )
            text_file.close()

            break


        if answer == '2':
            #Compare the two profiles with initial and exclusive events for pairs of the same genotype
            nightComputation = input("Plot profile only during night events (Y or N or merged)? ")
            text_file = getFileNameInput()
            eventTypes = input("Is this the computation for initial or exclusive events (init or exclu)?")
            singleEvents = eventsSingle[eventTypes]
            dyadicEvents = eventsDyadic[eventTypes]

            nbRows = {'init': 2, 'exclu': 3}
            nbCols = {'init': 4, 'exclu': 4}

            if nightComputation == "N":
                n = 0
                file = getJsonFileToProcess()
                print(file)
                # create a dictionary with profile data
                with open(file) as json_data:
                    profileData = json.load(json_data)

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
                    fig, axes = plt.subplots(nrows=nbRows[eventTypes], ncols=nbCols[eventTypes], figsize=(4*nbCols[eventTypes], 3*nbRows[eventTypes]))
                    if valueCat == ' TotalLen':
                        ylabel = 'total duration'
                        unit = '(frames)'
                    if valueCat == ' Nb':
                        ylabel = 'occurrences'
                        unit = ''
                    if valueCat == ' MeanDur':
                        ylabel = 'mean duration'
                        unit = '(frames)'
                    row = 0
                    col = 0
                    k = 0
                    fig.suptitle(t="{} of events (night {})".format(valueCat, n), y=1.2, fontweight='bold')
                    for event in singleEvents:
                        ax = axes[row, col]
                        plotProfileDataDurationPairs(ax=ax, profileData=profileDataSingle, night=n, valueCat=valueCat, behavEvent=event, mode='single', letter=letterList[k], text_file=text_file )
                        ax.set_ylabel("{} {}".format(ylabel, unit), fontsize=14)
                        ax.set_title(getFigureBehaviouralEventsLabels(event), y=1, fontsize=12, weight='bold')
                        
                        if col < nbCols[eventTypes]-1:
                            col += 1
                            row = row
                        else:
                            col = 0
                            row += 1
                        k += 1

                    for event in dyadicEvents:
                        ax = axes[row, col]
                        plotProfileDataDurationPairs(ax=ax, profileData=profileDataDyadic,
                                                     night=n, valueCat=valueCat, behavEvent=event,
                                                     mode='dyadic',
                                                     text_file=text_file, letter=letterList[k])
                        ax.set_ylabel("{} {}".format(ylabel, unit), fontsize=14)
                        ax.set_title(getFigureBehaviouralEventsLabels(event), y=1, fontsize=12, weight='bold')
                        
                        if col < nbCols[eventTypes]-1:
                            col += 1
                            row = row
                        else:
                            col = 0
                            row += 1
                        k += 1

                    fig.tight_layout()
                    fig.savefig("FigProfilePair_{}_Events_night_{}_{}.pdf".format(valueCat, n, eventTypes), dpi=100)
                    fig.savefig("FigProfilePair_{}_Events_night_{}_{}.jpg".format(valueCat, n, eventTypes), dpi=100)
                    plt.close(fig)


            elif nightComputation == "Y":
                file = getJsonFileToProcess()
                
                # create a dictionary with profile data
                with open(file) as json_data:
                    profileData = json.load(json_data)
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
                        fig, axes = plt.subplots(nrows=nbRows[eventTypes], ncols=nbCols[eventTypes], figsize=(4*nbCols[eventTypes], 3*nbRows[eventTypes]))
                        if valueCat == ' TotalLen':
                            ylabel = 'total duration'
                            unit = '(frames)'
                        if valueCat == ' Nb':
                            ylabel = 'occurrences'
                            unit = ''
                        if valueCat == ' MeanDur':
                            ylabel = 'mean duration'
                            unit = '(frames)'
                        row = 0
                        col = 0
                        k = 0
                        fig.suptitle(t="{} of events (night {})".format(valueCat, n), y=1.2, fontweight='bold')
                        for event in singleEvents:
                            ax = axes[row, col]
                            plotProfileDataDurationPairs(ax=ax, profileData=profileDataSingle,
                                                         night=n, valueCat=valueCat, behavEvent=event,
                                                         mode = 'single',
                                                         text_file=text_file, letter=letterList[k])
                            ax.set_ylabel("{} {}".format(ylabel, unit), fontsize=14)
                            ax.set_title(getFigureBehaviouralEventsLabels(event), y=1, fontsize=12, weight='bold')
                        
                            if col < nbCols[eventTypes]-1:
                                col += 1
                                row = row
                            else:
                                col = 0
                                row += 1
                            k += 1

                        for event in dyadicEvents:
                            ax = axes[row, col]
                            plotProfileDataDurationPairs(ax=ax, profileData=profileDataDyadic,
                                                         night=n, valueCat=valueCat, behavEvent=event,
                                                         mode='dyadic',
                                                         text_file=text_file, letter=letterList[k])
                            ax.set_ylabel("{} {}".format(ylabel, unit), fontsize=14)
                            ax.set_title(getFigureBehaviouralEventsLabels(event), y=1, fontsize=12, weight='bold')
                        
                            if col < nbCols[eventTypes]-1:
                                col += 1
                                row = row
                            else:
                                col = 0
                                row += 1
                            k += 1

                        fig.tight_layout()
                        fig.savefig("FigProfilePair_{}_Events_night_{}_{}.pdf".format(valueCat, n, eventTypes), dpi=100)
                        fig.savefig("FigProfilePair_{}_Events_night_{}_{}.jpg".format(valueCat, n, eventTypes), dpi=100)
                        plt.close(fig)

            elif nightComputation == "merged":
                file = getJsonFileToProcess()
                # create a dictionary with profile data
                with open(file) as json_data:
                    profileData = json.load(json_data)
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
                                                      behaviouralEventOneMouse=singleEvents)
                profileDataDyadicMerged = mergeProfileOverNights(profileData=profileDataDyadic,
                                                                 categoryList=categoryList,
                                                                 behaviouralEventOneMouse=dyadicEvents)
                print(profileDataSingleMerged)

                for n in ['all nights']:
                    print("Night: ", n)
                    for valueCat in categoryList:
                        fig, axes = plt.subplots(nrows=nbRows[eventTypes], ncols=nbCols[eventTypes], figsize=(4*nbCols[eventTypes], 3*nbRows[eventTypes]))
                        
                        if valueCat == ' TotalLen':
                            ylabel = 'total duration'
                            unit = '(frames)'
                        if valueCat == ' Nb':
                            ylabel = 'occurrences'
                            unit = ''
                        if valueCat == ' MeanDur':
                            ylabel = 'mean duration'
                            unit = '(frames)'
                        
                        row = 0
                        col = 0
                        k = 0
                        fig.suptitle(t="{} of events (night {})".format(valueCat, n), y=1.2, fontweight='bold')
                        for event in singleEvents:
                            ax = axes[row, col]
                            plotProfileDataDurationPairs(ax=ax, profileData=profileDataSingleMerged,
                                                         night=n, valueCat=valueCat, behavEvent=event,
                                                         mode = 'single',
                                                         text_file=text_file, letter=letterList[k])
                            ax.set_ylabel("{} {}".format(ylabel, unit), fontsize=14)
                            ax.set_title(getFigureBehaviouralEventsLabels(event), y=1, fontsize=12, weight='bold')
                            if col < nbCols[eventTypes]-1:
                                col += 1
                                row = row
                            else:
                                col = 0
                                row += 1
                            k += 1

                        for event in dyadicEvents:
                            ax = axes[row, col]
                            plotProfileDataDurationPairs(ax=ax, profileData=profileDataDyadicMerged,
                                                         night=n, valueCat=valueCat, behavEvent=event,
                                                         mode='dyadic',
                                                         text_file=text_file, letter=letterList[k])
                            ax.set_title(getFigureBehaviouralEventsLabels(event), y=1, fontsize=12, weight='bold')
                            ax.set_ylabel("{} {}".format(ylabel, unit), fontsize=14)
                            if col < nbCols[eventTypes]-1:
                                col += 1
                                row = row
                            else:
                                col = 0
                                row += 1
                            k += 1

                        fig.tight_layout()
                        fig.savefig("FigProfilePair_{}_Events_night_{}_{}.pdf".format(valueCat, n, eventTypes), dpi=100)
                        fig.savefig("FigProfilePair_{}_Events_night_{}_{}.jpg".format(valueCat, n, eventTypes), dpi=100)
                        plt.close(fig)

            print ("Plots saved as pdf and analyses saved in text file.")

            text_file.close()
            break


    print('Job done.')
