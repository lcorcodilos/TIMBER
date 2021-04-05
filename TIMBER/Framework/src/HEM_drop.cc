#include "../include/HEM_drop.h"

HEM_drop::HEM_drop(std::string setname, std::vector<int> idxToCheck) :
    _isAffectedData(InString("data",setname) && (InString("C",setname) || InString("D",setname) || InString("B",setname))),
    _isDataB(InString("dataB",setname)), _idxToCheck(idxToCheck), _setname(setname)
{};

std::vector<float> HEM_drop::eval(RVec<float> FatJet_eta, RVec<float> FatJet_phi, int run) {
    float eventWeight = 1.0;
    if (_idxToCheck.empty()) {
        _idxToCheck.resize(FatJet_eta.size());
        std::iota(_idxToCheck.begin(), _idxToCheck.end(), 0);
    }
    for (size_t i = 0; i < _idxToCheck.size(); i++) {
        int idx = _idxToCheck[i];
        if ((FatJet_eta[idx] < -1.3) && (FatJet_eta[idx] > -2.5) && (FatJet_phi[idx] < -0.87) && (FatJet_phi[idx] > -1.57)){
            if (_isAffectedData) {
                if (!(_isDataB && run<319077)) {
                    eventWeight = 0.0; // If affected 2018B, C, or D
                    break;
                }
            } else if (!InString("data",_setname)){
                eventWeight = 0.353; // If affected MC
                break;
            }
        }
        // std::cout << eventWeight << std::endl;
    }
    return {eventWeight};

}