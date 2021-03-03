#ifndef _TIMBER_JME_COMMON
#define _TIMBER_JME_COMMON
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"
#include "JetMETCorrections/Modules/interface/JetResolution.h"
#include "common.h"

using str = std::string;

class JMEpaths {
    protected:
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
        const str _jesTag, _jetType;

    public:
        JESpaths(){};

        JESpaths(str jesTag, str jetType) :
                _jesTag(jesTag), _jetType(jetType){};

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
            str tarfile = _jmeArchivePath + _jesTag + ".tgz";
            str jmefile = _jesTag+this->GetLevel(level)+_jetType+".txt";
            return this->_GetPath(tarfile, jmefile);
        }

        str GetTxtFileStr(str level) {
            str tarfile = _jmeArchivePath + _jesTag + ".tgz";
            str jmefile = _jesTag+this->GetLevel(level)+_jetType+".txt";
            return this->_GetTxtFileStr(tarfile, jmefile);
        }

        JetCorrectorParameters GetParameters(str level, str uncertType = "") {
            return JetCorrectorParameters(this->GetPath(level), "");
        };
        JetCorrectionUncertainty GetUncertainty(str uncertType) {
            return JetCorrectionUncertainty(this->GetParameters("Uncert",uncertType));
        }
};

class JERpaths : JMEpaths {
    private:
        str _jerTag, _jetType;

    public: 
        JERpaths(){};

        JERpaths(str jerTag, str jetType) :
            _jerTag(jerTag), _jetType(jetType){};

        str GetPath(str resOrSF) {
            str tarfile = _jmeArchivePath + _jerTag + "_MC.tgz";
            str jmefile = _jerTag + resOrSF + _jetType + ".txt";
            return this->_GetPath(tarfile, jmefile);
        };

        str GetTxtFileStr(str resOrSF) {
            str tarfile = _jmeArchivePath + _jerTag + "_MC.tgz";
            str jmefile = _jerTag + resOrSF + _jetType + ".txt";
            return this->_GetTxtFileStr(tarfile, jmefile);
        };

        JME::JetResolution GetResPath() {
            return JME::JetResolution(GetPath("_PtResolution_"));
        }

        JME::JetResolutionScaleFactor GetSFpath() {
            return JME::JetResolutionScaleFactor(GetPath("_SF_"));
        }

};
#endif