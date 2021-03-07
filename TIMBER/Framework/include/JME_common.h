#ifndef _TIMBER_JME_COMMON
#define _TIMBER_JME_COMMON
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"
#include "JetMETCorrections/Modules/interface/JetResolution.h"
#include "common.h"

using str = std::string;

class JMEpaths {
    protected:
        const str _timberPath;
        const str _jmeArchivePath;
        TempDir _tempdir;

    public:
        JMEpaths();
        
        str _GetPath(str tarfile, str jmefile);
        str _GetTxtFileStr(str tarfile, str jmefile);
};

class JESpaths : JMEpaths {
    private:
        const str _jesTag, _jetType;
        const str _jesArchivePath;

    public:
        JESpaths();
        JESpaths(str jesTag, str jetType);

        str GetLevel(str level);
        str GetPath(str level);
        str GetTxtFileStr(str level);

        JetCorrectorParameters GetParameters(str level, str uncertType = "");
};

class JERpaths : JMEpaths {
    private:
        const str _jerTag, _jetType;
        const str _jerArchivePath;

    public: 
        JERpaths();
        JERpaths(str jerTag, str jetType);

        str GetPath(str resOrSF);
        str GetTxtFileStr(str resOrSF);

        JME::JetResolution GetResPath();
        JME::JetResolutionScaleFactor GetSFpath();
};
#endif