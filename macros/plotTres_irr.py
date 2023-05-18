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
from data_structures import *



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
        if ( y < ymin):
            ymin = y
            xmin = x 
    return xmin
    


# =====================================


# =====================================
# import file with VovEff and DCR
with open('/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_May2023/VovsEff.json', 'r') as f:
    data = json.load(f)       


# =====================================
#outdir = '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_2E14_20um_25um/'
outdir = '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_1E14_25um_T1/'
if (os.path.exists(outdir)==False):
    os.mkdir(outdir)
if (os.path.exists(outdir+'/plotsSR')==False):
    os.mkdir(outdir+'/plotsSR/')


#outfile   = ROOT.TFile.Open(outdir+'/plots_timeResolution_2E14_20um_25um_TBMay23.root','recreate')
outfile   = ROOT.TFile.Open(outdir+'/plots_timeResolution_1E14_25um_T1_TBMay23.root','recreate')

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
g_data_vs_staticPower = {}
g_data_vs_GainNpe = {}

bars = {}
Vovs = {}
Npe = {}
gain = {}

for ds in data_structs:
    f = ROOT.TFile.Open(ds.fName)
    print(ds.moduleLabel, ds.fName)

    listOfKeys = [key.GetName().replace('g_deltaT_energyRatioCorr_bestTh_vs_vov_','') for key in ROOT.gDirectory.GetListOfKeys() if ( 'g_deltaT_energyRatioCorr_bestTh_vs_vov_bar' in key.GetName())]
    bars[ds.moduleLabel] = []
    for k in listOfKeys:
        bars[ds.moduleLabel].append( int(k[3:5]) )

    listOfKeys2 = [key.GetName().replace('g_deltaT_energyRatioCorr_bestTh_vs_bar_','') for key in ROOT.gDirectory.GetListOfKeys() if key.GetName().startswith('g_deltaT_energyRatioCorr_bestTh_vs_bar_')]
    Vovs[ds.moduleLabel] = []
    for k in listOfKeys2:
        Vovs[ds.moduleLabel].append( float(k[3:7]) )

    if ( 'HPK_2E14_LYSO825' in ds.moduleLabel ): Vovs[ds.moduleLabel].remove(0.6) # too small signals for reasonable SR fits
    print(bars[ds.moduleLabel])
    print(Vovs[ds.moduleLabel])

    
fPS = {}
f   = {}

