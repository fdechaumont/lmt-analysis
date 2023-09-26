'''
Created on 6 sept. 2023

@author: eye
'''
from lmtanalysis.FileUtil import getFilesToProcess, behaviouralEventOneMouse,\
    getJsonFilesToProcess, mergeJsonFilesForProfiles, categoryList,\
    getBehaviouralTraitsPerCategory
from lmtanalysis.Util import getMinTMaxTInput
from lmtanalysis.Measure import oneMinute, oneHour
import os
import sqlite3
from lmtanalysis.Animal import *
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from scripts.ComputeMeasuresIdentityProfileOneMouseAutomatic import computeProfile
from collections import Counter

if __name__ == '__main__':
    """
    This script aims at providing behavioural profiles for each individual over time bins.
    The user is able to choose the time for the whole experiment or only during nights. It starts from a fix position across experiments, to allow comparisons between experiments.
    It works for four animals.
    """
    print("Code launched.")
    # set font
    from matplotlib import rc, gridspec
    pd.set_option("display.max_columns", None)
    rc('font', **{'family': 'serif', 'serif': ['Arial']})
    
    while True:

        question = "Do you want to:"
        question += "\n\t [1] compute profile data per time bin for the beginning of the exp (save json file)?"
        question += "\n\t [2] plot the profile per time bins for the beginning of the exp"
        question += "\n"
        answer = input(question)

        if answer == "1":
            """compute profile per time bin for the beginning of the experiments """
            files = getFilesToProcess()
            questionTimeBin = "Choose the time bin you want to use"
            timeBinDuration = getFrameInput(questionTimeBin)
            questionDuration = "How long do you want to compute the profile per time bin starting from the beginning of the exp?"
            recordingDuration = getFrameInput(questionDuration)
            maxDurationOfRecording = 71*oneHour
            numberOfTimeBinsToCompute = np.round( recordingDuration / timeBinDuration, 0 )
            print("Number of time bins to compute: ", numberOfTimeBinsToCompute)
            
            
            for file in files:
                #initialize the result dic
                profileData = {}
                tmin = 0
                print(file)
                #get the path and the name of file
                head, tail = os.path.split(file)
                profileData[file] = {}
                for timeBin in range(int(numberOfTimeBinsToCompute)):
                    tmax = tmin + timeBinDuration
                    profileData[file][tmin] = computeProfile(file=file, minT=tmin, maxT=tmax, behaviouralEventList=behaviouralEventOneMouse)
                    tmin += timeBinDuration
                    
                # Create a json file to store the computation
                with open( f"{head}/{tail}_profile_initial_{recordingDuration}_{timeBinDuration}timeBins.json", 'w') as fp:
                    json.dump(profileData, fp, indent=4)
                print("json file with profile measurements created.")
            
            print("Job done.")
            break
                
                
        if answer == "2":
            """plot profile per time bin for the beginning of the experiments """
            files = getJsonFilesToProcess()
            dataDic = mergeJsonFilesForProfiles(files)
            
            for behaviouralCategory in ['activity', 'exploration', 'general contacts', 'specific contacts', 'follow', 'approach', 'escape']:
                
                df = pd.DataFrame({'file': [], 'group': [], 'rfid': [], 'sex': [], 'genotype': [], 'strain': [], 'timebin': [], 'event': [], 'value': []})
                for file in dataDic.keys():
                    print("New file: ", file)
                    for timebin in dataDic[file].keys():
                        for rfid in dataDic[file][timebin].keys():
                            for event in getBehaviouralTraitsPerCategory(behaviouralCategory):
                                new_row = pd.Series({'file': file, 'group': dataDic[file][timebin][rfid]['group'],
                                                'rfid': rfid, 'sex': dataDic[file][timebin][rfid]['sex'],
                                                'genotype': dataDic[file][timebin][rfid]['genotype'], 'strain': dataDic[file][timebin][rfid]['strain'],
                                                'timebin': timebin, 'event': event, 'value': dataDic[file][timebin][rfid][event]})
                                df = pd.concat([df, new_row.to_frame().T], ignore_index = True)
                
                fig, axes = plt.subplots(nrows=len(getBehaviouralTraitsPerCategory(behaviouralCategory)), ncols=1, figsize=(14, 3*len(getBehaviouralTraitsPerCategory('activity'))))
                row=0
                
                for event in getBehaviouralTraitsPerCategory(behaviouralCategory):
                    
                    genotypeList = list(Counter(df['genotype']).keys())
                    my_pal = {genotypeList[0]: getColorGeno(genotypeList[0]), genotypeList[1]: getColorGeno(genotypeList[1])}
                    
                    ax=axes[row]
                    ax.spines['right'].set_visible(False)
                    ax.spines['top'].set_visible(False)
                    ax.set_ylabel(event)
                    sns.lineplot(data = df.loc[df['event']==event], x='timebin', y='value', hue='genotype', palette=my_pal, ax=ax, ci="sd" )
                    #sns.lineplot(data = df.loc[df['event']==event], x='timebin', y='value', hue='genotype', units='rfid', style='group', estimator=None, lw=1, palette=my_pal, ax=ax )
                    row += 1
                    
                fig.savefig( f"fig_timebin_beginning_{behaviouralCategory}.pdf" ,dpi=100)
                
            print("Job done.")
            break