'''
#Created on 22 September 2021

#@author: Elodie
'''
import numpy as np; np.random.seed(0)
from scripts.Novel_Object_Recognition_Test.ConfigurationNOR import *


def plotTrajectoriesNorPhasesPerConfig(files, figName, organisation, objectConfig, title, phase, exp, colorObjects,
                              objectPosition, radiusObjects):
    fig, axes = plt.subplots(nrows=5, ncols=5, figsize=(14, 15))  # building the plot for trajectories

    nRow = 0  # initialisation of the row
    nCol = 0  # initialisation of the column
    text_file = open('data_config_config.txt', 'w')

    for file in files:
        connection = sqlite3.connect(file)  # connection to the database

        pool = AnimalPool()
        pool.loadAnimals(connection)  # upload all the animals from the database
        animal = pool.animalDictionnary[1]
        rfid = animal.RFID
        setup = float(animal.setup)
        print('setup: ', setup)
        configName = organisation[exp][rfid]

        config = getConfigCat(rfid, exp, organisation)

        if phase == 'acquisition':
            '''tmin = getStartTestPhase(pool)'''
            tmin = 0
        else:
            tmin = 0
        tmax = tmin + 10 * oneMinute

        # set the axes. Check the number of file to get the dimension of axes and grab the correct ones.
        ax = axes[nRow][nCol]  # set the subplot where to draw the plot
        plotTrajectorySingleAnimal(file, color='black', colorTitle=getColorConfig(config), ax=ax, tmin=tmin,
                                   tmax=tmax, title=title, xa=128, xb=383, ya=80,
                                   yb=336)  # function to draw the trajectory
        text_file.write('{}\n'.format([exp, phase, rfid, setup, configName, objectConfig[configName][phase]]))
        object = objectConfig[configName][phase][0]
        print('object left: ', object)
        plotObjectZone(ax=ax, colorFill=colorObjects[object], x=objectPosition[setup]['left'][0],
                       y=objectPosition[setup]['left'][1], radius=radiusObjects[object],
                       alpha=0.5)  # plot the object on the right side
        plotObjectZone(ax=ax, colorFill=colorObjects[object], x=objectPosition[setup]['left'][0],
                       y=objectPosition[setup]['left'][1], radius=radiusObjects[object] + VIBRISSAE / scaleFactor,
                       alpha=0.2)
        plotObjectZone(ax=ax, colorFill=colorObjects[object], x=objectPosition[setup]['left'][0],
                       y=objectPosition[setup]['left'][1], radius=radiusObjects[object] + 2 * VIBRISSAE / scaleFactor,
                       alpha=0.1)
        object = objectConfig[configName][phase][1]
        print('object right: ', object)
        plotObjectZone(ax=ax, colorFill=colorObjects[object], x=objectPosition[setup]['right'][0],
                       y=objectPosition[setup]['right'][1], radius=radiusObjects[object],
                       alpha=0.5)  # plot the object on the left side
        plotObjectZone(ax=ax, colorFill=colorObjects[object], x=objectPosition[setup]['right'][0],
                       y=objectPosition[setup]['right'][1], radius=radiusObjects[object] + VIBRISSAE / scaleFactor,
                       alpha=0.2)  # plot a zone around the object on the left side
        plotObjectZone(ax=ax, colorFill=colorObjects[object], x=objectPosition[setup]['right'][0],
                       y=objectPosition[setup]['right'][1], radius=radiusObjects[object] + 2 * VIBRISSAE / scaleFactor,
                       alpha=0.1)  # plot a zone around the object on the left side

        if phase == 'test':
            if '1'in configName:
                positionNew = 'right'
            elif '2' in configName:
                positionNew = 'left'
            xNew = objectPosition[setup][positionNew][0]
            #yNew = objectPosition[setup][positionNew][1]
            yNew = -60
            ax.text(xNew, yNew, '*', horizontalalignment = 'center', verticalalignment = 'center', fontsize=24)

        if nCol < 5:
            nCol += 1
        if nCol >= 5:
            nCol = 0
            nRow += 1

        text_file.write('\n')
        connection.close()

    fig.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
    # plt.show() #display the plot
    fig.savefig('{}.pdf'.format(figName), dpi=200)
    fig.savefig('{}.jpg'.format(figName), dpi=200)
    text_file.close()


def computeSniffTimeConfig(files=None, tmin=None, phase=None):
    print('Compute time of exploration.')
    if phase == 'acquisition':
        eventList = ['SniffLeft', 'SniffRight', 'SniffLeftFar', 'SniffRightFar','UpLeft', 'UpRight']
    elif phase == 'test':
        eventList = ['SniffFamiliar', 'SniffNew', 'SniffFamiliarFar', 'SniffNewFar', 'UpFamiliar', 'UpNew']
    data = {}
    for val in ['nbEvent', 'meanEventLength', 'totalDuration']:
        data[val] = {}
        for event in eventList:
            data[val][event] = {}
            for config in configList:
                data[val][event][config] = {}
                for sex in ['male', 'female']:
                    data[val][event][config][sex] = {}

    for ratio in ['ratio', 'ratioFar']:
        data[ratio] = {}
        for phaseType in ['acquisition', 'test']:
            data[ratio][phaseType] = {}
            for config in configList:
                data[ratio][phaseType][config] = {}
                for sex in ['male', 'female']:
                    data[ratio][phaseType][config][sex] = {}


    for file in files:
        connection = sqlite3.connect(file)
        pool = AnimalPool()
        pool.loadAnimals(connection)
        animal = pool.animalDictionnary[1]
        sex = animal.sex
        setup = int(animal.setup)
        rfid = animal.RFID
        configName = organisation[exp][rfid]
        config = getConfigCat(rfid, exp, organisation)

        if tmin==None:
            tmin = getStartTestPhase(pool=pool)
        tmax = tmin + 10*oneMinute
        print('tmin-tmax: ', tmin, tmax)

        for eventType in eventList:
            # upload event timeline:
            eventTypeTimeLine = EventTimeLine(connection, eventType, minFrame=tmin, maxFrame=tmax)
            nbEvent = eventTypeTimeLine.getNbEvent()
            if nbEvent != 0:
                meanEventLength = eventTypeTimeLine.getMeanEventLength() / 30
                totalDuration = eventTypeTimeLine.getTotalLength() / 30
            elif nbEvent == 0:
                meanEventLength = 0
                totalDuration = 0
            print('###############total duration: ', eventType, totalDuration)
            data['nbEvent'][eventType][config][sex][rfid] = nbEvent
            data['meanEventLength'][eventType][config][sex][rfid] = meanEventLength
            data['totalDuration'][eventType][config][sex][rfid] = totalDuration

        if phase == 'acquisition':
            try:
                data['ratio'][phase][config][sex][rfid] = data['totalDuration']['SniffRight'][config][sex][rfid] / (
                            data['totalDuration']['SniffRight'][config][sex][rfid] +
                            data['totalDuration']['SniffLeft'][config][sex][rfid])
            except:
                data['ratio'][phase][config][sex][rfid] = 0

            try:
                data['ratioFar'][phase][config][sex][rfid] = data['totalDuration']['SniffRightFar'][config][sex][
                                                                rfid] / (data['totalDuration']['SniffRightFar'][
                                                                             config][sex][rfid] +
                                                                         data['totalDuration']['SniffLeftFar'][
                                                                             config][sex][rfid])
            except:
                data['ratioFar'][phase][config][sex][rfid] = 0

        if phase == 'test':
            try:
                data['ratio'][phase][config][sex][rfid] = data['totalDuration']['SniffNew'][config][sex][rfid] / (
                            data['totalDuration']['SniffNew'][config][sex][rfid] +
                            data['totalDuration']['SniffFamiliar'][config][sex][rfid])
            except:
                data['ratio'][phase][config][sex][rfid] = 0
            try:
                data['ratioFar'][phase][config][sex][rfid] = data['totalDuration']['SniffNewFar'][config][sex][rfid] / (data['totalDuration']['SniffNewFar'][config][sex][rfid] + data['totalDuration']['SniffFamiliarFar'][config][sex][rfid])
            except:
                data['ratioFar'][phase][config][sex][rfid] = 0
        connection.close()

    return data


