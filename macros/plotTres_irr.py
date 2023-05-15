#! /usr/bin/env python3
import os
import shutil
import glob
import math
import array
import sys
import time
import argparse
import json                                                                                                                                                                      
from typing import NamedTuple


import ROOT
import CMS_lumi, tdrstyle

#set the tdr style
tdrstyle.setTDRStyle()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(1)
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetLabelSize(0.055,'X')
ROOT.gStyle.SetLabelSize(0.055,'Y')
ROOT.gStyle.SetTitleSize(0.06,'X')
ROOT.gStyle.SetTitleSize(0.06,'Y')
ROOT.gStyle.SetTitleOffset(1.05,'X')
ROOT.gStyle.SetTitleOffset(1.1,'Y')
ROOT.gStyle.SetLegendFont(42)
ROOT.gStyle.SetLegendTextSize(0.045)
ROOT.gStyle.SetPadTopMargin(0.07)
ROOT.gStyle.SetPadRightMargin(0.1)

ROOT.gROOT.SetBatch(True)
#ROOT.gROOT.SetBatch(False)
ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.gStyle.SetOptStat(0)
#ROOT.gStyle.SetOptFit(0111)

from SiPM import *
from VovsEff import *



def getSlewRateFromPulseShape(g1, timingThreshold, npoints, gtemp, canvas=None):
    if ( g1.GetN() < npoints): return (-1, -1)
    # find index at the timing threshold
    itiming = 0
    for i in range(0,g1.GetN()):
        if (round(g1.GetY()[i]/0.313) == timingThreshold):
            itiming = i
            break

    ifirst = ROOT.TMath.LocMin(g1.GetN(), g1.GetX())
    imin = max(0, itiming-2)
    if ( imin >= 0 and g1.GetX()[imin+1] < g1.GetX()[imin] ): imin = ifirst
    tmin = g1.GetX()[imin]
    tmax = 3
    if ((imin+npoints) < g1.GetN()): 
        tmax = min(g1.GetX()[imin+npoints],3.)
        nmax = imin+npoints+1
    else:
        tmax = 3
        nmax = g1.GetN()
    for i in range(imin, nmax):
        gtemp.SetPoint(gtemp.GetN(), g1.GetX()[i], g1.GetY()[i])
        gtemp.SetPointError(gtemp.GetN()-1, g1.GetErrorX(i), g1.GetErrorY(i))
    fitSR = ROOT.TF1('fitSR', 'pol1', tmin, tmax)
    fitSR.SetLineColor(g1.GetMarkerColor()+1)
    fitSR.SetRange(tmin,tmax)
    fitSR.SetParameters(0, 10)
    fitStatus = int(gtemp.Fit(fitSR, 'QRS+'))
    sr = fitSR.Derivative( g1.GetX()[itiming])
    err_sr = fitSR.GetParError(1)
    if (canvas!=None):
        canvas.cd()
        gtemp.SetMarkerStyle(g1.GetMarkerStyle())
        gtemp.SetMarkerColor(g1.GetMarkerColor())
        gtemp.Draw('psames')
        g1.Draw('psames')
        fitSR.Draw('same')
        canvas.Update()
        #ps = g1.FindObject("stats")
        ps = gtemp.FindObject("stats")
        ps.SetTextColor(g1.GetMarkerColor())
        if ('L' in g1.GetName()):
            ps.SetY1NDC(0.85) # new y start position
            ps.SetY2NDC(0.95)# new y end position
        if ('R' in g1.GetName()):
            ps.SetY1NDC(0.73) # new y start position
            ps.SetY2NDC(0.83)# new y end position

    return(sr,err_sr)


def findTimingThreshold(g2, ov):
    xmin = 0
    ymin = 9999
    for i in range(0, g2.GetN()):
        y = g2.GetY()[i] #tRes
        x = g2.GetX()[i] #threshold
        # best th < 13 for low OV to avoid cases where MIP peak is cut out by the threshold
        #if ( ov <= 1.50 and x >= 13): continue
        if ( y < ymin):
            ymin = y
            xmin = x 
    return xmin
    


# =====================================
class DataStruct(NamedTuple):
    lyso: str
    sipm: str
    sipmType: str
    irradiation : str
    fName: str
    fNamePS: str
    label: str
    temperature: int
    stoch_ref: float
    ov_ref: float
    LO: str
    #tau: str
    marker: int
    color: int

data_structs = []


#LYSO815 HPK_25 um T = -40 
data_structs.append(
        DataStruct(
            lyso = 'LYSO815',
            sipm = 'HPK_2E14_T-40C',
            sipmType = 'HPK-PIT-C25-ES2',
            irradiation = '2E14',
            fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/summaryPlots_HPK_2E14_LYSO815_T-40C.root',
            fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/pulseShape_HPK_2E14_LYSO815',
            label = 'HPK(25#mum,2E14)+LYSO815',
            temperature = -40,
            stoch_ref = 30., # tRes for non-irradiated at 1.0 V
            ov_ref    = 1.00,
            LO = 2418, # LO at 3.5 V non-irradiated
            #tau = 41.4,
            marker = 20,
            color = 92
        )
)

#LYSO815 HPK_25 um T = -35 
data_structs.append(
        DataStruct(
            lyso = 'LYSO815',
            sipm = 'HPK_2E14_T-35C',
            sipmType = 'HPK-PIT-C25-ES2',
            irradiation = '2E14',
            fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/summaryPlots_HPK_2E14_LYSO815_T-35C.root',
            #fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/pulseShape_HPK_2E14_LYSO815',
            fNamePS = '/afs/cern.ch/user/s/spalluot/public/4martina/pulseShapes/pulseShape_HPK_2E14_LYSO815',
            label = 'HPK(25#mum,2E14)+LYSO815 T=-35C',
            temperature = -35,
            stoch_ref = 30., # tRes for non-irradiated at 1.0 V
            ov_ref    = 1.00,
            LO = 2418, # LO at 3.5 V non-irradiated
            #tau = 41.4,
            marker = 20,
            color = 96
        )
)


#LYSO815 HPK_25 um T = -30
data_structs.append(
        DataStruct(
            lyso = 'LYSO815',
            sipm = 'HPK_2E14_T-30C',
            sipmType = 'HPK-PIT-C25-ES2',
            irradiation = '2E14',
            #fName = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/summaryPlots_HPK_2E14_LYSO815_T-35C.root',
            #fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/pulseShape_HPK_2E14_LYSO815',
            fName = '/afs/cern.ch/user/s/spalluot/public/4martina/summaryPlots/summaryPlots_HPK_2E14_LYSO815_T-30C.root',
            fNamePS = '/afs/cern.ch/user/s/spalluot/public/4martina/pulseShapes/pulseShape_HPK_2E14_LYSO815',
            label = 'HPK(25#mum,2E14)+LYSO815 T=-30C',
            temperature = -30,
            stoch_ref = 30., # tRes for non-irradiated at 1.0 V
            ov_ref    = 1.00,
            LO = 2418, # LO at 3.5 V non-irradiated
            #tau = 41.4,
            marker = 20,
            color = 2
        )
)




# =====================================
# import file with VovEff and DCR
with open('/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_May2023/VovsEff.json', 'r') as f:
    data = json.load(f)       


# =====================================
outdir = '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_irradiated/'
if (os.path.exists(outdir)==False):
    os.mkdir(outdir)
if (os.path.exists(outdir+'/plotsSR')==False):
    os.mkdir(outdir+'/plotsSR/')


outfile   = ROOT.TFile.Open(outdir+'/plots_timeResolution_irradiated_TBMay23.root','recreate')

np = 3
errSRsyst  = 0.10 # error on the slew rate
errPDE     = 0.05 # assumed uncertainty on PDE (5-10%)

g_data = {}
g_data_average = {}

g_Noise_vs_Vov = {}
g_Stoch_vs_Vov = {}
g_DCR_vs_Vov = {}
g_Tot_vs_Vov   = {}

g_Stoch_vs_Npe = {}
g_DCR_vs_Npe = {}

g_bestTh_vs_Vov = {}

g_SR_vs_Vov = {}
g_SR_vs_GainNpe = {}

