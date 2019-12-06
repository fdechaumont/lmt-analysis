'''
Created on 21 nov. 2018

@author: Elodie
'''


import matplotlib.pyplot as plt
import numpy as np; np.random.seed(0)
import sqlite3
from lmtanalysis.Animal import *
from tkinter.filedialog import askopenfilename
from matplotlib.patches import *
from matplotlib.collections import PatchCollection
from lmtanalysis.Util import *
from lmtanalysis.Measure import *
from matplotlib import patches


def plot( ax , animal, title , color = None ):
    xList, yList = animal.getTrajectoryData( )

    if ( color == None ):
        color = animal.getColor()
    ax.plot( xList, yList, color=color, linestyle='-', linewidth=0.5, alpha=0.8, label= animal.name )
    ax.set_title( title + " " + animal.RFID )
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
        detection = animal.detectionDictionnary.get( t )
        xList.append( detection.massX )
        yList.append( -detection.massY )    
    color = "red"
    ax.scatter( xList, yList,  color=color, alpha=1, label= "sap", s=10 )
    

if __name__ == '__main__':
    
    print("Code launched.")
    
    '''
    This script draws the trajectory of the mouse in the two phases of the single object exploration test. The positions at which
    the animal is in SAP is marked in red. The object zone is drawn in light blue.
    '''
    
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    text_file = getFileNameInput()
        
    nbFiles = len(files)
    fig, axes = plt.subplots( nrows = nbFiles, ncols = 2, figsize = (6,12*nbFiles) )
    
    plt.tight_layout(pad=2, h_pad=4, w_pad=0)

    n = 0
        
    for file in files:
        connection = sqlite3.connect( file )
             
        pool = AnimalPool()
        pool.loadAnimals( connection )
        animal = pool.animalDictionnary[1]
        
        # set the axes. Check the number of file to get the dimension of axes and grab the correct ones. This makes it compatible with 1 or n files.
        axLeft = None
        axMiddle2 = None

        if ( len(files) == 1 ):
            axLeft = axes[0]
            axMiddle2 = axes[1]
        else:
            axLeft = axes[n,0]
            axMiddle2 = axes[n,1]
            
        #draw the trajectory in the first phase, without the object
        pool.loadDetection( start=0 , end=28*oneMinute )
        pool.filterDetectionByInstantSpeed( 0,70 );
        plotZone(axLeft, colorEdge='lightgrey', colorFill='lightgrey' ) #whole cage
        #plotZone(axes[n,0], colorEdge='dimgrey', colorFill='dimgrey', xa=120, xb=250, ya=-210, yb=-340) #object zone
        plot ( axLeft, animal , title = "First phase" , color ="black")
        
        #add the frames where the animal is in SAP
        plotSap( axLeft, animal )
        dt1 = animal.getDistance( 0 , 28*oneMinute )
        d1 = animal.getDistanceSpecZone( 0 , 28*oneMinute , xa=120, xb=250, ya=210, yb=340 )
        t1 = animal.getCountFramesSpecZone( 0*oneMinute , 28*oneMinute , xa=120, xb=250, ya=210, yb=340)
        sap1=len(animal.getSap(tmin=0, tmax=28*oneMinute, xa=120, xb=250, ya=210, yb=340 ))
                   
            
        #draw the trajectory in the second phase, with the object
        pool.loadDetection( start=32*oneMinute , end=60*oneMinute )
        pool.filterDetectionByInstantSpeed( 0,70 );
        plotZone(axMiddle2, colorEdge='lightgrey', colorFill='lightgrey' ) #whole cage
        plotZone(axMiddle2, colorEdge='dimgrey', colorFill='dimgrey', xa=120, xb=250, ya=-210, yb=-340) #object zone
        plot ( axMiddle2, animal, title = "Second phase", color ="black" )
        #add the frames where the animal is in SAP
        plotSap( axMiddle2, animal )
        dt2 = animal.getDistance( 32*oneMinute , 60*oneMinute )
        d2 = animal.getDistanceSpecZone( 32*oneMinute , 60*oneMinute , xa=120, xb=250, ya=210, yb=340 )
        t2 = animal.getCountFramesSpecZone( 32*oneMinute , 60*oneMinute , xa=120, xb=250, ya=210, yb=340)
        sap2=len(animal.getSap(tmin=32*oneMinute, tmax=60*oneMinute, xa=120, xb=250, ya=210, yb=340)) 
                  
        n = n+1
        
        text_file.write( "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( file, animal.RFID, animal.genotype, animal.user1, d1*10/57, dt1*10/57, t1, sap1, d2*10/57, dt2*10/57, t2, sap2 ) )
        
    fig.suptitle('Single object exploration', fontsize=14, fontweight='bold') 
    plt.show()
    fig.savefig('single_obj_explo.pdf', transparent=False, dpi=80, bbox_inches="tight")
    
    text_file.write( "\n" )
    text_file.close()
    
    print("All jobs done")
   
       