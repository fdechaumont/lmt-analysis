'''
#Created on 22 September 2021

#@author: Elodie
'''

from scripts.Novel_Object_Recognition_Test.ConfigurationNOR import *
np.random.seed(0)
from lmtanalysis import BuildEventObjectSniffingNorAcquisitionWithConfig, BuildEventObjectSniffingNorTestWithConfig
from scripts.ComputeObjectRecognition import *


def plotTrajectoriesNorPhasesPerGeno(files, figName, organisation, objectConfig, title, phase, exp, colorObjects,
                              objectPosition, radiusObjects ):
    
    
    nbRowFig = 1 + len(files) // 5
    fig, axes = plt.subplots(nrows=nbRowFig, ncols=5, figsize=(14, 3*nbRowFig))  # building the plot for trajectories

    nRow = 0  # initialisation of the row
    nCol = 0  # initialisation of the column

    for file in files:
        connection = sqlite3.connect(file)  # connection to the database
        pool = AnimalPool()
        pool.loadAnimals(connection)  # upload all the animals from the database
        animal = pool.animalDictionnary[1]
        geno = animal.genotype
        rfid = animal.RFID
        setup = animal.setup
        print('setup: ', setup)
        configName = organisation[exp][rfid]

        config = getConfigCat(rfid, exp, organisation)

        if phase == 'acquisition':
            tmin = getStartTestPhase(pool)
            '''tmin = 0'''
        else:
            tmin = 0
        tmax = tmin + 10 * oneMinute

        # set the axes. Check the number of files to get the dimension of axes and grab the correct ones.
        ax = axes[nRow][nCol]  # set the subplot where to draw the plot
        plotTrajectorySingleAnimal(file, color='black', colorTitle=getColorGeno(geno), ax=ax, tmin=tmin,
                                   tmax=tmax, title='{} ({})'.format(title, config[-1:]), xa=128, xb=383, ya=80,
                                   yb=336)  # function to draw the trajectory

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
            if '1' in configName:
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

        connection.close()

    fig.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
    # plt.show() #display the plot
    fig.savefig('{}.pdf'.format(figName), dpi=200)
    fig.savefig('{}.jpg'.format(figName), dpi=200)



def computeSniffTimePerGeno(files=None, tmin=None, phase=None):
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
            for sex in ['male', 'female']:
                data[val][event][sex] = {}
                for geno in genoList:
                    data[val][event][sex][geno] = {}

    for ratio in ['ratio', 'ratioFar']:
        data[ratio] = {}
        for phaseType in ['acquisition', 'test']:
            data[ratio][phaseType] = {}
            for sex in sexList:
                data[ratio][phaseType][sex] = {}
                for geno in genoList:
                    data[ratio][phaseType][sex][geno] = {}


    for file in files:
        connection = sqlite3.connect(file)
        pool = AnimalPool()
        pool.loadAnimals(connection)
        animal = pool.animalDictionnary[1]
        sex = animal.sex
        setup = animal.setup
        rfid = animal.RFID
        genotype = animal.genotype
        config = getConfigCat(rfid, exp, organisation)

        if tmin==None:
            tmin = getStartTestPhase(pool=pool)
        tmax = tmin + 10*oneMinute

        for eventType in eventList:
            # upload event timeline:
            eventTypeTimeLine = EventTimeLine(connection, eventType, minFrame=tmin, maxFrame=tmax)
            nbEvent = eventTypeTimeLine.getNbEvent()
            if nbEvent != 0:
                meanEventLength = eventTypeTimeLine.getMeanEventLength() / oneSecond
                totalDuration = eventTypeTimeLine.getTotalLength() / oneSecond
            elif nbEvent == 0:
                meanEventLength = 0
                totalDuration = 0
            print('###############total duration: ', eventType, totalDuration)
            data['nbEvent'][eventType][sex][genotype][rfid] = nbEvent
            data['meanEventLength'][eventType][sex][genotype][rfid] = meanEventLength
            data['totalDuration'][eventType][sex][genotype][rfid] = totalDuration

        if phase == 'acquisition':
            try:
                data['ratio'][phase][sex][genotype][rfid] = data['totalDuration']['SniffRight'][sex][genotype][rfid] / (
                            data['totalDuration']['SniffRight'][sex][genotype][rfid] +
                            data['totalDuration']['SniffLeft'][sex][genotype][rfid])
            except:
                data['ratio'][phase][sex][genotype][rfid] = None

            try:
                data['ratioFar'][phase][sex][genotype][rfid] = data['totalDuration']['SniffRightFar'][sex][genotype][
                                                                rfid] / (data['totalDuration']['SniffRightFar'][sex][genotype][rfid] +
                                                                         data['totalDuration']['SniffLeftFar'][sex][genotype][rfid])
            except:
                data['ratioFar'][phase][sex][genotype][rfid] = None

        if phase == 'test':
            try:
                data['ratio'][phase][sex][genotype][rfid] = data['totalDuration']['SniffNew'][sex][genotype][rfid] / (
                            data['totalDuration']['SniffNew'][sex][genotype][rfid] +
                            data['totalDuration']['SniffFamiliar'][sex][genotype][rfid])
            except:
                data['ratio'][phase][sex][genotype][rfid] = None
            try:
                data['ratioFar'][phase][sex][genotype][rfid] = data['totalDuration']['SniffNewFar'][sex][genotype][rfid] / (data['totalDuration']['SniffNewFar'][sex][genotype][rfid] + data['totalDuration']['SniffFamiliarFar'][sex][genotype][rfid])
            except:
                data['ratioFar'][phase][sex][genotype][rfid] = None
        connection.close()

    return data


