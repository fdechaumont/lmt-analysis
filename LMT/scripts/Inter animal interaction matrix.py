'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.Util import getAllEvents
from lmtanalysis import BuildEventTrain3, BuildEventTrain4, BuildEventTrain2, BuildEventFollowZone, BuildEventRear5, BuildEventFloorSniffing,\
    BuildEventSocialApproach, BuildEventSocialEscape, BuildEventApproachContact,BuildEventOralOralContact,\
    BuildEventApproachRear, BuildEventGroup2, BuildEventGroup3, BuildEventGroup4, BuildEventOralGenitalContact, \
    BuildEventStop, BuildEventWaterPoint, \
    BuildEventMove, BuildEventGroup3MakeBreak, BuildEventGroup4MakeBreak,\
    BuildEventSideBySide, BuildEventSideBySideOpposite, BuildEventDetection,\
    BuildDataBaseIndex, BuildEventWallJump, BuildEventSAP,\
    BuildEventOralSideSequence

import lmtanalysis, sys
from tkinter.filedialog import askopenfilename


def process( files, eventName ):

    for file in files:

        print(file)
        connection = sqlite3.connect( file )

        pool = AnimalPool( )
        pool.loadAnimals( connection )

        event= {}

        for idAnimalA in pool.animalDictionnary.keys():

            for idAnimalB in pool.animalDictionnary.keys():

                event[idAnimalA, idAnimalB] = EventTimeLine( connection, eventName, idAnimalA, idAnimalB )



        for idAnimalA in pool.animalDictionnary.keys():

            txt = str(idAnimalA) + ":" + str( pool.animalDictionnary[idAnimalA]) + "\t"

            for idAnimalB in pool.animalDictionnary.keys():

                txt += str( len( event[idAnimalA, idAnimalB].getEventList() ) ) + "\t"

            print( txt )


    print( "*** DONE ***")


if __name__ == '__main__':

    print("Code launched.")


    files = askopenfilename( title="Choose a set of file to process", multiple=1 )

    eventList = getAllEvents(file=files[0] )

    for i in range( 0 , len( eventList) ):
        print( "[" + str( i ) + "] :" + eventList[i] )

    while( True ):

        userInput = input ("Event to read (full name or number ) (enter to quit): ")

        if userInput=="":
            print("Exit :)")
            quit()

        if ( userInput.isdigit() ):
            eventName = eventList[ int( userInput )]
        else:
            eventName = userInput

        process( files, eventName )


