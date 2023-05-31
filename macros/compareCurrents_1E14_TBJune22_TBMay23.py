#! /usr/bin/env python
import os
import shutil
import glob
import math
import array
import sys
import time
import argparse

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
ROOT.gStyle.SetLegendTextSize(0.040)
ROOT.gStyle.SetPadTopMargin(0.07)
ROOT.gStyle.SetPadBottomMargin(0.15)
ROOT.gStyle.SetPadLeftMargin(0.15)
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kWarning

confs = {'HPK_1E14_LYSO844_T-30C', 'HPK_1E14_LYSO802_T-35C'}

fnames = {'HPK_1E14_LYSO844_T-30C': '../logIVEff_TOFHIR2C.root',
          'HPK_1E14_LYSO802_T-35C': '../logIVEff_TBJune2022.root',
}
          

plotAttrs = {'HPK_1E14_LYSO844_T-30C' : [ 4, 20, 'HPK(15#mum, 1E14)+LYSO844(prod10) - TB May23' ],
             'HPK_1E14_LYSO802_T-35C' : [ 2, 20, 'HPK(15#mum, 1E14)+LYSO802(prod9) - TB June22' ] ,
}

gA = {}
gB = {}
g  = {}
gRatio= {}




for conf in confs:
    f = ROOT.TFile.Open(fnames[conf])
    print(conf)
    lyso = conf.split('_')[2]
    sipm = conf.split('_')[0]+'_'+conf. split('_')[1]
    temp = conf.split('_')[3][:-1]
    g1 =  f.Get('g_IVEff_ch_%s_%s_%s_ALDOA'%(sipm, lyso, temp))
    g2 =  f.Get('g_IVEff_ch_%s_%s_%s_ALDOB'%(sipm, lyso, temp))
    gA[conf] = ROOT.TGraphErrors()
    gB[conf] = ROOT.TGraphErrors()
    g[conf] = ROOT.TGraphErrors()
    for i in range(0, g1.GetN()):
        ov = g1.GetPointX(i)
        currentA = g1.Eval(ov)/1000. #uA -> mA
        currentB = g2.Eval(ov)/1000. #uA -> mA
        current = 0.5*(currentA+currentB)
        gA[conf].SetPoint(i, ov, currentA)
        gB[conf].SetPoint(i, ov, currentB)
        g[conf].SetPoint(i, ov, current)
        #g[conf].SetPointError(i, 0, 0.5*abs(currentA-currentB))

leg = ROOT.TLegend(0.2, 0.2, 0.4, 0.39)
leg.SetBorderSize(0)

c1 = ROOT.TCanvas('c_IV_15um_1E14_TBJune2022_TBMay2023','c_IV_15um_1E14_TBJune2022_TBMay2023',700,600)
hPad1 = ROOT.gPad.DrawFrame(0., 0.0001, 2.5, 20.0)
#hPad1 = ROOT.gPad.DrawFrame(0., 0.0, 2.5, 2.0)
hPad1.SetTitle(";V_{ov}^{eff} [V]; I_{array} / 16 [mA]")
hPad1.Draw()
ROOT.gPad.SetLogy()
ROOT.gPad.SetTickx()
ROOT.gPad.SetTicky()
for conf in confs:
    gA[conf].SetLineColor(plotAttrs[conf][0])
    gB[conf].SetLineColor(plotAttrs[conf][0])
    g[conf].SetLineColor(plotAttrs[conf][0])
    gA[conf].SetMarkerColor(plotAttrs[conf][0])
    gB[conf].SetMarkerColor(plotAttrs[conf][0])
    g[conf].SetMarkerColor(plotAttrs[conf][0])
    gA[conf].SetLineStyle(2)
    gB[conf].SetLineStyle(2)
    g[conf].SetLineStyle(1)
    gA[conf].SetMarkerStyle(plotAttrs[conf][1])
    gB[conf].SetMarkerStyle(24)
    gA[conf].Draw('plsame')
    gB[conf].Draw('plsame')
    g[conf].Draw('lsame')
    leg.AddEntry(g[conf], '%s'%plotAttrs[conf][2],'L')
leg.Draw()
c1.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2C/MTDTB_CERN_May23/IV/conf_38.00/'+c1.GetName()+'.png')
c1.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2C/MTDTB_CERN_May23/IV/conf_38.00/'+c1.GetName()+'.pdf')


c2 = ROOT.TCanvas('c_IV_ratio_15um_1E14_TBJune2022_TBMay2023','c_IV_ratio_15um_1E14_TBJune2022_TBMay2023',700,600)
hPad2 = ROOT.gPad.DrawFrame(0., 0., 2.5, 2)
hPad2.SetTitle(";V_{ov}^{eff} [V]; ratio")
hPad2.Draw()
ROOT.gPad.SetTickx()
ROOT.gPad.SetTicky()
for conf in confs:
    gRatio[conf] = ROOT.TGraphErrors()
    for i in range(0, g[conf].GetN()):
        ov = g[conf].GetPointX(i)
        r  = g[conf].Eval(ov)/g['HPK_1E14_LYSO802_T-35C'].Eval(ov) 
        gRatio[conf].SetPoint(i, ov, r)
    gRatio[conf].SetLineColor(plotAttrs[conf][0])
    gRatio[conf].SetLineWidth(2)
    gRatio[conf].Draw('lsame')
leg.Draw()

c2.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2C/MTDTB_CERN_May23/IV/conf_38.00/'+c2.GetName()+'.png')
c2.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2C/MTDTB_CERN_May23/IV/conf_38.00/'+c2.GetName()+'.pdf')