for ds in data_structs:
    f[ds.moduleLabel] = ROOT.TFile.Open(ds.fName)
    
    g_data_average[ds.moduleLabel] = f[ds.moduleLabel].Get('g_deltaT_totRatioCorr_bestTh_vs_vov_enBin01_average')

    Npe[ds.moduleLabel] = {}
    gain[ds.moduleLabel] = {}

    g_data[ds.moduleLabel] = {}
    g_Noise_vs_Vov[ds.moduleLabel] = {}
    g_Stoch_vs_Vov[ds.moduleLabel] = {}
    g_DCR_vs_Vov[ds.moduleLabel] = {}
    g_Tot_vs_Vov[ds.moduleLabel] = {}

    g_Tot_vs_SR[ds.moduleLabel] = {}

    g_Stoch_vs_Npe[ds.moduleLabel] = {}
    g_DCR_vs_Npe[ds.moduleLabel] = {}

    g_SR_vs_Vov[ds.moduleLabel] = {}
    g_SR_vs_GainNpe[ds.moduleLabel] = {}
    g_bestTh_vs_Vov[ds.moduleLabel] = {}

    g_SR_vs_bar[ds.moduleLabel] = {}
    g_bestTh_vs_bar[ds.moduleLabel] = {}
    g_Noise_vs_bar[ds.moduleLabel] = {}
    g_Stoch_vs_bar[ds.moduleLabel] = {}
    g_DCR_vs_bar[ds.moduleLabel] = {}

    g_data_vs_Npe[ds.moduleLabel] = ROOT.TGraphErrors()
    g_data_vs_DCR[ds.moduleLabel] = ROOT.TGraphErrors()
    g_data_vs_staticPower[ds.moduleLabel] = ROOT.TGraphErrors()
    g_data_vs_GainNpe[ds.moduleLabel] = ROOT.TGraphErrors()
    

    fPS[ds.moduleLabel] = {}
    for ov in Vovs[ds.moduleLabel]:
        print(ds.fNamePS+'_Vov%.2f_T%dC.root'%(ov,ds.temperature))
        if (ds.temperature == -35 and ds.lyso == 'LYSO815'):
            fPS[ds.moduleLabel][ov] = ROOT.TFile.Open(ds.fNamePS+'_Vov%.2f_angle52_T%dC.root'%(ov,ds.temperature))
        else:
            fPS[ds.moduleLabel][ov] = ROOT.TFile.Open(ds.fNamePS+'_Vov%.2f_T%dC.root'%(ov,ds.temperature))


        g_SR_vs_bar[ds.moduleLabel][ov] = ROOT.TGraphErrors()
        g_bestTh_vs_bar[ds.moduleLabel][ov] = ROOT.TGraphErrors()
        g_Noise_vs_bar[ds.moduleLabel][ov] = ROOT.TGraphErrors()
        g_Stoch_vs_bar[ds.moduleLabel][ov] = ROOT.TGraphErrors()
        g_DCR_vs_bar[ds.moduleLabel][ov] = ROOT.TGraphErrors()
        g_Tot_vs_SR[ds.moduleLabel][ov] = ROOT.TGraphErrors()

        
    for bar in bars[ds.moduleLabel]:
        g_data[ds.moduleLabel][bar] = f[ds.moduleLabel].Get('g_deltaT_totRatioCorr_bestTh_vs_vov_bar%02d_enBin01;1'%bar)
        if (g_data[ds.moduleLabel][bar].GetN()==0): 
            print('No data for bar ', bar)
            continue

        g_Noise_vs_Vov[ds.moduleLabel][bar] = ROOT.TGraphErrors()
        g_Stoch_vs_Vov[ds.moduleLabel][bar] = ROOT.TGraphErrors()
        g_DCR_vs_Vov[ds.moduleLabel][bar] = ROOT.TGraphErrors()
        g_Tot_vs_Vov[ds.moduleLabel][bar] = ROOT.TGraphErrors()

        g_Stoch_vs_Npe[ds.moduleLabel][bar] = ROOT.TGraphErrors()
        g_DCR_vs_Npe[ds.moduleLabel][bar] = ROOT.TGraphErrors()

        g_SR_vs_Vov[ds.moduleLabel][bar] = ROOT.TGraphErrors()
        g_SR_vs_GainNpe[ds.moduleLabel][bar] = ROOT.TGraphErrors()
        g_bestTh_vs_Vov[ds.moduleLabel][bar] = ROOT.TGraphErrors()
                   
        for ov in Vovs[ds.moduleLabel]:
            ovEff = getVovEffDCR(data, ds.lyso, (ds.sipm+'_T%dC'%ds.temperature), ('%.02f'%ov))[0]
                    
            # get measured time resolution
            s_data = g_data[ds.moduleLabel][bar].Eval(ovEff)
            indref = [i for i in range(0, g_data[ds.moduleLabel][bar].GetN()) if g_data[ds.moduleLabel][bar].GetPointX(i) == ovEff]
            if ( len(indref)<1 ): continue
            err_s_data = g_data[ds.moduleLabel][bar].GetErrorY(indref[0])            

            # Npe and Gain at this OVeff
            Npe[ds.moduleLabel][ov]  = 4.2*ds.LO*PDE(ds.sipmType,ovEff,ds.irradiation)/PDE(ds.sipmType,3.50,'0') #LO is referred to 3.50 V OV
            gain[ds.moduleLabel][ov] = Gain(ds.sipmType, ovEff, ds.irradiation)
        
            # get pulse shapes
            g_psL = fPS[ds.moduleLabel][ov].Get('g_pulseShapeL_bar%02d_Vov%.2f'%(bar,ov))
            g_psR = fPS[ds.moduleLabel][ov].Get('g_pulseShapeR_bar%02d_Vov%.2f'%(bar,ov))
            if (g_psL==None and g_psR==None): continue
            if (g_psL!=None): g_psL.SetName('g_pulseShapeL_bar%02d_Vov%.2f_%s'%(bar,ov,ds.moduleLabel))
            if (g_psR!=None): g_psR.SetName('g_pulseShapeR_bar%02d_Vov%.2f_%s'%(bar,ov,ds.moduleLabel))
            timingThreshold = findTimingThreshold(f[ds.moduleLabel].Get('g_deltaT_energyRatioCorr_vs_th_bar%02d_Vov%.2f_enBin01'%(bar,ov)), ovEff)
            srL = -1
            srR = -1
            sr = -1
            err_srL = -1
            err_srR = -1
            c = ROOT.TCanvas('c_%s'%(g_psL.GetName().replace('g_pulseShapeL','pulseShape').replace('Vov%.2f'%ov,'VovEff%.2f'%ovEff)),'',600,600)  
            hdummy = ROOT.TH2F('hdummy','', 100, min(g_psL.GetX())-1., 5, 100, 0., 15.)
            hdummy.GetXaxis().SetTitle('time [ns]')
            hdummy.GetYaxis().SetTitle('amplitude [#muA]')
            hdummy.Draw()
            gtempL = ROOT.TGraphErrors()
            gtempR = ROOT.TGraphErrors()
            
            if ( ov == 0.60 and 'LYSO825' in ds.moduleLabel): np = 2 # reduce npoints for SR fit
            else: np = 3
                
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

            #print sipm, ov, ovEff, gain, Npe[ds.moduleLabel][ov], srL, srR, sr, errSR
            g_SR_vs_Vov[ds.moduleLabel][bar].SetPoint( g_SR_vs_Vov[ds.moduleLabel][bar].GetN(), ovEff, sr )
            g_SR_vs_Vov[ds.moduleLabel][bar].SetPointError( g_SR_vs_Vov[ds.moduleLabel][bar].GetN()-1, 0, errSR )
            
            g_SR_vs_GainNpe[ds.moduleLabel][bar].SetPoint( g_SR_vs_GainNpe[ds.moduleLabel][bar].GetN(), gain[ds.moduleLabel][ov]*Npe[ds.moduleLabel][ov], sr )
            g_SR_vs_GainNpe[ds.moduleLabel][bar].SetPointError( g_SR_vs_GainNpe[ds.moduleLabel][bar].GetN()-1, 0, errSR )

            g_bestTh_vs_Vov[ds.moduleLabel][bar].SetPoint( g_bestTh_vs_Vov[ds.moduleLabel][bar].GetN(), ovEff, timingThreshold )
            g_bestTh_vs_Vov[ds.moduleLabel][bar].SetPointError( g_bestTh_vs_Vov[ds.moduleLabel][bar].GetN()-1, 0, 0 )
            
            g_SR_vs_bar[ds.moduleLabel][ov].SetPoint( g_SR_vs_bar[ds.moduleLabel][ov].GetN(), bar, sr )
            g_SR_vs_bar[ds.moduleLabel][ov].SetPointError( g_SR_vs_bar[ds.moduleLabel][ov].GetN()-1, 0, errSR )
            
            g_bestTh_vs_bar[ds.moduleLabel][ov].SetPoint( g_bestTh_vs_bar[ds.moduleLabel][ov].GetN(), bar, timingThreshold )
            g_bestTh_vs_bar[ds.moduleLabel][ov].SetPointError( g_bestTh_vs_bar[ds.moduleLabel][ov].GetN()-1, 0, 0)
            
            s_noise = sigma_noise(sr)
            err_s_noise =  0.5*(sigma_noise(sr*(1-errSR/sr))-sigma_noise(sr*(1+errSR/sr)))
            g_Noise_vs_bar[ds.moduleLabel][ov].SetPoint( g_Noise_vs_bar[ds.moduleLabel][ov].GetN(), bar, s_noise )
            g_Noise_vs_bar[ds.moduleLabel][ov].SetPointError( g_Noise_vs_bar[ds.moduleLabel][ov].GetN()-1, 0,  err_s_noise)
            
            g_Noise_vs_Vov[ds.moduleLabel][bar].SetPoint(g_Noise_vs_Vov[ds.moduleLabel][bar].GetN(), ovEff, s_noise)
            g_Noise_vs_Vov[ds.moduleLabel][bar].SetPointError(g_Noise_vs_Vov[ds.moduleLabel][bar].GetN()-1, 0, err_s_noise)
            
            
            # compute s_stoch by scaling the stochastic term measured for non-irradiated SiPMs for sqrt(PDE) 
            alpha = 0.50 
            s_stoch = ds.stoch_ref/pow( PDE(ds.sipmType,ovEff,ds.irradiation)/PDE(ds.sipmType,ds.ov_ref,'0'), alpha )
            # assume 5% uncertainty on PDE...
            s_stoch_up = ds.stoch_ref/pow( PDE(ds.sipmType,ovEff,ds.irradiation)*(1-errPDE)/PDE(ds.sipmType,ds.ov_ref,'0'), alpha  )
            s_stoch_down = ds.stoch_ref/pow( PDE(ds.sipmType,ovEff,ds.irradiation)*(1+errPDE)/PDE(ds.sipmType,ds.ov_ref,'0'), alpha  )
            err_s_stoch = 0.5*(s_stoch_up-s_stoch_down)
            g_Stoch_vs_Vov[ds.moduleLabel][bar].SetPoint(g_Stoch_vs_Vov[ds.moduleLabel][bar].GetN(), ovEff, s_stoch)
            g_Stoch_vs_Vov[ds.moduleLabel][bar].SetPointError(g_Stoch_vs_Vov[ds.moduleLabel][bar].GetN()-1, 0, err_s_stoch)
            g_Stoch_vs_bar[ds.moduleLabel][ov].SetPoint( g_Stoch_vs_bar[ds.moduleLabel][ov].GetN(), bar, s_stoch )
            g_Stoch_vs_bar[ds.moduleLabel][ov].SetPointError( g_Stoch_vs_bar[ds.moduleLabel][ov].GetN()-1, 0,  err_s_stoch)

            # compute sigma_DCR as difference in quadrature between measured tRes and noise, stoch
            if ( s_data*s_data - s_stoch*s_stoch - s_noise*s_noise > 0):
                s_dcr = math.sqrt( s_data*s_data - s_stoch*s_stoch - s_noise*s_noise )
                err_s_dcr = 1./s_dcr * math.sqrt( pow( err_s_data*s_data,2) + pow( err_s_stoch*s_stoch,2) + pow(err_s_noise*s_noise,2))
                g_DCR_vs_Vov[ds.moduleLabel][bar].SetPoint(g_DCR_vs_Vov[ds.moduleLabel][bar].GetN(), ovEff, s_dcr)
                g_DCR_vs_Vov[ds.moduleLabel][bar].SetPointError(g_DCR_vs_Vov[ds.moduleLabel][bar].GetN()-1, 0, err_s_dcr)
                g_DCR_vs_bar[ds.moduleLabel][ov].SetPoint( g_DCR_vs_bar[ds.moduleLabel][ov].GetN(), bar, s_dcr )
                g_DCR_vs_bar[ds.moduleLabel][ov].SetPointError( g_DCR_vs_bar[ds.moduleLabel][ov].GetN()-1, 0,  err_s_dcr)
                
                dcr = getVovEffDCR(data, ds.lyso, (ds.sipm+'_T%dC'%ds.temperature),('%.02f'%ov))[1]
                g_DCR_vs_Npe[ds.moduleLabel][bar].SetPoint( g_DCR_vs_Npe[ds.moduleLabel][bar].GetN(), math.sqrt(dcr)/Npe[ds.moduleLabel][ov]/(math.sqrt(30.)/3000.), s_dcr )
                g_DCR_vs_Npe[ds.moduleLabel][bar].SetPointError( g_DCR_vs_Npe[ds.moduleLabel][bar].GetN()-1, 0,  err_s_dcr)

                # total time resolution
                s_tot = math.sqrt( s_stoch*s_stoch + s_noise*s_noise + s_dcr*s_dcr )
                err_s_tot = 1./s_tot * math.sqrt( pow( err_s_stoch*s_stoch,2) + pow(s_noise*err_s_noise,2) + pow(s_dcr*err_s_dcr,2))

                g_Tot_vs_Vov[ds.moduleLabel][bar].SetPoint(g_Tot_vs_Vov[ds.moduleLabel][bar].GetN(), ovEff, s_tot)
                g_Tot_vs_Vov[ds.moduleLabel][bar].SetPointError(g_Tot_vs_Vov[ds.moduleLabel][bar].GetN()-1, 0, err_s_tot)

            

