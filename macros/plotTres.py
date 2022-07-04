#! /usr/bin/env python
import os
import shutil
import glob
import math
import array
import sys
import time
import argparse

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

ROOT.gROOT.SetBatch(True)
#ROOT.gROOT.SetBatch(False)
ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0111)



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
    imin = max(0, itiming-2)
    if ( imin >= 0 and g1.GetX()[imin+1] < g1.GetX()[imin] ): imin = ifirst
    tmin = g1.GetX()[imin]
    tmax = min(g1.GetX()[imin+npoints],3.)
    for i in range(imin, imin+npoints+1):
        gtemp.SetPoint(gtemp.GetN(), g1.GetX()[i], g1.GetY()[i])
        gtemp.SetPointError(gtemp.GetN()-1, g1.GetErrorX(i), g1.GetErrorY(i))
    fitSR = ROOT.TF1('fitSR', 'pol1', tmin, tmax)
    fitSR.SetLineColor(g1.GetMarkerColor()+1)
    fitSR.SetRange(tmin,tmax)
    fitSR.SetParameters(0, 10)
    fitStatus = int(gtemp.Fit(fitSR, 'QRS+'))
    sr = fitSR.Derivative( g1.GetX()[itiming])
    err_sr = fitSR.GetParError(1)
    #print g1.GetName(), 'SR = ', sr,'+/-', fitSR.GetParError(1) , '   chi2 = ', fitSR.GetChisquare(), '   NDF = ', fitSR.GetNDF(), '  fitStatus = ', fitStatus
    #if (fitSR.GetNDF()==0):
    #    sr = -1
    #    err_sr = -1
    if (canvas!=None):
        canvas.cd()
        #gtemp.SetMarkerStyle(g1.GetMarkerStyle())
        #gtemp.SetMarkerColor(g1.GetMarkerColor())
        gtemp.Draw('psames')
        g1.Draw('psames')
        gtemp.Draw('p*sames')
        fitSR.Draw('same')
        canvas.Update()
        #ps = g1.FindObject("stats")
        ps = gtemp.FindObject('stats')
        ps.SetTextColor(g1.GetMarkerColor())
        if ('L' in g1.GetName()):
            ps.SetY1NDC(0.85) # new y start position
            ps.SetY2NDC(0.95)# new y end position
        if ('R' in g1.GetName()):
            ps.SetY1NDC(0.73) # new y start position
            ps.SetY2NDC(0.83)# new y end position
        #canvas.Modified()
    return(sr,err_sr)


def findTimingThreshold(g2):
    xmin = 0
    ymin = 9999
    for i in range(0, g2.GetN()):
        y = g2.GetY()[i]
        x = g2.GetX()[i]
        if ( y < ymin):
            ymin = y
            xmin = x 
    return xmin

# =====================================
outdir = '/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_Vov_FBK_nonIrr/'
#outdir = '/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_Vov_HPK_FBK_nonIrr/'
#outdir = '/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_Vov_HPK_nonIrr_TOFHIR2B/'
if (os.path.exists(outdir)==False):
    os.mkdir(outdir)
if (os.path.exists(outdir+'/plotsSR')==False):
    os.mkdir(outdir+'/plotsSR/')
#outfile   = ROOT.TFile.Open(outdir+'/plots_timeResolution_HPK_FBK_nonIrr_TBJune22.root','recreate')  
outfile   = ROOT.TFile.Open(outdir+'/plots_timeResolution_FBK_nonIrr_TBJune22.root','recreate')  
#outfile   = ROOT.TFile.Open(outdir+'/plots_timeResolution_HPK_nonIrr_TOFHIR2B_TBJune22.root','recreate')  


#sipmTypes = ['HPK_nonIrr_LYSO528','FBK_nonIrr_LYSO522', 'FBK_nonIrr_LYSO524']
#sipmTypes = ['HPK_nonIrr_LYSO528','FBK_nonIrr_LYSO800','FBK_nonIrr_LYSO522']
sipmTypes = ['FBK_nonIrr_LYSO800','FBK_nonIrr_LYSO522', 'FBK_nonIrr_LYSO524']

#sipmTypes = ['HPK_nonIrr_LYSO528_2X','HPK_nonIrr_LYSO528_2B']
#sipmTypes = ['FBK_nonIrr_LYSO522','HPK_nonIrr_LYSO528_2X']


fnames = {'HPK_nonIrr_LYSO528' : '../plots/HPK_nonIrr_LYSO528_T10C_summary.root',
          'FBK_nonIrr_LYSO800' : '../plots/FBK_nonIrr_LYSO800_T10C_summary.root',
          'FBK_nonIrr_LYSO522' : '../plots/FBK_nonIrr_LYSO522_T10C_summary.root',
          'FBK_nonIrr_LYSO524' : '../plots/FBK_nonIrr_LYSO524_T10C_summary.root',
          'HPK_nonIrr_LYSO528_2X' : '../plots/HPK_nonIrr_LYSO528_T10C_summary.root',   
          'HPK_nonIrr_LYSO528_2B' : '../plots_tofhir2b/HPK_nonIrr_LYSO528_T10C_scaling1_summary.root',   
          }

labels = { 'HPK_nonIrr_LYSO528' : 'HPK+LYSO528',
           'FBK_nonIrr_LYSO800' : 'FBK+LYSO800',
           'FBK_nonIrr_LYSO522' : 'FBK+LYSO522',
           'FBK_nonIrr_LYSO524' : 'FBK+LYSO524',
           'HPK_nonIrr_LYSO528_2X' : 'HPK+LYSO528 (2X)',
           'HPK_nonIrr_LYSO528_2B' : 'HPK+LYSO528 (2B)',
       }


