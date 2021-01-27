'''
#Created on 26 January 2021

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
    pauseValueList = []
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


def plotTrajectorySingleAnimal(file, ax, tmin, tmax):
    connection = sqlite3.connect(file) #connection to the database

    pool = AnimalPool()
    pool.loadAnimals(connection) #upload all the animals from the database
    animal = pool.animalDictionnary[1] #select one animal from the group of animals in the database

    # draw the trajectory in the habituation phase
    pool.loadDetection( start=tmin, end=tmax ) #upload all the detections for the animal (all frames where it has been detected)
    pool.filterDetectionByInstantSpeed(0, 70) #filter the detections to get rid of abberrant points (animals not detected and set at -1,-1); filter based on speed of the animal
    plotZone(ax, colorEdge='lightgrey', colorFill='lightgrey', xa = 111, xb = 400, ya = -353, yb = -63)  # draw the rectangle for the whole cage
    plotZone(ax, colorEdge='lightgrey', colorFill='grey', xa=191, xb=320, ya=-273, yb=-143 ) # draw the rectangle for the center zone
    plot(ax, animal, title="Hab day1", color="black") #plot the trajectory of the center of mass

    plotSapNose(ax, animal) # add the frames where the animal is in SAP


if __name__ == '__main__':

    print("Code launched.")
    # set font
    from matplotlib import rc, gridspec

    rc('font', **{'family': 'serif', 'serif': ['Arial']})
    #object positions (x,y) order: up left, up right, down left, down right
    objectPosition = {'C1_M01': [(185,175), (316,160), (194,258), (309,268)],
                      'C1_M02': [(192,164), (319,162), (191,272), (318,269)],
                      'C1_M03': [(194,155), (322,162), (195,251), (313,252)],
                      'C2_M01': [(187,166), (313,163), (187,272), (307,271)],
                      'C3_M01': [(184,168), (329,163), (180,269), (329,270)],
                      'C3_M02': [(192,168), (315,168), (197,277), (309,277)],
                      'C3_M03': [(193,164), (322,156), (190,269), (321,268)],
                      'C3_M04': [(194,167), (321,169), (190,268), (313,262)],
                      'C4_F01': [(186,156), (322,163), (187,267), (320,261)],
                      'C4_F02': [(194,166), (318,167), (195,270), (312,271)],
                      'C5_F01': [(197,162), (322,159), (197,263), (321,264)],
                      'C5_F02': [(190,161), (313,164), (196,265), (309,260)],
                      'C5_F03': [(192,174), (320,174), (194,273), (318,271)]
                 }
    colorDic = {'C1_M01': 'blue',
                'C1_M02': 'skyblue',
                'C1_M03': 'darkblue',
                'C2_M01': 'tan',
                'C3_M01': 'gold',
                'C3_M02': 'firebrick',
                'C3_M03': 'red',
                'C3_M04': 'orange',
                'C4_F01': 'purple',
                'C4_F02': 'hotpink',
                'C5_F01': 'green',
                'C5_F02': 'mediumseagreen',
                'C5_F03': 'greenyellow'
                      }
    # object radius order: up left = cup, up right = flask, down left = falcon, down right = shaker
    radiusObjects = [18, 15, 9, 11]
    colorObjects = ['orangered', 'gold', 'dodgerblue', 'mediumseagreen']
    objectList = ['cup', 'flask', 'falcon', 'shaker']

    while True:
        question = "Do you want to:"
        question += "\n\t [r]ebuild all events?"
        question += "\n\t [ph]lot trajectories in the habituation phase?"
        question += "\n\t [pt]lot trajectories in the test phase?"
        question += "\n\t plot [m]anual scoring in the test phase?"
        question += "\n\t [c]orrelate manual and automatic scoring?"
        question += "\n"
        answer = input(question)

        if answer == 'r':
            print("Rebuilding all events.")
            processAll()

            break

        if answer == 'ph':
            print('Plot trajectory in the habituation phase')
            #distance travelled
            #space use
            #traj of center of mass
            files = getFilesToProcess() #upload files for the analysis
            nbFiles = len(files) #number of files to be processed
            fig, axes = plt.subplots(nrows=4, ncols=5, figsize=(18, 24)) #building the plot for trajectories

            nRow = 0 #initialisation of the row
            nCol = 0 #initialisation of the column

            tminHab = 0 #start time of the computation
            tmaxHab = 15 * oneMinute #end time of the computation

            for file in files:
                # set the axes. Check the number of file to get the dimension of axes and grab the correct ones.
                ax = axes[nRow][nCol] #set the subplot where to draw the plot
                plotTrajectorySingleAnimal( file, ax = ax, tmin = tminHab, tmax = tmaxHab) #function to draw the trajectory

                if nCol < 5:
                    nCol += 1
                if nCol >= 5:
                    nCol = 0
                    nRow += 1

            plt.tight_layout(pad=2, h_pad=4, w_pad=0) #reduce the margins to the minimum
            plt.show() #display the plot

            print('Compute distance travelled and number of SAP displayed.')
            data = {}
            for val in ['totDistance', 'centerDistance', 'centerTime', 'nbSap']:
                data[val] = {}
                for sex in ['male', 'female']:
                    data[val][sex] = {}
                    for geno in ['WT', 'Del/+']:
                        data[val][sex][geno] = {}

            for file in files:
                connection = sqlite3.connect(file)

                pool = AnimalPool()
                pool.loadAnimals(connection)
                animal = pool.animalDictionnary[1]
                animal.loadDetection( tminHab, tmaxHab )
                sex = animal.sex
                geno = animal.genotype
                rfid = animal.RFID

                dt1 = animal.getDistance(tmin = tminHab, tmax = tmaxHab) #compute the total distance traveled in the whole cage
                #get distance and time spent in the middle of the cage
                #coordinates of the whole cage: xa = 111, xb = 400, ya = 63, yb = 353
                d1 = animal.getDistanceSpecZone(tminHab, tmaxHab, xa=191, xb=320, ya=143, yb=273) #compute the distance traveled in the center zone
                t1 = animal.getCountFramesSpecZone(tminHab, tmaxHab, xa=191, xb=320, ya=143, yb=273) #compute the time spent in the center zone
                #get the number of frames in sap in whole cage
                sap1 = len(animal.getSap(tmin=tminHab, tmax=tmaxHab, xa = 111, xb = 400, ya = 63, yb = 353))
                #fill the data dictionary with the computed data for each file:
                data['totDistance'][sex][geno][rfid] = dt1
                data['centerDistance'][sex][geno][rfid] = d1
                data['centerTime'][sex][geno][rfid] = t1
                data['nbSap'][sex][geno][rfid] = sap1

            print(data)
            #store the data dictionary in a json file
            with open('habituationDay1.json', 'w') as jFile:
                json.dump(data, jFile, indent=4)
            print("json file created")

            fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(16, 4)) #create the figure for the graphs of the computation

            col = 0 #initialise the column number
            #reformate the data dictionary to get the correct format of data for plotting and statistical analyses
            for val in ['totDistance', 'centerDistance', 'centerTime', 'nbSap']:
                dataVal = {}
                for sex in ['male', 'female']:
                    dataVal[sex] = {}
                    for geno in ['WT', 'Del/+']:
                        dataVal[sex][geno] = []
                        for rfid in data[val][sex][geno].keys():
                            dataVal[sex][geno].append(data[val][sex][geno][rfid])

                ax = axes[col]
                yLabel = val
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                xIndex = [1, 2, 4, 5]
                ax.set_xticks(xIndex)
                ax.set_xticklabels(['WT', 'Del/+', 'WT', 'Del/+'], rotation=0, FontSize=12, horizontalalignment='center')
                ax.set_ylabel(yLabel, FontSize=15)
                ax.legend().set_visible(False)
                ax.xaxis.set_tick_params(direction="in")
                ax.set_xlim(0, 6)
                #ax.set_ylim(0, 60)
                ax.tick_params(axis='y', labelsize=14)

                #compute the mean and the standard error of mean
                mean = {}
                sem = {}
                for sex in ['male', 'female']:
                    mean[sex] = {}
                    sem[sex] = {}
                    for geno in ['WT', 'Del/+']:
                        mean[sex][geno] = np.mean(dataVal[sex][geno])
                        sem[sex][geno] = np.std(dataVal[sex][geno])/ np.sqrt(len(dataVal[sex][geno]))

                #plot the points for each value:
                ax.scatter(addJitter([1] * len(dataVal['male']['WT']), 0.2), dataVal['male']['WT'], color='blue', alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([2] * len(dataVal['male']['Del/+']), 0.2), dataVal['male']['Del/+'], color='darkorange', alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([4] * len(dataVal['female']['WT']), 0.2), dataVal['female']['WT'], color='blue', alpha=0.8, label="on", s=8)
                ax.scatter(addJitter([5] * len(dataVal['female']['Del/+']), 0.2), dataVal['female']['Del/+'], color='darkorange', alpha=0.8, label="on", s=8)

                #plot the mean and SEM on the graphs:
                ax.errorbar([1,2, 4,5], [mean['male']['WT'], mean['male']['Del/+'], mean['female']['WT'], mean['female']['Del/+']], [sem['male']['WT'], sem['male']['Del/+'], sem['female']['WT'], sem['female']['Del/+']], color='black', linestyle='None', marker='o')

                #conduct statistical testing: Mann-Whitney U test (non-parametric for non normal data with small sample size):
                xPos = {'male': 1.5, 'female': 4.5}
                for sex in ['male', 'female']:
                    try:
                        U, p = stats.mannwhitneyu( dataVal[sex]['WT'] , dataVal[sex]['Del/+'])
                        print('Mann-Whitney U-test for {} in {}: U={}, p={}'.format(val, sex, U, p))
                        ax.text(xPos[sex], max(max(dataVal[sex]['WT']), max(dataVal[sex]['Del/+'])), getStarsFromPvalues(pvalue=p, numberOfTests=2), fontsize=16)
                    except:
                        continue
                col += 1

            break

        if answer == 'pt':
            print('Plot trajectory during the preference test phase.')
            #traj of center of mass
            #traj of the nose position
            #sap
            #time spent sniffing the object
            timeSniff = {}
            #time spent around the object
            #body orientation toward each object
            files = getFilesToProcess()
            nbFiles = len(files)
            fig, axes = plt.subplots(nrows=3, ncols=5, figsize=(18, 16))

            nRow = 0
            nCol = 0

            for file in files:
                connection = sqlite3.connect(file)

                pool = AnimalPool()
                pool.loadAnimals(connection)
                animal = pool.animalDictionnary[1]

                #determine the startframe of the test phase:
                startTestFrame = getStartTestPhase(pool = pool)

                # set the axes.
                axLeft = axes[nRow][nCol]

                # draw the trajectory in the test phase
                pool.loadDetection(start=startTestFrame, end=startTestFrame + 15 * oneMinute)
                pool.filterDetectionByInstantSpeed(0, 70)
                plotZone(axLeft, colorEdge='lightgrey', colorFill='lightgrey')  # whole cage
                #object zones:
                for obj in [0,1,2,3]:
                    plotObjectZone(axLeft, colorFill=colorObjects[obj], x=objectPosition[animal.name][obj][0], y=-objectPosition[animal.name][obj][1], radius=radiusObjects[obj], alpha=0.5)
                    plotObjectZone(axLeft, colorFill=colorObjects[obj], x=objectPosition[animal.name][obj][0], y=-objectPosition[animal.name][obj][1], radius=radiusObjects[obj]+2/scaleFactor, alpha=0.2)  # object up left
                #trajectory:
                plotNoseTrajectory(axLeft, animal, title="Preference {}".format(animal.name), color="black")

                # add the frames where the animal is in SAP
                plotSapNose(axLeft, animal)
                dt1 = animal.getDistance(0, 10 * oneMinute)
                sap1 = len(animal.getSap(tmin=0, tmax=10 * oneMinute, xa=120, xb=250, ya=210, yb=340))

                timeSniff[animal.name] = {}
                selectedFrames = {}
                for obj in [0,1,2,3]:
                    selectedFrames[obj] = []
                noneVec = []
                onObjectX = []
                onObjectY = []
                for t in animal.detectionDictionnary.keys():
                    for obj in [0,1,2,3]:
                        distanceNose = animal.getDistanceNoseToPoint(t=t, xPoint=objectPosition[animal.name][obj][0], yPoint=objectPosition[animal.name][obj][1])
                        distanceMass = animal.getDistanceToPoint(t=t, xPoint=objectPosition[animal.name][obj][0], yPoint=objectPosition[animal.name][obj][1])
                        if distanceNose == None:
                            noneVec.append(t)
                            break
                        else:
                            if distanceNose <= radiusObjects[obj]+2/scaleFactor:
                                # check if the animal is on the object:
                                if distanceMass <= radiusObjects[obj]:
                                    detection = animal.detectionDictionnary.get(t)
                                    onObjectX.append(detection.massX)
                                    onObjectY.append(-detection.massY)
                                else:
                                    selectedFrames[obj].append(t)
                                '''
                                #Use of the height to detect whether animal is on the object not valid since Z is the height from the floor and objects are part of the floor
                                detection = animal.detectionDictionnary.get(t)

                                if (detection.massZ > 80) and (detection.backZ > 50):
                                    print('Mouse on the object at ', t)
                                    onObjectX.append(detection.massX)
                                    onObjectY.append(-detection.massY)
                                else:
                                    selectedFrames[obj].append(t)
                                '''

                for obj in [0, 1, 2, 3]:
                    timeSniff[animal.name][objectList[obj]] = len(selectedFrames[obj])
                timeSniff[animal.name]['noNose'] = len(noneVec)
                timeSniff[animal.name]['totalDetection'] = len(animal.detectionDictionnary.keys())
                timeSniff[animal.name]['totalSniff'] = timeSniff[animal.name][objectList[0]]+timeSniff[animal.name][objectList[1]]+timeSniff[animal.name][objectList[2]]+timeSniff[animal.name][objectList[3]]
                print('no distance computed: ', len(noneVec), ' over ', len(animal.detectionDictionnary.keys()))
                axLeft.scatter(onObjectX, onObjectY, color='blue', alpha=0.5, label="on", s=8)

                if nCol < 5:
                    nCol += 1
                if nCol >= 5:
                    nCol = 0
                    nRow += 1

            cup_patch = mpatches.Patch(color=colorObjects[0], alpha = 0.7, label='cup')
            flask_patch = mpatches.Patch(color=colorObjects[1], alpha = 0.7, label='flask')
            falcon_patch = mpatches.Patch(color=colorObjects[2], alpha = 0.7, label='falcon')
            shaker_patch = mpatches.Patch(color=colorObjects[3], alpha = 0.7, label='shaker')
            ax = axes[nRow, nCol]
            ax.legend(handles = [cup_patch, flask_patch, falcon_patch, shaker_patch])

            print(timeSniff)
            #plt.tight_layout(pad=2, h_pad=4, w_pad=0)
            plt.tight_layout()
            plt.show()

            fig1, axes = plt.subplots(nrows=1, ncols=2, figsize=(9, 4))
            jitterValue = 0.2

            ax = axes[0]
            yLabel = 'sniff time (s)'
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            xIndex = [1, 2, 3, 4]
            ax.set_xticks(xIndex)
            ax.set_xticklabels(objectList, rotation=45, FontSize=12, horizontalalignment='right')
            ax.set_ylabel(yLabel, FontSize=15)
            ax.legend().set_visible(False)
            ax.xaxis.set_tick_params(direction="in")
            ax.set_xlim(0, 5)
            ax.set_ylim(0,60)
            #ax.set_ylim(yMinUsv['nbUsvBurst'], yMaxUsv['nbUsvBurst'])
            ax.tick_params(axis='y', labelsize=14)
            timeDic = {}
            for obj in [0, 1, 2, 3]:
                timeDic[objectList[obj]] = []
                for id in timeSniff.keys():
                    ax.scatter(obj+1, timeSniff[id][objectList[obj]]/30, marker = 'o', c=colorDic[id], alpha=0.7)
                    timeDic[objectList[obj]].append(timeSniff[id][objectList[obj]]/30)
                ax.errorbar(obj + 1.2, np.mean(timeDic[objectList[obj]]), np.std(timeDic[objectList[obj]]), marker='o', color='black')

            ax = axes[1]
            yLabel = 'sniff time (%)'
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            xIndex = [1, 2, 3, 4]
            ax.set_xticks(xIndex)
            ax.set_xticklabels(objectList, rotation=45, FontSize=12,
                               horizontalalignment='right')
            ax.set_ylabel(yLabel, FontSize=15)
            ax.legend().set_visible(False)
            ax.xaxis.set_tick_params(direction="in")
            ax.set_ylim(0, 1)
            ax.set_xlim(0, 5)
            # ax.set_ylim(yMinUsv['nbUsvBurst'], yMaxUsv['nbUsvBurst'])
            ax.tick_params(axis='y', labelsize=14)
            ratioDic = {}
            for obj in [0, 1, 2, 3]:
                ratioDic[obj] = []
                for id in timeSniff.keys():
                    if timeSniff[id]['totalSniff'] == 0:
                        ratio = 0
                    else:
                        ratio = timeSniff[id][objectList[obj]]/timeSniff[id]['totalSniff']
                    ratioDic[obj].append(ratio)
                    ax.scatter(obj+1, ratio, marker='o', c=colorDic[id], alpha=0.7)
                ax.errorbar(obj+1.2, np.mean(ratioDic[obj]), np.std(ratioDic[obj]), marker='o', color='black')

            patch = {}
            legendList = []
            for id in timeSniff.keys():
                patch[id] = mpatches.Patch(color=colorDic[id], alpha=0.7, label=id)
                legendList.append(patch[id])

            plt.legend(handles = legendList, bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.show()

            with open('timeSniff.json', 'w') as jFile:
                json.dump(timeSniff, jFile, indent=4)
            print("json file created")
            break

        if answer == 'm':
            print('Plot sniffing time with manual scoring')
            file = 'C:/Users/eye/Documents/2020_10_novel_object_recognition/2020_12_object_pref_test/time_budget_export.xlsx'
            df = pd.read_excel( file, sheet_name= 'time_budget' )
            print(df)
            manualTimeSniff = {}
            for i in df.index:
                manualTimeSniff[df['Observations id'][i]] = {}
                manualTimeSniff[df['Observations id'][i]]['manualTotalSniff'] = df['tot_explo'][i]
                manualTimeSniff[df['Observations id'][i]][objectList[0]] = df['tot_dur_cup'][i]
                manualTimeSniff[df['Observations id'][i]][objectList[1]] = df['tot_dur_flask'][i]
                manualTimeSniff[df['Observations id'][i]][objectList[2]] = df['tot_dur_falcon'][i]
                manualTimeSniff[df['Observations id'][i]][objectList[3]] = df['tot_dur_shaker'][i]

            fig2, axes = plt.subplots(nrows=1, ncols=2, figsize=(9, 4))
            jitterValue = 0.2

            ax = axes[0]
            yLabel = 'sniff time (s)'
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            xIndex = [1, 2, 3, 4]
            ax.set_xticks(xIndex)
            ax.set_xticklabels(objectList, rotation=45, FontSize=12, horizontalalignment='right')
            ax.set_ylabel(yLabel, FontSize=15)
            ax.legend().set_visible(False)
            ax.xaxis.set_tick_params(direction="in")
            ax.set_xlim(0, 5)
            ax.set_ylim(0, 60)
            # ax.set_ylim(yMinUsv['nbUsvBurst'], yMaxUsv['nbUsvBurst'])
            ax.tick_params(axis='y', labelsize=14)
            timeDic = {}
            for obj in [0, 1, 2, 3]:
                timeDic[objectList[obj]] = []
                for id in manualTimeSniff.keys():
                    ax.scatter(obj + 1, manualTimeSniff[id][objectList[obj]], marker='o', c=colorDic[id], alpha=0.7)
                    timeDic[objectList[obj]].append(manualTimeSniff[id][objectList[obj]])
                ax.errorbar(obj + 1.2, np.mean(timeDic[objectList[obj]]), np.std(timeDic[objectList[obj]]), marker='o', color='black')

            ax = axes[1]
            yLabel = 'sniff time (%)'
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            xIndex = [1, 2, 3, 4]
            ax.set_xticks(xIndex)
            ax.set_xticklabels(objectList, rotation=45, FontSize=12, horizontalalignment='right')
            ax.set_ylabel(yLabel, FontSize=15)
            ax.legend().set_visible(False)
            ax.xaxis.set_tick_params(direction="in")
            ax.set_ylim(0, 1)
            ax.set_xlim(0, 5)
            # ax.set_ylim(yMinUsv['nbUsvBurst'], yMaxUsv['nbUsvBurst'])
            ax.tick_params(axis='y', labelsize=14)
            ratioDic = {}
            for obj in [0, 1, 2, 3]:
                ratioDic[objectList[obj]] = []
                for id in manualTimeSniff.keys():
                    if manualTimeSniff[id]['manualTotalSniff'] == 0:
                        ratio = 0
                    else:
                        ratio = manualTimeSniff[id][objectList[obj]] / manualTimeSniff[id]['manualTotalSniff']
                    ratioDic[objectList[obj]].append(ratio)
                    ax.scatter(obj + 1, ratio, marker='o', c=colorDic[id], alpha=0.7)
                ax.errorbar(obj + 1.2, np.mean(ratioDic[objectList[obj]]), np.std(ratioDic[objectList[obj]]), marker='o', color='black')

            patch = {}
            legendList = []
            for id in manualTimeSniff.keys():
                patch[id] = mpatches.Patch(color=colorDic[id], alpha=0.7, label=id)
                legendList.append(patch[id])

            plt.legend(handles=legendList, bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.show()

            with open('manualTimeSniff.json', 'w') as jFile:
                json.dump(manualTimeSniff, jFile, indent=4)
            print("json file created")
            break

        if answer == 'c':
            jsonFile = 'manualTimeSniff.json'
            with open(jsonFile) as json_data:
                dataManual = json.load(json_data)
            print("json file for manual estimation re-imported.")

            jsonFile = 'timeSniff.json'
            with open(jsonFile) as json_data:
                dataAuto = json.load(json_data)
            print("json file for automatic estimation re-imported.")

            fig2, axes = plt.subplots(nrows=1, ncols=4, figsize=(18, 4), sharey=True)

            for i in [0,1,2,3]:
                ax = axes[i]
                yLabel = 'sniff time auto'
                xLabel = 'sniff time manual'
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.set_xlabel(xLabel, FontSize=15)
                ax.set_ylabel(yLabel, FontSize=15)
                ax.legend().set_visible(False)
                ax.xaxis.set_tick_params(direction="in")
                ax.set_xlim(0, 60)
                ax.set_ylim(0, 60)
                ax.tick_params(axis='x', labelsize=14)
                ax.tick_params(axis='y', labelsize=14)
                ax.title.set_text(objectList[i])
                autoList = []
                manualList = []
                for id in dataAuto.keys():
                    ax.scatter(dataManual[id][objectList[i]], dataAuto[id][objectList[i]]/30, marker='o', c=colorDic[id], alpha=0.7)
                    autoList.append(dataAuto[id][objectList[i]]/30)
                    manualList.append(dataManual[id][objectList[i]])

                slope, intercept, r_value, p_value, std_err = stats.linregress(manualList, autoList)

                def predict(x):
                    return slope * np.array(x) + intercept

                fitLine = predict(manualList)
                ax.plot(manualList, fitLine, c='r')
                print(objectList[i])
                print( 'correlation: slope: {}, intercept: {}, r_value: {}, p-value: {}'.format(slope, intercept, r_value, p_value))



            patch = {}
            legendList = []
            for id in dataAuto.keys():
                patch[id] = mpatches.Patch(color=colorDic[id], alpha=0.7, label=id)
                legendList.append(patch[id])

            plt.legend(handles=legendList, bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.show()
            break