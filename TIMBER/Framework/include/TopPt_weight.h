#include "common.h"
#include <cmath>
#include <stdbool.h>
#include <ctime> 
#include <vector>
#include <stdio.h>

using namespace ROOT::VecOps;

/** @class TopPt_weight
 *  @brief Handles the top \f$p_T\f$ reweighting value for \f$t\bar{t}\f$ simulation
 * based on doing gen particle matching. The weight is calculated as 
 * 
 * \f[ \sqrt{e^{\alpha - \beta \cdot p_{T}^{\textrm{Gen} t}} \cdot e^{\alpha - \beta \cdot p_{T}^{\textrm{Gen} \bar{t}} }} \f].
 * 
 * where \f$\alpha = 0.0615\f$ and \f$\beta = 0.0005\f$. See the alpha() and beta() functions
 * to calculate the weights with these parameters varied.
 * 
 * WARNING: You MUST run corr() before alpha() and beta() since these functions
 * recycle information derived from corr().
 * 
 */
class TopPt_weight {
    private:
        std::vector<float> matchingGenPt(RVec<int> GenPart_pdgId, RVec<int> GenPart_statusFlags, RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vects,
                ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1);

    public:
        TopPt_weight(){};
        ~TopPt_weight(){};
        /**
         * @brief Calculate the top \f$p_T\f$ reweighting value for \f$t\bar{t}\f$ simulation
         * based on doing gen particle matching. The weight is calculated as 
         * \f[ \sqrt{e^{\alpha - \beta \cdot p_{T}^{\textrm{Gen } t}} \cdot e^{\alpha - \beta \cdot p_{T}^{\textrm{Gen } \bar{t}} }} \f].
         * where \f$\alpha = 0.0615\f$ and \f$\beta = 0.0005\f$. See the alpha() and beta() functions
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
         * @brief Calculate variations of top \f$p_T\f$ weight by varying the \f$\alpha\f$ parameter.
         * The amount of variation can be changed via the scale arguement which is a 
         * percent change on \f$\alpha\f$. The output is the weight calculated with the variation
         * divided by the nominal value. When using MakeWeightCols(), the nominal will be multiplied
         * by this variation to recover the total weight.
         * 
         * @param GenPart_pdgId NanoAOD branch
         * @param GenPart_statusFlags NanoAOD branch
         * @param GenPart_vects Vector of ROOT::Math::PtEtaPhiMVectors (create through hardware::TLvector)
         * @param jet0 
         * @param jet1 
         * @param scale Percent variation on \f$\alpha\f$ parameter.
         * @return RVec<float> {up, down} variations of the top \f$p_T\f$ reweighting value divided by the nominal weight.
         */
        RVec<float> alpha(
                RVec<int> GenPart_pdgId, RVec<int> GenPart_statusFlags, RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vects,
                ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1, float scale = 0.5);
        /**
         * @brief Calculate variations of the top \f$p_T\f$ weight by varying the \f$\beta\f$ parameter.
         * The amount of variation can be changed via the scale arguement which is a 
         * percent change on \f$\beta\f$. The output is the weight calculated with the variation
         * divided by the nominal value. When using MakeWeightCols(), the nominal will be multiplied
         * by this variation to recover the total weight.
         * 
         * @param GenPart_pdgId NanoAOD branch
         * @param GenPart_statusFlags NanoAOD branch
         * @param GenPart_vects Vector of ROOT::Math::PtEtaPhiMVectors (create through hardware::TLvector)
         * @param jet0 
         * @param jet1 
         * @param scale Percent variation on \f$\beta\f$ parameter.
         * @return RVec<float> {up, down} variations of the top \f$p_T\f$ reweighting value divided by the nominal weight.
         */
        RVec<float> beta(
                RVec<int> GenPart_pdgId, RVec<int> GenPart_statusFlags, RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vects,
                ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1, float scale = 0.5);
};