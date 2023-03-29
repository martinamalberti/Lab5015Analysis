#! /usr/bin/env python3
import os
import shutil
import glob
import math
import array
import sys
import time
import argparse

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

ROOT.gROOT.SetBatch(True)
#ROOT.gROOT.SetBatch(False)
ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(111)

from SiPM import *



def getSlewRateFromPulseShape(g1, timingThreshold, npoints, gtemp, canvas=None):
    if ( g1.GetN() < npoints): return (-1, -1)
    # find index at the timing threshold
    itiming = 0
    for i in range(0,g1.GetN()):
        if (round(g1.GetY()[i]/0.313) == timingThreshold):
            itiming = i
            break

    ifirst = ROOT.TMath.LocMin(g1.GetN(), g1.GetX())
    #imin = max(0, itiming-2)
    imin = max(0, itiming - round(npoints/2))
    if ( imin >= 0 and g1.GetX()[imin+1] < g1.GetX()[imin] ): imin = ifirst
    tmin = g1.GetX()[imin]
    tmax = min(g1.GetX()[ min(imin+npoints, g1.GetN()-1)],3.)
    for i in range(imin, min(imin+npoints,g1.GetN()-1)+1):
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
        gtemp.Draw('psames')
        g1.Draw('psames')
        gtemp.Draw('p*sames')
        fitSR.Draw('same')
        canvas.Update()
        ps = gtemp.FindObject('stats')
        ps.SetTextColor(g1.GetMarkerColor())
        if ('L' in g1.GetName()):
            ps.SetY1NDC(0.85) # new y start position
            ps.SetY2NDC(0.95)# new y end position
        if ('R' in g1.GetName()):
            ps.SetY1NDC(0.73) # new y start position
            ps.SetY2NDC(0.83)# new y end position
    return(sr,err_sr)


def findTimingThreshold(g2):
    xmin = 0
    ymin = 9999
    for i in range(0, g2.GetN()):
        y = g2.GetY()[i]
        x = g2.GetX()[i]
        yerr = g2.GetErrorY(i)
        if ( y < ymin):
            ymin = y
            xmin = x 
    return xmin
    
# =====================================

class DataStruct(NamedTuple):
    sipm: str
    sipmType: str
    fName: str
    fNamePS: str
    label: str
    LO: str
    tau: str
    marker: int
    color: int

data_structs = []


#HPK_25 um 
data_structs.append(
        DataStruct(
            sipm = 'HPK_nonIrr_LYSO813',
            sipmType = 'HPK-PIT-C25-ES2',
            fName = '/afs/cern.ch/work/m/malberti/MTD/TBatFNALMar2023/Lab5015Analysis/plots/summaryPlots_HPK_nonIrr_LYSO813.root',
            fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatFNALMar2023/Lab5015Analysis/plots/pulseShape_HPK_nonIrr_LYSO813',
            label = 'HPK(25#mum)+LYSO813',
            LO = 2418,
            tau = 41.4,
            marker = 20,
            color = 1
        )
)

#HPK_20 um 
data_structs.append(
        DataStruct(
            sipm = 'HPK_nonIrr_LYSO814',
            sipmType = 'HPK-PIT-C20-ES2',
            fName = '/afs/cern.ch/work/m/malberti/MTD/TBatFNALMar2023/Lab5015Analysis/plots/summaryPlots_HPK_nonIrr_LYSO814.root',
            fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatFNALMar2023/Lab5015Analysis/plots/pulseShape_HPK_nonIrr_LYSO814',
            label = 'HPK(20#mum)+LYSO814',
            LO = 2165,
            tau = 41.4,
            marker = 20,
            color = 2
        )
)


#HPK_15 um 
data_structs.append(
        DataStruct(
            sipm = 'HPK_nonIrr_LYSO528',
            sipmType = 'HPK-MS',
            fName = '/afs/cern.ch/work/m/malberti/MTD/TBatFNALMar2023/Lab5015Analysis/plots/summaryPlots_HPK_nonIrr_LYSO528.root',
            fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatFNALMar2023/Lab5015Analysis/plots/pulseShape_HPK_nonIrr_LYSO528',
            label = 'HPK(15#mum)+LYSO528',
            LO = 1323,
            tau = 38.6,
            marker = 20,
            color = 3
        )
)

#HPK_25 um - low Cgrid
'''
data_structs.append(
        DataStruct(
            sipm ='HPK_nonIrr_LYSO824',
            sipmType = 'HPK-PIT-C25-ES3',
            fName = '/afs/cern.ch/work/m/malberti/MTD/TBatFNALMar2023/Lab5015Analysis/plots/summaryPlots_HPK_nonIrr_LYSO824.root',
            fNamePS = '/afs/cern.ch/work/m/malberti/MTD/TBatFNALMar2023/Lab5015Analysis/plots/pulseShape_HPK_nonIrr_LYSO824',
            label = 'HPK(25#mum, low Cgrid)+LYSO824',
            LO = 2418,
            tau = 38.6,
            marker = 24,
            color = 4
        )
)
'''





# =====================================

outdir = '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_FNAL_Mar23/timeResolution_vs_Vov_HPK_cellSizes_test/'
#outdir = '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_FNAL_Mar23/timeResolution_vs_Vov_HPK_Cgrid/'

if (os.path.exists(outdir)==False):
    os.mkdir(outdir)
if (os.path.exists(outdir+'/plotsSR')==False):
    os.mkdir(outdir+'/plotsSR/')

outfile   = ROOT.TFile.Open(outdir+'/plots_timeResolution_HPK_nonIrr_TBMar23_cellSizes_test.root','recreate')  
#outfile   = ROOT.TFile.Open(outdir+'/plots_timeResolution_HPK_nonIrr_TBMar23_Cgrid.root','recreate')  


np = 3
errSRsyst  = 0.10 # error on the slew rate

g_data = {}
g_data_average = {}

g_Noise_vs_Vov = {}
g_Stoch_vs_Vov = {}
g_Tot_vs_Vov   = {}

g_Stoch_vs_Npe = {}

g_SR_vs_bar = {}
g_SR_vs_Vov = {}
g_SR_vs_GainNpe = {}

g_bestTh_vs_bar = {}
g_bestTh_vs_Vov = {}

g_Noise_vs_bar = {}
g_Stoch_vs_bar = {}


bars = {}
Vovs = {}

for ds in data_structs:
    f = ROOT.TFile.Open(ds.fName)
    print(ds.sipm, ds.fName)

    listOfKeys = [key.GetName().replace('g_deltaT_totRatioCorr_bestTh_vs_vov_','') for key in ROOT.gDirectory.GetListOfKeys() if ( 'g_deltaT_totRatioCorr_bestTh_vs_vov_bar' in key.GetName())]
    bars[ds.sipm] = []
    for k in listOfKeys:
        bars[ds.sipm].append( int(k[3:5]) )

    listOfKeys2 = [key.GetName().replace('g_deltaT_totRatioCorr_bestTh_vs_bar_','') for key in ROOT.gDirectory.GetListOfKeys() if key.GetName().startswith('g_deltaT_totRatioCorr_bestTh_vs_bar_')]
    Vovs[ds.sipm] = []
    for k in listOfKeys2:
        Vovs[ds.sipm].append( float(k[3:7]) )
    
    print(bars[ds.sipm])
    print(Vovs[ds.sipm])

