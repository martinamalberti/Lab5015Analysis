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




fnames = { #(25, 'FNAL') : '/afs/cern.ch/work/m/malberti/MTD/TBatFNALMar2023/Lab5015Analysis/plots/summaryPlots_HPK_nonIrr_LYSO813.root',
           (25, 'CERN')    : '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_nonIrr_LYSO813_T5C.root',
           (30, 'CERN')    : '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_nonIrr_LYSO820.root',
}


gnames = { #(25, 'FNAL') : 'g_deltaT_totRatioCorr_bestTh_vs_vov_enBin01_average',
           (25, 'CERN') : 'g_deltaT_totRatioCorr_bestTh_vs_vov_enBin01_average',
           (30, 'CERN') : 'g_deltaT_totRatioCorr_bestTh_vs_vov_bar07_enBin01'
}

plotAttrs = { (25, 'FNAL') : [20, ROOT.kBlue,  'LYSO813 + HPK 25#mum (FNAL March23)'],
              (25, 'CERN') : [20, ROOT.kRed ,  'LYSO813 + HPK 25#mum (CERN May23)' ],
              (30, 'CERN') : [20, ROOT.kRed+2 ,'LYSO820 + HPK 30#mum (CERN May23)' ],
}


#c = ROOT.TCanvas('c_comparison_HPK_nonIrr_LYSO813','c_comparison_HPK_nonIrr_LYSO813')
c = ROOT.TCanvas('c_comparison_HPK_nonIrr_25um_30um','c_comparison_HPK_nonIrr_25um_30um')
hPad = ROOT.gPad.DrawFrame(0.,0.,5.,130.)
hPad.SetTitle(";V_{OV};#sigma_{t}^{bar} [ps]")
hPad.Draw()
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()

leg = ROOT.TLegend(0.20, 0.75, 0.85, 0.89)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
leg.SetTextFont(42)
leg.SetTextSize(0.04) 

g = {}
f = {}

#for temp in ['FNAL','CERN']:
for temp in ['CERN']:
    for cell in [25,30]:
        f[(cell,temp)] = ROOT.TFile.Open(fnames[(cell,temp)])
        g[(cell,temp)] = f[(cell,temp)].Get(gnames[(cell,temp)])
        g[(cell,temp)].SetMarkerSize(1)
        g[(cell,temp)].SetMarkerStyle(plotAttrs[(cell,temp)][0])
        g[(cell,temp)].SetMarkerColor(plotAttrs[(cell,temp)][1])
        g[(cell,temp)].SetLineColor(plotAttrs[(cell,temp)][1])
        leg.AddEntry(g[(cell,temp)], '%s'%plotAttrs[(cell,temp)][2],'PL')
        g[(cell,temp)].Draw('plsame')
        
leg.Draw()

c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/ModuleCharacterization/%s.png'%c.GetName())
c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/ModuleCharacterization/%s.pdf'%c.GetName())


