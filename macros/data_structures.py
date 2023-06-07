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
# LYSO813 HPK 25um non Irr
##########################

# LYSO 813 25 um T = 5C
HPK_nonIrr_LYSO813_Tp5C = DataStruct(
    moduleLabel = 'HPK_nonIrr_LYSO813_T5C',
    lyso = 'LYSO813',
    thickness = 3.00,
    sipmType = 'HPK-PIT-C25-ES2',
    sipm = 'HPK_nonIrr',
    irradiation = '0',
    temperature = 5,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_nonIrr_LYSO813_T5C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_nonIrr_LYSO813',
    plotLabel = 'HPK(25#mum) - Type2 - T=5#circC (TOFHIR2X)',
    ov_ref = 3.50,
    stoch_ref = 30., 
    LO = 2250,
    marker = 20,
    color = 98
)


# LYSO 813 25 um T = -30
HPK_nonIrr_LYSO813_Tm30C = DataStruct(
    moduleLabel = 'HPK_nonIrr_LYSO813_T-30C',
    lyso = 'LYSO813',
    thickness = 3.00,
    sipm = 'HPK_nonIrr',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '0',
    temperature = -30,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_nonIrr_LYSO813_T-30C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_nonIrr_LYSO813',
    #plotLabel = 'HPK(25#mum) - Type2 - T=-30#circC',
    plotLabel = 'HPK(25#mum) T=-30#circC (TOFHIR2X)',
    ov_ref = 3.50,
    stoch_ref = 30.,
    LO = 2250,
    marker = 20,
    color = 4
)

# LYSO 813 25 um T = -15C
HPK_nonIrr_LYSO813_Tm15C = DataStruct(
    moduleLabel = 'HPK_nonIrr_LYSO813_T-15C',
    lyso = 'LYSO813',
    thickness = 3.00,
    sipm = 'HPK_nonIrr',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '0',
    temperature = -15,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_nonIrr_LYSO813_T-15C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_nonIrr_LYSO813',
    plotLabel = 'HPK(25#mum) - Type2 - T=-15#circC',
    ov_ref = 3.50,
    stoch_ref = 30.,
    LO = 2250,
    marker = 20,
    color = 8
)

# LYSO 813 25 um T = 0C
HPK_nonIrr_LYSO813_T0C = DataStruct(
    moduleLabel = 'HPK_nonIrr_LYSO813_T0C',
    lyso = 'LYSO813',
    thickness = 3.00,
    sipm = 'HPK_nonIrr',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '0',
    temperature = 0,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_nonIrr_LYSO813_T0C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_nonIrr_LYSO813',
    plotLabel = 'HPK(25#mum) - Type2 - T=0#circC',
    ov_ref = 3.50,
    stoch_ref = 30.,
    LO = 2250,
    marker = 20,
    color = 92
)


# LYSO 813 25 um T = 15C
HPK_nonIrr_LYSO813_Tp15C = DataStruct(
    moduleLabel = 'HPK_nonIrr_LYSO813_T15C',
    lyso = 'LYSO813',
    thickness = 3.00,
    sipm = 'HPK_nonIrr',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '0',
    temperature = 15,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_nonIrr_LYSO813_T15C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_nonIrr_LYSO813',
    plotLabel = 'HPK(25#mum) - Type2 - T=15#circC',
    ov_ref = 3.50,
    stoch_ref = 30.,
    LO = 2250,
    marker = 20,
    color = 2
)


#######################
# LYSO815 HPK 25um 2E14
#######################
#LYSO815 HPK_25 um T = -40                                                                                                                                    
HPK_2E14_LYSO815_Tm40C = DataStruct(
    moduleLabel = 'HPK_2E14_LYSO815_T-40C',
    lyso = 'LYSO815',
    thickness = 3.00,
    sipm = 'HPK_2E14',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '2E14',
    temperature = -40,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_2E14_LYSO815_T-40C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_2E14_LYSO815',
    plotLabel = 'HPK(25#mum,2E14) - Type2 - T=-40#circC',
    stoch_ref = 30., # tRes for non-irradiated at 1.0 V                                                                                               
    ov_ref    = 1.00,
    LO = 2250, # LO at 3.5 V non-irradiated                                                                                                           
    marker = 20,
    color = 4
)