# average plots
g_SR_vs_Vov_average = {}
g_Noise_vs_Vov_average = {}
g_Stoch_vs_Vov_average = {}
g_DCR_vs_Vov_average = {}
g_Tot_vs_Vov_average = {}

g_DCR_vs_DCRNpe_average = {}
g_DCR_vs_DCRNpe_average_all = ROOT.TGraphErrors()

g_DCRNpe_vs_DCR_average = {}
g_DCRNpe_vs_DCR_average_all = ROOT.TGraphErrors()


for ds in data_structs:
    g_SR_vs_Vov_average[ds.moduleLabel] = ROOT.TGraphErrors()
    g_DCR_vs_DCRNpe_average[ds.moduleLabel] = ROOT.TGraphErrors()
    g_DCRNpe_vs_DCR_average[ds.moduleLabel] = ROOT.TGraphErrors()
    
    # average tRes, split contributions
    g_Noise_vs_Vov_average[ds.moduleLabel] = ROOT.TGraphErrors()
    g_Stoch_vs_Vov_average[ds.moduleLabel] = ROOT.TGraphErrors()
    g_DCR_vs_Vov_average[ds.moduleLabel] = ROOT.TGraphErrors()
    g_Tot_vs_Vov_average[ds.moduleLabel] = ROOT.TGraphErrors()

    for ov in Vovs[ds.moduleLabel]:
        ovEff = getVovEffDCR(data, ds.lyso, (ds.sipm+'_T%dC'%ds.temperature), ('%.02f'%ov))[0] 
        dcr   = getVovEffDCR(data, ds.lyso, (ds.sipm+'_T%dC'%ds.temperature), ('%.02f'%ov))[1] 
        staticCurrent = dcr*1E09 * Gain(ds.sipmType, ovEff, ds.irradiation) * 1.602E-19; 
        staticPower = staticCurrent * (37. + ovEff) * 1000.; #in mW

        if (ov in  g_SR_vs_bar[ds.moduleLabel].keys()): 

            # average SR
            fitpol0_sr = ROOT.TF1('fitpol0_sr','pol0',-100,100)
            if (g_SR_vs_bar[ds.moduleLabel][ov].GetN()==0): continue;
            g_SR_vs_bar[ds.moduleLabel][ov].Fit(fitpol0_sr,'QNR')
            sr = fitpol0_sr.GetParameter(0)
            g_SR_vs_Vov_average[ds.moduleLabel].SetPoint(g_SR_vs_Vov_average[ds.moduleLabel].GetN(), ovEff, sr)
            g_SR_vs_Vov_average[ds.moduleLabel].SetPointError(g_SR_vs_Vov_average[ds.moduleLabel].GetN()-1, 0, fitpol0_sr.GetParError(0))

            # noise using average SR
            g_Noise_vs_Vov_average[ds.moduleLabel].SetPoint(g_Noise_vs_Vov_average[ds.moduleLabel].GetN(), ovEff, sigma_noise(sr))
            sr_err = max(fitpol0_sr.GetParError(0), errSRsyst*sr)
            sr_up   = sr + sr_err 
            sr_down = sr - sr_err 
            noise_err  = 0.5 * ( sigma_noise(sr_down) - sigma_noise(sr_up) ) 
            g_Noise_vs_Vov_average[ds.moduleLabel].SetPointError(g_Noise_vs_Vov_average[ds.moduleLabel].GetN()-1, 0, noise_err) 
    
            # average stochastic 
            fitpol0_stoch = ROOT.TF1('fitpol0_stoch','pol0',-100,100)  
            g_Stoch_vs_bar[ds.moduleLabel][ov].Fit(fitpol0_stoch,'QNR')
            s_stoch = fitpol0_stoch.GetParameter(0)
            err_s_stoch = g_Stoch_vs_bar[ds.moduleLabel][ov].GetErrorY(0) # fixme!
            g_Stoch_vs_Vov_average[ds.moduleLabel].SetPoint(g_Stoch_vs_Vov_average[ds.moduleLabel].GetN(), ovEff, s_stoch)
            g_Stoch_vs_Vov_average[ds.moduleLabel].SetPointError(g_Stoch_vs_Vov_average[ds.moduleLabel].GetN()-1, 0, err_s_stoch)

            # average dcr
            fitpol0_dcr = ROOT.TF1('fitpol0_dcr','pol0',-100,100)  
            g_DCR_vs_bar[ds.moduleLabel][ov].Fit(fitpol0_dcr,'QNR')
            s_dcr =  fitpol0_dcr.GetParameter(0)
            #err_s_dcr = fitpol0_dcr.GetParError(0)
            err_s_dcr = fitpol0_dcr.GetParError(0)
            g_DCR_vs_Vov_average[ds.moduleLabel].SetPoint(g_DCR_vs_Vov_average[ds.moduleLabel].GetN(), ovEff, s_dcr)
            g_DCR_vs_Vov_average[ds.moduleLabel].SetPointError(g_DCR_vs_Vov_average[ds.moduleLabel].GetN()-1, 0, err_s_dcr)

            # tot resolution summing noise + stochastic + dcr in quadrature
            tot = math.sqrt( s_stoch*s_stoch + sigma_noise(sr)*sigma_noise(sr) + s_dcr*s_dcr )
            err_tot = 1./tot * math.sqrt( pow( err_s_stoch*s_stoch,2) + pow(noise_err*sigma_noise(sr),2) + pow(s_dcr*err_s_dcr, 2) )
            g_Tot_vs_Vov_average[ds.moduleLabel].SetPoint(g_Tot_vs_Vov_average[ds.moduleLabel].GetN(), ovEff, tot)
            g_Tot_vs_Vov_average[ds.moduleLabel].SetPointError(g_Tot_vs_Vov_average[ds.moduleLabel].GetN()-1, 0, err_tot)

            
            # average tRes vs Npe, DCR, static power, GainNpe            
            fitpol0 = ROOT.TF1('fitpol0','pol0',-100,100)
            gg = f[ds.moduleLabel].Get('g_deltaT_totRatioCorr_bestTh_vs_bar_Vov%.02f_enBin01'%ov)    
            gg.Fit(fitpol0,'QNR')
            g_data_vs_Npe[ds.moduleLabel].SetPoint(g_data_vs_Npe[ds.moduleLabel].GetN(), Npe[ds.moduleLabel][ov], fitpol0.GetParameter(0))
            g_data_vs_Npe[ds.moduleLabel].SetPointError(g_data_vs_Npe[ds.moduleLabel].GetN()-1, 0, fitpol0.GetParError(0))

            g_data_vs_DCR[ds.moduleLabel].SetPoint(g_data_vs_DCR[ds.moduleLabel].GetN(), dcr, fitpol0.GetParameter(0))
            g_data_vs_DCR[ds.moduleLabel].SetPointError(g_data_vs_DCR[ds.moduleLabel].GetN()-1, 0,  fitpol0.GetParError(0))

            g_data_vs_staticPower[ds.moduleLabel].SetPoint(g_data_vs_staticPower[ds.moduleLabel].GetN(), staticPower, fitpol0.GetParameter(0))
            g_data_vs_staticPower[ds.moduleLabel].SetPointError(g_data_vs_staticPower[ds.moduleLabel].GetN()-1, 0,  fitpol0.GetParError(0))

            g_data_vs_GainNpe[ds.moduleLabel].SetPoint(g_data_vs_GainNpe[ds.moduleLabel].GetN(), gain[ds.moduleLabel][ov]*Npe[ds.moduleLabel][ov], fitpol0.GetParameter(0))
            g_data_vs_GainNpe[ds.moduleLabel].SetPointError(g_data_vs_GainNpe[ds.moduleLabel].GetN()-1, 0, fitpol0.GetParError(0))


            x = math.sqrt(dcr)/Npe[ds.moduleLabel][ov]/ (math.sqrt(30.)/3000)
            x_down = math.sqrt(dcr)/(Npe[ds.moduleLabel][ov]*(1+errPDE) )/ (math.sqrt(30.)/3000)
            x_up   = math.sqrt(dcr)/(Npe[ds.moduleLabel][ov]*(1-errPDE))/ (math.sqrt(30.)/3000)
            if (g_DCR_vs_bar[ds.moduleLabel][ov].GetN()==0):continue

            g_DCR_vs_DCRNpe_average[ds.moduleLabel].SetPoint( g_DCR_vs_DCRNpe_average[ds.moduleLabel].GetN(), x,  s_dcr)
            g_DCR_vs_DCRNpe_average[ds.moduleLabel].SetPointError( g_DCR_vs_DCRNpe_average[ds.moduleLabel].GetN()-1, 0.5*(x_up-x_down), g_DCR_vs_bar[ds.moduleLabel][ov].GetRMS(2))
            g_DCR_vs_DCRNpe_average_all.SetPoint( g_DCR_vs_DCRNpe_average_all.GetN(), x,  s_dcr)
            g_DCR_vs_DCRNpe_average_all.SetPointError( g_DCR_vs_DCRNpe_average_all.GetN()-1, 0.5*(x_up-x_down),  g_DCR_vs_bar[ds.moduleLabel][ov].GetRMS(2))
            
            y = s_dcr * Npe[ds.moduleLabel][ov]/6000 
            #err_y = err_s_dcr * Npe[ds.moduleLabel][ov]/6000  # fixme: need to account also for error on Npe
            err_y = g_DCR_vs_bar[ds.moduleLabel][ov].GetRMS(2) * Npe[ds.moduleLabel][ov]/6000
            g_DCRNpe_vs_DCR_average[ds.moduleLabel].SetPoint( g_DCRNpe_vs_DCR_average[ds.moduleLabel].GetN(), dcr, y )
            g_DCRNpe_vs_DCR_average[ds.moduleLabel].SetPointError( g_DCRNpe_vs_DCR_average[ds.moduleLabel].GetN()-1, 0., err_y)
            g_DCRNpe_vs_DCR_average_all.SetPoint( g_DCRNpe_vs_DCR_average_all.GetN(), dcr, y)
            g_DCRNpe_vs_DCR_average_all.SetPointError( g_DCRNpe_vs_DCR_average_all.GetN()-1, 0, err_y)





