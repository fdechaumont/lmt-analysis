'''
Created by Nicolas Torquet at 07/02/2023
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''

from lmtanalysis.Event import *
from lmtanalysis.FileUtil import getFilesToProcess, getJsonFileToProcess


def addColumns(file):
    print(file)

    connection = sqlite3.connect(file)

    c = connection.cursor()
    # Check if columns already exist
    check = "PRAGMA table_info(ANIMAL)"
    c.execute(check)
    rows = c.fetchall()
    columnNames = []
    for row in rows:
        columnNames.append(row[1])

    if 'AGE' not in columnNames:
        query = "ALTER TABLE ANIMAL ADD AGE TEXT";
        c.execute(query)
    if 'SEX' not in columnNames:
        query = "ALTER TABLE ANIMAL ADD SEX TEXT";
        c.execute(query)
    if 'STRAIN' not in columnNames:
        query = "ALTER TABLE ANIMAL ADD STRAIN TEXT";
        c.execute(query)
    if 'SETUP' not in columnNames:
        query = "ALTER TABLE ANIMAL ADD SETUP TEXT";
        c.execute(query)
    if 'TREATMENT' not in columnNames:
        query = "ALTER TABLE ANIMAL ADD TREATMENT TEXT";
        c.execute(query)
    connection.commit()
    c.close()
    connection.close()


def updateField(file, jsonFile):
    with open(jsonFile) as json_data:
        fieldsToUpdate = json.load(json_data)
    '''
    Take a dictionary: First key: animal (rfid number), then keys are the columns, values are data to store for that field
    ex of the fieldsToUpadte dict:
    {
        "001039552597":
            {
                "genotype": "wt",
                "sex": "female",
                "strain": "C57BL6J",
                "treatment": "saline"
            },
        "001039552595":
            {
                "genotype": "ko",
                "age": "6mo",
                "sex": "female",
                "strain": "C57BL6J",
                "treatment": "saline"
            }
    }
    '''
    print(file)

    connection = sqlite3.connect(file)
    c = connection.cursor()
    for mouse in fieldsToUpdate.keys():
        query = "UPDATE ANIMAL SET "
        for field in fieldsToUpdate[mouse].keys():
            if (field != 'file') and (field != 'group'): # these two variables are not in sqlite databases
                if field == 'animal':
                    field = 'ID'
                query += f"{field} = '{fieldsToUpdate[mouse][field]}', "
        query = query [0:-2]    # to remove the last comma
        query += f" WHERE ANIMAL.RFID = '{mouse}'"
        print(query)
        try:
            c.execute(query)
        except:
            print("There was a problem when trying to modify database fields")
    connection.commit()
    c.close()
    connection.close()



def processAddColumns():
    files = getFilesToProcess()

    chronoFullBatch = Chronometer("Full batch")

    if (files != None):

        for file in files:
            print("Processing file", file)
            addColumns(file)

    chronoFullBatch.printTimeInS()
    print("*** ALL JOBS DONE ***")


def processUpdateFields():
    files = getFilesToProcess()

    jsonFile = getJsonFileToProcess()

    chronoFullBatch = Chronometer("Full batch")

    if (files != None):
        for file in files:
            print("Processing file", file)
            updateField(file, jsonFile)

    chronoFullBatch.printTimeInS()
    print("*** ALL JOBS DONE ***")


def processAddColumnsAndUpdateFields():
    files = getFilesToProcess()

    jsonFile = getJsonFileToProcess()

    chronoFullBatch = Chronometer("Full batch")

    if (files != None):
        for file in files:
            print("Processing file", file)
            addColumns(file)
            updateField(file, jsonFile)

    chronoFullBatch.printTimeInS()
    print("*** ALL JOBS DONE ***")


if __name__ == '__main__':
    print("Code launched.")

    while True:

        question = "Do you want to:"
        question += "\n\t [1] add columns in SQLite databases?"
        question += "\n\t [2] update animal tables of SQLite databases from a json file?"
        question += "\n\t [3] add columns and update animal tables of SQLite databases from a json file?"
        question += "\n"
        answer = input(question)

        if answer == "1":
            print("********** Add columns **********")
            processAddColumns()
            break


        if answer == "2":
            print("********** Update animal tables of SQLite databases **********")
            processUpdateFields()
            break

        if answer == "3":
            print("********** Add columns and update animal tables of SQLite databases **********")
            processAddColumnsAndUpdateFields()
            break