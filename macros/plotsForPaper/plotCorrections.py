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
from VovsEff import *

#set the tdr style
tdrstyle.setTDRStyle()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetLabelSize(0.055,'X')
ROOT.gStyle.SetLabelSize(0.055,'Y')
ROOT.gStyle.SetTitleSize(0.072,'X')
ROOT.gStyle.SetTitleSize(0.072,'Y')
ROOT.gStyle.SetTitleOffset(1.05,'X')
ROOT.gStyle.SetTitleOffset(1.1,'Y')
ROOT.gStyle.SetLegendFont(42)
ROOT.gStyle.SetLegendTextSize(0.045)
ROOT.gStyle.SetPadTopMargin(0.07)
ROOT.gStyle.SetPadRightMargin(0.07)
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kWarning

def removeOffset1D(h, offset, hnew):
    for ibin in range(1, h.GetNbinsX()):
        cont = h.GetBinContent(ibin)
        err  = h.GetBinError(ibin)
        if cont == 0 : continue
        hnew.SetBinContent(ibin, cont-offset)
        hnew.SetBinError(ibin, err)

def removeOffset2D(h, offset, hnew):
    for ibin in range(1, h.GetNbinsX()):
        for jbin in range(1, h.GetNbinsY()):
            cont = h.GetBinContent(ibin, jbin)
            err  = h.GetBinError(ibin, jbin)
            if cont == 0 : continue
            hnew.SetBinContent(ibin, jbin, cont)
            hnew.SetBinError(ibin, jbin, err)
    

outdir = '/eos/user/m/malberti/www/MTD/TOFHIR2C/plotsForPaper/'

th = 5
ov = 1.00

# NON-IRRADIATED
#fname1 = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_May2023/ANALYSIS/TOFHIR2C/ModuleCharacterization/moduleCharacterization_step2_HPK_nonIrr_LYSO813_Vov%.2f_T5C.root'%ov
#fname1 = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_May2023/ANALYSIS/TOFHIR2X/ModuleCharacterization/moduleCharacterization_step2_HPK_nonIrr_LYSO813_Vov%.2f_T-30C.root'%ov
fname1 = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_Sep2023/ANALYSIS/TOFHIR2C/RootFiles/moduleCharacterization_step2_HPK_nonIrr_LYSO818_Vov%.2f_angle52_checkGoodBeam_T5C.root'%ov
f1 = ROOT.TFile.Open(fname1)

#hMIPpeak  = f1.Get('h1_energy_bar07L-R_Vov%.2f_th%02d'%(ov,th))
hMIPpeak  = f1.Get('h1_energy_bar07L-R_Vov%.2f_th11'%(ov))
'''
p1TotCorr = f1.Get('p1_deltaT_vs_totRatio_bar07L-R_Vov%.2f_th%02d_energyBin01'%(ov,th))
h2TotCorr = f1.Get('h2_deltaT_vs_totRatio_bar07L-R_Vov%.2f_th%02d_energyBin01'%(ov,th))
p1EnergyCorr = f1.Get('p1_deltaT_vs_energyRatio_bar07L-R_Vov%.2f_th%02d_energyBin01'%(ov,th))
#h2EnergyCorr = f1.Get('h2_deltaT_vs_energyRatio_bar07L-R_Vov%.2f_th%02d_energyBin01'%(ov,th))
p1PhaseCorr = f1.Get('p1_deltaT_totRatioCorr_vs_t1fineMean_bar07L-R_Vov%.2f_th%02d_energyBin01'%(ov,th))
h2PhaseCorr = f1.Get('h2_deltaT_totRatioCorr_vs_t1fineMean_bar07L-R_Vov%.2f_th%02d_energyBin01'%(ov,th))
'''

# remove offset in y
p1TotCorr_0 = f1.Get('p1_deltaT_vs_totRatio_bar07L-R_Vov%.2f_th%02d_energyBin01'%(ov,th))
h2TotCorr_0 = f1.Get('h2_deltaT_vs_totRatio_bar07L-R_Vov%.2f_th%02d_energyBin01'%(ov,th))
p1EnergyCorr_0 = f1.Get('p1_deltaT_vs_energyRatio_bar07L-R_Vov%.2f_th%02d_energyBin01'%(ov,th))
#h2EnergyCorr_0 = f1.Get('h2_deltaT_vs_energyRatio_bar07L-R_Vov%.2f_th%02d_energyBin01'%(ov,th))
p1PhaseCorr_0 = f1.Get('p1_deltaT_energyRatioCorr_vs_t1fineMean_bar07L-R_Vov%.2f_th%02d_energyBin01'%(ov,th))
h2PhaseCorr_0 = f1.Get('h2_deltaT_energyRatioCorr_vs_t1fineMean_bar07L-R_Vov%.2f_th%02d_energyBin01'%(ov,th))

