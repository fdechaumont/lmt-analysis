'''
Created by Nicolas Torquet at 11/03/2026
nicolas.torquet@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - PHEN-ICS
PHEN-ICS, CNRS UAR 2062, INSERM U66, Université de Strasbourg
Code under GPL v3.0 licence
'''

from lmtanalysis.FileUtil import getFilesToProcess
import sqlite3

def getFileName(file):
    return file.split('.sqlite')[0].split('\\')[-1].split("/")[-1]

def checkTimestamp(file):
    '''
    :param file: file path
    :return: timestamp timeline error
    '''
    print(f"Checking Timestamp Error of {getFileName(file)}")
    connection = sqlite3.connect(file)
    cursor = connection.cursor()
    query = "select FRAMENUMBER, TIMESTAMP from FRAME ORDER By FRAMENUMBER"
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    timestamp_error_list = []
    for row in rows:
        if row[0] > 1:
            if row[1] < current_timestamp:
                timestamp_error_list.append((row[0], row[1]))
            else:
                current_timestamp = row[1]
        else:
            current_timestamp = row[1]

    if len(timestamp_error_list) > 0:
        print("Error: timestamp back in time during experient!")
        return timestamp_error_list
    else:
        print("No timestamp error during the experiment")


if __name__ == '__main__':
    files = getFilesToProcess()
    errorDico = {}
    for file in files:
        errorDico[getFileName(file)] = checkTimestamp(file)