def computeSniffTimePerTimeBinPerGeno(files=None, sexList=sexList, genoList = genoList, tmin=None, phase=None, timeBin=1*oneMinute):
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
            for sex in sexList:
                data[val][event][sex] = {}
                for geno in genoList:
                    data[val][event][sex][geno] = {}

    for file in files:
        connection = sqlite3.connect(file)
        pool = AnimalPool()
        pool.loadAnimals(connection)
        animal = pool.animalDictionnary[1]
        sex = animal.sex
        rfid = animal.RFID
        geno = animal.genotype

        if tmin==None:
            tmin = getStartTestPhase(pool=pool)
        tmax = tmin + 10*oneMinute
        #print('tmin-tmax: ', tmin, tmax)

        for eventType in eventList:
            data['durationPerTimeBin'][eventType][sex][geno][rfid] = []
            data['cumulPerTimeBin'][eventType][sex][geno][rfid] = []

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
                data['durationPerTimeBin'][eventType][sex][geno][rfid].append( durInTimeBin )
                minT = minT + timeBin

            totalDuration = sum(data['durationPerTimeBin'][eventType][sex][geno][rfid])
            totalLength = eventTypeTimeLine.getTotalDurationEvent(tmin = tmin, tmax = tmin+10*oneMinute)
            print('verif total duration: ', totalDuration, totalLength)
            previousTime = 0
            for i in data['durationPerTimeBin'][eventType][sex][geno][rfid]:
                if totalDuration != 0:
                    propCumul = (previousTime + i) / totalDuration
                elif totalDuration == 0:
                    propCumul = 0
                data['cumulPerTimeBin'][eventType][sex][geno][rfid].append( propCumul )
                previousTime = previousTime + i


        #Compute ratio based on cumulated time per time bin
        eventType = 'ratio'
        data['ratioCumulPerTimeBin']['ratio'][sex][geno][rfid] = []
        data['ratioFarCumulPerTimeBin']['ratioFar'][sex][geno][rfid] = []
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
            data['ratioCumulPerTimeBin']['ratio'][sex][geno][rfid].append( ratioNew )

            # Ratio with extended contact zone:
            durSniffNewFarInTimeBin = sniffNewFarTimeLine.getTotalDurationEvent(tmin=minT, tmax=maxT)
            durSniffNewFar += durSniffNewFarInTimeBin
            durSniffFamiliarFarInTimeBin = sniffFamiliarFarTimeLine.getTotalDurationEvent(tmin=minT, tmax=maxT)
            durSniffFamiliarFar += durSniffFamiliarFarInTimeBin
            if durSniffNewFar + durSniffFamiliarFar == 0:
                ratioNewFar = 0
            else:
                ratioNewFar = durSniffNewFar / (durSniffNewFar + durSniffFamiliarFar)
            data['ratioFarCumulPerTimeBin']['ratioFar'][sex][geno][rfid].append(ratioNewFar)
            print('Verif: close: {} {}; far: {} {}'.format(durSniffNew, durSniffNewInTimeBin, durSniffNewFar, durSniffNewFarInTimeBin))
            #update timebin limits
            minT = minT + timeBin

        connection.close()

    return data


def getCumulDataSniffingPerTimeBinPerGeno(val, data, genoList, eventList, sex):
    K = [i for i in range(10)]
    resultDic = {}
    for event in eventList:
        resultDic[event] = {}
        for geno in genoList:
            resultDic[event][geno] = {}
            for k in K:
                resultDic[event][geno][k] = []

    for event in eventList:
        for geno in genoList:
            for k in K:
                for rfid in data[val][event][sex][geno].keys():
                    resultDic[event][geno][k].append(data[val][event][sex][geno][rfid][k])

    return resultDic


