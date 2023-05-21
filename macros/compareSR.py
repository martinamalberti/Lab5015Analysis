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
ROOT.gStyle.SetLabelSize(0.055,'X')
ROOT.gStyle.SetLabelSize(0.055,'Y')
ROOT.gStyle.SetTitleSize(0.07,'X')
ROOT.gStyle.SetTitleSize(0.07,'Y')
ROOT.gStyle.SetTitleOffset(1.05,'X')
ROOT.gStyle.SetTitleOffset(1.1,'Y')
ROOT.gStyle.SetLegendFont(42)
ROOT.gStyle.SetLegendTextSize(0.045)
ROOT.gStyle.SetPadTopMargin(0.07)
ROOT.gROOT.SetBatch(False)
ROOT.gErrorIgnoreLevel = ROOT.kWarning




fnames = { 815 : '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/pulseShape_HPK_2E14_LYSO815_Vov1.00_T-40C.root',
           813 : '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/pulseShape_HPK_nonIrr_LYSO813_Vov0.80.root',
}

plotAttrs = { 815 : [20, ROOT.kBlue,  'HPK 25#mum 2E14 T=-40C'],
              813 : [20, ROOT.kRed ,  'HPK 25#mum noIrr' ],
}


c = ROOT.TCanvas('c_comparison_SR','c_comparison_SR')
hPad = ROOT.gPad.DrawFrame(-0.5,0.,15.5,15.)
hPad.SetTitle(";bar;slope[#muA/ns]")
hPad.Draw()
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()

leg = ROOT.TLegend(0.50, 0.20, 0.85, 0.39)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
leg.SetTextFont(42)
leg.SetTextSize(0.04) 

gPS = {}
f = {}

g = {}
fitFun = {}
for sipm in [815, 813]:
    f[sipm] = ROOT.TFile.Open(fnames[sipm])
    g[sipm] = ROOT.TGraphErrors()
    for bar in [0,3,4,5,7,8,9,11,12,13,15]:
        ov = 1.00
        if (sipm == 813): ov = 0.80
        gPS[(bar,sipm)] = f[sipm].Get('g_pulseShapeR_bar%02d_Vov%.2f'%(bar,ov))
        gPS[(bar,sipm)] = f[sipm].Get('g_pulseShapeL_bar%02d_Vov%.2f'%(bar,ov))
        if (gPS[(bar,sipm)] == None): continue
        fitFun[(bar,sipm)] = ROOT.TF1('fitFun_%d_%d'%(bar,sipm),'pol1',gPS[(bar,sipm)].GetPointX(0),gPS[(bar,sipm)].GetPointX(3))
        fitFun[(bar,sipm)].SetParameters(0,8)
        gPS[(bar,sipm)].Fit(fitFun[(bar,sipm)],'QSR')
        print(sipm, bar, fitFun[(bar,sipm)].GetParameter(0),fitFun[(bar,sipm)].GetParameter(1))
        g[sipm].SetPoint(g[sipm].GetN(), bar, fitFun[(bar,sipm)].GetParameter(1))
        g[sipm].SetPointError(g[sipm].GetN()-1, 0, fitFun[(bar,sipm)].GetParError(1))
        g[sipm].SetMarkerSize(1)
        g[sipm].SetMarkerStyle(plotAttrs[sipm][0])
        g[sipm].SetMarkerColor(plotAttrs[sipm][1])
        g[sipm].SetLineColor(plotAttrs[sipm][1])
    leg.AddEntry(g[sipm], '%s'%plotAttrs[sipm][2],'P')
    g[sipm].Draw('psame')
        
leg.Draw()

c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/%s.png'%c.GetName())
c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/%s.pdf'%c.GetName())