fPS = {}
Npe = {}


for ds in data_structs:
    f = ROOT.TFile.Open(ds.fName)
    
    g_data_average[ds.sipm] = f.Get('g_deltaT_totRatioCorr_bestTh_vs_vov_enBin01_average')

    Npe[ds.sipm] = {}
    g_data[ds.sipm] = {}
    g_Noise_vs_Vov[ds.sipm] = {}
    g_Stoch_vs_Vov[ds.sipm] = {}
    g_Tot_vs_Vov[ds.sipm] = {}

    g_Stoch_vs_Npe[ds.sipm] = {}

    g_SR_vs_Vov[ds.sipm] = {}
    g_bestTh_vs_Vov[ds.sipm] = {}

    g_SR_vs_bar[ds.sipm] = {}
    g_bestTh_vs_bar[ds.sipm] = {}
    g_Noise_vs_bar[ds.sipm] = {}
    g_Stoch_vs_bar[ds.sipm] = {}

    g_SR_vs_GainNpe[ds.sipm] = {}

    fPS[ds.sipm] = {}
    for ov in Vovs[ds.sipm]:
        fPS[ds.sipm][ov] = ROOT.TFile.Open(ds.fNamePS+'_Vov%.2f.root'%ov)

        g_SR_vs_bar[ds.sipm][ov] = ROOT.TGraphErrors()
        g_bestTh_vs_bar[ds.sipm][ov] = ROOT.TGraphErrors()
        g_Noise_vs_bar[ds.sipm][ov] = ROOT.TGraphErrors()
        g_Stoch_vs_bar[ds.sipm][ov] = ROOT.TGraphErrors()

    for bar in bars[ds.sipm]:
        g_data[ds.sipm][bar] = f.Get('g_deltaT_totRatioCorr_bestTh_vs_vov_bar%02d_enBin01'%bar)
        g_Noise_vs_Vov[ds.sipm][bar] = ROOT.TGraphErrors()
        g_Stoch_vs_Vov[ds.sipm][bar] = ROOT.TGraphErrors()
        g_Tot_vs_Vov[ds.sipm][bar] = ROOT.TGraphErrors()

        g_Stoch_vs_Npe[ds.sipm][bar] = ROOT.TGraphErrors()

        g_SR_vs_Vov[ds.sipm][bar] = ROOT.TGraphErrors()
        g_SR_vs_GainNpe[ds.sipm][bar] = ROOT.TGraphErrors()
        g_bestTh_vs_Vov[ds.sipm][bar] = ROOT.TGraphErrors()
        
        sigma_stoch_ref = 0
        err_sigma_stoch_ref = 0
        ov_ref = 3.50

        data = g_data[ds.sipm][bar].Eval(ov_ref)
        indref = [i for i in range(0, g_data[ds.sipm][bar].GetN()) if g_data[ds.sipm][bar].GetPointX(i) == ov_ref]
        if ( len(indref)<1): continue
        data_err = g_data[ds.sipm][bar].GetErrorY(indref[0])
        g_psL = fPS[ds.sipm][ov_ref].Get('g_pulseShapeL_bar%02d_Vov%.2f'%(bar,ov_ref))
        g_psR = fPS[ds.sipm][ov_ref].Get('g_pulseShapeR_bar%02d_Vov%.2f'%(bar,ov_ref))
        if (g_psL==None): continue
        if (g_psR==None): continue
        g_psL.SetName('g_pulseShapeL_bar%02d_Vov%.2f'%(bar,ov_ref))
        g_psR.SetName('g_pulseShapeR_bar%02d_Vov%.2f'%(bar,ov_ref))
        timingThreshold = findTimingThreshold(f.Get('g_deltaT_totRatioCorr_vs_th_bar%02d_Vov%.2f_enBin01'%(bar,ov_ref)))
        gtempL = ROOT.TGraphErrors()
        gtempR = ROOT.TGraphErrors()
        srL,err_srL = getSlewRateFromPulseShape(g_psL, timingThreshold, np, gtempL)
        srR,err_srR = getSlewRateFromPulseShape(g_psR, timingThreshold, np, gtempR)
        if (srL>0 and srR>0):
            # weighted average
            sr =  ( (srL/(err_srL*err_srL) + srR/(err_srR*err_srR) ) / (1./(err_srL*err_srL) + 1./(err_srR*err_srR) ) )
            errSR = 1./math.sqrt( 1./(err_srL*err_srL)  +  1./(err_srR*err_srR) )
            errSR = errSR/sr
        if (srL>0 and srR<0):
            sr = srL
            errSR = err_srL/sr
        if (srL<0 and srR>0):
            sr = srR
            errSR = err_srR/sr
        errSR = math.sqrt(errSR*errSR+errSRsyst*errSRsyst) 
        if (data>=sigma_noise(sr)):
            stoch_ref = math.sqrt(data*data - sigma_noise(sr)*sigma_noise(sr))
            noise_err = 0.5*(sigma_noise(sr*(1-errSR))-sigma_noise(sr*(1+errSR)))
            stoch_ref_err = 1./stoch_ref*math.sqrt( pow(data_err*data,2)+pow( sigma_noise(sr)*noise_err ,2) )
        else:
            print('skipping bar%02d:  %.1f   %.1f'%(bar, data,sigma_noise(sr)))
            continue
                
        for i in range(0,g_data[ds.sipm][bar].GetN()):
            sigma_meas = g_data[ds.sipm][bar].GetY()[i]
            err_sigma_meas   = g_data[ds.sipm][bar].GetErrorY(i)
            ov = g_data[ds.sipm][bar].GetX()[i]
            if (ov not in Vovs[ds.sipm]): continue
            Npe[ds.sipm][ov]  = ds.LO*4.2*PDE(ds.sipmType,ov)/PDE(ds.sipmType,3.50)
            gain = Gain(ds.sipmType,ov) 
            g_psL = fPS[ds.sipm][ov].Get('g_pulseShapeL_bar%02d_Vov%.2f'%(bar,ov))
            g_psR = fPS[ds.sipm][ov].Get('g_pulseShapeR_bar%02d_Vov%.2f'%(bar,ov))
            if (g_psL==None): continue
            if (g_psR==None): continue
            g_psL.SetName('g_pulseShapeL_bar%02d_Vov%.2f_%s'%(bar,ov,ds.sipm))
            g_psR.SetName('g_pulseShapeR_bar%02d_Vov%.2f_%s'%(bar,ov,ds.sipm))
            timingThreshold = findTimingThreshold(f.Get('g_deltaT_totRatioCorr_vs_th_bar%02d_Vov%.2f_enBin01'%(bar,ov)))
            srL = -1
            srR = -1
            sr = -1
            err_srL = -1
            err_srR = -1
            c = ROOT.TCanvas('c_%s_%s'%(g_psL.GetName().replace('g_pulseShapeL','pulseShape'),ds.sipm),'',600,600)  
            #hdummy = ROOT.TH2F('hdummy','', 100, min(g_psL.GetX())-1., 30., 100, 0., 15.)
            hdummy = ROOT.TH2F('hdummy','', 100, min(g_psL.GetX())-1., 5., 100, 0., 15.)
            hdummy.GetXaxis().SetTitle('time [ns]')
            hdummy.GetYaxis().SetTitle('amplitude [#muA]')
            hdummy.Draw()
            gtempL = ROOT.TGraphErrors()
            gtempR = ROOT.TGraphErrors()
            srL,err_srL = getSlewRateFromPulseShape(g_psL, timingThreshold, np, gtempL, c)
            srR,err_srR = getSlewRateFromPulseShape(g_psR, timingThreshold, np, gtempR, c) 
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
            if (srL>0 and srR<0):
                sr = srL
                errSR = err_srL
            if (srL<0 and srR>0):
                sr = srR
                errSR = err_srR
            if (srL<0 and srR<0): continue
            errSR = math.sqrt(errSR*errSR+errSRsyst*errSRsyst*sr*sr) 
            #print (ov, gain, Npe, srL, srR, sr, errSR)
            g_SR_vs_Vov[ds.sipm][bar].SetPoint( g_SR_vs_Vov[ds.sipm][bar].GetN(), ov, sr )
            g_SR_vs_Vov[ds.sipm][bar].SetPointError( g_SR_vs_Vov[ds.sipm][bar].GetN()-1, 0, errSR )
            
            g_SR_vs_GainNpe[ds.sipm][bar].SetPoint( g_SR_vs_GainNpe[ds.sipm][bar].GetN(), gain*Npe[ds.sipm][ov], sr )
            g_SR_vs_GainNpe[ds.sipm][bar].SetPointError( g_SR_vs_GainNpe[ds.sipm][bar].GetN()-1, 0, errSR )
            
            g_bestTh_vs_Vov[ds.sipm][bar].SetPoint( g_bestTh_vs_Vov[ds.sipm][bar].GetN(), ov, timingThreshold )
            g_bestTh_vs_Vov[ds.sipm][bar].SetPointError( g_bestTh_vs_Vov[ds.sipm][bar].GetN()-1, 0, 0 )
            
            g_SR_vs_bar[ds.sipm][ov].SetPoint( g_SR_vs_bar[ds.sipm][ov].GetN(), bar, sr )
            g_SR_vs_bar[ds.sipm][ov].SetPointError( g_SR_vs_bar[ds.sipm][ov].GetN()-1, 0, errSR )
            
            g_bestTh_vs_bar[ds.sipm][ov].SetPoint( g_bestTh_vs_bar[ds.sipm][ov].GetN(), bar, timingThreshold )
            g_bestTh_vs_bar[ds.sipm][ov].SetPointError( g_bestTh_vs_bar[ds.sipm][ov].GetN()-1, 0, 0)
            
            g_Noise_vs_bar[ds.sipm][ov].SetPoint( g_Noise_vs_bar[ds.sipm][ov].GetN(), bar, sigma_noise(sr) )
            g_Noise_vs_bar[ds.sipm][ov].SetPointError( g_Noise_vs_bar[ds.sipm][ov].GetN()-1, 0,  0.5*(sigma_noise(sr*(1-errSR/sr))-sigma_noise(sr*(1+errSR/sr))) )
            g_Noise_vs_Vov[ds.sipm][bar].SetPoint(g_Noise_vs_Vov[ds.sipm][bar].GetN(), ov, sigma_noise(sr))
            g_Noise_vs_Vov[ds.sipm][bar].SetPointError(g_Noise_vs_Vov[ds.sipm][bar].GetN()-1, 0, 0.5*(sigma_noise(sr*(1-errSR/sr))-sigma_noise(sr*(1+errSR/sr))))
            # compute s_stoch as diff in quadrature between measured tRes and noise term
            if ( sigma_meas > sigma_noise(sr) ):
                s = math.sqrt(sigma_meas*sigma_meas-sigma_noise(sr)*sigma_noise(sr))
                es = 1./s * math.sqrt( pow(sigma_meas*g_data[ds.sipm][bar].GetErrorY(i),2) + pow( sigma_noise(sr)*g_Noise_vs_Vov[ds.sipm][bar].GetErrorY(g_Noise_vs_Vov[ds.sipm][bar].GetN()-1),2) )
                g_Stoch_vs_Npe[ds.sipm][bar].SetPoint(g_Stoch_vs_Npe[ds.sipm][bar].GetN(), Npe[ds.sipm][ov], s)
                g_Stoch_vs_Npe[ds.sipm][bar].SetPointError(g_Stoch_vs_Npe[ds.sipm][bar].GetN()-1, 0., es )
            

            # compute stoch by scaling from 3.5 V OV
            stoch = stoch_ref/math.sqrt(  PDE(ds.sipmType,ov)/PDE(ds.sipmType,ov_ref)  )
            stoch_err = stoch_ref_err/math.sqrt( PDE(ds.sipmType,ov)/PDE(ds.sipmType,ov_ref) )
          
            g_Stoch_vs_Vov[ds.sipm][bar].SetPoint(g_Stoch_vs_Vov[ds.sipm][bar].GetN(), ov, stoch)
            g_Stoch_vs_Vov[ds.sipm][bar].SetPointError(g_Stoch_vs_Vov[ds.sipm][bar].GetN()-1, 0, stoch_err)
            
            g_Stoch_vs_bar[ds.sipm][ov].SetPoint( g_Stoch_vs_bar[ds.sipm][ov].GetN(), bar, stoch )
            g_Stoch_vs_bar[ds.sipm][ov].SetPointError( g_Stoch_vs_bar[ds.sipm][ov].GetN()-1, 0,  stoch_err)
            
            # tot resolution summing noise + stochastic in quadrature
            tot = math.sqrt( stoch*stoch + sigma_noise(sr)*sigma_noise(sr) )
            tot_err = 1./tot * math.sqrt( pow( stoch_err*stoch,2) + pow(sigma_noise(sr)*g_Noise_vs_Vov[ds.sipm][bar].GetErrorY(g_Noise_vs_Vov[ds.sipm][bar].GetN()-1),2))
            g_Tot_vs_Vov[ds.sipm][bar].SetPoint(g_Tot_vs_Vov[ds.sipm][bar].GetN(), ov, tot)
            g_Tot_vs_Vov[ds.sipm][bar].SetPointError(g_Tot_vs_Vov[ds.sipm][bar].GetN()-1, 0, tot_err)
            #print sipm,' OV = %.2f  gain = %d  Npe = %d  bar = %02d  thr = %02d  SR = %.1f   noise = %.1f    stoch = %.1f   tot = %.1f'%(ov, gain, Npe, bar, timingThreshold, sr, sigma_noise(sr), stoch, tot)


