// Requires CMSSW
#include <string>
#include <vector>
#include <cstdlib>
#include <TFile.h>
#include <TString.h>
#include "../include/Pythonic.h"
#include <map>



//Class to handle JMS uncertainty shift
class JMSUncShifter {
    public:

        JMSUncShifter();
        ~JMSUncShifter(){};
        float shiftMsd(float mSD,std::string year,int shift);//shift 0,1,2: nominal,down,up

        std::map<std::string, std::array<float, 3>> jmsTable;
};


