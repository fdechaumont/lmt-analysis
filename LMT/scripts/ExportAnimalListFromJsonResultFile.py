'''
Created by Nicolas Torquet at 07/02/2023
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''


'''
Take a Json file to extract animal's information
Json file structure for 3 nights experiment:
{
    "D:/LMT Gods21\\20211026cage1_Experiment 5067.sqlite": {
        "1": {  # night number
            "001038125095": {
                "animal": "10",
                "file": "D:/LMT Gods21\\20211026cage1_Experiment 5067.sqlite",
                "genotype": "HZ",
                "sex": "male",
                "group": "001038125095",
                "strain": "Dp1Yey",
                "age": "21we",
                "Move isolated TotalLen": 189621,
                ...
            },
            "001038125140": {
            

Json file structure for dyadic experiments:
{
    "E:/gods21/females\\20211207_1_52_Experiment 3421\\20211207_1_52_Experiment 3421.sqlite": {
        "0": {
            "001038125115_001038125146": {
                "genotype": "B6_WT",
                "file": "E:/gods21/females\\20211207_1_52_Experiment 3421\\20211207_1_52_Experiment 3421.sqlite",
                "animal": "001038125115_001038125146",
                "sex": "female",
                "age": "26we",
                "strain": "C57BL6J_Dp1Yey",
###### all of those information are for the pair of mice
Then:
            "001038125146": {
                "animal": "52",
                "file": "E:/gods21/females\\20211207_1_52_Experiment 3421\\20211207_1_52_Experiment 3421.sqlite",
                "genotype": "B6",
                "sex": "female",
                "age": "26we",
                "strain": "C57BL6J",
                "group": "001038125115_001038125146",
                "Move isolated TotalLen": 15956,
                ...

'''

import json
import pandas
from lmtanalysis.FileUtil import getJsonFileToProcess


def extractInfoFromJson3Nights():
    file = getJsonFileToProcess()
    print(file)
    # create a dictionary with profile data
    with open(file) as json_data:
        jsonData = json.load(json_data)
    animalsInfo = {}
    for experiment in jsonData:
        # First night is enough to get info
        for mouse in jsonData[experiment]['1']:
            animalsInfo[mouse] = {}
            print(mouse)
            animalsInfo[mouse]["animal"] = jsonData[experiment]['1'][mouse]["animal"]
            animalsInfo[mouse]["file"] = jsonData[experiment]['1'][mouse]["file"]
            animalsInfo[mouse]["genotype"] = jsonData[experiment]['1'][mouse]["genotype"]
            animalsInfo[mouse]["sex"] = jsonData[experiment]['1'][mouse]["sex"]
            animalsInfo[mouse]["group"] = jsonData[experiment]['1'][mouse]["group"]
            animalsInfo[mouse]["strain"] = jsonData[experiment]['1'][mouse]["strain"]
            animalsInfo[mouse]["age"] = jsonData[experiment]['1'][mouse]["age"]

    return animalsInfo


def extractInfoFromJsonDyadic():
    file = getJsonFileToProcess()
    print(file)
    # create a dictionary with profile data
    with open(file) as json_data:
        jsonData = json.load(json_data)
    animalsInfo = {}
    for experiment in jsonData:
        # First night is enough to get info
        for mouse in jsonData[experiment]['0']:
            if len(mouse) < 14:
                animalsInfo[mouse] = {}
                print(mouse)
                animalsInfo[mouse]["animal"] = jsonData[experiment]['0'][mouse]["animal"]
                animalsInfo[mouse]["file"] = jsonData[experiment]['0'][mouse]["file"]
                animalsInfo[mouse]["genotype"] = jsonData[experiment]['0'][mouse]["genotype"]
                animalsInfo[mouse]["sex"] = jsonData[experiment]['0'][mouse]["sex"]
                animalsInfo[mouse]["group"] = jsonData[experiment]['0'][mouse]["group"]
                animalsInfo[mouse]["strain"] = jsonData[experiment]['0'][mouse]["strain"]
                animalsInfo[mouse]["age"] = jsonData[experiment]['0'][mouse]["age"]

    return animalsInfo


def changeValueInJsonFile(jsonData, valueName, oldValue, newValue):
    for mouse in jsonData:
        if jsonData[mouse][valueName] == oldValue:
            jsonData[mouse][valueName] = newValue
    return jsonData


if __name__ == '__main__':
    print("Code launched.")

    while True:
        question = "Do you want to:"
        question += "\n\t [1] extract from 3 night experiments?"
        question += "\n\t [2] extract from dyadic experiments?"
        question += "\n\t [3] change a genotype name by a new one?"
        question += "\n"
        answer = input(question)


        if answer == '1':
            print("Extract from 3 night experiments.")
            animalsInfo = extractInfoFromJson3Nights()
            outputFileName = input("Enter the name of the Json file to be saved")
            with open(outputFileName+'.json', 'w') as jFile:
                json.dump(animalsInfo, jFile, indent=4)
            print(outputFileName+" json file created")

            break


        if answer == '2':
            print("Extract from dyadic experiments.")
            animalsInfo = extractInfoFromJsonDyadic()
            outputFileName = input("Enter the name of the Json file to be saved")
            with open(outputFileName+'.json', 'w') as jFile:
                json.dump(animalsInfo, jFile, indent=4)
            print(outputFileName+" json file created")

            break


        if answer == '3':
            print("change a genotype name by a new one.")
            print("Select your Json file:")
            file = getJsonFileToProcess()
            print(file)
            # create a dictionary with profile data
            with open(file) as json_data:
                jsonData = json.load(json_data)

            # get value in jsonFile
            valueNameList = ["genotype", "strain", "sex", "age", "setup", "treatment"]
            valueNameSelectionStr = "Select the name of the value you want to change:"
            for index, val in enumerate(valueNameList):
                valueNameSelectionStr += f"\n\t [{index}] {val}"
            valueNameSelectionStr += "\n"
            valueNameSelectionAnswer = input(valueNameSelectionStr)
            valueName = valueNameList[int(valueNameSelectionAnswer)]
            print(valueName+" selected")
            valueList = []
            for mouse in jsonData:
                if jsonData[mouse][valueNameList[int(valueNameSelectionAnswer)]] not in valueList:
                    valueList.append(jsonData[mouse][valueNameList[int(valueNameSelectionAnswer)]])
            print(valueNameList[int(valueNameSelectionAnswer)] + ' present in the Json file: ' + str(valueList))
            valueToChangeStr = "Select the value you want to change:"
            for index, value in enumerate(valueList):
                valueToChangeStr += f"\n\t [{index}] {value}"
            valueToChangeStr += "\n"
            valueToChange = input(valueToChangeStr)
            oldValue = valueList[int(valueToChange)]
            print(oldValue+" will be changed")
            newValue = input("Write the new value you want to put instead of the selected one:\n")
            jsonData = changeValueInJsonFile(jsonData, valueName, oldValue, newValue)
            outputFileName = input("Enter the name of the Json file to be saved")
            with open(outputFileName + '.json', 'w') as jFile:
                json.dump(jsonData, jFile, indent=4)
            print(outputFileName + " json file created")
            break