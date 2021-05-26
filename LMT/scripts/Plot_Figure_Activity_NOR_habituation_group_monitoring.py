'''
#Created on 26 January 2021

#@author: Elodie
'''
from ComputeMeasuresIdentityProfileOneMouseAutomatic import singlePlotPerEventProfileBothSexes, mergeProfileOverNights
from scripts.Rebuild_All_Event import *
from scripts.Plot_Trajectory_Single_Object_Explo import *
import numpy as np; np.random.seed(0)
from lmtanalysis.Animal import *
from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import *
from lmtanalysis.Measure import *
from matplotlib import patches
from scipy import stats
from scripts.ComputeActivityHabituationNorTest import *
from lmtanalysis.FileUtil import *


if __name__ == '__main__':

    print("Code launched.")
    # set font
    from matplotlib import rc, gridspec

    rc('font', **{'family': 'serif', 'serif': ['Arial']})

    colorSap = {'WT': 'steelblue', 'Del/+': 'darkorange'}

    variableList = ['totDistance', 'centerDistance', 'centerTime', 'nbSap', 'rearTotal Nb', 'rearTotal Duration',
                    'rearCenter Nb', 'rearCenter Duration', 'rearPeriphery Nb', 'rearPeriphery Duration']

    unitDic = {'totDistance': 'cm', 'centerDistance': 'cm', 'centerTime': 's', 'nbSap': 'occurrences', 'rearTotal Nb': 'occurrences', 'rearTotal Duration': 's',
                    'rearCenter Nb': 'occurrences', 'rearCenter Duration': 's', 'rearPeriphery Nb': 'occurrences', 'rearPeriphery Duration': 's'}
    yMinDic = {'totDistance': 4000, 'centerDistance': 0, 'centerTime': 0, 'nbSap': 0,
               'rearTotal Nb': 0, 'rearTotal Duration': 0,
               'rearCenter Nb': 0, 'rearCenter Duration': 0, 'rearPeriphery Nb': 0,
               'rearPeriphery Duration': 0}

    yMaxDic = {'totDistance': 9000, 'centerDistance': 2400, 'centerTime': 450, 'nbSap': 50,
               'rearTotal Nb': 900, 'rearTotal Duration': 150,
               'rearCenter Nb': 200, 'rearCenter Duration': 25, 'rearPeriphery Nb': 600,
               'rearPeriphery Duration': 140}

    while True:
        question = "Do you want to:"
        question += "\n\t [1] plot a figure for the activity in NOR habituation phase and long-term group monitoring?"
        question += "\n"
        answer = input(question)

        if answer == '1':

            sexList = ['male', 'female']
            genoList = ['WT', 'Del/+']

            fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(4 * 4, 4))  # create the figure for the graphs of the computation

            col = 0  # initialise the column number
            #Activity during the openfield test on the first day of habituation of the NOR
            # open the json file
            jsonFileName = "habituationDay1.json"
            with open(jsonFileName) as json_data:
                data = json.load(json_data)
            print("json file re-imported.")

            variableListShort = ['totDistance', 'centerDistance', 'centerTime']
            letter = ['A', 'B', 'C', 'D']
            for val in variableListShort:
                plotVariablesHabituationNorBoxplots(ax=axes[col], sexList=sexList, genoList=genoList, data=data,
                                                    val=val, unitDic=unitDic, yMinDic=yMinDic, yMaxDic=yMaxDic)
                axes[col].text(-1, yMaxDic[val] + 0.05 * (yMaxDic[val] - yMinDic[val]), letter[col], fontsize=20, horizontalalignment='center',
                        color='black', weight='bold')

                col += 1
            axes[0].legend(loc='lower right', fancybox=False, ncol=2).set_visible(True)

            #Activity during the long term group monitoring
            # fix the night:
            n = 'all nights'
            print('Choose the file for the males')
            fileM = getJsonFileToProcess()

            print('Choose the file for the females')
            fileF = getJsonFileToProcess()

            # create a dictionary with profile data
            with open(fileM) as json_data:
                profileDataM = json.load(json_data)

            with open(fileF) as json_data:
                profileDataF = json.load(json_data)

            categoryList = [' TotalLen', ' Nb', ' MeanDur']
            #profile data are merged over the three nights
            behaviouralEventOneMouse = ["Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact",
             "Side by side Contact, opposite way", "Social approach", "Get away", "Approach contact", "Approach rear",
             "Break contact", "FollowZone Isolated", "Train2", "Group2", "Group3", "Group 3 break", "Group 3 make",
             "Group 4 break", "Group 4 make", "Huddling", "Move isolated", "Move in contact", "Nest3_", "Nest4_",
             "Rearing", "Rear isolated", "Rear in contact", "Stop isolated", "WallJump", "Water Zone", "totalDistance",
             "experiment"]

            mergeProfileM = mergeProfileOverNights(profileData=profileDataM, categoryList=categoryList, behaviouralEventOneMouse=behaviouralEventOneMouse)
            mergeProfileF = mergeProfileOverNights(profileData=profileDataF, categoryList=categoryList, behaviouralEventOneMouse=behaviouralEventOneMouse)

            profileDataM = mergeProfileM
            profileDataF = mergeProfileF

            print("json files for profile data re-imported.")

            # plot the data for each behavioural event
            text_file = getFileNameInput()
            behavEvent = 'totalDistance'
            valueCatEvent = ''
            imgPos = (0.5, 17000)
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[col],
                                               row=0, col=col,
                                               letter=letter[col], text_file=text_file, pM=0.025, pF=0.015,
                                               image='img_nose-nose.jpg', imgPos=imgPos)

            # plt.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
            plt.tight_layout()
            plt.show()  # display the plot
            fig.savefig('fig_values_activity.pdf', dpi=200)
            print('Job done.')

            break
