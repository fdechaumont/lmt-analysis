'''
#Created on 16 December 2020

#@author: Elodie
'''

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
from lmtanalysis import BuildEventObjectSniffingNor
from lmtanalysis.Event import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached


def getStartTestPhase(pool):
    cursor = pool.conn.cursor()
    query = "SELECT FRAMENUMBER, PAUSED FROM FRAME"
    try:
        cursor.execute(query)
    except:
        print("can't access data for PAUSED")

    rows = cursor.fetchall()
    cursor.close()

    frameNumberList = []

    for row in rows:
        pauseValue = row[1]
        if pauseValue == 1:
            frameNumberList.append(row[0])
    sortedFrameList = sorted(frameNumberList)

    lastPausedFrame = sortedFrameList[-1]
    startFrameTestPhase = lastPausedFrame + 1
    return startFrameTestPhase

def plotObjectZone(ax, colorFill, x, y, radius, alpha):
    circle1 = plt.Circle((x, y), radius, color=colorFill, alpha = alpha)
    ax.add_artist(circle1)


def plotTrajectoriesNorPhases(files, figName, title, phase, exp, colorSap, objectDic, colorObjects,
                              objectPosition, radiusObjects, xa=111, xb=400, ya=63, yb=353):
    figM, axesM = plt.subplots(nrows=6, ncols=5, figsize=(14, 20))  # building the plot for trajectories
    figF, axesF = plt.subplots(nrows=8, ncols=5, figsize=(14, 25))  # building the plot for trajectories

    nRow = {'male': 0, 'female': 0}  # initialisation of the row
    nCol = {'male': 0, 'female': 0}  # initialisation of the column

    for file in files:
        connection = sqlite3.connect(file)  # connection to the database

        pool = AnimalPool()
        pool.loadAnimals(connection)  # upload all the animals from the database
        animal = pool.animalDictionnary[1]
        setup = float(animal.setup)
        print('setup: ', setup)

        if phase == 'learning':
            tmin = getStartTestPhase(pool)
        else:
            tmin = 0
        tmax = tmin + 10 * oneMinute

        if animal.sex == 'male':
            # set the axes. Check the number of file to get the dimension of axes and grab the correct ones.
            ax = axesM[nRow['male']][nCol['male']]  # set the subplot where to draw the plot
            plotTrajectorySingleAnimal(file, color=colorSap[animal.genotype], ax=ax, tmin=tmin,
                                       tmax=tmax, title=title, xa=128, xb=383, ya=80,
                                       yb=336)  # function to draw the trajectory
            object = objectDic[setup][exp][phase][1]
            plotObjectZone(ax=ax, colorFill=colorObjects[object], x=objectPosition[setup]['right'][0],
                           y=objectPosition[setup]['right'][1], radius=radiusObjects[object],
                           alpha=0.5)  # plot the object on the right side
            object = objectDic[setup][exp][phase][0]
            plotObjectZone(ax=ax, colorFill=colorObjects[object], x=objectPosition[setup]['left'][0],
                           y=objectPosition[setup]['left'][1], radius=radiusObjects[object],
                           alpha=0.5)  # plot the object on the left side
            object = objectDic[setup][exp][phase][1]
            plotObjectZone(ax=ax, colorFill=colorObjects[object], x=objectPosition[setup]['right'][0],
                           y=objectPosition[setup]['right'][1], radius=radiusObjects[object] + vibrissae / scaleFactor,
                           alpha=0.2)  # plot a zone around the object on the right side
            object = objectDic[setup][exp][phase][0]
            plotObjectZone(ax=ax, colorFill=colorObjects[object], x=objectPosition[setup]['left'][0],
                           y=objectPosition[setup]['left'][1], radius=radiusObjects[object] + vibrissae / scaleFactor,
                           alpha=0.2)  # plot a zone around the object on the left side

            if nCol['male'] < 5:
                nCol['male'] += 1
            if nCol['male'] >= 5:
                nCol['male'] = 0
                nRow['male'] += 1

        if animal.sex == 'female':
            # set the axes. Check the number of file to get the dimension of axes and grab the correct ones.
            ax = axesF[nRow['female']][nCol['female']]  # set the subplot where to draw the plot
            plotTrajectorySingleAnimal(file, color=colorSap[animal.genotype], ax=ax, tmin=tmin,
                                       tmax=tmax, title=title, xa=128, xb=383, ya=80,
                                       yb=336)  # function to draw the trajectory
            object = objectDic[setup][exp][phase][1]
            plotObjectZone(ax=ax, colorFill=colorObjects[object], x=objectPosition[setup]['right'][0],
                           y=objectPosition[setup]['right'][1], radius=radiusObjects[object],
                           alpha=0.5)  # plot the object on the right side
            object = objectDic[setup][exp][phase][0]
            plotObjectZone(ax=ax, colorFill=colorObjects[object], x=objectPosition[setup]['left'][0],
                           y=objectPosition[setup]['left'][1], radius=radiusObjects[object],
                           alpha=0.5)  # plot the object on the left side
            object = objectDic[setup][exp][phase][1]
            plotObjectZone(ax=ax, colorFill=colorObjects[object], x=objectPosition[setup]['right'][0],
                           y=objectPosition[setup]['right'][1], radius=radiusObjects[object] + vibrissae / scaleFactor,
                           alpha=0.2)  # plot a zone around the object on the right side
            object = objectDic[setup][exp][phase][0]
            plotObjectZone(ax=ax, colorFill=colorObjects[object], x=objectPosition[setup]['left'][0],
                           y=objectPosition[setup]['left'][1], radius=radiusObjects[object] + vibrissae / scaleFactor,
                           alpha=0.2)  # plot a zone around the object on the left side

            if nCol['female'] < 5:
                nCol['female'] += 1
            if nCol['female'] >= 5:
                nCol['female'] = 0
                nRow['female'] += 1

    figM.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
    # plt.show() #display the plot
    figM.savefig('{}_males.pdf'.format(figName), dpi=200)
    figF.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
    figF.savefig('{}_females.pdf'.format(figName), dpi=200)