#LYSO815 HPK_25 um T = -35
HPK_2E14_LYSO815_Tm35C = DataStruct(
    moduleLabel = 'HPK_2E14_LYSO815_T-35C',
    lyso = 'LYSO815',
    thickness = 3.00,
    sipm = 'HPK_2E14',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '2E14',
    temperature = -35,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_2E14_LYSO815_T-35C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/4martina/pulseShapes/pulseShape_HPK_2E14_LYSO815',
    plotLabel = 'HPK(25#mum,2E14) - Type2 - T=-35#circC',
    stoch_ref = 30., # tRes for non-irradiated at 1.0 V                                                                                                             
    ov_ref    = 1.00,
    LO = 2250, # LO at 3.5 V non-irradiated                                                                                                                         
    marker = 20,
    color = 92
    #color = 1
)


#LYSO815 HPK_25 um T = -30
HPK_2E14_LYSO815_Tm30C = DataStruct(
    moduleLabel = 'HPK_2E14_LYSO815_T-30C',
    lyso = 'LYSO815',
    thickness = 3.00,
    sipm = 'HPK_2E14',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '2E14',
    temperature = -30,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/4martina/summaryPlots/summaryPlots_HPK_2E14_LYSO815_T-30C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/4martina/pulseShapes/pulseShape_HPK_2E14_LYSO815',
    plotLabel = 'HPK(25#mum,2E14) - Type2 - T=-30#circC',
    stoch_ref = 30., # tRes for non-irradiated at 1.0 V                                                                                                             
    ov_ref    = 1.00,
    LO = 2250, # LO at 3.5 V non-irradiated                                                                                                                         
    marker = 20,
    color = 2
)


#######################
# LYSO825 HPK 20um 2E14
#######################
#LYSO825 HPK_20 um T = -40                                                                                                                                    
HPK_2E14_LYSO825_Tm40C = DataStruct(
    moduleLabel = 'HPK_2E14_LYSO825_T-40C',
    lyso = 'LYSO825',
    thickness = 3.00,
    sipm = 'HPK_2E14',
    sipmType = 'HPK-PIT-C20-ES2',
    irradiation = '2E14',
    temperature = -40,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_2E14_LYSO825_T-40C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_2E14_LYSO825',
    plotLabel = 'HPK(20#mum,2E14) - Type2 - T=-40#circC',
    stoch_ref = 35., # tRes for non-irradiated at 1.0 V                                                                                               
    ov_ref    = 1.00,
    LO = 2050, # LO at 3.5 V non-irradiated                                                                                                           
    marker = 24,
    color = 4
)

#LYSO825 HPK_20 um T = -35                                                                                                                                    
HPK_2E14_LYSO825_Tm35C = DataStruct(
    moduleLabel = 'HPK_2E14_LYSO825_T-35C',
    lyso = 'LYSO825',
    sipm = 'HPK_2E14',
    thickness = 3.00,
    sipmType = 'HPK-PIT-C20-ES2',
    irradiation = '2E14',
    temperature = -35,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_2E14_LYSO825_T-35C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_2E14_LYSO825',
    plotLabel = 'HPK(20#mum,2E14) - Type2 - T=-35#circC',
    stoch_ref = 35., # tRes for non-irradiated at 1.0 V                                                                                               
    ov_ref    = 1.00,
    LO = 2050, # LO at 3.5 V non-irradiated                                                                                                           
    marker = 24,
    color = 92
)

