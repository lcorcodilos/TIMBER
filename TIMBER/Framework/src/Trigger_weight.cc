#include <cmath>
#include <algorithm>
#include "HistLoader.cc"
#include <ROOT/RVec.hxx>
using namespace ROOT::VecOps;

/** @class Trigger_weight
 *  @brief Specializes in the construction of trigger efficiency weights.
 * Uncertainties are calculated as one half of the trigger inefficiency (ie. (1-eff)/2).
 * 
 * Uncertainties are capped to never be greater than 1 or less
 * than 0. Additionally, a plateau value can be provided which
 * assumes 100% efficiency (and zero uncertainty) beyond the provided
 * threshold. 
 * 
 * Finally, if a bin is 0 and the surrounding bins are non-zero 
 * (this could happen in the case of poor statistics),
 * a value for the 0 bin will be linearly interpolated from the two
 * neighboring bins.
 * 
 */
class Trigger_weight
{
    private:
        TH1 *hist;
        HistLoader HL;
    public:
        /**
         * @brief Construct a new Trigger_weight object.
         * 
         * @param filename 
         * @param histname 
         */
        Trigger_weight(std::string filename, std::string histname){
            HistLoader HL(filename,histname);
            TH1 *hist = HL.hist;
        };
        ~Trigger_weight(){};
        /**
         * @brief Evaluates the efficiency as a weight for the provided value, `var`.
         * Also calculates variations of the weight with uncertainties calculated
         * as one half of the trigger inefficiency.
         * 
         * @param var Branch/column name to evaluate
         * @param plateau Assumes plateau (100% efficiency with no uncertainty) beyond provided value.
         *                Defaults to -1.0 in which case there is no plateau considered.
         * @return RVec<float> {nominal, up, down}
         */
        RVec<float> eval(float var,float plateau = 0);
};

RVec<float> Trigger_weight::eval(float var, float plateau) {
    RVec<float> out;

    float weight = 1.;
    float weight_up = 1.;
    float weight_down = 1.;
    float delta = 0.;
    int ibin;

    if ((plateau > 0) && (var > plateau)) {
    } else {
        ibin = hist->FindBin(var);
        weight = hist->GetBinContent(ibin);

        if (weight == 0) { // interpolate bin values in case of zero bin from lack of stats
            if ((hist->GetBinContent(ibin-1) == 1.0) && (hist->GetBinContent(ibin+1) == 1.0)){
                weight = 1.0;
            } else if (((hist->GetBinContent(ibin-1) > 0) || (hist->GetBinContent(ibin+1) > 0))){
                weight = (hist->GetBinContent(ibin-1)+hist->GetBinContent(ibin+1))/2.0;
            }
        }
        delta = 0.5*(1.0-weight);
        weight_up = std::min((float)1.0,(weight + delta));
        weight_down = std::max((float)0.0,(weight - delta));
    }

    out = {weight,weight_up,weight_down};
    return out;
}