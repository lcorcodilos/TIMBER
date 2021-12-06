# Ledger of data files and their sources

## Luminosity "golden" JSONs
| Year | Date added | File | Source |
|------|------------|------|--------|
| 2016 | Apr 19. 2021 | Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt | [Twiki](https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM#CurRec) |
| 2017 | Apr 19. 2021 | Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt | [Twiki](https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM#CurRec) |
| 2018 | Apr 19. 2021 | Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt | [Twiki](https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM#CurRec) |

## Scale Factors

| Correction | Group | Date added | File | TIMBER module(s) | Sources |
|------------|-------|------------|------|-----------------------|---------|
| DeepCSV (2016 Legacy) | BTV | Jan 9, 2020   | DeepCSV_2016LegacySF_V1.csv        | SJBtag_SF.cc | [Twiki](https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation2016Legacy) |
| DeepCSV (2017)        | BTV | Jan 9, 2020   | DeepCSV_94XSF_V4_B_F.csv           | SJBtag_SF.cc | [Twiki](https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X) |
| DeepCSV (2018)        | BTV | Jan 9, 2020   | DeepCSV_102XSF_V1.csv              | SJBtag_SF.cc | [Twiki](https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation102X) |
| Top tagging (N-subjetiness) | JME | Sept 22, 2020 | 201\*TopTaggingScaleFactors\*.root | TopTag_SF.cc | [Twiki](https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetTopTagging) [GitHub](https://github.com/cms-jet/TopTaggingScaleFactors) |
| Top and W tagging (DeepAK8) | JME | Apr 14, 2021 | DeepAK8V2_Top_W_SFs.csv | TopTagDAK8_SF.cc | [Twiki](https://twiki.cern.ch/twiki/bin/viewauth/CMS/DeepAK8Tagging2018WPsSFs) [GitHub](https://github.com/cms-jet/deepAK8ScaleFactors/blob/master/DeepAK8V2_Top_W_SFs.csv) |

## JEC/JES tarballs
| Era        | Date added   | Files                                    | Sources |
|------------|--------------|------------------------------------------|---------|
| 2016       | Mar 18, 2021 | Summer16_07Aug2017*_V11_DATA(MC).tar.gz  | https://github.com/cms-jet/JECDatabase/tree/master/tarballs |
| 2017       | Mar 18, 2021 | Fall17_17Nov2017*_V32_DATA(MC).tar.gz    | |
| 2018       | Mar 18, 2021 | Autumn18*_V19_DATA(MC).tar.gz            | |
| 2016UL     | Nov 10, 2021 | Summer19UL16*_V7_DATA(MC).tar.gz         | |
| 2016UL APV | Nov 10, 2021 | Summer19UL16APV*_V7_DATA(MC).tar.gz      | |
| 2017UL     | Mar 18, 2021 | Summer19UL17*_V5_DATA(MC).tar.gz         | |
| 2018UL     | Mar 18, 2021 | Summer19UL18*_V5_DATA(MC).tar.gz         | |

## JER tarballs and files
| Era        | Date added   | Files                             | Sources |
|------------|--------------|-----------------------------------|---------|
| 2016       | Mar 18, 2021 | Summer16_25nsV1b_DATA(MC).tar.gz  | https://github.com/cms-jet/JRDatabase/tree/master/tarballs |
| 2017       | Mar 18, 2021 | Fall17_V3b_DATA(MC).tar.gz        | |
| 2018       | Mar 18, 2021 | Autumn18_V7b_DATA(MC).tar.gz      | |
| 2016UL     | Nov 10, 2021 | Summer20UL16_JRV3_DATA(MC).tar.gz | |
| 2016UL APV | Nov 10, 2021 | Summer20UL16APV_JRV3_DATA(MC).tar.gz | |
| 2017UL     | Mar 18, 2021 | Summer19UL17_JRV2_DATA(MC).tar.gz | |
| 2018UL     | Mar 18, 2021 | Summer19UL18_JRV2_DATA(MC).tar.gz | |
| All        | Mar 18, 2021 | puppiSoftdropResol.root           | https://github.com/cms-jet/PuppiSoftdropMassCorrections/tree/80X/weights |

## Prefire Maps
| Era    | Date added   | Files                             | Sources |
|--------|--------------|-----------------------------------|---------|
| 2016   | Apr 5, 2021  | L1prefiring_*pt_2016BtoH.root     | https://github.com/cms-nanoAOD/nanoAOD-tools/tree/master/data/prefire_maps |
| 2017   | Apr 5, 2021  | L1prefiring_*pt_2017BtoF.root     | |

## PDF sets
File pdfsets.index downloaded from [https://lhapdfsets.web.cern.ch/current/pdfsets.index](https://lhapdfsets.web.cern.ch/current/pdfsets.index) on Oct. 19, 2020.

## Pileup files
The derivation of the files in the `TIMBER/data/Pileup/` directory can be found in `TIMBER/data/Pileup/generate_files.sh`. The procedure follows the instructions outlined in [this](https://twiki.cern.ch/twiki/bin/view/CMS/PileupJSONFileforData#Recommended_cross_section) TWiki with .txt file locations from [this](https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM#PileupInformation) TWiki.

*(Last updated Nov 11, 2021)*