g_bestTh_vs_bar = {}
g_SR_vs_bar = {}
g_Noise_vs_bar = {}
g_Stoch_vs_bar = {}
g_DCR_vs_bar = {}

g_Tot_vs_SR   = {}

g_data_vs_Npe = {}
g_data_vs_DCR = {}
g_data_vs_GainNpe = {}

bars = {}
Vovs = {}
Npe = {}
gain = {}

for ds in data_structs:
    f = ROOT.TFile.Open(ds.fName)
    print(ds.sipm, ds.fName)

    listOfKeys = [key.GetName().replace('g_deltaT_energyRatioCorr_bestTh_vs_vov_','') for key in ROOT.gDirectory.GetListOfKeys() if ( 'g_deltaT_energyRatioCorr_bestTh_vs_vov_bar' in key.GetName())]
    bars[ds.sipm] = []
    for k in listOfKeys:
        bars[ds.sipm].append( int(k[3:5]) )

    listOfKeys2 = [key.GetName().replace('g_deltaT_energyRatioCorr_bestTh_vs_bar_','') for key in ROOT.gDirectory.GetListOfKeys() if key.GetName().startswith('g_deltaT_energyRatioCorr_bestTh_vs_bar_')]
    Vovs[ds.sipm] = []
    for k in listOfKeys2:
        Vovs[ds.sipm].append( float(k[3:7]) )

    print(bars[ds.sipm])
    print(Vovs[ds.sipm])

    
fPS = {}
f   = {}

