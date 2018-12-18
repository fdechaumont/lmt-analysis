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

def getValue( connection, animal, eventName ):
    
    timeLine = EventTimeLine( connection, eventName, animal.baseId )
    return timeLine.getNbEvent()    

def drawGraph( connection, animal, animalList , drawContext ):

    event_list = []
    values = []
    colors = []
    
    event_list.append( "Moving alone" )
    colors.append( "black" )
    values.append( getValue( connection, animal, "Move isolated" ) )
    
    event_list.append( "Stopped alone" )
    colors.append( "black" )
    values.append( getValue( connection, animal, "Stop isolated" ) )

    event_list.append( "Rearing isolated" )
    colors.append( "black" )
    values.append( getValue( connection, animal, "Rear isolated" ) )

    event_list.append( "Heading up" )
    colors.append( "black" )
    values.append( getValue( connection, animal, "Look up" ) )

    event_list.append( "Heading down" )
    colors.append( "black" )
    values.append( getValue( connection, animal, "Look down" ) )
    
    event_list.append( "Huddled" )
    colors.append( "black" )
    values.append( getValue( connection, animal, "Huddling" ) )

    event_list.append( "Jumping" )
    colors.append( "black" )
    values.append( getValue( connection, animal, "WallJump" ) )

    event_list.append( "SAP" )
    colors.append( "black" )
    values.append( getValue( connection, animal, "SAP" ) )

    ''' separator '''
    event_list.append( "" )
    colors.append( "black" )
    values.append( 0 )
    
    event_list.append( "Moving in contact" )
    colors.append( "red" )
    values.append( getValue( connection, animal, "Move in contact" ) )
    
    event_list.append( "Stopped in contact" )
    colors.append( "red" )
    values.append( getValue( connection, animal, "Stopped in contact" ) )
    
    event_list.append( "Rearing in contact" )
    colors.append( "red" )
    values.append( getValue( connection, animal, "Rear in contact" ) )
    
    event_list.append( "Side by side sw" )
    colors.append( "red" )
    values.append( getValue( connection, animal, "Side by side Contact" ) )
    
    event_list.append( "Side by side ow" )
    colors.append( "red" )
    values.append( getValue( connection, animal, "Side by side Contact, opposite way" ) )
    
    event_list.append( "Nose-nose" )
    colors.append( "red" )
    values.append( getValue( connection, animal, "Oral-oral Contact" ) )
    
    event_list.append( "Nose-anogenital" )
    colors.append( "red" )
    values.append( getValue( connection, animal, "Oral-genital Contact" ) )
    
    ''' separator '''
    event_list.append( "" )
    colors.append( "black" )
    values.append( 0 )
        
    event_list.append( "Group of 2 mice" )
    colors.append( "orange" )
    values.append( getValue( connection, animal, "Group2" ) )

    event_list.append( "Group of 3 mice" )
    colors.append( "red" )
    values.append( getValue( connection, animal, "Group3" ) )

    event_list.append( "Group of 4 mice" )
    colors.append( "purple" )
    values.append( getValue( connection, animal, "Group4" ) )

    event_list.append( "Out of nest" )
    colors.append( "black" )
    values.append( getValue( connection, animal, "Nest3" ) )

    event_list.append( "Nest of 4 mice" )
    colors.append( "black" )
    values.append( getValue( connection, animal, "Nest4" ) )

    event_list.append( "Train of 2 mice" )
    colors.append( "red" )
    values.append( getValue( connection, animal, "Train2" ) )

    event_list.append( "Train of 3 mice" )
    colors.append( "red" )
    values.append( getValue( connection, animal, "Train3" ) )

    event_list.append( "Train of 4 mice" )
    colors.append( "red" )
    values.append( getValue( connection, animal, "Train4" ) )

    ''' separator '''
    event_list.append( "" )
    colors.append( "black" )
    values.append( 0 )
        
    event_list.append( "Approach in social range" )
    colors.append( "green" )
    values.append( getValue( connection, animal, "Social approach" ) )
    
    event_list.append( "Approach a mouse in rearing in social range" )
    colors.append( "green" )
    values.append( getValue( connection, animal, "Approach rear" ) )
    
    event_list.append( "Making contact" )
    colors.append( "red" )
    values.append( getValue( connection, animal, "Approach contact" ) )
    
    event_list.append( "Moving away from a mouse in social range" )
    colors.append( "green" )
    values.append( getValue( connection, animal, "Social escape" ) )
    
    event_list.append( "Breaking contact" )
    colors.append( "green" )
    values.append( getValue( connection, animal, "Social escape" ) )
    
    event_list.append( "Follow within path" )
    colors.append( "green" )
    values.append( getValue( connection, animal, "FollowZone Isolated" ) )
    
    ''' separator '''
    event_list.append( "" )
    colors.append( "black" )
    values.append( 0 )
        
    event_list.append( "Group making of 3 mice" )
    colors.append( "purple" )
    values.append( getValue( connection, animal, "Group 3 make" ) )

    event_list.append( "Group making of 4 mice" )
    colors.append( "purple" )
    values.append( getValue( connection, animal, "Group 4 make" ) )

    event_list.append( "Group breaking of 3 mice" )
    colors.append( "pink" )
    values.append( getValue( connection, animal, "Group 3 break" ) )

    event_list.append( "Group breaking of 4 mice" )
    colors.append( "pink" )
    values.append( getValue( connection, animal, "Group 4 break" ) )
        
    
    #plt.figure(1)
    h = drawContext.bar( range( len(event_list) ) , values, label=event_list , color=colors )
    #drawContext.subplots_adjust(bottom=0.3)
    
    xticks_pos = [0.65*patch.get_width() + patch.get_xy()[0] for patch in h]
    
    title= animal.name + " - " + animal.genotype
    
    drawContext.set_title( title )
    
    ''' log scale '''
    drawContext.set_yscale("log", nonposy='clip')
    
    plt.sca( drawContext )
    #plt.xticks( xticks_pos, event_list,  ha='right', rotation=45, fontsize="x-small" )
    
