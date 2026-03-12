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
from FileUtil import getFilesToProcess
import pandas as pd




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


def plotActivityPerTimebin(meanAndSEM, timeLine, nights, title):
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(14, 9))
    # females
    ax = axes[0]
    ax.title.set_text(f'{title} - male')
    ax.set_xlabel("time")

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

    ax.legend(loc="upper center")
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    plotNightTimeLine(nights, timeBin, ax)

    # males
    ax = axes[1]
    ax.title.set_text(f'{title} - male')
    ax.set_xlabel("time")

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

    ax.legend(loc="upper center")

    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    plotNightTimeLine(nights, timeBin, ax)

    plt.show()
    fig.savefig(f"{title}.pdf")


if __name__ == '__main__':
    # Data from ICS

    files = getFilesToProcess()
    filterList = ["sex", "treatment", "genotype"]
    reorganizedResults = exportResultsSortedBy(files, filterList)

    nights = getNightsFromJson(files[0])
    timeBin = getTimebinFromJson(files[0])

    meanAndSEM = {}
    timeLine = []
    timeLineDone = False
    for sex in reorganizedResults:
        if sex not in meanAndSEM:
            meanAndSEM[sex] = {}
        for treatment in reorganizedResults[sex]:
            if treatment not in meanAndSEM[sex]:
                meanAndSEM[sex][treatment] = {}
            for genotype in reorganizedResults[sex][treatment]:
                timeLineAsIndexCompleted = False
                if genotype not in meanAndSEM[sex][treatment]:
                    meanAndSEM[sex][treatment][genotype] = pd.DataFrame()
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


    plotActivityPerTimebin(meanAndSEM, timeLine, nights, "GO-DS21 activity ICS timebin 10min")

    # Data from HMGU
    files = getFilesToProcess()
    reorganizedResults = exportResultsSortedBy(files, filterList)

    meanAndSEM = {}
    timeLine = []
    timeLineDone = False
    for sex in reorganizedResults:
        if sex not in meanAndSEM:
            meanAndSEM[sex] = {}
        for treatment in reorganizedResults[sex]:
            if treatment not in meanAndSEM[sex]:
                meanAndSEM[sex][treatment] = {}
            for genotype in reorganizedResults[sex][treatment]:
                timeLineAsIndexCompleted = False
                if genotype not in meanAndSEM[sex][treatment]:
                    meanAndSEM[sex][treatment][genotype] = pd.DataFrame()
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

    plotActivityPerTimebin(meanAndSEM, timeLine, nights, "GO-DS21 activity HMGU timebin 10min")
