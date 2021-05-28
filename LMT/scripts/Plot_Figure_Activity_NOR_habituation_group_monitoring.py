'''
#Created on 26 January 2021

#@author: Elodie
'''
import mpimg as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

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
import matplotlib.image as mpimg


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
               'rearPeriphery Duration': 0, 'Rear isolated Nb': 0, 'Rear isolated TotalLen': 0, 'Rear isolated MeanDur': 0 }

    yMaxDic = {'totDistance': 9000, 'centerDistance': 2400, 'centerTime': 450, 'nbSap': 50,
               'rearTotal Nb': 900, 'rearTotal Duration': 150,
               'rearCenter Nb': 200, 'rearCenter Duration': 25, 'rearPeriphery Nb': 600,
               'rearPeriphery Duration': 140, 'Rear isolated Nb': 20000, 'Rear isolated TotalLen': 300000, 'Rear isolated MeanDur': 100}

    while True:
        question = "Do you want to:"
        question += "\n\t [1] plot a figure for the activity in NOR habituation phase and long-term group monitoring?"
        question += "\n\t [2] plot a figure for the exploration in NOR habituation phase and long-term group monitoring?"
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
                axes[col].set_xticklabels(['males', 'femelles'], fontsize=14)

                col += 1
            #Add the legend manually
            wtPatch = mpatches.Patch(edgecolor='black', facecolor='steelblue', label='WT')
            delPatch = mpatches.Patch(edgecolor='black', facecolor='darkorange', label='Del/+')
            handles = [wtPatch, delPatch]
            axes[0].legend(handles=handles, loc='lower right').set_visible(True)
            axes[0].set_ylabel('distance totale 15min hab (cm)', fontsize=16)
            axes[0].set_title('openfield 15 min', fontsize=16)
            axes[1].set_ylabel('distance parcourue au centre (cm)', fontsize=16)
            axes[1].set_title('openfield 15 min', fontsize=16)
            axes[2].set_ylabel('temps passe au centre (s)', fontsize=16)
            axes[2].set_title('openfield 15 min', fontsize=16)

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
            imgPos = (0.5, 12000)
            zoom = 0.25
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[col],
                                               letter=letter[col], text_file=text_file,
                                               image='img_moving.jpg', imgPos=imgPos, zoom=zoom)
            axes[col].set_ylabel('distance totale (m)', fontsize=16)
            axes[col].set_title('3 nuits en groupe', fontsize=16)
            axes[col].set_xticklabels(['males', 'femelles'], fontsize=14)

            # plt.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
            plt.tight_layout()
            plt.show()  # display the plot
            fig.savefig('fig_values_activity.pdf', dpi=200)
            print('Job done.')

            break


        if answer == '2':

            sexList = ['male', 'female']
            genoList = ['WT', 'Del/+']

            fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(3 * 4, 8))  # create the figure for the graphs of the computation

            col = 0  # initialise the column number
            row = 0 #initialise the row number
            #Exploration during the openfield test on the first day of habituation of the NOR
            # open the json file
            jsonFileName = "habituationDay1.json"
            with open(jsonFileName) as json_data:
                data = json.load(json_data)
            print("json file re-imported.")

            variableListShort = ['nbSap', 'rearTotal Nb', 'rearTotal Duration']
            letter = ['A', 'B', 'C', 'D', 'E', 'F']
            k = 0
            for val in variableListShort:
                plotVariablesHabituationNorBoxplots(ax=axes[row][col], sexList=sexList, genoList=genoList, data=data,
                                                    val=val, unitDic=unitDic, yMinDic=yMinDic, yMaxDic=yMaxDic)
                axes[row][col].text(-1, yMaxDic[val] + 0.05 * (yMaxDic[val] - yMinDic[val]), letter[k], fontsize=20, horizontalalignment='center',
                        color='black', weight='bold')
                axes[row][col].set_xticklabels(['males', 'femelles'], fontsize=14)

                k += 1

                col += 1

            #add manually the legend on the first plot
            wtPatch = mpatches.Patch(edgecolor='black', facecolor='steelblue', label='WT')
            delPatch = mpatches.Patch(edgecolor='black', facecolor='darkorange', label='Del/+')
            handles = [wtPatch, delPatch]
            axes[0][0].legend(handles=handles, loc=(0.45, 0.6)).set_visible(True)
            axes[0][0].set_ylabel('nombre de SAP', fontsize=16)
            axes[0][0].set_title('openfield 15 min', fontsize=16)
            axes[0][1].set_ylabel('nombre de redressements', fontsize=16)
            axes[0][1].set_title('openfield 15 min', fontsize=16)
            axes[0][2].set_ylabel('duree totale des redressements', fontsize=16)
            axes[0][2].set_title('openfield 15 min', fontsize=16)

            # add scale on the plot
            image = 'img_sap.jpg'
            imgPos = (0.5, 47)
            behavSchema = mpimg.imread(image)
            imgBox = OffsetImage(behavSchema, zoom=0.2)
            imageBox = AnnotationBbox(imgBox, imgPos, frameon=False)
            axes[0][0].add_artist(imageBox)

            # add scale on the plot
            image = 'img_rearing.jpg'
            imgPos = (0.5, 820)
            behavSchema = mpimg.imread(image)
            imgBox = OffsetImage(behavSchema, zoom=0.2)
            imageBox = AnnotationBbox(imgBox, imgPos, frameon=False)
            axes[0][1].add_artist(imageBox)

            # add scale on the plot
            image = 'img_rearing.jpg'
            imgPos = (0.5, 135)
            behavSchema = mpimg.imread(image)
            imgBox = OffsetImage(behavSchema, zoom=0.2)
            imageBox = AnnotationBbox(imgBox, imgPos, frameon=False)
            axes[0][2].add_artist(imageBox)

            row += 1
            col = 0
            #Exploration during the long term group monitoring
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
            behavEvent = 'Rear isolated'
            valueCatEvent = ' Nb'
            imgPos = (0.5, 39000)
            zoom=0.2
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row][col],
                                               letter=letter[k], text_file=text_file,
                                               image='img_rearing.jpg', imgPos=imgPos, zoom=zoom)
            axes[row][col].set_ylabel('nombre de redressements', fontsize=16)
            axes[row][col].set_title('3 nuits en groupe', fontsize=16)
            axes[row][col].set_xticklabels(['males', 'femelles'], fontsize=14)

            k += 1
            col += 1

            # plot the data for each behavioural event
            behavEvent = 'Rear isolated'
            valueCatEvent = ' TotalLen'
            imgPos = (0.5, 7000)
            zoom=0.2
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row][col],
                                               letter=letter[k], text_file=text_file,
                                               image='img_rearing.jpg', imgPos=imgPos, zoom=zoom)
            axes[row][col].set_ylabel('duree totale des redressements', fontsize=16)
            axes[row][col].set_title('3 nuits en groupe', fontsize=16)
            axes[row][col].set_xticklabels(['males', 'femelles'], fontsize=14)

            k += 1
            col += 1

            # plot the data for each behavioural event
            behavEvent = 'Rear isolated'
            valueCatEvent = ' MeanDur'
            imgPos = (0.5, 7.7)
            zoom=0.2
            singlePlotPerEventProfileBothSexes(profileDataM=profileDataM, profileDataF=profileDataF, night=n,
                                               valueCat=valueCatEvent, behavEvent=behavEvent, ax=axes[row][col],
                                               letter=letter[k], text_file=text_file,
                                               image='img_rearing.jpg', imgPos=imgPos, zoom=zoom)
            axes[row][col].set_ylabel('duree moyenne des redressements', fontsize=16)
            axes[row][col].set_xticklabels(['males', 'femelles'], fontsize=14)
            axes[row][col].set_title('3 nuits en groupe', fontsize=16)


            # plt.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
            plt.tight_layout()
            plt.show()  # display the plot
            fig.savefig('fig_values_exploration.pdf', dpi=200)
            print('Job done.')

            break
