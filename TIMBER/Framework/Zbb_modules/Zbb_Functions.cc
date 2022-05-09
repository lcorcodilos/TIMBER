#include <TFile.h>
#include <TMath.h>
#include <stdio.h>
#include <vector>
#include <iostream>
#include "ROOT/RVec.hxx"
#include "../include/common.h"

using namespace ROOT::VecOps;
using namespace ROOT::VecOps;
using rvec_i  = ROOT::VecOps::RVec<int>;
using rvec_f  = ROOT::VecOps::RVec<float>;
using LVector = ROOT::Math::PtEtaPhiMVector;


Int_t VinJet(Float_t FatJet_phi, Float_t FatJet_eta,Int_t nGenPart, rvec_f GenPart_phi,rvec_f GenPart_eta, rvec_i GenPart_pdgId,rvec_i GenPart_statusFlags )
//returns 1 if W/Z within jet cone, 0 otherwise
{
    Int_t pid;
    for(Int_t i=0; i<nGenPart;i++){
        if (!(GenPart_statusFlags[i]&(1 << 7))){
            //If not hard process particle, continue
            continue;
        }
        pid = GenPart_pdgId[i];
        if((TMath::Abs(pid)==24 || pid==23) && hardware::DeltaR(LVector(1.,GenPart_eta[i],GenPart_phi[i],0.),LVector(1.,FatJet_eta,FatJet_phi,0.))<0.8){
            return 1;
        }
    }
    return 0;
}

Int_t qqInJet(Float_t FatJet_phi, Float_t FatJet_eta,Int_t nGenPart, rvec_f GenPart_phi,rvec_f GenPart_eta, rvec_i GenPart_pdgId, rvec_i GenPart_genPartIdxMother, rvec_i GenPart_statusFlags, Int_t qPid)
//checks if qqbar from Z hard process are within jet cone (1 if yes, 0 if no)
{
    Int_t qIdx = -1;
    Int_t qbarIdx = -1;
    Int_t pid, motherID;
    for(Int_t i=0; i<nGenPart;i++){
        if(qIdx!=-1 && qbarIdx!=-1){
            //If we found b and bbar, return 1
            return 1;
        }
        if (!(GenPart_statusFlags[i]&(1 << 7))){
            //If not hard process particle, continue
            continue;
        }

        pid         = GenPart_pdgId[i];
        motherID    = GenPart_pdgId[GenPart_genPartIdxMother[i]];

        if(pid==qPid && motherID==23 && hardware::DeltaR(LVector(1.,GenPart_eta[i],GenPart_phi[i],0.),LVector(1.,FatJet_eta,FatJet_phi,0.))<0.8){
            qIdx = i;
        }
        if(pid==-qPid && motherID==23 && hardware::DeltaR(LVector(1.,GenPart_eta[i],GenPart_phi[i],0.),LVector(1.,FatJet_eta,FatJet_phi,0.))<0.8){
            qbarIdx = i;
        }
    }
    return 0;
}

Int_t qInJet(Float_t FatJet_phi, Float_t FatJet_eta,Int_t nGenPart, rvec_f GenPart_phi,rvec_f GenPart_eta, rvec_i GenPart_pdgId, rvec_i GenPart_genPartIdxMother, rvec_i GenPart_statusFlags, Int_t qPid)
//checks if q or qbar from W+/- hard process are within jet cone (1 if yes, 0 if no)
{
    Int_t qIdx = -1;
    Int_t pid, motherID;
    for(Int_t i=0; i<nGenPart;i++){
        if(qIdx!=-1){
            //If we found b and bbar, return 1
            return 1;
        }
        if (!(GenPart_statusFlags[i]&(1 << 7))){
            //If not hard process particle, continue
            continue;
        }

        pid         = GenPart_pdgId[i];
        motherID    = GenPart_pdgId[GenPart_genPartIdxMother[i]];

        if(TMath::Abs(pid)==qPid && TMath::Abs(motherID)==24 && hardware::DeltaR(LVector(1.,GenPart_eta[i],GenPart_phi[i],0.),LVector(1.,FatJet_eta,FatJet_phi,0.))<0.8){
            qIdx = i;
        }
    }
    return 0;
}



