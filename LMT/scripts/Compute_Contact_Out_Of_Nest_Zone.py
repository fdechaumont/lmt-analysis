'''
Created on 19 juin 2019

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

def fuseTimeLine( timeLineDico, animalA ):
    '''
    Fuse the timeline with key animalA, animalB.
    Fuse all possible animal B
    '''
    print( "Start timeLineFusion for animalA: " , animalA )
    fusedTimeLine = EventTimeLine( None, "Fusion" , animalA, loadEvent=False )
    fusedTimeLineDico = {}
    keys = timeLineDico.keys();
    for k in keys:
        print( k )
        if k[0] == animalA:
            print( "ok: ", k )
            for t in timeLineDico[ k ].getDictionnary():
                fusedTimeLineDico[ t ] = True
    
    fusedTimeLine.reBuildWithDictionnary( fusedTimeLineDico )
    return fusedTimeLine

def inZone( detection ):
    return detection.isInZone( xa=114, ya=353, xb=256, yb=208 ) #Danger: the y-axis is reversed! classic nest zone:  xa=114, ya=353, xb=256, yb=208 

       
if __name__ == '__main__':
    
    '''
    This script computes the time spent in contact out of the nest zone (the coordinates of the nest zone can be adapted) during each night.
    '''
    
    files = getFilesToProcess()
    tmin, tmax, text_file = getMinTMaxTAndFileNameInput()
    
    for file in files:
        
        print(file)
        connection = sqlite3.connect( file )
        
        nightTimeLine = {}
        nightTimeLine = EventTimeLine( connection, "night", minFrame = tmin, maxFrame = tmax )
        
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        
        nightIndex=1
        
        # create a new timeline to store the events "Contact out of the nest zone" and "Contact in the nest zone":
        ContactOutOfNestZoneTimeLine = {}
        ContactInNestZoneTimeLine = {}
            
        for animalA in pool.animalDictionnary.keys():
                for animalB in pool.animalDictionnary.keys():
                    if (animalA == animalB):
                        continue
                    ContactOutOfNestZoneTimeLine[animalA, animalB] = EventTimeLine( None, "Contact out of nest zone" , animalA, animalB, loadEvent=False )
                    ContactInNestZoneTimeLine[animalA, animalB] = EventTimeLine( None, "Contact in nest zone" , animalA, animalB, loadEvent=False )
        
        # process for each night
        
        for night in nightTimeLine.getEventList():
            print( "night ", nightIndex )
            
            pool.loadDetection( start=night.startFrame, end=night.endFrame, lightLoad = True )
            
            # load the timeline of contacts during this night
            contactTimeLine = {}
            
            resultInZone = {}
            resultOutZone = {}

            for animalA in pool.animalDictionnary.keys():
                for animalB in pool.animalDictionnary.keys():
                    if (animalA == animalB):
                        continue
                    
                    print("Load contact timeline for animal {} and animal {}".format(animalA, animalB))                
                    contactTimeLine[animalA, animalB] = EventTimeLine( connection, "Approach contact" , animalA, animalB, minFrame=night.startFrame, maxFrame=night.endFrame )
                    resultInZone[animalA, animalB] = {}
                    resultOutZone[animalA, animalB] = {}

            
            for animalA in pool.animalDictionnary.keys():
                
                detectionDicoAnimalA = pool.getAnimalWithId( animalA ).detectionDictionnary 
                for animalB in pool.animalDictionnary.keys():
                    if (animalA == animalB):
                        continue
                    
                    detectionDicoAnimalB = pool.getAnimalWithId( animalB ).detectionDictionnary
                    
                    
                    # load all frames in which animalA and animalB are in contact
                    dicAB = contactTimeLine[ animalA , animalB ].getDictionnary()
                    
                    
                    # Test if the detection at the given frame is in or out the nest zone (nest zone = lower left quarter)
                    for t in dicAB:
                        
                        # test if both animal are in zone.
                        
                        # check if we have detection at those time point
                        if t in detectionDicoAnimalA and t in detectionDicoAnimalB:
                            
                            # check detection A and B are both in Zone
                            if ( inZone( detectionDicoAnimalA[t] ) and inZone( detectionDicoAnimalB[t] ) ):
                                resultInZone[ animalA , animalB ][t] = True

                            # check detection A and B are both NOT in Zone
                            if ( (not inZone(detectionDicoAnimalA[t])) and (not inZone(detectionDicoAnimalB[t]) )):
                                resultOutZone[ animalA , animalB ][t] = True
                    
            
            for animalA in pool.animalDictionnary.keys():
                for animalB in pool.animalDictionnary.keys():
                    if (animalA == animalB):
                        continue

                    # Build the timelines
                    ContactInNestZoneTimeLine[ animalA , animalB ].reBuildWithDictionnary( resultInZone[ animalA , animalB ] )    
                    ContactOutOfNestZoneTimeLine[ animalA , animalB ].reBuildWithDictionnary( resultOutZone[ animalA , animalB ] )
                    
                    # Record events in the database
                    ContactInNestZoneTimeLine[ animalA , animalB ].endRebuildEventTimeLine( connection , deleteExistingEvent = True )
                    ContactOutOfNestZoneTimeLine[ animalA , animalB ].endRebuildEventTimeLine( connection , deleteExistingEvent = True )

            
            text_file.write("{}\t{}\t{}\t{}\t{}\t{}\n".format( "file", "rfid", "genotype", "night", "timeOutOfNestZone", "contactOutOfNestDuration" ) )
            
            #Compute the time spent out of the nest        
            for animalA in pool.animalDictionnary.keys():
                #upper half
                print( "night duration: ",night.startFrame , night.endFrame)
                timeZone1 = pool.animalDictionnary[animalA].getCountFramesSpecZone( tmin=night.startFrame, tmax=night.endFrame, xb=114, yb=208, xa=398, ya=63 )
                #lower right quarter
                timeZone2 = pool.animalDictionnary[animalA].getCountFramesSpecZone( tmin=night.startFrame, tmax=night.endFrame, xb=256, yb=353, xa=398, ya=208 )       
                #total number of frames spent out of the nest zone during the night
                timeOutOfNestZone = timeZone1 + timeZone2
                print( timeZone1 , timeZone2 )
                
                #Compute the time spent in contact out of the nest zone:
                contactOutOfNestDuration = fuseTimeLine(ContactOutOfNestZoneTimeLine, animalA ).getTotalDurationEvent(tmin=night.startFrame, tmax=night.endFrame)
                
                text_file.write("{}\t{}\t{}\t{}\t{}\t{}\n".format( file, pool.animalDictionnary[animalA].RFID, pool.animalDictionnary[animalA].genotype, nightIndex, timeOutOfNestZone, contactOutOfNestDuration ) )
            
            text_file.write( "\n" )
            
            text_file.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( "file", "rfidA", "genoA", "rfidB", "genoB", "night", "contactOutOfNestDuration" ) )
            
            for animalA in pool.animalDictionnary.keys():
                
                for animalB in pool.animalDictionnary.keys():
                    if (animalA == animalB):
                        continue
                    
                    contactOutOfNestDuration = ContactOutOfNestZoneTimeLine[animalA, animalB].getTotalDurationEvent(tmin=night.startFrame, tmax=night.endFrame)
                    text_file.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( file, pool.animalDictionnary[animalA].RFID, pool.animalDictionnary[animalA].genotype, pool.animalDictionnary[animalB].RFID, pool.animalDictionnary[animalB].genotype, nightIndex, contactOutOfNestDuration ) )
            

            nightIndex+=1

                     
    text_file.write( "\n" )
    
    text_file.close()
    print("calculation done")
    
