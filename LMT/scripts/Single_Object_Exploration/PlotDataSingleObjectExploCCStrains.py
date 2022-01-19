'''
Created on 06 Jan. 2022

@author: Elodie
'''

import sqlite3

from matplotlib.colors import ListedColormap

from lmtanalysis.FileUtil import getFigureBehaviouralEventsLabelsFrench
from lmtanalysis.Animal import *
import numpy as np
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
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
from scipy.stats import mannwhitneyu, kruskal, ttest_1samp
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox
from scripts.Single_Object_Exploration.Configuration_Single_Object_Explo import *

import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def getDicValues(data, event=None):
    dataDic = {}
    dataDic['genotype'] = []
    dataDic['value'] = []
    dataDic['rfid'] = []
    dataDic['age'] = []
    dataDic['strain'] = []
    dataDic['sex'] = []

    for strain in data.keys():
        for sex in data[strain].keys():
            for rfid in data[strain][sex].keys():
                dataDic['value'].append(data[strain][sex][rfid][event])
                dataDic['rfid'].append(rfid)
                dataDic['age'].append(data[strain][sex][rfid]['age'])
                dataDic['strain'].append(strain)
                dataDic['sex'].append(sex)
                dataDic['genotype'].append(data[strain][sex][rfid]['genotype'])

    return dataDic

