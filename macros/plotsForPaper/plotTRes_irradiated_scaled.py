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

sipmProd = 'HPK'
#sipmProd = 'FBK'

enScale = math.cos(52.*math.pi/180)/math.cos(55.*math.pi/180) # for 3 deg angle offset in Sep2023 TB
srScale = 1.20 # scaling SR from TOPFHIR2X to 2C

fnames = {}
gnames = {}
labels = {}

if sipmProd == 'HPK':

    cells = [15, 20, 25, 30]

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

else:

    cells = [15]
             
    fnames = { 15 : '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_Jun22/timeResolution_2E14_15um_T2/plots_timeResolution_2E14_15um_T2_TBJune22_TOFHIR2X.root',
              }

    gnames = { 15 : 'g_data_vs_Vov_average_FBK_2E14_LYSO797_T-40C'  # less annealing for this module
              }
    
    labels = { 15 : 'FBK_2E14_LYSO797_T-40C',
              }




              
plotAttrs = { 30 : [23, ROOT.kOrange+1, '30 #mum'],
              25 : [20, ROOT.kGreen+2,  '25 #mum'],
              20 : [21, ROOT.kBlue,     '20 #mum'],
              15 : [22, ROOT.kRed,      '15 #mum']}


g = {}
g_scaled = {}
gNoise = {}
gStoch = {}
gDCR = {}
gSR = {}
f = {}

for cell in cells:
    f[cell] = ROOT.TFile.Open(fnames[cell])
    g[cell] = f[cell].Get(gnames[cell])
    g_scaled[cell] = ROOT.TGraphErrors()
    
# scale 15 um 2X --> 2C
gNoise[15] = f[15].Get('g_Noise_vs_Vov_average_%s'%labels[15])
gStoch[15] = f[15].Get('g_Stoch_vs_Vov_average_%s'%labels[15])
gDCR[15]   = f[15].Get('g_DCR_vs_Vov_average_%s'%labels[15])
gSR[15]    = f[15].Get('g_SR_vs_Vov_average_%s'%labels[15])

print()

for i in range(0, g[15].GetN()):
    vov = g[15].GetX()[i]
    sr = gSR[15].Eval(vov)
    s_noise_scaled = sigma_noise(sr*srScale, '2C')
    s_stoch = gStoch[15].Eval(vov)
    s_dcr = gDCR[15].Eval(vov)
    s_tot = math.sqrt(s_noise_scaled*s_noise_scaled + s_stoch*s_stoch + s_dcr*s_dcr)
    g_scaled[15].SetPoint(i, vov, s_tot)
    g_scaled[15].SetPointError(i, 0, g[15].GetErrorY(i))


# scale others (2C) to take into account angle offset in 2023 Sep TB 
for cell in [20, 25, 30]:
    if (cell not in fnames.keys()): continue
    gNoise[cell] = f[cell].Get('g_Noise_vs_Vov_average_%s'%labels[cell])
    gStoch[cell] = f[cell].Get('g_Stoch_vs_Vov_average_%s'%labels[cell])
    gDCR[cell]   = f[cell].Get('g_DCR_vs_Vov_average_%s'%labels[cell])
    for i in range(0, g[cell].GetN()):
        vov = g[cell].GetX()[i]
        s_noise = gNoise[cell].Eval(vov)/enScale
        s_stoch = gStoch[cell].Eval(vov)/math.sqrt(enScale)
        s_dcr = gDCR[cell].Eval(vov)/enScale
        s_tot = math.sqrt(s_noise*s_noise + s_stoch*s_stoch + s_dcr*s_dcr)
        #print(cell, vov, gNoise[cell].Eval(vov), s_noise)
        #print(cell, vov, gStoch[cell].Eval(vov), s_stoch)
        #print(cell, vov, gDCR[cell].Eval(vov), s_dcr)
        #print(cell, vov, g[cell].GetY()[i], s_tot)
        g_scaled[cell].SetPoint(i, vov, s_tot) # correct for angle offset 
        g_scaled[cell].SetPointError(i, 0, g[cell].GetErrorY(i)/enScale) # correct for angle offset
        


# plot
        
leg = ROOT.TLegend(0.20, 0.60, 0.50, 0.89)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
leg.SetTextFont(42)
leg.SetTextSize(0.045) 

c = ROOT.TCanvas('c_timeResolution_%s_2E14_vs_Vov'%sipmProd,'c_timeResolution_%s_2E14_vs_Vov'%sipmProd, 600, 500)
hPad = ROOT.gPad.DrawFrame(0.,40.,2.0,140.)
if (sipmProd == 'FBK'): hPad = ROOT.gPad.DrawFrame(0.5,40.,2.5,140.)
hPad.SetTitle(";V_{OV} [V];time resolution [ps]")
hPad.Draw()
ROOT.gPad.SetTicks(1)
for cell in cells:
    g_scaled[cell].SetMarkerSize(1)
    if (plotAttrs[cell][0] == 22 or plotAttrs[cell][0] == 23): g_scaled[cell].SetMarkerSize(1.15)
    g_scaled[cell].SetMarkerStyle(plotAttrs[cell][0])
    g_scaled[cell].SetMarkerColor(plotAttrs[cell][1])
    g_scaled[cell].SetLineColor(plotAttrs[cell][1])
    leg.AddEntry(g_scaled[cell], '%s'%plotAttrs[cell][2],'PL')
    g_scaled[cell].Draw('plsame')
    g[cell].SetMarkerSize(0.1)
    #g[cell].SetMarkerStyle(plotAttrs[cell][0]+4)
    #g[cell].SetMarkerColor(plotAttrs[cell][1])
    g[cell].SetLineColor(plotAttrs[cell][1])
    g[cell].SetLineStyle(2)
    #g[cell].Draw('lsame')
leg.Draw()

tl2 = ROOT.TLatex()
tl2.SetNDC()
tl2.SetTextFont(42)
tl2.SetTextSize(0.045)
tl2.DrawLatex(0.20,0.20,'%s'%sipmProd)

tl = ROOT.TLatex()
tl.SetNDC()
tl.SetTextFont(42)
tl.SetTextSize(0.045)
tl.DrawLatex(0.58,0.20,'2 #times 10^{14} 1 MeV n_{eq}/cm^{2}')

cms_logo = draw_logo()
cms_logo.Draw()

c.SaveAs(outdir+'%s.png'%c.GetName())
c.SaveAs(outdir+'%s.pdf'%c.GetName())




