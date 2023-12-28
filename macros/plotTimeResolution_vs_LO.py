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
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetLabelSize(0.05,'X')
ROOT.gStyle.SetLabelSize(0.05,'Y')
ROOT.gStyle.SetTitleSize(0.06,'X')
ROOT.gStyle.SetTitleSize(0.06,'Y')
ROOT.gStyle.SetTitleOffset(1.05,'X')
ROOT.gStyle.SetTitleOffset(1.15,'Y')
ROOT.gStyle.SetLegendFont(42)
ROOT.gStyle.SetLegendTextSize(0.045)
ROOT.gStyle.SetPadTopMargin(0.07)
ROOT.gStyle.SetPadRightMargin(0.1)
ROOT.gStyle.SetPadLeftMargin(0.15)

ROOT.gROOT.SetBatch(True)
#ROOT.gROOT.SetBatch(False)
ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(1)
ROOT.gStyle.SetFitFormat('6.3g')

from SiPM import *

#sipmTypes = ['FBK+LYSO524', 'FBK+LYSO800','FBK+LYSO522', 'HPK+LYSO528']
sipmTypes = ['FBK+LYSO522']

fLO_L = {}
fLO_R = {}
fRes = {}
fRes2 = {}

fNames = { 'FBK+LYSO524': '../plots/FBK_nonIrr_LYSO524_T10C_summary.root',
           'FBK+LYSO800': '../plots/FBK_nonIrr_LYSO800_T10C_summary.root',
           'FBK+LYSO522': '../plots/FBK_nonIrr_LYSO522_T10C_summary.root',
           'HPK+LYSO528': '../plots/HPK_nonIrr_LYSO528_T10C_summary.root'}

fNames2 = {'FBK+LYSO524': '/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_Vov_FBK_nonIrr_Types/plots_timeResolution_FBK_nonIrr_TBJune22.root',
           'FBK+LYSO800': '/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_Vov_FBK_nonIrr_Types/plots_timeResolution_FBK_nonIrr_TBJune22.root',
           'FBK+LYSO522': '/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_Vov_FBK_nonIrr_Types/plots_timeResolution_FBK_nonIrr_TBJune22.root',
           'HPK+LYSO528': '/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_Vov_HPK_FBK_nonIrr/plots_timeResolution_HPK_FBK_nonIrr_TBJune22.root'}

fNamesLO_L = { 'FBK+LYSO522' : './LOmeasurements/Npe_LYSO522_SiPM_1-140_GLUE.root',
               'FBK+LYSO800' : './LOmeasurements/Npe_LYSO800_SiPM_2-156.root',
               'FBK+LYSO524' : './LOmeasurements/Npe_LYSO524_SiPM_3-130.root',
               'HPK+LYSO528' : './LOmeasurements/Npe_LYSO528_SiPM_2-40_newAnalysis.root'}

fNamesLO_R = { 'FBK+LYSO522' : './LOmeasurements/Npe_LYSO522_SiPM_1-141_GLUE.root',
               'FBK+LYSO800' : './LOmeasurements/Npe_LYSO800_SiPM_2-166.root',
               'FBK+LYSO524' : './LOmeasurements/Npe_LYSO524_SiPM_3-132.root',
               'HPK+LYSO528' : './LOmeasurements/Npe_LYSO528_SiPM_2-41_newAnalysis.root'}


Vovs = { 'FBK+LYSO524' :[1.50, 2.00, 3.50, 4.00],
         'FBK+LYSO800' :[1.50, 2.00, 3.00, 3.50, 4.00, 7.00],
         'FBK+LYSO522' :[1.50, 2.00, 3.00, 3.50],
         'HPK+LYSO528' :[1.50, 2.50, 3.50]}


ovRef = {'FBK+LYSO524': 3.50,
         'FBK+LYSO800': 3.50,
         'FBK+LYSO522': 3.50,
         'HPK+LYSO528': 3.50 }

cols = { 1.50 : 51,
         2.00 : 51 + 20,
         2.50 : 51 + 32,
         3.00 : 51 + 40,
         3.50 : 51 + 48,
         4.00 : 1      ,
         5.00 : 12     ,
         7.00 : 15     }  

labels = {'FBK+LYSO524': 'FBK+LYSO524(type3)',
          'FBK+LYSO800': 'FBK+LYSO800(type2) ',
          'FBK+LYSO522': 'FBK+LYSO522(type1)',
          'HPK+LYSO528': 'HPK+LYSO528(type2)' }

gRes = {}     
gRes_stoch = {}
gRes_noise = {}
gSR_L = {}
gSR_R = {}

# plots per sipm, ov
g_dtRes_vs_dLO = {}
g_tRes_vs_LO = {}
g_tRes_vs_LO_R = {}
g_tRes_vs_LO_L = {}
g_tRes_vs_asym = {}
g_tRes_vs_LOmin = {}
g_tRes_stoch_vs_LO = {}
g_tRes_noise_vs_LO = {}
g_SR_vs_LO = {}
g_asym_vs_LOmin = {}
g_asym_vs_LOmax = {}
fitFun = {}

# plots per sipm type
g_tRes_vs_LO_allOVs = {}
g_tRes_stoch_vs_LO_allOVs = {}
g_tRes_noise_vs_LO_allOVs = {}


