'''
Created on 6 sept. 2023

@author: eye
'''
from lmtanalysis.FileUtil import getFilesToProcess, behaviouralEventOneMouse,\
    getJsonFilesToProcess, mergeJsonFilesForProfiles, categoryList,\
    getBehaviouralTraitsPerCategory, getFigureBehaviouralEventsLabels,\
    extractPValueFromLMMResult
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
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from scripts.PlotTimeLineActivity import frameToTimeTicker
import statsmodels.formula.api as smf

def getDayNightPeriodPerTimeBin(timeBinNb, binNight1, binNight2, binNight3, binDay1, binDay2):
    timePeriod = "day3"
    if timeBinNb in binNight1:
        timePeriod = "night1"
    elif timeBinNb in binNight2:
        timePeriod = "night2"
    elif timeBinNb in binNight3:
        timePeriod = "night3"
    elif timeBinNb in binDay0:
        timePeriod = "day0"
    elif timeBinNb in binDay1:
        timePeriod = "day1"
    elif timeBinNb in binDay2:
        timePeriod = "day2"
        
    return timePeriod
                    

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
    letterList = list(string.ascii_uppercase)
    
    while True:

        question = "Do you want to:"
        question += "\n\t [1] compute profile data per time bin from the beginning of the exp (save json file)?"
        question += "\n\t [1a] compute profile data per time bin starting one hour before the first night (save json file)?"
        question += "\n\t [1b] compute distance per time bin starting xx hours before the night"
        question += "\n\t [2] plot the profile per time bins for the beginning of the exp"
        question += "\n\t [2a] plot the distance travelled per time bin?"
        question += "\n\t [2b] plot distance traveled per time bin from a synchronised beginning?"
        question += "\n\t [3] evaluate the area under the curve"
        question += "\n"
        answer = input(question)

        if answer == "1":
            """compute profile per time bin from the beginning of the experiments """
            files = getFilesToProcess()
            questionTimeBin = "Choose the time bin you want to use"
            timeBinDuration = getFrameInput(questionTimeBin)
            questionDuration = "How long do you want to compute the profile per time bin starting from the beginning of the exp?"
            recordingDuration = getFrameInput(questionDuration)
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
        
        if answer == "1a":
            """ compute profile per time bin starting xx hours before the night """
            files = getFilesToProcess()
            hoursBeforeNight = 3
            questionTimeBin = "Choose the time bin you want to use"
            timeBinDuration = getFrameInput(questionTimeBin)
            questionDuration = f"How long do you want to compute the profile per time bin starting from {hoursBeforeNight} hours before the first night?"
            recordingDuration = getFrameInput(questionDuration)
            numberOfTimeBinsToCompute = np.round( recordingDuration / timeBinDuration, 0 )
            print("Number of time bins to compute: ", numberOfTimeBinsToCompute)
            
            for file in files:
                #initialize the result dic
                profileData = {}
                
                #determine the starting time according to the position of the night event
                connection = sqlite3.connect( file )
                pool = AnimalPool( )
                pool.loadAnimals( connection )
                nightEventTimeLine = EventTimeLineCached( connection, file, "night", minFrame=0, maxFrame=None )
                firstNightEvent = nightEventTimeLine.getEventList()[0]
                minT = firstNightEvent.startFrame - hoursBeforeNight*oneHour
                
                print(file)
                #get the path and the name of file
                head, tail = os.path.split(file)
                profileData[file] = {}
                tmin = minT
                for timeBin in range(int(numberOfTimeBinsToCompute)):
                    tmax = tmin + timeBinDuration
                    profileData[file][tmin] = computeProfile(file=file, minT=tmin, maxT=tmax, behaviouralEventList=[""])
                    #profileData[file][tmin] = computeProfile(file=file, minT=tmin, maxT=tmax, behaviouralEventList=behaviouralEventOneMouse)
                    tmin += timeBinDuration
                    
                # Create a json file to store the computation
                with open( f"{head}/{tail}_distance_from_first_night_{recordingDuration}_{timeBinDuration}timeBins.json", 'w') as fp:
                    json.dump(profileData, fp, indent=4)
                print("json file with profile measurements created.")
            
            
            break
        
        if answer == "1b":
            """ compute distance per time bin starting xx hours before the night """
            files = getFilesToProcess()
            hoursBeforeNight = 2
            questionTimeBin = "Choose the time bin you want to use"
            timeBinDuration = getFrameInput(questionTimeBin)
            questionDuration = f"How long do you want to compute the profile per time bin starting from {hoursBeforeNight} hours before the first night?"
            recordingDuration = getFrameInput(questionDuration)
            numberOfTimeBinsToCompute = np.round( recordingDuration / timeBinDuration, 0 )
            print("Number of time bins to compute: ", numberOfTimeBinsToCompute)
            
            for file in files:
                #initialize the result dic
                profileData = {}
                
                #determine the starting time according to the position of the night event
                connection = sqlite3.connect( file )
                pool = AnimalPool( )
                pool.loadAnimals( connection )
                nightEventTimeLine = EventTimeLineCached( connection, file, "night", minFrame=0, maxFrame=None )
                firstNightEvent = nightEventTimeLine.getEventList()[0]
                minT = firstNightEvent.startFrame - hoursBeforeNight*oneHour
                
                #load animal detections
                for animalObject in pool.getAnimalList():
                    animalObject.loadDetection( start=minT, end=minT+recordingDuration, lightLoad = True )
                
                print(file)
                #get the path and the name of file
                head, tail = os.path.split(file)
                profileData[file] = {}
                tmin = minT
                for timeBin in range(int(numberOfTimeBinsToCompute)):
                    tmax = tmin + timeBinDuration
                    profileData[file][tmin] = {}
                    for animalObject in pool.getAnimalList():
                        rfid = animalObject.RFID
                        profileData[file][tmin][rfid] = {}
                        genotype = animalObject.genotype
                        profileData[file][tmin][rfid]["genotype"] = genotype
                        strain = animalObject.strain
                        profileData[file][tmin][rfid]["strain"] = strain
                        age = animalObject.age
                        profileData[file][tmin][rfid]["age"] = age
                        sex = animalObject.sex
                        profileData[file][tmin][rfid]["sex"] = sex
                        distanceInBin = animalObject.getDistance( tmin=tmin,tmax=tmax, filter_flickering=True, filter_stop=True)/100
                        profileData[file][tmin][rfid]["totalDistance"] = distanceInBin
                    
                    tmin += timeBinDuration
                    
                # Create a json file to store the computation
                with open( f"{head}/{tail}_distance_from_first_night_{recordingDuration}_{timeBinDuration}timeBins.json", 'w') as fp:
                    json.dump(profileData, fp, indent=4)
                print("json file with profile measurements created.")
            
            
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
                    sns.lineplot(data = df.loc[df['event']==event], x='timebin', y='value', hue='rfid', ax=ax, errorbar="sd" )
                    #sns.lineplot(data = df.loc[df['event']==event], x='timebin', y='value', hue='genotype', palette=my_pal, ax=ax, errorbar="sd" )
                    #sns.lineplot(data = df.loc[df['event']==event], x='timebin', y='value', hue='genotype', units='rfid', style='group', estimator=None, lw=1, palette=my_pal, ax=ax )
                    row += 1
                    
                fig.savefig( f"fig_timebin_beginning_{behaviouralCategory}.pdf" ,dpi=100)
                
            
            break
        
        if answer == "2a":
            """plot profile per time bin for the beginning of the experiments """
            files = getJsonFilesToProcess()
            dataDic = mergeJsonFilesForProfiles(files)
            
            for behaviouralCategory in ['activity', 'exploration', 'general contacts', 'specific contacts', 'follow', 'approach', 'escape']:
                
                df = pd.DataFrame({'file': [], 'group': [], 'rfid': [], 'sex': [], 'genotype': [], 'strain': [], 'timebin': [], 'event': [], 'value': []})
                for file in dataDic.keys():
                    print("New file: ", file)
                    for timebin in dataDic[file].keys():
                        for rfid in dataDic[file][timebin].keys():
                            event = "totalDistance"
                            new_row = pd.Series({'file': file, 'group': file,
                                            'rfid': rfid, 'sex': dataDic[file][timebin][rfid]['sex'],
                                            'genotype': dataDic[file][timebin][rfid]['genotype'], 'strain': dataDic[file][timebin][rfid]['strain'],
                                            'timebin': timebin, 'event': event, 'value': dataDic[file][timebin][rfid][event]})
                            df = pd.concat([df, new_row.to_frame().T], ignore_index = True)
            
                fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(14, 3*2))
                row=0
                
                
                genotypeList = list(Counter(df['genotype']).keys())
                my_pal = {genotypeList[0]: getColorGeno(genotypeList[0]), genotypeList[1]: getColorGeno(genotypeList[1])}
                
                ax=axes[row]
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.set_ylabel(event)
                #sns.lineplot(data = df.loc[df['event']==event], x='timebin', y='value', hue='rfid', ax=ax, errorbar='sd' )
                sns.lineplot(data = df.loc[df['event']==event], x='timebin', y='value', hue='genotype', palette=my_pal, ax=ax, errorbar='sd' )
                #sns.lineplot(data = df.loc[df['event']==event], x='timebin', y='value', hue='genotype', units='rfid', style='group', estimator=None, lw=1, palette=my_pal, ax=ax )
                row += 1
                    
                fig.savefig( f"fig_timebin_beginning_{event}.png" ,dpi=100)
                
            break
        
        if answer == "2b":
            """plot distance traveled per time bin from a synchronised beginning """
            files = getJsonFilesToProcess()
            dataDic = mergeJsonFilesForProfiles(files)
            
            event = "totalDistance"
            
            binNight1 = range(12, 83+1)
            binNight2 = range(156, 227+1)
            binNight3 = range(300, 371+1)
            binDay0 = range(0, 11+1)
            binDay1 = range(84, 155+1)
            binDay2 = range(228, 299+1)
    
            
            df = pd.DataFrame({'file': [], 'group': [], 'rfid': [], 'sex': [], 'genotype': [], 'strain': [], 'timebin': [], 'timePeriod': [], 'event': [], 'value': []})
            for file in dataDic.keys():
                print("New file: ", file)
                timeBinNb = 0
                for timebin in dataDic[file].keys():
                    for rfid in dataDic[file][timebin].keys():
                        timePeriod = getDayNightPeriodPerTimeBin(timeBinNb, binNight1, binNight2, binNight3, binDay1, binDay2)
                        new_row = pd.Series({'file': file, 'group': file,
                                        'rfid': rfid, 'sex': dataDic[file][timebin][rfid]['sex'],
                                        'genotype': dataDic[file][timebin][rfid]['genotype'], 'strain': dataDic[file][timebin][rfid]['strain'],
                                        'timebin': timeBinNb*10*oneMinute, 'event': event, 'timePeriod': timePeriod, 'value': dataDic[file][timebin][rfid][event]})
                        df = pd.concat([df, new_row.to_frame().T], ignore_index = True)
                        
                    timeBinNb += 1
            
            #compute activity per time period
            dfPeriod = pd.DataFrame({'file': [], 'group': [], 'rfid': [], 'sex': [], 'genotype': [], 'strain': [], 'timePeriod': [], 'event': [], 'value': []})
            rfidList = list(Counter(df['rfid']).keys())
            timePeriodList = list(Counter(df['timePeriod']).keys())
            
            for rfid in rfidList:
                for period in timePeriodList:
                    selectedDf = df.loc[(df['rfid']==rfid) &  (df['timePeriod']==period)]
                    
                    new_row = pd.Series({'file': list(selectedDf['file'])[0], 'group': list(selectedDf['file'])[0],
                                        'rfid': list(selectedDf['rfid'])[0], 'sex': list(selectedDf['sex'])[0],
                                        'genotype': list(selectedDf['genotype'])[0], 'strain': list(selectedDf['strain'])[0],
                                        'event': event, 'timePeriod': period, 'value': sum(list(selectedDf['value']))})
                    dfPeriod = pd.concat([dfPeriod, new_row.to_frame().T], ignore_index = True)
                    
            
            
            #draw plots
            nRow=2
            nCol=5
            k = 0
            gs = gridspec.GridSpec(nrows=nRow, ncols=nCol)
            fig = plt.figure( figsize=(nCol*3, nRow*3) )     
            
            row=0
            genotypeList = list(Counter(df['genotype']).keys())
            my_pal = {genotypeList[0]: getColorGeno(genotypeList[0]), genotypeList[1]: getColorGeno(genotypeList[1])}
               
            for sex in ["male", "female"]:
                print(f"####### {sex} row={row}")
                #timeline of activity
                dfPerSex = df.loc[df['sex']==sex]
                print(dfPerSex)
                ax=fig.add_subplot(gs[row, 0:4])
                
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.set_ylim(0, 35)
                ax.set_ylabel(f"{getFigureBehaviouralEventsLabels(event)} (m/10 min)")
                ax.set_xlim(0, 71*oneHour)
                ax.set_xlabel("time")
                                
                ''' set x axis '''
                formatter = matplotlib.ticker.FuncFormatter( frameToTimeTicker )
                ax.xaxis.set_major_formatter(formatter)
                ax.tick_params(labelsize=10 )
                ax.xaxis.set_major_locator(ticker.MultipleLocator( 30 * 60 * 60 * 12 ))
                ax.xaxis.set_minor_locator(ticker.MultipleLocator( 30 * 60 * 60 ))
        
                #add night grey rectangles
                nightStart = 11*10*oneMinute
                for night in ["night 1", "night 2", "night 3"]:
                    nightPatch = matplotlib.patches.Rectangle( xy=(nightStart, 0) , width=72*10*oneMinute, height=36, facecolor = "lightgrey", alpha=0.2 )
                    ax.add_patch(nightPatch)
                    ax.text(x=nightStart+36*10*oneMinute, y=32, s=night, fontsize=12, c="grey", ha='center')
                    nightStart += 24*6*10*oneMinute
                
                #draw the activity lines    
                #sns.lineplot(data = dfPerSex.loc[dfPerSex['event']==event], x='timebin', y='value', hue='rfid', ax=ax, errorbar='sd' )
                sns.lineplot(data = dfPerSex.loc[dfPerSex['event']==event], x='timebin', y='value', hue='genotype', palette=my_pal, ax=ax, errorbar='sd' )
                #sns.lineplot(data = dfPerSex.loc[dfPerSex['event']==event], x='timebin', y='value', hue='genotype', units='rfid', style='group', estimator=None, lw=1, palette=my_pal, ax=ax )
                ax.legend().set_visible(False)
                ax.set_title(f"{sex}s", fontdict={'fontsize': 16, 'fontweight': "bold"})
                ax.text(-0.05, 1.05, letterList[k], fontsize=18, horizontalalignment='center', color='black', weight='bold', transform=ax.transAxes)
                k += 2
                row += 1
            
               
            row1 = 0
            k = 1
            for sex in ["male", "female"]:    
                #distance computation per time period
                ax=fig.add_subplot(gs[row1, 4])
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.set_ylim(0, 1200)
                ax.set_ylabel(f"{getFigureBehaviouralEventsLabels(event)} (m)")
                
                ax.set_xlabel("time periods")
                selectedDfPeriod = dfPeriod.loc[(dfPeriod['sex']==sex) & ((dfPeriod['timePeriod']=="night1") | (dfPeriod['timePeriod']=="night2") | (dfPeriod['timePeriod']=="night3") | (dfPeriod['timePeriod']=="day1") | (dfPeriod['timePeriod']=="day2"))]
                sns.boxplot(data=selectedDfPeriod, x='timePeriod', y='value', hue='genotype', order=["night1", "day1", "night2", "day2", "night3"], hue_order=reversed(genotypeList), ax=ax, linewidth=0.5, showmeans=True,
                meanprops={"marker": 'o',
                           "markerfacecolor": 'white',
                           "markeredgecolor": 'black',
                           "markersize": '8'}, showfliers=False, width=0.8, palette=my_pal, dodge=True)
                
                sns.stripplot(data=selectedDfPeriod, x='timePeriod', y='value', hue='genotype', order=["night1", "day1", "night2", "day2", "night3"], hue_order=reversed(genotypeList), jitter=True, palette='dark:black', s=3,
                              dodge=True, ax=ax)
                ax.legend().set_visible(False)
                ax.set_title(f"{sex}s", fontdict={'fontsize': 16, 'fontweight': "bold"})
                ax.text(-0.3, 1.05, letterList[k], fontsize=18, horizontalalignment='center', color='black', weight='bold', transform=ax.transAxes)
                k += 2
                
                #statistics
                pos=0
                for timePeriod in ["night1", "day1", "night2", "day2", "night3"]:
                    data = dfPeriod.loc[(dfPeriod['sex']==sex) & (dfPeriod['timePeriod']==timePeriod)]
                    print(data)
                    dic = {}
                    dic["value"] = list(data["value"])
                    dic["genotype"] = list(data["genotype"])
                    dic["group"] = list(data["group"])
                    print("########################")
                    dataSimple = pd.DataFrame.from_dict(dic)
                    print(dataSimple.dtypes)
                    # create model:
                    model = smf.mixedlm("value ~ genotype", dataSimple, groups=data["group"])
                    # run model:
                    result = model.fit()
                    # print summary
                    print(event, timePeriod)
                    print(result.summary())
                    p, sign = extractPValueFromLMMResult(result=result, keyword='wt')
                    #add p-values on the plot
                    ax.text(pos, 1150, getStarsFromPvalues(p, 1), fontsize=11, horizontalalignment='center', color='black', weight='bold')
                    pos+=1
        
                               
                row1 += 1
            
            # add legend
            wtPoint = matplotlib.lines.Line2D([0], [0], marker='o', color='w',
                                              markerfacecolor=getColorGeno(genotypeList[0]), markersize=8, alpha=0.9,
                                              label=f"17q21.31 {genotypeList[0]}")
            koPoint = matplotlib.lines.Line2D([0], [0], marker='o', color='w',
                                              markerfacecolor=getColorGeno(genotypeList[1]), markersize=8, alpha=0.9,
                                              label=f"17q21.31 {genotypeList[1]}")
            ax=plt.subplot(gs[0, 0:4])
            ax.legend(handles=[koPoint, wtPoint], frameon=True, fontsize=10, bbox_to_anchor=(0.35, 0.8))
            
            fig.tight_layout()
            print ("Saving figure..." )   
            fig.savefig( f"suppl_fig_actiivty_timeline.png" ,dpi=200)
            fig.savefig( f"suppl_fig_actiivty_timeline.pdf" ,dpi=100)
            
            break
        
        if answer == "3":
            """compute the area under the curve """
            """
            area for one time bin = ((x2-x1) * (min(y1,y2) - 0) + ((x2-x1) * (max(y1, y2) - min(y1, y2)) )/2
            """
            
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
            
            
            
            
            
            break
    
    print("Job done.")