Int_t classifyZJet(Float_t FatJet_phi, Float_t FatJet_eta,Int_t nGenPart, rvec_f GenPart_phi,rvec_f GenPart_eta, rvec_i GenPart_pdgId, rvec_i GenPart_genPartIdxMother, rvec_i GenPart_statusFlags )
//check if both Z and its both qq products in jet
//returns 3 if Z+bbbar found in jet, 2 if Z+ccbar, 1 if Z+uds pairs, 0 otherwise
{
    Int_t bbFlag, ccFlag, ssFlag, uuFlag, ddFlag, Vflag;

    Vflag  = VinJet(FatJet_phi, FatJet_eta,nGenPart,GenPart_phi,GenPart_eta,GenPart_pdgId,GenPart_statusFlags);
    if(Vflag==0){
        return 0;//unmatched if V is not in jet
    }

    bbFlag = qqInJet(FatJet_phi,FatJet_eta,nGenPart,GenPart_phi,GenPart_eta,GenPart_pdgId,GenPart_genPartIdxMother,GenPart_statusFlags,5);
    ccFlag = qqInJet(FatJet_phi,FatJet_eta,nGenPart,GenPart_phi,GenPart_eta,GenPart_pdgId,GenPart_genPartIdxMother,GenPart_statusFlags,4);
    ssFlag = qqInJet(FatJet_phi,FatJet_eta,nGenPart,GenPart_phi,GenPart_eta,GenPart_pdgId,GenPart_genPartIdxMother,GenPart_statusFlags,3);
    uuFlag = qqInJet(FatJet_phi,FatJet_eta,nGenPart,GenPart_phi,GenPart_eta,GenPart_pdgId,GenPart_genPartIdxMother,GenPart_statusFlags,2);
    ddFlag = qqInJet(FatJet_phi,FatJet_eta,nGenPart,GenPart_phi,GenPart_eta,GenPart_pdgId,GenPart_genPartIdxMother,GenPart_statusFlags,1);

    if(bbFlag==1){
        return 3;
    }
    if(ccFlag==1){
        return 2;
    }
    if(uuFlag==1 || ddFlag==1 || ssFlag==1){
        return 1;
    }

    //if V matched, but qq are not
    return 0;

}


Int_t classifyWJet(Float_t FatJet_phi, Float_t FatJet_eta,Int_t nGenPart, rvec_f GenPart_phi,rvec_f GenPart_eta, rvec_i GenPart_pdgId, rvec_i GenPart_genPartIdxMother, rvec_i GenPart_statusFlags )
//check if both W and its both q product in jet
//returns 2 if W+cs found in jet, 1 if Z+ud, 0 otherwise
{
    Int_t cFlag, uFlag, sFlag, dFlag, Vflag;

    Vflag  = VinJet(FatJet_phi,FatJet_eta,nGenPart,GenPart_phi,GenPart_eta,GenPart_pdgId,GenPart_statusFlags);
    if(Vflag==0){
        return 0;//unmatched if V is not in jet
    }

    cFlag = qInJet(FatJet_phi,FatJet_eta,nGenPart,GenPart_phi,GenPart_eta,GenPart_pdgId,GenPart_genPartIdxMother,GenPart_statusFlags,4);
    sFlag = qInJet(FatJet_phi,FatJet_eta,nGenPart,GenPart_phi,GenPart_eta,GenPart_pdgId,GenPart_genPartIdxMother,GenPart_statusFlags,3);
    uFlag = qInJet(FatJet_phi,FatJet_eta,nGenPart,GenPart_phi,GenPart_eta,GenPart_pdgId,GenPart_genPartIdxMother,GenPart_statusFlags,2);
    dFlag = qInJet(FatJet_phi,FatJet_eta,nGenPart,GenPart_phi,GenPart_eta,GenPart_pdgId,GenPart_genPartIdxMother,GenPart_statusFlags,1);
    if(cFlag==1 && sFlag==1){
        return 2;
    }
    if(uFlag==1 && dFlag==1){
        return 1;
    }
    return 0;
}

