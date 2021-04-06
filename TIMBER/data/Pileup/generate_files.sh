#!/bin/bash
PU18=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PileUp/pileup_latest.txt
PU17=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/PileUp/pileup_latest.txt
PU16=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/pileup_latest.txt

golden18UL=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt
golden17UL=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt
golden16UL=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt
golden18=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/ReReco/Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt
golden17=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/ReReco/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt
golden16=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt

if [[ -n $1 && $1=="--download" ]]; then
    scp $USER@lxplus.cern.ch:$PU18 pileup_2018.txt
    scp $USER@lxplus.cern.ch:$PU17 pileup_2017.txt
    scp $USER@lxplus.cern.ch:$PU16 pileup_2016.txt

    scp $USER@lxplus.cern.ch:$golden18UL Cert_golden18UL.txt
    scp $USER@lxplus.cern.ch:$golden17UL Cert_golden17UL.txt
    scp $USER@lxplus.cern.ch:$golden16UL Cert_golden16UL.txt
    scp $USER@lxplus.cern.ch:$golden18 Cert_golden18.txt
    scp $USER@lxplus.cern.ch:$golden17 Cert_golden17.txt
    scp $USER@lxplus.cern.ch:$golden16 Cert_golden16.txt
fi

MINBIAS=$((69200))
MINBIAS_UP=$(bc <<< "$MINBIAS*(1.0+0.046)")
MINBIAS_DOWN=$(bc <<< "$MINBIAS*(1.0-0.046)")

OLDIFS=$IFS
IFS=','
for i in $MINBIAS,"" $MINBIAS_UP,"_up" $MINBIAS_DOWN,"_down"; do set -- $i;
    for j in 16 17 18; do
        echo "pileupCalc.py -i Cert_golden${j}UL.txt --inputLumiJSON pileup_20${j}.txt --calcMode true --minBiasXsec $1 --maxPileupBin 120 --numPileupBins 120 pileup_20${j}UL$2.root"
        pileupCalc.py -i Cert_golden${j}UL.txt --inputLumiJSON pileup_20${j}.txt --calcMode true --minBiasXsec $1 --maxPileupBin 120 --numPileupBins 120 pileup_20${j}UL$2.root
        echo "pileupCalc.py -i Cert_golden${j}.txt --inputLumiJSON pileup_20${j}.txt --calcMode true --minBiasXsec $1 --maxPileupBin 120 --numPileupBins 120 pileup_20${j}$2.root"
        pileupCalc.py -i Cert_golden${j}.txt --inputLumiJSON pileup_20${j}.txt --calcMode true --minBiasXsec $1 --maxPileupBin 120 --numPileupBins 120 pileup_20${j}$2.root
    done
done