#! /usr/bin/env python
import os
import shutil
import glob
import math
import array
import sys
import time
import argparse
import json                                                                                                                                                                      

import ROOT
import CMS_lumi, tdrstyle

#set the tdr style
tdrstyle.setTDRStyle()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(1)
ROOT.gStyle.SetOptTitle(0)
#ROOT.gStyle.SetLabelSize(0.04,'X')
#ROOT.gStyle.SetLabelSize(0.04,'Y')
#ROOT.gStyle.SetTitleSize(0.04,'X')
#ROOT.gStyle.SetTitleSize(0.04,'Y')
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
ROOT.gStyle.SetOptFit(0111)

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
        if ( ov <= 1.50 and x >= 13): continue
 
        if ( y < ymin):
            ymin = y
            xmin = x 
    return xmin
    
# =====================================


# import file with VovEff and DCR
with open('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/Currents/VovsEff.json', 'r') as f:
    data = json.load(f)       


#mysipm = 'HPK'
mysipm = 'FBK'

outdir = ''
outfile = None
sipmTypes = []

if (mysipm == 'HPK'):
    outdir    = '/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_Vov_HPK_2E14_1E14/'        
    if (os.path.exists(outdir)==False):
        os.mkdir(outdir)   
    outfile   = ROOT.TFile.Open(outdir+'/plots_timeResolution_HPK_2E14_1E14_TBJune22.root','recreate')
    sipmTypes = ['HPK_2E14_T-35C','HPK_2E14_T-40C', 'HPK_1E14_T-35C', 'HPK_1E14_T-40C']
    ov_ref    = 1.5

if (mysipm == 'FBK'):
    outdir    = '/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_Vov_FBK_2E14_1E14_TEST/'        
    if (os.path.exists(outdir)==False):
        os.mkdir(outdir)   
    outfile   = ROOT.TFile.Open(outdir+'/plots_timeResolution_FBK_2E14_1E14_TBJune22_TEST.root','recreate')
    sipmTypes = ['FBK_2E14_T-35C','FBK_2E14_T-40C','FBK_1E14_T-35C','FBK_1E14_T-40C']
    ov_ref    = 1.8

if (os.path.exists(outdir+'/plotsSR')==False):
    os.mkdir(outdir+'/plotsSR/')



# inputs
fnames = {'HPK_2E14_T-40C' : '../plots/HPK_2E14_LYSO796_T-40C_summary.root',
          'HPK_2E14_T-35C' : '../plots/HPK_2E14_LYSO796_T-35C_summary.root',
          'HPK_1E14_T-40C' : '../plots/HPK_1E14_LYSO802_T-40C_summary.root',
          'HPK_1E14_T-35C' : '../plots/HPK_1E14_LYSO802_T-35C_summary.root',
          'FBK_2E14_T-40C' : '../plots/FBK_2E14_LYSO797_T-40C_summary.root',
          'FBK_2E14_T-35C' : '../plots/FBK_2E14_LYSO797_T-35C_summary.root',
          'FBK_1E14_T-40C' : '../plots/FBK_1E14_LYSO803_T-40C_summary.root',
          'FBK_1E14_T-35C' : '../plots/FBK_1E14_LYSO803_T-35C_summary.root'}
          
LO = { 'HPK_2E14_T-40C': 1250., #? boh assumo +15% rispetto a quelli tipici...????  1100*1.15
       'HPK_2E14_T-35C': 1250., #? boh assumo +15% rispetto a quelli tipici...????  1100*1.15
       'HPK_1E14_T-40C': 1250., #? boh assumo +15% rispetto a quelli tipici...????  1100*1.15
       'HPK_1E14_T-35C': 1250., #? boh assumo +15% rispetto a quelli tipici...????  1100*1.15
       'FBK_2E14_T-40C': 1050., # uso LO misurato su FBK non irr in lab ?
       'FBK_2E14_T-35C': 1050.,
       'FBK_1E14_T-40C': 1050.,
       'FBK_1E14_T-35C': 1050.}

sigma_stoch_ref = {'HPK_2E14_T-40C' : 37., # uso valore misurato a OV = 1.50V su HPK+528 non irr?
                   'HPK_2E14_T-35C' : 37., # uso valore misurato a OV = 1.50V su HPK+528 non irr?
                   'HPK_1E14_T-40C' : 37., # uso valore misurato a OV = 1.50V su HPK+528 non irr?
                   'HPK_1E14_T-35C' : 37., # uso valore misurato a OV = 1.50V su HPK+528 non irr?
                   'FBK_2E14_T-40C' : 45., # uso valore misurato a OV = 1.80V su FBK non irr?
                   'FBK_2E14_T-35C' : 45., # uso valore misurato a OV = 1.80V su FBK non irr?
                   'FBK_1E14_T-40C' : 45., # uso valore misurato a OV = 1.80V su FBK non irr?
                   'FBK_1E14_T-35C' : 45., # uso valore misurato a OV = 1.80V su FBK non irr?
                   }


np = 3
errSRsyst  = 0.10 # error on the slew rate
errPDE     = 0.05 # assumed uncertainty on PDE (5-10%)

g = {}
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

for sipm in sipmTypes:
    f = ROOT.TFile.Open(fnames[sipm])
    print sipm, fnames[sipm]
    listOfKeys = [key.GetName().replace('g_deltaT_energyRatioCorr_bestTh_vs_vov_','') for key in ROOT.gDirectory.GetListOfKeys() if ( 'g_deltaT_energyRatioCorr_bestTh_vs_vov_bar' in key.GetName())]
    bars[sipm] = []
    for k in listOfKeys:
        bars[sipm].append( int(k[3:5]) )

    listOfKeys2 = [key.GetName().replace('g_deltaT_energyRatioCorr_bestTh_vs_bar_','') for key in ROOT.gDirectory.GetListOfKeys() if key.GetName().startswith('g_deltaT_energyRatioCorr_bestTh_vs_bar_')]
    Vovs[sipm] = []
    for k in listOfKeys2:
        Vovs[sipm].append( float(k[3:7]) )

    print bars[sipm]
    print Vovs[sipm]
    
print('continue?')
    
