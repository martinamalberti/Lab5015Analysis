#!/bin/bash
#!/bin/sh
echo
echo 'START---------------'
echo 'current dir: ' ${PWD}
cd /afs/cern.ch/work/m/malberti/MTD/TBatH8Sep2023/Lab5015Analysis/
echo 'current dir: ' ${PWD}
source scripts/setup.sh
echo $LD_LIBRARY_PATH
echo $ROOT_INCLUDE_PATH
./bin/drawPulseShapeTB.exe $1
echo 'STOP---------------'
echo
echo
