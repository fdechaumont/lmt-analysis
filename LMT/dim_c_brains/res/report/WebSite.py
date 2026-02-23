'''
Created on 5 févr. 2025

@author: Fab
'''

import os

from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from dim_c_brains.res.report.Experiment import ExperimentManager
import ftplib
from glob import glob
import shutil
import os.path
from random import randint



class WebSite(object):
    '''
    manage static website generation
    '''

    def __init__(self, templateFolder, outFolder, defaultWebSiteFolder=None, cacheFolder=None, passFile = None ):

        self.name =""
        self.reportList = []
        self.experimentManager = ExperimentManager() 
        self.cacheFolder = cacheFolder
        self.templateFolder = templateFolder
        self.outFolder = outFolder
        self.defaultWebSiteFolder=defaultWebSiteFolder
        self.passFile = passFile
    
    def moveReportToPosition(self , report, targetIndex ):
        # find report
        self.experimentManager.getExperimentWithReport( report )
        
        
    def moveReport(self , source, target, experimentName ):
        self.experimentManager.moveReport( source, target, experimentName )
        
    def addReport(self , report , index=None ):
        
        self.experimentManager.addReport( report, index )
        

    def addReports(self , reports ):
        
        for report in reports:
            self.experimentManager.addReport( report )
        
    def insertReport(self , report, index ):        
        
        self.experimentManager.insertReport( report, index )

    def nowStr(self):    
        return datetime.now().strftime("%d %b %Y %H:%M:%S")
    
    def miniCard(self , title, content, style="primary" ):
        # primary, success, danger, warning
        return self.env.get_template( "miniCard.html").render( title = title, content = content , style=style )
    
    def collapse(self , t1 , t2):
  
        html="""<style>
        
        #collDesc a:link, a:visited {
          text-decoration: none;
          display: inline-block;
          color:inherit;          
        }

        #collDesc a:hover, a:active {
          text-decoration: underline;
        }
        </style>"""
  
        
        style2 = """
              background-color: lightgray;
              padding: 10px 30px;
              border-radius: 10px;
              box-shadow: 10px 5px 5px gray;
              border-style: solid;
              border-width: thin;
        """      
        # class="collapsed"
        id = "id"+str( randint(0,1000000) )
        html+=f"""<div id="collDesc"><span><i class="fas fa-book-open"></i></span><a  href="#" data-bs-toggle="collapse" data-bs-target="#collapseLayouts{id}" aria-expanded="false" aria-controls="collapseLayouts{id}"> {t1}</a></div>"""
        html+=f"""<div class="collapse" style="{style2}" id="collapseLayouts{id}" aria-labelledby="headingOne" data-bs-parent="#sidenavAccordion">{t2}</div>"""
        return html
  
    
    def renderReportList(self , reportList, templateFolder , outFolder, experimentName, showMenuItem=True ):
        
        content =""
        
        '''
        if showMenuItem:
            # list of report
            content+="""<div style="
            font-size:small;            
            ">"""
            #content+=f"<h1>{experimentName}:</h1>"
            content+=f"<h3>Quick jump to sections:</h3>"
            content+="<ul>"
            for report in reportList:
                i = reportList.index( report )
                content+=f"<li><a href='#report{i}' style='text-decoration:none;color:inherit;'>{report.title}</a></li>"
            content+="</ul>"
            content+="</div>"
        '''
        
        if showMenuItem:
            
            t1 = "Quick jump to sections"
            
            t2 = ""
            t2+="<ul>"
            for report in reportList:
                i = reportList.index( report )
                t2+=f"<li><a href='#report{i}' style='text-decoration:none;color:inherit;'>{report.title}</a></li>"
            t2+="</ul>"
            content+=self.collapse( t1 , t2 )
        
         
        
        inRow = False
        for report in reportList:                
            
            number=reportList.index( report )
            
            if report.template.lower() != "minicard.html": # fixme: if the anchor is present, it generates a line break
                content+= f"<a name='report{number}'></a>"
            
            if report.template.lower() == "minicard.html":
                
                if inRow == False:
                    content+="<div class='row'>"
                    inRow=True
                content+= self.miniCard( report.title, report.data, style = report.style )
                continue                
                
            if inRow:
                content+="</div>"
                inRow = False    
            
            
            content+= report.render( templateFolder=templateFolder, outFolder = outFolder, reportList=reportList )
        
        return content

    def cache(self, file ):
        if self.cacheFolder==None:
            print("Website > can't cache: no cache folder set.")
            return 
        file = os.path.basename( file )
        fileToCache = self.outFolder + "/" + file
        cacheFile = self.cacheFolder+"/"+file
        print(f"Caching file {file}")
        shutil.copy( fileToCache , cacheFile )
        
    def useCache(self, file ):
        if self.cacheFolder==None:
            print("Website > can't retreive cache: no cache folder set.")
            return
        file = os.path.basename( file )
        cacheFile = self.cacheFolder+"/"+file
        if os.path.isfile( cacheFile ):
            print(f"Using cache for file {file}")
            shutil.copy( cacheFile , self.outFolder + "/" + file )
            return True
            
        return False

    def setCacheFolder(self, cacheFolder ):
        self.cacheFolder = cacheFolder
        
    def initWebSiteOutFolder(self  ):
        
        print("remove existing files...")
        
        files = []
        files.extend( glob( f"{self.outFolder}/*.html" ) ) 
        files.extend( glob( f"{self.outFolder}/*.xlsx" ) )
        files.extend( glob( f"{self.outFolder}/*.mp4" ) )
        files.extend( glob( f"{self.outFolder}/*.css" ) )
        files.extend( glob( f"{self.outFolder}/*.js" ) )

        for f in files:
            print("removing..." , f )
            os.remove(f)
            
        # copy initial files
        print("Copy default website ...")
        if self.defaultWebSiteFolder != None:        
            files = []
            files.extend( glob( f"{self.defaultWebSiteFolder}/*.css" ) )
            files.extend( glob( f"{self.defaultWebSiteFolder}/*.js" ) )
            files.extend( glob( f"{self.defaultWebSiteFolder}/*.jpg" ) )
            files.extend( glob( f"{self.defaultWebSiteFolder}/*.png" ) )
            files.extend( glob( f"{self.defaultWebSiteFolder}/*.pdf" ) )
            for file in files:      
                print(f"copy {file} --> {self.outFolder}/{os.path.basename(file)} ")      
                shutil.copy( f"{file}" , f"{self.outFolder}/{os.path.basename(file)}")
        
        
    def generateWebSite(self ):
        print("Generating website...")
        
        templateFolder = self.templateFolder
        outFolder = self.outFolder
        
        

        # Create the jinja2 environment.        
        self.env = Environment(loader=FileSystemLoader( templateFolder ))
        env = self.env
        
        experimentList = self.experimentManager.getExperimentList()
        print( experimentList )
        

        # Main index generation
                       
        
        content = ""            
        '''
        content+="<div class='row'>"
        content+= self.miniCard("Result generation",f"Date: { self.nowStr()  }")
        content+= self.miniCard("Number of experiments",f"<h1>{len(experimentList)}</h1>", style = "success")
        content+= self.miniCard("Number of reports",f"<h1>{len(self.experimentManager.getAllReports())}</h1>", style = "success")                
        content+="</div>"
        '''
        
        experimentMain = self.experimentManager.getExperimentByName("main")
        experimentMainTimeGenerationInS = 0
        
        if experimentMain != None:        
            content += self.renderReportList( experimentMain.reportList , templateFolder, outFolder, "Main" )
            experimentMainTimeGenerationInS = experimentMain.getGenerationTimeInS()
            
        mainHTML = env.get_template( "index.html").render( 
            mainContentTitle="Overview", 
            content = content,
            generationDate= self.nowStr(),
            experimentList= self.experimentManager.getExperimentListAsNameURL(), 
            timeForGeneration = experimentMainTimeGenerationInS
            )
                
        with open( outFolder+"index.html", "w", encoding='utf-8' ) as text_file:
            text_file.write( mainHTML )
        
        # Sub pages generation
        
        print("Sub page generation...")
        
        for experiment in experimentList:
        
            print ( experiment ) 
            experimentFile = experiment.url
                       
            content = ""
                 
            content += self.renderReportList( experiment.reportList , templateFolder, outFolder, experiment.name  )
                            
            # put content in main            
            mainHTML = env.get_template( "index.html").render(                 
                content = content,
                generationDate = datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
                timeForGeneration = experiment.getGenerationTimeInS(),
                experimentList = self.experimentManager.getExperimentListAsNameURL(),
                title = "<small>MiceCraft Reports</small> - " + experiment.name
                )
            
            with open( outFolder+experimentFile, "w", encoding='utf-8' ) as text_file:
                text_file.write( mainHTML )
         
    def upload(self, localFolder, remoteFolder ):
        
        import json
        
        #self.passFile
        #passFile = os.path.dirname(os.path.abspath(__file__)) + '/ftp_password.json'
        
        if self.passFile == None:
            print("No passfile set. Upload canceled.")
            return
            
        with open( self.passFile ) as f:
            connectData = json.load(f)
                        
        session = ftplib.FTP_TLS(connectData["url"],connectData["login"],connectData["password"])
        print( session )
                
        # www/report
        
        print ( localFolder )
        files = []
        files.extend( glob( f"{localFolder}/*.css" ) )
        files.extend( glob( f"{localFolder}/*.js" ) )
        files.extend( glob( f"{localFolder}/*.html" ) ) 
        files.extend( glob( f"{localFolder}/*.xlsx" ) )
        files.extend( glob( f"{localFolder}/*.mp4" ) )
        files.extend( glob( f"{localFolder}/*.png" ) )
        files.extend( glob( f"{localFolder}/*.jpg" ) )
        files.extend( glob( f"{localFolder}/*.pdf" ) )

        onServerFiles = []
        
        session.cwd( f"{remoteFolder}/" )
        session.dir( onServerFiles.append )
        session.cwd( f"/" )
        
        for f in onServerFiles:
            print( f )
        
        # don't re upload files in mp4 if already on server
        filesToRemove = []
        for file in files:
            simpleFile = os.path.basename( file )
            if ".mp4" in simpleFile:                
                for fileOnline in onServerFiles:
                    if simpleFile in fileOnline:
                        filesToRemove.append( file )
                        print(f"Already existing file on server: Skip upload for file {file}")
                        break
        for file in filesToRemove:
            files.remove( file )
        
        for file in files:
            
            f = open( file ,'rb')
            fileName = os.path.basename(file)
            print( f"sending {file}")
            storeCommand = f"STOR {remoteFolder}/{fileName}"
            print( storeCommand )
            session.storbinary( storeCommand, f )            
            
            
            f.close()
    
        print("Upload done.")
        
        session.quit()
        
        
        
                
            