fPS = {}
f   = {}
for sipm in sipmTypes:
    Npe[sipm] = {}
    gain[sipm] = {}
    g[sipm] = {}
    g_Noise_vs_Vov[sipm] = {}
    g_Stoch_vs_Vov[sipm] = {}
    g_DCR_vs_Vov[sipm] = {}
    g_Tot_vs_Vov[sipm] = {}

    g_Tot_vs_SR[sipm] = {}

    g_Stoch_vs_Npe[sipm] = {}
    g_DCR_vs_Npe[sipm] = {}

    g_SR_vs_Vov[sipm] = {}
    g_SR_vs_GainNpe[sipm] = {}
    g_bestTh_vs_Vov[sipm] = {}

    g_SR_vs_bar[sipm] = {}
    g_bestTh_vs_bar[sipm] = {}
    g_Noise_vs_bar[sipm] = {}
    g_Stoch_vs_bar[sipm] = {}
    g_DCR_vs_bar[sipm] = {}

    g_data_vs_Npe[sipm] = ROOT.TGraphErrors()
    g_data_vs_DCR[sipm] = ROOT.TGraphErrors()
    g_data_vs_GainNpe[sipm] = ROOT.TGraphErrors()
    

    fPS[sipm] = {}
    for ov in Vovs[sipm]:
        if (sipm == 'HPK_2E14_T-40C'): fPS[sipm][ov] = ROOT.TFile.Open('../plots/pulseShape_HPK_2E14_LYSO796_T-40C_Vov%.2f.root'%ov)
        if (sipm == 'HPK_2E14_T-35C'): fPS[sipm][ov] = ROOT.TFile.Open('../plots/pulseShape_HPK_2E14_LYSO796_T-35C_Vov%.2f.root'%ov)
        if (sipm == 'HPK_1E14_T-40C'): fPS[sipm][ov] = ROOT.TFile.Open('../plots/pulseShape_HPK_1E14_LYSO802_T-40C_Vov%.2f.root'%ov)
        if (sipm == 'HPK_1E14_T-35C'): fPS[sipm][ov] = ROOT.TFile.Open('../plots/pulseShape_HPK_1E14_LYSO802_T-35C_Vov%.2f.root'%ov)
        if (sipm == 'FBK_2E14_T-40C'): fPS[sipm][ov] = ROOT.TFile.Open('../plots/pulseShape_FBK_2E14_LYSO797_T-40C_Vov%.2f.root'%ov)
        if (sipm == 'FBK_2E14_T-35C'): fPS[sipm][ov] = ROOT.TFile.Open('../plots/pulseShape_FBK_2E14_LYSO797_T-35C_Vov%.2f.root'%ov)
        if (sipm == 'FBK_1E14_T-40C'): fPS[sipm][ov] = ROOT.TFile.Open('../plots/pulseShape_FBK_1E14_LYSO803_T-40C_Vov%.2f.root'%ov)
        if (sipm == 'FBK_1E14_T-35C'): fPS[sipm][ov] = ROOT.TFile.Open('../plots/pulseShape_FBK_1E14_LYSO803_T-35C_Vov%.2f.root'%ov)
        
        g_SR_vs_bar[sipm][ov] = ROOT.TGraphErrors()
        g_bestTh_vs_bar[sipm][ov] = ROOT.TGraphErrors()
        g_Noise_vs_bar[sipm][ov] = ROOT.TGraphErrors()
        g_Stoch_vs_bar[sipm][ov] = ROOT.TGraphErrors()
        g_DCR_vs_bar[sipm][ov] = ROOT.TGraphErrors()
        g_Tot_vs_SR[sipm][ov] = ROOT.TGraphErrors()

        
    f[sipm] = ROOT.TFile.Open(fnames[sipm])

    for bar in bars[sipm]:
        g[sipm][bar] = f[sipm].Get('g_deltaT_energyRatioCorr_bestTh_vs_vov_bar%02d_enBin01;1'%bar)
        if (g[sipm][bar].GetN()==0): 
            print 'No data for bar ', bar
            continue
        g_Noise_vs_Vov[sipm][bar] = ROOT.TGraphErrors()
        g_Stoch_vs_Vov[sipm][bar] = ROOT.TGraphErrors()
        g_DCR_vs_Vov[sipm][bar] = ROOT.TGraphErrors()
        g_Tot_vs_Vov[sipm][bar] = ROOT.TGraphErrors()

        g_Stoch_vs_Npe[sipm][bar] = ROOT.TGraphErrors()
        g_DCR_vs_Npe[sipm][bar] = ROOT.TGraphErrors()

        g_SR_vs_Vov[sipm][bar] = ROOT.TGraphErrors()
        g_SR_vs_GainNpe[sipm][bar] = ROOT.TGraphErrors()
        g_bestTh_vs_Vov[sipm][bar] = ROOT.TGraphErrors()
                   
        for ov in Vovs[sipm]:
            ovEff = getVovEffDCR(data, sipm, ('%.02f'%ov))[0]
            #ovEff = getVovEffDCR(data, sipm, ('%.02f'%ov))[0]
            if ( ovEff < g[sipm][bar].GetX()[0] or ovEff > g[sipm][bar].GetX()[g[sipm][bar].GetN()-1]): continue
            # get measured time resolution
            sigma_meas = g[sipm][bar].Eval(ovEff)
            err_sigma_meas = 0.
            for i in range(0,g[sipm][bar].GetN()):
                if g[sipm][bar].GetX()[i] == g[sipm][bar].Eval(ovEff):
                    err_sigma_meas = g[sipm][bar].GetErrorY[i]
            # Npe and Gain at this OVeff
            irr = '2E14'
            if ('1E14' in sipm): irr = '1E14'
            if ('1E13' in sipm): irr = '1E13'
            Npe[sipm][ov]  = 4.2*LO[sipm]*PDE(ovEff,sipm,irr)/PDE(3.50,sipm,'0') #LO is referred to 3.50 V OV
            gain[sipm][ov] = Gain(ovEff, sipm, irr)
            # get pulse shapes
            g_psL = fPS[sipm][ov].Get('g_pulseShapeL_bar%02d_Vov%.2f'%(bar,ov))
            g_psR = fPS[sipm][ov].Get('g_pulseShapeR_bar%02d_Vov%.2f'%(bar,ov))
            if (g_psL==None and g_psR==None): continue
            if (g_psL!=None): g_psL.SetName('g_pulseShapeL_bar%02d_Vov%.2f_%s'%(bar,ov,sipm))
            if (g_psR!=None): g_psR.SetName('g_pulseShapeR_bar%02d_Vov%.2f_%s'%(bar,ov,sipm))
            timingThreshold = findTimingThreshold(f[sipm].Get('g_deltaT_energyRatioCorr_vs_th_bar%02d_Vov%.2f_enBin01'%(bar,ov)), ovEff)
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

            np = 3
            # capire meglio. O mettere un errore piu' grande su SR
            #if ( 'FBK' in sipm and ovEff <= 1.60 ): np = 2
            #if ( 'HPK' in sipm and ovEff <= 1.50 ): np = 2


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

            #print sipm, ov, ovEff, gain, Npe[sipm][ov], srL, srR, sr, errSR
            g_SR_vs_Vov[sipm][bar].SetPoint( g_SR_vs_Vov[sipm][bar].GetN(), ovEff, sr )
            g_SR_vs_Vov[sipm][bar].SetPointError( g_SR_vs_Vov[sipm][bar].GetN()-1, 0, errSR )
            
            g_SR_vs_GainNpe[sipm][bar].SetPoint( g_SR_vs_GainNpe[sipm][bar].GetN(), gain[sipm][ov]*Npe[sipm][ov], sr )
            g_SR_vs_GainNpe[sipm][bar].SetPointError( g_SR_vs_GainNpe[sipm][bar].GetN()-1, 0, errSR )

            g_bestTh_vs_Vov[sipm][bar].SetPoint( g_bestTh_vs_Vov[sipm][bar].GetN(), ovEff, timingThreshold )
            g_bestTh_vs_Vov[sipm][bar].SetPointError( g_bestTh_vs_Vov[sipm][bar].GetN()-1, 0, 0 )
            
            g_SR_vs_bar[sipm][ov].SetPoint( g_SR_vs_bar[sipm][ov].GetN(), bar, sr )
            g_SR_vs_bar[sipm][ov].SetPointError( g_SR_vs_bar[sipm][ov].GetN()-1, 0, errSR )
            
            g_bestTh_vs_bar[sipm][ov].SetPoint( g_bestTh_vs_bar[sipm][ov].GetN(), bar, timingThreshold )
            g_bestTh_vs_bar[sipm][ov].SetPointError( g_bestTh_vs_bar[sipm][ov].GetN()-1, 0, 0)
            
            err_sigma_noise =  0.5*(sigma_noise(sr*(1-errSR/sr))-sigma_noise(sr*(1+errSR/sr)))
            g_Noise_vs_bar[sipm][ov].SetPoint( g_Noise_vs_bar[sipm][ov].GetN(), bar, sigma_noise(sr) )
            g_Noise_vs_bar[sipm][ov].SetPointError( g_Noise_vs_bar[sipm][ov].GetN()-1, 0,  err_sigma_noise)
            
            g_Noise_vs_Vov[sipm][bar].SetPoint(g_Noise_vs_Vov[sipm][bar].GetN(), ovEff, sigma_noise(sr))
            g_Noise_vs_Vov[sipm][bar].SetPointError(g_Noise_vs_Vov[sipm][bar].GetN()-1, 0, err_sigma_noise)
            
            g_Tot_vs_SR[sipm][ov].SetPoint(g_Tot_vs_SR[sipm][ov].GetN(), sr, sigma_meas)
            g_Tot_vs_SR[sipm][ov].SetPointError(g_Tot_vs_SR[sipm][ov].GetN()-1, errSR, err_sigma_meas)
            
            # compute s_stoch by scaling the stochastic term measured for non-irradiated SiPMs (40 ps HPK, 45 ps FBK) for sqrt(PDE) 
            alpha = 0.50 
            sigma_stoch = sigma_stoch_ref[sipm]/pow( PDE(ovEff,sipm,irr)/PDE(ov_ref,sipm,'0'), alpha  )
            # assume 5% uncertainty on PDE...
            sigma_stoch_up = sigma_stoch_ref[sipm]/pow( PDE(ovEff,sipm,irr)*(1-errPDE)/PDE(ov_ref,sipm,'0'), alpha  )
            sigma_stoch_down = sigma_stoch_ref[sipm]/pow( PDE(ovEff,sipm,irr)*(1+errPDE)/PDE(ov_ref,sipm,'0'), alpha  )
            err_sigma_stoch = 0.5*(sigma_stoch_up-sigma_stoch_down)
            g_Stoch_vs_Vov[sipm][bar].SetPoint(g_Stoch_vs_Vov[sipm][bar].GetN(), ovEff, sigma_stoch)
            g_Stoch_vs_Vov[sipm][bar].SetPointError(g_Stoch_vs_Vov[sipm][bar].GetN()-1, 0, err_sigma_stoch)
            g_Stoch_vs_bar[sipm][ov].SetPoint( g_Stoch_vs_bar[sipm][ov].GetN(), bar, sigma_stoch )
            g_Stoch_vs_bar[sipm][ov].SetPointError( g_Stoch_vs_bar[sipm][ov].GetN()-1, 0,  err_sigma_stoch)

            # compute sigma_DCR as difference in quadrature between measured tRes and noise, stoch
            if ( sigma_meas*sigma_meas - sigma_stoch*sigma_stoch - sigma_noise(sr)*sigma_noise(sr) > 0):
                sigma_dcr = math.sqrt( sigma_meas*sigma_meas - sigma_stoch*sigma_stoch - sigma_noise(sr)*sigma_noise(sr) ) 
                err_sigma_dcr = 1./sigma_dcr * math.sqrt( pow( err_sigma_meas*sigma_meas,2) + pow( err_sigma_stoch*sigma_stoch,2) + pow(err_sigma_noise*sigma_noise(sr),2))
                print sipm, bar, ov, sigma_dcr , err_sigma_dcr 
                g_DCR_vs_Vov[sipm][bar].SetPoint(g_DCR_vs_Vov[sipm][bar].GetN(), ovEff, sigma_dcr)
                g_DCR_vs_Vov[sipm][bar].SetPointError(g_DCR_vs_Vov[sipm][bar].GetN()-1, 0, err_sigma_dcr)
                g_DCR_vs_bar[sipm][ov].SetPoint( g_DCR_vs_bar[sipm][ov].GetN(), bar, sigma_dcr )
                g_DCR_vs_bar[sipm][ov].SetPointError( g_DCR_vs_bar[sipm][ov].GetN()-1, 0,  err_sigma_dcr)
                
                #dcr = VovsEff[sipm][ov][1]
                #if ('2E14' in sipm and 'HPK' in sipm): dcr = dcr/0.92 #8% gain reduction
                #if ('1E14' in sipm and 'HPK' in sipm): dcr = dcr/0.96 #4% gain reduction ???
                dcr = getVovEffDCR(data,sipm,('%.02f'%ov))[1]

                #print sipm, bar, ov, ovEff, dcr, Npe[sipm][ov], math.sqrt(dcr)/Npe[sipm][ov]/(math.sqrt(30.)/3000.)
                g_DCR_vs_Npe[sipm][bar].SetPoint( g_DCR_vs_Npe[sipm][bar].GetN(), math.sqrt(dcr)/Npe[sipm][ov]/(math.sqrt(30.)/3000.), sigma_dcr )
                g_DCR_vs_Npe[sipm][bar].SetPointError( g_DCR_vs_Npe[sipm][bar].GetN()-1, 0,  err_sigma_dcr)

            #
            sigma_tot = math.sqrt( sigma_stoch*sigma_stoch + sigma_noise(sr)*sigma_noise(sr) )
            err_sigma_tot = 1./sigma_tot * math.sqrt( pow( err_sigma_stoch*sigma_stoch,2) + pow(sigma_noise(sr)*g_Noise_vs_Vov[sipm][bar].GetErrorY(g_Noise_vs_Vov[sipm][bar].GetN()-1),2))

            g_Tot_vs_Vov[sipm][bar].SetPoint(g_Tot_vs_Vov[sipm][bar].GetN(), ovEff, sigma_tot)
            g_Tot_vs_Vov[sipm][bar].SetPointError(g_Tot_vs_Vov[sipm][bar].GetN()-1, 0, err_sigma_tot)

            #print sipm,' OV = %.2f  gain = %d  Npe = %d  bar = %02d  thr = %02d  SR = %.1f   noise = %.1f    stoch = %.1f   tot = %.1f'%(ov, gain, Npe, bar, timingThreshold, sr, sigma_noise(sr), sigma_stoch, sigma_tot)
            

