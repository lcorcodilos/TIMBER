#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"
#include "common.h"

using str = std::string;

class JMEpaths {
    private:
        const str _globalTag, _jetFlavour;
        const str _jmeArchivePath = "TIMBER/data/JME/";
        TempDir tempdir;

    public:
        JMEpaths(str globalTag, str jetFlavour) :
                _globalTag(globalTag), _jetFlavour(jetFlavour){

        };
        str GetLevel(str level){
            str out;
            if (level == "L1") {
                out = "_L1FastJet_";
            } else if (level == "L2") {
                out = "_L2Relative_";
            } else if (level == "L3") {
                out = "_L3Absolute_";
            } else if (level == "Res") {
                out = "_L2L3Residual_";
            } else if (level == "Uncert") {
                out = "_Uncertainty_";
            }

            return out;
        }
        str GetPath(str level) {
            str tarfile, jmefile, filestr, p;
            tarfile = _jmeArchivePath + _globalTag + ".tgz";
            jmefile = _globalTag+this->GetLevel(level)+_jetFlavour+".txt";
            filestr = ReadTarFile(tarfile, jmefile);
            p = tempdir.Write(jmefile, filestr);
            return p;
        }

        str GetTxtFileStr(str level) {
            str tarfile, jmefile, filestr, p;
            tarfile = _jmeArchivePath + _globalTag + ".tgz";
            jmefile = _globalTag+this->GetLevel(level)+_jetFlavour+".txt";
            filestr = ReadTarFile(tarfile, jmefile);
            return filestr;
        }

        JetCorrectorParameters GetParameters(str level, str uncertType = "") {
            return JetCorrectorParameters(this->GetPath(level), "");
        };
        JetCorrectionUncertainty GetUncertainty(str uncertType) {
            return JetCorrectionUncertainty(this->GetParameters("Uncert",uncertType));
        }
};