# average slew rate
g_SR_vs_Vov_average = {}
g_Noise_vs_Vov_average = {}
g_Stoch_vs_Vov_average = {}
g_Tot_vs_Vov_average = {}

g_stoch_vs_NpeTau_average = ROOT.TGraphErrors()                                                

for ds in data_structs:                             
    # stochastic term at the reference OV
    fitpol0_stoch = ROOT.TF1('fitpol0_stoch','pol0',-100,100)  
    g_Stoch_vs_bar[ds.sipm][ov_ref].Fit(fitpol0_stoch,'QNR')
    err_npetau = Npe[ds.sipm][ov_ref]/ds.tau*math.sqrt( pow(0.05,2) + pow(0.03,2) )
    g_stoch_vs_NpeTau_average.SetPoint(g_stoch_vs_NpeTau_average.GetN(), Npe[ds.sipm][ov_ref]/ds.tau, fitpol0_stoch.GetParameter(0))
    g_stoch_vs_NpeTau_average.SetPointError(g_stoch_vs_NpeTau_average.GetN()-1, err_npetau, fitpol0_stoch.GetParError(0))
    
    # average tRes, split contributions
    g_SR_vs_Vov_average[ds.sipm] = ROOT.TGraphErrors()
    g_Noise_vs_Vov_average[ds.sipm] = ROOT.TGraphErrors()
    g_Stoch_vs_Vov_average[ds.sipm] = ROOT.TGraphErrors()
    g_Tot_vs_Vov_average[ds.sipm] = ROOT.TGraphErrors()
    
    stoch_average = fitpol0_stoch.GetParameter(0)
    stoch_average_err = fitpol0_stoch.GetParError(0)
    
    for ov in Vovs[ds.sipm]:                                       
        if (ov in  g_SR_vs_bar[ds.sipm].keys()):
            fitpol0_sr = ROOT.TF1('fitpol0_sr','pol0',-100,100)
            g_SR_vs_bar[ds.sipm][ov].Fit(fitpol0_sr,'QNR')
            sr = fitpol0_sr.GetParameter(0)
            g_SR_vs_Vov_average[ds.sipm].SetPoint(g_SR_vs_Vov_average[ds.sipm].GetN(), ov, sr)
            g_SR_vs_Vov_average[ds.sipm].SetPointError(g_SR_vs_Vov_average[ds.sipm].GetN()-1, 0, fitpol0_sr.GetParError(0)) 

            # noise using average SR
            g_Noise_vs_Vov_average[ds.sipm].SetPoint(g_Noise_vs_Vov_average[ds.sipm].GetN(), ov, sigma_noise(sr))
            sr_err = max(fitpol0_sr.GetParError(0), errSRsyst*sr)
            sr_up   = sr + sr_err 
            sr_down = sr - sr_err 
            noise_err  = 0.5 * ( sigma_noise(sr_down) - sigma_noise(sr_up) ) 
            g_Noise_vs_Vov_average[ds.sipm].SetPointError(g_Noise_vs_Vov_average[ds.sipm].GetN()-1, 0, noise_err) 
    
            # compute stoch by scaling from 3.5 V OV
            stoch = stoch_average/math.sqrt(  PDE(ds.sipmType,ov)/PDE(ds.sipmType,ov_ref)  )
            stoch_err = stoch_average_err/math.sqrt( PDE(ds.sipmType,ov)/PDE(ds.sipmType,ov_ref) )
            g_Stoch_vs_Vov_average[ds.sipm].SetPoint(g_Stoch_vs_Vov_average[ds.sipm].GetN(), ov, stoch)
            g_Stoch_vs_Vov_average[ds.sipm].SetPointError(g_Stoch_vs_Vov_average[ds.sipm].GetN()-1, 0, stoch_err)

            # tot resolution summing noise + stochastic in quadrature
            tot = math.sqrt( stoch*stoch + sigma_noise(sr)*sigma_noise(sr) )
            tot_err = 1./tot * math.sqrt( pow( stoch_err*stoch,2) + pow(noise_err*sigma_noise(sr),2))
            g_Tot_vs_Vov_average[ds.sipm].SetPoint(g_Tot_vs_Vov_average[ds.sipm].GetN(), ov, tot)
            g_Tot_vs_Vov_average[ds.sipm].SetPointError(g_Tot_vs_Vov_average[ds.sipm].GetN()-1, 0, tot_err)


