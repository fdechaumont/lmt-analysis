'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3

from lmtanalysis.FileUtil import getFigureBehaviouralEventsLabelsFrench
from lmtanalysis.Animal import *
import numpy as np
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from scripts.Single_Object_Exploration.PlotDataSingleObjectExploCCStrains import *
from scripts.Single_Object_Exploration.Configuration_Single_Object_Explo import *
from lmtanalysis.Measure import *
import colorsys
from collections import Counter
import seaborn as sns
import matplotlib.patches as mpatches

from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import getMinTMaxTAndFileNameInput
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.FileUtil import *
from lmtanalysis.Util import getFileNameInput, getStarsFromPvalues
import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas
from scipy.stats import mannwhitneyu, pearsonr, kruskal, ttest_1samp
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def convertDicToDataframe(data, variableList):
    dataDic = {}
    #dataDic['genotype'] = []
    dataDic['rfid'] = []
    #dataDic['age'] = []
    dataDic['strain'] = []
    dataDic['sex'] = []
    dataDic['cat'] = []
    for value in variableList:
        dataDic[value] = []

    for strain in data.keys():
        for sex in data[strain].keys():
            for rfid in data[strain][sex].keys():
                dataDic['rfid'].append(rfid)
                #dataDic['age'].append(data[strain][sex][rfid]['age'])
                dataDic['strain'].append(strain)
                dataDic['sex'].append(sex)
                #dataDic['genotype'].append(data[strain][sex][rfid]['genotype'])
                for value in variableList:
                    dataDic[value].append(data[strain][sex][rfid][value])
                if strain in orderedFounderStrainList:
                    dataDic['cat'].append('founder')
                elif strain in orderedCCStrainList:
                    dataDic['cat'].append('CC')
                elif strain in orderedOtherStrainList:
                    dataDic['cat'].append('other')

    dataframe = pd.DataFrame.from_dict(dataDic)

    return dataframe

