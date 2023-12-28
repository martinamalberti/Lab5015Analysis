#! /usr/bin/python

import ROOT
import glob
import math
import argparse
import json
import os
import numpy
from collections import OrderedDict 

from SiPM_base import *

aldos = ['A', 'B']


# TB June 2022 : ASIC2 ref module, ASIC0 odule under test
channelMap = {}
channelMap[(0,'A')] = 5
channelMap[(0,'B')] = 6
channelMap[(2,'A')] = 7
channelMap[(2,'B')] = 8

inputfolder = '/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_Jun2022/'


parser = argparse.ArgumentParser(description='draw IV scans from stress test')
parser.add_argument("--asic", type=int, required=True, help="asic") 
args = parser.parse_args()


################################
### edit here
################################

confs = [ '6.00',
          '6.01',
          '9.00',
          '9.01']

temps = {}
temps['6.00'] = -40.
temps['6.01'] = -35.
temps['9.00'] = -35.
temps['9.01'] = -40.

sipmTypes = {}
sipmTypes['6.00'] = 'HPK-MS' #15 um 
sipmTypes['6.01'] = 'HPK-MS' #15 um
sipmTypes['9.00'] = 'FBK-W4C' #15 um 
sipmTypes['9.01'] = 'FBK-W4C' #15 um 


labels = {}
labels['6.00'] = 'HPK_2E14_LYSO796'
labels['6.01'] = 'HPK_2E14_LYSO796'
labels['9.00'] = 'FBK_2E14_LYSO797'
labels['9.01'] = 'FBK_2E14_LYSO797'


gainDrops = {}
gainDrops['6.00'] = 0.08
gainDrops['6.01'] = 0.08
gainDrops['9.00'] = 0.08
gainDrops['9.01'] = 0.08




################################


graphs_IVarray = {}
graphs_IVch = {}
graphs_DCR = {}
for aldo in aldos:
        graphs_IVarray[(args.asic,aldo)] = ROOT.TGraph()
        graphs_IVch[(args.asic,aldo)] = ROOT.TGraph()
        graphs_DCR[(args.asic,aldo)] = ROOT.TGraph()


outfile = ROOT.TFile('./logIVEff_TBJune2022.root','RECREATE')
#outfile = ROOT.TFile('./logIVEff_TOFHIR2C.root','RECREATE')

output_dict = OrderedDict()

for conf in confs:
        print('\n'+labels[conf]+' - '+'T = %s'%temps[conf])
        for aldo in aldos:
                graphs_IVarray[(conf,args.asic,aldo)] = ROOT.TGraph()
                graphs_IVch[(conf,args.asic,aldo)] = ROOT.TGraph()
                graphs_DCR[(conf,args.asic,aldo)] = ROOT.TGraph()
        
        for aldo in aldos:
            print('>>> ALDO'+aldo)
        
            infilenames = glob.glob('%s/LOGS/logs_%s/logIV*_ASIC%d_ALDO%s_ch%d_*.root'%(inputfolder,conf,args.asic,aldo,channelMap[(args.asic,aldo)]))
            print ('%s/LOGS/logs_%s/logIV*_ASIC%d_ALDO%s_ch%d_*.root'%(inputfolder,conf,args.asic,aldo,channelMap[(args.asic,aldo)]))
            print(infilenames)
            
            VbiasList = []
            
            for infilename in infilenames:
                # get Vbr from bias_settings_aldo.tsv
                infilealdo = open('%s/CONF/config_%s/bias_settings_aldo.tsv'%(inputfolder,conf),'r')
                Vbr = 0
                for line in infilealdo:
                        tokens = line.split()
                        if tokens[2] == str(args.asic) and tokens[3] == aldo:
                                Vbr = tokens[4]
                print("Vbr: "+str(Vbr))
                
                infile = ROOT.TFile(infilename,"READ")
                graph = infile.Get('g_IV')
                for point in range(graph.GetN()):
                        x = graph.GetPointX(point)
                        y = graph.GetPointY(point)
                        
                        VovEff = x - float(Vbr) - y*1E-06*25.
                        DCR = y*1E-6 / (1.602E-19 * Gain(sipmTypes[conf],VovEff) * (1.-gainDrops[conf]) ) * 1E-09 / 16.
                        #print(round(x,2),round(x-float(Vbr),2),round(VovEff,2),round(y,2),round(y/16.,2),round(Gain(sipmTypes[conf],VovEff),0),round(DCR,1))
                        
                        graphs_IVarray[(conf,args.asic,aldo)].SetPoint(graphs_IVarray[(conf,args.asic,aldo)].GetN(),VovEff,y)
                        graphs_IVch[(conf,args.asic,aldo)].SetPoint(graphs_IVch[(conf,args.asic,aldo)].GetN(),VovEff,y/16.)
                        graphs_DCR[(conf,args.asic,aldo)].SetPoint(graphs_DCR[(conf,args.asic,aldo)].GetN(),VovEff,DCR)
                
                
                output_dict['%s_T%dC_%s'%(labels[conf],temps[conf],aldo)] = OrderedDict()
                for VovSet in numpy.arange(0.5, 3.1, 0.05):
                        current = graph.Eval(float(Vbr)+VovSet)
                        VovEff = VovSet - current*1E-06*25.
                        DCR = current*1E-6 / (1.602E-19 * Gain(sipmTypes[conf],VovEff) * (1.-gainDrops[conf]) ) * 1E-09 / 16.
                        #output_dict['%s_T%dC_%s'%(labels[conf],temps[conf],aldo)]['%.2f'%(VovSet)] = ['%.2f'%round(VovEff,2),'%.1f'%round(DCR,1)]
                        output_dict['%s_T%dC_%s'%(labels[conf],temps[conf],aldo)]['%.2f'%(VovSet)] = ['%.2f'%round(VovEff,2),'%.1f'%round(DCR,1), '%.2f'%round(current/16*1E-3,2)]

        
        for aldo in aldos:
                outfile.cd()

                graphs_IVarray[(conf,args.asic,aldo)].Sort()
                graphs_IVch[(conf,args.asic,aldo)].Sort()
                graphs_DCR[(conf,args.asic,aldo)].Sort()

                graphs_IVarray[(conf,args.asic,aldo)].Write('g_IVEff_array_%s_T%.0f_ALDO%s'%(labels[conf],temps[conf],aldo))
                graphs_IVch[(conf,args.asic,aldo)].Write('g_IVEff_ch_%s_T%.0f_ALDO%s'%(labels[conf],temps[conf],aldo))
                graphs_DCR[(conf,args.asic,aldo)].Write('g_DCR_%s_T%.0f_ALDO%s'%(labels[conf],temps[conf],aldo))
                
                
