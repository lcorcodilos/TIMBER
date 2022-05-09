#include <TFile.h>
#include <TMath.h>
#include <stdio.h>
#include <vector>
#include <iostream>
#include "ROOT/RVec.hxx"

using namespace ROOT::VecOps;
using rvec_i = ROOT::VecOps::RVec<int>;
using rvec_f = ROOT::VecOps::RVec<float>;
using LVector = ROOT::Math::PtEtaPhiMVector;

Float_t getMTT(Int_t nGenPart, rvec_i GenPart_pdgId, rvec_f GenPart_pt, rvec_f GenPart_phi, rvec_f GenPart_eta, rvec_f GenPart_mass);
Float_t getPartIdx(Int_t nGenPart, rvec_i GenPart_pdgId, rvec_i GenPart_statusFlags, Int_t pdgId);

Float_t getPartIdx(Int_t nGenPart, rvec_i GenPart_pdgId, rvec_i GenPart_statusFlags, Int_t pdgId){
    //returns idx of the first hard process parton with GenPart_pdgId == pdgId, -1 otherwise
    // statusFlags bit 7 : isHardProcess, bit counting starts from zero!
    for(Int_t i=0;i<nGenPart;i++){
        if(GenPart_pdgId[i]==pdgId && (GenPart_statusFlags[i]&(1 << 7))){
            return i;
        }
    }
    return -1;    
}

Float_t getMTT(Int_t nGenPart, rvec_i GenPart_pdgId, rvec_f GenPart_pt, rvec_f GenPart_phi, rvec_f GenPart_eta, rvec_f GenPart_mass){
    //Finds two first genParts with pdgId 6 or -6 and calculates their inv mass
    //Assumes TTbar samples where there will be top and antitop one after the other in the particle chain
    Int_t nTops = 0;
    std::vector<LVector> topVecs;
    Float_t invMass = 0.0;

    for(Int_t i=0;i<nGenPart;i++){
        if(nTops>1){
            break;
        }
        if(GenPart_pdgId[i]==6 || GenPart_pdgId[i]==-6){
            topVecs.push_back(LVector(GenPart_pt[i],GenPart_eta[i],GenPart_phi[i],GenPart_mass[i]));
            nTops=nTops+1;
        }
    }

    if(nTops==2){
        invMass = (topVecs[0]+topVecs[1]).M();
    }

    return invMass;

}

