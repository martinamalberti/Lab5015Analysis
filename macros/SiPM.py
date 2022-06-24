#! /usr/bin/env python
import math

def PDE(ov, sipm, irr='0'):
    k = 1.
    if (irr == '2E14' and 'HPK' in sipm): k = 0.78 # 22% PDE reduction for HPK SiPMs irradiated 2E14   
    if (irr == '1E14' and 'HPK' in sipm): k = 0.89 # 11% PDE reduction for HPK SiPMs irradiated 1E14 ?(assume that for 1E14 is half of 2E14) 
    if ('HPK' in sipm):
        return k * 1.0228 * 0.384 * ( 1. - math.exp(-1.*0.583*ov) ) # 1.0228 factor to account for LYSO emission spectrum
    # FBK-MS
    #if ('FBK' in sipm):
    #    return k * 0.8847*0.466 * ( 1. - math.exp(-1.*0.314*ov) ) # 0.8847 factor to account for LYSO emission spectrum
    #FBK W4C
    if ('FBK' in sipm):
        return k * 0.490 * ( 1. - math.exp(-1.*0.225*ov) )/1.071 # 1.071 factor to account for bech calib, convolution PDE with LYSO already accounted for

def Gain(ov, sipm, irr='0'):
    k = 1.
    if (irr == '2E14' and 'HPK' in sipm): k = 0.92 # gain reduction for HPK 2E14 irradiated SiPMs 
    if (irr == '1E14' and 'HPK' in sipm): k = 0.96 # gain reduction for HPK 2E14 irradiated SiPMs (assume that for 1E14 is half of 2E14)
    if ('HPK' in sipm):
        return k*(36890. + 97602.*ov) # HPK
    # FBK-MS
    #if ('FBK' in sipm):
    #    return k*(50739. + 95149.*ov) # FBK-MS
    # FBK-W4C 
    if ('FBK' in sipm):
        return 91541.7*(ov+0.408182) # FBK-W4C
    
def sigma_noise(sr):
    noise_single = math.sqrt( pow(420./sr,2) + 16.7*16.7 )
    return noise_single / math.sqrt(2)
                                                                                    
                            
