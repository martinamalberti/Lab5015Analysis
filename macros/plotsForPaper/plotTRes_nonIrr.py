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

#sipmProd = 'HPK'
sipmProd = 'FBK'

fnames = {}
gnames = {}
labels = {}

#cells = [15, 20, 25, 30]
cells = [15]

if (sipmProd == 'HPK'):  # USE FILES FROM SIMONA
    fnames = { 30 : '',
               25 : '',
               20 : '',
               15 : ''}

    gnames = { 30 : 'g_data_vs_Vov_average_HPK_',
               25 : 'g_data_vs_Vov_average_HPK_',
               20 : 'g_data_vs_Vov_average_HPK_',
               15 : 'g_data_vs_Vov_average_HPK_',
              }

    labels = { 30 : '',
               25 : '',
               20 : '',
               15 : '',
              }

else: # FILES FROM JIN WANG (20,25,30) and MARTINA (15 un June22 TB)
    fnames = { 30 : '',
               25 : '',
               20 : '',
               15 : '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_Jun22/timeResolution_nonIrr/plots_timeResolution_HPK_FBK_nonIrr_TBJun22_TOFHIR2X.root'}

    gnames = { 30 : '',
               25 : '',
               20 : '',
               15 : 'g_data_vs_Vov_average_FBK_nonIrr_LYSO800_T10C',
              }

    labels = { 30 : '',
               25 : '',
               20 : '',
               15 : 'FBK_nonIrr_LYSO800_T10C',
              }
    
    


              
plotAttrs = { 30 : [23, ROOT.kOrange+1, '30 #mum'],
              25 : [20, ROOT.kGreen+2,  '25 #mum'],
              20 : [21, ROOT.kBlue,     '20 #mum'],
              15 : [22, ROOT.kRed,      '15 #mum']}



g = {}
g_scaled = {}
g_Noise = {}
g_Stoch = {}
g_DCR = {}
g_SR = {}
f = {}

for cell in cells:
    f[cell] = ROOT.TFile.Open(fnames[cell])
    g[cell] = f[cell].Get(gnames[cell])
    g_scaled[cell] = ROOT.TGraphErrors()
    print(gnames[cell].replace('g_data','g_data_scaled'))
    g_scaled[cell].SetName(gnames[cell].replace('g_data','g_data_scaled'))

# scale (2C) to take into account angle offset in 2023 Sep TB 
for cell in [20, 25, 30]:
    if (cell not in cells): continue
    gNoise[cell] = f[cell].Get('g_Noise_vs_Vov_average_%s'%labels[cell])
    gStoch[cell] = f[cell].Get('g_Stoch_vs_Vov_average_%s'%labels[cell])
    gDCR[cell]   = f[cell].Get('g_DCR_vs_Vov_average_%s'%labels[cell])
    gSR[cell]   = f[cell].Get('g_SR_vs_Vov_average_%s'%labels[cell])
    for i in range(0, g[cell].GetN()):
        vov = g[cell].GetX()[i]
        #s_noise = gNoise[cell].Eval(vov)/enScale
        sr = gSR[cell].Eval(vov)
        s_noise =  sigma_noise(sr*enScale, '2C')
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

c = ROOT.TCanvas('c_timeResolution_%s_nonIrr_vs_Vov'%sipmProd,'c_timeResolution_%s_nonIrr_vs_Vov'%sipmProd, 600, 500)
hPad = ROOT.gPad.DrawFrame(0.,0.,4.0,120.)
if (sipmProd == 'FBK'): hPad = ROOT.gPad.DrawFrame(0., 0., 7.5, 120.)
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
    g[cell].SetMarkerStyle(plotAttrs[cell][0])
    g[cell].SetMarkerColor(plotAttrs[cell][1])
    g[cell].SetMarkerSize(1.15)
    g[cell].SetLineColor(plotAttrs[cell][1])
    g[cell].SetLineWidth(1)
    if (cell != 15):
        g_scaled[cell].Draw('plsame')
    else:
        g[cell].Draw('plsame')
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
tl.DrawLatex(0.58,0.20,'non-irradiated')

cms_logo = draw_logo()
cms_logo.Draw()

c.SaveAs(outdir+'%s.png'%c.GetName())
c.SaveAs(outdir+'%s.pdf'%c.GetName())
c.SaveAs(outdir+'%s.C'%c.GetName())