# Andrea's model
fitFun_tRes_dcr_model = ROOT.TF1('fitFun_tRes_dcr_model','[1] * 2 * pow(x,[0]/0.5)', 0,10)  # factor 2 as Andrea normalize to 6000 pe # questa e' sbagliata! 
fitFun_tRes_dcr_model.SetParameter(0,0.4)
fitFun_tRes_dcr_model.SetParameter(1,40)
fitFun_tRes_dcr_model.SetLineColor(1)
g_DCR_vs_DCRNpe_average_all.Fit(fitFun_tRes_dcr_model)



# draw
leg = {}

# Tres vs OV
print('Plotting time resolution vs OV...')
for ds in data_structs:
    leg[ds.moduleLabel] = ROOT.TLegend(0.65,0.60,0.89,0.79)
    leg[ds.moduleLabel].SetBorderSize(0)
    leg[ds.moduleLabel].SetFillStyle(0)
    for i,bar in enumerate(bars[ds.moduleLabel]):
        if (bar not in g_data[ds.moduleLabel].keys()): continue
        if (g_data[ds.moduleLabel][bar].GetN()==0): continue
        c =  ROOT.TCanvas('c_timeResolution_vs_Vov_%s_bar%02d'%(ds.moduleLabel,bar),'c_timeResolution_vs_Vov_%s_bar%02d'%(ds.moduleLabel,bar),600,600)
        c.SetGridy()
        c.cd()
        xmin = 0.0
        xmax = 2.0
        hdummy = ROOT.TH2F('hdummy_%s_%d'%(ds.moduleLabel,bar),'',100,xmin,xmax,140,0,140)
        hdummy.GetXaxis().SetTitle('V_{OV}^{eff} [V]')
        hdummy.GetYaxis().SetTitle('#sigma_{t} [ps]')
        hdummy.Draw()
        g_data[ds.moduleLabel][bar].SetMarkerStyle(20)
        g_data[ds.moduleLabel][bar].SetMarkerSize(1)
        g_data[ds.moduleLabel][bar].SetMarkerColor(1)
        g_data[ds.moduleLabel][bar].SetLineColor(1)
        g_data[ds.moduleLabel][bar].SetLineWidth(2)
        g_data[ds.moduleLabel][bar].Draw('plsame')
        if (bar not in g_Noise_vs_Vov[ds.moduleLabel].keys()): continue
        g_Noise_vs_Vov[ds.moduleLabel][bar].SetLineWidth(2)
        g_Noise_vs_Vov[ds.moduleLabel][bar].SetLineColor(ROOT.kBlue)
        g_Noise_vs_Vov[ds.moduleLabel][bar].SetFillColor(ROOT.kBlue)
        g_Noise_vs_Vov[ds.moduleLabel][bar].SetFillColorAlpha(ROOT.kBlue,0.5)
        g_Noise_vs_Vov[ds.moduleLabel][bar].SetFillStyle(3004)
        g_Noise_vs_Vov[ds.moduleLabel][bar].Draw('E3lsame')
        g_Stoch_vs_Vov[ds.moduleLabel][bar].SetLineWidth(2)
        g_Stoch_vs_Vov[ds.moduleLabel][bar].SetLineColor(ROOT.kGreen+2)
        g_Stoch_vs_Vov[ds.moduleLabel][bar].SetFillColor(ROOT.kGreen+2)
        g_Stoch_vs_Vov[ds.moduleLabel][bar].SetFillStyle(3001)
        g_Stoch_vs_Vov[ds.moduleLabel][bar].SetFillColorAlpha(ROOT.kGreen+2,0.5)
        g_Stoch_vs_Vov[ds.moduleLabel][bar].Draw('E3lsame')
        g_DCR_vs_Vov[ds.moduleLabel][bar].SetLineWidth(2)
        g_DCR_vs_Vov[ds.moduleLabel][bar].SetLineColor(ROOT.kOrange+2)
        g_DCR_vs_Vov[ds.moduleLabel][bar].SetFillColor(ROOT.kOrange+2)
        g_DCR_vs_Vov[ds.moduleLabel][bar].SetFillColorAlpha(ROOT.kOrange+2,0.5)
        g_DCR_vs_Vov[ds.moduleLabel][bar].SetFillStyle(3001)
        g_DCR_vs_Vov[ds.moduleLabel][bar].Draw('E3lsame')
        g_Tot_vs_Vov[ds.moduleLabel][bar].SetLineWidth(2)
        g_Tot_vs_Vov[ds.moduleLabel][bar].SetLineColor(ROOT.kRed+1)
        g_Tot_vs_Vov[ds.moduleLabel][bar].SetFillColor(ROOT.kRed+1)
        g_Tot_vs_Vov[ds.moduleLabel][bar].SetFillColorAlpha(ROOT.kRed+1,0.5)
        g_Tot_vs_Vov[ds.moduleLabel][bar].SetFillStyle(3001)
        #g_Tot_vs_Vov[ds.moduleLabel][bar].Draw('E3lsame')
        #save on file
        outfile.cd()
        g_data[ds.moduleLabel][bar].Write('g_Data_vs_Vov_%s_bar%02d'%(ds.moduleLabel,  bar))
        g_Noise_vs_Vov[ds.moduleLabel][bar].Write('g_Noise_vs_Vov_%s_bar%02d'%(ds.moduleLabel, bar))
        g_Stoch_vs_Vov[ds.moduleLabel][bar].Write('g_Stoch_vs_Vov_%s_bar%02d'%(ds.moduleLabel, bar))
        g_DCR_vs_Vov[ds.moduleLabel][bar].Write('g_DCR_vs_Vov_%s_bar%02d'%(ds.moduleLabel, bar))
        if (i==0):
            leg[ds.moduleLabel].AddEntry(g_data[ds.moduleLabel][bar], 'data', 'PL')
            leg[ds.moduleLabel].AddEntry(g_Noise_vs_Vov[ds.moduleLabel][bar], 'noise', 'L')
            leg[ds.moduleLabel].AddEntry(g_Stoch_vs_Vov[ds.moduleLabel][bar], 'stoch', 'L')
            leg[ds.moduleLabel].AddEntry(g_DCR_vs_Vov[ds.moduleLabel][bar], 'DCR', 'L')
        leg[ds.moduleLabel].Draw('same')
        latex = ROOT.TLatex(0.20,0.85,'%s'%(ds.moduleLabel.replace('_',' ').replace('T','T=')))
        latex.SetNDC()
        latex.SetTextSize(0.045)
        latex.SetTextFont(42)
        latex.Draw('same')
        #c1[ds.moduleLabel][bar].SaveAs(outdir+'/'+c1[ds.moduleLabel][bar].GetName()+'.png')
        #c1[ds.moduleLabel][bar].SaveAs(outdir+'/'+c1[ds.moduleLabel][bar].GetName()+'.pdf')
        c.SaveAs(outdir+'/'+c.GetName()+'.png')
        c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
        hdummy.Delete()