g_DCR_vs_DCR = {}
g1_DCR_vs_Vov = {}
g_DCR_vs_DCRNpe_average = {}
g_DCR_vs_DCRNpe_average_all = ROOT.TGraphErrors()
g_SR_vs_Vov_average = {}

for sipm in sipmTypes:
    g1_DCR_vs_Vov[sipm] = ROOT.TGraphErrors() 
    g_DCR_vs_DCRNpe_average[sipm] = ROOT.TGraphErrors()
    g_SR_vs_Vov_average[sipm] = ROOT.TGraphErrors()
    
    for ov in Vovs[sipm]:
        ovEff = getVovEffDCR(data,sipm,('%.02f'%ov))[0] 
        dcr   = getVovEffDCR(data,sipm,('%.02f'%ov))[1]
        #if ('2E14' in sipm and 'HPK' in sipm): dcr = dcr/0.92 #8% gain reduction
        #if ('1E14' in sipm and 'HPK' in sipm): dcr = dcr/0.96 #4% gain reduction ???

        if (ov in  g_SR_vs_bar[sipm].keys()): 
            fitpol0 = ROOT.TF1('fitpol0','pol0',-100,100)
            g_SR_vs_bar[sipm][ov].Fit(fitpol0,'QNR')
            g_SR_vs_Vov_average[sipm].SetPoint(g_SR_vs_Vov_average[sipm].GetN(), ovEff, fitpol0.GetParameter(0))
            g_SR_vs_Vov_average[sipm].SetPointError(g_SR_vs_Vov_average[sipm].GetN()-1, 0, fitpol0.GetParError(0))
            
            
            gg = f[sipm].Get('g_deltaT_energyRatioCorr_bestTh_vs_bar_Vov%.02f_enBin01'%ov)    
            gg.Fit(fitpol0,'QNR')
            print sipm, ovEff, LO[sipm],  Npe[sipm][ov]
            g_data_vs_Npe[sipm].SetPoint(g_data_vs_Npe[sipm].GetN(), Npe[sipm][ov], fitpol0.GetParameter(0))
            g_data_vs_Npe[sipm].SetPointError(g_data_vs_Npe[sipm].GetN()-1, 0, fitpol0.GetParError(0))

            g_data_vs_DCR[sipm].SetPoint(g_data_vs_DCR[sipm].GetN(), dcr, fitpol0.GetParameter(0))
            g_data_vs_DCR[sipm].SetPointError(g_data_vs_DCR[sipm].GetN()-1, 0,  fitpol0.GetParError(0))

            g_data_vs_GainNpe[sipm].SetPoint(g_data_vs_GainNpe[sipm].GetN(), gain[sipm][ov]*Npe[sipm][ov], fitpol0.GetParameter(0))
            g_data_vs_GainNpe[sipm].SetPointError(g_data_vs_GainNpe[sipm].GetN()-1, 0, fitpol0.GetParError(0))


        g1_DCR_vs_Vov[sipm].SetPoint(g1_DCR_vs_Vov[sipm].GetN(), ovEff, dcr) # DCR vs OV

        x = math.sqrt(dcr)/Npe[sipm][ov]/ (math.sqrt(30.)/3000)
        x_down = math.sqrt(dcr)/(Npe[sipm][ov]*(1+errPDE) )/ (math.sqrt(30.)/3000)
        x_up   = math.sqrt(dcr)/(Npe[sipm][ov]*(1-errPDE))/ (math.sqrt(30.)/3000)
        if (g_DCR_vs_bar[sipm][ov].GetN()==0):continue
        g_DCR_vs_DCRNpe_average[sipm].SetPoint( g_DCR_vs_DCRNpe_average[sipm].GetN(), x,  g_DCR_vs_bar[sipm][ov].GetMean(2))
        g_DCR_vs_DCRNpe_average[sipm].SetPointError( g_DCR_vs_DCRNpe_average[sipm].GetN()-1, 0.5*(x_up-x_down),  g_DCR_vs_bar[sipm][ov].GetRMS(2))
        g_DCR_vs_DCRNpe_average_all.SetPoint( g_DCR_vs_DCRNpe_average_all.GetN(), x,  g_DCR_vs_bar[sipm][ov].GetMean(2))
        g_DCR_vs_DCRNpe_average_all.SetPointError( g_DCR_vs_DCRNpe_average_all.GetN()-1, 0.5*(x_up-x_down),  g_DCR_vs_bar[sipm][ov].GetRMS(2))





