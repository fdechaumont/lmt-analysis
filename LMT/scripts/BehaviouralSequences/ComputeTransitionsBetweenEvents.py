'''
Created on 17 Feb 2022

@author: Elodie
'''

import sqlite3
from random import randint

from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.FileUtil import *
from lmtanalysis.Util import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.BehaviouralSequencesUtil import exclusiveEventList, exclusiveEventsLabels, sexList, genoList, sexListGeneral, genoListGeneral,\
    exclusiveEventListLabels
import pandas as pd
#import pyvis
import seaborn as sns
#from pyvis.network import Network
import matplotlib.pyplot as plt
import networkx as nx
from scipy.stats import mannwhitneyu, ttest_ind, levene
import string
import matplotlib.image as mpimg
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle
from scipy.stats._morestats import shapiro
import os

def computeTransitionsBetweenExclusiveEventsPerFile(file, minT, maxT, resultsTransitionsProba):
    print(file)
    #get the path and the name of file
    head, tail = os.path.split(file)
    
    connection = sqlite3.connect(file)
    pool = AnimalPool()
    pool.loadAnimals(connection)
    pool.loadDetection(start=minT, end=maxT, lightLoad=True)
    
    genoPossibility = []
    sexPossibility = []
    for animal in pool.animalDictionary.keys():
        print("computing individual animal: {}".format(animal))
        geno = pool.animalDictionary[animal].genotype
        sex = pool.animalDictionary[animal].sex
        genoPossibility.append(geno)
        sexPossibility.append(sex)

    genoListInFile = sorted( genoPossibility, reverse=True )
    genoGroup = '{}-{}'.format(genoListInFile[0], genoListInFile[1])
    sexListInFile = sorted( sexPossibility, reverse=True )
    sexGroup = '{}-{}'.format(sexListInFile[0], sexListInFile[1])
    
    if not sexGroup in resultsTransitionsProba.keys():
        resultsTransitionsProba[sexGroup] = {}
    if not genoGroup in resultsTransitionsProba[sexGroup].keys():
        resultsTransitionsProba[sexGroup][genoGroup] = {}
    
    resultsTransitionsProba[sexGroup][genoGroup][file] = {}

    for animal in pool.animalDictionary.keys():
        print("computing individual animal: {}".format(animal))
        rfid = pool.animalDictionary[animal].RFID
        sex = pool.animalDictionary[animal].sex
        geno = pool.animalDictionary[animal].genotype

        #load timelines for exclusive events for animal:
        eventTimeLine = {}
        dicoEvent = {}
        results = {}
        timeLineList = []
        for exclusiveEvent in exclusiveEventList:
            eventTimeLine[exclusiveEvent] = EventTimeLineCached( connection, file, exclusiveEvent, animal, None, minFrame=minT, maxFrame=maxT )
            dicoEvent[exclusiveEvent] = eventTimeLine[exclusiveEvent].getDictionary(minFrame=minT, maxFrame=maxT)
            timeLineList.append(eventTimeLine[exclusiveEvent])
            results[exclusiveEvent] = {}
            for event in exclusiveEventList:
                results[exclusiveEvent][event] = 0

        totalDurationEvents = 0
        for exclusiveEvent in exclusiveEventList:
            print('{}: event total duration: {}, length of dico: {}'.format(exclusiveEvent, eventTimeLine[exclusiveEvent].getTotalLength(), len(dicoEvent[exclusiveEvent])))
            totalDurationEvents += len(dicoEvent[exclusiveEvent])

        detection = pool.animalDictionary[animal].detectionDictionary
        print('Number of frames detected: {}; sum of duration of events: {}'.format(len(detection.keys()), totalDurationEvents))

        counter = {}
        labels = {}
        for t in detection.keys():
            counter[t] = 0
            labels[t] = []
            for exclusiveEvent in exclusiveEventList:
                if t in dicoEvent[exclusiveEvent].keys():
                    counter[t] += 1
                    labels[t].append(exclusiveEvent)

        for t in detection.keys():
            if counter[t] == 0:
                print('No event at ', t, labels[t])
            elif counter[t] > 1:
                print('More than one event at t=', t, ': ', counter[t], labels[t])

        for exclusiveEvent in exclusiveEventList:
            for event in eventTimeLine[exclusiveEvent].eventList:
                firstFrame = event.startFrame
                lastFrame = event.endFrame
                if lastFrame >= maxT:
                    break
                else:
                    test = 0
                    for exclusiveEventFollow in exclusiveEventList:
                        if eventTimeLine[exclusiveEventFollow].hasEvent(lastFrame+1):
                            test = 1
                            results[exclusiveEvent][exclusiveEventFollow] += 1
                            #print('Event {}: first frame = {} last frame = {}, next event: {}'.format(exclusiveEvent, firstFrame, lastFrame, exclusiveEventFollow))

                if test == 0:
                    print('############Event {}: first frame = {} last frame = {}'.format(exclusiveEvent, firstFrame, lastFrame))

            results[exclusiveEvent]['all'] = eventTimeLine[exclusiveEvent].getNumberOfEvent(minFrame=minT, maxFrame=maxT)

        resultsDic = {}
        for exclusiveEvent in exclusiveEventList:
            resultsDic[exclusiveEvent] = []
            for exclusiveEventFollow in exclusiveEventList:
                resultsDic[exclusiveEvent].append(results[exclusiveEvent][exclusiveEventFollow])

        print(resultsDic)
        resultsTransitionsProba[sexGroup][genoGroup][file][rfid] = { 'geno': geno, 'sex': sex, 'value': resultsDic }

    
    with open(f"{head}/transition_{minT}_{maxT}.json", 'w') as jFile:
        json.dump(resultsTransitionsProba, jFile, indent=4)
    print("json file created")


