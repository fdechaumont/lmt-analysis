'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3

from lmtanalysis.BuildDataBaseIndex import buildDataBaseIndex
from tkinter.filedialog import askopenfilename

if __name__ == '__main__':
    
    print("Code launched.")
    
    #file = "/Users/elodie/Documents/2016_09_shank2_exp/2016_10_exp_tracking/2017_03_lg_term_rec_group/2017_05_16_test_48h/test_24h/20170516_6559/20170516_Experiment 6559_test.sqlite"
    
    #file = "/Users/elodie/ownCloud/phenoRT/2017_03_17/Experiment 2082_4 petites/Experiment 2082_test.sqlite"
    
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    
    for file in files:
        connection = sqlite3.connect( file )
    
        buildDataBaseIndex( connection , force=True )
        


    
    