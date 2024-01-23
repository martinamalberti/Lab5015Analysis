#! /usr/bin/env python
import math

def PDE(sipm_type, ov, irr='0'):
    k = 1.
    if (irr == '2E14' and 'HPK-MS' in sipm_type): k = 0.78 # 22% PDE reduction for HPK SiPMs irradiated 2E14   
    if (irr == '1E14' and 'HPK-MS' in sipm_type): k = 0.89 # 11% PDE reduction for HPK SiPMs irradiated 1E14 ?(assume that for 1E14 is half of 2E14) 
    if (irr == '2E14' and 'HPK-PIT' in sipm_type): k = 0.85 # 15% PDE reduction for HPK SiPMs irradiated 2E14  - large cell-size 
    if (irr == '1E14' and 'HPK-PIT' in sipm_type): k = 0.925 # %7.5% PDE reduction for HPK SiPMs irradiated 1E14 ?(assume that for 1E14 is half of 2E14) 

    if   (sipm_type == "HPK-MS"): 
        return k * 0.389 * ( 1. - math.exp(-1.*0.593*ov) )
    elif (sipm_type == "FBK-MS"): 
        return k * 0.419907 * ( 1. - math.exp(-1.*0.3046*ov) )
    elif (sipm_type == "FBK-W4S"): 
        return k * 0.411 * ( 1. - math.exp(-1.*0.191*ov) )/1.071
    elif (sipm_type == "FBK-W4C"): 
        return k * 0.490 * ( 1. - math.exp(-1.*0.225*ov) )/1.071
    elif (sipm_type == "HPK-PIT-C20-ES2"):
        return k * 0.576 * ( 1. - math.exp(-1.*0.625*ov) )
    elif (sipm_type == "HPK-PIT-C25-ES2"):
        return k * 0.638 * ( 1. - math.exp(-1.*0.651*ov) )
    elif (sipm_type == "HPK-PIT-C20-ES3"):
        return k * 0.568 * ( 1. - math.exp(-1.*0.588*ov) )
    elif (sipm_type == "HPK-PIT-C25-ES3"):
        return k * 0.638 * ( 1. - math.exp(-1.*0.589*ov) )
    elif (sipm_type == "HPK-PIT-C30-ES3"):
        return k * 0.653 * ( 1. - math.exp(-1.*0.728*ov) )
        
    else:
        print("error!!! PDE not specified!")
        #return 0.389 * ( 1. - math.exp(-1.*0.593*ov) )
        return 0


def Gain(sipm_type, ov, irr='0'):

    k = 1.
    if (irr == '2E14' and 'HPK-MS' in sipm_type): k = 0.92 # gain reduction for HPK 2E14 irradiated SiPMs 
    if (irr == '1E14' and 'HPK-MS' in sipm_type): k = 0.96 # gain reduction for HPK 1E14 irradiated SiPMs (assume that for 1E14 is half of 2E14)
    if (irr == '2E14' and 'HPK-PIT' in sipm_type): k = 0.95 # gain reduction for HPK 2E14 irradiated SiPMs - large cells
    if (irr == '1E14' and 'HPK-PIT' in sipm_type): k = 0.975 # gain reduction for HPK 1E14 irradiated SiPMs (assume that for 1E14 is half of 2E14) - large cells

    if   (sipm_type == "HPK-MS"): 
        return k * (97602.9*(ov+0.377962))
    elif (sipm_type == "FBK-MS"): 
        return k * (94954.6*(ov+0.512167))
    elif (sipm_type == "FBK-W4S"): 
        return k * (91541.7*(ov+0.408182))
    elif (sipm_type == "FBK-W4C"): 
        return k * (91541.7*(ov+0.408182))
    elif   (sipm_type == "HPK-PIT-C20-ES2"): 
        return k * (6.234E04 + 1.787E05*ov)
    elif   (sipm_type == "HPK-PIT-C25-ES2"): 
        return k * (7.044E04 + 2.895E05*ov)
    elif   (sipm_type == "HPK-PIT-C20-ES3"): 
        return k * (5.731E04 + 1.759E05*ov)
    elif   (sipm_type == "HPK-PIT-C25-ES3"): 
        return k * (7.857E04 + 2.836E05*ov)
    elif   (sipm_type == "HPK-PIT-C30-ES3"): 
        return k * (9.067E04 + 4.020E05*ov)

    else:
        print("error!!! Gain not specified!")
        return 1
        
    #        return 36890.225 + 97602.904*ov
    

        
def ECF(sipm_type, ov):
    if   (sipm_type == "HPK-MS"): 
        return 1 + 0.000790089*ov + 0.00226734*ov*ov
    elif (sipm_type == "FBK-MS"): 
        return 1 + 0.00215668*ov +0.00303006*ov*ov
    elif (sipm_type == "FBK-W4S"): 
        return 1 +  0.00215668*ov +0.00303006*ov*ov
    elif (sipm_type == "FBK-W4C"): 
        return 1 +  0.00215668*ov +0.00303006*ov*ov
    elif   ("HPK-PIT" in sipm_type): 
        return 1 + 0.000790089*ov + 0.00226734*ov*ov # place-holder
        
    else:
        print("error!!! ECF not specified!")
        return 100 
        
        #return 1. -2.60076e-02*ov + 9.10258e-03*ov*ov
        #return 1.




def GetSaturationCorrection(Ncells, Edep, LY, PDE, LCE):
    Npe    = Edep * LY * PDE * LCE
    Nfired = Ncells * (1 - math.exp(-Npe/Ncells))
    k = Nfired/Npe
    return k

def fit_PDE(x, par):
        xx = x[0]
        return par[0] * ( PDE(sipm_type, xx-par[1]) )

def fit_PDE_ECF_Gain(x, par):
        xx = x[0]
        return par[0] * ( PDE(sipm_type, xx-par[1]) * ECF(sipm_type, xx-par[1]) * Gain(sipm_type, xx-par[1]) )



def sigma_noise(sr, tofhir = '2X'):
    noise_single = math.sqrt( pow(420./sr,2) + 16.7*16.7 )
    if ('2C' in tofhir):
        #noise_single = math.sqrt( pow( 278./pow(sr,0.8)  ,2) + 19.1*19.1 ) 
        noise_single = math.sqrt( pow(463./sr,2) + 19.1*19.1 ) # da fittone Andrea
    return noise_single / math.sqrt(2)
