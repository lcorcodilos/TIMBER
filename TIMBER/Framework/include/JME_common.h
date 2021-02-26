#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"
#include "JetMETCorrections/Modules/interface/JetResolution.h"
#include "common.h"

using str = std::string;

class JMEpaths {
    private:
        const std::string _timberPath = std::string(std::getenv("TIMBERPATH"));
        const str _jmeArchivePath = _timberPath + "TIMBER/data/JME/";
        TempDir tempdir;

    public:
        JMEpaths(){};
        
        str _GetPath(str tarfile, str jmefile) {
            str filestr = ReadTarFile(tarfile, jmefile);
            str p = tempdir.Write(jmefile, filestr);
            return p;
        }

        str _GetTxtFileStr(str tarfile, str jmefile) {
            str filestr = ReadTarFile(tarfile, jmefile);
            return filestr;
        }
};

class JESpaths : JMEpaths {
    private:
        const str _globalTag, _jetFlavour;

    public:
        JESpaths(str globalTag, str jetFlavour) :
                _globalTag(globalTag), _jetFlavour(jetFlavour){};

        str GetLevel(str level){
            str out;
            if (level == "L1") {out = "_L1FastJet_";}
            else if (level == "L2") {out = "_L2Relative_";}
            else if (level == "L3") {out = "_L3Absolute_";}
            else if (level == "Res") {out = "_L2L3Residual_";}
            else if (level == "Uncert") {out = "_Uncertainty_";}
            return out;
        }

        str GetPath(str level) {
            str tarfile = _jmeArchivePath + _globalTag + ".tgz";
            str jmefile = _globalTag+this->GetLevel(level)+_jetFlavour+".txt";
            return this->_GetPath(tarfile, jmefile);
        }

        str GetTxtFileStr(str level) {
            str tarfile = _jmeArchivePath + _globalTag + ".tgz";
            str jmefile = _globalTag+this->GetLevel(level)+_jetFlavour+".txt";
            return this->_GetTxtFileStr(tarfile, jmefile);
        }

        JetCorrectorParameters GetParametersJES(str level, str uncertType = "") {
            return JetCorrectorParameters(this->GetPath(level), "");
        };
        JetCorrectionUncertainty GetUncertaintyJES(str uncertType) {
            return JetCorrectionUncertainty(this->GetParameters("Uncert",uncertType));
        }
}

class JERpaths : JMEpaths {
    private:
        str _jerTag;

    public: 
        JERpaths(str jetFlavour, str jertag) : _jetFlavour(jetFlavour), _jerTag(jerTag){};

        str GetPath(str resOrSF) {
            str tarfile = _jmeArchivePath + _jerTag + "_MC.tgz";
            str jmefile = _jerTag + resOrSF + _jetFlavour + ".txt";
            return this->_GetPath(tarfile, jmefile);
        };

        str GetTxtFileStr(str resOrSF) {
            str tarfile = _jmeArchivePath + _jerTag + "_MC.tgz";
            str jmefile = _jerTag + resOrSF + _jetFlavour + ".txt";
            return this->_GetTxtFileStr(tarfile, jmefile);
        };

        JME::JetResolution GetResPath() {
            JetResolution(GetPath("_PtResolution_"));
        }

        JME::JetResolutionScaleFactor GetSFpath() {
            JetResolutionScaleFactor(GetPath("_SF_"));
        }

}