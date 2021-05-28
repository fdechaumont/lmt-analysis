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

            fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(12, 9))
            fig.suptitle(t="no night", y=1.2, fontweight='bold')

            # plot the data for each behavioural event
            #Fig 1A
            row = 0
            col = 0
            behavEvent = 'Oral-oral Contact'
            # behavEvent = 'FollowZone Isolated'
            valueCatEvent = ' Nb'
            imgPos = (0.5, 17000)
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row, col], row=row, col=col,
                                               letter='A', text_file=text_file, image='img_nose-nose.jpg', imgPos=imgPos)
            axes[row, col].legend(loc='lower left', fancybox=False, ncol=2).set_visible(True)

            # Fig 1B
            row = 0
            col = 1
            behavEvent = 'Oral-genital Contact'
            valueCatEvent = ' Nb'
            imgPos = (0.5, 18000)
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row, col], row=row, col=col,
                                               letter='B', text_file=text_file, image='img_nose-anogenital.jpg', imgPos=imgPos)

            # Fig 1C
            row = 0
            col = 2
            behavEvent = 'Side by side Contact'
            valueCatEvent = ' TotalLen'
            imgPos = (0.5, 5400)
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row, col],
                                               letter='C', text_file=text_file, image='img_side-side.jpg', imgPos=imgPos)

            # Fig 1D
            row = 1
            col = 0
            behavEvent = 'Contact'
            valueCatEvent = ' MeanDur'
            image = 'img_cct.jpg'
            imgPos = (0.5, 160)
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row, col],
                                               letter='D', text_file=text_file, image='img_cct.jpg', imgPos=imgPos)

            # Fig 1E
            row = 1
            col = 1
            behavEvent = 'Approach contact'
            valueCatEvent = ' Nb'
            imgPos = (0.5, 79500)
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n, valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row, col], letter='E', text_file=text_file, image='img_app_cct.jpg', imgPos=imgPos)

            # Fig 1F: USVs
            row = 1
            col = 2

            df = createDataframeFromJsonNumberUsvPerBurstDiffGeno(jsonFile='dataUsvDescriptionDiffGeno750_16p11.json')
            dataframe = getDataFramePerSex(df, sex='female')
            yMinUsv = {'nbUsvBurst': 0}
            yMaxUsv = {'nbUsvBurst': 50}
            strainListShort = ['B6C3B16p11.2']
            genoList = ['WT-WT', 'Del/+-Del/+']

            plotNumberUsvPerBurstBoxplotDiffGeno(ax=axes[row,col], dataframe=dataframe, yMinUsv=yMinUsv,
                                                 yMaxUsv=yMaxUsv, letter='F', strain=strainListShort[0], sex='female',
                                                 genoList=genoList)

            # create model:
            print('nbUsvBurst')
            model = smf.mixedlm("nbUsvBurst ~ geno", dataframe, groups=dataframe['pair'])
            # run model:
            result = model.fit()
            # print summary
            print(result.summary())
            text_file.write('{} {}'.format('females', 'number of USV per burst'))
            text_file.write(result.summary().as_text())
            text_file.write('\n')
            p = 0.006
            axes[row,col].text(0.5, yMaxUsv['nbUsvBurst'] - 0.06 * (yMaxUsv['nbUsvBurst'] - yMinUsv['nbUsvBurst']),
                    getStarsFromPvalues(p, 1), FontSize=16, horizontalalignment='center', color='black', weight='bold')

            fig.tight_layout()
            fig.savefig("FigSimple_Profile_Events_night_{}.pdf".format(n), dpi=100)
            plt.close(fig)


            print ("Plots saved as pdf and analyses saved in text file.")

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

            fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(12, 8))

            # plot the data for each behavioural event
            #Fig 1A
            n = 2
            row = 0
            col = 0
            behavEvent = 'Train2'
            valueCatEvent = ' Nb'
            image = 'img_train2.jpg'
            imgPos = (0.5, 30)
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row, col], image=image, imgPos=imgPos)
            axes[row, col].set_ylabel("nombre d'occurrences", fontsize=16)
            wtPatch = mpatches.Patch(edgecolor='black', facecolor='steelblue', label='WT-WT')
            delPatch = mpatches.Patch(edgecolor='black', facecolor='darkorange', label='Del/+-Del/+')
            handles = [wtPatch, delPatch]
            axes[row, col].legend(handles=handles, loc=(0.02, 0.1)).set_visible(True)

            # Fig 1B
            n = 2
            row = 0
            col = 1
            behavEvent = 'Contact'
            valueCatEvent = ' TotalLen'
            image = 'img_cct.jpg'
            imgPos = (0.5, 30)
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row, col], image=image, imgPos=imgPos)
            axes[row, col].set_ylabel("duree totale (s)", fontsize=16)

            # Fig 1C
            n = 2
            row = 0
            col = 2
            behavEvent = 'Social approach'
            valueCatEvent = ' Nb'
            image = 'img_soc_app.jpg'
            imgPos = (0.5, 30)
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, ax=axes[row, col], image=image, imgPos=imgPos)
            axes[row, col].set_ylabel("nombre d'occurrences", fontsize=16)

            # Fig 1D
            n = 2
            row = 1
            col = 0
            behavEvent = 'Approach contact'
            valueCatEvent = ' Nb'
            image = 'img_app_cct.jpg'
            imgPos = (0.5, 30)
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, ax=axes[row, col], image=image, imgPos=imgPos)
            axes[row, col].set_ylabel("nombre d'occurrences", fontsize=16)

            # Fig 1E
            n = 1
            row = 1
            col = 1
            behavEvent = 'Get away'
            valueCatEvent = ' TotalLen'
            image = 'img_getaway.jpg'
            imgPos = (0.5, 30)
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, ax=axes[row, col], image=image, imgPos=imgPos)
            axes[row, col].set_ylabel('duree totale (s)', fontsize=16)

            # Fig 1F
            n = 2
            row = 1
            col = 2
            behavEvent = 'Break contact'
            valueCatEvent = ' TotalLen'
            image = 'img_break_cct.jpg'
            imgPos = (0.5, 30)
            singlePlotPerEventProfilePairs(profileData=profileData, night=n, valueCat=valueCatEvent,
                                      behavEvent=behavEvent, ax=axes[row, col], image=image, imgPos=imgPos)
            axes[row, col].set_ylabel('duree totale (s)', fontsize=16)


            fig.tight_layout()
            fig.savefig("FigSimple_Profile_Events_night_pair_AR.pdf", dpi=300)
            plt.close(fig)

            print ("Plots saved as pdf.")

            break