# ratio of stochatic terms at 3.5 OV
'''
g_ratio_stoch1 = ROOT.TGraphErrors()
g_ratio_stoch2 = ROOT.TGraphErrors()
g_ratio_stoch3 = ROOT.TGraphErrors()
for bar in range(0,16):
    if (bar not in bars[sipms[1]]): continue
    if (bar not in bars[sipms[0]]): continue
    if (g_Stoch_vs_Vov[sipms[0]][bar].Eval(3.5)<=0): continue
    ratio_stoch =  g_Stoch_vs_Vov[sipms[1]][bar].Eval(3.5)/g_Stoch_vs_Vov[sipms[0]][bar].Eval(3.5)
    err1 = [  g_Stoch_vs_Vov[sipms[1]][bar].GetErrorY(i) for i in range(0, g_Stoch_vs_Vov[sipms[1]][bar].GetN()) if g_Stoch_vs_Vov[sipms[1]][bar].GetX()[i] == 3.50]
    err0 = [  g_Stoch_vs_Vov[sipms[0]][bar].GetErrorY(i) for i in range(0, g_Stoch_vs_Vov[sipms[0]][bar].GetN()) if g_Stoch_vs_Vov[sipms[0]][bar].GetX()[i] == 3.50]
    if (err1 == [] or err0 == []): continue
    err_ratio_stoch = ratio_stoch * math.sqrt( pow(err1[0]/g_Stoch_vs_Vov[sipms[1]][bar].Eval(3.5),2) + pow(err0[0]/g_Stoch_vs_Vov[sipms[0]][bar].Eval(3.5),2) ) 
    print sipms[1], sipms[0], ' ratio stochastic term at 3.5 V OV = ', ratio_stoch
    g_ratio_stoch1.SetPoint(g_ratio_stoch1.GetN(), bar, ratio_stoch)
    g_ratio_stoch1.SetPointError(g_ratio_stoch1.GetN()-1, 0, err_ratio_stoch)

if (len(sipms)>2):

    for bar in range(0,16):
        if (bar not in bars[sipms[1]]): continue
        if ( len(sipms)>2 and bar not in bars[sipms[2]]): continue
        if ( len(sipms)>2 and g_Stoch_vs_Vov[sipms[2]][bar].Eval(3.5)<=0): continue
        if (g_Stoch_vs_Vov[sipms[1]][bar].Eval(3.5)<=0): continue
        ratio_stoch =  g_Stoch_vs_Vov[sipms[1]][bar].Eval(3.5)/g_Stoch_vs_Vov[sipms[2]][bar].Eval(3.5)
        err1 = [  g_Stoch_vs_Vov[sipms[1]][bar].GetErrorY(i) for i in range(0, g_Stoch_vs_Vov[sipms[1]][bar].GetN()) if g_Stoch_vs_Vov[sipms[1]][bar].GetX()[i] == 3.50]
        err0 = [  g_Stoch_vs_Vov[sipms[2]][bar].GetErrorY(i) for i in range(0, g_Stoch_vs_Vov[sipms[2]][bar].GetN()) if g_Stoch_vs_Vov[sipms[2]][bar].GetX()[i] == 3.50]
        if (err1 == [] or err0 == []): continue
        err_ratio_stoch = ratio_stoch * math.sqrt( pow(err1[0]/g_Stoch_vs_Vov[sipms[1]][bar].Eval(3.5),2) + pow(err0[0]/g_Stoch_vs_Vov[sipms[2]][bar].Eval(3.5),2) ) 
        print sipms[1], sipms[2],' ratio stochastic term at 3.5 V OV = ', ratio_stoch
        g_ratio_stoch2.SetPoint(g_ratio_stoch2.GetN(), bar, ratio_stoch)
        g_ratio_stoch2.SetPointError(g_ratio_stoch2.GetN()-1, 0, err_ratio_stoch)


    for bar in range(0,16):
        if (bar not in bars[sipms[0]]): continue
        if (bar not in bars[sipms[2]]): continue
        if (g_Stoch_vs_Vov[sipms[2]][bar].Eval(3.5)<=0): continue
        if (g_Stoch_vs_Vov[sipms[0]][bar].Eval(3.5)<=0): continue
        ratio_stoch =  g_Stoch_vs_Vov[sipms[0]][bar].Eval(3.5)/g_Stoch_vs_Vov[sipms[2]][bar].Eval(3.5)
        err1 = [  g_Stoch_vs_Vov[sipms[0]][bar].GetErrorY(i) for i in range(0, g_Stoch_vs_Vov[sipms[0]][bar].GetN()) if g_Stoch_vs_Vov[sipms[0]][bar].GetX()[i] == 3.50]
        err0 = [  g_Stoch_vs_Vov[sipms[2]][bar].GetErrorY(i) for i in range(0, g_Stoch_vs_Vov[sipms[2]][bar].GetN()) if g_Stoch_vs_Vov[sipms[2]][bar].GetX()[i] == 3.50]
        if (err1 == [] or err0 == []): continue
        err_ratio_stoch = ratio_stoch * math.sqrt( pow(err1[0]/g_Stoch_vs_Vov[sipms[0]][bar].Eval(3.5),2) + pow(err0[0]/g_Stoch_vs_Vov[sipms[2]][bar].Eval(3.5),2) ) 
        print sipms[0], sipms[2],' ratio stochastic term at 3.5 V OV = ', ratio_stoch
        g_ratio_stoch3.SetPoint(g_ratio_stoch3.GetN(), bar, ratio_stoch)
        g_ratio_stoch3.SetPointError(g_ratio_stoch3.GetN()-1, 0, err_ratio_stoch)
'''
        
