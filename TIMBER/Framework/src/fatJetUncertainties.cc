#include "TIMBER/Framework/include/jetSmearer.h"
#include "TIMBER/Framework/include/jetRecalib.h"
#include "TIMBER/Framework/include/common.h"
#include <string>

class fatJetUncertainties
{
private:
    const std::string era_;
    const std::string globalTag_;
    const std::vector<std::string>jesUncertainties_;
    const std::string archive_;
    const std::string jetType_;
    const bool noGroom_;
    const std::string jerTag_;
    const std::vector<float> jmrVals_, jmsVals_;
    const bool isData_;

    bool applySmearing_, applyHEMfix_, splitJER_;
    std::string jerInputFileName_, jerUncertaintyInputFileName_;
    std::vector<std::string> splitJERIDs_ = {""};
    JetSmearer jetSmearer_;

public:
    fatJetUncertainties(std::string year,
            std::string globalTag,
            std::vector<std::string>jesUncertainties = {"Total"},
            std::string archive = "",
            std::string jetType = "AK8PFPuppi",
            bool noGroom = false,
            std::string jerTag,
            std::vector<float> jmrVals = {},
            std::vector<float> jmsVals = {},
            bool isData = false,
            bool applySmearing = true,
            bool applyHEMfix = false,
            bool splitJER = false);
    ~fatJetUncertainties();
};

fatJetUncertainties::fatJetUncertainties(std::string era,
            std::string globalTag,
            std::vector<std::string>jesUncertainties = {"Total"},
            std::string archive, std::string jetType,
            bool noGroom, std::string jerTag,
            std::vector<float> jmrVals,
            std::vector<float> jmsVals,
            bool isData, bool applySmearing,
            bool applyHEMfix, bool splitJER) :
            era_(era), globalTag_(globalTag),
            jesUncertainties_(jesUncertainties),
            archive_(archive), jetType_(jetType),
            noGroom_(noGroom), jerTag_(jerTag),
            jmrVals_(jmrVals), jmsVals_(jmsVals),
            isData_(isData), applySmearing_(applySmearing),
            applyHEMfix_(applyHEMfix), splitJER_(splitJER),
            jerInputFileName_(jerTag + "_PtResolution_" + jetType + ".txt"),
            jerUncertaintyInputFileName_(jerTag + "_SF_" + jetType + ".txt")
{
    if (isData_) {applySmearing_ = false;} // don't smear for data

    // JER, JMR
    jetSmearer_ = jetSmearer(globalTag_, jetType_, jerInputFileName_,
                             jerUncertaintyInputFileName_, jmrVals_)


}

fatJetUncertainties::~fatJetUncertainties()
{
}
