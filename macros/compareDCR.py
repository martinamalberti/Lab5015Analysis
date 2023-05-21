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
from collections import OrderedDict

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


inputdir = '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/'

irradiations = ['2E14', '1E14']
temperatures = {'2E14' : [-40, -35, -30],
                '1E14' : [-37, -32, -27, -22]}

module_dict = OrderedDict()

module_dict= { 'HPK_2E14_LYSO815_T-40C' : ['2E14', -40, 25, inputdir+'/timeResolution_2E14_20um_25um_T2/plots_timeResolution_2E14_20um_25um_T2_TBMay23.root'],
               'HPK_2E14_LYSO815_T-35C' : ['2E14', -35, 25, inputdir+'/timeResolution_2E14_20um_25um_T2/plots_timeResolution_2E14_20um_25um_T2_TBMay23.root'],
               'HPK_2E14_LYSO815_T-30C' : ['2E14', -30, 25, inputdir+'/timeResolution_2E14_20um_25um_T2/plots_timeResolution_2E14_20um_25um_T2_TBMay23.root'],

               'HPK_2E14_LYSO825_T-40C' : ['2E14', -40, 20, inputdir+'/timeResolution_2E14_20um_25um_T2/plots_timeResolution_2E14_20um_25um_T2_TBMay23.root'],
               'HPK_2E14_LYSO825_T-35C' : ['2E14', -35, 20, inputdir+'/timeResolution_2E14_20um_25um_T2/plots_timeResolution_2E14_20um_25um_T2_TBMay23.root'],
               'HPK_2E14_LYSO825_T-30C' : ['2E14', -30, 20, inputdir+'/timeResolution_2E14_20um_25um_T2/plots_timeResolution_2E14_20um_25um_T2_TBMay23.root'],

               'HPK_1E14_LYSO819_T-37C' : ['1E14', -37, 25, inputdir+'/timeResolution_1E14_25um_T1/plots_timeResolution_1E14_25um_T1_TBMay23.root'],
               'HPK_1E14_LYSO819_T-32C' : ['1E14', -32, 25, inputdir+'/timeResolution_1E14_25um_T1/plots_timeResolution_1E14_25um_T1_TBMay23.root'],
               'HPK_1E14_LYSO819_T-27C' : ['1E14', -27, 25, inputdir+'/timeResolution_1E14_25um_T1/plots_timeResolution_1E14_25um_T1_TBMay23.root'],
               'HPK_1E14_LYSO819_T-22C' : ['1E14', -22, 25, inputdir+'/timeResolution_1E14_25um_T1/plots_timeResolution_1E14_25um_T1_TBMay23.root'],
           }


# ratio temp vs OV

g = {}
gratio = {}

for k in module_dict:
    irr  = module_dict[k][0]
    temp = module_dict[k][1]
    cell = module_dict[k][2]
    fname = module_dict[k][3]
    f = ROOT.TFile.Open(fname)
    g[irr,temp,cell] = f.Get('g_DCRfromCurrent_vs_Vov_%s'%k)
    
for irr in irradiations:
    for cell in [20,25]:
        for temp in temperatures[irr]:
            if ( (irr,temp,cell) not in g.keys() ): continue
            gratio[irr,temp,cell] = ROOT.TGraphErrors()
            gratio[irr,temp,cell].SetLineColor( g[irr,temp,cell].GetLineColor())
            gratio[irr,temp,cell].SetMarkerColor( g[irr,temp,cell].GetMarkerColor())
            gratio[irr,temp,cell].SetMarkerSize(1)
            for i in range(0,g[irr,temp,cell].GetN()):
                x = g[irr,temp,cell].GetPointX(i)
                y = g[irr,temp,cell].GetPointY(i)/g[irr,temperatures[irr][0],cell].Eval(x)
                gratio[irr,temp,cell].SetPoint(i,x,y) 
    


#plot
for irr in irradiations:
    for cell in [20,25]:
        leg = ROOT.TLegend(0.20, 0.75, 0.85, 0.89)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)
        leg.SetTextFont(42)
        leg.SetTextSize(0.04)

        c = ROOT.TCanvas('c_comparison_DCR_%s_%dum_vs_temperature'%(irr,cell), 'c_comparison_DCR_%s_%dum_vs_temperature'%(irr,cell), 1200, 600)
        c.Divide(2,1)
        c.cd(1)
        hPad = ROOT.gPad.DrawFrame(0.,0.,2.,50)
        hPad.SetTitle(";V_{OV}; DCR[GHz]")
        hPad.Draw()
        ROOT.gPad.SetGridx()
        ROOT.gPad.SetGridy()
        for temp in temperatures[irr]:
            if ( (irr,temp,cell) not in g.keys() ): continue
            g[irr,temp,cell].Draw('plsame')
            leg.AddEntry(g[irr,temp,cell], '%s %dum T=%d#circC'%(irr, cell, temp), 'PL')
        leg.Draw()

        c.cd(2)
        hPad2 = ROOT.gPad.DrawFrame(0.,0.,2.,3)
        hPad2.SetTitle(";V_{OV}; ratio")
        hPad2.Draw()
        ROOT.gPad.SetGridx()
        ROOT.gPad.SetGridy()
        for temp in temperatures[irr]:
            if ( (irr,temp,cell) not in gratio.keys() ): continue
            gratio[irr,temp,cell].Draw('plsame')
        #leg.Draw()

        c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/DCR/%s.png'%c.GetName())
        c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/DCR/%s.pdf'%c.GetName())


