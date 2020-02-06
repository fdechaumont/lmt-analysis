'''

@author: Fab

Loads log of process performed on a lmtanalysis

CREATE TABLE "LOG" (
    `id`    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    `process`    TEXT,
    `version`    TEXT,
    `date`    TEXT,
    `tmin`    INTEGER,
    `tmax`    INTEGER
)

test in: 2478 USV event

'''
from datetime import date, datetime
from tabulate import tabulate

class Log:
    
    def __init__(self, id, process, version, date, tmin, tmax ):        
        
        self.id = id
        self.process = process
        self.version = version
        self.date = date
        self.tmin = tmin
        self.tmax = tmax
    
class TaskLogger:

    def __init__(self, connection ):        
        self.logList = []
        self.conn = connection
        
        self.createLogTableIfNeeded()
        
        self.loadLog()
        
    def createLogTableIfNeeded(self):
        
        try:
            cursor = self.conn.cursor()
            query = "SELECT ID, PROCESS, VERSION, DATE, TMIN, TMAX FROM LOG"
            cursor.execute( query )
            cursor.close()
        except:
            #create table
            print("Log table does not exists, creating Log table")
            cursor = self.conn.cursor()
            query = "CREATE TABLE LOG ( id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, process TEXT, version TEXT,date TEXT,tmin INTEGER, tmax INTEGER)"
            cursor.execute( query )
            self.conn.commit()
            cursor.close()
    
    def loadLog(self):

        #print ( self.__str__(), ": Loading log" )

        self.logList.clear()
        cursor = self.conn.cursor()
        query = "SELECT ID, PROCESS, VERSION, DATE, TMIN, TMAX FROM LOG"
            
        #print( query )
        cursor.execute( query )
        
        rows = cursor.fetchall()
        cursor.close()    
        
        for row in rows:
            id = row[0]
            process = row[1]
            version = row[2]
            date = row[3]
            tmin = row[4]
            tmax = row[5]
            
            log = Log( id, process, version, date, tmin, tmax )
            
            self.logList.append( log )
        
        #print ( self.__str__(), " ", " {} log line loaded: " )

    def listLog(self):
        
        header = [ "ID", "Process", "version", "date Y-M-D H:M:S", "tmin", "tmax" ]
        data =[]
    
        for l in self.logList:
    
            data.append( [ l.id, l.process, l.version, l.date , l.tmin, l.tmax ])
    
        print ( tabulate( data, header, tablefmt='orgtbl') )

    def addLog(self, process, version='0', date=None, tmin=0, tmax=-1 ):

        if date==None:
            
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor = self.conn.cursor()
        query = "INSERT INTO LOG( process,version,date,tmin,tmax) VALUES ( '{process}','{version}','{date}','{tmin}','{tmax}' );".format( process=process, version=version, date=date, tmin=tmin, tmax=tmax )
                    
        print( query )
        cursor.execute( query )
        self.conn.commit()
        cursor.close()    
        
        self.loadLog()

    


