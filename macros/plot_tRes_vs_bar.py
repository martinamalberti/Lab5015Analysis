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

#set the tdr style
tdrstyle.setTDRStyle()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)
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

from VovsEff import *
# Import file with VovEff and DCR
with open('/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_May2023/VovsEff.json', 'r') as f:
   data = json.load(f)

modules = {'HPK_nonIrr_LYSO813_T5C', 'HPK_2E14_LYSO815_T-35C', 'HPK_2E14_LYSO825_T-35C', 'HPK_1E14_LYSO819_T-22C'}

fnames = { 'HPK_nonIrr_LYSO813_T5C' : '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2C/summaryPlots_HPK_nonIrr_LYSO813_T5C.root',
           'HPK_2E14_LYSO815_T-35C' : '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_2E14_LYSO815_T-35C.root',
           'HPK_2E14_LYSO825_T-35C' : '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_2E14_LYSO825_T-35C.root',
           'HPK_1E14_LYSO819_T-22C' : '/afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/plots/TOFHIR2X/summaryPlots_HPK_1E14_LYSO819_T-22C.root',
       }

labels = {'HPK_nonIrr_LYSO813_T5C' : 'HPK (25 #mum) + LYSO813 (prod1, type2) T=5#circC',
          'HPK_2E14_LYSO815_T-35C' : 'HPK (25 #mum, 2E14) + LYSO815 (prod1, type2) T=-35#circC',
          'HPK_2E14_LYSO825_T-35C' : 'HPK (20 #mum, 2E14) + LYSO825 (prod1, type2) T=-35#circC',
          'HPK_1E14_LYSO819_T-22C' : 'HPK (25 #mum, 1E14) + LYSO819 (prod1, type1) T=-22#circC',
     }


Vovs = { 'HPK_nonIrr_LYSO813_T5C' : [0.80, 1.25, 1.50, 3.50],
         'HPK_2E14_LYSO815_T-35C' : [1.00, 1.25, 1.50, 2.00],
         'HPK_2E14_LYSO825_T-35C' : [0.80, 1.00, 1.25, 1.50, 2.00],
         'HPK_1E14_LYSO819_T-22C' : [0.80, 1.00, 1.25, 1.50, 2.00],
}

bestVovs = { 'HPK_nonIrr_LYSO813_T5C' : 0.80,
             'HPK_2E14_LYSO815_T-35C' : 1.50,
             'HPK_2E14_LYSO825_T-35C' : 1.50,
             'HPK_1E14_LYSO819_T-22C' : 2.00

          }

h = {}
h_all = ROOT.TH1F('h_all','h_all', 40, -0.8,0.8)
h_irr = ROOT.TH1F('h_irr','h_irr', 40, -0.8,0.8)

