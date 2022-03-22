'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *
import numpy as np
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
import colorsys
from collections import Counter
import seaborn as sns
import matplotlib.patches as mpatches

import matplotlib.pyplot as plt


from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import getMinTMaxTAndFileNameInput
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.FileUtil import getFilesToProcess, getJsonFileToProcess
from lmtanalysis.Util import getFileNameInput, getStarsFromPvalues
import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas
from scipy.stats import mannwhitneyu, kruskal, ttest_1samp
from scripts.ComputeMeasuresIdentityProfileOneMouseAutomatic import *
#from USV.usvDescription.Compute_Number_USVs_Diff_Geno import *
from USV.usvDescription import *


def plotBehaviouralEventBothSexes(ax, behavEvent, valueCatEvent, title, image, zoom, profileDataM, profileDataF, night, letter, text_file, mode):

    singlePlotPerEventProfilePairBothSexes(profileDataM=profileDataM, profileDataF=profileDataF,
                                           night=night,
                                           valueCat=valueCatEvent, behavEvent=behavEvent, ax=ax,
                                           letter=letter, text_file=text_file, image=image,
                                           zoom=zoom, mode=mode)

    ax.set_title(title, fontsize=16)
    ax.set_xticklabels(['males', 'females'], fontsize=16)



if __name__ == '__main__':

    print("Code launched.")
    # set font
    from matplotlib import rc, gridspec

    rc('font', **{'family': 'serif', 'serif': ['Arial']})
    # List of events to be computed within the behavioural profile2, and header for the computation of the total distance travelled.
    behaviouralEventOneMouse = ["Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact",
                                "Side by side Contact, opposite way", "Social approach", "Get away", "Approach contact",
                                "Approach rear", "Break contact", "FollowZone Isolated", "Train2", "Group2", "Group3",
                                "Group 3 break", "Group 3 make", "Group 4 break", "Group 4 make", "Huddling",
                                "Move isolated", "Move in contact", "Nest3_", "Nest4_", "Rearing", "Rear isolated",
                                "Rear in contact", "Stop isolated", "WallJump", "Water Zone", "totalDistance",
                                "experiment"]
    behaviouralEventOneMouse = ["Move isolated", "Move in contact", "WallJump", "Stop isolated", "Rear isolated",
                                "Rear in contact",
                                "Contact", "Group2", "Group3", "Oral-oral Contact", "Oral-genital Contact",
                                "Side by side Contact", "Side by side Contact, opposite way",
                                "Train2", "FollowZone Isolated",
                                "Social approach", "Approach contact",
                                "Group 3 make", "Group 4 make", "Get away", "Break contact",
                                "Group 3 break", "Group 4 break",
                                "totalDistance", "experiment"
                                ]
    behaviouralEventOneMouseSingle = ["Move isolated", "Move in contact", "WallJump", "Stop isolated", "Rear isolated",
                                      "Rear in contact"]
    behaviouralEventOneMouseSocial = ["Contact", "Group2", "Oral-oral Contact", "Oral-genital Contact",
                                      "Side by side Contact", "Side by side Contact, opposite way",
                                      "Train2", "FollowZone Isolated",
                                      "Social approach", "Approach contact",
                                      "Get away", "Break contact"]

    while True:
        question = "Do you want to:"
        question += "\n\t [1] plot figure with selected symetric behaviours for pairs for both sexes (from json file)?"
        question += "\n\t [2] plot figure with selected assymetric social behaviours for pairs of mice (from json file)?"
        question += "\n"
        answer = input(question)

        if answer == "1":
            text_file = getFileNameInput()
            #fix the night:
            n = '0'
            print('Choose the file for the males')
            fileM = getJsonFileToProcess()

            print('Choose the file for the females')
            fileF = getJsonFileToProcess()

            # create a dictionary with profile data
            with open(fileM) as json_data:
                profileDataMFull = json.load(json_data)

            with open(fileF) as json_data:
                profileDataFFull = json.load(json_data)

            print("json files for profile data re-imported.")

            #reduce the data dictionaries to fit with the types of behaviours
            profileDataMPair = {}
            profileDataFPair = {}
            profileDataMInd = {}
            profileDataFInd = {}
            for file in profileDataMFull.keys():
                profileDataMPair[file] = {str(n): {}}
                profileDataMInd[file] = {str(n): {}}
                for ind in profileDataMFull[file][str(n)].keys():
                    if '_' in ind:
                        profileDataMPair[file][str(n)][ind] = profileDataMFull[file][str(n)][ind]
                    if '_' not in ind:
                        profileDataMInd[file][str(n)][ind] = profileDataMFull[file][str(n)][ind]

            for file in profileDataFFull.keys():
                profileDataFPair[file] = {str(n): {}}
                profileDataFInd[file] = {str(n): {}}
                for ind in profileDataFFull[file][str(n)].keys():
                    if '_' in ind:
                        profileDataFPair[file][str(n)][ind] = profileDataFFull[file][str(n)][ind]
                    if '_' not in ind:
                        profileDataFInd[file][str(n)][ind] = profileDataFFull[file][str(n)][ind]

            #Plot fig and save it in a pdf file

            letter = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

            fig, axes = plt.subplots(nrows=1, ncols=5, figsize=(20, 4))
            k = 0

            # plot the data for each behavioural event
            #Fig 1B
            row = 0
            col = 0
            behavEvent = 'Contact'
            valueCatEvent = ' Nb'
            image = 'img_cct.jpg'
            imgPos = (0.5, 350)
            zoom = 0.6

            ax = axes[col]
            singlePlotPerEventProfilePairBothSexes(profileDataM=profileDataMPair, profileDataF=profileDataFPair, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=ax,
                                               letter=letter[k], text_file=text_file, image=image, imgPos=imgPos, zoom=zoom)
            wtPatch = mpatches.Patch(edgecolor='black', facecolor='steelblue', label='WT_B6')
            delPatch = mpatches.Patch(edgecolor='black', facecolor='darkorange', label='HZ_B6')
            handles = [wtPatch, delPatch]
            ax.legend(handles=handles, loc=(0.02, 0.02)).set_visible(True)
            ax.set_title("contact", fontsize=16)
            ax.set_xticklabels(['males', 'females'], fontsize=14)
            k += 1

            # Fig 1C
            row = 0
            col = 1
            behavEvent = 'Contact'
            valueCatEvent = ' MeanDur'
            image = 'img_cct.jpg'
            imgPos = (0.5, 1500)
            zoom = 0.6

            ax = axes[col]
            singlePlotPerEventProfilePairBothSexes(profileDataM=profileDataMPair, profileDataF=profileDataFPair, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=ax,
                                               letter=letter[k], text_file=text_file, image=image, imgPos=imgPos,
                                               zoom=zoom)
            ax.set_title("contact", fontsize=16)
            ax.set_xticklabels(['males', 'females'], fontsize=14)
            k += 1

            # Fig 1D
            row = 0
            col = 2
            behavEvent = 'Oral-oral Contact'
            valueCatEvent = ' TotalLen'
            image='img_nose-nose.jpg'
            imgPos = (0.5, 100)
            zoom = 0.6
            ax = axes[col]
            singlePlotPerEventProfilePairBothSexes(profileDataM=profileDataMPair, profileDataF=profileDataFPair, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=ax,
                                               letter=letter[k], text_file=text_file, image=image, imgPos=imgPos, zoom=zoom)
            ax.set_title("nose-nose contact", fontsize=16)
            ax.set_xticklabels(['males', 'females'], fontsize=14)
            k += 1

            # Fig 1D
            row = 0
            col = 3
            behavEvent = 'Oral-oral Contact'
            valueCatEvent = ' Nb'
            image = 'img_nose-nose.jpg'
            imgPos = (0.5, 1000)
            zoom = 0.6
            ax = axes[col]
            singlePlotPerEventProfilePairBothSexes(profileDataM=profileDataMPair, profileDataF=profileDataFPair,
                                                   night=n,
                                                   valueCat=valueCatEvent, behavEvent=behavEvent, ax=ax,
                                                   letter=letter[k], text_file=text_file, image=image, imgPos=imgPos,
                                                   zoom=zoom)
            ax.set_title("nose-nose contact", fontsize=16)
            ax.set_xticklabels(['males', 'females'], fontsize=14)
            k += 1

            """# Fig 1E
            row = 2
            col = 0
            behavEvent = 'Side by side Contact'
            valueCatEvent = ' TotalLen'
            image = 'img_side-side.jpg'
            imgPos = (0.5, 160)
            zoom = 0.5
            ax = axes[row, col]
            singlePlotPerEventProfilePairBothSexes(profileDataM=profileDataMPair, profileDataF=profileDataFPair, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=ax,
                                               letter=letter[k], text_file=text_file, image=image, imgPos=imgPos,
                                               zoom=zoom)

            ax.set_title("side-side contact", fontsize=16)
            ax.set_xticklabels(['males', 'females'], fontsize=14)
            k += 1
"""
            # Fig 1F
            row = 0
            col = 4
            behavEvent = 'Side by side Contact'
            valueCatEvent = ' MeanDur'
            image = 'img_side-side.jpg'
            imgPos = (0.5, 27)
            zoom = 0.5
            ax = axes[col]
            singlePlotPerEventProfilePairBothSexes(profileDataM=profileDataMPair, profileDataF=profileDataFPair, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=ax,
                                               letter=letter[k], text_file=text_file, image=image, imgPos=imgPos,
                                               zoom=zoom)
            ax.set_title("side-side contact", fontsize=16)
            ax.set_xticklabels(['males', 'females'], fontsize=14)
            k += 1


            fig.tight_layout()
            fig.show()
            fig.savefig("Fig_pairs_paired_behav_both_sexes.pdf", dpi=300)
            fig.savefig("Fig_pairs_paired_behav_both_sexes.png", dpi=300)
            plt.close(fig)


            print ("Plots saved as pdf and png.")

            text_file.close()
            break


        if answer == "2":
            text_file = getFileNameInput()
            # fix the night:
            n = '0'
            print('Choose the file for the males')
            fileM = getJsonFileToProcess()

            print('Choose the file for the females')
            fileF = getJsonFileToProcess()

            # create a dictionary with profile data
            with open(fileM) as json_data:
                profileDataMFull = json.load(json_data)

            with open(fileF) as json_data:
                profileDataFFull = json.load(json_data)

            print("json files for profile data re-imported.")

            # reduce the data dictionaries to fit with the types of behaviours
            profileDataMPair = {}
            profileDataFPair = {}
            profileDataMInd = {}
            profileDataFInd = {}
            for file in profileDataMFull.keys():
                profileDataMPair[file] = {str(n): {}}
                profileDataMInd[file] = {str(n): {}}
                for ind in profileDataMFull[file][str(n)].keys():
                    if '_' in ind:
                        profileDataMPair[file][str(n)][ind] = profileDataMFull[file][str(n)][ind]
                    if '_' not in ind:
                        profileDataMInd[file][str(n)][ind] = profileDataMFull[file][str(n)][ind]

            for file in profileDataFFull.keys():
                profileDataFPair[file] = {str(n): {}}
                profileDataFInd[file] = {str(n): {}}
                for ind in profileDataFFull[file][str(n)].keys():
                    if '_' in ind:
                        profileDataFPair[file][str(n)][ind] = profileDataFFull[file][str(n)][ind]
                    if '_' not in ind:
                        profileDataFInd[file][str(n)][ind] = profileDataFFull[file][str(n)][ind]

            # Plot fig and save it in a pdf file

            letterList = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']

            '''behavEventList = ['totalDistance', 'Move isolated', 'Move isolated', 'Rear isolated', 'Rear isolated']
            valueCatEventList = ['', ' TotalLen', ' MeanDur', ' TotalLen', ' MeanDur']'''
            behavEventList = ['Oral-genital Contact', 'Oral-genital Contact', 'Train2', 'Train2', 'FollowZone Isolated', 'Social approach']
            valueCatEventList = [' TotalLen', ' MeanDur', ' TotalLen', ' MeanDur', ' TotalLen', ' Nb']
            imageDic = {'totalDistance': 'img_moving.jpg', 'Move isolated': 'img_moving.jpg', 'Rear isolated': 'img_rearing.jpg',
                        'Oral-genital Contact': 'img_nose-anogenital.jpg', 'Train2': 'img_train2.jpg', 'FollowZone Isolated': 'img_follow.jpg', 'Social approach': 'img_soc_app.jpg'}
            zoomDic = {'totalDistance': 0.55, 'Move isolated': 0.55, 'Rear isolated': 0.3,
                       'Oral-genital Contact': 0.55, 'Train2': 0.33, 'FollowZone Isolated': 0.32, 'Social approach':0.36}
            titleDic = {'totalDistance': 'total distance', 'Move isolated': 'moving alone', 'Rear isolated': 'rearing',
                        'Oral-genital Contact': 'oral-anogenital contact', 'Train2': 'train2', 'FollowZone Isolated': 'follow', 'Social approach': 'social approach'}

            fig, axes = plt.subplots(nrows=1, ncols=len(behavEventList), figsize=(4*len(behavEventList), 6))
            k = 0

            # plot the data for each behavioural event
            # Fig 1A
            #row = 0
            col = 0
            for col in range(len(behavEventList)):
                ax = axes[col]
                plotBehaviouralEventBothSexes(ax = ax, behavEvent=behavEventList[k], title=titleDic[behavEventList[k]], valueCatEvent=valueCatEventList[k], image=imageDic[behavEventList[k]], zoom=zoomDic[behavEventList[k]], profileDataM=profileDataMInd,
                                              profileDataF=profileDataFInd, night=n, letter=letterList[k], text_file= text_file, mode='single')

                k += 1

            """wtPatch = mpatches.Patch(edgecolor='black', facecolor='steelblue', label='WT')
            delPatch = mpatches.Patch(edgecolor='black', facecolor='darkorange', label='HZ')
            B6Patch = mpatches.Patch(edgecolor='black', facecolor='green', label='B6')
            handles = [wtPatch, delPatch, B6Patch]"""
            wtPatch = mpatches.Patch(edgecolor='black', facecolor='steelblue', label='WT')
            delPatch = mpatches.Patch(edgecolor='black', facecolor='darkorange', label='KO')
            handles = [wtPatch, delPatch]
            axes[0].legend(handles=handles, loc=(0.75, 0.70)).set_visible(True)


            fig.tight_layout()
            fig.savefig("Fig_pairs_asymetric_behav_both_sexes.pdf", dpi=300)
            fig.savefig("Fig_pairs_asymetric_behav_both_sexes.png", dpi=300)
            plt.close(fig)

            print ("Plots saved as pdf and png and analyses saved in text file.")

            text_file.close()
            break
