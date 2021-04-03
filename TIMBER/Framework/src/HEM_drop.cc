#include "../include/HEM_check.h"

float HEM_drop(std::string setname, RVec<float> FatJet_eta, RVec<float> FatJet_phi, int run, std::vector<int> idxToCheck) {
    bool isAffectedData = InString("data",setname) && (InString("C",setname) || InString("D",setname) || InString("B",setname));
    bool isDataB = InString("dataB",setname);
    float eventWeight = 1.0;
    if (idxToCheck.empty()) {
        idxToCheck.resize(FatJet_eta.size());
        std::iota(idxToCheck.begin(), idxToCheck.end(), 0);
    }

    for (size_t i = 0; i < idxToCheck.size(); i++) {
        int idx = idxToCheck[i];
        if ((FatJet_eta[idx] < -1.3) && (FatJet_eta[idx] > -2.5) && (FatJet_phi[idx] < -0.87) && (FatJet_phi[idx] > -1.57)){
            if (isAffectedData) {
                if (!(isDataB && run<319077)) {
                    eventWeight = 0.0; // If affected 2018B, C, or D
                    break;
                }
            } else if (!InString("data",setname)){
                eventWeight = 0.353; // If affected MC
                break;
            }
        }
        // std::cout << eventWeight << std::endl;
    }
    return eventWeight;
}