#LYSO825 HPK_20 um T = -30                                                                                                                                    
HPK_2E14_LYSO825_Tm30C = DataStruct(
    moduleLabel = 'HPK_2E14_LYSO825_T-30C',
    lyso = 'LYSO825',
    thickness = 3.00,
    sipm = 'HPK_2E14',
    sipmType = 'HPK-PIT-C20-ES2',
    irradiation = '2E14',
    temperature = -30,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_2E14_LYSO825_T-30C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_2E14_LYSO825',
    plotLabel = 'HPK(20#mum,2E14) - Type2 - T=-30#circC',
    stoch_ref = 35., # tRes for non-irradiated at 1.0 V                                                                                               
    ov_ref    = 1.00,
    LO = 2050, # LO at 3.5 V non-irradiated                                                                                                           
    marker = 24,
    color = 2
)



#######################
# LYSO819 HPK 25um 1E14
#######################
#LYSO819 HPK_25 um T = -22                                                                                                                                    
HPK_1E14_LYSO819_Tm22C = DataStruct(
    moduleLabel = 'HPK_1E14_LYSO819_T-22C',
    lyso = 'LYSO819',
    thickness = 3.75,  
    sipm = 'HPK_1E14',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '1E14',
    temperature = -22,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_1E14_LYSO819_T-22C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_1E14_LYSO819',
    plotLabel = 'HPK(25#mum,1E14) - Type1 - T=-22#circC',
    stoch_ref = 28., # tRes for non-irradiated at 1.0 V                                                                                               
    ov_ref    = 1.00,
    LO = 2410, # LO at 3.5 V non-irradiated ???                                                                                                          
    marker = 21,
    color = 2
)

#LYSO819 HPK_25 um T = -27
HPK_1E14_LYSO819_Tm27C = DataStruct(
    moduleLabel = 'HPK_1E14_LYSO819_T-27C',
    lyso = 'LYSO819',
    thickness = 3.75,
    sipm = 'HPK_1E14',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '1E14',
    temperature = -27,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_1E14_LYSO819_T-27C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_1E14_LYSO819',
    plotLabel = 'HPK(25#mum,1E14) - Type1 - T=-27#circC',
    stoch_ref = 28., # tRes for non-irradiated at 1.0 V 
    ov_ref    = 1.00,
    LO = 2410, # LO at 3.5 V non-irradiated ???                                                                                                          
    marker = 21,
    color = 92
)

#LYSO819 HPK_25 um T = -32                                                                                                                                    
HPK_1E14_LYSO819_Tm32C = DataStruct(
    moduleLabel = 'HPK_1E14_LYSO819_T-32C',
    lyso = 'LYSO819',
    thickness = 3.75,
    sipm = 'HPK_1E14',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '1E14',
    temperature = -32,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_1E14_LYSO819_T-32C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_1E14_LYSO819',
    plotLabel = 'HPK(25#mum,1E14) - Type1 - T=-32#circC',
    stoch_ref = 28., # tRes for non-irradiated at 1.0 V                                                                                               
    ov_ref    = 1.00,
    LO = 2410, # LO at 3.5 V non-irradiated ???                                                                                                          
    marker = 21,
    color = 8
)

#LYSO819 HPK_25 um T = -37
HPK_1E14_LYSO819_Tm37C = DataStruct(
    moduleLabel = 'HPK_1E14_LYSO819_T-37C',
    lyso = 'LYSO819',
    thickness = 3.75,
    sipm = 'HPK_1E14',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '1E14',
    temperature = -37,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_1E14_LYSO819_T-37C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_1E14_LYSO819',
    plotLabel = 'HPK(25#mum,1E14) - Type1 - T=-37#circC',
    stoch_ref = 28., # tRes for non-irradiated at 1.0 V                                                                                               
    ov_ref    = 1.00,
    LO = 2410, # LO at 3.5 V non-irradiated ???                                                                                                          
    marker = 21,
    color = 4
)


#######################
# LYSO829 HPK 25um 1E13
#######################
HPK_1E13_LYSO829_Tm32C = DataStruct(
    moduleLabel = 'HPK_1E13_LYSO829_T-32C',
    lyso = 'LYSO829',
    thickness = 3.75,
    sipm = 'HPK_1E13',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '1E13',
    temperature = -32,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_1E13_LYSO829_T-32C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_1E13_LYSO829',
    plotLabel = 'HPK(25#mum,1E13) - Type1 - T=-32#circC',
    stoch_ref = 28., # tRes for non-irradiated at 1.0 V                                                                                               
    ov_ref    = 1.00,
    LO = 2410, # LO at 3.5 V non-irradiated ???                                                                                                          
    marker = 22,
    color = 4
)

