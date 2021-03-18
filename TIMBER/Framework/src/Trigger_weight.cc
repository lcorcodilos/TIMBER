#include "../include/Trigger_weight.h"

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