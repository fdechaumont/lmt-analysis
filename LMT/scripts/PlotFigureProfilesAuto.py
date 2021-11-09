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
from USV.usvDescription.Compute_Number_USVs_Diff_Geno import *
from USV.usvDescription import *

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
        question += "\n\t [1] plot figure with selected behaviours for one sex only (from json file)?"
        question += "\n\t [2] plot figure with selected behaviours for both sexes (from json file)?"
        question += "\n\t [3] plot figure with selected behaviours for pairs of mice (from json file)?"
        question += "\n\t [4] plot figure with selected behaviours for pairs of mice (from json file) for master?"
        question += "\n\t [5] plot figure for LMT presentation in grant application?"
        question += "\n"
        answer = input(question)

        if answer == "1":
            text_file = getFileNameInput()
            #fix the night:
            n = 1
            file = getJsonFileToProcess()
            print(file)
            # create a dictionary with profile data
            with open(file) as json_data:
                profileData = json.load(json_data)

            print("json file for profile data re-imported.")
            #Plot fig and save it in a pdf file

            fig, axes = plt.subplots(nrows=2, ncols=4, figsize=(14, 9))
            fig.suptitle(t="no night", y=1.2, fontweight='bold')

            # plot the data for each behavioural event
            #Fig 1A
            row = 0
            col = 0
            behavEvent = 'Contact'
            valueCatEvent = ' TotalLen'
            singlePlotPerEventProfile(profileData=profileData, night=n, valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row, col])

            # Fig 1B
            row = 0
            col = 1
            behavEvent = 'FollowZone Isolated'
            valueCatEvent = ' TotalLen'
            singlePlotPerEventProfile(profileData=profileData, night=n, valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row, col])

            # Fig 1C
            row = 0
            col = 2
            behavEvent = 'Oral-oral Contact'
            valueCatEvent = ' TotalLen'
            singlePlotPerEventProfile(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, ax=axes[row, col])

            # Fig 1D
            row = 0
            col = 3
            behavEvent = 'Oral-genital Contact'
            valueCatEvent = ' TotalLen'
            singlePlotPerEventProfile(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, ax=axes[row, col])

            # Fig 1E
            row = 1
            col = 0
            behavEvent = 'Side by side Contact'
            valueCatEvent = ' TotalLen'
            singlePlotPerEventProfile(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, ax=axes[row, col])

            # Fig 1F
            row = 1
            col = 1
            behavEvent = 'Side by side Contact, opposite way'
            valueCatEvent = ' TotalLen'
            singlePlotPerEventProfile(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, ax=axes[row, col])

            # Fig 1G
            row = 1
            col = 2
            behavEvent = 'Approach contact'
            valueCatEvent = ' TotalLen'
            singlePlotPerEventProfile(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, ax=axes[row, col])

            # Fig 1H: USVs
            row = 1
            col = 3

            fig.tight_layout()
            fig.savefig("FigSimple_Profile_Events_night_{}.pdf".format(n), dpi=100)
            plt.close(fig)


            print ("Plots saved as pdf and analyses saved in text file.")

            text_file.close()
            break


        if answer == "2":
            text_file = getFileNameInput()
            #fix the night:
            n = 1
            print('Choose the file for the males')
            fileM = getJsonFileToProcess()

            print('Choose the file for the females')
            fileF = getJsonFileToProcess()

            # create a dictionary with profile data
            with open(fileM) as json_data:
                profileDataM = json.load(json_data)

            with open(fileF) as json_data:
                profileDataF = json.load(json_data)

            print("json files for profile data re-imported.")
            #Plot fig and save it in a pdf file

            letter = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

            fig, axes = plt.subplots(nrows=2, ncols=5, figsize=(20, 9))
            k = 0
            #insert figure for database extraction
            row = 0
            col = 0
            ax = axes[row, col]
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.tick_params(bottom=False, left=False)
            ax.patch.set_facecolor('white')

            imgPos = (0.5, 0.5)
            image = 'img_lmt_db_player.jpg'
            behavSchema = mpimg.imread(image)
            imgBox = OffsetImage(behavSchema, zoom=0.47)
            imageBox = AnnotationBbox(imgBox, imgPos, frameon=False)
            ax.add_artist(imageBox)

            ax.text(-0.1, 1.06, letter[k], fontsize=20, horizontalalignment='center', color='black', weight='bold')
            k += 1

            # plot the data for each behavioural event
            #Fig 1B
            row = 0
            col = 1
            behavEvent = 'Contact'
            valueCatEvent = ' TotalLen'
            image = 'img_cct.jpg'
            imgPos = (0.5, 23000)
            zoom = 0.7

            ax = axes[row, col]
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=ax,
                                               letter=letter[k], text_file=text_file, image=image, imgPos=imgPos, zoom=zoom)
            wtPatch = mpatches.Patch(edgecolor='black', facecolor='steelblue', label='WT')
            delPatch = mpatches.Patch(edgecolor='black', facecolor='darkorange', label='Del/+')
            handles = [wtPatch, delPatch]
            ax.legend(handles=handles, loc=(0.02, 0.1)).set_visible(True)
            ax.set_title("contact", fontsize=16)
            ax.set_xticklabels(['males', 'femelles'], fontsize=14)
            k += 1

            # Fig 1C
            row = 0
            col = 2
            behavEvent = 'Oral-oral Contact'
            valueCatEvent = ' Nb'
            image='img_nose-nose.jpg'
            imgPos = (0.5, 18000)
            zoom = 0.6
            ax = axes[row, col]
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=ax,
                                               letter=letter[k], text_file=text_file, image=image, imgPos=imgPos, zoom=zoom)
            ax.set_title("contact nez-nez", fontsize=16)
            ax.set_xticklabels(['males', 'femelles'], fontsize=14)
            k += 1

            # Fig 1D
            row = 0
            col = 3
            behavEvent = 'Oral-genital Contact'
            valueCatEvent = ' Nb'
            image = 'img_nose-anogenital.jpg'
            imgPos = (0.5, 18500)
            zoom = 0.65
            ax = axes[row, col]
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=ax,
                                               letter=letter[k], text_file=text_file, image=image, imgPos=imgPos, zoom=zoom)
            ax.set_title("contact nez-anogenital", fontsize=16)
            ax.set_xticklabels(['males', 'femelles'], fontsize=14)
            k += 1

            # Fig 1E
            row = 0
            col = 4
            behavEvent = 'Side by side Contact'
            valueCatEvent = ' Nb'
            image = 'img_side-side.jpg'
            imgPos = (0.5, 17000)
            zoom = 0.65
            ax = axes[row, col]
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=ax,
                                               letter=letter[k], text_file=text_file, image=image, imgPos=imgPos, zoom=zoom)

            ax.set_title("contact cote-a-cote", fontsize=16)
            ax.set_xticklabels(['males', 'femelles'], fontsize=14)
            k += 1

            # Fig 1F
            row = 1
            col = 0
            behavEvent = 'Side by side Contact, opposite way'
            valueCatEvent = ' Nb'
            image = 'img_side-side_opp.jpg'
            imgPos = (0.5, 16000)
            zoom = 0.4
            ax = axes[row, col]
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=ax,
                                               letter=letter[k], text_file=text_file, image=image, imgPos=imgPos,
                                               zoom=zoom)
            ax.set_title("contact cote-a-cote, tete beche", fontsize=16)
            ax.set_xticklabels(['males', 'femelles'], fontsize=14)
            k += 1

            # Fig 1G
            row = 1
            col = 1
            behavEvent = 'Social approach'
            valueCatEvent = ' Nb'
            image = 'img_soc_app.jpg'
            imgPos = (0.5, 90000)
            zoom = 0.38
            ax = axes[row, col]
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=ax,
                                               letter=letter[k], text_file=text_file, image=image, imgPos=imgPos, zoom=zoom)
            ax.set_title("approche", fontsize=16)
            ax.set_xticklabels(['males', 'femelles'], fontsize=14)
            k += 1

            # Fig 1H
            row = 1
            col = 2
            behavEvent = 'Approach contact'
            valueCatEvent = ' Nb'
            image = 'img_app_cct.jpg'
            imgPos = (0.5, 80000)
            zoom = 0.5
            ax = axes[row, col]
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=ax,
                                               letter=letter[k], text_file=text_file, image=image,
                                               imgPos=imgPos, zoom=zoom)
            ax.set_title("approche avant contact", fontsize=16)
            ax.set_xticklabels(['males', 'femelles'], fontsize=14)
            k += 1

            # Fig 1I
            row = 1
            col = 3
            behavEvent = 'Get away'
            valueCatEvent = ' TotalLen'
            image = 'img_getaway.jpg'
            imgPos = (0.5, 11500)
            zoom = 0.4
            ax = axes[row, col]
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=ax,
                                               letter=letter[k], text_file=text_file, image=image,
                                               imgPos=imgPos, zoom=zoom)
            ax.set_title("echappement", fontsize=16)
            ax.set_xticklabels(['males', 'femelles'], fontsize=14)
            k += 1

            # Fig 1J
            row = 1
            col = 4
            behavEvent = 'Break contact'
            valueCatEvent = ' TotalLen'
            image = 'img_break_cct.jpg'
            imgPos = (0.5, 1900)
            zoom = 0.35
            ax = axes[row, col]
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=ax,
                                               letter=letter[k], text_file=text_file, image=image,
                                               imgPos=imgPos, zoom=zoom)
            ax.set_title("rupture de contact", fontsize=16)
            ax.set_xticklabels(['males', 'femelles'], fontsize=14)

            fig.tight_layout()
            fig.show()
            fig.savefig("FigSimple_Profile_Events_3d_both_sexes.pdf", dpi=300)
            plt.close(fig)


            print ("Plots saved as pdf.")

            text_file.close()
            break

        if answer == "3":
            #text_file = getFileNameInput()
            #fix the night:
            n = 1
            file = getJsonFileToProcess()
            print(file)
            # create a dictionary with profile data
            with open(file) as json_data:
                profileData = json.load(json_data)

            print("json file for profile data re-imported.")
            #Plot fig and save it in a pdf file

            fig, axes = plt.subplots(nrows=2, ncols=4, figsize=(14, 9))
            fig.suptitle(t="no night", y=1.2, fontweight='bold')

            # plot the data for each behavioural event
            #Fig 1A
            row = 0
            col = 0
            behavEvent = 'Contact'
            valueCatEvent = ' TotalLen'
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row, col])

            # Fig 1B
            row = 0
            col = 1
            behavEvent = 'FollowZone Isolated'
            valueCatEvent = ' TotalLen'
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row, col])

            # Fig 1C
            row = 0
            col = 2
            behavEvent = 'Oral-oral Contact'
            valueCatEvent = ' TotalLen'
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, ax=axes[row, col])

            # Fig 1D
            row = 0
            col = 3
            behavEvent = 'Oral-genital Contact'
            valueCatEvent = ' TotalLen'
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, ax=axes[row, col])

            # Fig 1E
            row = 1
            col = 0
            behavEvent = 'Side by side Contact'
            valueCatEvent = ' TotalLen'
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, ax=axes[row, col])

            # Fig 1F
            row = 1
            col = 1
            behavEvent = 'Side by side Contact, opposite way'
            valueCatEvent = ' TotalLen'
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, ax=axes[row, col])

            # Fig 1G
            row = 1
            col = 2
            behavEvent = 'Approach contact'
            valueCatEvent = ' TotalLen'
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, ax=axes[row, col])


            fig.tight_layout()
            fig.savefig("FigSimple_Profile_Events_night_pair_{}.pdf".format(n), dpi=100)
            plt.close(fig)


            print ("Plots saved as pdf and analyses saved in text file.")

            #text_file.close()
            break

        if answer == "4":
            #text_file = getFileNameInput()
            file = getJsonFileToProcess()
            print(file)
            # create a dictionary with profile data
            with open(file) as json_data:
                profileData = json.load(json_data)

            print("json file for profile data re-imported.")
            #Plot fig and save it in a pdf file
            letter = ['A', 'B', 'C', 'D', 'E', 'F']
            k = 0
            fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(12, 8))

            # plot the data for each behavioural event
            #Fig 1A
            n = 2
            row = 0
            col = 0
            behavEvent = 'Train2'
            valueCatEvent = ' Nb'
            image = 'img_train2.jpg'
            imgPos = (0.5, 36)
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent, behavEvent=behavEvent, letter=letter[k], ax=axes[row, col], image=image, imgPos=imgPos, zoom=0.20)
            axes[row, col].set_ylabel("nombre d'occurrences", fontsize=16)
            wtPatch = mpatches.Patch(edgecolor='black', facecolor='steelblue', label='WT-WT')
            delPatch = mpatches.Patch(edgecolor='black', facecolor='darkorange', label='Del/+-Del/+')
            handles = [wtPatch, delPatch]
            axes[row, col].legend(handles=handles, loc=(0.02, 0.1)).set_visible(True)
            k += 1

            # Fig 1B
            n = 2
            row = 0
            col = 1
            behavEvent = 'Contact'
            valueCatEvent = ' TotalLen'
            image = 'img_cct.jpg'
            imgPos = (0.5, 11100)
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent, behavEvent=behavEvent, letter=letter[k], ax=axes[row, col], image=image, imgPos=imgPos, zoom=0.36)
            axes[row, col].set_ylabel("duree totale (s)", fontsize=16)
            k += 1

            # Fig 1C
            n = 2
            row = 0
            col = 2
            behavEvent = 'Social approach'
            valueCatEvent = ' Nb'
            image = 'img_soc_app.jpg'
            imgPos = (0.5, 66000)
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, letter=letter[k], ax=axes[row, col], image=image, imgPos=imgPos, zoom=0.23)
            axes[row, col].set_ylabel("nombre d'occurrences", fontsize=16)
            k += 1

            # Fig 1D
            n = 2
            row = 1
            col = 0
            behavEvent = 'Approach contact'
            valueCatEvent = ' Nb'
            image = 'img_app_cct.jpg'
            imgPos = (0.5, 56000)
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, letter=letter[k], ax=axes[row, col], image=image, imgPos=imgPos, zoom=0.3)
            axes[row, col].set_ylabel("nombre d'occurrences", fontsize=16)
            k += 1

            # Fig 1E
            n = 1
            row = 1
            col = 1
            behavEvent = 'Get away'
            valueCatEvent = ' TotalLen'
            image = 'img_getaway.jpg'
            imgPos = (0.5, 10400)
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, letter=letter[k], ax=axes[row, col], image=image, imgPos=imgPos, zoom=0.22)
            axes[row, col].set_ylabel('duree totale (s)', fontsize=16)
            k += 1

            # Fig 1F
            n = 2
            row = 1
            col = 2
            behavEvent = 'Break contact'
            valueCatEvent = ' TotalLen'
            image = 'img_break_cct.jpg'
            imgPos = (0.5, 1550)
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, letter=letter[k], ax=axes[row, col], image=image, imgPos=imgPos, zoom=0.18)
            axes[row, col].set_ylabel('duree totale (s)', fontsize=16)


            fig.tight_layout()
            fig.show()
            fig.savefig("FigSimple_Profile_Events_night_pair_AR.pdf", dpi=300)
            plt.close(fig)

            print ("Plots saved as pdf.")

            break

        if answer == "5":
            # Create general figure
            gs = gridspec.GridSpec(3, 12)
            fig = plt.figure(figsize=(24, 16))

            #subplot for lmt setup
            ax = fig.add_subplot(gs[0, 0:3])
            letter = 'A'
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.tick_params(bottom=False, left=False)
            #ax.patch.set_facecolor('white')

            image = 'img_lmt_video.jpg'
            imgPos = (0.3, 0.5)
            zoom = 0.33

            behavSchema = mpimg.imread(image)
            imgBox = OffsetImage(behavSchema, zoom=zoom)
            imageBox = AnnotationBbox(imgBox, imgPos, frameon=False)
            ax.add_artist(imageBox)

            ax.text(-0.4, 1.06, letter, fontsize=28, horizontalalignment='center', color='black', weight='bold')

            #subplot for lmt player
            ax = fig.add_subplot(gs[0, 3:6])
            letter = 'B'
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.tick_params(bottom=False, left=False)
            #ax.patch.set_facecolor('white')

            image = 'img_lmt_db_player.jpg'
            imgPos = (0.5, 0.5)
            zoom = 0.63

            behavSchema = mpimg.imread(image)
            imgBox = OffsetImage(behavSchema, zoom=zoom)
            imageBox = AnnotationBbox(imgBox, imgPos, frameon=False)
            ax.add_artist(imageBox)

            ax.text(-0.1, 1.06, letter, fontsize=28, horizontalalignment='center', color='black', weight='bold')

            # subplot for behaviours
            ax = fig.add_subplot(gs[1:3, 0:6])
            letter = 'C'
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.tick_params(bottom=False, left=False)
            ax.patch.set_facecolor('white')

            image = 'img_behav_lmt.png'
            imgPos = (0.4, 0.4)
            zoom = 0.75

            behavSchema = mpimg.imread(image)
            imgBox = OffsetImage(behavSchema, zoom=zoom)
            imageBox = AnnotationBbox(imgBox, imgPos, frameon=False)
            ax.add_artist(imageBox)

            ax.text(-0.2, 0.95, letter, fontsize=28, horizontalalignment='center', color='black', weight='bold')

            #subplot for Z-scores profile
            ax = fig.add_subplot(gs[0:3, 8:12])
            letter = 'D'
            print('Choose the profile json file to process.')
            file = getJsonFileToProcess()
            # create a dictionary with profile data
            with open(file) as json_data:
                profileData = json.load(json_data)
            print("json file for profile data re-imported.")
            categoryList = [' TotalLen', ' Nb', ' MeanDur']

            mergeProfile = mergeProfileOverNights(profileData=profileData, categoryList=categoryList,
                                                  behaviouralEventOneMouse=behaviouralEventOneMouse)
            # If the profiles are computed over the nights separately as in the original json file:
            # dataToUse = profileData
            # If the profiles are computed over the merged nights:
            dataToUse = mergeProfile

            # compute the data for the control animal of each cage
            genoControl = 'WT'
            wtData = extractControlData(profileData=dataToUse, genoControl=genoControl, behaviouralEventOneMouse=behaviouralEventOneMouse)
            wtData = extractCageData(profileData=dataToUse, behaviouralEventOneMouse=behaviouralEventOneMouse)

            # compute the mutant data, centered and reduced for each cage
            genoMutant = 'Del/+'
            koData = generateMutantData(profileData=dataToUse, genoMutant=genoMutant, wtData=wtData,
                                        categoryList=categoryList, behaviouralEventOneMouse=behaviouralEventOneMouse)

            print(koData)

            cat = ' TotalLen'

            koDataDic = {}
            for key in ['night', 'trait', 'rfid', 'exp', 'value']:
                koDataDic[key] = []
            night = 'all nights'

            for file in koData.keys():
                print('file: ', file)
                for night in koData[file].keys():
                    print('night: ', night)
                    for rfid in koData[file][night].keys():
                        print('rfid: ', rfid)
                        eventListForTest = []
                        for event in koData[file][night][rfid].keys():
                            print('event: ', event)
                            if (cat in event) or (event == 'totalDistance'):
                                koDataDic['exp'].append(file)
                                koDataDic['night'].append(night)
                                koDataDic['rfid'].append(rfid)
                                koDataDic['trait'].append(event)
                                koDataDic['value'].append(koData[file][night][rfid][event])
                                eventListForTest.append(event)

            koDataframe = pd.DataFrame.from_dict(koDataDic)
            # print(koDataframe)

            night = 'all nights'
            plotZScoreProfileAuto(ax=ax, koDataframe=koDataframe, night=night, eventListForTest=eventListForTest)

            ax.text(-5, -1, letter, fontsize=28, horizontalalignment='center', color='black', weight='bold')


            plt.tight_layout()
            plt.show()
            fig.savefig('figure_lmt_social.pdf', dpi=300)
            fig.savefig('figure_lmt_social.jpg', dpi=300)
            print('Job done.')
            break

        if answer == "6":
            # Create general figure
            gs = gridspec.GridSpec(1, 20)
            fig = plt.figure(figsize=(10, 16))

            # subplot for lmt setup
            ax = fig.add_subplot(gs[0, 0])
            letter = ''
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.tick_params(bottom=False, left=False)

            # subplot for Z-scores profile
            ax = fig.add_subplot(gs[0, 10:20])
            letter=''
            print('Choose the profile json file to process.')
            file = getJsonFileToProcess()
            # create a dictionary with profile data
            with open(file) as json_data:
                profileData = json.load(json_data)
            print("json file for profile data re-imported.")
            categoryList = [' TotalLen', ' Nb', ' MeanDur']

            mergeProfile = mergeProfileOverNights(profileData=profileData, categoryList=categoryList,
                                                  behaviouralEventOneMouse=behaviouralEventOneMouse)
            # If the profiles are computed over the nights separately as in the original json file:
            # dataToUse = profileData
            # If the profiles are computed over the merged nights:
            dataToUse = mergeProfile

            # compute the data for the control animal of each cage
            genoControl = 'WT'
            wtData = extractControlData(profileData=dataToUse, genoControl=genoControl,
                                        behaviouralEventOneMouse=behaviouralEventOneMouse)
            wtData = extractCageData(profileData=dataToUse, behaviouralEventOneMouse=behaviouralEventOneMouse)

            # compute the mutant data, centered and reduced for each cage
            genoMutant = 'Del/+'
            koData = generateMutantData(profileData=dataToUse, genoMutant=genoMutant, wtData=wtData,
                                        categoryList=categoryList, behaviouralEventOneMouse=behaviouralEventOneMouse)

            print(koData)

            cat = ' TotalLen'

            koDataDic = {}
            for key in ['night', 'trait', 'rfid', 'exp', 'value']:
                koDataDic[key] = []
            night = 'all nights'

            for file in koData.keys():
                print('file: ', file)
                for night in koData[file].keys():
                    print('night: ', night)
                    for rfid in koData[file][night].keys():
                        print('rfid: ', rfid)
                        eventListForTest = []
                        for event in koData[file][night][rfid].keys():
                            print('event: ', event)
                            if (cat in event) or (event == 'totalDistance'):
                                koDataDic['exp'].append(file)
                                koDataDic['night'].append(night)
                                koDataDic['rfid'].append(rfid)
                                koDataDic['trait'].append(event)
                                koDataDic['value'].append(koData[file][night][rfid][event])
                                eventListForTest.append(event)

            koDataframe = pd.DataFrame.from_dict(koDataDic)
            # print(koDataframe)

            night = 'all nights'
            plotZScoreProfileAuto(ax=ax, koDataframe=koDataframe, night=night, eventListForTest=eventListForTest)

            ax.text(-5, -1, letter, fontsize=28, horizontalalignment='center', color='black', weight='bold')

            plt.tight_layout()
            plt.show()
            fig.savefig('figure_lmt_social_profile.pdf', dpi=300)
            fig.savefig('figure_lmt_social_profile.jpg', dpi=300)
            print('Job done.')
            break
