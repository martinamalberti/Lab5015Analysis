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


from SiPM import *
from VovsEff import *

# Import file with VovEff and DCR                                                                                                                                                
#with open('/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_May2023/VovsEff_TOFHIR2C.json', 'r') as f:
with open('/eos/cms/store/group/dpg_mtd/comm_mtd/TB/MTDTB_H8_May2023/VovsEff.json', 'r') as f:
   data = json.load(f)

for ov in [0.60, 0.80, 1.00, 1.25, 1.50, 2.00]:
    ovEff = getVovEffDCR(data, 'HPK_2E14_LYSO815_T-30C', ('%.02f'%ov))[0]
    dcr   = getVovEffDCR(data, 'HPK_2E14_LYSO815_T-30C', ('%.02f'%ov))[1]
    current = getVovEffDCR(data, 'HPK_2E14_LYSO815_T-30C', ('%.02f'%ov))[2]
  
    staticCurrent = dcr*1E09 * Gain('HPK-PIT-C25-ES2', ovEff, '2E14') * 1.602E-19;
    staticPower = staticCurrent * (37. + ovEff) * 1000.; # P  = V I (in mW)   



    print(current, staticCurrent*1E3, staticPower)
    
