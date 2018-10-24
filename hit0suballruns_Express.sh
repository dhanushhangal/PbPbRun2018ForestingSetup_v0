#!/bin/bash
if [ $# -lt 1 ]
then
  echo "Usage: ./hit0suballruns_Express.sh <version>"
  exit 1
fi


for i in `cat expressrunstoprocess ` 
do
  dasgoclient --limit 0 --query "file dataset=/ExpressPhysics/Run2017G-Express-v1/FEVT run=$i" > raw$i.list
  cat raw$i.list | awk -F "/000/" '{print "root://eoscms//eos/cms"$1"/000/"$2}' > ExpressPhysics.$i.${1}.list
done

for i in `cat expressrunstoprocess` 
do
	python submitForestExpress.py -q cmscaf1nd -o /eos/cms/store/group/phys_heavyions/dhangal/ExpressForests/v${1}/ -i ExpressPhysics.$i.${1}.list --proxy=proxyforprod
done

#rm allruns
cat expressrunstoprocess > allExpressruns
