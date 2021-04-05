#ifndef _TIMBER_PREFIRE_WEIGHT
#define _TIMBER_PREFIRE_WEIGHT
#include "TFile.h"
#include "TH1.h"
#include <ROOT/RVec.hxx>
#include <string>
#include <algorithm>
#include <math.h>
#include "common.h"

class Prefire_weight {
    private:
        std::string _jetmapname, _photonmapname;
        TFile *_jetroot, *_photonroot;
        TH1* _jetmap, *_photonmap;
        std::pair<float,float> _jetPtRange, _jetEtaRange, _photonPtRange, _photonEtaRange;
        std::vector<std::pair<int, std::string>> _variations = {{0,"PrefireWeight"},{1,"PrefireWeight_Up"},{-1,"PrefireWeight_Down"}};
        int _variation;

    public:
        Prefire_weight(int year, bool UseEMpt=false);
        ~Prefire_weight();

        template <class Photon, class Electron>
        float EGvalue(int jetidx, std::vector<Photon> PhoColl, std::vector<Electron> EleColl) {
            float phopf = 1.0;
            float phopf_temp, elepf_temp;
            std::vector<int> PhotonInJet;
            Photon *pho;
            for (size_t pid = 0; pid < PhoColl.size(); pid++) {
                pho = &PhoColl[pid];
                if (pho->jetIdx == jetidx) {
                    if (PhotonInRange(pho->pt,pho->eta)) {
                        phopf_temp = 1 - GetPrefireProbability(_photonmap, pho->eta, pho->pt, _photonPtRange.second);
                        elepf_temp = 1.0;
                        if (pho->electronIdx > -1) {
                            Electron *matchEle = &EleColl[pho->electronIdx];
                            if (PhotonInRange(matchEle->pt,matchEle->eta)) {
                                elepf_temp = 1 - GetPrefireProbability(_photonmap,matchEle->eta,matchEle->pt,_photonPtRange.second);
                            }
                        }
                        phopf *= std::min(phopf_temp,elepf_temp);
                        PhotonInJet.push_back(pid);
                    }
                }
            }
            Electron *ele;
            for (size_t eid = 0; eid < EleColl.size(); eid++){
                ele = &EleColl[eid];
                if ((ele->jetIdx == jetidx) && (Pythonic::InList(ele->photonIdx, PhotonInJet) == -1)) {
                    if (PhotonInRange(ele->pt, ele->eta)) {
                        phopf *= 1 - GetPrefireProbability(_photonmap, ele->eta, ele->pt, _photonPtRange.second);
                    }
                }
            }
            return phopf;
        }

        float GetPrefireProbability(TH1* map, float eta, float pt, float maxpt);
        bool PhotonInRange(float pt, float eta);
        bool JetInRange(float pt, float eta);
        bool ObjInRange(float pt, float eta, std::pair<float,float> ptRange, std::pair<float,float> etaRange);

        template <class Jet, class Photon, class Electron>
        ROOT::VecOps::RVec<float> eval(std::vector<Jet> Jets, std::vector<Photon> Photons, std::vector<Electron> Electrons) {
            Jet *jet;
            float weight, jetpf, phopf;
            std::string branchname;
            ROOT::VecOps::RVec<float> out(3);
            for (size_t i = 0; i<_variations.size(); i++){
                _variation = _variations[i].first;
                branchname = _variations[i].second;
                weight = 1.0;
                for (size_t ijet = 0; ijet<Jets.size(); ijet++) {
                    jetpf = 1.0;
                    jet = &Jets[ijet];

                    if (JetInRange(jet->pt,jet->eta)) {
                        jetpf *= 1 - GetPrefireProbability(_jetmap, jet->eta, jet->pt, _jetPtRange.second);
                    }
                    phopf = EGvalue(ijet, Photons, Electrons);
                    weight *= std::min(jetpf, phopf);
                }
                weight *= EGvalue(-1, Photons, Electrons);
                out[i] = weight;
            }
            return out;
        }
};
#endif