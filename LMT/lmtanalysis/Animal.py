'''
Created on 7 sept. 2017

@author: Fab
'''

from lmtanalysis.Detection import *

import matplotlib


#matplotlib fix for mac (uncomment if needed)
#matplotlib.use('TkAgg' )


import matplotlib.pyplot as plt
from lmtanalysis.Chronometer import *
import matplotlib as mpl
import numpy as np
import pandas as pd
from collections import defaultdict
from mpl_toolkits.mplot3d import *
import matplotlib.ticker
import math
import time
from lmtanalysis.Measure import *
from lmtanalysis.Measure import ARENA_SIZE, CENTER_MARGIN
from statistics import *
from scipy.spatial import distance
from scipy.ndimage.measurements import standard_deviation
from statistics import mean
from lmtanalysis.Event import EventTimeLine
from lmtanalysis.Point import Point
from lmtanalysis.Mask import Mask
from lmtanalysis.Util import getAllEvents
import matplotlib.patches as mpatches
from lxml import etree
import matplotlib.ticker as ticker
from lmtanalysis.Util import convert_to_d_h_m_s, getDatetimeFromFrame, mute_prints

idAnimalColor = [ None, "red","green","blue","orange"]

def getAnimalColor( animalId ):
    return idAnimalColor[ animalId ]

