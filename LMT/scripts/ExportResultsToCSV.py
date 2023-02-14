'''
Created on 11 juillet. 2022

@author: Nicolas Torquet
'''
import json
import pandas

from scripts.ComputeMeasuresIdentityProfileOneMouseAutomatic import mergeProfileOverNights, extractCageData, \
    generateMutantData
from lmtanalysis.FileUtil import behaviouralEventOneMouse, getJsonFileToProcess

categoryList = [' TotalLen', ' Nb', ' MeanDur']
convertColumns = {
    'genotype': 'Group',
    'sex': 'Gender',
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

if __name__ == '__main__':
    print("Code launched.")

    file = getJsonFileToProcess()
    print(file)
    # create a dictionary with profile data
    with open(file) as json_data:
        profileData = json.load(json_data)

    mergeProfile = mergeProfileOverNights(profileData=profileData, categoryList=categoryList,
                                                  behaviouralEventOneMouse=behaviouralEventOneMouse)

    ################# Export raw data #################

    dicoPreCSV = {'Mouse label': [], 'Group': [], 'Gender': [], 'Nb/Cage': [], 'Experiment': [], 'Distance (m)': [], 'Approach contact Nb': [],
        'Approach contact MeanDur': [], 'Contact Nb': [], 'Contact MeanDur': [], 'oral-genital Nb': [], 'oral-genital MeanDur': [],
        'oral-oral Nb': [], 'oral-oral MeanDur': [], 'side by side Nb': [], 'side by side MeanDur': [], 'Follow Nb': [], 'Follow MeanDur': []}


    for experiment in mergeProfile:
        for mouse in mergeProfile[experiment]['all nights']:
            # print(mergeProfile[experiment]['all nights'][mouse]['file'])
            dicoPreCSV['Mouse label'].append(mouse)
            dicoPreCSV['Group'].append(mergeProfile[experiment]['all nights'][mouse]['genotype'])
            dicoPreCSV['Gender'].append(mergeProfile[experiment]['all nights'][mouse]['sex'])
            dicoPreCSV['Nb/Cage'].append(len(mergeProfile[experiment]['all nights']))
            dicoPreCSV['Experiment'].append(mergeProfile[experiment]['all nights'][mouse]['file'].split('\\')[1])
            dicoPreCSV['Distance (m)'].append(mergeProfile[experiment]['all nights'][mouse]['totalDistance'])
            dicoPreCSV['Approach contact Nb'].append(mergeProfile[experiment]['all nights'][mouse]['Approach contact Nb'])
            dicoPreCSV['Approach contact MeanDur'].append(mergeProfile[experiment]['all nights'][mouse]['Approach contact MeanDur']/30)
            dicoPreCSV['Contact Nb'].append(mergeProfile[experiment]['all nights'][mouse]['Contact Nb'])
            dicoPreCSV['Contact MeanDur'].append(mergeProfile[experiment]['all nights'][mouse]['Contact MeanDur']/30)
            dicoPreCSV['oral-genital Nb'].append(mergeProfile[experiment]['all nights'][mouse]['Oral-genital Contact Nb'])
            dicoPreCSV['oral-genital MeanDur'].append(mergeProfile[experiment]['all nights'][mouse]['Oral-genital Contact MeanDur']/30)
            dicoPreCSV['oral-oral Nb'].append(mergeProfile[experiment]['all nights'][mouse]['Oral-oral Contact Nb'])
            dicoPreCSV['oral-oral MeanDur'].append(mergeProfile[experiment]['all nights'][mouse]['Oral-oral Contact MeanDur']/30)
            dicoPreCSV['side by side Nb'].append(mergeProfile[experiment]['all nights'][mouse]['Side by side Contact Nb'])
            dicoPreCSV['side by side MeanDur'].append(mergeProfile[experiment]['all nights'][mouse]['Side by side Contact MeanDur']/30)
            dicoPreCSV['Follow Nb'].append(mergeProfile[experiment]['all nights'][mouse]['FollowZone Nb'])
            dicoPreCSV['Follow MeanDur'].append(mergeProfile[experiment]['all nights'][mouse]['FollowZone MeanDur']/30)

    tabResults = pandas.DataFrame.from_dict(dicoPreCSV)
    tabResults = tabResults.sort_values(by=['Group', 'Gender'])
    csvFileName = file.split('.')[0] + '_export.csv'
    tabResults.to_csv(csvFileName)

    ################# Export Z-score #################
    cageData = extractCageData(profileData=mergeProfile, behaviouralEventOneMouse=behaviouralEventOneMouse)
    genoControl = 'wt'
    genoMutant = 'ko'
    koData = generateMutantData(profileData=mergeProfile, genoMutant=genoMutant, wtData=cageData,
                                categoryList=categoryList, behaviouralEventOneMouse=behaviouralEventOneMouse)

    dicoZScorePreCSV = {'Mouse label': [], 'Group': [], 'Gender': [], 'Nb/Cage': [], 'Experiment': [], 'Distance (m)': [],
                  'Approach contact Nb': [],
                  'Approach contact MeanDur': [], 'Contact Nb': [], 'Contact MeanDur': [], 'oral-genital Nb': [],
                  'oral-genital MeanDur': [],
                  'oral-oral Nb': [], 'oral-oral MeanDur': [], 'side by side Nb': [], 'side by side MeanDur': [],
                  'Follow Nb': [], 'Follow MeanDur': []}

    sex = 'male'
    numberInCage = 4
    for experiment in koData:
        for mouse in koData[experiment]['all nights']:
            # print(mergeProfile[experiment]['all nights'][mouse]['file'])
            dicoZScorePreCSV['Mouse label'].append(mouse)
            dicoZScorePreCSV['Group'].append('ko')
            dicoZScorePreCSV['Gender'].append(sex)
            dicoZScorePreCSV['Nb/Cage'].append(numberInCage)
            dicoZScorePreCSV['Experiment'].append(experiment.split('\\')[1])
            dicoZScorePreCSV['Distance (m)'].append(koData[experiment]['all nights'][mouse]['totalDistance'])
            dicoZScorePreCSV['Approach contact Nb'].append(koData[experiment]['all nights'][mouse]['Approach contact Nb'])
            dicoZScorePreCSV['Approach contact MeanDur'].append(koData[experiment]['all nights'][mouse]['Approach contact MeanDur']/30)
            dicoZScorePreCSV['Contact Nb'].append(koData[experiment]['all nights'][mouse]['Contact Nb'])
            dicoZScorePreCSV['Contact MeanDur'].append(koData[experiment]['all nights'][mouse]['Contact MeanDur']/30)
            dicoZScorePreCSV['oral-genital Nb'].append(koData[experiment]['all nights'][mouse]['Oral-genital Contact Nb'])
            dicoZScorePreCSV['oral-genital MeanDur'].append(koData[experiment]['all nights'][mouse]['Oral-genital Contact MeanDur']/30)
            dicoZScorePreCSV['oral-oral Nb'].append(koData[experiment]['all nights'][mouse]['Oral-oral Contact Nb'])
            dicoZScorePreCSV['oral-oral MeanDur'].append(koData[experiment]['all nights'][mouse]['Oral-oral Contact MeanDur']/30)
            dicoZScorePreCSV['side by side Nb'].append(koData[experiment]['all nights'][mouse]['Side by side Contact Nb'])
            dicoZScorePreCSV['side by side MeanDur'].append(koData[experiment]['all nights'][mouse]['Side by side Contact MeanDur']/30)
            dicoZScorePreCSV['Follow Nb'].append(koData[experiment]['all nights'][mouse]['FollowZone Nb'])
            dicoZScorePreCSV['Follow MeanDur'].append(koData[experiment]['all nights'][mouse]['FollowZone MeanDur']/30)

    tabResultsZscore = pandas.DataFrame.from_dict(dicoZScorePreCSV)
    tabResultsZscore = tabResultsZscore.sort_values(by=['Group', 'Gender'])
    csvZScoreFileName = file.split('.')[0] + '_zscore_export.csv'
    tabResultsZscore.to_csv(csvZScoreFileName)

