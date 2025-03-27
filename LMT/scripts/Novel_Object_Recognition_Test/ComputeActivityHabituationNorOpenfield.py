'''
#Created on 22 September 2021

#@author: Elodie
'''
import numpy as np; np.random.seed(0)
from lmtanalysis.FileUtil import *

from scripts.Novel_Object_Recognition_Test.ConfigurationNOR import *
# from scripts.Novel_Object_Recognition_Test.ComputeActivityHabituationNorTestRedCage import buildFigTrajectoryPerSetup,\
#     plotVariablesHabituationNorBoxplotsPerSetup, plotVariablesHabituationNorBoxplotsPerGenotype, \
#     getCumulDistancePerTimeBinRedCage, plotDistancePerBinRedCage
import matplotlib.pyplot as plt
import sqlite3
from experimental.Animal_LMTtoolkit import AnimalPoolToolkit
from scripts.Novel_Object_Recognition_Test.ComputeActivityHabituationNorTest import plotTrajectorySingleAnimal
from scripts.Rebuild_All_Events import processAll
from lmtanalysis.Event import EventTimeLine
import json

def buildFigTrajectoryPerGenotype(files, tmin, tmax, figName, title, xa = 111, xb = 400, ya = 63, yb = 353):

    fig, axes = plt.subplots(nrows=6, ncols=5, figsize=(14, 18))  # building the plot for trajectories
    nRow = 0  # initialisation of the row
    nCol = 0  # initialisation of the column

    tminHab = tmin  # start time of the computation
    tmaxHab = tmax  # end time of the computation

    for file in files:
        connection = sqlite3.connect(file)  # connection to the database

        pool = AnimalPoolToolkit()
        pool.loadAnimals(connection)  # upload all the animals from the database
        animal = pool.animalDictionary[1]

        # set the axes. Check the number of file to get the dimension of axes and grab the correct ones.
        ax = axes[nRow][nCol]  # set the subplot where to draw the plot
        plotTrajectorySingleAnimal(file, color='black', colorTitle=getColorGeno(animal.genotype), ax=ax, tmin=tminHab,
                                   tmax=tmaxHab, title=title+' '+animal.setup, xa = 111, xb = 400, ya = 63, yb = 353)  # function to draw the trajectory

        if nCol < 5:
            nCol += 1
        if nCol >= 5:
            nCol = 0
            nRow += 1

        connection.close()

    fig.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
    # plt.show() #display the plot
    fig.savefig('{}.pdf'.format(figName), dpi=200)
    fig.savefig('{}.jpg'.format(figName), dpi=200)