# LO
LO = { 'HPK_nonIrr_LYSO528' : 1300.,
       'FBK_nonIrr_LYSO800' : 1042.,
       'FBK_nonIrr_LYSO522' : 1100.,
       'FBK_nonIrr_LYSO524' :  950.,
       'HPK_nonIrr_LYSO528_2X' : 1300.,
       'HPK_nonIrr_LYSO528_2B' : 1300.,
}


# decay time
tau = { 'HPK_nonIrr_LYSO528' : 41.6,   # MiB measurements
        'FBK_nonIrr_LYSO800' : 38.7,   # MiB measurements
        'FBK_nonIrr_LYSO522' : 41.6,   # MiB measurements
        'FBK_nonIrr_LYSO524' : 40.4,   # MiB measurements
        'HPK_nonIrr_LYSO528_2X' : 41.6,   # MiB measurements
        'HPK_nonIrr_LYSO528_2B' : 41.6,   # MiB measurements
}

np = 3
errSRsyst  = 0.10 # error on the slew rate

g = {}
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

g_Stoch_vs_SR   = {}
g_Noise_vs_SR   = {}
g_Tot_vs_SR   = {}


bars = {}
Vovs = {}
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

    #Vovs[sipm] = [1.50,3.50]

fPS = {}
Npe = {}
for sipm in sipmTypes:
    f = ROOT.TFile.Open(fnames[sipm])

    Npe[sipm] = {}
    g[sipm] = {}
    g_Noise_vs_Vov[sipm] = {}
    g_Stoch_vs_Vov[sipm] = {}
    g_Tot_vs_Vov[sipm] = {}

    g_Stoch_vs_Npe[sipm] = {}

    g_SR_vs_Vov[sipm] = {}
    g_bestTh_vs_Vov[sipm] = {}

    g_SR_vs_bar[sipm] = {}
    g_bestTh_vs_bar[sipm] = {}
    g_Noise_vs_bar[sipm] = {}
    g_Stoch_vs_bar[sipm] = {}

    g_SR_vs_GainNpe[sipm] = {}

    g_Stoch_vs_SR[sipm] = {}
    g_Noise_vs_SR[sipm] = {}
    g_Tot_vs_SR[sipm] = {}

    fPS[sipm] = {}
    for ov in Vovs[sipm]:
        if (sipm == 'HPK_nonIrr_LYSO528'): fPS[sipm][ov] = ROOT.TFile.Open('../plots/pulseShape_HPK_nonIrr_LYSO528_T10C_Vov%.2f.root'%ov)
        if (sipm == 'FBK_nonIrr_LYSO800'): fPS[sipm][ov] = ROOT.TFile.Open('../plots/pulseShape_FBK_nonIrr_LYSO800_T10C_Vov%.2f.root'%ov)
        if (sipm == 'FBK_nonIrr_LYSO522'): fPS[sipm][ov] = ROOT.TFile.Open('../plots/pulseShape_FBK_nonIrr_LYSO522_T10C_Vov%.2f.root'%ov)
        if (sipm == 'FBK_nonIrr_LYSO524'): fPS[sipm][ov] = ROOT.TFile.Open('../plots/pulseShape_FBK_nonIrr_LYSO524_T10C_Vov%.2f.root'%ov)
        if (sipm == 'HPK_nonIrr_LYSO528_2X'): fPS[sipm][ov] = ROOT.TFile.Open('../plots/pulseShape_HPK_nonIrr_LYSO528_T10C_Vov%.2f.root'%ov)
        if (sipm == 'HPK_nonIrr_LYSO528_2B'): fPS[sipm][ov] = ROOT.TFile.Open('../plots_tofhir2b/pulseShape_HPK_nonIrr_LYSO528_T10C_Vov%.2f_tofhir2b_scaling1.root'%ov)

        g_SR_vs_bar[sipm][ov] = ROOT.TGraphErrors()
        g_bestTh_vs_bar[sipm][ov] = ROOT.TGraphErrors()
        g_Noise_vs_bar[sipm][ov] = ROOT.TGraphErrors()
        g_Stoch_vs_bar[sipm][ov] = ROOT.TGraphErrors()
        g_Stoch_vs_SR[sipm][ov] = ROOT.TGraphErrors()
        g_Noise_vs_SR[sipm][ov] = ROOT.TGraphErrors()
        g_Tot_vs_SR[sipm][ov]   = ROOT.TGraphErrors()

    for bar in bars[sipm]:
        #g[sipm][bar] = f.Get('g_deltaT_energyRatioCorr_vs_vov_bar%02d_th10_enBin01'%bar)
        g[sipm][bar] = f.Get('g_deltaT_energyRatioCorr_bestTh_vs_vov_bar%02d_enBin01'%bar)
        g_Noise_vs_Vov[sipm][bar] = ROOT.TGraphErrors()
        g_Stoch_vs_Vov[sipm][bar] = ROOT.TGraphErrors()
        g_Tot_vs_Vov[sipm][bar] = ROOT.TGraphErrors()

        g_Stoch_vs_Npe[sipm][bar] = ROOT.TGraphErrors()

        g_SR_vs_Vov[sipm][bar] = ROOT.TGraphErrors()
        g_SR_vs_GainNpe[sipm][bar] = ROOT.TGraphErrors()
        g_bestTh_vs_Vov[sipm][bar] = ROOT.TGraphErrors()
        
        sigma_stoch_ref = 0
        err_sigma_stoch_ref = 0
        ov_ref = 3.5
    
        for i in range(0,g[sipm][bar].GetN()):
            ov = g[sipm][bar].GetX()[i]
            if (ov != ov_ref): continue
            sigma_tot = g[sipm][bar].GetY()[i]
            err_sigma_tot = g[sipm][bar].GetErrorY(i)
            g_psL = fPS[sipm][ov].Get('g_pulseShapeL_bar%02d_Vov%.2f'%(bar,ov))
            g_psR = fPS[sipm][ov].Get('g_pulseShapeR_bar%02d_Vov%.2f'%(bar,ov))
            if (g_psL==None): continue
            if (g_psR==None): continue
            g_psL.SetName('g_pulseShapeL_bar%02d_Vov%.2f'%(bar,ov))
            g_psR.SetName('g_pulseShapeR_bar%02d_Vov%.2f'%(bar,ov))
            timingThreshold = findTimingThreshold(f.Get('g_deltaT_energyRatioCorr_vs_th_bar%02d_Vov%.2f_enBin01'%(bar,ov)))
            gtempL = ROOT.TGraphErrors()
            gtempR = ROOT.TGraphErrors()
            srL,err_srL = getSlewRateFromPulseShape(g_psL, timingThreshold, np, gtempL)
            srR,err_srR = getSlewRateFromPulseShape(g_psR, timingThreshold, np, gtempR)
            if (srL>0 and srR>0):
                print sipm, ov, srL, srR
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
            if (sigma_tot>=sigma_noise(sr)):
                sigma_stoch_ref = math.sqrt(sigma_tot*sigma_tot - sigma_noise(sr)*sigma_noise(sr))
                err_sigma_noise = 0.5*(sigma_noise(sr*(1-errSR))-sigma_noise(sr*(1+errSR)))
                err_sigma_stoch_ref = 1./sigma_stoch_ref*math.sqrt( pow(err_sigma_tot*sigma_tot,2)+pow( sigma_noise(sr)*err_sigma_noise ,2) )
            else:
                print 'skipping bar%02d:  %.1f   %.1f'%(bar, sigma_tot,sigma_noise(sr))
                continue
                
        for i in range(0,g[sipm][bar].GetN()):
            sigma_meas = g[sipm][bar].GetY()[i]
            err_sigma_meas   = g[sipm][bar].GetErrorY(i)
            ov = g[sipm][bar].GetX()[i]
            if (ov not in Vovs[sipm]): continue
            Npe[sipm][ov]  = LO[sipm]*4.2*PDE(ov,sipm)/PDE(3.5,sipm) #module type2
            if ('522' in sipm):                                                                                                                                       
                Npe[sipm][ov] = 3.75/3.00*LO[sipm]*4.2*PDE(ov,sipm)/PDE(3.5,sipm) # module of type1
            if ('524' in sipm):                                                                                                                                       
                Npe[sipm][ov] = 2.4/3.00*LO[sipm]*4.2*PDE(ov,sipm)/PDE(3.5,sipm) # module of type3
            gain = Gain(ov, sipm) 
            g_psL = fPS[sipm][ov].Get('g_pulseShapeL_bar%02d_Vov%.2f'%(bar,ov))
            g_psR = fPS[sipm][ov].Get('g_pulseShapeR_bar%02d_Vov%.2f'%(bar,ov))
            if (g_psL!=None): g_psL.SetName('g_pulseShapeL_bar%02d_Vov%.2f_%s'%(bar,ov,sipm))
            if (g_psR!=None): g_psR.SetName('g_pulseShapeR_bar%02d_Vov%.2f_%s'%(bar,ov,sipm))
            timingThreshold = findTimingThreshold(f.Get('g_deltaT_energyRatioCorr_vs_th_bar%02d_Vov%.2f_enBin01'%(bar,ov)))
            srL = -1
            srR = -1
            sr = -1
            err_srL = -1
            err_srR = -1
            c = ROOT.TCanvas('c_%s_%s'%(g_psL.GetName().replace('g_pulseShapeL','pulseShape'),sipm),'',600,600)  
            #hdummy = ROOT.TH2F('hdummy','', 100, min(g_psL.GetX())-1., 30., 100, 0., 15.)
            hdummy = ROOT.TH2F('hdummy','', 100, min(g_psL.GetX())-1., 5., 100, 0., 15.)
            hdummy.GetXaxis().SetTitle('time [ns]')
            hdummy.GetYaxis().SetTitle('amplitude [#muA]')
            hdummy.Draw()
            gtempL = ROOT.TGraphErrors()
            gtempR = ROOT.TGraphErrors()
            if (g_psL!=None): srL,err_srL = getSlewRateFromPulseShape(g_psL, timingThreshold, np, gtempL, c)
            if (g_psR!=None): srR,err_srR = getSlewRateFromPulseShape(g_psR, timingThreshold, np, gtempR, c) 
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
            #print ov, gain, Npe, srL, srR, sr, errSR
            g_SR_vs_Vov[sipm][bar].SetPoint( g_SR_vs_Vov[sipm][bar].GetN(), ov, sr )
            g_SR_vs_Vov[sipm][bar].SetPointError( g_SR_vs_Vov[sipm][bar].GetN()-1, 0, errSR )
            g_SR_vs_GainNpe[sipm][bar].SetPoint( g_SR_vs_GainNpe[sipm][bar].GetN(), gain*Npe[sipm][ov], sr )
            g_SR_vs_GainNpe[sipm][bar].SetPointError( g_SR_vs_GainNpe[sipm][bar].GetN()-1, 0, errSR )
            g_bestTh_vs_Vov[sipm][bar].SetPoint( g_bestTh_vs_Vov[sipm][bar].GetN(), ov, timingThreshold )
            g_bestTh_vs_Vov[sipm][bar].SetPointError( g_bestTh_vs_Vov[sipm][bar].GetN()-1, 0, 0 )
            g_SR_vs_bar[sipm][ov].SetPoint( g_SR_vs_bar[sipm][ov].GetN(), bar, sr )
            g_SR_vs_bar[sipm][ov].SetPointError( g_SR_vs_bar[sipm][ov].GetN()-1, 0, errSR )
            g_bestTh_vs_bar[sipm][ov].SetPoint( g_bestTh_vs_bar[sipm][ov].GetN(), bar, timingThreshold )
            g_bestTh_vs_bar[sipm][ov].SetPointError( g_bestTh_vs_bar[sipm][ov].GetN()-1, 0, 0)
            g_Noise_vs_bar[sipm][ov].SetPoint( g_Noise_vs_bar[sipm][ov].GetN(), bar, sigma_noise(sr) )
            g_Noise_vs_bar[sipm][ov].SetPointError( g_Noise_vs_bar[sipm][ov].GetN()-1, 0,  0.5*(sigma_noise(sr*(1-errSR/sr))-sigma_noise(sr*(1+errSR/sr))) )
            g_Noise_vs_Vov[sipm][bar].SetPoint(g_Noise_vs_Vov[sipm][bar].GetN(), ov, sigma_noise(sr))
            g_Noise_vs_Vov[sipm][bar].SetPointError(g_Noise_vs_Vov[sipm][bar].GetN()-1, 0, 0.5*(sigma_noise(sr*(1-errSR/sr))-sigma_noise(sr*(1+errSR/sr))))
            # compute s_stoch as diff in quadrature between measured tRes and noise term
            if ( sigma_meas > sigma_noise(sr) ):
                s = math.sqrt(sigma_meas*sigma_meas-sigma_noise(sr)*sigma_noise(sr))
                es = 1./s * math.sqrt( pow(sigma_meas*g[sipm][bar].GetErrorY(i),2) + pow( sigma_noise(sr)*g_Noise_vs_Vov[sipm][bar].GetErrorY(g_Noise_vs_Vov[sipm][bar].GetN()-1),2) )
                g_Stoch_vs_Npe[sipm][bar].SetPoint(g_Stoch_vs_Npe[sipm][bar].GetN(), Npe[sipm][ov], s)
                g_Stoch_vs_Npe[sipm][bar].SetPointError(g_Stoch_vs_Npe[sipm][bar].GetN()-1, 0., es )

            # compute stoch by scaling from 3.5 V OV
            sigma_stoch = sigma_stoch_ref/math.sqrt(  PDE(ov,sipm)/PDE(ov_ref,sipm)  )
            err_sigma_stoch = err_sigma_stoch_ref/math.sqrt( PDE(ov,sipm)/PDE(ov_ref,sipm) )
            g_Stoch_vs_Vov[sipm][bar].SetPoint(g_Stoch_vs_Vov[sipm][bar].GetN(), ov, sigma_stoch)
            g_Stoch_vs_Vov[sipm][bar].SetPointError(g_Stoch_vs_Vov[sipm][bar].GetN()-1, 0, err_sigma_stoch)
            g_Stoch_vs_bar[sipm][ov].SetPoint( g_Stoch_vs_bar[sipm][ov].GetN(), bar, sigma_stoch )
            g_Stoch_vs_bar[sipm][ov].SetPointError( g_Stoch_vs_bar[sipm][ov].GetN()-1, 0,  err_sigma_stoch)
            # tot resolution summing noise + stochastic in quadrature
            sigma_tot = math.sqrt( sigma_stoch*sigma_stoch + sigma_noise(sr)*sigma_noise(sr) )
            err_sigma_tot = 1./sigma_tot * math.sqrt( pow( err_sigma_stoch*sigma_stoch,2) + pow(sigma_noise(sr)*g_Noise_vs_Vov[sipm][bar].GetErrorY(g_Noise_vs_Vov[sipm][bar].GetN()-1),2))
            g_Tot_vs_Vov[sipm][bar].SetPoint(g_Tot_vs_Vov[sipm][bar].GetN(), ov, sigma_tot)
            g_Tot_vs_Vov[sipm][bar].SetPointError(g_Tot_vs_Vov[sipm][bar].GetN()-1, 0, err_sigma_tot)
            #print sipm,' OV = %.2f  gain = %d  Npe = %d  bar = %02d  thr = %02d  SR = %.1f   noise = %.1f    stoch = %.1f   tot = %.1f'%(ov, gain, Npe, bar, timingThreshold, sr, sigma_noise(sr), sigma_stoch, sigma_tot)

            # tRes vs SR
            g_Stoch_vs_SR[sipm][ov].SetPoint(g_Stoch_vs_SR[sipm][ov].GetN(), sr, sigma_stoch)
            g_Stoch_vs_SR[sipm][ov].SetPointError(g_Stoch_vs_SR[sipm][ov].GetN()-1, errSR, err_sigma_stoch)

            g_Tot_vs_SR[sipm][ov].SetPoint(g_Tot_vs_SR[sipm][ov].GetN(), sr, sigma_meas)
            g_Tot_vs_SR[sipm][ov].SetPointError(g_Tot_vs_SR[sipm][ov].GetN()-1, errSR, err_sigma_meas)


