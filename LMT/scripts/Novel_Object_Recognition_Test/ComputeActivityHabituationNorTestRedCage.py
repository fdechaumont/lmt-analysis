'''
#Created on 26 January 2021

#@author: Elodie
'''

from scripts.Novel_Object_Recognition_Test.ConfigurationNOR import getColorSetup,\
    getColorGeno

import numpy as np; np.random.seed(0)
from lmtanalysis.Animal import *
from lmtanalysis.Util import *
from lmtanalysis.FileUtil import *
from lmtanalysis.Measure import *
from ConfigurationNOR import *
from scipy import stats
import seaborn as sns
from scripts.Rebuild_All_Events import processAll
import json
from ComputeActivityHabituationNorOpenfield import buildFigTrajectoryPerGenotype
from ComputeActivityHabituationNorTest import plotTrajectorySingleAnimal


def buildFigTrajectoryPerSetup(files, tmin, tmax, figName, title, xa = 111, xb = 400, ya = 63, yb = 353):

    fig, axes = plt.subplots(nrows=6, ncols=5, figsize=(14, 18))  # building the plot for trajectories
    nRow = 0  # initialisation of the row
    nCol = 0  # initialisation of the column

    tminHab = tmin  # start time of the computation
    tmaxHab = tmax  # end time of the computation

    for file in files:
        connection = sqlite3.connect(file)  # connection to the database

        pool = AnimalPool()
        pool.loadAnimals(connection)  # upload all the animals from the database
        animal = pool.animalDictionary[1]

        # set the axes. Check the number of file to get the dimension of axes and grab the correct ones.
        ax = axes[nRow][nCol]  # set the subplot where to draw the plot
        plotTrajectorySingleAnimal(file, color='black', colorTitle=getColorSetup(animal.setup), ax=ax, tmin=tminHab,
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
    

def buildFigTrajectoryPerStrain(files, tmin, tmax, figName, title, xa = 111, xb = 400, ya = 63, yb = 353):

    fig, axes = plt.subplots(nrows=6, ncols=5, figsize=(14, 18))  # building the plot for trajectories
    nRow = 0  # initialisation of the row
    nCol = 0  # initialisation of the column

    tminHab = tmin  # start time of the computation
    tmaxHab = tmax  # end time of the computation

    for file in files:
        connection = sqlite3.connect(file)  # connection to the database

        pool = AnimalPool()
        pool.loadAnimals(connection)  # upload all the animals from the database
        animal = pool.animalDictionary[1]

        # set the axes. Check the number of file to get the dimension of axes and grab the correct ones.
        ax = axes[nRow][nCol]  # set the subplot where to draw the plot
        plotTrajectorySingleAnimal(file, color='black', colorTitle=getColorStrain(animal.strain), ax=ax, tmin=tminHab,
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



def plotVariablesHabituationNorBoxplotsPerSetup(ax, sexList, setupList, data, val, unitDic, yMinDic, yMaxDic ):
    # reformate the data dictionary to get the correct format of data for plotting and statistical analyses
    dataVal = {}
    for sex in sexList:
        dataVal[sex] = {}
        for setup in setupList:
            dataVal[sex][setup] = []
            for rfid in data[val][sex][setup].keys():
                dataVal[sex][setup].append(data[val][sex][setup][rfid])

    dic = {'setup' : [], 'sex' : [], 'val': [], 'variable': []}
    for sex in sexList:
        for setup in setupList:
            dic['variable'].extend( [val] * len(dataVal[sex][setup]) )
            dic['val'].extend(dataVal[sex][setup])
            dic['sex'].extend( [sex] * len(dataVal[sex][setup]) )
            dic['setup'].extend( [setup] * len(dataVal[sex][setup]) )

    df = pd.DataFrame.from_dict(dic)
    print(df)

    bp = sns.boxplot(data=df, x='sex', y='val', hue='setup', hue_order=setupList, ax=ax, linewidth=0.5, showmeans=True,
                     meanprops={"marker": 'o',
                                "markerfacecolor": 'white',
                                "markeredgecolor": 'black',
                                "markersize": '8'}, showfliers=False, width=0.8, dodge=True)

    # Add transparency to colors
    k = 0
    for patch in bp.artists:
        patch.set_facecolor(getColorSetup(setupList[k]))
        k += 1

    sns.stripplot(data=df, x='sex', y='val', hue='setup', hue_order=setupList, jitter=True, color='black', s=5,
                  dodge=True, ax=ax)
    #ax.set_title(val, fontsize=14)
    ax.xaxis.set_tick_params(direction="in")
    ax.tick_params(axis='x', labelsize=14)
    ax.yaxis.set_tick_params(direction="in")
    ax.tick_params(axis='y', labelsize=12)
    ylabel = '{} ({})'.format(val, unitDic[val])
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_xlabel('', fontsize=14)
    ax.set_ylim(yMinDic[val], yMaxDic[val])
    ax.legend().set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # conduct statistical testing: Mann-Whitney U test (non-parametric for non normal data with small sample size):
    xPos = {'male': 0, 'female': 0}
    for sex in sexList:
        try:
            U, p = stats.mannwhitneyu(list(df['val'][(df['sex']==sex) & (df['setup']=='1')]), list(df['val'][(df['sex']==sex) & (df['setup']=='2')]))
            print('Mann-Whitney U-test for {} in {}: U={}, p={}'.format(val, sex, U, p))
            if p != 0:
                ax.text(xPos[sex], yMaxDic[val] - 0.1 * (yMaxDic[val]-yMinDic[val]),
                        getStarsFromPvalues(pvalue=p, numberOfTests=1), horizontalalignment='center', fontsize=20, weight='bold')
        except:
            print('stats problem!')
            continue
        
def plotVariablesHabituationNorBoxplotsPerStrain(ax, sexList, strainList, data, val, unitDic, yMinDic, yMaxDic ):
    # reformate the data dictionary to get the correct format of data for plotting and statistical analyses
    dataVal = {}
    for sex in sexList:
        dataVal[sex] = {}
        for strain in strainList:
            dataVal[sex][strain] = []
            for rfid in data[val][sex][strain].keys():
                dataVal[sex][strain].append(data[val][sex][strain][rfid])

    dic = {'strain' : [], 'sex' : [], 'val': [], 'variable': []}
    for sex in sexList:
        for strain in strainList:
            dic['variable'].extend( [val] * len(dataVal[sex][strain]) )
            dic['val'].extend(dataVal[sex][strain])
            dic['sex'].extend( [sex] * len(dataVal[sex][strain]) )
            dic['strain'].extend( [strain] * len(dataVal[sex][strain]) )

    df = pd.DataFrame.from_dict(dic)
    print(df)

    bp = sns.boxplot(data=df, x='sex', y='val', hue='strain', hue_order=strainList, ax=ax, linewidth=0.5, showmeans=True,
                     meanprops={"marker": 'o',
                                "markerfacecolor": 'white',
                                "markeredgecolor": 'black',
                                "markersize": '8'}, showfliers=False, width=0.8, dodge=True)

    # Add transparency to colors
    k = 0
    for patch in bp.artists:
        patch.set_facecolor(getColorStrain(strainList[k]))
        k += 1

    sns.stripplot(data=df, x='sex', y='val', hue='strain', hue_order=strainList, jitter=True, color='black', s=5,
                  dodge=True, ax=ax)
    #ax.set_title(val, fontsize=14)
    ax.xaxis.set_tick_params(direction="in")
    ax.tick_params(axis='x', labelsize=14)
    ax.yaxis.set_tick_params(direction="in")
    ax.tick_params(axis='y', labelsize=12)
    ylabel = '{} ({})'.format(val, unitDic[val])
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_xlabel('', fontsize=14)
    ax.set_ylim(yMinDic[val], yMaxDic[val])
    ax.legend().set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # conduct statistical testing: Mann-Whitney U test (non-parametric for non normal data with small sample size):
    xPos = {'male': 0, 'female': 0}
    for sex in sexList:
        try:
            U, p = stats.mannwhitneyu(list(df['val'][(df['sex']==sex) & (df['strain']==strainList[0])]), list(df['val'][(df['sex']==sex) & (df['strain']==strainList[1])]))
            print('Mann-Whitney U-test for {} in {}: U={}, p={}'.format(val, sex, U, p))
            if p != 0:
                ax.text(xPos[sex], yMaxDic[val] - 0.1 * (yMaxDic[val]-yMinDic[val]),
                        getStarsFromPvalues(pvalue=p, numberOfTests=1), horizontalalignment='center', fontsize=20, weight='bold')
        except:
            print('stats problem!')
            continue
        
def plotVariablesHabituationNorBoxplotsPerGenotype(ax, sexList, genoList, data, val, unitDic, yMinDic, yMaxDic ):
    # reformate the data dictionary to get the correct format of data for plotting and statistical analyses
    dataVal = {}
    for sex in sexList:
        dataVal[sex] = {}
        for geno in genoList:
            dataVal[sex][geno] = []
            for rfid in data[val][sex][geno].keys():
                dataVal[sex][geno].append(data[val][sex][geno][rfid])

    dic = {'geno' : [], 'sex' : [], 'val': [], 'variable': []}
    for sex in sexList:
        for geno in genoList:
            dic['variable'].extend( [val] * len(dataVal[sex][geno]) )
            dic['val'].extend(dataVal[sex][geno])
            dic['sex'].extend( [sex] * len(dataVal[sex][geno]) )
            dic['geno'].extend( [geno] * len(dataVal[sex][geno]) )

    df = pd.DataFrame.from_dict(dic)
    print(df)

    bp = sns.boxplot(data=df, x='sex', y='val', hue='geno', hue_order=genoList, ax=ax, linewidth=0.5, showmeans=True,
                     meanprops={"marker": 'o',
                                "markerfacecolor": 'white',
                                "markeredgecolor": 'black',
                                "markersize": '8'}, showfliers=False, width=0.8, dodge=True)

    # Add transparency to colors
    k = 0
    for patch in bp.artists:
        patch.set_facecolor(getColorGeno(genoList[k]))
        k += 1

    sns.stripplot(data=df, x='sex', y='val', hue='geno', hue_order=genoList, jitter=True, color='black', s=5,
                  dodge=True, ax=ax)
    #ax.set_title(val, fontsize=14)
    ax.xaxis.set_tick_params(direction="in")
    ax.tick_params(axis='x', labelsize=14)
    ax.yaxis.set_tick_params(direction="in")
    ax.tick_params(axis='y', labelsize=12)
    ylabel = '{} ({})'.format(val, unitDic[val])
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_xlabel('', fontsize=14)
    ax.set_ylim(yMinDic[val], yMaxDic[val])
    ax.legend().set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # conduct statistical testing: Mann-Whitney U test (non-parametric for non normal data with small sample size):
    xPos = {'male': 0, 'female': 1}
    for sex in sexList:
        try:
            U, p = stats.mannwhitneyu(list(df['val'][(df['sex']==sex) & (df['geno']==genoList[0])]), list(df['val'][(df['sex']==sex) & (df['geno']==genoList[1])]))
            print('Mann-Whitney U-test for {} in {}: U={}, p={}'.format(val, sex, U, p))
            if p != 0:
                ax.text(xPos[sex], yMaxDic[val] - 0.1 * (yMaxDic[val]-yMinDic[val]),
                        getStarsFromPvalues(pvalue=p, numberOfTests=1), horizontalalignment='center', fontsize=20, weight='bold')
        except:
            print('stats problem!')
            continue


def getCumulDistancePerTimeBinRedCage(data, eventList):
    K = [i for i in range(15)]
    resultDic = {}
    for event in eventList:
        resultDic[event] = {}
        for setup in ['1', '2']:
            resultDic[event][setup] = {}
            for k in K:
                resultDic[event][setup][k] = []

    for event in eventList:
        for setup in ['1', '2']:
            for k in K:
                for rfid in data[event]['female'][setup].keys():
                    resultDic[event][setup][k].append(data[event]['female'][setup][rfid][k])

    return resultDic

def plotDistancePerBinRedCage(ax, title, event, resultDic, timeBin):
    K = [i for i in range(15)]

    yMean = {event: {}}
    yError = {event: {}}

    for setup in ['1', '2']:
        yMean[event][setup] = []
        yError[event][setup] = []
        for k in K:
            yMean[event][setup].append(np.mean(resultDic[event][setup][k]))
            yError[event][setup].append(np.std(resultDic[event][setup][k]))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    xIndex = K
    ax.set_xticks(xIndex)
    ax.set_xticklabels(K, rotation=0, fontsize=12, horizontalalignment='right')
    ax.set_ylabel('distance (cm) (mean+-sd)', fontsize=15)
    ax.set_xlabel('time bins of {} min'.format(timeBin / oneMinute), fontsize=15)
    ax.legend().set_visible(False)
    ax.xaxis.set_tick_params(direction="in")
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 1500)
    ax.tick_params(axis='y', labelsize=14)
    ax.set_title('{} {}'.format(title, event), fontsize=16)

    xList = {'1': [i + 0.3 for i in K], '2': [i + 0.6 for i in K]}
    starPos = [i + 0.45 for i in K]

    for setup in ['1', '2']:
        ax.errorbar(x=xList[setup], y=yMean[event][setup], yerr=yError[event][setup], fmt='o',
                    ecolor=getColorSetup(setup), markerfacecolor=getColorSetup(setup),
                    markeredgecolor=getColorSetup(setup))

    for k in K:
        print('setup1: ', resultDic[event]['1'][k])
        print('setup2: ', resultDic[event]['2'][k])
        W, p = stats.mannwhitneyu(resultDic[event]['1'][k], resultDic[event]['2'][k])
        ax.text(x=starPos[k], y=1.05, s=getStarsFromPvalues(p, 1), ha='center')


def getCumulDistancePerTimeBinPerStrain(data, tmin, tmax, timeBin, eventList, sexList, strainList):
    nbIntervals = (tmax-tmin) / timeBin
    K = [i for i in range(int(nbIntervals))]
    resultDic = {}
    for event in eventList:
        resultDic[event] = {}
        for sex in sexList:
            resultDic[event][sex] = {}
            for strain in strainList:
                resultDic[event][sex][strain] = {}
                for k in K:
                    resultDic[event][sex][strain][k] = []

    for event in eventList:
        for sex in sexList:
            for strain in strainList:
                for k in K:
                    for rfid in data[event][sex][strain].keys():
                        resultDic[event][sex][strain][k].append(data[event][sex][strain][rfid][k])

    return resultDic


def plotDistancePerBinPerStrain(ax, tmin, tmax, timeBin, sex, title, event, resultDic, strainList):
    nbIntervals = (tmax-tmin) / timeBin
    K = [i for i in range(int(nbIntervals))]
    
    yMean = {event: {}}
    yError = {event: {}}

    for strain in strainList:
        yMean[event][strain] = []
        yError[event][strain] = []
        for k in K:
            yMean[event][strain].append(np.mean(resultDic[event][sex][strain][k]))
            yError[event][strain].append(np.std(resultDic[event][sex][strain][k]))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    xIndex = K
    ax.set_xticks(xIndex)
    ax.set_xticklabels(K, rotation=0, fontsize=12, horizontalalignment='right')
    ax.set_ylabel('distance (cm) (mean+-sd)', fontsize=15)
    ax.set_xlabel('time bins of {} min'.format(timeBin / oneMinute), fontsize=15)
    ax.legend().set_visible(False)
    ax.xaxis.set_tick_params(direction="in")
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 1500)
    ax.tick_params(axis='y', labelsize=14)
    ax.set_title('{} {}'.format(title, event), fontsize=16)

    xList = {strainList[0]: [i + 0.3 for i in K], strainList[1]: [i + 0.6 for i in K]}
    starPos = [i + 0.45 for i in K]

    for strain in strainList:
        ax.errorbar(x=xList[strain], y=yMean[event][strain], yerr=yError[event][strain], fmt='o',
                    ecolor=getColorStrain(strain), markerfacecolor=getColorStrain(strain),
                    markeredgecolor=getColorStrain(strain))

    for k in K:
        print(strainList[0])
        print(resultDic[event][sex][strainList[0]][k])
        print(strainList[1])
        print(resultDic[event][sex][strainList[1]][k])
        W, p = stats.mannwhitneyu(resultDic[event][sex][strainList[0]][k], resultDic[event][sex][strainList[1]][k])
        ax.text(x=starPos[k], y=1.05, s=getStarsFromPvalues(p, 1), ha='center')


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

    yMinDic = {'totDistance': 6000, 'centerDistance': 0, 'centerTime': 0, 'nbSap': 0,
               'rearTotal Nb': 0, 'rearTotal Duration': 0,
               'rearCenter Nb': 0, 'rearCenter Duration': 0, 'rearPeriphery Nb': 0,
               'rearPeriphery Duration': 0}

    yMaxDic = {'totDistance': 20000, 'centerDistance': 5000, 'centerTime': 300, 'nbSap': 8,
               'rearTotal Nb': 2000, 'rearTotal Duration': 400,
               'rearCenter Nb': 400, 'rearCenter Duration': 50, 'rearPeriphery Nb': 2000,
               'rearPeriphery Duration': 250}

    while True:
        question = "Do you want to:"
        question += "\n\t [1] rebuild all events?"
        question += "\n\t [2] plot trajectories in the habituation phase per setup?"
        question += "\n\t [3] plot the distance and anxiety measures in the habituation phase?"
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

                pool = AnimalPool()
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
            with open('habituationDay1.json', 'w') as jFile:
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
            buildFigTrajectoryPerGenotype(files=files, tmin=0, tmax=15*oneMinute, figName='fig_traj_hab_nor_geno', title='hab d1', xa=128, xb=383, ya=80, yb=336)

            print('Compute distance travelled, number of SAP displayed, and rearing.')

            data = {}
            for val in variableList:
                data[val] = {}
                for sex in ['male', 'female']:
                    data[val][sex] = {}
                    for geno in genoList:
                        data[val][sex][geno] = {}
            tminHab = 0
            tmaxHab = 15*oneMinute

            for file in files:
                connection = sqlite3.connect(file)

                pool = AnimalPool()
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
            with open('habituationDay1.json', 'w') as jFile:
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