outfile.Close()

with open('VovsEff_TBJune2022.json', 'w') as fp:
        json.dump(output_dict, fp, indent=2)


'''
    c1 = ROOT.TCanvas('c1_ASIC%d_ALDO%s'%(args.asic,aldo),'c1_ASIC%d_ALDO%s'%(args.asic,aldo),1400,700)
    c1.Divide(2,1)
    c1.cd(1)
    hPad1 = ROOT.gPad.DrawFrame(xMin-0.1*(xMax-xMin),0.,xMax+0.1*(xMax-xMin),1.1*yMax)
    hPad1.SetTitle(";V_{bias} [V]; I [#muA]")
    hPad1.Draw() 
    graph_ave.SetMarkerStyle(20)
    graph_ave.SetMarkerSize(0.7)
    graph_ave.Draw("PL,same")
    
    c1.cd(2)
    hPad2 = ROOT.gPad.DrawFrame(xMin-0.1*(xMax-xMin),0.,xMax+0.1*(xMax-xMin),15.)
    hPad2.SetTitle(";V_{bias} [V]; #DeltalogI/#DeltaV [#muA/V]")
    hPad2.Draw()
    
    graph_dlogIdV = ROOT.TGraph()
    for point in range(1,graph_ave.GetN()):
        x1 = graph.GetPointX(point-1)
        y1 = graph.GetPointY(point-1)
        x2 = graph.GetPointX(point)
        y2 = graph.GetPointY(point)
        print(x1,y1,x2,y2)
        graph_dlogIdV.SetPoint(graph_dlogIdV.GetN(),0.5*(x1+x2),(math.log(y2)-math.log(y1))/(x2-x1))
    graph_dlogIdV.SetMarkerStyle(20)
    graph_dlogIdV.SetMarkerSize(0.7)
    graph_dlogIdV.Draw("PL,same")
    
    graph_dlogIdV_ave = ROOT.TGraph()
    for point in range(1,graph_dlogIdV.GetN()-1):
        x = graph_dlogIdV.GetPointX(point)
        y1 = graph_dlogIdV.GetPointY(point-1)
        y2 = graph_dlogIdV.GetPointY(point)
        y3 = graph_dlogIdV.GetPointY(point+1)
        graph_dlogIdV_ave.SetPoint(graph_dlogIdV_ave.GetN(),x,(y1+y2+y3)/3.)
    graph_dlogIdV_ave.SetLineColor(ROOT.kTeal)
    graph_dlogIdV_ave.SetLineWidth(2)
    graph_dlogIdV_ave.Draw("L,same")
    
    maximum = FindMaximumPoint(graph_dlogIdV_ave)
    fitFunc = ROOT.TF1("fitFunc","gaus(0)",xMin,xMax)
    fitFunc.SetParameter(1,maximum)
    graph_dlogIdV_ave.Fit(fitFunc,"QNRS+")
    
    xMin = maximum - fitFunc.GetParameter(2)
    xMax = maximum + fitFunc.GetParameter(2)
    fitFunc2 = ROOT.TF1("fitFunc2","gaus(0)",xMin,xMax)
    graph_dlogIdV_ave.Fit(fitFunc2,"QNRS+")
    fitFunc2.SetLineColor(ROOT.kRed)
    fitFunc2.SetLineWidth(1)
    fitFunc2.Draw("same")
    
    Vbr = fitFunc2.GetParameter(1)
    latex = ROOT.TLatex(Vbr,fitFunc2.Eval(Vbr),'V_{br.} = %.2f V'%Vbr)
    latex.SetTextFont(42)
    latex.SetTextSize(0.04)
    latex.SetTextColor(ROOT.kRed)
    latex.Draw("same")
    
    print('ASIC %d, ALDO %s:   Vbr = %.2f'%(args.asic,aldo,Vbr))
    c1.Print('../logs/IV_%s_ASIC%d_ALDO%s.png'%(args.label, args.asic,aldo))
    
    key='0       0       %d       %s'%(args.asic,aldo)
    VbrString='%.2f'%Vbr
    command = 'sed -i \"s%^'+key+'.*$%'+key+'        '+VbrString+'           5.00%\"'+' ../config/bias_settings_aldo.tsv'
    #print(command)
    os.system(command)
'''