# vs npe
print('Plotting tRes_DCR vs Npe...')
for bar in range(0,16):      
    c =  ROOT.TCanvas('c_timeResolutionDCR_vs_DCRNpe_bar%02d'%(bar),'c_timeResolutionDCR_vs_DCRNpe_bar%02d'%(bar),600,600)
    c.SetGridx()
    c.SetGridy()
    c.cd()
    xmax = 2
    ymax = 100
    hdummy = ROOT.TH2F('hdummy_%d'%(bar),'',100,0,xmax,100,0,ymax)
    hdummy.GetXaxis().SetTitle('#sqrt{DCR/30GHz}/(Npe/3000)')
    hdummy.GetYaxis().SetTitle('#sigma_{t}^{DCR} [ps]')
    hdummy.Draw()
    for ds in data_structs:
        if (bar not in g_DCR_vs_Npe[ds.moduleLabel].keys()): continue
        g_DCR_vs_Npe[ds.moduleLabel][bar].SetMarkerStyle(ds.marker)
        g_DCR_vs_Npe[ds.moduleLabel][bar].SetMarkerColor(ds.color)
        g_DCR_vs_Npe[ds.moduleLabel][bar].SetLineWidth(1)
        g_DCR_vs_Npe[ds.moduleLabel][bar].SetLineColor(ds.color)
        g_DCR_vs_Npe[ds.moduleLabel][bar].Draw('psame')
    c.SaveAs(outdir+'/'+c.GetName()+'.png')
    c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
    hdummy.Delete()
    #c.Delete()


c =  ROOT.TCanvas('c_timeResolutionDCR_vs_DCRNpe_average','c_timeResolutionDCR_vs_DCRNpe_average',600,600)
c.SetGridx()
c.SetGridy()
c.cd()    
hdummy = ROOT.TH2F('hdummy_%d'%(bar),'',100,0,2.0,100,0,100)
hdummy.GetXaxis().SetTitle('#sqrt{DCR/30GHz}/(Npe/3000)')
hdummy.GetYaxis().SetTitle('#sigma_{t}^{DCR} [ps]')
hdummy.Draw()
g_DCR_vs_DCRNpe_average_all.SetMarkerSize(0.1)
g_DCR_vs_DCRNpe_average_all.Draw('p*same')
fitFun_tRes_dcr_model.Draw('same')
outfile.cd() 
g_DCR_vs_DCRNpe_average_all.Write('g_DCR_vs_DCRNpe_average_all')
for ds in data_structs:
    g_DCR_vs_DCRNpe_average[ds.moduleLabel].SetMarkerStyle(ds.marker)
    g_DCR_vs_DCRNpe_average[ds.moduleLabel].SetMarkerColor(ds.color)
    g_DCR_vs_DCRNpe_average[ds.moduleLabel].SetLineWidth(1)
    g_DCR_vs_DCRNpe_average[ds.moduleLabel].SetLineColor(ds.color)
    g_DCR_vs_DCRNpe_average[ds.moduleLabel].Draw('psame')
    outfile.cd() 
    g_DCR_vs_DCRNpe_average[ds.moduleLabel].Write('g_DCR_vs_DCRNpe_average_%s'%ds.moduleLabel)
c.SaveAs(outdir+'/'+c.GetName()+'.png')
c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
hdummy.Delete()
#c.Delete()


