'''
Created on 15 December 2021

@author: Elodie
'''
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Event import *

from lmtanalysis.FileUtil import getFilesToProcess, getCsvFileToProcess

import pandas as pd


def process(file, dataframe, expListToCheck, expListToCheckForPause, expListToCheckForRfid):
    print(file)
    #open the database file
    connection = sqlite3.connect(file)
    c = connection.cursor()


    pool = AnimalPool()
    pool.loadAnimals(connection)
    if len(pool.animalDictionnary.keys()) > 1:
        print('More than one animal in this experiment. Please check.')
        expListToCheck.append(file)

    elif len(pool.animalDictionnary.keys()) == 1:
        query = "SELECT PAUSED FROM FRAME WHERE PAUSED = '1'";
        c.execute(query)
        rows = c.fetchall()
        print('existing paused frames: ', rows)

        if len(rows) == 0:
            # get the RFID of the tracked animal in the database
            rfidDatabase = pool.animalDictionnary[1].RFID
            print('RFID database: ', rfidDatabase)

            #attribute the corresponding frame number to be changed
            count = 0
            for rfidTable in dataframe['RFID']:
                #print('RFID table: ', rfidTable)
                if rfidTable in rfidDatabase:
                    print('RFID: ', rfidTable, rfidDatabase)
                    frameToPause = dataframe[dataframe['RFID'] == rfidTable]['paused_frame'].item()
                    print('paused frame: ', frameToPause)
                    count = 1

            if count == 0:
                print('This RFID is not referenced in the table.')
                print(file, rfidDatabase)
                expListToCheckForRfid.append(file)

            else:
                #modify the PAUSED status in the database for the corresponding framenumber
                query = "UPDATE FRAME SET PAUSED = '1' WHERE FRAMENUMBER = {}".format(frameToPause);
                c.execute(query)
        else:
            print('Paused frames already exist; please check')
            expListToCheckForPause.append(file)

        connection.commit()
        c.close()
        connection.close()


def processAll():
    #choose the sqlite files to process
    files = getFilesToProcess()

    #choose the file containing the frame numbers that should be paused
    refFile = getCsvFileToProcess()
    #open the file containing the frame number that should be set on pause.
    df = pd.read_csv(refFile, sep=';')

    expListToCheck = []
    expListToCheckForPause = []
    expListToCheckForRfid = []

    chronoFullBatch = Chronometer("Full batch")

    if (files != None):

        for file in files:
            print("Processing file", file)
            process(file, df, expListToCheck, expListToCheckForPause, expListToCheckForRfid)

    chronoFullBatch.printTimeInS()
    print('Experiment files to be checked for multiple animals: ')
    print(expListToCheck)
    print('Experiment files to be checked for paused frames: ')
    print(expListToCheckForPause)
    print('Experiment files to be checked for RFID: ')
    print(expListToCheckForRfid)
    print("*** ALL JOBS DONE ***")


if __name__ == '__main__':
    print("Code launched.")
    """This code allows to set to pause a specific frame within a database.
    It is meant to be used on single tracked animals, for single object exploration for instance.
    """
    print("This code allows to set to pause a specific frame within a database. It is meant to be used on single tracked animals, for single object exploration for instance.")
    processAll()
