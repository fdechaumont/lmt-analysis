'''
Created on 2 dec. 2019

@author: Elodie
'''

from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.Animal import *
import numpy as np; np.random.seed(0)
from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import getMinTMaxTAndFileNameInput
import sqlite3
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
import pandas as pd
import seaborn as sns


if __name__ == '__main__':
    '''
    This codes compute the successive visits to the water point, based on the water stop events. 
    '''
    print("Code launched.")
    
    files = getFilesToProcess()
    tmin, tmax, text_file = getMinTMaxTAndFileNameInput()
    
    for file in files:
        print(file)
        connection = sqlite3.connect( file )
        expName = file[-22:-7]
        print( expName )
        
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        
        #Load the timeline of the water stop event over all individuals
        waterStopTimeLine = {}
        for animal in pool.animalDictionnary.keys():
            print ( pool.animalDictionnary[animal].RFID )
            waterStopTimeLine[animal] = EventTimeLine( connection, "Water Stop", idA=animal, minFrame=tmin, maxFrame=tmax )
            waterStopTimeLine[animal].removeEventsBelowLength( maxLen = MIN_WATER_STOP_DURATION )
            
        #Check if one t within the time window of interest belongs to an event of the AnimalB timeline:
        eventWaterStop = {}
        for animalA in pool.animalDictionnary.keys():
            for animalB in pool.animalDictionnary.keys():
                eventWaterStop[(animalA,animalB)] = 0
                
                for event in waterStopTimeLine[animalA].getEventList():
                    #determines the time window of interest:
                    windowStart = event.endFrame+1
                    windowEnd = event.endFrame+2*oneSecond
                    
                    #if any frame of the window of interest is included in a water stop event of the animalB, the water stop event of
                    #animalA is counted as a water stop follow by a water stop from animalB and we check the next water stop event from animalA
                    for t in range(windowStart, windowEnd):
                        if waterStopTimeLine[animalB].hasEvent(t) == True:
                            eventWaterStop[(animalA,animalB)]+=1
                            break
        
        #compute the number of unfollowed water stops for each individual        
        print("results: ")
        followedWaterStop = {}
        unfollowedWaterStop = {}
        for animalA in pool.animalDictionnary.keys():
            followedWaterStop[animalA] = []
            for animalB in pool.animalDictionnary.keys():
                followedWaterStop[animalA].append(eventWaterStop[(animalA,animalB)])
                
            unfollowedWaterStop[animalA] = waterStopTimeLine[animalA].getNumberOfEvent(minFrame=tmin, maxFrame=tmax) - np.sum(followedWaterStop[animalA])
        
        #print the header of the text file
        header = ["file","tmin","tmax","animalA","genoA","animalB","genoB","nbWaterStop", "nbTotalWaterStop", "nbUnfollowedWaterStop"]
        for name in header:
            text_file.write( "{}\t".format ( name ) )
        
        text_file.write("\n")
        
        #print the results and store them in a text file        
        print("results: ")
        for animalA in pool.animalDictionnary.keys():
            for animalB in pool.animalDictionnary.keys():
                print("animal {} followed by animal {}: {}".format( animalA, animalB, eventWaterStop[(animalA,animalB)]) )
                
                text_file.write( "{}\t".format( file ) )
                text_file.write( "{}\t".format( tmin ) )
                text_file.write( "{}\t".format( tmax ) )
                text_file.write( "{}\t".format( pool.animalDictionnary[animalA].RFID ) )
                text_file.write( "{}\t".format( pool.animalDictionnary[animalA].genotype ) )
                text_file.write( "{}\t".format( pool.animalDictionnary[animalB].RFID ) )
                text_file.write( "{}\t".format( pool.animalDictionnary[animalB].genotype ) )
                text_file.write( "{}\t".format( eventWaterStop[(animalA,animalB)] ) )
                text_file.write( "{}\t".format( unfollowedWaterStop[animalA] ) )
                text_file.write( "{}\n".format( waterStopTimeLine[animalA].getNumberOfEvent(minFrame=tmin, maxFrame=tmax) ) )
        
        text_file.write( "\n")
        
        #print the results and store them in a dataframe        
        print("dataframe: ")
        df = pd.DataFrame(columns=['file', 'tmin', 'tmax', 'idA', 'genoA', 'idB', 'genoB', 'waterStop', 'unfollowedWaterStop', 'totalWaterStop'])
        n=0
        for animalA in pool.animalDictionnary.keys():
            for animalB in pool.animalDictionnary.keys():
                df.loc['{}'.format(n)] = [ file, tmin, tmax, pool.animalDictionnary[animalA].RFID, pool.animalDictionnary[animalA].genotype, pool.animalDictionnary[animalB].RFID, pool.animalDictionnary[animalB].genotype, eventWaterStop[(animalA,animalB)], unfollowedWaterStop[animalA], waterStopTimeLine[animalA].getNumberOfEvent(minFrame=tmin, maxFrame=tmax) ]
                n+=1
        df['waterStop'] = df.waterStop.convert_objects(convert_numeric=True)        
        df.info()
        
        df_wide=df.pivot_table( index='idA', columns='idB', values='waterStop' )
    
        '''Generate the heatmap'''
        fig, ax = plt.subplots(1,1)
        
        plt.figure(figsize=(5,5))
        #plt.tight_layout()
        p2=sns.heatmap( df_wide, cmap="Blues", annot=True, fmt='d' ) 
                
        plt.savefig('heatmap_waterStop_{}.pdf'.format( expName ), dpi=100)   
        plt.close()      
        
            
        #Compute results in a matrix for each experiment (raw numbers):    
        text_file.write("results as a matrix: \n")
        text_file.write( "\n" )

        text_file.write( "{}\n".format( file ) )
        for animalA in pool.animalDictionnary.keys():
            text_file.write( "{}\t".format( pool.animalDictionnary[animalA].genotype ) )
        text_file.write( "\n" )
        for animalA in pool.animalDictionnary.keys():
            for animalB in pool.animalDictionnary.keys():        
                text_file.write( "{}\t".format( eventWaterStop[(animalA,animalB)] ) )
                
            text_file.write( "{}\n".format( unfollowedWaterStop[animalA] ) )
        text_file.write( "\n" )
        
        
        #Compute results in a matrix for each experiment (proportions):       
        text_file.write("results as proportions of the total nb of water stops in a matrix: \n")
        text_file.write( "\n" )

        text_file.write( "{}\n".format( file ) )
        for animalA in pool.animalDictionnary.keys():
            text_file.write( "{}\t".format( pool.animalDictionnary[animalA].genotype ) )
        text_file.write( "\n" )
        for animalA in pool.animalDictionnary.keys():
            for animalB in pool.animalDictionnary.keys():        
                text_file.write( "{}\t".format( eventWaterStop[(animalA,animalB)] / waterStopTimeLine[animalA].getNumberOfEvent(minFrame=tmin, maxFrame=tmax) ) )
                
            text_file.write( "{}\n".format( unfollowedWaterStop[animalA] / waterStopTimeLine[animalA].getNumberOfEvent(minFrame=tmin, maxFrame=tmax) ) )
        text_file.write( "\n")
        
    text_file.close()            
    print("Job done.")      