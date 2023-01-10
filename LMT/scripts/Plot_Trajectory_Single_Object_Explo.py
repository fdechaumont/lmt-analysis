'''
Created on 21 nov. 2018

@author: Elodie
'''


import matplotlib.pyplot as plt
import numpy as np;

from lmtanalysis.FileUtil import getFilesToProcess

np.random.seed(0)
import sqlite3
from lmtanalysis.Animal import *
from tkinter.filedialog import askopenfilename
from matplotlib.patches import *
from matplotlib.collections import PatchCollection
from lmtanalysis.Util import *
from lmtanalysis.Measure import *
from matplotlib import patches

def plotNoseTrajectory( ax , animal, title , color = None, colorTitle = 'black' ):
    xList, yList = animal.getNoseTrajectoryData( )

    if ( color == None ):
        color = animal.getColor()
    ax.plot( xList, yList, color=color, linestyle='-', linewidth=0.3, alpha=0.5, label= animal.name )
    ax.set_title( title + " " + animal.RFID, color=colorTitle )
    ax.legend().set_visible(False)
    ax.set_xlim(90, 420)
    ax.set_ylim(-370, -40)
    ax.axis('off')

def plot( ax , animal, title , color = None ):
    xList, yList = animal.getTrajectoryData( )

    if ( color == None ):
        color = animal.getColor()
    ax.plot( xList, yList, color=color, linestyle='-', linewidth=0.5, alpha=0.5, label= animal.name )
    ax.set_title( title + " " + animal.sex[0] + " " + animal.RFID[-4:] + " " + animal.genotype )
    ax.legend().set_visible(False)
    ax.set_xlim(90, 420)
    ax.set_ylim(-370, -40)
    ax.axis('off')
    
def plotZone( ax, colorEdge, colorFill, xa=114, xb=398, ya=-353, yb=-63 ):
    ax.add_artist(patches.Rectangle((xa, ya), xb-xa, yb-ya, edgecolor=colorEdge, fill=True, facecolor=colorFill, alpha=0.2, linewidth=2))
    
    
def plotSap( ax , animal ):

    sapDico = animal.getSapDictionnary()
        
    xList = []
    yList = []
    
    for t in sapDico.keys() :
        detection = animal.detectionDictionary.get( t )
        xList.append( detection.massX )
        yList.append( -detection.massY )    
    color = "red"
    ax.scatter( xList, yList,  color=color, alpha=1, label= "sap", s=10 )


def plotSapNose(ax, animal, color = 'red', xa = 111, xb = 400, ya = 63, yb = 353):
    #plot the position of the nose if the animal is in SAP within the determined zone
    sapDico = animal.getSapDictionnary()

    xList = []
    yList = []

    for t in sapDico.keys():
        detection = animal.detectionDictionary.get(t)
        x = detection.frontX
        y = detection.frontY
        if ( x >= xa ) & (x <= xb ) & ( y >= ya ) & (y <= yb ):
            xList.append(x)
            yList.append(-y)

    ax.scatter(xList, yList, color=color, alpha=0.9, label="sap", s=8)


def plotTrajectoriesInBothPhases(pool, animal, durationPhase1, durationPhase2, axLeft, axRight):
    # draw the trajectory in the first phase, without the object
    pool.loadDetection(start=0, end=durationPhase1)
    pool.filterDetectionByInstantSpeed(0, 70)
    plotZone(axLeft, colorEdge='lightgrey', colorFill='lightgrey')  # whole cage
    plotZone(axLeft, colorEdge='lightgrey', colorFill='grey', xa=168, xb=343, ya=-296,
             yb=-120)  # draw the rectangle for the center zone
    # plotZone(axes[n,0], colorEdge='dimgrey', colorFill='dimgrey', xa=120, xb=250, ya=-210, yb=-340) #object zone
    plot(axLeft, animal, title="First phase", color="black")

    # add the frames where the animal is in SAP
    plotSapNose(axLeft, animal, color='red', xa=111, xb=400, ya=63, yb=353)  # add the frames where the animal is in SAP
    dt1 = animal.getDistance(0, durationPhase1)
    d1 = animal.getDistanceSpecZone(0, durationPhase1, xa=120, xb=250, ya=210, yb=340)
    t1 = animal.getCountFramesSpecZone(0, durationPhase1, xa=120, xb=250, ya=210, yb=340)
    sap1 = len(animal.getSap(tmin=0, tmax=durationPhase1, xa=120, xb=250, ya=210, yb=340))

    # draw the trajectory in the second phase, with the object
    pool.loadDetection(start=getStartTestPhase(pool=pool), end=getStartTestPhase(pool=pool) + durationPhase2)
    pool.filterDetectionByInstantSpeed(0, 70)
    plotZone(axRight, colorEdge='lightgrey', colorFill='lightgrey')  # whole cage
    plotZone(axRight, colorEdge='dimgrey', colorFill='dimgrey', xa=120, xb=250, ya=-210, yb=-340)  # object zone
    plot(axRight, animal, title="Second phase", color="black")
    # add the frames where the animal is in SAP
    plotSapNose(axRight, animal, color='red', xa=111, xb=400, ya=63, yb=353)  # add the frames where the animal is in SAP
    dt2 = animal.getDistance(tmin=getStartTestPhase(pool=pool), tmax=getStartTestPhase(pool=pool) + durationPhase2)
    d2 = animal.getDistanceSpecZone(tmin=getStartTestPhase(pool=pool),
                                    tmax=getStartTestPhase(pool=pool) + durationPhase2, xa=120, xb=250, ya=210, yb=340)
    t2 = animal.getCountFramesSpecZone(tmin=getStartTestPhase(pool=pool),
                                       tmax=getStartTestPhase(pool=pool) + durationPhase2, xa=120, xb=250, ya=210,
                                       yb=340)
    sap2 = len(animal.getSap(tmin=getStartTestPhase(pool=pool), tmax=getStartTestPhase(pool=pool) + durationPhase2, xa=120,
                      xb=250, ya=210, yb=340))


