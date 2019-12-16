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
    This script computes the time spent in contact out of the nest zone during each night.
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
        
        #pool.loadDetection( lightLoad = True )
        
        nightIndex=1
        
        # process for each night
        
        for night in nightTimeLine.getEventList():
            print( "night ", nightIndex )
            
            pool.loadDetection( start=night.startFrame, end=night.endFrame, lightLoad = True )
            
            # load the timeline of contacts during this night
            contactTimeLine = {}
            
            for animalA in pool.animalDictionnary.keys():
                for animalB in pool.animalDictionnary.keys():
                    if (animalA == animalB):
                        continue
                    
                    print("Load contact timeline for animal {} and animal {}".format(animalA, animalB))                



                    contactTimeLine[animalA, animalB] = EventTimeLine( connection, "Contact" , animalA, animalB, minFrame=night.startFrame, maxFrame=night.endFrame )
           
           
            # create a new timeline to store the events "Contact out of the nest zone" and "Contact in the nest zone":
            ContactOutOfNestZoneTimeLine = {}
            inNestZoneTimeLine = {}

            
            for animalA in pool.animalDictionnary.keys():
                
                detectionDicoAnimalA = pool.getAnimalWithId( animalA ).detectionDictionnary 
                for animalB in pool.animalDictionnary.keys():
                    if (animalA == animalB):
                        continue
                    
                    detectionDicoAnimalB = pool.getAnimalWithId( animalB ).detectionDictionnary
                    
                    resultInZone = {}
                    resultOutZone = {}
                    
                    # load all frames in which animalA and animalB are in contact
                    dicAB = contactTimeLine[ animalA , animalB ].getDictionnary()
                    
                    ContactOutOfNestZoneTimeLine[animalA, animalB] = EventTimeLine( None, "Contact out of nest zone" , animalA, animalB, loadEvent=False )
                    inNestZoneTimeLine[animalA, animalB] = EventTimeLine( None, "Contact in nest zone" , animalA, animalB, loadEvent=False )
                    
                    # Test if the detection at the given frame is in or out the nest zone (nest zone = lower left quarter)
                    for t in dicAB:
                        
                        # test if both animal are in zone.
                        
                        # check if we have detection at those time point
                        if t in detectionDicoAnimalA and t in detectionDicoAnimalB:
                            
                            # check detection A and B are both in Zone
                            if ( detectionDicoAnimalA[t].isInZone( xa=114, ya=63, xb=256, yb=208 ) and detectionDicoAnimalB[t].isInZone( xa=114, ya=63, xb=256, yb=208 ) ):
                                resultInZone[t] = True

                            # check detection A and B are both NOT in Zone
                            if ( (not detectionDicoAnimalA[t].isInZone( xa=114, ya=63, xb=256, yb=208 )) and (not detectionDicoAnimalB[t].isInZone( xa=114, ya=63, xb=256, yb=208 ) )):
                                resultOutZone[t] = True
                                                        
                        #
                        #if ( dicAB[t].isInZone( xa=114, ya=63, xb=256, yb=208 ) == True):
                        #    resultInZone[t] = True
                        #else:
                        #    resultOutZone[t] = True
                        
                        #if (dicAB[t].isInZone( xa=114, ya=63, xb=256, yb=208 ) == False):
                        #    resultOutZone[t] = True
                    
                    # Build the timelines
                    inNestZoneTimeLine[ animalA , animalB ].reBuildWithDictionnary( resultInZone )    
                    ContactOutOfNestZoneTimeLine[ animalA , animalB ].reBuildWithDictionnary( resultOutZone )
                    
                    # Record events in the database
                    inNestZoneTimeLine[ animalA , animalB ].endRebuildEventTimeLine( connection )
                    ContactOutOfNestZoneTimeLine[ animalA , animalB ].endRebuildEventTimeLine( connection )
            
            text_file.write("{}\t{}\t{}\t{}\t{}\t{}\n".format( "file", "rfid", "genotype", "night", "timeOutOfNestZone", "contactOutOfNestDuration" ) )
            
            #Compute the time spent out of the nest        
            for animalA in pool.animalDictionnary.keys():
                #upper half
                timeZone1 = pool.animalDictionnary[animalA].getCountFramesSpecZone( tmin=night.startFrame, tmax=night.endFrame, xa=114, ya=208, xb=398, yb=353 )
                #lower right quarter
                timeZone2 = pool.animalDictionnary[animalA].getCountFramesSpecZone( tmin=night.startFrame, tmax=night.endFrame, xa=256, ya=63, xb=398, yb=208 )       
                #total number of frames spent out of the nest zone during the night
                timeOutOfNestZone = timeZone1 + timeZone2
                
                # ********* can't work:
                # contactOutOfNestDuration = ContactOutOfNestZoneTimeLine[animalA].getTotalDurationEvent(tmin=night.startFrame, tmax=night.endFrame)
                
                # code proposal:
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
            
                     
    text_file.write( "\n" )
    
    text_file.close()
    print("calculation done")
    