# average slew rate
g_SR_vs_Vov_average = {}                                                                                                                                                         
g_stoch_vs_NpeTau_average = ROOT.TGraphErrors()                                                

for sipm in sipmTypes:                             

    fitpol0_stoch = ROOT.TF1('fitpol0_stoch','pol0',-100,100)  
    g_Stoch_vs_bar[sipm][ov_ref].Fit(fitpol0_stoch,'QNR')
    print sipm, Npe[sipm][ov_ref]/tau[sipm], fitpol0_stoch.GetParameter(0)
    g_stoch_vs_NpeTau_average.SetPoint(g_stoch_vs_NpeTau_average.GetN(), Npe[sipm][ov_ref]/tau[sipm], fitpol0_stoch.GetParameter(0))
    g_stoch_vs_NpeTau_average.SetPointError(g_stoch_vs_NpeTau_average.GetN()-1, 0, fitpol0_stoch.GetParError(0))
    
    g_SR_vs_Vov_average[sipm] = ROOT.TGraphErrors()
    for ov in Vovs[sipm]:                                       
        if (ov in  g_SR_vs_bar[sipm].keys()):
            fitpol0_sr = ROOT.TF1('fitpol0_sr','pol0',-100,100)
            g_SR_vs_bar[sipm][ov].Fit(fitpol0_sr,'QNR')
            g_SR_vs_Vov_average[sipm].SetPoint(g_SR_vs_Vov_average[sipm].GetN(), ov, fitpol0_sr.GetParameter(0))
            g_SR_vs_Vov_average[sipm].SetPointError(g_SR_vs_Vov_average[sipm].GetN()-1, 0, fitpol0_sr.GetParError(0)) 


