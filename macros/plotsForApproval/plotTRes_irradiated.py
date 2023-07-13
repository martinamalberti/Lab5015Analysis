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


outdir = '/eos/user/m/malberti/www/MTD/plotsForConferences2023/'

fnames = { 
    (25, -40, '2E14') :'/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_2E14_20um_25um_T2_v2/plots_timeResolution_2E14_20um_25um_T2_TBMay23_TOFHIR2X.root',
    (25, -35, '2E14') :'/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_2E14_20um_25um_T2_v2/plots_timeResolution_2E14_20um_25um_T2_TBMay23_TOFHIR2X.root',
    (25, -30, '2E14') :'/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_2E14_20um_25um_T2_v2/plots_timeResolution_2E14_20um_25um_T2_TBMay23_TOFHIR2X.root',

    (20, -40, '2E14') :'/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_2E14_20um_25um_T2_v2/plots_timeResolution_2E14_20um_25um_T2_TBMay23_TOFHIR2X.root',
    (20, -35, '2E14') :'/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_2E14_20um_25um_T2_v2/plots_timeResolution_2E14_20um_25um_T2_TBMay23_TOFHIR2X.root',
    (20, -30, '2E14') :'/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_2E14_20um_25um_T2_v2/plots_timeResolution_2E14_20um_25um_T2_TBMay23_TOFHIR2X.root',

    (25, -22, '1E14') :'/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_1E14_25um_T1_v2/plots_timeResolution_1E14_25um_T1_TBMay23_TOFHIR2X.root',
    (25, -27, '1E14') :'/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_1E14_25um_T1_v2/plots_timeResolution_1E14_25um_T1_TBMay23_TOFHIR2X.root',
    (25, -32, '1E14') :'/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_1E14_25um_T1_v2/plots_timeResolution_1E14_25um_T1_TBMay23_TOFHIR2X.root',
    (25, -37, '1E14') :'/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_1E14_25um_T1_v2/plots_timeResolution_1E14_25um_T1_TBMay23_TOFHIR2X.root'
}

names = {
    (25, -40,'2E14') : 'LYSO815',
    (25, -35,'2E14') : 'LYSO815',
    (25, -30,'2E14') : 'LYSO815',
    
    (20, -40,'2E14') : 'LYSO825',
    (20, -35,'2E14') : 'LYSO825',
    (20, -30,'2E14') : 'LYSO825',

    (25, -22,'1E14') : 'LYSO819',
    (25, -27,'1E14') : 'LYSO819',
    (25, -32,'1E14') : 'LYSO819',
    (25, -37,'1E14') : 'LYSO819',
}

plotAttrs = { #(25, -40,'2E14') : [20, ROOT.kBlue,     '25#mum T=-40#circC'],
              #(25, -35,'2E14') : [20, ROOT.kOrange+1, '25#mum T=-35#circC' ],
              #(25, -30,'2E14') : [20, ROOT.kRed ,     '25#mum T=-30#circC' ],
              #(20, -40,'2E14') : [24, ROOT.kBlue,     '20#mum T=-40#circC'],
              #(20, -35,'2E14') : [24, ROOT.kOrange+1, '20#mum T=-35#circC' ],
              #(20, -30,'2E14') : [24, ROOT.kRed ,     '20#mum T=-30#circC' ],
              
              #(25, -22, '1E14') : [20, ROOT.kRed,       '25#mum T=-22#circC'],
              #(25, -27, '1E14') : [20, ROOT.kOrange+1,  '25#mum T=-27#circC' ],
              #(25, -32, '1E14') : [20, ROOT.kGreen+1 ,  '25#mum T=-32#circC' ],
              #(25, -37, '1E14') : [20, ROOT.kBlue ,     '25#mum T=-37#circC' ],

              (25, -40,'2E14') : [20, ROOT.kBlue,     '25 #mum - #it{L}_{eq.DCR}=1900 fb^{-1}'], # round lumis to 2 digits
              (25, -35,'2E14') : [20, ROOT.kOrange+1, '25 #mum - #it{L}_{eq.DCR}=2700 fb^{-1}'],
              (25, -30,'2E14') : [20, ROOT.kRed ,     '25 #mum - #it{L}_{eq.DCR}=3700 fb^{-1}'],
              (20, -40,'2E14') : [24, ROOT.kBlue,     '20 #mum - #it{L}_{eq.DCR}=1900 fb^{-1}'],
              (20, -35,'2E14') : [24, ROOT.kOrange+1, '20 #mum - #it{L}_{eq.DCR}=2700 fb^{-1}'],
              (20, -30,'2E14') : [24, ROOT.kRed ,     '20 #mum - #it{L}_{eq.DCR}=3700 fb^{-1}'],
              
              (25, -22, '1E14') : [20, ROOT.kRed,       '25 #mum - #it{L}_{eq.DCR}=2500 fb^{-1}' ],
              (25, -27, '1E14') : [20, ROOT.kOrange+1,  '25 #mum - #it{L}_{eq.DCR}=1800 fb^{-1}' ],
              (25, -32, '1E14') : [20, ROOT.kGreen+1 ,  '25 #mum - #it{L}_{eq.DCR}=1300 fb^{-1}' ],
              (25, -37, '1E14') : [20, ROOT.kBlue ,     '25 #mum - #it{L}_{eq.DCR}=1000 fb^{-1}' ],
}

