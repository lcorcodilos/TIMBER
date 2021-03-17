#include "../include/JME_common.h"
#include <iostream>
#include <fstream>

JMEpaths::JMEpaths() :
    _timberPath(std::string(std::getenv("TIMBERPATH"))),
    _jmeArchivePath(_timberPath+"TIMBER/data/"), _tempdir(){
    };
        
str JMEpaths::_GetPath(str tarfile, str jmefile) {
    str filestr = ReadTarFile(tarfile, jmefile);
    return _tempdir.Write(jmefile, filestr);
}

str JMEpaths::_GetTxtFileStr(str tarfile, str jmefile) {
    return ReadTarFile(tarfile, jmefile);
}
//--------------------
JESpaths::JESpaths() : 
    _jesArchivePath(_jmeArchivePath+"JES/"){};

JESpaths::JESpaths(str jecTag, str jetType) :
                _jecTag(jecTag), _jetType(jetType),
                _jesArchivePath(_jmeArchivePath+"JES/"){};

str JESpaths::GetLevelStr(str level){
    str out = "_";
    if (level == "L1") {out = "_L1FastJet_";}
    else if (level == "L2") {out = "_L2Relative_";}
    else if (level == "L3") {out = "_L3Absolute_";}
    else if (level == "Res") {out = "_L2L3Residual_";}
    else if (level == "Uncert") {out = "_Uncertainty_";}
    return out;
}

str JESpaths::GetPath(str level) {
    str tarfile = _jesArchivePath + _jecTag + ".tar.gz";
    str jmefile = _jecTag+this->GetLevelStr(level)+_jetType+".txt";
    return this->_GetPath(tarfile, jmefile);
}

str JESpaths::GetTxtFileStr(str level) {
    str tarfile = _jesArchivePath + _jecTag + ".tar.gz";
    str jmefile = _jecTag+this->GetLevelStr(level)+_jetType+".txt";
    return this->_GetTxtFileStr(tarfile, jmefile);
}

JetCorrectorParameters JESpaths::GetParameters(str level, str uncertType) {
    return JetCorrectorParameters(this->GetPath(level), uncertType);
}
//---------------------
JERpaths::JERpaths() : 
    _jerArchivePath(_jmeArchivePath+"JER/"){};

JERpaths::JERpaths(str jerTag, str jetType) :
    _jerTag(jerTag), _jetType(jetType),
    _jerArchivePath(_jmeArchivePath+"JER/"){};

str JERpaths::GetPath(str resOrSF) {
    str tarfile = _jerArchivePath + _jerTag + ".tar.gz";
    str jmefile = _jerTag + resOrSF + _jetType + ".txt";
    return this->_GetPath(tarfile, jmefile);
};

str JERpaths::GetTxtFileStr(str resOrSF) {
    str tarfile = _jerArchivePath + _jerTag + ".tar.gz";
    str jmefile = _jerTag + resOrSF + _jetType + ".txt";
    return this->_GetTxtFileStr(tarfile, jmefile);
};

JME::JetResolution JERpaths::GetResolution() {
    return JME::JetResolution(this->GetPath("_PtResolution_"));
}

JME::JetResolutionScaleFactor JERpaths::GetSF() {
    return JME::JetResolutionScaleFactor(this->GetPath("_SF_"));
}