def computeSniffTime(files=None, tmin=None, objectDic=None):
    print('Compute time of exploration.')
    data = {}
    for val in ['sniffLeft', 'sniffRight', 'onLeftObject', 'onRightObject', 'totalSniff']:
        data[val] = {}
        for setup in [1,2]:
            data[val][setup] = {}
            for sex in ['male', 'female']:
                data[val][setup][sex] = {}
                for geno in ['WT', 'Del/+']:
                    data[val][setup][sex][geno] = {}

    for file in files:
        connection = sqlite3.connect(file)

        pool = AnimalPool()
        pool.loadAnimals(connection)
        animal = pool.animalDictionnary[1]
        sex = animal.sex
        setup = int(animal.setup)
        geno = animal.genotype
        rfid = animal.RFID
        object = objectDic[setup][exp]['test'][0]

        if tmin==None:
            tmin = getStartTestPhase(pool=pool)
        # load detection for the animal:
        pool.loadDetection(start=tmin, end=tmin + 10 * oneMinute)
        pool.filterDetectionByInstantSpeed(0, 70)

        selectedFrames = {}
        onObjectX = {}
        onObjectY = {}
        for obj in ['left', 'right']:
            selectedFrames[obj] = []
            onObjectX[obj] = []
            onObjectY[obj] = []

        noneVec = []

        for t in animal.detectionDictionnary.keys():
            for obj in ['left', 'right']:
                distanceNose = animal.getDistanceNoseToPoint(t=t, xPoint=objectPosition[setup][obj][0],
                                                             yPoint=-objectPosition[setup][obj][1])
                distanceMass = animal.getDistanceToPoint(t=t, xPoint=objectPosition[setup][obj][0],
                                                         yPoint=-objectPosition[setup][obj][1])
                if distanceNose == None:
                    noneVec.append(t)
                    break
                else:
                    if distanceNose <= radiusObjects[object] + 2 / scaleFactor:
                        # check if the animal is on the object:
                        if distanceMass <= radiusObjects[object]:
                            detection = animal.detectionDictionnary.get(t)
                            onObjectX[obj].append(detection.massX)
                            onObjectY[obj].append(-detection.massY)
                        else:
                            selectedFrames[obj].append(t)

        data['sniffLeft'][setup][sex][geno][rfid] = len(selectedFrames['left'])
        data['sniffRight'][setup][sex][geno][rfid] = len(selectedFrames['right'])
        data['totalSniff'][setup][sex][geno][rfid] = data['sniffLeft'][setup][sex][geno][rfid] + data['sniffRight'][setup][sex][geno][rfid]

    return data