g = {}
gg = {}
f = {}

# ==== 2E14
for temp in [-40, -35, -30]:
    for cell in [20,25]:
        f[(cell,temp,'2E14')] = ROOT.TFile.Open(fnames[(cell,temp,'2E14')])

leg = ROOT.TLegend(0.45, 0.60, 0.89, 0.89)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
leg.SetTextFont(42)
leg.SetTextSize(0.045) 

c = ROOT.TCanvas('c_timeResolution_HPK_2E14_vs_Vov','c_timeResolution_HPK_2E14_vs_Vov', 600, 500)
hPad = ROOT.gPad.DrawFrame(0.,40.,2.0,140.)
hPad.SetTitle(";V_{OV} [V];time resolution [ps]")
hPad.Draw()
#ROOT.gPad.SetGridx()
#ROOT.gPad.SetGridy()
ROOT.gPad.SetTicks(1)
for cell in [25, 20]:
    for temp in [-40, -35, -30]:
        g[(cell,temp,'2E14')] = f[(cell,temp, '2E14')].Get('g_data_vs_Vov_average_HPK_2E14_%s_T%sC'%(names[cell, temp, '2E14'], str(temp)))
        g[(cell,temp,'2E14')].SetMarkerSize(1)
        g[(cell,temp,'2E14')].SetMarkerStyle(plotAttrs[(cell,temp,'2E14')][0])
        g[(cell,temp,'2E14')].SetMarkerColor(plotAttrs[(cell,temp,'2E14')][1])
        g[(cell,temp,'2E14')].SetLineColor(plotAttrs[(cell,temp,'2E14')][1])
        leg.AddEntry(g[(cell,temp,'2E14')], '%s'%plotAttrs[(cell,temp,'2E14')][2],'PL')
        g[(cell,temp,'2E14')].Draw('plsame')
leg.Draw()

tl2 = ROOT.TLatex()
tl2.SetNDC()
tl2.SetTextFont(42)
tl2.SetTextSize(0.045)
tl2.DrawLatex(0.58,0.25,'                            Type 2')

tl = ROOT.TLatex()
tl.SetNDC()
tl.SetTextFont(42)
tl.SetTextSize(0.045)
tl.DrawLatex(0.58,0.20,'2 #times 10^{14} 1 MeV n_{eq}/cm^{2}')

cms_logo = draw_logo()
cms_logo.Draw()

c.SaveAs(outdir+'%s.png'%c.GetName())
c.SaveAs(outdir+'%s.pdf'%c.GetName())


c = ROOT.TCanvas('c_timeResolution_HPK_2E14_vs_staticPower','c_timeResolution_HPK_2E14_vs_staticPower', 600, 500)
hPad = ROOT.gPad.DrawFrame(0.,40.,120.0,140.)
hPad.SetTitle(";SiPM static power [mW]; time resolution [ps]")
hPad.Draw()
#ROOT.gPad.SetGridx()
#ROOT.gPad.SetGridy()
ROOT.gPad.SetTicks(1)
for cell in [25, 20]:
    for temp in [-40, -35, -30]:
        g[(cell,temp,'2E14')] = f[(cell,temp, '2E14')].Get('g_data_vs_staticPower_average_HPK_2E14_%s_T%sC'%(names[cell, temp, '2E14'], str(temp)))
        g[(cell,temp,'2E14')].SetMarkerSize(1)
        g[(cell,temp,'2E14')].SetMarkerStyle(plotAttrs[(cell,temp,'2E14')][0])
        g[(cell,temp,'2E14')].SetMarkerColor(plotAttrs[(cell,temp,'2E14')][1])
        g[(cell,temp,'2E14')].SetLineColor(plotAttrs[(cell,temp,'2E14')][1])
        g[(cell,temp,'2E14')].Draw('plsame')
leg.Draw()

tl2.DrawLatex(0.58,0.25,'                            Type 2')
tl.DrawLatex(0.58,0.20, '2 #times 10^{14} 1 MeV n_{eq}/cm^{2}')
cms_logo = draw_logo()
cms_logo.Draw()

