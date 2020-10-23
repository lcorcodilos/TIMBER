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

// (Lepton_pt > 10) && (analyzer::DeltaR(Lepton_eta, Jet_eta, Lepton_phi, Jet_phi) < 0.4)
RVec<float> CloseLepVeto (RVec<float> Lepton_pt, RVec<float> Lepton_eta, RVec<float> Lepton_phi, RVec<float> Jet_eta, RVec<float> Jet_phi) {
    RVec<bool> jet_bool_vect;
    bool bool_pt, bool_deltaR, found_lep;
    for (int ijet = 0; ijet < Jet_eta.size(); ijet++) {
        found_lep = false;
        for (int ilep = 0; ilep < Lepton_pt.size(); ilep++) {
            bool_pt = Lepton_pt[ilep] > 10;
            bool_deltaR = DeltaR(Lepton_eta[ilep], Jet_eta[ijet], Lepton_phi[ilep], Jet_phi[ijet]) < 0.4;
            if (bool_pt && bool_deltaR){
                found_lep = true;
            }
        }
        jet_bool_vect.push_back(found_lep);
    }
    return jet_bool_vect;
}

int NonZlep(RVec<ROOT::Math::PtEtaPhiMVector> Lepton_vect, RVec<int> Lepton_pdgId, RVec<int> Lepton_charge) {
    RVec<RVec<int>> combos = Combinations(Lepton_vect,3); // build combinations where first two are the Z
    int NonZlep_idx = -1;
    float deltaMZ = 1000.; // start at large value for comparison
    float dMZ;
    bool sameFlavOppSign;
    for (int i = 0; i < combos[0].size(); i++) { // loop over combinations
        dMZ = abs(91.2-(Lepton_vect[combos[0][i]]+Lepton_vect[combos[1][i]]).M());
        sameFlavOppSign = (Lepton_pdgId[combos[0][i]] == -1*Lepton_pdgId[combos[1][i]]);
        if ((dMZ < deltaMZ) && sameFlavOppSign) {
            deltaMZ = dMZ;
            NonZlep_idx = combos[2][i];
        }
    }
    return NonZlep_idx;
}