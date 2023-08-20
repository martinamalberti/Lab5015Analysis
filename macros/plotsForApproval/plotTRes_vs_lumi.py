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
ROOT.gStyle.SetEndErrorSize(2)
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kWarning


outdir = '/eos/user/m/malberti/www/MTD/plotsForConferences2023/'

fnames = { 
    ('T2', 25, '0')    : '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_FNAL_Mar23/timeResolution_vs_Vov_HPK_cellSizes/plots_timeResolution_HPK_nonIrr_TBMar23_cellSizes.root',
    ('T2', 20, '0')    : '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_FNAL_Mar23/timeResolution_vs_Vov_HPK_cellSizes/plots_timeResolution_HPK_nonIrr_TBMar23_cellSizes.root',
    ('T1', 25, '0')    : '/eos/home-s/spalluot/MTD/TB_FNAL_Mar23/Lab5015Analysis/plots/compareTimeResolution_vs_Vov_HPK_nonIrr_T1_T2_T3_angle52.root',
    ('T2', 25, '2E14') : '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_2E14_20um_25um_T2_v2/plots_timeResolution_2E14_20um_25um_T2_TBMay23_TOFHIR2X.root',
    ('T2', 20, '2E14') : '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_2E14_20um_25um_T2_v2/plots_timeResolution_2E14_20um_25um_T2_TBMay23_TOFHIR2X.root',
    ('T1', 25, '1E14') :'/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_1E14_25um_T1_v2/plots_timeResolution_1E14_25um_T1_TBMay23_TOFHIR2X.root',

}

gnames = { ('T2', 25, '0', 5) : 'g_data_vs_Vov_average_HPK_nonIrr_LYSO813',
           ('T2', 20, '0', 5) : 'g_data_vs_Vov_average_HPK_nonIrr_LYSO814',
           ('T1', 25, '0', 12) : 'g_HPK_nonIrr_LYSO818_angle52_T12C',
           ('T2', 25, '2E14', -40) : 'g_data_vs_staticPower_average_HPK_2E14_LYSO815_T-40C',
           ('T2', 25, '2E14', -35) : 'g_data_vs_staticPower_average_HPK_2E14_LYSO815_T-35C',
           ('T2', 25, '2E14', -30) : 'g_data_vs_staticPower_average_HPK_2E14_LYSO815_T-30C',
           ('T2', 20, '2E14', -40) : 'g_data_vs_staticPower_average_HPK_2E14_LYSO825_T-40C',
           ('T2', 20, '2E14', -35) : 'g_data_vs_staticPower_average_HPK_2E14_LYSO825_T-35C',
           ('T2', 20, '2E14', -30) : 'g_data_vs_staticPower_average_HPK_2E14_LYSO825_T-30C',
           ('T1', 25, '1E14', -37) : 'g_data_vs_staticPower_average_HPK_1E14_LYSO819_T-37C',
           ('T1', 25, '1E14', -32) : 'g_data_vs_staticPower_average_HPK_1E14_LYSO819_T-32C',
           ('T1', 25, '1E14', -27) : 'g_data_vs_staticPower_average_HPK_1E14_LYSO819_T-27C',
           ('T1', 25, '1E14', -22) : 'g_data_vs_staticPower_average_HPK_1E14_LYSO819_T-22C',
}

lumiMap = { 
    ('0', 5)      : 0,
    ('0', 12)     : 0,
    ('2E14', -40) : 1944,
    ('2E14', -35) : 2680,
    ('2E14', -30) : 3690,
    ('1E14', -37) :  972,
    ('1E14', -32) : 1340,
    ('1E14', -27) : 1850,
    ('1E14', -22) : 2546,
}


plotAttrs = { ('T1', 25) :[20, ROOT.kGreen+1, 'Type1 + annealing at 60 #circC: 25 #mum'],
              ('T2', 25) :[20, ROOT.kGray+2 , 'Type2 + annealing at 60 #circC: 25 #mum'],
              ('T2', 20) :[20, ROOT.kGray+1 , 'Type2 + annealing at 60 #circC: 20 #mum'],
}

g_vs_lumi = {}
for typ in ['T2', 'T1']:
    for cell in [25, 20]:
        g_vs_lumi[(typ,cell)] = ROOT.TGraphErrors()
        for irr in ['0', '1E14', '2E14']:
            for temp in [5, 12, -40, -30, -35, -37, -32, -27]:
                if ( (typ, cell, irr)  not in fnames.keys() ): continue
                f = ROOT.TFile.Open(fnames[ (typ, cell, irr)] )
                if (typ, cell, irr, temp) not in gnames.keys(): continue
                g = f.Get( gnames[(typ, cell, irr, temp)])
                x = 30 #mW
                if irr == '0': x = 3.5 # OV
                g_vs_lumi[(typ,cell)].SetPoint( g_vs_lumi[(typ,cell)].GetN(), lumiMap[(irr, temp)], g.Eval(x))
                g_vs_lumi[(typ,cell)].SetPointError( g_vs_lumi[(typ,cell)].GetN()-1, 0.1*lumiMap[(irr, temp)], 1)


tdrLine = ROOT.TLine(0, 30, 4000, 65)
tdrLine.SetLineStyle(2)
tdrLine.SetLineColor(ROOT.kGray+2)

leg = ROOT.TLegend(0.20, 0.70, 0.60, 0.89)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
leg.SetTextFont(42)
leg.SetTextSize(0.045) 

c = ROOT.TCanvas('c_timeResolution_vs_lumi','c_timeResolution_vs_lumi', 600, 500)
hPad = ROOT.gPad.DrawFrame(0.,0.,4000.0,120.)
hPad.SetTitle(";Integrated luminosity [fb^{-1}]; time resolution [ps]")
hPad.Draw()
#ROOT.gPad.SetGridx()
#ROOT.gPad.SetGridy()
ROOT.gPad.SetTicks(1)

for typ in ['T1', 'T2']:
    for cell in [25, 20]:
        if ( g_vs_lumi[(typ, cell)].GetN() == 0 ): continue
        g_vs_lumi[(typ,cell)].SetMarkerSize(1)
        g_vs_lumi[(typ,cell)].SetMarkerStyle(plotAttrs[(typ,cell)][0])
        g_vs_lumi[(typ,cell)].SetMarkerColor(plotAttrs[(typ,cell)][1])
        g_vs_lumi[(typ,cell)].SetLineColor(plotAttrs[(typ,cell)][1])
        g_vs_lumi[(typ,cell)].Draw('p e 1 l same')
        leg.AddEntry( g_vs_lumi[(typ,cell)], '%s'%plotAttrs[(typ,cell)][2], 'PL')

leg.AddEntry( tdrLine, 'TDR', 'L')
tdrLine.Draw()
leg.Draw()

cms_logo = draw_logo()
cms_logo.Draw()

c.SaveAs(outdir+'%s.png'%c.GetName())
c.SaveAs(outdir+'%s.pdf'%c.GetName())
