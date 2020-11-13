#ifndef COMMON_H
#define COMMON_H
#include "TIMBER/Framework/include/common.h"
#endif

#include <cmath>
#include <stdbool.h>
#include <ctime> 
#include <vector>
#include <stdio.h>

using namespace ROOT::VecOps;

/** @class
 *  @brief Handles the top \f$p_T\f$ reweighting value for \f$t\bar{t}\f$ simulation
 * based on doing gen particle matching. The weight is calculated as 
 * \f$ \sqrt{e^{\alpha - \beta*p_{T}^{Gen t}} * e^{\alpha - \beta*p_{T}^{Gen \bar{t}}}} \f$.
 * where \f$\alpha = 0.0615f$ and \f$\beta = 0.0005\f$. See the alpha() and beta() functions
 * to calculate the weights with these parameters varied.
 * 
 * WARNING: You MUST run corr() before alpha() and beta() since these functions
 * recycle information derived from corr().
 * 
 */
class TopPt_weight {
    private:
        // float genTPt; //!< Generator top \f$p_T\f$ 
        // float genTbarPt; //!< Generator anti-top \f$p_T\f$ 
        std::vector<float> matchingGenPt(RVec<int> GenPart_pdgId, RVec<int> GenPart_statusFlags, RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vects,
                ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1);

    public:
        TopPt_weight(){};
        ~TopPt_weight(){};
        /**
         * @brief Calculate the top \f$p_T\f$ reweighting value for \f$t\bar{t}\f$ simulation
         * based on doing gen particle matching. The weight is calculated as 
         * \f$ \sqrt{e^{\alpha - \beta*p_{T}^{Gen t}} * e^{\alpha - \beta*p_{T}^{Gen \bar{t}}}} \f$.
         * where \f$\alpha = 0.0615f$ and \f$\beta = 0.0005\f$. See the alpha() and beta() functions
         * to calculate the weights with these parameters varied.
         * 
         * @param GenPart_pdgId NanoAOD branch
         * @param GenPart_statusFlags NanoAOD branch
         * @param GenPart_vects Vector of ROOT::Math::PtEtaPhiMVectors (create through hardware::TLvector)
         * @param jet0 
         * @param jet1 
         * @return RVec<float> Will only be length 1. Stored as vector to satisfy TIMBER Correction() requirements
         */
        RVec<float> corr(RVec<int> GenPart_pdgId, RVec<int> GenPart_statusFlags, RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vects,
                ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1);
        /**
         * @brief MUST RUN corr() FIRST.
         * Calculate variations of top \f$\p_T\f$ weight by varying the \f$\alpha\f$ parameter.
         * The amount of variation can be changed via the scale arguement which is a 
         * percent change on \f$\alpha\f$. The output is the weight calculated with the variation
         * divided by the nominal value. When using MakeWeightCols(), the nominal will be multiplied
         * by this variation to recover the total weight.
         * 
         * @param scale Percent variation on \f$\alpha\f$ parameter.
         * @return RVec<float> {up, down} variations of the top \f$p_T\f$ reweighting value divided by the nominal weight.
         */
        RVec<float> alpha(
                RVec<int> GenPart_pdgId, RVec<int> GenPart_statusFlags, RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vects,
                ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1, float scale = 0.5);
        /**
         * @brief Calculate variations of the top \f$\p_T\f$ weight by varying the \f$\beta\f$ parameter.
         * The amount of variation can be changed via the scale arguement which is a 
         * percent change on \f$\beta\f$. The output is the weight calculated with the variation
         * divided by the nominal value. When using MakeWeightCols(), the nominal will be multiplied
         * by this variation to recover the total weight.
         * 
         * @param scale Percent variation on \f$\beta\f$ parameter.
         * @return RVec<float> {up, down} variations of the top \f$p_T\f$ reweighting value divided by the nominal weight.
         */
        RVec<float> beta(
                RVec<int> GenPart_pdgId, RVec<int> GenPart_statusFlags, RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vects,
                ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1, float scale = 0.5);
};

