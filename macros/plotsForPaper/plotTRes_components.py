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

#irr = 'nonIrr'
irr = '2E14'

fnames = {}
gnames = {}
labels = {}

cells = [15, 25]

if (irr == '2E14'):
    fnames = { 30 : '/eos/user/m/malberti/www/MTD/TOFHIR2C/MTDTB_CERN_Sep23/timeResolution_2E14_20um_25um_30um_T2/plots_timeResolution_2E14_20um_25um_30um_T2_TBSep23_TOFHIR2C.root',
               25 : '/eos/user/m/malberti/www/MTD/TOFHIR2C/MTDTB_CERN_Sep23/timeResolution_2E14_20um_25um_30um_T2/plots_timeResolution_2E14_20um_25um_30um_T2_TBSep23_TOFHIR2C.root',
               20 : '/eos/user/m/malberti/www/MTD/TOFHIR2C/MTDTB_CERN_Sep23/timeResolution_2E14_20um_25um_30um_T2/plots_timeResolution_2E14_20um_25um_30um_T2_TBSep23_TOFHIR2C.root',
               15 : '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_Jun22/timeResolution_2E14_15um_T2/plots_timeResolution_2E14_15um_T2_TBJune22_TOFHIR2X.root'}

    gnames = { 30 : 'g_data_vs_Vov_average_HPK_2E14_LYSO200104_T-35C_TOFHIR2C',
               25 : 'g_data_vs_Vov_average_HPK_2E14_LYSO815_T-35C_TOFHIR2C',
               20 : 'g_data_vs_Vov_average_HPK_2E14_LYSO825_T-35C_TOFHIR2C',
               15 : 'g_data_vs_Vov_average_HPK_2E14_LYSO796_T-40C'  # less annealing for this module
              }

    labels = { 30 : 'HPK_2E14_LYSO200104_T-35C_TOFHIR2C',
               25 : 'HPK_2E14_LYSO815_T-35C_TOFHIR2C',
               20 : 'HPK_2E14_LYSO825_T-35C_TOFHIR2C',
               15 : 'HPK_2E14_LYSO796_T-40C'
              }
              
    plotAttrs = { 30 : [23, ROOT.kOrange+1, '30 #mum'],
                  25 : [20, ROOT.kGreen+2,  '25 #mum'],
                  20 : [21, ROOT.kBlue,     '20 #mum'],
                  15 : [22, ROOT.kRed,      '15 #mum']}

else: # non irr from Simona
    fnames = { }

    gnames = { }

    labels = { } 


gData = {}
gNoise = {}
gStoch = {}
gDCR = {}
gSR = {}

gData_scaled = {}
gNoise_scaled = {}
gStoch_scaled = {}
gDCR_scaled = {}

f = {}

for cell in cells:
    f[cell] = ROOT.TFile.Open(fnames[cell])
    gData[cell] = f[cell].Get(gnames[cell])
    gData_scaled[cell] = ROOT.TGraphErrors()
    gNoise_scaled[cell] = ROOT.TGraphErrors()
    gStoch_scaled[cell] = ROOT.TGraphErrors()
    gDCR_scaled[cell] = ROOT.TGraphErrors()
    gData_scaled[cell].SetName(gnames[cell].replace('g_data','g_data_scaled'))
    gNoise_scaled[cell].SetName(gnames[cell].replace('g_Noise','g_Noise_scaled'))
    gStoch_scaled[cell].SetName(gnames[cell].replace('g_Stoch','g_Stoch_scaled'))
    gDCR_scaled[cell].SetName(gnames[cell].replace('g_DCR','g_DCR_scaled'))
    
# scale contributions to take into account angle offset in 2023 Sep TB 
for cell in cells:
    if (cell not in fnames.keys()): continue
    gNoise[cell] = f[cell].Get('g_Noise_vs_Vov_average_%s'%labels[cell])
    gStoch[cell] = f[cell].Get('g_Stoch_vs_Vov_average_%s'%labels[cell])
    gDCR[cell]   = f[cell].Get('g_DCR_vs_Vov_average_%s'%labels[cell])
    gSR[cell]   = f[cell].Get('g_SR_vs_Vov_average_%s'%labels[cell])
    # if 15 um from June22 TB non need to scale for angle offset.
    enScale = math.cos(49.*math.pi/180.)/math.cos(52.*math.pi/180.) # for 3 deg angle offset in Sep2023 TB
    if ('TBJun22' in fnames[cell] ): enScale = 1.
    for i in range(0, gData[cell].GetN()):
        vov = gData[cell].GetX()[i]
        sr = gSR[cell].Eval(vov)
        s_noise =  sigma_noise(sr*enScale, '2C')
        s_stoch = gStoch[cell].Eval(vov)/math.sqrt(enScale)
        s_dcr = 0.
        if (irr == '2E14'): s_dcr = gDCR[cell].Eval(vov)/enScale
        s_tot = math.sqrt(s_noise*s_noise + s_stoch*s_stoch + s_dcr*s_dcr)
        gData_scaled[cell].SetPoint(i, vov, s_tot) 
        gData_scaled[cell].SetPointError(i, 0, gData[cell].GetErrorY(i)/enScale) 
        gNoise_scaled[cell].SetPoint(i, vov, s_noise)  
        gNoise_scaled[cell].SetPointError(i, 0, gNoise[cell].GetErrorY(i)/enScale) 
        gStoch_scaled[cell].SetPoint(i, vov, s_stoch)  
        gStoch_scaled[cell].SetPointError(i, 0, gStoch[cell].GetErrorY(i)/math.sqrt(enScale)) 
        gDCR_scaled[cell].SetPoint(i, vov, s_dcr)  
        gDCR_scaled[cell].SetPointError(i, 0, gDCR[cell].GetErrorY(i)/enScale) 


