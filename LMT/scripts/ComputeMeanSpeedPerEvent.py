'''
Created on 10. May 2021

@author: Elodie
'''

import matplotlib.pyplot as plt
from lmtanalysis.Animal import *
from lmtanalysis.Event import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.Measure import *
import numpy as np; np.random.seed(0)
from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import getMinTMaxTAndFileNameInput, getMinTMaxTInput
import sqlite3
import seaborn as sns
from lmtanalysis.FileUtil import getFilesToProcess, getJsonFileToProcess

from scripts.ComputeMeasuresIdentityProfileOneMouseAutomatic import *

#from LMT.USV.usvEventsCorrelations.Compute_Speed_Duration_Events_With_USV import *
from scipy.spatial.transform import rotation
#from LMT.USV.figure.figParameter import *
from _collections import OrderedDict

from lmtanalysis.Util import getFileNameInput, getStarsFromPvalues, addJitter
from scipy.stats import mannwhitneyu, wilcoxon
from lmtanalysis.BehaviouralSequencesUtil import genoListGeneral, genoList
#from scipy.stats.morestats import wilcoxon

def computeSpeedDurationPerEvent(animalData, files, tmin, tmax, eventToTest=None):
    print("Compute the speed and duration of specific events ")
    for file in files:
        connection = sqlite3.connect(file)
        pool = AnimalPool()
        pool.loadAnimals(connection)
        pool.loadDetection(tmin, tmax, lightLoad=True)
        rfidList = []
        for animal in pool.animalDictionary.keys():
            print("computing individual animal: {}".format(animal))
            rfid = pool.animalDictionary[animal].RFID
            rfidList.append(rfid)

        group = rfidList[0]
        for n in range(1, len(rfidList)):
            group=group+'-'+rfidList[n]

        animalData[file] = {}

        nightEventTimeLine = EventTimeLineCached(connection, file, "night", minFrame=tmin, maxFrame=tmax)
        
        if nightEventTimeLine.getNumberOfEvent(minFrame=tmin, maxFrame=tmax) == 0:
            n = 0
            minT = tmin
            maxT = tmax
            
            animalData[file][n] = {}

            for animal in pool.animalDictionary.keys():
                print("computing individual animal: {}".format(animal))
                rfid = pool.animalDictionary[animal].RFID
                print("RFID: {}".format(rfid))
                animalData[file][n][rfid] = {}
                # store the animal
                animalData[file][n][rfid]["animal"] = pool.animalDictionary[animal].name
                animalObject = pool.animalDictionary[animal]
                animalData[file][n][rfid]["file"] = file
                animalData[file][n][rfid]['genotype'] = pool.animalDictionary[animal].genotype
                animalData[file][n][rfid]['sex'] = pool.animalDictionary[animal].sex
                animalData[file][n][rfid]['strain'] = pool.animalDictionary[animal].strain
                animalData[file][n][rfid]['age'] = pool.animalDictionary[animal].age
                animalData[file][n][rfid]['group'] = group

                print("computing individual event: {}".format(eventToTest))

                behavEventTimeLine = EventTimeLineCached(connection, file, eventToTest, animal, minFrame=minT, maxFrame=maxT)
                #clean the behavioural event timeline:
                behavEventTimeLine.mergeCloseEvents(numberOfFrameBetweenEvent=1)
                behavEventTimeLine.removeEventsBelowLength(maxLen=3)
                animalData[file][n][rfid]['DurationSpeed'] = []
                animalData[file][n][rfid]['speed'] = []
                animalData[file][n][rfid]['distance'] = []
                for event in behavEventTimeLine.getEventList():
                    results = getDurationSpeedDistance(event=event, animal=animalObject)
                    #print('duration, speed: ', results)
                    animalData[file][n][rfid]['DurationSpeed'].append( results )
                    animalData[file][n][rfid]['speed'].append(results[1])
                    animalData[file][n][rfid]['distance'].append(results[2])
        
        else:
            n = 1
            for eventNight in nightEventTimeLine.getEventList():
                minT = eventNight.startFrame
                maxT = eventNight.endFrame
                print("Night: ", n)
                animalData[file][n] = {}
    
                for animal in pool.animalDictionary.keys():
                    print("computing individual animal: {}".format(animal))
                    rfid = pool.animalDictionary[animal].RFID
                    print("RFID: {}".format(rfid))
                    animalData[file][n][rfid] = {}
                    # store the animal
                    animalData[file][n][rfid]["animal"] = pool.animalDictionary[animal].name
                    animalObject = pool.animalDictionary[animal]
                    animalData[file][n][rfid]["file"] = file
                    animalData[file][n][rfid]['genotype'] = pool.animalDictionary[animal].genotype
                    animalData[file][n][rfid]['sex'] = pool.animalDictionary[animal].sex
                    animalData[file][n][rfid]['strain'] = pool.animalDictionary[animal].strain
                    animalData[file][n][rfid]['age'] = pool.animalDictionary[animal].age
                    animalData[file][n][rfid]['group'] = group
    
                    print("computing individual event: {}".format(eventToTest))
    
                    behavEventTimeLine = EventTimeLineCached(connection, file, eventToTest, animal, minFrame=minT, maxFrame=maxT)
                    #clean the behavioural event timeline:
                    behavEventTimeLine.mergeCloseEvents(numberOfFrameBetweenEvent=1)
                    behavEventTimeLine.removeEventsBelowLength(maxLen=3)
                    animalData[file][n][rfid]['DurationSpeed'] = []
                    animalData[file][n][rfid]['speed'] = []
                    animalData[file][n][rfid]['distance'] = []
                    for event in behavEventTimeLine.getEventList():
                        results = getDurationSpeedDistance(event=event, animal=animalObject)
                        #print('duration, speed: ', results)
                        animalData[file][n][rfid]['DurationSpeed'].append( results )
                        animalData[file][n][rfid]['speed'].append(results[1])
                        animalData[file][n][rfid]['distance'].append(results[2])
    
                n += 1
        connection.close()

    with open("durationSpeedData_{}.json".format(eventToTest), 'w') as jFile:
        json.dump(animalData, jFile, indent=3)

    print("json file created for all data")