# draw
c1 = {}
c2 = {}
c3 = {}
c4 = {}
hdummy1 = {}
hdummy2 = {}
hdummy3 = {}
hdummy4 = {}
leg = {}

h = {}
for ds in data_structs:
    c1[ds.sipm] = {}
    hdummy1[ds.sipm] = {}
    c2[ds.sipm] = {}
    hdummy2[ds.sipm] = {}
    h[ds.sipm] = ROOT.TH1F('h_coeff_%s'%ds.sipm,'',100,-2.0,1.0)
    leg[ds.sipm] = ROOT.TLegend(0.60,0.70,0.85,0.89) 
    leg[ds.sipm].SetBorderSize(0)
    leg[ds.sipm].SetFillStyle(0) 
    for i,bar in enumerate(bars[ds.sipm]):
        c1[ds.sipm][bar] =  ROOT.TCanvas('c_timeResolution_vs_Vov_%s_bar%02d'%(ds.sipm,bar),'c_timeResolution_vs_Vov_%s_bar%02d'%(ds.sipm,bar),600,600)
        c1[ds.sipm][bar].SetGridy()
        c1[ds.sipm][bar].cd()
        hdummy1[ds.sipm][bar] = ROOT.TH2F('hdummy1_%s_%d'%(ds.sipm,bar),'',100,0,5,100,0,100)
        hdummy1[ds.sipm][bar].GetXaxis().SetTitle('V_{OV} [V]')
        hdummy1[ds.sipm][bar].GetYaxis().SetTitle('#sigma_{t} [ps]')
        hdummy1[ds.sipm][bar].Draw()
        g_data[ds.sipm][bar].SetMarkerStyle(20)
        g_data[ds.sipm][bar].SetMarkerSize(1)
        g_data[ds.sipm][bar].SetMarkerColor(1)
        g_data[ds.sipm][bar].SetLineColor(1)
        g_data[ds.sipm][bar].SetLineWidth(2)
        g_data[ds.sipm][bar].Draw('plsame')
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
        g_Tot_vs_Vov[ds.sipm][bar].SetLineWidth(2)
        g_Tot_vs_Vov[ds.sipm][bar].SetLineColor(ROOT.kRed+1)
        g_Tot_vs_Vov[ds.sipm][bar].SetFillColor(ROOT.kRed+1)
        g_Tot_vs_Vov[ds.sipm][bar].SetFillColorAlpha(ROOT.kRed+1,0.5)
        g_Tot_vs_Vov[ds.sipm][bar].SetFillStyle(3001)
        g_Tot_vs_Vov[ds.sipm][bar].Draw('E3lsame')
        #save on file
        outfile.cd()
        g_data[ds.sipm][bar].Write('g_Data_vs_Vov_%s_bar%02d'%(ds.sipm,bar))
        g_Noise_vs_Vov[ds.sipm][bar].Write('g_Noise_vs_Vov_%s_bar%02d'%(ds.sipm,bar))
        g_Stoch_vs_Vov[ds.sipm][bar].Write('g_Stoch_vs_Vov_%s_bar%02d'%(ds.sipm,bar))
        g_Tot_vs_Vov[ds.sipm][bar].Write('g_Tot_vs_Vov_%s_bar%02d'%(ds.sipm,bar))
        if (i==0):
            leg[ds.sipm].AddEntry(g_data[ds.sipm][bar], 'data', 'PL')
            leg[ds.sipm].AddEntry(g_Noise_vs_Vov[ds.sipm][bar], 'noise', 'L')
            leg[ds.sipm].AddEntry(g_Stoch_vs_Vov[ds.sipm][bar], 'stoch', 'L')
            leg[ds.sipm].AddEntry(g_Tot_vs_Vov[ds.sipm][bar], 'stoch #oplus noise', 'L')
        leg[ds.sipm].Draw('same')
        latex = ROOT.TLatex(0.20,0.86,'%s'%(ds.sipm.replace('_nonIrr_','+')))
        latex.SetNDC()
        latex.SetTextSize(0.045)
        latex.SetTextFont(42)
        latex.Draw('same')
        c1[ds.sipm][bar].SaveAs(outdir+'/'+c1[ds.sipm][bar].GetName()+'.png')
        c1[ds.sipm][bar].SaveAs(outdir+'/'+c1[ds.sipm][bar].GetName()+'.pdf')

        # vs npe
        c2[ds.sipm][bar] =  ROOT.TCanvas('c_timeResolution_vs_Npe_%s_bar%02d'%(ds.sipm,bar),'c_timeResolution_vs_Npe_%s_bar%02d'%(ds.sipm,bar),600,600)
        c2[ds.sipm][bar].SetGridy()
        c2[ds.sipm][bar].cd()
        hdummy2[ds.sipm][bar] = ROOT.TH2F('hdummy2_%s_%d'%(ds.sipm,bar),'',10000,1000,10000,100,0,100)
        hdummy2[ds.sipm][bar].GetXaxis().SetTitle('Npe')
        hdummy2[ds.sipm][bar].GetYaxis().SetTitle('#sigma_{t} [ps]')
        hdummy2[ds.sipm][bar].Draw()
        g_Stoch_vs_Npe[ds.sipm][bar].SetMarkerStyle(20)
        g_Stoch_vs_Npe[ds.sipm][bar].SetMarkerSize(0.8)
        g_Stoch_vs_Npe[ds.sipm][bar].SetMarkerColor(ROOT.kGreen+2)
        g_Stoch_vs_Npe[ds.sipm][bar].SetLineWidth(1)
        g_Stoch_vs_Npe[ds.sipm][bar].SetLineColor(ROOT.kGreen+2)
        g_Stoch_vs_Npe[ds.sipm][bar].Draw('psame')
        fitFun = ROOT.TF1('fitFun_%s_%.2d'%(ds.sipm,bar),'[0]*pow(x,[1])',2000,9500)
        fitFun.SetParameters(30,-0.5)
        fitFun.SetLineColor(ROOT.kGreen+3)
        g_Stoch_vs_Npe[ds.sipm][bar].Fit(fitFun,'QRS+')
        if (fitFun.GetNDF()>0): h[ds.sipm].Fill(fitFun.GetParameter(1))
        c2[ds.sipm][bar].SaveAs(outdir+'/'+c2[ds.sipm][bar].GetName()+'.png')
        c2[ds.sipm][bar].SaveAs(outdir+'/'+c2[ds.sipm][bar].GetName()+'.pdf')

    ROOT.gStyle.SetOptStat(1111)
    cc =  ROOT.TCanvas('c_coeff_%s'%(ds.sipm),'c_coeff_%s'%(ds.sipm),600,600)
    h[ds.sipm].GetXaxis().SetTitle('#alpha')
    h[ds.sipm].Draw('')
    cc.SaveAs(outdir+'/'+cc.GetName()+'.png')
    ROOT.gStyle.SetOptStat(0)



