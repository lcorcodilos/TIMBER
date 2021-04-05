#include "../include/Prefire_weight.h"

Prefire_weight::Prefire_weight(int year, bool UseEMpt) :
        _jetPtRange(20,500), _jetEtaRange(2,3), _photonPtRange(20,500), _photonEtaRange(2,3),
        _variation(0) {
    if ((year-2000 == 16) or (year == 16)) {
        if (UseEMpt) {_jetmapname = "L1prefiring_jetempt_2016BtoH";}
        else {_jetmapname = "L1prefiring_jetpt_2016BtoH";}
        _photonmapname = "L1prefiring_photonpt_2016BtoH";
    } else if ((year-2000 == 17) or (year == 17)) {
        if (UseEMpt) {_jetmapname = "L1prefiring_jetempt_2017BtoF";}
        else {_jetmapname = "L1prefiring_jetpt_2017BtoF";}
        _photonmapname = "L1prefiring_photonpt_2017BtoF";
    } else {
        throw "Prefire_weight: Year not supported. 2016 or 2017 only.";
    }
    _jetroot = hardware::Open("TIMBER/data/PrefireMaps/"+_jetmapname+".root");
    _photonroot = hardware::Open("TIMBER/data/PrefireMaps/"+_photonmapname+".root");
    _jetmap = (TH2F*)_jetroot->Get(_jetmapname.c_str());
    _photonmap = (TH2F*)_photonroot->Get(_photonmapname.c_str());
}
Prefire_weight::~Prefire_weight() {
    _jetroot->Close();
    _photonroot->Close();
}

float Prefire_weight::GetPrefireProbability(TH2F* map, float eta, float pt, float maxpt) {
    int bin = map->FindBin(eta, std::min(pt, (float)(maxpt - 0.01)));
    float pref_prob = map->GetBinContent(bin);

    float stat = map->GetBinError(bin);  // bin statistical uncertainty
    float syst = 0.2 * pref_prob;  // 20% of prefire rate

    if (_variation == 1) {
        pref_prob = std::min(pref_prob + sqrt(stat * stat + syst * syst), (float)1.0);
    } else if (_variation == -1) {
        pref_prob = std::max(pref_prob - sqrt(stat * stat + syst * syst), (float)0.0);
    }
    return pref_prob;
}

bool Prefire_weight::JetInRange(float pt, float eta) {
    return ObjInRange(pt,eta,_jetPtRange,_jetEtaRange);
}

bool Prefire_weight::PhotonInRange(float pt, float eta) {
    return ObjInRange(pt,eta,_photonPtRange,_photonEtaRange);
}

bool Prefire_weight::ObjInRange(float pt, float eta, std::pair<float,float> ptRange, std::pair<float,float> etaRange) {
    bool out = false;
    if ((pt >= ptRange.first) &&
        (abs(eta) <= etaRange.second) &&
        (abs(eta) >= etaRange.first)) {
            out = true;
    }
    return out;
}