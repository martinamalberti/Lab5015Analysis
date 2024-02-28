#! /usr/bin/env python
import math

import ROOT

def draw_logo():
    logo_x = 0.16
    logo = ROOT.TLatex()
    logo.SetNDC()
    logo.SetTextSize(0.045)
    logo.SetTextFont(62)
    logo.DrawText(logo_x,0.95,'CMS')
    logo.SetTextFont(52)
    #logo.DrawText(logo_x+0.07, 0.95, '  Phase-2 Preliminary')
    logo.DrawText(logo_x+0.07, 0.95, '  MTD Test beam')
    return logo
