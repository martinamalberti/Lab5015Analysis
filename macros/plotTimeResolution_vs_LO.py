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
ROOT.gStyle.SetOptFit(0)
ROOT.gStyle.SetFitFormat('6.3g')



def PDE(ov, sipm, irr='0'):
    k = 1.
    if (irr == '2E14' and 'HPK' in sipm): k = 0.78 # 22% PDE reduction for HPK SiPMs irradiated 2E14
    if (irr == '1E14' and 'HPK' in sipm): k = 0.89 # 11% PDE reduction for HPK SiPMs irradiated 1E14 ?(assume that for 1E14 is half of 2E14)
    if ('HPK' in sipm):
        return k * 1.0228 * 0.384 * ( 1. - math.exp(-1.*0.583*ov) ) # 1.0228 factor to account for LYSO emission spectrum
    # FBK-MS
    #if ('FBK' in sipm):
    #    return k * 0.8847 * 0.466 * ( 1. - math.exp(-1.*0.314*ov) ) # 0.8847 factor to account for LYSO emission spectrum
    #FBK W4C
    if ('FBK' in sipm):
        return k * 0.490 * ( 1. - math.exp(-1.*0.225*ov) )/1.071 # 1.071 factor to account for bench calib, convolution PDE with LYSO already accounted for



sipmTypes = ['FBK+LYSO524', 'FBK+LYSO800','FBK+LYSO522', 'HPK+LYSO528']

fLO_L = {}
fLO_R = {}
fRes = {}
fNames = { 'FBK+LYSO524': '../plots/FBK_nonIrr_LYSO524_T10C_summary.root',
           'FBK+LYSO800': '../plots/FBK_nonIrr_LYSO800_T10C_summary.root',
           'FBK+LYSO522': '../plots/FBK_nonIrr_LYSO522_T10C_summary.root',
           'HPK+LYSO528': '../plots/HPK_nonIrr_LYSO528_T10C_summary.root'}

fNamesLO_L = { 'FBK+LYSO522' : './LOmeasurements/Npe_LYSO522_SiPM_1-140_GLUE.root',
               'FBK+LYSO800' : './LOmeasurements/Npe_LYSO800_SiPM_2-156.root',
               'FBK+LYSO524' : './LOmeasurements/Npe_LYSO524_SiPM_3-130.root',
               'HPK+LYSO528' : './LOmeasurements/Npe_LYSO528_SiPM_2-40_newAnalysis.root'}

fNamesLO_R = { 'FBK+LYSO522' : './LOmeasurements/Npe_LYSO522_SiPM_1-141_GLUE.root',
               'FBK+LYSO800' : './LOmeasurements/Npe_LYSO800_SiPM_2-166.root',
               #'FBK+LYSO524' : './LOmeasurements/Npe_LYSO524_SiPM_3-132_postTB.root',
               'FBK+LYSO524' : './LOmeasurements/Npe_LYSO524_SiPM_3-132.root',
               'HPK+LYSO528' : './LOmeasurements/Npe_LYSO528_SiPM_2-41_newAnalysis.root'}


Vovs = { 'FBK+LYSO524' :[1.50, 2.00, 3.50],
         'FBK+LYSO800' :[1.50, 2.00, 3.00, 3.50],
         'FBK+LYSO522' :[1.50, 2.00, 3.00, 3.50],
         'HPK+LYSO528' :[1.50, 2.50, 3.50]}

ovRef = {'FBK+LYSO524': 3.50,
         'FBK+LYSO800': 3.50,
         'FBK+LYSO522': 3.50,
         'HPK+LYSO528': 3.50 }

cols = { 1.50 : 51,
         2.00 : 51 + 20,
         2.50 : 51 + 32,
         3.00  : 51 + 40,
         3.50  : 51 + 48}  

g_tRes_vs_LO = {}
g_tRes_vs_LO_R = {}
g_tRes_vs_LO_L = {}


hdummy = {}

errLO = 0.02 # 2% uncertainty on LO measurements