c =  ROOT.TCanvas('c_timeResolutionDCRNpe_vs_DCR_average','c_timeResolutionDCRNpe_vs_DCR_average',600,600)
c.SetGridx()
c.SetGridy()
c.cd()    
hdummy = ROOT.TH2F('hdummy_%d'%(bar),'',100,0,50,100,0,100)
hdummy.GetXaxis().SetTitle('DCR[GHz]')
hdummy.GetYaxis().SetTitle('(Npe/6000) #times #sigma_{t}^{DCR} [ps]')
hdummy.Draw()
fitFun_tRes_dcr = ROOT.TF1('fitFun_tRes_dcr','[1] * pow(x/30.,[0])', 0,10)  
fitFun_tRes_dcr.SetParameter(0,0.5)
fitFun_tRes_dcr.SetParameter(1,40)
fitFun_tRes_dcr.SetLineColor(1)
g_DCRNpe_vs_DCR_average_all.Fit(fitFun_tRes_dcr)
g_DCRNpe_vs_DCR_average_all.SetMarkerSize(0.1)
g_DCRNpe_vs_DCR_average_all.Draw('p*same')
fitFun_tRes_dcr.Draw('same')
outfile.cd() 
g_DCRNpe_vs_DCR_average_all.Write('g_DCRNpe_vs_DCR_average_all')
for ds in data_structs:
    g_DCRNpe_vs_DCR_average[ds.moduleLabel].SetMarkerStyle(ds.marker)
    g_DCRNpe_vs_DCR_average[ds.moduleLabel].SetMarkerColor(ds.color)
    g_DCRNpe_vs_DCR_average[ds.moduleLabel].SetLineWidth(1)
    g_DCRNpe_vs_DCR_average[ds.moduleLabel].SetLineColor(ds.color)
    g_DCRNpe_vs_DCR_average[ds.moduleLabel].Draw('psame')
    outfile.cd() 
    g_DCRNpe_vs_DCR_average[ds.moduleLabel].Write('g_DCRNpe_vs_DCR_average_%s'%ds.moduleLabel)
c.SaveAs(outdir+'/'+c.GetName()+'.png')
c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
hdummy.Delete()


# SR and best threshold vs Vov
leg2 = ROOT.TLegend(0.20,0.70,0.45,0.89)
leg2.SetBorderSize(0)
leg2.SetFillStyle(0)
i = 0
for bar in range(0,16):
    if (bar not in g_data[ds.moduleLabel].keys()): continue
    if (g_data[ds.moduleLabel][bar].GetN()==0): continue     
    c = ROOT.TCanvas('c_slewRate_vs_Vov_bar%02d'%(bar),'c_slewRate_vs_Vov_bar%02d'%(bar),600,600)
    c.SetGridy()
    c.cd()
    xmin = 0.0
    xmax = 2.0
    ymax = 35
    hdummy = ROOT.TH2F('hdummy_%d'%(bar),'',100,xmin,xmax,100,0,ymax)
    hdummy.GetXaxis().SetTitle('V_{OV}^{eff} [V]')
    hdummy.GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
    hdummy.Draw()
    for ds in data_structs:
        if (bar not in g_SR_vs_Vov[ds.moduleLabel].keys()): continue
        if (i==0):
            leg2.AddEntry(g_SR_vs_Vov[ds.moduleLabel][bar], '%s'%ds.moduleLabel.replace('_',' ').replace('T','T='), 'PL')
        g_SR_vs_Vov[ds.moduleLabel][bar].SetMarkerStyle(ds.marker)
        g_SR_vs_Vov[ds.moduleLabel][bar].SetMarkerColor(ds.color)
        g_SR_vs_Vov[ds.moduleLabel][bar].SetLineColor(ds.color)
        g_SR_vs_Vov[ds.moduleLabel][bar].Draw('plsame')
    leg2.Draw()
    outfile.cd()
    g_SR_vs_Vov[ds.moduleLabel][bar].Write('g_SR_vs_Vov_%s_bar%02d'%(ds.moduleLabel,bar))
    c.SaveAs(outdir+'/'+c.GetName()+'.png')
    c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
    hdummy.Delete()
    i=i+1

    c = ROOT.TCanvas('c_slewRate_vs_GainNpe_bar%02d'%(bar),'c_slewRate_vs_GainNpe_bar%02d'%(bar),600,600)
    c.SetGridy()
    c.cd()
    hdummy = ROOT.TH2F('hdummy_%d'%(bar),'',100,0,3E09,100,0,35)
    hdummy.GetXaxis().SetTitle('gain x Npe')
    hdummy.GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
    hdummy.Draw()
    for ds in data_structs:
        if (bar not in g_SR_vs_GainNpe[ds.moduleLabel].keys()): continue
        g_SR_vs_GainNpe[ds.moduleLabel][bar].SetMarkerStyle( ds.marker )
        g_SR_vs_GainNpe[ds.moduleLabel][bar].SetMarkerColor(ds.color)
        g_SR_vs_GainNpe[ds.moduleLabel][bar].SetLineColor(ds.color)
        g_SR_vs_GainNpe[ds.moduleLabel][bar].Draw('psame')
    leg2.Draw()
    c.SaveAs(outdir+'/'+c.GetName()+'.png')
    c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
    hdummy.Delete()

    c = ROOT.TCanvas('c_bestTh_vs_Vov_bar%02d'%(bar),'c_bestTh_vs_Vov_bar%02d'%(bar),600,600)
    c.SetGridy()
    c.cd()
    hdummy = ROOT.TH2F('hdummy_%d'%(bar),'',100,xmin,xmax,100,0,20)
    hdummy.GetXaxis().SetTitle('V_{OV}^{eff} [V]')
    hdummy.GetYaxis().SetTitle('best threshold [DAC]')
    hdummy.Draw()
    for ds in data_structs:
        if (bar not in g_bestTh_vs_Vov[ds.moduleLabel].keys()): continue
        g_bestTh_vs_Vov[ds.moduleLabel][bar].SetMarkerStyle(ds.marker)
        g_bestTh_vs_Vov[ds.moduleLabel][bar].SetMarkerColor(ds.color)
        g_bestTh_vs_Vov[ds.moduleLabel][bar].SetLineColor(ds.color)
        g_bestTh_vs_Vov[ds.moduleLabel][bar].Draw('plsame')
    c.SaveAs(outdir+'/'+c.GetName()+'.png')
    c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
    hdummy.Delete()

# average slew rate vs OV
c =  ROOT.TCanvas('c_slewRate_vs_Vov_average','c_slewRate_vs_Vov_average',600,600)
c.SetGridx()
c.SetGridy()
c.cd()    
hdummy = ROOT.TH2F('hdummy','',16, 0.0, 2.0 ,100, 0,35)
hdummy.GetXaxis().SetTitle('V_{OV}^{eff} [V]')
hdummy.GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
hdummy.Draw()
for ds in data_structs:
    g_SR_vs_Vov_average[ds.moduleLabel].SetMarkerStyle(ds.marker)
    g_SR_vs_Vov_average[ds.moduleLabel].SetMarkerColor(ds.color)
    g_SR_vs_Vov_average[ds.moduleLabel].SetLineWidth(1)
    g_SR_vs_Vov_average[ds.moduleLabel].SetLineColor(ds.color)
    g_SR_vs_Vov_average[ds.moduleLabel].Draw('plsame')
    outfile.cd()
    g_SR_vs_Vov_average[ds.moduleLabel].Write('g_SR_vs_Vov_average_%s'%(ds.moduleLabel))
leg2.Draw()
c.SaveAs(outdir+'/'+c.GetName()+'.png')
c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
hdummy.Delete()

