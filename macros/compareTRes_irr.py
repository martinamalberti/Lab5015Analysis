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




fnames = { (25, -40) : '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/summaryPlots_HPK_2E14_LYSO815_T-40C.root',
           (25, -35) : '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/summaryPlots_HPK_2E14_LYSO815_T-35C.root',
}


gnames = { (25, -40) : 'g_deltaT_totRatioCorr_bestTh_vs_vov_enBin01_average',
           #(25, -35) : 'g_deltaT_totRatioCorr_bestTh_vs_vov_enBin01_average',
}

plotAttrs = { (25, -40) : [20, ROOT.kBlack,  'HPK 25#mum 2E14 T=-40C'],
              #(25, -35) : [20, ROOT.kRed,    'HPK 25#mum 2E14 T=-35C' ],
}


c = ROOT.TCanvas('c_comparison_HPK_2E14_LYSO815','c_comparison_HPK_2E14_LYSO815')
hPad = ROOT.gPad.DrawFrame(0.,0.,4.,175.)
hPad.SetTitle(";V_{OV};#sigma_{t}^{bar} [ps]")
hPad.Draw()
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()

leg = ROOT.TLegend(0.60, 0.60, 0.89, 0.89)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
leg.SetTextFont(42)
leg.SetTextSize(0.04) 

g = {}
f = {}

for temp in [-40]:
    for cell in [25]:
        f[(cell,temp)] = ROOT.TFile.Open(fnames[(cell,temp)])
        g[(cell,temp)] = f[(cell,temp)].Get(gnames[(cell,temp)])
        g[(cell,temp)].SetMarkerSize(1)
        g[(cell,temp)].SetMarkerStyle(plotAttrs[(cell,temp)][0])
        g[(cell,temp)].SetMarkerColor(plotAttrs[(cell,temp)][1])
        g[(cell,temp)].SetLineColor(plotAttrs[(cell,temp)][1])
        leg.AddEntry(g[(cell,temp)], '%s'%plotAttrs[(cell,temp)][2],'PL')
        if (temp == 'Laser'): 
            g[(cell,temp)].Draw('plsame')
        else: 
            g[(cell,temp)].Draw('psame')
leg.Draw()

c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/ModuleCharacterization/%s.png'%c.GetName())
c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/ModuleCharacterization/%s.pdf'%c.GetName())