def plotCumulTimeSniffingPerGeno(ax, genoList, ylabel, title, event, resultDic, timeBin):
    K = [i for i in range(10)]

    yMean = {event: {}}
    yError = {event: {}}
    for geno in genoList:
        yMean[event][geno] = {}
        yError[event][geno] = {}

    for geno in genoList:
        yMean[event][geno] = []
        yError[event][geno] = []
        for k in K:
            yMean[event][geno].append(np.mean(resultDic[event][geno][k]))
            yError[event][geno].append(np.std(resultDic[event][geno][k]))

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

    xList = {genoList[0]: [i+0.3 for i in K], genoList[1]: [i+0.6 for i in K]}
    starPos = [i+0.45 for i in K]

    for geno in genoList:
        ax.errorbar(x=xList[geno], y=yMean[event][geno], yerr=yError[event][geno], fmt='o',
                    ecolor=getColorGeno(geno), markerfacecolor=getColorGeno(geno), markeredgecolor=getColorGeno(geno))

    for k in K[:-1]:
        print(genoList[0], resultDic[event][genoList[0]][k])
        print(genoList[1], resultDic[event][genoList[1]][k])
        W, p = stats.mannwhitneyu(resultDic[event][genoList[0]][k], resultDic[event][genoList[1]][k])
        ax.text(x=starPos[k], y=1.05, s=getStarsFromPvalues(p, 1), ha='center')