def getDurationSpeedDistance(event, animal):
                    
    duration = event.duration()
    sum = 0
    for t in range ( event.startFrame, event.endFrame+1 ) :
        speed = animal.getSpeed(t)
        if ( speed != None ):
            sum+= speed
    
    meanSpeed = sum / event.duration()
    
    distance = animal.getDistance(tmin=event.startFrame, tmax=event.endFrame)
    
    return ( duration, meanSpeed, distance )


def plotBoxplotSpeedPerEvent(dataDic, ax, eventToTest, n):
    y = dataDic["meanValue"]
    x = dataDic["genotype"]
    genotypeType = list(Counter(x).keys())
    print(genotypeType)
    group = dataDic["exp"]

    print("y: ", y)
    print("x: ", x)
    print("group: ", group)
    experimentType = Counter(group)
    print("Nb of experiments: ", len(experimentType))

    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(min(y) - 0.2 * max(y), max(y) + 0.2 * max(y))
    sns.boxplot(x, y, order=[genotypeType[1], genotypeType[0]], ax=ax, linewidth=0.5, showmeans=True,
                meanprops={"marker": 'o',
                           "markerfacecolor": 'white',
                           "markeredgecolor": 'black',
                           "markersize": '8'}, showfliers=False, width=0.4)
    sns.stripplot(x, y, order=[genotypeType[1], genotypeType[0]], jitter=True, color='black', hue=group, s=5,
                  ax=ax)
    ax.set_title('{} night {}'.format(eventToTest, n))
    ax.set_ylabel("mean speed (cm/s)")
    ax.legend().set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
def plotBoxplotValSpeedPerEvent(dataDic, ax, eventToTest, n, label):
    y = dataDic["meanValue"]
    x = dataDic["genotype"]
    genotypeType = list(Counter(x).keys())
    print(genotypeType)
    group = dataDic["exp"]

    print("y: ", y)
    print("x: ", x)
    print("group: ", group)
    experimentType = Counter(group)
    print("Nb of experiments: ", len(experimentType))

    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(min(y) - 0.2 * max(y), max(y) + 0.2 * max(y))
    sns.boxplot(x, y, order=[genotypeType[1], genotypeType[0]], ax=ax, linewidth=0.5, showmeans=True,
                meanprops={"marker": 'o',
                           "markerfacecolor": 'white',
                           "markeredgecolor": 'black',
                           "markersize": '8'}, showfliers=False, width=0.4)
    sns.stripplot(x, y, order=[genotypeType[1], genotypeType[0]], jitter=True, color='black', hue=group, s=5,
                  ax=ax)
    ax.set_title('{} night {}'.format(eventToTest, n))
    ax.set_ylabel(label)
    ax.legend().set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)


