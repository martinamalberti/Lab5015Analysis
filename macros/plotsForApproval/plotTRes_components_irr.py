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

inputdir = '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_2E14_20um_25um_T2_v2/'
fnames = { 25 : inputdir+'plots_timeResolution_2E14_20um_25um_T2_TBMay23_TOFHIR2X.root',
           20 : inputdir+'plots_timeResolution_2E14_20um_25um_T2_TBMay23_TOFHIR2X.root',
}


names = { 25 : 'LYSO815',
          20 : 'LYSO825',
}

g_data = {}
g_stoch = {}
g_noise = {}
g_dcr = {}
g_tot = {}
f = {}

for cell in [25,20]:
    c = ROOT.TCanvas('c_timeResolution_components_vs_Vov_%dum_2E14'%cell,'c_timeResolution_components_vs_Vov_%dum_2E14'%cell, 600, 500)
    hPad = ROOT.gPad.DrawFrame(0.,0.,2.,140.)
    hPad.SetTitle(";V_{OV}[V];time resolution[ps]")
    hPad.Draw()
    #ROOT.gPad.SetGridx()
    #ROOT.gPad.SetGridy()
    ROOT.gPad.SetTicks(1)

    f[cell] = ROOT.TFile.Open(fnames[cell])
    g_data[cell]   = f[cell].Get('g_data_vs_Vov_average_HPK_2E14_%s_T-35C'%names[cell])
    g_stoch[cell]  = f[cell].Get('g_Stoch_vs_Vov_average_HPK_2E14_%s_T-35C'%names[cell])
    g_noise[cell]  = f[cell].Get('g_Noise_vs_Vov_average_HPK_2E14_%s_T-35C'%names[cell])
    g_dcr[cell]    = f[cell].Get('g_DCR_vs_Vov_average_HPK_2E14_%s_T-35C'%names[cell])
    g_tot[cell]    = f[cell].Get('g_Tot_vs_Vov_average_HPK_2E14_%s_T-35C'%names[cell])

    if (cell==20): g_data[cell].RemovePoint(0)
    g_data[cell].SetLineWidth(2)
    g_data[cell].SetMarkerSize(1)
    g_data[cell].Draw('plsame')
    g_noise[cell].SetLineWidth(2)
    g_noise[cell].SetLineColor(ROOT.kBlue)
    g_noise[cell].SetFillColor(ROOT.kBlue)
    g_noise[cell].SetFillColorAlpha(ROOT.kBlue,0.5)
    g_noise[cell].SetFillStyle(3004)
    g_noise[cell].Draw('E3lsame')
    g_stoch[cell].SetLineWidth(2)
    g_stoch[cell].SetLineColor(ROOT.kGreen+2)
    g_stoch[cell].SetFillColor(ROOT.kGreen+2)
    g_stoch[cell].SetFillStyle(3001)
    g_stoch[cell].SetFillColorAlpha(ROOT.kGreen+2,0.5)
    g_stoch[cell].Draw('E3lsame')
    g_dcr[cell].SetLineWidth(2)
    g_dcr[cell].SetLineColor(ROOT.kOrange+1)
    g_dcr[cell].SetFillColor(ROOT.kOrange+1)
    g_dcr[cell].SetFillStyle(3001)
    g_dcr[cell].SetFillColorAlpha(ROOT.kOrange+1,0.5)
    g_dcr[cell].Draw('E3lsame')
    g_tot[cell].SetLineWidth(2)
    g_tot[cell].SetLineColor(ROOT.kRed+1)
    g_tot[cell].SetFillColor(ROOT.kRed+1)
    g_tot[cell].SetFillColorAlpha(ROOT.kRed+1,0.5)
    g_tot[cell].SetFillStyle(3001)
    #g_tot[cell].Draw('E3lsame')
    
    leg = ROOT.TLegend(0.70, 0.60, 0.89, 0.89)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.050)
    leg.AddEntry(g_data[cell], 'data', 'PL')
    leg.AddEntry(g_noise[cell], 'noise', 'L')
    leg.AddEntry(g_stoch[cell], 'stochastic', 'L')    
    leg.AddEntry(g_stoch[cell], 'DCR', 'L')    
    leg.Draw()

    tl = ROOT.TLatex()
    tl.SetNDC()
    tl.SetTextFont(42)
    tl.SetTextSize(0.050)
    tl.DrawLatex(0.20,0.80,'%d #mum'%cell)

    tl2 = ROOT.TLatex()
    tl2.SetNDC()
    tl2.SetTextFont(42)
    tl2.SetTextSize(0.050)
    tl2.DrawLatex(0.20,0.86,'Type 2')

    tl3 = ROOT.TLatex()
    tl3.SetNDC()
    tl3.SetTextFont(42)
    tl3.SetTextSize(0.050)
    tl3.DrawLatex(0.20,0.74,'2 #times 10^{14} 1 MeV n_{eq}/cm^{2}')

    cms_logo = draw_logo()
    cms_logo.Draw()

    c.SaveAs('/eos/user/m/malberti/www/MTD/plotsForConferences2023/%s.png'%c.GetName())
    c.SaveAs('/eos/user/m/malberti/www/MTD/plotsForConferences2023/%s.pdf'%c.GetName())




    