# SR and best threshold vs Vov
print('Plotting slew rate vs Vov...')

leg2 = ROOT.TLegend(0.20,0.70,0.45,0.89)
leg2.SetBorderSize(0)
leg2.SetFillStyle(0)
for i,bar in enumerate(bars[ds.sipm]):
    c3[bar] = ROOT.TCanvas('c_slewRate_vs_Vov_bar%02d'%(bar),'c_slewRate_vs_Vov_bar%02d'%(bar),600,600)
    c3[bar].SetGridy()
    c3[bar].cd()
    hdummy3[bar] = ROOT.TH2F('hdummy3_%d'%(bar),'',100,0,5,100,0,35)
    hdummy3[bar].GetXaxis().SetTitle('V_{OV} [V]')
    hdummy3[bar].GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
    hdummy3[bar].Draw()
    for j,ds in enumerate(data_structs):
        if (bar not in g_SR_vs_Vov[ds.sipm].keys()):continue
        if (bar == 8):
            leg2.AddEntry(g_SR_vs_Vov[ds.sipm][bar], '%s'%(ds.label), 'PL')
        g_SR_vs_Vov[ds.sipm][bar].SetMarkerStyle( ds.marker )
        g_SR_vs_Vov[ds.sipm][bar].SetMarkerColor(ds.color)
        g_SR_vs_Vov[ds.sipm][bar].SetLineColor(ds.color)
        g_SR_vs_Vov[ds.sipm][bar].Draw('psame')
        outfile.cd()
        g_SR_vs_Vov[ds.sipm][bar].Write('g_SR_vs_Vov_%s_bar%02d'%(ds.sipm,bar))
    leg2.Draw()
    c3[bar].SaveAs(outdir+'/'+c3[bar].GetName()+'.png')
    c3[bar].SaveAs(outdir+'/'+c3[bar].GetName()+'.pdf')
    hdummy3[bar].Delete() 

    c3[bar] = ROOT.TCanvas('c_slewRate_vs_GainNpe_bar%02d'%(bar),'c_slewRate_vs_GainNpe_bar%02d'%(bar),600,600)
    c3[bar].SetGridy()
    c3[bar].cd()
    #hdummy3[bar] = ROOT.TH2F('hdummy3_%d'%(bar),'',100,0,2,100,0,35)
    hdummy3[bar] = ROOT.TH2F('hdummy3_sr_%d'%(bar),'',100,0,3E09,100,0,35)
    hdummy3[bar].GetXaxis().SetTitle('gain x Npe')
    hdummy3[bar].GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
    hdummy3[bar].Draw()
    for j,ds in enumerate(data_structs):
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
    hdummy4[bar] = ROOT.TH2F('hdummy4_%d'%(bar),'',100,0,5,100,0,20)
    hdummy4[bar].GetXaxis().SetTitle('V_{OV} [V]')
    hdummy4[bar].GetYaxis().SetTitle('best threshold [DAC]')
    hdummy4[bar].Draw()
    for j,ds in enumerate(data_structs):
        if (bar not in g_bestTh_vs_Vov[ds.sipm].keys()):continue
        g_bestTh_vs_Vov[ds.sipm][bar].SetMarkerStyle( ds.marker )
        g_bestTh_vs_Vov[ds.sipm][bar].SetMarkerColor(ds.color)
        g_bestTh_vs_Vov[ds.sipm][bar].SetLineColor(ds.color)
        g_bestTh_vs_Vov[ds.sipm][bar].Draw('plsame')
    leg2.Draw()
    c4[bar].SaveAs(outdir+'/'+c4[bar].GetName()+'.png')
    c4[bar].SaveAs(outdir+'/'+c4[bar].GetName()+'.pdf')


