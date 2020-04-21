#include <cmath>
#include <stdbool.h>
using namespace ROOT::VecOps;
using rvec_i = const RVec<int> &;
using rvec_d = const RVec<double> &;

namespace analyzer {
    std::vector<float> PTWLookup(int nGenJet, rvec_i GPpdgId, rvec_i GPstatusFlags, rvec_d GPpt, rvec_d GPeta, rvec_d GPphi, rvec_d GPmass, ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1 ){

        std::vector<float> out;

        float genTpt = 0;
        float genTBpt = 0;
        float wTPt, wTbarPt; 
        bool pair_exists = 0.0;

        // For all gen particles
        for (int i =0; i < nGenJet; i++){
            if ((GPpdgId[i] == -6) && (GPstatusFlags[i] & (1 << 13))){ 
                ROOT::Math::PtEtaPhiMVector antitop_lv(GPpt[i],GPeta[i],GPphi[i],GPmass[i]);
                if ((sqrt((antitop_lv.Eta()-jet0.Eta())*(antitop_lv.Eta()-jet0.Eta()) + (deltaPhi(antitop_lv.Phi(),jet0.Phi()))*(deltaPhi(antitop_lv.Phi(),jet0.Phi()))) <0.8) || (sqrt((antitop_lv.Eta()-jet1.Eta())*(antitop_lv.Eta()-jet1.Eta()) + (deltaPhi(antitop_lv.Phi(),jet1.Phi()))*(deltaPhi(antitop_lv.Phi(),jet1.Phi()))) <0.8)){
                    genTBpt = GPpt[i];
                }
            }else if ((GPpdgId[i] == 6) && (GPstatusFlags[i] & (1 << 13))){ 
                ROOT::Math::PtEtaPhiMVector top_lv(GPpt[i],GPeta[i],GPphi[i],GPmass[i]);
                if ((sqrt((top_lv.Eta()-jet0.Eta())*(top_lv.Eta()-jet0.Eta()) + (deltaPhi(top_lv.Phi(),jet0.Phi()))*(deltaPhi(top_lv.Phi(),jet0.Phi()))) <0.8) || (sqrt((top_lv.Eta()-jet1.Eta())*(top_lv.Eta()-jet1.Eta()) + (deltaPhi(top_lv.Phi(),jet1.Phi()))*(deltaPhi(top_lv.Phi(),jet1.Phi()))) <0.8)){
                    genTpt = GPpt[i];
                }
            }
        }

        if ((genTpt == 0) || (genTBpt == 0)){
            pair_exists = 0.0;
        }else{ 
            pair_exists = 1.0;
        }
        
        if (genTpt == 0){ 
            wTPt = 1.0;
        }else{
            wTPt = exp(0.0615-0.0005*genTpt);
        }

        if (genTBpt == 0){ 
            wTbarPt = 1.0;
        }else{
            wTbarPt = exp(0.0615-0.0005*genTBpt);
        }

        out.push_back(sqrt(wTPt*wTbarPt));
        out.push_back(1.25*sqrt(wTPt*wTbarPt));
        out.push_back(0.75*sqrt(wTPt*wTbarPt));
        out.push_back(pair_exists);
        return out;
    }
}
