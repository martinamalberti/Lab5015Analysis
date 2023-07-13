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


outdir = '/eos/user/m/malberti/www/MTD/plotsForConferences2023/'

fnames = { 'HPK_nonIrr_LYSO818' : '/eos/home-s/spalluot/MTD/TB_FNAL_Mar23/Lab5015Analysis/plots/compareTimeResolution_vs_Vov_HPK_nonIrr_T1_T2_T3_angle52.root',
           #'HPK_nonIrr_LYSO813' : '/eos/home-s/spalluot/MTD/TB_FNAL_Mar23/Lab5015Analysis/plots/compareTimeResolution_vs_Vov_HPK_nonIrr_T1_T2_T3_angle52.root',
           'HPK_nonIrr_LYSO816' : '/eos/home-s/spalluot/MTD/TB_FNAL_Mar23/Lab5015Analysis/plots/compareTimeResolution_vs_Vov_HPK_nonIrr_T1_T2_T3_angle52.root',           
           'HPK_1E14_LYSO819_T-32C' : '/eos/home-s/spalluot/MTD/TB_CERN_May23/Lab5015Analysis/plots/plot_tRes_HPK_1E14_T1_T3_BTLequiv.root',
           'HPK_1E14_LYSO817_T-32C' : '/eos/home-s/spalluot/MTD/TB_CERN_May23/Lab5015Analysis/plots/plot_tRes_HPK_1E14_T1_T3_BTLequiv.root',
}

labels = {'HPK_nonIrr_LYSO818' : 'Type 1 - 25 #mum',
          'HPK_nonIrr_LYSO813' : 'Type 2 - 25 #mum',
          'HPK_nonIrr_LYSO816' : 'Type 3 - 25 #mum',

          'HPK_1E14_LYSO819_T-32C' : 'Type 1 - 25 #mum',
          'HPK_1E14_LYSO817_T-32C' : 'Type 3 - 25 #mum',
     }


gnames = {'HPK_nonIrr_LYSO818' : 'g_HPK_nonIrr_LYSO818_angle52_T12C',
          'HPK_nonIrr_LYSO813' : 'g_HPK_nonIrr_LYSO813_angle52_T12C',
          'HPK_nonIrr_LYSO816' : 'g_HPK_nonIrr_LYSO816_angle52_T12C',

          'HPK_1E14_LYSO819_T-32C' : 'g_data_vs_staticPower_average_HPK_1E14_LYSO819_angle64_T-32C',
          'HPK_1E14_LYSO817_T-32C' : 'g_data_vs_staticPower_average_HPK_1E14_LYSO817_angle64_T-32C'
}


# non-irradiated
c = ROOT.TCanvas('c_timeResolution_nonIrr_T1_T3','c_timeResolution_nonIrr_T1_T3', 600, 500)
hPad = ROOT.gPad.DrawFrame(0.,0.,4.0,120.)
hPad.SetTitle(";V_{OV} [V];time resolution [ps]")
hPad.Draw()
ROOT.gPad.SetTicks(1)

leg = ROOT.TLegend(0.60, 0.70, 0.89, 0.89)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
leg.SetTextFont(42)
leg.SetTextSize(0.045)

for mod in ['HPK_nonIrr_LYSO818','HPK_nonIrr_LYSO816']:
    f = ROOT.TFile.Open(fnames[mod])
    g = f.Get(gnames[mod]) 
    g.Draw('plsame')
    leg.AddEntry(g, '%s'%labels[mod],'PL')

leg.Draw()

latex = ROOT.TLatex(0.70,0.60,'non-irradiated')
latex.SetNDC()
latex.SetTextSize(0.045)
latex.SetTextFont(42)
latex.Draw()

cms_logo = draw_logo()
cms_logo.Draw()
   
c.SaveAs(outdir+'%s.png'%c.GetName())
c.SaveAs(outdir+'%s.pdf'%c.GetName())
hPad.Delete()



# 1E14 irradiated
c = ROOT.TCanvas('c_timeResolution_1E14_T1_T3','c_timeResolution_1E14_T1_T3', 600, 500)
hPad = ROOT.gPad.DrawFrame(0.,0.,120.0,120.)
hPad.SetTitle(";SiPM static power [mW];time resolution [ps]")
hPad.Draw()
ROOT.gPad.SetTicks(1)

for mod in ['HPK_1E14_LYSO819_T-32C','HPK_1E14_LYSO817_T-32C']:
    f = ROOT.TFile.Open(fnames[mod])
    g = f.Get(gnames[mod]) 
    g.Draw('plsame')
leg.Draw()

latex = ROOT.TLatex(0.60,0.60,'1 #times 10^{14} 1 MeV n_{eq}/cm^{2}')
latex.SetNDC()
latex.SetTextSize(0.045)
latex.SetTextFont(42)
latex.Draw()

cms_logo = draw_logo()
cms_logo.Draw()

c.SaveAs(outdir+'%s.png'%c.GetName())
c.SaveAs(outdir+'%s.pdf'%c.GetName())
hPad.Delete()