correspondanceList = [ (0.001, 1),
                      ( 0.01 , 0.9 ),
                      ( 0.05 , 0.8 ),
                      ( 0.1 , 0.2 )
                      ]
radiusScale = 3/7.0
effectSizeAmplitude = 1

def pValueToCircleSize( pValue ):
    
    size = 1
    for v in correspondanceList:
        if pValue >= v[0]:
            size = v[1]
    print( "pval to size: " , pValue, size )
    return size

def featureHeatMap( dfEffectSize, dfPValue, ax , title=None,showLegend=False ):
    
    print("Data frame effect size:")            
    print( dfEffectSize )

    print("Data frame dfPValue:")            
    print( dfPValue )
    
    # labels
    
    xlabels = list( dfEffectSize.head() )
    ylabels = list( dfEffectSize.index )
        
    M= len( xlabels )
    N= len( ylabels )
    
    x, y = np.meshgrid(np.arange(M), np.arange(N))
    print( x )
    print( y )
    

    circles = []
    colors = []
    s = []
    xx = 0
    for labX in xlabels:
        row = []
        yy=0
        for labY in ylabels:        
            effectSizeValue = dfEffectSize.loc[labY][labX]
            pValue = dfPValue.loc[labY][labX]
            row.append( dfEffectSize.loc[labY][labX] )
            print( xx , yy , effectSizeValue )
            circles.append ( Circle(( xx,yy ), radius=pValueToCircleSize(pValue) * radiusScale ) )
            colors.append( effectSizeValue )                    
            yy+=1
        xx+=1
        s.append(row)
    
    s = np.array( s )
    print( s )
    
    #fig, ax = plt.subplots( figsize=( len( xlabels ), len( ylabels ) ) )
    

    print ( circles )
    print( colors )
    col = PatchCollection(circles, array=np.array(colors), cmap="coolwarm" )
    # effect size scale
    col.set_clim([-effectSizeAmplitude, effectSizeAmplitude ])
    ax.add_collection(col)
        
    ax.set(xticks=np.arange(M), yticks=np.arange(N),
           xticklabels=xlabels , yticklabels= ""*len(ylabels) )
    ax.set_xticks(np.arange(M+1)-0.5, minor=True)
    ax.set_yticks(np.arange(N+1)-0.5, minor=True)
    ax.grid(which='minor')

    if title!=None:
        ax.set_title( title )

    ax.invert_yaxis()
    
    #plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    #plt.tight_layout()

    #FIXME
    #fig.colorbar(col)
    
    # draw p-value legend    
    if showLegend==True:
        y=0
        for v in correspondanceList:
            pValue= v[0]
            circle = plt.Circle( ( M+1, y ), pValueToCircleSize(pValue) * radiusScale , color='grey', clip_on=False)
            plt.text(M+1, y+0.6, "<="+str(pValue), fontsize=10, ha="center",va="center")
            ax.add_patch( circle )
            y+=1.2

    #plt.savefig( "test_"+ str( randint(1,1000))+".pdf" )
    return ax
    #plt.show()
    




def plotTransitionGraphExclusiveEvents(ax, exclusiveEventList, exclusiveEventsLabels, posNodes, matrix, nodeWeightPropList):
    G = nx.DiGraph()

    # plot the nodes
    n = 0
    for event in exclusiveEventList:
        G.add_node(event, label=exclusiveEventsLabels)
        n += 1

    # plot the connections
    row = 0
    for event in exclusiveEventList:
        col = 0
        for nextEvent in exclusiveEventList:
            if nextEvent != event:
                G.add_edge(event, nextEvent, weight=matrix[row][col])

            col += 1
        row += 1

    edge0 = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] > 0.5]
    edge1 = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= 0.5 and d['weight'] > 0.4]
    edge2 = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= 0.4 and d['weight'] > 0.3]
    edge3 = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= 0.3 and d['weight'] > 0.2]
    edge4 = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= 0.2 and d['weight'] > 0.1]
    edge5 = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= 0.1]

    width0 = [d['weight'] * 10 for (u, v, d) in G.edges(data=True) if d['weight'] > 0.5]
    width1 = [d['weight'] * 10 for (u, v, d) in G.edges(data=True) if d['weight'] <= 0.5 and d['weight'] > 0.4]
    width2 = [d['weight'] * 10 for (u, v, d) in G.edges(data=True) if d['weight'] <= 0.4 and d['weight'] > 0.3]
    width3 = [d['weight'] * 10 for (u, v, d) in G.edges(data=True) if d['weight'] <= 0.3 and d['weight'] > 0.2]
    width4 = [d['weight'] * 10 for (u, v, d) in G.edges(data=True) if d['weight'] <= 0.2 and d['weight'] > 0.1]
    width5 = [d['weight'] * 10 for (u, v, d) in G.edges(data=True) if d['weight'] <= 0.1]

    # determine the positions of the nodes
    # nodes
    nx.draw_networkx_nodes(G, posNodes, ax=ax, node_size=nodeWeightPropList, node_color='blue', alpha=0.4)

    # labels
    nx.draw_networkx_labels(G, posNodes, ax=ax, labels=exclusiveEventsLabels, font_size=16, font_color='black',
                            font_family='sans-serif', font_weight='bold', verticalalignment='top')

    #curved edges
    # edges
    nx.draw_networkx_edges(G, posNodes, ax=ax, edgelist=edge0, width=width0, edge_color='red', arrows=True, arrowstyle='-|>',
                           connectionstyle='arc3,rad=0.3', alpha=0.65)
    nx.draw_networkx_edges(G, posNodes, ax=ax, edgelist=edge1, width=width1, edge_color='darkorange', arrows=True,
                           arrowstyle='-|>', connectionstyle='arc3,rad=0.3', alpha=0.65)
    nx.draw_networkx_edges(G, posNodes, ax=ax, edgelist=edge2, width=width2, edge_color='gold', arrows=True,
                           arrowstyle='-|>', connectionstyle='arc3,rad=0.3', alpha=0.65)
    nx.draw_networkx_edges(G, posNodes, ax=ax, edgelist=edge3, width=width3, edge_color='lightgreen', arrows=True,
                           arrowstyle='-|>', connectionstyle='arc3,rad=0.3', alpha=0.65)
    nx.draw_networkx_edges(G, posNodes, ax=ax, edgelist=edge4, width=width4, edge_color='darkgreen', arrows=True,
                           arrowstyle='-|>', connectionstyle='arc3,rad=0.3', alpha=0.65)
    nx.draw_networkx_edges(G, posNodes, ax=ax, edgelist=edge5, width=width5, edge_color='blue', arrows=True,
                           arrowstyle='-|>', connectionstyle='arc3,rad=0.3', alpha=0.05)

    ax.axis('off')
    patch0 = mpatches.Patch(edgecolor='red', facecolor='red', alpha=0.65, label='>0.5')
    patch1 = mpatches.Patch(edgecolor='darkorange', facecolor='darkorange', alpha=0.65, label='0.4<x<=0.5')
    patch2 = mpatches.Patch(edgecolor='gold', facecolor='gold', alpha=0.65, label='0.3<x<=0.4')
    patch3 = mpatches.Patch(edgecolor='lightgreen', facecolor='lightgreen', alpha=0.65, label='0.2<x<=0.3')
    patch4 = mpatches.Patch(edgecolor='darkgreen', facecolor='darkgreen', alpha=0.65, label='0.1<x<=0.2')
    patch5 = mpatches.Patch(edgecolor='blue', facecolor='blue', alpha=0.1, label='x<=0.1')
    
    handles = [patch0, patch1, patch2, patch3, patch4, patch5]
    return handles


