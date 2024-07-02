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
from VovsEff import *

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


# NON-IRRADIATED
fname = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_May2023/ANALYSIS/TOFHIR2C/ModuleCharacterization/summaryPlots_HPK_nonIrr_LYSO813_T5C.root'
f = ROOT.TFile.Open(fname)

Vovs = [0.60, 0.80, 1.25, 1.50, 3.50]
g = {}

c = ROOT.TCanvas('c_timeResolution_HPK_nonIrr_vs_th','c_timeResolution_HPK_nonIrr_vs_th', 600, 500)
hPad = ROOT.gPad.DrawFrame(0.,0.,10.0,200.)
hPad.SetTitle(";threshold [#muA];time resolution [ps]")
hPad.Draw()
ROOT.gPad.SetTicks(1)
        
leg = ROOT.TLegend(0.20, 0.60, 0.60, 0.89)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
leg.SetTextFont(42)
leg.SetTextSize(0.045)

for vov in Vovs:
    gg = f.Get('g_deltaT_energyRatioCorr_vs_th_bar07_Vov%.02f_enBin01'%vov)
    g[vov] = ROOT.TGraphErrors()
    g[vov].SetMarkerColor(gg.GetMarkerColor())
    g[vov].SetMarkerSize(1)
    g[vov].SetLineColor(gg.GetLineColor())
    for i in range(0, gg.GetN()):
        th = 0.313 * gg.GetPointX(i)
        g[vov].SetPoint(i, 0.313 * gg.GetPointX(i), gg.GetPointY(i))
        g[vov].SetPointError(i, 0., gg.GetErrorY(i))
    g[vov].SetMarkerStyle(20)
    g[vov].Draw('plsame')
    leg.AddEntry(g[vov], 'V_{OV} = %.2f V'%vov, 'PL')

leg.Draw()

tl = ROOT.TLatex()
tl.SetNDC()
tl.SetTextFont(42)
tl.SetTextSize(0.045)
tl.DrawLatex(0.75,0.85,'HPK 25 #mum')

tl2 = ROOT.TLatex()
tl2.SetNDC()
tl2.SetTextFont(42)
tl2.SetTextSize(0.045)
tl2.DrawLatex(0.72,0.80,'non-irradiated')

#cms_logo = draw_logo()
#cms_logo.Draw()

c.SaveAs(outdir+'%s.png'%c.GetName())
c.SaveAs(outdir+'%s.pdf'%c.GetName())


# irradiated
fname2 = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_May2023/ANALYSIS/TOFHIR2C/ModuleCharacterization/summaryPlots_HPK_2E14_LYSO815_T-35C.root'
f2 = ROOT.TFile.Open(fname2)

with open('/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_May2023/VovsEff_TOFHIR2C.json', 'r') as f:
      data = json.load(f)
      
Vovs = [0.60, 0.80, 1.25, 1.50, 2.00]
#Vovs = [0.60, 0.80, 1.25, 1.50]
g2 = {}

c2 = ROOT.TCanvas('c_timeResolution_HPK_2E14_vs_th','c_timeResolution_HPK_2E14_vs_th', 600, 500)
hPad2 = ROOT.gPad.DrawFrame(0.,0.,10.0,200.)
hPad2.SetTitle(";threshold [#muA];time resolution [ps]")
hPad2.Draw()
ROOT.gPad.SetTicks(1)

leg2 = ROOT.TLegend(0.20, 0.60, 0.60, 0.89)
leg2.SetBorderSize(0)
leg2.SetFillStyle(0)
leg2.SetTextFont(42)
leg2.SetTextSize(0.045)

for vov in Vovs:
    gg = f2.Get('g_deltaT_energyRatioCorr_vs_th_bar07_Vov%.02f_enBin01'%vov)
    g2[vov] = ROOT.TGraphErrors()
    g2[vov].SetMarkerColor(gg.GetMarkerColor())
    g2[vov].SetMarkerSize(1)
    g2[vov].SetLineColor(gg.GetLineColor())
    for i in range(0, gg.GetN()):
        th = 0.313 * gg.GetPointX(i)
        g2[vov].SetPoint(i, 0.313 * gg.GetPointX(i), gg.GetPointY(i))
        g2[vov].SetPointError(i, 0., gg.GetErrorY(i))
    g2[vov].SetMarkerStyle(20)
    g2[vov].Draw('plsame')
    vovEff = getVovEffDCR(data,'HPK_2E14_LYSO815_T-35C', ('%.02f'%vov))[0]
    leg2.AddEntry(g2[vov], 'V_{OV} = %.2f V'%vovEff, 'PL')

leg2.Draw()

tl.DrawLatex(0.75,0.85,'HPK 25 #mum')
tl2.DrawLatex(0.60,0.80,'2 #times 10^{14} 1 MeV n_{eq}/cm^{2}')

#cms_logo = draw_logo()
#cms_logo.Draw()

c2.SaveAs(outdir+'%s.png'%c2.GetName())
c2.SaveAs(outdir+'%s.pdf'%c2.GetName())
c2.SaveAs(outdir+'%s.C'%c2.GetName())