def graphIdentity( file ):
    
    '''
    draw 4 figures with all parameters    
    '''
    
    print(file)
    connection = sqlite3.connect( file )

    pool = AnimalPool( )
    pool.loadAnimals( connection )

    ''' create a list with WT and then KO '''
    animalList = []
    
    animalList.extend( pool.getAnimalsWithGenotype("WT") )
    animalList.extend( pool.getAnimalsWithGenotype("KO") )

    for animal in animalList:
        print ( animal )

    ''' prepare figure '''
    fig, ax = plt.subplots( 2 , 2 )        

    index = 0
    for x in range( 2 ):
        for y in range( 2 ):
            drawContext = ax[x,y]
            drawGraph( connection, animalList[index] , animalList , drawContext )
            index+=1

    fig.tight_layout()
    plt.suptitle( "exp. " + file )

    plt.show()
    #plt.savefig('test.pdf', bbox_inches='tight')

    

def getNumberOfEventWithList( connection, eventName, animalA , animalToCompareList ):
    
    sumOfEvent = 0
    for animalCandidate in animalToCompareList:
        
        timeLine = EventTimeLine( connection , eventName , animalA , animalCandidate )
        sumOfEvent += timeLine.getNbEvent()
    
    return sumOfEvent


if __name__ == '__main__':
    
    print("Code launched.")
    
    #files = ["/Users/elodie/Documents/2016_09_shank2_exp/2016_10_exp_tracking/2017_03_lg_term_rec_group/2017_05_16_test_48h/test_24h/20170516_6559/20170516_Experiment 6559_test.sqlite"]
    #files = ["/Users/elodie/ownCloud/phenoRT/2017_03_17/Experiment 2082_4 petites/Experiment 2082_test.sqlite"]
    '''
    files = ["/Users/elodie/Documents/2016_09_shank2_exp/2016_10_exp_tracking/2017_03_lg_term_rec_group/2017_05_16_test_48h/test_24h/20170516_6559/20170516_Experiment 6559.sqlite",
"/Users/elodie/Documents/2016_09_shank2_exp/2016_10_exp_tracking/2017_03_lg_term_rec_group/2017_05_16_test_48h/test_24h/20170606_6778/20170606_Experiment 6778.sqlite",
"/Users/elodie/Documents/2016_09_shank2_exp/2016_10_exp_tracking/2017_03_lg_term_rec_group/2017_05_16_test_48h/test_24h/20170607_7690/20170607_Experiment 7690.sqlite",
"/Users/elodie/Documents/2016_09_shank2_exp/2016_10_exp_tracking/2017_03_lg_term_rec_group/2017_05_16_test_48h/test_24h/20170612_8637/20170612_Experiment 8637.sqlite",
"/Users/elodie/Documents/2016_09_shank2_exp/2016_10_exp_tracking/2017_03_lg_term_rec_group/2017_05_16_test_48h/test_24h/20170614_6507/20170614_Experiment 6507.sqlite",
"/Users/elodie/Documents/2016_09_shank2_exp/2016_10_exp_tracking/2017_03_lg_term_rec_group/2017_05_16_test_48h/test_24h/20170627_1111/20170627_Experiment 1111.sqlite",

"/Users/elodie/Documents/2016_09_shank2_exp/2016_10_exp_tracking/2017_03_lg_term_rec_group/2017_05_16_test_48h/test_24h/20170920_1997/20170920_Experiment_1997_processed.sqlite",
"/Users/elodie/Documents/2016_09_shank2_exp/2016_10_exp_tracking/2017_03_lg_term_rec_group/2017_05_16_test_48h/test_24h/20170921_288/20170921_Experiment_288_processed.sqlite",
"/Users/elodie/Documents/2016_09_shank2_exp/2016_10_exp_tracking/2017_03_lg_term_rec_group/2017_05_16_test_48h/test_24h/20170925_8269/20170925_Experiment_8269 processed.sqlite",
"/Users/elodie/Documents/2016_09_shank2_exp/2016_10_exp_tracking/2017_03_lg_term_rec_group/2017_05_16_test_48h/test_24h/20170926_3195/20170926_Experiment_3195 processed.sqlite"]
    
    files = ["/Users/elodie/Documents/2016_09_shank2_exp/2016_10_exp_tracking/2017_03_shank2_social_recognition/2017_03_updated_db_hab/hab_4576-4667/20170322_4576-4667_hab_v2.sqlite"]
    '''
    
    files = [ 
    #"/Users/elodie/Documents/2017_09_shank3_live_mouse_tracker/2017_11_shank3_long_term/shank3_databases/20171107_Exp_0177.sqlite",
    #"/Users/elodie/Documents/2017_09_shank3_live_mouse_tracker/2017_11_shank3_long_term/shank3_databases/20171113_Experiment_6233.sqlite",
    #"/Users/elodie/Documents/2017_09_shank3_live_mouse_tracker/2017_11_shank3_long_term/shank3_databases/20171113_Experiment_9078.sqlite",
    #"/Users/elodie/Documents/2017_09_shank3_live_mouse_tracker/2017_11_shank3_long_term/shank3_databases/20171117_Experiment_7589long.sqlite",
    "/Users/elodie/Documents/2017_09_shank3_live_mouse_tracker/2017_11_shank3_long_term/shank3_databases/20171124_Experiment_889.sqlite" ]
    
    files = [ "c:/testbase/valid4.sqlite" 
        ]
    
    '''
    files = [ "c:/testbase/0177.sqlite" 
        ]
    '''
    
    maxT = oneMinute*240
    
    for file in files:
        graphIdentity( file )
    
    quit()
    
        
    for file in files:
        
        print(file)
        connection = sqlite3.connect( file )

        pool = AnimalPool( )
        pool.loadAnimals( connection )
        
        for animalA in pool.animalDictionnary :
            
            animalDiffGeno = []
            animalSameGeno = []
            
            for animal in pool.animalDictionnary:
                if animal.genotype == animalA.genotype:
                    animalSameGeno.append( animal )
                else:
                    animalDiffGeno.append( animal )
                    
            ''' start computation of animalA against the others '''
                    
            nbContact = getNumberOfEventWithList( connection, "Contact" , animalA , animalDiffGeno )
            
            print ( nbContact )
        
        
        
        print( "*** ALL JOBS DONE ***")
        
        