for ds in data_structs:
    f[ds.sipm] = ROOT.TFile.Open(ds.fName)
    
    g_data_average[ds.sipm] = f[ds.sipm].Get('g_deltaT_totRatioCorr_bestTh_vs_vov_enBin01_average')

    Npe[ds.sipm] = {}
    gain[ds.sipm] = {}

    g_data[ds.sipm] = {}
    g_Noise_vs_Vov[ds.sipm] = {}
    g_Stoch_vs_Vov[ds.sipm] = {}
    g_DCR_vs_Vov[ds.sipm] = {}
    g_Tot_vs_Vov[ds.sipm] = {}

    g_Tot_vs_SR[ds.sipm] = {}

    g_Stoch_vs_Npe[ds.sipm] = {}
    g_DCR_vs_Npe[ds.sipm] = {}

    g_SR_vs_Vov[ds.sipm] = {}
    g_SR_vs_GainNpe[ds.sipm] = {}
    g_bestTh_vs_Vov[ds.sipm] = {}

    g_SR_vs_bar[ds.sipm] = {}
    g_bestTh_vs_bar[ds.sipm] = {}
    g_Noise_vs_bar[ds.sipm] = {}
    g_Stoch_vs_bar[ds.sipm] = {}
    g_DCR_vs_bar[ds.sipm] = {}

    g_data_vs_Npe[ds.sipm] = ROOT.TGraphErrors()
    g_data_vs_DCR[ds.sipm] = ROOT.TGraphErrors()
    g_data_vs_GainNpe[ds.sipm] = ROOT.TGraphErrors()
    

    fPS[ds.sipm] = {}
    for ov in Vovs[ds.sipm]:
        print(ds.fNamePS+'_Vov%.2f_T%dC.root'%(ov,ds.temperature))
        if (ds.temperature == -35):
            fPS[ds.sipm][ov] = ROOT.TFile.Open(ds.fNamePS+'_Vov%.2f_angle52_T%dC.root'%(ov,ds.temperature))
        else:
            fPS[ds.sipm][ov] = ROOT.TFile.Open(ds.fNamePS+'_Vov%.2f_T%dC.root'%(ov,ds.temperature))


        g_SR_vs_bar[ds.sipm][ov] = ROOT.TGraphErrors()
        g_bestTh_vs_bar[ds.sipm][ov] = ROOT.TGraphErrors()
        g_Noise_vs_bar[ds.sipm][ov] = ROOT.TGraphErrors()
        g_Stoch_vs_bar[ds.sipm][ov] = ROOT.TGraphErrors()
        g_DCR_vs_bar[ds.sipm][ov] = ROOT.TGraphErrors()
        g_Tot_vs_SR[ds.sipm][ov] = ROOT.TGraphErrors()

        
    for bar in bars[ds.sipm]:
        g_data[ds.sipm][bar] = f[ds.sipm].Get('g_deltaT_totRatioCorr_bestTh_vs_vov_bar%02d_enBin01;1'%bar)
        if (g_data[ds.sipm][bar].GetN()==0): 
            print('No data for bar ', bar)
            continue

        g_Noise_vs_Vov[ds.sipm][bar] = ROOT.TGraphErrors()
        g_Stoch_vs_Vov[ds.sipm][bar] = ROOT.TGraphErrors()
        g_DCR_vs_Vov[ds.sipm][bar] = ROOT.TGraphErrors()
        g_Tot_vs_Vov[ds.sipm][bar] = ROOT.TGraphErrors()

        g_Stoch_vs_Npe[ds.sipm][bar] = ROOT.TGraphErrors()
        g_DCR_vs_Npe[ds.sipm][bar] = ROOT.TGraphErrors()

        g_SR_vs_Vov[ds.sipm][bar] = ROOT.TGraphErrors()
        g_SR_vs_GainNpe[ds.sipm][bar] = ROOT.TGraphErrors()
        g_bestTh_vs_Vov[ds.sipm][bar] = ROOT.TGraphErrors()
                   
        for ov in Vovs[ds.sipm]:
            ovEff = getVovEffDCR(data, ds.lyso, ds.sipm, ('%.02f'%ov))[0]
            #if ( ovEff < g_data[ds.sipm][bar].GetX()[0] or ovEff > g_data[ds.sipm][bar].GetX()[g_data[ds.sipm][bar].GetN()-1]): continue
            
            # get measured time resolution
            s_data = g_data[ds.sipm][bar].Eval(ovEff)
            indref = [i for i in range(0, g_data[ds.sipm][bar].GetN()) if g_data[ds.sipm][bar].GetPointX(i) == ovEff]
            if ( len(indref)<1 ): continue
            err_s_data = g_data[ds.sipm][bar].GetErrorY(indref[0])            

            # Npe and Gain at this OVeff
            Npe[ds.sipm][ov]  = 4.2*ds.LO*PDE(ds.sipmType,ovEff,ds.irradiation)/PDE(ds.sipmType,3.50,'0') #LO is referred to 3.50 V OV
            gain[ds.sipm][ov] = Gain(ds.sipmType, ovEff, ds.irradiation)
            # get pulse shapes
            g_psL = fPS[ds.sipm][ov].Get('g_pulseShapeL_bar%02d_Vov%.2f'%(bar,ov))
            g_psR = fPS[ds.sipm][ov].Get('g_pulseShapeR_bar%02d_Vov%.2f'%(bar,ov))
            if (g_psL==None and g_psR==None): 
                print('ciao')
                continue
            if (g_psL!=None): g_psL.SetName('g_pulseShapeL_bar%02d_Vov%.2f_%s'%(bar,ov,ds.sipm))
            if (g_psR!=None): g_psR.SetName('g_pulseShapeR_bar%02d_Vov%.2f_%s'%(bar,ov,ds.sipm))
            timingThreshold = findTimingThreshold(f[ds.sipm].Get('g_deltaT_energyRatioCorr_vs_th_bar%02d_Vov%.2f_enBin01'%(bar,ov)), ovEff)
            srL = -1
            srR = -1
            sr = -1
            err_srL = -1
            err_srR = -1
            c = ROOT.TCanvas('c_%s'%(g_psL.GetName().replace('g_pulseShapeL','pulseShape').replace('Vov%.2f'%ov,'VovEff%.2f'%ovEff)),'',600,600)  
            #hdummy = ROOT.TH2F('hdummy','', 100, min(g_psR.GetX())-1., 30., 100, 0., 15.)
            hdummy = ROOT.TH2F('hdummy','', 100, min(g_psL.GetX())-1., 5, 100, 0., 15.)
            hdummy.GetXaxis().SetTitle('time [ns]')
            hdummy.GetYaxis().SetTitle('amplitude [#muA]')
            hdummy.Draw()
            gtempL = ROOT.TGraphErrors()
            gtempR = ROOT.TGraphErrors()
            
            if (g_psL!=None): 
                srL,err_srL = getSlewRateFromPulseShape(g_psL, timingThreshold, np, gtempL, c)
                #srL_up,err_srL_up = getSlewRateFromPulseShape(g_psL, timingThreshold, np+1, gtempL, c)
                #srL_down,err_srLdown = getSlewRateFromPulseShape(g_psL, timingThreshold, np-1, gtempL, c)
                #err_srL = abs(srL_up-srL_down)
            if (g_psR!=None): 
                srR,err_srR = getSlewRateFromPulseShape(g_psR, timingThreshold, np, gtempR, c) 
                #srR_up,err_srR_up = getSlewRateFromPulseShape(g_psR, timingThreshold, np+1, gtempR, c) 
                #srR_down,err_srR_down = getSlewRateFromPulseShape(g_psR, timingThreshold, np-1, gtempR, c) 
                #err_srR = abs(srR_up-srR_down)
            line = ROOT.TLine(min(g_psL.GetX())-1., timingThreshold*0.313, 30., timingThreshold*0.313)
            line.SetLineStyle(7)
            line.SetLineWidth(2)
            line.SetLineColor(ROOT.kOrange+1)        
            line.Draw('same')
            c.SaveAs(outdir+'/plotsSR/'+c.GetName()+'.png')   
            hdummy.Delete()
            if (srL>0 and srR>0):
                # weighted average
                sr =  ( (srL/(err_srL*err_srL) + srR/(err_srR*err_srR) ) / (1./(err_srL*err_srL) + 1./(err_srR*err_srR) ) )
                errSR = 1./math.sqrt( 1./(err_srL*err_srL)  +  1./(err_srR*err_srR) )
                errSR = errSR
            if (srL>0 and srR<0):
                sr = srL
                errSR = err_srL
            if (srL<0 and srR>0):
                sr = srR
                errSR = err_srR
            if (srL<0 and srR<0): continue
            errSR = math.sqrt(errSR*errSR+errSRsyst*errSRsyst*sr*sr) 

            #print sipm, ov, ovEff, gain, Npe[ds.sipm][ov], srL, srR, sr, errSR
            g_SR_vs_Vov[ds.sipm][bar].SetPoint( g_SR_vs_Vov[ds.sipm][bar].GetN(), ovEff, sr )
            g_SR_vs_Vov[ds.sipm][bar].SetPointError( g_SR_vs_Vov[ds.sipm][bar].GetN()-1, 0, errSR )
            
            g_SR_vs_GainNpe[ds.sipm][bar].SetPoint( g_SR_vs_GainNpe[ds.sipm][bar].GetN(), gain[ds.sipm][ov]*Npe[ds.sipm][ov], sr )
            g_SR_vs_GainNpe[ds.sipm][bar].SetPointError( g_SR_vs_GainNpe[ds.sipm][bar].GetN()-1, 0, errSR )

            g_bestTh_vs_Vov[ds.sipm][bar].SetPoint( g_bestTh_vs_Vov[ds.sipm][bar].GetN(), ovEff, timingThreshold )
            g_bestTh_vs_Vov[ds.sipm][bar].SetPointError( g_bestTh_vs_Vov[ds.sipm][bar].GetN()-1, 0, 0 )
            
            g_SR_vs_bar[ds.sipm][ov].SetPoint( g_SR_vs_bar[ds.sipm][ov].GetN(), bar, sr )
            g_SR_vs_bar[ds.sipm][ov].SetPointError( g_SR_vs_bar[ds.sipm][ov].GetN()-1, 0, errSR )
            
            g_bestTh_vs_bar[ds.sipm][ov].SetPoint( g_bestTh_vs_bar[ds.sipm][ov].GetN(), bar, timingThreshold )
            g_bestTh_vs_bar[ds.sipm][ov].SetPointError( g_bestTh_vs_bar[ds.sipm][ov].GetN()-1, 0, 0)
            
            s_noise = sigma_noise(sr)
            err_s_noise =  0.5*(sigma_noise(sr*(1-errSR/sr))-sigma_noise(sr*(1+errSR/sr)))
            g_Noise_vs_bar[ds.sipm][ov].SetPoint( g_Noise_vs_bar[ds.sipm][ov].GetN(), bar, s_noise )
            g_Noise_vs_bar[ds.sipm][ov].SetPointError( g_Noise_vs_bar[ds.sipm][ov].GetN()-1, 0,  err_s_noise)
            
            g_Noise_vs_Vov[ds.sipm][bar].SetPoint(g_Noise_vs_Vov[ds.sipm][bar].GetN(), ovEff, s_noise)
            g_Noise_vs_Vov[ds.sipm][bar].SetPointError(g_Noise_vs_Vov[ds.sipm][bar].GetN()-1, 0, err_s_noise)
            
            
            # compute s_stoch by scaling the stochastic term measured for non-irradiated SiPMs (40 ps HPK, 45 ps FBK) for sqrt(PDE) 
            alpha = 0.50 
            s_stoch = ds.stoch_ref/pow( PDE(ds.sipmType,ovEff,ds.irradiation)/PDE(ds.sipmType,ds.ov_ref,'0'), alpha )
            # assume 5% uncertainty on PDE...
            s_stoch_up = ds.stoch_ref/pow( PDE(ds.sipmType,ovEff,ds.irradiation)*(1-errPDE)/PDE(ds.sipmType,ds.ov_ref,'0'), alpha  )
            s_stoch_down = ds.stoch_ref/pow( PDE(ds.sipmType,ovEff,ds.irradiation)*(1+errPDE)/PDE(ds.sipmType,ds.ov_ref,'0'), alpha  )
            err_s_stoch = 0.5*(s_stoch_up-s_stoch_down)
            g_Stoch_vs_Vov[ds.sipm][bar].SetPoint(g_Stoch_vs_Vov[ds.sipm][bar].GetN(), ovEff, s_stoch)
            g_Stoch_vs_Vov[ds.sipm][bar].SetPointError(g_Stoch_vs_Vov[ds.sipm][bar].GetN()-1, 0, err_s_stoch)
            g_Stoch_vs_bar[ds.sipm][ov].SetPoint( g_Stoch_vs_bar[ds.sipm][ov].GetN(), bar, s_stoch )
            g_Stoch_vs_bar[ds.sipm][ov].SetPointError( g_Stoch_vs_bar[ds.sipm][ov].GetN()-1, 0,  err_s_stoch)

            # compute sigma_DCR as difference in quadrature between measured tRes and noise, stoch
            if ( s_data*s_data - s_stoch*s_stoch - s_noise*s_noise > 0):
                s_dcr = math.sqrt( s_data*s_data - s_stoch*s_stoch - s_noise*s_noise )
                err_s_dcr = 1./s_dcr * math.sqrt( pow( err_s_data*s_data,2) + pow( err_s_stoch*s_stoch,2) + pow(err_s_noise*s_noise,2))
                g_DCR_vs_Vov[ds.sipm][bar].SetPoint(g_DCR_vs_Vov[ds.sipm][bar].GetN(), ovEff, s_dcr)
                g_DCR_vs_Vov[ds.sipm][bar].SetPointError(g_DCR_vs_Vov[ds.sipm][bar].GetN()-1, 0, err_s_dcr)
                g_DCR_vs_bar[ds.sipm][ov].SetPoint( g_DCR_vs_bar[ds.sipm][ov].GetN(), bar, s_dcr )
                g_DCR_vs_bar[ds.sipm][ov].SetPointError( g_DCR_vs_bar[ds.sipm][ov].GetN()-1, 0,  err_s_dcr)
                
                dcr = getVovEffDCR(data,ds.lyso, ds.sipm,('%.02f'%ov))[1]
                g_DCR_vs_Npe[ds.sipm][bar].SetPoint( g_DCR_vs_Npe[ds.sipm][bar].GetN(), math.sqrt(dcr)/Npe[ds.sipm][ov]/(math.sqrt(30.)/3000.), s_dcr )
                g_DCR_vs_Npe[ds.sipm][bar].SetPointError( g_DCR_vs_Npe[ds.sipm][bar].GetN()-1, 0,  err_s_dcr)

            # total time resolution
            s_tot = math.sqrt( s_stoch*s_stoch + s_noise*s_noise + s_dcr*s_dcr )
            err_s_tot = 1./s_tot * math.sqrt( pow( err_s_stoch*s_stoch,2) + pow(s_noise*err_s_noise,2) + pow(s_dcr*err_s_dcr,2))

            g_Tot_vs_Vov[ds.sipm][bar].SetPoint(g_Tot_vs_Vov[ds.sipm][bar].GetN(), ovEff, s_tot)
            g_Tot_vs_Vov[ds.sipm][bar].SetPointError(g_Tot_vs_Vov[ds.sipm][bar].GetN()-1, 0, err_s_tot)

            

