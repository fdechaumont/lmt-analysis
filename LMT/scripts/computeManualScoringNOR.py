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
from scripts.ComputeObjectRecognition import *



def computeSniffTimeNoSetup(files, exp, phase, objectDic):

    print('Compute time of exploration.')
    vibrissae = 3  # estimated size of the vibrissae to determine the contact zone with the object
    data = {}
    for val in ['sniffLeft', 'sniffRight', 'onLeftObject', 'onRightObject', 'totalSniff']:
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
        sex = animal.sex
        geno = animal.genotype
        setup = int(animal.setup)
        print(setup)
        rfid = animal.RFID
        object = objectDic[setup][exp][phase][0]

        # determine the startframe of the test phase:
        if phase == 'same':
            tmin = getStartTestPhase(pool=pool)
        if phase == 'diff':
            tmin = 0
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
                    if distanceNose <= radiusObjects[object] + vibrissae / scaleFactor:
                        # check if the animal is on the object:
                        if distanceMass <= radiusObjects[object]:
                            detection = animal.detectionDictionnary.get(t)
                            onObjectX[obj].append(detection.massX)
                            onObjectY[obj].append(-detection.massY)
                        else:
                            selectedFrames[obj].append(t)

        data['sniffLeft'][sex][geno][rfid] = len(selectedFrames['left'])
        data['sniffRight'][sex][geno][rfid] = len(selectedFrames['right'])
        data['totalSniff'][sex][geno][rfid] = data['sniffLeft'][sex][geno][rfid] + data['sniffRight'][sex][geno][rfid]

    return data