fitFun2 = {}
hdummy = {}
hdummy3 = {}
hdummy4 = {}
hdummy5 = {}

errLO = 0.02 # 2% uncertainty on LO measurements

# LO plots
for sipm in sipmTypes:
    fRes[sipm] = ROOT.TFile.Open(fNames[sipm])
    fRes2[sipm] = ROOT.TFile.Open(fNames2[sipm])
    fLO_L[sipm] = ROOT.TFile.Open(fNamesLO_L[sipm])
    fLO_R[sipm] = ROOT.TFile.Open(fNamesLO_R[sipm])
    gLO_L  = fLO_L[sipm].Get('g_Npe_511_vs_bar_Vov3.5')
    gLO_R  = fLO_R[sipm].Get('g_Npe_511_vs_bar_Vov3.5')
    gLO  = ROOT.TGraphErrors()
    gLOratio = ROOT.TGraphErrors()
    gLOasym    = ROOT.TGraphErrors()

    for bar in range(0, 16):
        if (bar not in gLO_L.GetX() or bar not in gLO_R.GetX()): continue
        if ('522' in sipm and bar in [0,1,3,13]) :continue
        gLO.SetPoint(gLO.GetN(), bar, 0.5*(gLO_L.Eval(bar)+gLO_R.Eval(bar)))
        #gLO.SetPointError(gLO.GetN()-1, 0, 0.5*math.sqrt(gLO_L.GetErrorY(i)*gLO_L.GetErrorY(i)+gLO_R.GetErrorY(i)*gLO_R.GetErrorY(i)))
    
    fit0 = ROOT.TF1('fit0','pol0', 0, 15)
    fit0.SetLineColor(ROOT.kGray)
    fit0.SetLineWidth(1)
    gLO.Fit(fit0,'QRS')

    for bar in range(0, 16):
        if (bar not in gLO.GetX()): continue 
        gLOratio.SetPoint(gLOratio.GetN(), bar, gLO.Eval(bar)/fit0.GetParameter(0))
        gLOratio.SetPointError(gLOratio.GetN()-1, 0, 0)
        asym = (gLO_L.Eval(bar) - gLO_R.Eval(bar))/(gLO_L.Eval(bar) + gLO_R.Eval(bar))
        gLOasym.SetPoint(gLOasym.GetN(), bar, asym)


    gLO.SetMarkerStyle(24)
    gLO.SetMarkerColor(ROOT.kBlack)
    gLO.SetMarkerSize(1.3)
    gLO.SetLineStyle(2)
    gLO_L.SetMarkerStyle(20)
    gLO_L.SetMarkerColor(ROOT.kRed)
    gLO_L.SetLineColor(ROOT.kRed)
    gLO_R.SetMarkerStyle(20)
    gLO_R.SetMarkerColor(ROOT.kBlue)
    gLO_R.SetLineColor(ROOT.kBlue)
    leg = ROOT.TLegend(0.40,0.75,0.85, 0.89)
    leg.SetBorderSize(0)  
    leg.AddEntry(gLO_L, 'left', 'PL')
    leg.AddEntry(gLO_R, 'right', 'PL')
    leg.AddEntry(gLO  , 'ave: %d Npe/MeV'%fit0.GetParameter(0), 'PL')

    c  = ROOT.TCanvas('c_LOlab_ratio_%s'%(sipm),'c_LOlab_ratio_%s'%(sipm), 800, 600)
    pad1 = ROOT.TPad('pad1', 'pad1', 0.0,  0.40, 1.0, 1.0)
    pad1.SetBottomMargin(0.0)
    pad1.Draw()
    pad1.cd()
    hh = ROOT.TH2F('hh','', 16, -0.5, 15.5, 100, gLO.GetMean(2) - 400, gLO.GetMean(2) + 400)
    hh.GetXaxis().SetTitle('bar')
    hh.GetYaxis().SetTitle('N_{pe}/MeV')
    hh.Draw()
    hh.GetXaxis().SetLabelSize(0.04*1./0.6)
    hh.GetYaxis().SetLabelSize(0.04*1./0.6)
    hh.GetXaxis().SetTitleSize(0.04*1./0.6)
    hh.GetYaxis().SetTitleSize(0.04*1./0.6)
    hh.Draw()
    gLO_L.Draw('psame')
    gLO_R.Draw('psame')
    gLO.Draw('plsame')
    leg.Draw('same')
    c.cd()
    pad2 = ROOT.TPad('pad2', 'pad2', 0.0,  0.05, 1.0, 0.39)
    pad2.SetGridy()
    pad2.SetBottomMargin(0.25)
    pad2.Draw()
    pad2.cd()
    hh2 = ROOT.TH2F('hh2','', 16, -0.5, 15.5, 100,0.90,1.10)
    hh2.GetXaxis().SetTitleOffset(0.6)
    hh2.GetYaxis().SetTitleOffset(0.6)
    hh2.GetXaxis().SetTitle('bar')
    hh2.GetYaxis().SetTitle('LO/<LO>')
    hh2.GetXaxis().SetLabelSize(0.04*1./0.34)
    hh2.GetYaxis().SetLabelSize(0.04*1./0.34)
    hh2.GetXaxis().SetTitleSize(0.04*1./0.34)
    hh2.GetYaxis().SetTitleSize(0.04*1./0.34)
    hh2.GetYaxis().SetNdivisions(505)
    hh2.Draw()
    gLOratio.Draw('psame')  
    line = ROOT.TLine(-0.5, 1, 15.5, 1)
    line.Draw('same')
    c.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c.GetName()+'.png')
    c.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c.GetName()+'.pdf')
    hh2.Delete()


    cc  = ROOT.TCanvas('c_LOlab_asym_%s'%(sipm),'c_LOlab_asym_%s'%(sipm), 800, 600)
    pad1 = ROOT.TPad('pad1', 'pad1', 0.0,  0.40, 1.0, 1.0)
    pad1.SetBottomMargin(0.0)
    pad1.Draw()
    pad1.cd()
    hh.GetXaxis().SetLabelSize(0.04*1./0.6)
    hh.GetYaxis().SetLabelSize(0.04*1./0.6)
    hh.GetXaxis().SetTitleSize(0.04*1./0.6)
    hh.GetYaxis().SetTitleSize(0.04*1./0.6)
    hh.Draw()
    gLO_L.Draw('psame')
    gLO_R.Draw('psame')
    gLO.Draw('plsame')
    leg.Draw('same')
    cc.cd()
    pad2 = ROOT.TPad('pad2', 'pad2', 0.0,  0.05, 1.0, 0.39)
    pad2.SetGridy()
    pad2.SetBottomMargin(0.25)
    pad2.Draw()
    pad2.cd()
    hh2 = ROOT.TH2F('hh2','', 16, -0.5, 15.5, 100,-0.3,0.3)
    hh2.GetXaxis().SetTitleOffset(0.6)
    hh2.GetYaxis().SetTitleOffset(0.6)
    hh2.GetXaxis().SetTitle('bar')
    hh2.GetYaxis().SetTitle('LO asym')
    hh2.GetXaxis().SetLabelSize(0.04*1./0.34)
    hh2.GetYaxis().SetLabelSize(0.04*1./0.34)
    hh2.GetXaxis().SetTitleSize(0.04*1./0.34)
    hh2.GetYaxis().SetTitleSize(0.04*1./0.34)
    hh2.GetYaxis().SetNdivisions(505)
    hh2.Draw()
    gLOasym.Draw('psame')  
    line = ROOT.TLine(-0.5, 0, 15.5, 0)
    line.Draw('same')
    cc.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+cc.GetName()+'.png')
    cc.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+cc.GetName()+'.pdf')
    hh2.Delete()




    # time resol vs LO plots
    g_tRes_vs_LO_allOVs[sipm] = ROOT.TGraphErrors()
    g_tRes_stoch_vs_LO_allOVs[sipm] = ROOT.TGraphErrors()
    g_tRes_noise_vs_LO_allOVs[sipm] = ROOT.TGraphErrors()

    fitFun2[sipm,''] = ROOT.TF1('fitFun2_%s'%sipm,'sqrt([0]*[0]*pow(x,[1])*pow(x,[1]) + [2]*[2])',0,10000)
    fitFun2[sipm,'stoch'] = ROOT.TF1('fitFun2_%s_stoch'%sipm,'[0]*pow(x,[1])',0,10000)
    fitFun2[sipm,'noise'] = ROOT.TF1('fitFun2_%s_noise'%sipm,'sqrt([0]*[0]*pow(x,[1])*pow(x,[1]) + [2]*[2])',0,10000)

    
    for ov in Vovs[sipm]:
        gRes[sipm,ov] = fRes[sipm].Get('g_deltaT_totRatioCorr_bestTh_vs_bar_Vov%.02f_enBin01'%ov)
        #gRes[sipm,ov] = fRes[sipm].Get('g_deltaT_totRatioCorr_vs_bar__Vov%.02f_th09'%ov)
        if (gRes[sipm,ov]==None):
            print '%s: g_deltaT_totRatioCorr_bestTh_vs_bar_Vov%.02f_enBin01  does not exists!'%(sipm,ov)
            
        gRes_stoch[sipm,ov] = fRes2[sipm].Get('gg_Stoch_vs_bar_FBK_nonIrr_%s_Vov%.02f'%(sipm.replace('FBK+',''),ov))
        gRes_noise[sipm,ov] = fRes2[sipm].Get('g_Noise_vs_bar_FBK_nonIrr_%s_Vov%.02f'%(sipm.replace('FBK+',''),ov))
        gSR_L[sipm,ov] = fRes2[sipm].Get('g_SR_vs_bar_L_FBK_nonIrr_%s_Vov%.02f'%(sipm.replace('FBK+',''),ov))
        gSR_R[sipm,ov] = fRes2[sipm].Get('g_SR_vs_bar_R_FBK_nonIrr_%s_Vov%.02f'%(sipm.replace('FBK+',''),ov))
        
        if ('HPK' in sipm):
            gRes_stoch[sipm,ov] = fRes2[sipm].Get('gg_Stoch_vs_bar_HPK_nonIrr_%s_Vov%.02f'%(sipm.replace('HPK+',''),ov))
            gRes_noise[sipm,ov] = fRes2[sipm].Get('g_Noise_vs_bar_HPK_nonIrr_%s_Vov%.02f'%(sipm.replace('HPK+',''),ov))
            gSR_L[sipm,ov] = fRes2[sipm].Get('g_SR_vs_bar_L_HPK_nonIrr_%s_Vov%.02f'%(sipm.replace('HPK+',''),ov))
            gSR_R[sipm,ov] = fRes2[sipm].Get('g_SR_vs_bar_R_HPK_nonIrr_%s_Vov%.02f'%(sipm.replace('HPK+',''),ov))

        g_dtRes_vs_dLO[sipm,ov] = ROOT.TGraphErrors()
        g_tRes_vs_LO[sipm,ov]   = ROOT.TGraphErrors()
        g_tRes_vs_LO_L[sipm,ov] = ROOT.TGraphErrors()
        g_tRes_vs_LO_R[sipm,ov] = ROOT.TGraphErrors()
        g_tRes_vs_asym[sipm,ov] = ROOT.TGraphErrors()
        g_tRes_vs_LOmin[sipm,ov] = ROOT.TGraphErrors()
        g_tRes_stoch_vs_LO[sipm,ov] = ROOT.TGraphErrors()
        g_tRes_noise_vs_LO[sipm,ov] = ROOT.TGraphErrors()
        g_SR_vs_LO[sipm,ov]   = ROOT.TGraphErrors()
        g_asym_vs_LOmin[sipm,ov]   = ROOT.TGraphErrors()
        g_asym_vs_LOmax[sipm,ov]   = ROOT.TGraphErrors()

        for i in range(0,gRes[sipm,ov].GetN()):
            bar  = gRes[sipm,ov].GetX()[i]
            if (bar not in gLO.GetX()): continue
            #if ('522' in sipm and bar == 12) : continue # bad sr fit and noise term
            tRes = gRes[sipm,ov].GetY()[i]
            tRes_stoch = gRes_stoch[sipm,ov].GetY()[i]
            tRes_noise = gRes_noise[sipm,ov].GetY()[i]
            lo   = gLO.Eval(bar)*PDE(ov,sipm,'0')/PDE(ovRef[sipm],sipm,'0')
            lo_L = gLO_L.Eval(bar)*PDE(ov,sipm,'0')/PDE(ovRef[sipm],sipm,'0')
            lo_R = gLO_R.Eval(bar)*PDE(ov,sipm,'0')/PDE(ovRef[sipm],sipm,'0')
            lo_min = min(lo_L, lo_R)
            lo_max = max(lo_L, lo_R)
            sr_L = gSR_L[sipm,ov].Eval(bar)
            sr_R = gSR_R[sipm,ov].Eval(bar)
            asym = (lo_L-lo_R)/(lo_L+lo_R)
            err_asym = abs(asym) * math.sqrt( pow(errLO*lo_L,2) + pow(errLO*lo_R,2)) * math.sqrt(1/(lo_L-lo_R)/(lo_L-lo_R) + 1/(lo_L+lo_R)/(lo_L+lo_R)) 

            g_asym_vs_LOmin[sipm,ov].SetPoint(g_asym_vs_LOmin[sipm,ov].GetN(), lo_min , asym)
            g_asym_vs_LOmin[sipm,ov].SetPointError(g_asym_vs_LOmin[sipm,ov].GetN()-1, errLO*lo_min, err_asym)
            g_asym_vs_LOmax[sipm,ov].SetPoint(g_asym_vs_LOmax[sipm,ov].GetN(), lo_max , asym)
            g_asym_vs_LOmax[sipm,ov].SetPointError(g_asym_vs_LOmax[sipm,ov].GetN()-1, errLO*lo_max, err_asym)

            if (abs(asym)>=0.10):continue
            
            g_tRes_vs_LO[sipm,ov].SetPoint(g_tRes_vs_LO[sipm,ov].GetN(), lo , tRes)
            g_tRes_vs_LO[sipm,ov].SetPointError(g_tRes_vs_LO[sipm,ov].GetN()-1, errLO*lo, gRes[sipm,ov].GetErrorY(i))

            g_tRes_vs_LO_L[sipm,ov].SetPoint(g_tRes_vs_LO_L[sipm,ov].GetN(), lo_L, tRes)
            g_tRes_vs_LO_L[sipm,ov].SetPointError(g_tRes_vs_LO_L[sipm,ov].GetN()-1, errLO*lo_L, gRes[sipm,ov].GetErrorY(i))

            g_tRes_vs_LO_R[sipm,ov].SetPoint(g_tRes_vs_LO_R[sipm,ov].GetN(), lo_R, tRes)
            g_tRes_vs_LO_R[sipm,ov].SetPointError(g_tRes_vs_LO_R[sipm,ov].GetN()-1, errLO*lo_R, gRes[sipm,ov].GetErrorY(i))

            g_tRes_stoch_vs_LO[sipm,ov].SetPoint(g_tRes_stoch_vs_LO[sipm,ov].GetN(), lo, tRes_stoch)
            g_tRes_stoch_vs_LO[sipm,ov].SetPointError(g_tRes_stoch_vs_LO[sipm,ov].GetN()-1, errLO*lo, gRes_stoch[sipm,ov].GetErrorY(i))

            g_tRes_noise_vs_LO[sipm,ov].SetPoint(g_tRes_noise_vs_LO[sipm,ov].GetN(), lo, tRes_noise)
            g_tRes_noise_vs_LO[sipm,ov].SetPointError(g_tRes_noise_vs_LO[sipm,ov].GetN()-1, errLO*lo, gRes_noise[sipm,ov].GetErrorY(i))
            
            g_tRes_vs_LO_allOVs[sipm].SetPoint(g_tRes_vs_LO_allOVs[sipm].GetN(), lo, tRes)
            g_tRes_vs_LO_allOVs[sipm].SetPointError(g_tRes_vs_LO_allOVs[sipm].GetN()-1, errLO*lo, gRes[sipm,ov].GetErrorY(i))

            g_tRes_stoch_vs_LO_allOVs[sipm].SetPoint(g_tRes_stoch_vs_LO_allOVs[sipm].GetN(), lo, tRes_stoch)
            g_tRes_stoch_vs_LO_allOVs[sipm].SetPointError(g_tRes_stoch_vs_LO_allOVs[sipm].GetN()-1, errLO*lo, gRes_stoch[sipm,ov].GetErrorY(i))
 
            g_tRes_noise_vs_LO_allOVs[sipm].SetPoint(g_tRes_noise_vs_LO_allOVs[sipm].GetN(), lo*Gain(ov,sipm)/1E05, tRes_noise)
            g_tRes_noise_vs_LO_allOVs[sipm].SetPointError(g_tRes_noise_vs_LO_allOVs[sipm].GetN()-1, errLO*lo*Gain(ov,sipm)/1E05, gRes_noise[sipm,ov].GetErrorY(i))

            g_SR_vs_LO[sipm, ov].SetPoint(g_SR_vs_LO[sipm,ov].GetN(), lo_L, sr_L/lo_L)
            g_SR_vs_LO[sipm, ov].SetPointError(g_SR_vs_LO[sipm,ov].GetN()-1, errLO*lo_L, gSR_L[sipm,ov].GetErrorY(i)/lo_L)
            g_SR_vs_LO[sipm, ov].SetPoint(g_SR_vs_LO[sipm,ov].GetN(), lo_R, sr_R/lo_R)
            g_SR_vs_LO[sipm, ov].SetPointError(g_SR_vs_LO[sipm,ov].GetN()-1, errLO*lo_R, gSR_R[sipm,ov].GetErrorY(i)/lo_R)

        #draw SR vs LO
        c2 = ROOT.TCanvas('c_SR_vs_LOlab_%s_Vov%.02f'%(sipm,ov),'c_SR_vs_LOlab_%s_Vov%.02f'%(sipm,ov), 600, 600)
        xmin = int( (g_SR_vs_LO[sipm, ov].GetMean() - 4*g_SR_vs_LO[sipm, ov].GetRMS())/10 ) * 10
        xmax = int( (g_SR_vs_LO[sipm, ov].GetMean() + 4*g_SR_vs_LO[sipm, ov].GetRMS())/10 ) * 10
        ymin = g_SR_vs_LO[sipm, ov].GetMean(2)-4*g_SR_vs_LO[sipm, ov].GetRMS(2)
        ymax = g_SR_vs_LO[sipm, ov].GetMean(2)+4*g_SR_vs_LO[sipm, ov].GetRMS(2) 
        hh3 = ROOT.TH2F('hh3','',100, xmin, xmax, 100, ymin, ymax)
        hh3.GetXaxis().SetTitle('LO [Npe/MeV]')
        hh3.GetYaxis().SetTitle('SR [#muA/ns]')
        hh3.Draw()
        g_SR_vs_LO[sipm, ov].Draw('psame')
        c2.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c2.GetName()+'.png')
        c2.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c2.GetName()+'.pdf')
        hh3.Delete()

        #draw asym vs LOmin
        c2 = ROOT.TCanvas('c_asym_vs_LOmin_%s_Vov%.02f'%(sipm,ov),'c_asym_vs_LOmin_%s_Vov%.02f'%(sipm,ov), 600, 600)
        xmin = int( (g_asym_vs_LOmin[sipm, ov].GetMean() - 4*g_asym_vs_LOmin[sipm, ov].GetRMS())/10 ) * 10
        xmax = int( (g_asym_vs_LOmin[sipm, ov].GetMean() + 4*g_asym_vs_LOmin[sipm, ov].GetRMS())/10 ) * 10
        ymin = g_asym_vs_LOmin[sipm, ov].GetMean(2)-4*g_asym_vs_LOmin[sipm, ov].GetRMS(2)
        ymax = g_asym_vs_LOmin[sipm, ov].GetMean(2)+4*g_asym_vs_LOmin[sipm, ov].GetRMS(2) 
        hh3 = ROOT.TH2F('hh3','',100, xmin, xmax, 100, ymin, ymax)
        hh3.GetXaxis().SetTitle('LO_{min} [Npe/MeV]')
        hh3.GetYaxis().SetTitle('asym')
        hh3.Draw()
        g_asym_vs_LOmin[sipm, ov].Draw('psame')
        #g_asym_vs_LOmax[sipm, ov].SetMarkerStyle(24)
        #g_asym_vs_LOmax[sipm, ov].Draw('psame')
        c2.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c2.GetName()+'.png')
        c2.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c2.GetName()+'.pdf')
        hh3.Delete()


        #draw tRes vs LO
        for ii, g in enumerate([g_tRes_vs_LO[sipm,ov], g_tRes_stoch_vs_LO[sipm,ov], g_tRes_noise_vs_LO[sipm,ov]]):
            
            suffix = ''
            if ii == 1: suffix = 'stoch'
            if ii == 2: suffix = 'noise'
            
            c2 = ROOT.TCanvas('c_timeResolution_%s_vs_LOlab_%s_Vov%.02f'%(suffix,sipm,ov),'c_timeResolution_%s_vs_LOlab_%s_Vov%.02f'%(suffix,sipm,ov), 600, 600)
            
            xmin = int( (g.GetMean() - 4*g.GetRMS())/10 ) * 10
            xmax = int( (g.GetMean() + 4*g.GetRMS())/10 ) * 10
            ymin = g.GetMean(2)-4*g.GetRMS(2)
            ymax = g.GetMean(2)+4*g.GetRMS(2) 
            
            hdummy[sipm, ov] = ROOT.TH2F('hdummy_%s_%s_%f'%(suffix,sipm,ov),'',100,xmin, xmax, 100, ymin, ymax)
            hdummy[sipm, ov].GetXaxis().SetNdivisions(505)
            hdummy[sipm, ov].GetXaxis().SetTitle('LO_{LAB} [Npe/MeV]')
            hdummy[sipm, ov].GetYaxis().SetTitle('#sigma_{t}^{%s} [ps]'%suffix)
            hdummy[sipm, ov].Draw()
            g.SetMarkerStyle(20)
            g.SetMarkerColor(cols[ov])
            g.SetLineColor(cols[ov])
            g.Draw('psame')
            latex = ROOT.TLatex(0.20,0.86,'%s - V_{OV} = %.02f V'%(labels[sipm], ov)) 
            latex.SetNDC()
            latex.SetTextSize(0.045)
            latex.SetTextFont(42)
            latex.Draw('same') 
            
            fitFun[sipm, ov, suffix] = ROOT.TF1('fitFun_%s_%s_%f'%(suffix,sipm, ov),'[0] * pow(x/%f,[1])'%(g.GetMean()), 0,10000)
            #fitFun[sipm, ov, suffix] = ROOT.TF1('fitFun_%s_%f'%(sipm, ov),'pol1', 0,10000)
            fitFun[sipm, ov, suffix].SetLineColor(cols[ov])
            fitFun[sipm, ov, suffix].SetParameter(0, g.GetMean(2))
            fitFun[sipm, ov, suffix].SetParameter(1, -1.0)
            g.Fit(fitFun[sipm, ov, suffix],'QSR+')
            #print '****',sipm, ov, fitFun[sipm, ov].GetParameter(0), fitFun[sipm, ov].GetParameter(1), fitFun[sipm, ov].GetChisquare()/fitFun[sipm, ov].GetNDF()
            
            c2.Update()
            ps = g.FindObject('stats')
            if (ps == None): continue
            ps.SetTextColor(g.GetMarkerColor())
            ps.SetBorderSize(1)
            ps.SetX1NDC(0.18) # new x start position 
            ps.SetX2NDC(0.50)# new x end position 
            ps.SetY1NDC(0.20) # new y start position 
            ps.SetY2NDC(0.35)# new y end position 
            c2.Modified()
            
            c2.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c2.GetName()+'.png')
            c2.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c2.GetName()+'.pdf')
            

    # draw tRes vs LO global plot all OV's together
    for ii, g in enumerate([g_tRes_vs_LO_allOVs[sipm], g_tRes_stoch_vs_LO_allOVs[sipm], g_tRes_noise_vs_LO_allOVs[sipm]] ):                    

        suffix = ''
        if ii == 1: suffix = 'stoch'
        if ii == 2: suffix = 'noise'

        c2 = ROOT.TCanvas('c_timeResolution_%s_vs_LOlab_all_%s'%(suffix,sipm),'c_timeResolution_%s_vs_LOlab_all_%s'%(suffix,sipm), 600, 600)
        hh4 = ROOT.TH2F('hh4','', 100, 300, 1700, 100, 0, 120)
        hh4.GetXaxis().SetTitle('LO [Npe/MeV]')
        if (suffix == 'noise' or ''): 
            hh4.Delete()
            hh4 = ROOT.TH2F('hh4','', 100, 0, 6000, 100, 0, 100)
            hh4.GetXaxis().SetTitle('Gain x LO [Npe/MeV]')
            fitFun2[sipm,suffix].SetParameter(2,12)
            fitFun2[sipm,suffix].SetParLimits(2,0,100)    

        hh4.GetYaxis().SetTitle('#sigma_{t}^{%s} [ps]'%suffix)
        hh4.Draw()
        g.SetMarkerStyle(20)
        g.Draw('psame')
        fitFun2[sipm,suffix].SetParameter(0,500000)
        fitFun2[sipm,suffix].SetParameter(1,-1.0)
        g.Fit(fitFun2[sipm,suffix],'QSR+')
        latex2 = ROOT.TLatex(0.20,0.86,'%s'%(labels[sipm]))
        latex2.SetNDC()
        latex2.SetTextSize(0.045)
        latex2.SetTextFont(42)
        latex2.Draw('same')      
        c2.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c2.GetName()+'.png')
        c2.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c2.GetName()+'.pdf')
        hh4.Delete()


    #draw vs asym LO
    for ov in Vovs[sipm]:  

        for i in range(0,gRes[sipm,ov].GetN()):
            bar  = gRes[sipm,ov].GetX()[i]
            if (bar not in gLO.GetX()): continue
            tRes = gRes[sipm,ov].GetY()[i]
            tRes_stoch = gRes_stoch[sipm,ov].GetY()[i]
            tRes_noise = gRes_noise[sipm,ov].GetY()[i]
            lo   = gLO.Eval(bar)*PDE(ov,sipm,'0')/PDE(ovRef[sipm],sipm,'0')
            lo_L   = gLO_L.Eval(bar)*PDE(ov,sipm,'0')/PDE(ovRef[sipm],sipm,'0')
            lo_R   = gLO_R.Eval(bar)*PDE(ov,sipm,'0')/PDE(ovRef[sipm],sipm,'0')
            lo_min = min(lo_L, lo_R)
            sr_L   = gSR_L[sipm,ov].Eval(bar)
            sr_R   = gSR_R[sipm,ov].Eval(bar)
            asym   = (lo_L-lo_R)/(lo_L+lo_R)
            err_asym = abs(asym) * math.sqrt( pow(errLO*lo_L,2) + pow(errLO*lo_R,2)) * math.sqrt(1/(lo_L-lo_R)/(lo_L-lo_R) + 1/(lo_L+lo_R)/(lo_L+lo_R)) 

            g_dtRes_vs_dLO[sipm,ov].SetPoint(g_dtRes_vs_dLO[sipm,ov].GetN(), lo/g_tRes_vs_LO[sipm,ov].GetMean(), tRes/g_tRes_vs_LO[sipm,ov].GetMean(2))
            g_dtRes_vs_dLO[sipm,ov].SetPointError(g_dtRes_vs_dLO[sipm,ov].GetN()-1, errLO*lo/g_tRes_vs_LO[sipm,ov].GetMean(), gRes[sipm,ov].GetErrorY(i)/g_tRes_vs_LO[sipm,ov].GetMean(2))

            #g_tRes_vs_asym[sipm,ov].SetPoint(g_tRes_vs_asym[sipm,ov].GetN(), asym, tRes * ( lo / g_tRes_vs_LO[sipm,ov].GetMean()))
            #g_tRes_vs_asym[sipm,ov].SetPointError(g_tRes_vs_asym[sipm,ov].GetN()-1, err_asym, gRes[sipm,ov].GetErrorY(i) *  ( lo / g_tRes_vs_LO[sipm,ov].GetMean()))

            g_tRes_vs_asym[sipm,ov].SetPoint(g_tRes_vs_asym[sipm,ov].GetN(), asym, tRes/fitFun[sipm, ov,''].Eval(lo)*fitFun[sipm, ov,''].Eval(g_tRes_vs_LO[sipm,ov].GetMean()) )
            g_tRes_vs_asym[sipm,ov].SetPointError(g_tRes_vs_asym[sipm,ov].GetN()-1, err_asym, gRes[sipm,ov].GetErrorY(i) / fitFun[sipm, ov,''].Eval(lo)* fitFun[sipm, ov,''].Eval(g_tRes_vs_LO[sipm,ov].GetMean()))

            g_tRes_vs_LOmin[sipm,ov].SetPoint(g_tRes_vs_LOmin[sipm,ov].GetN(), lo_min, tRes/fitFun[sipm, ov,''].Eval(lo)*fitFun[sipm, ov,''].Eval(g_tRes_vs_LO[sipm,ov].GetMean()) )
            g_tRes_vs_LOmin[sipm,ov].SetPointError(g_tRes_vs_LOmin[sipm,ov].GetN()-1, errLO*lo_min, gRes[sipm,ov].GetErrorY(i) / fitFun[sipm, ov,''].Eval(lo)* fitFun[sipm, ov,''].Eval(g_tRes_vs_LO[sipm,ov].GetMean()))
                        

            
        c4 = ROOT.TCanvas('c_timeResolutionVariation_vs_LO_%s_Vov%.02f'%(sipm,ov),'c_timeResolutionVariation_vs_LO_%s_Vov%.02f'%(sipm,ov), 600, 600)
        c4.SetGridx()
        c4.SetGridy()
        hdummy4[sipm,ov] = ROOT.TH2F('hdummy4_%s_%f'%(sipm,ov),'',100, 0.70, 1.30, 100, 0.70, 1.30)
        hdummy4[sipm,ov].GetXaxis().SetNdivisions(505)
        hdummy4[sipm,ov].GetXaxis().SetTitle('LO/<LO>')
        hdummy4[sipm,ov].GetYaxis().SetTitle('#sigma_{t}/<#sigma_{t}>')
        hdummy4[sipm,ov].Draw()
        g_dtRes_vs_dLO[sipm,ov].SetMarkerStyle(20)
        g_dtRes_vs_dLO[sipm,ov].SetMarkerColor(cols[ov])
        g_dtRes_vs_dLO[sipm,ov].SetLineColor(cols[ov])
        g_dtRes_vs_dLO[sipm,ov].Draw('psame')
        fitFun1 = ROOT.TF1('fitFun1','[0]*(x-1)+[1]', -10, 10)
        fitFun1.SetParameters(-1,1)
        g_dtRes_vs_dLO[sipm,ov].Fit('fitFun1','Q')
        latex = ROOT.TLatex(0.20,0.20,'%s - V_{OV} = %.02f V'%(labels[sipm], ov)) 
        latex.SetNDC()
        latex.SetTextSize(0.045)
        latex.SetTextFont(42)
        latex.Draw('same') 

        c4.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c4.GetName()+'.png')
        c4.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c4.GetName()+'.pdf')


        c3 = ROOT.TCanvas('c_timeResolution_vs_asym_%s_Vov%.02f'%(sipm,ov),'c_timeResolution_vs_asym_%s_Vov%.02f'%(sipm,ov), 600, 600)    
        c3.SetGridx()
        c3.SetGridy()
        #hdummy3[sipm,ov] = ROOT.TH2F('hdummy3_%s_%f'%(sipm,ov),'',100,-0.40, 0.40, 100, g_tRes_vs_asym[sipm,ov].GetMean(2)-7*g_tRes_vs_asym[sipm,ov].GetRMS(2),g_tRes_vs_asym[sipm,ov].GetMean(2)+7*g_tRes_vs_asym[sipm,ov].GetRMS(2))
        hdummy3[sipm,ov] = ROOT.TH2F('hdummy3_%s_%f'%(sipm,ov),'',100,-0.40, 0.40, 100, g_tRes_vs_asym[sipm,ov].GetMean(2)-30, g_tRes_vs_asym[sipm,ov].GetMean(2)+30)
        hdummy3[sipm,ov].GetXaxis().SetNdivisions(505)
        hdummy3[sipm,ov].GetXaxis().SetTitle('(LO_{L}-LO_{R})/(LO_{L}+LO_{R})')
        hdummy3[sipm,ov].GetYaxis().SetTitle('time resolution #times LO/<LO>')
        hdummy3[sipm,ov].Draw()
        g_tRes_vs_asym[sipm,ov].SetMarkerStyle(20)
        g_tRes_vs_asym[sipm,ov].SetMarkerColor(cols[ov])
        g_tRes_vs_asym[sipm,ov].SetLineColor(cols[ov])
        g_tRes_vs_asym[sipm,ov].Draw('psame')
        fA = ROOT.TF1("fA","[0]/sqrt(2)*sqrt(1./pow((1+x),2*[1]) + 1/pow( (1-x), 2*[1]))", -1, 1)
        fA.SetLineWidth(1)
        fA.SetLineStyle(2)
        fA.SetLineColor(cols[ov])
        fA.SetParameter(0, g_tRes_vs_asym[sipm,ov].GetMean(2))
        fA.FixParameter(1, fitFun[sipm, ov,''].GetParameter(1))
        g_tRes_vs_asym[sipm,ov].Fit(fA,'QRS')
        latex.Draw('same') 

        c3.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c3.GetName()+'.png')
        c3.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c3.GetName()+'.pdf')

        
        c5 = ROOT.TCanvas('c_timeResolution_vs_LOmin_%s_Vov%.02f'%(sipm,ov),'c_timeResolution_vs_LOmin_%s_Vov%.02f'%(sipm,ov), 600, 600)    
        c5.SetGridx()
        c5.SetGridy()
        xmin = int( (g_tRes_vs_LOmin[sipm,ov].GetMean() - 4*g_tRes_vs_LOmin[sipm,ov].GetRMS())/10 ) * 10
        xmax = int( (g_tRes_vs_LOmin[sipm,ov].GetMean() + 4*g_tRes_vs_LOmin[sipm,ov].GetRMS())/10 ) * 10
        hdummy5[sipm,ov] = ROOT.TH2F('hdummy5_%s_%f'%(sipm,ov),'',100,xmin, xmax, 100, g_tRes_vs_LOmin[sipm,ov].GetMean(2)-30, g_tRes_vs_LOmin[sipm,ov].GetMean(2)+30)
        hdummy5[sipm,ov].GetXaxis().SetNdivisions(505)
        hdummy5[sipm,ov].GetXaxis().SetTitle(' LO_{min} [N_pe/MeV]')
        hdummy5[sipm,ov].GetYaxis().SetTitle('time resolution #times LO/<LO>')
        hdummy5[sipm,ov].Draw()
        g_tRes_vs_LOmin[sipm,ov].SetMarkerStyle(20)
        g_tRes_vs_LOmin[sipm,ov].SetMarkerColor(cols[ov])
        g_tRes_vs_LOmin[sipm,ov].SetLineColor(cols[ov])
        g_tRes_vs_LOmin[sipm,ov].Draw('psame')
        g_tRes_vs_LOmin[sipm,ov].Fit(fA,'QRS')
        latex.Draw('same') 

        c5.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c5.GetName()+'.png')
        c5.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c5.GetName()+'.pdf')



