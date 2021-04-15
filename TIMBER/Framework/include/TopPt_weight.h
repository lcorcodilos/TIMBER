#ifndef _TIMBER_TOPPT_WEIGHT
#define _TIMBER_TOPPT_WEIGHT
#include "common.h"
#include <cmath>
#include <stdbool.h>
#include <ctime> 
#include <vector>
#include <stdio.h>

using namespace ROOT::VecOps;

/** @class TopPt_weight
 *  @brief C++ class. Handles the top \f$p_T\f$ reweighting value for \f$t\bar{t}\f$ simulation
 * based on doing gen particle matching. The weight is calculated as 
 * 
 * \f[ \sqrt{e^{\alpha - \beta \cdot p_{T}^{\textrm{Gen} t}} \cdot e^{\alpha - \beta \cdot p_{T}^{\textrm{Gen} \bar{t}} }} \f].
 * 
 * where \f$\alpha = 0.0615\f$ and \f$\beta = 0.0005\f$. See the eval() function
 * to calculate the weight plus variations of the \f$\beta\f$ parameter. The \f$\alpha\f$ parameter
 * is not varied since it would only represent a flat normalization change.
 * 
 */
class TopPt_weight {
    private:
        std::vector<float> matchingGenPt(RVec<int> GenPart_pdgId, RVec<int> GenPart_statusFlags, RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vect,
                ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1);

    public:
        /**
         * @brief Construct a new TopPt_weight object. No arguments.
         * 
         */
        TopPt_weight();
        ~TopPt_weight(){};
        /**
         * @brief Calculate the top \f$p_T\f$ reweighting value for \f$t\bar{t}\f$ simulation
         * based on doing gen particle matching. Additionally, calculate variations of the top
         * \f$p_T\f$ weight by varying the \f$\beta\f$ parameter.
         * The amount of variation can be changed via the scale arguement which is a 
         * percent change on \f$\beta\f$. There is no corresponding function for \f$\alpha\f$
         * because the effect is only a flat normalization change.
         * 
         * @param GenPart_pdgId NanoAOD branch
         * @param GenPart_statusFlags NanoAOD branch
         * @param GenPart_vect Vector of ROOT::Math::PtEtaPhiMVectors (create through hardware::TLvector)
         * @param jet0 
         * @param jet1 
         * @param scale Percent variation on \f$\beta\f$ parameter.
         * @return RVec<float> {nom, up, down} variations of the top \f$p_T\f$ reweighting value (absolute).
         */
        RVec<float> eval(
                RVec<int> GenPart_pdgId, RVec<int> GenPart_statusFlags, RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vect,
                ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1, float scale = 0.5);
};
#endif