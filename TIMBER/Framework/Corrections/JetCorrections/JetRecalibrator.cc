using namespace std;

class JetRecalibrator
{
private:
    string globalTag;
    string jetFlavor;
    bool doResidualJECs;
    string jecPath;
    int upToLevel;
    bool calculateSeparateCorrections;
    bool calculateType1METCorrection;
    float type1MET_jetPtThreshold;
    float type1MET_skipEMfractionThreshold;
    bool type1MET_skipMuons;

public:
    JetRecalibrator(): 
        upToLevel(3),calculateSeparateCorrections(false),
        calculateType1METCorrection(false),
        type1MET_jetPtThreshold(15.0),type1MET_skipEMfractionThreshold(0.9),type1MET_skipMuons(true)
    {
        

    }
    ~JetRecalibrator();
    
};