if __name__ == '__main__':

    print("Code launched.")
    # set font
    from matplotlib import rc

    rc('font', **{'family': 'serif', 'serif': ['Arial']})

    colorSapPerSetup = {'1': 'steelblue', '2': 'darkorange'}

    variableList = ['totDistance', 'distancePerBin', 'centerDistance', 'centerTime', 'nbSap', 'rearTotal Nb', 'rearTotal Duration',
                    'rearCenter Nb', 'rearCenter Duration', 'rearPeriphery Nb', 'rearPeriphery Duration']

    unitDic = {'totDistance': 'cm', 'centerDistance': 'cm', 'centerTime': 's', 'nbSap': 'occurrences', 'rearTotal Nb': 'occurrences', 'rearTotal Duration': 's',
                    'rearCenter Nb': 'occurrences', 'rearCenter Duration': 's', 'rearPeriphery Nb': 'occurrences', 'rearPeriphery Duration': 's'}

    yMinDic = {'totDistance': 2000, 'centerDistance': 0, 'centerTime': 0, 'nbSap': 0,
               'rearTotal Nb': 0, 'rearTotal Duration': 0,
               'rearCenter Nb': 0, 'rearCenter Duration': 0, 'rearPeriphery Nb': 0,
               'rearPeriphery Duration': 0}

    yMaxDic = {'totDistance': 20000, 'centerDistance': 4000, 'centerTime': 250, 'nbSap': 16,
               'rearTotal Nb': 2200, 'rearTotal Duration': 500,
               'rearCenter Nb': 400, 'rearCenter Duration': 50, 'rearPeriphery Nb': 2000,
               'rearPeriphery Duration': 250}

    while True:
        question = "Do you want to:"
        question += "\n\t [1] rebuild all events?"
        question += "\n\t [2] compute and plot trajectories in the habituation phase per setup?"
        question += "\n\t [2b] compute and plot trajectories in the habituation phase per genotype?"
        question += "\n\t [3] plot the distance and anxiety measures in the habituation phase?"
        question += "\n\t [3b] plot the distance and anxiety measures in the habituation phase per genotype?"
        question += "\n\t [4] plot the distance per one minute time bin in the habituation phase?"
        question += "\n"
        answer = input(question)

        if answer == '1':
            print("Rebuilding all events.")
            processAll()

            break

        if answer == '2':
            print('Plot trajectory in the habituation phase')
            #distance travelled
            #space use
            #traj of center of mass
            files = getFilesToProcess() #upload files for the analysis
            #plot the trajectories, with SAP only in the inner zone of the cage to avoid SAP against the walls
            buildFigTrajectoryPerSetup(files=files, tmin=0, tmax=15*oneMinute, figName='fig_traj_hab_nor_setup', title='hab d1', xa=128, xb=383, ya=80, yb=336)

            print('Compute distance travelled, number of SAP displayed, and rearing.')

            data = {}
            for val in variableList:
                data[val] = {}
                for sex in ['male', 'female']:
                    data[val][sex] = {}
                    for setup in ['1', '2']:
                        data[val][sex][setup] = {}
            tminHab = 0
            tmaxHab = 15*oneMinute

            for file in files:
                connection = sqlite3.connect(file)

                pool = AnimalPoolToolkit()
                pool.loadAnimals(connection)
                animal = pool.animalDictionary[1]
                animal.loadDetection( tminHab, tmaxHab )
                sex = animal.sex
                geno = animal.genotype
                rfid = animal.RFID
                setup = animal.setup

                dt1 = animal.getDistance(tmin = tminHab, tmax = tmaxHab) #compute the total distance traveled in the whole cage
                #get distance per time bin
                dBin = animal.getDistancePerBin(binFrameSize=1*oneMinute , minFrame=tminHab, maxFrame=tmaxHab)
                #get distance and time spent in the middle of the cage
                #coordinates of the whole cage: xa = 111, xb = 400, ya = 63, yb = 353
                #center zone: xa = 168, xb = 343, ya = -296, yb = -120
                #d1 = animal.getDistanceSpecZone(tminHab, tmaxHab, xa=191, xb=320, ya=143, yb=273) #compute the distance traveled in the center zone
                #t1 = animal.getCountFramesSpecZone(tminHab, tmaxHab, xa=191, xb=320, ya=143, yb=273) #compute the time spent in the center zone
                d1 = animal.getDistanceSpecZone(tminHab, tmaxHab, xa = 168, xb = 343, ya = 120, yb = 296)  # compute the distance traveled in the center zone
                t1 = animal.getCountFramesSpecZone(tminHab, tmaxHab, xa = 168, xb = 343, ya = 120, yb = 296)  # compute the time spent in the center zone

                '''#get the number of frames in sap in whole cage
                sap1 = len(animal.getSap(tmin=tminHab, tmax=tmaxHab, xa = 111, xb = 400, ya = 63, yb = 353))'''
                # get the number of frames in sap in whole cage but without counting the border (3 cm) to filter out SAPs against the wall
                sap1 = len(animal.getSap(tmin=tminHab, tmax=tmaxHab, xa=128, xb=383, ya=80, yb=336))
                #fill the data dictionary with the computed data for each file:
                data['totDistance'][sex][setup][rfid] = dt1
                data['distancePerBin'][sex][setup][rfid] = dBin
                data['centerDistance'][sex][setup][rfid] = d1
                data['centerTime'][sex][setup][rfid] = t1 / 30
                data['nbSap'][sex][setup][rfid] = sap1 / 30

                #get the number and time of rearing
                rearTotalTimeLine = EventTimeLine( connection, "Rear isolated", minFrame = tminHab, maxFrame = tmaxHab, loadEventIndependently = True )
                rearCenterTimeLine = EventTimeLine(connection, "Rear in center", minFrame=tminHab, maxFrame=tmaxHab, loadEventIndependently=True)
                rearPeripheryTimeLine = EventTimeLine(connection, "Rear at periphery", minFrame=tminHab, maxFrame=tmaxHab, loadEventIndependently=True)

                data['rearTotal Nb'][sex][setup][rfid] = rearTotalTimeLine.getNbEvent()
                data['rearTotal Duration'][sex][setup][rfid] = rearTotalTimeLine.getTotalLength() / 30
                data['rearCenter Nb'][sex][setup][rfid] = rearCenterTimeLine.getNbEvent()
                data['rearCenter Duration'][sex][setup][rfid] = rearCenterTimeLine.getTotalLength() / 30
                data['rearPeriphery Nb'][sex][setup][rfid] = rearPeripheryTimeLine.getNbEvent()
                data['rearPeriphery Duration'][sex][setup][rfid] = rearPeripheryTimeLine.getTotalLength() / 30

                connection.close()
            print(data)
            #store the data dictionary in a json file
            with open('hab_males.json', 'w') as jFile:
                json.dump(data, jFile, indent=4)
            print("json file created")

            break
        
        
        if answer == '2b':
            print('Plot trajectory in the habituation phase per genotype')
            #distance travelled
            #space use
            #traj of center of mass
            files = getFilesToProcess() #upload files for the analysis
            #plot the trajectories, with SAP only in the inner zone of the cage to avoid SAP against the walls
            #buildFigTrajectoryPerGenotype(files=files, tmin=0, tmax=15*oneMinute, figName='fig_traj_hab_nor_setup', title='hab d1', xa=128, xb=383, ya=80, yb=336)

            print('Compute distance travelled, number of SAP displayed, and rearing.')

            data = {}
            for val in variableList:
                data[val] = {}
                for sex in ['M', 'F']:
                    data[val][sex] = {}
                    for geno in genoList:
                        data[val][sex][geno] = {}
            tminHab = 0
            tmaxHab = 15*oneMinute

            for file in files:
                connection = sqlite3.connect(file)

                pool = AnimalPoolToolkit()
                pool.loadAnimals(connection)
                animal = pool.animalDictionary[1]
                animal.loadDetection( tminHab, tmaxHab )
                sex = animal.sex
                geno = animal.genotype
                rfid = animal.RFID
                setup = animal.setup

                dt1 = animal.getDistance(tmin = tminHab, tmax = tmaxHab) #compute the total distance traveled in the whole cage
                #get distance per time bin
                dBin = animal.getDistancePerBin(binFrameSize=1*oneMinute , minFrame=tminHab, maxFrame=tmaxHab)
                #get distance and time spent in the middle of the cage
                #coordinates of the whole cage: xa = 111, xb = 400, ya = 63, yb = 353
                #center zone: xa = 168, xb = 343, ya = -296, yb = -120
                #d1 = animal.getDistanceSpecZone(tminHab, tmaxHab, xa=191, xb=320, ya=143, yb=273) #compute the distance traveled in the center zone
                #t1 = animal.getCountFramesSpecZone(tminHab, tmaxHab, xa=191, xb=320, ya=143, yb=273) #compute the time spent in the center zone
                d1 = animal.getDistanceSpecZone(tminHab, tmaxHab, xa = 168, xb = 343, ya = 120, yb = 296)  # compute the distance traveled in the center zone
                t1 = animal.getCountFramesSpecZone(tminHab, tmaxHab, xa = 168, xb = 343, ya = 120, yb = 296)  # compute the time spent in the center zone

                '''#get the number of frames in sap in whole cage
                sap1 = len(animal.getSap(tmin=tminHab, tmax=tmaxHab, xa = 111, xb = 400, ya = 63, yb = 353))'''
                # get the number of frames in sap in whole cage but without counting the border (3 cm) to filter out SAPs against the wall
                sap1 = len(animal.getSap(tmin=tminHab, tmax=tmaxHab, xa=128, xb=383, ya=80, yb=336))
                #fill the data dictionary with the computed data for each file:
                data['totDistance'][sex][geno][rfid] = dt1
                data['distancePerBin'][sex][geno][rfid] = dBin
                data['centerDistance'][sex][geno][rfid] = d1
                data['centerTime'][sex][geno][rfid] = t1 / 30
                data['nbSap'][sex][geno][rfid] = sap1 / 30

                #get the number and time of rearing
                rearTotalTimeLine = EventTimeLine( connection, "Rear isolated", minFrame = tminHab, maxFrame = tmaxHab, loadEventIndependently = True )
                rearCenterTimeLine = EventTimeLine(connection, "Rear in center", minFrame=tminHab, maxFrame=tmaxHab, loadEventIndependently=True)
                rearPeripheryTimeLine = EventTimeLine(connection, "Rear at periphery", minFrame=tminHab, maxFrame=tmaxHab, loadEventIndependently=True)

                data['rearTotal Nb'][sex][geno][rfid] = rearTotalTimeLine.getNbEvent()
                data['rearTotal Duration'][sex][geno][rfid] = rearTotalTimeLine.getTotalLength() / 30
                data['rearCenter Nb'][sex][geno][rfid] = rearCenterTimeLine.getNbEvent()
                data['rearCenter Duration'][sex][geno][rfid] = rearCenterTimeLine.getTotalLength() / 30
                data['rearPeriphery Nb'][sex][geno][rfid] = rearPeripheryTimeLine.getNbEvent()
                data['rearPeriphery Duration'][sex][geno][rfid] = rearPeripheryTimeLine.getTotalLength() / 30

                connection.close()
            print(data)
            #store the data dictionary in a json file
            with open('hab_males.json', 'w') as jFile:
                json.dump(data, jFile, indent=4)
            print("json file created")

            break

        
        if answer == '3':

            # open the json file
            jsonFileName = getJsonFileToProcess()
            with open(jsonFileName) as json_data:
                data = json.load(json_data)
            print("json file re-imported.")

            sexList = ['male', 'female']
            setupList = ['1', '2']
            variableList = ['totDistance', 'centerDistance', 'centerTime', 'nbSap', 'rearTotal Nb',
                            'rearTotal Duration',
                            'rearCenter Nb', 'rearCenter Duration', 'rearPeriphery Nb', 'rearPeriphery Duration']
            #variableList = ['rearTotal Nb', 'rearCenter Nb', 'rearPeriphery Nb']
            #variableList = ['totDistance', 'centerDistance', 'centerTime']

            fig, axes = plt.subplots(nrows=1, ncols=len(variableList), figsize=(2*len(variableList), 4)) #create the figure for the graphs of the computation

            col = 0 #initialise the column number

            for val in variableList:
                plotVariablesHabituationNorBoxplotsPerSetup(ax=axes[col], sexList=sexList, setupList=setupList, data=data, val=val, unitDic=unitDic, yMinDic=yMinDic, yMaxDic=yMaxDic)

                col += 1

            #plt.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
            plt.tight_layout()
            plt.show()  # display the plot
            fig.savefig('fig_values_hab_nor.pdf', dpi=200)
            fig.savefig('fig_values_hab_nor.jpg', dpi=200)
            print('Job done.')
            break
        
        
        if answer == '3b':

            # open the json file
            jsonFileName = getJsonFileToProcess()
            with open(jsonFileName) as json_data:
                data = json.load(json_data)
            print("json file re-imported.")

            variableList = ['totDistance', 'centerDistance', 'centerTime', 'nbSap', 'rearTotal Nb',
                            'rearTotal Duration',
                            'rearCenter Nb', 'rearCenter Duration', 'rearPeriphery Nb', 'rearPeriphery Duration']
            #variableList = ['rearTotal Nb', 'rearCenter Nb', 'rearPeriphery Nb']
            #variableList = ['totDistance', 'centerDistance', 'centerTime']
            variableList = ['totDistance', 'centerDistance', 'centerTime', 'nbSap', 'rearTotal Nb',
                            'rearTotal Duration']

            fig, axes = plt.subplots(nrows=1, ncols=len(variableList), figsize=(2*len(variableList), 4)) #create the figure for the graphs of the computation

            col = 0 #initialise the column number

            for val in variableList:
                plotVariablesHabituationNorBoxplotsPerGenotype(ax=axes[col], sexList=sexList, genoList=genoList, data=data, val=val, unitDic=unitDic, yMinDic=yMinDic, yMaxDic=yMaxDic)

                col += 1

            #plt.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
            plt.tight_layout()
            plt.show()  # display the plot
            fig.savefig('fig_values_hab_nor.pdf', dpi=200)
            fig.savefig('fig_values_hab_nor.png', dpi=200)
            print('Job done.')
            break


        if answer == '4':
            #plot the distance travelled per time bin in the habituation
            sexList = ['male', 'female']
            setupList = ['1', '2']
            variableList = ['distancePerBin']
            val = variableList[0]
            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=( 5 * 2, 4))  # create the figure for the graphs of the computation

            col = 0  # initialise the column number
            # open the json files
            print('Choose json file for habituation day 1')
            jsonFileName1 = getJsonFileToProcess()
            with open(jsonFileName1) as json_data:
                data1 = json.load(json_data)
            print('Choose json file for habituation day 2')
            jsonFileName2 = getJsonFileToProcess()
            with open(jsonFileName2) as json_data:
                data2 = json.load(json_data)
            print("json files re-imported.")

            ax = axes[col]
            resultDic1 = getCumulDistancePerTimeBinRedCage(data=data1, eventList=variableList)
            plotDistancePerBinRedCage(ax=ax, title='day 1', event=val, resultDic=resultDic1, timeBin=1 * oneMinute)

            col += 1
            ax = axes[col]
            resultDic2 = getCumulDistancePerTimeBinRedCage(data=data2, eventList=variableList)
            plotDistancePerBinRedCage(ax=ax, title='day 2', event=val, resultDic=resultDic2, timeBin=1 * oneMinute)

            #plt.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
            plt.tight_layout()
            plt.show()  # display the plot
            fig.savefig('fig_hab_nor_cumul_distance.pdf', dpi=200)
            fig.savefig('fig_hab_nor_cumul_distance.jpg', dpi=200)
            print('Job done.')
            break