def computeSniffTimePerTimeBinConfig(files=None, tmin=None, phase=None, timeBin=1*oneMinute):
    print('Compute time of exploration.')
    if phase == 'acquisition':
        eventList = ['SniffLeft', 'SniffRight', 'SniffLeftFar', 'SniffRightFar','UpLeft', 'UpRight', 'ratio', 'ratioFar']
    elif phase == 'test':
        eventList = ['SniffFamiliar', 'SniffNew', 'SniffFamiliarFar', 'SniffNewFar', 'UpFamiliar', 'UpNew', 'ratio', 'ratioFar']
    data = {}
    for val in ['durationPerTimeBin', 'cumulPerTimeBin', 'ratioCumulPerTimeBin', 'ratioFarCumulPerTimeBin']:
        data[val] = {}
        for event in eventList:
            data[val][event] = {}
            for config in configList:
                data[val][event][config] = {}
                for sex in ['male', 'female']:
                    data[val][event][config][sex] = {}

    for file in files:
        connection = sqlite3.connect(file)
        pool = AnimalPool()
        pool.loadAnimals(connection)
        animal = pool.animalDictionnary[1]
        sex = animal.sex
        setup = int(animal.setup)
        rfid = animal.RFID
        configName = organisation[exp][rfid]

        config = getConfigCat(rfid, exp, organisation)

        if tmin==None:
            tmin = getStartTestPhase(pool=pool)
        tmax = tmin + 10*oneMinute
        #print('tmin-tmax: ', tmin, tmax)

        for eventType in eventList:
            data['durationPerTimeBin'][eventType][config][sex][rfid] = []
            data['cumulPerTimeBin'][eventType][config][sex][rfid] = []

            # upload event timeline:
            eventTypeTimeLine = EventTimeLine(connection, eventType, minFrame=tmin, maxFrame=tmax)
            minT = tmin
            K = [i for i in range(10)]
            for k in K:
                if k < 9:
                    maxT = minT + timeBin - 1
                elif k == 9:
                    maxT = minT + timeBin
                #print('k=', k, 'interval: ', minT, maxT)
                durInTimeBin = eventTypeTimeLine.getTotalDurationEvent(tmin=minT, tmax=maxT)
                data['durationPerTimeBin'][eventType][config][sex][rfid].append( durInTimeBin )
                minT = minT + timeBin

            totalDuration = sum(data['durationPerTimeBin'][eventType][config][sex][rfid])
            totalLength = eventTypeTimeLine.getTotalDurationEvent(tmin = tmin, tmax = tmin+10*oneMinute)
            print('verif total duration: ', totalDuration, totalLength)
            previousTime = 0
            for i in data['durationPerTimeBin'][eventType][config][sex][rfid]:
                if totalDuration != 0:
                    propCumul = (previousTime + i) / totalDuration
                elif totalDuration == 0:
                    propCumul = 0
                data['cumulPerTimeBin'][eventType][config][sex][rfid].append( propCumul )
                previousTime = previousTime + i


        #Compute ratio based on cumulated time per time bin
        eventType = 'ratio'
        data['ratioCumulPerTimeBin']['ratio'][config][sex][rfid] = []
        data['ratioFarCumulPerTimeBin']['ratioFar'][config][sex][rfid] = []
        # upload event timeline:
        sniffNewTimeLine = EventTimeLine(connection, 'SniffNew', minFrame=tmin, maxFrame=tmax)
        sniffNewFarTimeLine = EventTimeLine(connection, 'SniffNewFar', minFrame=tmin, maxFrame=tmax)
        sniffFamiliarTimeLine = EventTimeLine(connection, 'SniffFamiliar', minFrame=tmin, maxFrame=tmax)
        sniffFamiliarFarTimeLine = EventTimeLine(connection, 'SniffFamiliarFar', minFrame=tmin, maxFrame=tmax)

        minT = tmin
        K = [i for i in range(10)]
        durSniffNew = 0
        durSniffNewFar = 0
        durSniffFamiliar = 0
        durSniffFamiliarFar = 0

        for k in K:
            if k < 9:
                maxT = minT + timeBin - 1
            elif k == 9:
                maxT = minT + timeBin
            print('k=', k, 'interval: ', minT, maxT)
            # Ratio with restricted contact zone:
            durSniffNewInTimeBin = sniffNewTimeLine.getTotalDurationEvent(tmin=minT, tmax=maxT)
            durSniffNew += durSniffNewInTimeBin
            durSniffFamiliarInTimeBin = sniffFamiliarTimeLine.getTotalDurationEvent(tmin=minT, tmax=maxT)
            durSniffFamiliar += durSniffFamiliarInTimeBin
            if durSniffNew + durSniffFamiliar == 0:
                ratioNew = 0
            else:
                ratioNew = durSniffNew / ( durSniffNew + durSniffFamiliar )
            data['ratioCumulPerTimeBin']['ratio'][config][sex][rfid].append( ratioNew )

            # Ratio with extended contact zone:
            durSniffNewFarInTimeBin = sniffNewFarTimeLine.getTotalDurationEvent(tmin=minT, tmax=maxT)
            durSniffNewFar += durSniffNewFarInTimeBin
            durSniffFamiliarFarInTimeBin = sniffFamiliarFarTimeLine.getTotalDurationEvent(tmin=minT, tmax=maxT)
            durSniffFamiliarFar += durSniffFamiliarFarInTimeBin
            if durSniffNewFar + durSniffFamiliarFar == 0:
                ratioNewFar = 0
            else:
                ratioNewFar = durSniffNewFar / (durSniffNewFar + durSniffFamiliarFar)
            data['ratioFarCumulPerTimeBin']['ratioFar'][config][sex][rfid].append(ratioNewFar)
            print('Verif: close: {} {}; far: {} {}'.format(durSniffNew, durSniffNewInTimeBin, durSniffNewFar, durSniffNewFarInTimeBin))
            #update timebin limits
            minT = minT + timeBin

        connection.close()

    return data


