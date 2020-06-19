'''
Created on 6 sept. 2017

@author: Fab
'''

import sys
import math
import time
import sqlite3
import datetime
import contextlib


class DummyFile(object):
    def write(self, x): pass

@contextlib.contextmanager
def mute_prints():
    # https://stackoverflow.com/questions/2828953/silence-the-stdout-of-a-function-in-python-without-trashing-sys-stdout-and-resto
    save_stdout = sys.stdout
    sys.stdout = DummyFile()
    yield
    sys.stdout = save_stdout

def getAllEvents(connection=None, file=None, ):
    """Returns names of all events present in database

    Args:
        file (str, optional): The path of the sqlite database. Defaults to None.
        connection (sqlite conn, optional): the sqlite connection. Defaults to None.

    Raises:
        ValueError: if , none of args have been supplied

    Returns:
        list(str): names of all events present in database
    """

    if not (file or connection):
        raise ValueError("Enter file or connection")
    elif file:
        connection = sqlite3.connect(file)

    print( "Loading event names:", end="")
    c = connection.cursor().execute( "SELECT name FROM event GROUP BY name" )
    all_rows = c.fetchall()
    print(f"{len(all_rows)} Done.")

    return [row[0] for row in all_rows]

def level( data ):
    ''' similar to level in R '''
    dico = {}
    for entry in data:
        dico[entry]=True
    return sorted( dico.keys( ) )


def pixelToCm( nbPixel ):
    return nbPixel * 10 / 57

def getFrameInput( text ):

    entryOk = False
    t = 0
    while not entryOk:
        try:
            t = 0
            r = input( text + " : ")

            if ( len( r ) == 0 ):
                return None
            answers  = r.split( sep=" ")

            for answer in answers:
                if answer.isdigit():
                    t+= float( answer )

                if answer.endswith("d"):
                    t+= float( answer[:-1] ) * 30 * 60 * 60 * 24

                if answer.endswith("h"):
                    t+= float( answer[:-1] ) * 30 * 60 * 60

                if answer.endswith("m"):
                    t+= float( answer[:-1] ) * 30 * 60

                if answer.endswith("s"):
                    t+= float( answer[:-1] ) * 30

                if answer.endswith("f"):
                    t+= float( answer[:-1] )
        except:
            print("Error in entry.")
            continue
        entryOk = True

    t = int(t)
    print("Entry (in frame) : " + str( t ) )
    return t


def getMinTMaxTAndFileNameInput():

    print ("Enter time information in frame. You can also set in days, hour, minutes")
    print ("valid entries: 100, 1d, 1.5d, 23.5h, 1d 2h 3m 4s 5f")


    tmin = getFrameInput("Starting t")
    tmax = getFrameInput("Ending t")

    text_file_name = input("Enter file name to save data (.txt will be added) : ")
    text_file_name = text_file_name+".txt"
    text_file = open ( text_file_name, "w")

    return tmin,tmax,text_file


def getMinTMaxTInput():

    print ("Enter time information in frame. You can also set in days, hour, minutes")
    print ("valid entries: 100, 1d, 1.5d, 23.5h, 1d 2h 3m 4s 5f")

    tmin = getFrameInput("Starting t")
    tmax = getFrameInput("Ending t")

    return tmin,tmax


def getFileNameInput():

    text_file_name = input("File name : ")
    text_file_name = text_file_name+".txt"
    text_file = open ( text_file_name, "w")

    return text_file

def convert_to_d_h_m_s( frames ):
    """Return the tuple of days, hours, minutes and seconds."""
    #seconds = frames / 30
    seconds, f = divmod( frames, 30)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    return days, hours, minutes, seconds, f

def d_h_m_s_toText( t ):
    """Return the d h m s f as text"""
    return "{} days {} hours {} minutes {} seconds {} frames".format( t[0],t[1],t[2],t[3],t[4] )

def getDistanceBetweenPointInPx( x1 , y1, x2, y2 ):
    ''' return the distance between two points in pixel '''
    distance = math.hypot( x1 - x2, y1 - y2 )
    return distance

