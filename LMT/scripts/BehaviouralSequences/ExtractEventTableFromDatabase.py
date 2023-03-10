'''
Created on 17 Feb 2022

@author: Elodie
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.FileUtil import *
from lmtanalysis.Util import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.BehaviouralSequencesUtil import exclusiveEventList, exclusiveEventsLabels, sexList, genoList
import pandas as pd
import seaborn as sns

if __name__ == '__main__':

    pd.set_option("display.max_rows", None, "display.max_columns", None)

    print("Code launched.")

    #Extract the event table of the database and export it as csv
    files = getFilesToProcess()

    fileName = 'exclusiveEventTable'

    for file in files:
        print(file)
        connection = sqlite3.connect(file)
        pool = AnimalPool()
        pool.loadAnimals(connection)
        
        genotype = []

        for animal in pool.animalDictionary.keys():
            geno = pool.animalDictionary[animal].genotype
            genotype.append(geno)

        genoPair = ('{}_{}'.format(genotype[0], genotype[1]))
        genoPair = genoPair.replace('/', '')

        c = connection.cursor()
        query = "SELECT * FROM EVENT WHERE NAME LIKE '%exclusive%' "
        c.execute(query)

        db_df = pd.read_sql_query(query, connection)
        db_df.to_csv('{}_{}_exp_{}.csv'.format(fileName, genoPair, file[-11:-7]), sep=';', index=False)

        connection.commit()
        c.close()
        connection.close()


    print('Job done.')
