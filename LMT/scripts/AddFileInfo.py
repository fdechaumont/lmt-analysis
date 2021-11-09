'''
Created on 24 Septembre 2021

@author: Elodie
'''


from lmtanalysis.Event import *


from lmtanalysis.FileUtil import getFilesToProcess


def process( file ):

    print(file)
    #extract the name of the individual from the name of the file; adjust position!!!
    '''print('ind name: ', file[36:39])
    ind = str(file[36:39])'''
    '''print('ind name: ', file[53:56])
    ind = str(file[53:56])'''
        

    connection = sqlite3.connect( file )
    
    c = connection.cursor()
    '''query = "UPDATE ANIMAL SET GENOTYPE = 'WT'";
    c.execute(query)'''
    query = "UPDATE ANIMAL SET AGE = '6mo'";
    c.execute( query )
    query = "UPDATE ANIMAL SET SEX = 'female'";
    c.execute( query )
    query = "UPDATE ANIMAL SET STRAIN = 'SHANK3'";
    c.execute( query )
    query = "UPDATE ANIMAL SET SETUP = '1'";
    c.execute(query)
    '''query = "UPDATE ANIMAL SET NAME = '{}'".format(ind);
    c.execute(query)'''
    """query = "UPDATE ANIMAL SET RFID = '{}'".format(ind);
    c.execute(query)"""

    connection.commit()
    c.close()
    connection.close()

    

def processAll():
    
    
    files = getFilesToProcess()

    chronoFullBatch = Chronometer("Full batch" )    
        
    if ( files != None ):
    
        for file in files:
                print ( "Processing file" , file )
                process( file )
        
    chronoFullBatch.printTimeInS()
    print( "*** ALL JOBS DONE ***")

if __name__ == '__main__':
    
    print("Code launched.")
    processAll()
    