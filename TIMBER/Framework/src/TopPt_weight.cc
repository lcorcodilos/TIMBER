#include <cmath>
#include <stdbool.h>
#include "TIMBER/Framework/include/common.h"
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
        float genTpt; //!< Generator top \f$p_T\f$ 
        float genTBpt; //!< Generator anti-top \f$p_T\f$ 

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
         * Calculate variations of the \f$\alpha\f$ parameter as defined in corr().
         * The amount of variation can be changed via the scale arguement which is a 
         * percent change on \f$\alpha\f$.
         * 
         * @param scale Percent variation on \f$\alpha\f$ parameter.
         * @return RVec<float> {up, down} variations of the top \f$p_T\f$ reweighting value.
         */
        RVec<float> alpha(float scale = 0.5);
        /**
         * @brief MUST RUN corr() FIRST.
         * Calculate variations of the \f$\beta\f$ parameter as defined in corr().
         * The amount of variation can be changed via the scale arguement which is a 
         * percent change on \f$\beta\f$.
         * 
         * @param scale Percent variation on \f$\beta\f$ parameter.
         * @return RVec<float> {up, down} variations of the top \f$p_T\f$ reweighting value.
         */
        RVec<float> beta(float scale = 0.5);
};

RVec<float> TopPt_weight::corr(
        RVec<int> GenPart_pdgId, RVec<int> GenPart_statusFlags, RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vects,
        ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1) {

    RVec<float> out;

    genTpt = 0.0;
    genTBpt = 0.0;
    float wTPt = 1.0;
    float wTbarPt = 1.0;
    // For all gen particles
    for (int i = 0; i < GenPart_pdgId.size(); i++){
        if ((GenPart_pdgId[i] == -6) && (GenPart_statusFlags[i] & (1 << 13))){ 
            if ((hardware::DeltaR(GenPart_vects[i],jet0) <0.8) || (hardware::DeltaR(GenPart_vects[i],jet1) <0.8)){
                genTBpt = GenPart_vects[i].Pt();
            }
        } else if ((GenPart_pdgId[i] == 6) && (GenPart_statusFlags[i] & (1 << 13))){ 
            if ((hardware::DeltaR(GenPart_vects[i],jet0) <0.8) || (hardware::DeltaR(GenPart_vects[i],jet1) <0.8)){
                genTpt = GenPart_vects[i].Pt();
            }
        }
    }
    
    if (genTpt > 0){ 
        wTPt = exp(0.0615 - 0.0005*genTpt);
    }

    if (genTBpt > 0){ 
        wTbarPt = exp(0.0615 - 0.0005*genTBpt);
    }
    out.push_back(sqrt(wTPt*wTbarPt))

    return out;
}

RVec<float> TopPt_weight::alpha(float scale = 0.5){
    RVec<float> out = {1.0,1.0};

    float wTPt_up = 1.0;
    float wTPt_down = 1.0;
    if (genTpt > 0){ 
        wTPt_up = exp((1+scale)*0.0615 - 0.0005*genTpt);
        wTPt_down = exp((1-scale)*0.0615 - 0.0005*genTpt);
    }

    float wTbarPt_up = 1.0;
    float wTbarPt_down = 1.0;
    if (genTBpt > 0){ 
        wTbarPt_up = exp((1+scale)*0.0615 - 0.0005*genTBpt);
        wTbarPt_down = exp((1-scale)*0.0615 - 0.0005*genTBpt);
    }

    out[0] = sqrt(wTPt_up*wTbarPt_up);
    out[1] = sqrt(wTPt_down*wTbarPt_down);
    return out;
}

RVec<float> TopPt_weight::beta(float scale = 0.5){
    RVec<float> out = {1.0,1.0};

    float wTPt_up = 1.0;
    float wTPt_down = 1.0;
    if (genTpt > 0){ 
        wTPt_up = exp(0.0615 - (1+scale)*0.0005*genTpt);
        wTPt_down = exp(0.0615 - (1-scale)*0.0005*genTpt);
    }

    float wTbarPt_up = 1.0;
    float wTbarPt_down = 1.0;
    if (genTBpt > 0){ 
        wTbarPt_up = exp(0.0615 - (1+scale)*0.0005*genTBpt);
        wTbarPt_down = exp(0.0615 - (1-scale)*0.0005*genTBpt);
    }

    out[0] = sqrt(wTPt_up*wTbarPt_up);
    out[1] = sqrt(wTPt_down*wTbarPt_down);
    return out;
}