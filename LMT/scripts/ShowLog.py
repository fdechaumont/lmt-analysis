'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3

from tkinter.filedialog import askopenfilename
from lmtanalysis.TaskLogger import TaskLogger

def process( file ):

    print ("**********************")
    print(file)
    print ("**********************")
    connection = sqlite3.connect( file )        
        
    t = TaskLogger( connection )
    t.listLog()
  

if __name__ == '__main__':
    
    print("Code launched.")
     
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    
    for file in files:

        process( file )
        
    print( "*** ALL JOBS DONE ***")
        
        