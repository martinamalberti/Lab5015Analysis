#! /usr/bin/env python
import math


def getVovEffDCR(data, label, ov_set) :
  label = label.replace('_TOFHIR2C','')
  ov_eff_A = float(data[label+'_A'][ov_set][0])
  dcr_A    = float(data[label+'_A'][ov_set][1])
  ov_eff_B = float(data[label+'_B'][ov_set][0])
  dcr_B    = float(data[label+'_B'][ov_set][1])

  if (len(data[label+'_A'][ov_set]) > 2):
    i_A      = float(data[label+'_A'][ov_set][2])
    i_B      = float(data[label+'_B'][ov_set][2])
  else:
    i_A = 0.
    i_B = 0.
    
  ov_eff =  0.5*(ov_eff_A+ov_eff_B)
  dcr    =  0.5*(dcr_A+dcr_B)
  i      =  0.5*(i_A+i_B)

  ov_err  = abs(0.5*(ov_eff_A-ov_eff_B))
  dcr_err = abs(0.5*(dcr_A-dcr_B))
  i_err   = abs(0.5*(i_A-i_B))

  return ([ov_eff, dcr, i, ov_err, dcr_err, i_err])


'''
def getVovEffDCR(data, sipm, ov_set) :
  ov_eff_A = float(data[sipm+'_A'][ov_set][0])
  dcr_A    = float(data[sipm+'_A'][ov_set][1])
  ov_eff_B = float(data[sipm+'_B'][ov_set][0])
  dcr_B    = float(data[sipm+'_B'][ov_set][1])
  ov_eff =  0.5*(ov_eff_A+ov_eff_B)
  dcr    =  0.5*(dcr_A+dcr_B)
  return ([ov_eff, dcr])      
'''