# Andrea's model
fitFun_tRes_dcr_model = ROOT.TF1('fitFun_tRes_dcr_model','[1] * 2 * pow(x,[0]/0.5)', 0,10)
fitFun_tRes_dcr_model.SetParameter(0,0.4)
fitFun_tRes_dcr_model.SetParameter(1,40)
fitFun_tRes_dcr_model.SetLineColor(2)
g_DCR_vs_DCRNpe_average_all.Fit(fitFun_tRes_dcr_model)


for bar in range(0,16):
    g_DCR_vs_DCR[bar] = ROOT.TGraphErrors()
    for sipm in sipmTypes:
        if (bar not in g_DCR_vs_Vov[sipm].keys()): continue
        ovEff = ov_ref # 2E14
        dcr = g_DCR_vs_Vov[sipm][bar].Eval(ovEff)
        err_dcr = 0
        for i in range(0, g_DCR_vs_Vov[sipm][bar].GetN()):
            if ( g_DCR_vs_Vov[sipm][bar].GetX()[i] >= 1.4): 
                err_dcr = g_DCR_vs_Vov[sipm][bar].GetErrorY(i)
                break
        g_DCR_vs_DCR[bar].SetPoint( g_DCR_vs_DCR[bar].GetN(), g1_DCR_vs_Vov[sipm].Eval(ovEff), dcr)
        g_DCR_vs_DCR[bar].SetPointError( g_DCR_vs_DCR[bar].GetN()-1, 0, err_dcr)


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