g1_DCR_vs_Vov = {}
g_DCR_vs_DCRNpe_average = {}
g_DCR_vs_DCRNpe_average_all = ROOT.TGraphErrors()

# average plots
g_SR_vs_Vov_average = {}
g_Noise_vs_Vov_average = {}
g_Stoch_vs_Vov_average = {}
g_DCR_vs_Vov_average = {}
g_Tot_vs_Vov_average = {}

for ds in data_structs:
    g1_DCR_vs_Vov[ds.sipm] = ROOT.TGraphErrors() 
    g_DCR_vs_DCRNpe_average[ds.sipm] = ROOT.TGraphErrors()
    g_SR_vs_Vov_average[ds.sipm] = ROOT.TGraphErrors()
    
    # average tRes, split contributions
    g_Noise_vs_Vov_average[ds.sipm] = ROOT.TGraphErrors()
    g_Stoch_vs_Vov_average[ds.sipm] = ROOT.TGraphErrors()
    g_DCR_vs_Vov_average[ds.sipm] = ROOT.TGraphErrors()
    g_Tot_vs_Vov_average[ds.sipm] = ROOT.TGraphErrors()

    for ov in Vovs[ds.sipm]:
        ovEff = getVovEffDCR(data,ds.lyso,ds.sipm,('%.02f'%ov))[0] 
        dcr   = getVovEffDCR(data,ds.lyso,ds.sipm,('%.02f'%ov))[1]


        if (ov in  g_SR_vs_bar[ds.sipm].keys()): 

            # average SR
            fitpol0_sr = ROOT.TF1('fitpol0_sr','pol0',-100,100)
            if (g_SR_vs_bar[ds.sipm][ov].GetN()==0): continue;
            g_SR_vs_bar[ds.sipm][ov].Fit(fitpol0_sr,'QNR')
            sr = fitpol0_sr.GetParameter(0)
            g_SR_vs_Vov_average[ds.sipm].SetPoint(g_SR_vs_Vov_average[ds.sipm].GetN(), ovEff, sr)
            g_SR_vs_Vov_average[ds.sipm].SetPointError(g_SR_vs_Vov_average[ds.sipm].GetN()-1, 0, fitpol0_sr.GetParError(0))

            # noise using average SR
            g_Noise_vs_Vov_average[ds.sipm].SetPoint(g_Noise_vs_Vov_average[ds.sipm].GetN(), ovEff, sigma_noise(sr))
            sr_err = max(fitpol0_sr.GetParError(0), errSRsyst*sr)
            sr_up   = sr + sr_err 
            sr_down = sr - sr_err 
            noise_err  = 0.5 * ( sigma_noise(sr_down) - sigma_noise(sr_up) ) 
            g_Noise_vs_Vov_average[ds.sipm].SetPointError(g_Noise_vs_Vov_average[ds.sipm].GetN()-1, 0, noise_err) 
    
            # average stochastic
            fitpol0_stoch = ROOT.TF1('fitpol0_stoch','pol0',-100,100)  
            g_Stoch_vs_bar[ds.sipm][ov].Fit(fitpol0_stoch,'QNR')
            stoch = fitpol0_stoch.GetParameter(0)
            stoch_err = 0 # fixme!
            g_Stoch_vs_Vov_average[ds.sipm].SetPoint(g_Stoch_vs_Vov_average[ds.sipm].GetN(), ovEff, stoch)
            g_Stoch_vs_Vov_average[ds.sipm].SetPointError(g_Stoch_vs_Vov_average[ds.sipm].GetN()-1, 0, stoch_err)

            # average dcr
            fitpol0_dcr = ROOT.TF1('fitpol0_dcr','pol0',-100,100)  
            g_DCR_vs_bar[ds.sipm][ov].Fit(fitpol0_dcr,'QNR')
            g_DCR_vs_Vov_average[ds.sipm].SetPoint(g_DCR_vs_Vov_average[ds.sipm].GetN(), ovEff, fitpol0_dcr.GetParameter(0))
            g_DCR_vs_Vov_average[ds.sipm].SetPointError(g_DCR_vs_Vov_average[ds.sipm].GetN()-1, 0, fitpol0_dcr.GetParError(0))

            # tot resolution summing noise + stochastic + dcr in quadrature
            tot = math.sqrt( stoch*stoch + sigma_noise(sr)*sigma_noise(sr) + fitpol0_dcr.GetParameter(0)*fitpol0_dcr.GetParameter(0) )
            tot_err = 1./tot * math.sqrt( pow( stoch_err*stoch,2) + pow(noise_err*sigma_noise(sr),2) + pow(fitpol0_dcr.GetParameter(0)*fitpol0_dcr.GetParError(0) , 2) )
            g_Tot_vs_Vov_average[ds.sipm].SetPoint(g_Tot_vs_Vov_average[ds.sipm].GetN(), ovEff, tot)
            g_Tot_vs_Vov_average[ds.sipm].SetPointError(g_Tot_vs_Vov_average[ds.sipm].GetN()-1, 0, tot_err)

            
            # average tRes vs Npe, DCR            
            fitpol0 = ROOT.TF1('fitpol0','pol0',-100,100)
            gg = f[ds.sipm].Get('g_deltaT_totRatioCorr_bestTh_vs_bar_Vov%.02f_enBin01'%ov)    
            gg.Fit(fitpol0,'QNR')
            g_data_vs_Npe[ds.sipm].SetPoint(g_data_vs_Npe[ds.sipm].GetN(), Npe[ds.sipm][ov], fitpol0.GetParameter(0))
            g_data_vs_Npe[ds.sipm].SetPointError(g_data_vs_Npe[ds.sipm].GetN()-1, 0, fitpol0.GetParError(0))

            g_data_vs_DCR[ds.sipm].SetPoint(g_data_vs_DCR[ds.sipm].GetN(), dcr, fitpol0.GetParameter(0))
            g_data_vs_DCR[ds.sipm].SetPointError(g_data_vs_DCR[ds.sipm].GetN()-1, 0,  fitpol0.GetParError(0))

            g_data_vs_GainNpe[ds.sipm].SetPoint(g_data_vs_GainNpe[ds.sipm].GetN(), gain[ds.sipm][ov]*Npe[ds.sipm][ov], fitpol0.GetParameter(0))
            g_data_vs_GainNpe[ds.sipm].SetPointError(g_data_vs_GainNpe[ds.sipm].GetN()-1, 0, fitpol0.GetParError(0))


        g1_DCR_vs_Vov[ds.sipm].SetPoint(g1_DCR_vs_Vov[ds.sipm].GetN(), ovEff, dcr) # DCR vs OV

        x = math.sqrt(dcr)/Npe[ds.sipm][ov]/ (math.sqrt(30.)/3000)
        x_down = math.sqrt(dcr)/(Npe[ds.sipm][ov]*(1+errPDE) )/ (math.sqrt(30.)/3000)
        x_up   = math.sqrt(dcr)/(Npe[ds.sipm][ov]*(1-errPDE))/ (math.sqrt(30.)/3000)
        if (g_DCR_vs_bar[ds.sipm][ov].GetN()==0):continue
        g_DCR_vs_DCRNpe_average[ds.sipm].SetPoint( g_DCR_vs_DCRNpe_average[ds.sipm].GetN(), x,  g_DCR_vs_bar[ds.sipm][ov].GetMean(2))
        g_DCR_vs_DCRNpe_average[ds.sipm].SetPointError( g_DCR_vs_DCRNpe_average[ds.sipm].GetN()-1, 0.5*(x_up-x_down),  g_DCR_vs_bar[ds.sipm][ov].GetRMS(2))
        g_DCR_vs_DCRNpe_average_all.SetPoint( g_DCR_vs_DCRNpe_average_all.GetN(), x,  g_DCR_vs_bar[ds.sipm][ov].GetMean(2))
        g_DCR_vs_DCRNpe_average_all.SetPointError( g_DCR_vs_DCRNpe_average_all.GetN()-1, 0.5*(x_up-x_down),  g_DCR_vs_bar[ds.sipm][ov].GetRMS(2))





