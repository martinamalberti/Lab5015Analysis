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
ROOT.gStyle.SetTitleOffset(1.05,'X')
ROOT.gStyle.SetTitleOffset(1.1,'Y')
ROOT.gStyle.SetLegendFont(42)
ROOT.gStyle.SetLegendTextSize(0.040)
ROOT.gStyle.SetPadTopMargin(0.07)
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kWarning   


#outdir = '/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_Oct21/'
outdir = '/var/www/html/TOFHIR2X/MTDTB_CERN_June22/'


irr = 'unirr'
#irr = '2E14'

sipmTypes = ['HPK_nonIrr_LYSO528','FBK_nonIrr_LYSO800', 'FBK_nonIrr_LYSO522']
if (irr == '2E14'):
    sipmTypes = ['HPK_2E14_LYSO796_T-40C']

fnames = {'HPK_nonIrr_LYSO528' : '../plots/HPK_nonIrr_LYSO528_T10C_summary.root',
          'FBK_nonIrr_LYSO800' : '../plots/FBK_nonIrr_LYSO800_T10C_summary.root',
          'FBK_nonIrr_LYSO522' : '../plots/FBK_nonIrr_LYSO522_T10C_summary.root',
          'HPK_2E14_LYSO796_T-40C' : '../plots/HPK_2E14_LYSO796_T-40C_summary.root',
          'FBK_2E14_T-40' : '../plots/FBK_2E14_52deg_T-40C_summary.root'}

labels = {'HPK_nonIrr_LYSO528' : 'HPK + LYSO528 (prod5, type2)',
          'FBK_nonIrr_LYSO800' : 'FBK + LYSO800 (prod5, type2)',
          'FBK_nonIrr_LYSO522' : 'FBK + LYSO522 (prod5, type1)',
          'HPK_2E14_LYSO796_T-40C' : 'HPK + LYSO796 (prod10 opt) - T=-40#circC'}

VovsEff = {}
VovsEff['HPK_nonIrr_LYSO528'] = { 1.50 : 1.50 ,
                                  2.50 : 2.50 ,
                                  3.50 : 3.50 ,
                                  5.00 : 5.00 }

VovsEff['FBK_nonIrr_LYSO800'] = { 1.50 : 1.50 ,
                                 2.00 : 2.00 ,
                                 3.00 : 3.00 ,
                                 3.50 : 3.50 ,
                                 4.00 : 4.00 ,
                                 7.00 : 7.00 }

VovsEff['FBK_nonIrr_LYSO522'] = { 1.50 : 1.50 ,
                                 2.00 : 2.00 ,
                                 3.00 : 3.00 ,
                                 3.50 : 3.50 ,
                                 4.00 : 4.00 }

VovsEff['HPK_2E14_LYSO796_T-40C'] = { 1.10 : 1.02,
                                      1.20 : 1.10,
                                      1.30 : 1.17,
                                      1.50 : 1.31,
                                      1.70 : 1.43,
                                      1.90 : 1.53,
                                      2.10 : 1.60,
                                      2.50 : 1.71}

VovsEff['FBK_2E14_T-40'] = { 1.70 : 1.57,
                            2.00  : 1.78,
                            2.50  : 2.06,
                            3.00  : 2.27,
                            3.50  : 2.40}


g = {}
Vovs = {}
for sipm in sipmTypes:
    f = ROOT.TFile.Open(fnames[sipm])
    g[sipm] = ROOT.TGraphErrors()
    Vovs[sipm] = []
    listOfKeys = [key.GetName().replace('g_deltaT_energyRatioCorr_bestTh_vs_bar_','') for key in ROOT.gDirectory.GetListOfKeys() if key.GetName().startswith('g_deltaT_energyRatioCorr_bestTh_vs_bar_')]
    for k in listOfKeys:
        Vovs[sipm].append( float (k[3:7]) )
    Vovs[sipm].sort()    
    print sipm, Vovs[sipm]
    for i,vov in enumerate(Vovs[sipm]):
        gg = f.Get('g_deltaT_energyRatioCorr_bestTh_vs_bar_Vov%.02f_enBin01'%(vov))
        fitFun = ROOT.TF1('fitFun','pol0',0,16)
        #fitFun.SetRange(3,12)
        gg.Fit(fitFun,'QR')
        print sipm, VovsEff[sipm][vov], fitFun.GetParameter(0)
        g[sipm].SetPoint(g[sipm].GetN(), VovsEff[sipm][vov], fitFun.GetParameter(0))
        #g[sipm].SetPointError(g[sipm].GetN()-1, 0, fitFun.GetParError(0))
        g[sipm].SetPointError( g[sipm].GetN()-1, 0, gg.GetRMS(2) )# use RMS as error on the points
        #g[sipm].SetPoint(g[sipm].GetN(), VovsEff[sipm][vov], gg.GetMean(2))
        #g[sipm].SetPointError(g[sipm].GetN()-1, 0, gg.GetRMS(2)/math.sqrt(gg.GetN()))
        
c1 =  ROOT.TCanvas('c_timeResolution_bestTh_vs_Vov','c_timeResolution_bestTh_vs_Vov',600,600)
c1.SetGridy()
c1.cd()
jsipm= 1
if len(sipmTypes)==1: jsipm = 0 
n = g[sipmTypes[jsipm]].GetN()
xmax = g[sipmTypes[jsipm]].GetX()[n-1] + 0.5
xmin = g[sipmTypes[jsipm]].GetX()[0]   - 0.5 
ymin = 70
ymax = 180
if (irr=='unirr'):
    ymin = 20
    ymax = 100
hdummy = ROOT.TH2F('hdummy','',100,xmin,xmax,100,ymin,ymax)
hdummy.GetXaxis().SetTitle('V_{OV}^{eff} [V]')
hdummy.GetYaxis().SetTitle('#sigma_{t} [ps]')
hdummy.Draw()
#leg = ROOT.TLegend(0.15,0.60,0.45,0.89)
leg = ROOT.TLegend(0.15,0.74,0.80,0.92)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
for i,sipm in enumerate(sipmTypes):
    g[sipm].SetMarkerStyle(20+i)
    g[sipm].SetMarkerSize(1)
    g[sipm].SetMarkerColor(2+i*2)
    g[sipm].SetLineColor(2+i*2)
    g[sipm].SetLineStyle(1)
    g[sipm].SetLineWidth(1)
    g[sipm].Draw('plsame')
    leg.AddEntry( g[sipm], labels[sipm], 'PL')
leg.Draw('same')

latex = ROOT.TLatex(0.65,0.68,'%s'%irr)
if (irr == 'unirr'):
    latex = ROOT.TLatex(0.65,0.68,'non-irradiated')
latex.SetNDC()
latex.SetTextSize(0.045)
latex.SetTextFont(42)
latex.Draw('same')

for c in [c1]:
    c.SaveAs(outdir+c.GetName()+'_%s.png'%irr)
    c.SaveAs(outdir+c.GetName()+'_%s.pdf'%irr)


outfile = ROOT.TFile('timeResolution_averaged_vs_Vov_%s_TBJune22.root'%irr,'recreate')
for sipm in sipmTypes:
    g[sipm].Write('g_%s'%sipm)
outfile.Close()
    
#raw_input('OK?')
