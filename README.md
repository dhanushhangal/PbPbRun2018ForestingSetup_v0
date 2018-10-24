# PbPbRun2018ForestingSetup_v0

First iteration setup. 

## Setup environment:
```bash
cmsrel CMSSW_8_0_23
cd CMSSW_8_0_23/src
cmsenv
# Main forest
git cms-merge-topic -u CmsHI:forest_CMSSW_8_0_22
# Dfinder
git clone -b test80forpPb https://github.com/taweiXcms/Bfinder.git
git clone git@github.com:kurtejung/production.git
scram build -j8

# grab submit scripts
cp production/pARun2016ForestingSetup_v0/* .
```

## Run interactively:
```bash
cmsRun runForestAOD_pPb_DATA_80X.py outputFile=HiForest_test.root maxEvents=2 inputFiles=root://eoscms//eos/cms/store/express/PARun2016A/ExpressPhysicsPA/FEVT/Express-v1/000/284/755/00000/08BA510B-D6A4-E611-84C9-02163E0141DE.root
```

## Submit one streamer run to caf queue

This needs a fresh checkout of CMSSW_8_0_23 independent of the forest - there are conflicts in the reco script if you use the same CMSSW_BASE as the forest.  Instead do, from a clean area:
```bash
cmsrel CMSSW_8_0_23
```
then change the path of L56 in submitForestStreamer.py to correspond with the path of the new checked out 8_0_23 release.  
!! MAKE SURE you cmsenv in your FOREST release though - NOT the new fresh release or else the scripts will not work!
Once this is setup, and your streamer RECO script has been created (see bottom of this README), you can forest streamers on the batch farm:
```bash
## NOTE - The streamers need to be RECOed also - see instructions at the bottom of this README to get the reco cfg...
python submitForestStreamer.py -q cmscaf1nd -o /store/group/phys_heavyions/kjung/StreamerForests/v1 -i ExpressPA.284755.v1.txt
```

## Submit one express run to the caf queue
```bash
python submitForestExpress.py -q cmscaf1nd -o /store/group/phys_heavyions/kjung/ExpressForests/v1 -i ExpressForest_284755_v1.txt
```

## Submit all runs in 'expressrunstoprocess' to caf queue
```bash
./hit0suballruns.sh 1
```
this will also append the runs in 'expressrunstoprocess' to 'allruns' for bookkeeping


##############################################################

## How to run RECO on streamer (raw) files

```bash
cmsrel CMSSW_8_0_23
cd CMSSW_8_0_23/src
cmsenv
git cms-addpkg Configuration/DataProcessing
scram build -j8
git clone git@github.com:kurtejung/production.git
cp production/pARun2016ForestingSetup_v0/submitRunExpressProcessingCfg.py Configuration/DataProcessing/test/
cd Configuration/DataProcessing/test/

# you can look in run_CfgTest.sh to see different running configuration, I will show how to do Express pPb on DATA
python RunExpressProcessing.py --scenario ppEra_Run2_2016_pA --global-tag 80X_dataRun2_Express_v15 --lfn /some/path/ --fevt
```
This will generate a RunExpressProcessingCfg.py config, make the following changes:
```python
# replace process.source block with this to read the streamer dat files 
process.source = cms.Source("NewEventStreamFileReader",
                            fileNames = cms.untracked.vstring('/store/t0streamer/Data/HIExpress/000/262/548/run262548_ls0333_streamHIExpress_StorageManager.dat')
)
```
Now just cmsRun RunExpressProcessingCfg.py to test it/run it interactively

To submit to lxbatch you need to make more changes.
```python
# add this at the top
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing('analysis')
options.register ('isPP',
                  False,
                  VarParsing.multiplicity.singleton,
                  VarParsing.varType.bool,
                  "Flag if this is a pp simulation")
options.parseArguments()

# replace the relevant blocks with these three

process.source = cms.Source("NewEventStreamFileReader",
    fileNames = cms.untracked.vstring(options.inputFiles[0])
)

# in process.write_FEVT = cms.OutputModule("PoolOutputModule",
fileName = cms.untracked.string(options.outputFile),

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
)
```

You can test if the changes are properly made by trying the follwoing:
```bash
cmsRun RunExpressProcessingCfg.py outputFile=step3_0.root maxEvents=3 inputFiles=root://eoscms//eos/cms/store/t0streamer/Data/ExpressPA/000/285/216/run285216_ls0045_streamExpressPA_StorageManager.dat
```

Now you're ready to submit, to do that:
```bash
# the second time you run this add --proxy=proxyforprod to the following command , also set the outputpath/username
python submitForestStreamer.py -q cmscaf1nd -o /store/group/phys_heavyions/kjung/StreamerForests/v1 -i ExpressPA.284755.v1.txt --proxy=proxyforprod
```

That's it! bjobs to check job status and look in the path for those  /store/group/phys_heavyions/YOURUSERNAME/reco/HIPhysicsMinBiasUPC/v0/