#LYSO829 HPK_25 um T = -19  1E13 T1
HPK_1E13_LYSO829_Tm19C = DataStruct(
    moduleLabel = 'HPK_1E13_LYSO829_T-19C',
    lyso = 'LYSO829',
    thickness = 3.75,
    sipm = 'HPK_1E13',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '1E13',
    temperature = -19,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_1E13_LYSO829_T-19C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_1E13_LYSO829',
    plotLabel = 'HPK(25#mum,1E13) - Type1 - T=-19#circC',
    stoch_ref = 28., # tRes for non-irradiated at 1.0 V                                                                                               
    ov_ref    = 1.00,
    LO = 2410, # LO at 3.5 V non-irradiated ???                                                                                                          
    marker = 22,
    color = 8
)

#LYSO829 HPK_25 um T = 0C  1E13 T1 
HPK_1E13_LYSO829_T0C = DataStruct(
    moduleLabel = 'HPK_1E13_LYSO829_T0C',
    lyso = 'LYSO829',
    thickness = 3.75,
    sipm = 'HPK_1E13',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '1E13',
    temperature = 0,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_1E13_LYSO829_T0C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_1E13_LYSO829',
    plotLabel = 'HPK(25#mum,1E13) - Type1 - T=0#circC',
    stoch_ref = 28., # tRes for non-irradiated at 1.0 V                                                                                               
    ov_ref    = 1.00,
    LO = 2410, # LO at 3.5 V non-irradiated ???                                                                                                          
    marker = 22,
    color = 92
)

#LYSO829 HPK_25 um T = 12C  1E13 T1
HPK_1E13_LYSO829_Tp12C = DataStruct(
    moduleLabel = 'HPK_1E13_LYSO829_T12C',
    lyso = 'LYSO829',
    thickness = 3.75,
    sipm = 'HPK_1E13',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '1E13',
    temperature = 12,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_1E13_LYSO829_T12C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/pulseShape_HPK_1E13_LYSO829',
    plotLabel = 'HPK(25#mum,1E13) - Type1 - T=12#circC',
    stoch_ref = 28., # tRes for non-irradiated at 1.0 V                                                                                               
    ov_ref    = 1.00,
    LO = 2410, # LO at 3.5 V non-irradiated ???                                                                                                          
    marker = 22,
    color = 2
)


###################################
###################################
#TOFHIR2C
###################################
###################################



###################################
#LYSO813 HPK_25 um TOFHIR2C 
###################################
HPK_nonIrr_LYSO813_Tp5C_TOFHIR2C = DataStruct(
    moduleLabel = 'HPK_nonIrr_LYSO813_T5C_TOFHIR2C',
    lyso = 'LYSO813',
    thickness = 3.00,
    sipm = 'HPK_nonIrr',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '0',
    temperature = 5,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2C/summaryPlots_HPK_nonIrr_LYSO813_T5C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2C/pulseShape_HPK_nonIrr_LYSO813',
    plotLabel = 'HPK(25#mum)  T=5#circC (TOFHIR2C)',
    ov_ref = 3.50,
    stoch_ref = 30., 
    LO = 2250,
    marker = 24,
    color = 98
)

HPK_nonIrr_LYSO813_Tm30C_TOFHIR2C = DataStruct(
    moduleLabel = 'HPK_nonIrr_LYSO813_T-30C_TOFHIR2C',
    lyso = 'LYSO813',
    thickness = 3.00,
    sipm = 'HPK_nonIrr',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '0',
    temperature = -30,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2C/summaryPlots_HPK_nonIrr_LYSO813_T-30C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2C/pulseShape_HPK_nonIrr_LYSO813',
    plotLabel = 'HPK(25#mum) T=-30#circC (TOFHIR2C)',
    ov_ref = 3.50,
    stoch_ref = 30., 
    LO = 2250,
    marker = 24,
    color = 4
)