def getCumulDataSniffingPerTimeBinConfig(val, data, configList, eventList, sex):
    K = [i for i in range(10)]
    resultDic = {}
    for event in eventList:
        resultDic[event] = {}
        for config in configList:
            resultDic[event][config] = {}
            for k in K:
                resultDic[event][config][k] = []

    for event in eventList:
        for config in configList:
            for k in K:
                for rfid in data[val][event][config][sex].keys():
                    resultDic[event][config][k].append(data[val][event][config][sex][rfid][k])

    return resultDic


def plotCumulTimeSniffingConfig(ax, configList, ylabel, title, event, resultDic, timeBin):
    K = [i for i in range(10)]

    yMean = {event: {}}
    yError = {event: {}}
    for config in configList:
        yMean[event][config] = {}
        yError[event][config] = {}

    for config in configList:
        yMean[event][config] = []
        yError[event][config] = []
        for k in K:
            yMean[event][config].append(np.mean(resultDic[event][config][k]))
            yError[event][config].append(np.std(resultDic[event][config][k]))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    xIndex = K
    ax.set_xticks(xIndex)
    ax.set_xticklabels(K, rotation=0, fontsize=12, horizontalalignment='right')
    ax.set_ylabel(ylabel, fontsize=15)
    ax.set_xlabel('time bins of {} min'.format(timeBin/oneMinute), fontsize=15)
    ax.legend().set_visible(False)
    ax.xaxis.set_tick_params(direction="in")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1.1)
    ax.tick_params(axis='y', labelsize=14)
    ax.set_title('{} {}'.format(title, event), fontsize=16)

    xList = {'config1': [i+0.3 for i in K], 'config2': [i+0.6 for i in K]}
    starPos = [i+0.45 for i in K]

    for config in configList:
        ax.errorbar(x=xList[config], y=yMean[event][config], yerr=yError[event][config], fmt='o',
                    ecolor=getColorConfig(config), markerfacecolor=getColorConfig(config), markeredgecolor=getColorConfig(config))

    for k in K[:-1]:
        print('config1: ', resultDic[event][configList[0]][k])
        print('config2: ', resultDic[event][configList[1]][k])
        W, p = stats.mannwhitneyu(resultDic[event][configList[0]][k], resultDic[event][configList[1]][k])
        ax.text(x=starPos[k], y=1.05, s=getStarsFromPvalues(p, 1), ha='center')


def plotTotalTimeSniffingConfig(ax, configList, phase, totalSniffList):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    xIndex = [1, 2]
    ax.set_xticks(xIndex)
    ax.set_xticklabels(configList, rotation=45, fontsize=12, horizontalalignment='right')
    ax.set_ylabel('total time spent sniffing objects (s)', fontsize=13)
    ax.legend().set_visible(False)
    ax.xaxis.set_tick_params(direction="in")
    ax.set_title(phase, fontsize=14)
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 160)
    ax.tick_params(axis='y', labelsize=14)

    xPos = {'config1': 1, 'config2': 2}

    # plot the points for each value:
    for config in configList:
        ax.scatter(addJitter([xPos[config]] * len(totalSniffList[phase][config]['female']), 0.2),
                   totalSniffList[phase][config]['female'], color=getColorConfig(config), marker='o',
                   alpha=0.8, label="on", s=8)
        ax.errorbar(x=xPos[config], y=np.mean(totalSniffList[phase][config]['female']), yerr=np.std(totalSniffList[phase][config]['female']), fmt='o', ecolor='black', markerfacecolor='black', markeredgecolor='black')

    # conduct statistical testing: Wilcoxon paired test:
    st1 = totalSniffList[phase][configList[0]]['female']
    st2 = totalSniffList[phase][configList[1]]['female']
    print(st1)
    print(st2)
    U, p = stats.mannwhitneyu(st1, st2)
    print(
        'Mann-Whitney U test for {} versus {} females between setups: U={}, p={}'.format(len(st1), len(st2), U,
                                                                                         p))
    ax.text((xPos['config1'] + xPos['config2']) / 2, 160 * 0.90,
            getStarsFromPvalues(pvalue=p, numberOfTests=1), fontsize=16, horizontalalignment='center')