# ratio of stochatic terms at 3.5 OV
g_ratio_stoch1 = ROOT.TGraphErrors()
g_ratio_stoch2 = ROOT.TGraphErrors()
g_ratio_stoch3 = ROOT.TGraphErrors()
for bar in range(0,16):
    if (bar not in bars[sipmTypes[1]]): continue
    if (bar not in bars[sipmTypes[0]]): continue
    if (g_Stoch_vs_Vov[sipmTypes[0]][bar].Eval(3.5)<=0): continue
    ratio_stoch =  g_Stoch_vs_Vov[sipmTypes[1]][bar].Eval(3.5)/g_Stoch_vs_Vov[sipmTypes[0]][bar].Eval(3.5)
    err1 = [  g_Stoch_vs_Vov[sipmTypes[1]][bar].GetErrorY(i) for i in range(0, g_Stoch_vs_Vov[sipmTypes[1]][bar].GetN()) if g_Stoch_vs_Vov[sipmTypes[1]][bar].GetX()[i] == 3.50]
    err0 = [  g_Stoch_vs_Vov[sipmTypes[0]][bar].GetErrorY(i) for i in range(0, g_Stoch_vs_Vov[sipmTypes[0]][bar].GetN()) if g_Stoch_vs_Vov[sipmTypes[0]][bar].GetX()[i] == 3.50]
    if (err1 == [] or err0 == []): continue
    err_ratio_stoch = ratio_stoch * math.sqrt( pow(err1[0]/g_Stoch_vs_Vov[sipmTypes[1]][bar].Eval(3.5),2) + pow(err0[0]/g_Stoch_vs_Vov[sipmTypes[0]][bar].Eval(3.5),2) ) 
    print sipmTypes[1], sipmTypes[0], ' ratio stochastic term at 3.5 V OV = ', ratio_stoch
    g_ratio_stoch1.SetPoint(g_ratio_stoch1.GetN(), bar, ratio_stoch)
    g_ratio_stoch1.SetPointError(g_ratio_stoch1.GetN()-1, 0, err_ratio_stoch)

