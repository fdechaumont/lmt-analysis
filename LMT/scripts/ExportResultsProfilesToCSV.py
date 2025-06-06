'''
Created by Nicolas Torquet at 1/02/2023
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''
import json
import pandas

from scripts.ComputeMeasuresIdentityProfileOneMouseAutomatic import mergeProfileOverNights, extractCageData, \
    generateMutantData
from lmtanalysis.FileUtil import behaviouralEventOneMouse, getJsonFileToProcess,\
    getJsonFilesToProcess



def mergeProfileOverNights( profileData, categoryList, behaviouralEventOneMouse ):
    #merge data from the different nights
    mergeProfile = {}
    for file in profileData.keys():
        nightList = list( profileData[file].keys() )
        print('###############night List: ', nightList)
        mergeProfile[file] = {}
        mergeProfile[file]['0'] = {}
        for rfid in profileData[file][nightList[0]].keys():
            print('rfid: ', rfid)
            mergeProfile[file]['0'][rfid] = {}
            mergeProfile[file]['0'][rfid]['animal'] = profileData[file][nightList[0]][rfid]['animal']
            mergeProfile[file]['0'][rfid]['genotype'] = profileData[file][nightList[0]][rfid]['genotype']
            mergeProfile[file]['0'][rfid]['file'] = profileData[file][nightList[0]][rfid]['file']
            mergeProfile[file]['0'][rfid]['sex'] = profileData[file][nightList[0]][rfid]['sex']
            mergeProfile[file]['0'][rfid]['treatment'] = profileData[file][nightList[0]][rfid]['treatment']
            mergeProfile[file]['0'][rfid]['age'] = profileData[file][nightList[0]][rfid]['age']
            mergeProfile[file]['0'][rfid]['strain'] = profileData[file][nightList[0]][rfid]['strain']
            mergeProfile[file]['0'][rfid]['group'] = profileData[file][nightList[0]][rfid]['group']


            for cat in categoryList:
                traitList = [trait+cat for trait in behaviouralEventOneMouse]
                for event in traitList:
                    print('event: ', event)
                    try:
                        dataNight = 0
                        for night in profileData[file].keys():
                            dataNight += profileData[file][night][rfid][event]

                        if ' MeanDur' in event:
                            mergeProfile[file]['0'][rfid][event] = dataNight / len(profileData[file].keys())
                        else:
                            mergeProfile[file]['0'][rfid][event] = dataNight
                    except:
                        print('No event of this name: ', rfid, event)
                        continue
            try:
                distNight = 0
                for night in profileData[file].keys():
                    distNight += profileData[file][night][rfid]['totalDistance']
            except:
                print('No calculation of distance possible.', rfid)
                distNight = 'totalDistance'

            mergeProfile[file]['0'][rfid]['totalDistance'] = distNight

    return mergeProfile

if __name__ == '__main__':
    print("Code launched.")
    
    dic = {"experiment": [], "night": [], "rfid": [], "animal": [], "genotype": [], "sex": [], "age": [], "strain": [], "group": [], "variable": [], "value": []}
    
    files = getJsonFilesToProcess()
    
    for file in files:
        # create a dictionary with profile data
        with open(file) as json_data:
            profileData = json.load(json_data)

        for experiment in profileData.keys():
            for night in profileData[experiment].keys():
                for rfid in profileData[experiment][night].keys():
                    for variable in profileData[experiment][night][rfid].keys():
                        if variable in ["file", "rfid", "animal", "genotype", "sex", "age", "strain", "group"]:
                            continue
                        else:
                            dic["experiment"].append( experiment )
                            dic["night"].append( night )
                            dic["rfid"].append( rfid )
                            dic["animal"].append( profileData[experiment][night][rfid]["animal"] )
                            dic["genotype"].append( profileData[experiment][night][rfid]["genotype"])
                            dic["sex"].append( profileData[experiment][night][rfid]["sex"])
                            dic["age"].append( profileData[experiment][night][rfid]["age"])
                            dic["strain"].append( profileData[experiment][night][rfid]["strain"])
                            dic["group"].append( profileData[experiment][night][rfid]["group"])
                            dic["variable"].append( variable )
                            dic["value"].append( profileData[experiment][night][rfid][variable])
                        
    df = pandas.DataFrame.from_dict( dic )
    
    df.to_csv('export_profile.csv', index=False)
    
    print( "Job done.")
    
    

