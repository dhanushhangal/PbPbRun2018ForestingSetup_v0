#!/bin/bash
if [ $# -lt 1 ]
then
  echo "Usage: ./hit0suballruns_Express.sh <version>"
  exit 1
fi


for i in `cat expressrunstoprocess ` 
do
  dasgoclient --limit 0 --query "file dataset=/HIExpressPhysics/Run2018D-Express-v1/FEVT run=$i" > raw$i.list
  cat raw$i.list | awk -F "/000/" '{print "root://eoscms//eos/cms"$1"/000/"$2}' > ExpressPhysics.$i.${1}.list
done

for i in `cat expressrunstoprocess` 
do
	python submitForestExpress.py -q 8nh -o /eos/cms/store/group/phys_heavyions/dhangal/PbPb2018_ExpressForests/trial/v${1}/ -i ExpressPhysics.$i.${1}.list --proxy=proxyforprod
done

#rm allruns
cat expressrunstoprocess > allExpressruns
