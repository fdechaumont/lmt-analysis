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

    variableList = ["dist_tot1", "dist_center1", "time_center1", "dist_obj1", "time_obj1", "sap1", "dist_tot2", "dist_center2", "time_center2", "dist_obj2", "time_obj2", "sap2", "Stop TotalLen1", "Stop Nb1", "Stop MeanDur1", "Center Zone TotalLen1", "Center Zone Nb1",
"Center Zone MeanDur1", "Periphery Zone TotalLen1", "Periphery Zone Nb1", "Periphery Zone MeanDur1", "Rear isolated TotalLen1", "Rear isolated Nb1", "Rear isolated MeanDur1",
"Rear in centerWindow TotalLen1", "Rear in centerWindow Nb1", "Rear in centerWindow MeanDur1", "Rear at periphery TotalLen1", "Rear at periphery Nb1", "Rear at periphery MeanDur1", "SAP TotalLen1", "SAP Nb1", "SAP MeanDur1", "WallJump TotalLen1", "WallJump Nb1",
"WallJump MeanDur1", "Stop TotalLen2", "Stop Nb2", "Stop MeanDur2", "Center Zone TotalLen2", "Center Zone Nb2", "Center Zone MeanDur2", "Periphery Zone TotalLen2", "Periphery Zone Nb2",
"Periphery Zone MeanDur2", "Rear isolated TotalLen2", "Rear isolated Nb2", "Rear isolated MeanDur2", "Rear in centerWindow TotalLen2", "Rear in centerWindow Nb2", "Rear in centerWindow MeanDur2", "Rear at periphery TotalLen2",
"Rear at periphery Nb2", "Rear at periphery MeanDur2", "SAP TotalLen2", "SAP Nb2", "SAP MeanDur2", "WallJump TotalLen2", "WallJump Nb2", "WallJump MeanDur2"]

    variableListExtension = {"dist_tot1": '(cm)', "dist_center1": '(cm)', "time_center1": '(frames)', "dist_obj1": '(cm)', "time_obj1": '(frames)', "sap1": '(frames)', "dist_tot2": '(cm)',
                    "dist_center2": '(cm)', "time_center2": '(frames)', "dist_obj2": '(cm)', "time_obj2": '(frames)', "sap2": '(frames)', "Stop TotalLen1": '(frames)', "Stop Nb1": '(nb)',
                    "Stop MeanDur1": '(frames)', "Center Zone TotalLen1": '(frames)', "Center Zone Nb1": '(nb)',
                    "Center Zone MeanDur1": '(frames)', "Periphery Zone TotalLen1": '(frames)', "Periphery Zone Nb1": '(nb)', "Periphery Zone MeanDur1": '(frames)',
                    "Rear isolated TotalLen1": '(frames)', "Rear isolated Nb1": '(nb)', "Rear isolated MeanDur1": '(frames)',
                    "Rear in centerWindow TotalLen1": '(frames)', "Rear in centerWindow Nb1": '(nb)', "Rear in centerWindow MeanDur1": '(frames)',
                    "Rear at periphery TotalLen1": '(frames)', "Rear at periphery Nb1": '(nb)', "Rear at periphery MeanDur1": '(frames)',
                    "SAP TotalLen1": '(frames)', "SAP Nb1": '(nb)', "SAP MeanDur1": '(frames)', "WallJump TotalLen1": '(frames)', "WallJump Nb1": '(nb)',
                    "WallJump MeanDur1": '(frames)', "Stop TotalLen2": '(frames)', "Stop Nb2": '(nb)', "Stop MeanDur2": '(frames)', "Center Zone TotalLen2": '(frames)',
                    "Center Zone Nb2": '(nb)', "Center Zone MeanDur2": '(frames)', "Periphery Zone TotalLen2": '(frames)', "Periphery Zone Nb2": '(nb)',
                    "Periphery Zone MeanDur2": '(frames)', "Rear isolated TotalLen2": '(frames)', "Rear isolated Nb2": '(nb)', "Rear isolated MeanDur2": '(frames)',
                    "Rear in centerWindow TotalLen2": '(frames)', "Rear in centerWindow Nb2": '(nb)', "Rear in centerWindow MeanDur2": '(frames)',
                    "Rear at periphery TotalLen2": '(frames)',
                    "Rear at periphery Nb2": '(nb)', "Rear at periphery MeanDur2": '(frames)', "SAP TotalLen2": '(frames)', "SAP Nb2": '(nb)', "SAP MeanDur2": '(frames)',
                    "WallJump TotalLen2": '(frames)', "WallJump Nb2": '(nb)', "WallJump MeanDur2": '(frames)'}

    orderedFounderStrainList = ['CAST', 'PWK', 'WSB', '129SvJ', 'AJ', 'NOD', 'NZO', 'C57BL6J']
    orderedCCStrainList = ['CC001', 'CC002', 'CC012', 'CCO18', 'CC024', 'CC037', 'CC040', 'CC041', 'CC042', 'CC051', 'CC059', 'CC061']
    orderedOtherStrainList = ['BTBR']

    orderedFullStrainList = orderedFounderStrainList+orderedCCStrainList+orderedOtherStrainList

    while True:

        question = "Do you want to:"
        question += "\n\t [1] plot simple barplots with all founder and CC strains?"
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
                                       "markersize": '10'})
                #sns.stripplot(x=x, y=y, jitter=True, hue=sex, hue_order=['male', 'female'], s=5, dodge=True, ax=ax)
                sns.stripplot(x=x, y=y, jitter=True, hue=sex, hue_order=['male', 'female'], order=orderedFullStrainList, s=5, dodge=True, ax=ax, color='black')

                ax.set_xticklabels(labels=ax.get_xticklabels(), rotation = 45, horizontalalignment = 'right', fontsize = 12)
                #ax.set_yticklabels(labels=ax.get_yticklabels(), fontsize=12)

                ax.legend().set_visible(False)

                plt.tight_layout()
                plt.show()
                fig.savefig('plot_single_object_{}.pdf'.format(value), dpi=300)

            print('Job done.')
            break