# average slew rate vs OV
c2 =  ROOT.TCanvas('c_slewRate_vs_Vov_average','c_slewRate_vs_Vov_average',600,600)
c2.SetGridx()
c2.SetGridy()
c2.cd()    
#hdummy2 = ROOT.TH2F('hdummy2','',16, 0.5, 2.7,100,0,15)
hdummy2 = ROOT.TH2F('hdummy2','',100, 0., 5.,100,0,35)
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
    g_SR_vs_Vov_average[ds.sipm].Write('g_SR_vs_Vov_average_%s'%ds.sipm)
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
    c2 =  ROOT.TCanvas('c_timeResolution_vs_Vov_average_%s'%ds.sipm,'c_timeResolution_vs_Vov_average_%s'%ds.sipm,600,600)
    c2.SetGridx()
    c2.SetGridy()
    c2.cd()    
    hdummy2 = ROOT.TH2F('hdummy2','',100, 0., 5.,100,0,120)
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
    g_Tot_vs_Vov_average[ds.sipm].SetLineWidth(2)
    g_Tot_vs_Vov_average[ds.sipm].SetLineColor(ROOT.kRed+1)
    g_Tot_vs_Vov_average[ds.sipm].SetFillColor(ROOT.kRed+1)
    g_Tot_vs_Vov_average[ds.sipm].SetFillColorAlpha(ROOT.kRed+1,0.5)
    g_Tot_vs_Vov_average[ds.sipm].SetFillStyle(3001)
    g_Tot_vs_Vov_average[ds.sipm].Draw('E3lsame')
    leg[ds.sipm].Draw()
    latex.Draw()
    outfile.cd()
    g_Noise_vs_Vov_average[ds.sipm].Write('g_Noise_vs_Vov_average_%s'%ds.sipm)
    g_Stoch_vs_Vov_average[ds.sipm].Write('g_Stoch_vs_Vov_average_%s'%ds.sipm)
    g_Tot_vs_Vov_average[ds.sipm].Write('g_Tot_vs_Vov_average_%s'%ds.sipm)
    c2.SaveAs(outdir+'/'+c2.GetName()+'.png')
    c2.SaveAs(outdir+'/'+c2.GetName()+'.pdf')
    hdummy2.Delete()



# average stoch. term vs Npe/tau
ROOT.gStyle.SetOptFit(111)
c2 =  ROOT.TCanvas('c_stoch_vs_NpeTau_average','c_stoch_vs_NpeTau_average',600,600)
c2.SetGridx()
c2.SetGridy()
c2.cd()    
hdummy2 = ROOT.TH2F('hdummy2','',100, 40, 300, 100, 0, 100)
hdummy2.GetXaxis().SetTitle('Npe/tau [p.e./ns]')
hdummy2.GetYaxis().SetTitle('#sigma_{t,stoch} [ps]')
hdummy2.Draw()
g_stoch_vs_NpeTau_average.Draw('psame')
fitFunStoch = ROOT.TF1('fitFunStoch','[0]*pow(x,[1])', 0, 1000)
fitFunStoch.SetNpx(10000)
fitFunStoch.SetLineStyle(2)
fitFunStoch.SetLineWidth(1)
fitFunStoch.SetLineColor(2)
fitFunStoch.SetParameters(30, -0.5)
g_stoch_vs_NpeTau_average.Fit(fitFunStoch)
#print fitFunStoch.GetChisquare()/fitFunStoch.GetNDF()
c2.SaveAs(outdir+'/'+c2.GetName()+'.png')
c2.SaveAs(outdir+'/'+c2.GetName()+'.pdf')
hdummy2.Delete()


    
# SR and best threshold vs bar
print('Plotting slew rate vs bar...')
c5 = {}
hdummy5 = {}
c6 = {}
hdummy6 = {}
c7 = {}
hdummy7 = {}
c8 = {}
hdummy8 = {}
for ov in Vovs[ds.sipm]:
    c5[ov] = ROOT.TCanvas('c_slewRate_vs_bar_Vov%.2f'%(ov),'c_slewRate_vs_bar_Vov%.2f'%(ov),600,600)
    c5[ov].SetGridy()
    c5[ov].cd()
    ymax = 40.
    hdummy5[ov] = ROOT.TH2F('hdummy5_%s_%d'%(ds.sipm,ov),'',100,-0.5,15.5,100,0,ymax)
    hdummy5[ov].GetXaxis().SetTitle('bar')
    hdummy5[ov].GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
    hdummy5[ov].Draw()
    for j,ds in enumerate(data_structs):
        if (ov not in g_SR_vs_bar[ds.sipm].keys()): continue
        g_SR_vs_bar[ds.sipm][ov].SetMarkerStyle( ds.marker )
        g_SR_vs_bar[ds.sipm][ov].SetMarkerColor(ds.color)
        g_SR_vs_bar[ds.sipm][ov].SetLineColor(ds.color)
        g_SR_vs_bar[ds.sipm][ov].Draw('psame')
    leg2.Draw()
    latex = ROOT.TLatex(0.65,0.82,'V_{OV} = %.02f V'%ov)
    latex.SetNDC()
    latex.SetTextSize(0.035)
    latex.SetTextFont(42)
    latex.Draw('same')
    c5[ov].SaveAs(outdir+'/'+c5[ov].GetName()+'.png')
    c5[ov].SaveAs(outdir+'/'+c5[ov].GetName()+'.pdf')
    hdummy5[ov].Delete()

    c6[ov] = ROOT.TCanvas('c_bestTh_vs_bar_Vov%.2f'%(ov),'c_bestTh_vs_bar_Vov%.2f'%(ov),600,600)
    c6[ov].SetGridy()
    c6[ov].cd()
    hdummy6[ov] = ROOT.TH2F('hdummy6_%s_%d'%(ds.sipm,ov),'',100,-0.5,15.5,100,0,20)
    hdummy6[ov].GetXaxis().SetTitle('bar')
    hdummy6[ov].GetYaxis().SetTitle('timing threshold [DAC]')
    hdummy6[ov].Draw()
    for j,ds in enumerate(data_structs):
        if (ov not in g_bestTh_vs_bar[ds.sipm].keys()): continue
        g_bestTh_vs_bar[ds.sipm][ov].SetMarkerStyle( ds.marker )
        g_bestTh_vs_bar[ds.sipm][ov].SetMarkerColor(ds.color)
        g_bestTh_vs_bar[ds.sipm][ov].SetLineColor(ds.color)
        g_bestTh_vs_bar[ds.sipm][ov].Draw('plsame')
    leg2.Draw()        
    c6[ov].SaveAs(outdir+'/'+c6[ov].GetName()+'.png')
    c6[ov].SaveAs(outdir+'/'+c6[ov].GetName()+'.pdf')
    hdummy6[ov].Delete() 

    c7[ov] = ROOT.TCanvas('c_noise_vs_bar_Vov%.2f'%(ov),'c_noise_vs_bar_Vov%.2f'%(ov),600,600)
    c7[ov].SetGridy()
    c7[ov].cd()
    hdummy7[ov] = ROOT.TH2F('hdummy7_%s_%d'%(ds.sipm,ov),'',100,-0.5,15.5,100,0,100)
    hdummy7[ov].GetXaxis().SetTitle('bar')
    hdummy7[ov].GetYaxis().SetTitle('#sigma_{t, noise} [ps]')
    hdummy7[ov].Draw()
    for j,ds in enumerate(data_structs):
        if (ov not in g_Noise_vs_bar[ds.sipm].keys()): continue
        g_Noise_vs_bar[ds.sipm][ov].SetMarkerStyle( ds.marker )
        g_Noise_vs_bar[ds.sipm][ov].SetMarkerColor(ds.color)
        g_Noise_vs_bar[ds.sipm][ov].SetLineColor(ds.color)
        g_Noise_vs_bar[ds.sipm][ov].Draw('psame')
    leg2.Draw()        
    latex = ROOT.TLatex(0.65,0.82,'V_{OV} = %.02f V'%ov)
    latex.SetNDC()
    latex.SetTextSize(0.035)
    latex.SetTextFont(42)
    latex.Draw('same')
    c7[ov].SaveAs(outdir+'/'+c7[ov].GetName()+'.png')
    c7[ov].SaveAs(outdir+'/'+c7[ov].GetName()+'.pdf')
    hdummy7[ov].Delete() 

    c8[ov] = ROOT.TCanvas('c_stoch_vs_bar_Vov%.2f'%(ov),'c_stoch_vs_bar_Vov%.2f'%(ov),600,600)
    c8[ov].SetGridy()
    c8[ov].cd()
    hdummy8[ov] = ROOT.TH2F('hdummy8_%s_%d'%(ds.sipm,ov),'',100,-0.5,15.5,100,0,100)
    hdummy8[ov].GetXaxis().SetTitle('bar')
    hdummy8[ov].GetYaxis().SetTitle('#sigma_{t, stoch} [ps]')
    hdummy8[ov].Draw()
    for j,ds in enumerate(data_structs):
        if (ov not in g_Stoch_vs_bar[ds.sipm].keys()): continue
        g_Stoch_vs_bar[ds.sipm][ov].SetMarkerStyle( ds.marker )
        g_Stoch_vs_bar[ds.sipm][ov].SetMarkerColor(ds.color)
        g_Stoch_vs_bar[ds.sipm][ov].SetLineColor(ds.color)
        g_Stoch_vs_bar[ds.sipm][ov].Draw('psame')
    leg2.Draw()        
    c8[ov].SaveAs(outdir+'/'+c8[ov].GetName()+'.png')
    c8[ov].SaveAs(outdir+'/'+c8[ov].GetName()+'.pdf')
    hdummy8[ov].Delete() 