nbinsx = p1TotCorr_0.GetNbinsX()
xmin = p1TotCorr_0.GetBinLowEdge(1)+p1TotCorr_0.GetBinWidth(1)
xmax = p1TotCorr_0.GetBinLowEdge(nbinsx)+p1TotCorr_0.GetBinWidth(nbinsx)
p1TotCorr = ROOT.TH1F('p1TotCorr', '', nbinsx, xmin, xmax)
removeOffset1D(p1TotCorr_0, p1TotCorr_0.GetMean(2), p1TotCorr) 

nbinsx = p1EnergyCorr_0.GetNbinsX()
xmin = p1EnergyCorr_0.GetBinLowEdge(1)+p1EnergyCorr_0.GetBinWidth(1)
xmax = p1EnergyCorr_0.GetBinLowEdge(nbinsx)+p1EnergyCorr_0.GetBinWidth(nbinsx)
p1EnergyCorr = ROOT.TH1F('p1EnergyCorr', '', nbinsx, xmin, xmax)
removeOffset1D(p1EnergyCorr_0, p1EnergyCorr_0.GetMean(2), p1EnergyCorr)

nbinsx = p1PhaseCorr_0.GetNbinsX()
xmin = p1PhaseCorr_0.GetBinLowEdge(1)+p1PhaseCorr_0.GetBinWidth(1)
xmax = p1PhaseCorr_0.GetBinLowEdge(nbinsx)+p1PhaseCorr_0.GetBinWidth(nbinsx)
p1PhaseCorr = ROOT.TH1F('p1PhaseCorr', '', nbinsx, xmin, xmax)
removeOffset1D(p1PhaseCorr_0, p1PhaseCorr_0.GetMean(2), p1PhaseCorr)

nbinsx = h2PhaseCorr_0.GetNbinsX()
nbinsy = h2PhaseCorr_0.GetNbinsY()
xmin = h2PhaseCorr_0.GetXaxis().GetBinLowEdge(1)
xmax = h2PhaseCorr_0.GetXaxis().GetBinLowEdge(nbinsx)+h2PhaseCorr_0.GetXaxis().GetBinWidth(nbinsx)
ymin = h2PhaseCorr_0.GetYaxis().GetBinLowEdge(1) - p1PhaseCorr_0.GetMean(2)
ymax = h2PhaseCorr_0.GetYaxis().GetBinLowEdge(nbinsy)+h2PhaseCorr_0.GetYaxis().GetBinWidth(nbinsy) - p1PhaseCorr_0.GetMean(2)
print(xmin,xmax,ymin,ymax)
h2PhaseCorr = ROOT.TH2F('h2PhaseCorr','', nbinsx, xmin, xmax, nbinsy, ymin, ymax)
removeOffset2D(h2PhaseCorr_0, 0, h2PhaseCorr) 

    
# MIP Peak
c = ROOT.TCanvas('c_MIPpeak','c_MIPpeak', 500, 500)
#c.SetLogy()
#hPad = ROOT.gPad.DrawFrame(0.,0.1,1000.0,hMIPpeak.GetMaximum()*10)
hPad = ROOT.gPad.DrawFrame(0.,0.1,1000.0,hMIPpeak.GetMaximum()*1.05)
hPad.SetTitle(';energy [ADC]; entries')
#hPad.Draw()
ROOT.gPad.SetTicks(1)
hPad.GetXaxis().SetNdivisions(205)
hMIPpeak.GetXaxis().SetNdivisions(205)
hMIPpeak.Draw('same')
fun = hMIPpeak.GetFunction('f_landau_bar07L-R_Vov%.2f_vth1_11'%(ov))
fun.SetLineColor(1)
hMIPpeak.Fit(fun,'RSL','', 280, 450)
fun.Draw('same')
l1 = ROOT.TLine(fun.GetParameter(1)*0.80,0,fun.GetParameter(1)*0.80,hMIPpeak.GetMaximum())
l2 = ROOT.TLine(950,0,950,hMIPpeak.GetMaximum())
l1.SetLineStyle(2)
l2.SetLineStyle(2)
l1.Draw()
l2.Draw()
tl = ROOT.TLatex()
tl.SetNDC()
tl.SetTextFont(42)
tl.SetTextSize(0.045)
tl.SetTextColor(ROOT.kRed)
tl.DrawLatex(0.65,0.82,'#splitline{V_{OV} = %.2f V}{HPK, 25 #mum}'%(ov))
#cms_logo = draw_logo()
#cms_logo.Draw()
c.SaveAs(outdir+'%s.png'%c.GetName())
c.SaveAs(outdir+'%s.pdf'%c.GetName())


