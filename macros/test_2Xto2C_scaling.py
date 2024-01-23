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

srScale = 1.2

labels = ['HPK_2E14_LYSO815_T-35C', 'HPK_2E14_LYSO825_T-35C']

outdir = '/eos/user/m/malberti/www/MTD/TOFHIR2C/MTDTB_CERN_May23/Test_2Xto2C/'

fnames = { '2X' : '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/timeResolution_2E14_20um_25um_T2_v2/plots_timeResolution_2E14_20um_25um_T2_TBMay23_TOFHIR2X.root',
           '2C' : '/eos/user/m/malberti/www/MTD/TOFHIR2C/MTDTB_CERN_May23/timeResolution_2E14_20um_25um_T2_v2/plots_timeResolution_2E14_20um_25um_T2_TBMay23_TOFHIR2C.root'
}

plotAttrs = { '2X' : [20, ROOT.kRed,  'TOFHIR2X'],
              '2C' : [21, ROOT.kGreen+2,'TOFHIR2C'],
}


gNoise = {}
gStoch = {}
gDCR = {}
gSR = {}
gData = {}
gData_scaled = {}
f = {}

for tofhir in ['2X','2C']:
    f[tofhir] = ROOT.TFile.Open(fnames[tofhir])
    suffix = ''
    if (tofhir == '2C'): suffix = '_TOFHIR2C'
    for label in labels:
        gNoise[tofhir, label] = f[tofhir].Get('g_Noise_vs_Vov_average_%s'%(label+suffix))
        gStoch[tofhir, label] = f[tofhir].Get('g_Stoch_vs_Vov_average_%s'%(label+suffix))
        gDCR[tofhir, label]   = f[tofhir].Get('g_DCR_vs_Vov_average_%s'%(label+suffix))
        gSR[tofhir, label]    = f[tofhir].Get('g_SR_vs_Vov_average_%s'%(label+suffix))
        gData[tofhir, label] = f[tofhir].Get('g_data_vs_Vov_average_%s'%(label+suffix))
        gData_scaled[tofhir, label] = ROOT.TGraphErrors()
    
        # scale noise 2X --> 2C
        if (tofhir == '2X'):
            for i in range(0, gData[tofhir, label].GetN()):
                vov = gData[tofhir, label].GetX()[i]
                s_data = gData[tofhir, label].Eval(vov)
                s_noise = gNoise[tofhir, label].Eval(vov)
                s_stoch_dcr = math.sqrt(s_data*s_data - s_noise*s_noise)
                #s_stoch = gStoch[tofhir, label].Eval(vov)
                #s_dcr = gDCR[tofhir, label].Eval(vov)
                #s_stoch_dcr = math.sqrt(s_stoch*s_stoch+s_dcr*s_dcr)
                sr = gSR[tofhir, label].Eval(vov)
                s_noise_scaled = sigma_noise(sr*srScale, '2C')
                s_tot = math.sqrt(s_noise_scaled*s_noise_scaled + s_stoch_dcr*s_stoch_dcr)
                s_tot_up = math.sqrt(s_noise_scaled*s_noise_scaled*1.05*1.05 + s_stoch_dcr*s_stoch_dcr) # assume 5% error on noise estimation (... to be checked)
                s_tot_down = math.sqrt(s_noise_scaled*s_noise_scaled*0.95*0.95 + s_stoch_dcr*s_stoch_dcr)
                gData_scaled[tofhir, label].SetPoint(i, vov, s_tot)
                gData_scaled[tofhir, label].SetPointError(i, 0, abs(s_tot_up-s_tot_down)/2)
        
                
# plot
for label in labels:
    c = ROOT.TCanvas('c_timeResolution_%s_scaling2Xto2C'%label,'c_timeResolution_%s_scaling2Xto2C'%label, 600, 500)
    leg = ROOT.TLegend(0.50, 0.65, 0.89, 0.89)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.045)
    hPad = ROOT.gPad.DrawFrame(0.,40.,1.8,110.)
    hPad.SetTitle(";V_{OV} [V];time resolution [ps]")
    hPad.Draw()
    ROOT.gPad.SetTicks(1)
    for tofhir in ['2X','2C']:
        suffix = ''
        if (tofhir == '2C'): suffix = '_TOFHIR2C'
        gData[tofhir,label].SetMarkerSize(1)
        gData[tofhir,label].SetMarkerStyle(plotAttrs[tofhir][0])
        gData[tofhir,label].SetMarkerColor(plotAttrs[tofhir][1])
        gData[tofhir,label].SetLineColor(plotAttrs[tofhir][1])
        gData[tofhir,label].Draw('plsame')
        leg.AddEntry(gData[tofhir,label], '%s'%plotAttrs[tofhir][2],'PL')
        if (tofhir == '2X'):
            gData_scaled[tofhir,label].SetLineColor(plotAttrs['2C'][1]+1)
            gData_scaled[tofhir,label].SetMarkerColor(plotAttrs['2C'][1]+1)
            gData_scaled[tofhir,label].SetMarkerStyle(24)
            gData_scaled[tofhir,label].SetMarkerSize(1.1)
            gData_scaled[tofhir,label].SetLineStyle(2)
            gData_scaled[tofhir,label].SetFillStyle(1)
            gData_scaled[tofhir,label].SetFillColorAlpha(plotAttrs['2C'][1]+1, 0.2)            
            leg.AddEntry(gData_scaled[tofhir,label], '%s - scaled'%plotAttrs['2C'][2],'FL')
            gData_scaled[tofhir,label].Draw('E3plsame')
    gData_scaled['2X',label].Draw('plsame')
    leg.Draw()

    tl2 = ROOT.TLatex()
    tl2.SetNDC()
    tl2.SetTextFont(42)
    tl2.SetTextSize(0.045)

    tl = ROOT.TLatex()
    tl.SetNDC()
    tl.SetTextFont(42)
    tl.SetTextSize(0.045)
    tl.DrawLatex(0.58,0.20,'2 #times 10^{14} 1 MeV n_{eq}/cm^{2}')

    cms_logo = draw_logo()
    cms_logo.Draw()

    c.SaveAs(outdir+'%s.png'%c.GetName())
    c.SaveAs(outdir+'%s.pdf'%c.GetName())