# ratio of photo-stat. terms:
'''
glist = [g_ratio_stoch1]
if (len(sipms) > 2): 
    glist.append(g_ratio_stoch2)
    glist.append(g_ratio_stoch3)

for i,g in enumerate(glist):
    if i == 0:
        sipm1 = sipms[1]
        sipm2 = sipms[0]
    if i == 1:
        sipm1 = sipms[1]
        sipm2 = sipms[2]
    if i == 2:
        sipm1 = sipms[0]
        sipm2 = sipms[2]
    
    cc = ROOT.TCanvas('c_ratioStoch_vs_bar_%s_%s'%(sipm1, sipm2),'c_ratioStoch_vs_bar_%s_%s_'%(sipm1, sipm2),600,600)
    print cc.GetName()
    cc.cd()
    hdummy = ROOT.TH2F('hdummy','',16,-0.5,15.5,100,0.2,1.5)
    hdummy.GetXaxis().SetTitle('bar')
    hdummy.GetYaxis().SetTitle('#sigma_{stoch.}^{%s}/#sigma_{stoch.}^{%s}'%(labels[sipm1],labels[sipm2]))
    hdummy.GetYaxis().SetTitleOffset(1.1)
    hdummy.Draw('')
    g.SetMarkerStyle(20)
    g.Draw('psame')
    expRatioLO    = math.sqrt(Npe[sipm2][ov_ref]/Npe[sipm1][ov_ref])
    expRatioLOTau = math.sqrt((Npe[sipm2][ov_ref]/tau[sipm2])/(Npe[sipm1][ov_ref]/tau[sipm1]))
    ll = ROOT.TLine(0, expRatioLO, 15, expRatioLO)
    ll.SetLineStyle(7)
    ll.SetLineWidth(2)
    ll.SetLineColor(ROOT.kGray+1)
    ll.Draw('same')
    lll = ROOT.TLine(0, expRatioLOTau, 15, expRatioLOTau)
    lll.SetLineStyle(7)
    lll.SetLineWidth(2)
    lll.SetLineColor(ROOT.kBlue)
    lll.Draw('same')
    leg2 = ROOT.TLegend(0.20,0.20,0.60,0.40)
    leg2.SetBorderSize(0)
    leg2.AddEntry(g,'ratio of photostat. terms','PL')
    leg2.AddEntry(ll,'sqrt(LO) = %.2f'%expRatioLO,'L')
    leg2.AddEntry(lll,'sqrt(LO/#tau) = %.2f'%expRatioLOTau,'L')
    leg2.Draw('same')
    fitFun=ROOT.TF1('fitFun','pol0',0,16)
    fitFun.SetLineColor(1)
    g.Fit(fitFun,'QRS')
    hint = ROOT.TH1F("hint","Fitted Gaussian with .95 conf.band", 16, -0.5, 15.5);
    hint.SetMarkerStyle(1)
    hint.SetMarkerSize(0)
    tvf = ROOT.TVirtualFitter.GetFitter()
    tvf.GetConfidenceIntervals(hint);
    hint.SetFillColorAlpha(1,0.2);
    hint.Draw("e3 same");
    print 'ratio of stoch. terms expected from sqrt(LO)      = ', expRatioLO
    print 'ratio of stoch. terms expected from sqrt(LO/tau)  = ', expRatioLOTau
    print 'ratio of stoch. terms measured at 3.5 V           = ', fitFun.GetParameter(0)
    cc.SaveAs(outdir+'/'+cc.GetName()+'.png')                        
    cc.SaveAs(outdir+'/'+cc.GetName()+'.pdf')                        
    hdummy.Delete()
'''

for ds in data_structs: 
    for ov in Vovs[ds.sipm]:
            print(ds.sipm, ov, '  average stoch. term = ', g_Stoch_vs_bar[ds.sipm][ov].GetMean(2),' ps' )
            print(ds.sipm, ov, '  average noise  term = ', g_Noise_vs_bar[ds.sipm][ov].GetMean(2),' ps')
    

outfile.Close()    

