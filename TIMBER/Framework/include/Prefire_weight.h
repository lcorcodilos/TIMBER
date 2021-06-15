#ifndef _TIMBER_PREFIRE_WEIGHT
#define _TIMBER_PREFIRE_WEIGHT
#include "TFile.h"
#include "TH2F.h"
#include <ROOT/RVec.hxx>
#include <string>
#include <algorithm>
#include <math.h>
#include "common.h"

/**
 * @brief C++ class to handle the trigger prefire weighting.
 * Based off of the equivalent NanoAOD-tools module.
 */
class Prefire_weight {
    private:
        std::string _jetmapname, _photonmapname;
        TFile *_jetroot, *_photonroot;
        TH2F *_jetmap, *_photonmap;
        std::pair<float,float> _jetPtRange, _jetEtaRange, _photonPtRange, _photonEtaRange;
        std::vector<std::pair<int, std::string>> _variations = {{0,"PrefireWeight"},{1,"PrefireWeight_Up"},{-1,"PrefireWeight_Down"}};
        int _variation;

        float EGvalue(int jetidx, RVec<float> Photon_pt, RVec<float> Photon_eta, RVec<int> Photon_jetIdx, RVec<int> Photon_electronIdx,
                                  RVec<float> Electron_pt, RVec<float> Electron_eta, RVec<int> Electron_jetIdx, RVec<int> Electron_photonIdx);

        float GetPrefireProbability(TH2F* map, float eta, float pt, float maxpt);
        bool PhotonInRange(float pt, float eta);
        bool JetInRange(float pt, float eta);
        bool ObjInRange(float pt, float eta, std::pair<float,float> ptRange, std::pair<float,float> etaRange);

    public:
        /**
         * @brief Construct a new Prefire_weight object
         * 
         * @param year 
         * @param UseEMpt 
         */
        Prefire_weight(int year, bool UseEMpt=false);
        ~Prefire_weight();
        /**
         * @brief Calculate the value of the weight.
         * 
         * @param Jet_pt 
         * @param Jet_eta 
         * @param Photon_pt 
         * @param Photon_eta 
         * @param Photon_jetIdx 
         * @param Photon_electronIdx 
         * @param Electron_pt 
         * @param Electron_eta 
         * @param Electron_jetIdx 
         * @param Electron_photonIdx 
         * @return ROOT::VecOps::RVec<float> 
         */
        ROOT::VecOps::RVec<float> eval(RVec<float> Jet_pt, RVec<float> Jet_eta,
                                       RVec<float> Photon_pt, RVec<float> Photon_eta, RVec<int> Photon_jetIdx, RVec<int> Photon_electronIdx,
                                       RVec<float> Electron_pt, RVec<float> Electron_eta, RVec<int> Electron_jetIdx, RVec<int> Electron_photonIdx);
};
#endif