'''
Created on 29 Aug. 2019

@author: Elodie
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *

import lmtanalysis
from tkinter.filedialog import askopenfilename
from tabulate import tabulate
from collections import Counter
import collections
import xlsxwriter
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import os
from lmtanalysis.FileUtil import getFilesToProcess

from lmtanalysis.Util import convert_to_d_h_m_s, getMinTMaxTAndFileNameInput



def frameToTimeTicker(x, pos):
   
    vals= convert_to_d_h_m_s( x )
    return "D{0} - {1:02d}:{2:02d}".format( int(vals[0])+1, int(vals[1]), int(vals[2]) )


def plotNightTimeLine ( file ):
    
    print(file)
    connection = sqlite3.connect( file )
    
    nightTimeLineList = []
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    #print( "Event: " + event)
    print( "Loading event for file " + file )
    
    nightTimeLine = EventTimeLine( connection, "night" )
   
    nightTimeLineList.append( nightTimeLine )
    
    for nightEvent in nightTimeLine.getEventList():
        ax.axvspan( nightEvent.startFrame, nightEvent.endFrame, alpha=0.1, color='black')

        ax.text( nightEvent.startFrame+(nightEvent.endFrame-nightEvent.startFrame)/2 , 100 , "dark phase" ,fontsize=8,ha='center')

    
    
if __name__ == '__main__':
    '''
    This script allows to plot the activity of individual mice within a group containing two different genotypes. The output is a pdf file.
    Genotypes should be entered without typos.
    It also computes the total distance traveled and stores the value in a text file.
    '''
    
    print("Code launched.")
    saveFile = "figTimeLineActivity"
    files = getFilesToProcess()
    print("Enter the first genotype: ")
    geno1 = input()
    print("Enter the second genotype: ")
    geno2 = input()
    tmin, tmax, text_file = getMinTMaxTAndFileNameInput()
    
    for file in files:
        print(file)

        expName = file[-40:-23]

        print( expName )
        
        connection = sqlite3.connect( file )
    
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        
        pool.loadDetection( start = tmin, end = tmax, lightLoad=True)

        print("loading night events for file " + file)
        nightTimeLine = EventTimeLine( connection, "night" , minFrame=tmin, maxFrame=tmax )
        
        ''' build the plot '''
        fig, ax = plt.subplots( 1,1 , figsize=(8, 2 ) )
        ax = plt.gca() # get current axis
        ax.set_xlabel("time")
        ax.set_xlim([0, 7776000])

        ax.set_ylim([0, 250])

        
        ''' set x axis '''
        formatter = matplotlib.ticker.FuncFormatter( frameToTimeTicker )
        ax.xaxis.set_major_formatter(formatter)
        ax.tick_params(labelsize=6 )
        ax.xaxis.set_major_locator(ticker.MultipleLocator( 30 * 60 * 60 * 12 ))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator( 30 * 60 * 60 ))
        
        ''' draw the rectangles for the nights '''
        for nightEvent in nightTimeLine.getEventList():
            ax.axvspan( nightEvent.startFrame, nightEvent.endFrame, alpha=0.1, color='black')

            ax.text( nightEvent.startFrame+(nightEvent.endFrame-nightEvent.startFrame)/2 , 240 , "dark phase" ,fontsize=6,ha='center')

        
        ''' plot the distance traveled per timeBin and compute the total distance traveled and store it in a file '''
        timeBin = 20   
        
        dt = {}
        totalDistance = {}
        
        text_file.write("{}\t{}\t{}\t{}\t{}\t{}\n".format("file", "group", "rfid", "genotype", "tmin", "tmax", "totalDistance") )
        
        for animal in pool.animalDictionnary.keys():
            print ( pool.animalDictionnary[animal].RFID )
            dt[animal] = [x/100 for x in pool.animalDictionnary[animal].getDistancePerBin(binFrameSize = timeBin*oneMinute, minFrame=tmin, maxFrame = tmax )]
            totalDistance[animal]=pool.animalDictionnary[animal].getDistance( tmin=tmin, tmax=tmax )
            text_file.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(file, expName, pool.animalDictionnary[animal].RFID, pool.animalDictionnary[animal].genotype, tmin, tmax, totalDistance[animal]) )
        
        nTimeBins = len(dt[1])
        print(nTimeBins)
        
        
        
        abs = [10*oneMinute]
        for t in range(1, nTimeBins):
            x = abs[t-1] + timeBin*oneMinute
            abs.append(x)
        
        #print(abs)
        print(len(abs))
        
        colorGeno1=["steelblue", "dodgerblue"]
        colorGeno2=["orangered", "darkorange"]
        
        j=0
        n=0
        for animal in pool.animalDictionnary.keys():
            
            if pool.animalDictionnary[animal].genotype == geno1:
                ax.plot( abs, dt[animal], color = colorGeno1[j], linewidth=0.6, label="{} {}".format(geno1, pool.animalDictionnary[animal].RFID[8:12] ) )
                j+=1

            if pool.animalDictionnary[animal].genotype == geno2:
                ax.plot( abs, dt[animal], color = colorGeno2[n], linewidth=0.6, label="{} {}".format(geno2, pool.animalDictionnary[animal].RFID[8:12] ) )
                n+=1
        
        ax.legend(loc='best', prop={'size':5})
        
        fig.suptitle("Activity Time line {}".format( expName ))
        line = -10
        
        #line = -20
        yLabels = [" "]
        yTickList = [line]
        
       
    
           

        yLab=[0, 50, 100, 150, 200, 250]

        for i in yLab:
            yTickList.append(i)    
            yLabels.append(i)
        
        ax.set_yticks( yTickList )
        ax.set_yticklabels( yLabels )
        
        plt.tight_layout()
        print ("Saving figure..." )
        fig.savefig( "FigActivityTimeLine_{}.pdf".format( expName ) ,dpi=100)
        plt.close( fig )
        #print( "Showing figure...")
        #plt.show()
        connection.close()
        
    text_file.close()