def plotBoxplotSpeedPerEventPerSex(dataDic, ax, eventToTest, age):
    dfData = pandas.DataFrame({'group': dataDic["exp"],
                               'age': dataDic["age"],
                               'sex': dataDic["sex"],
                               'value': dataDic["meanValue"]})
    print(dfData)

    dfDataAge = dfData.loc[dfData['age'] == age, :]
    print(dfDataAge)
    y = dfDataAge["value"]
    x = dfDataAge["sex"]

    group = dfDataAge["group"]

    print("y: ", y)
    print("x: ", x)
    print("group: ", group)
    experimentType = Counter(group)
    print("Nb of experiments: ", len(experimentType))

    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(min(y) - 0.2 * max(y), max(y) + 0.2 * max(y))
    sns.boxplot(x, y, order=['male', 'female'], ax=ax, linewidth=0.5, showmeans=True,
                meanprops={"marker": 'o',
                           "markerfacecolor": 'white',
                           "markeredgecolor": 'black',
                           "markersize": '8'}, showfliers=False, width=0.4)
    sns.stripplot(x, y, order=['male', 'female'], jitter=True, color='black', hue=group, s=5,
                  ax=ax)
    ax.set_title('{} night {}'.format(eventToTest, n))
    ax.set_ylabel("mean speed (cm/s)")
    ax.legend().set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)


def testSpeedData(profileData=None, night=0, event=None ):

    print("event: ", event, 'night: ', night)

    profileValueDictionary = getProfileValues(profileData=profileData, night=night, event=event)

    dfData = pandas.DataFrame({'group': profileValueDictionary["exp"],
                               'genotype': profileValueDictionary["genotype"],
                               'value': profileValueDictionary["meanValue"]})

    # Mixed model: variable to explain: value; fixed factor = genotype; random effect: group
    # create model:
    model = smf.mixedlm("value ~ genotype", dfData, groups=dfData["group"])
    # run model:
    result = model.fit()
    # print summary
    print(result.summary())

def testSpeedDataBetweenSexes(profileData=None, night=0, event=None, age=None ):

    print("event: ", event, 'night: ', night, 'age: ', age)

    profileValueDictionary = getProfileValuesNoGroup(profileData=profileData, night=night, event=event)

    dfData = pandas.DataFrame({'group': profileValueDictionary["exp"],
                               'age': profileValueDictionary["age"],
                               'sex': profileValueDictionary["sex"],
                               'value': profileValueDictionary["meanValue"]})

    dfDataAge = dfData.loc[dfData['age'] == age, :]

    # Mixed model: variable to explain: value; fixed factor = genotype; random effect: group
    # create model:
    model = smf.mixedlm("value ~ sex", dfDataAge, groups=dfDataAge["group"])
    # run model:
    result = model.fit()
    # print summary
    print(result.summary())


def createDataframeFromDicDiffGenoShortLongTerm( dic, variable, nightDic, term ):
                
    dataDic = { 'rfid': [], 'strain': [], 'sex': [], 'geno': [], 'group': [], 'variable': [], 'term': [] }
    lenList = 0
    for file in dic.keys():
        for rfid in dic[file][nightDic[term]].keys():
            print('##########', rfid)
            nbData = len( dic[file][nightDic[term]][rfid][variable] )
            print(variable, nbData)
            print("#", [dic[file][nightDic[term]][rfid]['strain']] * nbData)
            dataDic['rfid'].extend( [rfid] * nbData )
            dataDic['strain'].extend( [dic[file][nightDic[term]][rfid]['strain']] * nbData )
            dataDic['sex'].extend ( [dic[file][nightDic[term]][rfid]['sex']] * nbData )
            dataDic['geno'].extend( [dic[file][nightDic[term]][rfid]['genotype']] * nbData )
            dataDic['group'].extend( [dic[file][nightDic[term]][rfid]['group']] * nbData )
            dataDic['variable'].extend( dic[file][nightDic[term]][rfid][variable] )
            dataDic['term'].extend( [term] * nbData )
            lenList += nbData

    print( '#####################')
    print('rfid: ', len(dataDic['rfid']))
    print('variable: ', len(dataDic['variable']))
    print('list: ', lenList)
    df = pd.DataFrame.from_dict(dataDic)
    print('################')
    print(df.head())
    return df