for mod in modules:
    f = ROOT.TFile.Open(fnames[mod])
    

    latex = ROOT.TLatex(0.18,0.94,'%s'%(labels[mod]))
    latex.SetNDC()
    latex.SetTextSize(0.05)
    latex.SetTextFont(42)

    c = ROOT.TCanvas('c_timeResolution_vs_bar_%s'%mod,'c_timeResolution_vs_bar_%s'%mod)
    hPad = ROOT.TH2F('hPad','', 100, -0.5, 15.5,100, 0,130)
    hPad.SetTitle("; bar; #sigma_{t} [ps]")
    hPad.Draw()
    c.SetGridy()
    leg = ROOT.TLegend(0.20, 0.90, 0.60, 0.70)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    if (len(Vovs[mod])>4):
        leg.SetNColumns(2);
        leg.SetColumnSeparation(0.2);
    for vov in Vovs[mod]:
        g = f.Get('g_deltaT_totRatioCorr_bestTh_vs_bar_Vov%.2f_enBin01'%vov) 
        
        if (vov == bestVovs[mod]): 
           h[mod] = ROOT. TH1F('h_%s'%mod,'h_%s'%mod, 40, -0.8,0.8 )
           h[mod].SetLineColor(g.GetLineColor())
           h[mod].SetFillColorAlpha(g.GetLineColor(),0.2)
           for i in range(0,g.GetN()):
              x = (g.GetPointY(i) - g.GetMean(2) )/g.GetMean(2)
              h[mod].Fill(x)
              h_all.Fill(x)
              if ('nonIrr' not in mod):
                 h_irr.Fill(x)

        g.SetMarkerSize(1)
        g.Draw('psame')
        ovEff = vov
        if ('2E14' in mod or '1E14' in mod or '1E13' in mod):
            ovEff = getVovEffDCR(data, mod, ('%.02f'%vov))[0]
        leg.AddEntry(g, 'V_{OV} = %.2f V'%ovEff, 'PL') 
    leg.Draw()
    latex.Draw()
    c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/tRes_uniformity/%s.png'%c.GetName())
    c.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/tRes_uniformity/%s.pdf'%c.GetName())
    hPad.Delete()


    c2 = ROOT.TCanvas('c_timeResolution_spread_%s'%mod,'c_timeResolution_spread_%s'%mod, 600, 600)
    c2.SetTickx()
    c2.SetTicky()
    h[mod].GetYaxis().SetRangeUser(0, h[mod].GetMaximum()*1.2)
    h[mod].GetXaxis().SetTitle('(#sigma_{t} - <#sigma_{t}>)/<#sigma_{t}>')
    h[mod].Draw('')
    fGaus = ROOT.TF1('fGaus_%s'%mod,'gaus', -1,1)
    fGaus.SetParameters(h[mod].GetMaximum(), h[mod].GetMean(), h[mod].GetRMS())
    h[mod].Fit(fGaus,'QRL')
    latex.Draw()
    latex2 = ROOT.TLatex(0.65,0.75,'RMS = %.1f %%'%(fGaus.GetParameter(2)*100))
    latex2.SetNDC()
    latex2.SetTextSize(0.05)
    latex2.SetTextFont(42)
    latex2.Draw()
    c2.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/tRes_uniformity/%s.png'%c2.GetName())
    c2.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/tRes_uniformity/%s.pdf'%c2.GetName())

c3 = ROOT.TCanvas('c_timeResolution_spread_irr','c_timeResolution_spread_irr', 600, 600)
c3.SetTickx()
c3.SetTicky()
h_irr.SetFillColorAlpha(1,0.2)
h_irr.GetYaxis().SetRangeUser(0, h_irr.GetMaximum()*1.2)
h_irr.GetXaxis().SetTitle('(#sigma_{t} - <#sigma_{t}>)/<#sigma_{t}>')
h_irr.Draw('')
fGaus = ROOT.TF1('fGaus','gaus', -1,1)
fGaus.SetParameters(h_irr.GetMaximum(), h_irr.GetMean(), h_irr.GetRMS())
h_irr.Fit(fGaus,'QRL')
latex2 = ROOT.TLatex(0.65,0.75,'RMS =  %.1f %%'%(fGaus.GetParameter(2)*100))
latex2.SetNDC()
latex2.SetTextSize(0.05)
latex2.SetTextFont(42)
latex2.Draw()
c3.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/tRes_uniformity/%s.png'%c3.GetName())
c3.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/tRes_uniformity/%s.pdf'%c3.GetName())
fGaus.Delete()

c4 = ROOT.TCanvas('c_timeResolution_spread_all','c_timeResolution_spread_all', 600, 600)
h_all.SetFillColorAlpha(1,0.2)
h_all.GetYaxis().SetRangeUser(0, h_all.GetMaximum()*1.2)
h_all.GetXaxis().SetTitle('(#sigma_{t} - <#sigma_{t}>)/<#sigma_{t}>')
h_all.Draw('')
fGaus = ROOT.TF1('fGaus','gaus', -1,1)
fGaus.SetParameters(h_irr.GetMaximum(), h_irr.GetMean(), h_irr.GetRMS())
h_all.Fit(fGaus,'QRL')
latex2 = ROOT.TLatex(0.65,0.75,'RMS =  %.1f %%'%(fGaus.GetParameter(2)*100))
latex2.SetNDC()
latex2.SetTextSize(0.05)
latex2.SetTextFont(42)
latex2.Draw()
c4.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/tRes_uniformity/%s.png'%c4.GetName())
c4.SaveAs('/eos/user/m/malberti/www/MTD/TOFHIR2X/MTDTB_CERN_May23/tRes_uniformity/%s.pdf'%c4.GetName())