if __name__ == '__main__':

    print("Code launched.")
    # set font
    from matplotlib import rc, gridspec

    rc('font', **{'family': 'serif', 'serif': ['Arial']})


    while True:

        question = "Do you want to:"
        question += "\n\t [1] plot simple barplots with all founder and CC strains?"
        question += "\n\t [2] plot heatmaps to represent sex-related variations in all founder and CC strains?"
        question += "\n"
        answer = input(question)

        if answer == "1":
            '''Plot simple barplots with all founder and CC strains'''
            file = getJsonFileToProcess()
            print(file)
            # create a dictionary with profile data
            with open(file) as json_data:
                data = json.load(json_data)

            print("json file for profile data re-imported.")

            statSexResults = {}
            statSexPval = {}
            for strain in orderedFullStrainList:
                statSexResults[strain] = {}
                statSexPval[strain] = {}

            for value in variableList:
                print(value)
                dataDic = getDicValues(data, event=value)
                print(dataDic)

                fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(18, 8), sharey=True)

                ax = axes

                ax.set_xlim(-1, 21)
                #ax.set_ylim(min(dataDic['value']) - 0.1 * max(dataDic['value']), max(dataDic['value']) + 0.1 * max(dataDic['value']))
                ax.set_ylim(0, max(dataDic['value']) + 0.1 * max(dataDic['value']))
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)

                ax.set_ylabel('{} {}'.format(value, variableListExtension[value]), fontsize=16)


                ax.add_patch(mpatches.Rectangle((-1, 0), width=8.5, height=max(dataDic['value'])*1.1, facecolor='grey', alpha=0.3))
                ax.text(3, max(dataDic['value'])*1.05, s='FOUNDERS', color='white', fontsize=14, fontweight='bold', rotation='horizontal',
                        horizontalalignment='center')

                ax.add_patch(mpatches.Rectangle((7.6, 0), width=11.9, height=max(dataDic['value'])*1.1, facecolor='grey', alpha=0.3))
                ax.text(14, max(dataDic['value'])*1.05, s='COLLABORATIVE CROSS', color='white', fontsize=14, fontweight='bold', rotation='horizontal',
                        horizontalalignment='center')

                ax.add_patch(
                    mpatches.Rectangle((19.6, 0), width=1.5, height=max(dataDic['value'])*1.1, facecolor='grey', alpha=0.3))
                ax.text(20, max(dataDic['value'])*1.05, s='OTHER', color='white', fontsize=14, fontweight='bold', rotation='horizontal',
                        horizontalalignment='center')

                x = dataDic['strain']
                y = dataDic['value']
                sex = dataDic['sex']
                sns.boxplot(x=x, y=y, hue=sex, hue_order=['male', 'female'], order=orderedFullStrainList, ax=ax, linewidth=0.5, showmeans=True,
                            meanprops={"marker": 'o',
                                       "markerfacecolor": 'white',
                                       "markeredgecolor": 'black',
                                       "markersize": '10'}, showfliers=False)
                #sns.stripplot(x=x, y=y, jitter=True, hue=sex, hue_order=['male', 'female'], s=5, dodge=True, ax=ax)
                sns.stripplot(x=x, y=y, jitter=True, hue=sex, hue_order=['male', 'female'], order=orderedFullStrainList, s=5, dodge=True, ax=ax, color='black')

                ax.set_xticklabels(labels=ax.get_xticklabels(), rotation = 45, horizontalalignment = 'right', fontsize = 12)
                #ax.set_yticklabels(labels=ax.get_yticklabels(), fontsize=12)

                ax.legend().set_visible(False)

                #comparison between sexes:
                df = pd.DataFrame.from_dict(dataDic)

                n = 0
                labelPos = ax.get_xticks()
                for strain in orderedFullStrainList:
                    dataMales = df['value'][(df['sex'] == 'male') & (df['strain'] == strain)]
                    dataFemales = df['value'][(df['sex'] == 'female') & (df['strain'] == strain)]

                    if (len(dataMales) > 0) & (len(dataFemales) > 0):
                        try:
                            U, p = mannwhitneyu(dataMales, dataFemales)
                            print('Mann-Whitney U test for {} males versus {} females in {}: U={}, p={}'.format(len(dataMales), len(dataFemales), strain, U, p))
                            ax.text(labelPos[n], max(dataDic['value']) * 1.01, getStarsFromPvalues(pvalue=p, U=U, numberOfTests=1), fontsize=16, horizontalalignment='center')
                            #computation of Cohen's d:
                            effectSize = (np.mean(dataMales) - np.mean(dataFemales)) / np.std( list(dataMales) + list(dataFemales))
                            statSexPval[strain][value] = getStarsFromPvalues(pvalue=p, U=U, numberOfTests=1)
                        except:
                            effectSize = 0
                            statSexPval[strain][value] = 'NA'
                            print('problem', dataMales, dataFemales)

                    else:
                        ax.text(labelPos[n], max(dataDic['value']) * 1.01, 'NA', fontsize=16, horizontalalignment='center')
                        effectSize = 0
                        statSexPval[strain][value] = 'NA'


                    # statSexResults[strain][value] = (U, p, effectSize)
                    statSexResults[strain][value] = effectSize


                    n += 1

                plt.tight_layout()
                plt.show()
                fig.savefig('plot_single_object_{}.pdf'.format(value), dpi=300)

            with open("single_object_explo_sex_diff_effect_size.json", 'w') as fp:
                json.dump(statSexResults, fp, indent=4)
            print("json file with profile measurements created.")

            with open("single_object_explo_sex_diff_pval.json", 'w') as fp:
                json.dump(statSexPval, fp, indent=4)
            print("json file with profile measurements created.")

            print('Job done.')
            break

        if answer == "2":
            '''Draw heatmaps for sex differences in all founder and CC strains'''
            print('Choose the file containing the size effect of the sex-related variations')
            file = getJsonFileToProcess()
            print(file)
            # create a dictionary with profile data
            with open(file) as json_data:
                statSexResults = json.load(json_data)

            print('Choose the file containing the p-values of the sex-related variations')
            file = getJsonFileToProcess()
            print(file)
            # create a dictionary with profile data
            with open(file) as json_data:
                statSexPval = json.load(json_data)

            print("json files for sex-related variations re-imported.")

            fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(12, 10))  # building the plot for trajectories


            sexEffect = pd.DataFrame.from_dict(statSexResults)
            dfStatSex = np.transpose(sexEffect)
            print(dfStatSex)
            dfStatSexReduced = dfStatSex.loc[:, selectedVariableList ]

            sexPval = pd.DataFrame.from_dict(statSexPval)
            dfStatSexPval = np.transpose(sexPval)
            dfStatSexPvalReduced = dfStatSexPval.loc[:, selectedVariableList]

            h = sns.heatmap(dfStatSexReduced, center=0, cmap=ListedColormap(
                ['steelblue', 'skyblue', 'powderblue', 'white', 'lemonchiffon', 'sandybrown', 'firebrick']), vmin=-1.8,
                            vmax=1.8,
                            cbar_kws={'ticks': [-1.2, -0.8, -0.5, 0.5, 0.8, 1.2], 'extend': 'both'},
                            annot=dfStatSexPvalReduced, annot_kws={"fontsize":10}, fmt='')
            plt.show()
            figure = h.get_figure()
            figure.savefig('single_obj_explo_CC_heatmap_sex_variations.pdf', dpi=200)
            figure.savefig('single_obj_explo_CC_heatmap_sex_variations.jpg', dpi=200)
            print('Job done.')

            break