def plotTransitionOccurrencesPerGeno(ax, dataDic, exclusiveEventList, sexGroup, genoGroup, posNodes, exclusiveEventsLabels, addLegend):
    matrixGeneral = []
    for event in exclusiveEventList:
        matrix = []
        for file in dataDic[sexGroup][genoGroup].keys():
            for rfid in dataDic[sexGroup][genoGroup][file].keys():
                rawVal = dataDic[sexGroup][genoGroup][file][rfid]['value'][event]
                #print('raw: ', rawVal)
                proba = [x / np.sum(rawVal) for x in rawVal]
                #print('proba: ', proba)
                matrix.append(proba)
        matrixPerEvent = list(np.mean(matrix, axis=0))
        matrixGeneral.append(matrixPerEvent)
    print('Transitions: ', matrixGeneral)

    #node weight
    nodeWeightPropGeneral = []
    for file in dataDic[sexGroup][genoGroup].keys():
        for rfid in dataDic[sexGroup][genoGroup][file].keys():
            nodeWeightList = []
            for event in exclusiveEventList:
                rawVal = dataDic[sexGroup][genoGroup][file][rfid]['value'][event]
                #print('raw: ', rawVal)
                proba = [x / np.sum(rawVal) for x in rawVal]
                #print('proba: ', proba)
                #matrix[event].append(proba)
                nodeWeightList.append(np.sum(rawVal))

            totalNbEvents = np.sum(nodeWeightList)
            nodeWeightPropList = [a / totalNbEvents for a in nodeWeightList]
            nodeWeightPropGeneral.append(nodeWeightPropList)

    nodeWeightPropPerGeno = np.mean(nodeWeightPropGeneral, axis=0)
    print(genoGroup, nodeWeightPropPerGeno*1000, np.sum(nodeWeightPropPerGeno*1000))

    handles = plotTransitionGraphExclusiveEvents(ax=ax, exclusiveEventList=exclusiveEventList,
                                       exclusiveEventsLabels=exclusiveEventsLabels, posNodes=posNodes, matrix=matrixGeneral,
                                       nodeWeightPropList=nodeWeightPropPerGeno*1000)
    if addLegend == True:
        ax.legend(handles=handles, loc=(0.95, 0.1), fontsize=14, title='Prop. of transitions:', title_fontsize=14).set_visible(True)

    ax.text(x=0, y=1.3, s='{}'.format(genoGroup), fontsize=20, weight='bold')



