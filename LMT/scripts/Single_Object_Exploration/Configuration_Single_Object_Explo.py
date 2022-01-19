'''
Created on 06 Jan. 2022

@author: Elodie
'''


variableList = ["dist_tot1", "dist_center1", "time_center1", "dist_obj1", "time_obj1", "sap1", "dist_tot2", "dist_center2", "time_center2", "dist_obj2", "time_obj2", "sap2", "Stop TotalLen1", "Stop Nb1", "Stop MeanDur1", "Center Zone TotalLen1", "Center Zone Nb1",
"Center Zone MeanDur1", "Periphery Zone TotalLen1", "Periphery Zone Nb1", "Periphery Zone MeanDur1", "Rear isolated TotalLen1", "Rear isolated Nb1", "Rear isolated MeanDur1",
#"Rear in centerWindow TotalLen1", "Rear in centerWindow Nb1", "Rear in centerWindow MeanDur1",
                    "Rear at periphery TotalLen1", "Rear at periphery Nb1", "Rear at periphery MeanDur1", "SAP TotalLen1", "SAP Nb1", "SAP MeanDur1", "WallJump TotalLen1", "WallJump Nb1",
"WallJump MeanDur1", "Stop TotalLen2", "Stop Nb2", "Stop MeanDur2", "Center Zone TotalLen2", "Center Zone Nb2", "Center Zone MeanDur2", "Periphery Zone TotalLen2", "Periphery Zone Nb2",
"Periphery Zone MeanDur2", "Rear isolated TotalLen2", "Rear isolated Nb2", "Rear isolated MeanDur2",
                    #"Rear in centerWindow TotalLen2", "Rear in centerWindow Nb2", "Rear in centerWindow MeanDur2",
                    "Rear at periphery TotalLen2",
"Rear at periphery Nb2", "Rear at periphery MeanDur2", "SAP TotalLen2", "SAP Nb2", "SAP MeanDur2", "WallJump TotalLen2", "WallJump Nb2", "WallJump MeanDur2"]

'''selectedVariableList = ["dist_tot1", "Stop MeanDur1", #activity
 "dist_obj2", "SAP Nb2", "Rear isolated TotalLen1", "Rear isolated MeanDur1", "Rear isolated MeanDur2",  #exploration
 "Center Zone TotalLen1", "Center Zone TotalLen2", "Periphery Zone TotalLen2", "Center Zone MeanDur2", "Periphery Zone MeanDur2", "Center Zone Nb2",  #anxiety
 "WallJump Nb1", "WallJump MeanDur1"] #stereotypes & stress'''

selectedVariableList = ["dist_tot1", "Stop MeanDur2", #activity
"Rear isolated TotalLen1", "Rear isolated MeanDur2", #vertical exploration
"SAP TotalLen2", "dist_obj2", #exploration object phase 2
"Periphery Zone TotalLen1", "Center Zone TotalLen1", #anxiety phase 1
"Periphery Zone TotalLen2", "Center Zone TotalLen2", "Periphery Zone MeanDur2", #anxiety phase 2
"WallJump TotalLen1" #stereotypes
]

variableListExtension = {"dist_tot1": '(cm)', "dist_center1": '(cm)', "time_center1": '(frames)', "dist_obj1": '(cm)', "time_obj1": '(frames)', "sap1": '(frames)', "dist_tot2": '(cm)',
                "dist_center2": '(cm)', "time_center2": '(frames)', "dist_obj2": '(cm)', "time_obj2": '(frames)', "sap2": '(frames)', "Stop TotalLen1": '(frames)', "Stop Nb1": '(nb)',
                "Stop MeanDur1": '(frames)', "Center Zone TotalLen1": '(frames)', "Center Zone Nb1": '(nb)',
                "Center Zone MeanDur1": '(frames)', "Periphery Zone TotalLen1": '(frames)', "Periphery Zone Nb1": '(nb)', "Periphery Zone MeanDur1": '(frames)',
                "Rear isolated TotalLen1": '(frames)', "Rear isolated Nb1": '(nb)', "Rear isolated MeanDur1": '(frames)',
                "Rear in centerWindow TotalLen1": '(frames)', "Rear in centerWindow Nb1": '(nb)', "Rear in centerWindow MeanDur1": '(frames)',
                "Rear at periphery TotalLen1": '(frames)', "Rear at periphery Nb1": '(nb)', "Rear at periphery MeanDur1": '(frames)',
                "SAP TotalLen1": '(frames)', "SAP Nb1": '(nb)', "SAP MeanDur1": '(frames)', "WallJump TotalLen1": '(frames)', "WallJump Nb1": '(nb)',
                "WallJump MeanDur1": '(frames)', "Stop TotalLen2": '(frames)', "Stop Nb2": '(nb)', "Stop MeanDur2": '(frames)', "Center Zone TotalLen2": '(frames)',
                "Center Zone Nb2": '(nb)', "Center Zone MeanDur2": '(frames)', "Periphery Zone TotalLen2": '(frames)', "Periphery Zone Nb2": '(nb)',
                "Periphery Zone MeanDur2": '(frames)', "Rear isolated TotalLen2": '(frames)', "Rear isolated Nb2": '(nb)', "Rear isolated MeanDur2": '(frames)',
                "Rear in centerWindow TotalLen2": '(frames)', "Rear in centerWindow Nb2": '(nb)', "Rear in centerWindow MeanDur2": '(frames)',
                "Rear at periphery TotalLen2": '(frames)',
                "Rear at periphery Nb2": '(nb)', "Rear at periphery MeanDur2": '(frames)', "SAP TotalLen2": '(frames)', "SAP Nb2": '(nb)', "SAP MeanDur2": '(frames)',
                "WallJump TotalLen2": '(frames)', "WallJump Nb2": '(nb)', "WallJump MeanDur2": '(frames)'}

orderedFounderStrainList = ['CAST', 'PWK', 'WSB', '129SvJ', 'AJ', 'NOD', 'NZO', 'C57BL6J']
orderedCCStrainList = ['CC001', 'CC002', 'CC012', 'CC018', 'CC024', 'CC037', 'CC040', 'CC041', 'CC042', 'CC051', 'CC059', 'CC061']
orderedOtherStrainList = ['BTBR']

orderedFullStrainList = orderedFounderStrainList+orderedCCStrainList+orderedOtherStrainList

colorStrainDic = {
        'CAST': 'gold', 'PWK': 'darkorange', 'WSB': 'darkred', '129SvJ': 'dodgerblue', 'AJ': 'darkviolet', 'NOD': 'forestgreen', 'NZO': 'red', 'C57BL6J': 'black',
        'CC001': 'lightpink', 'CC002': 'mediumorchid', 'CC012': 'blue', 'CC018': 'cyan', 'CC024': 'springgreen', 'CC037': 'lemonchiffon', 'CC040': 'olivedrab', 'CC041': 'magenta', 'CC042': 'sienna', 'CC051': 'burlywood', 'CC059': 'lightseagreen', 'CC061': 'skyblue',
        'BTBR': 'lightgrey'
}

colorFounderStrainDic = {
    'CAST': 'gold', 'PWK': 'darkorange', 'WSB': 'darkred', '129SvJ': 'dodgerblue', 'AJ': 'darkviolet',
    'NOD': 'forestgreen', 'NZO': 'red', 'C57BL6J': 'black'
}

sexList = ['male', 'female']
