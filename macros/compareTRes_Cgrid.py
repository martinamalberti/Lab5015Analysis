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




fnames = { 'nominal'  : '/afs/cern.ch/work/m/malberti/MTD/TBatFNALMar2023/Lab5015Analysis/plots/summaryPlots_HPK_nonIrr_LYSO813.root',
           'lowCgrid' : '/afs/cern.ch/work/m/malberti/MTD/TBatFNALMar2023/Lab5015Analysis/plots/summaryPlots_HPK_nonIrr_LYSO824.root',
}


gnames = { 'nominal' : 'g_deltaT_totRatioCorr_bestTh_vs_vov_enBin01_average',
           'lowCgrid': 'g_deltaT_totRatioCorr_bestTh_vs_vov_enBin01_average',
}

plotAttrs = { 'nominal'  : [20, ROOT.kBlack,  'LYSO813(prod1) + 25#mum SiPMs'],
              'lowCgrid' : [20, ROOT.kRed  ,  'LYSO824(prod5) + 25#mum SiPMs, low C_{g}'],
}


c = ROOT.TCanvas('c_comparison_Cgrid_T2','c_comparison_Cgrid_T2')
hPad = ROOT.gPad.DrawFrame(0.,0.,4.,175.)
hPad.SetTitle(";V_{OV};#sigma_{t}^{bar} [ps]")
hPad.Draw()
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()

leg = ROOT.TLegend(0.35, 0.70, 0.89, 0.89)
leg.SetBorderSize(0)
leg.SetFillStyle(0)  
leg.SetTextFont(42)
leg.SetTextSize(0.04) 

g = {}
f = {}

for cg in ['nominal','lowCgrid']:
    f[cg] = ROOT.TFile.Open(fnames[cg])
    g[cg] = f[cg].Get(gnames[cg])
    g[cg].SetMarkerSize(1)
    g[cg].SetMarkerStyle(plotAttrs[cg][0])
    g[cg].SetMarkerColor(plotAttrs[cg][1])
    g[cg].SetLineColor(plotAttrs[cg][1])
    leg.AddEntry(g[cg], '%s'%plotAttrs[cg][2],'PL')
    g[cg].Draw('plsame')
leg.Draw()

c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_FNAL_Mar23/ModuleCharacterization/%s.png'%c.GetName())
c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_FNAL_Mar23/ModuleCharacterization/%s.pdf'%c.GetName())