if (len(sipmTypes)>2):

    for bar in range(0,16):
        if (bar not in bars[sipmTypes[1]]): continue
        if ( len(sipmTypes)>2 and bar not in bars[sipmTypes[2]]): continue
        if ( len(sipmTypes)>2 and g_Stoch_vs_Vov[sipmTypes[2]][bar].Eval(3.5)<=0): continue
        if (g_Stoch_vs_Vov[sipmTypes[1]][bar].Eval(3.5)<=0): continue
        ratio_stoch =  g_Stoch_vs_Vov[sipmTypes[1]][bar].Eval(3.5)/g_Stoch_vs_Vov[sipmTypes[2]][bar].Eval(3.5)
        err1 = [  g_Stoch_vs_Vov[sipmTypes[1]][bar].GetErrorY(i) for i in range(0, g_Stoch_vs_Vov[sipmTypes[1]][bar].GetN()) if g_Stoch_vs_Vov[sipmTypes[1]][bar].GetX()[i] == 3.50]
        err0 = [  g_Stoch_vs_Vov[sipmTypes[2]][bar].GetErrorY(i) for i in range(0, g_Stoch_vs_Vov[sipmTypes[2]][bar].GetN()) if g_Stoch_vs_Vov[sipmTypes[2]][bar].GetX()[i] == 3.50]
        if (err1 == [] or err0 == []): continue
        err_ratio_stoch = ratio_stoch * math.sqrt( pow(err1[0]/g_Stoch_vs_Vov[sipmTypes[1]][bar].Eval(3.5),2) + pow(err0[0]/g_Stoch_vs_Vov[sipmTypes[2]][bar].Eval(3.5),2) ) 
        print sipmTypes[1], sipmTypes[2],' ratio stochastic term at 3.5 V OV = ', ratio_stoch
        g_ratio_stoch2.SetPoint(g_ratio_stoch2.GetN(), bar, ratio_stoch)
        g_ratio_stoch2.SetPointError(g_ratio_stoch2.GetN()-1, 0, err_ratio_stoch)


    for bar in range(0,16):
        if (bar not in bars[sipmTypes[0]]): continue
        if (bar not in bars[sipmTypes[2]]): continue
        if (g_Stoch_vs_Vov[sipmTypes[2]][bar].Eval(3.5)<=0): continue
        if (g_Stoch_vs_Vov[sipmTypes[0]][bar].Eval(3.5)<=0): continue
        ratio_stoch =  g_Stoch_vs_Vov[sipmTypes[0]][bar].Eval(3.5)/g_Stoch_vs_Vov[sipmTypes[2]][bar].Eval(3.5)
        err1 = [  g_Stoch_vs_Vov[sipmTypes[0]][bar].GetErrorY(i) for i in range(0, g_Stoch_vs_Vov[sipmTypes[0]][bar].GetN()) if g_Stoch_vs_Vov[sipmTypes[0]][bar].GetX()[i] == 3.50]
        err0 = [  g_Stoch_vs_Vov[sipmTypes[2]][bar].GetErrorY(i) for i in range(0, g_Stoch_vs_Vov[sipmTypes[2]][bar].GetN()) if g_Stoch_vs_Vov[sipmTypes[2]][bar].GetX()[i] == 3.50]
        if (err1 == [] or err0 == []): continue
        err_ratio_stoch = ratio_stoch * math.sqrt( pow(err1[0]/g_Stoch_vs_Vov[sipmTypes[0]][bar].Eval(3.5),2) + pow(err0[0]/g_Stoch_vs_Vov[sipmTypes[2]][bar].Eval(3.5),2) ) 
        print sipmTypes[0], sipmTypes[2],' ratio stochastic term at 3.5 V OV = ', ratio_stoch
        g_ratio_stoch3.SetPoint(g_ratio_stoch3.GetN(), bar, ratio_stoch)
        g_ratio_stoch3.SetPointError(g_ratio_stoch3.GetN()-1, 0, err_ratio_stoch)
        
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
for sipm in sipmTypes:
    c1[sipm] = {}
    hdummy1[sipm] = {}
    c2[sipm] = {}
    hdummy2[sipm] = {}
    h[sipm] = ROOT.TH1F('h_coeff_%s'%sipm,'',100,-2.0,1.0)
    leg[sipm] = ROOT.TLegend(0.60,0.70,0.85,0.89) 
    leg[sipm].SetBorderSize(0)
    leg[sipm].SetFillStyle(0) 
    for i,bar in enumerate(bars[sipm]):
        c1[sipm][bar] =  ROOT.TCanvas('c_timeResolution_vs_Vov_%s_bar%02d'%(sipm,bar),'c_timeResolution_vs_Vov_%s_bar%02d'%(sipm,bar),600,600)
        c1[sipm][bar].SetGridy()
        c1[sipm][bar].cd()
        hdummy1[sipm][bar] = ROOT.TH2F('hdummy1_%s_%d'%(sipm,bar),'',100,0,8,100,0,100)
        hdummy1[sipm][bar].GetXaxis().SetTitle('V_{OV} [V]')
        hdummy1[sipm][bar].GetYaxis().SetTitle('#sigma_{t} [ps]')
        hdummy1[sipm][bar].Draw()
        g[sipm][bar].SetMarkerStyle(20)
        g[sipm][bar].SetMarkerSize(1)
        g[sipm][bar].SetMarkerColor(1)
        g[sipm][bar].SetLineColor(1)
        g[sipm][bar].SetLineWidth(2)
        g[sipm][bar].Draw('plsame')
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
        g_Tot_vs_Vov[sipm][bar].SetLineWidth(2)
        g_Tot_vs_Vov[sipm][bar].SetLineColor(ROOT.kRed+1)
        g_Tot_vs_Vov[sipm][bar].SetFillColor(ROOT.kRed+1)
        g_Tot_vs_Vov[sipm][bar].SetFillColorAlpha(ROOT.kRed+1,0.5)
        g_Tot_vs_Vov[sipm][bar].SetFillStyle(3001)
        g_Tot_vs_Vov[sipm][bar].Draw('E3lsame')
        #save on file
        outfile.cd()
        g[sipm][bar].Write('g_Data_vs_Vov_%s_bar%02d'%(sipm,bar))
        g_Noise_vs_Vov[sipm][bar].Write('g_Noise_vs_Vov_%s_bar%02d'%(sipm,bar))
        g_Stoch_vs_Vov[sipm][bar].Write('g_Stoch_vs_Vov_%s_bar%02d'%(sipm,bar))
        g_Tot_vs_Vov[sipm][bar].Write('g_Tot_vs_Vov_%s_bar%02d'%(sipm,bar))
        if (i==0):
            leg[sipm].AddEntry(g[sipm][bar], 'data', 'PL')
            leg[sipm].AddEntry(g_Noise_vs_Vov[sipm][bar], 'noise', 'L')
            leg[sipm].AddEntry(g_Stoch_vs_Vov[sipm][bar], 'stoch', 'L')
            leg[sipm].AddEntry(g_Tot_vs_Vov[sipm][bar], 'stoch #oplus noise', 'L')
        leg[sipm].Draw('same')
        latex = ROOT.TLatex(0.20,0.86,'%s'%(sipm.replace('_nonIrr_','+')))
        latex.SetNDC()
        latex.SetTextSize(0.045)
        latex.SetTextFont(42)
        latex.Draw('same')
        c1[sipm][bar].SaveAs(outdir+'/'+c1[sipm][bar].GetName()+'.png')
        c1[sipm][bar].SaveAs(outdir+'/'+c1[sipm][bar].GetName()+'.pdf')

        # vs npe
        c2[sipm][bar] =  ROOT.TCanvas('c_timeResolution_vs_Npe_%s_bar%02d'%(sipm,bar),'c_timeResolution_vs_Npe_%s_bar%02d'%(sipm,bar),600,600)
        c2[sipm][bar].SetGridy()
        c2[sipm][bar].cd()
        hdummy2[sipm][bar] = ROOT.TH2F('hdummy2_%s_%d'%(sipm,bar),'',10000,1000,10000,100,0,100)
        hdummy2[sipm][bar].GetXaxis().SetTitle('Npe')
        hdummy2[sipm][bar].GetYaxis().SetTitle('#sigma_{t} [ps]')
        hdummy2[sipm][bar].Draw()
        g_Stoch_vs_Npe[sipm][bar].SetMarkerStyle(20)
        g_Stoch_vs_Npe[sipm][bar].SetMarkerSize(0.8)
        g_Stoch_vs_Npe[sipm][bar].SetMarkerColor(ROOT.kGreen+2)
        g_Stoch_vs_Npe[sipm][bar].SetLineWidth(1)
        g_Stoch_vs_Npe[sipm][bar].SetLineColor(ROOT.kGreen+2)
        g_Stoch_vs_Npe[sipm][bar].Draw('psame')
        fitFun = ROOT.TF1('fitFun_%s_%.2d'%(sipm,bar),'[0]*pow(x,[1])',2000,9500)
        fitFun.SetParameters(30,-0.5)
        fitFun.SetLineColor(ROOT.kGreen+3)
        g_Stoch_vs_Npe[sipm][bar].Fit(fitFun,'QRS+')
        if (fitFun.GetNDF()>0): h[sipm].Fill(fitFun.GetParameter(1))
        c2[sipm][bar].SaveAs(outdir+'/'+c2[sipm][bar].GetName()+'.png')
        c2[sipm][bar].SaveAs(outdir+'/'+c2[sipm][bar].GetName()+'.pdf')

    ROOT.gStyle.SetOptStat(1111)
    cc =  ROOT.TCanvas('c_coeff_%s'%(sipm),'c_coeff_%s'%(sipm),600,600)
    h[sipm].GetXaxis().SetTitle('#alpha')
    h[sipm].Draw('')
    cc.SaveAs(outdir+'/'+cc.GetName()+'.png')
    ROOT.gStyle.SetOptStat(0)


