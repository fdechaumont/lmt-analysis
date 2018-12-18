'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis import BuildEventTrain3, BuildEventTrain4, BuildEventTrain2, BuildEventFollowZone, BuildEventRear5, BuildEventFloorSniffing,\
    BuildEventSocialApproach, BuildEventSocialEscape, BuildEventApproachContact,BuildEventOralOralContact,\
    BuildEventApproachRear, BuildEventGroup2, BuildEventGroup3, BuildEventGroup4, BuildEventOralGenitalContact, \
    BuildEventStop, BuildEventWaterPoint,  \
    BuildEventMove, BuildEventGroup3MakeBreak, BuildEventGroup4MakeBreak
    
import matplotlib.gridspec as gridspec
from tkinter.filedialog import askopenfilename


'''
setName = "night 1"
minDur = 0*oneDay
maxDur = minDur+ 23*oneHour
'''

'''
setName = "night 2"
minDur = 1*oneDay
maxDur = minDur+ 23*oneHour
'''


setName = "night 1"
minDur = 0*oneDay
maxDur = minDur+ 23*oneHour

def getValue( connection, animal, animalListWT, eventName , type="duration" ):
    
    timeLineWT1 = EventTimeLine( connection, eventName, animalListWT[0].baseId, minFrame=minDur, maxFrame=maxDur )
    timeLineWT2 = EventTimeLine( connection, eventName, animalListWT[1].baseId, minFrame=minDur, maxFrame=maxDur )
    timeLineKO = EventTimeLine( connection, eventName, animal.baseId, minFrame=minDur, maxFrame=maxDur )

    scoreWT1 = 0
    scoreWT2 = 0
    scoreKO = 0 
    
    if ( type == "duration" ):
         
        scoreWT1 = timeLineWT1.getTotalLength()
        scoreWT2 = timeLineWT2.getTotalLength()
        scoreKO = timeLineKO.getTotalLength() 
    
    if ( type == "number" ):
        
        scoreWT1 = len( timeLineWT1.eventList )
        scoreWT2 = len( timeLineWT2.eventList )
        scoreKO = len ( timeLineKO.eventList ) 
     
    meanScoreWT = ( ( scoreWT1+scoreWT2 ) / 2 )
    
    value = 0
    if ( not meanScoreWT == 0 ):
        value = scoreKO / meanScoreWT
        value = value-1
    
    return value    

