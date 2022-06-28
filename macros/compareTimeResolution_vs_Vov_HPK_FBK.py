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


#irr = 'unirr'
irr = '1E14'
#irr = '2E14'

sipmTypes = ['HPK_nonIrr_LYSO528','FBK_nonIrr_LYSO800', 'FBK_nonIrr_LYSO522']
if (irr == '1E14'):
    sipmTypes = ['HPK_1E14_LYSO802_T-40C','HPK_1E14_LYSO802_T-35C','FBK_1E14_LYSO803_T-40C','FBK_1E14_LYSO803_T-35C']
    #sipmTypes = ['HPK_1E14_LYSO802_T-40C','HPK_1E14_LYSO802_T-35C']
if (irr == '2E14'):
    sipmTypes = ['HPK_2E14_LYSO796_T-40C','HPK_2E14_LYSO796_T-35C','FBK_2E14_LYSO797_T-40C','FBK_2E14_LYSO797_T-35C']
    #sipmTypes = ['HPK_2E14_LYSO796_T-40C','HPK_2E14_LYSO796_T-35C']

fnames = {'HPK_nonIrr_LYSO528' : '../plots/HPK_nonIrr_LYSO528_T10C_summary.root',
          'FBK_nonIrr_LYSO800' : '../plots/FBK_nonIrr_LYSO800_T10C_summary.root',
          'FBK_nonIrr_LYSO522' : '../plots/FBK_nonIrr_LYSO522_T10C_summary.root',
          'HPK_1E14_LYSO802_T-40C' : '../plots/HPK_1E14_LYSO802_T-40C_summary.root',
          'HPK_1E14_LYSO802_T-35C' : '../plots/HPK_1E14_LYSO802_T-35C_summary.root',
          'HPK_2E14_LYSO796_T-40C' : '../plots/HPK_2E14_LYSO796_T-40C_summary.root',
          'HPK_2E14_LYSO796_T-35C' : '../plots/HPK_2E14_LYSO796_T-35C_summary.root',
          'FBK_1E14_LYSO803_T-40C' : '../plots/FBK_1E14_LYSO803_T-40C_summary.root',
          'FBK_1E14_LYSO803_T-35C' : '../plots/FBK_1E14_LYSO803_T-35C_summary.root',
          'FBK_2E14_LYSO797_T-40C' : '../plots/FBK_2E14_LYSO797_T-40C_summary.root',
          'FBK_2E14_LYSO797_T-35C' : '../plots/FBK_2E14_LYSO797_T-35C_summary.root'}

labels = {'HPK_nonIrr_LYSO528' : 'HPK + LYSO528 (prod5, type2)',
          'FBK_nonIrr_LYSO800' : 'FBK + LYSO800 (prod5, type2)',
          'FBK_nonIrr_LYSO522' : 'FBK + LYSO522 (prod5, type1)',
          'HPK_1E14_LYSO802_T-40C' : 'HPK + LYSO802 (prod9 opt) - T=-40#circC',
          'HPK_1E14_LYSO802_T-35C' : 'HPK + LYSO802 (prod9 opt) - T=-35#circC',
          'HPK_2E14_LYSO796_T-40C' : 'HPK + LYSO796 (prod10 opt) - T=-40#circC',
          'HPK_2E14_LYSO796_T-35C' : 'HPK + LYSO796 (prod10 opt) - T=-35#circC',
          'FBK_1E14_LYSO803_T-40C' : 'FBK + LYSO803 (prod9 opt) - T=-40#circC',
          'FBK_1E14_LYSO803_T-35C' : 'FBK + LYSO803 (prod9 opt) - T=-35#circC',
          'FBK_2E14_LYSO797_T-40C' : 'FBK + LYSO797 (prod10 opt) - T=-40#circC',
          'FBK_2E14_LYSO797_T-35C' : 'FBK + LYSO797 (prod10 opt) - T=-35#circC'}

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