if __name__ == '__main__':

    print("Code launched.")
    # set font
    from matplotlib import rc, gridspec

    pd.set_option('display.max_rows', 20)
    pd.set_option('display.max_columns', 20)

    rc('font', **{'family': 'serif', 'serif': ['Arial']})

    objectPosition = {1: {'left': (190, -152), 'right': (330, -152)},
                      2: {'left': (186, -152), 'right': (330, -152)}
                      }

    # object information
    objectDic = {1: {'short': {'same': ('cup', 'cup'), 'diff': ('cup', 'shaker')},
                     'medium': {'same': ('falcon', 'falcon'), 'diff': ('falcon', 'flask')}},
                 2: {'short': {'same': ('falcon', 'falcon'), 'diff': ('falcon', 'flask')},
                     'medium': {'same': ('cup', 'cup'), 'diff': ('cup', 'shaker')}}
                 }

    radiusObjects = {'cup': 18, 'flask': 15, 'falcon': 9, 'shaker': 11}

    expList = ['short', 'medium']
    #expList = ['short']

    while True:
        question = "Do you want to:"
        question += "\n\t [p]lot sniffing time with manual scoring?"
        question += "\n\t [r]ecompute automatic detection to compare with manual scoring?"
        question += "\n\t [c]ompare manual scoring with automatic detection?"
        question += "\n"
        answer = input(question)

        if answer == 'p':
            print('Plot sniffing time with manual scoring')
            file = 'C:/Users/eye/Documents/2020_09_biblio_16p11/2021_01_NOR/nor short/time_budget_ee.xlsx'
            df = pd.read_excel( file, sheet_name= 'time_budget_short_same_ee' )
            print(df)

            annotatePlot = True

            manualTimeSniff = {}
            for exp in expList:
                manualTimeSniff[exp] = {}
                for phase in ['same', 'diff']:
                    manualTimeSniff[exp][phase] = {}
                    for sex in ['male', 'female']:
                        manualTimeSniff[exp][phase][sex] = {}
                        for side in ['left', 'right', 'total', 'ratio_left', 'ratio_right']:
                            manualTimeSniff[exp][phase][sex][side] = {}
                            for geno in ['WT', 'Del/+']:
                                manualTimeSniff[exp][phase][sex][side][geno] = {}


            for i in df.index:
                exp = df['test'][i]
                phase = df['phase'][i]
                geno = df['genotype'][i]
                sex = df['sex'][i]
                ind = df['Observations id'][i][-4:]
                manualTimeSniff[exp][phase][sex]['left'][df['genotype'][i]][ind] = df['tot_dur_left'][i]
                manualTimeSniff[exp][phase][sex]['right'][df['genotype'][i]][ind] = df['tot_dur_right'][i]
                manualTimeSniff[exp][phase][sex]['total'][df['genotype'][i]][ind] = df['tot_dur_left'][i] + df['tot_dur_right'][i]
                if ((df['tot_dur_left'][i] + df['tot_dur_right'][i]) >= 5):
                    manualTimeSniff[exp][phase][sex]['ratio_left'][df['genotype'][i]][ind] = df['tot_dur_left'][i] / (df['tot_dur_left'][i] + df['tot_dur_right'][i])
                    manualTimeSniff[exp][phase][sex]['ratio_right'][df['genotype'][i]][ind] = df['tot_dur_right'][i] / (df['tot_dur_left'][i] + df['tot_dur_right'][i])


            fig2, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 8))
            jitterValue = 0.2
            row = 0

            for exp in expList:
                col = 0
                for phase in ['same', 'diff']:
                    ax = axes[row][col]
                    yLabel = 'ratio sniff time'
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    xIndex = [1, 2.5, 4.5, 6]
                    ax.set_xticks(xIndex)
                    ax.set_xticklabels(['WT M', 'Del/+ M', 'WT F', 'Del/+ F'], rotation=45, FontSize=12, horizontalalignment='right')
                    ax.set_ylabel(yLabel, FontSize=15)
                    ax.legend().set_visible(False)
                    ax.xaxis.set_tick_params(direction="in")
                    ax.set_xlim(0, 7)
                    ax.set_ylim(0, 1.2)
                    ax.tick_params(axis='y', labelsize=14)
                    ax.axhline(y=0.5, color='black')
                    sex = 'male'
                    for ind in manualTimeSniff[exp][phase][sex]['ratio_left']['WT'].keys():
                        ax.scatter(xIndex[0]-0.5, manualTimeSniff[exp][phase][sex]['ratio_left']['WT'][ind], marker='o', c='blue', alpha=0.7)
                        ax.scatter(xIndex[0]+0.5, manualTimeSniff[exp][phase][sex]['ratio_right']['WT'][ind], marker='o', c='blue', alpha=0.7)
                    for ind in manualTimeSniff[exp][phase][sex]['ratio_left']['Del/+'].keys():
                        ax.scatter(xIndex[1] - 0.5, manualTimeSniff[exp][phase][sex]['ratio_left']['Del/+'][ind], marker='o', c='darkorange', alpha=0.7)
                        ax.scatter(xIndex[1] + 0.5, manualTimeSniff[exp][phase][sex]['ratio_right']['Del/+'][ind], marker='o', c='darkorange', alpha=0.7)

                    sex = 'female'
                    for ind in manualTimeSniff[exp][phase][sex]['ratio_left']['WT'].keys():
                        ax.scatter(xIndex[2] - 0.5, manualTimeSniff[exp][phase][sex]['ratio_left']['WT'][ind], marker='o', c='blue', alpha=0.7)
                        ax.scatter(xIndex[2] + 0.5, manualTimeSniff[exp][phase][sex]['ratio_right']['WT'][ind], marker='o', c='blue', alpha=0.7)
                    for ind in manualTimeSniff[exp][phase][sex]['ratio_left']['Del/+'].keys():
                        ax.scatter(xIndex[3] - 0.5, manualTimeSniff[exp][phase][sex]['ratio_left']['Del/+'][ind], marker='o', c='darkorange', alpha=0.7)
                        ax.scatter(xIndex[3] + 0.5, manualTimeSniff[exp][phase][sex]['ratio_right']['Del/+'][ind], marker='o', c='darkorange', alpha=0.7)

                    if annotatePlot == True:
                        sex = 'male'
                        for ind in manualTimeSniff[exp][phase][sex]['ratio_left']['WT'].keys():
                            ax.annotate(ind, (xIndex[0] - 0.4, manualTimeSniff[exp][phase][sex]['ratio_left']['WT'][ind]), fontsize=8)
                            ax.annotate(ind, (xIndex[0] + 0.1, manualTimeSniff[exp][phase][sex]['ratio_right']['WT'][ind]), fontsize=8)
                        for ind in manualTimeSniff[exp][phase][sex]['ratio_left']['Del/+'].keys():
                            ax.annotate(ind, (xIndex[1] - 0.4, manualTimeSniff[exp][phase][sex]['ratio_left']['Del/+'][ind]), fontsize=8)
                            ax.annotate(ind, (xIndex[1] + 0.1, manualTimeSniff[exp][phase][sex]['ratio_right']['Del/+'][ind]), fontsize=8)

                        sex = 'female'
                        for ind in manualTimeSniff[exp][phase][sex]['ratio_left']['WT'].keys():
                            ax.annotate(ind, (xIndex[2] - 0.4, manualTimeSniff[exp][phase][sex]['ratio_left']['WT'][ind]), fontsize=8)
                            ax.annotate(ind, (xIndex[2] + 0.1, manualTimeSniff[exp][phase][sex]['ratio_right']['WT'][ind]), fontsize=8)
                        for ind in manualTimeSniff[exp][phase][sex]['ratio_left']['Del/+'].keys():
                            ax.annotate(ind, (xIndex[3] - 0.4, manualTimeSniff[exp][phase][sex]['ratio_left']['Del/+'][ind]), fontsize=8)
                            ax.annotate(ind, (xIndex[3] + 0.1, manualTimeSniff[exp][phase][sex]['ratio_right']['Del/+'][ind]), fontsize=8)


                    # conduct statistical testing: one sample Student t-test:
                    T = {}
                    p = {}
                    for sex in ['male', 'female']:
                        T[sex] = {}
                        p[sex] = {}
                        for geno in ['WT', 'Del/+']:
                            prop = []
                            for ind in manualTimeSniff[exp][phase][sex]['ratio_left'][geno].keys():
                                prop.append(manualTimeSniff[exp][phase][sex]['ratio_left'][geno][ind])
                            T[sex][geno], p[sex][geno] = stats.ttest_1samp(a=prop, popmean=0.5)
                            print('One-sample Student T-test for {} {} {} {} {}: T={}, p={}'.format(exp, phase, len(prop), sex, geno, T[sex][geno], p[sex][geno]))
                            #ax.text(xPos[sex][geno], 1.1, getStarsFromPvalues(pvalue=p[sex][geno], numberOfTests=1), fontsize=16)

                    col += 1
                row += 1

            plt.tight_layout()
            plt.show()
            fig2.savefig('figure_manul_sniff.pdf', dpi=300)

            with open('manualTimeSniff.json', 'w') as jFile:
                json.dump(manualTimeSniff, jFile, indent=4)
            print("json file created")

            break

        if answer == 'r':
            print('Recompute automatic detection to be able to compare with manual scoring')
            question = "Is it the short or medium retention time? (short / medium)"
            exp = input(question)
            question = "Is it the same or diff phase? (same / diff)"
            phase = input(question)
            files = getFilesToProcess()

            ##############
            data = computeSniffTimeNoSetup(files, exp= exp, phase=phase, objectDic=objectDic)

            # store the data dictionary in a json file
            with open('auto_sniff_time_{}_{}.json'.format(exp, phase), 'w') as jFile:
                json.dump(data, jFile, indent=4)
            print("json file created")
            break

        if answer == 'c':
            print('Compare manual scoring with automatic detection')
            #store manual data in a dictionary
            file = 'C:/Users/eye/Documents/2020_09_biblio_16p11/2021_01_NOR/nor short/time_budget_ee.xlsx'
            df = pd.read_excel( file, sheet_name= 'time_budget_short_same_ee' )
            print(df)
            manualTimeSniff = {}
            for exp in expList:
                manualTimeSniff[exp] = {}
                for phase in ['same', 'diff']:
                    manualTimeSniff[exp][phase] = {}
                    for side in ['sniffLeft', 'sniffRight', 'totalSniff']:
                        manualTimeSniff[exp][phase][side] = {}
                        for sex in ['male', 'female']:
                            manualTimeSniff[exp][phase][side][sex] = {}
                            for geno in ['WT', 'Del/+']:
                                manualTimeSniff[exp][phase][side][sex][geno] = {}

            for i in df.index:
                exp = df['test'][i]
                phase = df['phase'][i]
                geno = df['genotype'][i]
                sex = df['sex'][i]
                ind = '00103812{}'.format(df['Observations id'][i][-4:]) #to obtain the same dic keys as in automatic measures
                #print('data: ', exp, phase, geno, sex, ind )
                manualTimeSniff[exp][phase]['sniffLeft'][sex][df['genotype'][i]][ind] = df['tot_dur_left'][i]
                manualTimeSniff[exp][phase]['sniffRight'][sex][df['genotype'][i]][ind] = df['tot_dur_right'][i]
                manualTimeSniff[exp][phase]['totalSniff'][sex][df['genotype'][i]][ind] = df['tot_dur_left'][i] + df['tot_dur_right'][i]


            #store automatic data in a dictionary
            autoTimeSniff = {}
            for exp in expList:
                autoTimeSniff[exp] = {}
                jsonFileName = "auto_sniff_time_{}_same.json".format(exp)
                with open(jsonFileName) as json_data:
                    autoTimeSniff[exp]['same'] = json.load(json_data)
                jsonFileName = "auto_sniff_time_{}_diff.json".format(exp)
                with open(jsonFileName) as json_data:
                    autoTimeSniff[exp]['diff'] = json.load(json_data)

            colorSex = {'female': 'red', 'male': 'black'}
            markerDic = {'female': 'o', 'male': 'v'}
            colorDic = {'WT': 'steelblue', 'Del/+': 'darkorange'}

            fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 8), sharex=True, sharey=True)
            row = 0
            for exp in expList:
                col = 0
                for phase in ['same', 'diff']:
                    ax = axes[row][col]
                    yLabel = 'manual sniff time'
                    xLabel = 'auto sniff time'
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.set_xlabel(xLabel, FontSize=15)
                    ax.set_ylabel(yLabel, FontSize=15)
                    ax.legend().set_visible(False)
                    ax.xaxis.set_tick_params(direction="in")
                    ax.yaxis.set_tick_params(direction="in")
                    ax.tick_params(axis='x', labelsize=14)
                    ax.tick_params(axis='y', labelsize=14)
                    ax.set_xlim(0, 50)
                    ax.set_ylim(0, 50)
                    ax.title.set_text('{} {}'.format(exp, phase))

                    for sex in ['male']:
                        autoList = []
                        manualList = []
                        for geno in ['WT', 'Del/+']:
                            x = []
                            y = []

                            for id in autoTimeSniff[exp][phase]['sniffLeft'][sex][geno].keys():
                                #print(id, autoTimeSniff[exp][phase]['sniffLeft'][sex][geno][id]/30, manualTimeSniff[exp][phase]['sniffLeft'][sex][geno][id] )
                                x.append(autoTimeSniff[exp][phase]['sniffLeft'][sex][geno][id]/30)
                                y.append(manualTimeSniff[exp][phase]['sniffLeft'][sex][geno][id])
                                ax.annotate(id[-4:], (x+1, y+1), fontsize=5)
                            '''
                            for id in autoTimeSniff[exp][phase]['sniffRight'][sex][geno].keys():
                                #print(id, autoTimeSniff[exp][phase]['sniffLeft'][sex][geno][id]/30, manualTimeSniff[exp][phase]['sniffLeft'][sex][geno][id] )
                                x.append(autoTimeSniff[exp][phase]['sniffRight'][sex][geno][id]/30)
                                y.append(manualTimeSniff[exp][phase]['sniffRight'][sex][geno][id])
                            '''
                            autoList.extend(x)
                            manualList.extend(y)
                            ax.scatter(x, y, marker=markerDic[sex], c=colorDic[geno], alpha=0.7)

                        slope, intercept, r_value, p_value, std_err = stats.linregress(autoList, manualList)
                        def predict(x):
                            return slope * np.array(x) + intercept

                        fitLine = predict(autoList)
                        ax.plot(autoList, fitLine, c=colorSex[sex])
                        print('correlation: slope: {}, intercept: {}, r_value: {}, p-value: {}'.format(slope, intercept, r_value, p_value))

                    ax.plot([0,50], [0,50], c='black', alpha=0.3)


                    col += 1
                row += 1

            plt.tight_layout()
            fig.show()

            break