#include "../include/EffLoader.h"

EffLoader::EffLoader(){}

EffLoader::EffLoader(std::string filename, std::string effname) {
    file = TFile::Open(filename.c_str());
    efficiency = (TEfficiency*)file->Get(effname.c_str());
}

std::vector<float> EffLoader::eval_byglobal(int globalbin){
    effval  = efficiency->GetEfficiency(globalbin);
    effup   = effval + efficiency->GetEfficiencyErrorUp(globalbin);
    effdown = effval - efficiency->GetEfficiencyErrorLow(globalbin);
    return {effval,effup,effdown};
}

std::vector<float> EffLoader::eval_bybin(int binx, int biny, int binz){
    globalbin    = efficiency->GetGlobalBin(binx, biny, binz);
    return eval_byglobal(globalbin);
}

std::vector<float> EffLoader::eval(float xval, float yval, float zval){
    globalbin    = efficiency->FindFixBin(xval, yval, zval);
    return eval_byglobal(globalbin);
}