def plotSpeedBoxplotDiffGenoShortLongTerm(ax, variable, dataframe, yMin, yMax, letter, strain, sex, genoList, yLabel, p='NA'):
    genotypeType = list(Counter(dataframe['geno']).keys())
    print(genotypeType)
    orderedGenotypeType = list(sorted(genotypeType))
    print(orderedGenotypeType)
    
    yLabel = yLabel
    print(yLabel)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    xIndex = [0, 1]
    ax.set_xticks(xIndex)
    ax.set_ylabel(yLabel, fontsize=15)
    ax.legend().set_visible(False)
    ax.xaxis.set_tick_params(direction="in")
    ax.yaxis.set_tick_params(direction="in")
    ax.set_xlim(0, 2)
    ax.set_ylim(yMin[variable], yMax[variable])
    ax.tick_params(axis='y', labelsize=14)

    ax.text(-1, yMax[variable] + 0.06 * (yMax[variable] - yMin[variable]), letter,
            fontsize=20, horizontalalignment='center', color='black', weight='bold')
    my_pal = {list(reversed(orderedGenotypeType))[0]: getColorGeno(genoList[0]), list(reversed(orderedGenotypeType))[1]: getColorGeno(genoList[1])}
    print('###palette:', my_pal)
    meanprops = dict(marker='o', markerfacecolor='white', markeredgecolor='black')
    bp = sns.boxplot(x='term', y='variable', data=dataframe, hue='geno', hue_order=list(reversed(orderedGenotypeType)), ax=ax, showfliers = False, meanprops=meanprops, palette=my_pal, showmeans=True, notch=False, width=0.4, dodge=True)
    
    ax.set_xticklabels(['15 min', '2 nights'], rotation=0, fontsize=12, horizontalalignment='center')

    # Add transparency to colors
    for patch in bp.artists:
        r, g, b, a = patch.get_facecolor()
        patch.set_facecolor((r, g, b, .7))
    bp.set(xlabel=None)
    bp.set_ylabel(yLabel, fontsize=15)

    bp.legend().set_visible(False)

    dataList = {}
    
    labelPos = {'short': {list(reversed(orderedGenotypeType))[0]: -0.15, list(reversed(orderedGenotypeType))[1]: 0.15}, 'long': {list(reversed(orderedGenotypeType))[0]: 0.85, list(reversed(orderedGenotypeType))[1]: 1.15}}
    for termType in ['short', 'long']:
        dataList[termType] = {}
        
        for geno in list(reversed(orderedGenotypeType)):
            dataList[termType][geno] = dataframe[(dataframe['geno'] == geno) & (dataframe['sex'] == sex) & (dataframe['strain'] == strain) & (dataframe['term'] == termType)]['variable'].values
            print( geno, dataList[termType][geno])
            print(geno, len(dataList[termType][geno]), np.mean(dataList[termType][geno]), '+/-', np.std(dataList[termType][geno]))
        
            ax.text(labelPos[termType][geno], yMin[variable] - 0.1 * (yMax[variable] - yMin[variable]), '(n={})'.format(len(dataList[termType][geno])),
            rotation=45, fontsize=11, verticalalignment='top', horizontalalignment='right', color='black')
    

        selectedDf = dataframe.loc[dataframe['term'] == termType,:]
    
        # create model:
        model = smf.mixedlm("variable ~ geno", selectedDf, groups=selectedDf['group'])
        # run model:
        result = model.fit()
        # print summary
        print(result.summary())
        p, sign = extractPValueFromLMMResult(result=result, keyword='WT')
        ax.text(labelPos[termType][geno]-0.3, yMax[variable] - 0.06 * (yMax[variable] - yMin[variable]), getStarsFromPvalues(pvalue=p, numberOfTests=1), fontsize=20)


