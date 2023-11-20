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


cells  = [25, 20, 15]
#cells  = [30, 25, 20, 15]


inputdir = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_FNAL_Mar2023/ANALYSIS/ModuleCharacterization/'

fnames = { (30, 'TB') : '/eos/home-s/spalluot/MTD/TB_CERN_May23/Lab5015Analysis/plots/summaryPlots_HPK_nonIrr_LYSO820_angle52_T5C.root',
           (25, 'TB') : inputdir+'summaryPlots_HPK_nonIrr_LYSO813.root',
           (20, 'TB') : inputdir+'summaryPlots_HPK_nonIrr_LYSO814.root',
           (15, 'TB') : inputdir+'summaryPlots_HPK_nonIrr_LYSO528.root',

           (25, 'Laser') : '/afs/cern.ch/work/m/malberti/MTD/TBatFNALMar2023/Lab5015Analysis/data/plots_LYSO743_SiPM_HPK_C25-3-T2_3.root',
           (20, 'Laser') : '/afs/cern.ch/work/m/malberti/MTD/TBatFNALMar2023/Lab5015Analysis/data/plots_LYSO743_SiPM_HPK_C20-3-T2_2.root',
           (15, 'Laser') : '/afs/cern.ch/work/m/malberti/MTD/TBatFNALMar2023/Lab5015Analysis/data/plots_LYSO743_SiPM_HPK_2-32.root',
}


gnames = { (30, 'TB') : 'g_deltaT_totRatioCorr_bestTh_vs_vov_enBin01_average',
           (25, 'TB') : 'g_deltaT_totRatioCorr_bestTh_vs_vov_enBin01_average',
           (20, 'TB') : 'g_deltaT_totRatioCorr_bestTh_vs_vov_enBin01_average',
           (15, 'TB') : 'g_deltaT_totRatioCorr_bestTh_vs_vov_enBin01_average',

           (25, 'Laser') : 'g_tRes_vs_Vov_LYSO743_SiPM_HPK_C25-3-T2_3_tune19',
           (20, 'Laser') : 'g_tRes_vs_Vov_LYSO743_SiPM_HPK_C20-3-T2_2_tune72',
           (15, 'Laser') : 'g_tRes_vs_Vov_LYSO743_SiPM_HPK_2-32_tune78',
}

plotAttrs = { (30, 'TB') : [33, ROOT.kGray+1,  'TB - 30 #mum'],
              (25, 'TB') : [22, ROOT.kBlack,  'TB - 25 #mum'],
              (20, 'TB') : [21, ROOT.kRed,  'TB - 20 #mum' ],
              (15, 'TB') : [20, ROOT.kGreen+1,'TB - 15 #mum'],
              (25, 'Laser') : [26, ROOT.kBlack, 'Laser - 25 #mum'],
              (20, 'Laser') : [25, ROOT.kRed+2,   'Laser - 20 #mum'],
              (15, 'Laser') : [24, ROOT.kGreen+2,  'Laser - 15 #mum'],
}


c = ROOT.TCanvas('c_comparison_TB_Laser_cellSizes','c_comparison_TB_Laser_cellSizes', 600, 500)
if (30 in cells):
    c = ROOT.TCanvas('c_comparison_TB_Laser_cellSizes_v2','c_comparison_TB_Laser_cellSizes_v2', 600, 500)
hPad = ROOT.gPad.DrawFrame(0.,0.,4.,175.)
hPad.SetTitle(";V_{OV} [V]; time resolution [ps]")
hPad.Draw()
#ROOT.gPad.SetGridx()
#ROOT.gPad.SetGridy()
ROOT.gPad.SetTicks(1)

leg = ROOT.TLegend(0.60, 0.60, 0.89, 0.89)
leg.SetBorderSize(0)
#leg.SetFillStyle(0)
leg.SetFillColor(0)
leg.SetTextFont(42)
leg.SetTextSize(0.04) 

#gtemp = {}
g = {}
f = {}


for data in ['Laser', 'TB']:
    for cell in cells:
        if (data == 'Laser' and cell == 30): continue
        f[(cell,data)] = ROOT.TFile.Open(fnames[(cell,data)])
        gtemp = f[(cell,data)].Get(gnames[(cell,data)])
        if (gtemp == None): continue
        g[(cell,data)] = ROOT.TGraphErrors()
        for i in range(0, gtemp.GetN()):
            if (gtemp.GetPointX(i) > 0.5):
                g[(cell,data)].SetPoint(g[(cell,data)].GetN(), gtemp.GetPointX(i), gtemp.GetPointY(i))
                g[(cell,data)].SetPointError(g[(cell,data)].GetN()-1, gtemp.GetErrorX(i), gtemp.GetErrorY(i))

        g[(cell,data)].SetMarkerSize(1.0)
        if (cell == 25 and data == 'TB'): g[(cell,data)].SetMarkerSize(1.2)
        g[(cell,data)].SetMarkerStyle(plotAttrs[(cell,data)][0])
        g[(cell,data)].SetMarkerColor(plotAttrs[(cell,data)][1])
        g[(cell,data)].SetLineColor(plotAttrs[(cell,data)][1])
        leg.AddEntry(g[(cell,data)], '%s'%plotAttrs[(cell,data)][2],'PL')
        if (data == 'Laser'): 
            g[(cell,data)].Draw('plsame')
        else: 
            g[(cell,data)].Draw('psame')
leg.Draw()

cms_logo = draw_logo()
cms_logo.Draw()

c.SaveAs('/eos/user/m/malberti/www/MTD/plotsForConferences2023/v2/%s.png'%c.GetName())
c.SaveAs('/eos/user/m/malberti/www/MTD/plotsForConferences2023/v2/%s.pdf'%c.GetName())

for vov in [0.8, 1.0, 1.5, 2.0, 3.5]:
    for cell in [25,20,15]:
        res1 = g[(cell,'TB')].Eval(vov)
        res2 = g[(cell,'Laser')].Eval(vov)
        if (res1>res2):
            print vov, cell, res1, res2, math.sqrt(res1*res1-res2*res2)
        else:
            print vov, cell, res1, res2