# Andrea's model
fitFun_tRes_dcr_model = ROOT.TF1('fitFun_tRes_dcr_model','[1] * 2 * pow(x,[0]/0.5)', 0,10)  # factor 2 as Andrea normalize to 6000 pe
fitFun_tRes_dcr_model.SetParameter(0,0.4)
fitFun_tRes_dcr_model.SetParameter(1,40)
fitFun_tRes_dcr_model.SetLineColor(2)
g_DCR_vs_DCRNpe_average_all.Fit(fitFun_tRes_dcr_model)


# draw
c1 = {}
#c2 = {}
c3 = {}
c4 = {}
hdummy1 = {}
hdummy2 = {}
hdummy3 = {}
hdummy4 = {}
leg = {}

# Tres vs OV
print('Plotting time resolution vs OV...')
for ds in data_structs:
    c1[ds.sipm] = {}
    hdummy1[ds.sipm] = {}
    leg[ds.sipm] = ROOT.TLegend(0.65,0.70,0.89,0.89)
    leg[ds.sipm].SetBorderSize(0)
    leg[ds.sipm].SetFillStyle(0)
    for i,bar in enumerate(bars[ds.sipm]):
        if (bar not in g_data[ds.sipm].keys()): continue
        if (g_data[ds.sipm][bar].GetN()==0): continue
        c1[ds.sipm][bar] =  ROOT.TCanvas('c_timeResolution_vs_Vov_%s_bar%02d'%(ds.sipm,bar),'c_timeResolution_vs_Vov_%s_%s_T%sC_bar%02d'%(ds.lyso,ds.sipm,ds.temperature,bar),600,600)
        c1[ds.sipm][bar].SetGridy()
        c1[ds.sipm][bar].cd()
        xmin = 0.0
        xmax = 2.0
        hdummy1[ds.sipm][bar] = ROOT.TH2F('hdummy1_%s_%d'%(ds.sipm,bar),'',100,xmin,xmax,180,0,180)
        hdummy1[ds.sipm][bar].GetXaxis().SetTitle('V_{OV}^{eff} [V]')
        hdummy1[ds.sipm][bar].GetYaxis().SetTitle('#sigma_{t} [ps]')
        hdummy1[ds.sipm][bar].Draw()
        g_data[ds.sipm][bar].SetMarkerStyle(20)
        g_data[ds.sipm][bar].SetMarkerSize(1)
        g_data[ds.sipm][bar].SetMarkerColor(1)
        g_data[ds.sipm][bar].SetLineColor(1)
        g_data[ds.sipm][bar].SetLineWidth(2)
        g_data[ds.sipm][bar].Draw('plsame')
        if (bar not in g_Noise_vs_Vov[ds.sipm].keys()): continue
        g_Noise_vs_Vov[ds.sipm][bar].SetLineWidth(2)
        g_Noise_vs_Vov[ds.sipm][bar].SetLineColor(ROOT.kBlue)
        g_Noise_vs_Vov[ds.sipm][bar].SetFillColor(ROOT.kBlue)
        g_Noise_vs_Vov[ds.sipm][bar].SetFillColorAlpha(ROOT.kBlue,0.5)
        g_Noise_vs_Vov[ds.sipm][bar].SetFillStyle(3004)
        g_Noise_vs_Vov[ds.sipm][bar].Draw('E3lsame')
        g_Stoch_vs_Vov[ds.sipm][bar].SetLineWidth(2)
        g_Stoch_vs_Vov[ds.sipm][bar].SetLineColor(ROOT.kGreen+2)
        g_Stoch_vs_Vov[ds.sipm][bar].SetFillColor(ROOT.kGreen+2)
        g_Stoch_vs_Vov[ds.sipm][bar].SetFillStyle(3001)
        g_Stoch_vs_Vov[ds.sipm][bar].SetFillColorAlpha(ROOT.kGreen+2,0.5)
        g_Stoch_vs_Vov[ds.sipm][bar].Draw('E3lsame')
        g_DCR_vs_Vov[ds.sipm][bar].SetLineWidth(2)
        g_DCR_vs_Vov[ds.sipm][bar].SetLineColor(ROOT.kOrange+2)
        g_DCR_vs_Vov[ds.sipm][bar].SetFillColor(ROOT.kOrange+2)
        g_DCR_vs_Vov[ds.sipm][bar].SetFillColorAlpha(ROOT.kOrange+2,0.5)
        g_DCR_vs_Vov[ds.sipm][bar].SetFillStyle(3001)
        g_DCR_vs_Vov[ds.sipm][bar].Draw('E3lsame')
        g_Tot_vs_Vov[ds.sipm][bar].SetLineWidth(2)
        g_Tot_vs_Vov[ds.sipm][bar].SetLineColor(ROOT.kRed+1)
        g_Tot_vs_Vov[ds.sipm][bar].SetFillColor(ROOT.kRed+1)
        g_Tot_vs_Vov[ds.sipm][bar].SetFillColorAlpha(ROOT.kRed+1,0.5)
        g_Tot_vs_Vov[ds.sipm][bar].SetFillStyle(3001)
        #g_Tot_vs_Vov[ds.sipm][bar].Draw('E3lsame')
        #save on file
        outfile.cd()
        g_data[ds.sipm][bar].Write('g_Data_vs_Vov_%s_%s_T%dC_bar%02d'%(ds.lyso, ds.sipm, ds.temperature,  bar))
        g_Noise_vs_Vov[ds.sipm][bar].Write('g_Noise_vs_Vov_%s_%s_T%dC_bar%02d'%(ds.lyso, ds.sipm, ds.temperature, bar))
        g_Stoch_vs_Vov[ds.sipm][bar].Write('g_Stoch_vs_Vov_%s_%s_T%dC_bar%02d'%(ds.lyso, ds.sipm, ds.temperature, bar))
        g_DCR_vs_Vov[ds.sipm][bar].Write('g_DCR_vs_Vov_%s_%s_T%dC_bar%02d'%(ds.lyso, ds.sipm, ds.temperature, bar))
        if (i==0):
            leg[ds.sipm].AddEntry(g_data[ds.sipm][bar], 'data', 'PL')
            leg[ds.sipm].AddEntry(g_Noise_vs_Vov[ds.sipm][bar], 'noise', 'L')
            leg[ds.sipm].AddEntry(g_Stoch_vs_Vov[ds.sipm][bar], 'stoch', 'L')
            leg[ds.sipm].AddEntry(g_DCR_vs_Vov[ds.sipm][bar], 'DCR', 'L')
            #leg[ds.sipm].AddEntry(g_Tot_vs_Vov[ds.sipm][bar], 'stoch (+) noise', 'PL')
        leg[ds.sipm].Draw('same')
        latex = ROOT.TLatex(0.20,0.85,'%s'%(ds.sipm.replace('_',' ').replace('T','T=')))
        latex.SetNDC()
        latex.SetTextSize(0.045)
        latex.SetTextFont(42)
        latex.Draw('same')
        c1[ds.sipm][bar].SaveAs(outdir+'/'+c1[ds.sipm][bar].GetName()+'.png')
        c1[ds.sipm][bar].SaveAs(outdir+'/'+c1[ds.sipm][bar].GetName()+'.pdf')
        hdummy1[ds.sipm][bar].Delete()
        #c1[ds.sipm][bar].Delete()