# total time resolution vs SR
for sipm in sipmTypes:
    for ov in Vovs[sipm]:
        if (ov not in g_Tot_vs_SR[sipm].keys()): continue
        c =  ROOT.TCanvas('c_timeResolution_vs_SR_%s_Vov%.02f'%(sipm,ov),'c_timeResolution_vs_SR_%s_Vov%.02f'%(sipm,ov),600,600)
        c.SetGridy()
        c.cd()
        xmin = 0.
        xmax = g_Tot_vs_SR[sipm][ov].GetMean() + 5.
        ymin = g_Tot_vs_SR[sipm][ov].GetMean(2)-20.
        ymax = g_Tot_vs_SR[sipm][ov].GetMean(2)+20.
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


# SR and best threshold vs Vov
print 'Plotting slew rate vs Vov...'

markers = { 'HPK_nonIrr_LYSO528' : 20 ,
            'FBK_nonIrr_LYSO800' : 24 ,
            'FBK_nonIrr_LYSO522' : 24 ,
            'FBK_nonIrr_LYSO524' : 24 ,
            'HPK_nonIrr_LYSO528_2X' : 20 ,
            'HPK_nonIrr_LYSO528_2B' : 25 ,
}

cols = { 'HPK_nonIrr_LYSO528' : ROOT.kBlack ,
         'FBK_nonIrr_LYSO800' : ROOT.kBlue ,
         'FBK_nonIrr_LYSO522' : ROOT.kRed  , 
         'FBK_nonIrr_LYSO524' : ROOT.kMagenta,
         'HPK_nonIrr_LYSO528_2X' : ROOT.kBlack ,
         'HPK_nonIrr_LYSO528_2B' : ROOT.kBlack ,
}