# ToT ratio corr
xmin = p1TotCorr_0.GetMean(1)-0.2
xmax = p1TotCorr_0.GetMean(1)+0.2
ymin = p1TotCorr.GetMean(2)-100.
ymax = p1TotCorr.GetMean(2)+100.
c = ROOT.TCanvas('c_totCorr','c_totCorr', 500, 500)
hPad = ROOT.gPad.DrawFrame(xmin, ymin, xmax, ymax)
hPad.SetTitle('; ToT ratio; #Deltat [ps]')
ROOT.gPad.SetTicks(1)
#h2TotCorr.Draw('colz same')
p1TotCorr.Draw('same')
fun = ROOT.TF1('fun','pol3')
fun.SetLineColor(2)
p1TotCorr.Fit(fun,'QRS', '', p1TotCorr_0.GetMean()-3*p1TotCorr_0.GetRMS(), p1TotCorr_0.GetMean()+3*p1TotCorr_0.GetRMS())
tl.DrawLatex(0.65,0.82,'#splitline{V_{OV} = %.2f V}{HPK, 25 #mum}'%(ov))
#cms_logo = draw_logo()
#cms_logo.Draw()
c.SaveAs(outdir+'%s.png'%c.GetName())
c.SaveAs(outdir+'%s.pdf'%c.GetName())

# Energy ratio corr
xmin = p1EnergyCorr_0.GetMean(1)-0.22
xmax = p1EnergyCorr_0.GetMean(1)+0.22
ymin = p1EnergyCorr.GetMean(2)-100
ymax = p1EnergyCorr.GetMean(2)+100.
c = ROOT.TCanvas('c_energyCorr','c_energyCorr', 500, 500)
hPad = ROOT.gPad.DrawFrame(xmin, ymin , xmax, ymax)
hPad.SetTitle(';energy ratio; #Deltat [ps]')
hPad.GetXaxis().SetNdivisions(205)
ROOT.gPad.SetTicks(1)
#h2EnergyCorr.Draw('colz same')
p1EnergyCorr.Draw('same')
fun = ROOT.TF1('fun','pol3')
fun.SetLineColor(2)
p1EnergyCorr.Fit(fun,'QRS', '', p1EnergyCorr_0.GetMean()-3*p1EnergyCorr_0.GetRMS(), p1EnergyCorr_0.GetMean()+3*p1EnergyCorr_0.GetRMS())
tl.DrawLatex(0.65,0.82,'#splitline{V_{OV} = %.2f V}{HPK, 25 #mum}'%(ov))
#cms_logo = draw_logo()
#cms_logo.Draw()
c.SaveAs(outdir+'%s.png'%c.GetName())
c.SaveAs(outdir+'%s.pdf'%c.GetName())


# phase corr
xmin = 300
xmax = 840
ymin = p1PhaseCorr.GetMean(2)-400
ymax = p1PhaseCorr.GetMean(2)+400
c = ROOT.TCanvas('c_phaseCorr','c_phaseCorr', 500, 500)
hPad = ROOT.gPad.DrawFrame(xmin, ymin , xmax, ymax)
hPad.SetTitle('; phase [a.u.]; #Deltat [ps]')
hPad.GetXaxis().SetNdivisions(205)
ROOT.gPad.SetTicks(1)
h2PhaseCorr.Draw('col same')
p1PhaseCorr.Draw('same')
tl.DrawLatex(0.65,0.82,'#splitline{V_{OV} = %.2f V}{HPK, 25 #mum}'%(ov))
#cms_logo = draw_logo()
#cms_logo.Draw()
c.SaveAs(outdir+'%s.png'%c.GetName())
c.SaveAs(outdir+'%s.pdf'%c.GetName())