def plotHeatmapEffectSizePVal(dataDic, ax, n, exclusiveEventList, genoGroupList, sexGroup, exclusiveEventListLabels, letterList, titleList):
    # generate the data for the comparison of the transitions
    dicPerInd = {}
    for eventA in exclusiveEventList:
        dicPerInd[eventA] = {}
        for eventB in exclusiveEventList:
            if eventA == eventB:
                continue
            dicPerInd[eventA][eventB] = {}
            for geno in genoGroupList:
                dicPerInd[eventA][eventB][geno] = []
                for file in dataDic[sexGroup][geno].keys():
                    for rfid in dataDic[sexGroup][geno][file].keys():
                        rawValList = dataDic[sexGroup][geno][file][rfid]['value'][eventA]
                        propList = [x / np.sum(rawValList) for x in rawValList]
                        rawVal = propList[exclusiveEventList.index(eventB)]
                        dicPerInd[eventA][eventB][geno].append(rawVal)
            
    dfEffectSize = pd.DataFrame(columns=exclusiveEventList)
    dfPValue = pd.DataFrame(columns=exclusiveEventList)
    # compare the transitions between genotypes
    for eventA in exclusiveEventList:
        transitRowEffectSize = []
        transitRowPValue = []
        for eventB in exclusiveEventList:
            if eventA == eventB:
                p = 1
                effectSize = 0
                effectSizeCorrected = 0
                transitRowEffectSize.append(effectSizeCorrected)
                transitRowPValue.append(p)
                continue
            
            dataGenoA = dicPerInd[eventA][eventB][genoGroupList[0]]
            dataGenoB = dicPerInd[eventA][eventB][genoGroupList[1]]
            
            WA, pNormA = shapiro( dataGenoA )
            WB, pNormB = shapiro( dataGenoB )
            L, pLevene = levene( dataGenoA, dataGenoB )
            if (pNormA >= 0.05) & (pNormB >= 0.05) & (pLevene >= 0.05):
                print("####normal data")
                W, p = ttest_ind(dataGenoA, dataGenoB, nan_policy='omit')
            else:
                print("####data not normal")
                W, p = mannwhitneyu(dataGenoA, dataGenoB)
            print('p=', p)
            
            #W, p = mannwhitneyu(dataGenoA, dataGenoB)
            effectSize = (np.mean(dataGenoA) - np.mean(dataGenoB)) / np.std(dataGenoA+dataGenoB)
            effectSizeCorrected = effectSize * (len(dataGenoA) + len(dataGenoB) - 3) / (len(dataGenoA) + len(dataGenoB) -2.25) #corrected because the effect size is boosted with small sample sizes
            transitRowEffectSize.append(effectSizeCorrected)
            transitRowPValue.append(p*12*11) #correction by the number of tests conducted!
            
            if (p < 0.05) and (np.mean(dataGenoA)>0.1) and (np.mean(dataGenoB)>0.1):
                print(eventA, ' versus ', eventB)
                print('Mann-Whitney U for transitions proba, {} n={} {}+/-{}, {} n={} {}+/-{}: W={}, p={}, d={}'.format(genoGroupList[0], len(dataGenoA), round(np.mean(dataGenoA), 3), round(np.std(dataGenoA), 3), genoGroupList[1],
                                                                                  len(dataGenoB), round(np.mean(dataGenoB),3), round(np.std(dataGenoB),3), W, p, round(effectSizeCorrected, 3)))
        newRowEffectSize = pd.DataFrame(data=np.array([transitRowEffectSize]), columns=exclusiveEventList)
        dfEffectSize = pd.concat([dfEffectSize, newRowEffectSize], ignore_index=True)
        newRowPValue = pd.DataFrame(data=np.array([transitRowPValue]), columns=exclusiveEventList)
        dfPValue = pd.concat([dfPValue, newRowPValue], ignore_index=True)
        
    dfEffectSize['eventA'] = exclusiveEventList
    dfEffectSize.set_index('eventA', inplace=True)
    print('##########', dfEffectSize)
    
    dfPValue['eventA'] = exclusiveEventList
    dfPValue.set_index('eventA', inplace=True)
    #print(dfPValue)
    
    ax.text(-5.2, -1, letterList[n], fontsize=22, horizontalalignment='center', color='black', weight='bold')
    ax.text(-4.8, 6, 'initial event', fontsize=16, rotation=90, verticalalignment='center', color='black', weight='bold')
    ax.text(5, 14.5, 'subsequent event', fontsize=16, horizontalalignment='center', color='black', weight='bold')
    
    g = featureHeatMap( dfEffectSize, dfPValue , ax =ax , title = titleList[n], showLegend=False )
    #g.set_yticks(tickPos)
    g.set_yticklabels(exclusiveEventListLabels, rotation=0, fontsize=12)
    g.set_xticklabels(exclusiveEventListLabels, rotation=45, fontsize=12, horizontalalignment='right')
    

posNodes = {'Oral-oral Contact exclusive': [0.8, 0.4],
           'Side by side Contact exclusive': [0.7, 0.9],
           'Oral-genital Contact exclusive': [0.9, -0.4],
           'Passive oral-genital Contact exclusive': [-0.6, -0.4],
           'Side by side Contact, opposite way exclusive': [0.3, -0.4],
           'Oral-oral and Side by side Contact exclusive': [1.1, 0.9],
           'Oral-genital and Side by side Contact, opposite way exclusive': [0.7, -1],
           'Oral-genital passive and Side by side Contact, opposite way exclusive': [-0.3, -1],
            'Other contact exclusive': [0.3, 0.2],
           'Move isolated exclusive': [-0.9, 0.4],
           'Stop isolated exclusive': [-0.3, 0.4],
           'Undetected exclusive': [-0.6, 1.1]}


'''#positions of nodes for circular representation
posNodes = {'Oral-oral Contact exclusive': [0.92967342, -0.21574688],
           'Side by side Contact exclusive': [-0.24521204, -0.97102128],
           'Oral-genital Contact exclusive': [0.71596641, -0.69632756],
           'Passive oral-genital Contact exclusive': [0.25670149, -0.83772246],
           'Side by side Contact, opposite way exclusive': [-0.59330737, -0.68161536],
           'Oral-oral and Side by side Contact exclusive': [-0.89684737, -0.32672216],
           'Oral-genital and Side by side Contact, opposite way exclusive': [-0.85378855,
                                                                             0.17365384],
           'Oral-genital passive and Side by side Contact, opposite way exclusive':
               [-0.77021796, 0.64558224], 'Other contact exclusive': [0.86265226, 0.27528991],
           'Move isolated exclusive': [0.22122907, 1.],
           'Stop isolated exclusive': [-0.30592075, 0.90912759],
           'Undetected exclusive': [0.6790714, 0.72550211]}'''