class Animal():

    def __init__(self, baseId , RFID , name=None, genotype=None , user1 = None, age=None, sex=None, strain=None, conn = None ):
        self.baseId = baseId
        self.RFID = RFID
        self.name = name
        self.genotype = genotype
        self.user1 = user1
        self.age = age
        self.sex = sex
        self.strain = strain
        self.conn = conn
        self.detectionDictionnary = {}

    def setGenotype(self, genotype ):
        self.genotype = genotype
        cursor = self.conn.cursor()
        query = "UPDATE `ANIMAL` SET `GENOTYPE`='{}' WHERE `ID`='{}';".format( genotype, self.baseId )
        cursor.execute( query )
        self.conn.commit()
        cursor.close()

    def __str__(self):
        return "Animal Id:{id} Name:{name} RFID:{rfid} Genotype:{genotype} User1:{user1}"\
            .format( id=self.baseId, rfid=self.RFID, name=self.name, genotype=self.genotype, user1=self.user1 )

    def getColor(self):
        return getAnimalColor( self.baseId )

    def getDetectionAt(self, t):
        if t in self.detectionDictionnary:
            return self.detectionDictionnary[t]
        return None

    def loadDetection(self, start=None, end=None, lightLoad = False ):
        '''
        lightLoad only loads massX and massY to speed up the load. Then one can only compute basic features such as global speed of the animals
        '''
        print ( self.__str__(), ": Loading detection.")
        chrono = Chronometer("Load detection")

        self.detectionDictionnary.clear()

        cursor = self.conn.cursor()
        query =""
        if lightLoad == True :
            query = "SELECT FRAMENUMBER, MASS_X, MASS_Y FROM DETECTION WHERE ANIMALID={}".format( self.baseId )
        else:
            query = "SELECT FRAMENUMBER, MASS_X, MASS_Y, MASS_Z, FRONT_X, FRONT_Y, FRONT_Z, BACK_X, BACK_Y, BACK_Z,REARING,LOOK_UP,LOOK_DOWN FROM DETECTION WHERE ANIMALID={}".format( self.baseId )

        if ( start != None ):
            query += " AND FRAMENUMBER>={}".format(start )
        if ( end != None ):
            query += " AND FRAMENUMBER<={}".format(end )

        print( query )
        cursor.execute( query )

        rows = cursor.fetchall()
        cursor.close()

        for row in rows:
            frameNumber = row[0]
            massX = row[1]
            massY = row[2]
            detection = None
            #filter detection at 0

            if ( massX < 10 ):
                continue

            if not lightLoad:
                massZ = row[3]

                frontX = row[4]
                frontY = row[5]
                frontZ = row[6]

                backX = row[7]
                backY = row[8]
                backZ = row[9]

                rearing = row[10]
                lookUp = row[11]
                lookDown = row[12]

                detection = Detection( massX, massY, massZ, frontX, frontY, frontZ, backX, backY, backZ, rearing, lookUp, lookDown )
            else:
                detection = Detection( massX, massY , lightLoad = True )

            self.detectionDictionnary[frameNumber] = detection

        print ( self.__str__(), " ", len( self.detectionDictionnary ) , " detections loaded in {} seconds.".format( chrono.getTimeInS( )) )

    def loadMask(self , frame ):
        self.setMask( self.getBinaryDetectionMask( frame ) )

    def clearMask(self):
        self.setMask( None )

    def getNumberOfDetection(self, tmin, tmax):


        return len ( self.detectionDictionnary.keys() )


    def filterDetectionByInstantSpeed(self , minSpeed, maxSpeed ):
        """
        speed function in LMT use t-1 and t+1 detection to provide a result.
        here we remove spurious tracking jump, so we check on t to t+1 frame.
        speed is in cm per second
        """
        nbRemoved = 0
        for key in sorted(self.detectionDictionnary.keys()):
            a = self.detectionDictionnary.get( key )
            b = self.detectionDictionnary.get( key+1 )

            if ( b==None or a==None):
                continue

            speed = math.hypot( a.massX - b.massX, a.massY - b.massY )*scaleFactor/(1/30)

            if ( speed > maxSpeed or speed < minSpeed ):
                self.detectionDictionnary.pop( key )
                nbRemoved+=1

        print( "Filtering Instant speed min:",minSpeed, "max:",maxSpeed, "number of detection removed:", nbRemoved )

    def filterDetectionByArea(self, x1, y1, x2, y2 ):
        '''
        filter detection in the cage ( using centimeter, starting at top left of the cage )
        '''
        nbRemoved = 0
        for key in sorted(self.detectionDictionnary.keys()):
            a = self.detectionDictionnary.get( key )

            if ( a==None):
                continue

            x = (a.massX - cornerCoordinates50x50Area[0][0] )* scaleFactor
            y = (a.massY - cornerCoordinates50x50Area[0][1] )* scaleFactor

            if ( x < x1 or x > x2 or y < y1 or y > y2 ):
                self.detectionDictionnary.pop( key )
                nbRemoved+=1

        print( "Filtering area, number of detection removed:", nbRemoved )

    def filterDetectionByEventTimeLine( self, eventTimeLineVoc ):
        '''
        filter detection using an event. Keep only what matches the event
        '''
        eventDic = eventTimeLineVoc.getDictionnary()
        nbRemoved = 0
        for key in sorted( self.detectionDictionnary.keys() ):
            a = self.detectionDictionnary.get( key )

            if ( a==None):
                continue

            if not ( key in eventDic ):
                self.detectionDictionnary.pop( key )
                nbRemoved+=1

        print( "Filtering area, number of detection removed:", nbRemoved )

    def clearDetection(self):

        self.detectionDictionnary.clear()

    def getMaxDetectionT(self):
        """
        returns the timepoint of the last detection.
        """

        if len ( self.detectionDictionnary.keys() ) == 0:
            return None

        return sorted(self.detectionDictionnary.keys())[-1]

    def getTrajectoryData( self , maskingEventTimeLine=None ):

        keyList = sorted(self.detectionDictionnary.keys())

        if maskingEventTimeLine!=None:
            keyList = maskingEventTimeLine.getDictionnary()

        xList = []
        yList = []

        previousKey = 0


        for key in keyList:

            #print ( "key:", key, "value", self.getSpeed( key ) , "previous:" , previousKey )

            if previousKey+1 != key:
                xList.append( [np.nan, np.nan] )
                yList.append( [np.nan, np.nan] )
                previousKey = key

                #print("break previous")
                continue
            previousKey = key

            a = self.detectionDictionnary.get( key )
            if ( a==None):
                xList.append( [np.nan, np.nan] )
                yList.append( [np.nan, np.nan] )
                #print("break none A")
                continue
            b = self.detectionDictionnary.get( key+1 )
            if ( b==None):
                xList.append( [np.nan, np.nan] )
                yList.append( [np.nan, np.nan] )
                #print("break none B")
                continue

            xList.append( [a.massX,b.massX] )
            yList.append( [-a.massY,-b.massY] )

        return xList, yList


    def plotTrajectory(self , show=True, color='k', maskingEventTimeLine=None, title = "" ):

        print ("Draw trajectory of animal " + self.name )

        xList, yList = self.getTrajectoryData( maskingEventTimeLine )

        plt.plot( xList, yList, color=color, linestyle='-', linewidth=1, alpha=0.5, label= self.name )
        plt.title( title + self.RFID )
        plt.xlim(90, 420)
        plt.ylim(-370, -40)

        if ( show ):
            plt.show()


    def plotTrajectory3D(self):

        print ("Draw 3D trajectory")
        keyList = sorted(self.detectionDictionnary.keys())

        mpl.rcParams['legend.fontsize'] = 10

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        theta = np.linspace(-4 * np.pi, 4 * np.pi, 100)

        z = np.linspace(-2, 2, 100)
        r = z**2 + 1
        x = r * np.sin(theta)
        y = r * np.cos(theta)

        '''
        print ( z )
        print ( r )
        print ( x )
        print ( y )
        '''

        xList = []
        yList = []
        zList = []

        for key in keyList:

            a = self.detectionDictionnary.get( key )
            b = self.detectionDictionnary.get( key+1 )
            if ( b==None):
                continue

            xList.append( a.massX )
            yList.append( a.massY )
            zList.append( a.massZ )

        ax.plot(xList, yList, zList, label= "3D Trajectory of " + self.RFID )
        ax.legend()

        plt.show()


    def getDistancePerBin(self , binFrameSize , minFrame=0, maxFrame=None ):
        if ( maxFrame==None ):
            maxFrame= self.getMaxDetectionT()

        distanceList = []
        t = minFrame
        while ( t < maxFrame ):
            distanceBin = self.getDistance( t , t+binFrameSize )
            print( "Distance bin n:{} value:{}".format ( t , distanceBin ) )
            distanceList.append( distanceBin )
            t=t+binFrameSize

        return distanceList


    def getDistance(self , tmin=0, tmax= None ):
        '''
        Returns the distance traveled by the animal (in cm)
        '''
        print("Compute total distance min:{} max:{} ".format( tmin , tmax ))


        '''
        keyList = list( self.detectionDictionnary.keys() )
        if not alreadySorted:
            keyList = sorted(self.detectionDictionnary.keys())
        '''
        if ( tmax==None ):
            tmax= self.getMaxDetectionT()

        totalDistance = 0
        for t in range( tmin , tmax ):
        #for key in keyList:

            '''
            if ( key <= tmin or key >= tmax ):
                continue
            '''

            a = self.detectionDictionnary.get( t )
            b = self.detectionDictionnary.get( t+1 )

            if b==None or a==None:
                continue
            distance = math.hypot( a.massX - b.massX, a.massY - b.massY )
            if ( distance >85.5): #if the distance calculated between two frames is too large, discard
                continue

            totalDistance += distance

        totalDistance *= scaleFactor

        return totalDistance

    def getOrientationVector(self, t):

        d = self.detectionDictionnary.get( t )

        if d == None:
            return None

        if d.frontX == None:
            return None

        if d.backX == None:
            return None

        deltaX = d.frontX - d.backX
        deltaY = d.frontY - d.backY
        p = Point( deltaX, deltaY )
        return p

    def getSpeedVector(self, t):

        a = self.detectionDictionnary.get( t-1 )
        b = self.detectionDictionnary.get( t+1 )

        if a == None or b == None:
            return None

        speedVectorX = a.massX - b.massX
        speedVectorY = a.massY - b.massY

        p = Point( speedVectorX, speedVectorY )
        return p

    def getFrontSpeed(self, t):

        a = self.detectionDictionnary.get( t-1 )
        b = self.detectionDictionnary.get( t+1 )

        if a == None or b == None:
            return None

        speedVectorX = a.frontX - b.frontX
        speedVectorY = a.frontY - b.frontY

        p = Point( speedVectorX, speedVectorY )
        return p

    def getBackSpeed(self, t):

        a = self.detectionDictionnary.get( t-1 )
        b = self.detectionDictionnary.get( t+1 )

        if a == None or b == None:
            return None

        speedVectorX = a.backX - b.backX
        speedVectorY = a.backY - b.backY

        p = Point( speedVectorX, speedVectorY )
        return p


    def getDistanceSpecZone(self, tmin=0, tmax=None, xa=None, ya=None, xb=None, yb=None):

        keyList = sorted(self.detectionDictionnary.keys())

        if ( tmax==None ):
            tmax = self.getMaxDetectionT()

        distance = 0

        for key in keyList:

            if ( key <= tmin or key >= tmax ):
                #print ( 1 )
                continue

            a = self.detectionDictionnary.get( key )
            b = self.detectionDictionnary.get( key+1 )

            if ( b==None):
                continue

            if (a.massX<xa or a.massX>xb or a.massY<ya or a.massY>yb or b.massX<xa or b.massX>xb or b.massY<ya or b.massY>yb):
                #print ( 2 )
                continue

            if (math.hypot( a.massX - b.massX, a.massY - b.massY )>85.5): #if the distance calculated between two frames is too large, discard
                continue

            distance += math.hypot( a.massX - b.massX, a.massY - b.massY )

        distance *= scaleFactor

        return distance


    def getDistanceTo (self, t, animalB):
        '''
        determine the distance between the focal animal and another one specified in argument at one specified time point t
        check before that both animals are detected at this time point
        '''
        distanceTo = None

        if ( not ( t in animalB.detectionDictionnary ) ):
            return None

        if ( not ( t in self.detectionDictionnary ) ):
            return None

        if (animalB.detectionDictionnary[t].massX == None):
            return None

        if (math.hypot( self.detectionDictionnary[t].massX - animalB.detectionDictionnary[t].massX, self.detectionDictionnary[t].massY - animalB.detectionDictionnary[t].massY ) > 71*57/10): #if the distance calculated between the two individuals is too large, discard
            return None

        else:
            distanceTo = math.hypot( self.detectionDictionnary[t].massX - animalB.detectionDictionnary[t].massX, self.detectionDictionnary[t].massY - animalB.detectionDictionnary[t].massY )
            return distanceTo


    def getDistanceToPoint (self, t, xPoint, yPoint):
        '''
        determine the distance between the focal animal and a specific point in the arena at one specified time point t
        '''
        distanceToPoint = None

        if ( not ( t in self.detectionDictionnary ) ):
            return None

        if (math.hypot( self.detectionDictionnary[t].massX - xPoint, self.detectionDictionnary[t].massY - yPoint ) > MAX_DISTANCE_THRESHOLD): #if the distance calculated is too large, discard
            return None

        else:
            distanceToPoint = math.hypot( self.detectionDictionnary[t].massX - xPoint, self.detectionDictionnary[t].massY - yPoint )
            return distanceToPoint


    def getMeanBodyLength (self, tmin=0, tmax=None):
        '''
        determine the mean body length over the time window specified
        '''
        keyList = sorted(self.detectionDictionnary.keys())

        if ( tmax==None ):
            tmax= self.getMaxDetectionT()

        if ( tmax==None ):
            self.meanBodyLength = None
            return self.meanBodyLength

        bodySizeList = []

        for key in keyList:

            if ( key <= tmin or key >= tmax ):
                continue

            a = self.detectionDictionnary.get( key )
            bodySizeList.append(a.getBodySize())

        mean = np.nanmean(bodySizeList)
        print( "mean animal bodysize: "  , mean )

        self.meanBodyLength = mean

        return self.meanBodyLength


    def getBodyThreshold (self, tmin=0, tmax=None):
        '''
        determine the body size threshold used to determine SAP
        '''
        keyList = sorted(self.detectionDictionnary.keys())

        if ( tmax==None ):
            tmax= self.getMaxDetectionT()

        bodySizeList = []

        for key in keyList:

            if ( key <= tmin or key >= tmax ):
                continue

            a = self.detectionDictionnary.get( key )
            bodySizeList.append(a.getBodySize())

        #verifier si ce calcul tourne bien:
        threshold = np.nanmean(bodySizeList) + np.nanstd(bodySizeList)

        self.bodyThreshold = threshold

        return self.bodyThreshold


    def getMedianBodyHeight (self, tmin=0, tmax=None):
        '''
        determine the body size threshold used to determine SAP
        '''
        keyList = sorted(self.detectionDictionnary.keys())

        if ( tmax==None ):
            tmax= self.getMaxDetectionT()

        bodyHeightList = []

        for key in keyList:

            if ( key <= tmin or key >= tmax ):
                continue

            a = self.detectionDictionnary.get( key )
            bodyHeightList.append(a.massZ)

        self.medianBodyHeight = np.median(np.array(bodyHeightList))

        return self.medianBodyHeight


    def getThresholdMassHeight (self, tmin=0, tmax=None):
        '''
        determine the body size height threshold used to determine whether the animal is rearing or not
        here we use the 7th decile
        '''
        keyList = sorted(self.detectionDictionnary.keys())

        if ( tmax==None ):
            tmax= self.getMaxDetectionT()

        massHeightList = []

        for key in keyList:

            if ( key <= tmin or key >= tmax ):
                continue

            a = self.detectionDictionnary.get( key )
            massHeightList.append(a.massZ)

        decile = 7*len(massHeightList)/10
        print("7eme decile mass:")
        print(decile)
        print("arrondi massZ:")
        print(math.ceil(decile)-1)

        self.eightDecileMassHeight = sorted(massHeightList)[math.ceil(decile)-1]

        return self.eightDecileMassHeight


    def getThresholdFrontHeight (self, tmin=0, tmax=None):
        '''
        determine the body size height threshold used to determine whether the animal is rearing or not
        here we use the 7th decile
        '''
        keyList = sorted(self.detectionDictionnary.keys())

        if ( tmax==None ):
            tmax= self.getMaxDetectionT()

        frontHeightList = []

        for key in keyList:

            if ( key <= tmin or key >= tmax ):
                continue

            a = self.detectionDictionnary.get( key )
            frontHeightList.append(a.frontZ)

        decile = 7*len(frontHeightList)/10
        print("7eme decile front:")
        print(decile)
        print("arrondi frontZ:")
        print(math.ceil(decile)-1)

        self.eightDecileFrontHeight = sorted(frontHeightList)[math.ceil(decile)-1]

        return self.eightDecileFrontHeight


    def getDirection(self, t):
        '''
        determines the direction of the animal using the head and the mass center
        '''
        a = self.detectionDictionnary.get( t )
        return a.getDirection();


    def getSpeed(self , t ):
        '''
        calculate the instantaneous speed of the animal at each frame
        '''
        a = self.detectionDictionnary.get( t-1 )
        b = self.detectionDictionnary.get( t+1 )

        if ( b==None or a==None):
            return None

        speed = math.hypot( a.massX - b.massX, a.massY - b.massY )*scaleFactor/(2/30)

        return speed


    def getVerticalSpeed(self , t ):
        '''
        calculate the instantaneous vertical speed of the mass center of the animal at each frame
        '''
        a = self.detectionDictionnary.get( t-1 )
        b = self.detectionDictionnary.get( t+1 )

        if ( b==None or a==None):
            return None

        verticalSpeed = (b.massZ - a.massZ)/2

        return verticalSpeed


    def getSap(self, tmin=0, tmax=None, xa=None, ya=None, xb=None, yb=None):
        print("Compute number of frames in SAP in specific zone of the cage")

        self.getBodyThreshold( )
        self.getMedianBodyHeight()

        #TODO: pas mettre body threshold en self car ... c'est pas la peine.

        keyList = sorted(self.detectionDictionnary.keys())

        if ( tmax==None ):
            tmax = self.getMaxDetectionT()

        sapList = []

        for key in keyList:

            if ( key <= tmin or key >= tmax ):
                #print ( 1 )
                continue

            detection = self.detectionDictionnary.get(key);
            if (detection.massX<xa or detection.massX>xb or detection.massY<ya or detection.massY>yb or detection.massZ>self.medianBodyHeight):
                #print ( 2 )
                continue

            speed = self.getSpeed( key )
            if ( speed == None ):
                #print ( 3 )
                continue

            if (detection.getBodySize( ) >=self.bodyThreshold and speed<SPEED_THRESHOLD_LOW and detection.massZ<self.medianBodyHeight):
                #print ( 4 )
                sapList.append( detection )

        return sapList


    def getSapDictionnary(self, tmin=0, tmax=None ):

        self.getBodyThreshold( )
        self.getMedianBodyHeight()

        keyList = sorted(self.detectionDictionnary.keys())

        if ( tmax==None ):
            tmax = self.getMaxDetectionT()

        sapDictionnary = {}

        for key in keyList:

            if ( key <= tmin or key >= tmax ):
                continue

            detection = self.detectionDictionnary.get(key);

            speed = self.getSpeed( key )
            if ( speed == None ):
                continue

            if (detection.getBodySize( ) >=self.bodyThreshold and speed<SPEED_THRESHOLD_LOW and detection.massZ<self.medianBodyHeight):
                sapDictionnary[key] = True

        return sapDictionnary


    def getCountFramesSpecZone(self, tmin=0, tmax=None, xa=None, ya=None, xb=None, yb=None):
        '''
        coordinates are in pixel
        '''
        keyList = sorted(self.detectionDictionnary.keys())

        x1=min( xa, xb )
        x2=max( xa, xb )
        y1=min( ya, yb )
        y2=max( ya, yb )

        if ( tmax==None ):
            tmax = self.getMaxDetectionT()

        count =0

        for key in keyList:

            if ( key <= tmin or key >= tmax ):
                #print ( 1 )
                continue

            detection = self.detectionDictionnary.get(key);
            if (detection.massX<x1 or detection.massX>x2 or detection.massY<y1 or detection.massY>y2):
                #print ( 2 )
                continue

            count+=1

        return count


    def plotDistance(self, color='k' , show=True ):
        print ("Plot distance")
        keyList = sorted(self.detectionDictionnary.keys())

        tList = []
        distanceList = []

        totalDistance = 0
        for key in keyList:

            a = self.detectionDictionnary.get( key )
            b = self.detectionDictionnary.get( key+1 )

            if ( b==None):
                continue

            totalDistance += math.hypot( a.massX - b.massX, a.massY - b.massY )

            tList.append( key / 30 / 60 )
            distanceList.append( totalDistance )

        #fig,ax = plt.subplots()
        plt.plot( tList, distanceList, color=color, linestyle='-', linewidth=2 , label="Cumulated distance of " + self.__str__() )

        #formatter = matplotlib.ticker.FuncFormatter(lambda frame, x: time.strftime('%Hh%Mm%Ss', time.gmtime( frame // 30)))
        #formatter = matplotlib.ticker.FuncFormatter(lambda frame, x: time.strftime('%Hh%Mm', time.gmtime( frame // 30)))
        #ax.xaxis.set_major_formatter( formatter )
        #ax.xaxis.set_minor_locator( matplotlib.ticker.MultipleLocator(30*60) )
        #ax.xaxis.set_major_locator( matplotlib.ticker.MultipleLocator(30*60*10) )

        plt.legend()

        if ( show ):
            plt.show()


    def getBinaryDetectionMask(self , t):
        '''
        returns the mask of a detection at a given T.
        '''
        query = "SELECT DATA FROM DETECTION WHERE ANIMALID={} AND FRAMENUMBER={}".format( self.baseId , t )

        cursor = self.conn.cursor()
        cursor.execute( query )

        rows = cursor.fetchall()
        cursor.close()

        if ( len(rows)!=1 ):
            #print ("unexpected number of row: " , str( len(rows ) ) )
            return None

        row = rows[0]
        data = row[0]

        mask = Mask( data, self.getColor( ) )

        return mask