def plotTotalTimeSniffingPerGeno(ax, genoList, phase, totalSniffList, sex):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    xIndex = [1, 2]
    ax.set_xticks(xIndex)
    ax.set_xticklabels(genoList, rotation=45, fontsize=12, horizontalalignment='right')
    ax.set_ylabel('total time spent sniffing objects (s)', fontsize=13)
    ax.legend().set_visible(False)
    ax.xaxis.set_tick_params(direction="in")
    ax.set_title(phase, fontsize=14)
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 160)
    ax.tick_params(axis='y', labelsize=14)

    xPos = {genoList[0]: 1, genoList[1]: 2}

    # plot the points for each value:
    for geno in genoList:
        ax.scatter(addJitter([xPos[geno]] * len(totalSniffList[phase][sex][geno]), 0.2),
                   totalSniffList[phase][sex][geno], color=getColorGeno(geno), marker=markerListSex[sex],
                   alpha=0.8, label="on", s=8)
        ax.errorbar(x=xPos[geno], y=np.mean(totalSniffList[phase][sex][geno]), yerr=np.std(totalSniffList[phase][sex][geno]), fmt='o', ecolor='black', markerfacecolor='black', markeredgecolor='black')

    # conduct statistical testing: Wilcoxon paired test:
    st1 = totalSniffList[phase][sex][genoList[0]]
    st2 = totalSniffList[phase][sex][genoList[1]]
    print(st1)
    print(st2)
    U, p = stats.mannwhitneyu(st1, st2)
    print(
        'Mann-Whitney U test for {} versus {} {}: U={}, p={}'.format(len(st1), len(st2), sex, U, p))
    ax.text((xPos[genoList[0]] + xPos[genoList[1]]) / 2, 160 * 0.90,
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
        question += "\n\t [4] plot trajectories in the habituation phase?"
        question += "\n\t [5] plot trajectories in the acquisition phase (same objects)?"
        question += "\n\t [6] plot trajectories in the test phase (different objects)?"
        question += "\n\t [7] plot ratio for sniffing?"
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
            question1 = "Is it the short, medium or long retention time? (short / medium / long)"
            exp = input(question1)
            question2 = "Is it the acquisition or test phase? (acquisition / test)"
            phase = input(question2)
            files = getFilesToProcess()
            rfidList = []
            print('##############', organisation[exp])

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
                rfidList.append(rfid)
                age = animal.age
                config = organisation[exp][rfid]
                infoList = [file, rfid, sex, geno, age, setup, phase, config]
                for info in infoList:
                    text_file.write("{}\t".format(info))
                text_file.write("\n")
                connection.close()

            text_file.write("\n")
            text_file.close()
            print(rfidList)
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
            yLim = {'nbEvent': 120, 'meanEventLength': 10, 'totalDuration': 100, 'ratio': 1.2}

            figName = 'fig_timeline_nor_{}_{}.pdf'.format(exp, phase)
            fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14, 8))  # building the plot for timelines

            nRow = {'male': {genoList[0]: 0, genoList[1]: 1}, 'female': {genoList[0]: 0, genoList[1]: 1}}  # initialisation of the row
            nCol = {'male': {genoList[0]: 0, genoList[1]: 0}, 'female': {genoList[0]: 1, genoList[1]: 1}}  # initialisation of the column
            line = {}
            for sex in sexList:
                line[sex] = {}
                for geno in genoList:
                    line[sex][geno] = 1

            for col in [0, 1]:
                for row in [0, 1]:
                    ax = axes[row][col]
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['left'].set_visible(False)
                    ax.set_title('{} {}'.format(genoList[row], sexList[col]), fontsize=18)
                    print('############', genoList[row], sexList[col])
                    ax.legend().set_visible(False)
                    ax.xaxis.set_tick_params(direction="in")
                    ax.get_yaxis().set_visible(False)
                    ax.set_xlim(0, 14400)
                    ax.set_ylim(0, 34)

            measureData = {}
            for var in ['nbEvent', 'meanEventLength', 'totalDuration', 'ratio']:
                measureData[var] = {}
                for eventType in eventList[phase]:
                    measureData[var][eventType] = {}
                    for sex in sexList:
                        measureData[var][eventType][sex] = {}
                        for geno in genoList:
                            measureData[var][eventType][sex][geno] = []


            for file in files:
                print(file)
                connection = sqlite3.connect(file)
                pool = AnimalPool()
                pool.loadAnimals(connection)
                animal = pool.animalDictionnary[1]
                sex = animal.sex
                geno = animal.genotype
                setup = animal.setup
                rfid = animal.RFID
                configName = organisation[exp][rfid]
                config = getConfigCat(rfid, exp, organisation)
                # determine the start frame:
                if phase == 'acquisition':
                    tmin = getStartTestPhase(pool)
                elif phase == 'test':
                    tmin = 0
                # determine the end of the computation
                tmax = tmin + 10 * oneMinute

                ax = axes[nRow[sex][geno]][nCol[sex][geno]]
                ax.text(-20, line[sex][geno] - 0.5, s=animal.RFID[-4:], fontsize=10, horizontalalignment='right')
                # compute the coordinates for the drawing:
                lineData = {}
                for eventType in eventList[phase]:
                    # upload event timeline:
                    eventTypeTimeLine = EventTimeLine(connection, eventType, idA=1, minFrame=tmin, maxFrame=tmax)
                    nbEvent = eventTypeTimeLine.getNbEvent()
                    meanEventLength = eventTypeTimeLine.getMeanEventLength()
                    totalDuration = eventTypeTimeLine.getTotalLength()
                    measureData['nbEvent'][eventType][sex][geno].append(nbEvent)
                    try:
                        measureData['meanEventLength'][eventType][sex][geno].append(meanEventLength/oneSecond)
                    except:
                        measureData['meanEventLength'][eventType][sex][geno].append(None)
                    measureData['totalDuration'][eventType][sex][geno].append(totalDuration/oneSecond)

                    lineData[eventType] = []
                    for event in eventTypeTimeLine.eventList:
                        lineData[eventType].append(
                            (event.startFrame - tmin - addThickness, event.duration() + addThickness))

                    ax.broken_barh(lineData[eventType], (line[sex][geno] - 1, 1), facecolors=colorEvent[eventType])
                    print('plot for ', animal.RFID)
                    print('line: ', line[sex][geno])

                if phase == 'acquisition':
                    eventA = 'SniffRight'
                    eventB = 'SniffLeft'
                    eventAFar = 'SniffRightFar'
                    eventBFar = 'SniffLeftFar'
                elif phase == 'test':
                    eventB = 'SniffFamiliar'
                    eventA = 'SniffNew'
                    eventBFar = 'SniffFamiliarFar'
                    eventAFar = 'SniffNewFar'

                sniffATimeLine = EventTimeLine(connection, eventA, idA=1, minFrame=tmin, maxFrame=tmax)
                totalDurationA = sniffATimeLine.getTotalLength()
                sniffBTimeLine = EventTimeLine(connection, eventB, idA=1, minFrame=tmin, maxFrame=tmax)
                totalDurationB = sniffBTimeLine.getTotalLength()
                sniffAFarTimeLine = EventTimeLine(connection, eventAFar, idA=1, minFrame=tmin, maxFrame=tmax)
                totalDurationAFar = sniffAFarTimeLine.getTotalLength()
                sniffBFarTimeLine = EventTimeLine(connection, eventBFar, idA=1, minFrame=tmin, maxFrame=tmax)
                totalDurationBFar = sniffBFarTimeLine.getTotalLength()

                if phase == 'acquisition':
                    measureData['ratio']['SniffRight'][sex][geno].append(
                        totalDurationA / (totalDurationA + totalDurationB))
                    measureData['ratio']['SniffRightFar'][sex][geno].append(
                        totalDurationAFar / (totalDurationAFar + totalDurationBFar))



                elif phase == 'test':
                    measureData['ratio']['SniffNew'][sex][geno].append(
                        totalDurationA / (totalDurationA + totalDurationB))
                    measureData['ratio']['SniffNewFar'][sex][geno].append(
                    totalDurationAFar / (totalDurationAFar + totalDurationBFar))

                line[sex][geno] += 1.5
                connection.close()

            fig.show()
            fig.savefig(figName, dpi=300)

            print('################################################')

            figName = 'fig_measures_events_{}_{}.pdf'.format(exp, phase)
            figMeasures, axesMeasures = plt.subplots(nrows=1, ncols=4, figsize=(24, 4))
            col = 0
            for var in ['nbEvent', 'meanEventLength', 'totalDuration']:
                ax = axesMeasures[col]
                yLabel = var
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                xIndex = [1, 2, 4, 5, 7, 8, 10, 11]
                ax.set_xticks(xIndex)
                if phase == 'acquisition':
                    ax.set_xticklabels(['left', 'right', 'left', 'right', 'left', 'right', 'left', 'right'], rotation=45,
                                       fontsize=12, horizontalalignment='right')
                elif phase == 'test':
                    ax.set_xticklabels(['familiar', 'new', 'familiar', 'new', 'familiar', 'new', 'familiar', 'new'], rotation=45,
                                       fontsize=12, horizontalalignment='right')

                ax.set_ylabel(yLabel, fontsize=15)
                ax.legend().set_visible(False)
                ax.xaxis.set_tick_params(direction="in")
                ax.set_xlim(0, 12)
                ax.set_ylim(0, yLim[var])
                ax.tick_params(axis='y', labelsize=14)
                ax.text(1.5, yLim[var], s='{} {}'.format(genoList[0], sexList[0]), fontsize=14, horizontalalignment='center')
                ax.text(4.5, yLim[var], s='{} {}'.format(genoList[1], sexList[0]), fontsize=14, horizontalalignment='center')
                ax.text(7.5, yLim[var], s='{} {}'.format(genoList[0], sexList[1]), fontsize=14, horizontalalignment='center')
                ax.text(10.5, yLim[var], s='{} {}'.format(genoList[1], sexList[1]), fontsize=14, horizontalalignment='center')

                # plot the points for each value:
                i = 0

                if phase == 'acquisition':
                    selectedSniffEventList = ['SniffLeft', 'SniffRight']
                elif phase == 'test':
                    selectedSniffEventList = ['SniffFamiliar', 'SniffNew']

                for sex in sexList:
                    for geno in genoList:
                        for eventSniff in selectedSniffEventList:
                            ax.scatter(addJitter([xIndex[i]] * len(measureData[var][eventSniff][sex][geno]), 0.2),
                                               measureData[var][eventSniff][sex][geno], color=getColorGeno(geno),
                                               marker=markerListSex[sex], alpha=0.8, label="on", s=8)
                            i += 1
                col += 1

            for var in ['ratio']:
                ax = axesMeasures[col]
                yLabel = var
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                xIndex = [1, 2, 4,5, 7,8, 10,11]
                ax.set_xticks(xIndex)
                if phase == 'acquisition':
                    ax.set_xticklabels(['close', 'far', 'close', 'far', 'close', 'far', 'close', 'far'], rotation=45, fontsize=12, horizontalalignment='right')
                elif phase == 'test':
                    ax.set_xticklabels(['new close', 'new far', 'new close', 'new far', 'new close', 'new far', 'new close', 'new far'], rotation=45, fontsize=12, horizontalalignment='right')

                ax.set_ylabel(yLabel, fontsize=15)
                ax.legend().set_visible(False)
                ax.xaxis.set_tick_params(direction="in")
                ax.set_xlim(0, 12)
                ax.set_ylim(0, yLim[var])
                ax.tick_params(axis='y', labelsize=14)
                ax.text(1.5, yLim[var], s='{} {}'.format(genoList[0], sexList[0]), fontsize=14,
                        horizontalalignment='center')
                ax.text(4.5, yLim[var], s='{} {}'.format(genoList[1], sexList[0]), fontsize=14,
                        horizontalalignment='center')
                ax.text(7.5, yLim[var], s='{} {}'.format(genoList[0], sexList[1]), fontsize=14,
                        horizontalalignment='center')
                ax.text(10.5, yLim[var], s='{} {}'.format(genoList[1], sexList[1]), fontsize=14,
                        horizontalalignment='center')

                ax.hlines(0.5, xmin=0, xmax=12, colors='grey', linestyles='dashed')

                # plot the points for each value:
                i = 0
                if phase == 'acquisition':
                    selectedSniffEventList = ['SniffRight', 'SniffRightFar']
                elif phase == 'test':
                    selectedSniffEventList = ['SniffNew', 'SniffNewFar']

                for sex in sexList:
                    for geno in genoList:
                        for eventSniff in selectedSniffEventList:
                            ax.scatter(addJitter([xIndex[i]] * len(measureData[var][eventSniff][sex][geno]), 0.2),
                                       measureData[var][eventSniff][sex][geno], color=getColorGeno(geno),
                                       marker=markerListSex[sex], alpha=0.8, label="on", s=8)
                            prop = measureData[var][eventSniff][sex][geno]
                            T, p = stats.ttest_1samp(a=prop, popmean=0.5, nan_policy='omit')
                            print( 'One-sample Student T-test for {} acquisition {} {} {}: T={}, p={}'.format(exp, len(prop), sex, geno, T, p))
                            ax.text(xIndex[i], 1.1, getStarsFromPvalues(pvalue=p, numberOfTests=1), fontsize=14)

                            i += 1


            figMeasures.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
            figMeasures.show()  # display the plot
            figMeasures.savefig(figName, dpi=200)

            print('Job done.')
            break



        if answer == '4':
            print('Plot trajectory in the habituation phase')
            #distance travelled
            #space use
            #traj of center of mass
            files = getFilesToProcess()
            buildFigTrajectoryMalesFemales(files=files, title='hab', tmin=0, tmax=15*oneMinute, figName='fig_traj_hab_long_nor', colorSap=colorSap, xa=128, xb=383, ya=80, yb=336)
            print('Job done.')
            break

        if answer == '5':
            print('Plot trajectory during the acquisition phase.')
            question = "Is it the short, medium or long retention time? (short / medium / long)"
            exp = input(question)
            phase = 'acquisition'

            timeSniff = {}
            files = getFilesToProcess()
            figName = 'fig_traj_nor_{}_same'.format(exp)
            plotTrajectoriesNorPhasesPerGeno(files=files, figName=figName, organisation=organisation, objectConfig=objectConfig, title=phase, phase=phase, exp=exp, colorObjects=colorObjects, objectPosition=objectPosition, radiusObjects=radiusObjects)

            data = computeSniffTimePerGeno(files, tmin=0, phase=phase)

            # store the data dictionary in a json file
            with open('sniff_time_same_{}.json'.format(exp), 'w') as jFile:
                json.dump(data, jFile, indent=4)
            print("json file created")

            break

        if answer == '6':
            print('Plot trajectory in the test phase')
            question = "Is it the short, medium or long retention time? (short / medium / long)"
            exp = input(question)
            phase = 'test'
            #distance travelled
            #space use
            #traj of center of mass
            files = getFilesToProcess()
            figName = 'fig_traj_nor_{}_test'.format(exp)
            plotTrajectoriesNorPhasesPerGeno(files=files, figName=figName, organisation=organisation, objectConfig=objectConfig, title=phase, phase=phase, exp=exp, colorObjects=colorObjects, objectPosition=objectPosition, radiusObjects=radiusObjects)

            data = computeSniffTimePerGeno(files, tmin=0, phase=phase)

            # store the data dictionary in a json file
            with open('sniff_time_test_{}.json'.format(exp), 'w') as jFile:
                json.dump(data, jFile, indent=4)
            print("json file created")

            break

        if answer == '7':
            '''Plot ratio for sniffing'''
            # open the json files
            question = "Is it the short, medium or long retention time? (short / medium / long)"
            exp = input(question)

            jsonFileName = "sniff_time_same_{}.json".format(exp)
            with open(jsonFileName) as json_data:
                dataSame = json.load(json_data)
            jsonFileName = "sniff_time_test_{}.json".format(exp)
            with open(jsonFileName) as json_data:
                dataTest = json.load(json_data)
            print("json file re-imported.")
            print(dataSame)

            # reformate the data dictionary to get the correct format of data for plotting and statistical analyses

            xPos = {genoList[0]: 1, genoList[1]: 2}
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
                    for sex in sexList:
                        data[val][sex] = {}
                        for geno in genoList:
                            data[val][sex][geno] = []
                            for rfid in dataToAnalyse['ratio'][phase][sex][geno].keys():
                                if (dataToAnalyse['totalDuration'][event1[phase]][sex][geno][rfid] >= 3) & (
                                        dataToAnalyse['totalDuration'][event2[phase]][sex][geno][rfid] >= 3):
                                    data[val][sex][geno].append(dataToAnalyse['ratio'][phase][sex][geno][rfid])

                                else:
                                    print('Too Short exploration time in config {} for {} {}'.format(sex, geno, rfid))

                print(data)

                fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))  # create the figure for the graphs of the computation

                col = 0  # initialise the column number

                for sex in sexList:
                    ax = axes[col]
                    yLabel = 'ratio sniff time'
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    xIndex = [1, 2]
                    ax.set_xticks(xIndex)
                    ax.set_xticklabels(genoList, rotation=45, fontsize=12, horizontalalignment='right')
                    ax.set_ylabel(yLabel, fontsize=15)
                    ax.set_title(sex, fontsize=15)
                    ax.legend().set_visible(False)
                    ax.xaxis.set_tick_params(direction="in")
                    ax.set_xlim(0, 3)
                    ax.set_ylim(0, 1.2)
                    ax.tick_params(axis='y', labelsize=14)
                    #ax.text(1, 1.2, s='transparent', fontsize=16, horizontalalignment='center')
                    #ax.text(2, 1.2, s='red', fontsize=16, horizontalalignment='center')
                    ax.hlines(0.5, xmin = 0, xmax=12, colors='grey', linestyles='dashed')

                    for geno in genoList:
                        ax.scatter(addJitter([xPos[geno]] * len(data['ratio'][sex][geno]), 0.2),
                               data['ratio'][sex][geno], color=getColorGeno(geno), marker=markerListSex[sex], alpha=0.8, label="on", s=8)
                        prop = data['ratio'][sex][geno]
                        T, p = stats.ttest_1samp(a=prop, popmean=0.5, nan_policy='omit')
                        print('One-sample Student T-test for {} {} {} {} {}: T={}, p={}'.format(exp, phase, len(prop), sex, geno, T, p))
                        ax.text(xPos[geno], 1.1, getStarsFromPvalues(pvalue=p, numberOfTests=1), fontsize=16, horizontalalignment='center')

                    col += 1

                fig.tight_layout()
                fig.show()

                fig.savefig('fig_ratio_geno_{}_{}.pdf'.format(exp, phase), dpi=200)
                fig.savefig('fig_ratio_geno_{}_{}.jpg'.format(exp, phase), dpi=200)

            print('Job done.')
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

            data = computeSniffTimePerTimeBinPerGeno(files, sexList=sexList, genoList=genoList, tmin=tmin[phase], phase=phase, timeBin=timeBin)

            # store the data dictionary in a json file
            with open('sniff_time_timebin_geno_{}_{}.json'.format(phase, exp), 'w') as jFile:
                json.dump(data, jFile, indent=4)
            print("json file created")

            break


        if answer == '10':
            #compute cumulated proportion of time sniffing
            # open the json files
            question = "Is it the short, medium or long retention time? (short / medium / long)"
            exp = input(question)

            jsonFileName = "sniff_time_timebin_geno_acquisition_{}.json".format(exp)
            with open(jsonFileName) as json_data:
                dataSame = json.load(json_data)
            jsonFileName = "sniff_time_timebin_geno_test_{}.json".format(exp)
            with open(jsonFileName) as json_data:
                dataTest = json.load(json_data)
            print("json files re-imported.")

            val = 'cumulPerTimeBin'
            eventSame = ['SniffLeftFar', 'SniffRightFar']
            eventTest = ['SniffFamiliarFar', 'SniffNewFar']

            #for sex in sexList:
            for sex in ['female']:
                for eventList in [eventSame, eventTest]:
                    if eventList == eventSame:
                        data = dataSame
                        nameFig = 'acquisition'
                    elif eventList == eventTest:
                        data = dataTest
                        nameFig = 'test'

                    resultDic = getCumulDataSniffingPerTimeBinPerGeno(val = val, data = data, genoList = genoList, eventList = eventList, sex = sex)

                    #plot for learning phase
                    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))  # create the figure for the graphs of the computation

                    ax = axes[0]
                    plotCumulTimeSniffingPerGeno(ax, genoList=genoList, title=nameFig, ylabel='cumul. prop. sniffing (mean+-sd)', resultDic=resultDic, event=eventList[0], timeBin=timeBin)

                    ax = axes[1]
                    plotCumulTimeSniffingPerGeno(ax, genoList=genoList, title=nameFig, ylabel='cumul. prop. sniffing (mean+-sd)', resultDic=resultDic, event=eventList[1], timeBin=timeBin)

                    fig.tight_layout()
                    fig.show()
                    fig.savefig('fig_cumul_timebin_geno_{}_{}_{}.pdf'.format(exp, nameFig, sex), dpi=300)
                    fig.savefig('fig_cumul_timebin_geno_{}_{}_{}.jpg'.format(exp, nameFig, sex), dpi=300)

            print('Job done.')
            break


        if answer == '11':
            #plot ratio based on cumulated time per time bin only in the test phase
            #open the json files
            question = "Is it the short, medium or long retention time? (short / medium / long)"
            exp = input(question)

            jsonFileName = "sniff_time_timebin_geno_test_{}.json".format(exp)
            with open(jsonFileName) as json_data:
                dataTest = json.load(json_data)
            print("json files re-imported.")

            data = dataTest
            #for sex in sexList:
            for sex in ['female']:
                #plot for test phase
                fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))  # create the figure for the graphs of the computation

                ax = axes[0]
                val = 'ratioCumulPerTimeBin'
                resultDic = getCumulDataSniffingPerTimeBinPerGeno(val=val, data=data, genoList=genoList, eventList=['ratio'], sex=sex)
                plotCumulTimeSniffingPerGeno(ax, genoList=genoList, title='(restricted zone)', ylabel='ratio based on cumulative time', resultDic=resultDic, event='ratio', timeBin=timeBin)
                ax.hlines(y=0.5, xmin=0, xmax=10, colors='grey', linestyles='dashed')

                ax = axes[1]
                val = 'ratioFarCumulPerTimeBin'
                resultDic = getCumulDataSniffingPerTimeBinPerGeno(val=val, genoList=genoList, data=data, eventList=['ratioFar'], sex=sex)
                plotCumulTimeSniffingPerGeno(ax, genoList=genoList, title='(extended zone)', ylabel='ratio based on cumulative time', resultDic=resultDic, event='ratioFar', timeBin=timeBin)
                ax.hlines(y=0.5, xmin=0, xmax=10, colors='grey', linestyles='dashed')

                fig.tight_layout()
                fig.show()
                fig.savefig('fig_cumul_ratio_timebin_geno_{}_{}.pdf'.format(exp, sex), dpi=300)
                fig.savefig('fig_cumul_ratio_timebin_geno_{}_{}.jpg'.format(exp, sex), dpi=300)

            print('Job done.')
            break


        if answer == '12':
            print('compare sniff time between the two genotypes')
            eventList = {'acquisition': ['SniffLeft', 'SniffRight', 'UpLeft', 'UpRight'],
                         'test': ['SniffFamiliar', 'SniffNew', 'UpFamiliar', 'UpNew']}

            event1 = {'acquisition': eventList['acquisition'][0], 'test': eventList['test'][0]}
            event2 = {'acquisition': eventList['acquisition'][1], 'test': eventList['test'][1]}
            #expList = ['short', 'medium']
            expList = ['long']

            # open the json files
            for exp in expList:
                jsonFileName = "sniff_time_same_{}.json".format(exp)
                with open(jsonFileName) as json_data:
                    dataSame = json.load(json_data)
                jsonFileName = "sniff_time_test_{}.json".format(exp)
                with open(jsonFileName) as json_data:
                    dataTest = json.load(json_data)
                print("json file re-imported.")

                totalSniffTime = {}
                for phase in ['acquisition', 'test']:
                    totalSniffTime[phase] = {}
                    for sex in sexList:
                        totalSniffTime[phase][sex] = {}
                        for geno in genoList:
                            totalSniffTime[phase][sex][geno] = {}

                for sex in sexList:
                    #compute total duration of sniffing objects in the acquisition phase
                    phase = 'acquisition'
                    dataToAnalyse = dataSame
                    for geno in genoList:
                        for rfid in dataToAnalyse['totalDuration'][event1[phase]][sex][geno].keys():
                            totalSniffTime[phase][sex][geno][rfid] = dataToAnalyse['totalDuration'][event1[phase]][sex][geno][rfid] + dataToAnalyse['totalDuration'][event2[phase]][sex][geno][rfid]

                    # compute total duration of sniffing objects in the test phase
                    phase = 'test'
                    dataToAnalyse = dataTest
                    for geno in genoList:
                        for rfid in dataToAnalyse['totalDuration'][event1[phase]][sex][geno].keys():
                            totalSniffTime[phase][sex][geno][rfid] = \
                            dataToAnalyse['totalDuration'][event1[phase]][sex][geno][rfid] + \
                            dataToAnalyse['totalDuration'][event2[phase]][sex][geno][rfid]

                    totalSniffList = {}
                    for phase in ['acquisition', 'test']:
                        totalSniffList[phase] = {sex: {}}
                        for geno in genoList:
                            totalSniffList[phase][sex][geno] = []
                            for rfid in totalSniffTime[phase][sex][geno].keys():
                                totalSniffList[phase][sex][geno].append(totalSniffTime[phase][sex][geno][rfid])

                    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))  # create the figure for the graphs of the computation

                    phase = 'acquisition'
                    ax = axes[0]
                    plotTotalTimeSniffingPerGeno(ax=ax, genoList=genoList, sex=sex, phase=phase, totalSniffList=totalSniffList)

                    phase = 'test'
                    ax = axes[1]
                    plotTotalTimeSniffingPerGeno(ax=ax, genoList=genoList, sex=sex, phase=phase, totalSniffList=totalSniffList)

                    fig.tight_layout()
                    fig.show()
                    fig.savefig('fig_total_sniff_time_geno_{}_close_{}.pdf'.format(exp, sex), dpi=300)
                    fig.savefig('fig_total_sniff_time_geno_{}_close_{}.jpg'.format(exp, sex), dpi=300)

            print('Job done.')
            break




