#include "../include/TopPt_weight.h"

TopPt_weight::TopPt_weight(){};

std::vector<float> TopPt_weight::matchingGenPt(
        RVec<int> GenPart_pdgId, RVec<int> GenPart_statusFlags, RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vect,
        ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1){

    float genTPt = -1.;
    float genTbarPt = -1.;

    // For all gen particles
    for (size_t i = 0; i < GenPart_pdgId.size(); i++){
        if (GenPart_statusFlags[i] & (1 << 13)) {
            if (GenPart_pdgId[i] == -6) { 
                if ((hardware::DeltaR(GenPart_vect[i],jet0) < 0.8) || (hardware::DeltaR(GenPart_vect[i],jet1) < 0.8)) {
                    genTbarPt = GenPart_vect[i].Pt();
                }
            } else if (GenPart_pdgId[i] == 6) { 
                if ((hardware::DeltaR(GenPart_vect[i],jet0) < 0.8) || (hardware::DeltaR(GenPart_vect[i],jet1) < 0.8)) {
                    genTPt = GenPart_vect[i].Pt();
                }
            }
        }
    }
    return {genTPt,genTbarPt};
}

RVec<float> TopPt_weight::eval(
        RVec<int> GenPart_pdgId, RVec<int> GenPart_statusFlags, RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vect,
        ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1, float scale){

    std::vector<float> matched = matchingGenPt(GenPart_pdgId, GenPart_statusFlags,
                                          GenPart_vect, jet0, jet1);
    float genTPt = matched[0];
    float genTbarPt = matched[1];

    float wTPt = 1.0;
    float wTPt_up = 1.0;
    float wTPt_down = 1.0;
    if (genTPt > 0){ 
        wTPt = exp(0.0615 - 0.0005*genTPt);
        wTPt_up = exp((1+scale)*0.0615 - 0.0005*genTPt);
        wTPt_down = exp((1-scale)*0.0615 - 0.0005*genTPt);
    }

    float wTbarPt = 1.0;
    float wTbarPt_up = 1.0;
    float wTbarPt_down = 1.0;
    if (genTbarPt > 0){
        wTbarPt = exp(0.0615 - 0.0005*genTbarPt);
        wTbarPt_up = exp((1+scale)*0.0615 - 0.0005*genTbarPt);
        wTbarPt_down = exp((1-scale)*0.0615 - 0.0005*genTbarPt);
    }

    return {sqrt(wTPt*wTbarPt),sqrt(wTPt_up*wTbarPt_up),sqrt(wTPt_down*wTbarPt_down)};
}