class AnimalPool():
    """
    Manages an experiment.
    """

    def __init__(self):

        self.animalDictionnary = {}
        self.detectionStartFrame = None
        self.detectionEndFrame   = None

    def getAnimalDictionnary(self):
        return self.animalDictionnary

    def getAnimalWithId(self , id):
        return self.animalDictionnary[id]

    def getAnimalList(self):

        animalList= []

        for k in self.animalDictionnary:
            animal = self.animalDictionnary[k]
            animalList.append( animal )

        return animalList

    def loadAnimals( self, conn ):

        print ("Loading animals.")

        cursor = conn.cursor()
        self.conn = conn

        # Check the number of row available in base
        query = "SELECT * FROM ANIMAL"
        cursor.execute( query )
        field_names = [i[0] for i in cursor.description]
        print ( "Fields available in lmtanalysis: " , field_names )

        #build query
        query = "SELECT "
        nbField = len( field_names )
        if ( nbField == 3 ):
            query+="ID,RFID,NAME"
        elif ( nbField == 4 ):
            query+="ID,RFID,NAME,GENOTYPE"
        elif ( nbField == 5 ):
            query+="ID,RFID,NAME,GENOTYPE,IND"
        elif ( nbField == 7 ):
            query+="ID,RFID,NAME,GENOTYPE,AGE,SEX,STRAIN"

        query += " FROM ANIMAL ORDER BY GENOTYPE"
        print ( "SQL Query: " + query )

        cursor.execute( query )
        rows = cursor.fetchall()
        cursor.close()

        self.animalDictionnary.clear()

        for row in rows:

            animal = None
            if ( len( row ) == 3 ):
                animal = Animal( row[0] , row[1] , name=row[2] , conn = conn )
            if ( len( row ) == 4 ):
                animal = Animal( row[0] , row[1] , name=row[2] , genotype=row[3] , conn = conn )
            if ( len( row ) == 5 ):
                animal = Animal( row[0] , row[1] , name=row[2] , genotype=row[3] , user1=row[4] , conn = conn )
            if ( len( row ) == 7 ):
                animal = Animal( row[0] , row[1] , name=row[2] , genotype=row[3] , age=row[4] , sex=row[5] , strain=row[6], conn = conn )


            if ( animal!= None):
                self.animalDictionnary[animal.baseId] = animal
                print ( animal )
            else:
                print ( "Animal loader : error while loading animal.")

    def getAnonymousDetection(self, frame ):
        if frame not in self.anonymousDetection:
            return None

        return self.anonymousDetection[frame]

    def loadAnonymousDetection(self, start = None, end=None ):
        '''
        Load the dictionary of anonymous detection.
        each entry get a list of detection
        clear previous anonymous detection dictionary
        '''
        self.anonymousDetection = {}

        chrono = Chronometer("Load anonymous detection")
        cursor = self.conn.cursor()

        #query = "SELECT FRAMENUMBER, MASS_X, MASS_Y FROM DETECTION WHERE ANIMALID IS NULL"
        query = "SELECT FRAMENUMBER, MASS_X, MASS_Y FROM DETECTION WHERE ANIMALID IS NULL"

        if ( start != None ):
            query += " AND FRAMENUMBER>={}".format(start )
        if ( end != None ):
            query += " AND FRAMENUMBER<={}".format(end )

        print( query )
        cursor.execute( query )

        rows = cursor.fetchall()
        cursor.close()

        for row in rows:
            frameNumber = row[0]
            massX = row[1]
            massY = row[2]
            #data = row[3]
            detection = None
            #filter detection at 0
            if ( massX < 10 ):
                continue

            detection = Detection( massX, massY , lightLoad = True )
            #detection.setMask( Mask( data ) )

            if frameNumber not in self.anonymousDetection:
                self.anonymousDetection[frameNumber] = []

            self.anonymousDetection[frameNumber].append( detection )

        print ( len( self.anonymousDetection ) , " frames containing anonymous detections loaded in {} seconds.".format( chrono.getTimeInS( )) )


    def loadDetection (self , start = None, end=None , lightLoad = False ):
        self.detectionStartFrame = start
        self.detectionEndFrame   = end
        for animal in self.animalDictionnary.keys():
            self.animalDictionnary[animal].loadDetection( start = start, end = end , lightLoad=lightLoad )

    def filterDetectionByInstantSpeed(self, minSpeed, maxSpeed):
        for animal in self.animalDictionnary.keys():
            self.animalDictionnary[animal].filterDetectionByInstantSpeed( minSpeed, maxSpeed )

    def filterDetectionByArea(self, x1, y1, x2, y2 ):
        for animal in self.animalDictionnary.keys():
            self.animalDictionnary[animal].filterDetectionByArea( x1, y1, x2, y2 )

    def filterDetectionByEventTimeLine(self, eventTimeLineVoc ):
        for animal in self.animalDictionnary.keys():
            self.animalDictionnary[animal].filterDetectionByEventTimeLine( eventTimeLineVoc )

    def getGenotypeList(self):

        genotype = {}

        for k in self.animalDictionnary:
            animal = self.animalDictionnary[k]
            genotype[animal.genotype] = True

        return genotype.keys()

    def getAnimalsWithGenotype(self, genotype ):

        resultList= []

        for k in self.animalDictionnary:
            animal = self.animalDictionnary[k]
            if ( animal.genotype == genotype ):
                resultList.append( animal )

        return resultList

        #return [x for x in self.animalDictionnary if x.genotype==genotype ]

    def getNbAnimals(self):
        return len(self.animalDictionnary)

    def getMaxDetectionT(self):
        """
        returns the timepoint of the last detection of all animals
        """
        maxFrame = 0
        for animal in self.getAnimalList():
            maxFrame = max( maxFrame, animal.getMaxDetectionT() )

        return maxFrame

    def frameToTimeTicker(self, x, pos):
        vals= convert_to_d_h_m_s( x )
        experimentTime = "D{0} - {1:02d}:{2:02d}".format( int(vals[0])+1, int(vals[1]), int(vals[2]) )

        realTime = ""
        if x > 0:
            datetime = getDatetimeFromFrame( self.conn , x )
            if datetime != None:
                realTime = "\n" + getDatetimeFromFrame( self.conn , x ).strftime('%d-%b-%Y %H:%M:%S')

        return experimentTime + realTime

    def plotSensorData( self , sensor="TEMPERATURE", show = True , saveFile = None , minValue=0 , autoNight= False):
        """
        plots data for temperature
        """
        print( "plotting sensor data. " , sensor )
        cursor = self.conn.cursor()

        # Check the number of row available in base
        query = "SELECT FRAMENUMBER,"+sensor+" FROM FRAME"
        try:
            cursor.execute( query )
        except:
            print("plot sensor data: can't access data for ", sensor )
            return

        rows = cursor.fetchall()
        cursor.close()

        frameNumberList = []
        sensorValueList = []
        for row in rows:

            sensorValue = row[1]
            if ( sensorValue > minValue ):
                if sensorValue != None and minValue !=None:
                    frameNumberList.append( row[0] )
                    sensorValueList.append( sensorValue )

        fig, ax = plt.subplots( nrows = 1 , ncols = 1 , figsize=( 24, 8 ) )

        ''' set x axis '''
        formatter = ticker.FuncFormatter( self.frameToTimeTicker )
        ax.xaxis.set_major_formatter(formatter)

        ax.tick_params(labelsize=20 )
        ax.xaxis.set_major_locator(ticker.MultipleLocator( 30 * 60 * 60 * 12 ))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator( 30 * 60 * 60 ))

        ax.plot( frameNumberList, sensorValueList, color= "black" , linestyle='-', linewidth=1, label= sensor )
        ax.legend( loc=1 )

        # plot night
        nightTimeLine = EventTimeLine( self.conn, "night" , None, None, None , None )

        mean = 0
        std = 0

        if len( sensorValueList ) > 1 :
            mean = np.mean( sensorValueList )
            std = np.std( sensorValueList )

        for nightEvent in nightTimeLine.eventList:

            ax.axvspan( nightEvent.startFrame, nightEvent.endFrame, alpha=0.1, color='black', ymin= 0, ymax = 1 )
            ax.text( (nightEvent.startFrame+ nightEvent.endFrame)/2 , mean+std , "dark phase" ,fontsize=20,ha='center')

        autoNightList = []
        if autoNight:
            # compute mean value:
            plt.axhline(y=mean, color='r', linestyle='--' )
            ax.text( 0 , mean , "auto night threshold" ,fontsize=20, ha='left' , va='bottom')

            inNight=False
            start = None
            end = None
            for i in range(len(frameNumberList)):
                frame = frameNumberList[i]
                value = sensorValueList[i]
                if value < mean: # night
                    if inNight:
                        continue
                    else:
                        inNight = True
                        start=frame
                else:
                    if inNight:
                        end = frame
                        inNight = False
                        if end-start > 300:
                            autoNightList.append( ( start, end ) )
                        else:
                            print("Skipping very short night phase. (less than 10 seconds)")
                        start = None
                        end = None

            for autoNight in autoNightList:

                ax.axvspan( autoNight[0], autoNight[1], alpha=0.1, color='red', ymin= 0.2, ymax = 0.8 )
                ax.text( (autoNight[0]+autoNight[1])/2 , mean , "auto dark phase" ,fontsize=20,ha='center', color='red')

        plt.xlabel('time')

        if sensor == "TEMPERATURE":
            plt.ylabel('Temperature (C)')
            plt.ylim( 17, 28 )


        if sensor == "SOUND":
            plt.ylabel('Sound level (indice)')

        if sensor == "HUMIDITY":
            plt.ylabel('Humidity %')
            plt.ylim( 0, 100 )

        if sensor == "LIGHTVISIBLE":
            plt.ylabel('Visible light (indice)')

        if sensor == "LIGHTVISIBLEANDIR":
            plt.ylabel('Visible and infrared light (indice)')

        if saveFile !=None:
            print("Saving figure : " + saveFile )
            fig.savefig( saveFile, dpi=100)

        '''
        print("TEST 1")
        import os
        os.startfile( saveFile, 'open')
        print( "TEST 2")
        '''

        if ( show ):
            plt.show()
        plt.close()

        if autoNight:
            return autoNightList


    def plotNight(self, show = True , saveFile = None ):

        fig, ax = plt.subplots( nrows = 1 , ncols = 1 , figsize=( 12, 4 ) )

        nightTimeLine = EventTimeLine( self.conn, "night" , None, None, None , None )
        for nightEvent in nightTimeLine.eventList:

            ax.axvspan( nightEvent.startFrame, nightEvent.endFrame, alpha=0.1, color='black')
            ax.text( (nightEvent.startFrame+ nightEvent.endFrame)/2 , 0.5 , "dark phase" ,fontsize=8,ha='center')

        ''' set x axis '''
        formatter = ticker.FuncFormatter( self.frameToTimeTicker )
        ax.xaxis.set_major_formatter(formatter)
        ax.tick_params(labelsize=6 )
        ax.xaxis.set_major_locator(ticker.MultipleLocator( 30 * 60 * 60 * 12 ))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator( 30 * 60 * 60 ))

        if saveFile !=None:
            print("Saving figure : " + saveFile )
            fig.savefig( saveFile, dpi=100)

        if ( show ):
            plt.show()
        plt.close()

    def buildSensorData(self, file , show=False ):
        print("Build sensor data")
        #self.plotNight( show = show, saveFile = file+"_day night.pdf" )
        self.plotSensorData( sensor = "TEMPERATURE" , minValue = 10, saveFile = file+"_log_temperature.pdf", show = show )
        self.plotSensorData( sensor = "SOUND" , saveFile = file+"_log_sound level.pdf" , show = show )
        self.plotSensorData( sensor = "HUMIDITY" , minValue = 5 , saveFile = file+"_log_humidity.pdf" ,show = show )
        self.plotSensorData( sensor = "LIGHTVISIBLE" , minValue = 40 , saveFile = file+"_log_light visible.pdf", show = show  )
        self.plotSensorData( sensor = "LIGHTVISIBLEANDIR" , minValue = 50 , saveFile = file+"_log_light visible and infra.pdf", show = show  )


    def plotTrajectory( self , show=True, maskingEventTimeLine=None , title = None, scatter = False, saveFile = None ):

        print( "AnimalPool: plot trajectory.")
        nbCols = len( self.getAnimalList() )+1
        fig, axes = plt.subplots( nrows = 1 , ncols = nbCols , figsize=( nbCols*4, 1*4 ) , sharex='all', sharey='all'  )

        if title==None:
            title="Trajectory of animals"

        #draw all animals
        axis = axes[0]
        legendList=[]
        for animal in self.getAnimalList():

            print ("Compute trajectory of animal " + animal.name )
            xList, yList = animal.getTrajectoryData( maskingEventTimeLine )
            print ("Draw trajectory of animal " + animal.name )
            if scatter == True:
                axis.scatter( xList, yList, color= animal.getColor() , s=1 , linewidth=1, alpha=0.05, label= animal.RFID )
                legendList.append( mpatches.Patch(color=animal.getColor(), label=animal.RFID) )
            else:
                axis.plot( xList, yList, color= animal.getColor() , linestyle='-', linewidth=1, alpha=0.5, label= animal.RFID )

        axis.legend( handles = legendList , loc=1 )
        axis.set_xlim(90, 420)
        axis.set_ylim(-370, -40)

        #draw separated animals
        for animal in self.getAnimalList():
            axis = axes[self.getAnimalList().index(animal)+1]

            legendList=[]

            print ("Compute trajectory of animal " + animal.name )
            xList, yList = animal.getTrajectoryData( maskingEventTimeLine )
            print ("Draw trajectory of animal " + animal.name )
            if scatter == True:
                axis.scatter( xList, yList, color= animal.getColor() , s=1 , linewidth=1, alpha=0.05, label= animal.RFID )
                legendList.append( mpatches.Patch(color=animal.getColor(), label=animal.RFID) )
            else:
                axis.plot( xList, yList, color= animal.getColor() , linestyle='-', linewidth=1, alpha=0.5, label= animal.RFID )

            axis.legend( handles = legendList , loc=1 )

        fig.suptitle( title )

        if saveFile !=None:
            print("Saving figure : " + saveFile )
            fig.savefig( saveFile, dpi=100)

        if ( show ):
            plt.show()
        plt.close()

    def showMask(self, t ):
        '''
        show the mask of all animals in a figure
        '''

        fig, ax = plt.subplots()
        ax.set_xlim(90, 420)
        ax.set_ylim(-370, -40)

        for animal in self.getAnimalList():
            mask = animal.getBinaryDetectionMask( t )
            mask.showMask( ax=ax )

        plt.show()

    def getParticleDictionnary(self , start, end ):
        '''
        return the number of particle per frame
        '''

        query = "SELECT FRAMENUMBER, NUMPARTICLE FROM FRAME WHERE FRAMENUMBER>={} AND FRAMENUMBER<={}".format( start, end )

        print ( "SQL Query: " + query )

        cursor = self.conn.cursor()
        cursor.execute( query )
        rows = cursor.fetchall()
        cursor.close()

        particleDictionnary = {}

        for row in rows:

            particleDictionnary[ row[0] ] = row[1]

        return particleDictionnary


    def getDetectionTable(self):
        """
        Returns detections as pandas table for all animals in pool.

        * adds location also in cm
        * adds time column in pandas timedelta
        * adds column to indicate detections in center region

        Returns:
            pd.DataFrame: detections as pandas table
        """

        data = defaultdict(list)
        for animal in self.getAnimalList():
            for frame, detection in animal.detectionDictionnary.items():
                data["RFID"]         .append(f"{animal.name}_{animal.RFID}")
                data["name"]         .append(f"{animal.name}")
                data["genotype"]     .append(f"{animal.genotype}")
                data['frame']        .append(frame)
                data['sec']          .append(frame / oneSecond)
                data['x']            .append(detection.massX)
                data['y']            .append(detection.massY)
                data['z']            .append(detection.massZ)

        df = pd.DataFrame(data)


        df["x_cm"] = (df.x - cornerCoordinates50x50Area[0][0]) / (cornerCoordinates50x50Area[1][0] - cornerCoordinates50x50Area[0][0]) * ARENA_SIZE
        df["y_cm"] = (df.y - cornerCoordinates50x50Area[1][1]) / (cornerCoordinates50x50Area[2][1] - cornerCoordinates50x50Area[1][1]) * ARENA_SIZE

        df[f"in_arena_center"] = (df["x_cm"] > CENTER_MARGIN) & \
                                 (df["y_cm"] > CENTER_MARGIN) & \
                                 (df["x_cm"] < (ARENA_SIZE - CENTER_MARGIN)) & \
                                 (df["y_cm"] < (ARENA_SIZE - CENTER_MARGIN))

        df.insert(3, "time", pd.to_timedelta(df.sec, unit="s"))

        return df.sort_values("time").reset_index(drop=True)


    def getSingleEventTable(self, event_name):
        """
        Returns pandas table containing all found events for given event name'
            * Primary mouse' meta data
            * Event start time
            * Event end time
            * Event duration

        Args:
            event_name (str): Event name e. g. Rearing

        Returns:
            DataFrame
        """
        data = defaultdict(list)
        for animal in self.getAnimalList():
            with mute_prints():
                eventTimeLine = EventTimeLine(self.conn,
                                                event_name,
                                                idA=animal.baseId,
                                                minFrame=self.detectionStartFrame,
                                                maxFrame=self.detectionEndFrame)

            for e in eventTimeLine.getEventList():
                data["RFID"]         .append(f"{animal.name}_{animal.RFID}")
                data["name"]         .append(f"{animal.name}")
                data["genotype"]     .append(f"{animal.genotype}")
                data["event_name"]   .append(event_name)
                data["start_sec"]    .append(e.startFrame / oneSecond)
                data["end_sec"]      .append(e.endFrame   / oneSecond)
                data["duration"]     .append(e.duration() / oneSecond)

        df = pd.DataFrame(data)
        df.insert(2, "time", pd.to_timedelta(df["start_sec"], unit="s"))

        return df.sort_values("time").reset_index(drop=True)


    def getAllEventsTable(self):
        """
        Returns pandas table containing all found events for all found event types'
            * Primary mouse' meta data
            * Events' start time
            * Events' end time
            * Events' duration

        Returns:
            DataFrame
        """
        with mute_prints():
            all_event_names = getAllEvents(connection=self.conn)

        event_table =  pd.concat([self.getSingleEventTable(event_name)
                                    for event_name in all_event_names]
                                , axis=0)
        return event_table.sort_values("time").reset_index(drop=True)