# Tres vs OV
print 'Plotting time resolution vs OV...'
for sipm in sipmTypes:
    c1[sipm] = {}
    hdummy1[sipm] = {}
    leg[sipm] = ROOT.TLegend(0.65,0.70,0.89,0.89)
    leg[sipm].SetBorderSize(0)
    leg[sipm].SetFillStyle(0)
    for i,bar in enumerate(bars[sipm]):
        if (bar not in g[sipm].keys()): continue
        if (g[sipm][bar].GetN()==0): continue
        c1[sipm][bar] =  ROOT.TCanvas('c_timeResolution_vs_Vov_%s_bar%02d'%(sipm,bar),'c_timeResolution_vs_Vov_%s_bar%02d'%(sipm,bar),600,600)
        c1[sipm][bar].SetGridy()
        c1[sipm][bar].cd()
        #xmin = 0.8
        #xmax = 2.0
        xmin = g[sipm][bar].GetX()[0]-0.5
        xmax = g[sipm][bar].GetX()[g[sipm][bar].GetN()-1]+0.5
        if ('1E13' in sipm):
            xmin = 0.8
            xmax = 2.4
        #if ('1E13' in sipm and 'type1' in sipm):
        #    xmin = 1.1
        #    xmax = 5.0
        if ('2E14' in sipm):
            xmin = 0.8
            xmax = 2.4
        hdummy1[sipm][bar] = ROOT.TH2F('hdummy1_%s_%d'%(sipm,bar),'',100,xmin,xmax,180,0,180)
        hdummy1[sipm][bar].GetXaxis().SetTitle('V_{OV}^{eff} [V]')
        hdummy1[sipm][bar].GetYaxis().SetTitle('#sigma_{t} [ps]')
        hdummy1[sipm][bar].Draw()
        g[sipm][bar].SetMarkerStyle(20)
        g[sipm][bar].SetMarkerSize(1)
        g[sipm][bar].SetMarkerColor(1)
        g[sipm][bar].SetLineColor(1)
        g[sipm][bar].SetLineWidth(2)
        g[sipm][bar].Draw('plsame')
        if (bar not in g_Noise_vs_Vov[sipm].keys()): continue
        g_Noise_vs_Vov[sipm][bar].SetLineWidth(2)
        g_Noise_vs_Vov[sipm][bar].SetLineColor(ROOT.kBlue)
        g_Noise_vs_Vov[sipm][bar].SetFillColor(ROOT.kBlue)
        g_Noise_vs_Vov[sipm][bar].SetFillColorAlpha(ROOT.kBlue,0.5)
        g_Noise_vs_Vov[sipm][bar].SetFillStyle(3004)
        g_Noise_vs_Vov[sipm][bar].Draw('E3lsame')
        g_Stoch_vs_Vov[sipm][bar].SetLineWidth(2)
        g_Stoch_vs_Vov[sipm][bar].SetLineColor(ROOT.kGreen+2)
        g_Stoch_vs_Vov[sipm][bar].SetFillColor(ROOT.kGreen+2)
        g_Stoch_vs_Vov[sipm][bar].SetFillStyle(3001)
        g_Stoch_vs_Vov[sipm][bar].SetFillColorAlpha(ROOT.kGreen+2,0.5)
        g_Stoch_vs_Vov[sipm][bar].Draw('E3lsame')
        g_DCR_vs_Vov[sipm][bar].SetLineWidth(2)
        g_DCR_vs_Vov[sipm][bar].SetLineColor(ROOT.kOrange+2)
        g_DCR_vs_Vov[sipm][bar].SetFillColor(ROOT.kOrange+2)
        g_DCR_vs_Vov[sipm][bar].SetFillColorAlpha(ROOT.kOrange+2,0.5)
        g_DCR_vs_Vov[sipm][bar].SetFillStyle(3001)
        g_DCR_vs_Vov[sipm][bar].Draw('E3lsame')
        g_Tot_vs_Vov[sipm][bar].SetLineWidth(2)
        g_Tot_vs_Vov[sipm][bar].SetLineColor(ROOT.kRed+1)
        g_Tot_vs_Vov[sipm][bar].SetFillColor(ROOT.kRed+1)
        g_Tot_vs_Vov[sipm][bar].SetFillColorAlpha(ROOT.kRed+1,0.5)
        g_Tot_vs_Vov[sipm][bar].SetFillStyle(3001)
        #g_Tot_vs_Vov[sipm][bar].Draw('E3lsame')
        #save on file
        outfile.cd()
        g[sipm][bar].Write('g_Data_vs_Vov_%s_bar%02d'%(sipm,bar))
        g_Noise_vs_Vov[sipm][bar].Write('g_Noise_vs_Vov_%s_bar%02d'%(sipm,bar))
        g_Stoch_vs_Vov[sipm][bar].Write('g_Stoch_vs_Vov_%s_bar%02d'%(sipm,bar))
        g_DCR_vs_Vov[sipm][bar].Write('g_DCR_vs_Vov_%s_bar%02d'%(sipm,bar))
        if (i==0):
            leg[sipm].AddEntry(g[sipm][bar], 'data', 'PL')
            leg[sipm].AddEntry(g_Noise_vs_Vov[sipm][bar], 'noise', 'L')
            leg[sipm].AddEntry(g_Stoch_vs_Vov[sipm][bar], 'stoch', 'L')
            leg[sipm].AddEntry(g_DCR_vs_Vov[sipm][bar], 'DCR', 'L')
            #leg[sipm].AddEntry(g_Tot_vs_Vov[sipm][bar], 'stoch (+) noise', 'PL')
        leg[sipm].Draw('same')
        latex = ROOT.TLatex(0.20,0.85,'%s'%(sipm.replace('_',' ').replace('T','T=')))
        latex.SetNDC()
        latex.SetTextSize(0.045)
        latex.SetTextFont(42)
        latex.Draw('same')
        c1[sipm][bar].SaveAs(outdir+'/'+c1[sipm][bar].GetName()+'.png')
        c1[sipm][bar].SaveAs(outdir+'/'+c1[sipm][bar].GetName()+'.pdf')
        hdummy1[sipm][bar].Delete()
        #c1[sipm][bar].Delete()


# total time resolution vs SR
print 'Plotting time resolution vs slew rate...'
for sipm in sipmTypes:
    for ov in Vovs[sipm]:
        if (ov not in g_Tot_vs_SR[sipm].keys()): continue
        ovEff = getVovEffDCR(data,sipm, ('%.02f'%ov))[0] 
        c =  ROOT.TCanvas('c_timeResolution_vs_SR_%s_Vov%.02f'%(sipm,ovEff),'c_timeResolution_vs_SR_%s_Vov%.02f'%(sipm,ovEff),600,600)
        c.SetGridy()
        c.cd()
        xmin = 0.
        xmax = g_Tot_vs_SR[sipm][ov].GetMean() + 5.
        ymin = g_Tot_vs_SR[sipm][ov].GetMean(2)-40.
        ymax = g_Tot_vs_SR[sipm][ov].GetMean(2)+40.
        hdummy = ROOT.TH2F('hdummy_%s_%d'%(sipm,ov),'',100, xmin, xmax, 100, ymin, ymax)
        hdummy.GetXaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
        hdummy.GetYaxis().SetTitle('#sigma_{t} [ps]')
        hdummy.Draw()
        g_Tot_vs_SR[sipm][ov].SetMarkerStyle(20)
        g_Tot_vs_SR[sipm][ov].SetMarkerSize(1)
        g_Tot_vs_SR[sipm][ov].SetMarkerColor(1)
        g_Tot_vs_SR[sipm][ov].SetLineColor(1)
        g_Tot_vs_SR[sipm][ov].SetLineWidth(2)
        g_Tot_vs_SR[sipm][ov].Draw('psame')
        c.SaveAs(outdir+'/'+c.GetName()+'.png')
        c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
        hdummy.Delete()
        #c.Delete()