if __name__ == '__main__':

    pd.set_option("display.max_rows", None, "display.max_columns", None)
    # set font
    from matplotlib import rc, gridspec
    rc('font', **{'family': 'serif', 'serif': ['Arial']})
    letterList = list(string.ascii_uppercase)

    print("Code launched.")

    

    while True:
        question = "Do you want to:"
        question += "\n\t [1] compute transition occurrences between exclusive events over nights?"
        question += "\n\t [1a] compute transition occurrences between exclusive events over specific (short) duration?"
        question += "\n\t [1b] compute transition occurrences between exclusive events over specific (short) duration from paused frame?"
        question += "\n\t [2] plot transition occurrences between exclusive events for each individual per experiment?"
        question += "\n\t [2b] merge the json files of transitions of the two nights within one single json file?"
        question += "\n\t [3] plot transition occurrences between exclusive events per genotype?"
        question += "\n\t [4] conduct statistical comparisons of transition between exclusive events per genotype with two sets of data?"
        question += "\n\t [5] conduct statistical comparisons of transition between exclusive events per genotype with one set of data?"
        question += "\n"
        answer = input(question)

        if answer == '1':
            #Compute transition occurrences between exclusive events over nights
            tmin, tmax = getMinTMaxTInput()
            files = getFilesToProcess()
            
            for file in files:
                print(file)
                #get the path and the name of file
                head, tail = os.path.split(file)
                
                connection = sqlite3.connect(file)
                pool = AnimalPool()
                pool.loadAnimals(connection)

                resultsTransitionsProba = {}
                for sex in sexListGeneral:
                    resultsTransitionsProba[sex] = {}
                    for geno in genoListGeneral:
                        resultsTransitionsProba[sex][geno] = {}

                genoPossibility = []
                sexPossibility = []
                for animal in pool.animalDictionary.keys():
                    print("computing individual animal: {}".format(animal))
                    geno = pool.animalDictionary[animal].genotype
                    sex = pool.animalDictionary[animal].sex
                    genoPossibility.append(geno)
                    sexPossibility.append(sex)

                genoListInFile = sorted( genoPossibility, reverse=True )
                genoGroup = '{}-{}'.format(genoListInFile[0], genoListInFile[1])
                sexListInFile = sorted( sexPossibility, reverse=True )
                sexGroup = '{}-{}'.format(sexListInFile[0], sexListInFile[1])
                
                if not sexGroup in resultsTransitionsProba.keys():
                    resultsTransitionsProba[sexGroup] = {}
                if not genoGroup in resultsTransitionsProba[sexGroup].keys():
                    resultsTransitionsProba[sexGroup][genoGroup] = {}
    
                resultsTransitionsProba[sexGroup][genoGroup][file] = {}

                nightEventTimeLine = EventTimeLineCached(connection, file, "night", minFrame=tmin, maxFrame=tmax)
                n = 1

                for eventNight in nightEventTimeLine.getEventList():
                    minT = eventNight.startFrame
                    maxT = eventNight.endFrame
                    print("Night: ", n)
                    resultsTransitionsProba[sexGroup][genoGroup][file] = {}

                    pool.loadDetection(start=minT, end=maxT, lightLoad=True)

                    for animal in pool.animalDictionary.keys():
                        print("computing individual animal: {}".format(animal))
                        rfid = pool.animalDictionary[animal].RFID
                        sex = pool.animalDictionary[animal].sex
                        geno = pool.animalDictionary[animal].genotype

                        #load timelines for exclusive events for animal:
                        eventTimeLine = {}
                        dicoEvent = {}
                        results = {}
                        timeLineList = []
                        for exclusiveEvent in exclusiveEventList:
                            eventTimeLine[exclusiveEvent] = EventTimeLineCached( connection, file, exclusiveEvent, animal, None, minFrame=minT, maxFrame=maxT )
                            dicoEvent[exclusiveEvent] = eventTimeLine[exclusiveEvent].getDictionary(minFrame=minT, maxFrame=maxT)
                            timeLineList.append(eventTimeLine[exclusiveEvent])
                            results[exclusiveEvent] = {}
                            for event in exclusiveEventList:
                                results[exclusiveEvent][event] = 0

                        totalDurationEvents = 0
                        for exclusiveEvent in exclusiveEventList:
                            print('{}: event total duration: {}, length of dico: {}'.format(exclusiveEvent, eventTimeLine[exclusiveEvent].getTotalLength(), len(dicoEvent[exclusiveEvent])))
                            totalDurationEvents += len(dicoEvent[exclusiveEvent])

                        detection = pool.animalDictionary[animal].detectionDictionary
                        print('Number of frames detected: {}; sum of duration of events: {}'.format(len(detection.keys()), totalDurationEvents))

                        counter = {}
                        labels = {}
                        for t in detection.keys():
                            counter[t] = 0
                            labels[t] = []
                            for exclusiveEvent in exclusiveEventList:
                                if t in dicoEvent[exclusiveEvent].keys():
                                    counter[t] += 1
                                    labels[t].append(exclusiveEvent)

                        for t in detection.keys():
                            if counter[t] == 0:
                                print('No event at ', t, labels[t])
                            elif counter[t] > 1:
                                print('More than one event at t=', t, ': ', counter[t], labels[t])

                        for exclusiveEvent in exclusiveEventList:
                            for event in eventTimeLine[exclusiveEvent].eventList:
                                firstFrame = event.startFrame
                                lastFrame = event.endFrame
                                if lastFrame >= maxT:
                                    break
                                else:
                                    test = 0
                                    for exclusiveEventFollow in exclusiveEventList:
                                        if eventTimeLine[exclusiveEventFollow].hasEvent(lastFrame+1):
                                            test = 1
                                            results[exclusiveEvent][exclusiveEventFollow] += 1
                                            #print('Event {}: first frame = {} last frame = {}, next event: {}'.format(exclusiveEvent, firstFrame, lastFrame, exclusiveEventFollow))

                                if test == 0:
                                    print('############Event {}: first frame = {} last frame = {}'.format(exclusiveEvent, firstFrame, lastFrame))

                            results[exclusiveEvent]['all'] = eventTimeLine[exclusiveEvent].getNumberOfEvent(minFrame=minT, maxFrame=maxT)

                        resultsDic = {}
                        for exclusiveEvent in exclusiveEventList:
                            resultsDic[exclusiveEvent] = []
                            for exclusiveEventFollow in exclusiveEventList:
                                resultsDic[exclusiveEvent].append(results[exclusiveEvent][exclusiveEventFollow])

                        print(resultsDic)
                        resultsTransitionsProba[sexGroup][genoGroup][file][rfid] = { 'geno': geno, 'sex': sex, 'value': resultsDic }
                
                    with open(f"{head}/transition_night_{tail}_{n}.json", 'w') as jFile:
                        json.dump(resultsTransitionsProba, jFile, indent=4)
                    print("json file created")
                    
                    n +=1
            print("Job done.")
            break

        if answer == '1a':
            #Compute transition occurrences between exclusive events over shorter time
            tmin, tmax = getMinTMaxTInput()
            files = getFilesToProcess()
            
            for file in files:
                print(file)
                connection = sqlite3.connect(file)
                pool = AnimalPool()
                pool.loadAnimals(connection)
                
                resultsTransitionsProba = {}
                
                minT = tmin
                maxT = tmax
                
                computeTransitionsBetweenExclusiveEventsPerFile(file=file, minT=minT, maxT=maxT, resultsTransitionsProba=resultsTransitionsProba)
            
            print('Job done.')

            break

        if answer == '1b':
            #Compute transition occurrences between exclusive events over shorter time from paused frame
            experimentDuration = getExperimentDurationInput()
            files = getFilesToProcess()

            for file in files:
                print(file)
                connection = sqlite3.connect(file)
                pool = AnimalPool()
                pool.loadAnimals(connection)

                minT = getStartTestPhase(pool)
                maxT = minT + experimentDuration
                
                resultsTransitionsProba = {}
                
                computeTransitionsBetweenExclusiveEventsPerFile(file=file, minT=minT, maxT=maxT, resultsTransitionsProba=resultsTransitionsProba)
            
            print('Job done.')

            break
        
        if answer == '2':
            # Plot transition between exclusive events for each individual per experiment
            jsonFilesList = getJsonFilesWithSpecificNameToProcess(namePartIncluded = 'transition_')
            
            for jsonFileName in jsonFilesList:
                with open(jsonFileName) as json_data:
                    dataDic = json.load(json_data)
                
                """dataDic = {}
                for jsonFileName in jsonFilesList:
                    with open(jsonFileName) as json_data:
                        data = json.load(json_data)
                    
                    sexGroup = list(data.keys())[0]
                    if not sexGroup in dataDic.keys():
                        dataDic[sexGroup] = {}
                    if not genoGroup in list(dataDic[sexGroup].keys())[0]:
                        dataDic[sexGroup][genoGroup] = {}"""
                         
                    
                print("json file re-imported.")

                print(dataDic)
                sexGroup = list(dataDic.keys())[0]
                print(sexGroup)
                genoGroup = list(dataDic[sexGroup].keys())[0]
                
                file = list(dataDic[sexGroup][genoGroup].keys())[0]
                #get the path and the name of file
                head, tail = os.path.split(jsonFileName)
                
                fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(16, 8))
                figNb = 0
                for rfid in dataDic[sexGroup][genoGroup][file].keys():
                    ax = axes[figNb]
                    matrix = []
                    nodeWeightList = []
                    for event in exclusiveEventList:
                        rawVal = dataDic[sexGroup][genoGroup][file][rfid]['value'][event]
                        print('raw: ', rawVal)
                        proba = [x/np.sum(rawVal) for x in rawVal]
                        print('proba: ', proba)
                        matrix.append(proba)
                        nodeWeightList.append(np.sum(rawVal))

                    totalNbEvents = np.sum(nodeWeightList)
                    nodeWeightPropList = [a/totalNbEvents*1000 for a in nodeWeightList]
                    print(matrix)

                    # pos = nx.spring_layout(G)
                    # print(pos)


                    plotTransitionGraphExclusiveEvents(ax=ax, exclusiveEventList=exclusiveEventList, exclusiveEventsLabels=exclusiveEventsLabels, posNodes=posNodes, matrix=matrix, nodeWeightPropList=nodeWeightPropList)

                    ax.set_title('{} {}'.format(rfid[-4:], dataDic[sexGroup][genoGroup][file][rfid]['geno']))
                    figNb += 1

                patch0 = mpatches.Patch(edgecolor='black', facecolor='red', label='>0.5')
                patch1 = mpatches.Patch(edgecolor='black', facecolor='darkorange', label='0.4<x<=0.5')
                patch2 = mpatches.Patch(edgecolor='black', facecolor='gold', label='0.3<x<=0.4')
                patch3 = mpatches.Patch(edgecolor='black', facecolor='lightgreen', label='0.2<x<=0.3')
                patch4 = mpatches.Patch(edgecolor='black', facecolor='darkgreen', label='0.1<x<=0.2')
                patch5 = mpatches.Patch(edgecolor='black', facecolor='blue', label='x<=0.1')
                handles = [patch0, patch1, patch2, patch3, patch4, patch5]
                axes[0].legend(handles=handles, loc=(0.90, 0.1)).set_visible(True)

                fig.tight_layout()
                #fig.show()
                fig.savefig(f'{head}/transition_exp_{file[-11:-7]}.png', dpi = 200)
            
            print('Job done.')
            
            break
        
        if answer == '2a':
            # Merge json files for transitions between the different experiments within a folder
            jsonFilesList = getJsonFilesWithSpecificNameToProcess(namePartIncluded = 'transition_')
            
            commonFolder = os.path.commonprefix(jsonFilesList)
            print(commonFolder)
            splitPath = os.path.split(commonFolder)
            print(splitPath)
            
            dataDic = {}
            
            for jsonFileName in jsonFilesList:
                print(jsonFileName)
                with open(jsonFileName) as json_data:
                    data = json.load(json_data)
                print("json file re-imported.")
                
                sexGroup = list(data.keys())[0]
                genoGroup = list(data[sexGroup].keys())[0]
                if not sexGroup in dataDic.keys():
                    dataDic[sexGroup] = {}
                if not genoGroup in dataDic[sexGroup].keys():
                    dataDic[sexGroup][genoGroup] = {}
                
                file = list(data[sexGroup][genoGroup].keys())[0]
                
                dataDic[sexGroup][genoGroup][file] = data[sexGroup][genoGroup][file]
                
                         
            with open(f"{splitPath[0]}/transitionEvents_merged_files.json", 'w') as jFile:
                json.dump(dataDic, jFile, indent=4)
            print("json file created")        
                

            print("Job done.")
            break
        
        if answer == '2b':
            # Merge json files for transitions between the different nights
            # open the json file for the first night
            print('Choose the json file for the first night.')
            jsonFileName = getJsonFileToProcess()
            with open(jsonFileName) as json_data:
                dataDic1 = json.load(json_data)
                
            # open the json file for the first night
            print('Choose the json file for the second night.')
            jsonFileName = getJsonFileToProcess()
            with open(jsonFileName) as json_data:
                dataDic2 = json.load(json_data)
            print("json files re-imported.")
            
            dataDic = {}
            for interaction in dataDic1.keys():
                dataDic[interaction] = {}
                for genoPair in dataDic1[interaction].keys():
                    dataDic[interaction][genoPair] = {}
                    for file in dataDic1[interaction][genoPair].keys():
                        dataDic[interaction][genoPair][file] = {}
                        for rfid in dataDic1[interaction][genoPair][file].keys():
                            dataDic[interaction][genoPair][file][rfid] = {}
                            dataDic[interaction][genoPair][file][rfid]['geno'] = dataDic1[interaction][genoPair][file][rfid]['geno']
                            dataDic[interaction][genoPair][file][rfid]['sex'] = dataDic1[interaction][genoPair][file][rfid]['sex']
                            dataDic[interaction][genoPair][file][rfid]['value'] = {}
                            for event in exclusiveEventList:
                                dataDic[interaction][genoPair][file][rfid]['value'][event] = []
                                for n in range(len(dataDic1[interaction][genoPair][file][rfid]['value'][event])):
                                    temporaryValue = dataDic1[interaction][genoPair][file][rfid]['value'][event][n] + dataDic2[interaction][genoPair][file][rfid]['value'][event][n]
                                    dataDic[interaction][genoPair][file][rfid]['value'][event].append(temporaryValue)
                                    
            with open('transition_over_nights.json', 'w') as jFile:
                json.dump(dataDic, jFile, indent=4)
            print("json file created")    
            
            break

        if answer == '3':
            # Plot transition between exclusive events for each genotype
            # open the json file
            jsonFileName = getJsonFileToProcess()
            splitPath = os.path.split(jsonFileName)
            print(splitPath)
            
            with open(jsonFileName) as json_data:
                dataDic = json.load(json_data)
            print("json file re-imported.")
            
            sexGroup = list(dataDic.keys())[0]
            genoGroupList = list(dataDic[sexGroup].keys())
            
            
            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(16, 8))
            figNb = 0
            for genoGroup in genoGroupList:

                ax = axes[figNb]
                legendOnPlot = False
                if figNb == 0:
                    legendOnPlot = True

                #transition plot
                plotTransitionOccurrencesPerGeno(ax=ax, dataDic=dataDic, exclusiveEventList=exclusiveEventList, sexGroup=sexGroup, genoGroup=genoGroup, posNodes=posNodes, exclusiveEventsLabels=exclusiveEventsLabels, addLegend=legendOnPlot)
            
                figNb += 1


            fig.tight_layout()
            #fig.show()
            fig.savefig(f'{splitPath[0]}/transitionsPerGeno.png', dpi=300)
            fig.savefig(f'{splitPath[0]}/transitionsPerGeno.pdf', dpi=300)
            print('Job done.')
            
            break

    
        if answer == '4':
            #This script computes and plots the statistics for the transitions between exclusive events for two conditions
            conditionList = ['male-female', 'female-female']
            #conditionList = ['15 min', '2 nights']
            gs = gridspec.GridSpec(1, 6)
            fig = plt.figure(figsize=(16, 6))
            
            # Statistical analyses of transitions between exclusive events for each genotype
                        
            # open the json file for first condition
            print('Choose the json file for the first condition.')
            jsonFileName = getJsonFileToProcess()
            #jsonFileName = 'transition_17q21_pairs_0_27000.json'
            with open(jsonFileName) as json_data:
                dataDic1 = json.load(json_data)
            print("json file for first condition re-imported.")
            sexGroup1 = list(dataDic1.keys())[0]
            genoGroupList1 = list(dataDic1[sexGroup1].keys())
            
            # open the json file for second condition
            print('Choose the json file for the second condition.')
            jsonFileName = getJsonFileToProcess()
            #jsonFileName = 'transition_17q21_pairs_2nights.json'
            with open(jsonFileName) as json_data:
                dataDic2 = json.load(json_data)
            print("json file for second condition re-imported.")
            sexGroup2 = list(dataDic2.keys())[0]
            genoGroupList2 = list(dataDic2[sexGroup2].keys())
            
            sexGroupList = [sexGroup1, sexGroup2]
            genoGroupList = [genoGroupList1, genoGroupList2]
            
            titleList = conditionList
            
            n = 0
            k = 0
            for dataDic in [dataDic1, dataDic2]:    
                ax = fig.add_subplot(gs[0, k:k+2])
                #plot the heatmap
                plotHeatmapEffectSizePVal(dataDic=dataDic, ax=ax, n=n, exclusiveEventList=exclusiveEventList, genoGroupList=genoGroupList[n], sexGroup=sexGroupList[n], exclusiveEventListLabels=exclusiveEventListLabels, letterList=letterList, titleList=titleList)
            
                n += 1
                k += 2
            
            
            #add legend
            ax = fig.add_subplot(gs[0, k:k+2])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.set_xlim(0, 2)
            ax.set_ylim(0, 3)
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.tick_params(bottom=False, left=False)
            ax.patch.set_facecolor('white')
            
            radiusScaleLocal = 0.08
            effectSizeAmplitudeLocal = 1.5
            
            y=0
            for v in correspondanceList:
                pValue= v[0]
                circle = plt.Circle( ( 0.1, y ), pValueToCircleSize(pValue) * radiusScaleLocal , color='grey', clip_on=False)
                ax.text(0.3, y, "p <="+str(pValue), fontsize=12, ha="left",va="center")
                ax.add_patch( circle )
                y+=0.2
            
            ax.text(0.05, y+0.04, 'significance', fontsize=14, ha="left",va="center")
            ax.text(1.6, 1.5, 'effect size', fontsize=14, ha="center",va="center", rotation=90)
            ax.text(1.9, 2.2, 'CTRL > MUT', fontsize=14, ha="center",va="center", rotation=90)
            ax.text(1.9, 0.7, 'MUT > CTRL', fontsize=14, ha="center",va="center", rotation=90)
            
            circles = []
            col = PatchCollection(circles, cmap="coolwarm")
            col.set_clim([-effectSizeAmplitudeLocal, effectSizeAmplitudeLocal])
            ax.add_collection(col)
            fig.colorbar(col)
            
            
            fig.tight_layout()
            #plt.show()    
            fig.savefig( "Fig_statistics_between_geno_transitions_two_conditions.pdf" ,dpi=300)
            fig.savefig( "Fig_statistics_between_geno_transitions_two_conditions.png" ,dpi=300)
            
            print('Job done.')
            break
        
        if answer == '5':
            #This script computes and plots the statistics for the transitions between exclusive events for one set of data
            gs = gridspec.GridSpec(1, 6)
            fig = plt.figure(figsize=(16, 6))
            
            # Statistical analyses of transitions between exclusive events for each genotype
                        
            # open the json file for one condition
            print('Choose the json file.')
            jsonFileName = getJsonFileToProcess()
            #jsonFileName = 'transition_17q21_pairs_0_27000.json'
            with open(jsonFileName) as json_data:
                dataDic = json.load(json_data)
            print("json file for first condition re-imported.")
            sexGroup = list(dataDic.keys())[0]
            genoGroupList = list(dataDic[sexGroup].keys())
            
            titleList = [sexGroup]
            
            n = 0
            k = 0
   
            ax = fig.add_subplot(gs[0, k:k+2])
            #plot the heatmap
            plotHeatmapEffectSizePVal(dataDic=dataDic, ax=ax, n=n, exclusiveEventList=exclusiveEventList, genoGroupList=genoGroupList, sexGroup=sexGroup, exclusiveEventListLabels=exclusiveEventListLabels, letterList=letterList, titleList=titleList)
            
            n += 1
            k += 2
            
            
            #add legend
            ax = fig.add_subplot(gs[0, k:k+2])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.set_xlim(0, 2)
            ax.set_ylim(0, 3)
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.tick_params(bottom=False, left=False)
            ax.patch.set_facecolor('white')
            
            radiusScaleLocal = 0.08
            effectSizeAmplitudeLocal = 1.5
            
            y=0
            for v in correspondanceList:
                pValue= v[0]
                circle = plt.Circle( ( 0.1, y ), pValueToCircleSize(pValue) * radiusScaleLocal , color='grey', clip_on=False)
                ax.text(0.3, y, "p <="+str(pValue), fontsize=12, ha="left",va="center")
                ax.add_patch( circle )
                y+=0.2
            
            ax.text(0.05, y+0.04, 'significance', fontsize=14, ha="left",va="center")
            ax.text(1.6, 1.5, 'effect size', fontsize=14, ha="center",va="center", rotation=90)
            ax.text(1.9, 2.2, 'CTRL > MUT', fontsize=14, ha="center",va="center", rotation=90)
            ax.text(1.9, 0.7, 'MUT > CTRL', fontsize=14, ha="center",va="center", rotation=90)
            
            circles = []
            col = PatchCollection(circles, cmap="coolwarm")
            col.set_clim([-effectSizeAmplitudeLocal, effectSizeAmplitudeLocal])
            ax.add_collection(col)
            fig.colorbar(col)
            
            
            fig.tight_layout()
            #plt.show()    
            fig.savefig( "Fig_statistics_between_geno_transitions.pdf" ,dpi=300)
            fig.savefig( "Fig_statistics_between_geno_transitions.png" ,dpi=300)
            
            print('Job done.')
            break
                
