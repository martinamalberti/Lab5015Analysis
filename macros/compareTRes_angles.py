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
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kWarning




fnames = { 52 : '/afs/cern.ch/work/m/malberti/MTD/TBatFNALMar2023/Lab5015Analysis/plots/summaryPlots_HPK_nonIrr_LYSO813.root',
           64 : '/afs/cern.ch/work/m/malberti/MTD/TBatFNALMar2023/Lab5015Analysis/plots/summaryPlots_HPK_nonIrr_LYSO813_angle64.root',
}


gnames = { 52 : 'g_deltaT_totRatioCorr_bestTh_vs_vov_enBin01_average',
           64 : 'g_deltaT_totRatioCorr_bestTh_vs_vov_enBin01_average',
}

plotAttrs = { 52 : [20, ROOT.kBlack,  'T2 - 25#mum SiPMs - 52#circ'],
              64 : [20, ROOT.kRed  ,  'T2 - 25#mum SiPMs - 64#circ'],
}


c = ROOT.TCanvas('c_comparison_angle_T2','c_comparison_angle_T2')
hPad = ROOT.gPad.DrawFrame(0.,0.,4.,175.)
hPad.SetTitle(";V_{OV};#sigma_{t}^{bar} [ps]")
hPad.Draw()
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()

leg = ROOT.TLegend(0.50, 0.70, 0.89, 0.89)
leg.SetBorderSize(0)
leg.SetFillStyle(0)                                                                                                                                                                                    
leg.SetTextFont(42)                                                                                                                                                                                    
leg.SetTextSize(0.05) 

g = {}
f = {}

for angle in [52,64]:
    f[angle] = ROOT.TFile.Open(fnames[angle])
    g[angle] = f[angle].Get(gnames[angle])
    g[angle].SetMarkerSize(1)
    g[angle].SetMarkerStyle(plotAttrs[angle][0])
    g[angle].SetMarkerColor(plotAttrs[angle][1])
    g[angle].SetLineColor(plotAttrs[angle][1])
    leg.AddEntry(g[angle], '%s'%plotAttrs[angle][2],'PL')
    g[angle].Draw('plsame')
leg.Draw()

c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_FNAL_Mar23/ModuleCharacterization/%s.png'%c.GetName())
c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_FNAL_Mar23/ModuleCharacterization/%s.pdf'%c.GetName())