# average time resolution vs Npe
c =  ROOT.TCanvas('c_timeResolution_vs_Npe_average','c_timeResolution_vs_Npe_average',600,600)
c.SetGridx()
c.SetGridy()
c.cd()    
hdummy = ROOT.TH2F('hdummy','',1000, 1000, 6000, 100, 20, 140)
hdummy.GetXaxis().SetTitle('Npe')
hdummy.GetYaxis().SetTitle('#sigma_{t} [ps]')
hdummy.GetXaxis().SetNdivisions(505)
hdummy.Draw()
for ds in data_structs:
    g_data_vs_Npe[ds.moduleLabel].SetMarkerStyle(ds.marker)
    g_data_vs_Npe[ds.moduleLabel].SetMarkerColor(ds.color)
    g_data_vs_Npe[ds.moduleLabel].SetLineWidth(1)
    g_data_vs_Npe[ds.moduleLabel].SetLineColor(ds.color)
    g_data_vs_Npe[ds.moduleLabel].Draw('plsame')
    outfile.cd()
    g_data_vs_Npe[ds.moduleLabel].Write('g_data_vs_Npe_average_%s'%(ds.moduleLabel))
leg2.Draw()  
c.SaveAs(outdir+'/'+c.GetName()+'.png')
c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
hdummy.Delete()


# average time resolution vs DCR
c =  ROOT.TCanvas('c_timeResolution_vs_DCR_average','c_timeResolution_vs_DCR_average',600,600)
c.SetGridx()
c.SetGridy()
c.cd()    
hdummy = ROOT.TH2F('hdummy','',1000, 0, 100, 20, 0, 140)
hdummy.GetXaxis().SetTitle('DCR [GHz]')
hdummy.GetYaxis().SetTitle('#sigma_{t} [ps]')
hdummy.Draw()
for ds in data_structs:
    g_data_vs_DCR[ds.moduleLabel].SetMarkerStyle(ds.marker)
    g_data_vs_DCR[ds.moduleLabel].SetMarkerColor(ds.color)
    g_data_vs_DCR[ds.moduleLabel].SetLineWidth(1)
    g_data_vs_DCR[ds.moduleLabel].SetLineColor(ds.color)
    g_data_vs_DCR[ds.moduleLabel].Draw('plsame')
    outfile.cd()
    g_data_vs_DCR[ds.moduleLabel].Write('g_data_vs_DCR_average_%s'%(ds.moduleLabel))
leg2.Draw()  
c.SaveAs(outdir+'/'+c.GetName()+'.png')
c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
hdummy.Delete()


# average time resolution vs static power
c =  ROOT.TCanvas('c_timeResolution_vs_staticPower_average','c_timeResolution_vs_staticPower_average',600,600)
c.SetGridx()
c.SetGridy()
c.cd()    
hdummy = ROOT.TH2F('hdummy','',1000, 0, 100, 100, 20, 140)
hdummy.GetXaxis().SetTitle('static power [mW]')
hdummy.GetYaxis().SetTitle('#sigma_{t} [ps]')
hdummy.Draw()
for ds in data_structs:
    g_data_vs_staticPower[ds.moduleLabel].SetMarkerStyle(ds.marker)
    g_data_vs_staticPower[ds.moduleLabel].SetMarkerColor(ds.color)
    g_data_vs_staticPower[ds.moduleLabel].SetLineWidth(1)
    g_data_vs_staticPower[ds.moduleLabel].SetLineColor(ds.color)
    g_data_vs_staticPower[ds.moduleLabel].Draw('plsame')
    outfile.cd()
    g_data_vs_staticPower[ds.moduleLabel].Write('g_data_vs_staticPower_average_%s'%(ds.moduleLabel))
leg2.Draw()  
c.SaveAs(outdir+'/'+c.GetName()+'.png')
c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
hdummy.Delete()

# average time resolution vs GainxNpe
c =  ROOT.TCanvas('c_timeResolution_vs_GainNpe_average','c_timeResolution_vs_GainNpe_average',600,600)
c.SetGridx()
c.SetGridy()
c.cd()    
hdummy = ROOT.TH2F('hdummy','',1000, 0, 3E09, 100, 20, 140)
hdummy.GetXaxis().SetTitle('Gain x Npe')
hdummy.GetYaxis().SetTitle('#sigma_{t} [ps]')
hdummy.GetXaxis().SetNdivisions(505)
hdummy.Draw()
for ds in data_structs:
    g_data_vs_GainNpe[ds.moduleLabel].SetMarkerStyle(ds.marker)
    g_data_vs_GainNpe[ds.moduleLabel].SetMarkerColor(ds.color)
    g_data_vs_GainNpe[ds.moduleLabel].SetLineWidth(1)
    g_data_vs_GainNpe[ds.moduleLabel].SetLineColor(ds.color)
    g_data_vs_GainNpe[ds.moduleLabel].Draw('plsame')
leg2.Draw()  
c.SaveAs(outdir+'/'+c.GetName()+'.png')
c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
hdummy.Delete()
                                       

# average tRes
for ds in data_structs:
    latex = ROOT.TLatex(0.18,0.94,'%s'%(ds.label))
    latex.SetNDC()
    latex.SetTextSize(0.05)
    latex.SetTextFont(42)
    c =  ROOT.TCanvas('c_timeResolution_vs_Vov_average_%s'%(ds.moduleLabel),'c_timeResolution_vs_Vov_average_%s'%(ds.moduleLabel),600,600)
    c.SetGridx()
    c.SetGridy()
    c.cd()
    hdummy = ROOT.TH2F('hdummy','',100, 0., 2.,100,0,120)
    hdummy.GetXaxis().SetTitle('V_{OV}^{eff} [V]')
    hdummy.GetYaxis().SetTitle('time resolution [ps]')
    hdummy.Draw()
    g_data_average[ds.moduleLabel].SetMarkerStyle(20)
    g_data_average[ds.moduleLabel].SetMarkerSize(1)
    g_data_average[ds.moduleLabel].SetMarkerColor(1)
    g_data_average[ds.moduleLabel].SetLineColor(1)
    g_data_average[ds.moduleLabel].SetLineWidth(2)
    g_data_average[ds.moduleLabel].Draw('plsame')
    g_Noise_vs_Vov_average[ds.moduleLabel].SetLineWidth(2)
    g_Noise_vs_Vov_average[ds.moduleLabel].SetLineColor(ROOT.kBlue)
    g_Noise_vs_Vov_average[ds.moduleLabel].SetFillColor(ROOT.kBlue)
    g_Noise_vs_Vov_average[ds.moduleLabel].SetFillColorAlpha(ROOT.kBlue,0.5)
    g_Noise_vs_Vov_average[ds.moduleLabel].SetFillStyle(3004)
    g_Noise_vs_Vov_average[ds.moduleLabel].Draw('E3lsame')
    g_Stoch_vs_Vov_average[ds.moduleLabel].SetLineWidth(2)
    g_Stoch_vs_Vov_average[ds.moduleLabel].SetLineColor(ROOT.kGreen+2)
    g_Stoch_vs_Vov_average[ds.moduleLabel].SetFillColor(ROOT.kGreen+2)
    g_Stoch_vs_Vov_average[ds.moduleLabel].SetFillStyle(3001)
    g_Stoch_vs_Vov_average[ds.moduleLabel].SetFillColorAlpha(ROOT.kGreen+2,0.5)
    g_Stoch_vs_Vov_average[ds.moduleLabel].Draw('E3lsame')
    g_DCR_vs_Vov_average[ds.moduleLabel].SetLineWidth(2)
    g_DCR_vs_Vov_average[ds.moduleLabel].SetLineColor(ROOT.kOrange+2)
    g_DCR_vs_Vov_average[ds.moduleLabel].SetFillColor(ROOT.kOrange+2)
    g_DCR_vs_Vov_average[ds.moduleLabel].SetFillStyle(3001)
    g_DCR_vs_Vov_average[ds.moduleLabel].SetFillColorAlpha(ROOT.kOrange+2,0.5)
    g_DCR_vs_Vov_average[ds.moduleLabel].Draw('E3lsame')
    g_Tot_vs_Vov_average[ds.moduleLabel].SetLineWidth(2)
    g_Tot_vs_Vov_average[ds.moduleLabel].SetLineColor(ROOT.kRed+1)
    g_Tot_vs_Vov_average[ds.moduleLabel].SetFillColor(ROOT.kRed+1)
    g_Tot_vs_Vov_average[ds.moduleLabel].SetFillColorAlpha(ROOT.kRed+1,0.5)
    g_Tot_vs_Vov_average[ds.moduleLabel].SetFillStyle(3001)
    #g_Tot_vs_Vov_average[ds.moduleLabel].Draw('E3lsame')
    leg[ds.moduleLabel].Draw()
    latex.Draw()
    outfile.cd()
    g_Noise_vs_Vov_average[ds.moduleLabel].Write('g_Noise_vs_Vov_average_%s'%ds.moduleLabel)
    g_Stoch_vs_Vov_average[ds.moduleLabel].Write('g_Stoch_vs_Vov_average_%s'%ds.moduleLabel)
    g_DCR_vs_Vov_average[ds.moduleLabel].Write('g_Stoch_vs_Vov_average_%s'%ds.moduleLabel)
    g_Tot_vs_Vov_average[ds.moduleLabel].Write('g_Tot_vs_Vov_average_%s'%ds.moduleLabel)
    c.SaveAs(outdir+'/'+c.GetName()+'.png')
    c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
    hdummy.Delete()


