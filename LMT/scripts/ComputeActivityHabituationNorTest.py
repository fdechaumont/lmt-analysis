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
import seaborn as sns


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


def plotTrajectorySingleAnimal(file, ax, color, tmin, tmax, title, xa = 111, xb = 400, ya = 63, yb = 353):
    connection = sqlite3.connect(file) #connection to the database

    pool = AnimalPool()
    pool.loadAnimals(connection) #upload all the animals from the database
    animal = pool.animalDictionnary[1] #select one animal from the group of animals in the database

    # draw the trajectory in the habituation phase
    pool.loadDetection( start=tmin, end=tmax ) #upload all the detections for the animal (all frames where it has been detected)
    pool.filterDetectionByInstantSpeed(0, 70) #filter the detections to get rid of abberrant points (animals not detected and set at -1,-1); filter based on speed of the animal
    plotZone(ax, colorEdge='lightgrey', colorFill='lightgrey', xa = 111, xb = 400, ya = -353, yb = -63)  # draw the rectangle for the whole cage
    #plotZone(ax, colorEdge='lightgrey', colorFill='grey', xa=191, xb=320, ya=-273, yb=-143 ) # draw the rectangle for the center zone
    plotZone(ax, colorEdge='lightgrey', colorFill='grey', xa=168, xb=343, ya=-296, yb=-120)  # draw the rectangle for the center zone

    #plot(ax, animal, title=title, color="black") #plot the trajectory of the center of mass
    plotNoseTrajectory(ax, animal, title=title, color='black') #plot the trajectory of the nose
    plotSapNose(ax, animal, color = color, xa=xa, xb=xb, ya=ya, yb=yb) # add the frames where the animal is in SAP
    connection.close()

def buildFigTrajectoryMalesFemales(files, tmin, tmax, figName, colorSap, title, xa = 111, xb = 400, ya = 63, yb = 353):

    figM, axesM = plt.subplots(nrows=6, ncols=5, figsize=(14, 20))  # building the plot for trajectories
    figF, axesF = plt.subplots(nrows=8, ncols=5, figsize=(14, 25))  # building the plot for trajectories

    nRow = {'male': 0, 'female': 0}  # initialisation of the row
    nCol = {'male': 0, 'female': 0}  # initialisation of the column

    tminHab = tmin  # start time of the computation
    tmaxHab = tmax  # end time of the computation

    for file in files:
        connection = sqlite3.connect(file)  # connection to the database

        pool = AnimalPool()
        pool.loadAnimals(connection)  # upload all the animals from the database
        animal = pool.animalDictionnary[1]

        if animal.sex == 'male':
            # set the axes. Check the number of file to get the dimension of axes and grab the correct ones.
            ax = axesM[nRow['male']][nCol['male']]  # set the subplot where to draw the plot
            plotTrajectorySingleAnimal(file, color=colorSap[animal.genotype], ax=ax, tmin=tminHab,
                                       tmax=tmaxHab, title=title, xa = 111, xb = 400, ya = 63, yb = 353)  # function to draw the trajectory

            if nCol['male'] < 5:
                nCol['male'] += 1
            if nCol['male'] >= 5:
                nCol['male'] = 0
                nRow['male'] += 1

        if animal.sex == 'female':
            # set the axes. Check the number of file to get the dimension of axes and grab the correct ones.
            ax = axesF[nRow['female']][nCol['female']]  # set the subplot where to draw the plot
            plotTrajectorySingleAnimal(file, color=colorSap[animal.genotype], ax=ax, tmin=tminHab,
                                       tmax=tmaxHab, title=title, xa = 111, xb = 400, ya = 63, yb = 353)  # function to draw the trajectory

            if nCol['female'] < 5:
                nCol['female'] += 1
            if nCol['female'] >= 5:
                nCol['female'] = 0
                nRow['female'] += 1
        connection.close()

    figM.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
    # plt.show() #display the plot
    figM.savefig('{}_males.pdf'.format(figName), dpi=200)
    figF.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
    figF.savefig('{}_females.pdf'.format(figName), dpi=200)

def getColorGeno(geno):
    if geno == 'WT':
        color = 'steelblue'
    else:
        color = 'darkorange'
    return color


