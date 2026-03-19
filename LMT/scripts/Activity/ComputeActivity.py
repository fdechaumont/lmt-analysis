'''
Created by Nicolas Torquet at 15/11/2024
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''


import json
import matplotlib.pyplot as plt
from Activity.ComputeActivityExperiment import completeDicoFromValues
from Animal_LMTtoolkit import *
from FileUtil import getFilesToProcess, getJsonFilesToProcess
import pandas as pd
from matplotlib import rc



def exportResultsSortedBy(files, filters: list):
    # check filters
    acceptedFilters = ["genotype", "sex", "age", "strain", "treatment"]
    for filter in filters:
        print("###### Filters: ######")
        print(filter)
        print("###### ------ ######")
        if filter not in acceptedFilters:
            print(f"Filter {filter} not accepted")
            return False

    reorganizedResults = {}
    for file in files:
        with open(file, 'r') as f:
            file_content = f.read()
        experiment = json.loads(file_content)
        for animal in experiment.keys():
            if animal != 'metadata':
                print(animal)
                reorganizedResults = completeDicoFromValues(experiment[animal], reorganizedResults, filters)


    return reorganizedResults


def getNightsFromJson(file):
    with open(file, 'r') as f:
        file_content = f.read()
    experiment = json.loads(file_content)
    nights = experiment['metadata']['nights']
    return nights


def getTimebinFromJson(file):
    with open(file, 'r') as f:
        file_content = f.read()
    experiment = json.loads(file_content)
    timebin = experiment['metadata']['timeBin']
    return timebin


def getColorGenoTreatment(treatment, geno):
    if (treatment == "chow diet") and (geno == '+/+'):
        return 'lightgrey'
    if (treatment == "chow diet") and (geno == 'Dp(16)1Yey/+'):
        return "yellow"
    if (treatment == "high fat diet") and (geno == '+/+'):
        return "gold"
    if (treatment == "high fat diet") and (geno == 'Dp(16)1Yey/+'):
        return "darkgoldenrod"
    if (treatment == "chow diet") and (geno == 'B6_+/+'):
        return 'white'
    if (treatment == "chow diet") and (geno == 'B6_Dp(16)1Yey/+'):
        return "yellow"
    if (treatment == "high fat diet") and (geno == 'B6_+/+'):
        return "gold"
    if (treatment == "high fat diet") and (geno == 'B6_Dp(16)1Yey/+'):
        return "darkgoldenrod"


def getColorPalettePerTreatment(genoList, treatment):
    paletteDic = {}
    for geno in genoList:
        paletteDic[geno] = getColorGenoTreatment(treatment, geno)
    return paletteDic


def getColorPaletteTreatment(conditionList, genoList):
    paletteDic = {}
    for condition in conditionList:
        paletteDic[condition] = {}
        for geno in genoList:
            paletteDic[condition][geno] = getColorGenoTreatment(condition, geno)
    return paletteDic


def convertFrameNumberForTimeBinTimeline(frameNumber, timebin):
    return frameNumber/timebin

def plotNightTimeLine(nights, timebin, ax):
    for nightEvent in nights:
        ax.axvspan(convertFrameNumberForTimeBinTimeline(nightEvent['startFrame'], timebin), convertFrameNumberForTimeBinTimeline(nightEvent['endFrame'], timebin), alpha=0.1, color='black')
        ax.text(convertFrameNumberForTimeBinTimeline(nightEvent['startFrame'], timebin) + (convertFrameNumberForTimeBinTimeline(nightEvent['endFrame'], timebin) - convertFrameNumberForTimeBinTimeline(nightEvent['startFrame'], timebin)) / 2, 100, "dark phase",
                fontsize=8, ha='center')


def plotActivityPerTimebin(meanAndSEM, timeLine, timeBin, nights, night_hours, title, unit = "cm"):
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(14, 9))
    # females
    ax = axes[1]
    ax.title.set_text(f'{title} - female')
    ax.set_xlabel("time")
    ax.set_ylabel(f"Distance in 10 min ({unit})", fontsize=14)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    for treatment in meanAndSEM['female']:
        print("plot female")
        for genotype in meanAndSEM['female'][treatment]:
            # print(meanAndSEM['female'][treatment][genotype].mean(axis=1))
            ax.plot(timeLine, meanAndSEM['female'][treatment][genotype].mean(axis=1), label=f"{treatment} - {genotype}",
                    color=getColorGenoTreatment(treatment, genotype))
            ax.fill_between(range(len(meanAndSEM['female'][treatment][genotype].mean(axis=1))),
                            meanAndSEM['female'][treatment][genotype].mean(axis=1) - meanAndSEM['female'][treatment][
                                genotype].sem(axis=1),
                            meanAndSEM['female'][treatment][genotype].mean(axis=1) + meanAndSEM['female'][treatment][
                                genotype].sem(axis=1),
                            color=getColorGenoTreatment(treatment, genotype),
                            alpha=0.2)

    ax.legend().set_visible(False)
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    x_ticks = []
    x_labels = []
    for night in nights:
        if night['startFrame']:
            x_ticks.append(convertFrameNumberForTimeBinTimeline(night['startFrame'], timeBin))
            x_labels.append(night_hours[0])
        if night['endFrame']:
            x_ticks.append(convertFrameNumberForTimeBinTimeline(night['endFrame'], timeBin))
            x_labels.append(night_hours[1])
    ax.set_xticks(x_ticks, labels=x_labels)
    plotNightTimeLine(nights, timeBin, ax)

    # males
    ax = axes[0]
    ax.title.set_text(f'{title} - male')
    ax.set_xlabel("time")
    ax.set_ylabel(f"Distance in 10 min ({unit})", fontsize=14)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    for treatment in meanAndSEM['male']:
        print("plot male")
        for genotype in meanAndSEM['male'][treatment]:
            # print(meanAndSEM['female'][treatment][genotype].mean(axis=1))
            ax.plot(timeLine, meanAndSEM['male'][treatment][genotype].mean(axis=1), label=f"{treatment} - {genotype}",
                    color=getColorGenoTreatment(treatment, genotype))
            ax.fill_between(range(len(meanAndSEM['male'][treatment][genotype].mean(axis=1))),
                            meanAndSEM['male'][treatment][genotype].mean(axis=1) - meanAndSEM['male'][treatment][
                                genotype].sem(axis=1),
                            meanAndSEM['male'][treatment][genotype].mean(axis=1) + meanAndSEM['male'][treatment][
                                genotype].sem(axis=1),
                            color=getColorGenoTreatment(treatment, genotype),
                            alpha=0.2)

    ax.legend(loc="best")
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    x_ticks = []
    x_labels = []
    for night in nights:
        if night['startFrame']:
            x_ticks.append(convertFrameNumberForTimeBinTimeline(night['startFrame'], timeBin))
            x_labels.append(night_hours[0])
        if night['endFrame']:
            x_ticks.append(convertFrameNumberForTimeBinTimeline(night['endFrame'], timeBin))
            x_labels.append(night_hours[1])
    ax.set_xticks(x_ticks, labels=x_labels)
    plotNightTimeLine(nights, timeBin, ax)

    plt.show()
    fig.savefig(f"{title}.pdf")
    fig.savefig(f"{title}.png", dpi=300)


def getDistanceDuringDayAndNight(data, nights, timebin):
    distance_during_night = 0
    dataList = []
    for item in data:
        dataList.append(data[item])
    for nightEvent in nights:
        start_night = int(round(convertFrameNumberForTimeBinTimeline(nightEvent['startFrame'], timebin), 0))
        end_night = int(round(convertFrameNumberForTimeBinTimeline(nightEvent['endFrame'], timebin), 0))
        distance_during_night += sum(dataList[start_night:end_night])
    distance_during_day = sum(dataList) - distance_during_night

    return {'distance_during_day': distance_during_day, 'distance_during_night': distance_during_night}


if __name__ == '__main__':
    #set font
    rc('font', **{'family': 'serif', 'serif': ['Arial']})

    # Data from ICS

    # files = getFilesToProcess()
    files = getJsonFilesToProcess()
    filterList = ["sex", "treatment", "genotype"]
    reorganizedResults = exportResultsSortedBy(files, filterList)

    nights = getNightsFromJson(files[0])
    timeBin = getTimebinFromJson(files[0])

    meanAndSEM = {}
    timeLine = []
    timeLineDone = False
    activity_day_night_ics = {}
    for sex in reorganizedResults:
        if sex not in meanAndSEM:
            meanAndSEM[sex] = {}
            activity_day_night_ics[sex] = {}
        for treatment in reorganizedResults[sex]:
            if treatment not in meanAndSEM[sex]:
                meanAndSEM[sex][treatment] = {}
                activity_day_night_ics[sex][treatment] = {}
            for genotype in reorganizedResults[sex][treatment]:
                timeLineAsIndexCompleted = False
                if genotype not in meanAndSEM[sex][treatment]:
                    meanAndSEM[sex][treatment][genotype] = pd.DataFrame()
                    activity_day_night_ics[sex][treatment][genotype] = {}
                for animal in reorganizedResults[sex][treatment][genotype]:
                    print(f"Animal: {animal}")
                    activity = []
                    for timebin in reorganizedResults[sex][treatment][genotype][animal]["results"]:
                        if not timeLineDone:
                            timeLine.append(timebin)
                        activity.append(reorganizedResults[sex][treatment][genotype][animal]["results"][timebin])
                    timeLineDone = True
                    if len(timeLine) > len(activity):
                        numberOfNaNToAdd = len(timeLine) - len(activity)
                        listToAppend = [np.nan] * numberOfNaNToAdd
                        for item in listToAppend:
                            activity.append(item)
                    meanAndSEM[sex][treatment][genotype][animal] = activity
                    activity_day_night_ics[sex][treatment][genotype][animal] = getDistanceDuringDayAndNight(reorganizedResults[sex][treatment][genotype][animal]["results"], nights, timeBin)
    with open('activity_day_night_ics.json', 'w') as f:
        json.dump(activity_day_night_ics, f, indent=4)


    plotActivityPerTimebin(meanAndSEM, timeLine, timeBin, nights, ("07:00", "19:00"), "ICS")

    # Data from HMGU
    files = getJsonFilesToProcess()
    reorganizedResults = exportResultsSortedBy(files, filterList)

    nights = getNightsFromJson(files[0])
    timeBin = getTimebinFromJson(files[0])

    meanAndSEM = {}
    timeLine = []
    timeLineDone = False
    activity_day_night_hmgu = {}
    for sex in reorganizedResults:
        if sex not in meanAndSEM:
            meanAndSEM[sex] = {}
            activity_day_night_hmgu[sex] = {}
        for treatment in reorganizedResults[sex]:
            if treatment not in meanAndSEM[sex]:
                meanAndSEM[sex][treatment] = {}
                activity_day_night_hmgu[sex][treatment] = {}
            for genotype in reorganizedResults[sex][treatment]:
                timeLineAsIndexCompleted = False
                if genotype not in meanAndSEM[sex][treatment]:
                    meanAndSEM[sex][treatment][genotype] = pd.DataFrame()
                    activity_day_night_hmgu[sex][treatment][genotype] = {}
                for animal in reorganizedResults[sex][treatment][genotype]:
                    print(f"Animal: {animal}")
                    activity = []
                    for timebin in reorganizedResults[sex][treatment][genotype][animal]["results"]:
                        if not timeLineDone:
                            timeLine.append(timebin)
                        activity.append(reorganizedResults[sex][treatment][genotype][animal]["results"][timebin])
                    timeLineDone = True
                    if len(timeLine) > len(activity):
                        numberOfNaNToAdd = len(timeLine) - len(activity)
                        listToAppend = [np.nan] * numberOfNaNToAdd
                        for item in listToAppend:
                            activity.append(item)
                    meanAndSEM[sex][treatment][genotype][animal] = activity
                    activity_day_night_hmgu[sex][treatment][genotype][animal] = getDistanceDuringDayAndNight(reorganizedResults[sex][treatment][genotype][animal]["results"], nights, timeBin)
    with open('activity_day_night_hmgu.json', 'w') as f:
        json.dump(activity_day_night_hmgu, f, indent=4)

    plotActivityPerTimebin(meanAndSEM, timeLine, timeBin, nights, ("06:00", "18:00"), "HMGU")