if __name__ == '__main__':

    print("Code launched.")
    # set font
    from matplotlib import rc, gridspec

    rc('font', **{'family': 'serif', 'serif': ['Arial']})

    while True:

        question = "Do you want to:"
        question += "\n\t [1] generate a dataframe with data from all founder and CC strains?"
        question += "\n\t [2] check the correlations between variables over all founder and CC strains?"
        question += "\n\t [3] compute z-scores to compare strains to a reference strain?"
        question += "\n\t [4] compare z-scores of a sample of strains to a reference strain"
        question += "\n"
        answer = input(question)

        if answer == "1":
            '''generate a dataframe with data from all founder and CC strains'''
            file = getJsonFileToProcess()
            print(file)
            # create a dictionary with profile data
            with open(file) as json_data:
                data = json.load(json_data)

            print("json file for profile data re-imported.")

            #dataframe = convertDicToDataframe( data, variableList=variableList )
            dataframe = convertDicToDataframe(data, variableList=selectedVariableList)

            df = {}
            for sex in sexList:

                df[sex] = dataframe.loc[(dataframe['sex']==sex),:]

                removedColumnSex = df[sex].pop('sex')
                removedColumnStrain = df[sex].pop('strain')
                removedColumnRfid = df[sex].pop('rfid')
                removedColumnCat = df[sex].pop('cat')
                cleanDataframe = df[sex]
                print(df[sex])

                row_colors = removedColumnStrain.map(colorStrainDic)
                g = sns.clustermap(df[sex], row_colors=row_colors, standard_scale=1)
                plt.show()

            print('Job done.')
            break

        if answer == "2":
            '''check the correlations between variables over all founder and CC strains'''
            file = getJsonFileToProcess()
            print(file)
            # create a dictionary with profile data
            with open(file) as json_data:
                data = json.load(json_data)

            print("json file for profile data re-imported.")

            dataframe = convertDicToDataframe( data, variableList=variableList )

            fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(14, 12))  # building the plot for trajectories

            corr = dataframe.corr()
            print(corr)
            #h = sns.heatmap(corr, center=0, cmap='bwr')
            h = sns.clustermap(corr, center=0, cmap='bwr', figsize=(22,20))

            # plt.show() #display the plot
            h.savefig('single_obj_explo_CC_heatmap_correlation.pdf', dpi=200)
            h.savefig('single_obj_explo_CC_heatmap_correlation.jpg', dpi=200)

            for var1 in variableList:
                for var2 in variableList:
                    if var1 == var2:
                        continue
                    else:
                        r, p = pearsonr(dataframe[var1], dataframe[var2])
                        if (p <= 0.05 / (len(variableList) - 1)) & (abs(r) > 0.8 ):
                            print('{} versus {}: r = {}, p = {}'.format(var1, var2, r, p))


            print('Job done.')
            break


        if answer == "3":
            '''compute z-scores to compare a sample of strains to a reference strain'''
            file = getJsonFileToProcess()
            print(file)
            # create a dictionary with profile data
            with open(file) as json_data:
                data = json.load(json_data)

            print("json file for profile data re-imported.")

            referenceStrain = 'C57BL6J'

            #sampleStrains = orderedCCStrainList
            sampleStrains = orderedFullStrainList
            #sampleStrains.remove(referenceStrain)

            #generate the mean and the standard deviation of the reference strain for each variable
            meanRefDic = {}
            stdRefDic = {}

            for sex in sexList:
                meanRefDic[sex] = {}
                stdRefDic[sex] = {}

            for sex in sexList:
                for variable in variableList:
                    valList = []
                    for rfid in data[referenceStrain][sex].keys():
                        valList.append( data[referenceStrain][sex][rfid][variable])

                    meanRefDic[sex][variable] = np.mean( valList )
                    stdRefDic[sex][variable] = np.std( valList )

            #Compute the Z-score for each of the sample strain compared to the reference strain.
            zScoreDic = {}

            for strain in sampleStrains:
                zScoreDic[strain] = {}
                for sex in sexList:
                    zScoreDic[strain][sex] = {}
                    for rfid in data[strain][sex].keys():
                        zScoreDic[strain][sex][rfid] = {}
                        for variable in variableList:
                            val = data[strain][sex][rfid][variable]
                            zScoreDic[strain][sex][rfid][variable] = (val - meanRefDic[sex][variable]) / stdRefDic[sex][variable]

            # Create a json file to store the computation
            with open("zscore_profile_ref_{}.json".format(referenceStrain), 'w') as fp:
                json.dump(zScoreDic, fp, indent=4)
            print("json file with z-Score profile created.")

            print( 'Job done.' )
            break


        if answer == "4":
            '''compare z-scores of a sample of strains to a reference strain'''
            file = getJsonFileToProcess()
            print(file)
            # create a dictionary with profile data
            with open(file) as json_data:
                data = json.load(json_data)

            print("json file for z-score data re-imported.")
            #print(data)

            referenceStrain = 'C57BL6J'
            sampleStrains = orderedFullStrainList
            #sampleStrains = orderedCCStrainList
            #sampleStrains = orderedFounderStrainList
            sampleStrains.remove(referenceStrain)

            dataDic = {}
            for columnNames in ['strain', 'sex', 'rfid', 'variable', 'value']:
                dataDic[columnNames] = []
            for strain in sampleStrains:
                for sex in data[strain].keys():
                    for rfid in data[strain][sex].keys():
                        for variable in data[strain][sex][rfid].keys():
                            dataDic['strain'].append(strain)
                            dataDic['sex'].append(sex)
                            dataDic['rfid'].append(rfid)
                            dataDic['variable'].append(variable)
                            dataDic['value'].append(data[strain][sex][rfid][variable])

            fullDataframe = pd.DataFrame.from_dict(dataDic)

            refDic = {}
            for columnNames in ['strain', 'sex', 'rfid', 'variable', 'value']:
                refDic[columnNames] = []
            for strain in [referenceStrain]:
                for sex in data[strain].keys():
                    for rfid in data[strain][sex].keys():
                        for variable in data[strain][sex][rfid].keys():
                            refDic['strain'].append(strain)
                            refDic['sex'].append(sex)
                            refDic['rfid'].append(rfid)
                            refDic['variable'].append(variable)
                            refDic['value'].append(data[strain][sex][rfid][variable])

            refDataframe = pd.DataFrame.from_dict(refDic)

            for variable in selectedVariableList:
                for sex in sexList:
                    df = fullDataframe.loc[(fullDataframe['variable'] == variable) & (fullDataframe['sex'] == sex)]

                    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(1.1 * len(sampleStrains), 8), sharey=True)
                    ax = axes
                    xMin = -1
                    xMax = len(sampleStrains)
                    yMinVal = min(df['value']) - 1
                    yMaxVal = max(df['value']) + 1
                    yMin = int(- (max( abs(yMinVal), abs(yMaxVal))) - 1)
                    yMax = int((max(abs(yMinVal), abs(yMaxVal))) + 1)
                    ax.set_xlim(xMin, xMax)
                    ax.set_ylim(yMin, yMax)
                    ax.spines['right'].set_visible(False)
                    ax.spines['top'].set_visible(False)
                    ax.legend().set_visible(False)
                    ax.set_title('{} {}'.format(sex, variable), fontsize=20)

                    if sex == 'female':
                        ax.add_patch(mpatches.Rectangle((xMin, yMin), width=7.4, height=yMax-yMin, facecolor='grey', alpha=0.3))
                        ax.text(2.5, yMax-1, s='FOUNDER', color='white', fontsize=18, fontweight='bold', rotation='horizontal', horizontalalignment='center')

                        ax.add_patch(mpatches.Rectangle((xMin+7.6, yMin), width=11.8, height=yMax - yMin, facecolor='grey', alpha=0.3))
                        ax.text(12.5, yMax - 1, s='COLLABORATIVE CROSS', color='white', fontsize=18, fontweight='bold', rotation='horizontal', horizontalalignment='center')

                        ax.add_patch(mpatches.Rectangle((xMin + 19.6, yMin), width=1.5, height=yMax - yMin, facecolor='grey', alpha=0.3))
                        ax.text(19.05, yMax - 1, s='OTHER', color='white', fontsize=18, fontweight='bold', rotation='horizontal', horizontalalignment='center')

                    if sex == 'male':
                        ax.add_patch(mpatches.Rectangle((xMin, yMin), width=6.4, height=yMax - yMin, facecolor='grey', alpha=0.3))
                        ax.text(2.5, yMax - 1, s='FOUNDER', color='white', fontsize=18, fontweight='bold', rotation='horizontal',  horizontalalignment='center')

                        ax.add_patch( mpatches.Rectangle((xMin + 6.6, yMin), width=11.8, height=yMax - yMin, facecolor='grey', alpha=0.3))
                        ax.text(11.5, yMax - 1, s='COLLABORATIVE CROSS', color='white', fontsize=18, fontweight='bold', rotation='horizontal', horizontalalignment='center')

                        ax.add_patch(mpatches.Rectangle((xMin + 18.6, yMin), width=1.5, height=yMax - yMin, facecolor='grey', alpha=0.3))
                        ax.text(18.05, yMax - 1, s='OTHER', color='white', fontsize=18, fontweight='bold', rotation='horizontal', horizontalalignment='center')

                    #draw the range of variation of the reference strain
                    dfRef = refDataframe.loc[(refDataframe['strain'] == referenceStrain) & (refDataframe['variable'] == variable) & (refDataframe['sex'] == sex)]
                    refMax = np.max(dfRef['value'])
                    refMin = np.min(dfRef['value'])
                    ax.hlines(y=refMin, xmin=xMin, xmax=xMax, colors='grey', linestyles='dotted')
                    ax.hlines(y=refMax, xmin=xMin, xmax=xMax, colors='grey', linestyles='dotted')

                    pos = 0
                    colorList = []
                    for strain in sampleStrains:
                        print('Strain: ', strain, sex)
                        valList = df['value'][(df['strain'] == strain) & (df['variable'] == variable) & (df['sex'] == sex)]
                        if len(valList) == 0:
                            continue
                        else:
                            T, p = ttest_1samp(valList, popmean=0, nan_policy='omit')
                            print('nb val: ', len(valList), 'T=', T, ' p=', p)
                            color = 'grey'
                            # if np.isnan(p) == True:
                            if getStarsFromPvalues(p, numberOfTests=len(sampleStrains)) == 'NA':
                                print('no test conducted.')
                                colorList.append(color)
                                pos += 1


                            else:
                                if p < 0.05 / len(sampleStrains):
                                    print(variable, strain, sex, T, p)
                                    ax.text(pos, yMin + 0.5, s=getStarsFromPvalues(p, numberOfTests=len(sampleStrains)), fontsize=16, ha='center')
                                    if T > 0:
                                        color = 'red'
                                    elif T < 0:
                                        color = 'blue'
                                    elif T == 0:
                                        color = 'grey'

                                colorList.append(color)
                                pos += 1

                            print('event position: ', strain, pos, T, p, getStarsFromPvalues(p, numberOfTests=len(sampleStrains)), color)


                    meanprops = dict(marker='D', markerfacecolor='white', markeredgecolor='black')
                    bp = sns.boxplot(data=df, x='strain', y='value', ax=ax, width=0.5, showfliers=False, meanprops=meanprops, showmeans=True, linewidth=0.4)
                    sns.swarmplot(data=df, x='strain', y='value', ax=ax, color='black')

                    ax.hlines(y=0, xmin=xMin, xmax=xMax, colors='grey', linestyles='dashed')

                    edgeList = 'black'
                    n = 0
                    print('################################################Number of boxes: ', variable, len(bp.artists), len(colorList))
                    for box in bp.artists:
                        box.set_facecolor(colorList[n])
                        box.set_edgecolor(edgeList)
                        #print('color: ', n, colorList[n])
                        n += 1
                    # Add transparency to colors
                    for box in bp.artists:
                        r, g, b, a = box.get_facecolor()
                        box.set_facecolor((r, g, b, .7))

                    bp.legend().set_visible(False)

                    ax.set_ylabel('Z-score compared to {}'.format(referenceStrain), fontsize=18)
                    ax.set_xlabel('', fontsize=18)
                    texts = [t.get_text() for t in ax.get_xticklabels()]
                    ax.set_xticklabels(texts, rotation=45, fontsize=16, horizontalalignment='right')
                    ax.set_yticks(list(range(yMin, yMax+1)))
                    ax.set_yticklabels(list(range(yMin, yMax+1)), fontsize=14)
                    ax.legend().set_visible(False)

                    plt.tight_layout()
                    plt.show()
                    fig.savefig('zscores_single_obj_explo_{}_{}.pdf'.format(variable, sex), dpi=300)
                    fig.savefig('zscores_single_obj_explo_{}_{}.jpg'.format(variable, sex), dpi=300)

            print('Job done.')
            break




