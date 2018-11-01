# PbPbRun2018ForestingSetup_v0

First iteration setup. 

## Setup environment:
```bash
cmsrel CMSSW_10_3_0_patch1
cd CMSSW_10_3_0_patch1/src
cmsenv
# Main forest
git cms-merge-topic -u bi-ran:forest_CMSSW_10_2_0_mergeable_103X
# Switch to the branch HEAD
git remote add  biran git@github.com:bi-ran/cmssw.git
git fetch biran
git checkout -b forest_CMSSW_10_2_0_mergeable_103X remotes/biran/forest_CMSSW_10_2_0_mergeable_103X
cd HeavyIonsAnalysis/JetAnalysis/python/jets
./makeJetSequences.sh
cd ../../../..
scram build -j4
# run the tests before making any changes to make sure that you have a working env: 
cd HeavyIonsAnalysis/JetAnalysis/test
./tests.sh

#In a separate production area, preferably in the work area
git clone git@github.com:dhanushhangal/PbPbRun2018ForestingSetup_v0.git
```

## Run interactively:
```bash
cmsRun runForestAOD_pponAA_MB_102X.py outputFile=HiForest_test.root maxEvents=3 inputFiles=file:step3_numEvent3.root
```

## Submit one streamer run to lxplus batch

This script does both jobs of RECO-ing and foresting the raw streamer files:
```bash
python submitForestStreamer.py -q 1nd -o /store/group/phys_heavyions/dhangal/PbPb_2018_streamer/trial -i sample_streamer.txt
```

## Submit one express run to the lxplus batch
```bash
python submitForestExpress.py -q 1nd -o /store/group/phys_heavyions/dhangal/ExpressForests/v1 -i ExpressForest_*_*.txt
```

## Submit all runs in 'expressrunstoprocess' to caf queue
```bash
./hit0suballruns_Express.sh 1
```
this will also append the runs in 'expressrunstoprocess' to 'allruns' for bookkeeping

That's it! bjobs to check job status and look in the path for the forests /store/group/phys_heavyions/YOURUSERNAME

##############################################################

## Making sure the RECO scripts and the foresting scripts work independently in the submitForestStreamer.py script

Verify the RECO script works fine and produces the streamer AOD input
```bash
cmsRun RunExpressProcessingCfg.py outputFile=step3_0.root maxEvents=3 inputFiles=root://eoscms//eos/cms/store/t0streamer/Data/HIPhysicsMinimumBias0/000/325/174/run325174_ls0015_streamHIPhysicsMinimumBias0_StorageManager.dat
```

Verfiy that the foresting script works with the output of the above RECO script as the input for this 
```bash
cmsRun runForestAOD_pponAA_MB_102X.py outputFile=HiForest_test.root maxEvents=3 inputFiles=file:step3_numEvent3.root
```