###################################
#LYSO815 HPK_25 um T = -35 TOFHIR2C
###################################

HPK_2E14_LYSO815_Tm35C_TOFHIR2C = DataStruct(
    moduleLabel = 'HPK_2E14_LYSO815_T-35C_TOFHIR2C',
    lyso = 'LYSO815',
    thickness = 3.00,
    sipm = 'HPK_2E14',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '2E14',
    temperature = -35,
    fName = '/afs/cern.cch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2C/summaryPlots_HPK_2E14_LYSO815_T-35C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2C/pulseShape_HPK_2E14_LYSO815',
    plotLabel = 'HPK(25#mum,2E14) - T=-35#circC (TOFHIR2C)',
    stoch_ref = 30., # tRes for non-irradiated at 1.0 V
    ov_ref    = 1.00,
    LO = 2250, # LO at 3.5 V non-irradiated
    marker = 20,
    color = 93
)

HPK_2E14_LYSO815_Tm30C_TOFHIR2C = DataStruct(
    moduleLabel = 'HPK_2E14_LYSO815_T-30C_TOFHIR2C',
    lyso = 'LYSO815',
    thickness = 3.00,
    sipm = 'HPK_2E14',
    sipmType = 'HPK-PIT-C25-ES2',
    irradiation = '2E14',
    temperature = -30,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2C/summaryPlots_HPK_2E14_LYSO815_T-30C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2C/pulseShape_HPK_2E14_LYSO815',
    plotLabel = 'HPK(25#mum,2E14) - Type2 - T=-30#circC (TOFHIR2C)',
    stoch_ref = 30., # tRes for non-irradiated at 1.0 V 
    ov_ref    = 1.00,
    LO = 2250, # LO at 3.5 V non-irradiated
    marker = 20,
    color = 2
)

###################################
#LYSO825 HPK_20 um T = -35 TOFHIR2C
###################################
HPK_2E14_LYSO825_Tm35C_TOFHIR2C = DataStruct(
    moduleLabel = 'HPK_2E14_LYSO825_T-35C_TOFHIR2C',
    lyso = 'LYSO825',
    sipm = 'HPK_2E14',
    thickness = 3.00,
    sipmType = 'HPK-PIT-C20-ES2',
    irradiation = '2E14',
    temperature = -35,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2C/summaryPlots_HPK_2E14_LYSO825_T-35C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2C/pulseShape_HPK_2E14_LYSO825',
    plotLabel = 'HPK(20#mum, 2E14) - T=-35#circC (TOFHIR2C)',
    stoch_ref = 35., # tRes for non-irradiated at 1.0 V
    ov_ref    = 1.00,
    LO = 2050, # LO at 3.5 V non-irradiated
    marker = 24,
    color = 93                                                                                                                                                           
)                                                                                                                                                                        


###################################
#LYSO844 HPK_15 um T = -30 TOFHIR2C
###################################
HPK_1E14_LYSO844_Tm30C_TOFHIR2C = DataStruct(
    moduleLabel = 'HPK_1E14_LYSO844_T-30C_TOFHIR2C',
    lyso = 'LYSO844',
    sipm = 'HPK_1E14',
    thickness = 3.00,
    sipmType = 'HPK-MS',
    irradiation = '1E14',
    temperature = -30,
    fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2C/summaryPlots_HPK_1E14_LYSO844_T-30C.root',
    fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2C/pulseShape_HPK_1E14_LYSO844',
    plotLabel = 'HPK(15#mum) - T=-30#circC (TOFHIR2C)',
    stoch_ref = 35., # tRes for non-irradiated at 1.0 V
    ov_ref    = 1.50,
    LO = 1250, # LO at 3.5 V non-irradiated
    marker = 20,
    color = 2                                                                                                                                                           
)                                                                                                                                                                        




