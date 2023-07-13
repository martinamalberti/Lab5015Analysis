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



fnames = { 25 : '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_FNAL_Mar23/timeResolution_vs_Vov_HPK_cellSizes/plots_timeResolution_HPK_nonIrr_TBMar23_cellSizes.root',
           20 : '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_FNAL_Mar23/timeResolution_vs_Vov_HPK_cellSizes/plots_timeResolution_HPK_nonIrr_TBMar23_cellSizes.root',
           15 : '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_FNAL_Mar23/timeResolution_vs_Vov_HPK_cellSizes/plots_timeResolution_HPK_nonIrr_TBMar23_cellSizes.root'
           #15 : '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_Jun22/timeResolution_vs_Vov_HPK_nonIrr/plots_timeResolution_HPK_nonIrr_TBJune22.root'
}


names = { 25 : 'LYSO813',
          20 : 'LYSO814',
          15 : 'LYSO528'
}

g_data = {}
g_stoch = {}
g_noise = {}
g_tot = {}
f = {}

for cell in [25,20,15]:
    c = ROOT.TCanvas('c_timeResolution_components_vs_Vov_%dum_nonIrradiated'%cell,'c_timeResolution_components_vs_Vov_%dum_nonIrradiated'%cell, 600, 500)
    hPad = ROOT.gPad.DrawFrame(0.,0.,4.,120.)
    hPad.SetTitle(";V_{OV}[V];time resolution[ps]")
    hPad.Draw()
    #ROOT.gPad.SetGridx()
    #ROOT.gPad.SetGridy()
    ROOT.gPad.SetTicks(1)

    f[cell] = ROOT.TFile.Open(fnames[cell])
    g_data[cell] = ROOT.TGraphErrors()
    g_stoch[cell] = ROOT.TGraphErrors()
    g_noise[cell] = ROOT.TGraphErrors()
    g_tot[cell] = ROOT.TGraphErrors()

    g_data_tmp  = f[cell].Get('g_data_vs_Vov_average_HPK_nonIrr_%s'%names[cell])
    g_stoch_tmp = f[cell].Get('g_Stoch_vs_Vov_average_HPK_nonIrr_%s'%names[cell])
    g_noise_tmp = f[cell].Get('g_Noise_vs_Vov_average_HPK_nonIrr_%s'%names[cell])
    g_tot_tmp   = f[cell].Get('g_Tot_vs_Vov_average_HPK_nonIrr_%s'%names[cell])

    for i in range(0, g_data_tmp.GetN()):
        print(i, g_data_tmp.GetPointX(i),g_data_tmp.GetPointY(i))
        if (g_data_tmp.GetPointX(i) > 0.5):
            g_data[cell].SetPoint(g_data[cell].GetN(), g_data_tmp.GetPointX(i), g_data_tmp.GetPointY(i))
            g_data[cell].SetPointError(g_data[cell].GetN()-1, g_data_tmp.GetErrorX(i), g_data_tmp.GetErrorY(i))

    for i in range(0, g_stoch_tmp.GetN()):
        if (g_stoch_tmp.GetPointX(i) > 0.5):
            g_stoch[cell].SetPoint(g_stoch[cell].GetN(), g_stoch_tmp.GetPointX(i), g_stoch_tmp.GetPointY(i))
            g_stoch[cell].SetPointError(g_stoch[cell].GetN()-1, g_stoch_tmp.GetErrorX(i), g_stoch_tmp.GetErrorY(i))

    for i in range(0, g_noise_tmp.GetN()):
        if (g_noise_tmp.GetPointX(i) > 0.5):
            g_noise[cell].SetPoint(g_noise[cell].GetN(), g_noise_tmp.GetPointX(i), g_noise_tmp.GetPointY(i))
            g_noise[cell].SetPointError(g_noise[cell].GetN()-1, g_noise_tmp.GetErrorX(i), g_noise_tmp.GetErrorY(i))

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
    cms_logo = draw_logo()
    cms_logo.Draw()
        
    c.SaveAs('/eos/user/m/malberti/www/MTD/plotsForConferences2023/%s.png'%c.GetName())
    c.SaveAs('/eos/user/m/malberti/www/MTD/plotsForConferences2023/%s.pdf'%c.GetName())




    
