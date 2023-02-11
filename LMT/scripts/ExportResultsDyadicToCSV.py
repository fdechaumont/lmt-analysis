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
from lmtanalysis.FileUtil import behaviouralEventOneMouse, getJsonFileToProcess

categoryList = [' TotalLen', ' Nb']
convertColumns = {
    'genotype': 'Group',
    'sex': 'Gender',
    'treatment': 'Treatment',
    'file': 'Experiment',
    'totalDistance': 'Distance (m)',
    'Approach contact Nb': 'Approach contact Nb',
    'Approach contact MeanDur': 'Approach contact MeanDur',
    'Contact Nb': 'Contact Nb',
    'Contact MeanDur': 'Contact MeanDur',
    'Oral-genital Contact Nb': 'oral-genital Nb',
    'Oral-genital Contact MeanDur': 'oral-genital MeanDur',
    'Oral-oral Contact Nb': 'oral-oral Nb',
    'Oral-oral Contact MeanDur': 'oral-oral MeanDur',
    'Side by side Contact Nb': 'side by side Nb',
    'Side by side Contact MeanDur': 'side by side MeanDur',
    'FollowZone Isolated Nb': 'Follow Nb',
    'FollowZone Isolated MeanDur': 'Follow MeanDur'
}


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

    file = getJsonFileToProcess()
    print(file)
    # create a dictionary with profile data
    with open(file) as json_data:
        profileData = json.load(json_data)

    # mergeProfile = mergeProfileOverNights(profileData=profileData, categoryList=categoryList,
    #                                               behaviouralEventOneMouse=behaviouralEventOneMouse)

    ################# Export raw data #################

    dicoPreCSV = {'Mouse label': [], 'Group': [], 'Gender': [], 'Treatment': [], 'Nb/Cage': [], 'Experiment': [], 'Distance (m)': [], 'Approach contact Nb': [],
        'Approach contact MeanDur': [], 'Contact Nb': [], 'Contact MeanDur': [], 'oral-genital Nb': [], 'oral-genital MeanDur': [],
        'oral-oral Nb': [], 'oral-oral MeanDur': [], 'side by side Nb': [], 'side by side MeanDur': [], 'Follow Nb': [], 'Follow MeanDur': []}


    for experiment in profileData:
        for mouse in profileData[experiment]['0']:
            # print(mergeProfile[experiment]['all nights'][mouse]['file'])
            dicoPreCSV['Mouse label'].append(mouse)
            dicoPreCSV['Group'].append(profileData[experiment]['0'][mouse]['genotype'])
            dicoPreCSV['Gender'].append(profileData[experiment]['0'][mouse]['sex'])
            dicoPreCSV['Treatment'].append(profileData[experiment]['0'][mouse]['treatment'])
            dicoPreCSV['Nb/Cage'].append(len(profileData[experiment]['0']))
            dicoPreCSV['Experiment'].append(profileData[experiment]['0'][mouse]['file'].split('\\')[1])
            dicoPreCSV['Distance (m)'].append(profileData[experiment]['0'][mouse]['totalDistance'])
            dicoPreCSV['Approach contact Nb'].append(profileData[experiment]['0'][mouse]['Approach contact Nb'])
            dicoPreCSV['Approach contact MeanDur'].append(profileData[experiment]['0'][mouse]['Approach contact MeanDur']/30)
            dicoPreCSV['Contact Nb'].append(profileData[experiment]['0'][mouse]['Contact Nb'])
            dicoPreCSV['Contact MeanDur'].append(profileData[experiment]['0'][mouse]['Contact MeanDur']/30)
            dicoPreCSV['oral-genital Nb'].append(profileData[experiment]['0'][mouse]['Oral-genital Contact Nb'])
            dicoPreCSV['oral-genital MeanDur'].append(profileData[experiment]['0'][mouse]['Oral-genital Contact MeanDur']/30)
            dicoPreCSV['oral-oral Nb'].append(profileData[experiment]['0'][mouse]['Oral-oral Contact Nb'])
            dicoPreCSV['oral-oral MeanDur'].append(profileData[experiment]['0'][mouse]['Oral-oral Contact MeanDur']/30)
            dicoPreCSV['side by side Nb'].append(profileData[experiment]['0'][mouse]['Side by side Contact Nb'])
            dicoPreCSV['side by side MeanDur'].append(profileData[experiment]['0'][mouse]['Side by side Contact MeanDur']/30)
            dicoPreCSV['Follow Nb'].append(profileData[experiment]['0'][mouse]['FollowZone Nb'])
            dicoPreCSV['Follow MeanDur'].append(profileData[experiment]['0'][mouse]['FollowZone MeanDur']/30)

    tabResults = pandas.DataFrame.from_dict(dicoPreCSV)
    tabResults = tabResults.sort_values(by=['Group', 'Gender', 'Treatment'])
    csvFileName = file.split('.')[0] + '_export.csv'
    tabResults.to_csv(csvFileName)

