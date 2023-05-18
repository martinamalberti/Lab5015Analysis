#! /usr/bin/env python
import os
import shutil
import glob
import math
import array
import sys
import time
import argparse
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
ROOT.gStyle.SetTitleOffset(1.0,'X')
ROOT.gStyle.SetTitleOffset(1.05,'Y')
ROOT.gStyle.SetLegendFont(42)
ROOT.gStyle.SetLegendTextSize(0.030)
ROOT.gStyle.SetPadTopMargin(0.07)
ROOT.gStyle.SetPadBottomMargin(0.15)
ROOT.gStyle.SetPadLeftMargin(0.15)
ROOT.gROOT.SetBatch(False)
ROOT.gErrorIgnoreLevel = ROOT.kWarning

inputdir = '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/'
outdir   = '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/'

fnames = OrderedDict()

fnames[('HPK_2E14_LYSO815_T-40C')] = inputdir+'/timeResolution_2E14_20um_25um_T2/plots_timeResolution_2E14_20um_25um_T2_TBMay23.root'
fnames[('HPK_2E14_LYSO815_T-35C')] = inputdir+'/timeResolution_2E14_20um_25um_T2/plots_timeResolution_2E14_20um_25um_T2_TBMay23.root'
fnames[('HPK_2E14_LYSO815_T-30C')] = inputdir+'/timeResolution_2E14_20um_25um_T2/plots_timeResolution_2E14_20um_25um_T2_TBMay23.root'

fnames[('HPK_2E14_LYSO825_T-40C')] = inputdir+'/timeResolution_2E14_20um_25um_T2/plots_timeResolution_2E14_20um_25um_T2_TBMay23.root'
fnames[('HPK_2E14_LYSO825_T-35C')] = inputdir+'/timeResolution_2E14_20um_25um_T2/plots_timeResolution_2E14_20um_25um_T2_TBMay23.root'
fnames[('HPK_2E14_LYSO825_T-30C')] = inputdir+'/timeResolution_2E14_20um_25um_T2/plots_timeResolution_2E14_20um_25um_T2_TBMay23.root'


#fnames[('HPK_1E14_LYSO819_T-22C')] = inputdir+'/timeResolution_1E14_25um_T1/plots_timeResolution_1E14_25um_T1_TBMay23.root'
#fnames[('HPK_1E14_LYSO819_T-27C')] = inputdir+'/timeResolution_1E14_25um_T1/plots_timeResolution_1E14_25um_T1_TBMay23.root'
#fnames[('HPK_1E14_LYSO819_T-32C')] = inputdir+'/timeResolution_1E14_25um_T1/plots_timeResolution_1E14_25um_T1_TBMay23.root'
#fnames[('HPK_1E14_LYSO819_T-37C')] = inputdir+'/timeResolution_1E14_25um_T1/plots_timeResolution_1E14_25um_T1_TBMay23.root'

#fnames[('HPK_1E13_LYSO829_T-19C')] = inputdir+'/timeResolution_1E13_25um_T1/plots_timeResolution_1E13_25um_T1_TBMay23.root'


gAll = ROOT.TGraphErrors()
gAll.SetMarkerSize(0.01)
gAll.SetMarkerColor(0)
gAll.SetLineColor(0)
g = OrderedDict()


for k in fnames.keys():
    print k
    f = ROOT.TFile.Open(fnames[k])
    g[k] = f.Get('g_DCRNpe_vs_DCR_average_%s'%k)
    g[k].SetMarkerSize(1)
    
    if ( '1E14' in k):
        g[k].SetMarkerStyle(30)

    if ( '1E13' in k):
        g[k].SetMarkerStyle(21)
            
    for i in range(0, g[k].GetN()):
        gAll.SetPoint(gAll.GetN(), g[k].GetPointX(i), g[k].GetPointY(i))
        gAll.SetPointError(gAll.GetN()-1, g[k].GetErrorX(i), g[k].GetErrorY(i))

# fit dcr contrib
fitFun_tRes_dcr = ROOT.TF1('fitFun_tRes_dcr','[1] * pow(x/30.,[0])', 0,100)
fitFun_tRes_dcr.SetParameter(0,0.5)
fitFun_tRes_dcr.SetParameter(1,40.)
fitFun_tRes_dcr.SetLineColor(1)
gAll.Fit(fitFun_tRes_dcr,'QRS')

interval = ROOT.TH1D('interval','',100,0,80)
interval.SetMarkerSize(0.1)
ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(interval, 0.68)
interval.SetFillColorAlpha(7,0.2);


leg = ROOT.TLegend(0.50,0.18,0.89,0.58)
leg.SetBorderSize(0)
leg.SetFillStyle(0)

#c = ROOT.TCanvas('c_timeResolution_DCR_all_TBMay23','', 700, 600)
#c = ROOT.TCanvas('c_timeResolution_DCR_1E13_1E14_TBMay23','', 700, 600)
c = ROOT.TCanvas('c_timeResolution_DCR_2E14_TBMay23','', 700, 600)
hdummy = ROOT.TH2F('hdummy','hdummy',100,0.0,80.0,100,0,80)
hdummy.GetXaxis().SetTitle('DCR [GHz]')
hdummy.GetYaxis().SetTitle('Npe/6000 #times #sigma_{t}^{DCR} [ps]')
hdummy.Draw()
interval.Draw("e3 same");
gAll.Draw('psame')
for k in g.keys():
    g[k].Draw('psame')
    leg.AddEntry(g[k],'%s'%k,'PL')
leg.Draw()
c.Update()
ps = gAll.FindObject("stats")
ps.SetBorderSize(1)
ps.SetX1NDC(0.65) # new y start position
ps.SetX2NDC(0.92)# new y end position
ps.SetY1NDC(0.80) # new y start position
ps.SetY2NDC(0.92)# new y end position
ps.Draw('same')
c.SaveAs(outdir+'/'+c.GetName()+'.png')
c.SaveAs(outdir+'/'+c.GetName()+'.pdf')