VovsEff['HPK_2E14_LYSO796_T-35C'] = { 0.90 : 0.83,
                                      1.10 : 0.99,
                                      1.25 : 1.09,                                                                  
                                      1.40 : 1.19,  
                                      1.60 : 1.31,   
                                      1.80 : 1.40,   
                                      2.00 : 1.48,
                                      2.40 : 1.59}  

VovsEff['HPK_1E14_LYSO802_T-40C'] = { 1.10 : 1.06,
                                      1.25 : 1.19,
                                      1.40 : 1.32,
                                      1.60 : 1.49,
                                      1.80 : 1.65,
                                      2.00 : 1.80,
                                      2.40 : 2.06,
                                      2.80 : 2.26} 

VovsEff['HPK_1E14_LYSO802_T-35C'] = { 1.10 : 1.04,
                                      1.25 : 1.17,
                                      1.40 : 1.30,
                                      1.60 : 1.46,
                                      1.80 : 1.61,
                                      2.00 : 1.74,
                                      2.40 : 1.99,
                                      3.10 : 2.28}

VovsEff['FBK_1E14_LYSO803_T-35C'] = { 1.10 : 1.07,
                                      1.25 : 1.21,
                                      1.40 : 1.34,
                                      1.60 : 1.52,
                                      1.80 : 1.70,
                                      2.00 : 1.86,
                                      2.40 : 2.18,
                                      2.80 : 2.45,
                                      3.60 : 2.89}           

VovsEff['FBK_1E14_LYSO803_T-40C'] = { 1.10 : 1.07,
                                      1.25 : 1.21,
                                      1.40 : 1.35,
                                      1.60 : 1.53,
                                      1.80 : 1.71,
                                      2.00 : 1.88,
                                      2.40 : 2.21,
                                      2.80 : 2.49,
                                      3.60 : 2.93}


VovsEff['FBK_2E14_LYSO797_T-35C'] = { 1.20 : 1.10,
                                      1.40 : 1.26,
                                      1.60 : 1.41,
                                      1.80 : 1.55,
                                      2.00 : 1.67,
                                      2.40 : 1.87,
                                      2.80 : 2.02,
                                      3.00 : 2.08}


VovsEff['FBK_2E14_LYSO797_T-40C'] = { 1.20 : 1.12,
                                      1.40 : 1.29,
                                      1.60 : 1.44,
                                      1.80 : 1.58,
                                      2.00 : 1.71,
                                      2.40 : 1.92,
                                      2.80 : 2.08,
                                      3.00 : 2.14}


# plots attr: markerStyle, color
attrs = { 'HPK_2E14_LYSO796_T-35C' : [ 20, ROOT.kRed], 
          'HPK_2E14_LYSO796_T-40C' : [ 24, ROOT.kRed], 
          'HPK_1E14_LYSO802_T-35C' : [ 21, ROOT.kRed-4], 
          'HPK_1E14_LYSO802_T-40C' : [ 25, ROOT.kRed-4], 
          'FBK_2E14_LYSO797_T-35C' : [ 20, ROOT.kBlue], 
          'FBK_2E14_LYSO797_T-40C' : [ 24, ROOT.kBlue], 
          'FBK_1E14_LYSO803_T-35C' : [ 21, ROOT.kBlue-4], 
          'FBK_1E14_LYSO803_T-40C' : [ 25, ROOT.kBlue-4]}


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
    if ('FBK' in sipm and 'E14' in sipm): 
        if (1.10 in Vovs[sipm]) : Vovs[sipm].remove(1.10)
        if (1.25 in Vovs[sipm]) : Vovs[sipm].remove(1.25)

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
jsipm = len(sipmTypes)-1
if len(sipmTypes)==1: jsipm = 0 
n = g[sipmTypes[jsipm]].GetN()
xmax = g[sipmTypes[jsipm]].GetX()[n-1] + 0.5
xmin = g[sipmTypes[jsipm]].GetX()[0]   - 0.5 
ymin = 60
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
    g[sipm].SetMarkerStyle(attrs[sipm][0])
    g[sipm].SetMarkerSize(1)
    g[sipm].SetMarkerColor(attrs[sipm][1])
    g[sipm].SetLineColor(attrs[sipm][1])
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