if __name__ == '__main__':
    '''
    This codes allows to test whether events are different in speed and duration if they occur with USVs or if they occur without USVs.
    '''
    print("Code launched.")

    # set font
    from matplotlib import rc

    rc('font', **{'family': 'serif', 'serif': ['Arial']})

    eventListToTest = ["Contact", "Approach contact", "Break contact", "Get away", "FollowZone",
                       "Oral-genital Contact", "Train2", "longChase"]
    behavEventListShort = ["Contact", "Approach contact", "Break contact", "FollowZone",
                           "Oral-genital Contact", "Train2"]
    behavEventListShortPoints = ["Train2", "FollowZone", "Approach contact", "Break contact"]

    while True:

        question = "Do you want to:"
        question += "\n\t [c] compute the speed and duration for a specific event?"
        question += "\n\t [p] plot the mean speed of animals in a specific event between genotypes?"
        question += "\n\t [3] plot the mean speed of animals in a specific event between sexes for each age?"
        question += "\n\t [4] plot the mean speed of animals in a specific event between short and long term?"
        question += "\n"
        answer = input(question)

        if answer == "c":
            eventToTest = 'FollowZone'
            #eventToTest = 'Get away'
            animalData = {}
            files = getFilesToProcess()
            computeSpeedDurationPerEvent(animalData=animalData, files=files, tmin=0, tmax=15*oneMinute, eventToTest=eventToTest)

            break

        if answer == 'p':
            jsonFile = getJsonFileToProcess()
            with open(jsonFile) as json_data:
                durationSpeedData = json.load(json_data)
            print("json file re-imported.")

            eventToTest = 'Approach contact'
            nightList = ['1', '2']

            fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 6), sharey=True)

            col = 0

            for n in nightList:
                dataDic = getProfileValues( durationSpeedData, night = str(n), event='distance' )
                testSpeedData(profileData=durationSpeedData, night = str(n), event='distance' )
                ax = axes[col]
                plotBoxplotSpeedPerEvent(dataDic, ax, eventToTest)
                col += 1

            fig.tight_layout()
            fig.savefig('Fig_meanSpeed_{}.pdf'.format(eventToTest), dpi=300)
            plt.close(fig)

            print('Job done.')

            break

        if answer == '3':
            '''This option provides the speed of the mice for each age class to compare between sexes'''
            jsonFile = getJsonFileToProcess()
            with open(jsonFile) as json_data:
                durationSpeedData = json.load(json_data)
            print("json file re-imported.")


            eventToTest = 'Get away'
            nightList = ['1', '2', '3']

            age = '2mo'

            fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 6), sharey=True)

            col = 0

            for n in nightList:
                dataDic = getProfileValuesNoGroup( durationSpeedData, night = str(n), event='speed' )
                testSpeedDataBetweenSexes(profileData=durationSpeedData, night = str(n), event='speed', age=age )
                ax = axes[col]
                plotBoxplotSpeedPerEventPerSex(dataDic, ax, eventToTest, age=age)
                col += 1

            fig.tight_layout()
            fig.savefig('Fig_meanSpeed_{}_{}.pdf'.format(eventToTest, age), dpi=300)
            plt.close(fig)

            print('Job done.')

            break
        
        
        if answer == '4':
            durationSpeedData = {}
            print('Choose the file for short term experiments.')
            #jsonFileShort = getJsonFileToProcess()
            #jsonFileShort = 'durationSpeedData_Approach contact_16p11_female_pairs_15min.json'
            jsonFileShort = 'durationSpeedData_FollowZone_16p11_female_pairs_15min.json'
            with open(jsonFileShort) as json_data:
                durationSpeedData['short'] = json.load(json_data)
            print("json file re-imported.")
            
            print('Choose the file for long term experiments.')
            #jsonFileLong = getJsonFileToProcess()
            #jsonFileLong = 'durationSpeedData_Approach contact_16p11_female_pairs_2days.json'
            jsonFileLong = 'durationSpeedData_FollowZone_16p11_female_pairs_2nights.json'
            with open(jsonFileLong) as json_data:
                durationSpeedDataLongPerNight = json.load(json_data)
            print("json file re-imported.")
            
            #merge the data over both nights
            durationSpeedData['long'] = {}
            for file in durationSpeedDataLongPerNight.keys():
                durationSpeedData['long'][file] = {}
                durationSpeedData['long'][file]['all nights'] = {}
                for rfid in durationSpeedDataLongPerNight[file]['1'].keys():
                    durationSpeedData['long'][file]['all nights'][rfid] = {}
                    durationSpeedData['long'][file]['all nights'][rfid]['animal'] = durationSpeedDataLongPerNight[file]['1'][rfid]['animal']
                    durationSpeedData['long'][file]['all nights'][rfid]['file'] = durationSpeedDataLongPerNight[file]['1'][rfid]['file']
                    durationSpeedData['long'][file]['all nights'][rfid]['genotype'] = durationSpeedDataLongPerNight[file]['1'][rfid]['genotype']
                    durationSpeedData['long'][file]['all nights'][rfid]['sex'] = durationSpeedDataLongPerNight[file]['1'][rfid]['sex']
                    durationSpeedData['long'][file]['all nights'][rfid]['strain'] = durationSpeedDataLongPerNight[file]['1'][rfid]['strain']
                    durationSpeedData['long'][file]['all nights'][rfid]['age'] = durationSpeedDataLongPerNight[file]['1'][rfid]['age']
                    durationSpeedData['long'][file]['all nights'][rfid]['group'] = durationSpeedDataLongPerNight[file]['1'][rfid]['group']
                    durationSpeedData['long'][file]['all nights'][rfid]['DurationSpeed'] = durationSpeedDataLongPerNight[file]['1'][rfid]['DurationSpeed'] + durationSpeedDataLongPerNight[file]['2'][rfid]['DurationSpeed']
                    durationSpeedData['long'][file]['all nights'][rfid]['speed'] = durationSpeedDataLongPerNight[file]['1'][rfid]['speed'] + durationSpeedDataLongPerNight[file]['2'][rfid]['speed']
                    durationSpeedData['long'][file]['all nights'][rfid]['distance'] = durationSpeedDataLongPerNight[file]['1'][rfid]['distance'] + durationSpeedDataLongPerNight[file]['2'][rfid]['distance']
            
            selectedVariable = 'distance'
            
            eventToTest = 'FollowZone'
            termList = ['short', 'long']
            nightDic = {'short': '0', 'long': 'all nights'}
            variableList = ['speed', 'distance']
            letterList = ['A', 'B', 'C', 'D', 'E', 'F']
            yLabelDic = {'speed': 'speed (cm/s)', 'distance': 'distance travelled (cm)'}
            yMin = {'speed': 0, 'distance': 0}
            yMax = {'speed': 60, 'distance': 25}
            strain = 'B6C3B16p11.2'
            sex = 'female'
            
            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4), sharey=False)

            col = 0
            n = 0

            for selectedVariable in variableList:
                
                ax = axes[col]
                dfDataShort = createDataframeFromDicDiffGenoShortLongTerm( durationSpeedData['short'], variable=selectedVariable, nightDic=nightDic, term='short' )
                dfDataLong = createDataframeFromDicDiffGenoShortLongTerm( durationSpeedData['long'], variable=selectedVariable, nightDic=nightDic, term='long' )
                dfData = pd.concat( [dfDataShort, dfDataLong], ignore_index=True )
                plotSpeedBoxplotDiffGenoShortLongTerm(ax=ax, variable=selectedVariable, dataframe=dfData, yMin=yMin, yMax=yMax, letter=letterList[n], strain=strain, sex=sex, genoList=genoList, yLabel=yLabelDic[selectedVariable], p='NA')
                col += 1
                n += 1

            fig.tight_layout()
            fig.savefig('Fig_speed_distance_per_period_{}.pdf'.format(eventToTest), dpi=300)
            fig.savefig('Fig_speed_distance_per_period_{}.png'.format(eventToTest), dpi=300)
            plt.close(fig)

            print('Job done.')

            break
