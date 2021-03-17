#ifndef _TIMBER_JME_COMMON
#define _TIMBER_JME_COMMON
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"
#include "JetMETCorrections/Modules/interface/JetResolution.h"
#include "common.h"

using str = std::string;

class JMEpaths {
    /**
     * @brief Parent class to handle shared attributes and methods
     *  among JESpaths and JERpaths.
     */
    protected:
        const str _timberPath;
        const str _jmeArchivePath;
        TempDir _tempdir;

    public:
        /**
         * @brief Construct a new JMEpaths object
         */
        JMEpaths();
        /**
         * @brief Extract jmefile from tarfile into a temporary directory
         *  and return the path to that directory.
         * 
         * @param tarfile JME tarball file path.
         * @param jmefile JME file name inside the tarball.
         * @return str Path to the temporary location of the extracted file.
         */
        str _GetPath(str tarfile, str jmefile);
        /**
         * @brief Extract jmefile from tarfile into a string which is returned.
         * 
         * @param tarfile JME tarball file path.
         * @param jmefile JME file name inside the tarball.
         * @return str Path to the temporary location of the extracted file.
         */
        str _GetTxtFileStr(str tarfile, str jmefile);
};

class JESpaths : JMEpaths {
    private:
        const str _jecTag, _jetType;
        const str _jesArchivePath;
        str GetLevelStr(str level);
        str GetPath(str level);
        str GetTxtFileStr(str level);

    public:
        /**
         * @brief Construct a new JESpaths object
         */
        JESpaths();
        /**
         * @brief Construct a new JESpaths object with the 
         *  jecTag and jetType specified.
         * @param jecTag 
         * @param jetType 
         */
        JESpaths(str jecTag, str jetType);
        /**
         * @brief Get the JetCorrectorParameters object
         * 
         * @param level JEC level. Ex. "L1"
         * @param uncertType Empty string for the total uncertainty but any uncertainty in the JEC file can be provided.
         * @return JetCorrectorParameters 
         */
        JetCorrectorParameters GetParameters(str level, str uncertType = "");
};

class JERpaths : JMEpaths {
    private:
        const str _jerTag, _jetType;
        const str _jerArchivePath;

        str GetPath(str resOrSF);
        str GetTxtFileStr(str resOrSF);

    public: 
        /**
         * @brief Construct a new JERpaths object
         */
        JERpaths();
        /**
         * @brief Construct a new JERpaths object with the 
         * JER tag and jet type specified.
         * 
         * @param jerTag 
         * @param jetType 
         */
        JERpaths(str jerTag, str jetType);
        /**
         * @brief Get the JetResolution object
         * 
         * @return JME::JetResolution 
         */
        JME::JetResolution GetResolution();
        /**
         * @brief Get the JetResolutionScaleFactor object
         * 
         * @return JME::JetResolutionScaleFactor 
         */
        JME::JetResolutionScaleFactor GetSF();
};
#endif