def getNumberOfFrames(file):
    """Return the number of frame for a given experiment"""
    connection = sqlite3.connect( file )
    c = connection.cursor()
    query = "SELECT MAX(FRAMENUMBER) FROM FRAME";
    c.execute( query )
    numberOfFrames = c.fetchall()

    return int(numberOfFrames[0][0])

def getStartInDatetime(file):
    """Return the start of a given experiment in a datetime format"""
    connection = sqlite3.connect( file )
    c = connection.cursor()
    query = "SELECT MIN(TIMESTAMP) FROM FRAME";
    c.execute( query )
    rows = c.fetchall()
    for row in rows:
        start = datetime.datetime.fromtimestamp(row[0]/1000)

    return start

def getEndInDatetime(file):
    """Return the end of a given experiment in a datetime format"""
    connection = sqlite3.connect( file )
    c = connection.cursor()
    query = "SELECT MAX(TIMESTAMP) FROM FRAME";
    c.execute( query )
    rows = c.fetchall()
    for row in rows:
        end = datetime.datetime.fromtimestamp(row[0]/1000)

    return end

def getDatetimeFromFrame(connection, frame):
    c = connection.cursor()
    query = "SELECT TIMESTAMP FROM FRAME WHERE FRAMENUMBER = {}".format(frame);

    c.execute( query )
    rows = c.fetchall()

    if (len(rows) <= 0):
        print ("The entered framenumber is out of range")
        return None

    else:
        for row in rows:
            targetDate = datetime.datetime.fromtimestamp(row[0]/1000)

    return targetDate

def recoverFrame(file, MyDatetime):
    """
    Return the clothest FRAMENUMBER from a given datetime
    The datetime must have this format: dd-mm-YYYY hh:mm:ss
    """
    connection = sqlite3.connect( file )
    c = connection.cursor()

    # get timedate of 1st and last frame

    query = "SELECT FRAMENUMBER, TIMESTAMP FROM FRAME WHERE FRAMENUMBER=1";
    c.execute( query )
    all_rows = c.fetchall()
    startTS = int ( int ( all_rows[0][1] ) / 1000 )
    startDate = datetime.datetime.fromtimestamp( startTS ).strftime('%d-%m-%Y %H:%M:%S')

    query = "SELECT max(FRAMENUMBER) FROM FRAME";
    c.execute( query )
    all_rows = c.fetchall()
    maxFrame = all_rows[0][0]

    query = "SELECT FRAMENUMBER, TIMESTAMP FROM FRAME WHERE FRAMENUMBER={}".format( maxFrame );
    c.execute( query )
    all_rows = c.fetchall()
    endTS = int ( int ( all_rows[0][1] ) / 1000 )
    endDate = datetime.datetime.fromtimestamp( endTS ).strftime('%d-%m-%Y %H:%M:%S')

    #print ( file )
    #print ( "Start date of record : " + startDate )
    #print ( "End date of record : " + endDate )

    #print(datetime.utcfromtimestamp(startTS).strftime('%Y/%m/%d %H:%M:%S'))
    print(MyDatetime)

    timeStamp = time.mktime(datetime.datetime.strptime(MyDatetime, "%Y-%m-%d %H:%M:%S").timetuple()) * 1000

    print( "TimeStamp * 1000 is : " + str( timeStamp ) )

    print( "Searching closest frame in database....")

    query = "SELECT FRAMENUMBER, TIMESTAMP FROM FRAME WHERE TIMESTAMP>{} AND TIMESTAMP<{}".format( timeStamp - 10000 , timeStamp + 10000 );

    c.execute( query )
    all_rows = c.fetchall()

    closestFrame = 0
    smallestDif = 100000000

    for row in all_rows:

        ts = int ( row[1] )
        dif = abs( ts - timeStamp )
        if ( dif < smallestDif ):
            smallestDif = dif
            closestFrame = int (row[0] )

    print( "Closest Frame in selected database is: " + str( closestFrame ) )
    print( "Distance to target: " + str( smallestDif ) + " milliseconds")
    return closestFrame