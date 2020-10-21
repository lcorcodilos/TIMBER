#include "TIMBER/Framework/include/common.h"
#include "ROOT/RVec.hxx"
#include <Math/Vector4Dfwd.h>
#include <Math/GenVector/LorentzVector.h>
using namespace ROOT::VecOps;

// For ex5.py and ex6.py
// Muon pair mass for all combinations of muons with opposite sign
RVec<float> InvMassOppMuMu (RVec<float> Muon_pt, RVec<float> Muon_eta, RVec<float> Muon_phi, RVec<float> Muon_mass, RVec<float> Muon_charge) {
    int nMuon = Muon_pt.size();
    int mu0idx, mu1idx;
    ROOT::Math::PtEtaPhiMVector mu0LV;
    ROOT::Math::PtEtaPhiMVector mu1LV; 
    RVec<RVec<int>> comboIdxs = Combinations(Muon_pt,2);
    RVec<float> invMass;

    for (int i = 0; i < comboIdxs[0].size(); i++) {
        mu0idx = comboIdxs[0][i];
        mu1idx = comboIdxs[1][i];

        if (Muon_charge[mu0idx] != Muon_charge[mu1idx]) {
            mu0LV.SetCoordinates(Muon_pt[mu0idx], Muon_eta[mu0idx], Muon_phi[mu0idx], Muon_mass[mu0idx]);
            mu1LV.SetCoordinates(Muon_pt[mu1idx], Muon_eta[mu1idx], Muon_phi[mu1idx], Muon_mass[mu1idx]);
            invMass.push_back((mu0LV+mu1LV).M());
        }
    }
    
    return invMass;
}

RVec<float> CloseLepVeto () {
    
}