markers = { 'HPK_2E14_T-40C' : 24 ,
            'HPK_2E14_T-35C' : 20 ,
            'HPK_1E14_T-40C' : 24 ,
            'HPK_1E14_T-35C' : 20 ,
            'FBK_2E14_T-40C' : 25,
            'FBK_2E14_T-35C' : 21,
            'FBK_1E14_T-40C' : 25,
            'FBK_1E14_T-35C' : 21}


cols = { 'HPK_2E14_T-40C' : ROOT.kBlack ,
         'HPK_2E14_T-35C' : ROOT.kBlack ,
         'HPK_1E14_T-40C' : ROOT.kBlue  ,
         'HPK_1E14_T-35C' : ROOT.kBlue  ,
         'FBK_2E14_T-40C' : ROOT.kRed   ,
         'FBK_2E14_T-35C' : ROOT.kRed   ,
         'FBK_1E14_T-40C' : ROOT.kOrange+1   ,
         'FBK_1E14_T-35C' : ROOT.kOrange+1  }

# vs npe
print 'Plotting tRes_DCR vs Npe...'
for bar in range(0,16):      
    c2 =  ROOT.TCanvas('c_timeResolutionDCR_vs_DCRNpe_bar%02d'%(bar),'c_timeResolutionDCR_vs_DCRNpe_bar%02d'%(bar),600,600)
    c2.SetGridx()
    c2.SetGridy()
    c2.cd()
    xmax = 2
    ymax = 120
    #if ('1E13' in sipm):        
    #    xmax = 2
    #    ymax = 100
    hdummy2 = ROOT.TH2F('hdummy2_%d'%(bar),'',100,0,xmax,100,0,ymax)
    hdummy2.GetXaxis().SetTitle('#sqrt{DCR/30GHz}/(Npe/3000)')
    hdummy2.GetYaxis().SetTitle('#sigma_{t}^{DCR} [ps]')
    hdummy2.Draw()
    for sipm in sipmTypes:    
        if (bar not in g_DCR_vs_Npe[sipm].keys()): continue
        g_DCR_vs_Npe[sipm][bar].SetMarkerStyle(markers[sipm])
        g_DCR_vs_Npe[sipm][bar].SetMarkerColor(cols[sipm])
        g_DCR_vs_Npe[sipm][bar].SetLineWidth(1)
        g_DCR_vs_Npe[sipm][bar].SetLineColor(cols[sipm])
        g_DCR_vs_Npe[sipm][bar].Draw('psame')
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
for sipm in sipmTypes:
    g_DCR_vs_DCRNpe_average[sipm].SetMarkerStyle(markers[sipm])
    g_DCR_vs_DCRNpe_average[sipm].SetMarkerColor(cols[sipm])
    g_DCR_vs_DCRNpe_average[sipm].SetLineWidth(1)
    g_DCR_vs_DCRNpe_average[sipm].SetLineColor(cols[sipm])
    g_DCR_vs_DCRNpe_average[sipm].Draw('psame')
    outfile.cd() 
    g_DCR_vs_DCRNpe_average[sipm].Write('g_DCR_vs_DCRNpe_average_%s'%sipm)
c2.SaveAs(outdir+'/'+c2.GetName()+'.png')
c2.SaveAs(outdir+'/'+c2.GetName()+'.pdf')
hdummy2.Delete()
#c2.Delete()


# sigma_DCR vs DCR @ reference OV
h = ROOT.TH1F('h_powerLawCoeffDCR','h_powerLawCoeffDCR',50,0.0,1.0)
for bar in range(0,16): 
    c2 =  ROOT.TCanvas('c_timeResolutionDCR_vs_DCR_bar%02d'%(bar),'c_timeResolutionDCR_vs_DCR_bar%02d'%(bar),600,600)
    c2.SetGridx()
    c2.SetGridy()
    c2.cd()
    hdummy2 = ROOT.TH2F('hdummy2_%d'%(bar),'',100,0,100,100,0,180)
    hdummy2.GetXaxis().SetTitle('DCR [GHz]')
    hdummy2.GetYaxis().SetTitle('#sigma_{t}^{DCR} [ps]')
    hdummy2.Draw()
    if (g_DCR_vs_DCR[bar].GetN() == 0): continue
    g_DCR_vs_DCR[bar].SetMarkerStyle(20)
    g_DCR_vs_DCR[bar].SetMarkerSize(1)
    g_DCR_vs_DCR[bar].Draw('psame')
    fitFun = ROOT.TF1('fitFun_%2d'%(bar),'[0]*pow(x,[1])',0,200)
    fitFun.SetParameters(20.,0.5)
    g_DCR_vs_DCR[bar].Fit(fitFun,'QRS+')
    print fitFun.GetParameter(1)
    h.Fill(fitFun.GetParameter(1))
    c2.SaveAs(outdir+'/'+c2.GetName()+'.png')
    c2.SaveAs(outdir+'/'+c2.GetName()+'.pdf')
    fitFun.Delete()
    hdummy2.Delete()
    #c2.Delete()

ROOT.gStyle.SetOptStat(1)
c2 = ROOT.TCanvas('c_powerLawCoeffDCR','c_powerLawCoeffDCR')
h.GetXaxis().SetTitle('power law coeff.')
h.Draw()
c2.SaveAs(outdir+'/'+c2.GetName()+'.png')
c2.SaveAs(outdir+'/'+c2.GetName()+'.pdf')
ROOT.gStyle.SetOptStat(0)


