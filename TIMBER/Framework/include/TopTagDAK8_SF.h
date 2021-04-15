#ifndef _TIMBER_TOPTAGDAK8_SF
#define _TIMBER_TOPTAGDAK8_SF
#include <vector>
#include <map>
#include <string>
#include <fstream>
#include <iostream>
#include <cstdlib>
#include <sstream>

class TopTagDAK8_SF {

    private:
        std::map<std::pair<int,int>, std::vector<float> > _values;
        std::string _p = std::string(std::getenv("TIMBERPATH"))+"TIMBER/data/OfficialSFs/DeepAK8V2_Top_W_SFs.csv";

    public:
        TopTagDAK8_SF(int year, std::string workingpoint, bool massDecorr);
        ~TopTagDAK8_SF(){};
        std::vector<float> eval(float pt);
};

#endif