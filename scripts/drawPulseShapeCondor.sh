#!/bin/bash
#!/bin/sh
echo
echo 'START---------------'
echo 'current dir: ' ${PWD}
cd /afs/cern.ch/work/m/malberti/MTD/TBatH8May2023/Lab5015Analysis/
echo 'current dir: ' ${PWD}
source scripts/setup.sh
./bin/drawPulseShapeTB.exe $1
echo 'STOP---------------'
echo
echo
