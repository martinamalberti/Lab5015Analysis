#! /usr/bin/env python
import math

'''
def getVovEffDCR(data, lyso, sipm, temperature, ov_set) :
  label_A = sipm+'_'+lyso+'_T'+temp+'C_A'
  label_B = sipm+'_'+lyso+'_T'+temp+'C_B'
  ov_eff_A = float(data[label_A][ov_set][0])
  dcr_A    = float(data[label_A][ov_set][1])
  ov_eff_B = float(data[label_B][ov_set][0])
  dcr_B    = float(data[label_B][ov_set][1])
  ov_eff =  0.5*(ov_eff_A+ov_eff_B)
  dcr    =  0.5*(dcr_A+dcr_B)
  return ([ov_eff, dcr])      
'''


def getVovEffDCR(data, label, ov_set) :
  label = label.replace('_TOFHIR2C','')
  ov_eff_A = float(data[label+'_A'][ov_set][0])
  dcr_A    = float(data[label+'_A'][ov_set][1])
  i_A      = float(data[label+'_A'][ov_set][2])
  ov_eff_B = float(data[label+'_B'][ov_set][0])
  dcr_B    = float(data[label+'_B'][ov_set][1])
  i_B      = float(data[label+'_B'][ov_set][2])

  ov_eff =  0.5*(ov_eff_A+ov_eff_B)
  dcr    =  0.5*(dcr_A+dcr_B)
  i      =  0.5*(i_A+i_B)

  ov_err  = abs(0.5*(ov_eff_A-ov_eff_B))
  dcr_err = abs(0.5*(dcr_A-dcr_B))
  i_err   = abs(0.5*(i_A-i_B))

  return ([ov_eff, dcr, i, ov_err, dcr_err, i_err])      