std::vector<float> TopPt_weight::matchingGenPt(
        RVec<int> GenPart_pdgId, RVec<int> GenPart_statusFlags, RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vects,
        ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1){

    float genTPt = -1.;
    float genTbarPt = -1.;

    // For all gen particles
    for (size_t i = 0; i < GenPart_pdgId.size(); i++){
        if (GenPart_statusFlags[i] & (1 << 13)) {
            if (GenPart_pdgId[i] == -6) { 
                if ((hardware::DeltaR(GenPart_vects[i],jet0) < 0.8) || (hardware::DeltaR(GenPart_vects[i],jet1) < 0.8)) {
                    genTbarPt = GenPart_vects[i].Pt();
                }
            } else if (GenPart_pdgId[i] == 6) { 
                if ((hardware::DeltaR(GenPart_vects[i],jet0) < 0.8) || (hardware::DeltaR(GenPart_vects[i],jet1) < 0.8)) {
                    genTPt = GenPart_vects[i].Pt();
                }
            }
        }
    }
    return {genTPt,genTbarPt};
}

RVec<float> TopPt_weight::corr(
        RVec<int> GenPart_pdgId, RVec<int> GenPart_statusFlags, RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vects,
        ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1) {

    std::vector<float> matched = matchingGenPt(GenPart_pdgId, GenPart_statusFlags,
                                          GenPart_vects, jet0, jet1);
    float genTPt = matched[0];
    float genTbarPt = matched[1];

    float wTPt = 1.0;
    if (genTPt > 0){ 
        wTPt = exp(0.0615 - 0.0005*genTPt);
    }

    float wTbarPt = 1.0;
    if (genTbarPt > 0){ 
        wTbarPt = exp(0.0615 - 0.0005*genTbarPt);
    }

    return {sqrt(wTPt*wTbarPt)};
}

RVec<float> TopPt_weight::alpha(
        RVec<int> GenPart_pdgId, RVec<int> GenPart_statusFlags, RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vects,
        ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1, float scale){

    std::vector<float> matched = matchingGenPt(GenPart_pdgId, GenPart_statusFlags,
                                          GenPart_vects, jet0, jet1);
    float genTPt = matched[0];
    float genTbarPt = matched[1];

    float wTPt_up = 1.0;
    float wTPt_down = 1.0;
    if (genTPt > 0){ 
        wTPt_up = exp((1+scale)*0.0615 - 0.0005*genTPt) / exp(0.0615 - 0.0005*genTPt);
        wTPt_down = exp((1-scale)*0.0615 - 0.0005*genTPt) / exp(0.0615 - 0.0005*genTPt);
    }

    float wTbarPt_up = 1.0;
    float wTbarPt_down = 1.0;
    if (genTbarPt > 0){ 
        wTbarPt_up = exp((1+scale)*0.0615 - 0.0005*genTbarPt) / exp(0.0615 - 0.0005*genTbarPt);
        wTbarPt_down = exp((1-scale)*0.0615 - 0.0005*genTbarPt) / exp(0.0615 - 0.0005*genTbarPt);
    }

    return {sqrt(wTPt_up*wTbarPt_up),sqrt(wTPt_down*wTbarPt_down)};
}

RVec<float> TopPt_weight::beta(
        RVec<int> GenPart_pdgId, RVec<int> GenPart_statusFlags, RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vects,
        ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1, float scale){

    std::vector<float> matched = matchingGenPt(GenPart_pdgId, GenPart_statusFlags,
                                          GenPart_vects, jet0, jet1);
    float genTPt = matched[0];
    float genTbarPt = matched[1];

    float wTPt_up = 1.0;
    float wTPt_down = 1.0;
    if (genTPt > 0){ 
        wTPt_up = exp(0.0615 - (1+scale)*0.0005*genTPt) / exp(0.0615 - 0.0005*genTPt);
        wTPt_down = exp(0.0615 - (1-scale)*0.0005*genTPt) / exp(0.0615 - 0.0005*genTPt);
    }

    float wTbarPt_up = 1.0;
    float wTbarPt_down = 1.0;
    if (genTbarPt > 0){ 
        wTbarPt_up = exp(0.0615 - (1+scale)*0.0005*genTbarPt) / exp(0.0615 - 0.0005*genTbarPt);
        wTbarPt_down = exp(0.0615 - (1-scale)*0.0005*genTbarPt) / exp(0.0615 - 0.0005*genTbarPt);
    }

    return {sqrt(wTPt_up*wTbarPt_up),sqrt(wTPt_down*wTbarPt_down)};
}