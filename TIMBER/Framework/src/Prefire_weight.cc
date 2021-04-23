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

float Prefire_weight::EGvalue(int jetidx, RVec<float> Photon_pt, RVec<float> Photon_eta, RVec<int> Photon_jetIdx, RVec<int> Photon_electronIdx,
                          RVec<float> Electron_pt, RVec<float> Electron_eta, RVec<int> Electron_jetIdx, RVec<int> Electron_photonIdx) {
    float phopf = 1.0;
    float phopf_temp, elepf_temp;
    std::vector<int> PhotonInJet;
    for (size_t pid = 0; pid < Photon_pt.size(); pid++) {
        if (Photon_jetIdx[pid] == jetidx) {
            if (PhotonInRange(Photon_pt[pid],Photon_eta[pid])) {
                phopf_temp = 1 - GetPrefireProbability(_photonmap, Photon_eta[pid], Photon_pt[pid], _photonPtRange.second);
                elepf_temp = 1.0;
                if (Photon_electronIdx[pid] > -1) {
                    int eid = Photon_electronIdx[pid];
                    if (PhotonInRange(Electron_pt[eid],Electron_eta[eid])) {
                        elepf_temp = 1 - GetPrefireProbability(_photonmap,Electron_eta[eid],Electron_pt[eid],_photonPtRange.second);
                    }
                }
                phopf *= std::min(phopf_temp,elepf_temp);
                PhotonInJet.push_back(pid);
            }
        }
    }
    for (size_t eid = 0; eid < Electron_pt.size(); eid++){
        if ((Electron_jetIdx[eid] == jetidx) && (Pythonic::InList(Electron_photonIdx[eid], PhotonInJet) == -1)) {
            if (PhotonInRange(Electron_pt[eid], Electron_eta[eid])) {
                phopf *= 1 - GetPrefireProbability(_photonmap, Electron_eta[eid], Electron_pt[eid], _photonPtRange.second);
            }
        }
    }
    return phopf;
}

ROOT::VecOps::RVec<float> Prefire_weight::eval(RVec<float> Jet_pt, RVec<float> Jet_eta,
                               RVec<float> Photon_pt, RVec<float> Photon_eta, RVec<int> Photon_jetIdx, RVec<int> Photon_electronIdx,
                               RVec<float> Electron_pt, RVec<float> Electron_eta, RVec<int> Electron_jetIdx, RVec<int> Electron_photonIdx) {
    float weight, jetpf, phopf;
    std::string branchname;
    ROOT::VecOps::RVec<float> out(3);
    for (size_t i = 0; i<_variations.size(); i++){
        _variation = _variations[i].first;
        branchname = _variations[i].second;
        weight = 1.0;
        for (size_t ijet = 0; ijet<Jet_pt.size(); ijet++) {
            jetpf = 1.0;

            if (JetInRange(Jet_pt[ijet],Jet_eta[ijet])) {
                jetpf *= 1 - GetPrefireProbability(_jetmap, Jet_eta[ijet], Jet_pt[ijet], _jetPtRange.second);
            }
            phopf = EGvalue(ijet, Photon_pt, Photon_eta, Photon_jetIdx, Photon_electronIdx,
                                  Electron_pt, Electron_eta, Electron_jetIdx, Electron_photonIdx);
            weight *= std::min(jetpf, phopf);
        }
        weight *= EGvalue(-1, Photon_pt, Photon_eta, Photon_jetIdx, Photon_electronIdx,
                              Electron_pt, Electron_eta, Electron_jetIdx, Electron_photonIdx);
        out[i] = weight;
    }
    return out;
}