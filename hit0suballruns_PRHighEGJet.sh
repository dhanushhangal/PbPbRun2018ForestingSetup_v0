#!/bin/bash
if [ $# -lt 1 ]
then
  echo "Usage: ./hit0suballruns_PRHighEGJet.sh <version>"
  exit 1
fi


for i in `cat PRrunstoprocess ` 
do
  dasgoclient --limit 0 --query "file dataset=/HighEGJet/Run2017G-PromptReco-v1/AOD run=$i" > raw$i.list
  cat raw$i.list | awk -F "/000/" '{print "root://xrootd-cms.infn.it/"$1"/000/"$2}' > PRPhysics.HighEGJet.$i.${1}.list
  #cat raw$i.list | awk -F "/000/" '{print "root://eoscms//eos/cms"$1"/000/"$2}' > ExpressPhysics.$i.${1}.list
done

for i in `cat PRrunstoprocess` 
do
	python submitForestPR.py -q cmscaf1nd -o /eos/cms/store/group/phys_heavyions/dhangal/pp_2017_Prompt_Reco/HighEGJet/v${1}/ -i PRPhysics.HighEGJet.$i.${1}.list --proxy=proxyforprod
done

#rm allruns
cat PRrunstoprocess >> PRallruns
