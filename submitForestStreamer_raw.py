#!/usr/bin/env python
import os,sys
import optparse
import commands
import time
import re

#command line configuration
usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-q', '--queue'      ,dest='queue'  ,help='batch queue'          ,default='cmscaf1nd')#cmscaf1nd
parser.add_option('-j', '--jobs'       ,dest='jobs'   ,help='number of jobs'       ,default=1,    type=int)
parser.add_option('-i', '--inputF'     ,dest='inputF',help='input file list'     ,default='express.list', type='string')
parser.add_option('-n', '--nevts'      ,dest='nevts'  ,help='number of evetns/job' ,default=5,  type=int)
parser.add_option(      '--proxy'      ,dest='proxy'  ,help='proxy to be used'     ,default=None, type='string')
parser.add_option('-o', '--output'     ,dest='output' ,help='output directory'     ,default='/store/group/phys_heavyions/bdiab/PbPb2018/Forests')
parser.add_option('-a', '--AODoutput'  ,dest='AODoutput' ,help='AOD output directory',default='/store/group/phys_heavyions/dhangal/PbPb2018_streamerAOD/v0')

(opt, args) = parser.parse_args()

#prepare working directory
cmsswBase=os.environ['CMSSW_BASE']
workBase=os.getcwd()
jobsBase='%s/FARM%s'%(workBase,time.time())
os.system('mkdir -p %s'%jobsBase)

recoCfg = "CMSSW_10_3_1_RECO_EXPRESS.py"
forestCfg = "runForestAOD_pponAA_DATA_103X.py"

#init a new proxy if none has been passed
if opt.proxy is None:
    print 'Initiating a new proxy'
    os.system('voms-proxy-init --voms cms --valid 72:00')
    os.system('cp /tmp/x509up_u`id -u \`whoami\`` %s/proxyforprod' % workBase)
    print 'Production proxy is now available in %s/proxyforprod (valid for 72h)' % workBase

#loop over the required number of jobs
inputfile='%s'% (opt.inputF)
newfile='new_%s' % (opt.inputF)
f = open(inputfile,'r')
newf = open(newfile,'w')
jobCounter=0
m = re.compile(r"RAW/\d\d\d\d\d\d") #used to find run number
for line in f:
    if not line.find('root://eoscms//eos/cms') :
        if not line.startswith('#') :
            print line
            newf.write(line.replace('root://eoscms//eos/cms', '# root://eoscms//eos/cms'))

            found = m.findall(line)
            #outdir = '%s/%s' % (opt.output,found[0])
            outdir1 = '%s/%s%s%s' % (opt.output,found[0][0],found[0][1],found[0][2])
            outdir2 = '%s/%s%s%s' % (outdir1,found[0][4],found[0][5],found[0][6])
            outdir3 = '%s/%s%s%s' % (outdir2,found[0][7],found[0][8],found[0][9])            
           
            outdir4 = '%s/%s%s%s' % (opt.AODoutput,found[0][0],found[0][1],found[0][2])
            outdir5 = '%s/%s%s%s' % (outdir4,found[0][4],found[0][5],found[0][6])
            outdir6 = '%s/%s%s%s' % (outdir5,found[0][7],found[0][8],found[0][9])            
            
            #create bash script to be submitted
            scriptFile = open('%s/runJob_%d.sh'%(jobsBase,jobCounter), 'w')
            scriptFile.write('#!/bin/bash\n')
            scriptFile.write('export X509_USER_PROXY=%s/proxyforprod\n' % workBase)
            scriptFile.write('cd %s/src\n'%cmsswBase)
            scriptFile.write('eval `scram r -sh`\n')
            scriptFile.write('cd -\n')
            scriptFile.write('cp %s/%s %s \n' % (workBase,forestCfg,jobsBase))
            scriptFile.write('cp %s/%s %s \n' % (workBase,recoCfg,jobsBase))
            scriptFile.write('cp %s/%s .\n' % (workBase,forestCfg))
            scriptFile.write('cp %s/%s .\n' % (workBase,recoCfg))
#            scriptFile.write('cp $CMSSW_BASE/src/HeavyIonsAnalysis/JetAnalysis/test/*.db .\n')
	    scriptFile.write('cmsRun %s outputFile=step3_%d.root maxEvents=100 inputFiles=%s\n' % (recoCfg,jobCounter,line) )
            scriptFile.write('cd %s/src\n'%cmsswBase)
            #scriptFile.write('cd /afs/cern.ch/user/d/dhangal/CMSSW_10_3_0_patch1/src\n')
            scriptFile.write('eval `scram r -sh`\n')
            scriptFile.write('cd -\n')
	    scriptFile.write('cmsRun %s outputFile=HiForest_%d.root maxEvents=100 inputFiles=file:step3_%d_numEvent100.root\n' % (forestCfg,jobCounter,jobCounter) )
            scriptFile.write('eos mkdir %s\n' % outdir1)
            scriptFile.write('eos mkdir %s\n' % outdir2)
            scriptFile.write('eos mkdir %s\n' % outdir3)
            scriptFile.write('ls\n')
            #use only if you want to save the streamer AOD files
            scriptFile.write('eos cp step3_%d_numEvent100.root root://eoscms//eos/cms%s/step3_%d_numEvent100.root\n' % (jobCounter,outdir6,jobCounter) )
            ###########################################
            scriptFile.write('eos cp HiForest_%d_numEvent100.root root://eoscms//eos/cms%s/HiForest_%d_numEvent100.root\n' % (jobCounter,outdir3,jobCounter) )
            scriptFile.write('rm HiForest_%d_numEvent100.root\n' % (jobCounter))
            scriptFile.write('rm step3_%d_numEvent100.root\n' % (jobCounter))
            scriptFile.close()

            #preare to run it
            os.system('chmod u+rwx %s/runJob_%d.sh' % (jobsBase,jobCounter))

            #submit it to the batch or run it locally
            if opt.queue=='':
                print 'Job #%d will run locally' % jobCounter
                os.system('%s/runJob_%d.sh' % (jobsBase,jobCounter) )
            else:
                print 'Job #%d will run remotely' % jobCounter
                os.system("echo bsub -q %s -R \"swp>1000 && pool>30000\" -J FOREST_%d \'%s/runJob_%d.sh\'" % (opt.queue,jobCounter,jobsBase,jobCounter) )
                os.system("bsub -q %s -N -u null@null -R \"swp>1000 && pool>30000\" -J FOREST_%d \'%s/runJob_%d.sh\'" % (opt.queue,jobCounter,jobsBase,jobCounter) )

            time.sleep(0.5)
	    #cooldown cycle to avoid overloading the submit buffer - reco script is BIG
	    if jobCounter%50==0:
		time.sleep(10)
	    jobCounter+=1