# SR and best threshold vs Vov
leg2 = ROOT.TLegend(0.20,0.70,0.45,0.89)
leg2.SetBorderSize(0)
leg2.SetFillStyle(0)
for i,bar in enumerate(bars[sipm]):
    if (bar not in g[sipm].keys()): continue
    if (g[sipm][bar].GetN()==0): continue     
    c3[bar] = ROOT.TCanvas('c_slewRate_vs_Vov_bar%02d'%(bar),'c_slewRate_vs_Vov_bar%02d'%(bar),600,600)
    c3[bar].SetGridy()
    c3[bar].cd()
    xmin = 0.9
    xmax = 2.5
    ymax = 15 
    if ('1E13' in sipm):
        xmin = 1.1
        xmax = 5.0
        ymax = 35.
    hdummy3[bar] = ROOT.TH2F('hdummy3_%d'%(bar),'',100,xmin,xmax,100,0,ymax)
    hdummy3[bar].GetXaxis().SetTitle('V_{OV}^{eff} [V]')
    hdummy3[bar].GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
    hdummy3[bar].Draw()
    for j,sipm in enumerate(sipmTypes):
        if (bar not in g_SR_vs_Vov[sipm].keys()): continue
        if (i==0):
            leg2.AddEntry(g_SR_vs_Vov[sipm][bar], '%s'%sipm, 'PL')
        g_SR_vs_Vov[sipm][bar].SetMarkerStyle(markers[sipm])
        g_SR_vs_Vov[sipm][bar].SetMarkerColor(cols[sipm])
        g_SR_vs_Vov[sipm][bar].SetLineColor(cols[sipm])
        g_SR_vs_Vov[sipm][bar].Draw('plsame')
    leg2.Draw()
    outfile.cd()
    g_SR_vs_Vov[sipm][bar].Write('g_SR_vs_Vov_%s_bar%02d'%(sipm,bar))
    c3[bar].SaveAs(outdir+'/'+c3[bar].GetName()+'.png')
    c3[bar].SaveAs(outdir+'/'+c3[bar].GetName()+'.pdf')
    hdummy3[bar].Delete()
    

    c3[bar] = ROOT.TCanvas('c_slewRate_vs_GainNpe_bar%02d'%(bar),'c_slewRate_vs_GainNpe_bar%02d'%(bar),600,600)
    c3[bar].SetGridy()
    c3[bar].cd()
    #hdummy3[bar] = ROOT.TH2F('hdummy3_%d'%(bar),'',100,0,2,100,0,35)
    hdummy3[bar] = ROOT.TH2F('hdummy3_%d'%(bar),'',100,0,3E09,100,0,35)
    hdummy3[bar].GetXaxis().SetTitle('gain x Npe')
    hdummy3[bar].GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
    hdummy3[bar].Draw()
    for j,sipm in enumerate(sipmTypes):
        if (bar not in g_SR_vs_GainNpe[sipm].keys()): continue
        g_SR_vs_GainNpe[sipm][bar].SetMarkerStyle( markers[sipm] )
        g_SR_vs_GainNpe[sipm][bar].SetMarkerColor(cols[sipm])
        g_SR_vs_GainNpe[sipm][bar].SetLineColor(cols[sipm])
        g_SR_vs_GainNpe[sipm][bar].Draw('psame')
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
    for j,sipm in enumerate(sipmTypes):
        if (bar not in g_bestTh_vs_Vov[sipm].keys()): continue
        g_bestTh_vs_Vov[sipm][bar].SetMarkerStyle(markers[sipm])
        g_bestTh_vs_Vov[sipm][bar].SetMarkerColor(cols[sipm])
        g_bestTh_vs_Vov[sipm][bar].SetLineColor(cols[sipm])
        g_bestTh_vs_Vov[sipm][bar].Draw('plsame')
    c4[bar].SaveAs(outdir+'/'+c4[bar].GetName()+'.png')
    c4[bar].SaveAs(outdir+'/'+c4[bar].GetName()+'.pdf')


# average slew rate vs OV
c2 =  ROOT.TCanvas('c_slewRate_vs_Vov_average','c_slewRate_vs_Vov_average',600,600)
c2.SetGridx()
c2.SetGridy()
c2.cd()    
hdummy2 = ROOT.TH2F('hdummy2','',16, 0.5, 2.5,100,0,15)
hdummy2.GetXaxis().SetTitle('V_{OV}^{eff} [V]')
hdummy2.GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
hdummy2.Draw()
for sipm in sipmTypes:
    g_SR_vs_Vov_average[sipm].SetMarkerStyle(markers[sipm])
    g_SR_vs_Vov_average[sipm].SetMarkerColor(cols[sipm])
    g_SR_vs_Vov_average[sipm].SetLineWidth(1)
    g_SR_vs_Vov_average[sipm].SetLineColor(cols[sipm])
    g_SR_vs_Vov_average[sipm].Draw('plsame')
    outfile.cd()
    g_SR_vs_Vov_average[sipm].Write('g_SR_vs_Vov_average_%s'%sipm)
leg2.Draw()  
c2.SaveAs(outdir+'/'+c2.GetName()+'.png')
c2.SaveAs(outdir+'/'+c2.GetName()+'.pdf')
hdummy2.Delete()


# average time resolution vs Npe
c2 =  ROOT.TCanvas('c_timeResolution_vs_Npe_average','c_timeResolution_vs_Npe_average',600,600)
c2.SetGridx()
c2.SetGridy()
c2.cd()    
hdummy2 = ROOT.TH2F('hdummy2','',1000, 1000, 5000, 100, 60, 180)
hdummy2.GetXaxis().SetTitle('Npe')
hdummy2.GetYaxis().SetTitle('#sigma_{t} [ps]')
hdummy2.GetXaxis().SetNdivisions(505)
hdummy2.Draw()
for sipm in sipmTypes:
    g_data_vs_Npe[sipm].SetMarkerStyle(markers[sipm])
    g_data_vs_Npe[sipm].SetMarkerColor(cols[sipm])
    g_data_vs_Npe[sipm].SetLineWidth(1)
    g_data_vs_Npe[sipm].SetLineColor(cols[sipm])
    g_data_vs_Npe[sipm].Draw('plsame')
    outfile.cd()
    g_data_vs_Npe[sipm].Write('g_data_vs_Npe_average_%s'%sipm)
leg2.Draw()  
c2.SaveAs(outdir+'/'+c2.GetName()+'.png')
c2.SaveAs(outdir+'/'+c2.GetName()+'.pdf')
hdummy2.Delete()


# average time resolution vs DCR
c2 =  ROOT.TCanvas('c_timeResolution_vs_DCR_average','c_timeResolution_vs_DCR_average',600,600)
c2.SetGridx()
c2.SetGridy()
c2.cd()    
hdummy2 = ROOT.TH2F('hdummy2','',1000, 0, 100, 100, 60, 180)
hdummy2.GetXaxis().SetTitle('DCR [GHz]')
hdummy2.GetYaxis().SetTitle('#sigma_{t} [ps]')
hdummy2.Draw()
for sipm in sipmTypes:
    g_data_vs_DCR[sipm].SetMarkerStyle(markers[sipm])
    g_data_vs_DCR[sipm].SetMarkerColor(cols[sipm])
    g_data_vs_DCR[sipm].SetLineWidth(1)
    g_data_vs_DCR[sipm].SetLineColor(cols[sipm])
    g_data_vs_DCR[sipm].Draw('plsame')
    outfile.cd()
    g_data_vs_DCR[sipm].Write('g_data_vs_DCR_average_%s'%sipm)
leg2.Draw()  
c2.SaveAs(outdir+'/'+c2.GetName()+'.png')
c2.SaveAs(outdir+'/'+c2.GetName()+'.pdf')
hdummy2.Delete()

# average time resolution vs GainxNpe
c2 =  ROOT.TCanvas('c_timeResolution_vs_GainNpe_average','c_timeResolution_vs_GainNpe_average',600,600)
c2.SetGridx()
c2.SetGridy()
c2.cd()    
hdummy2 = ROOT.TH2F('hdummy2','',1000, 0, 1.5E09, 100, 60, 180)
hdummy2.GetXaxis().SetTitle('Gain x Npe')
hdummy2.GetYaxis().SetTitle('#sigma_{t} [ps]')
hdummy2.GetXaxis().SetNdivisions(505)
hdummy2.Draw()
for sipm in sipmTypes:
    g_data_vs_GainNpe[sipm].SetMarkerStyle(markers[sipm])
    g_data_vs_GainNpe[sipm].SetMarkerColor(cols[sipm])
    g_data_vs_GainNpe[sipm].SetLineWidth(1)
    g_data_vs_GainNpe[sipm].SetLineColor(cols[sipm])
    g_data_vs_GainNpe[sipm].Draw('plsame')
