#include <TFile.h>
#include <TMath.h>
#include <stdio.h>
#include <vector>
#include <iostream>
#include "ROOT/RVec.hxx"

using namespace ROOT::VecOps;
using rvec_i = ROOT::VecOps::RVec<int>;
using rvec_f = ROOT::VecOps::RVec<float>;
using rvec_c = ROOT::VecOps::RVec<char>;
using rvec_b = ROOT::VecOps::RVec<bool>;


Int_t nMuons(Int_t nMuon, rvec_b Muon_id, rvec_c Muon_pfIsoId, Int_t iso_cut, rvec_f Muon_pt, Float_t pt_cut, rvec_f Muon_eta);
//variation of the goodMuon function which was used for skimming
//returns number of muons with Muon_id==True, pt>cut and passing required isolation
Int_t nElectrons(Int_t nElectron, rvec_i Electron_cutBased, Int_t id_cut, rvec_f Electron_pt, Float_t pt_cut, rvec_f Electron_eta);
//variation of the goodElectron function which was used for skimming
//returns number of electrons with cutbased_id > id_cut and pt>cut 


Int_t nElectrons(Int_t nElectron, rvec_i Electron_cutBased, Int_t id_cut, rvec_f Electron_pt, Float_t pt_cut, rvec_f Electron_eta){
    Int_t n = 0;
    for(Int_t i=0; i<nElectron;i++){
        if(Electron_cutBased[i]>id_cut && Electron_pt[i]>pt_cut && TMath::Abs(Electron_eta[i])<2.4){
            //0:fail,1:veto,2:loose,3:medium,4:tight
            n=n+1;
        }
    }
    return n;
}


Int_t nMuons(Int_t nMuon, rvec_b Muon_id, rvec_c Muon_pfIsoId, Int_t iso_cut, rvec_f Muon_pt, Float_t pt_cut, rvec_f Muon_eta){
    Int_t n = 0;
    for(Int_t i=0; i<nMuon;i++){
        if(Muon_id[i] && int(Muon_pfIsoId[i])>iso_cut && Muon_pt[i]>pt_cut && TMath::Abs(Muon_eta[i])<2.4){
        //1=PFIsoVeryLoose, 2=PFIsoLoose, 3=PFIsoMedium, 4=PFIsoTight, 5=PFIsoVeryTight, 6=PFIsoVeryVeryTight
        //1=MiniIsoLoose, 2=MiniIsoMedium, 3=MiniIsoTight, 4=MiniIsoVeryTight)
            n=n+1;
        }
    }
    return n;
}