if __name__ == '__main__':

    print("Code launched.")
    # set font
    from matplotlib import rc, gridspec

    rc('font', **{'family': 'serif', 'serif': ['Arial']})
    #object positions (x,y) according to the setup:
    objectPosition = {1: {'left': (190, -152), 'right': (330, -152)},
                      2: {'left': (186, -152), 'right': (330, -152)}
                      }

    # object information
    objectDic = {1: {'short': {'learning': ('cup', 'cup'), 'test': ('cup', 'shaker')},
                     'medium': {'learning': ('falcon', 'falcon'), 'test': ('falcon', 'flask')}},
                 2: {'short': {'learning': ('falcon', 'falcon'), 'test': ('falcon', 'flask')},
                     'medium': {'learning': ('cup', 'cup'), 'test': ('cup', 'shaker')}}
                 }
    '''
    objectDic = {1: {'short': ('cup', 'shaker'), 'medium': ('falcon', 'flask')},
                 2: {'short': ('falcon', 'flask'), 'medium': ('cup', 'shaker')}}
    '''
    radiusObjects = {'cup': 18, 'flask': 15, 'falcon': 9, 'shaker': 11}
    colorObjects = {'cup': 'gold', 'flask': 'mediumpurple', 'falcon': 'mediumseagreen', 'shaker': 'orchid'}
    objectList = ['cup', 'flask', 'falcon', 'shaker']

    colorSap = {'WT': 'steelblue', 'Del/+': 'darkorange'}

    sexList = ['male', 'female']
    genoList = ['WT', 'Del/+']

    markerList = ['o', 'v'] #for the setups

    xPos = {'male': {'WT': 1.5, 'Del/+': 4.5},
            'female': {'WT': 7.5, 'Del/+': 10.5}}

    vibrissae = 3 #estimated size of the vibrissae to determine the contact zone with the object

    while True:
        question = "Do you want to:"
        question += "\n\t [r]ebuild all events?"
        question += "\n\t [ch]eck file info?"
        question += "\n\t rebuild [sn]iff events?"
        question += "\n\t [ph]lot trajectories in the habituation phase?"
        question += "\n\t [pl]lot trajectories in the learning phase (same objects)?"
        question += "\n\t [pt]lot trajectories in the test phase (different objects)?"
        question += "\n\t plot sniffing [res]ults?"
        question += "\n\t compute and plot [raw] values for sniffing time?"
        question += "\n"
        answer = input(question)

        if answer == 'r':
            print("Rebuilding all events.")
            processAll()

            break

        if answer == 'ch':
            print('Check information entered into the databases')
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
                infoList = [file, rfid, sex, geno, age, setup]
                for info in infoList:
                    text_file.write("{}\t".format(info))
                text_file.write("\n")

            text_file.write("\n")
            text_file.close()
            print('Job done.')
            break

        if answer == 'sn':
            print("Rebuilding sniff events.")
            question1 = "Is it the short or medium retention time? (short / medium)"
            exp = input(question1)
            question2 = "Is it the learning or test phase? (learning / test)"
            phase = input(question2)
            files = getFilesToProcess()
            eventList = ['SniffLeft', 'SniffRight', 'UpLeft', 'UpRight']
            colorEvent = {'SniffLeft': 'dodgerblue', 'SniffRight': 'darkorange', 'UpLeft': 'skyblue', 'UpRight': 'peachpuff'}
            addThickness = 0
            yLim = {'nbEvent': 150, 'meanEventLength': 100, 'totalDuration': 4000, 'ratio': 1.2}

            for file in files:
                print(file)
                connection = sqlite3.connect(file)
                BuildEventObjectSniffingNor.reBuildEvent(connection, tmin=0, tmax=20*oneMinute, pool = None, exp=exp, phase=phase, objectPosition=objectPosition, radiusObjects=radiusObjects, objectDic=objectDic)
                print('Rebuild sniff events done.')

            figName = 'fig_timeline_nor_{}_{}.pdf'.format(exp, phase)
            fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14, 8))  # building the plot for timelines

            nRow = {'male': {'WT': 0, 'Del/+': 1}, 'female': {'WT': 0, 'Del/+': 1}}  # initialisation of the row
            nCol = {'male': {'WT': 0, 'Del/+': 0}, 'female': {'WT': 1, 'Del/+': 1}}  # initialisation of the column
            line = {}
            for sex in sexList:
                line[sex] = {}
                for geno in genoList:
                    line[sex][geno] = 1

            for row in [0,1]:
                for col in [0,1]:
                    ax = axes[row][col]
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['left'].set_visible(False)
                    ax.set_title('{} {}'.format(genoList[row], sexList[col]), fontsize=18)
                    ax.legend().set_visible(False)
                    ax.xaxis.set_tick_params(direction="in")
                    ax.get_yaxis().set_visible(False)
                    ax.set_xlim(0, 14400)
                    ax.set_ylim(0, 24)
            measureData = {}
            for var in ['nbEvent', 'meanEventLength', 'totalDuration', 'ratio']:
                measureData[var] = {}
                for eventType in eventList:
                    measureData[var][eventType] = {}
                    for setup in ['1','2']:
                        measureData[var][eventType][setup] = {}
                        for sex in sexList:
                            measureData[var][eventType][setup][sex] = {}
                            for geno in genoList:
                                measureData[var][eventType][setup][sex][geno] = []

            for file in files:
                print(file)
                connection = sqlite3.connect(file)
                pool = AnimalPool()
                pool.loadAnimals(connection)
                animal = pool.animalDictionnary[1]
                sex = animal.sex
                geno = animal.genotype
                setup = animal.setup
                #determine the start frame:
                if phase == 'learning':
                    tmin = getStartTestPhase(pool)
                elif phase == 'test':
                    tmin = 0
                #determine the end of the computation
                tmax = tmin + 10*oneMinute

                ax = axes[nRow[sex][geno]][nCol[sex][geno]]
                ax.text(-20, line[sex][geno]-0.5, s=animal.RFID[-4:], fontsize=10, horizontalalignment='right')
                #compute the coordinates for the drawing:
                lineData = {}
                for eventType in eventList:
                    #upload event timeline:
                    eventTypeTimeLine = EventTimeLine( connection, eventType, minFrame = tmin, maxFrame = tmax )
                    nbEvent = eventTypeTimeLine.getNbEvent()
                    meanEventLength = eventTypeTimeLine.getMeanEventLength()
                    totalDuration = eventTypeTimeLine.getTotalLength()
                    measureData['nbEvent'][eventType][setup][sex][geno].append(nbEvent)
                    measureData['meanEventLength'][eventType][setup][sex][geno].append(meanEventLength)
                    measureData['totalDuration'][eventType][setup][sex][geno].append(totalDuration)

                    lineData[eventType] = []
                    for event in eventTypeTimeLine.eventList:
                        lineData[eventType].append((event.startFrame - tmin - addThickness, event.duration() + addThickness))

                    ax.broken_barh(lineData[eventType], (line[sex][geno] - 1, 1), facecolors=colorEvent[eventType])
                    print('plot for ', animal.RFID)
                    print('line: ', line[sex][geno])

                sniffRightTimeLine = EventTimeLine(connection, 'SniffRight', minFrame=tmin, maxFrame=tmax)
                totalDurationRight = sniffRightTimeLine.getTotalLength()
                sniffLeftTimeLine = EventTimeLine(connection, 'SniffLeft', minFrame=tmin, maxFrame=tmax)
                totalDurationLeft = sniffLeftTimeLine.getTotalLength()

                measureData['ratio']['SniffRight'][setup][sex][geno].append(totalDurationRight / (totalDurationLeft + totalDurationRight))
                measureData['ratio']['SniffLeft'][setup][sex][geno].append(totalDurationLeft / (totalDurationLeft + totalDurationRight))

                line[sex][geno] += 1.5

            fig.show()
            fig.savefig(figName, dpi=300)

            figName = 'fig_measures_events_{}_{}.pdf'.format(exp, phase)
            figMeasures, axesMeasures = plt.subplots(nrows=1, ncols=4, figsize=(24, 4))
            col = 0
            for var in ['nbEvent', 'meanEventLength', 'totalDuration', 'ratio']:
                ax = axesMeasures[col]
                yLabel = var
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                xIndex = [1, 2, 4, 5, 7, 8, 10, 11]
                ax.set_xticks(xIndex)
                ax.set_xticklabels(['Left', 'Right', 'Left', 'Right', 'Left', 'Right', 'Left', 'Right'], rotation=45,
                                   FontSize=12, horizontalalignment='right')
                ax.set_ylabel(yLabel, FontSize=15)
                ax.legend().set_visible(False)
                ax.xaxis.set_tick_params(direction="in")
                ax.set_xlim(0, 12)
                ax.set_ylim(0, yLim[var])
                ax.tick_params(axis='y', labelsize=14)
                ax.text(1.5, yLim[var], s='WT males', fontsize=14, horizontalalignment='center')
                ax.text(4.5, yLim[var], s='Del/+ males', fontsize=14, horizontalalignment='center')
                ax.text(7.5, yLim[var], s='WT females', fontsize=14, horizontalalignment='center')
                ax.text(10.5, yLim[var], s='Del/+ females', fontsize=14, horizontalalignment='center')
                if var == 'ratio':
                    ax.hlines(0.5, xmin = 0, xmax=12, colors='grey', linestyles='dashed')

                # plot the points for each value:
                i = 0
                for setup in ['1', '2']:
                    ax.scatter(addJitter([1] * len(measureData[var]['SniffLeft'][setup]['male']['WT']), 0.2),
                               measureData[var]['SniffLeft'][setup]['male']['WT'], color='steelblue', marker=markerList[i], alpha=0.8,
                               label="on", s=8)
                    ax.scatter(addJitter([2] * len(measureData[var]['SniffRight'][setup]['male']['WT']), 0.2),
                               measureData[var]['SniffRight'][setup]['male']['WT'], color='steelblue', marker=markerList[i], alpha=0.8,
                               label="on", s=8)
                    ax.scatter(addJitter([4] * len(measureData[var]['SniffLeft'][setup]['male']['Del/+']), 0.2),
                               measureData[var]['SniffLeft'][setup]['male']['Del/+'], color='darkorange', marker=markerList[i],
                               alpha=0.8, label="on", s=8)
                    ax.scatter(addJitter([5] * len(measureData[var]['SniffRight'][setup]['male']['Del/+']), 0.2),
                               measureData[var]['SniffRight'][setup]['male']['Del/+'], color='darkorange', marker=markerList[i],
                               alpha=0.8, label="on", s=8)

                    ax.scatter(addJitter([7] * len(measureData[var]['SniffLeft'][setup]['female']['WT']), 0.2),
                               measureData[var]['SniffLeft'][setup]['female']['WT'], color='steelblue', marker=markerList[i], alpha=0.8,
                               label="on", s=8)
                    ax.scatter(addJitter([8] * len(measureData[var]['SniffRight'][setup]['female']['WT']), 0.2),
                               measureData[var]['SniffRight'][setup]['female']['WT'], color='steelblue', marker=markerList[i], alpha=0.8,
                               label="on", s=8)
                    ax.scatter(addJitter([10] * len(measureData[var]['SniffLeft'][setup]['female']['Del/+']), 0.2),
                               measureData[var]['SniffLeft'][setup]['female']['Del/+'], color='darkorange', marker=markerList[i],
                               alpha=0.8, label="on", s=8)
                    ax.scatter(addJitter([11] * len(measureData[var]['SniffRight'][setup]['female']['Del/+']), 0.2),
                               measureData[var]['SniffRight'][setup]['female']['Del/+'], color='darkorange', marker=markerList[i],
                               alpha=0.8, label="on", s=8)
                    i += 1

                if var == 'ratio':
                    # conduct statistical testing: one sample Student t-test:
                    T = {}
                    p = {}
                    for sex in ['male', 'female']:
                        T[sex] = {}
                        p[sex] = {}
                        for geno in ['WT', 'Del/+']:
                            prop = measureData['ratio']['SniffRight']['1'][sex][geno] + \
                                   measureData['ratio']['SniffRight']['2'][sex][geno]
                            T[sex][geno], p[sex][geno] = stats.ttest_1samp(a=prop, popmean=0.5)
                            print(
                                'One-sample Student T-test for {} learning {} {} {}: T={}, p={}'.format(exp, len(prop), sex, geno, T[sex][geno], p[sex][geno]))
                            ax.text(xPos[sex][geno], 1.1, getStarsFromPvalues(pvalue=p[sex][geno], numberOfTests=1),
                                    fontsize=14)

                col += 1

            figMeasures.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
            figMeasures.show() #display the plot
            figMeasures.savefig(figName, dpi=200)
            break

        if answer == 'ph':
            print('Plot trajectory in the habituation phase')
            #distance travelled
            #space use
            #traj of center of mass
            files = getFilesToProcess()
            buildFigTrajectoryMalesFemales(files=files, title='hab', tmin=0, tmax=4*oneMinute, figName='fig_traj_hab_long_nor', colorSap=colorSap, xa=128, xb=383, ya=80, yb=336)
            break

        if answer == 'pl':
            print('Plot trajectory during the learning phase.')
            question = "Is it the short or medium retention time? (short / medium)"
            exp = input(question)
            phase = 'learning'
            #traj of center of mass
            #traj of the nose position
            #sap
            #time spent sniffing the object
            timeSniff = {}
            #time spent around the object
            #body orientation toward each object
            files = getFilesToProcess()
            figName = 'fig_traj_nor_{}_same'.format(exp)
            plotTrajectoriesNorPhases(files=files, figName=figName, title=phase, phase=phase, exp=exp, colorSap=colorSap, xa=128, xb=383, ya=80, yb=336, objectDic=objectDic, colorObjects=colorObjects, objectPosition=objectPosition, radiusObjects=radiusObjects)

            data = computeSniffTime(files, objectDic=objectDic)

            # store the data dictionary in a json file
            with open('sniff_time_same_{}.json'.format(exp), 'w') as jFile:
                json.dump(data, jFile, indent=4)
            print("json file created")

            break

        if answer == 'pt':
            print('Plot trajectory in the test phase')
            question = "Is it the short or medium retention time? (short / medium)"
            exp = input(question)
            phase = 'test'
            #distance travelled
            #space use
            #traj of center of mass
            files = getFilesToProcess()
            figName = 'fig_traj_nor_{}_test'.format(exp)
            plotTrajectoriesNorPhases(files=files, figName=figName, title=phase, phase=phase, exp=exp, colorSap=colorSap, xa=128, xb=383, ya=80, yb=336,
                                      objectDic=objectDic, colorObjects=colorObjects, objectPosition=objectPosition,
                                      radiusObjects=radiusObjects)

            data = computeSniffTime(files, tmin=0, objectDic=objectDic)

            # store the data dictionary in a json file
            with open('sniff_time_test_{}.json'.format(exp), 'w') as jFile:
                json.dump(data, jFile, indent=4)
            print("json file created")

            break

        if answer == 'res':
            # open the json files
            question = "Is it the short or medium retention time? (short / medium)"
            exp = input(question)

            jsonFileName = "sniff_time_same_{}.json".format(exp)
            with open(jsonFileName) as json_data:
                dataSame = json.load(json_data)
            jsonFileName = "sniff_time_test_{}.json".format(exp)
            with open(jsonFileName) as json_data:
                dataTest = json.load(json_data)
            print("json file re-imported.")
            print(dataSame)

            fig, axes = plt.subplots(nrows=1, ncols=2,
                                     figsize=(16, 4))  # create the figure for the graphs of the computation

            col = 0  # initialise the column number
            # reformate the data dictionary to get the correct format of data for plotting and statistical analyses
            dataS = {}
            dataD = {}
            for val in ['sniffLeft', 'sniffRight']:
                print(val)
                dataS[val] = {}
                dataD[val] = {}
                for setup in ['1','2']:
                    dataS[val][setup] = {}
                    dataD[val][setup] = {}
                    for sex in ['male', 'female']:
                        dataS[val][setup][sex] = {}
                        dataD[val][setup][sex] = {}
                        for geno in ['WT', 'Del/+']:
                            dataS[val][setup][sex][geno] = []
                            dataD[val][setup][sex][geno] = []
                            for rfid in dataSame[val][setup][sex][geno].keys():
                                if (dataSame['totalSniff'][setup][sex][geno][rfid] >= 5*30) & (dataTest['totalSniff'][setup][sex][geno][rfid] >= 5*30):
                                    dataS[val][setup][sex][geno].append(dataSame[val][setup][sex][geno][rfid]/dataSame['totalSniff'][setup][sex][geno][rfid])
                                    dataD[val][setup][sex][geno].append(dataTest[val][setup][sex][geno][rfid]/dataTest['totalSniff'][setup][sex][geno][rfid])
                                else:
                                    print('Too Short exploration time in setup {} for {} {} {}'.format(setup, sex, geno, rfid))

            ax = axes[col]
            yLabel = 'Proportion sniff time (same)'
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            xIndex = [1,2, 4,5, 7,8, 10,11]
            ax.set_xticks(xIndex)
            ax.set_xticklabels(['Left', 'Right', 'Left', 'Right', 'Left', 'Right', 'Left', 'Right'], rotation=45, FontSize=12,
                               horizontalalignment='right')
            ax.set_ylabel(yLabel, FontSize=15)
            ax.legend().set_visible(False)
            ax.xaxis.set_tick_params(direction="in")
            ax.set_xlim(0, 12)
            ax.set_ylim(0, 1.2)
            ax.tick_params(axis='y', labelsize=14)
            ax.text(1.5, 1.2, s='WT males', fontsize=16, horizontalalignment='center')
            ax.text(4.5, 1.2, s='Del/+ males', fontsize=16, horizontalalignment='center')
            ax.text(7.5, 1.2, s='WT females', fontsize=16, horizontalalignment='center')
            ax.text(10.5, 1.2, s='Del/+ females', fontsize=16, horizontalalignment='center')
            ax.hlines(0.5, xmin = 0, xmax=12, colors='grey', linestyles='dashed')

            # compute the mean and the standard error of mean
            meanS = {}
            meanD = {}
            semS = {}
            semD = {}
            for val in ['sniffLeft', 'sniffRight']:
                meanS[val] = {}
                semS[val] = {}
                meanD[val] = {}
                semD[val] = {}
                for sex in ['male', 'female']:
                    meanS[val][sex] = {}
                    semS[val][sex] = {}
                    meanD[val][sex] = {}
                    semD[val][sex] = {}
                    for geno in ['WT', 'Del/+']:
                        meanS[val][sex][geno] = np.mean(dataS[val]['1'][sex][geno]+dataS[val]['2'][sex][geno])
                        semS[val][sex][geno] = np.std(dataS[val]['1'][sex][geno]+dataS[val]['2'][sex][geno]) / np.sqrt(len(dataS[val]['1'][sex][geno]+dataS[val]['2'][sex][geno]))
                        meanD[val][sex][geno] = np.mean(dataD[val]['1'][sex][geno]+dataD[val]['2'][sex][geno])
                        semD[val][sex][geno] = np.std(dataD[val]['1'][sex][geno]+dataD[val]['2'][sex][geno]) / np.sqrt(len(dataD[val]['1'][sex][geno]+dataD[val]['2'][sex][geno]))


            # plot the points for each value:
            i = 0
            for setup in ['1','2']:
                ax.scatter(addJitter([1] * len(dataS['sniffLeft'][setup]['male']['WT']), 0.2), dataS['sniffLeft'][setup]['male']['WT'], color='steelblue', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([2] * len(dataS['sniffRight'][setup]['male']['WT']), 0.2), dataS['sniffRight'][setup]['male']['WT'], color='steelblue', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([4] * len(dataS['sniffLeft'][setup]['male']['Del/+']), 0.2), dataS['sniffLeft'][setup]['male']['Del/+'], color='darkorange', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([5] * len(dataS['sniffRight'][setup]['male']['Del/+']), 0.2), dataS['sniffRight'][setup]['male']['Del/+'], color='darkorange', marker=markerList[i], alpha=0.8, label="on", s=8)

                ax.scatter(addJitter([7] * len(dataS['sniffLeft'][setup]['female']['WT']), 0.2), dataS['sniffLeft'][setup]['female']['WT'], color='steelblue', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([8] * len(dataS['sniffRight'][setup]['female']['WT']), 0.2), dataS['sniffRight'][setup]['female']['WT'], color='steelblue', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([10] * len(dataS['sniffLeft'][setup]['female']['Del/+']), 0.2), dataS['sniffLeft'][setup]['female']['Del/+'], color='darkorange', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([11] * len(dataS['sniffRight'][setup]['female']['Del/+']), 0.2), dataS['sniffRight'][setup]['female']['Del/+'], color='darkorange', marker=markerList[i], alpha=0.8, label="on", s=8)
                i += 1
            # plot the mean and SEM on the graphs:
            ax.errorbar([1,2, 4,5, 7,8, 10,11],
                        [meanS['sniffLeft']['male']['WT'], meanS['sniffRight']['male']['WT'],
                         meanS['sniffLeft']['male']['Del/+'], meanS['sniffRight']['male']['Del/+'],
                         meanS['sniffLeft']['female']['WT'], meanS['sniffRight']['female']['WT'],
                         meanS['sniffLeft']['female']['Del/+'], meanS['sniffRight']['female']['Del/+']],
                        [semS['sniffLeft']['male']['WT'], semS['sniffRight']['male']['WT'],
                         semS['sniffLeft']['male']['Del/+'], semS['sniffRight']['male']['Del/+'],
                         semS['sniffLeft']['female']['WT'], semS['sniffRight']['female']['WT'],
                         semS['sniffLeft']['female']['Del/+'], semS['sniffRight']['female']['Del/+']],
                        color='black', linestyle='None', marker='o')

            # conduct statistical testing: one sample Student t-test:
            T = {}
            p = {}
            for sex in ['male', 'female']:
                T[sex] = {}
                p[sex] = {}
                for geno in ['WT', 'Del/+']:
                    prop = dataS['sniffRight']['1'][sex][geno] + dataS['sniffRight']['2'][sex][geno]
                    T[sex][geno], p[sex][geno] = stats.ttest_1samp(a=prop, popmean=0.5)
                    print('One-sample Student T-test for {} learning {} {} {}: T={}, p={}'.format(exp, len(prop), sex, geno,
                                                                                              T[sex][geno],
                                                                                              p[sex][geno]))
                    ax.text(xPos[sex][geno], 1.1, getStarsFromPvalues(pvalue=p[sex][geno], numberOfTests=1),
                            fontsize=16)

            col += 1

            ax = axes[col]
            yLabel = 'Proportion sniff time (different)'
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            xIndex = [1, 2, 4, 5, 7, 8, 10, 11]
            ax.set_xticks(xIndex)
            ax.set_xticklabels(['Left', 'Right', 'Left', 'Right', 'Left', 'Right', 'Left', 'Right'],
                               rotation=45, FontSize=12,
                               horizontalalignment='right')
            ax.set_ylabel(yLabel, FontSize=15)
            ax.legend().set_visible(False)
            ax.xaxis.set_tick_params(direction="in")
            ax.set_xlim(0, 12)
            ax.set_ylim(0, 1.2)
            ax.tick_params(axis='y', labelsize=14)
            ax.text(1.5, 1.2, s='WT males', fontsize=16, horizontalalignment='center')
            ax.text(4.5, 1.2, s='Del/+ males', fontsize=16, horizontalalignment='center')
            ax.text(7.5, 1.2, s='WT females', fontsize=16, horizontalalignment='center')
            ax.text(10.5, 1.2, s='Del/+ females', fontsize=16, horizontalalignment='center')
            ax.hlines(0.5, xmin=0, xmax=12, colors='grey', linestyles='dashed')

            # plot the points for each value:
            i = 0
            for setup in ['1','2']:
                ax.scatter(addJitter([1] * len(dataD['sniffLeft'][setup]['male']['WT']), 0.2), dataD['sniffLeft'][setup]['male']['WT'], color='steelblue', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([2] * len(dataD['sniffRight'][setup]['male']['WT']), 0.2), dataD['sniffRight'][setup]['male']['WT'], color='steelblue', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([4] * len(dataD['sniffLeft'][setup]['male']['Del/+']), 0.2), dataD['sniffLeft'][setup]['male']['Del/+'], color='darkorange', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([5] * len(dataD['sniffRight'][setup]['male']['Del/+']), 0.2), dataD['sniffRight'][setup]['male']['Del/+'], color='darkorange', marker=markerList[i], alpha=0.8, label="on", s=8)

                ax.scatter(addJitter([7] * len(dataD['sniffLeft'][setup]['female']['WT']), 0.2), dataD['sniffLeft'][setup]['female']['WT'], color='steelblue', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([8] * len(dataD['sniffRight'][setup]['female']['WT']), 0.2), dataD['sniffRight'][setup]['female']['WT'], color='steelblue', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([10] * len(dataD['sniffLeft'][setup]['female']['Del/+']), 0.2), dataD['sniffLeft'][setup]['female']['Del/+'], color='darkorange', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([11] * len(dataD['sniffRight'][setup]['female']['Del/+']), 0.2), dataD['sniffRight'][setup]['female']['Del/+'], color='darkorange', marker=markerList[i], alpha=0.8, label="on", s=8)
                i += 1

            # plot the mean and SEM on the graphs:
            ax.errorbar([1, 2, 4, 5, 7, 8, 10, 11],
                        [meanD['sniffLeft']['male']['WT'], meanD['sniffRight']['male']['WT'],
                         meanD['sniffLeft']['male']['Del/+'], meanD['sniffRight']['male']['Del/+'],
                         meanD['sniffLeft']['female']['WT'], meanD['sniffRight']['female']['WT'],
                         meanD['sniffLeft']['female']['Del/+'], meanD['sniffRight']['female']['Del/+']],
                        [semD['sniffLeft']['male']['WT'], semD['sniffRight']['male']['WT'],
                         semD['sniffLeft']['male']['Del/+'], semD['sniffRight']['male']['Del/+'],
                         semD['sniffLeft']['female']['WT'], semD['sniffRight']['female']['WT'],
                         semD['sniffLeft']['female']['Del/+'], semD['sniffRight']['female']['Del/+']],
                        color='black', linestyle='None', marker='o')

            # conduct statistical testing: one sample Student t-test:
            T = {}
            p = {}
            for sex in ['male', 'female']:
                T[sex] = {}
                p[sex] = {}
                for geno in ['WT', 'Del/+']:
                    prop = dataD['sniffRight']['1'][sex][geno] + dataD['sniffRight']['2'][sex][geno]
                    T[sex][geno], p[sex][geno] = stats.ttest_1samp(a=prop, popmean=0.5)
                    print('One-sample Student T-test for {} test {} {} {}: T={}, p={}'.format(exp, len(prop), sex, geno, T[sex][geno], p[sex][geno]))
                    ax.text(xPos[sex][geno], 1.1, getStarsFromPvalues(pvalue=p[sex][geno], numberOfTests=1), fontsize=16)


            plt.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
            plt.show()  # display the plot
            fig.savefig('fig_values_sniff_nor_{}.pdf'.format(exp), dpi=200)

            break

        if answer == 'raw':
            # open the json files
            question = "Is it the short or medium retention time? (short / medium)"
            exp = input(question)

            jsonFileName = "sniff_time_same_{}.json".format(exp)
            with open(jsonFileName) as json_data:
                dataSame = json.load(json_data)
            jsonFileName = "sniff_time_test_{}.json".format(exp)
            with open(jsonFileName) as json_data:
                dataTest = json.load(json_data)
            print("json file re-imported.")
            print(dataSame.keys())

            # get raw values for sniffing time
            timeS = {}
            timeD = {}
            for val in ['sniffLeft', 'sniffRight']:
                print(val)
                timeS[val] = {}
                timeD[val] = {}
                for setup in ['1', '2']:
                    print(val)
                    timeS[val][setup] = {}
                    timeD[val][setup] = {}
                    for sex in ['male', 'female']:
                        timeS[val][setup][sex] = {}
                        timeD[val][setup][sex] = {}
                        for geno in ['WT', 'Del/+']:
                            timeS[val][setup][sex][geno] = []
                            timeD[val][setup][sex][geno] = []
                            for rfid in dataSame[val][setup][sex][geno].keys():
                                timeS[val][setup][sex][geno].append(dataSame[val][setup][sex][geno][rfid] / 30)
                                timeD[val][setup][sex][geno].append(dataTest[val][setup][sex][geno][rfid] / 30)

            fig, axes = plt.subplots(nrows=1, ncols=2,
                                     figsize=(16, 4))  # create the figure for the graphs of the computation

            ax = axes[0]
            yLabel = 'sniff time (same)'
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            xIndex = [1, 2, 4, 5, 7, 8, 10, 11]
            ax.set_xticks(xIndex)
            ax.set_xticklabels(['Left', 'Right', 'Left', 'Right', 'Left', 'Right', 'Left', 'Right'], rotation=45,
                               FontSize=12,
                               horizontalalignment='right')
            ax.set_ylabel(yLabel, FontSize=15)
            ax.legend().set_visible(False)
            ax.xaxis.set_tick_params(direction="in")
            ax.set_xlim(0, 12)
            ax.set_ylim(0, 50)
            ax.tick_params(axis='y', labelsize=14)
            ax.text(1.5, 50, s='WT males', fontsize=16, horizontalalignment='center')
            ax.text(4.5, 50, s='Del/+ males', fontsize=16, horizontalalignment='center')
            ax.text(7.5, 50, s='WT females', fontsize=16, horizontalalignment='center')
            ax.text(10.5, 50, s='Del/+ females', fontsize=16, horizontalalignment='center')
            ax.hlines(3, xmin=0, xmax=12, colors='grey', linestyles='dashed')

            # plot the points for each value:
            i = 0
            for setup in ['1', '2']:
                ax.scatter(addJitter([1] * len(timeS['sniffLeft'][setup]['male']['WT']), 0.2), timeS['sniffLeft'][setup]['male']['WT'],
                           color='steelblue', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([2] * len(timeS['sniffRight'][setup]['male']['WT']), 0.2), timeS['sniffRight'][setup]['male']['WT'],
                           color='steelblue', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([4] * len(timeS['sniffLeft'][setup]['male']['Del/+']), 0.2),
                           timeS['sniffLeft'][setup]['male']['Del/+'], color='darkorange', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([5] * len(timeS['sniffRight'][setup]['male']['Del/+']), 0.2),
                           timeS['sniffRight'][setup]['male']['Del/+'], color='darkorange', marker=markerList[i], alpha=0.8, label="on", s=8)

                ax.scatter(addJitter([7] * len(timeS['sniffLeft'][setup]['female']['WT']), 0.2),
                           timeS['sniffLeft'][setup]['female']['WT'], color='steelblue', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([8] * len(timeS['sniffRight'][setup]['female']['WT']), 0.2),
                           timeS['sniffRight'][setup]['female']['WT'], color='steelblue', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([10] * len(timeS['sniffLeft'][setup]['female']['Del/+']), 0.2),
                           timeS['sniffLeft'][setup]['female']['Del/+'], color='darkorange', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([11] * len(timeS['sniffRight'][setup]['female']['Del/+']), 0.2),
                           timeS['sniffRight'][setup]['female']['Del/+'], color='darkorange', marker=markerList[i], alpha=0.8, label="on", s=8)
                i += 1

            ax = axes[1]
            yLabel = 'sniff time (diff)'
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            xIndex = [1, 2, 4, 5, 7, 8, 10, 11]
            ax.set_xticks(xIndex)
            ax.set_xticklabels(['Left', 'Right', 'Left', 'Right', 'Left', 'Right', 'Left', 'Right'], rotation=45,
                               FontSize=12,
                               horizontalalignment='right')
            ax.set_ylabel(yLabel, FontSize=15)
            ax.legend().set_visible(False)
            ax.xaxis.set_tick_params(direction="in")
            ax.set_xlim(0, 12)
            ax.set_ylim(0, 50)
            ax.tick_params(axis='y', labelsize=14)
            ax.text(1.5, 50, s='WT males', fontsize=16, horizontalalignment='center')
            ax.text(4.5, 50, s='Del/+ males', fontsize=16, horizontalalignment='center')
            ax.text(7.5, 50, s='WT females', fontsize=16, horizontalalignment='center')
            ax.text(10.5, 50, s='Del/+ females', fontsize=16, horizontalalignment='center')
            ax.hlines(3, xmin=0, xmax=12, colors='grey', linestyles='dashed')

            # plot the points for each value:
            i = 0
            for setup in ['1', '2']:
                ax.scatter(addJitter([1] * len(timeD['sniffLeft'][setup]['male']['WT']), 0.2), timeD['sniffLeft'][setup]['male']['WT'],
                           color='steelblue', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([2] * len(timeD['sniffRight'][setup]['male']['WT']), 0.2), timeD['sniffRight'][setup]['male']['WT'],
                           color='steelblue', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([4] * len(timeD['sniffLeft'][setup]['male']['Del/+']), 0.2),
                           timeD['sniffLeft'][setup]['male']['Del/+'], color='darkorange', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([5] * len(timeD['sniffRight'][setup]['male']['Del/+']), 0.2),
                           timeD['sniffRight'][setup]['male']['Del/+'], color='darkorange', marker=markerList[i], alpha=0.8, label="on", s=8)

                ax.scatter(addJitter([7] * len(timeD['sniffLeft'][setup]['female']['WT']), 0.2),
                           timeD['sniffLeft'][setup]['female']['WT'], color='steelblue', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([8] * len(timeD['sniffRight'][setup]['female']['WT']), 0.2),
                           timeD['sniffRight'][setup]['female']['WT'], color='steelblue', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([10] * len(timeD['sniffLeft'][setup]['female']['Del/+']), 0.2),
                           timeD['sniffLeft'][setup]['female']['Del/+'], color='darkorange', marker=markerList[i], alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([11] * len(timeD['sniffRight'][setup]['female']['Del/+']), 0.2),
                           timeD['sniffRight'][setup]['female']['Del/+'], color='darkorange', marker=markerList[i], alpha=0.8, label="on", s=8)
                i += 1

            plt.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
            plt.show()  # display the plot
            fig.savefig('fig_time_sniff_nor_{}.pdf'.format(exp), dpi=200)

            break