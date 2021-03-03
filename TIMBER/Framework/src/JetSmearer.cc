#include "../include/JetSmearer.h"

const LorentzV* GenJetMatcher::match(LorentzV& jet, RVec<LorentzV> genJets, float resolution) {
    // Match if dR < _dRMax and dPt < dPtMaxFactor
    double min_dR = std::numeric_limits<double>::infinity();
    const LorentzV* out = nullptr;

    for (const LorentzV & genJet : genJets) {
        float dR = hardware::DeltaR(genJet, jet);
        if (dR > min_dR) {
            continue;
        }
        if (dR < _dRMax) {
            double dPt = std::abs(genJet.pt() - jet.pt());
            if ((resolution == -1) || (dPt <= _dPtMaxFactor * resolution)) {
                min_dR = dR;
                out = &genJet;
            }
        }
    }
    return out;
}

JetSmearer::JetSmearer(std::string jerTag, std::string jetType) : 
                        _jerTag(jerTag), _jetType(jetType){
    _rnd = std::mt19937(123456);
    JERpaths path(_jerTag, _jetType);
    JME::JetResolution _jer(path.GetResPath());
    JME::JetResolutionScaleFactor _jerSF(path.GetSFpath());
    if (Pythonic::InString("AK4",jetType)) {
        _genJetMatcher = std::make_shared<GenJetMatcher>(0.2);
    } else if (Pythonic::InString("AK8",jetType)) {
        _genJetMatcher = std::make_shared<GenJetMatcher>(0.4);
    } else {
        throw "Jet type is not AK4 or AK8.";
    }
};

JetSmearer::JetSmearer(std::vector<float> jmrVals) : 
                        _jetType("AK8"), _jmrVals(jmrVals),
                        _puppisd_res_central(GetPuppiSDResolutionCentral()),
                        _puppisd_res_forward(GetPuppiSDResolutionForward())
                         {
    _genJetMatcher = std::make_shared<GenJetMatcher>(0.4);
};

RVec<float> JetSmearer::GetSmearValsPt(LorentzV jet, RVec<LorentzV> genJets) {
    RVec<float> out(3);
    if (jet.Pt() <= 0.){
        printf("WARNING: jet pT = %f !!", jet.Pt());
        out = {1.,1.,1.};
    } else {
        // Do resolution first
        _paramsRes.setJetEta(jet.Eta());
        _paramsRes.setJetPt(jet.Pt());
        float jet_resolution = _jer.getResolution(_paramsRes);
        const LorentzV* genJet = _genJetMatcher->match(jet, genJets, jet.pt() * jet_resolution);
        float smearFactor, dPt, sigma, jet_sf;

        for (size_t i; i<_variationIndex.size(); i++) {
            Variation variation = _variationIndex[i];
            _paramsSF.setJetEta(jet.Eta());
            _paramsSF.setJetPt(jet.Pt());
            
            jet_sf = _jerSF.getScaleFactor(_paramsSF, variation);

            smearFactor = 1;
            if (genJet) { // Case 1: we have a "good" gen jet matched to the reco jet
                dPt = jet.pt() - genJet->pt();
                smearFactor = 1. + (jet_sf -1.) * dPt / jet.pt();
            } else if (jet_sf > 1) { // Case 2: we don't have a gen jet. Smear jet pt using a random gaussian variation
                sigma = jet_resolution * std::sqrt(jet_sf * jet_sf - 1.);
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
    }
    return out;
}

RVec<float> JetSmearer::GetSmearValsM(LorentzV jet, RVec<LorentzV> genJets){
    RVec<float> out(3);
    if (jet.M() <= 0.){
        printf("WARNING: jet m = %f !!", jet.M());
        out = {1.,1.,1.};
    } else {
        const LorentzV* genJet = _genJetMatcher->match(jet, genJets, -1); // -1 removes pt requirement
        float smearFactor, dMass, sigma, jet_resolution;
        if (std::abs(jet.Eta()) <= 1.3) {
            jet_resolution = _puppisd_res_central->Eval(jet.Pt());
        } else {
            jet_resolution = _puppisd_res_forward->Eval(jet.Pt());
        }
        for (size_t i; i<3; i++) {
            smearFactor = 1;
            if (genJet) { // Case 1: we have a "good" gen jet matched to the reco jet
                dMass = jet.M() - genJet->M();
                smearFactor = 1. + (_jmrVals[i] -1.) * dMass / jet.M();
            } else if (_jmrVals[i] > 1) { // Case 2: we don't have a gen jet. Smear jet pt using a random gaussian variation
                sigma = jet_resolution * std::sqrt(_jmrVals[i] * _jmrVals[i] - 1.);
                std::normal_distribution<> d(0, sigma);
                smearFactor = 1. + d(_rnd);
            }

            if (jet.M() *  smearFactor < MIN_JET_ENERGY) {
                // Negative or too small smearFactor. We would change direction of the jet
                // and this is not what we want.
                // Recompute the smearing factor in order to have jet.energy() == MIN_JET_ENERGY
                smearFactor = MIN_JET_ENERGY / jet.E();
            }
            out[i] = smearFactor;
        }
    }
    return out;
}