leg2.Draw()  
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
for j,sipm in enumerate(sipmTypes):
    for ov in Vovs[sipm]:
        if (ov not in g_SR_vs_bar[sipm].keys()): continue
        ovEff = getVovEffDCR(data,sipm, ('%.02f'%ov))[0] 
        c5[ov] = ROOT.TCanvas('c_slewRate_vs_bar_%s_Vov%.2f'%(sipm,ovEff),'c_slewRate_vs_bar_%s_Vov%.2f'%(sipm,ovEff),600,600)
        c5[ov].SetGridy()
        c5[ov].cd()
        #hdummy5[ov] = ROOT.TH2F('hdummy5_%d'%(ov),'',100,-0.5,15.5,100,0,15)
        hdummy5[ov] = ROOT.TH2F('hdummy5_%s_%.2f'%(sipm,ov),'',100,-0.5,15.5,100,0,35)
        hdummy5[ov].GetXaxis().SetTitle('bar')
        hdummy5[ov].GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
        hdummy5[ov].Draw()
        g_SR_vs_bar[sipm][ov].SetMarkerStyle(markers[sipm])
        g_SR_vs_bar[sipm][ov].SetMarkerColor(cols[sipm])
        g_SR_vs_bar[sipm][ov].SetLineColor(cols[sipm])
        g_SR_vs_bar[sipm][ov].Draw('psame')
        leg2.Draw()
        c5[ov].SaveAs(outdir+'/'+c5[ov].GetName()+'.png')
        c5[ov].SaveAs(outdir+'/'+c5[ov].GetName()+'.pdf')


        c6[ov] = ROOT.TCanvas('c_bestTh_vs_bar_%s_Vov%.2f'%(sipm,ovEff),'c_bestTh_vs_bar_%s_Vov%.2f'%(sipm,ovEff),600,600)
        c6[ov].SetGridy()
        c6[ov].cd()
        hdummy6[ov] = ROOT.TH2F('hdummy6_%s_%.2f'%(sipm,ov),'',100,-0.5,15.5,100,0,20)
        hdummy6[ov].GetXaxis().SetTitle('bar')
        hdummy6[ov].GetYaxis().SetTitle('timing threshold [DAC]')
        hdummy6[ov].Draw()
        g_bestTh_vs_bar[sipm][ov].SetMarkerStyle(markers[sipm])
        g_bestTh_vs_bar[sipm][ov].SetMarkerColor(cols[sipm])
        g_bestTh_vs_bar[sipm][ov].SetLineColor(cols[sipm])
        g_bestTh_vs_bar[sipm][ov].Draw('plsame')
        leg2.Draw()        
        c6[ov].SaveAs(outdir+'/'+c6[ov].GetName()+'.png')
        c6[ov].SaveAs(outdir+'/'+c6[ov].GetName()+'.pdf')

        c7[ov] = ROOT.TCanvas('c_noise_vs_bar_%s_Vov%.2f'%(sipm,ovEff),'c_noise_vs_bar_%s_Vov%.2f'%(sipm,ovEff),600,600)
        c7[ov].SetGridy()
        c7[ov].cd()
        hdummy7[ov] = ROOT.TH2F('hdummy7_%s_%.2f'%(sipm,ov),'',100,-0.5,15.5,100,0,80)
        hdummy7[ov].GetXaxis().SetTitle('bar')
        hdummy7[ov].GetYaxis().SetTitle('#sigma_{t, noise} [ps]')
        hdummy7[ov].Draw()
        g_Noise_vs_bar[sipm][ov].SetMarkerStyle( markers[sipm] )
        g_Noise_vs_bar[sipm][ov].SetMarkerColor(cols[sipm])
        g_Noise_vs_bar[sipm][ov].SetLineColor(cols[sipm])
        g_Noise_vs_bar[sipm][ov].Draw('psame')
        leg2.Draw()
        c7[ov].SaveAs(outdir+'/'+c7[ov].GetName()+'.png')
        c7[ov].SaveAs(outdir+'/'+c7[ov].GetName()+'.pdf')

        c8[ov] = ROOT.TCanvas('c_stoch_vs_bar_%s_Vov%.2f'%(sipm,ovEff),'c_stoch_vs_bar_%s_Vov%.2f'%(sipm,ovEff),600,600)
        c8[ov].SetGridy()
        c8[ov].cd()
        hdummy8[ov] = ROOT.TH2F('hdummy8_%s_%.2f'%(sipm,ov),'',100,-0.5,15.5,100,0,80)
        hdummy8[ov].GetXaxis().SetTitle('bar')
        hdummy8[ov].GetYaxis().SetTitle('#sigma_{t, stoch} [ps]')
        hdummy8[ov].Draw()
        g_Stoch_vs_bar[sipm][ov].SetMarkerStyle( markers[sipm] )
        g_Stoch_vs_bar[sipm][ov].SetMarkerColor(cols[sipm])
        g_Stoch_vs_bar[sipm][ov].SetLineColor(cols[sipm])
        g_Stoch_vs_bar[sipm][ov].Draw('psame')
        leg2.Draw()
        c8[ov].SaveAs(outdir+'/'+c8[ov].GetName()+'.png')
        c8[ov].SaveAs(outdir+'/'+c8[ov].GetName()+'.pdf')
        
        c9[ov] = ROOT.TCanvas('c_dcr_vs_bar_%s_Vov%.2f'%(sipm,ovEff),'c_dcr_vs_bar_%s_Vov%.2f'%(sipm,ovEff),600,600)
        c9[ov].SetGridy()
        c9[ov].cd()
        hdummy9[ov] = ROOT.TH2F('hdummy9_%s_%.2f'%(sipm,ov),'',100,-0.5,15.5,100,0,140)
        hdummy9[ov].GetXaxis().SetTitle('bar')
        hdummy9[ov].GetYaxis().SetTitle('#sigma_{t, DCR} [ps]')
        hdummy9[ov].Draw()
        g_DCR_vs_bar[sipm][ov].SetMarkerStyle( markers[sipm] )
        g_DCR_vs_bar[sipm][ov].SetMarkerColor(cols[sipm])
        g_DCR_vs_bar[sipm][ov].SetLineColor(cols[sipm])
        g_DCR_vs_bar[sipm][ov].Draw('psame')
        leg2.Draw()
        c9[ov].SaveAs(outdir+'/'+c9[ov].GetName()+'.png')
        c9[ov].SaveAs(outdir+'/'+c9[ov].GetName()+'.pdf')

outfile.Close()

raw_input('OK?')
