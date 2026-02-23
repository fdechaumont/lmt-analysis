'''
Created on 4 avr. 2025

@author: Fab
'''
import os
from experiments.api.report.WebSite import WebSite
from experiments.ghfc.altruism.analysis.logAnalysisAltruV2 import LogAltruAnalysis3
from experiments.api.report.Report import Report
import glob
from experiments.ghfc.results.TouchScreenAnalysis import TouchScreenAnalysis
from experiments.api.report.LogFileMerger import LogFileMerger
from experiments.ghfc.results.LogAnalyserGeneric import LogAnalyserGeneric
from experiments.ghfc.results.SugarSocialAnalysis import SugarSocialAnalysis
import plotly.express as px
import pandas as pd
from datetime import datetime
from experiments.ghfc.results.CollaborationAnalysis import CollaborationAnalysis
import time
from experiments.ghfc.results.LogStartEnd import LogStartEnd
import pathlib
from pathlib import Path
import traceback
import schedule

if __name__ == '__main__':
    
    
    print("Start Main Analysis of all the experiments")
    print( f"Starting at {datetime.now()}")
    
    startComputationTime = datetime.now()
    
    
    
     
    currentFolder = os.path.dirname(os.path.abspath(__file__))    
    outFolder = currentFolder+"/html/"
    defaultWebSiteFolder = currentFolder+"/defaultwebsite/"
    templateFolder = currentFolder+"/template/"
    remoteFolder="www/report5/"
    
    passFile = os.path.dirname(os.path.abspath(__file__)) + '/ftp_password.json'
    
    
    webSite = WebSite( templateFolder , outFolder, defaultWebSiteFolder, 
                       currentFolder+"/cache/", passFile = passFile )
    

    webSite.initWebSiteOutFolder( )
    
    
    webSite.addReport( Report( "First report test", f"My content" , experimentName="main" ) )

    webSite.addReport( Report( "My splitter/header", f"My title" , template="splitter.html", experimentName="main", style="primary" ) )
    
    webSite.addReport( Report( "First report test", f"My content" , experimentName="main", style="primary" ) )


    webSite.addReport( Report( "First report test", f"My content" , experimentName="verylongtestpage", style="primary" ) )
    
    
    # generate a graph
    
    import plotly.express as px

    df = px.data.gapminder().query("country=='Canada'")
    fig = px.line(df, x="year", y="lifeExp", title='Life expectancy in Canada')
    html = fig.to_html(full_html=False, include_plotlyjs='cdn', config= {'displaylogo': False} )    
    webSite.addReport( Report( "First report test", html , experimentName="main", style="danger" ) )
        
    # generate with a dataframe
    
    import pandas as pd

    data = {
      "calories": [420, 380, 390],
      "duration": [50, 40, 45]
    }
    df = pd.DataFrame(data)
    webSite.addReport( Report( "First dataframe test", df , template="table.html", experimentName="main", style="success" ) )

    webSite.addReport( Report( "First minicard", "ok" , template="miniCard.html", experimentName="main", style="success" ) )
    webSite.addReport( Report( "First minicard", "problem here and there" , template="miniCard.html", experimentName="main", style="danger" ) )

    
    
    webSite.generateWebSite( )
        
    webSite.upload( outFolder, remoteFolder )

    
    print("Done.")
    
    