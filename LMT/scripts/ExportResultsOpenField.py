'''
Created by Nicolas Torquet at 06/02/2023
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''

import json
import pandas

from lmtanalysis.FileUtil import behaviouralEventOneMouse, getJsonFileToProcess


if __name__ == '__main__':
    print("Code launched.")

    file = getJsonFileToProcess()
    print(file)
    # create a dictionary with profile data
    with open(file) as json_data:
        profileData = json.load(json_data)

    ################# Export raw data #################
    # Doesn't export time bin

    dicoPreCSV = {'Mouse label': [], 'Group': [], 'Gender': [], 'totDistance': [], 'centerDistance': [],
        'centerTime': [], 'nbSap': [], 'rearTotal Nb': [], 'rearTotal Duration': [], 'rearCenter Nb': [], 'rearCenter Duration': [],
        'rearPeriphery Nb': [], 'rearPeriphery Duration': []}

    for measure in profileData:
        if measure == "totDistance":
            for sex in profileData[measure]:
                for genotype in profileData[measure][sex]:
                    for mouse in profileData[measure][sex][genotype]:
                        dicoPreCSV['Mouse label'].append(mouse)
                        dicoPreCSV['Group'].append(genotype)
                        dicoPreCSV['Gender'].append(sex)
                        dicoPreCSV['totDistance'].append(profileData[measure][sex][genotype][mouse])
        elif measure != 'distancePerBin':
            for sex in profileData[measure]:
                for genotype in profileData[measure][sex]:
                    for mouse in profileData[measure][sex][genotype]:
                        dicoPreCSV[measure].append(profileData[measure][sex][genotype][mouse])

    tabResults = pandas.DataFrame.from_dict(dicoPreCSV)
    tabResults = tabResults.sort_values(by=['Group', 'Gender'])
    csvFileName = file.split('.')[0] + '_export.csv'
    tabResults.to_csv(csvFileName)
