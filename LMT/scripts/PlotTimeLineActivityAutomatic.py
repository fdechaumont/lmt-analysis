'''
Created on 12 sept. 2018

@author: Fab
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

def process( ):

    print("Code launched.")
    saveFile = "figTimeLineActivity"
    #Choose the files to process
    files = getFilesToProcess()
    tmin, tmax, text_file = getMinTMaxTAndFileNameInput()
    
    for file in files:
        print(file)
        expName = file[-22:-7]
        print( expName )
        
        connection = sqlite3.connect( file )
    
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        
        pool.loadDetection( start = tmin, end = tmax, lightLoad=True)
        
        #Load the timeline of the nest4 event over all individuals
        print( "Loading all nest4 for file " + file )
        nest4TimeLine = {}
        nest4TimeLine["all"] = EventTimeLine( connection, "Nest4", minFrame=tmin, maxFrame=tmax )
        
        #Load the timeline of the nest3 event over all individuals
        print( "Loading all nest3 for file " + file )
        nest3TimeLine = {}
        nest3TimeLine["all"] = EventTimeLine( connection, "Nest3", minFrame=tmin, maxFrame=tmax )
        
        print("loading night events for file " + file)
        nightTimeLine = EventTimeLine( connection, "night" , minFrame=tmin, maxFrame=tmax )
        
        ''' build the plot '''
        ymax=200
        ymin=-30
        fig, ax = plt.subplots( 1,1 , figsize=(8, 2 ) )
        ax = plt.gca() # get current axis
        ax.set_xlabel("time")
        ax.set_xlim([0, tmax])
        ax.set_ylim([ymin, ymax])
        
        #set x axis
        formatter = matplotlib.ticker.FuncFormatter( frameToTimeTicker )
        ax.xaxis.set_major_formatter(formatter)
        ax.tick_params(labelsize=6 )
        ax.xaxis.set_major_locator(ticker.MultipleLocator( 30 * 60 * 60 * 12 ))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator( 30 * 60 * 60 ))
        
        
        #draw the rectangles for the nights
        for nightEvent in nightTimeLine.getEventList():
            ax.axvspan( nightEvent.startFrame, nightEvent.endFrame, alpha=0.1, color='black')
            ax.text( nightEvent.startFrame+(nightEvent.endFrame-nightEvent.startFrame)/2 , 0.90*ymax , "dark phase" ,fontsize=6, ha='center')
        
        #plot the distance traveled per timeBin min time bin
        timeBin = 10
        dt = {}
        totalDistance = {}

        for animal in pool.animalDictionnary.keys():
            print ( pool.animalDictionnary[animal].RFID )
            dt[animal] = [x/100 for x in pool.animalDictionnary[animal].getDistancePerBin(binFrameSize = timeBin*oneMinute, maxFrame = tmax )]
            totalDistance[animal] = pool.animalDictionnary[animal].getDistance(tmin=tmin, tmax=tmax)
            
        
        nTimeBins = len(dt[1])
        print(nTimeBins)
        
        abs = [10*oneMinute]
        for t in range(1, nTimeBins):
            x = abs[t-1] + timeBin*oneMinute
            abs.append(x)
        
        #print(abs)
        print(len(abs))
        
        text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( "file", "rfid", "genotype", "user1", "tmin", "tmax", "totalDistance" ) )
        
        for animal in pool.animalDictionnary.keys():
            #print(dt[animal])
            ax.plot( abs, dt[animal], color = getAnimalColor(animal), linewidth=0.6 )
            
            #prepare data to be written in a txt file, with tab separating columns
            line =""
            line+= str ( file )+ "\t"
            line+= str ( pool.animalDictionnary[animal].RFID )+ "\t"
            line+= str ( pool.animalDictionnary[animal].genotype )+ "\t"
            line+= str ( pool.animalDictionnary[animal].user1 )+ "\t"
            line+= str ( tmin )+ "\t"
            line+= str ( tmax )+ "\t"
            line+= str ( totalDistance[animal]/100 )+ "\t"
            
            for val in dt[animal]:
                line+= str( val )+ "\t"
                
            text_file.write( line )
            text_file.write( "\n" ) 
        
        
        #Print the name and genotype of the animals on the graph, with the corresponding colors and the total distance traveled over the experiment
        legendHeight = 0.6*ymax
        for animal in pool.animalDictionnary.keys():
            print ( pool.animalDictionnary[animal].RFID )
            ax.text(30*60*60, legendHeight, "{} {} ({} m)".format(pool.animalDictionnary[animal].RFID[5:], pool.animalDictionnary[animal].genotype, round(totalDistance[animal]/100)), color=getAnimalColor(animal), fontsize=5 )
            legendHeight += 12 
        
        
        yLabels=[]
        line = -20
        yTickList = []
        addThickness=0
        
        fig.suptitle("Activity time line {}".format( expName ))
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        
        #draw the nest4 time line
        yLabels.append("nest4")
        lineData = []
            
        for eventList in nest4TimeLine["all"].eventList:                                
            lineData.append( ( eventList.startFrame-addThickness , eventList.duration()+addThickness ))    
            
        ax.broken_barh( lineData , ( line-4, 4 ), facecolors = "black" )    
        yTickList.append(line)
        
        line+=10
        
        #draw the nest3 time line
        yLabels.append("nest3")
        addThickness=0
        lineData = []
            
        for eventList in nest3TimeLine["all"].eventList:                                
            lineData.append( ( eventList.startFrame-addThickness , eventList.duration()+addThickness ))    
            
        ax.broken_barh( lineData , ( line-4, 4 ), facecolors = "black" )    
        yTickList.append(line)
        
        line+=10
 
        #draw the y axis  
        yLab=[0, 40, 80, 120, 160, 200]
        for i in yLab:
            yTickList.append(i)    
            yLabels.append(i)
        
        ax.set_yticks( yTickList )
        ax.set_yticklabels( yLabels )
        
        plt.tight_layout()
        print ("Saving figure...")
        fig.savefig( "FigActivityTimeLine_{}.pdf".format( expName ) ,dpi=100)
        plt.close( fig )
        text_file.close()    
    
if __name__ == '__main__':
    
    process()