# vs npe
print('Plotting tRes_DCR vs Npe...')
for bar in range(0,16):      
    c2 =  ROOT.TCanvas('c_timeResolutionDCR_vs_DCRNpe_bar%02d'%(bar),'c_timeResolutionDCR_vs_DCRNpe_bar%02d'%(bar),600,600)
    c2.SetGridx()
    c2.SetGridy()
    c2.cd()
    xmax = 2
    ymax = 120
    hdummy2 = ROOT.TH2F('hdummy2_%d'%(bar),'',100,0,xmax,100,0,ymax)
    hdummy2.GetXaxis().SetTitle('#sqrt{DCR/30GHz}/(Npe/3000)')
    hdummy2.GetYaxis().SetTitle('#sigma_{t}^{DCR} [ps]')
    hdummy2.Draw()
    for ds in data_structs:
        if (bar not in g_DCR_vs_Npe[ds.sipm].keys()): continue
        g_DCR_vs_Npe[ds.sipm][bar].SetMarkerStyle(ds.marker)
        g_DCR_vs_Npe[ds.sipm][bar].SetMarkerColor(ds.color)
        g_DCR_vs_Npe[ds.sipm][bar].SetLineWidth(1)
        g_DCR_vs_Npe[ds.sipm][bar].SetLineColor(ds.color)
        g_DCR_vs_Npe[ds.sipm][bar].Draw('psame')
    c2.SaveAs(outdir+'/'+c2.GetName()+'.png')
    c2.SaveAs(outdir+'/'+c2.GetName()+'.pdf')
    hdummy2.Delete()
    #c2.Delete()


c2 =  ROOT.TCanvas('c_timeResolutionDCR_vs_DCRNpe_average','c_timeResolutionDCR_vs_DCRNpe_average',600,600)
c2.SetGridx()
c2.SetGridy()
c2.cd()    
hdummy2 = ROOT.TH2F('hdummy2_%d'%(bar),'',100,0,2.0,100,0,140)
hdummy2.GetXaxis().SetTitle('#sqrt{DCR/30GHz}/(Npe/3000)')
hdummy2.GetYaxis().SetTitle('#sigma_{t}^{DCR} [ps]')
hdummy2.Draw()
g_DCR_vs_DCRNpe_average_all.SetMarkerSize(0.1)
g_DCR_vs_DCRNpe_average_all.Draw('p*same')
fitFun_tRes_dcr_model.Draw('same')
outfile.cd() 
g_DCR_vs_DCRNpe_average_all.Write('g_DCR_vs_DCRNpe_average_all')
for ds in data_structs:
    g_DCR_vs_DCRNpe_average[ds.sipm].SetMarkerStyle(ds.marker)
    g_DCR_vs_DCRNpe_average[ds.sipm].SetMarkerColor(ds.color)
    g_DCR_vs_DCRNpe_average[ds.sipm].SetLineWidth(1)
    g_DCR_vs_DCRNpe_average[ds.sipm].SetLineColor(ds.color)
    g_DCR_vs_DCRNpe_average[ds.sipm].Draw('psame')
    outfile.cd() 
    g_DCR_vs_DCRNpe_average[ds.sipm].Write('g_DCR_vs_DCRNpe_average_%s'%ds.sipm)
c2.SaveAs(outdir+'/'+c2.GetName()+'.png')
c2.SaveAs(outdir+'/'+c2.GetName()+'.pdf')
hdummy2.Delete()
#c2.Delete()


# SR and best threshold vs Vov
leg2 = ROOT.TLegend(0.20,0.70,0.45,0.89)
leg2.SetBorderSize(0)
leg2.SetFillStyle(0)
for bar in range(0,16):
    if (bar not in g_data[ds.sipm].keys()): continue
    if (g_data[ds.sipm][bar].GetN()==0): continue     
    c3[bar] = ROOT.TCanvas('c_slewRate_vs_Vov_bar%02d'%(bar),'c_slewRate_vs_Vov_bar%02d'%(bar),600,600)
    c3[bar].SetGridy()
    c3[bar].cd()
    xmin = 0.0
    xmax = 2.0
    ymax = 35
    hdummy3[bar] = ROOT.TH2F('hdummy3_%d'%(bar),'',100,xmin,xmax,100,0,ymax)
    hdummy3[bar].GetXaxis().SetTitle('V_{OV}^{eff} [V]')
    hdummy3[bar].GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
    hdummy3[bar].Draw()
    for ds in data_structs:
        if (bar not in g_SR_vs_Vov[ds.sipm].keys()): continue
        #if (i==0):
        #    leg2.AddEntry(g_SR_vs_Vov[ds.sipm][bar], '%s'%sipm, 'PL')
        g_SR_vs_Vov[ds.sipm][bar].SetMarkerStyle(ds.marker)
        g_SR_vs_Vov[ds.sipm][bar].SetMarkerColor(ds.color)
        g_SR_vs_Vov[ds.sipm][bar].SetLineColor(ds.color)
        g_SR_vs_Vov[ds.sipm][bar].Draw('plsame')
    leg2.Draw()
    outfile.cd()
    g_SR_vs_Vov[ds.sipm][bar].Write('g_SR_vs_Vov_%s_bar%02d'%(ds.sipm,bar))
    c3[bar].SaveAs(outdir+'/'+c3[bar].GetName()+'.png')
    c3[bar].SaveAs(outdir+'/'+c3[bar].GetName()+'.pdf')
    hdummy3[bar].Delete()
    

    c3[bar] = ROOT.TCanvas('c_slewRate_vs_GainNpe_bar%02d'%(bar),'c_slewRate_vs_GainNpe_bar%02d'%(bar),600,600)
    c3[bar].SetGridy()
    c3[bar].cd()
    hdummy3[bar] = ROOT.TH2F('hdummy3_%d'%(bar),'',100,0,3E09,100,0,35)
    hdummy3[bar].GetXaxis().SetTitle('gain x Npe')
    hdummy3[bar].GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
    hdummy3[bar].Draw()
    for ds in data_structs:
        if (bar not in g_SR_vs_GainNpe[ds.sipm].keys()): continue
        g_SR_vs_GainNpe[ds.sipm][bar].SetMarkerStyle( ds.marker )
        g_SR_vs_GainNpe[ds.sipm][bar].SetMarkerColor(ds.color)
        g_SR_vs_GainNpe[ds.sipm][bar].SetLineColor(ds.color)
        g_SR_vs_GainNpe[ds.sipm][bar].Draw('psame')
    leg2.Draw()
    c3[bar].SaveAs(outdir+'/'+c3[bar].GetName()+'.png')
    c3[bar].SaveAs(outdir+'/'+c3[bar].GetName()+'.pdf')


    c4[bar] = ROOT.TCanvas('c_bestTh_vs_Vov_bar%02d'%(bar),'c_bestTh_vs_Vov_bar%02d'%(bar),600,600)
    c4[bar].SetGridy()
    c4[bar].cd()
    hdummy4[bar] = ROOT.TH2F('hdummy4_%d'%(bar),'',100,xmin,xmax,100,0,20)
    hdummy4[bar].GetXaxis().SetTitle('V_{OV}^{eff} [V]')
    hdummy4[bar].GetYaxis().SetTitle('best threshold [DAC]')
    hdummy4[bar].Draw()
    for ds in data_structs:
        if (bar not in g_bestTh_vs_Vov[ds.sipm].keys()): continue
        g_bestTh_vs_Vov[ds.sipm][bar].SetMarkerStyle(ds.marker)
        g_bestTh_vs_Vov[ds.sipm][bar].SetMarkerColor(ds.color)
        g_bestTh_vs_Vov[ds.sipm][bar].SetLineColor(ds.color)
        g_bestTh_vs_Vov[ds.sipm][bar].Draw('plsame')
    c4[bar].SaveAs(outdir+'/'+c4[bar].GetName()+'.png')
    c4[bar].SaveAs(outdir+'/'+c4[bar].GetName()+'.pdf')


