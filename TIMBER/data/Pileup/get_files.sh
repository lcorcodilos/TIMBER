scp $USER@lxplus.cern.ch:/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/UltraLegacy/*99bins.root UltraLegacy/
scp $USER@lxplus.cern.ch:/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/PileUp/UltraLegacy/*99bins.root UltraLegacy/ 
scp $USER@lxplus.cern.ch:/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PileUp/UltraLegacy/*99bins.root UltraLegacy/

scp $USER@lxplus.cern.ch:/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PileUp/PrelLum13TeV/*99bins.root Preliminary/
scp $USER@lxplus.cern.ch:/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/PileUp/PrelLum13TeV/*99bins.root Preliminary/
scp $USER@lxplus.cern.ch:/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/PrelLum15And1613TeV/*99bins.root Preliminary/

golden18UL=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt
golden17UL=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt
golden16UL=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt
golden18=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/ReReco/Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt
golden17=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/ReReco/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt
golden16=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt

scp $USER@lxplus.cern.ch:$golden18UL Cert_golden2018UL.txt
scp $USER@lxplus.cern.ch:$golden17UL Cert_golden2017UL.txt
scp $USER@lxplus.cern.ch:$golden16UL Cert_golden2016UL.txt
scp $USER@lxplus.cern.ch:$golden18 Cert_golden2018.txt
scp $USER@lxplus.cern.ch:$golden17 Cert_golden2017.txt
scp $USER@lxplus.cern.ch:$golden16 Cert_golden2016.txt

python generate_ledger.py