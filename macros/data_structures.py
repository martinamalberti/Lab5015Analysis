#! /usr/bin/env python3   

from typing import NamedTuple


# =====================================                                                                                                                     
class DataStruct(NamedTuple):
    moduleLabel: str
    lyso: str
    sipm: str
    thickness: str
    sipmType: str
    irradiation : str
    temperature: int
    fName: str
    fNamePS: str
    plotLabel: str
    stoch_ref: float
    ov_ref: float
    LO: str
    #tau: str                                                                                                                                                 
    marker: int
    color: int

data_structs = []

##########################
##########################
#  TOFHIR2X
##########################
##########################

##########################
# LYSO528 HPK 15um non-irr
##########################

# LYSO 528 15um T = 10C
HPK_nonIrr_LYSO528_Tp10C = DataStruct(
    moduleLabel = 'HPK_nonIrr_LYSO528_T10C',
    lyso = 'LYSO800',
    thickness = 3.00,
    sipmType = 'HPK-MS',
    sipm = 'HPK_nonIrr',
    irradiation = '0',
    temperature = 10,
    fName = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_Jun2022/ANALYSIS/moduleCharacterization/summaryPlots_HPK_nonIrr_LYSO528_T10C.root',
    fNamePS = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_Jun2022/ANALYSIS/pulseShapes/pulseShape_HPK_nonIrr_LYSO528',
    plotLabel = 'HPK(15#mum) - Type2 - T=10#circC (TOFHIR2X)',
    ov_ref = 3.50,
    stoch_ref = 30., 
    LO = 1300,
    marker = 20,
    color = 4
)

##########################
# LYSO800 FBK 15um non-irr
##########################

# LYSO 800 15um T = 10C
FBK_nonIrr_LYSO800_Tp10C = DataStruct(
    moduleLabel = 'FBK_nonIrr_LYSO800_T10C',
    lyso = 'LYSO800',
    thickness = 3.00,
    sipmType = 'FBK-W4C',
    sipm = 'FBK_nonIrr',
    irradiation = '0',
    temperature = 10,
    fName = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_Jun2022/ANALYSIS/moduleCharacterization/summaryPlots_FBK_nonIrr_LYSO800_T10C.root',
    fNamePS = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_Jun2022/ANALYSIS/pulseShapes/pulseShape_FBK_nonIrr_LYSO800',
    plotLabel = 'FBK(15#mum) - Type2 - T=10#circC (TOFHIR2X)',
    ov_ref = 3.50,
    stoch_ref = 30., 
    LO = 1042,
    marker = 20,
    color = 2
)

##########################
# LYSO796 HPK 15um 2E14
##########################

# LYSO 796 15um T = -35C
HPK_2E14_LYSO796_Tm35C = DataStruct(
    moduleLabel = 'HPK_2E14_LYSO796_T-35C',
    lyso = 'LYSO796',
    thickness = 3.00,
    sipmType = 'HPK-MS',
    sipm = 'HPK_2E14',
    irradiation = '2E14',
    temperature = -35,
    fName = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_Jun2022/ANALYSIS/moduleCharacterization/summaryPlots_HPK_2E14_LYSO796_T-35C.root',
    fNamePS = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_Jun2022/ANALYSIS/pulseShapes/pulseShape_HPK_2E14_LYSO796',
    plotLabel = 'HPK(15#mum) - Type2 - T=-35#circC (TOFHIR2X)',
    ov_ref = 1.50,
    stoch_ref = 37., 
    LO = 1250,
    marker = 20,
    color = 2
)


# LYSO 796 15um T = -40C
HPK_2E14_LYSO796_Tm40C = DataStruct(
    moduleLabel = 'HPK_2E14_LYSO796_T-40C',
    lyso = 'LYSO796',
    thickness = 3.00,
    sipmType = 'HPK-MS',
    sipm = 'HPK_2E14',
    irradiation = '2E14',
    temperature = -40,
    fName = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_Jun2022/ANALYSIS/moduleCharacterization/summaryPlots_HPK_2E14_LYSO796_T-40C.root',
    fNamePS = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_Jun2022/ANALYSIS/pulseShapes/pulseShape_HPK_2E14_LYSO796',
    plotLabel = 'HPK(15#mum) - Type2 - T=-40#circC (TOFHIR2X)',
    ov_ref = 1.50,
    stoch_ref = 37., 
    LO = 1250,
    marker = 20,
    color = 4
)




# LYSO 797 15um T = -35C
FBK_2E14_LYSO797_Tm35C = DataStruct(
    moduleLabel = 'FBK_2E14_LYSO797_T-35C',
    lyso = 'LYSO797',
    thickness = 3.00,
    sipmType = 'FBK-W4C',
    sipm = 'FBK_2E14',
    irradiation = '2E14',
    temperature = -35,
    fName = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_Jun2022/ANALYSIS/moduleCharacterization/summaryPlots_FBK_2E14_LYSO797_T-35C.root',
    fNamePS = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_Jun2022/ANALYSIS/pulseShapes/pulseShape_FBK_2E14_LYSO797',
    plotLabel = 'FBK(15#mum) - Type2 - T=-35#circC (TOFHIR2X)',
    ov_ref = 1.80,
    stoch_ref = 45., 
    LO = 1050,
    marker =25,
    color = 2
)


# LYSO 797 15um T = -40C
FBK_2E14_LYSO797_Tm40C = DataStruct(
    moduleLabel = 'FBK_2E14_LYSO797_T-40C',
    lyso = 'LYSO797',
    thickness = 3.00,
    sipmType = 'FBK-W4C',
    sipm = 'FBK_2E14',
    irradiation = '2E14',
    temperature = -40,
    fName = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_Jun2022/ANALYSIS/moduleCharacterization/summaryPlots_FBK_2E14_LYSO797_T-40C.root',
    fNamePS = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_Jun2022/ANALYSIS/pulseShapes/pulseShape_FBK_2E14_LYSO797',
    plotLabel = 'FBK(15#mum) - Type2 - T=-40#circC (TOFHIR2X)',
    ov_ref = 1.80,
    stoch_ref = 45., 
    LO = 1050,
    marker = 21,
    color = 4
)