# average slew rate vs OV
c2 =  ROOT.TCanvas('c_slewRate_vs_Vov_average','c_slewRate_vs_Vov_average',600,600)
c2.SetGridx()
c2.SetGridy()
c2.cd()    
hdummy2 = ROOT.TH2F('hdummy2','',16, 0.0, 2.0 ,100, 0,35)
hdummy2.GetXaxis().SetTitle('V_{OV}^{eff} [V]')
hdummy2.GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
hdummy2.Draw()
for ds in data_structs:
    g_SR_vs_Vov_average[ds.sipm].SetMarkerStyle(ds.marker)
    g_SR_vs_Vov_average[ds.sipm].SetMarkerColor(ds.color)
    g_SR_vs_Vov_average[ds.sipm].SetLineWidth(1)
    g_SR_vs_Vov_average[ds.sipm].SetLineColor(ds.color)
    g_SR_vs_Vov_average[ds.sipm].Draw('plsame')
    outfile.cd()
    g_SR_vs_Vov_average[ds.sipm].Write('g_SR_vs_Vov_average_%s_%s_T%dC'%(ds.lyso, ds.sipm, ds.temperature))
leg2.Draw()
c2.SaveAs(outdir+'/'+c2.GetName()+'.png')
c2.SaveAs(outdir+'/'+c2.GetName()+'.pdf')


# average time resolution vs Npe
c2 =  ROOT.TCanvas('c_timeResolution_vs_Npe_average','c_timeResolution_vs_Npe_average',600,600)
c2.SetGridx()
c2.SetGridy()
c2.cd()    
hdummy2 = ROOT.TH2F('hdummy2','',1000, 1000, 6000, 100, 0, 150)
hdummy2.GetXaxis().SetTitle('Npe')
hdummy2.GetYaxis().SetTitle('#sigma_{t} [ps]')
hdummy2.GetXaxis().SetNdivisions(505)
hdummy2.Draw()
for ds in data_structs:
    g_data_vs_Npe[ds.sipm].SetMarkerStyle(ds.marker)
    g_data_vs_Npe[ds.sipm].SetMarkerColor(ds.color)
    g_data_vs_Npe[ds.sipm].SetLineWidth(1)
    g_data_vs_Npe[ds.sipm].SetLineColor(ds.color)
    g_data_vs_Npe[ds.sipm].Draw('plsame')
    outfile.cd()
    g_data_vs_Npe[ds.sipm].Write('g_data_vs_Npe_average_%s_%s_T%dC'%(ds.lyso, ds.sipm, ds.temperature))
leg2.Draw()  
c2.SaveAs(outdir+'/'+c2.GetName()+'.png')
c2.SaveAs(outdir+'/'+c2.GetName()+'.pdf')
hdummy2.Delete()


# average time resolution vs DCR
c2 =  ROOT.TCanvas('c_timeResolution_vs_DCR_average','c_timeResolution_vs_DCR_average',600,600)
c2.SetGridx()
c2.SetGridy()
c2.cd()    
hdummy2 = ROOT.TH2F('hdummy2','',1000, 0, 100, 100, 0, 150)
hdummy2.GetXaxis().SetTitle('DCR [GHz]')
hdummy2.GetYaxis().SetTitle('#sigma_{t} [ps]')
hdummy2.Draw()
for ds in data_structs:
    g_data_vs_DCR[ds.sipm].SetMarkerStyle(ds.marker)
    g_data_vs_DCR[ds.sipm].SetMarkerColor(ds.color)
    g_data_vs_DCR[ds.sipm].SetLineWidth(1)
    g_data_vs_DCR[ds.sipm].SetLineColor(ds.color)
    g_data_vs_DCR[ds.sipm].Draw('plsame')
    outfile.cd()
    g_data_vs_DCR[ds.sipm].Write('g_data_vs_DCR_average_%s_%s_T%dC'%(ds.lyso, ds.sipm, ds.temperature))
leg2.Draw()  
c2.SaveAs(outdir+'/'+c2.GetName()+'.png')
c2.SaveAs(outdir+'/'+c2.GetName()+'.pdf')
hdummy2.Delete()

# average time resolution vs GainxNpe
c2 =  ROOT.TCanvas('c_timeResolution_vs_GainNpe_average','c_timeResolution_vs_GainNpe_average',600,600)
c2.SetGridx()
c2.SetGridy()
c2.cd()    
hdummy2 = ROOT.TH2F('hdummy2','',1000, 0, 3E09, 100, 0, 150)
hdummy2.GetXaxis().SetTitle('Gain x Npe')
hdummy2.GetYaxis().SetTitle('#sigma_{t} [ps]')
hdummy2.GetXaxis().SetNdivisions(505)
hdummy2.Draw()
for ds in data_structs:
    g_data_vs_GainNpe[ds.sipm].SetMarkerStyle(ds.marker)
    g_data_vs_GainNpe[ds.sipm].SetMarkerColor(ds.color)
    g_data_vs_GainNpe[ds.sipm].SetLineWidth(1)
    g_data_vs_GainNpe[ds.sipm].SetLineColor(ds.color)
    g_data_vs_GainNpe[ds.sipm].Draw('plsame')
leg2.Draw()  
c2.SaveAs(outdir+'/'+c2.GetName()+'.png')
c2.SaveAs(outdir+'/'+c2.GetName()+'.pdf')
hdummy2.Delete()
                                       

# average tRes
for ds in data_structs:
    latex = ROOT.TLatex(0.18,0.94,'%s'%(ds.label))
    latex.SetNDC()
    latex.SetTextSize(0.05)
    latex.SetTextFont(42)
    c2 =  ROOT.TCanvas('c_timeResolution_vs_Vov_average_%s_%s_T%dC'%(ds.lyso,ds.sipm,ds.temperature),'c_timeResolution_vs_Vov_average_%s_%s_T%dC'%(ds.lyso,ds.sipm,ds.temperature),600,600)
    c2.SetGridx()
    c2.SetGridy()
    c2.cd()
    hdummy2 = ROOT.TH2F('hdummy2','',100, 0., 2.,100,0,180)
    hdummy2.GetXaxis().SetTitle('V_{OV}^{eff} [V]')
    hdummy2.GetYaxis().SetTitle('time resolution [ps]')
    hdummy2.Draw()
    g_data_average[ds.sipm].SetMarkerStyle(20)
    g_data_average[ds.sipm].SetMarkerSize(1)
    g_data_average[ds.sipm].SetMarkerColor(1)
    g_data_average[ds.sipm].SetLineColor(1)
    g_data_average[ds.sipm].SetLineWidth(2)
    g_data_average[ds.sipm].Draw('plsame')
    g_Noise_vs_Vov_average[ds.sipm].SetLineWidth(2)
    g_Noise_vs_Vov_average[ds.sipm].SetLineColor(ROOT.kBlue)
    g_Noise_vs_Vov_average[ds.sipm].SetFillColor(ROOT.kBlue)
    g_Noise_vs_Vov_average[ds.sipm].SetFillColorAlpha(ROOT.kBlue,0.5)
    g_Noise_vs_Vov_average[ds.sipm].SetFillStyle(3004)
    g_Noise_vs_Vov_average[ds.sipm].Draw('E3lsame')
    g_Stoch_vs_Vov_average[ds.sipm].SetLineWidth(2)
    g_Stoch_vs_Vov_average[ds.sipm].SetLineColor(ROOT.kGreen+2)
    g_Stoch_vs_Vov_average[ds.sipm].SetFillColor(ROOT.kGreen+2)
    g_Stoch_vs_Vov_average[ds.sipm].SetFillStyle(3001)
    g_Stoch_vs_Vov_average[ds.sipm].SetFillColorAlpha(ROOT.kGreen+2,0.5)
    g_Stoch_vs_Vov_average[ds.sipm].Draw('E3lsame')
    g_DCR_vs_Vov_average[ds.sipm].SetLineWidth(2)
    g_DCR_vs_Vov_average[ds.sipm].SetLineColor(ROOT.kOrange+2)
    g_DCR_vs_Vov_average[ds.sipm].SetFillColor(ROOT.kOrange+2)
    g_DCR_vs_Vov_average[ds.sipm].SetFillStyle(3001)
    g_DCR_vs_Vov_average[ds.sipm].SetFillColorAlpha(ROOT.kOrange+2,0.5)
    g_DCR_vs_Vov_average[ds.sipm].Draw('E3lsame')
    g_Tot_vs_Vov_average[ds.sipm].SetLineWidth(2)
    g_Tot_vs_Vov_average[ds.sipm].SetLineColor(ROOT.kRed+1)
    g_Tot_vs_Vov_average[ds.sipm].SetFillColor(ROOT.kRed+1)
    g_Tot_vs_Vov_average[ds.sipm].SetFillColorAlpha(ROOT.kRed+1,0.5)
    g_Tot_vs_Vov_average[ds.sipm].SetFillStyle(3001)
    #g_Tot_vs_Vov_average[ds.sipm].Draw('E3lsame')
    leg[ds.sipm].Draw()
    latex.Draw()
    outfile.cd()
    g_Noise_vs_Vov_average[ds.sipm].Write('g_Noise_vs_Vov_average_%s'%ds.sipm)
    g_Stoch_vs_Vov_average[ds.sipm].Write('g_Stoch_vs_Vov_average_%s'%ds.sipm)
    g_DCR_vs_Vov_average[ds.sipm].Write('g_Stoch_vs_Vov_average_%s'%ds.sipm)
    g_Tot_vs_Vov_average[ds.sipm].Write('g_Tot_vs_Vov_average_%s'%ds.sipm)
    c2.SaveAs(outdir+'/'+c2.GetName()+'.png')
    c2.SaveAs(outdir+'/'+c2.GetName()+'.pdf')
    hdummy2.Delete()