Int_t genVpt(Int_t nGenPart,rvec_i GenPart_pdgId,rvec_f GenPart_pt,rvec_i GenPart_statusFlags)
//returns gen pt of the first gen W or Z from hard process
//-1 otherwise
{
    Float_t pt = -1.;
    Int_t pid;
    for(Int_t i=0; i<nGenPart;i++){
        if (!(GenPart_statusFlags[i]&(1 << 7))){
            //If not hard process particle, continue
            continue;
        }
        pid = GenPart_pdgId[i];
        if(TMath::Abs(pid)==24 || pid==23){//W or Z
            pt = GenPart_pt[i];
            return pt;
        }
    }
    return pt;
}


Int_t nPartHardProcess(Int_t nGenPart,rvec_i GenPart_pdgId,rvec_i GenPart_statusFlags )
//number of hard process partons (PID<=5)
{
    Int_t n = 0;
    Int_t pid;
    for(Int_t i=0; i<nGenPart;i++){
        if (!(GenPart_statusFlags[i]&(1 << 7))){
            //If not hard process particle, continue
            continue;
        }

        pid = GenPart_pdgId[i];

        if(TMath::Abs(pid)<6){
            n = n+1;
        }

    }
    return n;
}


Int_t nLHEPartOutgoing(Int_t nLHEPart,rvec_i LHEPart_pdgId,rvec_i LHEPart_status )
//number of outgoing LHE partons
{
    Int_t n = 0;
    Int_t pid;
    for(Int_t i=0; i<nLHEPart;i++){
        pid = LHEPart_pdgId[i];
        if(TMath::Abs(pid)<6 && LHEPart_status[i]==1){
            n = n+1;
        }

    }
    return n;
}


Int_t topVeto(Float_t FatJet_eta, Float_t FatJet_phi, Int_t nJet, rvec_f Jet_eta, Float_t eta_cut, rvec_f Jet_phi, rvec_f Jet_pt, rvec_f Jet_bTag, Float_t bTagCut){
    //Loop over AK4 jets, find if any wit DR>0.8 from FatJet satisfying pt>30, |eta|<eta_cut and b-tagged
    //1 if yes, 0 if no
    Int_t kinematicFlag;
    Int_t btagFlag;
    Int_t DRflag;
    for(Int_t i=0; i<nJet;i++){
            DRflag = hardware::DeltaR(LVector(1.,FatJet_eta,FatJet_phi,0.),LVector(1.,Jet_eta[i],Jet_phi[i],0.))>0.8;
            kinematicFlag  = TMath::Abs(Jet_eta[i])<eta_cut && Jet_pt[i]>30;
            btagFlag       = Jet_bTag[i]>bTagCut;
            if(kinematicFlag && DRflag && btagFlag){
               return 1;
            }
    }
    return 0;
}


Int_t VmatchedFatJetIdx(Int_t nFatJet, rvec_f FatJet_phi, rvec_f FatJet_eta,Int_t nGenPart,rvec_f GenPart_phi,rvec_f GenPart_eta,rvec_i GenPart_pdgId, rvec_i GenPart_statusFlags)
{

    Int_t vFlag;
    for(Int_t i=0; i<nFatJet;i++){
        vFlag = VinJet(FatJet_phi[i],FatJet_eta[i],nGenPart,GenPart_phi,GenPart_eta,GenPart_pdgId,GenPart_statusFlags);
        if(vFlag==1){
            return i;
        }

    }
    return -1;
}