# plot        
for cell in cells:
    c = ROOT.TCanvas('c_timeResolution_components_%dum_%s_vs_Vov'%(cell, irr), 'c_timeResolution_components_%dum_%s_vs_Vov'%(cell, irr), 600, 500)
    hPad = ROOT.gPad.DrawFrame(0., 0., 4.0, 120.)
    #if (irr == '2E14'): hPad = ROOT.gPad.DrawFrame(0., 0., 2., 160.)
    if (irr == '2E14'): hPad = ROOT.gPad.DrawFrame(gData_scaled[cell].GetX()[0] - 0.2, 0., gData_scaled[cell].GetX()[0] + 1.2, 160.)
    hPad.SetTitle(";V_{OV} [V];time resolution [ps]")
    hPad.Draw()
    ROOT.gPad.SetTicks(1)
    
    gData_scaled[cell].SetMarkerStyle(20)
    gData_scaled[cell].SetMarkerSize(1)
    gData_scaled[cell].SetMarkerColor(1)
    gData_scaled[cell].SetLineColor(1)
    gData_scaled[cell].SetLineWidth(2)
    gData_scaled[cell].Draw('plsame')
    gNoise_scaled[cell].SetLineWidth(2)
    gNoise_scaled[cell].SetLineColor(ROOT.kBlue)
    gNoise_scaled[cell].SetFillColor(ROOT.kBlue)
    #gNoise_scaled[cell].SetFillColorAlpha(ROOT.kBlue,0.5)
    gNoise_scaled[cell].SetFillStyle(3004)
    gNoise_scaled[cell].Draw('E3lsame')
    gStoch_scaled[cell].SetLineWidth(2)
    gStoch_scaled[cell].SetLineColor(ROOT.kGreen+2)
    gStoch_scaled[cell].SetFillColor(ROOT.kGreen+2)
    gStoch_scaled[cell].SetFillStyle(3001)
    gStoch_scaled[cell].SetFillColorAlpha(ROOT.kGreen+2,0.5)
    gStoch_scaled[cell].Draw('E3lsame')
    if (irr == '2E14'):
        gDCR_scaled[cell].SetLineWidth(2)
        gDCR_scaled[cell].SetLineColor(ROOT.kOrange+2)
        gDCR_scaled[cell].SetFillColor(ROOT.kOrange+2)
        gDCR_scaled[cell].SetFillStyle(3005)
        #gDCR_scaled[cell].SetFillColorAlpha(ROOT.kOrange+2,0.5)
        gDCR_scaled[cell].Draw('E3lsame')

    leg = ROOT.TLegend(0.70, 0.60, 0.89, 0.89)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.050)
    leg.AddEntry(gData_scaled[cell], 'data', 'PL')
    leg.AddEntry(gNoise_scaled[cell], 'noise', 'FL')
    leg.AddEntry(gStoch_scaled[cell], 'stochastic', 'FL')    
    if (irr == '2E14'):
        leg.AddEntry(gDCR_scaled[cell], 'DCR', 'FL')    
    leg.Draw()
    
    tl = ROOT.TLatex()
    tl.SetNDC()
    tl.SetTextFont(42)
    tl.SetTextSize(0.050)
    tl.DrawLatex(0.20,0.86,'HPK, %d #mum'%cell)

    tl3 = ROOT.TLatex()
    tl3.SetNDC()
    tl3.SetTextFont(42)
    tl3.SetTextSize(0.050)
    if (irr == '2E14'): tl3.DrawLatex(0.20,0.80,'2 #times 10^{14} 1 MeV n_{eq}/cm^{2}')

    cms_logo = draw_logo()
    cms_logo.Draw()
        
    c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2C/plotsForPaper/%s.png'%c.GetName())
    c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2C/plotsForPaper/%s.pdf'%c.GetName())
    c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2C/plotsForPaper/%s.C'%c.GetName())

    