def buildFigTrajectorySingleObjectExploMalesFemales(files, numberMaleFiles, numberFemaleFiles, durationPhase1, durationPhase2, figName):
    if (numberMaleFiles == 0) & (numberFemaleFiles != 0):
        figF, axesF = plt.subplots(nrows=numberFemaleFiles, ncols=2,
                                   figsize=(7, 4 * numberFemaleFiles))  # building the plot for trajectories

    if (numberFemaleFiles == 0) & (numberMaleFiles != 0) :
        figM, axesM = plt.subplots(nrows=numberMaleFiles, ncols=2,
                                   figsize=(7, 4 * numberMaleFiles))  # building the plot for trajectories

    elif (numberFemaleFiles != 0) & (numberMaleFiles != 0) :
        figF, axesF = plt.subplots(nrows=numberFemaleFiles, ncols=2,
                                   figsize=(7, 4 * numberFemaleFiles))  # building the plot for trajectories
        figM, axesM = plt.subplots(nrows=numberMaleFiles, ncols=2,
                                       figsize=(7, 4 * numberMaleFiles))  # building the plot for trajectories

    nRow = {'male': 0, 'female': 0}  # initialisation of the row

    for file in files:
        connection = sqlite3.connect(file)  # connection to the database

        pool = AnimalPool()
        pool.loadAnimals(connection)  # upload all the animals from the database
        animal = pool.animalDictionnary[1]
        strain = animal.strain

        # set the axes. Check the number of file to get the dimension of axes and grab the correct ones. This makes it compatible with 1 or n files.
        axLeft = None
        axRight = None

        if animal.sex == 'male':
            # set the axes. Check the number of file to get the dimension of axes and grab the correct ones.
            if (len(files) == 1):
                axLeft = axesM[0]
                axRight = axesM[1]
            else:
                axLeft = axesM[nRow['male'], 0]  # set the subplot where to draw the plot
                axRight = axesM[nRow['male'], 1]
            plotTrajectoriesInBothPhases(pool, animal, durationPhase1, durationPhase2, axLeft, axRight)
            nRow['male'] += 1
            connection.close()

        if animal.sex == 'female':
            # set the axes. Check the number of file to get the dimension of axes and grab the correct ones.
            if (len(files) == 1):
                axLeft = axesF[0]
                axRight = axesF[1]
            else:
                axLeft = axesF[nRow['female'], 0]  # set the subplot where to draw the plot
                axRight = axesF[nRow['female'], 1]
            plotTrajectoriesInBothPhases(pool, animal, durationPhase1, durationPhase2, axLeft, axRight)
            nRow['female'] += 1

            connection.close()

    if (numberMaleFiles == 0) & (numberFemaleFiles != 0):
        figF.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
        figF.savefig('{}_{}_females.pdf'.format(figName, strain), dpi=100)
        figF.savefig('{}_{}_females.jpg'.format(figName, strain), dpi=100)
    if (numberFemaleFiles == 0) & (numberMaleFiles != 0):
        figM.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
        figM.savefig('{}_{}_males.pdf'.format(figName, strain), dpi=100)
        figM.savefig('{}_{}_males.jpg'.format(figName, strain), dpi=100)
    elif (numberFemaleFiles != 0) & (numberMaleFiles != 0):
        figM.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
        figM.savefig('{}_{}_males.pdf'.format(figName, strain), dpi=100)
        figM.savefig('{}_{}_males.jpg'.format(figName, strain), dpi=100)
        figF.tight_layout(pad=2, h_pad=4, w_pad=0)  # reduce the margins to the minimum
        figF.savefig('{}_{}_females.pdf'.format(figName, strain), dpi=100)
        figF.savefig('{}_{}_females.jpg'.format(figName, strain), dpi=100)

if __name__ == '__main__':
    
    print("Code launched.")
    
    '''
    This script draws the trajectory of the mouse in the two phases of the single object exploration test. The positions at which
    the animal is in SAP is marked in red. The object zone is drawn in light grey. This script should be run per strain.
    '''
    files = getFilesToProcess()
    numberMaleFiles = 0
    numberFemaleFiles = 0
    for file in files:
        connection = sqlite3.connect(file)  # connection to the database
        pool = AnimalPool()
        pool.loadAnimals(connection)  # upload all the animals from the database
        animal = pool.animalDictionnary[1]
        sex = animal.sex
        if sex == 'male':
            numberMaleFiles += 1
        elif sex == 'female':
            numberFemaleFiles += 1
        elif sex == None:
            print('Warning no sex!')
            quit()

    nbFiles = len(files)
    durationPhase1 = 20*oneMinute
    durationPhase2 = 20*oneMinute

    figName = 'single_object_explo_trajectory'

    buildFigTrajectorySingleObjectExploMalesFemales(files, numberMaleFiles, numberFemaleFiles, durationPhase1, durationPhase2, figName)
    
    print("All jobs done")
   
       