# SR and best threshold vs bar
for ds in data_structs:
    for ov in Vovs[ds.moduleLabel]:
        if (ov not in g_SR_vs_bar[ds.moduleLabel].keys()): continue
        ovEff = getVovEffDCR(data, ds.lyso, (ds.sipm+'_T%dC'%ds.temperature), ('%.02f'%ov))[0]        
        c = ROOT.TCanvas('c_slewRate_vs_bar_%s_Vov%.2f'%(ds.moduleLabel,ovEff),'c_slewRate_vs_bar_%s_Vov%.2f'%(ds.moduleLabel,ovEff),600,600)
        c.SetGridy()
        c.cd()
        #hdummy = ROOT.TH2F('hdummy5_%d'%(ov),'',100,-0.5,15.5,100,0,15)
        hdummy = ROOT.TH2F('hdummy_%s_%.2f'%(ds.moduleLabel,ov),'',100,-0.5,15.5,100,0,35)
        hdummy.GetXaxis().SetTitle('bar')
        hdummy.GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
        hdummy.Draw()
        g_SR_vs_bar[ds.moduleLabel][ov].SetMarkerStyle(ds.marker)
        g_SR_vs_bar[ds.moduleLabel][ov].SetMarkerColor(ds.color)
        g_SR_vs_bar[ds.moduleLabel][ov].SetLineColor(ds.color)
        g_SR_vs_bar[ds.moduleLabel][ov].Draw('psame')
        leg2.Draw()
        c.SaveAs(outdir+'/'+c.GetName()+'.png')
        c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
        hdummy.Delete()

        c = ROOT.TCanvas('c_bestTh_vs_bar_%s_Vov%.2f'%(ds.moduleLabel,ovEff),'c_bestTh_vs_bar_%s_Vov%.2f'%(ds.moduleLabel,ovEff),600,600)
        c.SetGridy()
        c.cd()
        hdummy = ROOT.TH2F('hdummy_%s_%.2f'%(ds.moduleLabel,ov),'',100,-0.5,15.5,100,0,20)
        hdummy.GetXaxis().SetTitle('bar')
        hdummy.GetYaxis().SetTitle('timing threshold [DAC]')
        hdummy.Draw()
        g_bestTh_vs_bar[ds.moduleLabel][ov].SetMarkerStyle(ds.marker)
        g_bestTh_vs_bar[ds.moduleLabel][ov].SetMarkerColor(ds.color)
        g_bestTh_vs_bar[ds.moduleLabel][ov].SetLineColor(ds.color)
        g_bestTh_vs_bar[ds.moduleLabel][ov].Draw('plsame')
        leg2.Draw()        
        c.SaveAs(outdir+'/'+c.GetName()+'.png')
        c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
        hdummy.Delete()

        c = ROOT.TCanvas('c_noise_vs_bar_%s_Vov%.2f'%(ds.moduleLabel,ovEff),'c_noise_vs_bar_%s_Vov%.2f'%(ds.moduleLabel,ovEff),600,600)
        c.SetGridy()
        c.cd()
        hdummy = ROOT.TH2F('hdummy_%s_%.2f'%(ds.moduleLabel,ov),'',100,-0.5,15.5,100,0,80)
        hdummy.GetXaxis().SetTitle('bar')
        hdummy.GetYaxis().SetTitle('#sigma_{t, noise} [ps]')
        hdummy.Draw()
        g_Noise_vs_bar[ds.moduleLabel][ov].SetMarkerStyle( ds.marker )
        g_Noise_vs_bar[ds.moduleLabel][ov].SetMarkerColor(ds.color)
        g_Noise_vs_bar[ds.moduleLabel][ov].SetLineColor(ds.color)
        g_Noise_vs_bar[ds.moduleLabel][ov].Draw('psame')
        leg2.Draw()
        c.SaveAs(outdir+'/'+c.GetName()+'.png')
        c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
        hdummy.Delete()

        c = ROOT.TCanvas('c_stoch_vs_bar_%s_Vov%.2f'%(ds.moduleLabel,ovEff),'c_stoch_vs_bar_%s_Vov%.2f'%(ds.moduleLabel,ovEff),600,600)
        c.SetGridy()
        c.cd()
        hdummy = ROOT.TH2F('hdummy_%s_%.2f'%(ds.moduleLabel,ov),'',100,-0.5,15.5,100,0,80)
        hdummy.GetXaxis().SetTitle('bar')
        hdummy.GetYaxis().SetTitle('#sigma_{t, stoch} [ps]')
        hdummy.Draw()
        g_Stoch_vs_bar[ds.moduleLabel][ov].SetMarkerStyle( ds.marker )
        g_Stoch_vs_bar[ds.moduleLabel][ov].SetMarkerColor(ds.color)
        g_Stoch_vs_bar[ds.moduleLabel][ov].SetLineColor(ds.color)
        g_Stoch_vs_bar[ds.moduleLabel][ov].Draw('psame')
        leg2.Draw()
        c.SaveAs(outdir+'/'+c.GetName()+'.png')
        c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
        hdummy.Delete()

        c = ROOT.TCanvas('c_DCR_vs_bar_%s_Vov%.2f'%(ds.moduleLabel,ovEff),'c_DCR_vs_bar_%s_Vov%.2f'%(ds.moduleLabel,ovEff),600,600)
        c.SetGridy()
        c.cd()
        hdummy = ROOT.TH2F('hdummy_%s_%.2f'%(ds.moduleLabel,ov),'',100,-0.5,15.5,100,0,140)
        hdummy.GetXaxis().SetTitle('bar')
        hdummy.GetYaxis().SetTitle('#sigma_{t, DCR} [ps]')
        hdummy.Draw()
        g_DCR_vs_bar[ds.moduleLabel][ov].SetMarkerStyle( ds.marker )
        g_DCR_vs_bar[ds.moduleLabel][ov].SetMarkerColor(ds.color)
        g_DCR_vs_bar[ds.moduleLabel][ov].SetLineColor(ds.color)
        g_DCR_vs_bar[ds.moduleLabel][ov].Draw('psame')
        leg2.Draw()
        c.SaveAs(outdir+'/'+c.GetName()+'.png')
        c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
        hdummy.Delete()

outfile.Close()