leg2 = ROOT.TLegend(0.20,0.70,0.45,0.89)
leg2.SetBorderSize(0)
leg2.SetFillStyle(0)
for i,bar in enumerate(bars[sipm]):
    c3[bar] = ROOT.TCanvas('c_slewRate_vs_Vov_bar%02d'%(bar),'c_slewRate_vs_Vov_bar%02d'%(bar),600,600)
    c3[bar].SetGridy()
    c3[bar].cd()
    hdummy3[bar] = ROOT.TH2F('hdummy3_%d'%(bar),'',100,0,8,100,0,35)
    hdummy3[bar].GetXaxis().SetTitle('V_{OV} [V]')
    hdummy3[bar].GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
    hdummy3[bar].Draw()
    for j,sipm in enumerate(sipmTypes):
        if (i==0):
            leg2.AddEntry(g_SR_vs_Vov[sipm][bar], '%s'%sipm, 'PL')
        if (bar not in g_SR_vs_Vov[sipm].keys()):continue
        g_SR_vs_Vov[sipm][bar].SetMarkerStyle( markers[sipm] )
        g_SR_vs_Vov[sipm][bar].SetMarkerColor(cols[sipm])
        g_SR_vs_Vov[sipm][bar].SetLineColor(cols[sipm])
        g_SR_vs_Vov[sipm][bar].Draw('psame')
    outfile.cd()
    g_SR_vs_Vov[sipm][bar].Write('g_SR_vs_Vov_%s_bar%02d'%(sipm,bar))
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
    hdummy4[bar] = ROOT.TH2F('hdummy4_%d'%(bar),'',100,0,8,100,0,20)
    hdummy4[bar].GetXaxis().SetTitle('V_{OV} [V]')
    hdummy4[bar].GetYaxis().SetTitle('best threshold [DAC]')
    hdummy4[bar].Draw()
    for j,sipm in enumerate(sipmTypes):
        if (bar not in g_bestTh_vs_Vov[sipm].keys()):continue
        g_bestTh_vs_Vov[sipm][bar].SetMarkerStyle( markers[sipm] )
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
#hdummy2 = ROOT.TH2F('hdummy2','',16, 0.5, 2.5,100,0,15)
hdummy2 = ROOT.TH2F('hdummy2','',100, 0.5, 7.5,100,0,35)
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



