#include "../include/JetSmearer.h"

JetSmearer::JetSmearer(std::string jetType, std::string jerTag) : 
                        _jetType(jetType), _jerTag(jerTag) {
    _rnd = std::mt19937(123456);
    JERpaths _path(_jetType, _jerTag);
    JME::JetResolution _jer(_path.GetResPath());
    JME::JetResolutionScaleFactor _jerSF(_path.GetSFpath());
    if (Pythonic::InString("AK4",jetType)) {
        _genJetMatcher = std::make_shared<GenJetMatcher>(0.2);
    } else if (Pythonic::InString("AK8",jetType)) {
        _genJetMatcher = std::make_shared<GenJetMatcher>(0.4);
    } else {
        throw "Jet type is not AK4 or AK8.";
    }
};

JetSmearer::JetSmearer(std::string jetType, std::vector<float> jmrVals) : 
                        _jetType(jetType), _jmrVals(jmrVals) {};


std::vector<float> JetSmearer::GetSmearValsPt(LorentzV jet, std::vector<LorentzV> genJets) {
    std::vector<float> out = {};
    if (jet.Pt() <= 0.){
        printf("WARNING: jet pT = %f !!", jet.Pt());
        out = {1.,1.,1.};
    } else {
        float sf, res;
        // Do resolution first
        _paramsRes.setJetEta(jet.Eta());
        _paramsRes.setJetPt(jet.Pt());
        float jet_resolution = _jer.getResolution(_paramsRes);
        const LorentzV* genJet = _genJetMatcher->match(jet, genJets, jet.pt() * jet_resolution);
        float smearFactor;

        for (size_t i; i<_variationIndex.size(); i++) {
            Variation variation = _variationIndex[i];
            _paramsSF.setJetEta(jet.Eta());
            _paramsSF.setJetPt(jet.Pt());
            
            float jet_sf = _jerSF.getScaleFactor(_paramsSF, variation);

            smearFactor = 1;
            if (genJet) { // Case 1: we have a "good" gen jet matched to the reco jet
                double dPt = jet.pt() - genJet->pt();
                smearFactor = 1. + (jet_sf -1.) * dPt / jet.pt();
            } else if (jet_sf > 1) { // Case 2: we don't have a gen jet. Smear jet pt using a random gaussian variation
                float sigma = jet_resolution * std::sqrt(jet_sf * jet_sf - 1.);
                std::normal_distribution<> d(0, sigma);
                smearFactor = 1. + d(_rnd);
            }

            if (jet.E() *  smearFactor < MIN_JET_ENERGY) {
                // Negative or too small smearFactor. We would change direction of the jet
                // and this is not what we want.
                // Recompute the smearing factor in order to have jet.energy() == MIN_JET_ENERGY
                smearFactor = MIN_JET_ENERGY / jet.E();
            }
            out[i] = smearFactor;
        }
        return out;
    }
}

// std::vector<float> JetSmearer::GetSmearValsM(LorentzV jet, LorentzV genJet){
//     std::vector<float> out = {};
//     if (jet.M() <= 0.){
//         printf("WARNING: jet m = %f !!", jet.M());
//         out = {1.,1.,1.};
//     }

//     int central_or_shift;
//     std::vector<int> variation_index = {0,2,1}; // nom,up,down

//     std::map<int, float> jet_m_sf_and_uncertainty = {
//         {0, _jmrVals[0]},
//         {1, _jmrVals[1]},
//         {2, _jmrVals[2]}
//     };
    
//     std::map<int, float> smear_vals = {};
//     float jet_pt_resolution, smear_factor;

//     if (genJet) { // Case 1
//         for (size_t i = 0; i < 3; i++) {
//             central_or_shift = variation_index[i];
//             float dM = jet.M() - genJet.M();
//             smear_factor =
//                 1. + jet_m_sf_and_uncertainty[central_or_shift] - 1. * dM / jet.M();
//         }
//     } else {
//         float jet_m_resolution;
//         if (abs(jet.Eta()) <= 1.3) {
//             jet_m_resolution = puppisd_resolution_cen->Eval(jet.Pt());
//         } else {
//             jet_m_resolution = puppisd_resolution_for->Eval(jet.Pt());
//         }

//         float rand = rnd.Gaus(0, jet_m_resolution);
//         for (size_t i = 0; i < 3; i++) {
//             central_or_shift = variation_index[i];
//             if (jet_m_sf_and_uncertainty[central_or_shift] > 1.){ // Case 2
//                 smear_factor =
//                     rand * sqrt(pow(jet_m_sf_and_uncertainty[central_or_shift],2) - 1.);
//             } else { // Case 3
//                 smear_factor = 1.;
//             }
//         }
//     }

//     // check that smeared jet energy remains positive, as the direction of
//     // the jet would change ("flip") otherwise - and this is not what we want
//     for (size_t i = 0; i < 3; i++) {
//         central_or_shift = variation_index[i];
//         if (smear_vals[central_or_shift] * jet.M() < 1.e-2){
//             smear_vals[central_or_shift] = 1.e-2;
//         }
//         out.push_back(smear_vals[central_or_shift]);
//     }
//     return out;
// }