def drawGraph( file, connection, animal, animalListWT , drawContext ):

    print( "*********** DRAWGRAPH")

    event_list = []
    values = []
    colors = []
    
    event_list.append( "Moving alone" )
    colors.append( "black" )
    values.append( getValue( connection, animal, animalListWT, "Move isolated" ) )
    
    event_list.append( "Stopped alone" )
    colors.append( "black" )
    values.append( getValue( connection, animal, animalListWT, "Stop isolated" ) )

    event_list.append( "Rearing isolated" )
    colors.append( "black" )
    values.append( getValue( connection, animal, animalListWT, "Rear isolated" ) )

    event_list.append( "Heading down" )
    colors.append( "black" )
    values.append( getValue( connection, animal, animalListWT, "Look down" ) )
    
    event_list.append( "Huddled" )
    colors.append( "black" )
    values.append( getValue( connection, animal, animalListWT, "Huddling" ) )

    event_list.append( "Jumping" )
    colors.append( "black" )
    values.append( getValue( connection, animal, animalListWT, "WallJump" ) )

    event_list.append( "SAP" )
    colors.append( "black" )
    values.append( getValue( connection, animal, animalListWT, "SAP" ) )

    ''' separator '''
    
    event_list.append( "Moving in contact" )
    colors.append( "red" )
    values.append( getValue( connection, animal, animalListWT, "Move in contact" ) )
        
    event_list.append( "Rearing in contact" )
    colors.append( "red" )
    values.append( getValue( connection, animal, animalListWT, "Rear in contact" ) )
    
    event_list.append( "Side by side sw" )
    colors.append( "red" )
    values.append( getValue( connection, animal, animalListWT, "Side by side Contact" ) )
    
    event_list.append( "Side by side ow" )
    colors.append( "red" )
    values.append( getValue( connection, animal, animalListWT, "Side by side Contact, opposite way" ) )
    
    event_list.append( "Nose-nose" )
    colors.append( "red" )
    values.append( getValue( connection, animal, animalListWT, "Oral-oral Contact" ) )
    
    event_list.append( "Nose-anogenital" )
    colors.append( "red" )
    values.append( getValue( connection, animal, animalListWT, "Oral-genital Contact" ) )
    
    ''' separator '''
    
    event_list.append( "Group of 2 mice" )
    colors.append( "orange" )
    values.append( getValue( connection, animal, animalListWT, "Group2" ) )

    event_list.append( "Group of 3 mice" )
    colors.append( "red" )
    values.append( getValue( connection, animal, animalListWT, "Group3" ) )

    event_list.append( "Out of nest" )
    colors.append( "black" )
    values.append( getValue( connection, animal, animalListWT, "Nest3" ) )

    event_list.append( "Train of 2 mice" )
    colors.append( "red" )
    values.append( getValue( connection, animal, animalListWT, "Train2" ) )

    event_list.append( "Train of 3 mice" )
    colors.append( "red" )
    values.append( getValue( connection, animal, animalListWT, "Train3" ) )

    event_list.append( "Train of 4 mice" )
    colors.append( "red" )
    values.append( getValue( connection, animal, animalListWT, "Train4" ) )

    ''' separator '''    
        
    event_list.append( "Approach in social range (number)" )
    colors.append( "green" )
    values.append( getValue( connection, animal, animalListWT, "Social approach" , type="number" ) )
    
    event_list.append( "Approach a mouse in rearing in social range (number)" )
    colors.append( "green" )
    values.append( getValue( connection, animal, animalListWT, "Approach rear" , type = "number" ) )
    
    event_list.append( "Making contact (duration)" )
    colors.append( "red" )
    values.append( getValue( connection, animal, animalListWT, "Approach contact" ) )

    event_list.append( "Making contact (number)" )
    colors.append( "red" )
    values.append( getValue( connection, animal, animalListWT, "Approach contact" , type="number" ) )

    event_list.append( "Contact" )
    colors.append( "red" )
    values.append( getValue( connection, animal, animalListWT, "Contact" ) )
    
    event_list.append( "Moving away from a mouse in social range (number)" )
    colors.append( "green" )
    values.append( getValue( connection, animal, animalListWT, "Social escape", type= "number" ) )
    
    event_list.append( "Breaking contact (number)" )
    colors.append( "green" )
    values.append( getValue( connection, animal, animalListWT, "Social escape" , type="number" ) )
    
    event_list.append( "Follow within path" )
    colors.append( "green" )
    values.append( getValue( connection, animal, animalListWT, "FollowZone Isolated" ) )
    
    ''' separator '''
    
    event_list.append( "Group making of 3 mice (number)" )
    colors.append( "purple" )
    values.append( getValue( connection, animal, animalListWT, "Group 3 make" , type="number") )

    event_list.append( "Group making of 4 mice (number)" )
    colors.append( "purple" )
    values.append( getValue( connection, animal, animalListWT, "Group 4 make" , type="number") )

    event_list.append( "Group breaking of 3 mice (number)" )
    colors.append( "pink" )
    values.append( getValue( connection, animal, animalListWT, "Group 3 break" , type="number") )

    event_list.append( "Group breaking of 4 mice (number)" )
    colors.append( "pink" )
    values.append( getValue( connection, animal, animalListWT, "Group 4 break" , type="number") )
        
    event_list.append( "seq oral oral - oral geni (number)" )
    colors.append( "pink" )
    values.append( getValue( connection, animal, animalListWT, "seq oral oral - oral genital", type="number" ) )
        
    event_list.append( "seq oral geni - oral oral (number)" )
    colors.append( "pink" )
    values.append( getValue( connection, animal, animalListWT, "seq oral geni - oral oral" , type="number" ) )
        
    
    
    #h = plt.bar( range( len(event_list) ) , values, label=event_list , color=colors )
    
    #xticks_pos = [0.65*patch.get_width() + patch.get_xy()[0] for patch in h]
    
    title= animal.RFID + " -ID- " + animal.genotype
    
    text_file = open ( file+title+setName+".txt", "w")

    text_file.write ( "*******\n" )
    
    text_file.write ( file + "\n")
    
    text_file.write ( title + "\n" )    
    for i in range ( 0, len(event_list ) ):
        text_file.write( event_list[i] + "\t" +  str( values[i] ) + "\n" )
    
                    
    text_file.write( "\n" )
    text_file.close()
    
    
    #plt.xticks( xticks_pos, event_list,  ha='right', rotation=45, fontsize="x-small" )
    #plt.title( title )
    #plt.show()
    
def graphIdentity( file ):
    
    '''
    draw 4 figures with all parameters    
    '''
    
    print(file)
    connection = sqlite3.connect( file )

    pool = AnimalPool( )
    pool.loadAnimals( connection )

    ''' create a list with WT and then KO '''
    
    animalListWT = pool.getAnimalsWithGenotype("WT")
    animalListKO = pool.getAnimalsWithGenotype("KO")

    ''' prepare figure '''
    
    for i in range( 2 ):
        drawGraph( file, connection, animalListKO[i] , animalListWT , None )
    
    

    #plt.savefig('test.pdf', bbox_inches='tight')

    

def getNumberOfEventWithList( connection, eventName, animalA , animalToCompareList ):
    
    sumOfEvent = 0
    for animalCandidate in animalToCompareList:
        
        timeLine = EventTimeLine( connection , eventName , animalA , animalCandidate )
        sumOfEvent += timeLine.getNbEvent()
    
    return sumOfEvent


if __name__ == '__main__':
    
    print("Code launched.")
    
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    
    
    
    for file in files:
        graphIdentity( file )
    
    quit()
    
        
        