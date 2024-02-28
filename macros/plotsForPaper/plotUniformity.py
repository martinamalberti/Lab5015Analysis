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
with open('/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_May2023/VovsEff_v2.json', 'r') as f:
   data = json.load(f)


inputdir = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_May2023/ANALYSIS/'
outdir   = '/eos/user/m/malberti/www/MTD/TOFHIR2C/plotsForPaper/'

modules = {'HPK_nonIrr_LYSO813_T5C', 'HPK_2E14_LYSO815_T-35C'}

fnames = { 'HPK_nonIrr_LYSO813_T5C' : inputdir+'TOFHIR2C/ModuleCharacterization/summaryPlots_HPK_nonIrr_LYSO813_T5C.root',
           'HPK_2E14_LYSO815_T-35C' : inputdir+'TOFHIR2C/ModuleCharacterization/summaryPlots_HPK_2E14_LYSO815_T-35C.root',
           'HPK_2E14_LYSO825_T-35C' : inputdir+'TOFHIR2X/ModuleCharacterization/summaryPlots_HPK_2E14_LYSO825_T-35C.root',
           'HPK_1E14_LYSO819_T-22C' : inputdir+'TOFHIR2X/ModuleCharacterization/summaryPlots_HPK_1E14_LYSO819_T-22C.root',
       }

labels = {'HPK_nonIrr_LYSO813_T5C' : '#splitline{HPK, 25 #mum}{non-irradiated}',
          'HPK_2E14_LYSO815_T-35C' : '#splitline{HPK, 25 #mum}{irradiated}',
          'HPK_2E14_LYSO825_T-35C' : 'HPK (20 #mum, 2E14), type 2',
          'HPK_1E14_LYSO819_T-22C' : 'HPK (25 #mum, 1E14), type 1',
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
   
   c = ROOT.TCanvas('c_timeResolution_vs_bar_%s'%mod,'c_timeResolution_vs_bar_%s'%mod, 600, 500)
   hPad = ROOT.TH2F('hPad','', 100, -0.5, 15.5, 100, 0, 120)
   hPad.SetTitle("; bar; time resolution [ps]")
   hPad.Draw()
   c.SetGridy()
   c.SetTicks()

   leg = ROOT.TLegend(0.65, 0.66, 0.95, 0.92)
   leg.SetBorderSize(0)
   leg.SetFillStyle(0)
   if (len(Vovs[mod])>4):
      leg.SetNColumns(2);
      leg.SetColumnSeparation(0.2);

   for iv,vov in enumerate(Vovs[mod]):
         
      g = f.Get('g_deltaT_totRatioCorr_bestTh_vs_bar_Vov%.2f_enBin01'%vov) 
      print('g_deltaT_totRatioCorr_bestTh_vs_bar_Vov%.2f_enBin01'%vov)
      print(g.GetN())
      
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

      g.SetMarkerStyle(20+iv)
      g.SetMarkerSize(1)
      if (g.GetMarkerStyle() == 22): g.SetMarkerSize(1.25)
      if ( mod == 'HPK_2E14_LYSO815_T-35C' and vov == 1.00): 
         g.SetMarkerColor(ROOT.kAzure+10)
         g.SetLineColor(ROOT.kAzure+10)
      g.Draw('psame')

      ovEff = vov
      if ('2E14' in mod or '1E14' in mod or '1E13' in mod):
         ovEff = getVovEffDCR(data, mod, ('%.02f'%vov))[0]
      leg.AddEntry(g, 'V_{OV} = %.2f V'%ovEff, 'PL') 
   leg.Draw()

   
   
   latex = ROOT.TLatex(0.20,0.84,'%s'%(labels[mod]))
   latex.SetNDC()
   latex.SetTextSize(0.050)
   latex.SetTextFont(42)
   latex.Draw()

   cms_logo = draw_logo()
   cms_logo.Draw()

   c.SaveAs(outdir+'%s.png'%c.GetName())
   c.SaveAs(outdir+'%s.pdf'%c.GetName())
   c.SaveAs(outdir+'%s.C'%c.GetName())
   hPad.Delete()
