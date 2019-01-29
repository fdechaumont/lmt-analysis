'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3

from lmtanalysis.BuildDataBaseIndex import buildDataBaseIndex
from tkinter.filedialog import askopenfilename
from lmtanalysis.FileUtil import getFilesToProcess

if __name__ == '__main__':
    
    print("Code launched.")
    
    files = getFilesToProcess()
    #files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    
    for file in files:
        connection = sqlite3.connect( file )
    
        buildDataBaseIndex( connection , force=True )
        


    
    