def plotVariablesHabituationNor(col, axes, sexList, genoList, data, val, unitDic, yMinDic, yMaxDic ):
    # reformate the data dictionary to get the correct format of data for plotting and statistical analyses
    dataVal = {}
    for sex in sexList:
        dataVal[sex] = {}
        for geno in genoList:
            dataVal[sex][geno] = []
            for rfid in data[val][sex][geno].keys():
                dataVal[sex][geno].append(data[val][sex][geno][rfid])

    ax = axes[col]
    yLabel = '{} ({})'.format(val, unitDic[val])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    xIndex = [1, 2, 4, 5]
    ax.set_xticks(xIndex)
    ax.set_xticklabels(genoList+genoList, rotation=0, fontsize=14, horizontalalignment='center')
    ax.set_ylabel(yLabel, fontsize=16)
    ax.legend().set_visible(False)
    ax.xaxis.set_tick_params(direction="in")
    ax.set_xlim(0, 6)
    ax.set_ylim(yMinDic[val], yMaxDic[val])
    ax.tick_params(axis='y', labelsize=14)
    ax.text(1.5, yMaxDic[val] , sexList[0]+'s', horizontalalignment= 'center', fontsize=16)
    ax.text(4.5, yMaxDic[val] , sexList[1]+'s', horizontalalignment='center', fontsize=16)

    # compute the mean and the standard error of mean
    mean = {}
    sem = {}
    for sex in sexList:
        mean[sex] = {}
        sem[sex] = {}
        for geno in genoList:
            mean[sex][geno] = np.mean(dataVal[sex][geno])
            sem[sex][geno] = np.std(dataVal[sex][geno]) / np.sqrt(len(dataVal[sex][geno]))

    # plot the points for each value:
    n = 0
    for sex in sexList:
        for geno in genoList:
            ax.scatter(addJitter([xIndex[n]] * len(dataVal[sex][geno]), 0.2), dataVal[sex][geno], color=getColorGeno(geno), alpha=0.8,
                       label="on", s=8)

            n += 1

    # plot the mean and SEM on the graphs:
    ax.errorbar(xIndex,
                [mean['male']['WT'], mean['male']['Del/+'], mean['female']['WT'], mean['female']['Del/+']],
                [sem['male']['WT'], sem['male']['Del/+'], sem['female']['WT'], sem['female']['Del/+']], color='black',
                linestyle='None', marker='o')

    # conduct statistical testing: Mann-Whitney U test (non-parametric for non normal data with small sample size):
    xPos = {'male': 1.5, 'female': 4.5}
    for sex in sexList:
        try:
            U, p = stats.mannwhitneyu(dataVal[sex]['WT'], dataVal[sex]['Del/+'])
            print('Mann-Whitney U-test for {} in {}: U={}, p={}'.format(val, sex, U, p))
            ax.text(xPos[sex], yMaxDic[val] - 0.1 * (yMaxDic[val]-yMinDic[val]),
                    getStarsFromPvalues(pvalue=p, numberOfTests=1), horizontalalignment='center',fontsize=20)
        except:
            print('stats problem!')
            continue


def plotVariablesHabituationNorBoxplots(ax, sexList, genoList, data, val, unitDic, yMinDic, yMaxDic ):
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
    '''for patch in bp.artists:
        r, g, b, a = patch.get_facecolor()
        patch.set_facecolor((r, g, b, .7))'''

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
            ax.text(xPos[sex], yMaxDic[val] - 0.1 * (yMaxDic[val]-yMinDic[val]),
                    getStarsFromPvalues(pvalue=p, numberOfTests=1), horizontalalignment='center', fontsize=20, weight='bold')
        except:
            print('stats problem!')
            continue


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
        question += "\n\t [r]ebuild all events?"
        question += "\n\t [ph]lot trajectories in the habituation phase?"
        question += "\n\t [p] plot the distance and anxiety measures in the habituation phase?"
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
            #plot the trajectories, with SAP only in the inner zone of the cage to avoid SAP against the walls
            buildFigTrajectoryMalesFemales(files=files, tmin=0, tmax=15*oneMinute, figName='fig_traj_hab_nor', colorSap=colorSap, title='hab d1', xa=128, xb=383, ya=80, yb=336)

            print('Compute distance travelled, number of SAP displayed, and rearing.')

            data = {}
            for val in variableList:
                data[val] = {}
                for sex in ['male', 'female']:
                    data[val][sex] = {}
                    for geno in ['WT', 'Del/+']:
                        data[val][sex][geno] = {}
            tminHab = 0
            tmaxHab = 15*oneMinute

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

        if answer == 'p':

            # open the json file
            jsonFileName = "habituationDay1.json"
            with open(jsonFileName) as json_data:
                data = json.load(json_data)
            print("json file re-imported.")

            sexList = ['male', 'female']
            genoList = ['WT', 'Del/+']


            fig, axes = plt.subplots(nrows=1, ncols=len(variableList), figsize=(4*len(variableList), 4)) #create the figure for the graphs of the computation

            col = 0 #initialise the column number

            for val in variableList:
                plotVariablesHabituationNorBoxplots(ax=axes[col], sexList=sexList, genoList=genoList, data=data, val=val, unitDic=unitDic, yMinDic=yMinDic, yMaxDic=yMaxDic)

                col += 1

            #plt.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
            plt.tight_layout()
            plt.show()  # display the plot
            fig.savefig('fig_values_hab_nor.pdf', dpi=200)
            print('Job done.')
            break

