#! /usr/bin/env python3   

from typing import NamedTuple


# =====================================                                                                                                                     
class DataStruct(NamedTuple):
    moduleLabel: str
    lyso: str
    sipm: str
    sipmType: str
    irradiation : str
    temperature: int
    fName: str
    fNamePS: str
    label: str
    stoch_ref: float
    ov_ref: float
    LO: str
    #tau: str                                                                                                                                                 
    marker: int
    color: int

data_structs = []

'''
#LYSO815 HPK_25 um T = -40                                                                                                                                    
data_structs.append(
    DataStruct(
        moduleLabel = 'HPK_2E14_LYSO815_T-40C',
        lyso = 'LYSO815',
        sipm = 'HPK_2E14',
        sipmType = 'HPK-PIT-C25-ES2',
        irradiation = '2E14',
        temperature = -40,
        fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/summaryPlots_HPK_2E14_LYSO815_T-40C.root',
        fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/pulseShape_HPK_2E14_LYSO815',
        label = 'HPK(25#mum,2E14)+LYSO815 T=-40#circC',
        stoch_ref = 30., # tRes for non-irradiated at 1.0 V                                                                                               
        ov_ref    = 1.00,
        LO = 2418, # LO at 3.5 V non-irradiated                                                                                                           
        #tau = 41.4,                                                                                                                                      
        marker = 20,
        color = 4
    )
)


#LYSO815 HPK_25 um T = -35
data_structs.append(
    DataStruct(
        moduleLabel = 'HPK_2E14_LYSO815_T-35C',
        lyso = 'LYSO815',
        sipm = 'HPK_2E14',
        sipmType = 'HPK-PIT-C25-ES2',
        irradiation = '2E14',
        temperature = -35,
        fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/summaryPlots_HPK_2E14_LYSO815_T-35C.root',
        #fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/pulseShape_HPK_2E14_LYSO815',                                                  
        fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/4martina/pulseShapes/pulseShape_HPK_2E14_LYSO815',
        label = 'HPK(25#mum,2E14)+LYSO815 T=-35#circC',
        stoch_ref = 30., # tRes for non-irradiated at 1.0 V                                                                                                             
        ov_ref    = 1.00,
        LO = 2418, # LO at 3.5 V non-irradiated                                                                                                                         
        #tau = 41.4,                                                                                                                                                    
        marker = 20,
        color = 92
    )
)



#LYSO815 HPK_25 um T = -30
data_structs.append(
    DataStruct(
        moduleLabel = 'HPK_2E14_LYSO815_T-30C',
        lyso = 'LYSO815',
        sipm = 'HPK_2E14',
        sipmType = 'HPK-PIT-C25-ES2',
        irradiation = '2E14',
        temperature = -30,
        #fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/summaryPlots_HPK_2E14_LYSO815_T-35C.root',                                       
        #fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/pulseShape_HPK_2E14_LYSO815',                                                  
        fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/4martina/summaryPlots/summaryPlots_HPK_2E14_LYSO815_T-30C.root',
        fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/4martina/pulseShapes/pulseShape_HPK_2E14_LYSO815',
        label = 'HPK(25#mum,2E14)+LYSO815 T=-30C',
        stoch_ref = 30., # tRes for non-irradiated at 1.0 V                                                                                                             
        ov_ref    = 1.00,
        LO = 2418, # LO at 3.5 V non-irradiated                                                                                                                         
        #tau = 41.4,                                                                                                                                                    
        marker = 20,
        color = 2
    )
)


#LYSO825 HPK_20 um T = -40                                                                                                                                    
data_structs.append(
    DataStruct(
        moduleLabel = 'HPK_2E14_LYSO825_T-40C',
        lyso = 'LYSO825',
        sipm = 'HPK_2E14',
        sipmType = 'HPK-PIT-C20-ES2',
        irradiation = '2E14',
        temperature = -40,
        fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/summaryPlots_HPK_2E14_LYSO825_T-40C.root',
        fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/pulseShape_HPK_2E14_LYSO825',
        label = 'HPK(20#mum,2E14)+LYSO825 T=-40#circC',
        stoch_ref = 35., # tRes for non-irradiated at 1.0 V                                                                                               
        ov_ref    = 1.00,
        LO = 2165, # LO at 3.5 V non-irradiated                                                                                                           
        #tau = 41.4,                                                                                                                                      
        marker = 24,
        color = 4
    )
)


#LYSO825 HPK_20 um T = -35                                                                                                                                    
data_structs.append(
    DataStruct(
        moduleLabel = 'HPK_2E14_LYSO825_T-35C',
        lyso = 'LYSO825',
        sipm = 'HPK_2E14',
        sipmType = 'HPK-PIT-C20-ES2',
        irradiation = '2E14',
        temperature = -35,
        fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/summaryPlots_HPK_2E14_LYSO825_T-35C.root',
        fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/pulseShape_HPK_2E14_LYSO825',
        label = 'HPK(20#mum,2E14)+LYSO825 T=-35#circC',
        stoch_ref = 35., # tRes for non-irradiated at 1.0 V                                                                                               
        ov_ref    = 1.00,
        LO = 2165, # LO at 3.5 V non-irradiated                                                                                                           
        #tau = 41.4,                                                                                                                                      
        marker = 24,
        color = 92
    )
)


#LYSO825 HPK_20 um T = -30                                                                                                                                    
data_structs.append(
    DataStruct(
        moduleLabel = 'HPK_2E14_LYSO825_T-30C',
        lyso = 'LYSO825',
        sipm = 'HPK_2E14',
        sipmType = 'HPK-PIT-C20-ES2',
        irradiation = '2E14',
        temperature = -30,
        fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/summaryPlots_HPK_2E14_LYSO825_T-30C.root',
        fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/pulseShape_HPK_2E14_LYSO825',
        label = 'HPK(20#mum,2E14)+LYSO825 T=-30#circC',
        stoch_ref = 35., # tRes for non-irradiated at 1.0 V                                                                                               
        ov_ref    = 1.00,
        LO = 2165, # LO at 3.5 V non-irradiated                                                                                                           
        #tau = 41.4,                                                                                                                                      
        marker = 24,
        color = 2
    )
)

'''

#LYSO819 HPK_25 um T = -32                                                                                                                                    
data_structs.append(
    DataStruct(
        moduleLabel = 'HPK_1E14_LYSO819_T-32C',
        lyso = 'LYSO819',
        sipm = 'HPK_1E14',
        sipmType = 'HPK-PIT-C25-ES2',
        irradiation = '1E14',
        temperature = -32,
        fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/summaryPlots_HPK_1E14_LYSO819_T-32C.root',
        fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/pulseShape_HPK_1E14_LYSO819',
        label = 'HPK(25#mum,1E14)+LYSO825 T=-32#circC',
        stoch_ref = 30., # tRes for non-irradiated at 1.0 V                                                                                               
        ov_ref    = 1.00,
        LO = 2400, # LO at 3.5 V non-irradiated ???                                                                                                          
        #tau = 41.4,                                                                                                                                      
        marker = 20,
        color = 4
    )
)

