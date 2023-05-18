#! /usr/bin/env python
import math


def getVovEffDCR(data, lyso, sipm, ov_set) :
  ov_eff_A = float(data[sipm+'_'+lyso+'_A'][ov_set][0])
  dcr_A    = float(data[sipm+'_'+lyso+'_A'][ov_set][1])
  ov_eff_B = float(data[sipm+'_'+lyso+'_B'][ov_set][0])
  dcr_B    = float(data[sipm+'_'+lyso+'_B'][ov_set][1])
  ov_eff =  0.5*(ov_eff_A+ov_eff_B)
  dcr    =  0.5*(dcr_A+dcr_B)
  return ([ov_eff, dcr])      
