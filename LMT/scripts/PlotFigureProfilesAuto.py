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
        question += "\n\t [pfig] plot figure with selected behaviours for one sex only (from json file)?"
        question += "\n\t [pfigsex] plot figure with selected behaviours for both sexes (from json file)?"
        question += "\n"
        answer = input(question)

        if answer == "pfig":
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


        if answer == "pfigsex":
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
                                               letter='A', text_file=text_file, pM=0.025, pF=0.015, image='img_nose-nose.jpg', imgPos=imgPos)
            axes[row, col].legend(loc='lower left', fancybox=False, ncol=2).set_visible(True)

            # Fig 1B
            row = 0
            col = 1
            behavEvent = 'Oral-genital Contact'
            valueCatEvent = ' Nb'
            imgPos = (0.5, 18000)
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row, col], row=row, col=col,
                                               letter='B', text_file=text_file, pM=0.003, pF=0.005, image='img_nose-anogenital.jpg', imgPos=imgPos)

            # Fig 1C
            row = 0
            col = 2
            behavEvent = 'Side by side Contact'
            valueCatEvent = ' TotalLen'
            imgPos = (0.5, 5400)
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row, col], row=row, col=col,
                                               letter='C', text_file=text_file, pM=0.044, pF=0.032, image='img_side-side.jpg', imgPos=imgPos)

            # Fig 1D
            row = 1
            col = 0
            behavEvent = 'Contact'
            valueCatEvent = ' MeanDur'
            imgPos = (0.5, 160)
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row, col], row=row, col=col,
                                               letter='D', text_file=text_file, pM=0.014, pF=0.002, image='img_cct.jpg', imgPos=imgPos)

            # Fig 1E
            row = 1
            col = 1
            behavEvent = 'Approach contact'
            valueCatEvent = ' Nb'
            imgPos = (0.5, 79500)
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n, valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row, col], row=row, col=col, letter='E', text_file=text_file, pM=0.005, pF=0.006, image='img_app_cct.jpg', imgPos=imgPos)

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