# average stoch. term vs Npe/tau
c2 =  ROOT.TCanvas('c_stoch_vs_NpeTau_average','c_stoch_vs_NpeTau_average',600,600)
c2.SetGridx()
c2.SetGridy()
c2.cd()    
hdummy2 = ROOT.TH2F('hdummy2','',100, 40, 200, 100, 20, 60)
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
c2.SaveAs(outdir+'/'+c2.GetName()+'.png')
c2.SaveAs(outdir+'/'+c2.GetName()+'.pdf')
hdummy2.Delete()


    
# SR and best threshold vs bar
print 'Plotting slew rate vs bar...'
c5 = {}
hdummy5 = {}
c6 = {}
hdummy6 = {}
c7 = {}
hdummy7 = {}
c8 = {}
hdummy8 = {}
for ov in Vovs[sipm]:
    c5[ov] = ROOT.TCanvas('c_slewRate_vs_bar_Vov%.2f'%(ov),'c_slewRate_vs_bar_Vov%.2f'%(ov),600,600)
    c5[ov].SetGridy()
    c5[ov].cd()
    ymax = 35.
    if (ov == 1.50): ymax = 15.
    hdummy5[ov] = ROOT.TH2F('hdummy5_%s_%d'%(sipm,ov),'',100,-0.5,15.5,100,0,ymax)
    hdummy5[ov].GetXaxis().SetTitle('bar')
    hdummy5[ov].GetYaxis().SetTitle('slew rate at the timing thr. [#muA/ns]')
    hdummy5[ov].Draw()
    for j,sipm in enumerate(sipmTypes):
        if (ov not in g_SR_vs_bar[sipm].keys()): continue
        g_SR_vs_bar[sipm][ov].SetMarkerStyle( markers[sipm] )
        g_SR_vs_bar[sipm][ov].SetMarkerColor(cols[sipm])
        g_SR_vs_bar[sipm][ov].SetLineColor(cols[sipm])
        g_SR_vs_bar[sipm][ov].Draw('psame')
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
    hdummy6[ov] = ROOT.TH2F('hdummy6_%s_%d'%(sipm,ov),'',100,-0.5,15.5,100,0,20)
    hdummy6[ov].GetXaxis().SetTitle('bar')
    hdummy6[ov].GetYaxis().SetTitle('timing threshold [DAC]')
    hdummy6[ov].Draw()
    for j,sipm in enumerate(sipmTypes):
        if (ov not in g_bestTh_vs_bar[sipm].keys()): continue
        g_bestTh_vs_bar[sipm][ov].SetMarkerStyle( markers[sipm] )
        g_bestTh_vs_bar[sipm][ov].SetMarkerColor(cols[sipm])
        g_bestTh_vs_bar[sipm][ov].SetLineColor(cols[sipm])
        g_bestTh_vs_bar[sipm][ov].Draw('plsame')
    leg2.Draw()        
    c6[ov].SaveAs(outdir+'/'+c6[ov].GetName()+'.png')
    c6[ov].SaveAs(outdir+'/'+c6[ov].GetName()+'.pdf')
    hdummy6[ov].Delete() 

    c7[ov] = ROOT.TCanvas('c_noise_vs_bar_Vov%.2f'%(ov),'c_noise_vs_bar_Vov%.2f'%(ov),600,600)
    c7[ov].SetGridy()
    c7[ov].cd()
    hdummy7[ov] = ROOT.TH2F('hdummy7_%s_%d'%(sipm,ov),'',100,-0.5,15.5,100,0,80)
    hdummy7[ov].GetXaxis().SetTitle('bar')
    hdummy7[ov].GetYaxis().SetTitle('#sigma_{t, noise} [ps]')
    hdummy7[ov].Draw()
    for j,sipm in enumerate(sipmTypes):
        if (ov not in g_Noise_vs_bar[sipm].keys()): continue
        g_Noise_vs_bar[sipm][ov].SetMarkerStyle( markers[sipm] )
        g_Noise_vs_bar[sipm][ov].SetMarkerColor(cols[sipm])
        g_Noise_vs_bar[sipm][ov].SetLineColor(cols[sipm])
        g_Noise_vs_bar[sipm][ov].Draw('psame')
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
    hdummy8[ov] = ROOT.TH2F('hdummy8_%s_%d'%(sipm,ov),'',100,-0.5,15.5,100,0,80)
    hdummy8[ov].GetXaxis().SetTitle('bar')
    hdummy8[ov].GetYaxis().SetTitle('#sigma_{t, stoch} [ps]')
    hdummy8[ov].Draw()
    for j,sipm in enumerate(sipmTypes):
        if (ov not in g_Stoch_vs_bar[sipm].keys()): continue
        g_Stoch_vs_bar[sipm][ov].SetMarkerStyle( markers[sipm] )
        g_Stoch_vs_bar[sipm][ov].SetMarkerColor(cols[sipm])
        g_Stoch_vs_bar[sipm][ov].SetLineColor(cols[sipm])
        g_Stoch_vs_bar[sipm][ov].Draw('psame')
    leg2.Draw()        
    c8[ov].SaveAs(outdir+'/'+c8[ov].GetName()+'.png')
    c8[ov].SaveAs(outdir+'/'+c8[ov].GetName()+'.pdf')
    hdummy8[ov].Delete() 

# ratio of photo-stat. terms:
glist = [g_ratio_stoch1]
if (len(sipmTypes) > 2): 
    glist.append(g_ratio_stoch2)
    glist.append(g_ratio_stoch3)

for i,g in enumerate(glist):
    if i == 0:
        sipm1 = sipmTypes[1]
        sipm2 = sipmTypes[0]
    if i == 1:
        sipm1 = sipmTypes[1]
        sipm2 = sipmTypes[2]
    if i == 2:
        sipm1 = sipmTypes[0]
        sipm2 = sipmTypes[2]
    
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

for sipm in sipmTypes: 
    for ov in Vovs[sipm]:
            print sipm, ov, '  average stoch. term = ', g_Stoch_vs_bar[sipm][ov].GetMean(2),' ps' 
            print sipm, ov, '  average noise  term = ', g_Noise_vs_bar[sipm][ov].GetMean(2),' ps'
    

outfile.Close()    
raw_input('OK?')
