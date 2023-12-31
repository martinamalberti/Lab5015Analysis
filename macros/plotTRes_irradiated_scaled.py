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
from utils import *
from SiPM import *

#set the tdr style
tdrstyle.setTDRStyle()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(1)
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetLabelSize(0.055,'X')
ROOT.gStyle.SetLabelSize(0.055,'Y')
ROOT.gStyle.SetTitleSize(0.07,'X')
ROOT.gStyle.SetTitleSize(0.07,'Y')
ROOT.gStyle.SetTitleOffset(1.05,'X')
ROOT.gStyle.SetTitleOffset(1.1,'Y')
ROOT.gStyle.SetLegendFont(42)
ROOT.gStyle.SetLegendTextSize(0.045)
ROOT.gStyle.SetPadTopMargin(0.07)
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kWarning


outdir = '/eos/user/m/malberti/www/MTD/TOFHIR2C/plotsForPaper/'

fnames = { #30 : '/eos/user/m/malberti/www/MTD/TOFHIR2C/MTDTB_CERN_May23/timeResolution_2E14_20um_25um_T2/plots_timeResolution_2E14_20um_25um_T2_TBMay23_TOFHIR2C.root',
    30 : '/afs/cern.ch/work/m/malberti/MTD/TBatH8Sep2023/Lab5015Analysis/plots/TOFHIR2C/summaryPlots_HPK_2E14_LYSO200104_T-35C_angle52.root',
    25 : '/eos/user/m/malberti/www/MTD/TOFHIR2C/MTDTB_CERN_May23/timeResolution_2E14_20um_25um_T2/plots_timeResolution_2E14_20um_25um_T2_TBMay23_TOFHIR2C.root',
    20 : '/eos/user/m/malberti/www/MTD/TOFHIR2C/MTDTB_CERN_May23/timeResolution_2E14_20um_25um_T2/plots_timeResolution_2E14_20um_25um_T2_TBMay23_TOFHIR2C.root',
    15 : '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_Jun22/timeResolution_2E14_15um_T2/plots_timeResolution_2E14_15um_T2_TBJune22_TOFHIR2X.root',
}

gnames = { 30 : 'g_deltaT_energyRatioCorr_bestTh_vs_vov_enBin01_average',
           25 : 'g_data_vs_Vov_average_HPK_2E14_LYSO815_T-35C_TOFHIR2C',
           20 : 'g_data_vs_Vov_average_HPK_2E14_LYSO825_T-35C_TOFHIR2C',
           15 : 'g_data_vs_Vov_average_HPK_2E14_LYSO796_T-40C'  # less annealing for this module
    }

plotAttrs = { 30 : [23, ROOT.kOrange+1,  '30 #mum'],
              25 : [20, ROOT.kGreen+2,  '25 #mum'],
              20 : [21, ROOT.kBlue,     '20 #mum'],
              15 : [22, ROOT.kRed,      '15 #mum'],
}


g = {}
g_scaled = {}
f = {}

for cell in [15,20,25,30]:
    f[cell] = ROOT.TFile.Open(fnames[cell])
    g[cell] = f[cell].Get(gnames[cell])
    g_scaled[cell] = ROOT.TGraphErrors()
    
# scale 15 um 2X --> 2C
gNoise = f[15].Get('g_Noise_vs_Vov_average_HPK_2E14_LYSO796_T-40C')
gStoch = f[15].Get('g_Stoch_vs_Vov_average_HPK_2E14_LYSO796_T-40C')
gDCR   = f[15].Get('g_DCR_vs_Vov_average_HPK_2E14_LYSO796_T-40C')
gSR    = f[15].Get('g_SR_vs_Vov_average_HPK_2E14_LYSO796_T-40C')

for i in range(0, g[15].GetN()):
    vov = g[15].GetX()[i]
    sr = gSR.Eval(vov)
    s_noise_scaled = sigma_noise(sr*1.20, '2C')
    s_stoch = gStoch.Eval(vov)
    s_dcr = gDCR.Eval(vov)
    s_tot = math.sqrt(s_noise_scaled*s_noise_scaled + s_stoch*s_stoch + s_dcr*s_dcr)
    g_scaled[15].SetPoint(i, vov, s_tot)
    g_scaled[15].SetPointError(i, 0, g[15].GetErrorY(i))


# scale others
for cell in [30, 25, 20]:
    if (cell == 30 ):
        for i in range(0, g[cell].GetN()):
            g_scaled[cell].SetPoint(i, g[cell].GetX()[i], g[cell].GetY()[i]/1.06) # correct for angle offset 
            g_scaled[cell].SetPointError(i, 0, g[cell].GetErrorY(i)/1.06) # correct for angle offset
    else:
        g_scaled[cell] = g[cell]



# plot
        
leg = ROOT.TLegend(0.20, 0.60, 0.50, 0.89)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
leg.SetTextFont(42)
leg.SetTextSize(0.045) 

c = ROOT.TCanvas('c_timeResolution_HPK_2E14_vs_Vov','c_timeResolution_HPK_2E14_vs_Vov', 600, 500)
hPad = ROOT.gPad.DrawFrame(0.,40.,2.0,140.)
hPad.SetTitle(";V_{OV} [V];time resolution [ps]")
hPad.Draw()
ROOT.gPad.SetTicks(1)
for cell in [30, 25, 20, 15]:
    g_scaled[cell].SetMarkerSize(1)
    g_scaled[cell].SetMarkerStyle(plotAttrs[cell][0])
    g_scaled[cell].SetMarkerColor(plotAttrs[cell][1])
    g_scaled[cell].SetLineColor(plotAttrs[cell][1])
    leg.AddEntry(g_scaled[cell], '%s'%plotAttrs[cell][2],'PL')
    g_scaled[cell].Draw('plsame')
    #g[cell].SetMarkerSize(1)
    #g[cell].SetMarkerStyle(plotAttrs[cell][0]+4)
    #g[cell].SetMarkerColor(plotAttrs[cell][1])
    #g[cell].SetLineColor(plotAttrs[cell][1])
    #g[cell].SetLineStyle(2)
    g[cell].Draw('lsame')
leg.Draw()

tl2 = ROOT.TLatex()
tl2.SetNDC()
tl2.SetTextFont(42)
tl2.SetTextSize(0.045)

tl = ROOT.TLatex()
tl.SetNDC()
tl.SetTextFont(42)
tl.SetTextSize(0.045)
tl.DrawLatex(0.58,0.20,'2 #times 10^{14} 1 MeV n_{eq}/cm^{2}')

cms_logo = draw_logo()
cms_logo.Draw()

c.SaveAs(outdir+'%s.png'%c.GetName())
c.SaveAs(outdir+'%s.pdf'%c.GetName())




