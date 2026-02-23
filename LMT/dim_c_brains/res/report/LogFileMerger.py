'''
Created on 12 févr. 2025

@author: Fab
'''
import os
import datetime as dt

class LogFileMerger(object):
    '''
    merges files of same experiment, same trial
    '''


    def __init__(self, inputFiles, outFolder ):
        
        print("Merging logs...")
        self.outFolder = outFolder
        filesOk = []
        
        for file in inputFiles:
            basename = os.path.basename(file)
            if "merged" in basename:
                print(f"ignoring file {file}")
                continue
            print(f"adding file {file}")
            filesOk.append( file )
                
        self.inputFiles = filesOk
        self.mergedFiles = []
        
        self.mergeDataFiles()
        
        
    def getMergedFiles( self ):
        return self.mergedFiles

        
    def getNameAndTrial(self , file ):
        
        basename = os.path.basename(file)
        s = basename.split("-")
        experimentName = s[0]
        experimentTrial = s[1]
        return experimentName, experimentTrial
        
    def getDateTime(self , line ):        
        datetime = line[0:23]
        datetime = dt.datetime.strptime(datetime,'%Y-%m-%d %H:%M:%S.%f')
        return datetime
    
    def getStartDateTimeFile(self , file ):
        
        print(f"Searching for start datetime for file: {file}...")
        
        with open( file ) as f:
            rawlines = f.readlines()
        
        self.lines = []
        for line in rawlines:
            # find first datetime
            try:
                dt = self.getDateTime( line )
                return dt
            except:                
                pass

    def merge( self, files, experimentName, experimentTrial ):
        
        if len( files ) == 0:
            print ("no files to merge, skip")
            return
            
        mergedFile = f"{self.outFolder}{experimentName}-{experimentTrial}-merged.log.txt"
        self.mergedFiles.append( mergedFile )
        print( f"Merging {files} to {mergedFile}")
        
        fileDateTimeDic = {}
        
        # order file by datetime in the logs
        
        for file in files:            
            fileDateTimeDic[ file ] = self.getStartDateTimeFile ( file )
            print ( file, fileDateTimeDic[ file ] )  
        
        fileList = []
        print("Merging in that order:")
        for item in sorted( fileDateTimeDic.items() , key = lambda x:x[1] ):
            print( item[0], item[1] )
            fileList.append( item[0] )
        
        # concat files.
            
        with open( mergedFile, 'w') as outfile:
            for fname in fileList:
                with open(fname) as infile:
                    for line in infile:
                        outfile.write(line)
            
        
        
    def mergeDataFiles(self):
        
        experimentDic = {}        
        
        for file in self.inputFiles:
        
            experimentName, experimentTrial = self.getNameAndTrial( file )
            experimentDic[experimentName,experimentTrial]="exists"
            
        for k in experimentDic:
            print("Merging...")
            print( k )
            fileListToMerge = []
            for file in self.inputFiles:
                experimentName, experimentTrial = self.getNameAndTrial( file )
                if k[0] == experimentName and k[1] == experimentTrial:
                    fileListToMerge.append( file )
                    
            self.merge( fileListToMerge, k[0], k[1] )
                 
            
            
            
        
            
        
        
        
        
        
        
    '''
        def mergeDataFiles( files ):
        
    # extract experiment names:
    for file in files:
        
        s = file.split("-")
        experimentName = s[0]
        experimentTrial = s[1] 
    '''
        
        