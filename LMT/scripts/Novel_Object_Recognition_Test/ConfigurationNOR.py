'''
#Created on 23 September 2021

#@author: Elodie
'''

from scripts.Rebuild_All_Event import *
from scripts.Plot_Trajectory_Single_Object_Explo import *
import numpy as np; np.random.seed(0)
from lmtanalysis.Animal import *
from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import *
from lmtanalysis.Measure import *
from matplotlib import patches
from scipy import stats
from scripts.ComputeActivityHabituationNorTest import *
from lmtanalysis import BuildEventObjectSniffingNor, BuildEventObjectSniffingNorAcquisitionWithConfig, \
    BuildEventObjectSniffingNorTestWithConfig
from lmtanalysis.Event import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from scripts.ComputeObjectRecognition import *

#object positions (x,y) according to the setup:
objectPosition = {1: {'left': (190, -152), 'right': (330, -152)},
                  2: {'left': (192, -152), 'right': (323, -152)}
                  }

# object information
objectConfig = {'cc1': {'acquisition': ('cup', 'cup'), 'test': ('cup', 'shaker')},
                'cc2': {'acquisition': ('cup', 'cup'), 'test': ('shaker', 'cup')},
                'ss1': {'acquisition': ('shaker', 'shaker'), 'test': ('shaker', 'cup')},
                'ss2': {'acquisition': ('shaker', 'shaker'), 'test': ('cup', 'shaker')},
                'ff1': {'acquisition': ('falcon', 'falcon'), 'test': ('falcon', 'flask')},
                'ff2': {'acquisition': ('falcon', 'falcon'), 'test': ('flask', 'falcon')},
                'kk1': {'acquisition': ('flask', 'flask'), 'test': ('flask', 'falcon')},
                'kk2': {'acquisition': ('flask', 'flask'), 'test': ('falcon', 'flask')},
                'ck1': {'acquisition': ('cup', 'cup'), 'test': ('cup', 'flask')},
                'ck2': {'acquisition': ('cup', 'cup'), 'test': ('flask', 'cup')},
                'dm1': {'acquisition': ('dice', 'dice'), 'test': ('dice', 'marble')},
                'dm2': {'acquisition': ('dice', 'dice'), 'test': ('marble', 'dice')},
                'kc1': {'acquisition': ('flask', 'flask'), 'test': ('flask', 'cup')},
                'kc2': {'acquisition': ('flask', 'flask'), 'test': ('cup', 'flask')},
                'md1': {'acquisition': ('marble', 'marble'), 'test': ('marble', 'dice')},
                'md2': {'acquisition': ('marble', 'marble'), 'test': ('dice', 'marble')}
                }

organisation = {'short':
                        {'001038125044': 'ff1',
                        '001038125005': 'cc1',
                        '001038124994': 'kk2',
                        '001038125001': 'ss2',
                        '001038125040': 'cc1',
                        '001038125023': 'ff1',
                        '001038124996': 'ss2',
                        '001038125045': 'kk2',
                        '001038125027': 'ff1',
                        '001038125024': 'cc1',
                        '001038124971': 'kk2',
                        '001038125028': 'ss2',
                        '001038125022': 'cc1',
                        '001038124973': 'ff1',
                        '001038124975': 'ff1',
                        '001038124968': 'cc1',
                        '001038125002': 'ss2',
                        '001038125012': 'kk2'
                            },
                'medium':
                    {'001038125044': 'cc2',
                    '001038125005': 'ff2',
                    '001038124994': 'cc1',
                    '001038125001': 'kk1',
                    '001038125040': 'ff2',
                    '001038125023': 'ss2',
                    '001038124996': 'ff1',
                    '001038125045': 'cc1',
                    '001038125027': 'cc2',
                    '001038125024': 'kk2',
                    '001038124971': 'cc1',
                    '001038125028': 'kk1',
                    '001038125022': 'ff2',
                    '001038124973': 'cc2',
                    '001038124975': 'cc2',
                    '001038124968': 'ff2',
                    '001038125002': 'ff1',
                    '001038125012': 'ss1'
                    },
                'long':
                    {'M01': 'dm1',
                     'M02': 'kc1',
                     'M03': 'dm2',
                     'M04': 'kc2',
                     'M05': 'ck1',
                     'M06': 'md1',
                     'M07': 'md2',
                     'M08': 'ck2',
                     'M09': 'dm1',
                     'M10': 'kc1',
                     'M11': 'dm2',
                     'M12': 'kc2',
                     'M13': 'md1',
                     'M14': 'ck1',
                     'M15': 'md2',
                     'M16': 'ck2',
                     'M17': 'dm1',
                     'M18': 'kc1',
                     'M19': 'dm2',
                     'M20': 'kc2',
                     'M21': 'md1',
                     'M22': 'ck1',
                     'M23': 'md2'
}
                    }


radiusObjects = {'cup': 18, 'flask': 15, 'falcon': 9, 'shaker': 11, 'marble': 7, 'dice': 6}
colorObjects = {'cup': 'gold', 'flask': 'mediumpurple', 'falcon': 'mediumseagreen', 'shaker': 'orchid', 'marble': 'royalblue', 'dice': 'red'}
objectList = ['cup', 'flask', 'falcon', 'shaker', 'marble', 'dice']

colorSap = {'WT': 'dodgerblue', 'Del/+': 'darkorange', '1': 'dodgerblue', '2': 'red'}

sexList = ['female', 'male']
genoList = ['WT', 'Del/+']
configList = ['config1', 'config2']
setupList = ['1', '2']

markerList = {'1': 'o', '2': 'v'} #for the setups
markerListConfig = {'config1': 'o', 'config2': 'v'} #for the setups

xPos = {'male': {'1': 7.5, '2': 10.5},
        'female': {'1': 1.5, '2': 4.5}}
xPosConfig = {'male': {'config1': 1.5, 'config2': 4.5},
        'female': {'config1': 7.5, 'config2': 10.5}}

VIBRISSAE = 3 #estimated size of the vibrissae to determine the contact zone with the object
timeBin = 1 * oneMinute

eventList = {'acquisition': ['SniffLeftFar', 'SniffRightFar', 'SniffLeft', 'SniffRight', 'UpLeft', 'UpRight'], 'test': ['SniffFamiliarFar', 'SniffNewFar', 'SniffFamiliar', 'SniffNew', 'UpFamiliar', 'UpNew']}
colorEvent = {'SniffLeft': 'dodgerblue', 'SniffRight': 'darkorange', 'SniffLeftFar': 'navy', 'SniffRightFar': 'gold', 'UpLeft': 'skyblue', 'UpRight': 'peachpuff',
                          'SniffFamiliar': 'mediumseagreen', 'SniffNew': 'blueviolet', 'SniffFamiliarFar': 'darkgreen', 'SniffNewFar': 'magenta', 'UpFamiliar': 'lightgreen', 'UpNew': 'violet'}


def getColorGeno(geno):
    if geno == 'WT':
        color = 'steelblue'
    else:
        color = 'darkorange'
    return color


def getColorSetup(setup):
    if setup == '1':
        color = 'royalblue'
    else:
        color = 'red'
    return color


def getColorConfig(config):
    if config == 'config1':
        color = 'steelblue'
    else:
        color = 'darkorange'
    return color

def getConfigCat(rfid, exp, organisation):
    configName = organisation[exp][rfid]
    if 'md' in configName:
        config = 'config1'
    elif 'dm' in configName:
        config = 'config1'
    elif 'kc' in configName:
        config = 'config2'
    elif 'ck' in configName:
        config = 'config2'
    return config