if __name__ == '__main__':

    print("Code launched.")
    # set font
    from matplotlib import rc

    rc('font', **{'family': 'serif', 'serif': ['Arial']})

    while True:
        question = "Do you want to:"
        question += "\n\t [1] rebuild all events?"
        question += "\n\t [2] check file info?"
        question += "\n\t [3] rebuild sniff events?"
        question += "\n\t [3b] plot sniffing timelines?"
        question += "\n\t [3c] plot sniffing timelines to check the events?"
        question += "\n\t [4] plot trajectories in the habituation phase?"
        question += "\n\t [5] plot trajectories in the acquisition phase (same objects)?"
        question += "\n\t [6] plot trajectories in the test phase (different objects)?"
        question += "\n\t [7] plot ratio for sniffing?"
        question += "\n\t [8] compute and plot raw values for sniffing time?"
        question += "\n\t [9] compute sniffing time per time bin?"
        question += "\n\t [10] plot sniffing time per time bin?"
        question += "\n\t [11] plot ratio based on cumulated time per time bin?"
        question += "\n\t [12] compare the total time spent sniffing in the two cage types?"
        question += "\n"
        answer = input(question)

        if answer == '1':
            print("Rebuilding all events.")
            processAll()

            break

        if answer == '2':
            print('Check information entered into the databases')
            question1 = "Is it the short or medium retention time? (short / medium / long)"
            exp = input(question1)
            question2 = "Is it the acquisition or test phase? (acquisition / test)"
            phase = input(question2)
            files = getFilesToProcess()
            text_file_name = 'file_info.text'
            text_file = open(text_file_name, "w")

            for file in files:
                print(file)
                connection = sqlite3.connect(file)  # connection to the database

                pool = AnimalPool()
                pool.loadAnimals(connection)  # upload all the animals from the database
                animal = pool.animalDictionnary[1]
                sex = animal.sex
                setup = int(animal.setup)
                geno = animal.genotype
                rfid = animal.RFID
                age = animal.age
                config = organisation[exp][rfid]
                infoList = [file, rfid, sex, geno, age, setup, phase, config]
                for info in infoList:
                    text_file.write("{}\t".format(info))
                text_file.write("\n")
                connection.close()

            text_file.write("\n")
            text_file.close()
            print('Job done.')
            break

        if answer == '3':
            print("Rebuilding sniff events.")
            question1 = "Is it the short, medium or long retention time? (short / medium / long)"
            exp = input(question1)
            question2 = "Is it the acquisition or test phase? (acquisition / test)"
            phase = input(question2)
            files = getFilesToProcess()

            if phase == 'acquisition':
                for file in files:
                    print(file)
                    connection = sqlite3.connect(file)
                    pool = AnimalPool()
                    pool.loadAnimals(connection)  # upload all the animals from the database
                    animal = pool.animalDictionnary[1]
                    sex = animal.sex
                    setup = int(animal.setup)
                    rfid = animal.RFID
                    config = organisation[exp][rfid]
                    objectType = objectConfig[config][phase]
                    BuildEventObjectSniffingNorAcquisitionWithConfig.reBuildEvent(connection, tmin=0, tmax=20 * oneMinute, pool = None, exp=exp, phase=phase, objectPosition=objectPosition, radiusObjects=radiusObjects, objectTuple=objectType, vibrissae=VIBRISSAE)
                    connection.close()
                    print('Rebuild sniff events done during acquisition.')

            if phase == 'test':
                for file in files:
                    print(file)
                    connection = sqlite3.connect(file)
                    pool = AnimalPool()
                    pool.loadAnimals(connection)  # upload all the animals from the database
                    animal = pool.animalDictionnary[1]
                    sex = animal.sex
                    setup = int(animal.setup)
                    rfid = animal.RFID
                    config = organisation[exp][rfid]
                    objectType = objectConfig[config][phase]
                    #determine the side the of novel object in the configuration:
                    if '1' in config:
                        side = 1
                    elif '2' in config:
                        side = 0

                    BuildEventObjectSniffingNorTestWithConfig.reBuildEvent(connection, tmin=0,
                                                                           tmax=20 * oneMinute, pool=None,
                                                                           objectPosition=objectPosition,
                                                                           radiusObjects=radiusObjects,
                                                                           objectTuple=objectType, side=side, vibrissae=VIBRISSAE)
                    connection.close()
                    print('Rebuild sniff events done during test.')
            break


        if answer == '3b':
            print('Plot sniffing timelines and compute number, total duration and mean duration of sniffing events')
            question1 = "Is it the short, medium or long retention time? (short / medium / long)"
            exp = input(question1)
            question2 = "Is it the acquisition or test phase? (acquisition / test)"
            phase = input(question2)
            files = getFilesToProcess()

            addThickness = 0
            yLim = {'nbEvent': 80, 'meanEventLength': 4, 'totalDuration': 70, 'ratio': 1.2}

            configList = ['config1', 'config2']

            figName = 'fig_timeline_nor_config_{}_{}.pdf'.format(exp, phase)
            fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14, 8))  # building the plot for timelines

            nRow = {'male': {'config1': 1, 'config2': 1}, 'female': {'config1': 0, 'config2': 0}}  # initialisation of the row
            nCol = {'male': {'config1': 0, 'config2': 1}, 'female': {'config1': 0, 'config2': 1}}  # initialisation of the column
            line = {}
            for sex in sexList:
                line[sex] = {}
                for config in configList:
                    line[sex][config] = 1

            for row in [0,1]:
                for col in [0,1]:
                    ax = axes[row][col]
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['left'].set_visible(False)
                    ax.set_title('configuration {} ({})'.format(configList[col], sexList[row]), fontsize=18)
                    ax.legend().set_visible(False)
                    ax.xaxis.set_tick_params(direction="in")
                    ax.get_yaxis().set_visible(False)
                    ax.set_xlim(0, 14400)
                    ax.set_ylim(0, 16)

            measureData = {}
            for var in ['nbEvent', 'meanEventLength', 'totalDuration', 'ratio']:
                measureData[var] = {}
                for eventType in eventList[phase]:
                    measureData[var][eventType] = {}
                    for config in configList:
                        measureData[var][eventType][config] = {}
                        for sex in sexList:
                            measureData[var][eventType][config][sex] = []


            for file in files:
                print(file)
                connection = sqlite3.connect(file)
                pool = AnimalPool()
                pool.loadAnimals(connection)
                animal = pool.animalDictionnary[1]
                sex = animal.sex
                rfid = animal.RFID
                geno = animal.genotype
                setup = animal.setup
                configTemporary = organisation[exp][rfid]
                config = getConfigCat(rfid, exp, organisation)

                #determine the start frame:
                if phase == 'acquisition':
                    '''tmin = getStartTestPhase(pool)'''
                    tmin = 0
                elif phase == 'test':
                    tmin = 0
                #determine the end of the computation
                tmax = tmin + 10*oneMinute

                ax = axes[nRow[sex][config]][nCol[sex][config]]
                ax.text(-20, line[sex][config]-0.5, s=animal.RFID[-4:], fontsize=10, horizontalalignment='right')
                #compute the coordinates for the drawing:
                lineData = {}
                for eventType in eventList[phase]:
                    #upload event timeline:
                    eventTypeTimeLine = EventTimeLine( connection, eventType, minFrame = tmin, maxFrame = tmax )
                    nbEvent = eventTypeTimeLine.getNbEvent()
                    if nbEvent != 0:
                        meanEventLength = eventTypeTimeLine.getMeanEventLength() / 30
                        totalDuration = eventTypeTimeLine.getTotalLength() / 30
                    elif nbEvent == 0:
                        meanEventLength = 0
                        totalDuration = 0
                    print('###############total duration: ', totalDuration)
                    measureData['nbEvent'][eventType][config][sex].append(nbEvent)
                    measureData['meanEventLength'][eventType][config][sex].append(meanEventLength)
                    measureData['totalDuration'][eventType][config][sex].append(totalDuration)

                    lineData[eventType] = []
                    for event in eventTypeTimeLine.eventList:
                        lineData[eventType].append((event.startFrame - tmin - addThickness, event.duration() + addThickness))

                    ax.broken_barh(lineData[eventType], (line[sex][config] - 1, 1), facecolors=colorEvent[eventType])
                    print('plot for ', animal.RFID)
                    print('line: ', line[sex][config])
                if phase == 'acquisition':
                    sniffRightTimeLine = EventTimeLine(connection, 'SniffRight', minFrame=tmin, maxFrame=tmax)
                    totalDurationRight = sniffRightTimeLine.getTotalLength()
                    sniffLeftTimeLine = EventTimeLine(connection, 'SniffLeft', minFrame=tmin, maxFrame=tmax)
                    totalDurationLeft = sniffLeftTimeLine.getTotalLength()

                    measureData['ratio']['SniffRight'][config][sex].append(totalDurationRight / (totalDurationLeft + totalDurationRight))
                    measureData['ratio']['SniffLeft'][config][sex].append(totalDurationLeft / (totalDurationLeft + totalDurationRight))

                if phase == 'test':
                    sniffNewTimeLine = EventTimeLine(connection, 'SniffNew', minFrame=tmin, maxFrame=tmax)
                    totalDurationNew = sniffNewTimeLine.getTotalLength()
                    sniffFamiliarTimeLine = EventTimeLine(connection, 'SniffFamiliar', minFrame=tmin, maxFrame=tmax)
                    totalDurationFamiliar = sniffFamiliarTimeLine.getTotalLength()

                    measureData['ratio']['SniffNew'][config][sex].append(
                        totalDurationNew / (totalDurationFamiliar + totalDurationNew))
                    measureData['ratio']['SniffFamiliar'][config][sex].append(
                        totalDurationFamiliar / (totalDurationFamiliar + totalDurationNew))

                line[sex][config] += 1.5
                connection.close()

            fig.show()
            fig.savefig(figName, dpi=300)

            labelList = {'acquisition': ['Left', 'Right', 'Left', 'Right'],
                         'test': ['Familiar', 'New', 'Familiar', 'New']}

            figName = 'fig_measures_events_config_{}_{}.pdf'.format(exp, phase)
            figMeasures, axesMeasures = plt.subplots(nrows=1, ncols=4, figsize=(24, 4))
            sex = 'male'
            col = 0
            for var in ['nbEvent', 'meanEventLength', 'totalDuration', 'ratio']:
                ax = axesMeasures[col]
                yLabel = var
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                xIndex = [1, 2, 4, 5]
                ax.set_xticks(xIndex)
                ax.set_xticklabels(labelList[phase], rotation=45, fontsize=12, horizontalalignment='right')
                ax.set_ylabel(yLabel, fontsize=15)
                ax.legend().set_visible(False)
                ax.xaxis.set_tick_params(direction="in")
                ax.set_xlim(0, 6)
                ax.set_ylim(0, yLim[var])
                ax.tick_params(axis='y', labelsize=14)
                ax.text(1.5, yLim[var], s='config 1', fontsize=14, horizontalalignment='center')
                ax.text(4.5, yLim[var], s='config 2', fontsize=14, horizontalalignment='center')

                if var == 'ratio':
                    ax.hlines(0.5, xmin = 0, xmax=12, colors='grey', linestyles='dashed')

                # plot the points for each value:
                if phase == 'acquisition':
                    event1 = 'SniffLeft'
                    event2 = 'SniffRight'
                elif phase == 'test':
                    event1 = 'SniffFamiliar'
                    event2 = 'SniffNew'
                config = 'config1'
                ax.scatter(addJitter([1] * len(measureData[var][event1][config][sex]), 0.2),
                           measureData[var][event1][config][sex], color='grey', marker=markerListConfig[config], alpha=0.8,
                           label="on", s=8)
                ax.scatter(addJitter([2] * len(measureData[var][event2][config][sex]), 0.2),
                           measureData[var][event2][config][sex], color='grey', marker=markerListConfig[config], alpha=0.8,
                           label="on", s=8)

                config = 'config2'
                ax.scatter(addJitter([4] * len(measureData[var][event1][config][sex]), 0.2),
                           measureData[var][event1][config][sex], color='red', marker=markerListConfig[config], alpha=0.8,
                           label="on", s=8)
                ax.scatter(addJitter([5] * len(measureData[var][event2][config][sex]), 0.2),
                           measureData[var][event2][config][sex], color='red', marker=markerListConfig[config], alpha=0.8,
                           label="on", s=8)



                if var == 'ratio':
                    # conduct statistical testing: one sample Student t-test:
                    if phase == 'acquisition':
                        eventToTest = 'SniffRight'
                    elif phase == 'test':
                        eventToTest = 'SniffNew'

                    for config in ['config1', 'config2']:
                        prop = measureData['ratio'][eventToTest][config][sex]
                        T, p = stats.ttest_1samp(a=prop, popmean=0.5)
                        print(
                            'One-sample Student T-test for {} acquisition {} {} {}: T={}, p={}'.format(exp, len(prop), sex, config, T, p))
                        ax.text(xPosConfig[sex][config], 1.1, getStarsFromPvalues(pvalue=p, numberOfTests=1), fontsize=14)

                col += 1

            figMeasures.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
            figMeasures.show() #display the plot
            figMeasures.savefig(figName, dpi=200)
            break


        if answer == '3c':
            print('plot sniffing events timelines to check the events')
            question1 = "Is it the short, medium or long retention time? (short / medium / long)"
            exp = input(question1)
            question2 = "Is it the acquisition or test phase? (acquisition / test)"
            phase = input(question2)
            files = getFilesToProcess()

            addThickness = 0
            yLim = {'nbEvent': 80, 'meanEventLength': 4, 'totalDuration': 70, 'ratio': 1.2}

            configList = ['config1', 'config2']

            figName = 'fig_timeline_nor_config_{}_{}_check.pdf'.format(exp, phase)
            fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14, 8))  # building the plot for timelines

            nRow = {'male': {'config1': 1, 'config2': 1}, 'female': {'config1': 0, 'config2': 0}}  # initialisation of the row
            nCol = {'male': {'config1': 0, 'config2': 1}, 'female': {'config1': 0, 'config2': 1}}  # initialisation of the column
            line = {}
            for sex in sexList:
                line[sex] = {}
                for config in configList:
                    line[sex][config] = 1

            for row in [0,1]:
                for col in [0,1]:
                    ax = axes[row][col]
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['left'].set_visible(False)
                    ax.set_title('configuration {} ({})'.format(configList[col], sexList[row]), fontsize=18)
                    ax.legend().set_visible(False)
                    ax.xaxis.set_tick_params(direction="in")
                    ax.get_yaxis().set_visible(False)
                    ax.set_xlim(0, 14400)
                    ax.set_ylim(0, 16)


            for file in files:
                print(file)
                connection = sqlite3.connect(file)
                pool = AnimalPool()
                pool.loadAnimals(connection)
                animal = pool.animalDictionnary[1]
                sex = animal.sex
                rfid = animal.RFID
                geno = animal.genotype
                setup = animal.setup
                configTemporary = organisation[exp][rfid]
                config = getConfigCat(rfid, exp, organisation)
                #determine the start frame:
                if phase == 'acquisition':
                    '''tmin = getStartTestPhase(pool)'''
                    tmin = 0
                elif phase == 'test':
                    tmin = 0
                #determine the end of the computation
                tmax = tmin + 10*oneMinute

                ax = axes[nRow[sex][config]][nCol[sex][config]]
                ax.text(-20, line[sex][config]-0.5, s=animal.RFID[-4:], fontsize=10, horizontalalignment='right')
                #compute the coordinates for the drawing:
                lineData = {}
                for eventType in eventList[phase]:
                    #upload event timeline:
                    eventTypeTimeLine = EventTimeLine( connection, eventType, minFrame = tmin, maxFrame = tmax )

                    lineData[eventType] = []
                    for event in eventTypeTimeLine.eventList:
                        lineData[eventType].append((event.startFrame - tmin - addThickness, event.duration() + addThickness))

                    ax.broken_barh(lineData[eventType], (line[sex][config] - 1, 1), facecolors=colorEvent[eventType])
                    print('plot for ', animal.RFID)
                    print('line: ', line[sex][config])
                    line[sex][config] += 0.2

                line[sex][config] += 1.5
                connection.close()

            fig.show()
            fig.savefig(figName, dpi=300)
            break


        if answer == '4':
            print('Plot trajectory in the habituation phase')
            #distance travelled
            #space use
            #traj of center of mass
            files = getFilesToProcess()
            buildFigTrajectoryMalesFemales(files=files, title='hab', tmin=0, tmax=4*oneMinute, figName='fig_traj_hab_long_nor', colorSap=colorSap, xa=128, xb=383, ya=80, yb=336)
            print('Job done.')
            break

        if answer == '5':
            print('Plot trajectory during the acquisition phase.')
            question = "Is it the short, medium or long retention time? (short / medium / long)"
            exp = input(question)
            phase = 'acquisition'

            #traj of center of mass
            #traj of the nose position
            #sap
            #time spent sniffing the object
            timeSniff = {}
            #time spent around the object
            #body orientation toward each object
            files = getFilesToProcess()
            figName = 'fig_traj_nor_config_{}_same'.format(exp)
            plotTrajectoriesNorPhasesPerConfig(files=files, figName=figName, organisation=organisation, objectConfig=objectConfig, title=phase, phase=phase, exp=exp, colorObjects=colorObjects, objectPosition=objectPosition, radiusObjects=radiusObjects)

            data = computeSniffTimeConfig(files, tmin=0, phase=phase)

            # store the data dictionary in a json file
            with open('sniff_time_config_same_{}.json'.format(exp), 'w') as jFile:
                json.dump(data, jFile, indent=4)
            print("json file created")

            break

        if answer == '6':
            print('Plot trajectory in the test phase')
            question = "Is it the short or medium retention time? (short / medium)"
            exp = input(question)
            phase = 'test'
            #distance travelled
            #space use
            #traj of center of mass
            files = getFilesToProcess()
            figName = 'fig_traj_nor_config_{}_test'.format(exp)
            plotTrajectoriesNorPhasesPerConfig(files=files, figName=figName, organisation=organisation, objectConfig=objectConfig, title=phase, phase=phase, exp=exp, colorObjects=colorObjects, objectPosition=objectPosition, radiusObjects=radiusObjects)

            data = computeSniffTimeConfig(files, tmin=0, phase=phase)

            # store the data dictionary in a json file
            with open('sniff_time_config_test_{}.json'.format(exp), 'w') as jFile:
                json.dump(data, jFile, indent=4)
            print("json file created")

            break

        if answer == '7':
            # open the json files
            question = "Is it the short, medium or long retention time? (short / medium / long)"
            exp = input(question)

            jsonFileName = "sniff_time_config_same_{}.json".format(exp)
            with open(jsonFileName) as json_data:
                dataSame = json.load(json_data)
            jsonFileName = "sniff_time_config_test_{}.json".format(exp)
            with open(jsonFileName) as json_data:
                dataTest = json.load(json_data)
            print("json file re-imported.")
            print(dataSame)

            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))  # create the figure for the graphs of the computation

            col = 0  # initialise the column number
            # reformate the data dictionary to get the correct format of data for plotting and statistical analyses

            xPos = {'config1': 1, 'config2': 2}
            ''' eventList = {'acquisition': ['SniffLeft', 'SniffRight', 'UpLeft', 'UpRight'],
                         'test': ['SniffFamiliar', 'SniffNew', 'UpFamiliar', 'UpNew']}'''
            eventList = {'acquisition': ['SniffLeftFar', 'SniffRightFar', 'UpLeft', 'UpRight'],
                         'test': ['SniffFamiliarFar', 'SniffNewFar', 'UpFamiliar', 'UpNew']}



            event1 = {'acquisition': eventList['acquisition'][0], 'test': eventList['test'][0]}
            event2 = {'acquisition': eventList['acquisition'][1], 'test': eventList['test'][1]}

            for phase in ['acquisition', 'test']:
                if phase == 'acquisition':
                    dataToAnalyse = dataSame
                elif phase == 'test':
                    dataToAnalyse = dataTest

                data = {}
                for val in ['ratio']:
                    data[val] = {}
                    for config in configList:
                        data[val][config] = {}
                        for sex in ['male', 'female']:
                            data[val][config][sex] = []
                            for rfid in dataToAnalyse['ratio'][phase][config][sex].keys():
                                if (dataToAnalyse['totalDuration'][event1[phase]][config][sex][rfid] >= 3) & (
                                        dataToAnalyse['totalDuration'][event2[phase]][config][sex][rfid] >= 3):
                                    data[val][config][sex].append(dataToAnalyse['ratio'][phase][config][sex][rfid])

                                else:
                                    print('Too Short exploration time in config {} for {} {}'.format(config, sex, rfid))


                print(data)

                sex = 'male'

                ax = axes[col]
                yLabel = 'ratio sniff time'
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                xIndex = [1, 2]
                ax.set_xticks(xIndex)
                ax.set_xticklabels(['config1', 'config2'], rotation=45, fontsize=12, horizontalalignment='right')
                ax.set_ylabel(yLabel, fontsize=15)
                ax.set_title(phase, fontsize=15)
                ax.legend().set_visible(False)
                ax.xaxis.set_tick_params(direction="in")
                ax.set_xlim(0, 3)
                ax.set_ylim(0, 1.2)
                ax.tick_params(axis='y', labelsize=14)
                #ax.text(1, 1.2, s='transparent', fontsize=16, horizontalalignment='center')
                #ax.text(2, 1.2, s='red', fontsize=16, horizontalalignment='center')
                ax.hlines(0.5, xmin = 0, xmax=12, colors='grey', linestyles='dashed')

                for config in configList:
                    ax.scatter(addJitter([xPos[config]] * len(data['ratio'][config][sex]), 0.2),
                           data['ratio'][config][sex], color=getColorConfig(config), marker='o', alpha=0.8, label="on", s=8)
                    prop = data['ratio'][config][sex]
                    T, p = stats.ttest_1samp(a=prop, popmean=0.5)
                    print('One-sample Student T-test for {} {} {} {} in config {}: T={}, p={}'.format(exp, phase, len(prop), sex, config, T, p))
                    ax.text(xPos[config], 1.1, getStarsFromPvalues(pvalue=p, numberOfTests=1), fontsize=16, horizontalalignment='center')

                col += 1

            fig.tight_layout()
            fig.show()

            fig.savefig('fig_ratio_config_{}.pdf'.format(exp), dpi=200)
            fig.savefig('fig_ratio_config_{}.jpg'.format(exp), dpi=200)
            break


        if answer == '8':
            print('Compute and plot raw values for sniffing time')
            # open the json files
            question = "Is it the short, medium or long retention time? (short / medium / long)"
            exp = input(question)
            question = "Is it the acquisition or the test phase? (acquisition / test)"
            phase = input(question)

            jsonFileName = "sniff_time_config_same_{}.json".format(exp)
            with open(jsonFileName) as json_data:
                dataSame = json.load(json_data)
            jsonFileName = "sniff_time_config_test_{}.json".format(exp)
            with open(jsonFileName) as json_data:
                dataTest = json.load(json_data)
            print("json file re-imported.")
            print(dataSame)

            if phase == 'acquisition':
                dataToAnalyse = dataSame
            elif phase == 'test':
                dataToAnalyse = dataTest

            '''eventList = {'acquisition': ['SniffLeft', 'SniffRight', 'UpLeft', 'UpRight'],
                         'test': ['SniffFamiliar', 'SniffNew', 'UpFamiliar', 'UpNew']}'''

            eventList = {'acquisition': ['SniffLeftFar', 'SniffRightFar', 'UpLeft', 'UpRight'],
                         'test': ['SniffFamiliarFar', 'SniffNewFar', 'UpFamiliar', 'UpNew']}

            event1 = {'acquisition': eventList['acquisition'][0], 'test': eventList['test'][0]}
            event2 = {'acquisition': eventList['acquisition'][1], 'test': eventList['test'][1]}

            fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(12, 4))  # create the figure for the graphs of the computation

            data = {}

            yLim = {'totalDuration': 60, 'nbEvent': 60, 'meanEventLength': 5}
            yLabel = {'totalDuration': 'total sniff (s)', 'nbEvent': 'nb of sniff events', 'meanEventLength': 'mean event duration (s)'}

            k = 0
            for measure in ['totalDuration', 'nbEvent', 'meanEventLength']:
                for val in eventList[phase]:
                    print(val)
                    data[val] = {}
                    for config in configList:
                        data[val][config] = {}
                        for sex in ['male', 'female']:
                            data[val][config][sex] = []
                            for rfid in dataToAnalyse[measure][val][config][sex].keys():
                                data[val][config][sex].append(dataToAnalyse[measure][val][config][sex][rfid])


                ax = axes[k]
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                xIndex = [1, 2, 4, 5]
                ax.set_xticks(xIndex)
                ax.set_xticklabels([eventList[phase][0], eventList[phase][1], eventList[phase][0], eventList[phase][1]], rotation=45, fontsize=12, horizontalalignment='right')
                ax.set_ylabel(yLabel[measure], fontsize=15)
                ax.legend().set_visible(False)
                ax.xaxis.set_tick_params(direction="in")
                ax.set_xlim(0, 6)
                ax.set_ylim(0, yLim[measure])
                ax.tick_params(axis='y', labelsize=14)
                ax.text(1.5, yLim[measure], s='config 1', fontsize=16, horizontalalignment='center')
                ax.text(4.5, yLim[measure], s='config 2', fontsize=16, horizontalalignment='center')
                if measure == 'totalDuration':
                    ax.hlines(5, xmin=0, xmax=12, colors='grey', linestyles='dashed')

                xPos = {'config1': (1,2), 'config2': (4,5)}
                sex = 'male'

                # plot the points for each value:
                for config in configList:
                    ax.scatter(addJitter([xPos[config][0]] * len(data[eventList[phase][0]][config][sex]), 0.2),
                               data[eventList[phase][0]][config][sex], color=getColorConfig(config), marker='o', alpha=0.8, label="on", s=8)
                    ax.scatter(addJitter([xPos[config][1]] * len(data[eventList[phase][1]][config][sex]), 0.2),
                               data[eventList[phase][1]][config][sex], color=getColorConfig(config), marker='o', alpha=0.8, label="on",
                               s=8)
                    # conduct statistical testing: Wilcoxon paired test:
                    obj0 = data[eventList[phase][0]][config][sex]
                    obj1 = data[eventList[phase][1]][config][sex]
                    U, p = stats.wilcoxon(obj0, obj1)
                    print('Wilcoxon paired test for {} test {} {} setup {}: T={}, p={}'.format(exp, len(obj0), sex, config, U, p))
                    ax.text((xPos[config][0]+xPos[config][1])/2, yLim[measure]*0.90, getStarsFromPvalues(pvalue=p, numberOfTests=1), fontsize=16, horizontalalignment='center')

                k += 1

            fig.tight_layout()
            fig.show()
            fig.savefig('fig_raw_values_config_{}_{}.pdf'.format(exp, phase), dpi=300)
            fig.savefig('fig_raw_values_config_{}_{}.jpg'.format(exp, phase), dpi=300)

            break

        if answer == '9':
            print('Compute sniff time per time bin.')
            question = "Is it the short, medium or long retention time? (short / medium / long)"
            exp = input(question)
            question = "Is it the acquisition or test phase? (acquisition / test)"
            phase = input(question)

            '''tmin = {'acquisition': None, 'test': 0}'''
            tmin = {'acquisition': 0, 'test': 0}

            files = getFilesToProcess()

            data = computeSniffTimePerTimeBinConfig(files, tmin=tmin[phase], phase=phase, timeBin=timeBin)

            # store the data dictionary in a json file
            with open('sniff_time_timebin_config_{}_{}.json'.format(phase, exp), 'w') as jFile:
                json.dump(data, jFile, indent=4)
            print("json file created")

            break


        if answer == '10':
            #compute cumulated proportion of time sniffing
            # open the json files
            question = "Is it the short, medium or long retention time? (short / medium / long)"
            exp = input(question)

            jsonFileName = "sniff_time_timebin_config_acquisition_{}.json".format(exp)
            with open(jsonFileName) as json_data:
                dataSame = json.load(json_data)
            jsonFileName = "sniff_time_timebin_config_test_{}.json".format(exp)
            with open(jsonFileName) as json_data:
                dataTest = json.load(json_data)
            print("json files re-imported.")

            val = 'cumulPerTimeBin'
            eventSame = ['SniffLeftFar', 'SniffRightFar']
            eventTest = ['SniffFamiliarFar', 'SniffNewFar']
            sex = 'male'

            for eventList in [eventSame, eventTest]:
                if eventList == eventSame:
                    data = dataSame
                    nameFig = 'acquisition'
                elif eventList == eventTest:
                    data = dataTest
                    nameFig = 'test'

                resultDic = getCumulDataSniffingPerTimeBinConfig(val = val, data = data, configList = configList, eventList = eventList, sex = sex)

                #plot for learning phase
                fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))  # create the figure for the graphs of the computation

                ax = axes[0]
                plotCumulTimeSniffingConfig(ax, configList=configList, title=nameFig, ylabel='cumul. prop. sniffing (mean+-sd)', resultDic=resultDic, event=eventList[0], timeBin=timeBin)

                ax = axes[1]
                plotCumulTimeSniffingConfig(ax, configList=configList, title=nameFig, ylabel='cumul. prop. sniffing (mean+-sd)', resultDic=resultDic, event=eventList[1], timeBin=timeBin)

                fig.tight_layout()
                fig.show()
                fig.savefig('fig_cumul_timebin_config_{}_{}.pdf'.format(exp, nameFig), dpi=300)
                fig.savefig('fig_cumul_timebin_config_{}_{}.jpg'.format(exp, nameFig), dpi=300)

            print('Job done.')
            break


        if answer == '11':
            #plot ratio based on cumulated time per time bin only in the test phase
            #open the json files
            question = "Is it the short, medium or long retention time? (short / medium / long)"
            exp = input(question)

            jsonFileName = "sniff_time_timebin_config_test_{}.json".format(exp)
            with open(jsonFileName) as json_data:
                dataTest = json.load(json_data)
            print("json files re-imported.")

            data = dataTest
            sex = 'male'
            #plot for test phase
            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))  # create the figure for the graphs of the computation

            ax = axes[0]
            val = 'ratioCumulPerTimeBin'
            resultDic = getCumulDataSniffingPerTimeBinConfig(val=val, data=data, configList=configList, eventList=['ratio'], sex=sex)
            plotCumulTimeSniffingConfig(ax, configList=configList, title='(restricted zone)', ylabel='ratio based on cumulative time', resultDic=resultDic, event='ratio', timeBin=timeBin)
            ax.hlines(y=0.5, xmin=0, xmax=10, colors='grey', linestyles='dashed')

            ax = axes[1]
            val = 'ratioFarCumulPerTimeBin'
            resultDic = getCumulDataSniffingPerTimeBinConfig(val=val, configList=configList, data=data, eventList=['ratioFar'], sex=sex)
            plotCumulTimeSniffingConfig(ax, configList=configList, title='(extended zone)', ylabel='ratio based on cumulative time', resultDic=resultDic, event='ratioFar', timeBin=timeBin)
            ax.hlines(y=0.5, xmin=0, xmax=10, colors='grey', linestyles='dashed')

            fig.tight_layout()
            fig.show()
            fig.savefig('fig_cumul_ratio_timebin_config_{}.pdf'.format(exp), dpi=300)
            fig.savefig('fig_cumul_ratio_timebin_config_{}.jpg'.format(exp), dpi=300)

            print('Job done.')
            break


        if answer == '12':
            print('conpare sniff time between the two configuration types')
            eventList = {'acquisition': ['SniffLeft', 'SniffRight', 'UpLeft', 'UpRight'],
                         'test': ['SniffFamiliar', 'SniffNew', 'UpFamiliar', 'UpNew']}

            '''eventList = {'acquisition': ['SniffLeftFar', 'SniffRightFar', 'UpLeft', 'UpRight'],
                         'test': ['SniffFamiliarFar', 'SniffNewFar', 'UpFamiliar', 'UpNew']}'''

            event1 = {'acquisition': eventList['acquisition'][0], 'test': eventList['test'][0]}
            event2 = {'acquisition': eventList['acquisition'][1], 'test': eventList['test'][1]}
            expList = ['short', 'medium']


            # open the json files
            for exp in expList:
                jsonFileName = "sniff_time_config_same_{}.json".format(exp)
                with open(jsonFileName) as json_data:
                    dataSame = json.load(json_data)
                jsonFileName = "sniff_time_config_test_{}.json".format(exp)
                with open(jsonFileName) as json_data:
                    dataTest = json.load(json_data)
                print("json file re-imported.")

                totalSniffTime = {}
                for phase in ['acquisition', 'test']:
                    totalSniffTime[phase] = {}
                    for config in configList:
                        totalSniffTime[phase][config] = {}
                        for sex in ['male', 'female']:
                            totalSniffTime[phase][config][sex] = {}

                sex = 'male'
                #compute total duration of sniffing objects in the acquisition phase
                phase = 'acquisition'
                dataToAnalyse = dataSame
                for config in configList:
                    for rfid in dataToAnalyse['totalDuration'][event1[phase]][config][sex].keys():
                        totalSniffTime[phase][config][sex][rfid] = dataToAnalyse['totalDuration'][event1[phase]][config][sex][rfid] + dataToAnalyse['totalDuration'][event2[phase]][config][sex][rfid]

                # compute total duration of sniffing objects in the test phase
                phase = 'test'
                dataToAnalyse = dataTest
                for config in configList:
                    for rfid in dataToAnalyse['totalDuration'][event1[phase]][config][sex].keys():
                        totalSniffTime[phase][config][sex][rfid] = \
                        dataToAnalyse['totalDuration'][event1[phase]][config][sex][rfid] + \
                        dataToAnalyse['totalDuration'][event2[phase]][config][sex][rfid]

                totalSniffList = {}
                for phase in ['acquisition', 'test']:
                    totalSniffList[phase] = {}
                    for config in configList:
                        totalSniffList[phase][config] = {sex: []}
                        for rfid in totalSniffTime[phase][config][sex].keys():
                            totalSniffList[phase][config][sex].append(totalSniffTime[phase][config][sex][rfid])

                fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))  # create the figure for the graphs of the computation

                phase = 'acquisition'
                ax = axes[0]
                plotTotalTimeSniffingConfig(ax=ax, configList=configList, phase=phase, totalSniffList=totalSniffList)

                phase = 'test'
                ax = axes[1]
                plotTotalTimeSniffingConfig(ax=ax, configList=configList, phase=phase, totalSniffList=totalSniffList)

                fig.tight_layout()
                fig.show()
                fig.savefig('fig_total_sniff_time_config_{}_close.pdf'.format(exp), dpi=300)
                fig.savefig('fig_total_sniff_time_config_{}_close.jpg'.format(exp), dpi=300)

            break