for sipm in sipmTypes:
    fRes[sipm] = ROOT.TFile.Open(fNames[sipm])
    fLO_L[sipm] = ROOT.TFile.Open(fNamesLO_L[sipm])
    fLO_R[sipm] = ROOT.TFile.Open(fNamesLO_R[sipm])
    gLO_L  = fLO_L[sipm].Get('g_Npe_511_vs_bar_Vov3.5')
    gLO_R  = fLO_R[sipm].Get('g_Npe_511_vs_bar_Vov3.5')
    gLO  = ROOT.TGraphErrors()
    gLOratio  = ROOT.TGraphErrors()

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
        
    c = ROOT.TCanvas('c_LOlab_%s'%(sipm),'c_LOlab_%s'%(sipm), 800, 600)                                                                        
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
    hh = ROOT.TH2F('hh','', 16, -0.5, 15.5, 100, gLO.GetMean(2) - 600, gLO.GetMean(2) + 600)
    hh.GetXaxis().SetTitle('bar')
    hh.GetYaxis().SetTitle('N_{pe}/MeV')
    hh.Draw()
    gLO_L.Draw('psame')
    gLO_R.Draw('psame')
    gLO.Draw('plsame')
    leg = ROOT.TLegend(0.40,0.75,0.85, 0.89)
    leg.SetBorderSize(0)  
    leg.AddEntry(gLO_L, 'left', 'PL')
    leg.AddEntry(gLO_R, 'right', 'PL')
    leg.AddEntry(gLO  , 'ave: %d Npe/MeV'%fit0.GetParameter(0), 'PL')
    leg.Draw('same')
    c.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c.GetName()+'.png')
    c.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c.GetName()+'.pdf')
    
    
    cc  = ROOT.TCanvas('c_LOlab_ratio_%s'%(sipm),'c_LOlab_ratio_%s'%(sipm), 800, 600)
    pad1 = ROOT.TPad('pad1', 'pad1', 0.0,  0.3, 1.0, 1.0)
    pad1.SetBottomMargin(0.0)
    pad1.Draw()
    pad1.cd()
    hh.GetXaxis().SetLabelSize(0.04*1./0.7)
    hh.GetYaxis().SetLabelSize(0.04*1./0.7)
    hh.GetXaxis().SetTitleSize(0.04*1./0.7)
    hh.GetYaxis().SetTitleSize(0.04*1./0.7)
    hh.Draw()
    gLO_L.Draw('psame')
    gLO_R.Draw('psame')
    gLO.Draw('plsame')
    leg.Draw('same')
    cc.cd()
    pad2 = ROOT.TPad('pad2', 'pad2', 0.0,  0.05, 1.0, 0.29)
    pad2.SetGridy()
    pad2.SetBottomMargin(0.25)
    pad2.Draw()
    pad2.cd()
    hh2 = ROOT.TH2F('hh2','', 16, -0.5, 15.5, 100,0.90,1.10)
    hh2.GetXaxis().SetTitleOffset(0.5)
    hh2.GetYaxis().SetTitleOffset(0.4)
    hh2.GetXaxis().SetTitle('bar')
    hh2.GetYaxis().SetTitle('LO/<LO>')
    hh2.GetXaxis().SetLabelSize(0.04*1./0.24)
    hh2.GetYaxis().SetLabelSize(0.04*1./0.24)
    hh2.GetXaxis().SetTitleSize(0.04*1./0.24)
    hh2.GetYaxis().SetTitleSize(0.04*1./0.24)
    hh2.GetYaxis().SetNdivisions(505)
    hh2.Draw()
    gLOratio.Draw('psame')  
    line = ROOT.TLine(-0.5, 1, 15.5, 1)
    line.Draw('same')
    cc.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+cc.GetName()+'.png')
    cc.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+cc.GetName()+'.pdf')
    
    for j, ov in enumerate(Vovs[sipm]):
        gRes = fRes[sipm].Get('g_deltaT_totRatioCorr_bestTh_vs_bar_Vov%.02f_enBin01'%ov)
        if (gRes==None):
            gRes = fRes[sipm].Get('g_deltaT_energyRatioCorr_bestTh_vs_bar_Vov%.02f_enBin01'%ov)
        g_tRes_vs_LO[sipm,ov] = ROOT.TGraphErrors()
        g_tRes_vs_LO_L[sipm,ov] = ROOT.TGraphErrors()
        g_tRes_vs_LO_R[sipm,ov] = ROOT.TGraphErrors()
        for i in range(0,gRes.GetN()):
            bar  = gRes.GetX()[i]
            if (bar not in gLO.GetX()): continue
            tRes = gRes.GetY()[i]
            lo   = gLO.Eval(bar)*PDE(ov,sipm,'0')/PDE(ovRef[sipm],sipm,'0')
            lo_L   = gLO_L.Eval(bar)*PDE(ov,sipm,'0')/PDE(ovRef[sipm],sipm,'0')
            lo_R   = gLO_R.Eval(bar)*PDE(ov,sipm,'0')/PDE(ovRef[sipm],sipm,'0')
            #print (sipm, bar, lo, tRes)
            g_tRes_vs_LO[sipm,ov].SetPoint(g_tRes_vs_LO[sipm,ov].GetN(), lo, tRes)
            g_tRes_vs_LO[sipm,ov].SetPointError(g_tRes_vs_LO[sipm,ov].GetN()-1, errLO*lo, gRes.GetErrorY(i))
            g_tRes_vs_LO_L[sipm,ov].SetPoint(g_tRes_vs_LO_L[sipm,ov].GetN(), lo_L, tRes)
            g_tRes_vs_LO_L[sipm,ov].SetPointError(g_tRes_vs_LO_L[sipm,ov].GetN()-1, errLO*lo_L, gRes.GetErrorY(i))
            g_tRes_vs_LO_R[sipm,ov].SetPoint(g_tRes_vs_LO_R[sipm,ov].GetN(), lo_R, tRes)
            g_tRes_vs_LO_R[sipm,ov].SetPointError(g_tRes_vs_LO_R[sipm,ov].GetN()-1, errLO*lo_R, gRes.GetErrorY(i))


        #draw
        c2 = ROOT.TCanvas('c_timeResolution_vs_LOlab_%s_Vov%.02f'%(sipm,ov),'c_timeResolution_vs_LOlab_%s_Vov%.02f'%(sipm,ov), 600, 600)
    
        xmin = int( (g_tRes_vs_LO[sipm,ov].GetMean() - 4*g_tRes_vs_LO[sipm,ov].GetRMS())/10 ) * 10
        xmax = int( (g_tRes_vs_LO[sipm,ov].GetMean() + 4*g_tRes_vs_LO[sipm,ov].GetRMS())/10 ) * 10
        ymin = g_tRes_vs_LO[sipm,ov].GetMean(2)-4*g_tRes_vs_LO[sipm,ov].GetRMS(2)
        ymax = g_tRes_vs_LO[sipm,ov].GetMean(2)+4*g_tRes_vs_LO[sipm,ov].GetRMS(2) 
 
        hdummy[sipm] = ROOT.TH2F('hdummy%s_%d'%(sipm,i),'',100,xmin, xmax, 100, ymin, ymax)
        hdummy[sipm].GetXaxis().SetNdivisions(505)
        hdummy[sipm].GetXaxis().SetTitle('LO_{LAB} [Npe/MeV]')
        hdummy[sipm].GetYaxis().SetTitle('time resolution [ps]')
        hdummy[sipm].Draw()
        g_tRes_vs_LO[sipm,ov].SetMarkerStyle(20)
        g_tRes_vs_LO[sipm,ov].SetMarkerColor(cols[ov])
        g_tRes_vs_LO[sipm,ov].SetLineColor(cols[ov])
        g_tRes_vs_LO[sipm,ov].Draw('psame')
        latex = ROOT.TLatex(0.20,0.86,'%s - V_{OV} = %.02f V'%(sipm, ov)) 
        latex.SetNDC()
        latex.SetTextSize(0.045)
        latex.SetTextFont(42)
        latex.Draw('same') 

        '''
        c2.cd()
        fitFun = ROOT.TF1('fitFun','[0]*100000. * pow(x,[1])', 0,10000)
        fitFun.SetLineColor(j+1)
        fitFun.SetParameters(50, -1.0)
        g_tRes_vs_LO[sipm,ov].Fit(fitFun,'QSR+')
        print sipm, ov, fitFun.GetParameter(0), fitFun.GetParameter(1), fitFun.GetChisquare()/fitFun.GetNDF()
        
        c2.Update()
        ps = g_tRes_vs_LO[sipm,ov].FindObject("stats")
        ps.SetTextColor(g_tRes_vs_LO[sipm,ov].GetMarkerColor())
        ps.SetBorderSize(1)
        ps.SetX1NDC(0.18) # new x start position 
        ps.SetX2NDC(0.50)# new x end position 
        ps.SetY1NDC(0.20) # new y start position 
        ps.SetY2NDC(0.35)# new y end position 
        '''

        c2.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c2.GetName()+'.png')
        c2.SaveAs('/var/www/html/TOFHIR2X/MTDTB_CERN_June22/timeResolution_vs_LOlab/'+c2.GetName()+'.pdf')