# SR and best threshold vs bar
c5 = {}
hdummy5 = {}
c6 = {}
hdummy6 = {}
c7 = {}
hdummy7 = {}
c8 = {}
hdummy8 = {}
c9 = {}
hdummy9 = {}
for ds in data_structs:
    for ov in Vovs[ds.sipm]:
        if (ov not in g_SR_vs_bar[ds.sipm].keys()): continue
        ovEff = getVovEffDCR(data,ds.lyso, ds.sipm, ('%.02f'%ov))[0] 
        c5[ov] = ROOT.TCanvas('c_slewRate_vs_bar_%s_Vov%.2f'%(ds.sipm,ovEff),'c_slewRate_vs_bar_%s_Vov%.2f'%(ds.sipm,ovEff),600,600)
        c5[ov].SetGridy()
        c5[ov].cd()
        #hdummy5[ov] = ROOT.TH2F('hdummy5_%d'%(ov),'',100,-0.5,15.5,100,0,15)
        hdummy5[ov] = ROOT.TH2F('hdummy5_%s_%.2f'%(ds.sipm,ov),'',100,-0.5,15.5,100,0,35)
        hdummy5[ov].GetXaxis().SetTitle('bar')
        hdummy5[ov].GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
        hdummy5[ov].Draw()
        g_SR_vs_bar[ds.sipm][ov].SetMarkerStyle(ds.marker)
        g_SR_vs_bar[ds.sipm][ov].SetMarkerColor(ds.color)
        g_SR_vs_bar[ds.sipm][ov].SetLineColor(ds.color)
        g_SR_vs_bar[ds.sipm][ov].Draw('psame')
        leg2.Draw()
        c5[ov].SaveAs(outdir+'/'+c5[ov].GetName()+'.png')
        c5[ov].SaveAs(outdir+'/'+c5[ov].GetName()+'.pdf')


        c6[ov] = ROOT.TCanvas('c_bestTh_vs_bar_%s_Vov%.2f'%(ds.sipm,ovEff),'c_bestTh_vs_bar_%s_Vov%.2f'%(ds.sipm,ovEff),600,600)
        c6[ov].SetGridy()
        c6[ov].cd()
        hdummy6[ov] = ROOT.TH2F('hdummy6_%s_%.2f'%(ds.sipm,ov),'',100,-0.5,15.5,100,0,20)
        hdummy6[ov].GetXaxis().SetTitle('bar')
        hdummy6[ov].GetYaxis().SetTitle('timing threshold [DAC]')
        hdummy6[ov].Draw()
        g_bestTh_vs_bar[ds.sipm][ov].SetMarkerStyle(ds.marker)
        g_bestTh_vs_bar[ds.sipm][ov].SetMarkerColor(ds.color)
        g_bestTh_vs_bar[ds.sipm][ov].SetLineColor(ds.color)
        g_bestTh_vs_bar[ds.sipm][ov].Draw('plsame')
        leg2.Draw()        
        c6[ov].SaveAs(outdir+'/'+c6[ov].GetName()+'.png')
        c6[ov].SaveAs(outdir+'/'+c6[ov].GetName()+'.pdf')

        c7[ov] = ROOT.TCanvas('c_noise_vs_bar_%s_Vov%.2f'%(ds.sipm,ovEff),'c_noise_vs_bar_%s_Vov%.2f'%(ds.sipm,ovEff),600,600)
        c7[ov].SetGridy()
        c7[ov].cd()
        hdummy7[ov] = ROOT.TH2F('hdummy7_%s_%.2f'%(ds.sipm,ov),'',100,-0.5,15.5,100,0,80)
        hdummy7[ov].GetXaxis().SetTitle('bar')
        hdummy7[ov].GetYaxis().SetTitle('#sigma_{t, noise} [ps]')
        hdummy7[ov].Draw()
        g_Noise_vs_bar[ds.sipm][ov].SetMarkerStyle( ds.marker )
        g_Noise_vs_bar[ds.sipm][ov].SetMarkerColor(ds.color)
        g_Noise_vs_bar[ds.sipm][ov].SetLineColor(ds.color)
        g_Noise_vs_bar[ds.sipm][ov].Draw('psame')
        leg2.Draw()
        c7[ov].SaveAs(outdir+'/'+c7[ov].GetName()+'.png')
        c7[ov].SaveAs(outdir+'/'+c7[ov].GetName()+'.pdf')

        c8[ov] = ROOT.TCanvas('c_stoch_vs_bar_%s_Vov%.2f'%(ds.sipm,ovEff),'c_stoch_vs_bar_%s_Vov%.2f'%(ds.sipm,ovEff),600,600)
        c8[ov].SetGridy()
        c8[ov].cd()
        hdummy8[ov] = ROOT.TH2F('hdummy8_%s_%.2f'%(ds.sipm,ov),'',100,-0.5,15.5,100,0,80)
        hdummy8[ov].GetXaxis().SetTitle('bar')
        hdummy8[ov].GetYaxis().SetTitle('#sigma_{t, stoch} [ps]')
        hdummy8[ov].Draw()
        g_Stoch_vs_bar[ds.sipm][ov].SetMarkerStyle( ds.marker )
        g_Stoch_vs_bar[ds.sipm][ov].SetMarkerColor(ds.color)
        g_Stoch_vs_bar[ds.sipm][ov].SetLineColor(ds.color)
        g_Stoch_vs_bar[ds.sipm][ov].Draw('psame')
        leg2.Draw()
        c8[ov].SaveAs(outdir+'/'+c8[ov].GetName()+'.png')
        c8[ov].SaveAs(outdir+'/'+c8[ov].GetName()+'.pdf')
        
        c9[ov] = ROOT.TCanvas('c_dcr_vs_bar_%s_Vov%.2f'%(ds.sipm,ovEff),'c_dcr_vs_bar_%s_Vov%.2f'%(ds.sipm,ovEff),600,600)
        c9[ov].SetGridy()
        c9[ov].cd()
        hdummy9[ov] = ROOT.TH2F('hdummy9_%s_%.2f'%(ds.sipm,ov),'',100,-0.5,15.5,100,0,140)
        hdummy9[ov].GetXaxis().SetTitle('bar')
        hdummy9[ov].GetYaxis().SetTitle('#sigma_{t, DCR} [ps]')
        hdummy9[ov].Draw()
        g_DCR_vs_bar[ds.sipm][ov].SetMarkerStyle( ds.marker )
        g_DCR_vs_bar[ds.sipm][ov].SetMarkerColor(ds.color)
        g_DCR_vs_bar[ds.sipm][ov].SetLineColor(ds.color)
        g_DCR_vs_bar[ds.sipm][ov].Draw('psame')
        leg2.Draw()
        c9[ov].SaveAs(outdir+'/'+c9[ov].GetName()+'.png')
        c9[ov].SaveAs(outdir+'/'+c9[ov].GetName()+'.pdf')

outfile.Close()

raw_input('OK?')