line = ROOT.TLine(30., 40., 30., 140.)
line.SetLineStyle(2)
line.SetLineColor(ROOT.kGray+1)
line.Draw()
tl3 = ROOT.TLatex(0.38, 0.45, '#splitline{nominal power}{bugdet}')
tl3.SetNDC()
tl3.SetTextColor(ROOT.kGray+1)
tl3.SetTextFont(42)
tl3.SetTextSize(0.035)
tl3.Draw()

c.SaveAs(outdir+'%s.png'%c.GetName())
c.SaveAs(outdir+'%s.pdf'%c.GetName())




# ==== 1E14
for temp in [-22, -27, -32, -37]:
    for cell in [25]:
        f[(cell,temp,'1E14')] = ROOT.TFile.Open(fnames[(cell,temp,'1E14')])

leg = ROOT.TLegend(0.45, 0.60, 0.89, 0.89)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
leg.SetTextFont(42)
leg.SetTextSize(0.045)

c = ROOT.TCanvas('c_timeResolution_HPK_1E14_vs_Vov','c_timeResolution_HPK_1E14_vs_Vov', 600, 500)
hPad = ROOT.gPad.DrawFrame(0.,20.,2.0,100.)
hPad.SetTitle(";V_{OV} [V];time resolution [ps]")
hPad.Draw()
#ROOT.gPad.SetGridx()
#ROOT.gPad.SetGridy()
ROOT.gPad.SetTicks(1)
for cell in [25]:
    #for temp in [-22, -27, -32, -37]:
    for temp in [-27, -32, -37]:
        g[(cell,temp,'1E14')] = f[(cell,temp, '1E14')].Get('g_data_vs_Vov_average_HPK_1E14_%s_T%sC'%(names[cell, temp, '1E14'], str(temp)))
        g[(cell,temp,'1E14')].SetMarkerSize(1)
        g[(cell,temp,'1E14')].SetMarkerStyle(plotAttrs[(cell,temp,'1E14')][0])
        g[(cell,temp,'1E14')].SetMarkerColor(plotAttrs[(cell,temp,'1E14')][1])
        g[(cell,temp,'1E14')].SetLineColor(plotAttrs[(cell,temp,'1E14')][1])
        leg.AddEntry(g[(cell,temp,'1E14')], '%s'%plotAttrs[(cell,temp,'1E14')][2],'PL')
        g[(cell,temp,'1E14')].Draw('plsame')
leg.Draw()

tl2.DrawLatex(0.58,0.25,'                            Type 1')
tl.DrawLatex(0.58,0.20, '1 #times 10^{14} 1 MeV n_{eq}/cm^{2}')
cms_logo = draw_logo()
cms_logo.Draw()

c.SaveAs(outdir+'%s.png'%c.GetName())
c.SaveAs(outdir+'%s.pdf'%c.GetName())


c = ROOT.TCanvas('c_timeResolution_HPK_1E14_vs_staticPower','c_timeResolution_HPK_1E14_vs_staticPower', 600, 500)
hPad = ROOT.gPad.DrawFrame(0.,20.,120.0,100.)
hPad.SetTitle(";SiPM static power [mW];time resolution [ps]")
hPad.Draw()
#ROOT.gPad.SetGridx()
#ROOT.gPad.SetGridy()
ROOT.gPad.SetTicks(1)
for cell in [25]:
    #for temp in [-22, -27, -32, -37]:
    for temp in [-27, -32, -37]:
        g[(cell,temp,'1E14')] = f[(cell,temp, '1E14')].Get('g_data_vs_staticPower_average_HPK_1E14_%s_T%sC'%(names[cell, temp, '1E14'], str(temp)))
        g[(cell,temp,'1E14')].SetMarkerSize(1)
        g[(cell,temp,'1E14')].SetMarkerStyle(plotAttrs[(cell,temp,'1E14')][0])
        g[(cell,temp,'1E14')].SetMarkerColor(plotAttrs[(cell,temp,'1E14')][1])
        g[(cell,temp,'1E14')].SetLineColor(plotAttrs[(cell,temp,'1E14')][1])
        g[(cell,temp,'1E14')].Draw('plsame')
leg.Draw()

tl2.DrawLatex(0.58,0.25,'                            Type 1')
tl.DrawLatex(0.58,0.20, '1 #times 10^{14} 1 MeV n_{eq}/cm^{2}')
line = ROOT.TLine(30., 20., 30., 100.)
line.SetLineStyle(2)
line.SetLineColor(ROOT.kGray+1)
line.Draw()
tl3.Draw()
cms_logo = draw_logo()
cms_logo.Draw()

c.SaveAs(outdir+'%s.png'%c.GetName())
c.SaveAs(outdir+'%s.pdf'%c.GetName())



